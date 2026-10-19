#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recorta o fundo de um token: torna transparente a regiao de cor uniforme que encosta
na borda da imagem, preservando o que estiver dentro da figura.

    python remover_fundo.py --imagem t.jpg --saida tokens/guerreiro.png

Por que preenchimento por conexao (flood fill) e nao limiar global: a cota de malha
deste guerreiro e cinza-clara, quase da cor do fundo branco. Um limiar por cor comeria
a armadura junto. O preenchimento so remove o que e parecido com o fundo *e* esta
ligado a borda, entao o cinza interno sobrevive.

--tolerancia controla quanto a cor pode se afastar do fundo e ainda ser considerada
fundo. Sombra projetada e cinza suave ligada a borda: tolerancia mais alta a engole.
Alta demais, o preenchimento vaza para dentro da figura — o script avisa quando a
regiao removida cresce demais de uma vez.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def cor_de_fundo(a):
    """Cor mais frequente na moldura de 1 px da imagem."""
    borda = np.concatenate([a[0, :, :3], a[-1, :, :3], a[:, 0, :3], a[:, -1, :3]])
    cores, contagens = np.unique(borda.reshape(-1, 3), axis=0, return_counts=True)
    return cores[contagens.argmax()].astype(np.int16)


def regiao_de_fundo(parecido):
    """Pixels 'parecidos com o fundo' que se ligam a borda, por crescimento iterativo.

    Semeia pelas quatro bordas ao mesmo tempo: como o fundo costuma ser aberto, o
    caminho ate a borda mais proxima e curto e isso converge em poucas dezenas de
    passadas, em vez das ~N passadas de uma semente unica.
    """
    mascara = np.zeros_like(parecido)
    mascara[0, :] = parecido[0, :]
    mascara[-1, :] = parecido[-1, :]
    mascara[:, 0] = parecido[:, 0]
    mascara[:, -1] = parecido[:, -1]

    while True:
        cresceu = mascara.copy()
        cresceu[1:, :] |= mascara[:-1, :]
        cresceu[:-1, :] |= mascara[1:, :]
        cresceu[:, 1:] |= mascara[:, :-1]
        cresceu[:, :-1] |= mascara[:, 1:]
        cresceu &= parecido
        if cresceu.sum() == mascara.sum():
            return mascara
        mascara = cresceu


def aparar(img, margem):
    """Corta a sobra transparente em volta, deixando `margem` px de folga."""
    if margem is None:
        return img
    caixa = img.getbbox()          # menor retangulo com alpha > 0
    if not caixa:
        return img
    x0, y0, x1, y1 = caixa
    return img.crop((max(0, x0 - margem), max(0, y0 - margem),
                     min(img.width, x1 + margem), min(img.height, y1 + margem)))


def ja_tem_alpha(img, minimo=0.02):
    """True se a imagem ja vem recortada (fracao relevante de pixels transparentes)."""
    if "A" not in img.getbands():
        return False
    alpha = np.asarray(img)[:, :, 3]
    return (alpha < 10).mean() >= minimo


