#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gm — o turno do roll6 fechado sem o Mestre na sala (Modo GM do Roll6), só pelo MCP.

    gm.py contexto --campanha N [--turno T] [--json]   # a mesa, os movimentos conferidos e a situação, numa tela só
    gm.py fechar gm-turnos/turno-T.json --campanha N   # confere o lote e chama process_turn pelo roll6.py
    gm.py fechar - --campanha N < lote.json            # o mesmo, com o lote pela entrada padrão

Tudo vem do roll6 e só o roll6 recebe o resultado: nada do repositório da campanha (campanha/, personagens/,
historico/, campanha/roll6.json) é lido ou gravado. `contexto` junta o `processar_turno.py contexto --so-mcp`
(quem agiu, o que declarou, onde está, PRONTO / FALTAM AÇÕES) com o `validar_movimento.py turno --so-mcp` (quem
passou do Deslocamento e para onde volta) e com a SITUAÇÃO lida do roll6: a narração do turno anterior, as últimas
narrações e o status de cada personagem e NPC. Não rola dado, não escreve nada, não chama process_turn.

`fechar` lê o lote montado pelo modelo (a forma da seção 6 de processar-turno), confere a forma, põe a campanha do
pedido e envia `process_turn` pelo cliente do roll6 — nunca pela ferramenta de MCP, que o pedido do Modo GM não
pré-aprova.

