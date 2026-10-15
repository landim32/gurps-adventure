#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca local (subida de encosta) em volta da pose atual: mexe um giro de cada vez, mantém o que
sobe a nota (IoU da silhueta menos o erro médio das juntas marcadas em "alvos") e passa a passos
menores. Serve para **refinar** uma primeira pose escrita à mão — não para achá-la do zero — e
sempre deve ser seguida de olhar a imagem: a nota pode subir escondendo um braço dentro do corpo.

    python .claude/skills/copiar-posicao/scripts/otimizar.py modelo.glb ref.png pose.json \
        --saida pose-otim.json [--ossos Hips,Spine,RightArm,...] [--passos 12,6,3] [--rodadas 3]

Os limites padrão seguem o corpo humano; o arquivo de pose pode **apertá-los** com
"limites": {"Spine": [[-6, 6], [-15, 15], [-15, 15]], ...} (por osso: faixa de X, de Y e de Z).
Use para manter o tronco em pé: sem isso a busca compensa a diferença de proporção entre o modelo
e a imagem inclinando o corpo para a frente.
Só mexe nos ossos de `graus` que não sejam dedos (ou nos de --ossos). Limites de cada junta seguem
o corpo humano (joelho e cotovelo só dobram para o lado certo).
"""
import argparse
import copy
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import glb  # noqa: E402
import renderizar as R  # noqa: E402

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

_COLUNA = {"Hips": 60, "Spine": 40, "Spine1": 30, "Spine2": 30, "Neck": 35, "Head": 45}


LIMITES_POSE = {}   # {osso: [[min,max] x, [min,max] y, [min,max] z]} do arquivo de pose


def limites(osso, i):
    if osso in LIMITES_POSE:
        return tuple(LIMITES_POSE[osso][i])
    if osso.endswith("ForeArm"):
        # no Roll6 o antebraço gira no referencial da pose T: X é torção, Y dobra o cotovelo
        # para a frente (negativo na esquerda, positivo na direita), Z o dobra para o lado
        if i == 1:
            return (-150, 20) if osso.startswith("Left") else (-20, 150)
        if i == 2:   # dobra para o lado/para cima, no plano frontal
            return (-20, 150) if osso.startswith("Left") else (-150, 20)
        return (-90, 90)
    if osso.endswith("UpLeg"):
        return (-80, 40) if i == 0 else (-35, 35)
    if osso.endswith("Leg"):
        return (0, 90) if i == 0 else (-10, 10)
    if osso.endswith("Arm"):
        return (-100, 30) if i == 0 else (-60, 60)
    v = _COLUNA.get(osso, 40)
    return (-v, v)


def main(argv):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("modelo")
    p.add_argument("referencia")
    p.add_argument("pose")
    p.add_argument("--saida", required=True)
    p.add_argument("--ossos", help="lista separada por vírgula; padrão: todos os de `graus` menos dedos")
    p.add_argument("--passos", default="12,6,3")
    p.add_argument("--rodadas", type=int, default=3)
    a = p.parse_args(argv)

    modelo = glb.carregar(a.modelo)
    rgb, mascara = R.carregar_referencia(a.referencia)
    pose = json.load(open(a.pose, encoding="utf-8"))
    mascara = R.aplicar_exclusoes(mascara, pose)
    alvos = pose.get("alvos", {})
    LIMITES_POSE.update(pose.get("limites", {}))

    def nota(q):
        img, sm, j = R.renderizar(modelo, q, rgb, mascara)
        iou = R.comparar(rgb, mascara, img, sm)[0]
        return R.nota(iou, R.erro_alvos(j, alvos))

    livres = a.ossos.split(",") if a.ossos else [o for o in pose["graus"] if "Hand" not in o or o.endswith("Hand")]
    melhor = nota(pose)
    print(f"início: nota {melhor:.4f}")
    t0 = time.time()
    for passo in [int(x) for x in a.passos.split(",")]:
        for r in range(a.rodadas):
            mudou = False
            for osso in livres:
                pose["graus"].setdefault(osso, [0, 0, 0])
                for i in range(3):
                    lo, hi = limites(osso, i)
                    for s in (passo, -passo):
                        v = pose["graus"][osso][i] + s
                        if not lo <= v <= hi:
                            continue
                        q = copy.deepcopy(pose)
                        q["graus"][osso][i] = v
                        n = nota(q)
                        if n > melhor + 1e-4:
                            melhor, pose, mudou = n, q, True
            print(f"passo {passo}° rodada {r + 1}: nota {melhor:.4f} ({time.time() - t0:.0f} s)")
            if not mudou:
                break
    json.dump(pose, open(a.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"escreveu {a.saida} — agora renderize e OLHE a comparação")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
