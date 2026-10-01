#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preenche a Planilha do Personagem (GURPS 3ed) a partir de um JSON de dados
e gera uma imagem final (JPEG/PNG), simulando preenchimento a mao.

Uso:
    python preencher_ficha.py --data personagem.json --template ficha-de-personagem.jpg --output saida.jpg

O JSON de entrada segue o esquema descrito em SKILL.md (secao "Esquema do JSON").

Notas de implementacao:
- Todas as coordenadas Y sao *baselines* (a linha onde o texto "senta"), medidas por
  analise de pixel sobre o formulario em branco (2481x3508 px). Isso permite trocar a
  fonte ou aumentar o corpo sem desalinhar nada: o texto cresce para cima a partir da linha.
- A fonte padrao e manuscrita (Segoe Script). Campos com largura limitada encolhem
  automaticamente ate caber (max_width).
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Fontes — manuscritas, com fallback
# ---------------------------------------------------------------------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\segoesc.ttf",    # Segoe Script (manuscrita, inclinada)
    r"C:\Windows\Fonts\segoepr.ttf",    # Segoe Print
    r"C:\Windows\Fonts\Inkfree.ttf",    # Ink Free
    r"C:\Windows\Fonts\comic.ttf",      # Comic Sans MS
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]
FONT_BOLD_CANDIDATES = [
    r"C:\Windows\Fonts\segoescb.ttf",   # Segoe Script Bold
    r"C:\Windows\Fonts\segoeprb.ttf",   # Segoe Print Bold
    r"C:\Windows\Fonts\comicbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
]

_font_cache = {}


def font(size, bold=False):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    for path in (FONT_BOLD_CANDIDATES if bold else FONT_CANDIDATES):
        if Path(path).exists():
            try:
                f = ImageFont.truetype(path, size=size)
                _font_cache[key] = f
                return f
            except Exception:
                continue
    f = ImageFont.load_default()
    _font_cache[key] = f
    return f


COLOR = (15, 15, 20)

# ---------------------------------------------------------------------------
# Mapa de campos. Formato: (x, baseline_y, size[, align[, max_width]])
#   align: "left" (padrao) ou "center"
# Coordenadas calibradas por analise de pixel sobre ficha-de-personagem.jpg.
# ---------------------------------------------------------------------------
HEADER = {
    "nome": (295, 220, 34, "left", 1000),
    "jogador": (1425, 218, 30, "left", 360),
    "aparencia": (385, 285, 30, "left", 1380),
    "historia": (370, 352, 30, "left", 1400),
    "data_criacao": (1959, 252, 26, "center", 245),
    "sequencia": (2193, 252, 26, "center", 155),
    "pontos_gastar": (1959, 375, 28, "center", 245),
    "pontos_total": (2193, 375, 28, "center", 155),
}

ATTR_BOXES = {
    "ST": {"value": (415, 508, 62), "cost": (117, 582, 30, "center", 75)},
    "DX": {"value": (415, 693, 62), "cost": (117, 760, 30, "center", 75)},
    "IQ": {"value": (415, 868, 62), "cost": (117, 938, 30, "center", 75)},
    "HT": {"value": (415, 1053, 62), "cost": (117, 1120, 30, "center", 75)},
}

DERIVED = {
    "fadiga": (650, 537, 40, "center", 200),
    "pontos_vida": (650, 1072, 40, "center", 200),
    "gdp": (670, 810, 32, "left", 140),
    "bal": (660, 895, 32, "left", 140),
    "velocidade_basica": (528, 1254, 32, "center", 165),
    "deslocamento": (705, 1254, 32, "center", 160),
}

CARGA_LINES = {
    "nenhuma": (495, 1486, 28, "left", 90),
    "leve": (520, 1548, 28, "left", 90),
    "media": (520, 1608, 28, "left", 90),
    "pesada": (520, 1671, 28, "left", 90),
    "muito_pesada": (505, 1734, 28, "left", 90),
}

DEFESA_PASSIVA = {
    "armadura": (737, 1517, 28, "center", 70),
    "escudo": (732, 1586, 28, "center", 70),
    "total": (715, 1718, 36, "center", 120),
}

DEFESAS_ATIVAS = {
    "esquiva": (290, 1927, 32, "center", 170),
    "aparar": (495, 1927, 32, "center", 170),
    "bloqueio": (700, 1927, 32, "center", 170),
}

REACAO = (1130, 1714, 30, "left", 440)

VANTAGENS = {
    "start_baseline": 2140, "row_h": 55, "max_rows": 15,
    "cost_x": 120, "cost_size": 26, "cost_w": 70,
    "desc_x": 212, "desc_size": 28, "desc_w": 430,
}

