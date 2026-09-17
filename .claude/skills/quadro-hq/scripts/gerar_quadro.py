#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a arte dos quadros da HQ numa IA externa (OpenAI, gpt-image-1), com os avatares
do elenco como referencia — e **sem balao nenhum**: o letreiramento e da skill
`baloes-hq`, aplicado depois, na pagina.

    # quem aparece no volume e quem ainda nao tem modelo
    python gerar_quadro.py elenco --roteiro campanha/hq/vol-01-.../roteiro.json

    # fixar o modelo de um personagem (folha de 3 vistas, a partir do retrato)
    python gerar_quadro.py modelo --quem comam-obabaroy
    python gerar_quadro.py avatar --quem hoel-meia-orelha --npc \
        --descricao "taberneiro, 50 anos, corpulento, falta metade da orelha esquerda"

    # a arte de um quadro, ou de todos os que faltam
    python gerar_quadro.py quadro --roteiro ... --pagina 3 --quadro 2
    python gerar_quadro.py quadro --roteiro ... --faltando

Onde mora o quê:

    personagens/<slug>/foto.png          retrato do PJ (skill criar-personagem-gurps)
    personagens/<slug>/modelo-hq.png     folha de modelo do PJ, para a HQ
    campanha/npcs/<slug>/avatar.png      retrato do NPC
    campanha/npcs/<slug>/modelo-hq.png   folha de modelo do NPC
    campanha/npcs/<slug>/npc.md          quem ele e, de onde saiu a descricao fisica

A folha de modelo e o que segura a semelhanca entre um quadro e outro: o retrato
sozinho da o rosto, a folha da o corpo, a roupa e as armas de tres angulos. Sem ela o
mesmo personagem muda de cara de um quadro para o outro, que e o defeito que denuncia
HQ feita por IA.

