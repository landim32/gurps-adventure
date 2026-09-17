#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O que `esboco.py` e `montar_pagina.py` tem em comum: ler o roteiro, achar onde cada
quadro cai na pagina em pixels e desenhar a moldura.

A pagina e A4 a 300 dpi (2480x3508) — a mesma medida da planilha de personagem do
repositorio, entao HQ e ficha imprimem no mesmo papel.

O roteiro (`roteiro.json`) e a fonte da verdade das tres skills da HQ:

    {
      "volume": "...", "campanha": "...", "capitulos": [1, 2],
      "estilo": "Digital illustration, fantasy RPG comic art, ...",
      "paginas": [
        {"n": 1, "titulo": "...", "quadros": [
          {"n": 1,
           "caixa": [0, 0, 100, 34],          # x, y, w, h em % da area util
           "enquadramento": "plano geral, da porta",
           "o_que_se_ve": "...",              # vira prompt na skill quadro-hq
           "elenco": ["comam-obabaroy", "hoel-meia-orelha"],
           "cenario": "campanha/plano/01-.../inicio.jpg",
           "arquivo": "quadros/p01q1.png",
           "figuras": [{"quem": "Comam", "em": [35, 78], "altura": 60,
                        "pose": "de pé", "olhando": "direita"}],
           "baloes": [{"tipo": "fala", "em": [30, 16], "apontando": [40, 55],
                       "quem": "Hoel", "texto": "..."}]}
        ]}
      ]
    }

`caixa` e opcional: sem ela os quadros da pagina entram numa grade automatica.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

SCRIPTS_BALOES = Path(__file__).resolve().parents[2] / "baloes-hq" / "scripts"
if str(SCRIPTS_BALOES) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_BALOES))
import baloes  # noqa: E402  (a skill baloes-hq e quem sabe desenhar balao)

PAGINA_PX = (2480, 3508)
MARGEM = 140          # branco em volta da mancha
CALHA = 34            # respiro entre quadros
ESPESSURA = 7         # traco da moldura

# Grades padrao por quantidade de quadros, em % da area util. Servem quando o roteiro
# nao declara `caixa` — e sao as divisoes que mais aparecem em HQ de 6 quadros.
GRADES = {
    1: [(0, 0, 100, 100)],
    2: [(0, 0, 100, 50), (0, 50, 100, 50)],
    3: [(0, 0, 100, 40), (0, 40, 50, 60), (50, 40, 50, 60)],
    4: [(0, 0, 50, 50), (50, 0, 50, 50), (0, 50, 50, 50), (50, 50, 50, 50)],
    5: [(0, 0, 100, 30), (0, 30, 50, 25), (50, 30, 50, 25),
        (0, 55, 50, 22), (0, 77, 100, 23)],
    6: [(0, 0, 50, 33), (50, 0, 50, 33), (0, 33, 50, 34), (50, 33, 50, 34),
        (0, 67, 50, 33), (50, 67, 50, 33)],
    7: [(0, 0, 100, 22), (0, 22, 33, 26), (33, 22, 34, 26), (67, 22, 33, 26),
        (0, 48, 50, 26), (50, 48, 50, 26), (0, 74, 100, 26)],
}


def carregar(caminho):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    if "paginas" not in dados:
        raise ValueError(f"{caminho}: roteiro sem a chave 'paginas'")
    return dados


def pasta_do_roteiro(caminho):
    return Path(caminho).resolve().parent


def resolver(caminho_rel, base, raiz):
    """Caminho do roteiro: primeiro relativo a pasta do volume, depois a raiz do
    projeto — assim `quadros/p01q1.png` e `campanha/plano/.../inicio.jpg` funcionam
    os dois no mesmo arquivo."""
    if not caminho_rel:
        return None
    p = Path(caminho_rel)
    if p.is_absolute():
        return p if p.exists() else None
    for cand in (base / p, Path(raiz) / p):
        if cand.exists():
            return cand
    return None


def area_util(roteiro):
    larg, alt = roteiro.get("pagina_px", PAGINA_PX)
    m = roteiro.get("margem_px", MARGEM)
    return m, m, larg - 2 * m, alt - 2 * m


def caixas(pagina, roteiro):
    """Devolve a caixa de cada quadro em pixels, ja descontada a calha."""
    ax, ay, aw, ah = area_util(roteiro)
    calha = roteiro.get("calha_px", CALHA)
    quadros = pagina.get("quadros", [])
    grade = GRADES.get(len(quadros))
    saida = []
    for i, q in enumerate(quadros):
        cx, cy, cw, ch = q.get("caixa") or (grade[i] if grade else (0, 0, 100, 100))
        x = ax + aw * cx / 100.0 + calha / 2
        y = ay + ah * cy / 100.0 + calha / 2
        w = aw * cw / 100.0 - calha
        h = ah * ch / 100.0 - calha
        saida.append((int(round(x)), int(round(y)), int(round(w)), int(round(h))))
    return saida


def nova_pagina(roteiro, fundo="#FFFFFF"):
    larg, alt = roteiro.get("pagina_px", PAGINA_PX)
    return Image.new("RGBA", (larg, alt), fundo)


def moldura(img, caixa, cor="#111111", esp=ESPESSURA):
    x, y, w, h = caixa
    ImageDraw.Draw(img).rectangle([x, y, x + w, y + h], outline=cor, width=esp)


def rodape(img, roteiro, pagina):
    larg, alt = img.size
    m = roteiro.get("margem_px", MARGEM)
    f = baloes.carregar_fonte("regular", 34)
    d = ImageDraw.Draw(img)
    esq = roteiro.get("volume", "")
    if esq:
        d.text((m, alt - m + 42), esq, font=f, fill="#777777")
    n = str(pagina.get("n", ""))
    d.text((larg - m - d.textlength(n, font=f), alt - m + 42), n, font=f,
           fill="#777777")


def paginas_pedidas(roteiro, quais):
    """--pagina 3 --pagina 5, ou nada para todas."""
    todas = roteiro["paginas"]
    if not quais:
        return todas
    alvo = {int(x) for x in quais}
    return [p for p in todas if int(p.get("n", 0)) in alvo]


def corpo_ref(roteiro):
    """A letra tem o mesmo tamanho na pagina inteira, venha de um quadro largo ou de
    um estreito. Metade da largura da pagina da um corpo de ~42 px em A4/300 dpi —
    perto dos 3,5 mm de altura de caixa alta que uma HQ impressa usa."""
    larg = roteiro.get("pagina_px", PAGINA_PX)[0]
    return roteiro.get("corpo_ref_px", larg / 2.0)


def desenhar_baloes(img, quadro, caixa, roteiro):
    ref = corpo_ref(roteiro)
    for b in quadro.get("baloes", []):
        baloes.desenhar(img, b, caixa=caixa, ref_px=ref)


def salvar(img, destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(destino, quality=95)
    return destino
