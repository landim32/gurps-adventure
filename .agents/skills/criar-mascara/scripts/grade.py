#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""grade — cópia da imagem com uma grade de coordenadas em pixels.

    grade.py --imagem cenarios/taberna3.png --saida taberna3-grade.png
    grade.py --imagem cenarios/taberna3.png --saida taberna3-grade.png --colunas 19 --linhas 12
    grade.py --imagem mapa.png --saida mapa-recorte.png --recorte 0,0,400,300 --ampliar 3

Linhas finas a cada `--passo` pixels (100 por padrão), com os números nas bordas, para
localizar paredes com precisão ao escrever o JSON. Com `--colunas` e `--linhas`, desenha
também a grade de hexágonos do Roll6 (flat-top, "odd-q"): um mapa de C colunas x L linhas
tem largura = 40 x (1,5 C + 0,5) e altura = 40 x raiz(3) x (L + 0,5), e a imagem é só uma
escala dessas medidas. `--recorte x0,y0,x1,y1` e `--ampliar N` servem para olhar um canto de
perto. As coordenadas escritas são sempre as da imagem ORIGINAL.
"""
import argparse
import math
import sys

from PIL import Image, ImageDraw, ImageFont

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def fonte(tam):
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:
        return ImageFont.load_default()


def hexagonos(largura, colunas, linhas):
    """[(coluna, linha, centro_x, centro_y, raio, [6 vértices])] na escala da imagem."""
    raio = largura / (1.5 * colunas + 0.5)
    out = []
    for c in range(colunas):
        for l in range(linhas):
            cx = raio * (1 + 1.5 * c)
            cy = raio * math.sqrt(3) * (l + 0.5 + 0.5 * (c & 1))
            vert = [(cx + raio * math.cos(math.radians(60 * k)),
                     cy + raio * math.sin(math.radians(60 * k))) for k in range(6)]
            out.append((c, l, cx, cy, raio, vert))
    return out


def main():
    ap = argparse.ArgumentParser(description="Imagem com grade de coordenadas em pixels.")
    ap.add_argument("--imagem", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--passo", type=int, default=100, help="Espaço das linhas, em px (100)")
    ap.add_argument("--colunas", type=int, help="Colunas da grade hexagonal do Roll6")
    ap.add_argument("--linhas", type=int, help="Linhas da grade hexagonal do Roll6")
    ap.add_argument("--rotulos-hex", action="store_true", help="Escreve coluna,linha em cada hexágono")
    ap.add_argument("--recorte", help="x0,y0,x1,y1 em px da imagem original")
    ap.add_argument("--ampliar", type=float, default=1.0, help="Fator de ampliação (1)")
    a = ap.parse_args()

    base = Image.open(a.imagem).convert("RGB")
    larg, alt = base.size
    x0, y0, x1, y1 = (0, 0, larg, alt)
    if a.recorte:
        x0, y0, x1, y1 = [int(v) for v in a.recorte.split(",")]
    k = a.ampliar
    rec = base.crop((x0, y0, x1, y1))
    rec = rec.resize((max(1, round(rec.width * k)), max(1, round(rec.height * k))), Image.NEAREST)
    cam = Image.new("RGBA", rec.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    f = fonte(max(11, round(11 * min(k, 2))))

    def tela(x, y):
        return ((x - x0) * k, (y - y0) * k)

    if a.colunas and a.linhas:
        for c, l, cx, cy, r, vert in hexagonos(larg, a.colunas, a.linhas):
            pts = [tela(*v) for v in vert]
            d.line(pts + [pts[0]], fill=(0, 200, 255, 150), width=1)
            if a.rotulos_hex:
                tx, ty = tela(cx, cy)
                d.text((tx, ty), f"{c},{l}", fill=(0, 255, 255, 230), font=f, anchor="mm")

    p = a.passo
    for x in range((x0 // p) * p, x1 + 1, p):
        if x < x0:
            continue
        tx = (x - x0) * k
        d.line([(tx, 0), (tx, rec.height)], fill=(255, 0, 255, 110), width=1)
        for ty in (2, rec.height - 14):
            d.text((tx + 2, ty), str(x), fill=(255, 255, 0, 255), font=f, stroke_width=2, stroke_fill=(0, 0, 0, 255))
    for y in range((y0 // p) * p, y1 + 1, p):
        if y < y0:
            continue
        ty = (y - y0) * k
        d.line([(0, ty), (rec.width, ty)], fill=(255, 0, 255, 110), width=1)
        for tx in (2, rec.width - 34):
            d.text((tx, ty + 2), str(y), fill=(255, 255, 0, 255), font=f, stroke_width=2, stroke_fill=(0, 0, 0, 255))

    Image.alpha_composite(rec.convert("RGBA"), cam).convert("RGB").save(a.saida)
    print(f"grade: {a.saida}  ({larg}x{alt} px na imagem original; passo {p} px)")
    if a.colunas and a.linhas:
        r = larg / (1.5 * a.colunas + 0.5)
        alt_esp = r * math.sqrt(3) * (a.linhas + 0.5)
        print(f"hexágono: raio {r:.1f} px, largura {2 * r:.1f} px; altura esperada {alt_esp:.0f} px "
              f"(imagem tem {alt}; diferença {abs(alt - alt_esp) / alt * 100:.1f}%)")
        print(f"abertura mínima para a câmera: {2 / 3 * 2 * r:.0f} px (2/3 de hexágono)")


if __name__ == "__main__":
    main()
