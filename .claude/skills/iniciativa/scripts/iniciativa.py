#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resolve surpresa e iniciativa pelo MB, cap. 14 ("Ataques de Surpresa e Iniciativa").

    iniciativa.py --surpresa parcial \
      --a "Personagens" --a-membros "Comam Obabaroy*, Irmão Kaelric, Jah Kagadu" \
      --b "Mortos-vivos" --b-membros "Morto-Vivo 1" --b-iq 8 --b-sem-lider

O `*` marca o líder do lado. Membro que exista em personagens/<slug>/personagem.json tem
os modificadores lidos da ficha; para NPC, passe --a-iq/--b-iq e as flags.

Os dados sao rolados AQUI. Quem usa a skill relata o que saiu — nunca inventa resultado.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
REGISTRAR_PY = SKILLS / "registrar-acao" / "scripts" / "registrar_acao.py"

# Quem rola dado neste repositorio e a skill `roll`, uma so. Ver .claude/skills/roll/.
ROLL_PY = SKILLS / "roll" / "scripts" / "roll.py"
try:
    _spec = importlib.util.spec_from_file_location("roll", ROLL_PY)
    _roll = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_roll)
except Exception as erro:
    raise SystemExit(f"Não consegui carregar a skill roll ({ROLL_PY}): {erro}")

# Quem sabe quem é cada nome e a folha `contexto`, uma so. Ver .claude/skills/contexto/.
CTX_PY = SKILLS / "contexto" / "scripts" / "contexto.py"
try:
    _spec = importlib.util.spec_from_file_location("contexto", CTX_PY)
    ctx = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(ctx)
except Exception as erro:
    raise SystemExit(f"Não consegui carregar a skill contexto ({CTX_PY}): {erro}")

# O console do Windows e cp1252 e engasga com seta, travessao e afins. A saida daqui e
# feita para ser copiada, entao tem de sair inteira.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass


d6 = _roll.d6


def ler_ficha(nome, raiz):
    """Modificadores que importam, pela folha de contexto. None se nao for PJ.

    Antes esta skill tinha um leitor proprio, de caminho exato: "Kaelric" nao achava
    irmao-kaelric e "Reflexos em Combate" era procurado como texto solto na lista de
    vantagens. O contexto resolve nome com fuzzy e ler vantagem por nome de verdade.
    """
    d = ctx.ler_ficha(nome, raiz)
    if not d:
        return None
    tatica = ctx.pericia(d, "Tática") or ctx.pericia(d, "Tatica") or (0,)
    return {
        "nome": d.get("nome", nome),
        "iq": int(ctx.atributos(d).get("IQ") or 0),
        "reflexos": ctx.nivel_vantagem(d, "Reflexos em Combate") is not None,
        "tatica": tatica[0],
        "ficha": True,
    }


def montar_lado(nome_lado, membros_txt, raiz, iq, reflexos, tatica, sem_lider, animais):
    membros, lider = [], None
    for bruto in [m.strip() for m in membros_txt.split(",") if m.strip()]:
        e_lider = bruto.endswith("*")
        nome = bruto.rstrip("*").strip()
        dados = ler_ficha(nome, raiz) or {"nome": nome, "iq": 0, "reflexos": False,
                                          "tatica": 0, "ficha": False}
        membros.append(dados)
        if e_lider:
            lider = dados
    if lider is None and membros and not sem_lider:
        lider = membros[0]

    # o que veio pela linha de comando manda sobre o lider sem ficha
    if lider and not lider["ficha"]:
        if iq:
            lider["iq"] = iq
        if reflexos:
            lider["reflexos"] = True
        if tatica:
            lider["tatica"] = tatica
    return {"nome": nome_lado, "membros": membros, "lider": lider,
            "sem_lider": sem_lider or lider is None, "animais": animais}


def modificadores(lado, outro):
    """Modificadores do MB. Devolve (total, [(texto p/ Mestre, texto p/ jogador)])."""
    mods, total = [], 0
    lider = lado["lider"]

    if lado["sem_lider"]:
        if lado["animais"]:
            mods.append(("sem líder, mas são animais — sem redutor", None))
        else:
            total -= 2
            mods.append(("-2 grupo sem líder", "sem ninguém no comando"))
    if lider and lider["reflexos"]:
        total += 2
        mods.append((f"+2 {lider['nome']} tem Reflexos em Combate e lidera",
                     "Reflexos em Combate"))
    elif any(m["reflexos"] for m in lado["membros"]):
        total += 1
        quem = next(m["nome"] for m in lado["membros"] if m["reflexos"])
        mods.append((f"+1 {quem} tem Reflexos em Combate (não é o líder)",
                     f"{quem} tem Reflexos em Combate"))

    if lider and outro["lider"] and lider["iq"] > outro["lider"]["iq"] > 0:
        total += 1
        mods.append((f"+1 líder mais inteligente (IQ {lider['iq']} contra "
                     f"{outro['lider']['iq']})", "cabeça mais fria"))
    if lider and lider["tatica"]:
        b = 2 if lider["tatica"] >= 20 else 1
        total += b
        mods.append((f"+{b} Tática {lider['tatica']}", "Tática"))
    return total, mods