def recortar(caminho, tolerancia, suavizar, margem, sombra, sat_max, lum_min,
             forcar=False):
    img = Image.open(caminho).convert("RGBA")

    if not forcar and ja_tem_alpha(img):
        # Nada a remover: a arte ja veio com fundo transparente. Mexer so pioraria —
        # e o caso do PNG que o Pinterest serve ao lado do JPG.
        resultado = aparar(img, margem)
        transparente = 100.0 * (np.asarray(img)[:, :, 3] < 10).mean()
        return resultado, None, transparente

    a = np.asarray(img).astype(np.int16)
    fundo = cor_de_fundo(a)

    dist = np.abs(a[:, :, :3] - fundo).max(axis=2)
    parecido = dist <= tolerancia
    mascara = regiao_de_fundo(parecido)

    if sombra:
        # Sombra projetada e cinza e nao tem contorno; a figura, neste estilo de arte,
        # e cercada por traco preto. Entao um segundo preenchimento que so anda por
        # pixel dessaturado e claro come a sombra e para na tinta do contorno — o que
        # protege ate as pecas cinzas encostadas no fundo, como a ponta da lanca.
        rgb = a[:, :, :3]
        saturacao = rgb.max(axis=2) - rgb.min(axis=2)
        luminancia = rgb.mean(axis=2)
        cinza_claro = (saturacao <= sat_max) & (luminancia >= lum_min)
        mascara = regiao_de_fundo(parecido | cinza_claro)
        dist = np.where(mascara, 0, dist)

    alpha = np.where(mascara, 0, 255).astype(np.uint8)

    if suavizar:
        # afina a borda serrilhada: alpha proporcional a distancia da cor de fundo
        borda = (~mascara) & (dist <= tolerancia * 2)
        graduado = np.clip((dist - tolerancia) / max(1, tolerancia), 0, 1) * 255
        alpha = np.where(borda, graduado.astype(np.uint8), alpha)

    saida = a.copy()
    saida[:, :, 3] = alpha
    resultado = Image.fromarray(saida.astype(np.uint8), "RGBA")

    resultado = aparar(resultado, margem)

    pct = 100.0 * mascara.sum() / mascara.size
    return resultado, fundo, pct


def main():
    ap = argparse.ArgumentParser(description="Deixa o fundo do token transparente.")
    ap.add_argument("--imagem", required=True)
    ap.add_argument("--saida", required=True, help="Precisa ser .png (guarda o alpha)")
    ap.add_argument("--tolerancia", type=int, default=30,
                    help="0-255 (padrao 30). Suba para comer sombra projetada")
    ap.add_argument("--sem-suavizar", action="store_true",
                    help="Nao graduar o alpha na borda")
    ap.add_argument("--margem", type=int, default=8,
                    help="Recorta a sobra em volta, deixando esta margem em px "
                         "(use --sem-recorte para manter o enquadramento)")
    ap.add_argument("--sem-recorte", action="store_true")
    ap.add_argument("--sombra", action="store_true",
                    help="Tambem remove a sombra projetada cinza. Funciona em arte com "
                         "contorno preto, que e o que segura o preenchimento")
    ap.add_argument("--sombra-saturacao", type=int, default=32,
                    help="Quanto de cor a sombra pode ter (padrao 32)")
    ap.add_argument("--sombra-luminancia", type=int, default=120,
                    help="Quao clara a sombra precisa ser (padrao 120)")
    ap.add_argument("--forcar", action="store_true",
                    help="Recorta mesmo que a imagem ja tenha alpha")
    args = ap.parse_args()

    saida = Path(args.saida)
    if saida.suffix.lower() != ".png":
        raise SystemExit("A saida precisa ser .png — jpg nao guarda transparencia.")

    resultado, fundo, pct = recortar(
        args.imagem, args.tolerancia, not args.sem_suavizar,
        None if args.sem_recorte else args.margem,
        args.sombra, args.sombra_saturacao, args.sombra_luminancia, args.forcar)

    saida.parent.mkdir(parents=True, exist_ok=True)
    resultado.save(saida)

    if fundo is None:
        print(f"Ja vinha com fundo transparente ({pct:.1f}%) — nada a remover, so aparei.")
        print(f"Tamanho final   : {resultado.size[0]}x{resultado.size[1]} px")
        print(f"Token gerado em: {saida}")
        return

    print(f"Fundo detectado : RGB{tuple(int(c) for c in fundo)}")
    print(f"Removido        : {pct:.1f}% da imagem")
    print(f"Tamanho final   : {resultado.size[0]}x{resultado.size[1]} px")
    if pct > 92:
        print("AVISO: removeu quase tudo — a tolerancia provavelmente vazou para dentro "
              "da figura. Tente um valor menor.")
    elif pct < 10:
        print("AVISO: removeu muito pouco — o fundo pode nao ser uniforme, ou a "
              "tolerancia esta baixa demais.")
    print(f"Token gerado em: {saida}")


if __name__ == "__main__":
    main()
