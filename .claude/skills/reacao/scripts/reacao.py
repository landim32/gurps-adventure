#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de reação de todo mundo que esta no local — MB, pag. 180 e 204.

    reacao.py --local "A Ancora Quebrada" \
      --npcs "Hoel Meia-Orelha, Osric de Bannock:-1, Giles Mao-de-Prata" \
      --mod "Giles>NelsOwned:+2:brindou ao noivado"

Um teste por par NPC x personagem. Os modificadores do personagem saem do campo Reacao
da ficha; os do NPC vem do npcs.md do capitulo, passados aqui.

O resultado fica em campanha/NN-.../reacoes.json — e NAO se rola de novo um par que ja
tem resultado. Reacao e a atitude do NPC, nao um dado por conversa.

RESULTADO E SEGREDO DO MESTRE (pag. 180): nao mostre aos jogadores.
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
REGISTRAR_PY = SKILLS / "registrar-acao" / "scripts" / "registrar_acao.py"

# Quem rola dado neste repositorio e a skill `roll`, uma so.
ROLL_PY = SKILLS / "roll" / "scripts" / "roll.py"
try:
    _spec = importlib.util.spec_from_file_location("roll", ROLL_PY)
    _roll = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_roll)
except Exception as erro:
    raise SystemExit(f"Não consegui carregar a skill roll ({ROLL_PY}): {erro}")

# Nome, ficha, estado da campanha e cache de reacoes vem da folha `contexto`, uma so.
CTX_PY = SKILLS / "contexto" / "scripts" / "contexto.py"
try:
    _spec = importlib.util.spec_from_file_location("contexto", CTX_PY)
    ctx = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(ctx)
except Exception as erro:
    raise SystemExit(f"Não consegui carregar a skill contexto ({CTX_PY}): {erro}")

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

# MB, 21-quadros-e-tabelas.md — "Tabela de Reações". Teto da faixa, nome, e a linha de
# Reação Geral. Para os outros contextos, o script aponta o arquivo.
FAIXAS = [
    (0, "Desastrosa", "extremo",
     "O NPC odeia os personagens e procurará prejudicá-los o mais possível."),
    (3, "Muito Ruim", "extremo",
     "O NPC antipatiza com os PCs e agirá contra eles se isto lhe for conveniente."),
    (6, "Ruim", "nota",
     "O NPC não se importa com os PCs e agirá contra eles se isto lhe trouxer algum benefício."),
    (9, "Fraca", "nota",
     "O NPC não se deixará impressionar. Pode se tornar hostil se isso lhe der lucro grande "
     "ou houver pouco perigo."),
    (12, "Neutra", "calado",
     "O NPC ignora os personagens tanto quanto possível. Está totalmente desinteressado."),
    (15, "Boa", "nota",
     "O NPC gosta dos personagens e será prestativo dentro do razoável."),
    (18, "Muito Bom", "extremo",
     "O NPC tem os personagens em alta conta e será muito gentil e prestativo."),
    (10 ** 6, "Excelente", "extremo",
     "O NPC ficará extremamente impressionado e agirá sempre no melhor interesse deles, "
     "dentro dos limites de sua capacidade."),
]

CONTEXTOS = {
    "geral": "Reações em Geral",
    "combate": "Situações de Combate Iminente (e Verificação do Moral)",
    "comercio": "Transações Comerciais",
    "ajuda": "Pedidos de Ajuda",
    "informacao": "Pedidos de Informação",
    "lealdade": "Lealdade",
}
TABELA_MD = "livros/gurps-mb-3ed/21-quadros-e-tabelas.md"

# A resolução de nome é da folha contexto; aqui só se herda o apelido.
slug = ctx.slug


def faixa_de(total):
    for teto, nome, peso, texto in FAIXAS:
        if total <= teto:
            return nome, peso, texto
    return FAIXAS[-1][1], FAIXAS[-1][2], FAIXAS[-1][3]


