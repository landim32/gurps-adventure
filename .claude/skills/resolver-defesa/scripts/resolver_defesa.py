#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""resolver-defesa — a defesa de quem apanhou, do corpo a corpo ao projétil.

Chamada por `atacar` e `atacar-distancia` depois de o ataque ter acertado (um golpe
fulminante não tem defesa). Decide o número, rola, e devolve o que a cascata de dano
precisa saber.

    resolver_defesa.py --alvo "Morto 3" --defesa esquiva --defesa-valor 6 \
      --ht-alvo 12 --local '{"nome":"Tronco","armadura":"tronco"}'

Não rola ataque, não calcula dano, não escreve em lugar nenhum.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
ROLL_PY = SKILLS / "roll" / "scripts" / "roll.py"
CTX_PY = SKILLS / "contexto" / "scripts" / "contexto.py"

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Reflexos em Combate e companhia: quem sabe ler vantagem na ficha é a folha contexto.
try:
    _espec = importlib.util.spec_from_file_location("contexto", CTX_PY)
    ctx = importlib.util.module_from_spec(_espec)
    _espec.loader.exec_module(ctx)
except Exception as erro:
    raise SystemExit(f"Não consegui carregar a skill contexto ({CTX_PY}): {erro}")

RE_DP_RD = re.compile(r"DP\s*(\d+)\s*/?\s*RD\s*(\d+)", re.I)

# MB, cap. 14 — armadura por região, e o que a RD natural do crânio soma.
def protecao(ficha, regiao_armadura, perfurante):
    """(DP, RD, peça) da região atingida. Sem ficha, sem proteção."""
    if not ficha:
        return 0, 0, None
    dp = rd = 0
    peca = None
    for o in ficha.get("armas_objetos") or []:
        if (o.get("categoria") or "").lower() != "armadura":
            continue
        m = RE_DP_RD.search(o.get("tipo") or "")
        if not m:
            continue
        cobre = (o.get("item") or "").lower()
        if regiao_armadura and regiao_armadura.lower() not in cobre:
            continue
        dp, rd = int(m.group(1)), int(m.group(2))
        peca = o.get("item")
        if perfurante:
            rd = max(0, rd - 1)     # perfuração ignora 1 ponto de RD (MB, cap. 14)
        break
    return dp, rd, peca


def escudo_dp(ficha):
    for o in (ficha or {}).get("armas_objetos") or []:
        nome = (o.get("item") or "").lower()
        if "escudo" in nome or "broquel" in nome:
            m = RE_DP_RD.search(o.get("tipo") or "")
            if m:
                return int(m.group(1)), o.get("item")
    return 0, None


