#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""detectar — ponto de partida: acha as paredes por cor ou luminosidade.

    detectar.py --imagem mapa.png --cor 137,130,122 --tolerancia 25 --saida detectado.png
    detectar.py --imagem mapa.png --escuro 60 --minimo 300 --fechar 3 --saida detectado.png \
                --saida-json mapa-mascara.json
    detectar.py --imagem mapa.png --cinza 28 --saida detectado.png     # pedra: pouca cor

Marca como parede os pixels que casam com o critério (qualquer um dos informados):
  --cor R,G,B (ou #RRGGBB, pode repetir) com --tolerancia (maior diferença em um canal, 40);
  --escuro N  : luminosidade <= N (0-255), para tijolo escuro e traço grosso;
  --claro N   : luminosidade >= N;
  --cinza S   : saturação <= S (0-255) e luminosidade entre --luz-min e --luz-max,
                para pedra cinza sobre piso colorido.
Depois fecha buracos (`--fechar` px: dilata e erode) e joga fora as manchas com menos de
`--minimo` px. Salva um PNG de 0/255 (preto = parede) e, com `--saida-json`, um JSON que
já referencia esse PNG (forma `imagem`), pronto para receber retângulos a mais ou
aberturas à mão. É só o começo: confira na prévia e refine o JSON.

Cada detecção vale UMA altura de parede (a Máscara 3D usa o tom como altura): `--altura 0.33`,
`--metros 1.05` ou `--nivel balcao` (veja niveis.py) vão para o JSON na forma `imagem`; sem
nada, é parede inteira. Para uma cena com alturas diferentes, rode a detecção uma vez por
tipo de elemento (paredes de tijolo, depois o balcão por cor) e junte tudo no mesmo JSON com
`--acrescentar`.
"""
import argparse
import colorsys
import json
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from niveis import NIVEIS  # noqa: E402

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def cor(txt):
    t = txt.strip().lstrip("#")
    if "," in t:
        r, g, b = [int(v) for v in t.split(",")]
        return r, g, b
    return int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16)


def casa_cor(img, alvo, tol):
    canais = img.split()
    pior = None
    for canal, v in zip(canais, alvo):
        dif = ImageChops.difference(canal, Image.new("L", img.size, v))
        pior = dif if pior is None else ImageChops.lighter(pior, dif)
    return pior.point(lambda p: 255 if p <= tol else 0)


def tira_manchas(mascara, minimo):
    """Remove componentes (4-vizinhos) de 255 com menos de `minimo` pixels."""
    larg, alt = mascara.size
    dados = bytearray(mascara.tobytes())
    visto = bytearray(larg * alt)
    removidas = 0
    for ini in range(larg * alt):
        if dados[ini] != 255 or visto[ini]:
            continue
        fila = deque([ini])
        visto[ini] = 1
        comp = [ini]
        while fila:
            p = fila.popleft()
            x = p % larg
            for q in (p - larg, p + larg, p - 1 if x else -1, p + 1 if x < larg - 1 else -1):
                if 0 <= q < larg * alt and dados[q] == 255 and not visto[q]:
                    visto[q] = 1
                    fila.append(q)
                    comp.append(q)
        if len(comp) < minimo:
            for p in comp:
                dados[p] = 0
            removidas += 1
    return Image.frombytes("L", mascara.size, bytes(dados)), removidas


def main():
    ap = argparse.ArgumentParser(description="Detecta paredes por cor ou luminosidade.")
    ap.add_argument("--imagem", required=True)
    ap.add_argument("--saida", required=True, help="PNG 0/255, preto = parede")
    ap.add_argument("--saida-json", help="JSON de paredes que referencia o PNG detectado")
    ap.add_argument("--acrescentar", action="store_true",
                    help="com --saida-json: soma a detecção ao JSON que já existe (mesmo tamanho) em vez de recriá-lo")
    ap.add_argument("--altura", type=float, help="altura da parede detectada, 0 a 1 (padrão: inteira)")
    ap.add_argument("--metros", type=float, help="altura da parede detectada em metros (inteira ~ 3,2 m)")
    ap.add_argument("--nivel", choices=list(NIVEIS), help="altura pelo nome da escala (niveis.py)")
    ap.add_argument("--nome", help="rótulo da forma no JSON (documentação)")
    ap.add_argument("--cor", action="append", type=cor, help="R,G,B ou #RRGGBB; pode repetir")
    ap.add_argument("--tolerancia", type=int, default=40)
    ap.add_argument("--escuro", type=int, help="luminosidade <= N")
    ap.add_argument("--claro", type=int, help="luminosidade >= N")
    ap.add_argument("--cinza", type=int, help="saturação <= S (0-255)")
    ap.add_argument("--luz-min", type=int, default=0, help="com --cinza: luminosidade mínima (0)")
    ap.add_argument("--luz-max", type=int, default=255, help="com --cinza: luminosidade máxima (255)")
    ap.add_argument("--minimo", type=int, default=200, help="área mínima da mancha, em px (200)")
    ap.add_argument("--fechar", type=int, default=2, help="raio do fechamento de buracos, em px (2)")
    a = ap.parse_args()

    if not (a.cor or a.escuro is not None or a.claro is not None or a.cinza is not None):
        ap.error("informe ao menos um critério: --cor, --escuro, --claro ou --cinza")

    img = Image.open(a.imagem).convert("RGB")
    lum = img.convert("L")
    acha = Image.new("L", img.size, 0)
    for alvo in a.cor or []:
        acha = ImageChops.lighter(acha, casa_cor(img, alvo, a.tolerancia))
    if a.escuro is not None:
        acha = ImageChops.lighter(acha, lum.point(lambda p: 255 if p <= a.escuro else 0))
    if a.claro is not None:
        acha = ImageChops.lighter(acha, lum.point(lambda p: 255 if p >= a.claro else 0))
    if a.cinza is not None:
        sat = img.convert("HSV").split()[1].point(lambda p: 255 if p <= a.cinza else 0)
        luz = lum.point(lambda p: 255 if a.luz_min <= p <= a.luz_max else 0)
        acha = ImageChops.lighter(acha, ImageChops.multiply(sat, luz))

    if a.fechar > 0:
        t = 2 * a.fechar + 1
        acha = acha.filter(ImageFilter.MaxFilter(t)).filter(ImageFilter.MinFilter(t))
    acha, n = tira_manchas(acha, a.minimo)

    # preto = parede
    saida = acha.point(lambda p: 0 if p >= 128 else 255)
    saida.save(a.saida)
    pct = acha.histogram()[255] / (img.width * img.height) * 100
    print(f"detectado: {a.saida}  ({img.width}x{img.height} px; {pct:.1f}% de parede; "
          f"{n} mancha(s) menor(es) que {a.minimo} px descartada(s))")

    if a.saida_json:
        forma = {"tipo": "imagem", "arquivo": Path(a.saida).name}
        if a.altura is not None:
            forma["altura"] = a.altura
        elif a.metros is not None:
            forma["metros"] = a.metros
        elif a.nivel:
            forma["nivel"] = a.nivel
        if a.nome:
            forma["nome"] = a.nome
        destino = Path(a.saida_json)
        if a.acrescentar and destino.exists():
            doc = json.loads(destino.read_text(encoding="utf-8"))
            if (doc.get("largura"), doc.get("altura")) != (img.width, img.height):
                raise SystemExit(f"{destino} tem {doc.get('largura')}x{doc.get('altura')} e a imagem {img.width}x{img.height}")
            doc.setdefault("paredes", []).append(forma)
        else:
            doc = {"largura": img.width, "altura": img.height, "paredes": [forma], "aberturas": []}
        destino.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"json: {a.saida_json}  (acrescente retângulos/polígonos em \"paredes\" e \"aberturas\", "
              f"cada um com \"nivel\", \"metros\" ou \"altura\" se não for parede inteira)")


if __name__ == "__main__":
    main()
