#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Junta num bloco so o estado de cada personagem: dinheiro, PV, Fadiga e ferimentos.

    status_atual.py
    status_atual.py --npcs        # inclui os NPCs feridos ou mortos
    status_atual.py --combate     # acrescenta defesas e Deslocamento

Nao rola nada e nao escreve nada: le a bolsa, a saude e as fichas, e monta o texto
pronto para colar no WhatsApp. Quem mantem esses arquivos e a skill `campanha`.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

CAMPANHA_PY = Path(".claude/skills/campanha/scripts/campanha.py")
PERSONAGENS = Path("personagens")

# O console do Windows e cp1252 e engasga com acento, seta e travessao.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass


def carregar_campanha(raiz):
    """Importa o campanha.py: bolsa e saude tem um formato so, e mora la."""
    script = raiz / CAMPANHA_PY
    if not script.is_file():
        raise SystemExit("Nao achei a skill campanha em {0}".format(script))
    spec = importlib.util.spec_from_file_location("campanha", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fichas(raiz):
    """(nome, jogador, dados) de cada personagem com ficha, em ordem alfabetica."""
    fora = []
    base = raiz / PERSONAGENS
    if not base.is_dir():
        return fora
    for pasta in sorted(x for x in base.glob("*") if x.is_dir()):
        f = pasta / "personagem.json"
        if not f.is_file():
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        fora.append((d.get("nome") or pasta.name, d.get("jogador") or "", d))
    return sorted(fora, key=lambda x: x[0].lower())


def dinheiro(camp, bolsa, nome):
    for _, quem, ls in bolsa:
        if camp.slug(quem) == camp.slug(nome):
            return sum(v for _, v, _ in ls)
    return None


def saude(camp, registros, raiz, nome, pj=True):
    for _, quem, ls in registros:
        if camp.slug(quem) == camp.slug(nome):
            pv_max, fad_max = camp.maximos_da_ficha(raiz, nome) if pj else (None, None)
            return camp.resumo_saude(ls, pv_max, fad_max)
    return None


def cifra(v):
    return ("-$" + str(-v)) if v < 0 else ("$" + str(v))


def main():
    ap = argparse.ArgumentParser(
        description="Estado de cada personagem, pronto para o WhatsApp.")
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--npcs", action="store_true",
                    help="Inclui os NPCs que têm ferimento ou estado anotado")
    ap.add_argument("--combate", action="store_true",
                    help="Acrescenta Deslocamento e defesas ativas de cada um")
    ap.add_argument("--nota", action="append", default=[], metavar="NOME: TEXTO",
                    help="Condição lida do mundo.md, ex.: "
                         "--nota \"Negrum: procurado em Wallace\". Repita à vontade")
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()
    camp = carregar_campanha(raiz)
    p = raiz / "campanha"
    if not (p / "README.md").is_file():
        raise SystemExit("Nao ha campanha ativa.")

    meta, _ = camp.ler_meta(p)
    bolsa = camp.ler_bolsa(p / camp.BOLSA)
    registros = camp.ler_saude(p / camp.SAUDE)

    cap = (meta.get("Capítulo atual") or "").strip()
    pasta_plano = camp.pasta_do_capitulo(p, cap) if cap else None
    titulo_cap = camp.titulo_do_readme(pasta_plano) if pasta_plano else ""
    local = (camp.meta_do_capitulo(pasta_plano).get("Local") or "").strip() \
        if pasta_plano else ""

    w = ["*STATUS DO GRUPO* — {0}".format(meta.get("Campanha", "?"))]
    if titulo_cap:
        w.append("_{0}{1}_".format(titulo_cap, " · " + local if local else ""))
    w.append("")

    for nome, jogador, d in fichas(raiz):
        w.append("*{0}*{1}".format(nome, " ({0})".format(jogador) if jogador else ""))
        est = saude(camp, registros, raiz, nome)
        if est:
            pv_txt, fad_txt, estados = est
        else:
            pv_txt = "{0}/{0}".format(d.get("pontos_vida"))
            fad_txt = "{0}/{0}".format(d.get("fadiga"))
            estados = []
        linha = "PV {0} · Fadiga {1}".format(pv_txt, fad_txt)
        moedas = dinheiro(camp, bolsa, nome)
        if moedas is not None:
            linha += " · {0}".format(cifra(moedas))
        w.append(linha)
        if args.combate:
            da = d.get("defesas_ativas") or {}
            w.append("Desloc {0} · Esquiva {1} · Aparar {2} · Bloqueio {3}".format(
                d.get("deslocamento"), da.get("esquiva"), da.get("aparar"),
                da.get("bloqueio")))
        for e in estados:
            w.append("_{0}_".format(e))
        for nota in args.nota:
            quem, _, texto = nota.partition(":")
            if texto.strip() and camp.slug(quem) in camp.slug(nome):
                w.append("_{0}_".format(texto.strip()))
        w.append("")

    if args.npcs:
        npcs = [(quem, ls) for sec, quem, ls in registros if sec == "NPCs"]
        if npcs:
            w.append("*NPCs*")
            for quem, ls in sorted(npcs, key=lambda x: x[0].lower()):
                pv_txt, fad_txt, estados = camp.resumo_saude(ls, None, None)
                marca = "; ".join(estados) or "sem ferimento anotado"
                pv = ("" if pv_txt == "—"
                      else " ({0} de dano)".format(-int(pv_txt))
                      if pv_txt.lstrip("-").isdigit() and int(pv_txt) < 0
                      else " (PV {0})".format(pv_txt))
                w.append("*{0}*{1} — _{2}_".format(quem, pv, marca))
            w.append("")

    bloco = "\n".join(w).rstrip()
    risco = "-" * 70
    print(risco)
    print("PARA O WHATSAPP (copie o bloco abaixo):")
    print(risco)
    print(bloco)
    print(risco)
    print("Fontes: {0}, {1}, e as fichas em personagens/.".format(
        (p / camp.BOLSA).as_posix(), (p / camp.SAUDE).as_posix()))


if __name__ == "__main__":
    main()