Custo: cada chamada e paga. O script diz quantas vai fazer antes de fazer, e
`--so-prompt` escreve o prompt sem gastar nada.
"""
import argparse
import base64
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

API = "https://api.openai.com/v1/images"
TIPOS = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".webp": "image/webp"}
MODELO = "gpt-image-1"
# gpt-image-1 so aceita estes tres formatos; o quadro escolhe o mais parecido com a
# sua caixa na pagina.
TAMANHOS = {"paisagem": "1536x1024", "quadrado": "1024x1024", "retrato": "1024x1536"}
MAX_REFS = 6

ESTILO_PADRAO = ("Digital illustration, fantasy RPG comic book art, clean bold "
                 "linework, warm soft coloring, hand-drawn look")
# Vale para todo quadro: o balao entra depois, em Pillow, e o gerador escreve garatuja
# se deixarem.
SEM_TEXTO = ("no text, no lettering, no speech balloons, no captions, no signage, "
             "no watermark, no panel borders, no frame")


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")


def raiz_de(args):
    return Path(args.raiz).resolve()


def pasta_de(quem, raiz, npc=False):
    """A pasta do personagem: PJ em personagens/, NPC em campanha/npcs/."""
    s = slug(quem)
    if not npc:
        p = raiz / "personagens" / s
        if p.is_dir():
            return p, False
    return raiz / "campanha" / "npcs" / s, True


def ficha_do_pj(pasta):
    arq = pasta / "personagem.json"
    if not arq.is_file():
        return {}
    try:
        return json.loads(arq.read_text(encoding="utf-8"))
    except Exception:
        return {}


# O que se ve numa pessoa: arma, armadura, escudo. Rações e corda ficam de fora.
VISIVEL = ("arma", "armadura", "escudo", "vestuario", "vestuário")


def descricao_do_pj(dados):
    """So o que se ve: raca, idade, aparencia e o que ele veste ou carrega na mao."""
    partes = []
    if dados.get("raca"):
        partes.append(str(dados["raca"]))
    if dados.get("idade"):
        partes.append(f"{dados['idade']} anos")
    aparencia = dados.get("aparencia") or dados.get("aparência")
    if aparencia:
        partes.append(str(aparencia))

    itens = dados.get("armas_objetos") or dados.get("equipamento") or []
    nomes = []
    if isinstance(itens, list):
        for it in itens:
            if isinstance(it, dict):
                categoria = str(it.get("categoria", "")).lower()
                if categoria and not any(v in categoria for v in VISIVEL):
                    continue
                nomes.append(str(it.get("item") or it.get("nome") or "").strip())
            else:
                nomes.append(str(it))
    nomes = [n for n in nomes if n][:8]
    if nomes:
        partes.append("carrega: " + ", ".join(nomes))
    return ". ".join(p for p in partes if p)


def imagem_de_referencia(pasta):
    """A melhor referencia que existir, na ordem: folha de modelo, retrato, corpo.

    Cada nome e tentado em .png, .jpg e .jpeg: nem todo retrato da pasta de
    personagem foi salvo em png (o do Jah Kagadu, por exemplo, e jpg)."""
    for talo in ("modelo-hq", "avatar", "foto", "foto-corpo"):
        for ext in (".png", ".jpg", ".jpeg"):
            p = pasta / (talo + ext)
            if p.is_file():
                return p
    return None


# ----------------------------------------------------------------- a IA externa

def chave(args):
    k = os.environ.get(args.chave_env, "")
    if not k:
        sys.exit(f"Sem chave: a variável {args.chave_env} não está definida no "
                 "ambiente. Exporte-a antes de gerar.")
    return k


def pedir(args, prompt, referencias, tamanho):
    """Uma chamada a IA. Com referencia vai para /edits (que e o que mantem a cara do
    personagem); sem referencia, /generations."""
    try:
        import requests
    except ImportError:
        sys.exit("Falta a biblioteca `requests` (pip install requests).")

    cabecalho = {"Authorization": f"Bearer {chave(args)}"}
    dados = {"model": args.modelo, "prompt": prompt, "size": tamanho,
             "quality": args.qualidade, "n": 1}

    def enviar(extra):
        if referencias:
            arquivos = [("image[]", (p.name, open(p, "rb"), TIPOS.get(
                            p.suffix.lower(), "image/png")))
                        for p in referencias]
            try:
                return requests.post(f"{API}/edits", headers=cabecalho,
                                     data={**dados, **extra}, files=arquivos,
                                     timeout=args.timeout)
            finally:
                for _, (_, fh, _) in arquivos:
                    fh.close()
        return requests.post(f"{API}/generations", headers=cabecalho,
                             json={**dados, **extra}, timeout=args.timeout)

    extra = {}
    if referencias and args.fidelidade == "alta":
        extra["input_fidelity"] = "high"
    r = enviar(extra)
    if r.status_code == 400 and extra and "input_fidelity" in r.text:
        # Conta ou modelo sem o parametro: repete sem ele em vez de falhar.
        print("  (a API recusou input_fidelity; repetindo sem ele)")
        r = enviar({})
    if r.status_code >= 300:
        sys.exit(f"A IA recusou ({r.status_code}): {r.text[:500]}")
    corpo = r.json()
    try:
        return base64.b64decode(corpo["data"][0]["b64_json"])
    except Exception:
        sys.exit(f"Resposta inesperada da IA: {json.dumps(corpo)[:500]}")


def escrever_prompt(caminho, prompt, referencias):
    """O prompt fica sempre ao lado da imagem: e o que permite refazer o quadro meses
    depois, ou refaze-lo mudando uma frase so."""
    nota = caminho.with_name(caminho.stem + "-prompt.md")
    nota.parent.mkdir(parents=True, exist_ok=True)
    nota.write_text(
        f"# Prompt — {caminho.name}\n\n"
        f"**Escrito em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        + ("**Referências:** " + ", ".join(str(p) for p in referencias) + "\n\n"
           if referencias else "")
        + "```\n" + prompt + "\n```\n", encoding="utf-8")
    return nota


def gravar(caminho, binario, prompt, referencias):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(binario)
    return caminho, escrever_prompt(caminho, prompt, referencias)


# ----------------------------------------------------------------- comandos

def cmd_avatar(args):
    """Retrato de referencia de um NPC (ou de um PJ sem foto)."""
    raiz = raiz_de(args)
    pasta, e_npc = pasta_de(args.quem, raiz, npc=args.npc)
    pasta.mkdir(parents=True, exist_ok=True)

    descricao = args.descricao
    if not descricao:
        ficha = pasta / "npc.md"
        if ficha.is_file():
            descricao = ficha.read_text(encoding="utf-8")[:1200]
        else:
            dados = ficha_do_pj(pasta)
            descricao = descricao_do_pj(dados)
    if not descricao:
        sys.exit(f"Sem descrição de {args.quem}: passe --descricao ou escreva "
                 f"{pasta / 'npc.md'}.")

    prompt = (f"{args.estilo}. Character portrait reference sheet of a single "
              f"character for a comic book: {descricao}. Waist-up, neutral standing "
              f"pose, facing the viewer, neutral plain background, even lighting, "
              f"full clothing and visible gear. {SEM_TEXTO}.")
    destino = pasta / "avatar.png"
    if destino.is_file() and not args.forcar:
        print(f"Já existe: {destino} (use --forcar para refazer)")
        return
    if args.so_prompt:
        print(f"Prompt escrito (nada gerado): "
              f"{escrever_prompt(destino, prompt, [])}")
        return
    print(f"1 chamada à IA — avatar de {args.quem}")
    img = pedir(args, prompt, [], TAMANHOS["retrato"])
    arq, nota = gravar(destino, img, prompt, [])
    print(f"Avatar: {arq}\nPrompt: {nota}")


def cmd_modelo(args):
    """Folha de modelo: tres vistas do mesmo personagem, a partir do retrato."""
    raiz = raiz_de(args)
    pasta, e_npc = pasta_de(args.quem, raiz, npc=args.npc)
    if not pasta.is_dir():
        sys.exit(f"Não achei a pasta de {args.quem} ({pasta}). Para NPC, rode antes: "
                 f"gerar_quadro.py avatar --quem {slug(args.quem)} --npc "
                 f"--descricao \"...\"")
    referencia = imagem_de_referencia(pasta)
    descricao = args.descricao or (
        (pasta / "npc.md").read_text(encoding="utf-8")[:1200]
        if (pasta / "npc.md").is_file() else descricao_do_pj(ficha_do_pj(pasta)))

    prompt = (f"{args.estilo}. Character model sheet of the SAME single character "
              f"shown in the reference image, redrawn in this comic style: three "
              f"full-body views side by side on one plain neutral background — front "
              f"view, three-quarter view, back view — same face, same hair, same "
              f"clothing, same armor and weapons in all three. "
              + (f"The character: {descricao}. " if descricao else "")
              + f"Even flat lighting, standing neutral pose, full body from head to "
                f"feet. {SEM_TEXTO}.")
    destino = pasta / "modelo-hq.png"
    if destino.is_file() and not args.forcar:
        print(f"Já existe: {destino} (use --forcar para refazer)")
        return
    if args.so_prompt:
        refs = [referencia] if referencia else []
        print(f"Prompt escrito (nada gerado): "
              f"{escrever_prompt(destino, prompt, refs)}")
        return
    if not referencia:
        print(f"  (sem retrato em {pasta}: o modelo será inventado do zero)")
    print(f"1 chamada à IA — modelo de {args.quem}")
    img = pedir(args, prompt, [referencia] if referencia else [], TAMANHOS["paisagem"])
    arq, nota = gravar(destino, img, prompt, [referencia] if referencia else [])
    print(f"Modelo: {arq}\nPrompt: {nota}")


def achar_elenco(roteiro):
    """Quem aparece no volume, com os quadros em que aparece."""
    elenco = {}
    for pagina in roteiro.get("paginas", []):
        for quadro in pagina.get("quadros", []):
            for nome in quadro.get("elenco", []):
                elenco.setdefault(slug(nome), []).append(
                    f"p{pagina.get('n')}q{quadro.get('n')}")
    return elenco


def cmd_elenco(args):
    raiz = raiz_de(args)
    roteiro = json.loads(Path(args.roteiro).read_text(encoding="utf-8"))
    elenco = achar_elenco(roteiro)
    if not elenco:
        print("Nenhum quadro declara `elenco` — nada a conferir.")
        return
    faltam = []
    print(f"{len(elenco)} no elenco do volume:\n")
    for s, onde in sorted(elenco.items()):
        pasta, e_npc = pasta_de(s, raiz)
        modelo = pasta / "modelo-hq.png"
        ref = imagem_de_referencia(pasta)
        if modelo.is_file():
            estado = "modelo fixado"
        elif ref:
            estado = f"só retrato ({ref.name}) — falta a folha de modelo"
            faltam.append((s, e_npc, "modelo"))
        else:
            estado = "SEM NADA — falta avatar e modelo"
            faltam.append((s, e_npc, "avatar"))
        tipo = "NPC" if e_npc else "PJ "
        print(f"  {tipo} {s:<24} {estado}   [{', '.join(onde[:6])}"
              f"{'…' if len(onde) > 6 else ''}]")
    if faltam:
        print("\nPara fixar o que falta:")
        for s, e_npc, o_que in faltam:
            npc = " --npc" if e_npc else ""
            if o_que == "avatar":
                print(f"  gerar_quadro.py avatar --quem {s}{npc} --descricao \"...\"")
            print(f"  gerar_quadro.py modelo --quem {s}{npc}")
        sys.exit(1)
    print("\nElenco inteiro com modelo fixado: dá para gerar os quadros.")


def forma_do_quadro(quadro, roteiro):
    """Paisagem, quadrado ou retrato, conforme a caixa do quadro na pagina."""
    caixa = quadro.get("caixa")
    if not caixa:
        return TAMANHOS["paisagem"]
    larg_pag, alt_pag = roteiro.get("pagina_px", [2480, 3508])
    prop = (caixa[2] / 100.0 * larg_pag) / max(1e-6, (caixa[3] / 100.0 * alt_pag))
    if prop >= 1.25:
        return TAMANHOS["paisagem"]
    if prop <= 0.85:
        return TAMANHOS["retrato"]
    return TAMANHOS["quadrado"]


def montar_prompt(quadro, roteiro, raiz, refs_nomeadas):
    estilo = roteiro.get("estilo", ESTILO_PADRAO)
    partes = [estilo + "."]
    if refs_nomeadas:
        partes.append("The reference images show the characters in this panel, in "
                      "order: " + "; ".join(
                          f"image {i + 1} is {nome}" for i, (nome, _)
                          in enumerate(refs_nomeadas))
                      + ". Keep every face, hairstyle, clothing, armor and weapon "
                        "exactly as in the reference.")
    lugar = quadro.get("lugar") or roteiro.get("lugar")
    if lugar:
        partes.append(f"Setting: {lugar}.")
    # `visual` e a mesma cena escrita em ingles, para o gerador; `o_que_se_ve` e o que
    # o roteiro mostra ao usuario. Havendo as duas, o prompt usa a inglesa.
    cena = quadro.get("visual") or quadro.get("o_que_se_ve")
    if cena:
        partes.append(cena)
    if quadro.get("enquadramento"):
        partes.append(f"Framing: {quadro['enquadramento']}.")
    if quadro.get("luz"):
        partes.append(f"Light: {quadro['luz']}.")
    partes.append("Single comic panel, one continuous illustration. " + SEM_TEXTO + ".")
    return " ".join(str(p).strip() for p in partes if p)


def referencias_do_quadro(quadro, roteiro, raiz, base):
    refs = []
    for nome in quadro.get("elenco", []):
        pasta, _ = pasta_de(nome, raiz)
        img = imagem_de_referencia(pasta)
        if img:
            refs.append((nome, img))
        else:
            print(f"  aviso: {nome} não tem avatar nem modelo — vai sair inventado")
    for chave_extra in ("cenario", "referencia"):
        valor = quadro.get(chave_extra) or roteiro.get(chave_extra)
        if valor:
            for cand in (base / valor, raiz / valor, Path(valor)):
                if cand.is_file():
                    refs.append((f"the setting ({cand.name})", cand))
                    break
    if len(refs) > MAX_REFS:
        print(f"  aviso: {len(refs)} referências; mando só as {MAX_REFS} primeiras")
        refs = refs[:MAX_REFS]
    return refs


def quadros_pedidos(roteiro, args):
    alvo = []
    paginas = {int(p) for p in args.pagina} if args.pagina else None
    quadros = {int(q) for q in args.quadro} if args.quadro else None
    for pagina in roteiro.get("paginas", []):
        if paginas and int(pagina.get("n", 0)) not in paginas:
            continue
        for quadro in pagina.get("quadros", []):
            if quadros and int(quadro.get("n", 0)) not in quadros:
                continue
            alvo.append((pagina, quadro))
    return alvo


def cmd_quadro(args):
    raiz = raiz_de(args)
    caminho = Path(args.roteiro)
    roteiro = json.loads(caminho.read_text(encoding="utf-8"))
    base = caminho.resolve().parent

    alvo = quadros_pedidos(roteiro, args)
    if args.faltando:
        alvo = [(p, q) for p, q in alvo
                if not (q.get("arquivo") and (base / q["arquivo"]).is_file())]
    if not alvo:
        print("Nenhum quadro a gerar.")
        return

    print(f"{len(alvo)} quadro(s)"
          + ("" if args.so_prompt else f" — {len(alvo)} chamada(s) paga(s) à IA"))
    for pagina, quadro in alvo:
        nome = f"p{int(pagina.get('n', 0)):02d}q{int(quadro.get('n', 0)):02d}"
        refs = referencias_do_quadro(quadro, roteiro, raiz, base)
        prompt = montar_prompt(quadro, roteiro, raiz, refs)
        destino = base / "quadros" / f"{nome}.png"
        print(f"\n{nome}: {len(refs)} referência(s), {forma_do_quadro(quadro, roteiro)}")
        if args.so_prompt:
            print(f"  prompt: {escrever_prompt(destino, prompt, [p for _, p in refs])}")
        else:
            img = pedir(args, prompt, [p for _, p in refs],
                        forma_do_quadro(quadro, roteiro))
            arq, nota = gravar(destino, img, prompt, [p for _, p in refs])
            print(f"  arte: {arq}")
        quadro["arquivo"] = f"quadros/{nome}.png"
        quadro["prompt"] = prompt

    if not args.sem_gravar_roteiro:
        caminho.write_text(json.dumps(roteiro, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
        print(f"\nRoteiro atualizado com os caminhos da arte: {caminho}")


def opcoes_gerais(p, herdado=False):
    """As mesmas opcoes valem antes e depois do subcomando — `--raiz . elenco` e
    `elenco --raiz .` funcionam os dois. Nos subparsers o padrao e SUPPRESS: sem
    isso, o subcomando reporia o padrao por cima do que foi dado antes dele."""
    d = argparse.SUPPRESS
    p.add_argument("--raiz", default=(d if herdado else "."), help="Raiz do projeto")
    p.add_argument("--modelo-ia", dest="modelo", default=(d if herdado else MODELO),
                   help=f"Modelo de imagem (padrão {MODELO})")
    p.add_argument("--qualidade", default=(d if herdado else "high"),
                   choices=["low", "medium", "high"])
    p.add_argument("--fidelidade", default=(d if herdado else "alta"),
                   choices=["alta", "padrao"],
                   help="alta preserva melhor o rosto da referência")
    p.add_argument("--estilo", default=(d if herdado else ESTILO_PADRAO),
                   help="Estilo visual do volume")
    p.add_argument("--chave-env", default=(d if herdado else "OPENAI_API_KEY"),
                   help="Variável de ambiente com a chave")
    p.add_argument("--timeout", type=int, default=(d if herdado else 300))
    p.add_argument("--so-prompt", action="store_true",
                   default=(d if herdado else False),
                   help="Escreve o prompt e não chama a IA (não gasta)")
    p.add_argument("--forcar", action="store_true", default=(d if herdado else False),
                   help="Refaz o que já existe")


def main():
    ap = argparse.ArgumentParser(
        description="Arte dos quadros da HQ numa IA externa, sem balões.")
    opcoes_gerais(ap)
    comum = argparse.ArgumentParser(add_help=False)
    opcoes_gerais(comum, herdado=True)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("avatar", parents=[comum], help="Retrato de referência de um NPC")
    s.add_argument("--quem", required=True)
    s.add_argument("--npc", action="store_true", help="Força a pasta campanha/npcs/")
    s.add_argument("--descricao", default="")
    s.set_defaults(func=cmd_avatar)

    s = sub.add_parser("modelo", parents=[comum], help="Folha de modelo (3 vistas) de um personagem")
    s.add_argument("--quem", required=True)
    s.add_argument("--npc", action="store_true")
    s.add_argument("--descricao", default="")
    s.set_defaults(func=cmd_modelo)

    s = sub.add_parser("elenco", parents=[comum], help="Confere quem tem modelo fixado")
    s.add_argument("--roteiro", required=True)
    s.set_defaults(func=cmd_elenco)

    s = sub.add_parser("quadro", parents=[comum], help="Gera a arte de um ou mais quadros")
    s.add_argument("--roteiro", required=True)
    s.add_argument("--pagina", action="append", default=[])
    s.add_argument("--quadro", action="append", default=[])
    s.add_argument("--faltando", action="store_true",
                   help="Só os quadros que ainda não têm arte")
    s.add_argument("--sem-gravar-roteiro", action="store_true")
    s.set_defaults(func=cmd_quadro)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
