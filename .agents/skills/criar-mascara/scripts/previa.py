#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""previa — o cenário com a máscara por cima, colorida pela ALTURA das paredes.

    previa.py --imagem cenarios/taberna3.png --mascara taberna3-mascara.png --saida taberna3-previa.png
    previa.py --imagem ... --mascara ... --saida ... --colunas 19 --linhas 12 --ampliar 2

Vermelho = parede inteira, laranja e amarelo = paredes cada vez mais baixas; sem cor = vazio.
Uma legenda no canto mostra a escala de alturas. Serve para conferir a máscara contra o
desenho: parede que faltou fica sem cor, vazamento (espaço que devia ser fechado) fica sem
cobertura, porta entupida fica colorida, e um balcão que devia ser baixo mas saiu vermelho é
parede inteira. Com `--colunas` e `--linhas` desenha a grade hexagonal do Roll6 por cima
(flat-top, 40 px do centro ao canto, na escala da imagem), para dar a medida de uma porta
contra um hexágono.
"""
import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from niveis import ALTURA_MINIMA, METROS_PAREDE, NIVEIS, tom_de  # noqa: E402

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BAIXA = (255, 215, 0)    # amarelo: parede baixa
ALTA = (225, 0, 0)       # vermelho: parede inteira


def cor_da_altura(h):
    """Amarelo -> laranja -> vermelho conforme a altura (h entre ALTURA_MINIMA e 1)."""
    t = max(0.0, min(1.0, (h - ALTURA_MINIMA) / (1 - ALTURA_MINIMA)))
    return tuple(round(b + (a - b) * t) for b, a in zip(BAIXA, ALTA))


def fonte(tam):
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:
        return ImageFont.load_default()


def legenda(img, opacidade):
    """Quadro com a escala de alturas no canto inferior esquerdo."""
    itens = [n for n in ("parede", "estante", "muro-alto", "balcao", "mesa", "banco") if n in NIVEIS]
    f = fonte(max(11, round(img.height / 70)))
    lin = round(f.size * 1.5) if hasattr(f, "size") else 16
    larg = round(lin * 9.5)
    alt = lin * (len(itens) + 1) + 8
    x0, y0 = 8, img.height - alt - 8
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x0, y0, x0 + larg, y0 + alt], fill=(0, 0, 0, 190))
    d.text((x0 + 6, y0 + 4), "altura da parede", fill=(255, 255, 255, 255), font=f)
    for i, n in enumerate(itens):
        h = NIVEIS[n][0]
        y = y0 + 4 + lin * (i + 1)
        d.rectangle([x0 + 6, y + 2, x0 + 6 + lin, y + lin - 2], fill=cor_da_altura(h) + (int(255 * max(opacidade, 0.7)),))
        d.text((x0 + 12 + lin, y), f"{h * 100:.0f}%  {n}", fill=(255, 255, 255, 255), font=f)


def main():
    ap = argparse.ArgumentParser(description="Prévia: cenário + máscara colorida pela altura.")
    ap.add_argument("--imagem", required=True)
    ap.add_argument("--mascara", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--opacidade", type=float, default=0.55, help="0 a 1 (0,55)")
    ap.add_argument("--colunas", type=int)
    ap.add_argument("--linhas", type=int)
    ap.add_argument("--ampliar", type=float, default=1.0)
    ap.add_argument("--sem-legenda", action="store_true")
    a = ap.parse_args()

    img = Image.open(a.imagem).convert("RGBA")
    m = Image.open(a.mascara).convert("L")
    if m.size != img.size:
        raise SystemExit(f"tamanhos diferentes: imagem {img.size}, máscara {m.size}")

    # tabelas tom -> cor: a altura da parede é 1 - tom/255
    r, g, b, al = [], [], [], []
    for tom in range(256):
        h = 1 - tom / 255
        if h < ALTURA_MINIMA:
            r.append(0), g.append(0), b.append(0), al.append(0)
        else:
            cr, cg, cb = cor_da_altura(h)
            r.append(cr), g.append(cg), b.append(cb), al.append(int(255 * a.opacidade))
    camada = Image.merge("RGBA", (m.point(r), m.point(g), m.point(b), m.point(al)))
    out = Image.alpha_composite(img, camada)

    if a.colunas and a.linhas:
        d = ImageDraw.Draw(out)
        raio = img.width / (1.5 * a.colunas + 0.5)
        for c in range(a.colunas):
            for l in range(a.linhas):
                cx = raio * (1 + 1.5 * c)
                cy = raio * math.sqrt(3) * (l + 0.5 + 0.5 * (c & 1))
                pts = [(cx + raio * math.cos(math.radians(60 * k)), cy + raio * math.sin(math.radians(60 * k)))
                       for k in range(6)]
                d.line(pts + [pts[0]], fill=(0, 200, 255, 160), width=1)

    if a.ampliar != 1.0:
        out = out.resize((round(out.width * a.ampliar), round(out.height * a.ampliar)), Image.NEAREST)
    if not a.sem_legenda:
        legenda(out, a.opacidade)
    out.convert("RGB").save(a.saida)
    print(f"prévia: {a.saida}  (vermelho = parede inteira, amarelo = parede baixa; "
          f"parede inteira ~ {METROS_PAREDE:.1f} m, tom {tom_de(1)})")


if __name__ == "__main__":
    main()
