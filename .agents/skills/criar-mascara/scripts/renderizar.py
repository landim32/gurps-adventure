#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""renderizar — desenha a Máscara 3D (tom = altura da parede) a partir do JSON.

    renderizar.py --json taberna3-mascara.json --saida taberna3-mascara.png
    renderizar.py --json taberna3-mascara.json --saida taberna3-mascara.png --imagem cenarios/taberna3.png
    renderizar.py --json ... --saida ... --legado        # máscara só preto/branco (Roll6 sem tons de cinza)

No Roll6 o tom de cada ponto é a ALTURA da parede: preto = parede inteira, branco = vazio,
cinza = parede mais baixa (50% de cinza = metade da altura). Cada forma do JSON tem uma altura:

    "altura": 0.33          fração da parede inteira (0 a 1)
    "metros": 1.05          altura real (a parede inteira vale ~3,2 m)
    "nivel":  "balcao"      nome da escala (veja `niveis.py`)
    sem nada                parede inteira (preto)

O JSON traz o tamanho e as formas, em pixels da imagem original:

    { "largura": 1220, "altura": 1074,
      "paredes":   [ {"tipo":"retangulo","x":0,"y":0,"w":1220,"h":40},
                     {"tipo":"retangulo","x":300,"y":200,"w":120,"h":30,"nivel":"balcao","nome":"balcão"},
                     {"tipo":"poligono","pontos":[[x,y],...],"altura":0.6},
                     {"tipo":"linha","pontos":[[x,y],...],"espessura":24},
                     {"tipo":"circulo","cx":300,"cy":200,"r":30},
                     {"tipo":"elipse","x":0,"y":0,"w":80,"h":40},
                     {"tipo":"imagem","arquivo":"detectado.png","nivel":"parede"} ],
      "aberturas": [ ...mesmas formas, em branco depois das paredes (portas)... ] }

`nome` só documenta (não afeta o desenho). `imagem` carrega um PNG em que o preto é parede
(a saída do detectar.py); o caminho é relativo ao JSON.

Onde duas paredes se sobrepõem vale a MAIS ALTA (o tom mais escuro). As aberturas são
desenhadas depois e sobrescrevem: em branco (padrão) abrem passagem; com `altura`/`nivel`
deixam uma parede mais baixa no lugar (um vão com parapeito, por exemplo).

Sem antialiasing: as formas são desenhadas com ImageDraw e cada uma entra com um único tom.
O PNG sai em 1 canal, com o tamanho EXATO do JSON — e, com `--imagem`, o script confere que é
o da imagem do cenário (o Roll6 recusa proporção diferente em mais de 1%).
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from niveis import ALTURA_INTEIRA, ALTURA_MINIMA, resolve_altura, tom_de  # noqa: E402

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def desenha(draw, camada, forma, base):
    """Desenha a forma em `camada` (L, fundo 0) com valor 255."""
    t = forma.get("tipo")
    cor = 255
    if t == "retangulo":
        x, y, w, h = forma["x"], forma["y"], forma["w"], forma["h"]
        draw.rectangle([x, y, x + w - 1, y + h - 1], fill=cor)
    elif t == "poligono":
        draw.polygon([tuple(p) for p in forma["pontos"]], fill=cor)
    elif t == "linha":
        pts = [tuple(p) for p in forma["pontos"]]
        esp = int(forma.get("espessura", 8))
        draw.line(pts, fill=cor, width=esp, joint="curve")
        r = esp / 2
        for x, y in pts:  # pontas e juntas redondas, sem buraco nas quinas
            draw.ellipse([x - r, y - r, x + r, y + r], fill=cor)
    elif t == "circulo":
        cx, cy, r = forma["cx"], forma["cy"], forma["r"]
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cor)
    elif t == "elipse":
        x, y, w, h = forma["x"], forma["y"], forma["w"], forma["h"]
        draw.ellipse([x, y, x + w - 1, y + h - 1], fill=cor)
    elif t == "imagem":
        arq = Path(base) / forma["arquivo"]
        im = Image.open(arq).convert("L").resize(camada.size, Image.NEAREST)
        parede = im.point(lambda p: 255 if p < 128 else 0)  # onde era preto
        camada.paste(cor, mask=parede)
    else:
        raise SystemExit(f"forma desconhecida: {forma!r} (use retangulo, poligono, linha, circulo, elipse, imagem)")


