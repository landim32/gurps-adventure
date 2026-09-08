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
import unicodedata
from datetime import datetime
from pathlib import Path

CAMPANHA_PY = Path(".claude/skills/campanha/scripts/campanha.py")

# Quem rola dado neste repositorio e a skill `roll`, uma so.
ROLL_PY = Path(__file__).resolve().parents[2] / "roll" / "scripts" / "roll.py"
try:
    _spec = importlib.util.spec_from_file_location("roll", ROLL_PY)
    _roll = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_roll)
except Exception as erro:
    raise SystemExit(f"Não consegui carregar a skill roll ({ROLL_PY}): {erro}")

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


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")


def faixa_de(total):
    for teto, nome, peso, texto in FAIXAS:
        if total <= teto:
            return nome, peso, texto
    return FAIXAS[-1][1], FAIXAS[-1][2], FAIXAS[-1][3]


def estado_campanha(raiz):
    script = raiz / CAMPANHA_PY
    if not script.is_file():
        return {}
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(script), "--raiz", str(raiz),
                        "estado", "--json"], capture_output=True, text=True,
                       encoding="utf-8", timeout=30, env=env)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def registrar(raiz, texto):
    script = raiz / CAMPANHA_PY
    if not script.is_file():
        return False, "skill campanha não encontrada"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(script), "--raiz", str(raiz),
                        "acontecimento", "--texto", texto], capture_output=True,
                       text=True, encoding="utf-8", timeout=30, env=env)
    return r.returncode == 0, (r.stdout or r.stderr).strip()


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
    """Nome e modificador de reação, direto do campo Reacao da ficha."""
    f = raiz / "personagens" / slug(nome) / "personagem.json"
    if not f.is_file():
        # nome parcial: "Negrum" acha negrum-carneiriums, "Kaelric" acha irmao-kaelric
        alvo, achado = slug(nome), None
        for cand in sorted((raiz / "personagens").glob("*/personagem.json")):
            s = slug(cand.parent.name)
            peso = 0 if s == alvo else (1 if s.startswith(alvo) else
                                        (2 if alvo in s.split("-") else None))
            if peso is not None and (achado is None or peso < achado[0]):
                achado = (peso, cand)
        if not achado:
            return {"nome": nome, "mod": 0, "bruto": "", "achou": False}
        f = achado[1]
    d = json.loads(f.read_text(encoding="utf-8"))
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


def carregar(arquivo):
    if arquivo.is_file():
        try:
            return json.loads(arquivo.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"reacoes": []}


def chave(r):
    return (slug(r["npc"]), slug(r["pj"]))


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
    est = estado_campanha(raiz)
    pasta = est.get("capitulo_atual_pasta")
    if pasta:
        destino = raiz / pasta
    else:
        destino = raiz / "campanha"
        if not args.listar:
            print("AVISO: sem capítulo atual marcado — gravando em campanha/reacoes.json.")
            print("       Marque com: campanha.py atual --capitulo N\n")
    destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / "reacoes.json"
    dados = carregar(arquivo)
    ja = {chave(r): r for r in dados["reacoes"]}

    if args.listar:
        if not dados["reacoes"]:
            print(f"Nenhuma reação registrada em {arquivo.relative_to(raiz)}.")
            return
        print(f"REAÇÕES JÁ ROLADAS — {arquivo.relative_to(raiz)}\n")
        for r in dados["reacoes"]:
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

    dados["reacoes"] = list(ja.values())   # dict preserva a ordem de insercao
    dados["local"] = args.local or dados.get("local", "")
    if args.nao_gravar:
        print("(--nao-gravar: nada foi escrito em disco nem na campanha)\n")
    else:
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

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

    if not args.nao_gravar:
        print(f"\nGravado em {arquivo.relative_to(raiz)} — "
              f"{len(dados['reacoes'])} reação(ões) neste capítulo.")
    print("SEGREDO DO MESTRE (MB, pág. 180): não mostre isto aos jogadores.")

    if not args.nao_gravar and novos:
        destaques = [f"{r['npc']}→{r['pj']} {r['faixa']} ({r['total']})"
                     for r in extremos + notas]
        resumo = (f"Testes de reação{' em ' + args.local if args.local else ''}: "
                  + ("; ".join(destaques) if destaques else "nada fora do neutro")
                  + (f". Outras {len(neutras)} neutras." if neutras else "."))
        ok, msg = registrar(raiz, resumo)
        print("\nRegistrado no capítulo atual." if ok else f"\nAVISO: não gravei — {msg}")


if __name__ == "__main__":
    main()
