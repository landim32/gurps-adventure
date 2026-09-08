#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anda com a estrutura da campanha ativa: cria, registra o que aconteceu, reindexa e
arquiva no fim.

    campanha.py estado
    campanha.py criar --nome "A Sombra sobre Mégalos" --mestre Rodrigo
    campanha.py capitulo --titulo "A caravana parte"
    campanha.py evento --titulo "Confusão na taberna" --resumo "..."
    campanha.py acontecimento --evento 1 --texto "Comam derruba a mesa"
    campanha.py imagem-inicial --arquivo cena.png
    campanha.py indexar
    campanha.py encerrar

O que e trabalho de escrever (o plano, a prosa de cada cena) nao esta aqui: o script
cuida do que da errado quando se faz a mao — numeracao, data, o indice que desatualiza
e a regra de uma campanha ativa por vez.
"""
import argparse
import json
import os
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

CAMPANHA = Path("campanha")
ARQUIVO = Path("historico/campanhas")

MARCA = "<!-- indice:{0} -->"
FIM = "<!-- /indice:{0} -->"


def hoje():
    return datetime.now().strftime("%d/%m/%Y")


def agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")


def raiz(args):
    return Path(args.raiz).resolve()


def pasta_campanha(r):
    return r / CAMPANHA


def exige_campanha(r):
    p = pasta_campanha(r)
    if not (p / "README.md").is_file():
        raise SystemExit(
            "Nao ha campanha ativa (falta campanha/README.md).\n"
            "Crie com: campanha.py criar --nome \"...\"")
    return p


def ler_meta(p):
    """Le o cabecalho de campos '**Campo:** valor' do README."""
    texto = (p / "README.md").read_text(encoding="utf-8")
    meta = dict(re.findall(r"^\*\*(.+?):\*\*\s*(.+?)\s*$", texto, re.M))
    return meta, texto


def _por_numero(base, numero):
    if numero in (None, "", "—"):
        return None
    try:
        n = int(str(numero).strip())
    except ValueError:
        return None
    for d in sorted(base.glob("*")):
        if d.is_dir() and d.name.startswith(f"{n:02d}-"):
            return d
    return None


def pasta_do_capitulo(p, numero):
    """plano/NN-... — o que foi PLANEJADO para o capitulo. Escrito uma vez, na criacao."""
    return _por_numero(p / "plano", numero)


def pasta_de_jogo(p, numero):
    """campanha/NN-... — o que ESTA ACONTECENDO no capitulo. Mexida enquanto ele e o atual.

    Mesmo nome da pasta do plano, um nivel acima: plano/03-fechem-os-portoes é o que se
    imaginou; 03-fechem-os-portoes é o que a mesa fez com isso.
    """
    return _por_numero(p, numero)


def meta_do_capitulo(pasta):
    """Le os campos '**Campo:** valor' do cabecalho de um capitulo do plano."""
    rd = pasta / "README.md" if pasta else None
    if not rd or not rd.is_file():
        return {}
    texto = rd.read_text(encoding="utf-8")
    # so o cabecalho, antes da primeira secao — o corpo tem '**Negrito:**' a rodo
    cabeca = texto.split("\n## ", 1)[0]
    return {k: v for k, v in re.findall(r"^\*\*(.+?):\*\*\s*(.+?)\s*$", cabeca, re.M)
            if v not in ("—", "-")}


def definir_campo(pasta, campo, valor):
    """Grava '**Campo:** valor' no cabecalho do capitulo, criando a linha se faltar."""
    rd = pasta / "README.md"
    texto = rd.read_text(encoding="utf-8")
    linha = f"**{campo}:** {valor}"
    if re.search(rf"^\*\*{re.escape(campo)}:\*\*.*$", texto, re.M):
        texto = re.sub(rf"^\*\*{re.escape(campo)}:\*\*.*$", linha, texto, count=1,
                       flags=re.M)
    else:
        # entra no fim do bloco de metadados do topo, nao antes dele
        linhas = texto.split("\n")
        i = 1
        while i < len(linhas) and not linhas[i].strip():
            i += 1
        while i < len(linhas) and linhas[i].startswith("**"):
            i += 1
        linhas.insert(i, linha)
        texto = "\n".join(linhas)

    # o bloco de metadados precisa de uma linha em branco antes do corpo
    texto = re.sub(r"(^\*\*[^\n]+\*\*[^\n]*\n)(?=[^\n*#])", r"\1\n", texto,
                   count=0, flags=re.M)
    rd.write_text(texto, encoding="utf-8")


def abrir_capitulo(p, pasta_plano):
    """Cria campanha/NN-... espelhando o nome do capitulo do plano, se ainda nao existe."""
    destino = p / pasta_plano.name
    if (destino / "README.md").is_file():
        return destino, False
    destino.mkdir(parents=True, exist_ok=True)   # pasta pode existir sem README
    rd = pasta_plano / "README.md"
    titulo = (rd.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
              if rd.is_file() else pasta_plano.name)
    (destino / "README.md").write_text(f"""# {titulo} — como aconteceu

**Aberto em:** {hoje()}
**Planejado em:** [`plano/{pasta_plano.name}/`](plano/{pasta_plano.name}/)

_(o que esta cena virou na mesa: quem estava, o que decidiram, onde acabou. O plano fica
onde está; aqui vai o que de fato houve, mesmo quando os dois não se parecem.)_

## Narração

_(o que foi lido aos jogadores, na ordem em que foi lido — a skill `narrar` grava aqui)_

## Acontecimentos

