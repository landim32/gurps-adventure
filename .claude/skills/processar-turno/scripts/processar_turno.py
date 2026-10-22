#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Junta, numa tela só, o que é preciso para processar um turno jogado no roll6.

    processar_turno.py contexto              # o turno em andamento
    processar_turno.py contexto --turno 3    # um turno já encerrado (só leitura)
    processar_turno.py contexto --json

Lê do roll6 (get_turn_data + get_turn_state) quem agiu, o que declarou, onde está e
como está; cruza com o repositório — ficha de cada um, saude.md, mapa local — e aponta
o que diverge. Diz se o turno está PRONTO (todo personagem aprovado declarou ação) ou
quem falta.

Não rola dado, não escreve nada e não chama process_turn: resolver é das skills de
regra, registrar é da skill campanha, e fechar o turno é do modelo, pelo MCP.
"""
import argparse
import json
import sys
from pathlib import Path

RAIZ_SKILLS = Path(".claude/skills")

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass


def importar(raiz):
    for s in ("roll6", "acao", "campanha"):
        sys.path.insert(0, str(raiz / RAIZ_SKILLS / s / "scripts"))
    import roll6, acao, campanha                                    # noqa: E401
    return roll6, acao, campanha


def ficha_local(acao, raiz, nome):
    alvo = acao.simples(nome)
    for pasta, d in acao.fichas(raiz):
        if alvo in (acao.simples(d.get("nome")), acao.simples(pasta.name)):
            return pasta, d
    return None, None


def saude_local(roll6, campanha, raiz, mapa, secao, nome_roll6):
    """(pv, fadiga, estados) do saude.md para quem, no roll6, se chama nome_roll6."""
    try:
        p = campanha.exige_campanha(raiz)
    except SystemExit:
        return None
    titulo = "Personagens" if secao == "pj" else "NPCs"
    for sec, nome, ls in campanha.ler_saude(p / campanha.SAUDE):
        if sec == titulo and roll6.slug(roll6.nome_no_roll6(mapa, nome)) == roll6.slug(nome_roll6):
            pv = sum(v for _, t, v, _ in ls if t == "PV" and v is not None)
            fad = sum(v for _, t, v, _ in ls if t == "FAD" and v is not None)
            if secao == "pj":
                pv_max, fad_max = campanha.maximos_da_ficha(raiz, nome)
                _, _, est = campanha.resumo_saude(ls, pv_max, fad_max)
                return {"nome_local": nome, "pv": (pv_max or 0) + pv, "fadiga": (fad_max or 0) + fad,
                        "estados": est}
            _, _, est = campanha.resumo_saude(ls, None, None)
            return {"nome_local": nome, "pv_acumulado": pv, "estados": est}
    return None


def reacoes_de_todos(roll6, raiz, mapa):
    """{(npc, pj): reação mais recente} de todos os reacoes.json da campanha, em ordem de
    capítulo — a do capítulo mais novo ganha. Fica só no repositório: nunca vai ao roll6."""
    fora = {}
    for f in sorted((raiz / "campanha").glob("*/reacoes.json")):
        try:
            dados = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in dados.get("reacoes", []):
            chave = (roll6.slug(roll6.nome_no_roll6(mapa, r.get("npc", ""))), roll6.slug(r.get("pj", "")))
            fora[chave] = {"faixa": r.get("faixa"), "total": r.get("total"), "capitulo": f.parent.name[:2]}
    return fora


def indice_local(mapa, map_id):
    """O índice de hexágonos ligado a este mapa do roll6, e só isso.

    A `ocupacao` do índice era escrita pela `atualizar-mapa`, que saiu do repo: compará-la
    com a mesa seria conferir uma foto parada contra o presente, e acusar de divergência
    quem só andou. A posição é a do roll6; do índice fica o `deslocamento`, que é estático
    e serve para renderizar o rótulo (`Q30`) que os registros já usam.
    """
    for indice, lig in (mapa.get("mapas") or {}).items():
        if lig.get("mapId") == map_id:
            return indice
    return None


def alvo_de(roll6, entrada, desloc=(0, 0)):
    """O alvo de uma ação declarada com "Agir sobre…" no roll6 (098): o hex, a distância em
    hexágonos e, quando havia uma peça no hex, a cópia dela feita na hora da declaração
    (nunca relida). None quando a ação não tem alvo."""
    a = entrada.get("target")
    if not a:
        return None
    alvo = {"xy": [a["x"], a["y"]], "hex": roll6.xy_para_rotulo(a["x"], a["y"], desloc),
            "distancia": a.get("distance", 0), "mapTokenId": a.get("mapTokenId")}
    if a.get("mapTokenId") is not None:
        alvo.update({"tipo": a.get("kindLabel") or a.get("kind"), "lado": a.get("sideLabel") or a.get("side"),
                     "nome": a.get("name"), "characterId": a.get("characterId"), "mapNpcId": a.get("mapNpcId"),
                     "frente": a.get("lookName"), "postura": a.get("postureLabel"), "status": a.get("status"),
                     "pv": [a.get("currentLife"), a.get("totalLife")] if a.get("totalLife") is not None else None,
                     "fadiga": [a.get("currentEnergy"), a.get("totalEnergy")] if a.get("totalEnergy") is not None else None})
    return alvo


def linha_alvo(alvo):
    """'Goblin (inimigo, NPC) em J8 (9,7), a 3 hexes, olhando Sudeste, Caído, PV 5/12, Fadiga 3/10,
    status: atordoado' ou 'o hex M5 (12,4), a 5 hexes'."""
    d = alvo["distancia"]
    hexes = "1 hex" if d == 1 else f"{d} hexes"
    onde = f'{alvo["hex"]} ({alvo["xy"][0]},{alvo["xy"][1]})'
    if alvo.get("mapTokenId") is None:
        return f"o hex {onde}, a {hexes}"
    if alvo.get("lado") in ("si mesmo", "self"):
        return f"si mesmo em {onde}"
    partes = [f'{alvo.get("nome")} ({alvo.get("lado")}, {alvo.get("tipo")}) em {onde}', f"a {hexes}"]
    if alvo.get("frente"):
        partes.append(f'olhando {alvo["frente"]}')
    if alvo.get("postura") and alvo["postura"] != "Em pé":
        partes.append(alvo["postura"])
    if alvo.get("pv"):
        partes.append(f'PV {alvo["pv"][0]}/{alvo["pv"][1]}')
    if alvo.get("fadiga"):
        partes.append(f'Fadiga {alvo["fadiga"][0]}/{alvo["fadiga"][1]}')
    if alvo.get("status"):
        partes.append(f'status: {alvo["status"]}')
    return ", ".join(partes)