Códigos de saída: 0 ok / PRONTO · 2 FALTAM AÇÕES · 3 campanha não informada · 4 erro do roll6 ou do lote · 5 turno
já encerrado (só leitura).
"""
import argparse
import importlib.util
import json
import os
import sys
import types
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
RAIZ = Path(__file__).resolve().parents[4]
PROCESSAR_PY = SKILLS / "processar-turno" / "scripts" / "processar_turno.py"
VALIDAR_PY = SKILLS / "validar-movimento" / "scripts" / "validar_movimento.py"
ROLL6_PY = SKILLS / "roll6" / "scripts" / "roll6.py"

MAX_NARRACAO = 10000
NARRACAO_ANTERIOR = 1500
ULTIMAS = 3
CAMPOS_PJ = {"characterId", "currentLife", "currentEnergy", "status", "clearStatus", "x", "y", "look", "posture", "currentMove"}
CAMPOS_NPC = {"mapNpcId", "currentLife", "currentEnergy", "status", "clearStatus", "x", "y", "look", "posture", "currentMove"}

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass


def carregar(nome, caminho):
    """Importa um script de outra skill pelo caminho (como validar_movimento importa calcular_alcance)."""
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def campanha_do_pedido(args):
    """A campanha vem do pedido (--campanha), nunca do campanha/roll6.json."""
    if args.campanha is None:
        print("campanha não informada (o Modo GM manda o campaignId no pedido; use --campanha N)")
        sys.exit(3)
    return int(args.campanha)


def voltas(movimentos):
    """Quem passou do Deslocamento: nome, personagem, o hexágono e a frente válidos, o motivo."""
    saida = []
    for p in (movimentos or {}).get("personagens", []):
        if p.get("corrigido") and p.get("posicao_valida"):
            saida.append({"nome": p["nome"], "characterId": p.get("characterId"), "de": p.get("para_declarado"),
                          "para": p["posicao_valida"], "look": p.get("look_valido"), "motivo": p.get("motivo") or ""})
    return saida


def uma_linha(texto, max_len):
    linha = " ".join(str(texto or "").split())
    return linha if len(linha) <= max_len else linha[:max_len - 1].rstrip() + "…"


def situacao(roll6, cid, mesa):
    """A memória do GM, lida do roll6: a narração anterior, as últimas narrações e o estado de cada um."""
    c = roll6.cliente()
    turno = mesa.get("turno") or 1
    anterior = None
    if turno > 1:
        try:
            r = c.chamar("get_turn_narration", {"campaignId": cid, "turnNo": turno - 1})
            anterior = (r or {}).get("narration") or (r or {}).get("text") or None
        except roll6.Roll6Erro as e:
            anterior = f"(não li a narração anterior: {e})"
    ultimas = []
    try:
        r = c.chamar("list_chat_messages", {"campaignId": cid, "kind": "narration", "limit": ULTIMAS})
        for item in (r or {}).get("items", []):
            ultimas.append({"turnNo": item.get("turnNo"), "inicio": uma_linha(item.get("text") or item.get("description"), 160)})
    except roll6.Roll6Erro as e:
        ultimas.append({"turnNo": None, "inicio": f"(não li as narrações: {e})"})
    estado = []
    for p in mesa.get("personagens", []):
        pos = p.get("posicao")
        estado.append({"tipo": "pj", "nome": p["nome"], "pv": p["pv"], "fadiga": p["fadiga"], "status": p.get("status"),
                       "posicao": pos and pos.get("xy"), "frente": pos and pos.get("frente"),
                       "ficha": f"get_participation {p.get('campaignCharacterId')}"})
    for n in mesa.get("npcs", []):
        pos = n.get("posicao")
        estado.append({"tipo": "npc", "nome": n["nome"], "pv": n["pv"], "fadiga": n["fadiga"], "status": n.get("status"),
                       "posicao": pos and pos.get("xy"), "frente": pos and pos.get("frente"),
                       "ficha": f"get_npc {n.get('npcId')}"})
    return {"turno_anterior": turno - 1 if turno > 1 else None,
            "narracao_anterior": uma_linha(anterior, NARRACAO_ANTERIOR) if anterior else None,
            "ultimas_narracoes": ultimas, "estado": estado}


def imprimir_situacao(s):
    print("\n=== SITUAÇÃO (lida do roll6) ===")
    if s["turno_anterior"]:
        print(f"Narração do turno {s['turno_anterior']}: {s['narracao_anterior'] or '(sem narração anterior)'}")
    else:
        print("Primeiro turno: sem narração anterior.")
    if s["ultimas_narracoes"]:
        print("Últimas narrações:")
        for u in s["ultimas_narracoes"]:
            print(f"  - turno {u['turnNo']}: {u['inicio']}")
    print("Estado de cada um (status = o que vale neste turno):")
    for e in s["estado"]:
        pos = f"({e['posicao'][0]},{e['posicao'][1]}) olhando {e['frente']}" if e["posicao"] else "fora do mapa"
        print(f"  - {e['nome']} [{e['tipo']}] · PV {e['pv'][0]}/{e['pv'][1]} · Fadiga {e['fadiga'][0]}/{e['fadiga'][1]} · "
              f"{pos} · status: {e['status'] or '—'} · ficha: {e['ficha']} (sheet)")


def contexto(args):
    cid = campanha_do_pedido(args)
    os.chdir(RAIZ)
    pt = carregar("processar_turno", PROCESSAR_PY)
    mesa = pt.montar(RAIZ, args.turno, cid, True)
    movimentos = None
    vm = None
    if mesa.get("em_andamento") and not mesa.get("turno_livre"):
        vm = carregar("validar_movimento", VALIDAR_PY)
        movimentos = vm.turno(types.SimpleNamespace(raiz=".", turno=args.turno, manobra=[], peso_atual=None,
                                                    so_mcp=True, campanha=cid))
    roll6 = carregar("roll6", ROLL6_PY)
    sit = situacao(roll6, cid, mesa)
    quem_volta = voltas(movimentos)
    if not mesa.get("em_andamento"):
        veredito, codigo = "SÓ LEITURA — turno já encerrado; nada a processar.", 5
    elif mesa.get("pendentes"):
        veredito, codigo = "FALTAM AÇÕES de: " + ", ".join(mesa["pendentes"]), 2
    else:
        veredito, codigo = "PRONTO — todo personagem que deve ação declarou.", 0
    if mesa.get("em_andamento") and mesa.get("fora_de_combate"):
        veredito += " Fora de combate (não esperados): " + ", ".join(mesa["fora_de_combate"]) + "."
    if args.json:
        print(json.dumps({"campaignId": cid, "veredito": veredito, "pronto": codigo == 0, "mesa": mesa,
                          "movimentos": movimentos, "situacao": sit, "voltam": quem_volta}, ensure_ascii=False, indent=2))
        sys.exit(codigo)
    pt.imprimir(mesa)
    if movimentos is not None:
        vm.imprimir_turno(movimentos)
    elif mesa.get("turno_livre"):
        print("\nTURNO LIVRE: o roll6 não registra movimentos no modo livre — não há rota a conferir; as peças ficam onde estão.")
    imprimir_situacao(sit)
    print("\n=== GM ===")
    print(f"VEREDITO: {veredito}")
    if quem_volta:
        for v in quem_volta:
            print(f"VOLTA PARA: {v['nome']} → ({v['para'][0]},{v['para'][1]}) look {v['look']} — {v['motivo']}")
    else:
        print("Ninguém passou do Deslocamento.")
    sys.exit(codigo)


def conferir_lote(lote, cid):
    erros = []
    if not isinstance(lote, dict):
        return ["o lote não é um objeto JSON"]
    if lote.get("campaignId") not in (None, cid):
        erros.append(f"campaignId {lote.get('campaignId')} não é o da campanha do pedido ({cid})")
    for chave, campos, ident in (("characters", CAMPOS_PJ, "characterId"), ("npcs", CAMPOS_NPC, "mapNpcId")):
        itens = lote.get(chave, [])
        if not isinstance(itens, list):
            erros.append(f"{chave} deve ser uma lista")
            continue
        for i, item in enumerate(itens):
            if not isinstance(item, dict) or ident not in item:
                erros.append(f"{chave}[{i}] precisa de {ident}")
                continue
            estranhos = set(item) - campos
            if estranhos:
                erros.append(f"{chave}[{i}]: campos desconhecidos {sorted(estranhos)}")
            if ("x" in item) != ("y" in item):
                erros.append(f"{chave}[{i}]: x e y andam juntos")
    narracao = lote.get("narration")
    if not isinstance(narracao, str) or not narracao.strip():
        erros.append("narration é obrigatória (a narração com a conta de cada ação)")
    elif len(narracao) > MAX_NARRACAO:
        erros.append(f"narration tem {len(narracao)} caracteres; o máximo é {MAX_NARRACAO} (corte a prosa, nunca a conta)")
    return erros


def fechar(args):
    cid = campanha_do_pedido(args)
    os.chdir(RAIZ)
    try:
        texto = sys.stdin.read() if args.lote == "-" else Path(args.lote).read_text(encoding="utf-8")
        lote = json.loads(texto)
    except (OSError, ValueError) as e:
        print(f"lote inválido: {e}")
        sys.exit(4)
    erros = conferir_lote(lote, cid)
    if erros:
        print("LOTE RECUSADO:")
        for e in erros:
            print(f"  - {e}")
        sys.exit(4)
    lote["campaignId"] = cid
    roll6 = carregar("roll6", ROLL6_PY)
    try:
        resposta = roll6.cliente().chamar("process_turn", lote)
    except roll6.Roll6Erro as e:
        print(f"process_turn recusado: {e}")
        print("Se foi 400, nada foi gravado: corrija o item apontado e envie de novo. Outra falha: confira com get_turn_data antes de reenviar.")
        sys.exit(4)
    print(json.dumps({"finishedTurn": resposta.get("finishedTurn"), "turnNo": resposta.get("turnNo")}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="Modo GM: o turno do roll6 fechado sem o Mestre, só pelo MCP.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("contexto", help="A mesa, os movimentos conferidos e a situação, numa tela só")
    c.add_argument("--campanha", type=int, default=None, help="campaignId do pedido (obrigatório)")
    c.add_argument("--turno", type=int, default=None)
    c.add_argument("--json", action="store_true")
    f = sub.add_parser("fechar", help="Confere o lote e chama process_turn pelo roll6.py")
    f.add_argument("lote", help="o lote da seção 6 de processar-turno (gm-turnos/turno-T.json), ou - para a entrada padrão")
    f.add_argument("--campanha", type=int, default=None, help="campaignId do pedido (obrigatório)")
    a = ap.parse_args()
    (contexto if a.cmd == "contexto" else fechar)(a)


if __name__ == "__main__":
    main()
