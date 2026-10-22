"""Acrescenta as formas de Metamorfose ao grimorio.jpg, logo abaixo das magias.

Uso (a partir da raiz): python historico/personagens/ilvaren-vento-manso/formas_grimorio.py
Roda DEPOIS de preencher_grimorio.py (que gera as magias) e sobrescreve o grimorio.jpg.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / ".claude/skills/criar-personagem/scripts"))
from preencher_grimorio import LINHAS, DESC_X, DESC_SIZE, DESC_LARGURA, DESC_BRANCO, draw_field  # noqa: E402

ARQ = Path(__file__).with_name("grimorio.jpg")

# (texto, "titulo"|"linha"|"branco") — cada item ocupa uma regra da folha
BLOCOS = [
    ("", "branco"),
    ("FORMAS DA METAMORFOSE (blocos de NPC em formas-npc.md)", "titulo"),
    ("Tigre | ST 30 DX 14 IQ 14 HT 14 | Desl 10 | Esquiva 11 Aparar 11 | DP 1 RD 3 | PV 14 Fadiga 30 | 2 hexes, 272 kg", "linha"),
    ("Ataques: mordida 1D+2 corte e garras 1D+2 corte (Briga 16).", "linha"),
    ("", "branco"),
    ("Urso | ST 20 DX 13 IQ 14 HT 14 | Desl 8 | Esquiva 9 Aparar 11 | DP 1 RD 4 | PV 14 Fadiga 20 | 2 hexes (1 em pé), 272 kg", "linha"),
    ("Ataques: mordida 1D corte e garras 2D-1 contusão (Briga 15).", "linha"),
    ("", "branco"),
    ("Águia gigante | ST 10 DX 13 IQ 14 HT 12 | Desl 20 (voo) | Esquiva 10 Aparar 11 | DP 0 RD 0 | PV 12 Fadiga 10 | 1 hex, 34 kg", "linha"),
    ("Ataque: garras 1D-2 perfuração (Briga 15). Envergadura de 3,65 m.", "linha"),
    ("", "branco"),
    ("Cobra gigante | ST 20 DX 13 IQ 14 HT 24 | Desl 4 | Esquiva 5, sem Aparar | RD 3 | PV 24 Fadiga 20 | 4 hexes (4 m), 68 kg", "linha"),
    ("Ataque: esmaga 1D contusão depois de segurar a vítima; só armadura de placas protege (com toda a RD).", "linha"),
    ("", "branco"),
    ("Toda forma: teste de IQ por hora (falha perde 1 de IQ; IQ 7 prende na forma até Remoção de Maldição). Mudar leva 3 seg, indefeso.", "linha"),
    ("Não fala nem usa as mãos; só faz mágica sem gesto (Fadiga p/ mágica continua 10). Roupas somem e voltam; mochila e bastão caem.", "linha"),
]

img = Image.open(ARQ).convert("RGB")
draw = ImageDraw.Draw(img)
primeira = 10  # as 10 mágicas ocupam as regras 0..9
for k, (texto, tipo) in enumerate(BLOCOS):
    i = primeira + k
    if i >= LINHAS["max_rows"]:
        continue
    y = int(LINHAS["start_baseline"] + i * LINHAS["row_h"])
    topo = int(y - 52)
    base = int(y + 5)
    draw.rectangle((DESC_BRANCO[0], topo, DESC_BRANCO[1], base), fill=(255, 255, 255))
    if tipo == "branco":
        continue
    tam = DESC_SIZE + (4 if tipo == "titulo" else 0)
    draw_field(draw, (DESC_X, y, tam, "left", DESC_LARGURA), texto)
img.save(ARQ, quality=92)
print("formas acrescentadas ao", ARQ)
