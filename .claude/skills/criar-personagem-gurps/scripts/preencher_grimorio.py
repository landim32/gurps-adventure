#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preenche a Ficha para Grimorio (GURPS 3ed) a partir do mesmo JSON do personagem
e gera uma imagem final (JPEG/PNG), simulando preenchimento a mao.

Uso:
    python preencher_grimorio.py --data personagem.json --template grimorio.jpg --output saida.jpg

Le a lista `magias` do JSON (esquema em SKILL.md, secao "Esquema do JSON"). Se o
personagem nao tiver magias, nao gera nada e avisa.

Cabem 45 magias por pagina. Havendo mais, sao geradas paginas extras com sufixo
numerico (saida.jpg, saida-2.jpg, ...).

Notas de implementacao:
- Como em preencher_ficha.py, todo Y e *baseline* (a linha impressa onde o texto senta),
  medido por analise de pixel sobre grimorio.jpg (2481x3508 px).
- A grade tem 46 regras horizontais de y=325 a y=3306 (passo ~66,25 px) e divisores
  verticais em x = 676, 842, 1061, 1280, 1499, 1737, 2217, com a moldura em 147..2329.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

from preencher_ficha import draw_field  # mesma fonte manuscrita e mesmo encolhimento

# ---------------------------------------------------------------------------
# Mapa de campos. Formato: (x, baseline_y, size[, align[, max_width]])
# ---------------------------------------------------------------------------
# "Grimorio pertencente a ______" — a linha de assinatura vai de x=1300 a x=1995.
TITULAR = (1320, 186, 34, "left", 650)

LINHAS = {
    "start_baseline": 382,   # primeira regra util (y=391) menos a folga da baseline
    "row_h": 66.25,          # passo medido entre as regras
    "max_rows": 45,
}

# Centros/limites das colunas, entre os divisores verticais medidos.
COLUNAS = {
    "nome":         (170,  30, "left",   490),  # Nome e Classe da Magica (147..676)
    "nh":           (759,  28, "center", 150),  # NH                      (676..842)
    "tempo":        (951,  26, "center", 200),  # Tempo op.               (842..1061)
    "duracao":      (1170, 26, "center", 200),  # Duracao                 (1061..1280)
    "custo_fazer":  (1389, 26, "center", 200),  # Custo p/fazer           (1280..1499)
    "custo_manter": (1618, 26, "center", 218),  # Custo p/manter          (1499..1737)
    "obs":          (1755, 25, "left",   450),  # Obs.                    (1737..2217)
    "pag":          (2273, 25, "center", 100),  # Pag.                    (2217..2329)
}


def montar_linhas(magias):
    """Ordena as magias e insere uma linha em branco a cada troca de categoria."""
    linhas = []
    cat_anterior = None
    for m in magias:
        cat = m.get("categoria")
        if linhas and cat_anterior is not None and cat != cat_anterior:
            linhas.append(None)
        linhas.append(m)
        cat_anterior = cat
    return linhas


def paginar(linhas, por_pagina):
    """Fatia as linhas em paginas, sem comecar pagina com separador em branco."""
    paginas, atual = [], []
    for linha in linhas:
        if linha is None and not atual:
            continue  # nao abre pagina com linha em branco
        atual.append(linha)
        if len(atual) == por_pagina:
            paginas.append(atual)
            atual = []
    if atual:
        paginas.append(atual)
    return paginas


def rotulo_magia(m):
    """'Nome (Classe)' — a coluna impressa pede nome e classe juntos."""
    nome = (m.get("nome") or "").strip()
    classe = (m.get("classe") or "").strip()
    return f"{nome} ({classe})" if classe else nome


def desenhar_pagina(template, titular, linhas):
    img = Image.open(template).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_field(draw, TITULAR, titular)

    for i, m in enumerate(linhas[: LINHAS["max_rows"]]):
        if m is None:
            continue
        y = int(LINHAS["start_baseline"] + i * LINHAS["row_h"])
        for campo, (x, size, align, largura) in COLUNAS.items():
            valor = rotulo_magia(m) if campo == "nome" else m.get(campo)
            draw_field(draw, (x, y, size, align, largura), valor)
    return img


def salvar(img, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in (".jpg", ".jpeg"):
        img.save(path, quality=92)
    else:
        img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="JSON com os dados do personagem")
    ap.add_argument("--template", required=True, help="Imagem em branco do grimorio (grimorio.jpg)")
    ap.add_argument("--output", required=True, help="Caminho da imagem final")
    args = ap.parse_args()

    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    magias = data.get("magias") or []
    if not magias:
        print("Personagem sem magias: grimorio nao gerado.")
        return

    titular = data.get("nome", "")
    paginas = paginar(montar_linhas(magias), LINHAS["max_rows"])

    out = Path(args.output)
    for n, linhas in enumerate(paginas, start=1):
        destino = out if n == 1 else out.with_name(f"{out.stem}-{n}{out.suffix}")
        salvar(desenhar_pagina(args.template, titular, linhas), destino)
        print(f"Grimorio gerado em: {destino}")

    if len(paginas) > 1:
        print(f"{len(magias)} magias em {len(paginas)} paginas.")


if __name__ == "__main__":
    main()
