#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validar — confere a máscara contra as regras do Roll6 e acha o que a câmera 3D não vê.

    validar.py --mascara taberna3-mascara.png --imagem cenarios/taberna3.png
    validar.py --mascara m.png --imagem i.png --colunas 19 --linhas 12
    validar.py --mascara m.png --imagem i.png --json

No Roll6 o tom de cada ponto é a ALTURA da parede (preto = inteira, branco = vazio, cinza =
mais baixa). Confere e imprime:
  - tamanho igual ao da imagem do cenário (a proporção pode diferir no máximo 1%, mas gere
    sempre com o tamanho exato);
  - PNG, sem transparência, e tamanho do arquivo (< 10 MB);
  - os tons usados, com a altura de cada um, o nível mais próximo da escala (niveis.py) e % da
    área; avisa de tons demais (antialiasing ou ruído) e de tons quase brancos (< 5% de altura:
    o Roll6 os lê como vazio);
  - % de área de parede;
  - regiões abertas desconectadas: sala fechada onde a câmera não chega (lista tamanho e
    posição de cada uma). Qualquer parede, mesmo baixa, bloqueia a câmera;
  - passagem mais estreita aproximada: avisa se é menor que 2/3 de hexágono (o hexágono vem
    de --colunas/--linhas; sem eles, supõe 80 px na escala de 1220 px de largura, ou seja 55 px);
  - paredes finas demais, que somem quando o Roll6 reduz a máscara a 512 células (ele usa a
    MEDIANA do tom de cada célula, e este script faz a mesma conta).
