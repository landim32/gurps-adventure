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
    campanha.py indexar
    campanha.py encerrar

O que e trabalho de escrever (o plano, a prosa de cada cena) nao esta aqui: o script
cuida do que da errado quando se faz a mao — numeracao, data, o indice que desatualiza
e a regra de uma campanha ativa por vez.
"""
import argparse
import json
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

{args.resumo or "_(introdução: o que era a cena quando começou)_"}

## Acontecimentos

{MARCA.format("acontecimentos")}
_(nada registrado ainda)_
{FIM.format("acontecimentos")}
""", encoding="utf-8")
    print(f"Cena de jogo aberta: {pasta}")
    reindexar(p)


def cmd_acontecimento(args):
    r = raiz(args)
    p = exige_campanha(r)
    pastas = sorted(x for x in p.glob("*") if x.is_dir() and x.name != "plano")

    if args.evento:
        alvo, chave = None, str(args.evento)
        for x in pastas:
            if (x.name == chave
                    or (chave.isdigit() and x.name.startswith(f"{int(chave):02d}-"))
                    or slug(chave) in x.name):
                alvo = x
                break
        if alvo is None:
            raise SystemExit(f"Nao achei a cena \"{args.evento}\". "
                             f"Existem: {', '.join(x.name for x in pastas) or '(nenhuma)'}")
    else:
        # sem --evento, escreve no capitulo atual: e o caso normal durante a sessao
        meta, _ = ler_meta(p)
        alvo = pasta_de_jogo(p, meta.get("Capítulo atual", "").strip())
        if alvo is None:
            raise SystemExit(
                "Nao ha capitulo atual aberto. Rode:\n"
                "  campanha.py atual --capitulo N\n"
                "ou aponte a cena com --evento.")

    readme = alvo / "README.md"
    texto = readme.read_text(encoding="utf-8")
    ini, fim = MARCA.format("acontecimentos"), FIM.format("acontecimentos")
    miolo = texto.split(ini, 1)[1].split(fim, 1)[0].strip() if ini in texto else ""
    if miolo.startswith("_("):
        miolo = ""
    linha = f"- **{agora()}** — {args.texto}"
    novo = (miolo + "\n" + linha).strip()
    readme.write_text(bloco(texto, "acontecimentos", novo), encoding="utf-8")
    print(f"Registrado em {alvo.name}: {args.texto[:70]}")
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
    s.set_defaults(func=cmd_acontecimento)

    s = sub.add_parser("atual", help="Marca em que capítulo a mesa está")
    s.add_argument("--capitulo", required=True, help="Número do capítulo (ex.: 3)")
    s.set_defaults(func=cmd_atual)

    s = sub.add_parser("mapa", help="Declara o cenário de um capítulo do plano")
    s.add_argument("--capitulo", required=True)
    s.add_argument("--mapa", required=True, help="Ex.: cenarios/taberna3.json")
    s.add_argument("--local", default="")
    s.set_defaults(func=cmd_mapa)

    s = sub.add_parser("indexar", help="Regera o índice do README")
    s.set_defaults(func=cmd_indexar)

    s = sub.add_parser("encerrar", help="Arquiva em historico/campanhas/")
    s.add_argument("--desfecho", default="")
    s.set_defaults(func=cmd_encerrar)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
