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


def pasta_do_capitulo(p, numero):
    """A pasta plano/NN-... do capitulo, pelo numero."""
    if numero in (None, "", "—"):
        return None
    try:
        n = int(str(numero).strip())
    except ValueError:
        return None
    for d in sorted((p / "plano").glob("*")):
        if d.is_dir() and d.name.startswith(f"{n:02d}-"):
            return d
    return None


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
        evs = sorted(x.name for x in (p / "historico").glob("*/") if x.is_dir())
        atual = meta.get("Capítulo atual", "").strip()
        pasta_cap = pasta_do_capitulo(p, atual)
        dados.update({"nome": meta.get("Campanha", "?"),
                      "estado": meta.get("Estado", "?"),
                      "mestre": meta.get("Mestre", "?"),
                      "inicio": meta.get("Início", "?"),
                      "capitulo_atual": atual or None,
                      "capitulo_atual_pasta":
                          pasta_cap.as_posix() if pasta_cap else None,
                      "capitulos": caps, "eventos": evs})
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
        print(f"Eventos   : {len(dados['eventos'])}")
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
    (p / "historico").mkdir(parents=True, exist_ok=True)

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
    print(f"  {p/'historico'}/ ")
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
    r = raiz(args)
    p = exige_campanha(r)
    hist = p / "historico"
    n = args.numero or proximo_numero(hist, "[0-9]*-*")
    pasta = hist / f"{n:02d}-{slug(args.titulo)}"
    if pasta.exists():
        raise SystemExit(f"{pasta} ja existe. Use 'acontecimento --evento {n}'.")
    pasta.mkdir(parents=True)
    cap = f"**Capítulo do plano:** {args.capitulo}\n" if args.capitulo else ""
    (pasta / "README.md").write_text(f"""# {n}. {args.titulo}

**Quando:** {hoje()}
{cap}**Onde:** {args.onde or "_(a preencher)_"}
**Quem estava:** {args.quem or "_(a preencher)_"}

{args.resumo or "_(introdução: o que era a cena quando começou)_"}

## Acontecimentos

{MARCA.format("acontecimentos")}
_(nada registrado ainda)_
{FIM.format("acontecimentos")}
""", encoding="utf-8")
    print(f"Evento criado: {pasta}")
    reindexar(p)


def cmd_acontecimento(args):
    r = raiz(args)
    p = exige_campanha(r)
    pastas = sorted(x for x in (p / "historico").glob("*") if x.is_dir())
    if not pastas:
        raise SystemExit("Nenhum evento ainda. Crie com: campanha.py evento --titulo ...")
    alvo = None
    chave = str(args.evento)
    for x in pastas:
        if x.name == chave or x.name.startswith(f"{int(chave):02d}-") if chave.isdigit() \
                else x.name == chave or slug(chave) in x.name:
            alvo = x
            break
    if alvo is None:
        raise SystemExit(f"Nao achei o evento \"{args.evento}\". "
                         f"Existem: {', '.join(x.name for x in pastas)}")

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

    eventos = sorted(x for x in (p / "historico").glob("*") if x.is_dir())
    linhas = []
    for x in eventos:
        rd = x / "README.md"
        titulo = x.name
        quando = ""
        n = 0
        if rd.is_file():
            t = rd.read_text(encoding="utf-8")
            titulo = t.splitlines()[0].lstrip("# ").strip()
            m = re.search(r"^\*\*Quando:\*\*\s*(.+?)\s*$", t, re.M)
            quando = m.group(1) if m else ""
            n = len(re.findall(r"^- \*\*", t.split(MARCA.format("acontecimentos"))[-1], re.M))
        linhas.append(f"- [{titulo}](historico/{x.name}/) — {quando}"
                      + (f" · {n} acontecimento(s)" if n else ""))
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
    print(f"Capítulo atual: {pasta.name}")
    print(f"  {pasta}")


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
    s.add_argument("--evento", required=True, help="Número (1) ou nome da pasta")
    s.add_argument("--texto", required=True)
    s.set_defaults(func=cmd_acontecimento)

    s = sub.add_parser("atual", help="Marca em que capítulo a mesa está")
    s.add_argument("--capitulo", required=True, help="Número do capítulo (ex.: 3)")
    s.set_defaults(func=cmd_atual)

    s = sub.add_parser("indexar", help="Regera o índice do README")
    s.set_defaults(func=cmd_indexar)

    s = sub.add_parser("encerrar", help="Arquiva em historico/campanhas/")
    s.add_argument("--desfecho", default="")
    s.set_defaults(func=cmd_encerrar)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