def arma_despreparada(status):
    """O status do roll6 diz que a arma está despreparada? (MB, p. 104: quem está assim não
    ataca nem apara com ela — a manobra do turno é Preparar.) É o aviso que faltava na
    tela: o modelo lia «machado despreparado» no status e rolava o ataque assim mesmo."""
    return bool(status) and "despreparad" in status.lower()


AVISO_DESPREPARADA = ("    ⚠ ARMA DESPREPARADA no status: a ação deste turno é PREPARAR (MB, p. 104). "
                      "Não role ataque nem aparar com ela — nem por ação repetida; o golpe fica "
                      "para o turno seguinte.")


def acoes_de(roll6, entradas, desloc):
    """[{texto, alvo}] das ações declaradas (turnType 2), na ordem do roll6."""
    return [{"texto": e["description"], "alvo": alvo_de(roll6, e, desloc),
             "repetida": REPETIDA.get(e.get("repeated"))} for e in entradas if e["turnType"] == 2]


# Ação repetida (099): "declared" = registrada quando o jogador a ativou; "turnStart" = aplicada no início do turno.
REPETIDA = {"declared": "declarada", "turnStart": "inicio"}


def montar(raiz, turno, campanha_id=None, so_mcp=False):
    roll6, acao, campanha = importar(raiz)
    # Só pelo MCP (097): a campanha vem do argumento e o mapeamento nem é lido — tudo "fora do repositório".
    if so_mcp:
        if campanha_id is None:
            print("campanha não informada (--so-mcp exige --campanha N).")
            raise SystemExit(3)
        mapa = None
    else:
        mapa = roll6.mapeamento(raiz)
    if not mapa and campanha_id is None:
        raise SystemExit("Sem campanha/roll6.json — a campanha ativa não está ligada ao roll6 (skill roll6).")
    # Outra campanha do roll6 (teste, one-shot): nada do repositório vale para ela —
    # nem saúde, nem mapa local, nem reações. Só a mesa e as fichas locais.
    fora_do_repo = campanha_id is not None and campanha_id != (mapa or {}).get("campaignId")
    if fora_do_repo:
        mapa = {"campaignId": campanha_id}
    cid = mapa["campaignId"]
    c = roll6.cliente()
    dados = c.chamar("get_turn_data", {"campaignId": cid, "turnNo": turno})
    em_andamento = dados["turnNo"] == dados["currentTurn"]
    livre = bool(c.chamar("get_campaign", {"campaignId": cid}).get("freeMode"))
    entradas = (c.chamar("get_turn_state", {"campaignId": cid})["entries"] if em_andamento
                else roll6.lista(c.chamar("list_turn_entries", {"campaignId": cid, "turnNo": dados["turnNo"]})))
    indice = indice_local(mapa, dados.get("mapId"))
    desloc = tuple(((mapa.get("mapas") or {}).get(indice) or {}).get("deslocamento") or (0, 0))
    est = {} if so_mcp else acao.estado(raiz)
    divergencias = []

    def posicao(x, y, look):
        if x is None:
            return None
        return {"xy": [x, y], "hex": roll6.xy_para_rotulo(x, y, desloc), "frente": roll6.LOOK_NOME.get(look)}

    pjs = []
    for ch in dados["characters"]:
        minhas = [e for e in entradas if e.get("characterId") == ch["characterId"]]
        acoes = acoes_de(roll6, minhas, desloc)
        moveu = [e for e in minhas if e["turnType"] == 1]
        pasta, ficha = (None, None) if so_mcp else ficha_local(acao, raiz, ch["name"])
        s = None if fora_do_repo else saude_local(roll6, campanha, raiz, mapa, "pj", ch["name"])
        pos = posicao(ch.get("x"), ch.get("y"), ch.get("look"))
        pj = {"nome": ch["name"], "jogador": ch.get("playerName"), "characterId": ch["characterId"],
              "campaignCharacterId": ch.get("campaignCharacterId"), "mapTokenId": ch.get("mapTokenId"),
              "ficha": (pasta / "personagem.md").as_posix() if pasta else None,
              "pv": [ch["currentLife"], ch["totalLife"]], "fadiga": [ch["currentEnergy"], ch["totalEnergy"]],
              "status": ch.get("status"), "posicao": pos, "repeticao": ch.get("repeatedAction"),
              "acoes": acoes, "movimentos": [f'({e.get("beforeX")},{e.get("beforeY")}) → ({e.get("x")},{e.get("y")})'
                                             for e in moveu],
              "reacoes": [] if fora_do_repo else acao.reacoes_do_pj(est.get("capitulo_atual_pasta"), ch["name"])}
        if not pasta and not so_mcp:
            divergencias.append(f"{ch['name']}: sem ficha em personagens/ — leia a ficha pelo get_participation (characterSheet)")
        if s and (s["pv"], s["fadiga"]) != (ch["currentLife"], ch["currentEnergy"]):
            divergencias.append(f"{ch['name']}: roll6 PV {ch['currentLife']} / Fadiga {ch['currentEnergy']}, "
                                f"saude.md PV {s['pv']} / Fadiga {s['fadiga']}")
        pjs.append(pj)

    reacoes = {} if fora_do_repo else reacoes_de_todos(roll6, raiz, mapa)
    npcs = []
    for n in dados["npcs"]:
        minhas = [e for e in entradas if e.get("mapNpcId") == n["mapNpcId"]]
        s = None if fora_do_repo else saude_local(roll6, campanha, raiz, mapa, "npc", n["name"])
        pos = posicao(n.get("x"), n.get("y"), n.get("look"))
        npcs.append({"nome": n["name"], "mapNpcId": n["mapNpcId"], "npcId": n.get("npcId"),
                     "mapTokenId": n.get("mapTokenId"),
                     "pv": [n["currentLife"], n["totalLife"]], "fadiga": [n["currentEnergy"], n["totalEnergy"]],
                     "status": n.get("status"), "posicao": pos, "repeticao": n.get("repeatedAction"),
                     "categoria": n.get("npcCategory") or n.get("category"),
                     "nome_no_saude": s["nome_local"] if s else None,
                     "acoes": acoes_de(roll6, minhas, desloc),
                     "moveu": any(e["turnType"] == 1 for e in minhas),
                     "reacoes": {p["nome"]: reacoes.get((roll6.slug(n["name"]), roll6.slug(p["nome"])))
                                 for p in pjs}})
        if s and n["totalLife"] + s["pv_acumulado"] != n["currentLife"]:
            divergencias.append(f"{n['name']}: roll6 PV {n['currentLife']}, saude.md "
                                f"{n['totalLife'] + s['pv_acumulado']} ({s['pv_acumulado']:+d} sobre {n['totalLife']})")

    pendentes = [p["nome"] for p in pjs if not p["acoes"]]
    so_moveu = [p["nome"] for p in pjs if not p["acoes"] and p["movimentos"]]
    arquivos = [] if so_mcp else [(k, v.as_posix(), d) for k, v, d in acao.arquivos_de_contexto(raiz, est, Path("."))
                                   if k != "ficha"]
    if fora_do_repo:
        arquivos, est = [], {}
    return {"campaignId": cid, "fora_do_repositorio": fora_do_repo, "so_mcp": bool(so_mcp), "turno": dados["turnNo"], "turno_atual": dados["currentTurn"],
            "em_andamento": em_andamento, "turno_livre": livre, "mapId": dados.get("mapId"), "indice_local": indice,
            "personagens": pjs, "npcs": npcs, "acoes_md": dados.get("actions") or "",
            "pendentes": pendentes, "so_moveu": so_moveu, "divergencias": divergencias,
            "arquivos": arquivos, "reacoes_json": (Path(est["capitulo_atual_pasta"]) / "reacoes.json").as_posix()
            if est.get("capitulo_atual_pasta") else None}


