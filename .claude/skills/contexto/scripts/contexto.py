#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Folha unica de contexto: quem age, o que ele tem, como as coisas estao.

    contexto.py contexto --quem Ricardo [--json]
    contexto.py quem --nome "Kaelric" --json
    contexto.py estado --json
    contexto.py classificar --total 17 --nh 16
    contexto.py reacoes --pj "Jah Kagadu" --json

Foi criada para acabar com a duplicacao medida no repo: seis politicas diferentes de
resolucao de nome em personagens/, quatro copias do leitor de estado da campanha, seis
implementacoes de slug(), cinco do registro, e nove do caminho fixo para o campana.py.

E biblioteca de fato: as outras skills importam este arquivo (com importlib a partir de
parents[2], como ja se faz com roll) em vez de reimplementar. Quem SO precisa do numero
chama por subprocesso com --json.

Nao rola dado e nao escreve nada em lugar nenhum.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RAZ = Path(__file__).resolve().parents[4]          # raiz do projeto, a partir daqui
SKILLS = Path(__file__).resolve().parents[2]       # .claude/skills
CAMPANHA_PY = SKILLS / "campanha" / "scripts" / "campanha.py"
LIVRO_PERICIAS = Path("livros/gurps-mb-3ed/06-pericias.md")
PERSONAGENS = Path("personagens")

ATRIBUTOS = ("ST", "DX", "IQ", "HT")

# O console do Windows e cp1252 e engasga com acento, seta e travessao.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ------------------------------------------------------------------ nomes

def simples(texto):
    """Sem acento, minusculo - para comparar nome digitado com nome de ficha."""
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t.lower()).strip()


def slug(texto):
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")


def raiz_de(caminho):
    return Path(caminho or ".").resolve()


# ------------------------------------------------------------------ campana

def estado(raiz=None):
    """Estado da campanha, sempre com a mesma forma: sem campanha, {"ativa": False}.

    As copias que existiam antes divergiam - tres devolviam {"ativa": False}, a skill
    reacao devolvia {} - e quem consultava nao sabia se nao havia campanha ou se havia
    uma campanha sem chave nenhuma.
    """
    raiz = raiz_de(raiz)
    script = raiz / ".claude" / "skills" / "campanha" / "scripts" / "campanha.py"
    if not script.is_file():
        script = CAMPANHA_PY
    if not script.is_file():
        return {"ativa": False}
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        r = subprocess.run(
            [sys.executable, str(script), "--raiz", str(raiz), "estado", "--json"],
            capture_output=True, text=True, encoding="utf-8", timeout=30, env=env)
        dados = json.loads(r.stdout) if r.returncode == 0 else None
        return dados if isinstance(dados, dict) and dados else {"ativa": False}
    except Exception:
        return {"ativa": False}


# ------------------------------------------------------------------ fichas

def fichas(raiz=None):
    """Todas as fichas do repositorio: [(pasta, dados do personagem.json)]."""
    raiz = raiz_de(raiz)
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


def achar_personagem(quem, raiz=None):
    """Resolve por nome do JOGADOR ou do PERSONAGEM, inteiro ou em parte.

    Devolve (pasta, dados). Erro com a lista do que existe - para a skill nao ter que
    adivinhar o que o usuario quis dizer.
    """
    raiz = raiz_de(raiz)
    alvo = simples(quem)
    if not alvo:
        raise SystemExit("Diga de quem é: --quem \"Ricardo\" ou --quem \"Jah\".")
    todas = fichas(raiz)
    if not todas:
        raise SystemExit(f"Nenhuma ficha em {raiz / PERSONAGENS}.")
    exatos, parciais = [], []
    for pasta, d in todas:
        campos = [simples(d.get("jogador")), simples(d.get("nome")), simples(pasta.name)]
        if alvo in campos:
            exatos.append((pasta, d))
        elif any(c and (alvo in c or c.startswith(alvo)) for c in campos):
            parciais.append((pasta, d))
        elif any(alvo in p for c in campos for p in c.split()):
            parciais.append((pasta, d))
    achados = exatos or parciais
    if not achados:
        lista = ", ".join(f"{d.get('nome')} ({d.get('jogador')})" for _, d in todas)
        raise SystemExit(f"Nao achei \"{quem}\". Existem: {lista}")
    if len(achados) > 1:
        lista = ", ".join(f"{d.get('nome')} ({d.get('jogador')})" for _, d in achados)
        raise SystemExit(f"\"{quem}\" da em mais de um: {lista}. Seja mais especifico.")
    return achados[0]


