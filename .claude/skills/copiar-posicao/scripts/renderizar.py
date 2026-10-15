#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Põe o modelo 3D (.glb Mixamo) na pose de um arquivo de pose e desenha uma imagem do tamanho da
imagem de referência, com a mesma posição e o mesmo zoom, para comparar. Só numpy, Pillow e
OpenCV (sem OpenGL): rasterizador por software, com ordenação de triângulos e sombreado simples.

    python .claude/skills/copiar-posicao/scripts/renderizar.py modelo.glb ref.png pose.json --saida tentativa-1
    python .claude/skills/copiar-posicao/scripts/renderizar.py modelo.glb --info

Escreve `<saida>.png` (o modelo sobre branco), `<saida>-comparacao.png` (referência | modelo |
sobreposição: verde = só a referência, vermelho = só o modelo, cinza = os dois) e imprime a
**IoU** das silhuetas e a distância entre os centros. Com `--esqueleto` desenha as juntas e seus
nomes sobre o modelo, para ler qual osso precisa mexer.

Arquivo de pose (JSON):
{
  "camera": {"yaw": 0, "pitch": 0, "fov": 30, "ajuste": "altura"},
  "graus": {"Spine": [10, 0, 0], "RightArm": [-25, -10, -55]},
  "hipsLift": -0.03, "hipsLiftDe": "height"
}
camera.yaw: gira a câmera em volta do modelo (graus; + vai para a esquerda do personagem);
camera.pitch: sobe a câmera (graus); camera.fov: abertura (graus; menor = mais achatado);
camera.ajuste: "altura" (padrão), "largura" ou "caixa" — o que casar com a silhueta da referência.
excluir (opcional): lista de polígonos [[x, y], ...] em pixels da imagem, tirados da silhueta da
referência — a arma, o escudo ou o cenário que o modelo não tem (senão a IoU puxa os ossos para
cobri-los). Eles aparecem em azul na comparação.
alvos (opcional): {"RightHandMiddle2": [x, y], ...} pontos da imagem de referência (em pixels da
imagem) onde cada junta deve cair — cotovelos, punhos, joelhos, topo da cabeça. A silhueta sozinha
não distingue um braço levantado de um braço cruzado sobre o peito; os alvos distinguem. Cruz verde
= ponto marcado, losango magenta = onde a junta caiu. "RightHandMiddle2" e "LeftHandMiddle2" são o
centro do punho; "RightForeArm" e "LeftForeArm" são os cotovelos; "*Hand" é o pulso.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import glb  # noqa: E402

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

SUPER = 2  # amostragem em dobro, reduzida no fim (suaviza as bordas)

JUNTAS_DESENHADAS = [
    "Hips", "Spine", "Spine1", "Spine2", "Neck", "Head",
    "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot",
    "LeftHandMiddle2", "RightHandMiddle2", "HeadTop_End",   # centro do punho e topo da cabeça
]


# ---------------------------------------------------------------- referência
def carregar_referencia(caminho):
    """(imagem RGB uint8, máscara bool). Usa o alfa do PNG; senão fundo liso; senão GrabCut."""
    im = Image.open(caminho)
    if im.mode in ("RGBA", "LA") and np.array(im.getchannel("A")).min() < 250:
        mascara = np.array(im.getchannel("A")) > 128
        fundo = Image.new("RGB", im.size, (255, 255, 255))
        fundo.paste(im.convert("RGB"), mask=im.getchannel("A"))
        return np.array(fundo), _limpar(mascara)
    rgb = np.array(im.convert("RGB"))
    return rgb, _limpar(_mascara_rgb(rgb))


def _mascara_rgb(rgb):
    h, w = rgb.shape[:2]
    borda = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]).astype(float)
    med = np.median(borda, axis=0)
    if np.abs(borda - med).max(axis=1).mean() < 12:   # fundo liso (branco, cinza, verde…)
        dist = np.abs(rgb.astype(float) - med).max(axis=2)
        return dist > 28
    m = np.zeros((h, w), np.uint8)
    ret = (int(w * .02), int(h * .02), int(w * .96), int(h * .96))
    bg, fg = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), m, ret, bg, fg, 6, cv2.GC_INIT_WITH_RECT)
    return (m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD)


