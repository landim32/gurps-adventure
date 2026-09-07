#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sobrepoe um grid hexagonal de combate (GURPS 3ed: 1 hex = 1 metro) a uma arte
de cenario vista de cima, rotulando cada hexagono com coluna+linha (A1, C5, F2).

Uso tipico:
    python aplicar_grid.py --imagem taberna.png --saida taberna-grid.png --metros-largura 15

A escala pode vir de tres lugares, nesta ordem de precedencia:
    1. --metro-px          pixels por metro, direto
    2. --metros-largura    largura do cenario em metros
    3. o sidecar <imagem>.json ao lado da arte (campo "largura_m"), que e o que a
       skill cenario-rpg grava em cenario/apenas-imagem/

Geometria (topo chato, colunas verticais):
- No GURPS a direcao aponta para um *lado* do hexagono e cada figura tem 3 hexagonos
  frontais (MB, cap. 14). Com o topo chato, o "para frente" do token aponta para a
  aresta de cima, que e o que a skill token-hex-gurps assume.
- 1 hex = 1 metro = a distancia entre centros de hexagonos vizinhos, que e igual a
  distancia entre lados opostos (flat-to-flat). Todos os 6 vizinhos ficam a essa mesma
  distancia, entao "andar 1 hex" e sempre andar 1 metro, em qualquer direcao.
- Dai: circunraio R = metro_px / sqrt(3); colunas espacadas 1,5*R; linhas espacadas
  metro_px; colunas impares descem meia linha.

O grid sai translucido (padrao: 25% de opacidade) para nao competir com a arte.