PECULIARIDADES = {
    "start_baseline": 3105, "row_h": 55, "max_rows": 5,
    "cost_x": 120, "cost_size": 26, "cost_w": 70,
    "desc_x": 212, "desc_size": 28, "desc_w": 430,
}

ARMAS = {
    "start_baseline": 1946, "row_h": 55, "max_rows": 24,
    # centros das colunas conforme o cabecalho impresso (Item/Dano/Tipo/Qtd./Peso)
    "item_x": 835, "item_size": 27, "item_w": 305,
    "dano_x": 1200, "dano_size": 25, "dano_w": 115,
    "tipo_x": 1338, "tipo_size": 25, "tipo_w": 135,
    "qtd_x": 1450, "qtd_size": 25, "qtd_w": 55,
    "peso_x": 1551, "peso_size": 25, "peso_w": 95,
}
TOTAIS_CUSTO = (1130, 3349, 30, "center", 200)
TOTAIS_KG = (1330, 3349, 30, "center", 130)

PERICIAS = {
    "start_baseline": 520, "row_h": 55, "max_rows": 44,
    "name_x": 1668, "name_size": 28, "name_w": 390,
    "nh_x": 2118, "nh_size": 27, "nh_w": 70,
    "tipo_x": 2228, "tipo_size": 25, "tipo_w": 100,
    "custo_x": 2344, "custo_size": 26, "custo_w": 60,
}

# Quadro do retrato do personagem (area interna, ja descontadas as bordas do formulario)
FOTO_BOX = (827, 426, 1611, 1595)
FOTO_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
FOTO_PREFERIDOS = ("foto", "retrato", "imagem", "portrait")

RESUMO = {
    "atributos": (2080, 3103, 30, "center", 300),
    "vantagens": (2080, 3155, 30, "center", 300),
    "desvantagens": (2080, 3207, 30, "center", 300),
    "peculiaridades": (2080, 3255, 30, "center", 300),
    "pericias": (2080, 3307, 30, "center", 300),
    "total": (2160, 3375, 36, "center", 260),
}


# ---------------------------------------------------------------------------
MIN_SIZE = 20  # abaixo disso a letra manuscrita fica ilegivel: melhor truncar


def draw_field(draw, spec, text, bold=False):
    """Desenha `text` conforme spec = (x, baseline_y, size[, align[, max_width]]).

    Se o texto nao couber em max_width, a fonte encolhe ate MIN_SIZE; se ainda assim
    nao couber, o texto e truncado com reticencias (mantendo a legibilidade).
    """
    if text is None:
        return
    if isinstance(text, float):  # notacao decimal em portugues: 2.5 -> 2,5
        text = f"{text:g}".replace(".", ",")
    text = str(text).strip()
    if not text:
        return
    x, y, size = spec[0], spec[1], spec[2]
    align = spec[3] if len(spec) > 3 else "left"
    max_width = spec[4] if len(spec) > 4 else None

    f = font(size, bold)
    if max_width:
        s = size
        while s > MIN_SIZE and draw.textlength(text, font=f) > max_width:
            s -= 1
            f = font(s, bold)
        while len(text) > 4 and draw.textlength(text, font=f) > max_width:
            text = text[:-2] + "…" if not text.endswith("…") else text[:-2] + "…"
    anchor = "ls" if align == "left" else "ms"
    draw.text((x, y), text, fill=COLOR, font=f, anchor=anchor)


def achar_foto(pasta: Path, saida: Path):
    """Procura uma imagem de retrato na pasta do personagem.

    Ignora o proprio arquivo de saida e qualquer coisa chamada 'ficha*'. Prefere nomes
    como foto/retrato/imagem; caso contrario, usa a primeira imagem em ordem alfabetica.
    """
    candidatos = []
    for f in sorted(pasta.iterdir()):
        if not f.is_file() or f.suffix.lower() not in FOTO_EXTS:
            continue
        if f.resolve() == saida.resolve() or f.stem.lower().startswith("ficha"):
            continue
        candidatos.append(f)
    if not candidatos:
        return None
    for pref in FOTO_PREFERIDOS:
        for f in candidatos:
            if f.stem.lower().startswith(pref):
                return f
    return candidatos[0]


