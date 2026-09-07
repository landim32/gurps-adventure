#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Junta o contexto do capitulo atual e arquiva a narracao gerada.

    narrar.py contexto            # o que ler antes de narrar
    narrar.py contexto --json
    narrar.py gravar --arquivo narracao.txt --resumo "Descreveu a taberna cheia"

Escrever a narracao nao esta aqui — isso e trabalho de prosa. O script cuida do que da
errado a mao: achar os arquivos certos do capitulo, numerar, carimbar a hora, e nao
esquecer de registrar no historico da campanha.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CAMPANHA_PY = Path(".claude/skills/gerenciar-campanha/scripts/campanha.py")

# O console do Windows e cp1252 e engasga com acento, seta e travessao.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass


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


def registrar_acontecimento(raiz, texto):
    script = raiz / CAMPANHA_PY
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run(
        [sys.executable, str(script), "--raiz", str(raiz), "acontecimento",
         "--texto", texto],
        capture_output=True, text=True, encoding="utf-8", timeout=30, env=env)
    return r.returncode == 0, (r.stdout or r.stderr).strip()


def exige_capitulo(raiz):
    est = estado(raiz)
    if not est.get("ativa"):
        raise SystemExit("Nao ha campanha ativa. Crie com gerenciar-campanha.")
    if not est.get("capitulo_atual_pasta"):
        raise SystemExit(
            "Nao ha capitulo atual. Marque com:\n"
            "  campanha.py atual --capitulo N")
    return est


def arquivos_de_contexto(raiz, est):
    """Tudo o que compoe o contexto do capitulo, na ordem em que deve ser lido."""
    p = Path(est["capitulo_atual_pasta"])
    plano = Path(est["capitulo_atual_plano"]) if est.get("capitulo_atual_plano") else None
    camp = raiz / "campanha"
    itens = [
        ("campanha", camp / "README.md", "quem são os personagens, a premissa"),
        ("cenario", camp / "plano" / "README.md", "Descrição do Cenário — o que os PJs sabem"),
        ("plano", (plano / "README.md") if plano else None, "a cena como foi planejada"),
        ("npcs_capitulo", (plano / "npcs.md") if plano else None, "quem aparece nesta cena"),
        ("npcs_campanha", camp / "plano" / "npcs.md", "quem atravessa a campanha"),
        ("jogo", p / "README.md",
         "o que JÁ aconteceu e o que JÁ foi narrado nesta cena — não repita"),
        ("reacoes", p / "reacoes.json",
         "como cada NPC já reagiu a cada personagem — manda no jeito de interpretá-los"),
    ]
    return [(k, v, d) for k, v, d in itens if v is not None]


def cmd_contexto(args):
    raiz = Path(args.raiz).resolve()
    est = exige_capitulo(raiz)
    itens = arquivos_de_contexto(raiz, est)

    if args.json:
        print(json.dumps({
            "capitulo": est["capitulo_atual"],
            "mapa": est.get("capitulo_atual_mapa"),
            "arquivos": {k: (str(v) if v.is_file() else None) for k, v, _ in itens},
        }, ensure_ascii=False, indent=2))
        return

    print(f"Capítulo atual : {est['capitulo_atual']}")
    if est.get("capitulo_atual_mapa"):
        print(f"Mapa da cena   : {est['capitulo_atual_mapa']}")
    print("\nLeia, nesta ordem:")
    for _, caminho, desc in itens:
        marca = " " if caminho.is_file() else "×"
        print(f"  [{marca}] {caminho}")
        print(f"       {desc}")
    print("\n× = ainda não existe; siga sem ele.")


def cmd_gravar(args):
    raiz = Path(args.raiz).resolve()
    est = exige_capitulo(raiz)
    pasta = Path(est["capitulo_atual_pasta"])

    texto = (Path(args.arquivo).read_text(encoding="utf-8") if args.arquivo
             else args.texto or "")
    texto = texto.strip()
    if not texto:
        raise SystemExit("Nada para gravar. Use --texto ou --arquivo.")

    destino = pasta / "README.md"
    if not destino.is_file():
        raise SystemExit(f"{destino} nao existe. Rode: campanha.py atual --capitulo N")
    doc = destino.read_text(encoding="utf-8")

    n = len(re.findall(r"^### Narração \d+ ", doc, re.M)) + 1
    cabeca = f"### Narração {n} — {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    bloco = cabeca + "\n\n" + (f"_{args.resumo}_\n\n" if args.resumo else "") + texto

    if "\n## Narração" in doc:
        # entra no fim da secao, antes da proxima secao de mesmo nivel
        ini = doc.index("\n## Narração")
        corte = doc.find("\n## ", ini + 1)
        corte = len(doc) if corte == -1 else corte
        miolo = doc[ini:corte]
        # tira o texto de espera que o modelo da secao traz
        miolo = re.sub(r"\n_\(o que foi lido aos jogadores.*?\)_\n", "\n", miolo,
                       flags=re.S)
        doc = doc[:ini] + miolo.rstrip() + "\n\n" + bloco + "\n" + doc[corte:]
    else:
        # sem a secao (README antigo): cria antes de Acontecimentos, ou no fim
        secao = "\n## Narração\n\n" + bloco + "\n"
        if "\n## Acontecimentos" in doc:
            i = doc.index("\n## Acontecimentos")
            doc = doc[:i] + secao + doc[i:]
        else:
            doc = doc.rstrip() + "\n" + secao
    destino.write_text(doc, encoding="utf-8")

    print(f"Narração {n} gravada em: {destino} (seção Narração)")
    print(f"  {len(texto)} caracteres, {len(texto.split(chr(10) + chr(10)))} parágrafo(s)")
    if len(texto) > 4000:
        print("  AVISO: passa de 4000 caracteres — o WhatsApp corta perto de 4096.")
    if not args.sem_acontecimento:
        resumo = args.resumo or f"Narração {n} lida aos jogadores."
        ok, saida = registrar_acontecimento(raiz, f"[narração {n}] {resumo}")
        print(f"  {'Registrado no histórico' if ok else 'AVISO: nao registrei: ' + saida}")


def main():
    ap = argparse.ArgumentParser(description="Contexto e arquivo das narrações.")
    ap.add_argument("--raiz", default=".", help="Raiz do projeto")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("contexto", help="Lista o que ler antes de narrar")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_contexto)

    s = sub.add_parser("gravar", help="Arquiva a narração no capítulo atual")
    s.add_argument("--texto", default="")
    s.add_argument("--arquivo", default="", help="Arquivo .txt com a narração")
    s.add_argument("--resumo", default="", help="Uma linha: o que foi narrado")
    s.add_argument("--sem-acontecimento", action="store_true",
                   help="Não registrar no histórico da campanha")
    s.set_defaults(func=cmd_gravar)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
