#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desenha baloes de HQ numa imagem — forma, contorno e letreiramento em Pillow, sem IA.

    python baloes.py --imagem quadros/p01q3.png --saida paginas/p01q3-letrado.png \
        --balao 'fala em 30,16 apontando para 44,55 de "Hoel": Senta aí, então.' \
        --balao 'grito em 72,22 apontando para 62,58: NÃO FOI TUA CULPA!'

A frase e a mesma que se escreve no roteiro:

    <tipo> em <X>,<Y> [apontando para <X>,<Y>] [largura N] [corpo N] [de "Quem"]: <texto>

X e Y sao *porcentagens do quadro* (0-100), nao pixels — o mesmo balao funciona no
quadro solto de 1536 px e na pagina montada de 2480 px. Por isso `montar_pagina.py`
importa este arquivo em vez de chamar o comando: ele passa a caixa do quadro dentro da
pagina e as mesmas coordenadas do roteiro caem no lugar certo.

O contorno nunca e desenhado forma a forma: as formas entram todas numa mascara, a
mascara e dilatada (MaxFilter) e o resultado e a silhueta *da uniao*. E o que faz o
rabicho colar no balao sem deixar a linha da elipse atravessada no meio dele, e o que
permite nuvem de pensamento e balao de grito com o mesmo codigo.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Fontes de letreiramento, em ordem de preferencia. Comic Sans e feia de texto corrido
# e certa aqui: foi desenhada a partir de letreiramento de HQ.
FONTES = {
    "regular": [r"C:\Windows\Fonts\comic.ttf", r"C:\Windows\Fonts\segoepr.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "negrito": [r"C:\Windows\Fonts\comicbd.ttf", r"C:\Windows\Fonts\segoeprb.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "italico": [r"C:\Windows\Fonts\comici.ttf", r"C:\Windows\Fonts\segoesc.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"],
    "pesada":  [r"C:\Windows\Fonts\comicz.ttf", r"C:\Windows\Fonts\comicbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
}

# corpo 34 = altura da fonte num quadro de 1000 px de largura; escala com o quadro.
CORPO_REF = 1000.0

ESTILOS = {
    "fala": dict(forma="elipse", fonte="negrito", rabicho="triangulo",
                 fundo="#FFFFFF", traco="#111111", tinta="#111111", corpo=1.0,
                 caixa_alta=True),
    "grito": dict(forma="estrela", fonte="pesada", rabicho="triangulo",
                  fundo="#FFFFFF", traco="#111111", tinta="#111111", corpo=1.18,
                  caixa_alta=True),
    "sussurro": dict(forma="elipse", fonte="italico", rabicho="triangulo",
                     fundo="#FFFFFF", traco="#111111", tinta="#333333", corpo=0.88,
                     caixa_alta=False, tracejado=True),
    "pensamento": dict(forma="nuvem", fonte="italico", rabicho="bolhas",
                       fundo="#FFFFFF", traco="#111111", tinta="#111111", corpo=0.95,
                       caixa_alta=False),
    "narracao": dict(forma="caixa", fonte="regular", rabicho=None,
                     fundo="#F6E7C1", traco="#111111", tinta="#1A1206", corpo=0.95,
                     caixa_alta=False),
    "off": dict(forma="retangulo", fonte="negrito", rabicho="triangulo",
                fundo="#FFFFFF", traco="#111111", tinta="#111111", corpo=1.0,
                caixa_alta=True),
    "eletronico": dict(forma="zigue", fonte="negrito", rabicho="triangulo",
                       fundo="#EAF2FF", traco="#111111", tinta="#0B1B33", corpo=1.0,
                       caixa_alta=True),
    "canto": dict(forma="onda", fonte="italico", rabicho="triangulo",
                  fundo="#FFFFFF", traco="#111111", tinta="#111111", corpo=1.0,
                  caixa_alta=False, musical=True),
    "onomatopeia": dict(forma=None, fonte="pesada", rabicho=None,
                        fundo="#FFD53D", traco="#111111", tinta="#FFD53D", corpo=2.4,
                        caixa_alta=True),
}

APELIDOS = {
    "dialogo": "fala", "conversa": "fala", "falar": "fala",
    "berro": "grito", "grita": "grito", "gritar": "grito",
    "cochicho": "sussurro", "baixinho": "sussurro",
    "pensa": "pensamento", "pensar": "pensamento",
    "recordatorio": "narracao", "legenda": "narracao", "caixa": "narracao",
    "narrador": "narracao", "narração": "narracao",
    "fora": "off", "fora-de-quadro": "off", "voz-off": "off",
    "radio": "eletronico", "magico": "eletronico", "magia": "eletronico",
    "sobrenatural": "eletronico", "eletrônico": "eletronico",
    "cancao": "canto", "canção": "canto", "musica": "canto", "música": "canto",
    "som": "onomatopeia", "sfx": "onomatopeia", "onomatopéia": "onomatopeia",
}

RE_BALAO = re.compile(
    r"^\s*(?P<tipo>[\wÀ-ÿ-]+)"
    r"\s+em\s+(?P<x>-?\d+(?:[.,]\d+)?)\s*,\s*(?P<y>-?\d+(?:[.,]\d+)?)"
    r"(?:\s+apontando\s+(?:para\s+)?(?P<ax>-?\d+(?:[.,]\d+)?)\s*,\s*"
    r"(?P<ay>-?\d+(?:[.,]\d+)?))?"
    r"(?:\s+largura\s+(?P<largura>\d+(?:[.,]\d+)?))?"
    r"(?:\s+corpo\s+(?P<corpo>\d+(?:[.,]\d+)?))?"
    r"(?:\s+de\s+\"(?P<quem>[^\"]+)\")?"
    r"\s*:\s*(?P<texto>.+)$", re.S)


def num(v, padrao=None):
    if v is None or v == "":
        return padrao
    return float(str(v).replace(",", "."))


def carregar_fonte(estilo, tamanho):
    for caminho in FONTES.get(estilo, FONTES["regular"]):
        try:
            return ImageFont.truetype(caminho, int(tamanho))
        except Exception:
            continue
    return ImageFont.load_default()


def tem_glifo(fonte, ch):
    try:
        return fonte.getmask(ch).getbbox() is not None
    except Exception:
        return False


def ler_frase(frase):
    """'fala em 30,16 apontando para 44,55: texto' -> dicionario do balao."""
    m = RE_BALAO.match(frase)
    if not m:
        raise ValueError(
            f"nao entendi o balao: {frase!r}\n"
            "  formato: <tipo> em X,Y [apontando para X,Y] [largura N] [corpo N] "
            "[de \"Quem\"]: <texto>")
    g = m.groupdict()
    d = {"tipo": g["tipo"], "em": [num(g["x"]), num(g["y"])],
         "texto": g["texto"].strip()}
    if g["ax"] is not None:
        d["apontando"] = [num(g["ax"]), num(g["ay"])]
    for chave in ("largura", "corpo"):
        if g[chave] is not None:
            d[chave] = num(g[chave])
    if g["quem"]:
        d["quem"] = g["quem"]
    return d


def normalizar_tipo(tipo):
    t = (tipo or "fala").strip().lower()
    t = APELIDOS.get(t, t)
    if t not in ESTILOS:
        raise ValueError(f"tipo de balao desconhecido: {tipo!r}. "
                         f"Conhecidos: {', '.join(sorted(ESTILOS))}")
    return t


def quebrar(texto, fonte, largura_px, desenho):
    linhas = []
    for paragrafo in texto.replace("\\n", "\n").split("\n"):
        palavras = paragrafo.split()
        if not palavras:
            linhas.append("")
            continue
        atual = palavras[0]
        for p in palavras[1:]:
            teste = f"{atual} {p}"
            if desenho.textlength(teste, font=fonte) <= largura_px:
                atual = teste
            else:
                linhas.append(atual)
                atual = p
        linhas.append(atual)
    return linhas


def pontos_elipse(cx, cy, rx, ry, n=96, mod=None):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1.0 if mod is None else mod(a, i)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return pts


def pontos_estrela(cx, cy, rx, ry, pontas=18):
    """Balao de grito: raio alternado com variacao fixa (nao sorteada) para nao
    parecer engrenagem."""
    pts = []
    n = pontas * 2
    for i in range(n):
        a = 2 * math.pi * i / n
        if i % 2:
            r = 1.30 + 0.06 * math.sin(i * 2.7)
        else:
            r = 0.92 + 0.04 * math.sin(i * 1.7)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return pts


def pontos_zigue(x0, y0, x1, y1, passo, amp):
    """Retangulo de contorno em zigue-zague — voz de radio, de morto-vivo, de magia."""
    pts = []

    def lado(ax, ay, bx, by):
        comp = math.hypot(bx - ax, by - ay)
        n = max(4, int(comp / max(passo, 1.0)) // 2 * 2)
        ux, uy = (bx - ax) / comp, (by - ay) / comp
        nx, ny = -uy, ux
        for i in range(n):
            t = i / n
            s = amp if i % 2 else 0.0
            pts.append((ax + (bx - ax) * t + nx * s, ay + (by - ay) * t + ny * s))

    lado(x0, y0, x1, y0)
    lado(x1, y0, x1, y1)
    lado(x1, y1, x0, y1)
    lado(x0, y1, x0, y0)
    return pts


def picotar(dc, p, q, cor, esp, partes=7):
    """Linha tracejada de p a q — o rabicho do sussurro, que e todo picotado."""
    for i in range(0, partes, 2):
        a = (p[0] + (q[0] - p[0]) * i / partes, p[1] + (q[1] - p[1]) * i / partes)
        b = (p[0] + (q[0] - p[0]) * (i + 1) / partes,
             p[1] + (q[1] - p[1]) * (i + 1) / partes)
        dc.line([a, b], fill=cor, width=esp)


def borda_no_rumo(cx, cy, rx, ry, alvo, desvio):
    """Dois pontos da elipse, um de cada lado do rumo do alvo: a base do rabicho."""
    ang = math.atan2(alvo[1] - cy, alvo[0] - cx)
    saida = []
    for s in (-desvio, desvio):
        a = ang + s
        saida.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return saida, ang


def desenhar(imagem, balao, caixa=None, escala_corpo=1.0, ref_px=None, prender=True):
    """Desenha um balao sobre `imagem` (RGBA). `caixa` = (x, y, w, h) em pixels: o
    quadro a que as porcentagens do balao se referem. Devolve o bbox usado.

    `ref_px` e a largura que vale por CORPO_REF no calculo do corpo da letra. Sem ela
    vale a largura do quadro — o que so serve para o quadro solto: numa pagina, quem
    monta passa a mesma referencia para todos, senao o quadro estreito sai com letra
    menor que o largo e a pagina parece letreirada por duas pessoas.

    `prender` mantem o balao dentro do quadro, empurrando o centro para dentro quando
    o texto cresceu mais do que o roteiro previu. O rabicho continua apontando para
    onde apontava."""
    if caixa is None:
        caixa = (0, 0, imagem.width, imagem.height)
    cx0, cy0, cw, ch = caixa

    tipo = normalizar_tipo(balao.get("tipo"))
    est = dict(ESTILOS[tipo])
    for chave in ("fundo", "traco", "tinta", "fonte", "rabicho"):
        if balao.get(chave):
            est[chave] = balao[chave]

    texto = str(balao.get("texto", "")).strip()
    if est.get("caixa_alta") and not balao.get("sem_caixa_alta"):
        texto = texto.upper()
    if est.get("musical") and not texto.startswith("\u266a"):
        if tem_glifo(carregar_fonte(est["fonte"], 40), "\u266a"):
            texto = f"\u266a {texto} \u266a"

    corpo = num(balao.get("corpo"), None)
    ref = float(ref_px) if ref_px else float(cw)
    base = (corpo if corpo else 34.0 * est["corpo"]) * (ref / CORPO_REF) * escala_corpo
    fonte = carregar_fonte(est["fonte"], max(9, base))
    esp = max(2, int(round(base * 0.085)))          # espessura do contorno
    pad = max(6, int(round(base * 0.55)))           # respiro entre texto e borda

    largura_texto = cw * num(balao.get("largura"), 30.0) / 100.0
    d0 = ImageDraw.Draw(imagem)
    linhas = quebrar(texto, fonte, largura_texto, d0)
    alt_linha = base * 1.22
    larg = max([d0.textlength(l, font=fonte) for l in linhas] + [1.0])
    alt = alt_linha * len(linhas)

    cx = cx0 + cw * num(balao["em"][0]) / 100.0
    cy = cy0 + ch * num(balao["em"][1]) / 100.0
    alvo = None
    if balao.get("apontando"):
        alvo = (cx0 + cw * num(balao["apontando"][0]) / 100.0,
                cy0 + ch * num(balao["apontando"][1]) / 100.0)

    if est["forma"] in (None, "caixa", "retangulo", "zigue"):
        meia_l, meia_a = larg / 2 + pad, alt / 2 + pad
    else:
        meia_l = larg / 2 * 1.28 + pad
        meia_a = alt / 2 * 1.45 + pad
    if est["forma"] == "estrela":
        meia_l, meia_a = meia_l * 0.86, meia_a * 0.86

    if prender:
        # O grito tem pontas e a nuvem tem bolhas para fora do eixo: o que se prende
        # dentro do quadro e a forma desenhada, nao a elipse de base.
        sobra = {"estrela": 1.32, "nuvem": 1.12, "onda": 1.08}.get(est["forma"], 1.0)
        mx, my = meia_l * sobra + esp * 2, meia_a * sobra + esp * 2
        if 2 * mx < cw:
            cx = min(max(cx, cx0 + mx), cx0 + cw - mx)
        if 2 * my < ch:
            cy = min(max(cy, cy0 + my), cy0 + ch - my)

    # A camada e recortada com folga: cabe o contorno dilatado, as pontas do grito,
    # os bumps da nuvem e o rabicho inteiro.
    folga = meia_l * 0.55 + esp * 4 + base
    x0 = min(cx - meia_l - folga, alvo[0] - base if alvo else cx)
    x1 = max(cx + meia_l + folga, alvo[0] + base if alvo else cx)
    y0 = min(cy - meia_a - folga, alvo[1] - base if alvo else cy)
    y1 = max(cy + meia_a + folga, alvo[1] + base if alvo else cy)
    ox, oy = int(math.floor(x0)), int(math.floor(y0))
    lw, lh = int(math.ceil(x1 - x0)) + 1, int(math.ceil(y1 - y0)) + 1
    lcx, lcy = cx - ox, cy - oy
    lalvo = (alvo[0] - ox, alvo[1] - oy) if alvo else None

    mascara = Image.new("L", (lw, lh), 0)
    dm = ImageDraw.Draw(mascara)

    if est["forma"] == "elipse":
        dm.polygon(pontos_elipse(lcx, lcy, meia_l, meia_a), fill=255)
    elif est["forma"] == "onda":
        dm.polygon(pontos_elipse(lcx, lcy, meia_l, meia_a,
                                 mod=lambda a, i: 1 + 0.07 * math.sin(7 * a)), fill=255)
    elif est["forma"] == "estrela":
        dm.polygon(pontos_estrela(lcx, lcy, meia_l, meia_a), fill=255)
    elif est["forma"] == "nuvem":
        # O bump sai do *menor* eixo: com a media, um balao largo e baixo ganhava
        # bolhas do tamanho dele e virava osso.
        rb = max(4.0, min(meia_l, meia_a) * 0.30)
        n = max(12, int(1.7 * (meia_l + meia_a) / rb))
        for px, py in pontos_elipse(lcx, lcy, meia_l - rb * 0.55, meia_a - rb * 0.55,
                                    n=n):
            dm.ellipse([px - rb, py - rb, px + rb, py + rb], fill=255)
        dm.ellipse([lcx - meia_l + rb, lcy - meia_a + rb,
                    lcx + meia_l - rb, lcy + meia_a - rb], fill=255)
    elif est["forma"] == "caixa":
        dm.rectangle([lcx - meia_l, lcy - meia_a, lcx + meia_l, lcy + meia_a], fill=255)
    elif est["forma"] == "retangulo":
        dm.rounded_rectangle([lcx - meia_l, lcy - meia_a, lcx + meia_l, lcy + meia_a],
                             radius=base * 0.45, fill=255)
    elif est["forma"] == "zigue":
        dm.polygon(pontos_zigue(lcx - meia_l, lcy - meia_a, lcx + meia_l, lcy + meia_a,
                                passo=base * 0.55, amp=base * 0.22), fill=255)

    # Rabicho
    if lalvo and est["rabicho"] == "triangulo" and est["forma"]:
        encolhe = 0.95 if est["forma"] != "estrela" else 0.80
        (b1, b2), _ = borda_no_rumo(lcx, lcy, meia_l * encolhe, meia_a * encolhe,
                                    lalvo, 0.30)
        dm.polygon([b1, b2, lalvo], fill=255)
    elif lalvo and est["rabicho"] == "bolhas":
        for i, t in enumerate((0.42, 0.68, 0.88)):
            px = lcx + (lalvo[0] - lcx) * t
            py = lcy + (lalvo[1] - lcy) * t
            r = base * (0.42 - 0.11 * i)
            dm.ellipse([px - r, py - r, px + r, py + r], fill=255)

    dilatada = mascara.filter(ImageFilter.MaxFilter(esp * 2 + 1))

    camada = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    if est["forma"]:
        if est.get("tracejado"):
            # Sussurro: o corpo e solido, o contorno e picotado.
            camada.paste(est["fundo"], (0, 0), mascara)
            dc = ImageDraw.Draw(camada)
            pts = pontos_elipse(lcx, lcy, meia_l, meia_a, n=64)
            for i in range(0, len(pts), 2):
                dc.line([pts[i], pts[(i + 1) % len(pts)]], fill=est["traco"], width=esp)
            if lalvo:
                (b1, b2), _ = borda_no_rumo(lcx, lcy, meia_l, meia_a, lalvo, 0.22)
                for b in (b1, b2):
                    picotar(dc, b, lalvo, est["traco"], esp)
        else:
            camada.paste(est["traco"], (0, 0), dilatada)
            camada.paste(est["fundo"], (0, 0), mascara)

    dc = ImageDraw.Draw(camada)
    ty = lcy - alt / 2
    for linha in linhas:
        w = dc.textlength(linha, font=fonte)
        if est["forma"] is None:                      # onomatopeia: letra com contorno
            dc.text((lcx - w / 2, ty), linha, font=fonte, fill=est["fundo"],
                    stroke_width=max(2, esp), stroke_fill=est["traco"])
        else:
            dc.text((lcx - w / 2, ty), linha, font=fonte, fill=est["tinta"])
        ty += alt_linha

    # Balao que vaza pela borda da imagem: recorta o que sobra em vez de estourar.
    corte = camada.crop((max(0, -ox), max(0, -oy),
                         min(lw, imagem.width - ox), min(lh, imagem.height - oy)))
    if corte.width > 0 and corte.height > 0:
        imagem.alpha_composite(corte, (max(0, ox), max(0, oy)))
    return (ox, oy, ox + lw, oy + lh)


def desenhar_varios(imagem, baloes, caixa=None, escala_corpo=1.0, ref_px=None):
    for b in baloes:
        desenhar(imagem, b, caixa=caixa, escala_corpo=escala_corpo, ref_px=ref_px)
    return imagem


def main():
    ap = argparse.ArgumentParser(
        description="Desenha baloes de HQ numa imagem, sem IA.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Tipos: " + ", ".join(sorted(ESTILOS)) +
               "\nFrase: <tipo> em X,Y [apontando para X,Y] [largura N] [corpo N] "
               "[de \"Quem\"]: <texto>")
    ap.add_argument("--imagem", default="", help="Quadro de entrada")
    ap.add_argument("--saida", default="", help="Padrao: <imagem>-letrado.png")
    ap.add_argument("--balao", action="append", default=[],
                    help="Uma frase de balao (repetivel)")
    ap.add_argument("--json", default="",
                    help="Arquivo com uma lista de baloes (mesmo esquema do roteiro)")
    ap.add_argument("--escala-corpo", type=float, default=1.0,
                    help="Multiplica o corpo de todos os baloes (padrao 1.0)")
    ap.add_argument("--amostra", action="store_true",
                    help="Ignora a imagem e desenha um exemplo de cada tipo")
    args = ap.parse_args()

    if args.amostra:
        img = Image.new("RGBA", (1600, 1200), (226, 217, 200, 255))
        exemplos = [
            'fala em 20,10 apontando para 26,26: Senta aí, então, forasteiro.',
            'grito em 66,11 apontando para 58,27: Não foi tua culpa, grandão!',
            'sussurro em 20,36 apontando para 28,50: Não olha agora, mas ele voltou.',
            'pensamento em 66,36 apontando para 58,50: Se eu correr, morro cansado.',
            'narracao em 20,63 largura 24: Wallace, na noite em que os mortos '
            'levantaram-se.',
            'off em 66,62 apontando para 97,66: Para o castelo! Sem parar!',
            'eletronico em 20,88 apontando para 30,99: Vocês já estão mortos.',
            'canto em 52,88 apontando para 50,99: E o carneiro dançou na feira!',
            'onomatopeia em 85,90: CRAC!',
        ]
        for e in exemplos:
            desenhar(img, ler_frase(e))
        destino = Path(args.saida or "amostra-baloes.png")
        destino.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(destino, quality=95)
        print(f"Amostra dos {len(exemplos)} tipos: {destino}")
        return

    caminho = Path(args.imagem)
    if not args.imagem or not caminho.is_file():
        sys.exit(f"Imagem nao encontrada: {args.imagem or '(nenhuma)'}")
    img = Image.open(caminho).convert("RGBA")

    baloes = [ler_frase(f) for f in args.balao]
    if args.json:
        dados = json.loads(Path(args.json).read_text(encoding="utf-8"))
        baloes += dados if isinstance(dados, list) else dados.get("baloes", [])
    if not baloes:
        sys.exit("Nenhum balão: use --balao ou --json.")

    for b in baloes:
        desenhar(img, b, escala_corpo=args.escala_corpo)

    destino = Path(args.saida) if args.saida else \
        caminho.with_name(caminho.stem + "-letrado.png")
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(destino, quality=95)
    print(f"{len(baloes)} balão(ões) em {destino}")


if __name__ == "__main__":
    main()