def colar_foto(img, foto_path: Path):
    """Preenche todo o quadro do retrato, preservando a proporcao e cortando o excesso."""
    x0, y0, x1, y1 = FOTO_BOX
    box_w, box_h = x1 - x0, y1 - y0
    foto = Image.open(foto_path)
    if foto.mode not in ("RGB", "RGBA"):
        foto = foto.convert("RGBA" if "A" in foto.mode else "RGB")

    escala = max(box_w / foto.width, box_h / foto.height)
    novo = (max(1, int(foto.width * escala)), max(1, int(foto.height * escala)))
    foto = foto.resize(novo, Image.LANCZOS)

    esquerda = (foto.width - box_w) // 2
    topo = (foto.height - box_h) // 2
    foto = foto.crop((esquerda, topo, esquerda + box_w, topo + box_h))

    if foto.mode == "RGBA":
        img.paste(foto.convert("RGB"), (x0, y0), foto.split()[-1])
    else:
        img.paste(foto, (x0, y0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="JSON com os dados do personagem")
    ap.add_argument("--template", required=True, help="Imagem em branco da ficha (jpg)")
    ap.add_argument("--output", required=True, help="Caminho da imagem final")
    ap.add_argument("--foto", help="Retrato do personagem (padrao: detecta na pasta do JSON)")
    ap.add_argument("--sem-foto", action="store_true", help="Nao colar retrato")
    args = ap.parse_args()

    data_path = Path(args.data)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    img = Image.open(args.template).convert("RGB")

    # --- Retrato -----------------------------------------------------------
    if not args.sem_foto:
        foto_path = None
        if args.foto:
            foto_path = Path(args.foto)
        elif data.get("foto"):
            foto_path = (data_path.parent / data["foto"]).resolve()
        else:
            foto_path = achar_foto(data_path.parent, Path(args.output))
        if foto_path and foto_path.exists():
            try:
                colar_foto(img, foto_path)
                print(f"Retrato aplicado: {foto_path.name}")
            except Exception as e:
                print(f"Aviso: nao foi possivel usar o retrato {foto_path}: {e}")
        elif foto_path:
            print(f"Aviso: retrato nao encontrado em {foto_path}")

    draw = ImageDraw.Draw(img)

    # --- Cabecalho -------------------------------------------------------
    draw_field(draw, HEADER["nome"], data.get("nome"))
    draw_field(draw, HEADER["jogador"], data.get("jogador", "IA (GURPS)"))
    draw_field(draw, HEADER["aparencia"], data.get("aparencia"))
    draw_field(draw, HEADER["historia"], data.get("historia"))
    draw_field(draw, HEADER["data_criacao"], data.get("data_criacao"))
    draw_field(draw, HEADER["sequencia"], data.get("sequencia", "1"))
    draw_field(draw, HEADER["pontos_gastar"], data.get("pontos_gastar"))
    draw_field(draw, HEADER["pontos_total"], data.get("pontos_total"))

    # --- Atributos --------------------------------------------------------
    atributos = data.get("atributos", {})
    for attr, box in ATTR_BOXES.items():
        info = atributos.get(attr, {})
        draw_field(draw, box["value"], info.get("valor"), bold=True)
        draw_field(draw, box["cost"], info.get("custo"))

    # --- Derivados ---------------------------------------------------------
    draw_field(draw, DERIVED["fadiga"], data.get("fadiga"))
    draw_field(draw, DERIVED["pontos_vida"], data.get("pontos_vida"))
    dano = data.get("dano_basico", {})
    draw_field(draw, DERIVED["gdp"], dano.get("gdp"))
    draw_field(draw, DERIVED["bal"], dano.get("bal"))
    draw_field(draw, DERIVED["velocidade_basica"], data.get("velocidade_basica"))
    draw_field(draw, DERIVED["deslocamento"], data.get("deslocamento"))

    # --- Carga -------------------------------------------------------------
    carga = data.get("carga", {})
    for key, spec in CARGA_LINES.items():
        draw_field(draw, spec, carga.get(key))

    # --- Defesas ------------------------------------------------------------
    dp = data.get("defesa_passiva", {})
    for key, spec in DEFESA_PASSIVA.items():
        draw_field(draw, spec, dp.get(key), bold=(key == "total"))

    da = data.get("defesas_ativas", {})
    for key, spec in DEFESAS_ATIVAS.items():
        draw_field(draw, spec, da.get(key))

    draw_field(draw, REACAO, data.get("reacao"))

    # --- Vantagens / Desvantagens (grupos separados por uma linha em branco) ---
    itens = data.get("vantagens_desvantagens", [])
    # "lado" resolve o traco de custo 0 (adquirido em jogo), que o sinal nao separa
    def e_desvantagem(i):
        lado = (i.get("lado") or "").lower()
        if lado.startswith("desv"):
            return True
        if lado.startswith("vant"):
            return False
        return (i.get("custo") or 0) < 0

    vantagens = [i for i in itens if not e_desvantagem(i)]
    desvantagens = [i for i in itens if e_desvantagem(i)]
    linhas = list(vantagens)
    if vantagens and desvantagens:
        linhas.append(None)  # linha em branco separando os grupos
    linhas += desvantagens
    for i, item in enumerate(linhas[: VANTAGENS["max_rows"]]):
        if item is None:
            continue
        y = VANTAGENS["start_baseline"] + i * VANTAGENS["row_h"]
        draw_field(draw, (VANTAGENS["cost_x"], y, VANTAGENS["cost_size"], "center",
                          VANTAGENS["cost_w"]), item.get("custo"))
        draw_field(draw, (VANTAGENS["desc_x"], y, VANTAGENS["desc_size"], "left",
                          VANTAGENS["desc_w"]), item.get("nome"))

    # --- Peculiaridades -----------------------------------------------------
    pecs = data.get("peculiaridades", [])[: PECULIARIDADES["max_rows"]]
    for i, nome in enumerate(pecs):
        y = PECULIARIDADES["start_baseline"] + i * PECULIARIDADES["row_h"]
        draw_field(draw, (PECULIARIDADES["cost_x"], y, PECULIARIDADES["cost_size"], "center",
                          PECULIARIDADES["cost_w"]), -1)
        draw_field(draw, (PECULIARIDADES["desc_x"], y, PECULIARIDADES["desc_size"], "left",
                          PECULIARIDADES["desc_w"]), nome)

    # --- Armas e Objetos Pessoais (linha em branco a cada troca de categoria) --
    armas = []
    cat_anterior = None
    for item in data.get("armas_objetos", []):
        cat = item.get("categoria")
        if armas and cat_anterior is not None and cat != cat_anterior:
            armas.append(None)  # linha em branco entre categorias
        armas.append(item)
        cat_anterior = cat
    for i, arma in enumerate(armas[: ARMAS["max_rows"]]):
        if arma is None:
            continue
        y = ARMAS["start_baseline"] + i * ARMAS["row_h"]
        draw_field(draw, (ARMAS["item_x"], y, ARMAS["item_size"], "left", ARMAS["item_w"]),
                   arma.get("item"))
        draw_field(draw, (ARMAS["dano_x"], y, ARMAS["dano_size"], "center", ARMAS["dano_w"]),
                   arma.get("dano"))
        draw_field(draw, (ARMAS["tipo_x"], y, ARMAS["tipo_size"], "center", ARMAS["tipo_w"]),
                   arma.get("tipo"))
        draw_field(draw, (ARMAS["qtd_x"], y, ARMAS["qtd_size"], "center", ARMAS["qtd_w"]),
                   arma.get("qtd"))
        draw_field(draw, (ARMAS["peso_x"], y, ARMAS["peso_size"], "center", ARMAS["peso_w"]),
                   arma.get("peso"))
    custo_total = data.get("custo_total")
    if custo_total is not None:
        draw_field(draw, TOTAIS_CUSTO, f"$ {custo_total}")
    draw_field(draw, TOTAIS_KG, data.get("peso_total"))

    # --- Pericias (uma linha em branco a cada mudanca de categoria) ------------
    pericias = []
    cat_anterior = None
    for per in data.get("pericias", []):
        cat = per.get("categoria")
        if pericias and cat_anterior is not None and cat != cat_anterior:
            pericias.append(None)  # linha em branco entre categorias
        pericias.append(per)
        cat_anterior = cat
    # Magicas sao pericias, mas moram no grimorio: aqui entra so a linha de remissao.
    magias = data.get("magias") or []
    if magias:
        if pericias:
            pericias.append(None)
        pericias.append({
            "nome": f"Mágicas: {len(magias)} (ver grimório)",
            "nh": "—",
            "tipo": None,   # cada magica tem a sua dificuldade; nao cabe um tipo unico
            "custo": sum(m.get("custo") or 0 for m in magias),
        })
    for i, per in enumerate(pericias[: PERICIAS["max_rows"]]):
        if per is None:
            continue
        y = PERICIAS["start_baseline"] + i * PERICIAS["row_h"]
        draw_field(draw, (PERICIAS["name_x"], y, PERICIAS["name_size"], "left",
                          PERICIAS["name_w"]), per.get("nome"))
        draw_field(draw, (PERICIAS["nh_x"], y, PERICIAS["nh_size"], "center",
                          PERICIAS["nh_w"]), per.get("nh"))
        draw_field(draw, (PERICIAS["tipo_x"], y, PERICIAS["tipo_size"], "center",
                          PERICIAS["tipo_w"]), per.get("tipo"))
        draw_field(draw, (PERICIAS["custo_x"], y, PERICIAS["custo_size"], "center",
                          PERICIAS["custo_w"]), per.get("custo"))

    # --- Resumo ---------------------------------------------------------------
    resumo = data.get("resumo", {})
    for key, spec in RESUMO.items():
        draw_field(draw, spec, resumo.get(key), bold=(key == "total"))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() in (".jpg", ".jpeg"):
        img.save(out_path, quality=92)
    else:
        img.save(out_path)
    print(f"Ficha gerada em: {out_path}")


if __name__ == "__main__":
    main()
