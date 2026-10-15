#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preenche a Ficha para Grimorio (GURPS 3ed) a partir do mesmo JSON do personagem
e gera uma imagem final (JPEG/PNG), simulando preenchimento a mao.

Uso:
    python preencher_grimorio.py --data personagem.json --template grimorio.jpg --output saida.jpg

Le a lista `magias` do JSON e, para o lutador de artes marciais, as manobras (as entradas
de `pericias` com categoria "Manobras"), ambas descritas em SKILL.md, secao "Esquema do
JSON". Quem so tem magias ganha o grimorio de magias; quem so tem manobras ganha o
grimorio de manobras no mesmo arquivo; quem tem as duas ganha o de magias em <saida>.jpg e o
de manobras em <saida>-manobras.jpg. Sem nenhuma das duas, nao gera nada e avisa.

No grimorio de manobras os cabecalhos impressos (Tempo, Duracao, Custos) sao cobertos e
reescritos: Uso, Dano, Mod., Alcance. A grade e a mesma.

No grimorio de manobras cada manobra pode ter uma `descricao` (texto ou lista de ate 3
linhas): ela ocupa as linhas logo abaixo da manobra, com as celulas mescladas (a grade
vertical e apagada nessas linhas) e escreve-se de uma ponta a outra da folha. Texto corrido
e quebrado sozinho em, no maximo, 3 linhas; o que passar disso e cortado com reticencias.
Uma manobra nunca e partida entre duas paginas, e uma linha em branco separa cada manobra
da seguinte.

Cabem 45 linhas por pagina. Havendo mais, sao geradas paginas extras com sufixo
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

from preencher_ficha import draw_field, font  # mesma fonte manuscrita e mesmo encolhimento

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


# ---------------------------------------------------------------------------
# Grimorio de manobras: os cabecalhos da folha sao de magia. Cobre-se a faixa de
# cabecalho (acima da primeira regra, y=325) e reescreve-se com os da manobra.
# ---------------------------------------------------------------------------
CABECALHO_BOX = (150, 228, 2327, 316)   # x0, y0, x1, y1 — so o texto, sem as regras
CABECALHO_Y = 306                       # baseline dos novos rotulos
CABECALHO = {                           # campo: texto
    "nome": "Manobra (perícia que a controla)",
    "nh": "NH",
    "tempo": "Uso",
    "duracao": "Dano",
    "custo_fazer": "Mod. ataque",
    "custo_manter": "Alcance",
    "obs": "Efeito, em resumo",
    "pag": "Pág.",
}
TITULAR_MANOBRAS = "{nome} — manobras"

# Descricao da manobra: ate 3 linhas, de uma ponta a outra da folha (celulas mescladas).
DESC_X = 170
DESC_SIZE = 26
DESC_LARGURA = 2120          # da margem esquerda ate perto da moldura direita
DESC_MAX_LINHAS = 3
DESC_BRANCO = (150, 2326)    # x0, x1 da faixa que apaga os divisores verticais


def manobras_de(data):
    """As manobras do personagem: entradas de `pericias` com categoria «Manobras», na
    ordem em que estao, em linhas prontas para as colunas do formulario."""
    saida = []
    for per in data.get("pericias") or []:
        if (per.get("categoria") or "").strip().lower() != "manobras":
            continue
        nome = per.get("nome") or ""
        controle = (per.get("tipo") or "").split("/")[0].strip()
        saida.append({
            "nome": nome,
            # a perícia que controla vira «(Judô)», salvo se o nome já a traz: «Finta (Katana)»
            "classe": "" if "(" in nome else controle,
            "nh": per.get("nh"),
            "tempo": per.get("uso"),
            "duracao": per.get("dano"),
            "custo_fazer": per.get("mod"),
            "custo_manter": per.get("alcance"),
            "obs": per.get("obs"),
            "pag": per.get("pag"),
            "descricao": per.get("descricao"),
            "categoria": controle,            # uma arte por bloco, com linha em branco
        })
    # Uma arte por bloco, na ordem em que cada uma aparece pela primeira vez; dentro do
    # bloco, a ordem original (que e a da ficha, do NH maior para o menor).
    ordem = {}
    for m in saida:
        ordem.setdefault(m["categoria"], len(ordem))
    return sorted(saida, key=lambda m: ordem[m["categoria"]])


