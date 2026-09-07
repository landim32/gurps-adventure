#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poe personagens e NPCs num mapa de cenario ja com grid, cada um no seu hexagono,
olhando para onde foi pedido, com aura azul (PJ) ou vermelha (NPC).

    python atualizar_mapa.py --indice cenarios/taberna3.json \
        --pj  "Comam Obabaroy em I5 olhando para H5" \
        --npc "lobo-negro em K7 olhando para I5"

Le o indice de hexagonos que add-grid-hex/aplicar_grid.py grava e escreve na mesma
chave `ocupacao`, so que com dois campos a mais: `tipo` (pj/npc) e `olhando` (o hex
alvo). Assim a mesa pode ser redesenhada do zero a qualquer momento.

A direcao vem do *hex alvo*, nao de um rumo cardinal: o script mede o angulo entre os
dois centros e encaixa na aresta mais proxima. Funciona com alvo distante — "olhando
para a porta" a 6 hexes de distancia da a mesma aresta que o vizinho naquela direcao.
"""
import argparse
import copy
import json
import math
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

CAMPANHA_PY = Path(".claude/skills/gerenciar-campanha/scripts/campanha.py")

# Token do acervo encara o sul (borda de baixo). PIL rotate e anti-horario.
GIRO_DESDE_SUL = {"S": 0, "SE": 60, "NE": 120, "N": 180, "NW": 240, "SW": 300}
# Rumo de cada aresta em coordenadas de tela (y cresce para baixo), em graus.
ARESTAS = {"N": -90.0, "NE": -30.0, "SE": 30.0, "S": 90.0, "SW": 150.0, "NW": -150.0}

COR_PJ = "#3B82F6"    # azul
COR_NPC = "#DC2626"   # vermelho

RE_PEDIDO = re.compile(
    r"^\s*(?P<quem>.+?)\s+em\s+(?P<hex>[A-Za-z]{1,3}\d{1,3})"
    r"(?:\s+olhando\s+(?:para\s+)?(?P<alvo>[A-Za-z]{1,3}\d{1,3}))?"
    r"(?:\s+ocupando\s+(?P<tam>\d+(?:[.,]\d+)?)\s*hex\w*)?\s*$",
    re.I)

OPOSTA = {"N": "S", "S": "N", "NE": "SW", "SW": "NE", "SE": "NW", "NW": "SE"}


def estado_da_campanha(raiz):
    """Pergunta a skill gerenciar-campanha onde estamos. Nunca cria campanha."""
    script = raiz / CAMPANHA_PY
    if not script.is_file():
        return {"ativa": False}
    # No Windows o filho escreveria na codificacao do console (cp1252) e o JSON viria
    # ilegivel; PYTHONIOENCODING obriga UTF-8 dos dois lados.
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        saida = subprocess.run(
            [sys.executable, str(script), "--raiz", str(raiz), "estado", "--json"],
            capture_output=True, text=True, encoding="utf-8", timeout=30, env=env)
        return json.loads(saida.stdout) if saida.returncode == 0 else {"ativa": False}
    except Exception:
        return {"ativa": False}


def destino_da_mesa(args, indice, dados, raiz):
    """Onde gravar a imagem: --saida manda; senao a pasta do capitulo atual; senao ao lado.

    Gravar na pasta do capitulo e o ponto de usar a campanha: o mapa da cena fica junto
    do texto da cena, em vez de solto em cenarios/.
    """
    nome = Path(dados["mapa"]).stem + "-mesa.png"
    if args.saida:
        return Path(args.saida), "--saida"
    est = estado_da_campanha(raiz)
    pasta = est.get("capitulo_atual_pasta")
    if est.get("ativa") and pasta and Path(pasta).is_dir():
        return Path(pasta) / nome, f"capítulo {est['capitulo_atual']} da campanha"
    if est.get("ativa"):
        return indice.parent / nome, ("campanha ativa, mas sem capítulo atual — use "
                                      "campanha.py atual --capitulo N")
    return indice.parent / nome, "sem campanha ativa"


def registrar_movimento(caminho, dados, acoes, ocupacao):
    """Acrescenta um passo ao historico de movimentacoes, para permitir rollback.

    Guarda a ocupacao *depois* de cada passo: voltar e so restaurar o instantaneo do
    passo desejado, sem ter que inverter operacao nenhuma.
    """
    if caminho.is_file():
        hist = json.loads(caminho.read_text(encoding="utf-8"))
    else:
        hist = {"mapa": dados["mapa"], "movimentos": []}
    hist["movimentos"].append({
        "n": len(hist["movimentos"]) + 1,
        "quando": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "acoes": acoes,
        "ocupacao": copy.deepcopy(ocupacao),
    })
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    return len(hist["movimentos"])


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")


def cor_rgb(txt):
    t = txt.lstrip("#")
    return tuple(int(t[i:i + 2], 16) for i in (0, 2, 4))


def achar_token(quem, tipo, raiz):
    """PJ: personagens/<slug>/token-hex.png. NPC: tokens/<slug>.png. Ou caminho direto."""
    p = Path(quem)
    if p.suffix and p.is_file():
        return p
    s = slug(quem)
    if tipo == "pj":
        alvo = raiz / "personagens" / s / "token-hex.png"
        if alvo.is_file():
            return alvo
        pastas = sorted(d.name for d in (raiz / "personagens").glob("*") if d.is_dir())
        raise SystemExit(
            f'Nao achei personagens/{s}/token-hex.png para "{quem}".\n'
            f"Pastas em personagens/: {', '.join(pastas) or '(nenhuma)'}\n"
            "Gere o token com a skill token-hex-gurps.")
    for cand in (raiz / "tokens" / f"{s}.png", raiz / "npcs" / f"{s}.png",
                 raiz / "npcs" / s / "token-hex.png"):
        if cand.is_file():
            return cand
    disponiveis = sorted(x.stem for x in (raiz / "tokens").glob("*.png"))
    raise SystemExit(
        f'Nao achei token de NPC para "{quem}" (tentei tokens/{s}.png).\n'
        f"No acervo: {', '.join(disponiveis[:12])}{'...' if len(disponiveis) > 12 else ''}")


def tamanho_catalogado(quem, tipo, raiz):
    """Quantos hexagonos a criatura ocupa, segundo tokens.json. Padrao 1.

    Tamanho e propriedade da criatura, nao da colocacao — por isso mora no catalogo
    (campo `hexes`) e nao no pedido. O MB, cap. 19, da os valores: urso em quatro
    patas, pantera, javali e asno = 2; cavalo = 3; lobo, cao e humano = 1; gato e
    simios pequenos = menos de 1.
    """
    if tipo == "pj":
        return 1.0
    cat = raiz / "tokens" / "tokens.json"
    if not cat.is_file():
        return 1.0
    try:
        dados = json.loads(cat.read_text(encoding="utf-8"))
    except Exception:
        return 1.0
    s = slug(quem)
    for t in dados.get("tokens", []):
        if Path(t.get("arquivo", "")).stem == s:
            return float(t.get("hexes") or 1)
    return 1.0


def aresta_para(hexes, origem, alvo):
    """Aresta do hexagono `origem` que aponta para o centro de `alvo`."""
    a, b = hexes[origem], hexes[alvo]
    dx, dy = b["cx"] - a["cx"], b["cy"] - a["cy"]
    if dx == 0 and dy == 0:
        return None
    ang = math.degrees(math.atan2(dy, dx))
    melhor, menor = None, 1e9
    for nome, rumo in ARESTAS.items():
        d = abs((ang - rumo + 180) % 360 - 180)
        if d < menor:
            melhor, menor = nome, d
    return melhor


def vizinho(hexes, rotulo, direcao, metro_px):
    """Hexagono adjacente na direcao dada, achado por projecao em pixels.

    Procurar pelo centro projetado em vez de somar coluna/linha evita todo o vexame
    de paridade do grid deslocado (colunas impares descem meia linha) — a geometria
    ja esta no indice, basta consultar.
    """
    a = hexes[rotulo]
    rad = math.radians(ARESTAS[direcao])
    px = a["cx"] + metro_px * math.cos(rad)
    py = a["cy"] + metro_px * math.sin(rad)
    melhor, menor = None, metro_px * 0.45
    for rot, h in hexes.items():
        d = math.hypot(h["cx"] - px, h["cy"] - py)
        if d < menor:
            melhor, menor = rot, d
    return melhor


def corpo_de(hexes, cabeca, frente, tamanho, metro_px):
    """Os hexagonos ocupados: a cabeca mais (tamanho-1) hexes para tras.

    MB, cap. 19: "o movimento de uma criatura que ocupa mais de um hex e controlado
    por sua cabeca... o resto do corpo segue a cabeca". Por isso o hexagono pedido e
    sempre o da cabeca, e o corpo se estende para o lado oposto ao que ela encara —
    e por isso um cavalo (3 hexes) fica com o cavaleiro no hexagono do meio.
    """
    ocupados = [cabeca]
    if tamanho <= 1:
        return ocupados, []
    atras = OPOSTA[frente or "S"]
    atual, faltando = cabeca, []
    for _ in range(int(math.ceil(tamanho)) - 1):
        prox = vizinho(hexes, atual, atras, metro_px)
        if prox is None:
            faltando.append(atras)
            break
        ocupados.append(prox)
        atual = prox
    return ocupados, faltando


def desenhar_aura(base, cx, cy, metro_px, cor, alpha=110):
    """Hexagono translucido sob a figura, alinhado ao grid (topo chato)."""
    R = metro_px / math.sqrt(3.0) * 0.94        # levemente encolhido, para nao vazar
    pontos = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
              for a in range(0, 360, 60)]
    camada = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(camada).polygon(pontos, fill=cor + (alpha,))
    camada = camada.filter(ImageFilter.GaussianBlur(max(1.0, metro_px * 0.06)))
    return Image.alpha_composite(base, camada)


def proporcao_ok(caminho, tamanho, minimo=0.8):
    """Quanto do comprimento declarado a arte consegue ocupar (1.0 = todo)."""
    if tamanho <= 1:
        return 1.0
    with Image.open(caminho) as im:
        w, h = im.size
    escala = min(tamanho / h, 1.15 / w)
    return (h * escala) / tamanho


def preparar_token(caminho, metro_px, frente, tamanho=1.0):
    """Escala o token para medir `tamanho` hexagonos no proprio comprimento.

    O token do acervo encara o sul, entao o comprimento da figura (cabeca->cauda) e o
    eixo *vertical* da imagem. Escalar pela altura e o que faz um cavalo de 3 hexes
    virar um corpo comprido de 3 m, em vez de um cavalo gordo de 1 hex.

    A largura tem teto: sem ele, uma arte quadrada declarada com 3 hexes viraria uma
    mancha de 3x3 hexagonos em cima dos vizinhos. Quando o teto e que manda, a figura
    fica mais curta do que o tamanho declarado — e ai `proporcao_ok` avisa que a arte
    nao tem a forma de uma criatura comprida.
    """
    img = Image.open(caminho).convert("RGBA")
    w, h = img.size
    comprimento = metro_px * tamanho
    largura_max = metro_px * (1.15 if tamanho > 1 else 1.0)
    escala = min(comprimento / h, largura_max / w)
    img = img.resize((max(1, round(w * escala)), max(1, round(h * escala))),
                     Image.Resampling.LANCZOS)
    if frente and GIRO_DESDE_SUL[frente]:
        img = img.rotate(GIRO_DESDE_SUL[frente], resample=Image.Resampling.BICUBIC,
                         expand=True)
    return img


def renderizar(dados, indice, saida, raiz, alpha):
    mapa = Path(dados["mapa"])
    if not mapa.is_file():
        mapa = indice.parent / dados["mapa"]
    base = Image.open(mapa).convert("RGBA")
    metro_px = dados["metro_px"]
    hexes = dados["hexagonos"]

    ocup = dados.get("ocupacao", {})
    # aura de todo mundo primeiro, para nenhuma passar por cima de figura vizinha
    for rot, o in ocup.items():
        cor = cor_rgb(o.get("cor") or (COR_PJ if o.get("tipo") == "pj" else COR_NPC))
        for r in o.get("hexes_ocupados") or [rot]:
            if r in hexes:
                base = desenhar_aura(base, hexes[r]["cx"], hexes[r]["cy"], metro_px,
                                     cor, alpha)
    n = 0
    for rot, o in ocup.items():
        if rot not in hexes:
            print(f"AVISO: {rot} nao existe neste grid — ignorei.")
            continue
        tok = Path(o["token"])
        if not tok.is_file():
            tok = raiz / o["token"]
        tam = float(o.get("tamanho_hex") or 1)
        img = preparar_token(tok, metro_px, o.get("frente") or "", tam)
        # centraliza no meio do corpo, nao na cabeca: assim a cabeca cai no hex pedido
        ocupados = [r for r in (o.get("hexes_ocupados") or [rot]) if r in hexes]
        cx = sum(hexes[r]["cx"] for r in ocupados) / len(ocupados)
        cy = sum(hexes[r]["cy"] for r in ocupados) / len(ocupados)
        camada = Image.new("RGBA", base.size, (0, 0, 0, 0))
        camada.paste(img, (int(round(cx - img.width / 2)),
                           int(round(cy - img.height / 2))), img)
        base = Image.alpha_composite(base, camada)
        n += 1

    saida.parent.mkdir(parents=True, exist_ok=True)
    if saida.suffix.lower() in (".jpg", ".jpeg"):
        base.convert("RGB").save(saida, quality=92)
    else:
        base.save(saida)
    return n


def main():
    ap = argparse.ArgumentParser(
        description="Poe PJs e NPCs num mapa com grid, com aura azul/vermelha.")
    ap.add_argument("--indice", required=True,
                    help="JSON de hexagonos gerado por add-grid-hex")
    ap.add_argument("--pj", action="append", default=[],
                    help='"Nome em I5 olhando para H5" (repetivel)')
    ap.add_argument("--npc", action="append", default=[],
                    help='"nome-do-token em K7 olhando para I5" (repetivel)')
    ap.add_argument("--remover", action="append", default=[], help="Tira o hex")
    ap.add_argument("--limpar", action="store_true", help="Esvazia o mapa")
    ap.add_argument("--saida", default="", help="Padrao: <mapa>-mesa.png")
    ap.add_argument("--raiz", default=".", help="Raiz do projeto")
    ap.add_argument("--alpha-aura", type=int, default=110, help="0-255 (padrao 110)")
    ap.add_argument("--movimentos", action="store_true",
                    help="Lista o historico de movimentacoes e sai")
    ap.add_argument("--desfazer", action="store_true", help="Volta um passo")
    ap.add_argument("--voltar", type=int, metavar="N",
                    help="Restaura o estado logo depois do passo N")
    args = ap.parse_args()

    indice = Path(args.indice)
    dados = json.loads(indice.read_text(encoding="utf-8"))
    if "hexagonos" not in dados:
        raise SystemExit(f"{indice} nao e um indice de add-grid-hex "
                         "(rode aplicar_grid.py no cenario primeiro).")
    raiz = Path(args.raiz).resolve()
    hexes = dados["hexagonos"]
    metro_px = dados["metro_px"]

    saida, motivo = destino_da_mesa(args, indice, dados, raiz)
    hist_path = saida.parent / (Path(dados["mapa"]).stem + "-movimentos.json")

    # --- historico: consultar e voltar atras -------------------------------
    if args.movimentos or args.desfazer or args.voltar is not None:
        if not hist_path.is_file():
            raise SystemExit(f"Ainda nao ha historico em {hist_path}.")
        hist = json.loads(hist_path.read_text(encoding="utf-8"))
        movs = hist["movimentos"]

        if args.movimentos:
            print(f"Historico: {hist_path}")
            for m in movs:
                print(f"  {m['n']:3d}. {m['quando']}  ({len(m['ocupacao'])} no mapa)")
                for a in m["acoes"]:
                    print(f"       {a}")
            return

        alvo = (len(movs) - 1) if args.desfazer else args.voltar
        if alvo < 0 or alvo > len(movs):
            raise SystemExit(f"Passo {alvo} nao existe (ha {len(movs)}).")
        dados["ocupacao"] = copy.deepcopy(movs[alvo - 1]["ocupacao"]) if alvo else {}
        indice.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        n = registrar_movimento(
            hist_path, dados,
            [f"voltou ao estado do passo {alvo}" if alvo else "voltou ao mapa vazio"],
            dados["ocupacao"])
        total = renderizar(dados, indice, saida, raiz, args.alpha_aura)
        print(f"Restaurado o estado do passo {alvo} (registrado como passo {n}).")
        print(f"Ocupados : {total} hex(es)")
        print(f"Mesa gerada em: {saida}")
        return

    ocup = {} if args.limpar else dict(dados.get("ocupacao") or {})
    acoes = []
    if args.limpar:
        acoes.append("limpou o mapa")

    for rot in args.remover:
        if ocup.pop(rot.upper(), None) is None:
            print(f"AVISO: {rot} nao tinha ninguem.")
        else:
            print(f"Removido : {rot.upper()}")
            acoes.append(f"removeu quem estava em {rot.upper()}")

    for tipo, pedidos in (("pj", args.pj), ("npc", args.npc)):
        for texto in pedidos:
            m = RE_PEDIDO.match(texto)
            if not m:
                raise SystemExit(
                    f'Nao entendi "{texto}".\n'
                    'Use: "Nome em I5 olhando para H5" (o "olhando" e opcional).')
            quem, rot = m["quem"].strip(), m["hex"].upper()
            alvo = m["alvo"].upper() if m["alvo"] else None
            if rot not in hexes:
                raise SystemExit(f"{rot} nao existe neste grid. "
                                 f"Exemplos: {', '.join(list(hexes)[:8])}...")
            if alvo and alvo not in hexes:
                raise SystemExit(f"O alvo {alvo} nao existe neste grid.")
            token = achar_token(quem, tipo, raiz)
            frente = aresta_para(hexes, rot, alvo) if alvo else None
            tam = (float(m["tam"].replace(",", ".")) if m["tam"]
                   else tamanho_catalogado(quem, tipo, raiz))

            corpo, faltando = corpo_de(hexes, rot, frente, tam, metro_px)
            frac = proporcao_ok(token, tam)
            if frac < 0.8:
                print(f"AVISO: a arte de {quem} e larga demais para {tam:g} hexes — "
                      f"vai entrar com {frac:.0%} do comprimento para nao invadir os "
                      "hexagonos vizinhos. Criatura comprida pede token desenhado "
                      "comprido; a aura marca os hexagonos certos de qualquer forma.")
            if faltando:
                print(f"AVISO: {quem} nao cabe inteiro — o corpo sairia do mapa "
                      f"para {faltando[0]}. Ficou com {len(corpo)} de {tam:g} hex.")
            alheios = [r for r in corpo[1:]
                       for outro, o in ocup.items()
                       if outro != rot and r in (o.get("hexes_ocupados") or [outro])]
            if alheios:
                print(f"AVISO: o corpo de {quem} invade {', '.join(sorted(set(alheios)))}"
                      ", que ja estava ocupado.")

            entrada = {"tipo": tipo, "quem": quem,
                       "token": token.relative_to(raiz).as_posix()
                       if raiz in token.resolve().parents else str(token)}
            if frente:
                entrada["frente"] = frente
                entrada["olhando"] = alvo
            if tam != 1:
                entrada["tamanho_hex"] = tam
            if len(corpo) > 1:
                entrada["hexes_ocupados"] = corpo
            de_onde = next((r for r, o in ocup.items()
                            if r != rot and o.get("quem") == quem), None)
            if de_onde:
                del ocup[de_onde]
            ocup[rot] = entrada
            cor = "azul" if tipo == "pj" else "vermelha"
            linha = (f"{'PJ ' if tipo == 'pj' else 'NPC'} {quem} "
                     + (f"{de_onde} -> {rot}" if de_onde else f"-> {rot}")
                     + (f", olhando {alvo} (aresta {frente})" if alvo else "")
                     + (f", corpo em {'+'.join(corpo)}" if len(corpo) > 1 else "")
                     + (f", {tam:g} hex" if tam != 1 else "")
                     + f", aura {cor}")
            print(linha)
            acoes.append(("moveu " if de_onde else "colocou ")
                         + linha.split(" ", 1)[1].strip())

    dados["ocupacao"] = ocup
    indice.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")

    n = renderizar(dados, indice, saida, raiz, args.alpha_aura)
    passo = registrar_movimento(hist_path, dados, acoes or ["redesenhou"], ocup)

    print(f"Ocupados : {n} hex(es)")
    print(f"Destino  : {motivo}")
    print(f"Mesa gerada em: {saida}")
    print(f"Movimento {passo} registrado em: {hist_path}")


if __name__ == "__main__":
    main()