def imprimir(r):
    print(f"Campanha {r['campaignId']} · turno {r['turno']}"
          + ("" if r["em_andamento"] else f" (encerrado; o atual é {r['turno_atual']})")
          + f" · mapa {r['mapId']} ↔ {r['indice_local'] or '(sem índice local ligado)'}")
    if r.get("so_mcp"):
        print("SÓ MCP — tudo vem do roll6; nada do repositório é lido ou gravado. Fichas pelo get_participation (sheet)\n"
              "  e get_npc (sheet); a situação (status, PV, posições, narração) só pelo process_turn.")
    elif r.get("fora_do_repositorio"):
        print("ATENÇÃO: campanha fora do repositório — sem saúde, mapa local, reações nem log locais.\n"
              "  Não registre com campanha.py (cairia na campanha ativa); o registro é só o process_turn.")
    if r.get("turno_livre"):
        print("TURNO LIVRE (freeMode): não valide o posicionamento nem o Deslocamento; "
              "mova as peças para onde a ação precisar.")
    print()
    if not r["em_andamento"]:
        veredito = "SÓ LEITURA — turno já encerrado; process_turn só vale para o turno em andamento."
    elif r["pendentes"]:
        veredito = ("FALTAM AÇÕES de: " + ", ".join(r["pendentes"])
                    + (f"  (só se moveram: {', '.join(r['so_moveu'])})" if r["so_moveu"] else "")
                    + "\n  → não processe; espere, ou só com ordem do Mestre.")
    else:
        veredito = "PRONTO — todo personagem aprovado declarou ação."
    print(f"VEREDITO: {veredito}\n")

    print("## Personagens")
    for p in r["personagens"]:
        pos = p["posicao"]
        print(f"- {p['nome']} ({p['jogador']}) · characterId {p['characterId']} · "
              f"PV {p['pv'][0]}/{p['pv'][1]} · Fadiga {p['fadiga'][0]}/{p['fadiga'][1]} · "
              + (f"{pos['hex']} {pos['xy']} olhando {pos['frente']}" if pos else "fora do mapa"))
        ficha = p['ficha'] or (f"get_participation {p.get('campaignCharacterId')} (sheet)" if r.get("so_mcp")
                               else "— (get_participation → characterSheet)")
        print(f"    ficha: {ficha}")
        print(f"    status: {p['status'] or '—'}")
        if arma_despreparada(p["status"]):
            print(AVISO_DESPREPARADA)
        if p.get("repeticao"):
            print(f"    REPETIÇÃO ATIVA: {p['repeticao']}")
            print("      → ao fechar, se o objetivo foi cumprido: clearRepeatedAction: true neste personagem")
        for a in p["acoes"]:
            print(f"    AÇÃO{' (repetida)' if a.get('repetida') else ''}: {a['texto']}")
            if a.get("alvo"):
                print(f"      → sobre {linha_alvo(a['alvo'])}")
        for m in p["movimentos"]:
            print(f"    moveu: {m}")
        if not p["acoes"]:
            print("    (sem ação declarada)")
        for rc in p["reacoes"]:
            print(f"    reação de {rc['npc']}: {rc['faixa']} ({rc['total']})")
    print("\n## NPCs no mapa")
    for n in r["npcs"]:
        pos = n["posicao"]
        print(f"- {n['nome']} · mapNpcId {n['mapNpcId']} · PV {n['pv'][0]}/{n['pv'][1]} · "
              + (f"{pos['hex']} {pos['xy']} olhando {pos['frente']}" if pos else "fora do mapa")
              + (f" · categoria: {n['categoria']}" if n.get("categoria") else "")
              + (f" · no saude.md: {n['nome_no_saude']}" if n["nome_no_saude"] else ""))
        if r.get("so_mcp"):
            print(f"    ficha: get_npc {n.get('npcId')} (sheet)")
        print(f"    status: {n['status'] or '—'}")
        if arma_despreparada(n["status"]):
            print(AVISO_DESPREPARADA)
        if n.get("repeticao"):
            print(f"    REPETIÇÃO ATIVA: {n['repeticao']}")
            print("      → ao fechar, se o objetivo foi cumprido: clearRepeatedAction: true neste NPC")
        for a in n["acoes"]:
            print(f"    AÇÃO{' (repetida)' if a.get('repetida') else ' (lançada no roll6)'}: {a['texto']}")
            if a.get("alvo"):
                print(f"      → sobre {linha_alvo(a['alvo'])}")
        if not n["acoes"] and not n["moveu"]:
            print("    SEM AÇÃO NEM MOVIMENTO — você decide (passo 3 da skill)")
        if not r.get("so_mcp"):
            rs = [f"{pj} {r['faixa']} {r['total']} (cap. {r['capitulo']})" if r else f"{pj} —"
                  for pj, r in n["reacoes"].items()]
            print("    reações [LOCAL, não vai ao roll6]: " + "; ".join(rs))
    print("\n## Divergências roll6 × repositório")
    print("\n".join(f"- {d}" for d in r["divergencias"]) or "- nenhuma")
    print("\n## O que a mesa fez neste turno (roll6)")
    print(r["acoes_md"].strip() or "_(nada lançado)_")
    print("\n## Leia, nesta ordem (mais a ficha de cada um acima)")
    for k, v, d in r["arquivos"]:
        print(f"  [{'x' if not Path(v).is_file() else ' '}] {v}\n       {d}")
    if r["reacoes_json"]:
        marca = " " if Path(r["reacoes_json"]).is_file() else "x"
        print(f"  [{marca}] {r['reacoes_json']}\n       reações já roladas — nunca role de novo um par que já tem")
    print("\n× = ainda não existe; siga sem ele.")


def main():
    ap = argparse.ArgumentParser(description="Contexto para processar um turno do roll6.")
    ap.add_argument("--raiz", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("contexto", help="Quem agiu, o que declarou, onde está e o que diverge")
    s.add_argument("--turno", type=int, default=None)
    s.add_argument("--campanha", type=int, default=None,
                   help="campaignId de outra campanha do roll6 (padrão: a do campanha/roll6.json)")
    s.add_argument("--so-mcp", action="store_true",
                   help="só pelo MCP (097): nada do repositório é lido ou gravado; exige --campanha")
    s.add_argument("--json", action="store_true")
    a = ap.parse_args()
    raiz = Path(a.raiz).resolve()
    r = montar(raiz, a.turno, a.campanha, a.so_mcp)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        imprimir(r)


if __name__ == "__main__":
    main()
