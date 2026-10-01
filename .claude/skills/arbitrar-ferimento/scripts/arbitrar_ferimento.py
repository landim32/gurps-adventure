#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arbitrar-ferimento — o que o ferimento faz com quem o recebeu.

Chamada depois da `causar-dano`, com o número pronto. Decide, na ordem:

1. redutor por ferimento do próximo turno (e a Hipoalgia, que o anula);
2. teste de HT para não cair, quando o golpe passou de metade da HT;
3. atordoamento (-4 nas defesas ativas) que vem junto da queda, ou do golpe fulminante;
4. teste de HT contra nocaute na cabeça, ou contundente nos órgãos vitais;
5. pelo crânio exposto: nocaute acima de HT/2, atordoamento acima de HT/3.

    arbitrar_ferimento.py --alvo "Morto 3" --ferimento 7 --ht-alvo 12 --chave cabeca \
      --tipo cont

Não rola ataque, não resolve defesa, não calcula dano, não escreve em lugar nenhum.
Quem rola dado é a skill `roll`; quem lança o que sobrou no capítulo é a `registrar-acao`.
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

try:
    _espec = importlib.util.spec_from_file_location("contexto", CTX_PY)
    ctx = importlib.util.module_from_spec(_espec)
    _espec.loader.exec_module(ctx)
except Exception as erro:
    raise SystemExit(f"Não consegui carregar a skill contexto ({CTX_PY}): {erro}")


def _txt_dados(d):
    return "[" + ", ".join(map(str, d)) + "]"


def _trio(txt):
    """'4,2,6' ou '[4, 2, 6]' -> [4, 2, 6]; vazio -> None, e a folha rola em vez de aceitar."""
    if not txt:
        return None
    n = [int(x) for x in re.findall(r"\d+", txt)]
    return n or None


def _rola_d6():
    try:
        espec = importlib.util.spec_from_file_location("roll", ROLL_PY)
        roll = importlib.util.module_from_spec(espec)
        espec.loader.exec_module(roll)
    except Exception as erro:
        raise SystemExit(f"Não consegui carregar a skill roll ({ROLL_PY}): {erro}")
    return roll.d6(3)