def ler_ficha(nome, raiz=None):
    """So os dados da ficha, ou None. Aceita nome parcial: 'Comam' acha comam-obabaroy."""
    raiz = raiz_de(raiz)
    base = raiz / PERSONAGENS
    if not base.is_dir():
        return None
    alvo = slug(nome)
    achado = None
    for f in sorted(base.glob("*/personagem.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for s in (slug(f.parent.name), slug(d.get("nome", ""))):
            peso = 0 if s == alvo else (1 if s.startswith(alvo) else
                                        (2 if alvo in s.split("-") or alvo in s else None))
            if peso is not None and (achado is None or peso < achado[0]):
                achado = (peso, d)
    return achado[1] if achado else None


def atributos(d):
    return {k: (v or {}).get("valor") for k, v in (d.get("atributos") or {}).items()}


def pericia(d, nome):
    """Melhor NH entre pericias e magias cujo nome case com o pedido: (nh, nome) ou None."""
    alvo = slug(nome)
    melhor = None
    for p in (d.get("pericias") or []) + (d.get("magias") or []):
        s = slug(p.get("nome", ""))
        if s == alvo or s.startswith(alvo) or alvo in s:
            nh = int(p.get("nh") or 0)
            if melhor is None or nh > melhor[0]:
                melhor = (nh, p.get("nome"))
    return melhor


def nivel_vantagem(d, prefixo):
    """'Prontidao +2' -> 2. 'Sorte' -> 0 (existe, sem nivel). None se nao tem."""
    alvo = slug(prefixo)
    for v in d.get("vantagens_desvantagens") or []:
        nome = v.get("nome", "")
        if slug(nome).startswith(alvo):
            m = re.search(r"([+-]?\d+)\s*$", nome.strip())
            return int(m.group(1)) if m else 0
    return None


# ------------------------------------------------------------------ a jogada

def classificar(total, nh):
    """Sucesso decisivo e falha critica - MB, cap. 12. Dona desta regra: esta folha."""
    if total <= 4:
        return "sucesso decisivo"
    if total == 5 and nh >= 15:
        return "sucesso decisivo"
    if total == 6 and nh >= 16:
        return "sucesso decisivo"
    if total == 18:
        return "falha crítica"
    if total == 17:
        return "falha crítica" if nh < 16 else "falha"
    if total >= nh + 10:
        return "falha crítica"
    return "sucesso" if total <= nh else "falha"


def margem(total, nh):
    """Quanto passou ou quanto falhou, na convencao da casa: nh - total."""
    return nh - total


# ------------------------------------------------------------------ livro

def busca_no_livro(nome, raiz=None):
    """Entrada da pericia no MB: dificuldade, pre-definido e a linha de Modificadores."""
    raiz = raiz_de(raiz)
    livro = raiz / LIVRO_PERICIAS
    if not livro.is_file():
        return None
    texto = livro.read_text(encoding="utf-8")
    blocos = re.split(r"^### ", texto, flags=re.M)[1:]
    alvo = slug(nome)
    achado = None
    for b in blocos:
        cab = b.splitlines()[0]
        m = re.match(r"^(.+?)\s*\((.+?)\)\s*$", cab)
        if not m:
            continue
        s = slug(m.group(1))
        peso = 0 if s == alvo else (1 if s.startswith(alvo) else (2 if alvo in s else None))
        if peso is None:
            continue
        if achado is None or peso < achado[0]:
            achado = (peso, m.group(1).strip(), m.group(2).strip(), b)
        if peso == 0:
            break
    if not achado:
        return None
    _, nome_livro, tipo, bloco = achado
    m = re.search(r"^\*\*Pr[ée]-definido:\*\*\s*(.+?)\s*$", bloco, re.M)
    mods = re.search(r"Modificadores:\s*(.+?)(?:\n|$)", bloco)
    return {"nome": nome_livro, "tipo": tipo,
            "predefinido": m.group(1) if m else "",
            "modificadores": mods.group(1).strip() if mods else ""}


# ------------------------------------------------------------------ reacoes e arquivos

def pastas_de_cache(raiz, est, todos):
    """Onde mora o reacoes.json. Sem capitulo atual, nada - quem escreve recusa."""
    if todos:
        return sorted((raiz / "campanha").glob("*/reacoes.json"))
    pasta = est.get("capitulo_atual_pasta")
    return [Path(pasta) / "reacoes.json"] if pasta else []


def ler_reacoes(raiz=None, est=None, todos=False):
    """As entradas cruas do cache, com o mais novo vencendo por (pj, npc).

    Leitura: quem escreve e a `registrar-acao`. As skills que precisam saber o que ja foi
    rolado passam por aqui, em vez de cada uma abrir o JSON do jeito que lhe convem.
    """
    raiz = raiz_de(raiz)
    est = est or estado(raiz)
    colhidas = {}
    for f in pastas_de_cache(raiz, est, todos):
        if not f.is_file():
            continue
        try:
            dados = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in dados.get("reacoes", []):
            k = (simples(r.get("pj")), simples(r.get("npc")))
            anterior = colhidas.get(k)
            # com todos=True varre os capitulos em ordem: o mais novo no arquivo manda
            if anterior is None or (f.parent.name >= Path(anterior["_de"]).parent.name):
                r = dict(r)
                r["_de"] = f.as_posix()
                colhidas[k] = r
    return [r for r in colhidas.values()]


def reacoes_do_pj(nome, est=None, raiz=None, todos=False):
    """O que cada NPC ja sentiu por este personagem, do reacoes.json do capitulo."""
    raiz = raiz_de(raiz)
    est = est or estado(raiz)
    alvo = simples(nome)
    fora = [{"npc": r.get("npc"), "faixa": r.get("faixa"),
             "total": r.get("total"), "peso": r.get("peso")}
            for r in ler_reacoes(raiz, est, todos) if simples(r.get("pj")) == alvo]
    return sorted(fora, key=lambda x: (x.get("total") or 0))


def arquivos_de_contexto(est=None, pasta_ficha=None, raiz=None):
    """O que ler antes de arbitrar, na ordem. Uma lista so, para a acao e para o narrar."""
    raiz = raiz_de(raiz)
    est = est or estado(raiz)
    camp = raiz / "campanha"
    jogo = Path(est["capitulo_atual_pasta"]) if est.get("capitulo_atual_pasta") else None
    plano = Path(est["capitulo_atual_plano"]) if est.get("capitulo_atual_plano") else None
    itens = [
        ("ficha", (pasta_ficha / "personagem.md") if pasta_ficha else None,
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


# ------------------------------------------------------------------ cli

def _print_contexto(d, pasta, est, itens, reacoes, json_out):
    atrs = atributos(d)
    perics = [{"nome": p.get("nome"), "nh": p.get("nh"), "tipo": p.get("tipo"),
               "categoria": p.get("categoria")} for p in d.get("pericias", [])]
    if json_out:
        print(json.dumps({
            "personagem": d.get("nome"), "jogador": d.get("jogador"),
            "pasta": pasta.as_posix(), "atributos": atrs,
            "defesas_ativas": d.get("defesas_ativas"),
            "deslocamento": d.get("deslocamento"),
            "velocidade_basica": d.get("velocidade_basica"),
            "pontos_vida": d.get("pontos_vida"), "fadiga": d.get("fadiga"),
            "pericias": perics,
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
          + (f"   Mapa: {est['capitulo_atual_mapa']}" if est.get("capitulo_atual_mapa") else ""))
    if perics:
        print(f"\nPerícias que ELE TEM ({len(perics)}) — o resto é pré-definido:")
        cat = {}
        for p in perics:
            cat.setdefault(p.get("categoria") or "Outras", []).append(p)
        for nome in sorted(cat):
            print(f"  {nome}: " + ", ".join(f"{p['nome']} {p['nh']}" for p in cat[nome]))
    if reacoes:
        print("\nComo os NPCs já reagiram a ele (não role de novo):")
        for r in reacoes:
            print(f"  {r['npc']}: {r['faixa']} ({r['total']}) — {r['peso']}")
    print("\nLeia, nesta ordem:")
    for _, caminho, desc in itens:
        print(f"  [{' ' if caminho.is_file() else '×'}] {caminho}\n       {desc}")
    if not est.get("ativa"):
        print("\nSem campanha ativa.")


def main():
    ap = argparse.ArgumentParser(description="Folha de contexto da mesa.")
    ap.add_argument("--raiz", default=".", help="Raiz do projeto")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("contexto", help="Quem é, o que sabe fazer, e o que ler")
    s.add_argument("--quem", required=True)
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("quem", help="So a resolucão do nome: pasta e ficha")
    s.add_argument("--nome", required=True)
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("estado", help="Estado da campanha, na forma única")
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("classificar", help="Veredito de uma rolagem contra um NH")
    s.add_argument("--total", type=int, required=True)
    s.add_argument("--nh", type=int, required=True)

    s = sub.add_parser("reacoes", help="Reações já roladas para um personagem")
    s.add_argument("--pj", required=True)
    s.add_argument("--todos", action="store_true", help="Varre todos os capítulos")
    s.add_argument("--json", action="store_true")

    args = ap.parse_args()
    raiz = raiz_de(args.raiz)

    if args.cmd == "contexto":
        est = estado(raiz)
        pasta, d = achar_personagem(args.quem, raiz)
        itens = arquivos_de_contexto(est, pasta, raiz)
        _print_contexto(d, pasta, est, itens,
                        reacoes_do_pj(d.get("nome", ""), est, raiz), args.json)
    elif args.cmd == "quem":
        pasta, d = achar_personagem(args.nome, raiz)
        if args.json:
            print(json.dumps({"pasta": pasta.as_posix(), "personagem": d},
                             ensure_ascii=False, indent=2))
        else:
            print(f"{d.get('nome')} ({d.get('jogador')}) -> {pasta.as_posix()}")
    elif args.cmd == "estado":
        print(json.dumps(estado(raiz), ensure_ascii=False, indent=2))
    elif args.cmd == "classificar":
        print(f"{classificar(args.total, args.nh)} (margem {margem(args.total, args.nh):+d})")
    elif args.cmd == "reacoes":
        dados = reacoes_do_pj(args.pj, estado(raiz), raiz, todos=args.todos)
        if args.json:
            print(json.dumps(dados, ensure_ascii=False, indent=2))
        else:
            for r in dados:
                print(f"{r['npc']}: {r['faixa']} ({r['total']}) — {r['peso']}")
            if not dados:
                print("(nenhuma reação registrada)")


if __name__ == "__main__":
    main()