def entregar(ato):
    """Passa o ato à `registrar-acao`. Esta skill não escreve em lugar nenhum.

    Antes: `registrar()` próprio, mais a escrita direta do reacoes.json com fallback para
    campanha/reacoes.json quando não havia capítulo — arquivo que ninguém mais lia.
    """
    if not REGISTRAR_PY.is_file():
        return False, "skill registrar-acao nao encontrada"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(REGISTRAR_PY), "--stdin"],
                       input=json.dumps(ato, ensure_ascii=False),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=60, env=env)
    linhas = [l for l in (r.stdout or "").splitlines() if l.startswith("[")]
    saida = "\n        ".join(linhas) or (r.stderr or "").strip()
    return r.returncode == 0, saida


def elenco(raiz):
    """Os PJs da campanha, na ordem do README. Sem campanha, todos os personagens."""
    readme = raiz / "campanha" / "README.md"
    nomes = []
    if readme.is_file():
        t = readme.read_text(encoding="utf-8")
        bloco = t.split("## Personagens")[-1].split("\n## ")[0] if "## Personagens" in t else ""
        for linha in bloco.splitlines():
            m = re.match(r"\s*\|\s*([^|]+?)\s*\|", linha)
            if m and m.group(1).lower() not in ("personagem", "---") and "--" not in m.group(1):
                nomes.append(m.group(1).strip())
    if not nomes:
        base = raiz / "personagens"
        nomes = [p.name for p in sorted(base.iterdir()) if (p / "personagem.json").is_file()] \
            if base.is_dir() else []
    return nomes


def ficha_pj(nome, raiz):
    """Nome e modificador de reação, direto do campo Reacao da ficha.

    A resolucao de nome (exato, comeco, parte) vem da folha contexto; o que e daqui e a
    leitura do campo, que texto livre e nao numero.
    """
    d = ctx.ler_ficha(nome, raiz)
    if not d:
        return {"nome": nome, "mod": 0, "bruto": "", "achou": False}
    bruto = str(d.get("reacao") or "").strip()
    # o campo e texto livre: "-3", "+2", "-2 (porte); +2 cristaos". Vale o primeiro
    # numero com sinal; o resto e condicional e fica para o Mestre aplicar.
    m = re.match(r"\s*([+-]\s*\d+)", bruto)
    return {
        "nome": d.get("nome", nome),
        "mod": int(re.sub(r"\s+", "", m.group(1))) if m else 0,
        "bruto": bruto,
        "condicional": bool(re.search(r"[;,].*[+-]\s*\d+", bruto)),
        "achou": True,
    }


def parse_npcs(txt):
    """'Hoel, Osric:-1, Giles:+1' -> [{'nome':..., 'mod':...}]"""
    saida = []
    for parte in [p.strip() for p in txt.split(",") if p.strip()]:
        m = re.match(r"^(?P<nome>.+?)\s*:\s*(?P<mod>[+-]?\d+)\s*$", parte)
        if m:
            saida.append({"nome": m.group("nome").strip(), "mod": int(m.group("mod"))})
        else:
            saida.append({"nome": parte, "mod": 0})
    return saida


def parse_mods(lista):
    """'Giles>NelsOwned:+2:brindou' -> (slug_npc, slug_pj, +2, 'brindou')"""
    saida = []
    for item in lista or []:
        m = re.match(r"^\s*(?P<npc>[^>]+?)\s*>\s*(?P<pj>[^:]+?)\s*:\s*"
                     r"(?P<mod>[+-]?\d+)\s*(?::\s*(?P<motivo>.+?))?\s*$", item)
        if not m:
            raise SystemExit(f'--mod "{item}" fora do formato NPC>Personagem:+2:motivo')
        saida.append((slug(m.group("npc")), slug(m.group("pj")),
                      int(m.group("mod")), (m.group("motivo") or "").strip()))
    return saida


