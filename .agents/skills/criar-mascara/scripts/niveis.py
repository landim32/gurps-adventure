#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""niveis — a escala de alturas da Máscara 3D e a conversão altura <-> tom de cinza.

    niveis.py                 # imprime a tabela de níveis
    niveis.py --tom 171       # que altura é o cinza 171?
    niveis.py --altura 0.33   # que cinza dá 33% da altura?

No Roll6 o tom de cada ponto da máscara é a ALTURA da parede ali:

    altura = 1 - tom / 255      preto (0) = parede inteira, branco (255) = vazio
    abaixo de 5% de altura vira vazio; a partir de 95% vale a parede inteira.

A parede inteira tem 120 unidades do mundo 3D (3 hexágonos de 40 px de raio / 1,5 largura de
hexágono); uma pessoa em pé tem 64 unidades (53%) e os olhos da câmera ficam a ~60 (50%).
Daí a conversão em metros usada nas tabelas: 1,7 m (uma pessoa) = 53%, parede inteira ~ 3,2 m.

Os outros scripts importam este módulo (`from niveis import ...`).
"""
import argparse
import sys

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Limites que o Roll6 aplica por célula da máscara reduzida.
ALTURA_MINIMA = 0.05    # abaixo disso a célula é vazio
ALTURA_INTEIRA = 0.95   # a partir disso a célula é parede inteira
# Calibração: uma pessoa de 1,7 m = 53% da parede inteira  =>  parede inteira ~ 3,2 m.
METROS_PAREDE = 3.2
OLHOS = 0.50            # altura dos olhos da câmera: abaixo dela se vê por cima da parede

# nome -> (altura 0-1, exemplos). Ordem: do mais alto ao mais baixo.
NIVEIS = {
    "parede":       (1.00, "paredes, colunas, fachadas, troncos grossos, penhascos (3,2 m ou mais)"),
    "rocha-grande": (0.78, "rochedo, estátua grande, árvore caída, carroça (cerca de 2,5 m)"),
    "estante":      (0.63, "estante, armário, tapeçaria pendurada, lareira (cerca de 2 m)"),
    "muro-alto":    (0.53, "muro até a altura de uma pessoa, barril grande, cerca alta (cerca de 1,7 m)"),
    "parapeito":    (0.40, "parapeito, mureta de jardim, mesa de mapa alta (cerca de 1,3 m)"),
    "balcao":       (0.33, "balcão de taverna, muro baixo, altar, sarcófago (cerca de 1,05 m)"),
    "mesa":         (0.23, "mesa, bancada, cama (cerca de 0,75 m)"),
    "banco":        (0.14, "banco, baú, caixote, degrau alto (cerca de 0,45 m)"),
    "degrau":       (0.08, "degrau baixo, soleira (cerca de 0,25 m)"),
    "vazio":        (0.00, "piso, tapete, porta aberta, arco, passagem"),
}


def tom_de(altura):
    """Tom de cinza (0-255) que dá essa altura (0-1) de parede."""
    altura = max(0.0, min(1.0, float(altura)))
    return int(round(255 * (1 - altura)))


def altura_de(tom):
    """Altura (0-1) que o Roll6 lê de um tom de cinza (0-255), com os encaixes de 5% e 95%."""
    h = 1 - float(tom) / 255
    if h < ALTURA_MINIMA:
        return 0.0
    if h >= ALTURA_INTEIRA:
        return 1.0
    return h


def altura_do_nivel(nome):
    try:
        return NIVEIS[nome][0]
    except KeyError:
        raise SystemExit(f"nível desconhecido: {nome!r} (use um de: {', '.join(NIVEIS)})")


def resolve_altura(forma, padrao=1.0):
    """Altura (0-1) de uma forma do JSON: `altura` (0-1), senão `metros`, senão `nivel`, senão o padrão."""
    if "altura" in forma:
        return max(0.0, min(1.0, float(forma["altura"])))
    if "metros" in forma:
        return max(0.0, min(1.0, float(forma["metros"]) / METROS_PAREDE))
    if "nivel" in forma:
        return altura_do_nivel(forma["nivel"])
    return padrao


def nivel_mais_proximo(altura):
    """(nome, altura do nível) do degrau da escala mais próximo dessa altura."""
    nome = min(NIVEIS, key=lambda n: abs(NIVEIS[n][0] - altura))
    return nome, NIVEIS[nome][0]


def main():
    ap = argparse.ArgumentParser(description="Escala de alturas da Máscara 3D.")
    ap.add_argument("--tom", type=int, help="mostra a altura do tom (0-255)")
    ap.add_argument("--altura", type=float, help="mostra o tom da altura (0-1)")
    a = ap.parse_args()
    if a.tom is not None:
        print(f"tom {a.tom}: altura {altura_de(a.tom) * 100:.0f}% (~{altura_de(a.tom) * METROS_PAREDE:.2f} m)")
    if a.altura is not None:
        print(f"altura {a.altura * 100:.0f}%: tom {tom_de(a.altura)}")
    if a.tom is None and a.altura is None:
        print(f"{'nível':13} {'altura':>6} {'tom':>4}  {'metros':>6}  exemplos")
        for nome, (h, ex) in NIVEIS.items():
            print(f"{nome:13} {h * 100:5.0f}% {tom_de(h):4}  {h * METROS_PAREDE:5.2f}m  {ex}")
        print(f"\nolhos da câmera: ~{OLHOS * 100:.0f}% (acima disso a parede esconde o que está atrás; "
              f"abaixo, vê-se por cima). Abaixo de {ALTURA_MINIMA * 100:.0f}% = vazio.")


if __name__ == "__main__":
    main()