def calcular(p):
    alvo = p.get("alvo", "o alvo")
    fer = int(p.get("ferimento") or 0)
    ht = int(p.get("ht_alvo") or 0)
    chave = p.get("chave") or ""
    tipo = p.get("tipo", "cont")
    efeito = p.get("efeito") or {}
    fd = p.get("ficha")
    proje = bool(p.get("projetil"))
    verbo = "Tiro" if proje else "Golpe"
    verbo2 = "tiro" if proje else "golpe"
    saida, mec = [], []
    res = {"hipoalgia": False, "redutor_ferimento": 0, "caiu": False,
           "atordoado": False, "nocauteado": False}

    if not ht:
        saida.append(f"\nSem a HT de {alvo} não dá para testar "
                     + ("queda, nocaute nem os tetos do local." if proje
                        else "queda, atordoamento nem os tetos do local.")
                     + " Passe --alvo-ht (está no npcs.md).")
        return {"saida": saida, "mec": mec, "resultado": res}

    saida.append(f"\nCONSEQUÊNCIAS (HT {ht}):")

    # 1. redutor por ferimento
    hipo = bool(p.get("hipoalgia")) or (fd is not None
                                        and ctx.nivel_vantagem(fd, "hipoalgia") is not None)
    if hipo:
        res["hipoalgia"] = True
        saida.append(f"  {alvo} tem Hipoalgia: **não** sofre o redutor por ferimento."
                     + ("" if proje else " Continua atacando com o NH cheio."))
    else:
        res["redutor_ferimento"] = fer
        saida.append(f"  No próximo turno, {alvo} {'age' if proje else 'ataca'} com -{fer} "
                     f"(redutor por ferimento).")

    # 2 e 3. queda e o atordoamento que vem junto
    if fer > ht // 2:
        d = p.get("dado_queda")
        dd = d if isinstance(d, (list, tuple)) else _rola_d6()
        tq = sum(dd)
        ok = tq <= ht
        res["caiu"] = not ok
        res["atordoado"] = True
        saida.append(f"  Perdeu mais da metade da HT num {verbo2} só: teste de HT para "
                     f"não cair.")
        saida.append(f"    3d [{', '.join(map(str, dd))}] = {tq} contra {ht} — "
                     + ("continua de pé" if ok else "CAIU"))
        mec.append(f"Perdeu mais de HT/2: teste de HT {ht} para não cair, "
                   f"3d {_txt_dados(dd)} = *{tq}* → "
                   + ("de pé" if ok else "*CAIU*") + "; *ATORDOADO* (-4 nas defesas)")
        saida.append(f"  Caindo ou não, {alvo} fica ATORDOADO: -4 "
                     + ("em todas as" if not proje else "nas")
                     + " defesas ativas no turno seguinte, e testa HT no início de cada "
                       "turno para se recuperar.")
    elif efeito.get("atordoa"):
        res["atordoado"] = True
        saida.append(f"  {alvo} fica ATORDOADO pelo golpe fulminante: -4 nas defesas ativas"
                     + ("" if proje else ", e testa HT a cada turno para sair") + ".")
        mec.append("*ATORDOADO* pelo golpe fulminante (-4 nas defesas)")

    # 4. nocaute na cabeça / contundente nos vitais
    if chave in ("cabeca", "cerebro") or (chave == "orgaos-vitais" and tipo == "cont"):
        d = p.get("dado_nocaute")
        dn = d if isinstance(d, (list, tuple)) else _rola_d6()
        tnk = sum(dn)
        ok = tnk <= ht
        res["nocauteado"] = not ok
        saida.append(f"  {verbo} na cabeça (ou contundente nos vitais): teste de HT "
                     f"contra nocaute.")
        saida.append(f"    3d [{', '.join(map(str, dn))}] = {tnk} contra {ht} — "
                     + ("aguentou" if ok else "NOCAUTEADO"))
        mec.append(f"Teste de HT {ht} contra nocaute: 3d {_txt_dados(dn)} = *{tnk}* → "
                   + ("aguentou" if ok else "*NOCAUTEADO*"))

    # 5. pelo crânio exposto
    if chave == "cerebro":
        if fer > ht // 2:
            res["nocauteado"] = True
            saida.append("  Perda acima de HT/2 pelo crânio: NOCAUTEADO.")
            mec.append("Perda acima de HT/2 pelo crânio: *NOCAUTEADO*")
        elif fer > ht // 3:
            res["atordoado"] = True
            saida.append("  Perda acima de HT/3 pelo crânio: ATORDOADO.")
            mec.append("Perda acima de HT/3 pelo crânio: *ATORDOADO*")

    return {"saida": saida, "mec": mec, "resultado": res}


def main():
    ap = argparse.ArgumentParser(description="Consequências do ferimento (MB, cap. 14/15).")
    ap.add_argument("--alvo", required=True)
    ap.add_argument("--ferimento", type=int, required=True)
    ap.add_argument("--ht-alvo", type=int, default=0)
    ap.add_argument("--chave", default="", help="região atingida: cabeca, cerebro, "
                                                "orgaos-vitais, pescoco…")
    ap.add_argument("--tipo", default="cont", choices=["cont", "corte", "perf", "bal"])
    ap.add_argument("--ficha", default="")
    ap.add_argument("--hipoalgia", action="store_true")
    ap.add_argument("--projetil", action="store_true")
    ap.add_argument("--efeito", default="{}")
    ap.add_argument("--dado-queda", default="", help="3d já rolados, p/ testar sem sorte")
    ap.add_argument("--dado-nocaute", default="", help="3d já rolados, p/ testar sem sorte")
    a = ap.parse_args()

    r = calcular({
        "alvo": a.alvo, "ferimento": a.ferimento, "ht_alvo": a.ht_alvo, "chave": a.chave,
        "tipo": a.tipo, "hipoalgia": a.hipoalgia, "projetil": a.projetil,
        "efeito": json.loads(a.efeito),
        "ficha": json.loads(a.ficha) if a.ficha else None,
        "dado_queda": _trio(a.dado_queda), "dado_nocaute": _trio(a.dado_nocaute),
    })
    print("\n".join(r["saida"]))
    if r["mec"]:
        print("\nConta da mesa:")
        for l in r["mec"]:
            print("  " + l)
    print("\nresultado: " + json.dumps(r["resultado"], ensure_ascii=False))


if __name__ == "__main__":
    main()