def casa(alvo_slug, nome):
    """Nome parcial casa com nome inteiro: 'Giles' acha 'Giles Mao-de-Prata'."""
    s = slug(nome)
    return s == alvo_slug or s.startswith(alvo_slug) or alvo_slug in s.split("-")


def bloco_extremo(r):
    barra = "!" * 66
    return "\n".join([
        "",
        barra,
        f"  {r['faixa'].upper()}  —  {r['npc']}  ➜  {r['pj']}",
        f"  {r['conta']}",
        "",
        f"  {r['texto']}",
        barra,
    ])


def main():
    ap = argparse.ArgumentParser(description="Testes de reação de todos com todos.")
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--npcs", default="",
                    help='Nomes separados por vírgula; ":-1" para a atitude de saída')
    ap.add_argument("--pjs", default="", help="Padrão: todos os PJs da campanha")
    ap.add_argument("--mod", action="append",
                    help='Modificador de par: "Giles>NelsOwned:+2:brindou ao noivado"')
    ap.add_argument("--contexto", default="geral", choices=sorted(CONTEXTOS))
    ap.add_argument("--local", default="", help="Onde a cena se passa")
    ap.add_argument("--refazer", action="store_true",
                    help="Rola de novo pares que já têm resultado")
    ap.add_argument("--listar", action="store_true",
                    help="Só mostra o que já foi rolado neste capítulo")
    ap.add_argument("--tudo", action="store_true", help="Mostra também as neutras, com a conta")
    ap.add_argument("--nao-gravar", action="store_true", help="Não registra na campanha")
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()
    est = ctx.estado(raiz)
    cache = ctx.ler_reacoes(raiz, est)
    onde = Path(est.get("capitulo_atual_pasta") or "campanha") / "reacoes.json"
    ja = {(slug(r["npc"]), slug(r["pj"])): r for r in cache}

    if not est.get("capitulo_atual_pasta") and not args.listar:
        print("AVISO: sem capítulo atual marcado — a registradora recusa escrever o cache.")
        print("       Marque com: campanha.py atual --capitulo N\n")

    if args.listar:
        if not cache:
            print(f"Nenhuma reação registrada em {onde}.")
            return
        print(f"REAÇÕES JÁ ROLADAS — {onde}\n")
        for r in cache:
            marca = "!!" if r["peso"] == "extremo" else "  "
            print(f" {marca} {r['npc']} ➜ {r['pj']}: {r['total']} — {r['faixa']}"
                  f"   ({r['quando']}, {r['contexto']})")
        print("\nEstes valores valem para a cena inteira. Não role de novo o mesmo par.")
        return

    if not args.npcs:
        raise SystemExit("Passe --npcs com quem está no local.")

    npcs = parse_npcs(args.npcs)
    pjs_nomes = [p.strip() for p in args.pjs.split(",") if p.strip()] or elenco(raiz)
    if not pjs_nomes:
        raise SystemExit("Não achei personagens. Passe --pjs.")
    pjs = [ficha_pj(n, raiz) for n in pjs_nomes]
    pares_mod = parse_mods(args.mod)

    for p in pjs:
        if not p["achou"]:
            print(f"AVISO: sem ficha para «{p['nome']}» — entrou sem modificador.")

    novos, pulados = [], []
    for npc in npcs:
        for pj in pjs:
            k = (slug(npc["nome"]), slug(pj["nome"]))
            if k in ja and not args.refazer:
                pulados.append(ja[k])
                continue

            detalhe, mod = [], 0
            if pj["mod"]:
                mod += pj["mod"]
                detalhe.append(f"{pj['mod']:+d} ficha de {pj['nome']}")
            if npc["mod"]:
                mod += npc["mod"]
                detalhe.append(f"{npc['mod']:+d} {npc['nome']} de saída")
            for s_npc, s_pj, valor, motivo in pares_mod:
                if casa(s_npc, npc["nome"]) and casa(s_pj, pj["nome"]):
                    mod += valor
                    detalhe.append(f"{valor:+d} {motivo}" if motivo else f"{valor:+d}")

            dados_rolados = _roll.d6(3)
            soma = sum(dados_rolados)
            total = soma + mod
            nome_faixa, peso, texto = faixa_de(total)
            conta = ("3d " + "[" + ", ".join(map(str, dados_rolados)) + f"] = {soma}"
                     + (f" {'+' if mod > 0 else '-'} {abs(mod)} = {total}" if mod else ""))

            r = {
                "npc": npc["nome"], "pj": pj["nome"], "dados": dados_rolados,
                "mod": mod, "total": total, "faixa": nome_faixa, "peso": peso,
                "texto": texto, "conta": conta, "detalhe": detalhe,
                "contexto": args.contexto, "local": args.local,
                "quando": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            if pj["bruto"] and pj.get("condicional"):
                r["atencao"] = f"ficha de {pj['nome']}: «{pj['bruto']}» — confira se a " \
                               f"parte condicional vale aqui"
            ja[k] = r
            novos.append(r)

    if args.nao_gravar:
        print("(--nao-gravar: nada foi escrito em disco nem na campanha)\n")

    # ---------------- saida ----------------
    cab = f"TESTES DE REAÇÃO — {args.local}" if args.local else "TESTES DE REAÇÃO"
    print("=" * 66)
    print(cab)
    print(f"{len(npcs)} NPC(s) × {len(pjs)} personagem(ns) — contexto: "
          f"{CONTEXTOS[args.contexto]}")
    if pulados:
        print(f"{len(pulados)} par(es) já tinham resultado e não foram rolados de novo.")
    print("=" * 66)

    extremos = [r for r in novos if r["peso"] == "extremo"]
    notas = [r for r in novos if r["peso"] == "nota"]
    neutras = [r for r in novos if r["peso"] == "calado"]

    for r in sorted(extremos, key=lambda r: r["total"]):
        print(bloco_extremo(r))
        if r["detalhe"]:
            print(f"  ({'; '.join(r['detalhe'])})")

    if notas:
        print("\n--- vale anotar ---")
        for r in sorted(notas, key=lambda r: r["total"]):
            print(f"  {r['npc']} ➜ {r['pj']}: {r['faixa']} ({r['total']})")
            if r["detalhe"]:
                print(f"      {'; '.join(r['detalhe'])}")

    if neutras:
        print(f"\nNeutras, sem nada a dizer: "
              + "; ".join(f"{r['npc']}/{r['pj']}" for r in neutras))

    if args.tudo:
        print("\n--- todos os pares, com a conta ---")
        for r in novos:
            print(f"  {r['npc']} ➜ {r['pj']}: {r['conta']} — {r['faixa']}")

    for aviso in dict.fromkeys(r["atencao"] for r in novos if "atencao" in r):
        print(f"\nATENÇÃO: {aviso}")

    if args.contexto != "geral":
        print(f"\nO texto acima é a coluna «Reação Geral». Para o que {CONTEXTOS[args.contexto]}"
              f" significa em cada faixa, veja {TABELA_MD}.")

    print("SEGREDO DO MESTRE (MB, pág. 180): não mostre isto aos jogadores.")

    if args.nao_gravar or not novos:
        return

    destaques = [f"{r['npc']}→{r['pj']} {r['faixa']} ({r['total']})"
                 for r in extremos + notas]
    resumo = (f"Testes de reação{' em ' + args.local if args.local else ''}: "
              + ("; ".join(destaques) if destaques else "nada fora do neutro")
              + (f". Outras {len(neutras)} neutras." if neutras else "."))
    ok, msg = entregar({"resumo": resumo, "reacoes": novos, "local": args.local})
    if ok:
        print(f"\nEntregue à registrar-acao:\n        {msg}")
        print(f"{len(cache) + len(novos)} reação(ões) no capítulo, e estes pares não rolam "
              "de novo.")
    else:
        print(f"\nAVISO: não registrei — {msg}")


if __name__ == "__main__":
    main()
