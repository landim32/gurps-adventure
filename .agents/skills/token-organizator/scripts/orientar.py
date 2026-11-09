#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gira um token no proprio plano para deixar o personagem virado para o sul.

    python orientar.py --imagem tokens/orc.png --girar 45

Sul e a borda de baixo da imagem: rosto, peito e arma apontando para la.

Girar um token visto de cima e legitimo — equivale a virar a miniatura na mesa, porque a
camera esta a pino e nao ha perspectiva para quebrar. O que a rotacao *nao* conserta e a
sombra projetada: ela gira junto e passa a apontar para o lado errado da luz. Em token
com sombra marcada, considere remove-la antes (remover_fundo.py --sombra).

--girar e em graus, **positivo = sentido horario** (o intuitivo ao olhar a imagem).
Sem --girar o script so relata o enquadramento atual e nao escreve nada.
"""
import argparse
from pathlib import Path

from PIL import Image


def aparar(img, margem):
    caixa = img.getbbox()
    if not caixa:
        return img
    x0, y0, x1, y1 = caixa
    return img.crop((max(0, x0 - margem), max(0, y0 - margem),
                     min(img.width, x1 + margem), min(img.height, y1 + margem)))


def main():
    ap = argparse.ArgumentParser(
        description="Gira o token para o personagem encarar o sul (base da imagem).")
    ap.add_argument("--imagem", required=True)
    ap.add_argument("--saida", help="Padrao: sobrescreve a propria imagem")
    ap.add_argument("--girar", type=float,
                    help="Graus, positivo = horario. Omitir = so relatar")
    ap.add_argument("--margem", type=int, default=8,
                    help="Folga ao reaparar depois de girar (padrao 8)")
    ap.add_argument("--sem-aparar", action="store_true")
    args = ap.parse_args()

    caminho = Path(args.imagem)
    img = Image.open(caminho).convert("RGBA")
    antes = img.size

    if args.girar is None:
        print(f"{caminho.name}: {antes[0]}x{antes[1]} px — nada girado "
              "(passe --girar para corrigir a direcao).")
        return

    angulo = args.girar % 360
    if angulo == 0:
        print(f"{caminho.name}: ja esta virado para o sul, nada a fazer.")
        return

    # PIL gira no anti-horario para angulo positivo; invertemos para o sentido intuitivo.
    girada = img.rotate(-angulo, expand=True, resample=Image.BICUBIC)
    if not args.sem_aparar:
        girada = aparar(girada, args.margem)

    saida = Path(args.saida) if args.saida else caminho
    saida.parent.mkdir(parents=True, exist_ok=True)
    girada.save(saida)

    sentido = "horario" if args.girar > 0 else "anti-horario"
    print(f"{caminho.name}: girado {abs(args.girar):g} graus no sentido {sentido}")
    print(f"  {antes[0]}x{antes[1]} -> {girada.size[0]}x{girada.size[1]} px")
    print(f"  gravado em: {saida}")


if __name__ == "__main__":
    main()
