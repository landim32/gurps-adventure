#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rola dados de GURPS.

    roll.py 1d+1        um dado de 6 faces, mais 1
    roll.py 3d          tres dados
    roll.py 2D-1        maiusculo tanto faz
    roll.py 2dx10       multiplicador (GURPS escreve "2Dx10")
    roll.py 1d 1d 3d-2  varias rolagens de uma vez

Cada dado e um aleatorio de 1 a 6. Imprime cada dado, a conta e o total.
"""
import argparse
import random
import re
import sys

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 3d+2, 1d, 2D-1, 2dx10 — o "6" de "1d6" e opcional e ignorado (todo dado tem 6 faces)
RE_FORMULA = re.compile(r"""^\s*
    (?P<n>\d+)?\s*[dD]\s*6?\s*
    (?P<mod>[+-]\s*\d+)?\s*
    (?:[x*×]\s*(?P<mult>\d+))?\s*$""", re.X)


def d6(n=1):
    """Um ou mais dados de 6 faces. É por aqui que toda skill rola dado."""
    return [random.randint(1, 6) for _ in range(n)]


def parse(txt):
    """'2D-1' -> (2, -1, 1). '3d' -> (3, 0, 1). '2dx10' -> (2, 0, 10)."""
    m = RE_FORMULA.match(txt)
    if not m:
        raise SystemExit(f'Não entendi "{txt}". Use 1d, 1d+1, 3d, 2D-1, 2dx10.')
    n = int(m.group("n") or 1)
    mod = int(re.sub(r"\s+", "", m.group("mod") or "0"))
    mult = int(m.group("mult") or 1)
    if not 1 <= n <= 100:
        raise SystemExit(f"{n} dados é fora do razoável.")
    return n, mod, mult


def rolar(txt):
    """Devolve (total, linha_legivel)."""
    n, mod, mult = parse(txt)
    dados = d6(n)
    total = sum(dados)

    # os dados entre colchetes, para nao confundir dado com modificador
    conta = "[" + ", ".join(str(d) for d in dados) + "]"
    if n > 1:
        conta += f" = {total}"
    if mod:
        total += mod
        conta += f" {'+' if mod > 0 else '-'} {abs(mod)} = {total}"
    if mult != 1:
        total *= mult
        conta += f" × {mult} = {total}"

    # o total aparece uma vez so, sempre em negrito no fim
    conta = re.sub(r"= \d+$", "", conta).rstrip()
    return total, f"{txt}: {conta} = **{total}**"


def main():
    ap = argparse.ArgumentParser(
        description="Rola dados de 6 faces no formato do GURPS.")
    ap.add_argument("formulas", nargs="+", metavar="FORMULA",
                    help="1d+1, 3d, 2D-1, 2dx10...")
    ap.add_argument("--vezes", type=int, default=1,
                    help="Repete cada fórmula N vezes")
    args = ap.parse_args()

    if args.vezes < 1:
        raise SystemExit("--vezes precisa ser 1 ou mais.")

    totais = []
    for f in args.formulas:
        for _ in range(args.vezes):
            total, linha = rolar(f)
            totais.append(total)
            print(linha)

    if len(totais) > 1:
        print(f"\nSoma de tudo: {sum(totais)}")


if __name__ == "__main__":
    main()
