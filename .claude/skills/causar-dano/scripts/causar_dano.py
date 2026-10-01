#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""causar-dano — o que acontece com o dano depois que o golpe passou pela defesa.

    causar_dano.py --alvo "Morto 3" --tipo perf --formula 2D+2 --local '{"nome":"Pescoço"}'
    causar_dano.py --arquivo payload.json --json

Ordem exata da MB, cap. 14 (e da casa), nesta folha:

1. rola o dano da arma (ou recebe `--dado` pronto) e soma o bônus de Ataque Total;
2. **dano mínimo**: corte e perfuração que acertam fazem pelo menos 1 ponto básico
   (MB, pág. 74) — vale ANTES da armadura;
3. teto da arma e ½D (arma de projétil), quando vêm no payload;
4. multiplicador do golpe fulminante;
5. armadura: RD do local, mais a RD natural do crânio onde houver; ignora armadura no
   golpe que a atravessa por fora;
6. multiplicador do tipo de dano e do local atingido;
7. teto do local (HT/, HT×, HT para perfurante em órgão vital) e o que se desperdiça;
8. membro incapacitado, e os efeitos terminais do pescoço (traqueia, decapitação).

**O que esta folha não faz:** não rola ataque, não resolve defesa (quem chegou aqui já
acertou), não decide queda/atordoamento/nocaute — isso é a `arbitrar-ferimento` —, e não
escreve em lugar nenhum. Devolve linhas prontas para o terminal e para o bloco da mesa, e
o número que a `registrar-acao` vai lançar em `saude.md`.

Quem rola dado é a skill `roll`: sem `--dado`, este script chama aquela. Com `--dado`, a
rolagem vem pronta — é assim que se testa a cascata sem depender de sorte.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
ROLL_PY = SKILLS / "roll" / "scripts" / "roll.py"

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

# MB, cap. 14: o que cada tipo de dano faz com o que passou da armadura.
TIPOS_DANO = {
    "cont": {"nome": "Contusão", "mult": 1.0,
             "como": "×1 depois da armadura — é o tipo que a RD mais segura"},
    "corte": {"nome": "Corte", "mult": 1.5,
              "como": "×1,5 depois que passar da armadura"},
    "perf": {"nome": "Perfuração", "mult": 2.0,
             "como": "×2 depois que passar da armadura"},
    "bal": {"nome": "Bala", "mult": 0.5,
            "como": "½ depois da armadura, mas ignora RD 2 ou menos"},
}

# Regra da casa (GURPS 4ª ed., MB Campanhas p. 552), aplicada pelo golpe no pescoço.
def efeitos_pescoco(chave, tipo, ferimento, ht, alvo, frontal=True):
    """[(linha do terminal, linha da mesa)] — nada aqui acontece fora do pescoço.

    Nas fichas desta campanha os PV são a HT, por isso os limiares falam em HT.
    """
    if chave != "pescoco" or not ht:
        return []
    meia = f"{ht / 2:g}".replace(".", ",")
    out = []
    if tipo == "cont" and frontal and ferimento > ht / 2:
        out.append((f"  ⇒ TRAQUEIA ESMAGADA: contusão pela frente acima de HT/2 ({meia}). "
                    f"Lesão incapacitante: {alvo} está SUFOCANDO (regra da casa, 4ª ed.).",
                    f"*TRAQUEIA ESMAGADA* (contusão pela frente > HT/2 = {meia}) — "
                    f"{alvo} está *sufocando*"))
    if tipo == "corte" and ferimento > 3 * ht:
        out.append((f"  ⇒ DECAPITAÇÃO POSSÍVEL: corte acima de 3×HT ({3 * ht}) num golpe só. "
                    f"O Mestre pode declarar {alvo} decapitado: morte automática.",
                    f"*Corte acima de 3×HT ({3 * ht})* — o Mestre pode declarar "
                    f"*DECAPITAÇÃO*"))
    return out


def _rola_dano(formula):
    try:
        espec = importlib.util.spec_from_file_location("roll", ROLL_PY)
        roll = importlib.util.module_from_spec(espec)
        espec.loader.exec_module(roll)
    except Exception as erro:
        raise SystemExit(f"Não consegui carregar a skill roll ({ROLL_PY}): {erro}")
    return roll.rolar(formula)