{MARCA.format("acontecimentos")}
_(nada registrado ainda)_
{FIM.format("acontecimentos")}
""", encoding="utf-8")
    return destino, True


def proximo_numero(pasta, padrao="*"):
    ns = [int(m.group(1)) for d in pasta.glob(padrao)
          if (m := re.match(r"^(\d+)-", d.name))]
    return max(ns, default=0) + 1


def bloco(texto, nome, conteudo):
    """Substitui o miolo entre os marcadores; acrescenta no fim se nao existirem."""
    ini, fim = MARCA.format(nome), FIM.format(nome)
    novo = f"{ini}\n{conteudo}\n{fim}"
    if ini in texto and fim in texto:
        return re.sub(re.escape(ini) + r".*?" + re.escape(fim), novo, texto, flags=re.S)
    return texto.rstrip() + "\n\n" + novo + "\n"


# ---------------------------------------------------------------- comandos


def cmd_estado(args):
    r = raiz(args)
    p = pasta_campanha(r)
    ativa = (p / "README.md").is_file()
    dados = {"ativa": ativa}
    if ativa:
        meta, _ = ler_meta(p)
        caps = sorted(x.name for x in (p / "plano").glob("*") if x.is_dir())
        evs = sorted(x.name for x in p.glob("*")
                     if x.is_dir() and x.name != "plano")
        atual = meta.get("Capítulo atual", "").strip()
        plano_cap = pasta_do_capitulo(p, atual)
        jogo_cap = pasta_de_jogo(p, atual)
        dados.update({"nome": meta.get("Campanha", "?"),
                      "estado": meta.get("Estado", "?"),
                      "mestre": meta.get("Mestre", "?"),
                      "inicio": meta.get("Início", "?"),
                      "capitulo_atual": atual or None,
                      # o que foi planejado
                      "capitulo_atual_plano":
                          plano_cap.as_posix() if plano_cap else None,
                      # cenario que o plano declara para esta cena
                      "capitulo_atual_mapa":
                          (meta_do_capitulo(plano_cap).get("Mapa") or "").strip("`")
                          or None,
                      # onde as outras skills gravam o que esta acontecendo
                      "capitulo_atual_pasta":
                          jogo_cap.as_posix() if jogo_cap else None,
                      # onde mora o que ja mudou no mundo
                      "mundo": (p / "mundo.md").as_posix()
                          if (p / "mundo.md").is_file() else None,
                      "capitulo_atual_estado": {
                          tipo: (jogo_cap / nome).as_posix()
                          for tipo, (nome, *_) in ANOTACOES.items()
                          if jogo_cap and (jogo_cap / nome).is_file()} or None,
                      "bolsa": (p / BOLSA).as_posix()
                          if (p / BOLSA).is_file() else None,
                      "saude": (p / SAUDE).as_posix()
                          if (p / SAUDE).is_file() else None,
                      "capitulos": caps, "em_jogo": evs})
    arquivadas = sorted(x.name for x in (r / ARQUIVO).glob("*") if x.is_dir()) \
        if (r / ARQUIVO).is_dir() else []
    dados["arquivadas"] = arquivadas

    if args.json:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        return
    if not ativa:
        print("Nenhuma campanha ativa.")
    else:
        print(f"Campanha  : {dados['nome']} ({dados['estado']})")
        print(f"Mestre    : {dados['mestre']}   Início: {dados['inicio']}")
        print(f"Capítulos : {len(dados['capitulos'])}"
              + (f"   Atual: {dados['capitulo_atual']} "
                 f"({dados['capitulo_atual_pasta'] or 'pasta não encontrada'})"
                 if dados["capitulo_atual"] else "   Atual: nenhum"))
        print(f"Em jogo   : {len(dados['em_jogo'])} capítulo(s) com registro")
    if arquivadas:
        print(f"Arquivadas: {', '.join(arquivadas)}")


def cmd_criar(args):
    r = raiz(args)
    p = pasta_campanha(r)
    if (p / "README.md").is_file():
        meta, _ = ler_meta(p)
        raise SystemExit(
            f"Ja existe uma campanha ativa: \"{meta.get('Campanha','?')}\".\n"
            "So pode haver uma por vez. Encerre a atual com: campanha.py encerrar")

    (p / "plano").mkdir(parents=True, exist_ok=True)

    corpo = f"""# {args.nome}

**Campanha:** {args.nome}
**Estado:** ativa
**Mestre:** {args.mestre}
**Início:** {hoje()}
**Cenário:** {args.cenario}
**Capítulo atual:** —
**Pontos dos personagens:** {args.pontos}

{args.premissa or "_(premissa a escrever: dois parágrafos que qualquer personagem saberia, no espírito da Descrição do Cenário de Caravana para Ein Arris)_"}

## Personagens

_(a preencher: nome, jogador e link para `personagens/<slug>/personagem.md`)_

## Plano

{MARCA.format("plano")}
_(nenhum capítulo ainda)_
{FIM.format("plano")}

## Histórico

{MARCA.format("historico")}
_(nada aconteceu ainda)_
{FIM.format("historico")}
"""
    (p / "README.md").write_text(corpo, encoding="utf-8")

    (p / "plano" / "README.md").write_text(
        f"""# Plano — {args.nome}

Estrutura no padrão de *Caravana para Ein Arris* (`livros/gurps-mb-3ed/23-caravana-para-ein-arris.md`):
uma **Descrição do Cenário** que pode ser lida aos jogadores, e depois capítulos
numerados como cenas encadeadas, com os testes e as consequências de falha explícitos.

Um arquivo por capítulo nesta pasta. O índice em `campanha/README.md` é gerado —
rode `campanha.py indexar` depois de acrescentar capítulo.

## Descrição do Cenário

_(o que qualquer personagem saberia antes de começar; pode ser lido em voz alta)_
""", encoding="utf-8")

    (p / "plano" / "npcs.md").write_text(
        f"""# NPCs de toda a campanha — {args.nome}

Quem **atravessa a campanha**: reaparece em vários capítulos, ou muda ao longo dela. Cada
capítulo tem o seu próprio `npcs.md` para quem só aparece lá.

O critério é este: se a ficha for consultada em **três ou mais capítulos**, ou se o NPC
**mudar** de um capítulo para outro, ele mora aqui. O resto fica no capítulo.

_(a preencher)_
""", encoding="utf-8")

    print(f"Campanha criada : {args.nome}")
    print(f"  {p/'README.md'}")
    print(f"  {p/'plano'}/ ")
    print("Agora escreva a Descrição do Cenário e os capítulos do plano.")


def cmd_capitulo(args):
    r = raiz(args)
    p = exige_campanha(r)
    plano = p / "plano"
    n = args.numero or proximo_numero(plano, "[0-9]*-*")
    pasta = plano / f"{n:02d}-{slug(args.titulo)}"
    if pasta.exists():
        raise SystemExit(f"{pasta} ja existe.")
    pasta.mkdir(parents=True)

    (pasta / "npcs.md").write_text(f"""# NPCs — {n}. {args.titulo}

Quem aparece **neste capítulo**. Ficha completa aqui só para quem é exclusivo dele; quem
atravessa a campanha fica em [`../npcs.md`](../npcs.md), com link daqui.

## Da campanha

_(liste aqui, com link para `../npcs.md`, quem vem de lá — e diga o que muda neste
capítulo: quantos são, em que estado, o que sabem)_

## Só deste capítulo

_(ficha completa: atributos, vantagens, desvantagens, perícias, armas, equipamento)_
""", encoding="utf-8")

    destino = pasta / "README.md"
    destino.write_text(f"""# {n}. {args.titulo}

**Mapa:** {args.mapa or "—"}
**Local:** {args.local or "—"}
**Imagem inicial:** —

_(cena no padrão de Caravana para Ein Arris: o que os PJs veem, o que só o Mestre sabe,
os testes com o NH exigido e a consequência de cada falha — inclusive a falha crítica.)_

## O que acontece

## Testes

