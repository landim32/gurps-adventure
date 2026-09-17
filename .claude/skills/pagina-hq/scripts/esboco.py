#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Esboco da pagina: a grade dos quadros, cada personagem em figura geometrica (circulo,
retangulo, linha) e os baloes de verdade por cima.

    python esboco.py --roteiro campanha/hq/vol-01-.../roteiro.json
    python esboco.py --roteiro ... --pagina 3

E o teste de leitura antes de gastar imagem: aqui se ve se o quadro comporta tres
figuras, se o balao cobre a cara de quem fala, se a pagina vira a direita. Os baloes
sao desenhados pela propria skill `baloes-hq`, no mesmo tamanho que terao na pagina
final — um balao que nao cabe no esboco tambem nao vai caber depois.

Nenhuma IA entra aqui: e so Pillow.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout  # noqa: E402
from layout import baloes  # noqa: E402

TRACO = "#5B6B8C"        # azul de lapis de esboco
TENUE = "#AAB6CC"
NOTA = "#7A6A50"

POSES = ("de pé", "sentado", "caído", "correndo", "montado", "close", "multidão",
         "objeto")


def olhar_para(olhando):
    o = (olhando or "").strip().lower()
    if o.startswith("esq"):
        return -1.0
    if o.startswith("dir"):
        return 1.0
    if o.startswith("cost"):
        return 0.0
    return 0.0


def figura(d, cx, pe_y, altura, pose="de pé", olhando="", cor=TRACO, esp=4):
    """Desenha uma pessoa com figuras basicas. `cx, pe_y` = onde os pes tocam o chao;
    `altura` em pixels. As proporcoes sao as de sempre: cabeca = 1/7 do corpo."""
    pose = (pose or "de pé").strip().lower()
    h = float(altura)
    r_cab = h / 7.0 / 2.0
    lado = olhar_para(olhando)

    if pose.startswith("close"):
        # Close: so a cabeca, grande, com os eixos do rosto para dizer para onde olha.
        r = h / 2.2
        d.ellipse([cx - r, pe_y - 2 * r, cx + r, pe_y], outline=cor, width=esp)
        cy = pe_y - r
        d.line([cx - r, cy, cx + r, cy], fill=TENUE, width=max(2, esp - 2))
        d.line([cx + lado * r * 0.35, cy - r, cx + lado * r * 0.35, cy + r],
               fill=TENUE, width=max(2, esp - 2))
        return

    if pose.startswith("multid"):
        # Multidao: circulos de tamanhos alternados, sem corpo.
        n = 9
        for i in range(n):
            t = (i / (n - 1)) - 0.5
            r = r_cab * (1.25 if i % 3 == 0 else 0.9)
            x = cx + t * h * 1.6
            y = pe_y - h * (0.55 + 0.12 * ((i * 7) % 3))
            d.ellipse([x - r, y - r, x + r, y + r], outline=cor, width=max(2, esp - 1))
        return

    if pose.startswith("objeto"):
        d.rectangle([cx - h / 2, pe_y - h / 2, cx + h / 2, pe_y], outline=cor,
                    width=esp)
        d.line([cx - h / 2, pe_y - h / 2, cx + h / 2, pe_y], fill=TENUE, width=2)
        return

    if pose.startswith("caí") or pose.startswith("cai"):
        # Caido: o mesmo bonecos deitado, da esquerda para a direita.
        comp = h * 0.85
        x0 = cx - comp / 2
        d.ellipse([x0 - r_cab, pe_y - r_cab * 2, x0 + r_cab, pe_y], outline=cor,
                  width=esp)
        d.rectangle([x0 + r_cab, pe_y - r_cab * 1.7, x0 + comp * 0.62, pe_y - r_cab * .2],
                    outline=cor, width=esp)
        d.line([x0 + comp * 0.62, pe_y - r_cab, x0 + comp, pe_y - r_cab * 1.4],
               fill=cor, width=esp)
        d.line([x0 + comp * 0.62, pe_y - r_cab * .4, x0 + comp * 0.98, pe_y],
               fill=cor, width=esp)
        return

    sentado = pose.startswith("senta")
    montado = pose.startswith("monta")
    corrida = pose.startswith("corr")
    if sentado:
        h *= 0.78
        r_cab = h / 7.0 / 2.0

    topo = pe_y - h
    cy_cab = topo + r_cab
    d.ellipse([cx - r_cab, topo, cx + r_cab, topo + 2 * r_cab], outline=cor, width=esp)
    if lado:                                  # nariz: para onde a figura olha
        d.line([cx + lado * r_cab, cy_cab, cx + lado * r_cab * 1.6, cy_cab],
               fill=cor, width=esp)

    ombro = topo + 2 * r_cab
    quadril = topo + h * (0.52 if not sentado else 0.58)
    larg = h * 0.17
    d.rectangle([cx - larg, ombro, cx + larg, quadril], outline=cor, width=esp)

    # Bracos
    braco = h * 0.30
    dx = braco * (0.75 if corrida else 0.5)
    d.line([cx - larg, ombro + braco * 0.15, cx - larg - dx, ombro + braco],
           fill=cor, width=esp)
    d.line([cx + larg, ombro + braco * 0.15, cx + larg + dx, ombro + braco * (0.4 if
            corrida else 1.0)], fill=cor, width=esp)

    # Pernas
    if sentado:
        joelho_y = quadril + h * 0.16
        d.line([cx - larg * .5, quadril, cx + larg * 1.9 * (lado or 1), joelho_y],
               fill=cor, width=esp)
        d.line([cx + larg * 1.9 * (lado or 1), joelho_y,
                cx + larg * 1.9 * (lado or 1), pe_y], fill=cor, width=esp)
        d.line([cx + larg * .5, quadril, cx + larg * 2.3 * (lado or 1), joelho_y],
               fill=cor, width=esp)
    elif montado:
        d.line([cx - larg, quadril, cx - larg * 1.4, pe_y - h * 0.18], fill=cor,
               width=esp)
        d.line([cx + larg, quadril, cx + larg * 1.4, pe_y - h * 0.18], fill=cor,
               width=esp)
        d.ellipse([cx - h * .45, pe_y - h * .30, cx + h * .45, pe_y], outline=TENUE,
                  width=esp)          # o cavalo, so o volume
    else:
        abre = larg * (2.2 if corrida else 1.0)
        d.line([cx - larg * .4, quadril, cx - abre, pe_y], fill=cor, width=esp)
        d.line([cx + larg * .4, quadril, cx + abre * (0.4 if corrida else 1.0), pe_y],
               fill=cor, width=esp)