def _limpar(m):
    m = m.astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, rot, est, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        grande = 1 + int(np.argmax(est[1:, cv2.CC_STAT_AREA]))
        m = (rot == grande).astype(np.uint8)
    return m.astype(bool)


def aplicar_exclusoes(mascara, pose):
    """Tira da máscara da referência o que não é corpo do modelo (arma, escudo, cenário).

    pose["excluir"] = [[[x, y], [x, y], ...], ...] — polígonos em pixels da referência."""
    polis = (pose or {}).get("excluir") or []
    if not polis:
        return mascara
    corte = np.zeros(mascara.shape, np.uint8)
    for poli in polis:
        cv2.fillPoly(corte, [np.array(poli, np.int32)], 1)
    return _limpar(mascara & (corte == 0))


def caixa_da_mascara(m):
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


# ---------------------------------------------------------------- câmera
class Camera:
    """Câmera em órbita em volta do centro do modelo, ajustada à caixa da referência."""

    def __init__(self, yaw=0.0, pitch=0.0, fov=30.0):
        self.yaw, self.pitch, self.fov = yaw, pitch, fov

    def base(self, centro):
        ya, pi = math.radians(self.yaw), math.radians(self.pitch)
        dir_ = np.array([math.sin(ya) * math.cos(pi), math.sin(pi), math.cos(ya) * math.cos(pi)])
        self.pos = centro + dir_ * 10.0
        self.f = -dir_
        r = np.cross(self.f, [0, 1, 0])
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)
        self.foco = 1.0 / math.tan(math.radians(self.fov) / 2)

    def projetar(self, p):
        d = p - self.pos
        z = d @ self.f
        return np.c_[(d @ self.r) / z * self.foco, (d @ self.u) / z * self.foco, z]


def ajustar(pts, caixa_ref, modo, w, h):
    """Escala e deslocamento (em pixels) que casam a caixa projetada com a da referência."""
    x0, y0, x1, y1 = caixa_ref
    bx0, bx1 = pts[:, 0].min(), pts[:, 0].max()
    by0, by1 = pts[:, 1].min(), pts[:, 1].max()
    esc_h = (y1 - y0) / max(by1 - by0, 1e-9)
    esc_w = (x1 - x0) / max(bx1 - bx0, 1e-9)
    esc = {"altura": esc_h, "largura": esc_w, "caixa": (esc_h + esc_w) / 2}[modo]
    cx_ref, cy_ref = (x0 + x1) / 2, (y0 + y1) / 2
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    return esc, cx_ref - cx * esc, cy_ref + cy * esc


# ---------------------------------------------------------------- desenho
def _cor_triangulos(pr, nor_tri, uv, luz):
    n = len(pr.tris)
    base = np.tile(pr.cor, (n, 1))
    if pr.textura is not None and uv is not None:
        h, w = pr.textura.shape[:2]
        c = uv[pr.tris].mean(axis=1)
        x = np.clip((c[:, 0] % 1.0) * (w - 1), 0, w - 1).astype(int)
        y = np.clip((c[:, 1] % 1.0) * (h - 1), 0, h - 1).astype(int)
        base = base * (pr.textura[y, x] / 255.0)
    sombra = 0.45 + 0.65 * np.clip(nor_tri @ luz, 0, 1)
    return np.clip(base * sombra[:, None], 0, 1)


