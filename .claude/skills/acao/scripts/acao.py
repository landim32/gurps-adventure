#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Junta tudo o que e preciso saber para arbitrar a acao declarada por um jogador.

    acao.py contexto --quem Ricardo
    acao.py contexto --quem "Jah" --json

Quem decide o que a acao exige (perícia, modificador, qual skill chamar) e o modelo;
o script cuida do que da errado a mao: achar de quem e o personagem, as pericias e o NH
que ele de fato tem, a reacao que cada NPC ja teve com ele, e os arquivos do capitulo.

Nao rola dado e nao escreve nada: a resolucao e das skills roll/teste-nh/disputa-nh/
combate, e o registro e da skill campanha.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

CAMPANHA_PY = Path(".claude/skills/campanha/scripts/campanha.py")
PERSONAGENS = Path("personagens")

# O console do Windows e cp1252 e engasga com acento, seta e travessao.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass


def simples(texto):
    """Sem acento, minusculo — para comparar nome digitado com nome de ficha."""
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t.lower()).strip()


def estado(raiz):
    script = raiz / CAMPANHA_PY
    if not script.is_file():
        return {"ativa": False}
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        r = subprocess.run(
            [sys.executable, str(script), "--raiz", str(raiz), "estado", "--json"],
            capture_output=True, text=True, encoding="utf-8", timeout=30, env=env)
        return json.loads(r.stdout) if r.returncode == 0 else {"ativa": False}
    except Exception:
        return {"ativa": False}


def fichas(raiz):
    """Todas as fichas do repositorio: (pasta, dados do personagem.json)."""
    fora = []
    base = raiz / PERSONAGENS
    if not base.is_dir():
        return fora
    for pasta in sorted(x for x in base.glob("*") if x.is_dir()):
        f = pasta / "personagem.json"
        if not f.is_file():
            continue
        try:
            fora.append((pasta, json.loads(f.read_text(encoding="utf-8"))))
        except Exception:
            continue
    return fora


def achar_personagem(raiz, quem):
    """Resolve por nome do JOGADOR ou do PERSONAGEM, inteiro ou em parte."""
    alvo = simples(quem)
    if not alvo:
        raise SystemExit("Diga de quem é a ação: --quem \"Ricardo\" ou --quem \"Jah\".")
    todos = fichas(raiz)
    if not todos:
        raise SystemExit("Nenhuma ficha em personagens/.")
    exatos, parciais = [], []
    for pasta, d in todos:
        campos = [simples(d.get("jogador")), simples(d.get("nome")), simples(pasta.name)]
        if alvo in campos:
            exatos.append((pasta, d))
        elif any(c and (alvo in c or c.startswith(alvo)) for c in campos):
            parciais.append((pasta, d))
        elif any(alvo in p for c in campos for p in c.split()):
            parciais.append((pasta, d))
    achados = exatos or parciais
    if not achados:
        lista = ", ".join(f"{d.get('nome')} ({d.get('jogador')})" for _, d in todos)
        raise SystemExit(f"Nao achei \"{quem}\". Existem: {lista}")
    if len(achados) > 1:
        lista = ", ".join(f"{d.get('nome')} ({d.get('jogador')})" for _, d in achados)
        raise SystemExit(f"\"{quem}\" da em mais de um: {lista}. Seja mais especifico.")
    return achados[0]


def reacoes_do_pj(pasta_jogo, nome):
    """O que cada NPC ja sentiu por este personagem, do reacoes.json do capitulo."""
    f = Path(pasta_jogo) / "reacoes.json" if pasta_jogo else None
    if not f or not f.is_file():
        return []
    try:
        dados = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return []
    alvo = simples(nome)
    fora = []
    for r in dados.get("reacoes", []):
        if simples(r.get("pj")) == alvo:
            fora.append({"npc": r.get("npc"), "faixa": r.get("faixa"),
                         "total": r.get("total"), "peso": r.get("peso")})
    return sorted(fora, key=lambda x: (x.get("total") or 0))


