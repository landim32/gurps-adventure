import json
from pathlib import Path

caminho = Path(r"C:\repos\gurps-adventure\animacoes\ogro.json")
anim = json.loads(caminho.read_text(encoding="utf-8"))
alvo = 2.732900000005962


def valor_em(times, graus, t):
    for i, x in enumerate(times):
        if abs(x - t) < 1e-9:
            return graus[i]
    for i in range(len(times) - 1):
        if times[i] < t < times[i + 1]:
            f = (t - times[i]) / (times[i + 1] - times[i])
            return [round(a + (b - a) * f, 2) for a, b in zip(graus[i], graus[i + 1])]
    raise ValueError(t)


for tr in anim["tracks"]:
    tr["degrees"] = [valor_em(tr["times"], tr["degrees"], alvo)]
    tr["times"] = [0]

h = anim["hipsLift"]
h["values"] = [round(valor_em(h["times"], [[v] for v in h["values"]], alvo)[0], 4)]
h["times"] = [0]

anim["description"] = "Ogro de pé, tronco reto, com o braço direito na pose 5 e o braço esquerdo caído."
caminho.write_text(json.dumps(anim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
