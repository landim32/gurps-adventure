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
atacar, e o registro e da skill campanha.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]

# Nome, ficha, estado da campana e cache de reacoes sao da folha `contexto`, uma so.
# Ver .claude/skills/contexto/.
CTX_PY = SKILLS / "contexto" / "scripts" / "contexto.py"
try:
    _spec = importlib.util.spec_from_file_location("contexto", CTX_PY)
    ctx = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(ctx)
except Exception as erro:
    raise SystemExit(f"Não consegui carregar a skill contexto ({CTX_PY}): {erro}")

# O console do Windows e cp1252 e engasga com acento, seta e travessao.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

simples = ctx.simples


def estado(raiz):
    return ctx.estado(raiz)


def fichas(raiz):
    return ctx.fichas(raiz)


def achar_personagem(raiz, quem):
    """Resolve por nome do JOGADOR ou do PERSONAGEM, inteiro ou em parte.

    A ordem de argumentos e a de sempre: `processar-turno` chama achar_personagem(raiz,
    quem), e a folha contexto recebe (quem, raiz). O embrulho converte — nao e preciosismo,
    e o que impede o turno de quebrar.
    """
    return ctx.achar_personagem(quem, raiz)


def reacoes_do_pj(pasta_jogo, nome):
    """O que cada NPC ja sentiu por este personagem, no capitulo indicado."""
    if not pasta_jogo:
        return []
    return ctx.reacoes_do_pj(nome, {"capitulo_atual_pasta": str(pasta_jogo)}, ".")


def arquivos_de_contexto(raiz, est, pasta_ficha):
    """O que ler antes de arbitrar, na ordem. A lista mora na folha contexto.

    Nao confundir com a lista da `narrar`: a de la leva a premissa da campanha, a
    Descrição do Cenário e o reacoes.json, e nao a ficha de um personagem — quem narra a
    cena lê outra coisa de quem arbitra a ação de um.
    """
    return ctx.arquivos_de_contexto(est, pasta_ficha, raiz)


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
