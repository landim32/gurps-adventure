#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inventaria uma pasta de imagens soltas antes de importar como token.

    python triar.py --origem ~/Downloads/tokens

Mostra dimensoes, se ja tem transparencia e o hash de cada arquivo, e agrupa os
duplicados exatos — pasta de download costuma acumular a mesma arte baixada duas vezes
com nomes diferentes. Tambem avisa quais ja estao em tokens/, comparando pelo conteudo.

Nao decide o que e token: isso e trabalho de olhar as imagens.
"""
import argparse
import hashlib
from collections import defaultdict
from pathlib import Path

from PIL import Image

EXTENSOES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def md5(caminho, blocos=1 << 20):
    h = hashlib.md5()
    with open(caminho, "rb") as f:
        for pedaco in iter(lambda: f.read(blocos), b""):
            h.update(pedaco)
    return h.hexdigest()


def inspecionar(caminho):
    try:
        with Image.open(caminho) as im:
            largura, altura = im.size
            tem_alpha = "A" in im.getbands()
            if tem_alpha:
                import numpy as np
                alpha = np.asarray(im.convert("RGBA"))[:, :, 3]
                tem_alpha = bool((alpha < 10).mean() >= 0.02)
            formato = im.format
    except Exception as e:
        return None, f"nao abriu ({type(e).__name__})"
    return {"largura": largura, "altura": altura, "alpha": tem_alpha,
            "formato": formato, "md5": md5(caminho),
            "kb": caminho.stat().st_size // 1024}, None


def main():
    ap = argparse.ArgumentParser(description="Inventaria imagens antes de virar token.")
    ap.add_argument("--origem", required=True, help="Pasta com as imagens soltas")
    ap.add_argument("--tokens", default="tokens",
                    help="Pasta de tokens ja importados (padrao tokens/)")
    ap.add_argument("--min-lado", type=int, default=150,
                    help="Marca como pequena demais abaixo disso (padrao 150)")
    ap.add_argument("--recursivo", action="store_true", help="Entrar em subpastas")
    args = ap.parse_args()

    origem = Path(args.origem).expanduser()
    if not origem.is_dir():
        raise SystemExit(f"{origem} nao e uma pasta.")

    padrao = "**/*" if args.recursivo else "*"
    arquivos = sorted(p for p in origem.glob(padrao)
                      if p.is_file() and p.suffix.lower() in EXTENSOES)
    if not arquivos:
        raise SystemExit(f"Nenhuma imagem em {origem}.")

    # o que ja esta importado, por conteudo
    ja_importados = {}
    pasta_tokens = Path(args.tokens)
    if pasta_tokens.is_dir():
        for p in pasta_tokens.glob("*.png"):
            ja_importados[md5(p)] = p.name

    print(f"{len(arquivos)} imagem(ns) em {origem}\n")
    por_hash = defaultdict(list)
    pequenas, quebradas = [], []

    for p in arquivos:
        info, erro = inspecionar(p)
        if erro:
            quebradas.append((p.name, erro))
            print(f"  x  {p.name[:44]:46s} {erro}")
            continue
        por_hash[info["md5"]].append(p)
        marcas = []
        if info["alpha"]:
            marcas.append("já recortada")
        if min(info["largura"], info["altura"]) < args.min_lado:
            marcas.append("PEQUENA")
            pequenas.append(p.name)
        if info["md5"] in ja_importados:
            marcas.append(f"JÁ EM tokens/ como {ja_importados[info['md5']]}")
        print(f"  .  {p.name[:44]:46s} {info['largura']:>5}x{info['altura']:<5} "
              f"{info['kb']:>5} KB  {', '.join(marcas)}")

    repetidos = {h: ps for h, ps in por_hash.items() if len(ps) > 1}
    if repetidos:
        print(f"\n{len(repetidos)} grupo(s) de duplicados exatos — importe so um de cada:")
        for ps in repetidos.values():
            print("   ", " = ".join(p.name for p in ps))

    print(f"\nResumo: {len(arquivos)} arquivo(s), "
          f"{len(por_hash)} imagem(ns) distinta(s), "
          f"{len(pequenas)} pequena(s), {len(quebradas)} ilegivel(is).")
    print("Agora olhe cada imagem e decida quais sao tokens.")


if __name__ == "__main__":
    main()