def arquivos_de_contexto(raiz, est, pasta_ficha):
    """O que ler antes de arbitrar, na ordem."""
    camp = raiz / "campanha"
    jogo = Path(est["capitulo_atual_pasta"]) if est.get("capitulo_atual_pasta") else None
    plano = Path(est["capitulo_atual_plano"]) if est.get("capitulo_atual_plano") else None
    itens = [
        ("ficha", pasta_ficha / "personagem.md",
         "a ficha de quem age: perícias, NH, equipamento, desvantagens"),
        ("mundo", camp / "mundo.md",
         "COMO AS COISAS ESTÃO AGORA — ferimentos, itens, relações já mudadas"),
        ("plano", (plano / "README.md") if plano else None,
         "a cena planejada: os testes que ela já prevê e as consequências"),
        ("npcs_plano", (plano / "npcs.md") if plano else None,
         "quem está em cena, com NH e atitude"),
        ("npcs_jogo", (jogo / "npcs.md") if jogo else None,
         "o que já mudou nesses NPCs na mesa — ganha do plano"),
        ("grupo", (jogo / "grupo.md") if jogo else None,
         "o que já mudou nos personagens dos jogadores"),
        ("lugares", (jogo / "lugares.md") if jogo else None,
         "o que já mudou no lugar e nas coisas"),
        ("jogo", (jogo / "README.md") if jogo else None,
         "o que já aconteceu e o que já foi narrado nesta cena"),
        ("npcs_campanha", camp / "plano" / "npcs.md", "quem atravessa a campanha"),
    ]
    return [(k, v, d) for k, v, d in itens if v is not None]


def cmd_contexto(args):
    raiz = Path(args.raiz).resolve()
    est = estado(raiz)
    pasta, d = achar_personagem(raiz, args.quem)
    itens = arquivos_de_contexto(raiz, est, pasta)
    pericias = [{"nome": p.get("nome"), "nh": p.get("nh"), "tipo": p.get("tipo"),
                 "categoria": p.get("categoria")} for p in d.get("pericias", [])]
    reacoes = reacoes_do_pj(est.get("capitulo_atual_pasta"), d.get("nome", ""))
    atrs = {k: v.get("valor") for k, v in (d.get("atributos") or {}).items()}

    if args.json:
        print(json.dumps({
            "personagem": d.get("nome"), "jogador": d.get("jogador"),
            "pasta": pasta.as_posix(),
            "atributos": atrs,
            "defesas_ativas": d.get("defesas_ativas"),
            "deslocamento": d.get("deslocamento"),
            "pericias": pericias,
            "vantagens_desvantagens": d.get("vantagens_desvantagens"),
            "peculiaridades": d.get("peculiaridades"),
            "equipamento": d.get("armas_objetos"),
            "reacoes_dos_npcs": reacoes,
            "capitulo": est.get("capitulo_atual"),
            "mapa": est.get("capitulo_atual_mapa"),
            "arquivos": {k: (v.as_posix() if v.is_file() else None) for k, v, _ in itens},
        }, ensure_ascii=False, indent=2))
        return

    print(f"Personagem : {d.get('nome')}  (jogador: {d.get('jogador')})")
    print("Atributos  : " + "  ".join(f"{k} {v}" for k, v in atrs.items()))
    da = d.get("defesas_ativas") or {}
    print(f"Defesas    : Esquiva {da.get('esquiva')}  Aparar {da.get('aparar')}"
          f"  Bloqueio {da.get('bloqueio')}   Deslocamento {d.get('deslocamento')}")
    print(f"Capítulo   : {est.get('capitulo_atual') or '(nenhum marcado)'}"
          + (f"   Mapa: {est['capitulo_atual_mapa']}"
             if est.get("capitulo_atual_mapa") else ""))

    if pericias:
        print(f"\nPerícias que ELE TEM ({len(pericias)}) — o resto é pré-definido, "
              "confira no livro:")
        cat = {}
        for p in pericias:
            cat.setdefault(p.get("categoria") or "Outras", []).append(p)
        for nome in sorted(cat):
            linha = ", ".join(f"{p['nome']} {p['nh']}" for p in cat[nome])
            print(f"  {nome}: {linha}")

    if reacoes:
        print("\nComo os NPCs já reagiram a ele (não role de novo):")
        for r in reacoes:
            print(f"  {r['npc']}: {r['faixa']} ({r['total']}) — {r['peso']}")

    print("\nLeia, nesta ordem:")
    for _, caminho, desc in itens:
        marca = " " if caminho.is_file() else "×"
        print(f"  [{marca}] {caminho}")
        print(f"       {desc}")
    print("\n× = ainda não existe; siga sem ele.")
    if not est.get("ativa"):
        print("\nSem campanha ativa: resolva a ação e diga que não houve onde registrar.")
    elif not est.get("capitulo_atual_pasta"):
        print("\nSem capítulo atual. Marque com: campanha.py atual --capitulo N")


def main():
    ap = argparse.ArgumentParser(
        description="Contexto para arbitrar a ação declarada por um jogador.")
    ap.add_argument("--raiz", default=".", help="Raiz do projeto")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("contexto", help="Quem é, o que sabe fazer, e o que ler")
    s.add_argument("--quem", required=True, help="Nome do jogador ou do personagem")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_contexto)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
