#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envia uma animação (formato "roll6-animation") para a biblioteca de animações do Roll6 pelo
servidor MCP — o mesmo acesso que a skill `roll6` usa (ROLL6_URL/ROLL6_API_KEY ou o servidor
"roll6" do ~/.claude.json). Valida antes com as regras do Roll6 (validar.py).

    python .claude/skills/criar-animacao/scripts/enviar.py animacoes/golpe.json --nome "Golpe de machado" --tipo Atacando

--nome  padrão: o "name" do arquivo, senão o nome do arquivo sem .json
--tipo  Parado, Andando, Correndo, Agachado, Derrotado, Atacando ou Defendendo (ou idle, walk,
        run, crouch, defeated, attack, defend); padrão: o "type" do arquivo

Imprime o animationId e o valor para usar no token: animation:{id}.
"""
import argparse
import importlib.util
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import validar  # noqa: E402

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

#: Tipos que já podem ser escolhidos nos estados do token (Parado ← 1, Caminhando ← 2, Caído ← 5).
USADOS_NO_TOKEN = {1: "Parado", 2: "Caminhando", 5: "Caído"}


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


def tipo_de(texto):
    """1–7 a partir do nome em português ou inglês (ou do número)."""
    if texto is None:
        return None
    t = _sem_acento(str(texto).strip())
    if t.isdigit() and 1 <= int(t) <= 7:
        return int(t)
    for i, (en, pt) in enumerate(zip(validar.TIPOS, validar.TIPOS_PT), start=1):
        if t in (en, _sem_acento(pt)):
            return i
    return None


def _roll6():
    """O módulo da skill roll6 (o cliente MCP), sem alterar nada nele."""
    caminho = AQUI.parents[1] / "roll6" / "scripts" / "roll6.py"
    espec = importlib.util.spec_from_file_location("roll6", caminho)
    modulo = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(modulo)
    return modulo


def main(argv):
    p = argparse.ArgumentParser(description="Envia uma animação para a biblioteca do Roll6.")
    p.add_argument("arquivo")
    p.add_argument("--nome")
    p.add_argument("--tipo")
    a = p.parse_args(argv)

    valor, erro = validar.ler(a.arquivo)
    if erro:
        print(f"ERRO {a.arquivo} {erro[0]}: {erro[1]}")
        return 1
    tipo = tipo_de(a.tipo) if a.tipo else tipo_de(valor.get("type"))
    if tipo is None:
        print("ERRO informe o tipo com --tipo (Parado, Andando, Correndo, Agachado, Derrotado, Atacando ou Defendendo).")
        return 1
    nome = (a.nome or valor.get("name") or Path(a.arquivo).stem).strip()[:100]

    roll6 = _roll6()
    try:
        criada = roll6.cliente().chamar("create_animation", {"name": nome, "type": tipo, "content": valor})
    except roll6.Roll6Erro as e:
        print(f"roll6: {e}")
        return 1
    ident = criada["animationId"]
    print(f"Enviada: \"{criada['name']}\" — {validar.TIPOS_PT[tipo - 1]}, animationId {ident}.")
    if tipo in USADOS_NO_TOKEN:
        print(f"No token, estado {USADOS_NO_TOKEN[tipo]}: animation:{ident}")
    else:
        print("Este tipo fica guardado na biblioteca: por enquanto os tokens só usam Parado, Andando e Derrotado.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