def aplica(mascara, forma, base, abertura):
    """Põe a forma na máscara: parede = o tom mais escuro; abertura = sobrescreve (branco por padrão)."""
    altura = resolve_altura(forma, padrao=0.0 if abertura else 1.0)
    tom = tom_de(altura)
    camada = Image.new("L", mascara.size, 0)
    d = ImageDraw.Draw(camada)
    d.fontmode = "1"
    desenha(d, camada, forma, base)
    camada = camada.point(lambda p: 255 if p >= 128 else 0)
    caixa = camada.getbbox()
    if caixa is None:
        return altura
    regiao = mascara.crop(caixa)
    nova = Image.new("L", regiao.size, tom) if abertura else ImageChops.darker(regiao, Image.new("L", regiao.size, tom))
    mascara.paste(nova, caixa[:2], camada.crop(caixa))
    return altura


def main():
    ap = argparse.ArgumentParser(description="Desenha a Máscara 3D (tom = altura) a partir do JSON.")
    ap.add_argument("--json", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--imagem", help="Imagem do cenário: confere o tamanho (e dá o tamanho se faltar no JSON)")
    ap.add_argument("--legado", action="store_true",
                    help="Só 0 e 255 (altura >= 50%% vira preto): para um Roll6 que ainda não lê tons de cinza")
    a = ap.parse_args()

    doc = json.loads(Path(a.json).read_text(encoding="utf-8"))
    base = Path(a.json).resolve().parent
    larg, alt = doc.get("largura"), doc.get("altura")
    if a.imagem:
        iw, ih = Image.open(a.imagem).size
        if larg and (larg, alt) != (iw, ih):
            raise SystemExit(f"o JSON diz {larg}x{alt} mas a imagem tem {iw}x{ih}: corrija o JSON")
        larg, alt = iw, ih
    if not larg or not alt:
        raise SystemExit("faltam \"largura\" e \"altura\" no JSON (ou passe --imagem)")

    m = Image.new("L", (larg, alt), 255)
    usadas = []
    for f in doc.get("paredes", []):
        usadas.append(aplica(m, f, base, abertura=False))
    for f in doc.get("aberturas", []):
        aplica(m, f, base, abertura=True)
    if a.legado:
        m = m.point(lambda p: 255 if p >= 128 else 0)
    m.save(a.saida)

    total = larg * alt
    hist = m.histogram()
    paredes = total - sum(hist[243:])  # tons que o Roll6 lê como parede (altura >= 5%)
    print(f"máscara: {a.saida}  ({larg}x{alt} px, {paredes / total * 100:.1f}% de parede; "
          f"{len(doc.get('paredes', []))} parede(s), {len(doc.get('aberturas', []))} abertura(s))")
    tons = sorted(((v, c) for v, c in enumerate(hist) if c and v < 243), key=lambda vc: vc[0])
    for v, c in tons:
        h = 1 - v / 255
        rotulo = "inteira" if h >= ALTURA_INTEIRA else f"{h * 100:.0f}%"
        print(f"  tom {v:3}  altura {rotulo:>7}  {c / total * 100:5.1f}% da área")
    invisiveis = [f for f in usadas if 0 < f < ALTURA_MINIMA]
    if invisiveis:
        print(f"AVISO: {len(invisiveis)} forma(s) com altura abaixo de {ALTURA_MINIMA * 100:.0f}%: "
              f"o Roll6 as lê como vazio")
    if a.legado:
        print("modo legado: só preto e branco (formas com altura < 50% ficaram de fora)")


if __name__ == "__main__":
    main()