def etiqueta(d, x, y, texto, fonte, cor=NOTA, fundo="#FFFFFFCC"):
    if not texto:
        return
    larg = d.textlength(texto, font=fonte)
    alt = fonte.size * 1.25
    d.rectangle([x - 6, y - 3, x + larg + 6, y + alt], fill=fundo)
    d.text((x, y), texto, font=fonte, fill=cor)


def desenhar_pagina(roteiro, pagina, raiz, base):
    img = layout.nova_pagina(roteiro, fundo="#FDFDFB")
    d = ImageDraw.Draw(img)
    f_nota = baloes.carregar_fonte("regular", 30)
    f_num = baloes.carregar_fonte("negrito", 52)

    for quadro, caixa in zip(pagina.get("quadros", []), layout.caixas(pagina, roteiro)):
        x, y, w, h = caixa
        d.rectangle([x, y, x + w, y + h], fill="#F4F3EE", outline="#111111",
                    width=layout.ESPESSURA)

        # Linha do horizonte: ajuda a ver se as figuras estao no mesmo chao.
        chao = y + h * 0.82
        d.line([x + 8, chao, x + w - 8, chao], fill="#E2DED2", width=3)

        for fig in quadro.get("figuras", []):
            fx = x + w * float(fig.get("em", [50, 82])[0]) / 100.0
            fy = y + h * float(fig.get("em", [50, 82])[1]) / 100.0
            altura = h * float(fig.get("altura", 55)) / 100.0
            figura(d, fx, fy, altura, fig.get("pose", "de pé"),
                   fig.get("olhando", ""))
            nome = fig.get("quem", "")
            if nome:
                larg = d.textlength(nome, font=f_nota)
                etiqueta(d, fx - larg / 2, fy + 8, nome, f_nota, cor="#33415C")

        layout.desenhar_baloes(img, quadro, caixa, roteiro)

        d.text((x + 16, y + 12), str(quadro.get("n", "")), font=f_num, fill="#B03030")
        nota = quadro.get("enquadramento", "")
        if nota:
            etiqueta(d, x + 16, y + h - 44, nota, f_nota)

    layout.rodape(img, roteiro, pagina)
    titulo = pagina.get("titulo", "")
    if titulo:
        m = roteiro.get("margem_px", layout.MARGEM)
        d.text((m, m - 54), f"ESBOÇO — {titulo}",
               font=baloes.carregar_fonte("negrito", 36), fill="#8A8A8A")
    return img


def main():
    ap = argparse.ArgumentParser(description="Esboco das paginas a partir do roteiro.")
    ap.add_argument("--roteiro", required=True, help="roteiro.json do volume")
    ap.add_argument("--pagina", action="append", default=[],
                    help="So estas paginas (repetivel)")
    ap.add_argument("--saida", default="", help="Pasta (padrao: <volume>/esbocos/)")
    ap.add_argument("--raiz", default=".", help="Raiz do projeto")
    args = ap.parse_args()

    roteiro = layout.carregar(args.roteiro)
    base = layout.pasta_do_roteiro(args.roteiro)
    destino = Path(args.saida) if args.saida else base / "esbocos"

    feitos = []
    for pagina in layout.paginas_pedidas(roteiro, args.pagina):
        img = desenhar_pagina(roteiro, pagina, args.raiz, base)
        arq = layout.salvar(img, destino / f"pagina-{int(pagina.get('n', 0)):02d}.png")
        feitos.append(arq)
        print(f"  pág. {pagina.get('n')}: {len(pagina.get('quadros', []))} quadro(s) "
              f"-> {arq}")
    print(f"{len(feitos)} esboço(s) em {destino}")


if __name__ == "__main__":
    main()