def gravar(raiz, resumo):
    """Entrega o ato à `registrar-acao` — esta skill não escreve em lugar nenhum.

    Antes havia uma copia de `registrar()` em cinco skills de calculo, cada uma montando
    o proprio `campanha.py acontecimento`. A fila de lancamentos agora e de uma so.
    """
    if not REGISTRAR_PY.is_file():
        return False, "skill registrar-acao nao encontrada"
    ato = {"resumo": f"[iniciativa] {resumo}", "jogadas": []}
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(REGISTRAR_PY), "--stdin"],
                       input=json.dumps(ato, ensure_ascii=False),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=60, env=env, cwd=str(raiz))
    linhas = [l for l in (r.stdout or "").splitlines() if l.startswith("[")]
    return r.returncode == 0, "\n        ".join(linhas) or (r.stderr or "").strip()


def main():
    ap = argparse.ArgumentParser(description="Surpresa e iniciativa (MB, cap. 14).")
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--surpresa", choices=["nenhuma", "parcial", "total"],
                    default="parcial",
                    help="parcial = rola iniciativa; total = 1d de paralisia")
    ap.add_argument("--surpreendido", default="b",
                    help="Na surpresa total, que lado foi pego: a ou b")
    for L in "ab":
        ap.add_argument(f"--{L}", default=f"Lado {L.upper()}", help="Nome do lado")
        ap.add_argument(f"--{L}-membros", default="", help="Nomes, vírgula; * = líder")
        ap.add_argument(f"--{L}-iq", type=int, default=0)
        ap.add_argument(f"--{L}-reflexos", action="store_true")
        ap.add_argument(f"--{L}-tatica", type=int, default=0)
        ap.add_argument(f"--{L}-sem-lider", action="store_true")
        ap.add_argument(f"--{L}-animais", action="store_true")
    ap.add_argument("--gravar", action="store_true",
                    help="Registra o resultado no capítulo atual da campanha")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    g = vars(args)

    lados = {}
    for L in "ab":
        lados[L] = montar_lado(g[L], g[f"{L}_membros"], raiz, g[f"{L}_iq"],
                               g[f"{L}_reflexos"], g[f"{L}_tatica"],
                               g[f"{L}_sem_lider"], g[f"{L}_animais"])
    A, B = lados["a"], lados["b"]

    print("=" * 66)
    for lado in (A, B):
        quem = ", ".join(m["nome"] + (" (líder)" if m is lado["lider"] else "")
                         for m in lado["membros"]) or "—"
        print(f"{lado['nome']}: {quem}")
        for m in lado["membros"]:
            if m["ficha"]:
                extra = []
                if m["reflexos"]:
                    extra.append("Reflexos em Combate")
                if m["tatica"]:
                    extra.append(f"Tática {m['tatica']}")
                print(f"   ficha: {m['nome']} — IQ {m['iq']}"
                      + (", " + ", ".join(extra) if extra else ""))
            else:
                print(f"   sem ficha: {m['nome']} — use --{'a' if lado is A else 'b'}-iq "
                      "e as flags se ele tiver modificador")
    print("=" * 66)

    if args.surpresa == "nenhuma":
        print("\nSem surpresa: não se rola iniciativa (MB, cap. 14).")
        print("Vá direto para a ordem de turnos, por maior Deslocamento.")
        whats = ("*Ninguém foi pego de surpresa.* O combate começa pela ordem normal de "
                 "turnos.")
        resumo = "Sem surpresa; combate na ordem normal."

    elif args.surpresa == "total":
        alvo = A if args.surpreendido == "a" else B
        dado = d6()[0]
        imunes = [m["nome"] for m in alvo["membros"] if m["reflexos"]]
        print(f"\nSURPRESA TOTAL sobre {alvo['nome']}")
        print(f"  Paralisia: 1d = {dado} → {dado} segundo(s) sem agir.")
        if imunes:
            print(f"  Nunca ficam paralisados (Reflexos em Combate): {', '.join(imunes)}")
        print("  Depois disso: teste de IQ no início de cada turno (+6 com Reflexos).")
        print("  Sucesso vale pelo resto do combate; falha = atordoado, sem defesa ativa.")
        if imunes:
            plural = len(imunes) > 1
            linha_imunes = (f"\n\n{', '.join(imunes)} "
                            + ("não congelam — reagem" if plural
                               else "não congela — reage")
                            + " desde o primeiro segundo.")
        else:
            linha_imunes = ""
        whats = (f"*Vocês foram pegos completamente de surpresa.*\n\n"
                 f"Rolei 1d para a paralisia: *{dado}*. Ninguém consegue reagir por "
                 f"{dado} segundo{'s' if dado > 1 else ''}.{linha_imunes}\n\n"
                 "Depois disso, cada um testa _IQ_ no começo do turno para se recuperar. "
                 "Quem passa, age normalmente até o fim da luta. Quem falha continua "
                 "atordoado — *e sem defesa ativa*.")
        resumo = (f"Surpresa total sobre {alvo['nome']}: paralisia de {dado}s"
                  + (f" (imunes: {', '.join(imunes)})" if imunes else ""))

    else:
        ma, expa = modificadores(A, B)
        mb, expb = modificadores(B, A)
        da, db = d6()[0], d6()[0]
        ta, tb = da + ma, db + mb

        print("\nSURPRESA PARCIAL — teste de iniciativa (um dado por lado)\n")
        for lado, mods, exp, dado, tot in ((A, ma, expa, da, ta), (B, mb, expb, db, tb)):
            nome_l = lado["lider"]["nome"] if lado["lider"] else "sem líder"
            sinal = f"{mods:+d}" if mods else ""
            print(f"  {lado['nome']} ({nome_l}): 1d{sinal} = {dado}{sinal} = *{tot}*")
            for e, _ in exp:
                print(f"      {e}")
            if not exp:
                print("      sem modificadores")
        if ta == tb:
            print(f"\n  EMPATE ({ta} a {tb}) → ninguém foi pego de surpresa.")
            whats = (f"*Empate na iniciativa* — {ta} a {tb}.\n\n"
                     "Ninguém foi pego de surpresa. O combate começa normalmente.")
            resumo = f"Iniciativa empatada em {ta}; ninguém surpreendido."
        else:
            venc, perd = (A, B) if ta > tb else (B, A)
            print(f"\n  {venc['nome']} ganha a iniciativa ({max(ta,tb)} a {min(ta,tb)}).")
            print(f"  {perd['nome']} fica mentalmente atordoado: teste de IQ por turno, "
                  "com +1 acumulativo a partir do segundo.")
            def frase(lado, dado, mods, exp):
                quem = (f"*{lado['lider']['nome']}*" if lado["lider"]
                        else f"Os *{lado['nome']}*")
                porques = [p for _, p in exp if p]
                por = f" ({', '.join(porques)})" if porques else ""
                verbo = "rolou" if lado["lider"] else "rolaram"
                tirou = "tirou" if lado["lider"] else "tiraram"
                return (f"{quem}{por} {verbo} 1d{f'{mods:+d}' if mods else ''} "
                        f"e {tirou} *{dado + mods}*")
            whats = (f"{frase(A, da, ma, expa)}.\n"
                     f"{frase(B, db, mb, expb)}.\n\n"
                     f"*{venc['nome']}: vocês começam.*\n\n"
                     if venc is A else
                     f"{frase(A, da, ma, expa)}.\n"
                     f"{frase(B, db, mb, expb)}.\n\n"
                     f"*{venc['nome']} começa.*\n\n")
            whats += (f"{perd['nome']} fica atordoado: só age depois de passar num teste "
                      "de _IQ_ no início do turno, e ganha +1 a cada turno que passa.")
            resumo = (f"Iniciativa: {venc['nome']} venceu {max(ta,tb)} a {min(ta,tb)}; "
                      f"{perd['nome']} atordoado.")

    print("\n" + "-" * 66)
    print("PARA O WHATSAPP (copie o bloco abaixo):")
    print("-" * 66)
    print(whats)
    print("-" * 66)

    if args.gravar:
        ok, saida = gravar(raiz, resumo)
        if ok:
            print("Entregue à registrar-acao:\n        " + saida)
        else:
            print(f"AVISO: não registrei — {saida}")
    else:
        print("(não gravado — use --gravar para entregar à registrar-acao)")


if __name__ == "__main__":
    main()