def desenhar(partes, cam, esc, dx, dy, w, h, esqueleto=None):
    """Rasteriza (painter) as partes deformadas. Devolve (rgba float, juntas 2D)."""
    W, H = w * SUPER, h * SUPER
    img = np.zeros((H, W, 4), np.uint8)
    luz = -cam.f * 0.6 + cam.u * 0.5 + cam.r * -0.3
    luz = luz / np.linalg.norm(luz)
    todos = []
    for pr, v, nor in partes:
        p = cam.projetar(v)
        sx = (p[:, 0] * esc + dx) * SUPER
        sy = (dy - p[:, 1] * esc) * SUPER
        t = pr.tris
        a = np.c_[sx, sy]
        area = (a[t[:, 1], 0] - a[t[:, 0], 0]) * (a[t[:, 2], 1] - a[t[:, 0], 1]) \
            - (a[t[:, 2], 0] - a[t[:, 0], 0]) * (a[t[:, 1], 1] - a[t[:, 0], 1])
        if nor is not None:
            nn = nor / np.maximum(np.linalg.norm(nor, axis=1, keepdims=True), 1e-9)
            nt = nn[t].mean(axis=1)
        else:
            e1, e2 = v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]]
            nt = np.cross(e1, e2)
            nt = nt / np.maximum(np.linalg.norm(nt, axis=1, keepdims=True), 1e-9)
        cor = _cor_triangulos(pr, nt, pr.uv, luz)
        prof = p[t, 2].mean(axis=1)
        frente = (nt @ -cam.f) > -0.05          # descarta as faces viradas para longe
        for i in np.where(frente)[0]:
            todos.append((prof[i], a[t[i]], cor[i]))
    todos.sort(key=lambda e: -e[0])
    for _, tri, c in todos:
        pts = np.round(tri * 16).astype(np.int32)
        col = (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255), 255)
        cv2.fillConvexPoly(img, pts, col, cv2.LINE_8, 4)
    rgba = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    return rgba


def juntas_2d(modelo, mundo, cam, esc, dx, dy):
    out = {}
    for nome in JUNTAS_DESENHADAS:
        i = modelo.osso(nome)
        if i is None:
            continue
        p = cam.projetar(mundo[i][:3, 3][None])[0]
        out[nome] = (p[0] * esc + dx, dy - p[1] * esc)
    return out