def calcular(p):
    """Devolve {"saida": [...], "mec": [...], "resultado": {...}}. Sem efeito colateral."""
    alvo = p.get("alvo", "o alvo")
    tipo = p.get("tipo", "cont")
    local = p.get("local") or {}
    chave = p.get("chave") or ""
    ht = int(p.get("ht_alvo") or 0)
    frontal = p.get("frontal", True)
    efeito = p.get("efeito") or {}
    saida, mec = [], []

    bonus = int(p.get("bonus_dano") or 0)
    mult_ful = int(p.get("mult_dano") or 1)

    if p.get("dado") is not None:
        bruto, linha = int(p["dado"]), None
    else:
        bruto, linha = _rola_dano(p.get("formula") or "1d")

    formula_txt = p.get("formula") or "1d"
    saida.append(f"\nDANO: {formula_txt}" + (f" ×{mult_ful}" if mult_ful > 1 else "")
                 + (f" +{bonus} (ataque total)" if bonus else ""))
    if linha:
        saida.append(f"  {linha.replace('**', '')}")
    mecanico = f"Dano: {linha.replace('**', '*') if linha else f'{bruto} (dado informado)'}"
    basico = bruto + bonus
    if bonus:
        saida.append(f"  +{bonus} do Ataque Total = {basico}")
        mecanico += f" +{bonus} Ataque Total = *{basico}*"

    # 2. dano mínimo antes da armadura (MB, pág. 74)
    if basico <= 0 and tipo in ("corte", "perf"):
        saida.append("  Dano minimo: corte e perfuracao que acertam fazem pelo menos 1 "
                     "(MB, pag. 74) -> 1")
        basico = 1
        mecanico += " → mínimo 1 (corte/perfuração)"

    # 3. teto da arma e ½D (projétil)
    teto_arma = p.get("teto_arma")
    if teto_arma is not None and basico > teto_arma:
        saida.append(f"  Teto da arma ({p.get('teto_arma_rotulo') or teto_arma} = "
                     f"{teto_arma}): o dano não passa disso → {teto_arma}")
        basico = teto_arma
        mecanico += f" → teto da arma {teto_arma}"
    if p.get("meia_dano"):
        basico //= 2
        meia_txt = f"{p['meia_de']:g}" if p.get("meia_de") is not None else "?"
        saida.append(f"  ½D: além de {meia_txt} m o dano cai à metade, "
                     f"arredondando para baixo → {basico}")
        mecanico += f" → metade (½D) = *{basico}*"

    # 4. golpe fulminante
    if mult_ful > 1:
        basico *= mult_ful
        saida.append(f"  ×{mult_ful} pelo golpe fulminante = {basico}")
        mecanico += f" ×{mult_ful} golpe fulminante = *{basico}*"
    mec.append(mecanico)

    # 5. armadura
    rd_local = int(p.get("rd_local") if p.get("rd_local") is not None else p.get("rd_total") or 0)
    rd_total = int(p.get("rd_total") or 0)
    if p.get("ignora_armadura"):
        passou = basico
        saida.append(f"  O golpe fulminante IGNORA a armadura: {passou} pontos entram inteiros.")
        mec.append(f"Armadura ignorada (golpe fulminante): {passou} entram")
    else:
        passou = max(0, basico - rd_total)
        detalhe_rd = f"RD {rd_local}" + (f" ({p['peca']})" if p.get("peca") else "")
        if local.get("rd_natural"):
            detalhe_rd += f" + RD {local['rd_natural']} do crânio"
        saida.append(f"  {detalhe_rd} → {passou} ponto(s) atravessam")
        mec.append(f"{detalhe_rd.replace(' (informado pelo Mestre)', '')} → {passou} passam")

    resultado = {"basico": basico, "passou": passou, "ferimento": 0, "perdido": 0,
                 "membro_incapacitado": False, "armadura_segurou": passou <= 0,
                 "ignora_armadura": bool(p.get("ignora_armadura"))}
    if passou <= 0:
        saida.append(f"\nA armadura segurou tudo. {alvo} não perde ponto de vida nenhum.")
        return {"saida": saida, "mec": mec, "resultado": resultado}

    # 6. multiplicador do local e do tipo
    ferimento, explica = passou, []
    if local.get("mult_todos"):
        ferimento = passou * local["mult_todos"]
        explica.append(f"×{local['mult_todos']} por atingir {local.get('nome', '').lower()} "
                       f"(vale para qualquer tipo de dano)")
    elif tipo == "perf" and local.get("mult_perf"):
        ferimento = passou * local["mult_perf"]
        explica.append(f"×{local['mult_perf']} — perfurante nos órgãos vitais")
    elif (local.get("mult_tipo") or {}).get(tipo):
        m = local["mult_tipo"][tipo]
        ferimento = int(passou * m)
        nome_tipo = TIPOS_DANO.get(tipo, {}).get("nome", tipo)
        explica.append(f"{nome_tipo} no {local.get('nome', '').lower()}: "
                       f"×{str(m).replace('.0', '').replace('.', ',')} do que passar da "
                       f"armadura (regra da casa, 4ª ed.)")
    elif local.get("incapacita") and tipo == "perf":
        explica.append("perfurante em membro NÃO ganha bônus de dano (MB, cap. 14)"
                       + (" — flecha no pé incomoda, flecha na cabeça mata"
                          if p.get("nota_membro") else ""))
    else:
        m = TIPOS_DANO.get(tipo, {"mult": 1.0})["mult"]
        if m != 1.0:
            ferimento = int(passou * m)
            explica.append(f"{TIPOS_DANO[tipo]['nome']}: {TIPOS_DANO[tipo]['como']}")
    for e in explica:
        saida.append(f"  {e} → {ferimento}")
        mec.append(f"{e[0].upper() + e[1:]} → *{ferimento}*")

    # 7. teto do local
    perdido = 0
    if ht:
        teto = None
        if local.get("teto_div_ht"):
            teto = ht // local["teto_div_ht"]
            rotulo = f"HT/{local['teto_div_ht']}"
        elif local.get("teto_mult_ht"):
            teto = ht * local["teto_mult_ht"]
            rotulo = f"HT×{local['teto_mult_ht']}"
        elif local.get("teto_perf_ht") and tipo == "perf":
            teto = ht
            rotulo = "HT"
        if teto is not None and ferimento > teto:
            perdido = ferimento - teto
            saida.append(f"  Teto do local ({rotulo} = {teto}): {perdido} ponto(s) "
                         f"desperdiçados — o {p.get('trespassa_por') or 'golpe'} trespassa")
            ferimento = teto
            mec.append(f"Teto do local ({rotulo} = {teto}): {perdido} desperdiçado(s)")
            if local.get("incapacita"):
                resultado["membro_incapacitado"] = True
                saida.append(f"  ⇒ {local.get('nome', 'O membro').upper()} INCAPACITADO: "
                             f"{alvo} perde o uso do membro na hora, e fica ATORDOADO "
                             f"automaticamente.")
                mec.append(f"*{local.get('nome')} INCAPACITADO* — {alvo} fica atordoado")

    if efeito.get("incapacita_membro") and local.get("incapacita") and not resultado["membro_incapacitado"]:
        saida.append(f"  ⇒ Pelo golpe fulminante, o membro fica incapacitado seja qual for o dano.")
        mec.append(f"*{local.get('nome')} INCAPACITADO* pelo golpe fulminante")
        resultado["membro_incapacitado"] = True

    # 8. o veredito em PV, e o que o pescoço acrescenta
    resultado["ferimento"] = ferimento
    resultado["perdido"] = perdido
    saida.append(f"\n**{alvo} perde {ferimento} ponto(s) de vida.**"
                 + (f" (mais {perdido} desperdiçados)" if perdido else ""))
    if local.get("obs"):
        saida.append(f"  {local['obs']}")
    for terminal, mesa in efeitos_pescoco(chave, tipo, ferimento, ht, alvo, frontal=frontal):
        saida.append(terminal)
        mec.append(mesa)

    return {"saida": saida, "mec": mec, "resultado": resultado}


