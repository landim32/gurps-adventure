#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monta a pagina final: a arte de cada quadro na sua caixa, moldura, calha e os baloes
por cima.

    python montar_pagina.py --roteiro campanha/hq/vol-01-.../roteiro.json
    python montar_pagina.py --roteiro ... --pagina 4 --sem-baloes
    python montar_pagina.py --roteiro ... --pdf campanha/hq/vol-01-.../volume.pdf

Quadro sem arte ainda gera pagina: entra uma caixa vazia com o numero e o que o
roteiro diz que se ve ali. Da para montar o volume inteiro antes de gerar imagem e ir
substituindo — por isso o comando pode ser repetido a vontade, ele redesenha do zero.

O letreiramento e sempre aplicado *na pagina*, nunca no quadro solto: a fonte fica no
tamanho final, igual em todos os quadros, e o quadro em `quadros/` continua limpo para
ser regerado sem perder o texto.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout  # noqa: E402
from layout import baloes  # noqa: E402


def encaixar(arte, w, h):
    """Preenche a caixa sem deformar: escala pelo lado que falta e corta o excesso
    pelo centro (um pouco acima do centro, que e onde costuma estar a cabeca)."""
    escala = max(w / arte.width, h / arte.height)
    nova = arte.resize((max(1, int(arte.width * escala + 0.5)),
                        max(1, int(arte.height * escala + 0.5))), Image.LANCZOS)
    x = (nova.width - w) // 2
    y = int((nova.height - h) * 0.42)
    return nova.crop((x, y, x + w, y + h))


def vazio(img, caixa, quadro):
    """Quadro sem arte: hachura leve, numero e a descricao do roteiro."""
    x, y, w, h = caixa
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill="#EFEFEA")
    for i in range(-h, w, 46):
        d.line([x + i, y + h, x + i + h, y], fill="#E3E3DC", width=3)
    f = baloes.carregar_fonte("regular", 30)
    d.text((x + 20, y + 16), f"quadro {quadro.get('n', '?')} — arte pendente",
           font=f, fill="#9A9A90")
    texto = quadro.get("o_que_se_ve", "")
    if texto:
        linhas = baloes.quebrar(texto, f, w - 48, d)[:6]
        ty = y + 64
        for linha in linhas:
            d.text((x + 20, ty), linha, font=f, fill="#B3B3A8")
            ty += f.size * 1.3


def montar(roteiro, pagina, base, raiz, com_baloes=True):
    img = layout.nova_pagina(roteiro)
    faltando = 0
    for quadro, caixa in zip(pagina.get("quadros", []), layout.caixas(pagina, roteiro)):
        x, y, w, h = caixa
        arquivo = layout.resolver(quadro.get("arquivo", ""), base, raiz)
        if arquivo:
            arte = Image.open(arquivo).convert("RGBA")
            img.paste(encaixar(arte, w, h), (x, y))
        else:
            vazio(img, caixa, quadro)
            faltando += 1
        layout.moldura(img, caixa)
        if com_baloes:
            layout.desenhar_baloes(img, quadro, caixa, roteiro)
    layout.rodape(img, roteiro, pagina)
    return img, faltando


def main():
    ap = argparse.ArgumentParser(description="Monta as paginas finais da HQ.")
    ap.add_argument("--roteiro", required=True, help="roteiro.json do volume")
    ap.add_argument("--pagina", action="append", default=[],
                    help="So estas paginas (repetivel)")
    ap.add_argument("--saida", default="", help="Pasta (padrao: <volume>/paginas/)")
    ap.add_argument("--sem-baloes", action="store_true",
                    help="Monta a arte sem letreiramento")
    ap.add_argument("--pdf", default="",
                    help="Junta as paginas montadas num PDF nesse caminho")
    ap.add_argument("--raiz", default=".", help="Raiz do projeto")
    args = ap.parse_args()

    roteiro = layout.carregar(args.roteiro)
    base = layout.pasta_do_roteiro(args.roteiro)
    destino = Path(args.saida) if args.saida else base / "paginas"

    feitas, pendentes = [], 0
    for pagina in layout.paginas_pedidas(roteiro, args.pagina):
        img, faltando = montar(roteiro, pagina, base, args.raiz,
                               com_baloes=not args.sem_baloes)
        nome = f"pagina-{int(pagina.get('n', 0)):02d}"
        if args.sem_baloes:
            nome += "-sem-baloes"
        arq = layout.salvar(img, destino / f"{nome}.png")
        feitas.append(arq)
        pendentes += faltando
        print(f"  pág. {pagina.get('n')}: {len(pagina.get('quadros', []))} quadro(s)"
              + (f", {faltando} sem arte" if faltando else "") + f" -> {arq}")

    print(f"{len(feitas)} página(s) em {destino}"
          + (f" — {pendentes} quadro(s) ainda sem arte" if pendentes else ""))

    if args.pdf and feitas:
        # O gravador de PDF do Pillow chama o codificador JPEG direto pela tabela
        # Image.SAVE, que so e preenchida por init(); sem isto, KeyError: 'JPEG'.
        Image.init()
        paginas = [Image.open(p).convert("RGB") for p in sorted(feitas)]
        Path(args.pdf).parent.mkdir(parents=True, exist_ok=True)
        paginas[0].save(args.pdf, save_all=True, append_images=paginas[1:],
                        resolution=300.0)
        print(f"PDF com {len(paginas)} página(s): {args.pdf}")


if __name__ == "__main__":
    main()
