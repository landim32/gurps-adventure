#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valida arquivos de animação no formato "roll6-animation" (versão 1) — exatamente as regras do
Roll6 (servidor `Domain/Animations/AnimationFormat.cs` e site `lib/animationFormat.ts`, feature
059): mesmas chaves de erro, mesma ordem, mesmas mensagens. Um arquivo que passa aqui é aceito
pelo envio do Roll6.

    python .claude/skills/criar-animacao/scripts/validar.py animacoes/golpe.json [outro.json ...]

Saída: "OK <arquivo> (1,4 s, uma vez, 13 ossos)" ou "ERRO <arquivo> <chave>: <mensagem>".
Código de saída 1 se algum arquivo falhar.
"""
import json
import math
import sys
from pathlib import Path

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

FORMATO = "roll6-animation"
VERSAO = 1
MAX_BYTES = 1_048_576
MAX_DURACAO = 30
MAX_TRILHAS = 64
MAX_CHAVES = 600
MAX_GRAUS = 360
MAX_ELEVACAO = 2
TOLERANCIA = 1e-6

_LADOS = ("Left", "Right")
_CORPO_LADO = ("Shoulder", "Arm", "ForeArm", "Hand", "UpLeg", "Leg", "Foot", "ToeBase")
_DEDOS = ("Thumb", "Index", "Middle", "Ring", "Pinky")

#: Os 52 ossos Mixamo (sem o prefixo "mixamorig:") que uma animação pode mover.
OSSOS = frozenset(
    ["Hips", "Spine", "Spine1", "Spine2", "Neck", "Head"]
    + [lado + osso for lado in _LADOS for osso in _CORPO_LADO]
    + [f"{lado}Hand{dedo}{n}" for lado in _LADOS for dedo in _DEDOS for n in (1, 2, 3)]
)

#: Tipos sugeridos pelo arquivo (inglês), na ordem dos tipos da biblioteca (1–7).
TIPOS = ("idle", "walk", "run", "crouch", "defeated", "attack", "defend")
TIPOS_PT = ("Parado", "Andando", "Correndo", "Agachado", "Derrotado", "Atacando", "Defendendo")


def _numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _instantes_validos(v, duracao):
    if not isinstance(v, list) or not (1 <= len(v) <= MAX_CHAVES):
        return False
    if not all(_numero(x) for x in v) or v[0] != 0:
        return False
    if any(v[i] <= v[i - 1] for i in range(1, len(v))):
        return False
    return v[-1] <= duracao + TOLERANCIA


def validar(valor, tamanho=None):
    """O primeiro problema como (chave, mensagem), ou None se o arquivo é válido."""
    if tamanho is not None and tamanho > MAX_BYTES:
        return "content", "O arquivo de animação passa de 1 MB."
    if not isinstance(valor, dict):
        return "content", "O conteúdo da animação deve ser um objeto JSON."
    if valor.get("format") != FORMATO:
        return "content.format", 'O campo "format" deve ser "roll6-animation".'
    versao = valor.get("version")
    if not _numero(versao) or versao != VERSAO:
        return "content.version", "Versão do formato não suportada (use 1)."
    duracao = valor.get("duration")
    if not _numero(duracao) or duracao <= 0 or duracao > MAX_DURACAO:
        return "content.duration", "A duração deve ser um número maior que 0 e até 30 segundos."
    if not isinstance(valor.get("loop"), bool):
        return "content.loop", 'O campo "loop" deve ser true ou false.'
    trilhas = valor.get("tracks")
    if not isinstance(trilhas, list) or not (1 <= len(trilhas) <= MAX_TRILHAS):
        return "content.tracks", 'A animação precisa de 1 a 64 trilhas ("tracks").'

    vistos = set()
    for i, trilha in enumerate(trilhas):
        n, chave = i + 1, f"content.tracks[{i}]"
        if not isinstance(trilha, dict):
            return chave, f"A trilha {n} deve ser um objeto."
        osso = trilha.get("bone")
        if not isinstance(osso, str) or osso == "":
            return f"{chave}.bone", f'A trilha {n} precisa do nome do osso ("bone").'
        if osso not in OSSOS:
            return f"{chave}.bone", f'Osso "{osso}" não existe no esqueleto Mixamo (trilha {n}).'
        if osso in vistos:
            return f"{chave}.bone", f'O osso "{osso}" aparece em mais de uma trilha (trilha {n}).'
        vistos.add(osso)
        instantes = trilha.get("times")
        if not _instantes_validos(instantes, duracao):
            return (f"{chave}.times",
                    f"Os instantes da trilha {n} devem ser de 1 a 600 números, começando em 0, em ordem crescente e até a duração.")
        graus = trilha.get("degrees")
        if not (isinstance(graus, list) and len(graus) == len(instantes) and all(
                isinstance(t, list) and len(t) == 3 and all(_numero(x) and abs(x) <= MAX_GRAUS for x in t) for t in graus)):
            return f"{chave}.degrees", f"A trilha {n} precisa de um giro [x, y, z] por instante, cada valor entre -360 e 360."

    if "hipsLift" in valor:
        quadril = valor["hipsLift"]
        if not isinstance(quadril, dict):
            return "content.hipsLift", 'O campo "hipsLift" deve ser um objeto.'
        instantes = quadril.get("times")
        if not _instantes_validos(instantes, duracao):
            return ("content.hipsLift.times",
                    'Os instantes de "hipsLift" devem ser de 1 a 600 números, começando em 0, em ordem crescente e até a duração.')
        valores = quadril.get("values")
        if not (isinstance(valores, list) and len(valores) == len(instantes)
                and all(_numero(x) and abs(x) <= MAX_ELEVACAO for x in valores)):
            return "content.hipsLift.values", '"hipsLift" precisa de um valor por instante, cada um entre -2 e 2.'
        if "of" in quadril and quadril["of"] not in ("height", "hips"):
            return "content.hipsLift.of", '"hipsLift.of" deve ser "height" ou "hips".'
    return None


def ler(caminho):
    """(animação, erro) de um arquivo: erro = (chave, mensagem) ou None."""
    bruto = Path(caminho).read_bytes()
    try:
        valor = json.loads(bruto.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        return None, ("content", "O arquivo não é um JSON válido.")
    return valor, validar(valor, len(bruto))


def resumo(valor):
    segundos = f"{valor['duration']:g}".replace(".", ",")
    vezes = "repete" if valor["loop"] else "uma vez"
    return f"{segundos} s, {vezes}, {len(valor['tracks'])} ossos"


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    falhou = False
    for caminho in argv:
        try:
            valor, erro = ler(caminho)
        except OSError as e:
            print(f"ERRO {caminho} content: não foi possível ler o arquivo ({e.strerror}).")
            falhou = True
            continue
        if erro:
            print(f"ERRO {caminho} {erro[0]}: {erro[1]}")
            falhou = True
        else:
            print(f"OK {caminho} ({resumo(valor)})")
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