Sai com código 1 se houver ERRO (formato, tamanho, transparência); AVISO não muda o código.
"""
import argparse
import json
import math
import os
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from niveis import ALTURA_INTEIRA, ALTURA_MINIMA, METROS_PAREDE, altura_de, nivel_mais_proximo  # noqa: E402

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

MAX_CELULAS = 512        # o Roll6 reduz a máscara a, no máximo, isto no lado maior
PAREDE_MIN_1220 = 4      # px de parede, na escala de 1220 px de largura, abaixo do qual some
TOM_VAZIO = 255 - int(ALTURA_MINIMA * 255)  # tons >= este valor têm altura < 5%: vazio
MUITOS_TONS = 10         # mais tons distintos que isto, cada um com área relevante, é suspeito
AREA_RELEVANTE = 0.0005  # fração da imagem que um tom precisa ter para contar


def componentes(dados, larg, alt):
    """Componentes 4-conexos de células abertas (valor 255): [(área, (x0,y0,x1,y1))]."""
    visto = bytearray(larg * alt)
    out = []
    for ini in range(larg * alt):
        if dados[ini] != 255 or visto[ini]:
            continue
        fila = deque([ini])
        visto[ini] = 1
        area = 0
        x0 = y0 = 10 ** 9
        x1 = y1 = -1
        while fila:
            p = fila.popleft()
            area += 1
            y, x = divmod(p, larg)
            x0, x1, y0, y1 = min(x0, x), max(x1, x), min(y0, y), max(y1, y)
            for q, ok in ((p - larg, y > 0), (p + larg, y < alt - 1), (p - 1, x > 0), (p + 1, x < larg - 1)):
                if ok and dados[q] == 255 and not visto[q]:
                    visto[q] = 1
                    fila.append(q)
        out.append((area, (x0, y0, x1, y1)))
    return sorted(out, key=lambda c: -c[0])


def reduzir(dados, larg, alt):
    """A redução do Roll6: grade de no máximo MAX_CELULAS células no lado maior, cada célula com a
    MEDIANA do tom dos pixels que cobre (empate entre escuro e claro fica com o claro), e depois os
    encaixes de altura (< 5% vira vazio, >= 95% vira parede inteira). Devolve (cw, ch, bytearray)."""
    escala = min(1.0, MAX_CELULAS / max(larg, alt))
    cw = max(1, round(larg * escala))
    ch = max(1, round(alt * escala))
    coluna = [min(cw - 1, x * cw // larg) for x in range(larg)]
    celulas = bytearray(cw * ch)
    hist = [0] * (cw * 256)
    linha_atual = 0

    def fecha(linha):
        for c in range(cw):
            faixa = hist[c * 256:(c + 1) * 256]
            total = sum(faixa)
            acumulado = 0
            tom = 255
            for v in range(256):
                acumulado += faixa[v]
                if acumulado * 2 > total:
                    tom = v
                    break
            h = altura_de(tom)
            celulas[linha * cw + c] = 255 if h == 0 else 0 if h == 1 else tom
            for v in range(256):
                hist[c * 256 + v] = 0

    for y in range(alt):
        linha = min(ch - 1, y * ch // alt)
        if linha != linha_atual:
            fecha(linha_atual)
            linha_atual = linha
        base = y * larg
        for x in range(larg):
            hist[coluna[x] * 256 + dados[base + x]] += 1
    fecha(linha_atual)
    return cw, ch, celulas


def main():
    ap = argparse.ArgumentParser(description="Valida a Máscara 3D.")
    ap.add_argument("--mascara", required=True)
    ap.add_argument("--imagem", required=True, help="Imagem do cenário")
    ap.add_argument("--colunas", type=int)
    ap.add_argument("--linhas", type=int)
    ap.add_argument("--json", action="store_true", help="Resultado em JSON")
    a = ap.parse_args()

    erros, avisos, info = [], [], {}
    raw = Image.open(a.mascara)
    img = Image.open(a.imagem)
    info["formato"] = raw.format
    info["modo"] = raw.mode
    info["bytes"] = os.path.getsize(a.mascara)

    if raw.format != "PNG":
        erros.append(f"o arquivo é {raw.format}, o Roll6 pede PNG")
    if "A" in raw.getbands() or raw.mode == "P" and "transparency" in raw.info:
        erros.append("a máscara tem transparência: o Roll6 trata pixel transparente como vazio")
    if info["bytes"] >= 10 * 1024 * 1024:
        erros.append(f"{info['bytes'] / 1048576:.1f} MB: o limite é 10 MB")

    larg, alt = raw.size
    iw, ih = img.size
    info["tamanho_mascara"] = [larg, alt]
    info["tamanho_imagem"] = [iw, ih]
    if (larg, alt) != (iw, ih):
        prop = abs((larg / alt) / (iw / ih) - 1) * 100
        msg = f"máscara {larg}x{alt} contra imagem {iw}x{ih} (proporção difere {prop:.2f}%)"
        (erros if prop > 1 else avisos).append(msg + (": o Roll6 recusa" if prop > 1 else ": gere com o tamanho exato"))

    m = raw.convert("L")
    hist = m.histogram()
    total = larg * alt
    vazios = sum(hist[TOM_VAZIO:])
    info["pixels_vazios"] = vazios
    info["pct_parede"] = round((total - vazios) / total * 100, 2)

    # --- os tons usados e a altura que cada um dá ---
    niveis = []
    for tom in range(TOM_VAZIO):
        if hist[tom] / total >= AREA_RELEVANTE:
            h = altura_de(tom)
            nome, _ = nivel_mais_proximo(h)
            niveis.append({"tom": tom, "altura_pct": round(h * 100, 1), "metros": round(h * METROS_PAREDE, 2),
                           "nivel_proximo": nome, "pct_area": round(hist[tom] / total * 100, 2)})
    info["niveis"] = niveis
    invisiveis = sum(hist[TOM_VAZIO:255])
    info["pixels_quase_brancos"] = invisiveis
    if invisiveis / total >= AREA_RELEVANTE:
        avisos.append(f"{invisiveis} pixel(s) quase brancos (tom {TOM_VAZIO}-254, altura abaixo de "
                      f"{ALTURA_MINIMA * 100:.0f}%): o Roll6 os lê como vazio. Use 255, ou suba a altura")
    if len(niveis) > MUITOS_TONS:
        avisos.append(f"{len(niveis)} tons distintos com área relevante: costuma ser antialiasing ou ruído "
                      f"(mais de {MUITOS_TONS} alturas diferentes é raro numa cena). Desenhe as formas com um tom só")
    nenhuma_inteira = not any(n["altura_pct"] >= ALTURA_INTEIRA * 100 for n in niveis)

    # --- o que o Roll6 enxerga: máscara reduzida a no máximo 512 células ---
    cw, ch, celulas = reduzir(m.tobytes(), larg, alt)
    f = max(1, math.ceil(max(larg, alt) / MAX_CELULAS))
    # para a câmera qualquer parede (mesmo baixa) bloqueia: aberto = vazio (255)
    pequena = Image.frombytes("L", (cw, ch), bytes(celulas)).point(lambda p: 255 if p == 255 else 0)
    info["celulas"] = [cw, ch]
    info["px_por_celula"] = f

    if a.colunas and a.linhas:
        raio = larg / (1.5 * a.colunas + 0.5)
        hexw = 2 * raio
    else:
        hexw = 80 * larg / 1220
    minimo = 2 / 3 * hexw
    info["hexagono_px"] = round(hexw, 1)
    info["passagem_minima_px"] = round(minimo, 1)

    # regiões abertas desconectadas
    comp = [c for c in componentes(bytearray(pequena.tobytes()), cw, ch) if c[0] * f * f >= (minimo / 2) ** 2]
    info["regioes_abertas"] = len(comp)
    if len(comp) > 1:
        for area, (x0, y0, x1, y1) in comp[1:]:
            avisos.append(f"região aberta desconectada: ~{area * f * f} px² em x {x0 * f}-{(x1 + 1) * f}, "
                          f"y {y0 * f}-{(y1 + 1) * f} — sala fechada, a câmera não chega lá")

    # passagem mais estreita: quantas erosões (3x3) até uma região se partir em duas
    base = len(comp)
    estreita = None
    if base >= 1:
        sofre = pequena
        limite = int(math.ceil(minimo / f / 2)) + 1
        for r in range(1, limite + 1):
            sofre = sofre.filter(ImageFilter.MinFilter(3))
            n = len([c for c in componentes(bytearray(sofre.tobytes()), cw, ch)
                     if c[0] * f * f >= (minimo / 2) ** 2 / 4])
            if n > base:
                estreita = (2 * r - 1) * f
                break
        if estreita is None:
            info["passagem_estreita_px"] = f">= {round(minimo)}"
        else:
            info["passagem_estreita_px"] = estreita
            if estreita < minimo:
                avisos.append(f"há uma passagem de ~{estreita} px, menor que o mínimo de {minimo:.0f} px "
                              f"(2/3 de hexágono): a câmera não atravessa. Alargue a porta ou o corredor")

    # paredes finas que somem na redução (parede = qualquer pixel com altura >= 5%)
    parede_orig = m.point(lambda p: 255 if p < TOM_VAZIO else 0)
    parede_peq = Image.frombytes("L", (cw, ch), bytes(celulas)).point(lambda p: 255 if p < TOM_VAZIO else 0)
    parede_peq = parede_peq.resize((larg, alt), Image.NEAREST)
    perdidos = ImageChops.subtract(parede_orig, parede_peq).histogram()[255]
    paredes = total - vazios
    if paredes:
        info["pct_parede_perdida_na_reducao"] = round(perdidos / paredes * 100, 1)
        if perdidos / paredes > 0.10:
            avisos.append(f"{perdidos / paredes * 100:.0f}% da parede some na redução a {MAX_CELULAS} células "
                          f"(parede mais fina que ~{f} px, ou que {PAREDE_MIN_1220 * larg / 1220:.0f} px): engrosse")
    if paredes == 0:
        avisos.append("a máscara não tem parede nenhuma (tudo branco)")
    elif nenhuma_inteira:
        avisos.append("não há nenhuma parede de altura inteira (preto): confira se era isso mesmo — "
                      "só muretas e móveis, sem paredes")
    if hist[255] == 0 and vazios == 0:
        avisos.append("a máscara é toda parede: não há por onde andar")

    if a.json:
        print(json.dumps({"erros": erros, "avisos": avisos, "info": info}, ensure_ascii=False, indent=2))
    else:
        print(f"máscara : {a.mascara}")
        print(f"formato : {info['formato']} {info['modo']}, {info['bytes'] / 1024:.0f} KB")
        print(f"tamanho : máscara {larg}x{alt}, imagem {iw}x{ih}  "
              f"{'IGUAL' if (larg, alt) == (iw, ih) else 'DIFERENTE'}")
        print(f"parede  : {info['pct_parede']}% da área; {len(niveis)} tom(ns) de parede")
        for n in niveis:
            print(f"  tom {n['tom']:3}  altura {n['altura_pct']:5.1f}% (~{n['metros']:.2f} m, "
                  f"perto de \"{n['nivel_proximo']}\")  {n['pct_area']:5.2f}% da área")
        print(f"redução : {cw}x{ch} células ({f} px por célula, mediana por célula)")
        print(f"hexágono: ~{info['hexagono_px']} px de largura; passagem mínima {info['passagem_minima_px']} px")
        print(f"regiões abertas: {info['regioes_abertas']}; passagem mais estreita: "
              f"{info.get('passagem_estreita_px', '-')}")
        for e in erros:
            print("ERRO  :", e)
        for w in avisos:
            print("AVISO :", w)
        if not erros and not avisos:
            print("OK: nada a corrigir.")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
