#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calcular-alcance — quantos hexágonos, quantos metros, e de que lado.

O mapa é o do roll6: hexágonos flat-top, colunas ímpares deslocadas meia célula para
baixo ("odd-q"), posição = (`x` coluna, `y` linha) desde 0, e frente (`look`) de 0 a 5
começando no topo, no sentido horário: 0 topo, 1 canto-direito-cima, 2 canto-direito-baixo,
3 baixo, 4 canto-esquerdo-baixo, 5 canto-esquerdo-cima.

    calcular_alcance.py --de Q30 --para P11 --frente 3
    calcular_alcance.py --de 16,29 --para 15,6
    python .../roll6.py chamar list_map_tokens '{"campaignId":1,"mapId":2}' \
      | calcular_alcance.py --tokens - --de "Comam Obabaroy" --para "Morto 5"

Devolve a distância em hexágonos e em metros (1 hexágono = 1 m), a linha da tabela de
escala que o modificador de velocidade/distância vai usar, o lado em que o alvo está a
partir de quem atira, e se ele está ou não no ângulo de visão. Não rola dado, não resolve
defesa nem dano, não escreve em lugar nenhum, e não fala com o roll6: recebe as posições.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
ESCALA_PY = SKILLS / "atacar-distancia" / "scripts" / "tabelas_distancia.py"

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# A escala de distância é da arma de longe; esta folha conta hexágonos, não reinventa tabela.
try:
    _espec = importlib.util.spec_from_file_location("tabelas_distancia", ESCALA_PY)
    _td = importlib.util.module_from_spec(_espec)
    _espec.loader.exec_module(_td)
except Exception as erro:                                  # nunca derruba quem chamou
    print(f"calcular-alcance: sem a tabela de escala ({ESCALA_PY}): {erro}")
    _td = None

METRO_POR_HEX = 1.0

# look -> (dx, dy) numa coluna PAR. Em coluna ímpar o topo/baixo são iguais, mas os
# cantos vão uma linha mais fundo (porque a coluna ímpar está meio hexágono mais baixa).
LOOK_PAR = {0: (0, -1), 1: (+1, -1), 2: (+1, 0), 3: (0, +1), 4: (-1, 0), 5: (-1, -1)}
LOOK_IMPAR = {0: (0, -1), 1: (+1, 0), 2: (+1, +1), 3: (0, +1), 4: (-1, +1), 5: (-1, 0)}
NOME_LOOK = {0: "topo (N)", 1: "canto direito cima (NE)", 2: "canto direito baixo (SE)",
             3: "baixo (S)", 4: "canto esquerdo baixo (SO)", 5: "canto esquerdo cima (NO)"}


def para_xy(pos, desloc=(0, 0)):
    """Aceita rótulo ('P7'), dupla ('15,6') ou lista [15,6] -> (x, y)."""
    if isinstance(pos, (list, tuple)):
        return int(pos[0]) + desloc[0], int(pos[1]) + desloc[1]
    t = str(pos).strip()
    m = re.fullmatch(r"([A-Za-z]+)(\d+)", t)
    if m:
        col = 0
        for ch in m.group(1).upper():
            col = col * 26 + (ord(ch) - 64)
        return col - 1 + desloc[0], int(m.group(2)) - 1 + desloc[1]
    m = re.fullmatch(r"(-?\d+)\s*,\s*(-?\d+)", t)
    if m:
        return int(m.group(1)) + desloc[0], int(m.group(2)) + desloc[1]
    raise ValueError(f"posição não entendida: {pos!r} (use rótulo 'P7' ou 'x,y')")


def para_rotulo(x, y, desloc=(0, 0)):
    col, letras = x - desloc[0] + 1, ""
    while col > 0:
        col, resto = divmod(col - 1, 26)
        letras = chr(65 + resto) + letras
    return f"{letras}{y - desloc[1] + 1}"


def vizinho(x, y, look):
    """A casa vizinha olhando para `look` — o que o roll6 usa para mover 1 hexágono."""
    tabela = LOOK_IMPAR if (x & 1) else LOOK_PAR
    dx, dy = tabela[look]
    return x + dx, y + dy