def calcular(p):
    """Devolve {"saida","mec","resultado"}. O caller imprime saida/mec e usa o resultado."""
    alvo = p.get("alvo", "o alvo")
    defesa = p.get("defesa") or "nenhuma"
    manobra = p.get("manobra_defesa") or "normal"
    md = p.get("md") or {"nome": "Normal", "defesas": 1, "mod": 0}
    local = p.get("local") or {}
    tipo = p.get("tipo", "cont")
    saida, mec, avisos = [], [], []

    fd = p.get("ficha")
    ht = int(p.get("ht_alvo") or 0)

    dp_local, rd_local, peca = protecao(fd, local.get("armadura"), tipo == "perf")
    if p.get("dp_informado") is not None:
        dp_local, peca = p["dp_informado"], peca or "informado pelo Mestre"
    if p.get("rd_informado") is not None:
        rd_local = p["rd_informado"]
    dp_escudo, nome_escudo = (0, None) if p.get("sem_escudo") else escudo_dp(fd)
    if p.get("dp_informado") is not None and p.get("dp_informado_zera_escudo"):
        dp_escudo, nome_escudo = 0, None
    rd_total = rd_local + local.get("rd_natural", 0)
    # no corpo a corpo a DP do escudo só vale onde a armadura vale; contra projétil a
    # mesa sempre somou as duas — mantido como opção até o Mestre decidir um regime só
    escudo_passivo = dp_escudo if p.get("escudo_sempre") else (
        dp_escudo if local.get("armadura") else 0)

    resultado = {"defendeu": False, "dp_local": dp_local, "rd_local": rd_local,
                 "rd_total": rd_total, "peca": peca, "dp_escudo": dp_escudo,
                 "nome_escudo": nome_escudo, "ht_alvo": ht, "alvo": alvo,
                 "defesa_final": defesa, "total_defesa": None}

    if p.get("ignora_defesa"):
        # golpe fulminante: não há defesa a rolar, mas a cascata de dano ainda quer a RD
        # da região e a peça de onde ela veio. Nada é impresso, nada é sorteado.
        resultado["dp_total_passivo"] = dp_local + escudo_passivo
        return {"saida": [], "mec": [], "avisos": [], "resultado": resultado}

    if md["defesas"] == 0 or defesa == "nenhuma":
        saida.append(f"\nDEFESA: {alvo} não tem defesa ativa — {md['nome']}.")
        if md.get("obs"):
            saida.append(f"  {md['obs']}")
        dp_total = dp_local + escudo_passivo
        resultado["dp_total_passivo"] = dp_total
        if dp_total:
            dd, td = _rola()
            defendeu = td <= dp_total or td <= 4
            resultado["defendeu"] = defendeu
            saida.append(f"  Só a defesa passiva vale: DP {dp_total}"
                         + (f" ({peca}" + (f" + {nome_escudo}" if dp_escudo else "") + ")"
                            if peca else ""))
            saida.append(f"  3d [{', '.join(map(str, dd))}] = {td} contra {dp_total} — "
                         + ("DEFENDEU" if defendeu else "não segurou"))
            mec.append(f"Defesa: {alvo} sem defesa ativa ({md['nome']}); só a DP "
                       f"{dp_total}" + (f" ({peca}" + (f" + {nome_escudo}" if dp_escudo
                                                       else "") + ")" if peca else ""))
            mec.append(f"3d {_txt_dados(dd)} = *{td}* → "
                       + ("defendeu" if defendeu else "não segurou"))
        else:
            mec.append(f"Defesa: {alvo} sem defesa ativa ({md['nome']}) e sem DP")
        return {"saida": saida, "mec": mec, "avisos": avisos, "resultado": resultado}

    base = int(p.get("defesa_valor") or 0)
    fonte = "informada pelo Mestre"
    if not base and fd:
        base = int((fd.get("defesas_ativas") or {}).get(defesa) or 0)
        fonte = "da ficha"
    if not base:
        raise SystemExit(f"Não sei a {defesa} de {alvo}. Passe --defesa-valor "
                         "(ou --alvo-{0} no chamador).".format(defesa))

    reflexos = fd is not None and ctx.nivel_vantagem(fd, "reflexos-em-combate") is not None
    comp, total = [f"{defesa} {base} ({fonte})"], base
    if reflexos:
        total += 1
        comp.append("+1 Reflexos em Combate")
    dp_total = dp_local + escudo_passivo
    if dp_total:
        total += dp_total
        comp.append(f"+{dp_local} DP {peca or 'armadura'}" if dp_local else "")
        if dp_escudo and (p.get("escudo_sempre") or local.get("armadura")):
            comp.append(f"+{dp_escudo} DP {nome_escudo}"
                        + (" (vale contra projétil)" if p.get("projetil") else ""))
    if p.get("recuar"):
        total += 3
        comp.append("+3 recuar")
    if md["mod"]:
        total += md["mod"]
        comp.append(f"{md['mod']:+d} {md['nome']}")
    if p.get("mod"):
        total += int(p["mod"])
        comp.append(_com_motivo(int(p["mod"]), p.get("mod_motivo")))

    saida.append(f"\nDEFESA de {alvo}: " + " ".join(c for c in comp if c) + f" = **{total}**")
    mec.append(f"Defesa de {alvo}: " + " ".join(c for c in comp if c)
               .replace(f" ({fonte})", "").replace(" informado pelo Mestre", "")
               + f" = *{total}*")
    if md.get("obs"):
        saida.append(f"  {md['obs']}")

    resultado["total_defesa"] = total
    for tentativa in range(1, (md["defesas"] or 1) + 1):
        dd, td = _rola()
        ok = (td <= 4) or (td <= total and td < 17)
        extra = ""
        if td <= 4:
            extra = "  ← 3 ou 4 sempre defende" + (
                ", e o atacante vai à Tabela de Erros Críticos" if not p.get("projetil")
                else "")
        if td >= 17:
            extra = "  ← 17 ou 18 é falha desastrosa na defesa" + (
                "" if p.get("projetil") else " (MB, cap. 14)")
        rot = f"  Defesa {tentativa}" if (md["defesas"] or 1) > 1 else "  Jogada"
        saida.append(f"{rot}: 3d [{', '.join(map(str, dd))}] = {td} — "
                     + ("DEFENDEU" if ok else "falhou") + extra)
        nota = (" — *DEFESA DECISIVA*: o atacante vai à Tabela de Erros Críticos" if td <= 4
                else " — *FALHA CRÍTICA* na defesa" if td >= 17 else "")
        mec.append(f"3d {_txt_dados(dd)} = *{td}* → "
                   + (("defendeu no limite" if td == total else
                       f"defendeu por {total - td}") if ok and td > 4 else
                      "defendeu" if ok else f"falhou por {td - total}") + nota)
        if ok:
            resultado["defendeu"] = True
            break
        if (md["defesas"] or 1) > 1 and tentativa < md["defesas"]:
            saida.append("    (Defesa Total: a segunda tem de ser uma defesa DIFERENTE)")

    return {"saida": saida, "mec": mec, "avisos": avisos, "resultado": resultado}