| Situação | Perícia / Atributo | Sucesso | Falha | Falha crítica |
|---|---|---|---|---|

## NPCs

Ver [`npcs.md`](npcs.md) desta pasta.

## Se os jogadores fizerem outra coisa
""", encoding="utf-8")
    print(f"Capítulo criado: {pasta}/")
    print(f"  README.md — a cena")
    print(f"  npcs.md   — quem aparece nela")
    print("Gere a imagem inicial da cena (skill imagine) e rode:")
    print(f"  campanha.py imagem-inicial --arquivo <png> --capitulo {n}")
    print("Se nao houver geracao de imagem, rode com --prompt.")
    reindexar(p)


def cmd_evento(args):
    """Abre uma cena de jogo que NAO esta no plano — os jogadores inventaram algo.

    Cena que esta no plano nao precisa disto: `atual --capitulo N` ja abre a pasta dela.
    """
    r = raiz(args)
    p = exige_campanha(r)
    usados = [d for d in list(p.glob("*")) + list((p / "plano").glob("*"))
              if d.is_dir() and re.match(r"^\d+-", d.name)]
    n = args.numero or (max((int(d.name.split("-")[0]) for d in usados), default=0) + 1)
    pasta = p / f"{n:02d}-{slug(args.titulo)}"
    if pasta.exists():
        raise SystemExit(f"{pasta} ja existe. Use 'acontecimento --evento {n}'.")
    pasta.mkdir(parents=True)
    cap = f"**Capítulo do plano:** {args.capitulo}\n" if args.capitulo else ""
    (pasta / "README.md").write_text(f"""# {n}. {args.titulo} — como aconteceu

**Quando:** {hoje()}
{cap}**Onde:** {args.onde or "_(a preencher)_"}
**Quem estava:** {args.quem or "_(a preencher)_"}
**Imagem inicial:** —

{args.resumo or "_(introdução: o que era a cena quando começou)_"}

## Acontecimentos

