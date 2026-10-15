#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transforma o arquivo de pose (o mesmo do renderizar.py) numa animação "roll6-animation", valida
com as regras do Roll6 (skill criar-animacao) e grava a imagem final do modelo na pose.

    python .claude/skills/copiar-posicao/scripts/gerar.py pose.json --nome "Orc Briguento 1" \
        --tipo idle --modelo orc.glb --ref foto.png

Escreve animacoes/<slug>.json e animacoes/<slug>.png (a última imagem do modelo 3D na pose).

Tipos que repetem (idle, defend, crouch): ciclo de 3 s já na pose, com uma respiração leve
(primeira chave = última). Tipos que tocam uma vez (defeated, attack): sai do descanso e chega
à pose em 0,6 s, e fica nela.
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parents[4]
VALIDAR = RAIZ / ".claude" / "skills" / "criar-animacao" / "scripts" / "validar.py"
REPETEM = {"idle", "defend", "crouch"}
UMA_VEZ = {"defeated", "attack"}

#: respiração: osso → variação em graus no meio do ciclo (volta ao valor da pose no fim)
RESPIRA = {"Spine1": [-1.0, 0, 0], "Spine2": [-0.8, 0, 0], "Neck": [0.8, 0, 0]}


def slug(nome):
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def soma(a, b, k=1.0):
    return [round(a[i] + b[i] * k, 2) for i in range(3)]


def montar(pose, nome, tipo, descricao):
    graus = {o: list(v) for o, v in pose.get("graus", {}).items()}
    lift = pose.get("hipsLift", 0.0)
    lift_de = pose.get("hipsLiftDe", "height")
    if tipo in REPETEM:
        tempos = [0, 0.75, 1.5, 2.25, 3]
        fase = [0, 0.5, 1, 0.5, 0]
        osso_ids = set(graus) | set(RESPIRA)
        trilhas = []
        for osso in sorted(osso_ids):
            base = graus.get(osso, [0, 0, 0])
            var = RESPIRA.get(osso, [0, 0, 0])
            trilhas.append({"bone": osso, "times": tempos, "degrees": [soma(base, var, f) for f in fase]})
        elev = {"times": tempos, "values": [round(lift + (-0.002 * f), 4) for f in fase]}
        dur, laco = 3, True
    elif tipo in UMA_VEZ:
        tempos = [0, 0.3, 0.6]
        trilhas = [{"bone": o, "times": tempos,
                    "degrees": [[0, 0, 0], soma([0, 0, 0], v, 0.5), v]} for o, v in sorted(graus.items())]
        elev = {"times": tempos, "values": [0, round(lift / 2, 4), round(lift, 4)]}
        dur, laco = 0.6, False
    else:
        raise SystemExit(f"tipo '{tipo}' sem receita aqui; use idle, defend, crouch, defeated ou attack "
                         "(walk e run pedem movimento: use a skill criar-animacao)")
    if lift_de != "height":
        elev["of"] = lift_de
    d = {"format": "roll6-animation", "version": 1, "name": nome, "type": tipo,
         "description": descricao, "duration": dur, "loop": laco, "tracks": trilhas}
    if any(elev["values"]):
        d["hipsLift"] = elev
    return d


def main(argv):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pose")
    p.add_argument("--nome", required=True)
    p.add_argument("--tipo", default="idle")
    p.add_argument("--descricao", default=None)
    p.add_argument("--modelo", help=".glb, para gravar a imagem final")
    p.add_argument("--ref", help="imagem de referência (define o tamanho e o enquadramento da imagem final)")
    p.add_argument("--pasta", default=str(RAIZ / "animacoes"))
    a = p.parse_args(argv)

    pose = json.load(open(a.pose, encoding="utf-8"))
    desc = a.descricao or pose.get("descricao") or         (f"Pose copiada de {Path(a.ref).name}." if a.ref else "Pose copiada de uma imagem.")
    anim = montar(pose, a.nome, a.tipo, desc)
    pasta = Path(a.pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    alvo = pasta / f"{slug(a.nome)}.json"
    alvo.write_text(json.dumps(anim, ensure_ascii=False, indent=2), encoding="utf-8")
    r = subprocess.run([sys.executable, "-I", str(VALIDAR), str(alvo)], capture_output=True, text=True,
                       encoding="utf-8")
    print((r.stdout or r.stderr).strip())
    if r.returncode != 0:
        return 1

    if a.modelo and a.ref:
        import glb
        import renderizar
        from PIL import Image
        modelo = glb.carregar(a.modelo)
        rgb, mascara = renderizar.carregar_referencia(a.ref)
        mascara = renderizar.aplicar_exclusoes(mascara, pose)
        img, sm, _ = renderizar.renderizar(modelo, pose, rgb, mascara)
        iou, _ = renderizar.comparar(rgb, mascara, img, sm)
        png = alvo.with_suffix(".png")
        Image.fromarray(img).save(png)
        print(f"imagem final: {png} (IoU com a referência: {iou:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