# ---------------------------------------------------------------- pipeline
def renderizar(modelo, pose, ref_rgb, ref_mascara, esqueleto=False):
    h, w = ref_rgb.shape[:2]
    c = pose.get("camera", {})
    cam = Camera(c.get("yaw", 0), c.get("pitch", 0), c.get("fov", 30))
    partes, mundo = modelo.deformar(pose.get("graus", {}), pose.get("hipsLift", 0.0),
                                    pose.get("hipsLiftDe", "height"))
    todos = np.concatenate([v for _, v, _ in partes])
    cam.base((todos.min(axis=0) + todos.max(axis=0)) / 2)
    pts = cam.projetar(todos)
    esc, dx, dy = ajustar(pts, caixa_da_mascara(ref_mascara), c.get("ajuste", "altura"), w, h)
    rgba = desenhar(partes, cam, esc, dx, dy, w, h)
    alfa = rgba[:, :, 3] / 255.0
    rgb = rgba[:, :, :3] * alfa[:, :, None] + 255 * (1 - alfa[:, :, None])
    saida = rgb.astype(np.uint8)
    mascara = alfa > 0.5
    juntas = juntas_2d(modelo, mundo, cam, esc, dx, dy)
    if esqueleto:
        for nome, (x, y) in juntas.items():
            cv2.circle(saida, (int(x), int(y)), 6, (255, 0, 255), -1)
            cv2.putText(saida, nome, (int(x) + 8, int(y) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                        (255, 0, 255), 1, cv2.LINE_AA)
    return saida, mascara, juntas


def comparar(ref_rgb, ref_m, saida, saida_m):
    inter = (ref_m & saida_m).sum()
    uniao = (ref_m | saida_m).sum()
    iou = inter / max(uniao, 1)
    sob = np.full(ref_rgb.shape, 255, np.uint8)
    sob[ref_m & ~saida_m] = (40, 200, 40)
    sob[saida_m & ~ref_m] = (220, 40, 40)
    sob[ref_m & saida_m] = (120, 120, 120)
    return iou, np.concatenate([ref_rgb, saida, sob], axis=1)


def erro_alvos(juntas, alvos):
    """Distância (px) de cada junta ao ponto marcado na referência. alvos = {osso: [x, y]}."""
    return {k: math.dist(juntas[k], v) for k, v in (alvos or {}).items() if k in juntas}


def nota(iou, erros):
    """IoU descontada do erro médio das juntas marcadas (150 px de erro = -0,10)."""
    return iou - (sum(erros.values()) / len(erros) / 1500 if erros else 0.0)


def marcar_alvos(img, alvos, juntas):
    """Cruz verde no ponto marcado, cruz magenta onde a junta caiu, e uma linha entre as duas."""
    for k, v in (alvos or {}).items():
        x, y = int(v[0]), int(v[1])
        cv2.drawMarker(img, (x, y), (0, 170, 0), cv2.MARKER_CROSS, 22, 3)
        if k in juntas:
            jx, jy = int(juntas[k][0]), int(juntas[k][1])
            cv2.line(img, (x, y), (jx, jy), (0, 170, 0), 1, cv2.LINE_AA)
            cv2.drawMarker(img, (jx, jy), (255, 0, 255), cv2.MARKER_DIAMOND, 14, 2)
        cv2.putText(img, k, (x + 8, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 120, 0), 1, cv2.LINE_AA)


def centro(m):
    ys, xs = np.where(m)
    return xs.mean(), ys.mean()


def main(argv):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("modelo")
    p.add_argument("referencia", nargs="?")
    p.add_argument("pose", nargs="?")
    p.add_argument("--saida", default="tentativa")
    p.add_argument("--esqueleto", action="store_true")
    p.add_argument("--info", action="store_true", help="só descreve o modelo")
    a = p.parse_args(argv)

    modelo = glb.carregar(a.modelo)
    if a.info:
        ossos = set(modelo.ossos_mixamo())
        faltam = [o for o in ("Hips", "Spine", "Head", "LeftArm", "RightArm", "LeftUpLeg", "RightUpLeg") if o not in ossos]
        print(f"{a.modelo}: {len(modelo.nomes)} nós, {sum(len(p.tris) for p in modelo.prims)} triângulos, "
              f"{len(modelo.peles)} pele(s), altura em descanso {modelo.altura_descanso():.3f}")
        print("esqueleto Mixamo:", "SIM" if not faltam else f"NÃO (faltam {', '.join(faltam)})")
        print("esquerda do personagem em +X:", "sim" if modelo.esquerda_e_mais_x() else "NÃO (modelo espelhado)")
        ossos_ani = sorted(ossos)
        print("ossos:", ", ".join(ossos_ani))
        return 0 if not faltam else 1

    if not (a.referencia and a.pose):
        p.error("informe a imagem de referência e o arquivo de pose")
    ref_rgb, ref_m = carregar_referencia(a.referencia)
    pose = json.load(open(a.pose, encoding="utf-8"))
    ref_m = aplicar_exclusoes(ref_m, pose)
    saida, sm, juntas = renderizar(modelo, pose, ref_rgb, ref_m, a.esqueleto)
    iou, comp = comparar(ref_rgb, ref_m, saida, sm)
    alvos = pose.get("alvos", {})
    erros = erro_alvos(juntas, alvos)
    if alvos:
        w = ref_rgb.shape[1]
        for k in range(3):                      # as três faixas da comparação
            faixa = np.ascontiguousarray(comp[:, k * w:(k + 1) * w])
            marcar_alvos(faixa, alvos, juntas)
            comp[:, k * w:(k + 1) * w] = faixa
    if pose.get("excluir"):
        w = ref_rgb.shape[1]
        for k in range(3):
            faixa = np.ascontiguousarray(comp[:, k * w:(k + 1) * w])
            for poli in pose["excluir"]:
                cv2.polylines(faixa, [np.array(poli, np.int32)], True, (40, 90, 255), 2, cv2.LINE_AA)
            comp[:, k * w:(k + 1) * w] = faixa
    Image.fromarray(saida).save(a.saida + ".png")
    Image.fromarray(comp).save(a.saida + "-comparacao.png")
    (rx, ry), (sx, sy) = centro(ref_m), centro(sm)
    print(f"IoU das silhuetas: {iou:.3f}  (1,000 = idêntica)")
    print(f"centro da referência ({rx:.0f}, {ry:.0f}) · do modelo ({sx:.0f}, {sy:.0f}) · "
          f"diferença ({sx - rx:+.0f}, {sy - ry:+.0f}) px")
    if erros:
        print("juntas marcadas (erro em px): " + ", ".join(f"{k} {d:.0f}" for k, d in erros.items()))
        print(f"nota (IoU − erro médio/1500): {nota(iou, erros):.3f}")
    print(f"escreveu {a.saida}.png e {a.saida}-comparacao.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
