#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regera tokens/CATALOGO.md a partir de tokens/tokens.json e dos arquivos reais.

    python catalogar.py

As dimensoes nunca sao copiadas do JSON: sao lidas do arquivo na hora. Assim o catalogo
nao mente depois que alguem redimensiona um token na mao.

Aponta as duas formas de desencontro:
  - arquivo em tokens/ que ninguem catalogou
  - entrada no JSON apontando para arquivo que nao existe mais
"""
import argparse
import json
from pathlib import Path

from PIL import Image

CABECALHO = """# Catálogo de tokens

Miniaturas vistas de cima para o mapa hexagonal (1 hexágono = 1 metro).
Gerado por `catalogar.py` — **não edite à mão**; edite `tokens.json` e rode de novo.

Arte de terceiros salvo indicação em contrário, guardada para uso próprio nesta mesa.
Não redistribuir.
"""


def main():
    ap = argparse.ArgumentParser(description="Regera o catalogo de tokens.")
    ap.add_argument("--tokens", default="tokens", help="Pasta de tokens")
    args = ap.parse_args()

    pasta = Path(args.tokens)
    if not pasta.is_dir():
        raise SystemExit(f"{pasta} nao existe.")

    dados_path = pasta / "tokens.json"
    dados = json.loads(dados_path.read_text(encoding="utf-8")) if dados_path.exists() else {"tokens": []}
    entradas = dados.get("tokens", [])

    catalogados = {e["arquivo"] for e in entradas}
    no_disco = {p.name for p in pasta.glob("*.png")}

    orfaos = sorted(no_disco - catalogados)
    fantasmas = sorted(catalogados - no_disco)

    linhas = [CABECALHO]
    por_categoria = {}
    for e in entradas:
        por_categoria.setdefault(e.get("categoria") or "Sem categoria", []).append(e)

    total = 0
    for categoria in sorted(por_categoria):
        linhas.append(f"\n## {categoria}\n")
        linhas.append("| Token | Descrição | Tamanho | Girado | Origem |")
        linhas.append("|---|---|---|---|---|")
        for e in sorted(por_categoria[categoria], key=lambda x: x["arquivo"]):
            caminho = pasta / e["arquivo"]
            if caminho.exists():
                with Image.open(caminho) as im:
                    tam = f"{im.size[0]}×{im.size[1]}"
                total += 1
            else:
                tam = "**ausente**"
            origem = e.get("origem", "—")
            if origem.startswith("http"):
                origem = f"[{origem.split('/')[2]}]({origem})"
            g = e.get("girado", 0)
            giro = "—" if not g else f"{abs(g):g}° {'↻' if g > 0 else '↺'}"
            linhas.append(f"| `{e['arquivo']}` | {e.get('descricao','—')} | {tam} | {giro} | {origem} |")

    linhas.append(f"\n**{total} token(s) catalogado(s).**")

    if orfaos:
        linhas.append("\n## Não catalogados\n")
        linhas.append("Arquivos em `tokens/` que faltam em `tokens.json`:\n")
        for nome in orfaos:
            linhas.append(f"- `{nome}`")

    (pasta / "CATALOGO.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"Catalogados : {total}")
    print(f"Categorias  : {len(por_categoria)}")
    if orfaos:
        print(f"AVISO: {len(orfaos)} arquivo(s) sem entrada no tokens.json: "
              + ", ".join(orfaos[:5]) + ("..." if len(orfaos) > 5 else ""))
    if fantasmas:
        print(f"AVISO: {len(fantasmas)} entrada(s) apontando para arquivo inexistente: "
              + ", ".join(fantasmas[:5]))
    print(f"Catalogo gerado em: {pasta / 'CATALOGO.md'}")


if __name__ == "__main__":
    main()