def quebrar_descricao(texto):
    """Devolve ate DESC_MAX_LINHAS linhas. Lista vem pronta; texto corrido e quebrado por
    palavras na largura da folha, e o excesso e cortado com reticencias."""
    if not texto:
        return []
    if isinstance(texto, (list, tuple)):
        linhas = [str(t).strip() for t in texto if str(t).strip()]
    else:
        f = font(DESC_SIZE)
        medir = ImageDraw.Draw(Image.new("RGB", (10, 10))).textlength
        linhas, atual = [], ""
        for palavra in str(texto).split():
            cand = f"{atual} {palavra}".strip()
            if atual and medir(cand, font=f) > DESC_LARGURA:
                linhas.append(atual)
                atual = palavra
            else:
                atual = cand
        if atual:
            linhas.append(atual)
    if len(linhas) > DESC_MAX_LINHAS:
        print(f"Aviso: descricao com {len(linhas)} linhas, cortada em {DESC_MAX_LINHAS}.")
        linhas = linhas[:DESC_MAX_LINHAS]
        linhas[-1] = linhas[-1].rstrip(" .,;") + "…"
    return linhas


def montar_blocos(itens, eh_manobra=False):
    """Agrupa as linhas em blocos que nao se partem entre paginas: cada item e um bloco
    (a manobra com as linhas da descricao logo abaixo). Uma linha em branco separa cada
    manobra da seguinte; nas magias, ela so separa as escolas."""
    blocos = []
    cat_anterior = None
    for m in itens:
        cat = m.get("categoria")
        # manobras: uma linha em branco depois de CADA manobra; magias: so na troca de escola
        if blocos and (eh_manobra or (cat_anterior is not None and cat != cat_anterior)):
            blocos.append([None])
        bloco = [m]
        if eh_manobra:
            bloco += [{"_desc": t} for t in quebrar_descricao(m.get("descricao"))]
        blocos.append(bloco)
        cat_anterior = cat
    return blocos


def paginar(blocos, por_pagina):
    """Fatia os blocos em paginas, sem partir um bloco e sem abrir pagina com separador."""
    paginas, atual = [], []
    for bloco in blocos:
        if bloco == [None] and not atual:
            continue  # nao abre pagina com linha em branco
        if atual and len(atual) + len(bloco) > por_pagina:
            while atual and atual[-1] is None:
                atual.pop()
            paginas.append(atual)
            atual = []
            if bloco == [None]:
                continue
        atual.extend(bloco)
    if atual:
        paginas.append(atual)
    return paginas


def rotulo_magia(m):
    """'Nome (Classe)' — a coluna impressa pede nome e classe juntos."""
    nome = (m.get("nome") or "").strip()
    classe = (m.get("classe") or "").strip()
    return f"{nome} ({classe})" if classe else nome


def desenhar_pagina(template, titular, linhas, manobras=False):
    img = Image.open(template).convert("RGB")
    draw = ImageDraw.Draw(img)
    if manobras:
        draw.rectangle(CABECALHO_BOX, fill=(255, 255, 255))
        for campo, texto in CABECALHO.items():
            x, size, align, largura = COLUNAS[campo]
            draw_field(draw, (x, CABECALHO_Y, 26, align, largura), texto)
        titular = TITULAR_MANOBRAS.format(nome=titular)
    draw_field(draw, TITULAR, titular)

    for i, m in enumerate(linhas[: LINHAS["max_rows"]]):
        if m is None:
            continue
        y = int(LINHAS["start_baseline"] + i * LINHAS["row_h"])
        if "_desc" in m:
            # celula mesclada: apaga os divisores verticais entre as duas regras da linha
            topo = int(LINHAS["start_baseline"] + i * LINHAS["row_h"] - 52)
            base = int(LINHAS["start_baseline"] + i * LINHAS["row_h"] + 5)
            draw.rectangle((DESC_BRANCO[0], topo, DESC_BRANCO[1], base), fill=(255, 255, 255))
            draw_field(draw, (DESC_X, y, DESC_SIZE, "left", DESC_LARGURA), m["_desc"])
            continue
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
    manobras = manobras_de(data)
    if not magias and not manobras:
        print("Personagem sem magias nem manobras: grimorio nao gerado.")
        return

    titular = data.get("nome", "")
    out = Path(args.output)

    # (linhas do grupo, e-manobras?, arquivo base)
    grupos = []
    if magias:
        grupos.append((magias, False, out))
    if manobras:
        # quem so tem manobras usa o proprio arquivo do grimorio; com magias tambem, vai ao lado
        base = out if not magias else out.with_name(f"{out.stem}-manobras{out.suffix}")
        grupos.append((manobras, True, base))

    for itens, eh_manobra, base in grupos:
        paginas = paginar(montar_blocos(itens, eh_manobra), LINHAS["max_rows"])
        for n, linhas in enumerate(paginas, start=1):
            destino = base if n == 1 else base.with_name(f"{base.stem}-{n}{base.suffix}")
            salvar(desenhar_pagina(args.template, titular, linhas, eh_manobra), destino)
            print(f"Grimorio {'de manobras ' if eh_manobra else ''}gerado em: {destino}")
        if len(paginas) > 1:
            print(f"{len(itens)} {'manobras' if eh_manobra else 'magias'} em "
                  f"{len(paginas)} paginas.")


if __name__ == "__main__":
    main()