def _rola():
    try:
        espec = importlib.util.spec_from_file_location("roll", ROLL_PY)
        roll = importlib.util.module_from_spec(espec)
        espec.loader.exec_module(roll)
    except Exception as erro:
        raise SystemExit(f"Não consegui carregar a skill roll ({ROLL_PY}): {erro}")
    d = roll.d6(3)
    return d, sum(d)


def _txt_dados(d):
    return "[" + ", ".join(map(str, d)) + "]"


def _com_motivo(valor, motivo):
    m = (motivo or "").strip()
    return m if m[:1] in "+-" else f"{valor:+d} {m or 'situação'}"


def main():
    ap = argparse.ArgumentParser(description="Defesa de quem apanhou (MB, cap. 14).")
    ap.add_argument("--alvo", required=True)
    ap.add_argument("--defesa", default="nenhuma",
                    choices=["nenhuma", "esquiva", "aparar", "bloqueio"])
    ap.add_argument("--defesa-valor", type=int, default=0)
    ap.add_argument("--ficha", default="", help="JSON da ficha do alvo (ou --arquivo-ficha)")
    ap.add_argument("--arquivo-ficha", default="")
    ap.add_argument("--local", default="{}", help="JSON da região atingida")
    ap.add_argument("--tipo", default="cont", choices=["cont", "corte", "perf", "bal"])
    ap.add_argument("--ht-alvo", type=int, default=0)
    ap.add_argument("--manobra-defesa", default="normal")
    ap.add_argument("--md", default="",
                    help='JSON da manobra de defesa resolvida: {"nome":"Defesa Total",'
                         '"defesas":2,"mod":-2,"obs":"..."}')
    ap.add_argument("--mod", type=int, default=0)
    ap.add_argument("--mod-motivo", default="")
    ap.add_argument("--recuar", action="store_true")
    ap.add_argument("--sem-escudo", action="store_true")
    ap.add_argument("--escudo-sempre", action="store_true",
                    help="conta a DP do escudo mesmo em região sem armadura (projétil)")
    ap.add_argument("--dp-informado", type=int, default=None)
    ap.add_argument("--rd-informado", type=int, default=None)
    ap.add_argument("--zera-escudo-com-dp", action="store_true")
    ap.add_argument("--projetil", action="store_true", help="ajusta só o texto da conta")
    a = ap.parse_args()

    ficha = None
    if a.arquivo_ficha:
        ficha = json.loads(Path(a.arquivo_ficha).read_text(encoding="utf-8"))
    elif a.ficha:
        ficha = json.loads(a.ficha)

    r = calcular({
        "alvo": a.alvo, "defesa": a.defesa, "defesa_valor": a.defesa_valor, "ficha": ficha,
        "local": json.loads(a.local), "tipo": a.tipo, "ht_alvo": a.ht_alvo,
        "manobra_defesa": a.manobra_defesa,
        "md": json.loads(a.md) if a.md else {"nome": "Normal", "defesas": 1, "mod": 0},
        "mod": a.mod, "mod_motivo": a.mod_motivo,
        "recuar": a.recuar, "sem_escudo": a.sem_escudo, "escudo_sempre": a.escudo_sempre,
        "dp_informado": a.dp_informado, "rd_informado": a.rd_informado,
        "dp_informado_zera_escudo": a.zera_escudo_com_dp, "projetil": a.projetil,
    })
    print("\n".join(r["saida"]))
    print("\nresultado: " + json.dumps(r["resultado"], ensure_ascii=False))


if __name__ == "__main__":
    main()