Ao lado da imagem grava um JSON-indice (mesmo nome, .json) com o centro em pixels
de cada hexagono. A skill atualizar-mapa le esse indice para colar os tokens.
"""
import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

SQRT3 = math.sqrt(3.0)


def font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def rotulo_coluna(i):
    """0 -> A, 25 -> Z, 26 -> AA, 27 -> AB ..."""
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(ord("A") + r) + s
    return s


def cor_rgb(texto):
    t = texto.lstrip("#")
    if len(t) == 3:
        t = "".join(c * 2 for c in t)
    if len(t) != 6:
        raise ValueError(f"cor invalida: {texto}")
    return tuple(int(t[i:i + 2], 16) for i in (0, 2, 4))


def largura_do_sidecar(imagem: Path):
    """Le 'largura_m' do <imagem>.json gravado pela skill cenario-rpg, se existir."""
    lado = imagem.with_suffix(".json")
    if not lado.exists():
        return None
    try:
        dados = json.loads(lado.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"{lado.name} existe mas nao e um JSON valido: {e}")
    largura = dados.get("largura_m") or (dados.get("escala") or {}).get("largura_m")
    if largura is None:
        raise SystemExit(f'{lado.name} nao tem o campo "largura_m".')
    return float(largura)


def vertices(cx, cy, R):
    """Hexagono de topo chato: vertices a 0, 60, ..., 300 graus."""
    return [(cx + R * math.cos(math.radians(a)),
             cy + R * math.sin(math.radians(a))) for a in range(0, 360, 60)]


def listar_hexes(L, A, metro_px, origem):
    """Todos os hexagonos cujo circulo circunscrito toca a imagem.

    Devolve (lista, n_col, n_lin). A lista e a fonte unica para desenhar o grid
    e gravar o indice — os dois nao podem divergir.
    """
    R = metro_px / SQRT3          # circunraio
    dx = 1.5 * R                  # espacamento horizontal entre colunas
    dy = metro_px                 # espacamento vertical dentro de uma coluna
    ox, oy = origem
    n_col = int(math.ceil((L - ox) / dx)) + 1
    n_lin = int(math.ceil((A - oy) / dy)) + 1
    meia_altura = metro_px / 2.0  # flat-to-flat vertical / 2

    lista = []
    for c in range(n_col):
        cx = ox + c * dx
        desloc = (dy / 2.0) if (c % 2) else 0.0
        for r in range(n_lin):
            cy = oy + desloc + r * dy
            if cx + R < 0 or cx - R > L or cy + R < 0 or cy - R > A:
                continue
            lista.append({
                "rotulo": f"{rotulo_coluna(c)}{r + 1}",
                "coluna": c,
                "linha": r,
                "cx": round(cx, 2),
                "cy": round(cy, 2),
                "bbox": [
                    round(cx - R, 2),
                    round(cy - meia_altura, 2),
                    round(cx + R, 2),
                    round(cy + meia_altura, 2),
                ],
            })
    return lista, n_col, n_lin


def desenhar(img, hexes, metro_px, cor, opacidade, espessura, rotulos, tam_rotulo):
    R = metro_px / SQRT3
    alpha = max(0, min(255, int(round(opacidade * 255))))
    traco = cor + (alpha,)
    # O rotulo leva um contorno escuro fino em vez de mais opacidade: assim ele
    # continua legivel tanto na madeira clara quanto na pedra escura sem "pesar".
    texto = cor + (max(0, min(255, int(round(opacidade * 1.25 * 255)))),)
    contorno = (0, 0, 0, max(0, min(255, int(round(opacidade * 0.9 * 255)))))

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    f = font(tam_rotulo) if rotulos else None

    for h in hexes:
        draw.polygon(vertices(h["cx"], h["cy"], R), outline=traco, width=espessura)
        if rotulos:
            draw.text((h["cx"], h["cy"]), h["rotulo"], fill=texto, font=f,
                      anchor="mm", stroke_width=1, stroke_fill=contorno)

    return Image.alpha_composite(img.convert("RGBA"), overlay)


def ocupar_ainda_validos(indice_path, rotulos):
    """Reaplicar o grid nao pode apagar a mesa: conserva ocupacao cujo hex ainda existe."""
    if not indice_path.exists():
        return {}
    try:
        antigo = json.loads(indice_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    ocupacao = antigo.get("ocupacao") or {}
    return {k: v for k, v in ocupacao.items() if k in rotulos}


def gravar_indice(caminho, *, mapa, L, A, metro_px, origem, n_col, n_lin, hexes,
                  ocupacao):
    por_rotulo = {}
    for h in hexes:
        por_rotulo[h["rotulo"]] = {
            "coluna": h["coluna"],
            "linha": h["linha"],
            "cx": h["cx"],
            "cy": h["cy"],
            "bbox": h["bbox"],
        }
    dados = {
        "mapa": Path(mapa).name,
        "largura_px": L,
        "altura_px": A,
        "metro_px": round(metro_px, 4),
        "largura_m": round(L / metro_px, 3),
        "altura_m": round(A / metro_px, 3),
        "origem": [round(origem[0], 2), round(origem[1], 2)],
        "orientacao": "topo-chato",
        "colunas": n_col,
        "linhas": n_lin,
        "rotulo_colunas": f"A–{rotulo_coluna(n_col - 1)}" if n_col else "",
        "hexagonos_desenhados": len(hexes),
        "token_1hex_px": round(metro_px, 2),
        "hexagonos": por_rotulo,
        "ocupacao": ocupacao,
    }
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    return dados


def main():
    ap = argparse.ArgumentParser(
        description="Aplica grid hexagonal de 1 metro a uma arte de cenario top-down.")
    ap.add_argument("--imagem", required=True, help="Arte do cenario (jpg/png)")
    ap.add_argument("--saida", required=True, help="Imagem final com o grid")
    escala = ap.add_mutually_exclusive_group()
    escala.add_argument("--metros-largura", type=float,
                        help="Largura do cenario em metros (o script deriva px/m)")
    escala.add_argument("--metro-px", type=float,
                        help="Pixels por metro, se voce ja souber")
    ap.add_argument("--origem", default="0,0",
                    help="Centro do hex A1 em pixels, 'X,Y' (padrao 0,0)")
    ap.add_argument("--cor", default="#FFFFFF", help="Cor do grid (padrao branco)")
    ap.add_argument("--opacidade", type=float, default=0.25,
                    help="0 a 1 (padrao 0,25 — quase transparente)")
    ap.add_argument("--espessura", type=int, default=0,
                    help="Espessura do traco em px (padrao: 1 px a cada 45 px de hex)")
    ap.add_argument("--sem-rotulos", action="store_true", help="Nao escrever A1, B2...")
    ap.add_argument("--tamanho-rotulo", type=int, default=0,
                    help="Corpo do rotulo em px (padrao: 28%% do hex)")
    ap.add_argument("--indice", default="",
                    help="JSON do indice de hexagonos (padrao: o mesmo nome da "
                         "saida, com .json)")
    args = ap.parse_args()

    img = Image.open(args.imagem)
    L, A = img.size

    if args.metro_px:
        metro_px, fonte = args.metro_px, "--metro-px"
    elif args.metros_largura:
        metro_px, fonte = L / args.metros_largura, "--metros-largura"
    else:
        largura_m = largura_do_sidecar(Path(args.imagem))
        if largura_m is None:
            raise SystemExit(
                "Nao sei a escala. Passe --metros-largura (ou --metro-px), ou deixe um\n"
                f"{Path(args.imagem).with_suffix('.json').name} ao lado da arte com o campo "
                '"largura_m" (e o que a skill cenario-rpg grava).')
        metro_px, fonte = L / largura_m, "sidecar .json"

    if metro_px < 12:
        raise SystemExit(
            f"Hex de {metro_px:.1f} px: pequeno demais para caber um rotulo legivel. "
            "Use uma arte maior ou um cenario com menos metros.")

    try:
        ox, oy = (float(v) for v in args.origem.split(","))
    except Exception:
        raise SystemExit("--origem precisa ser 'X,Y' em pixels, ex.: --origem 40,60")

    tam = args.tamanho_rotulo or max(9, int(metro_px * 0.26))
    espessura = args.espessura or max(1, int(round(metro_px / 45)))

    hexes, n_col, n_lin = listar_hexes(L, A, metro_px, (ox, oy))
    final = desenhar(
        img, hexes, metro_px, cor_rgb(args.cor), args.opacidade,
        espessura, not args.sem_rotulos, tam)

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    if saida.suffix.lower() in (".jpg", ".jpeg"):
        final.convert("RGB").save(saida, quality=92)
    else:
        final.save(saida)

    indice = Path(args.indice) if args.indice else saida.with_suffix(".json")
    ocupacao = ocupar_ainda_validos(indice, {h["rotulo"] for h in hexes})
    gravar_indice(
        indice, mapa=saida, L=L, A=A, metro_px=metro_px, origem=(ox, oy),
        n_col=n_col, n_lin=n_lin, hexes=hexes, ocupacao=ocupacao)

    print(f"Imagem : {L}x{A} px")
    print(f"Escala : {metro_px:.1f} px/m ({fonte})  ->  "
          f"{L / metro_px:.1f} m x {A / metro_px:.1f} m")
    print(f"Grid   : {n_col} colunas (A..{rotulo_coluna(n_col - 1)}) x {n_lin} linhas, "
          f"{len(hexes)} hexagonos")
    if ocupacao:
        print(f"Ocupacao preservada: {len(ocupacao)} hex(es)")
    print(f"Cenario gerado em: {saida}")
    print(f"Indice gerado em : {indice}")


if __name__ == "__main__":
    main()