def main():
    ap = argparse.ArgumentParser(description="Cascata de dano depois do golpe (MB, cap. 14).")
    ap.add_argument("--alvo", default="o alvo")
    ap.add_argument("--tipo", default="cont", choices=sorted(TIPOS_DANO))
    ap.add_argument("--formula", default="1d", help="fórmula de dano, ex. 2D+2")
    ap.add_argument("--dado", type=int, default=None,
                    help="dano já rolado (sem isto, rola pela skill roll)")
    ap.add_argument("--bonus-dano", type=int, default=0, help="Ataque Total")
    ap.add_argument("--mult-dano", type=int, default=1, help="multiplicador do fulminante")
    ap.add_argument("--ignora-armadura", action="store_true")
    ap.add_argument("--rd-total", type=int, default=0)
    ap.add_argument("--rd-local", type=int, default=None)
    ap.add_argument("--peca", default="", help="de onde veio a RD")
    ap.add_argument("--local", default="{}", help="JSON do local atingido (entrada de LOCAIS)")
    ap.add_argument("--ht-alvo", type=int, default=0)
    ap.add_argument("--teto-arma", type=int, default=None)
    ap.add_argument("--teto-arma-rotulo", default="")
    ap.add_argument("--meia-dano", action="store_true")
    ap.add_argument("--meia-de", type=float, default=None)
    ap.add_argument("--chave", default="")
    ap.add_argument("--nao-frontal", action="store_true")
    ap.add_argument("--trespassa-por", default="golpe",
                    help="o que trespassa quando o teto do local corta o dano: golpe, projétil")
    ap.add_argument("--nota-membro", action="store_true",
                    help="acrescenta a nota da flecha no pé ao perfurante em membro")
    ap.add_argument("--efeito", default="{}", help="JSON do efeito do golpe fulminante")
    ap.add_argument("--arquivo", default="", help="payload JSON completo (sobrepõe as flags)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    p = {}
    if args.arquivo:
        p = json.loads(Path(args.arquivo).read_text(encoding="utf-8"))
    p.update({
        "alvo": args.alvo, "tipo": args.tipo, "formula": args.formula, "dado": args.dado,
        "bonus_dano": args.bonus_dano, "mult_dano": args.mult_dano,
        "ignora_armadura": args.ignora_armadura, "rd_total": args.rd_total,
        "rd_local": args.rd_local, "peca": args.peca or None,
        "local": json.loads(args.local), "ht_alvo": args.ht_alvo,
        "teto_arma": args.teto_arma, "teto_arma_rotulo": args.teto_arma_rotulo,
        "meia_dano": args.meia_dano, "meia_de": args.meia_de, "chave": args.chave,
        "frontal": not args.nao_frontal, "efeito": json.loads(args.efeito),
        "trespassa_por": args.trespassa_por, "nota_membro": args.nota_membro,
    })

    r = calcular(p)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print("\n".join(r["saida"]))
        if r["mec"]:
            print("\nConta da mesa:")
            for l in r["mec"]:
                print("  " + l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