def _cubo(x, y):
    """odd-q -> cubo. s = x//2 é o quanto a coluna já desceu."""
    q = x
    r = y - (x // 2)
    return q, r, -q - r


def hexes_entre(a, b):
    """Distância em hexágonos entre duas casas."""
    ax, ay, az = _cubo(*a)
    bx, by, bz = _cubo(*b)
    return max(abs(ax - bx), abs(ay - by), abs(az - bz))


# Direções em cubo, derivadas das mesas de vizinho acima (paridade par, que é a base).
DIR_CUBO = {0: (0, -1, 1), 1: (1, -1, 0), 2: (1, 0, -1),
            3: (0, 1, -1), 4: (-1, 1, 0), 5: (-1, 0, 1)}


def look_de(a, b, com_empate=False):
    """O lado em que B está visto de A — o RUMO, não o último passo do caminho.

    Para casa vizinha coincide com a mesa de vizinhos; para casa distante escolhe o cone
    cúbico mais alinhado, e por isso o lado de lá é sempre o oposto do lado de cá.

    Em odd-q não existe "leste": alvo na linha exata entre dois cones empata. O empate não
    é decidido em silencio — `com_empate=True` devolve os dois lados possiveis.
    """
    if a == b:
        return (None, None) if com_empate else None
    ax, ay, az = _cubo(*a)
    bx, by, bz = _cubo(*b)
    dq, dr, ds = bx - ax, by - ay, bz - az
    notas = sorted(((dq * cq + dr * cr + ds * cs, lk)
                    for lk, (cq, cr, cs) in DIR_CUBO.items()), reverse=True)
    empate = len(notas) > 1 and notas[0][0] == notas[1][0]
    if com_empate:
        return notas[0][1], (notas[1][1] if empate else None)
    return notas[0][1]


def rela_frente(frente, lado):
    """Frente de quem atira vs. o lado em que o alvo está: frontal / lateral / por trás."""
    if frente is None or lado is None:
        return None
    giro = (lado - frente) % 6
    return {0: "frontal", 1: "lateral direita", 5: "lateral esquerda",
            2: "na traseira direita", 4: "na traseira esquerda",
            3: "por trás"}.get(giro), giro


def calcular(p):
    a = p.get("de")
    b = p.get("para")
    if a is None or b is None:
        raise SystemExit("Diga as duas casas: --de e --para (rótulo, 'x,y' ou lista).")
    desloc = tuple(p.get("desloc") or (0, 0))
    pa = a if isinstance(a, tuple) else para_xy(a, desloc)
    pb = b if isinstance(b, tuple) else para_xy(b, desloc)

    n = hexes_entre(pa, pb)
    metros = n * float(p.get("metro_por_hex") or METRO_POR_HEX)
    lado, lado_alt = look_de(pa, pb, com_empate=True)
    res = {
        "de": {"xy": list(pa), "rotulo": para_rotulo(pa[0], pa[1], desloc)},
        "para": {"xy": list(pb), "rotulo": para_rotulo(pb[0], pb[1], desloc)},
        "hexagonos": n, "metros": metros,
        "lado": lado, "lado_nome": NOME_LOOK.get(lado),
        "mesma_casa": n == 0,
    }
    if lado_alt is not None:
        # alvo exatamente entre dois cones: a mesa escolhe, a folha nao decide escondido
        res["lado_ambiguo"] = [lado, lado_alt]
        res["aviso_lado"] = (f"na linha exata entre {NOME_LOOK[lado]} e {NOME_LOOK[lado_alt]}"
                             " — odd-q não tem 'leste'; arbitre o lado")
    rel = rela_frente(p.get("frente"), lado)
    if rel:
        res["angulo_visao"], res["giro"] = rel
        res["fora_do_angulo"] = res["angulo_visao"].startswith("por tr") or \
            res["angulo_visao"].startswith("na tras")
    if _td and n:
        mod, medida = _td.mod_velocidade_distancia(metros)
        res["linha_tabela"] = medida
        res["mod_velocidade_distancia"] = mod
    elif not _td and n:
        res["aviso"] = ("sem a tabela de escala de atacar-distancia: devolvo hexágonos e "
                        "metros, mas não o modificador")
    return res


def _das_tokens(p):
    """Resolve nomes (ou ids de peça) contra a saída de list_map_tokens."""
    tokens = p.get("tokens")
    if not tokens:
        return p.get("de"), p.get("para")
    lista = tokens if isinstance(tokens, list) else (tokens.get("items") or [])
    def casa(alvo):
        for t in lista:
            if str(t.get("name", "")).strip().casefold() == str(alvo).strip().casefold():
                return (t["x"], t["y"])
            if str(t.get("mapTokenId", "")) == str(alvo):
                return (t["x"], t["y"])
        raise SystemExit(f"nenhuma peça chamada {alvo!r} no list_map_tokens (ou o nome "
                         "está grafado diferente no roll6)")
    return casa(p.get("de")), casa(p.get("para"))


def main():
    ap = argparse.ArgumentParser(description="Distância em hexágonos no mapa do roll6.")
    ap.add_argument("--de", required=True, help="rótulo (P7), 'x,y', ou nome da peça c/ --tokens")
    ap.add_argument("--para", required=True)
    ap.add_argument("--frente", type=int, default=None, choices=range(6),
                    help="look de quem atira (0=topo, horário)")
    ap.add_argument("--metro-por-hex", type=float, default=METRO_POR_HEX)
    ap.add_argument("--desloc-x", type=int, default=0)
    ap.add_argument("--desloc-y", type=int, default=0)
    ap.add_argument("--tokens", default="", help="JSON do list_map_tokens, ou '-' p/ stdin")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    tokens = None
    if a.tokens:
        tokens = sys.stdin.read() if a.tokens == "-" else Path(a.tokens).read_text(encoding="utf-8")
        tokens = json.loads(tokens)
    de, para = _das_tokens({"tokens": tokens, "de": a.de, "para": a.para})
    r = calcular({"de": de, "para": para, "frente": a.frente,
                  "metro_por_hex": a.metro_por_hex,
                  "desloc": (a.desloc_x, a.desloc_y)})
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"{r['de']['rotulo']} {tuple(r['de']['xy'])} → {r['para']['rotulo']} "
          f"{tuple(r['para']['xy'])}")
    print(f"  {r['hexagonos']} hexágonos = {r['metros']:g} m"
          + (f"  · linha da tabela: {r.get('linha_tabela'):g} m, mod {r.get('mod_velocidade_distancia'):+d}"
             if r.get("linha_tabela") is not None else ""))
    if r.get("lado_nome"):
        print(f"  o alvo está a {r['lado_nome']}")
    if r.get("angulo_visao"):
        print(f"  em relação à frente informada: {r['angulo_visao']} (giro {r['giro']})"
              + (" — FORA do ângulo de visão" if r.get("fora_do_angulo") else ""))


if __name__ == "__main__":
    main()