{MARCA.format("acontecimentos")}
_(nada registrado ainda)_
{FIM.format("acontecimentos")}
""", encoding="utf-8")
    print(f"Cena de jogo aberta: {pasta}")
    print("Gere a imagem inicial da cena (skill imagine) e rode:")
    print("  campanha.py imagem-inicial --arquivo <png>")
    print("Se nao houver geracao de imagem, rode com --prompt.")
    reindexar(p)


def pasta_ilustracoes(p, evento=None, capitulo=None):
    """Ilustrações da cena planejada: pasta do capítulo em plano/.

    Cena fora do plano (evento de jogo sem correspondente) grava na pasta de jogo.
    """
    if capitulo not in (None, ""):
        plano = pasta_do_capitulo(p, capitulo)
        if plano is None:
            caps = ", ".join(sorted(x.name for x in (p / "plano").glob("*") if x.is_dir()))
            raise SystemExit(f"Nao achei o capitulo {capitulo} no plano. Existem: {caps}")
        return plano
    if evento:
        jogo = pasta_jogo_atual(p, evento)
        candidato = p / "plano" / jogo.name
        return candidato if candidato.is_dir() else jogo
    meta, _ = ler_meta(p)
    atual = meta.get("Capítulo atual", "").strip()
    plano = pasta_do_capitulo(p, atual)
    if plano:
        return plano
    return pasta_jogo_atual(p, None)


def link_desde(origem_dir, arquivo):
    """Caminho relativo de origem_dir até arquivo, com barras POSIX."""
    return Path(os.path.relpath(arquivo, origem_dir)).as_posix()


def pasta_jogo_atual(p, evento=None):
    """Pasta de jogo do --evento, ou a do capítulo atual."""
    pastas = sorted(x for x in p.glob("*") if x.is_dir() and x.name != "plano")
    if evento:
        chave = str(evento)
        for x in pastas:
            if (x.name == chave
                    or (chave.isdigit() and x.name.startswith(f"{int(chave):02d}-"))
                    or slug(chave) in x.name):
                return x
        raise SystemExit(f"Nao achei a cena \"{evento}\". "
                         f"Existem: {', '.join(x.name for x in pastas) or '(nenhuma)'}")
    meta, _ = ler_meta(p)
    alvo = pasta_de_jogo(p, meta.get("Capítulo atual", "").strip())
    if alvo is None:
        raise SystemExit(
            "Nao ha capitulo atual aberto. Rode:\n"
            "  campanha.py atual --capitulo N\n"
            "ou aponte a cena com --evento.")
    return alvo


def copiar_para_pasta(origem, pasta, nome):
    src = Path(origem)
    if not src.is_file():
        raise SystemExit(f"Nao achei a imagem {src}")
    dest = pasta / nome
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    return dest.name


def inserir_apos_cabecalho(texto, linha):
    """Encaixa `linha` logo depois do bloco **Campo:** do topo, se ainda não estiver."""
    if linha in texto:
        return texto
    linhas = texto.split("\n")
    i = 1
    while i < len(linhas) and not linhas[i].strip():
        i += 1
    while i < len(linhas) and linhas[i].startswith("**"):
        i += 1
    extra = [linha] if linhas[i - 1].strip() == "" else ["", linha]
    if i < len(linhas) and linhas[i].strip():
        extra.append("")
    linhas[i:i] = extra
    return "\n".join(linhas)


def cmd_acontecimento(args):
    r = raiz(args)
    p = exige_campanha(r)
    alvo = pasta_jogo_atual(p, args.evento or None)
    figs = pasta_ilustracoes(p, args.evento or None)

    readme = alvo / "README.md"
    texto = readme.read_text(encoding="utf-8")
    ini, fim = MARCA.format("acontecimentos"), FIM.format("acontecimentos")
    miolo = texto.split(ini, 1)[1].split(fim, 1)[0].strip() if ini in texto else ""
    if miolo.startswith("_("):
        miolo = ""
    linha = f"- **{agora()}** — {args.texto}"
    if args.imagem:
        ext = Path(args.imagem).suffix.lower() or ".png"
        base = Path(args.nome).stem if args.nome else slug(args.texto)[:48]
        nome = (base or "acontecimento") + ext
        if (figs / nome).exists():
            stem = Path(nome).stem
            n = 2
            while (figs / f"{stem}-{n}{ext}").exists():
                n += 1
            nome = f"{stem}-{n}{ext}"
        gravado = copiar_para_pasta(args.imagem, figs, nome)
        href = link_desde(alvo, figs / gravado)
        linha += f"\n  ![]({href})"
    if args.prompt:
        linha += f"\n  **Prompt da imagem:** {args.prompt.strip()}"
    novo = (miolo + "\n" + linha).strip()
    readme.write_text(bloco(texto, "acontecimentos", novo), encoding="utf-8")
    print(f"Registrado em {alvo.name}: {args.texto[:70]}")
    if args.imagem:
        print(f"  imagem : {figs / gravado}")
    elif args.prompt:
        print("  prompt anexado (sem imagem gerada)")
    reindexar(p)


def cmd_imagem_inicial(args):
    """Grava a ilustração de abertura no capítulo do plano."""
    r = raiz(args)
    p = exige_campanha(r)
    alvo = pasta_ilustracoes(p, args.evento or None, args.capitulo or None)
    if not args.arquivo and not args.prompt:
        raise SystemExit("Passe --arquivo (png/jpg gerado) ou --prompt.")

    if args.arquivo:
        nome = copiar_para_pasta(args.arquivo, alvo, "inicio" + (
            Path(args.arquivo).suffix.lower() or ".png"))
        definir_campo(alvo, "Imagem inicial", f"`{nome}`")
        rd = alvo / "README.md"
        t = inserir_apos_cabecalho(rd.read_text(encoding="utf-8"), f"![]({nome})")
        rd.write_text(t, encoding="utf-8")
        print(f"Imagem inicial: {alvo / nome}")
    if args.prompt:
        if not args.arquivo:
            definir_campo(alvo, "Imagem inicial", "_(prompt — não gerada)_")
        rd = alvo / "README.md"
        t = rd.read_text(encoding="utf-8")
        bloco_p = f"**Prompt da imagem inicial:** {args.prompt.strip()}"
        if "**Prompt da imagem inicial:**" in t:
            t = re.sub(r"^\*\*Prompt da imagem inicial:\*\*.*$",
                       bloco_p, t, count=1, flags=re.M)
        else:
            t = inserir_apos_cabecalho(t, bloco_p)
        rd.write_text(t, encoding="utf-8")
        print("Prompt da imagem inicial anexado ao README do plano.")
    reindexar(p)


def reindexar(p):
    """Regera os dois indices do README a partir do que existe em disco."""
    plano = sorted(x for x in (p / "plano").glob("*") if x.is_dir())
    linhas = []
    for x in plano:
        rd = x / "README.md"
        titulo = (rd.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
                  if rd.is_file() else x.name)
        extra = " · [NPCs](plano/{}/npcs.md)".format(x.name) \
            if (x / "npcs.md").is_file() else ""
        linhas.append(f"- [{titulo}](plano/{x.name}/){extra}")
    if (p / "plano" / "npcs.md").is_file():
        linhas.append("- [NPCs de toda a campanha](plano/npcs.md)")
    conteudo_plano = "\n".join(linhas) or "_(nenhum capítulo ainda)_"

    eventos = sorted(x for x in p.glob("*") if x.is_dir() and x.name != "plano")
    linhas = []
    for x in eventos:
        rd = x / "README.md"
        titulo = x.name
        quando = ""
        n = 0
        if rd.is_file():
            t = rd.read_text(encoding="utf-8")
            titulo = t.splitlines()[0].lstrip("# ").strip()
            m = re.search(r"^\*\*(?:Quando|Aberto em):\*\*\s*(.+?)\s*$", t, re.M)
            quando = m.group(1) if m else ""
            # so entre os marcadores: o README tambem guarda a narracao, e prosa
            # nenhuma pode ser contada como acontecimento
            miolo = t.split(MARCA.format("acontecimentos"))[-1]
            miolo = miolo.split(FIM.format("acontecimentos"))[0]
            n = len(re.findall(r"^- \*\*", miolo, re.M))
        extras = sorted(f.name for f in x.glob("*")
                        if f.is_file() and f.name != "README.md")
        linhas.append(f"- [{titulo}]({x.name}/)" + (f" — {quando}" if quando else "")
                      + (f" · {n} acontecimento(s)" if n else "")
                      + (f" · {len(extras)} arquivo(s) de mesa" if extras else ""))
    conteudo_hist = "\n".join(linhas) or "_(nada aconteceu ainda)_"

    texto = (p / "README.md").read_text(encoding="utf-8")
    texto = bloco(texto, "plano", conteudo_plano)
    texto = bloco(texto, "historico", conteudo_hist)
    (p / "README.md").write_text(texto, encoding="utf-8")
    return len(plano), len(eventos)


def cmd_atual(args):
    """Marca em que capitulo a mesa esta. Outras skills leem isso para saber onde gravar."""
    r = raiz(args)
    p = exige_campanha(r)
    texto = (p / "README.md").read_text(encoding="utf-8")
    pasta = pasta_do_capitulo(p, args.capitulo)
    if pasta is None:
        caps = ", ".join(sorted(x.name for x in (p / "plano").glob("*") if x.is_dir()))
        raise SystemExit(f"Nao achei o capitulo {args.capitulo}. Existem: {caps}")

    linha = f"**Capítulo atual:** {int(args.capitulo):02d}"
    if "**Capítulo atual:**" in texto:
        texto = re.sub(r"^\*\*Capítulo atual:\*\*.*$", linha, texto, count=1, flags=re.M)
    else:
        alvo = "**Cenário:**"
        i = texto.index(alvo)
        fim = texto.index("\n", i)
        texto = texto[:fim + 1] + linha + "\n" + texto[fim + 1:]
    (p / "README.md").write_text(texto, encoding="utf-8")
    jogo, criada = abrir_capitulo(p, pasta)
    reindexar(p)
    print(f"Capítulo atual: {pasta.name}")
    print(f"  planejado em : {pasta}")
    print(f"  em jogo em   : {jogo}" + ("   (pasta aberta agora)" if criada else ""))


def cmd_mapa(args):
    """Declara no plano qual cenario a cena usa. E informacao de plano, nao de jogo."""
    r = raiz(args)
    p = exige_campanha(r)
    pasta = pasta_do_capitulo(p, args.capitulo)
    if pasta is None:
        caps = ", ".join(sorted(x.name for x in (p / "plano").glob("*") if x.is_dir()))
        raise SystemExit(f"Nao achei o capitulo {args.capitulo}. Existem: {caps}")

    alvo = r / args.mapa
    if not alvo.is_file():
        print(f"AVISO: {args.mapa} nao existe ainda — anotei mesmo assim.")
    elif alvo.suffix.lower() != ".json":
        print(f"AVISO: {args.mapa} nao e o indice .json de hexagonos da add-grid-hex; "
              "a atualizar-mapa precisa do .json para colar tokens.")

    definir_campo(pasta, "Mapa", f"`{args.mapa}`")
    if args.local:
        definir_campo(pasta, "Local", args.local)
    print(f"Capítulo {pasta.name}")
    print(f"  Mapa : {args.mapa}")
    if args.local:
        print(f"  Local: {args.local}")


def cmd_indexar(args):
    p = exige_campanha(raiz(args))
    c, e = reindexar(p)
    print(f"Índice regerado: {c} capítulo(s), {e} evento(s).")


def cmd_encerrar(args):
    r = raiz(args)
    p = exige_campanha(r)
    meta, texto = ler_meta(p)
    nome = meta.get("Campanha", p.name)
    destino = r / ARQUIVO / slug(nome)
    if destino.exists():
        raise SystemExit(f"{destino} ja existe — renomeie ou apague antes.")

    texto = re.sub(r"^\*\*Estado:\*\*.*$", "**Estado:** encerrada", texto, flags=re.M)
    if "**Encerramento:**" not in texto:
        texto = re.sub(r"^(\*\*Estado:\*\*.*)$",
                       r"\1\n**Encerramento:** " + hoje(), texto, count=1, flags=re.M)
    if args.desfecho:
        texto = texto.rstrip() + f"\n\n## Desfecho\n\n{args.desfecho}\n"
    (p / "README.md").write_text(texto, encoding="utf-8")

    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(p), str(destino))
    print(f"Campanha \"{nome}\" encerrada e movida para {destino}")
    print("Não há mais campanha ativa — o repositório está livre para a próxima.")


# ------------------------------------------------- estado do mundo (anotar)

# Onde mora cada tipo de mudanca, dentro da pasta de JOGO do capitulo.
# arquivo, secao no consolidado, titulo, de quem e, exemplos do que anotar
ANOTACOES = {
    "npc": ("npcs.md", "NPCs", "NPCs — {titulo}", "estes NPCs",
            "ferimento que ficou, morte, item, dívida, promessa, "
            "o que passaram a saber, relação que mudou"),
    "pj": ("grupo.md", "Grupo", "Grupo — {titulo}",
           "os personagens dos jogadores",
           "ferimento que ficou, dinheiro e item ganho ou perdido, "
           "dívida, promessa feita, o que descobriram"),
    "coisa": ("lugares.md", "Lugares e coisas", "Lugares e coisas — {titulo}",
              "o lugar, os objetos e o que se sabe",
              "porta arrombada, fogo, item largado no chão, boato que correu, "
              "o que a cidade já viu"),
}


def titulo_do_readme(pasta):
    """O `# Titulo` do README de uma pasta."""
    f = pasta / "README.md"
    if not f.is_file():
        return pasta.name
    for linha in f.read_text(encoding="utf-8").split("\n"):
        if linha.startswith("# "):
            # "1. Encontro na Taberna - como aconteceu" -> so o titulo da cena
            return linha[2:].split(" — ")[0].strip()
    return pasta.name


def criar_arquivo_estado(alvo, p, tipo):
    """Cria o arquivo de estado na pasta de jogo, com cabecalho e link ao plano."""
    nome, _, titulo_fmt, sujeito, exemplos = ANOTACOES[tipo]
    f = alvo / nome
    if f.is_file():
        return f
    plano = p / "plano" / alvo.name
    ref = ""
    if (plano / nome).is_file():
        ref = (" O planejado está em "
               "[`plano/{0}/{1}`]({2}), e não se mexe.".format(
                   alvo.name, nome, link_desde(alvo, plano / nome)))
    elif plano.is_dir():
        ref = (" A cena planejada está em "
               "[`plano/{0}/`]({1}), e não se mexe.".format(
                   alvo.name, link_desde(alvo, plano)))
    f.write_text(
        "# {0} — na mesa\n\n".format(titulo_fmt.format(titulo=titulo_do_readme(alvo)))
        + "_(o que de fato aconteceu com {0} durante o jogo — {1}.{2}\n".format(
            sujeito, exemplos, ref)
        + "**Leia isto antes de interpretar a cena de novo.**)_\n",
        encoding="utf-8")
    return f


def inserir_em_secao(texto, sujeito, linha):
    """Poe `linha` no fim da secao `## sujeito`, criando a secao se faltar."""
    linhas = texto.rstrip("\n").split("\n")
    alvo_slug = slug(sujeito)
    ini = None
    for i, l in enumerate(linhas):
        if l.startswith("## ") and slug(l[3:]) == alvo_slug:
            ini = i
            break
    if ini is None:
        return "\n".join(linhas) + "\n\n## {0}\n\n{1}\n".format(sujeito, linha)
    fim = len(linhas)
    for j in range(ini + 1, len(linhas)):
        if linhas[j].startswith("## "):
            fim = j
            break
    corte = fim
    while corte > ini + 1 and not linhas[corte - 1].strip():
        corte -= 1
    linhas[corte:corte] = [linha]
    return "\n".join(linhas) + "\n"


def cmd_anotar(args):
    r = raiz(args)
    p = exige_campanha(r)
    escolhidos = [(t, getattr(args, t)) for t in ANOTACOES if getattr(args, t)]
    if len(escolhidos) != 1:
        raise SystemExit("Diga de quem é a mudança: --npc, --pj ou --coisa (um só).")
    tipo, sujeito = escolhidos[0]
    alvo = pasta_jogo_atual(p, args.evento or None)
    f = criar_arquivo_estado(alvo, p, tipo)
    marca = " · _{0}_".format(args.tag) if args.tag else ""
    linha = "- **{0}**{1} — {2}".format(agora(), marca, args.texto.strip())
    f.write_text(inserir_em_secao(f.read_text(encoding="utf-8"),
                                  sujeito.strip(), linha), encoding="utf-8")
    print("Anotado em {0}/{1} - {2}: {3}".format(
        alvo.name, f.name, sujeito.strip(), args.texto[:60]))
    print("  consolidado: {0}".format(regerar_mundo(p).as_posix()))


def ler_estado(f):
    """Le um arquivo de estado: [(sujeito, [linhas])] na ordem do arquivo."""
    fora = []
    atual = None
    for l in f.read_text(encoding="utf-8").split("\n"):
        if l.startswith("## "):
            atual = (l[3:].strip(), [])
            fora.append(atual)
        elif atual is not None and l.startswith("- **"):
            atual[1].append(l)
    return [(s, ls) for s, ls in fora if ls]


def regerar_mundo(p):
    """Consolida o estado de todos os capitulos em campanha/mundo.md."""
    pastas = sorted(x for x in p.glob("*") if x.is_dir() and x.name != "plano")
    secoes = {}
    ordem = ["npc", "pj", "coisa"]
    for tipo in ordem:
        nome, secao = ANOTACOES[tipo][0], ANOTACOES[tipo][1]
        for pasta in pastas:
            f = pasta / nome
            if not f.is_file():
                continue
            cap = pasta.name.split("-", 1)[0]
            for sujeito, linhas in ler_estado(f):
                alvo = secoes.setdefault(secao, {}).setdefault(sujeito, [])
                for l in linhas:
                    alvo.append("{0}  _(cap. {1})_".format(l, cap))
    partes = []
    for tipo in ordem:
        secao = ANOTACOES[tipo][1]
        if secao not in secoes:
            continue
        partes.append("## {0}\n".format(secao))
        for sujeito in sorted(secoes[secao]):
            partes.append("### {0}\n".format(sujeito))
            partes.extend(secoes[secao][sujeito])
            partes.append("")
    corpo = "\n".join(partes).strip() or "_(nada anotado ainda)_"
    meta, _ = ler_meta(p)
    f = p / "mundo.md"
    cabecalho = (
        "# O estado do mundo — {0}\n\n".format(meta.get("Campanha", "?"))
        + "_(consolidado, gerado por `campanha.py anotar` e `campanha.py mundo` a partir\n"
        + "dos arquivos de estado de cada capítulo. **Não edite entre os marcadores**:\n"
        + "edite `campanha/NN-.../npcs.md`, `grupo.md` ou `lugares.md`, ou anote pelo\n"
        + "script, e rode `campanha.py mundo`.)_\n")
    texto = f.read_text(encoding="utf-8") if f.is_file() else cabecalho
    if MARCA.format("mundo") not in texto:
        texto = cabecalho
    f.write_text(bloco(texto, "mundo", corpo), encoding="utf-8")
    return f


def cmd_mundo(args):
    r = raiz(args)
    p = exige_campanha(r)
    f = regerar_mundo(p)
    print(f.read_text(encoding="utf-8") if args.mostrar
          else "Consolidado em {0}".format(f.as_posix()))


# ------------------------------------------------------------ bolsa (dinheiro)

BOLSA = "bolsa.md"
LANCAMENTO = re.compile(r"^- \*\*(?P<quando>[^*]+)\*\*\s+·\s+"
                        r"(?P<valor>[+-]\s*\d+)\s+—\s+(?P<motivo>.*)$")
BOLSA_SECOES = [("pj", "Personagens"), ("npc", "NPCs")]


def ler_bolsa(f):
    """[(secao, nome, [(quando, valor, motivo)])] na ordem do arquivo."""
    if not f.is_file():
        return []
    secao, nome, fora = None, None, []
    for l in f.read_text(encoding="utf-8").split("\n"):
        if l.startswith("## "):
            secao, nome = l[3:].strip(), None
        elif l.startswith("### "):
            nome = l[4:].strip()
            fora.append((secao, nome, []))
        elif nome and (m := LANCAMENTO.match(l.rstrip())):
            fora[-1][2].append((m.group("quando"),
                                int(m.group("valor").replace(" ", "")),
                                m.group("motivo").strip()))
    return fora


def escrever_bolsa(p, lancamentos):
    """Regera bolsa.md: tabela de saldos + extrato, a partir dos lancamentos."""
    meta, _ = ler_meta(p)
    partes, saldos = [], []
    for _, titulo in BOLSA_SECOES:
        desta = sorted(((n, ls) for sec, n, ls in lancamentos if sec == titulo),
                       key=lambda x: slug(x[0]))
        if not desta:
            continue
        partes.append("## {0}\n".format(titulo))
        for nome, ls in desta:
            total = sum(v for _, v, _ in ls)
            saldos.append((titulo, nome, total, len(ls)))
            partes.append("### {0}\n".format(nome))
            partes.append("**Saldo: ${0}**\n".format(total))
            for quando, valor, motivo in ls:
                partes.append("- **{0}** · {1}{2} — {3}".format(
                    quando, "+" if valor >= 0 else "-", abs(valor), motivo))
            partes.append("")
    corpo = "\n".join(partes).strip() or "_(ninguém tem lançamento ainda)_"

    tabela = ["| Quem | | Saldo | Lançamentos |", "|---|---|---:|---:|"]
    for titulo, nome, total, n in saldos:
        cifra = ("-$" + str(-total)) if total < 0 else ("$" + str(total))
        tabela.append("| {0} | {1} | {2} | {3} |".format(
            nome, "PJ" if titulo == "Personagens" else "NPC", cifra, n))
    resumo = "\n".join(tabela) if saldos else "_(sem saldos)_"

    f = p / BOLSA
    cabecalho = (
        "# A bolsa — {0}\n\n".format(meta.get("Campanha", "?"))
        + "_(o dinheiro de cada um **em jogo**. A ficha do personagem não é mexida por\n"
        + "causa de moeda: o que ele ganhou e gastou na mesa mora aqui. Lance com\n"
        + "`campanha.py bolsa --pj \"Nome\" --valor +50 --motivo \"...\"`; a tabela de\n"
        + "saldos e os totais são recalculados a partir dos lançamentos.)_\n\n"
        + "<!-- indice:saldos -->\n_(sem saldos)_\n<!-- /indice:saldos -->\n")
    texto = f.read_text(encoding="utf-8") if f.is_file() else cabecalho
    if MARCA.format("saldos") not in texto:
        texto = cabecalho
    texto = bloco(texto, "saldos", resumo)
    # o extrato vem depois do bloco de saldos e e regerado inteiro
    corte = texto.index(FIM.format("saldos")) + len(FIM.format("saldos"))
    f.write_text(texto[:corte] + "\n\n" + corpo + "\n", encoding="utf-8")
    return f


def cmd_bolsa(args):
    r = raiz(args)
    p = exige_campanha(r)
    f = p / BOLSA
    lancamentos = ler_bolsa(f)

    quem = (args.pj or args.npc or "").strip()
    if quem and args.valor:
        titulo = "Personagens" if args.pj else "NPCs"
        try:
            valor = int(str(args.valor).replace(" ", "").replace("$", ""))
        except ValueError:
            raise SystemExit("--valor e um numero com sinal: +300, -40.")
        entrada = (agora(), valor, args.motivo.strip() or "sem motivo dado")
        for sec, nome, ls in lancamentos:
            if sec == titulo and slug(nome) == slug(quem):
                # o saldo inicial abre o extrato, mesmo lancado depois
                ls.insert(0, entrada) if args.inicial else ls.append(entrada)
                break
        else:
            lancamentos.append((titulo, quem, [entrada]))
        escrever_bolsa(p, lancamentos)
        total = sum(v for sec, nome, ls in lancamentos
                    if sec == titulo and slug(nome) == slug(quem)
                    for _, v, _ in ls)
        print("Lancado: {0} {1}{2} - saldo ${3}".format(
            quem, "+" if valor >= 0 else "-", abs(valor), total))
        return
    if quem or args.valor:
        raise SystemExit("Diga os dois: --pj/--npc \"Nome\" e --valor +50.")

    f = escrever_bolsa(p, lancamentos)
    print(f.read_text(encoding="utf-8") if args.mostrar
          else "Saldos em {0}".format(f.as_posix()))


# ----------------------------------------------------- saude (PV, fadiga, ferimentos)

SAUDE = "saude.md"
LINHA_SAUDE = re.compile(
    r"^- \*\*(?P<quando>[^*]+)\*\*\s+·\s+(?P<tipo>PV|FAD|estado|curado)"
    r"(?:\s+(?P<valor>[+-]\s*\d+))?\s+—\s+(?P<texto>.*)$")
SAUDE_SECOES = [("pj", "Personagens"), ("npc", "NPCs")]


def maximos_da_ficha(r, nome):
    """PV e Fadiga maximos de um PJ, lidos da ficha. (None, None) se nao houver."""
    base = r / "personagens"
    if not base.is_dir():
        return None, None
    alvo = slug(nome)
    for pasta in sorted(x for x in base.glob("*") if x.is_dir()):
        f = pasta / "personagem.json"
        if not f.is_file():
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if slug(d.get("nome") or "") == alvo or slug(pasta.name) == alvo:
            return d.get("pontos_vida"), d.get("fadiga")
    return None, None


def ler_saude(f):
    """[(secao, nome, [(quando, tipo, valor, texto)])] na ordem do arquivo."""
    if not f.is_file():
        return []
    secao, nome, fora = None, None, []
    for l in f.read_text(encoding="utf-8").split("\n"):
        if l.startswith("## "):
            secao, nome = l[3:].strip(), None
        elif l.startswith("### "):
            nome = l[4:].strip()
            fora.append((secao, nome, []))
        elif nome and (m := LINHA_SAUDE.match(l.rstrip())):
            valor = m.group("valor")
            fora[-1][2].append((m.group("quando"), m.group("tipo"),
                                int(valor.replace(" ", "")) if valor else None,
                                m.group("texto").strip()))
    return fora


def resumo_saude(linhas, pv_max, fad_max):
    """Devolve (texto do PV, texto da Fadiga, [estados ativos])."""
    pv = sum(v for _, t, v, _ in linhas if t == "PV" and v is not None)
    fad = sum(v for _, t, v, _ in linhas if t == "FAD" and v is not None)
    curados = [txt for _, t, _, txt in linhas if t == "curado"]
    estados = [txt for _, t, _, txt in linhas if t == "estado"
               and not any(slug(c) in slug(txt) or slug(txt) in slug(c)
                           for c in curados)]
    # sem maximo conhecido (NPC), mostra so o acumulado; sem nada, um travessao
    pv_txt = f"{pv_max + pv}/{pv_max}" if pv_max else (str(pv) if pv else "—")
    fad_txt = f"{fad_max + fad}/{fad_max}" if fad_max else (str(fad) if fad else "—")
    return pv_txt, fad_txt, estados


def escrever_saude(r, p, registros):
    """Regera saude.md: tabela do estado de cada um + o histórico."""
    meta, _ = ler_meta(p)
    partes, tabela_linhas = [], []
    for _, titulo in SAUDE_SECOES:
        desta = sorted(((n, ls) for sec, n, ls in registros if sec == titulo),
                       key=lambda x: slug(x[0]))
        if not desta:
            continue
        partes.append("## {0}\n".format(titulo))
        for nome, ls in desta:
            pv_max, fad_max = maximos_da_ficha(r, nome) if titulo == "Personagens" \
                else (None, None)
            pv_txt, fad_txt, estados = resumo_saude(ls, pv_max, fad_max)
            tabela_linhas.append("| {0} | {1} | {2} | {3} | {4} |".format(
                nome, "PJ" if titulo == "Personagens" else "NPC", pv_txt, fad_txt,
                "; ".join(estados) or "—"))
            partes.append("### {0}\n".format(nome))
            partes.append("**PV {0} · Fadiga {1}**{2}\n".format(
                pv_txt, fad_txt,
                "  ·  " + "; ".join("**" + e + "**" for e in estados) if estados else ""))
            for quando, tipo, valor, texto in ls:
                if valor is not None:
                    partes.append("- **{0}** · {1} {2}{3} — {4}".format(
                        quando, tipo, "+" if valor >= 0 else "-", abs(valor), texto))
                else:
                    partes.append("- **{0}** · {1} — {2}".format(quando, tipo, texto))
            partes.append("")
    corpo = "\n".join(partes).strip() or "_(ninguém se machucou ainda)_"

    if tabela_linhas:
        resumo = "\n".join(["| Quem | | PV | Fadiga | Estado |",
                            "|---|---|---:|---:|---|"] + tabela_linhas)
    else:
        resumo = "_(todo mundo inteiro)_"

    f = p / SAUDE
    cabecalho = (
        "# Saúde — {0}\n\n".format(meta.get("Campanha", "?"))
        + "_(pontos de vida, Fadiga e ferimentos que ficam, **em jogo**. A ficha do\n"
        + "personagem não é mexida por causa de dano: ela guarda o PV e a Fadiga máximos,\n"
        + "e o que a mesa gastou mora aqui. Lance com `campanha.py saude --pj \"Nome\"\n"
        + "--pv -3 --motivo \"...\"`; os totais são recalculados a partir dos lançamentos.)_\n\n"
        + "<!-- indice:saude -->\n_(todo mundo inteiro)_\n<!-- /indice:saude -->\n")
    texto = f.read_text(encoding="utf-8") if f.is_file() else cabecalho
    if MARCA.format("saude") not in texto:
        texto = cabecalho
    texto = bloco(texto, "saude", resumo)
    corte = texto.index(FIM.format("saude")) + len(FIM.format("saude"))
    f.write_text(texto[:corte] + "\n\n" + corpo + "\n", encoding="utf-8")
    return f


def cmd_saude(args):
    r = raiz(args)
    p = exige_campanha(r)
    registros = ler_saude(p / SAUDE)
    quem = (args.pj or args.npc or "").strip()
    titulo = "Personagens" if args.pj else "NPCs"
    lancamentos = []
    for campo, tipo in (("pv", "PV"), ("fadiga", "FAD")):
        valor = getattr(args, campo)
        if valor:
            try:
                lancamentos.append((tipo, int(str(valor).replace(" ", "")), None))
            except ValueError:
                raise SystemExit("--{0} e um numero com sinal: -3, +2.".format(campo))
    if args.estado:
        lancamentos.append(("estado", None, args.estado.strip()))
    if args.curar:
        lancamentos.append(("curado", None, args.curar.strip()))

    if quem and lancamentos:
        motivo = args.motivo.strip() or "sem motivo dado"
        entradas = [(agora(), tipo, valor, texto or motivo)
                    for tipo, valor, texto in lancamentos]
        for sec, nome, ls in registros:
            if sec == titulo and slug(nome) == slug(quem):
                ls.extend(entradas)
                break
        else:
            registros.append((titulo, quem, entradas))
        f = escrever_saude(r, p, registros)
        ls = next(ls for sec, nome, ls in registros
                  if sec == titulo and slug(nome) == slug(quem))
        pv_max, fad_max = maximos_da_ficha(r, quem) if args.pj else (None, None)
        pv_txt, fad_txt, estados = resumo_saude(ls, pv_max, fad_max)
        print("{0}: PV {1}, Fadiga {2}{3}".format(
            quem, pv_txt, fad_txt,
            "  [" + "; ".join(estados) + "]" if estados else ""))
        print("  {0}".format(f.as_posix()))
        return
    if quem or lancamentos:
        raise SystemExit(
            "Diga quem e o que mudou: --pj/--npc \"Nome\" com --pv, --fadiga, "
            "--estado ou --curar.")

    f = escrever_saude(r, p, registros)
    print(f.read_text(encoding="utf-8") if args.mostrar
          else "Saúde em {0}".format(f.as_posix()))


def main():
    ap = argparse.ArgumentParser(description="Gerencia a campanha ativa.")
    ap.add_argument("--raiz", default=".", help="Raiz do projeto")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("estado", help="Mostra a campanha ativa")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_estado)

    s = sub.add_parser("criar", help="Cria a campanha (uma por vez)")
    s.add_argument("--nome", required=True)
    s.add_argument("--mestre", default="IA (Mestre)")
    s.add_argument("--cenario", default="Yrth (GURPS Fantasy)")
    s.add_argument("--pontos", default="150")
    s.add_argument("--premissa", default="")
    s.set_defaults(func=cmd_criar)

    s = sub.add_parser("capitulo", help="Novo capítulo no plano")
    s.add_argument("--titulo", required=True)
    s.add_argument("--numero", type=int)
    s.add_argument("--mapa", default="", help="Índice .json do cenário desta cena")
    s.add_argument("--local", default="", help="Onde a cena se passa, em uma linha")
    s.set_defaults(func=cmd_capitulo)

    s = sub.add_parser("evento", help="Novo evento no histórico")
    s.add_argument("--titulo", required=True)
    s.add_argument("--resumo", default="")
    s.add_argument("--onde", default="")
    s.add_argument("--quem", default="")
    s.add_argument("--capitulo", default="")
    s.add_argument("--numero", type=int)
    s.set_defaults(func=cmd_evento)

    s = sub.add_parser("acontecimento", help="Anota um fato num evento")
    s.add_argument("--evento", default="",
                   help="Número ou nome da cena. Sem isto, usa o capítulo atual")
    s.add_argument("--texto", required=True)
    s.add_argument("--imagem", default="",
                   help="PNG/JPG da ilustração; é copiada para a pasta do plano")
    s.add_argument("--nome", default="",
                   help="Nome do arquivo na pasta (kebab-case). Sem isto, deriva do texto")
    s.add_argument("--prompt", default="",
                   help="Prompt da imagem, quando nao foi possivel gera-la")
    s.set_defaults(func=cmd_acontecimento)

    s = sub.add_parser("imagem-inicial",
                       help="Grava a ilustração de abertura no capítulo do plano")
    s.add_argument("--arquivo", default="", help="PNG/JPG gerado (vira inicio.png)")
    s.add_argument("--prompt", default="",
                   help="Prompt, quando nao foi possivel gerar a imagem")
    s.add_argument("--capitulo", default="",
                   help="Número do capítulo no plano (padrão: o atual)")
    s.add_argument("--evento", default="",
                   help="Cena de jogo sem plano, se nao for o capítulo atual")
    s.set_defaults(func=cmd_imagem_inicial)

    s = sub.add_parser("atual", help="Marca em que capítulo a mesa está")
    s.add_argument("--capitulo", required=True, help="Número do capítulo (ex.: 3)")
    s.set_defaults(func=cmd_atual)

    s = sub.add_parser("mapa", help="Declara o cenário de um capítulo do plano")
    s.add_argument("--capitulo", required=True)
    s.add_argument("--mapa", required=True, help="Ex.: cenarios/taberna3.json")
    s.add_argument("--local", default="")
    s.set_defaults(func=cmd_mapa)

    s = sub.add_parser("anotar",
                       help="Anota uma mudança que fica (ferimento, item, relação)")
    s.add_argument("--npc", default="", help="Nome do NPC que mudou")
    s.add_argument("--pj", default="", help="Nome do personagem de jogador que mudou")
    s.add_argument("--coisa", default="", help="Lugar, objeto ou informação que mudou")
    s.add_argument("--texto", required=True, help="A mudança, em uma linha, no passado")
    s.add_argument("--tag", default="",
                   help="ferimento, morte, item, relação, informação, promessa...")
    s.add_argument("--evento", default="",
                   help="Número ou nome da cena. Sem isto, usa o capítulo atual")
    s.set_defaults(func=cmd_anotar)

    s = sub.add_parser("mundo", help="Regera (e mostra) o estado do mundo consolidado")
    s.add_argument("--mostrar", action="store_true", help="Imprime o arquivo inteiro")
    s.set_defaults(func=cmd_mundo)

    s = sub.add_parser("bolsa",
                       help="O dinheiro de cada um, fora da ficha")
    s.add_argument("--pj", default="", help="Personagem de jogador")
    s.add_argument("--npc", default="", help="NPC")
    s.add_argument("--valor", default="", help="Com sinal: +300, -40")
    s.add_argument("--motivo", default="", help="De onde veio ou para onde foi")
    s.add_argument("--inicial", action="store_true",
                   help="Saldo inicial: abre o extrato, mesmo lançado depois")
    s.add_argument("--mostrar", action="store_true", help="Imprime o arquivo inteiro")
    s.set_defaults(func=cmd_bolsa)

    s = sub.add_parser("saude",
                       help="PV, Fadiga e ferimentos que ficam, fora da ficha")
    s.add_argument("--pj", default="", help="Personagem de jogador")
    s.add_argument("--npc", default="", help="NPC")
    s.add_argument("--pv", default="", help="Com sinal: -3 (dano), +2 (cura)")
    s.add_argument("--fadiga", default="", help="Com sinal: -2, +5")
    s.add_argument("--estado", default="",
                   help="Ferimento que fica: \"Braço direito incapacitado (Maneta)\"")
    s.add_argument("--curar", default="",
                   help="Encerra um estado: parte do texto dele")
    s.add_argument("--motivo", default="", help="De onde veio o dano ou a cura")
    s.add_argument("--mostrar", action="store_true", help="Imprime o arquivo inteiro")
    s.set_defaults(func=cmd_saude)

    s = sub.add_parser("indexar", help="Regera o índice do README")
    s.set_defaults(func=cmd_indexar)

    s = sub.add_parser("encerrar", help="Arquiva em historico/campanhas/")
    s.add_argument("--desfecho", default="")
    s.set_defaults(func=cmd_encerrar)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
