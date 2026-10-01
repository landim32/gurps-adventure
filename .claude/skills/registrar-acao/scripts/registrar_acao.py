#!/usr/bin/env python3
"""Registra o que uma acao resolvida mudou no mundo.

Unica skill autorizada a escrever em disco depois de rolar dado: acontecimento do
capitulo, anotacoes de NPC/grupo/lugar, dinheiro na bolsa, corpo em saude, e o plano das
chamadas ao roll6 (que o MCP executa, nao este script).

  python registrar_acao.py --ato .qwen/tmp/ato.json
  python .../acao.py ... --json | python registrar_acao.py --stdin
  python registrar_acao.py --ato ato.json --dry-run
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
CAMPANHA = RAIZ / ".claude" / "skills" / "campanha" / "scripts" / "campanha.py"

# o campana.py escreve acento no nome do NPC e no motivo; sem isto o pipe estoura na
# codepage do console. PYTHONIOENCODING obliga UTF-8 dos dois lados.
AMBIENTE = {**os.environ, "PYTHONIOENCODING": "utf-8"}

# um so alvo por lancamento: quem: {"tipo": "pj"|"npc"|"coisa", "nome": "..."}
ALVO = {"pj": "--pj", "npc": "--npc", "coisa": "--coisa"}


def carregar_ato(args):
    if args.ato:
        bruto = Path(args.ato).read_text(encoding="utf-8")
    elif args.stdin or not sys.stdin.isatty():
        bruto = sys.stdin.read()
    else:
        raise SystemExit("Diga de onde vem o ato: --ato arquivo.json ou --stdin.")
    if not bruto.strip():
        raise SystemExit("O ato chegou vazio.")
    try:
        return json.loads(bruto)
    except json.JSONDecodeError as erro:
        raise SystemExit(f"O ato nao e JSON valido: {erro}")


def validar(ato):
    """Confere o essencial. Com erro, nada e escrito: devolve-se o ato para a origem."""
    problemas = []
    # so reacao nao gera acontecimento: o resultado e segredo do Mestre e o cache basta
    if not str(ato.get("resumo", "")).strip() and not ato.get("reacoes"):
        problemas.append("falta `resumo` - sem ele nao ha acontecimento a registrar")

    for campo in ("anotacoes", "dinheiro", "corpo"):
        for i, item in enumerate(ato.get(campo) or []):
            if item.get("tipo") not in ALVO:
                problemas.append(f"{campo}[{i}]: tipo {item.get('tipo')!r} nao e pj, npc nem coisa")
            if not str(item.get("nome", "")).strip():
                problemas.append(f"{campo}[{i}]: falta `nome` de quem mudou")
            if campo == "anotacoes" and not str(item.get("texto", "")).strip():
                problemas.append(f"anotacoes[{i}]: texto vazio")
            if campo == "dinheiro" and not isinstance(item.get("valor"), (int, float)):
                problemas.append(f"dinheiro[{i}]: `valor` precisa ser numero com sinal")
            if campo == "corpo" and not any(
                item.get(chave) not in (None, "", 0)
                for chave in ("pv", "fadiga", "estado", "curar")
            ):
                problemas.append(
                    f"corpo[{i}]: sem pv, fadiga, estado ou curar nao ha o que lancar"
                )
    return problemas


def nome_de(ato):
    return str((ato.get("quem") or {}).get("nome", "")).strip()


def cmd_acontecimento(texto, ato):
    c = [sys.executable, str(CAMPANHA), "acontecimento", "--texto", texto.strip()]
    if ato.get("capitulo"):
        c += ["--evento", str(ato["capitulo"])]
    return c


def lancamentos(ato):
    """A fila de comandos, na ordem em que devem rodar: log, anotacoes, narracao,
    bolsa, saude. As tres ultimas reescrevem tabelas geradas, vao por ultimo."""
    if str(ato.get("resumo", "")).strip():
        yield "acontecimento", cmd_acontecimento(ato["resumo"], ato)

    for a in ato.get("anotacoes") or []:
        c = [sys.executable, str(CAMPANHA), "anotar", ALVO[a["tipo"]], a["nome"]]
        if a.get("tag"):
            c += ["--tag", a["tag"]]
        if ato.get("capitulo"):
            c += ["--evento", str(ato["capitulo"])]
        yield "anotar", c + ["--texto", a["texto"].strip()]

    # narracao de rodada/cena: aqui ela e log do capitulo, como sempre foi na mesa -
    # anotar exige um sujeito (--npc/--pj/--coisa), e a rodada nao e de ninguem
    narracao = str((ato.get("narracao") or {}).get("texto", "")).strip()
    if narracao:
        yield "narracao", cmd_acontecimento("[narração] " + narracao, ato)

    for d in ato.get("dinheiro") or []:
        c = [sys.executable, str(CAMPANHA), "bolsa", ALVO[d["tipo"]], d["nome"],
             "--valor", f"{int(d['valor']):+d}"]
        if d.get("motivo"):
            c += ["--motivo", d["motivo"]]
        yield "bolsa", c

    for b in ato.get("corpo") or []:
        c = [sys.executable, str(CAMPANHA), "saude", ALVO[b["tipo"]], b["nome"]]
        for flag in ("pv", "fadiga"):
            if b.get(flag):
                c += [f"--{flag}", f"{int(b[flag]):+d}"]
        for flag in ("estado", "curar", "motivo"):
            if str(b.get(flag) or "").strip():
                c += [f"--{flag}", str(b[flag]).strip()]
        yield "saude", c


def executar(comando, seco):
    mostra = " ".join(f'"{p}"' if " " in str(p) else str(p) for p in comando)
    if seco:
        return True, "(dry-run) " + mostra
    r = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=AMBIENTE)
    saida = (r.stdout or "").strip().splitlines()
    if r.returncode != 0:
        detalhe = (r.stderr or r.stdout or "").strip().replace("\n", "\n    ")
        return False, mostra + "\n    " + detalhe
    return True, (saida[0] if saida else "ok")


def avisos(ato):
    """O que veio torto. Registrar um lado so e como plantar contradicao de capitulo."""
    out = []
    dinheiro = ato.get("dinheiro") or []
    if dinheiro:
        saldo = sum(int(d["valor"]) for d in dinheiro)
        if saldo:
            out.append(
                f"dinheiro desequilibrado em {saldo:+d}: alguem ganhou sem alguem perder. "
                "Se nao foi doacao nem achado, falta lancar o outro lado."
            )
    itens = [a for a in (ato.get("anotacoes") or []) if a.get("tag") == "item"]
    if len(itens) == 1:
        out.append(
            "uma anotacao de item e um lado so: quem passou e quem recebeu sao duas linhas. "
            "Anotada uma sem a outra, e ai que as versoes divergem."
        )
    if not (ato.get("corpo") or []):
        for jogada in ato.get("jogadas") or []:
            if "dano" in str(jogada.get("titulo", "")).lower():
                out.append("saiu dano de uma jogada e nao veio lancamento em `corpo`.")
                break
    return out


def bloco_mesa(ato):
    linhas = []
    narracao = str((ato.get("narracao") or {}).get("texto", "")).strip()
    if narracao:
        linhas.append(narracao)
    if str(ato.get("resumo", "")).strip():
        linhas.append(ato["resumo"].strip())
    for jogada in ato.get("jogadas") or []:
        linha = str(jogada.get("linha", "")).strip()
        if linha:
            linhas.append(f"> {linha}")
    return "\n".join(linhas)


def plano_roll6(ato):
    r = ato.get("roll6") or {}
    chamadas = []
    turno = r.get("turno")
    if turno:
        chamadas.append(
            "um único process_turn(campanhaId=%s) fecha o turno com %d personagem(ns) e a "
            "narração; dentro de turno do roll6 não se escreve peça por peça"
            % (turno.get("campanhaId", "?"), len(turno.get("personagens") or []))
        )
    for p in r.get("participations") or []:
        chamadas.append(
            f"get_participation(campaignCharacterId={p.get('campanhaCharacterId', '?')}) e, "
            "na volta, update_participation com currentLife/currentEnergy/characterStatus e "
            "**o mesmo `sheet` que veio** - omitir o sheet apaga a ficha da campanha"
        )
    for n in r.get("npcs") or []:
        chamadas.append(
            "update_map_npc(mapNpcId=%s, currentLife=%s, currentEnergy=%s, characterStatus=%r)"
            % (n.get("mapNpcId", "?"), n.get("currentLife", "manter"),
               n.get("currentEnergy", "manter"), str(n.get("characterStatus", ""))[:60])
        )
    if r.get("reacao"):
        chamadas.append("reacao fica FORA do roll6: o reacoes.json e segredo do Mestre.")
    return chamadas


def reacoes_de(ato, raiz):
    """Escreve o cache secreto das reacoes no reacoes.json do capitulo atual.

    Unico arquivo de estado que a registradora mantem fora das tabelas do campana.py, e por
    decisao: a reacao e do Mestre, nao do mundo narrado - nao vai para o bloco da mesa nem
    para o roll6. Sem capitulo atual, recusa: o cache antigo caia em campana/reacoes.json
    e la ninguem mais lia.
    """
    entradas = ato.get("reacoes") or []
    if not entradas:
        return None
    est = estado_da_campanha(raiz)
    pasta = est.get("capitulo_atual_pasta")
    if not pasta:
        return ("sem-capitulo", "reacoes: sem capitulo atual, cache nao escrito "
                                "(campanha.py atual --capitulo N)")
    return Path(pasta) / "reacoes.json", entradas


def mescla_reacoes(caminho, entradas, local=""):
    """Fusiona por (pj, npc): a rolagem mais nova substitui a anterior."""
    dados = {"reacoes": []}
    if caminho.is_file():
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        except Exception:
            pass
    existentes = dados.get("reacoes") or []
    chave = lambda r: ((r.get("pj") or "").casefold(), (r.get("npc") or "").casefold())
    marcadas = {chave(e) for e in entradas}
    fundidas = [e for e in existentes if chave(e) not in marcadas] + list(entradas)
    dados["reacoes"] = fundidas
    if local:
        dados["local"] = local
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    return len(entradas), len(fundidas)


def estado_da_campanha(raiz):
    """Pede o estado ao contexto - a folha dona desta leitura, nao mais copia propia."""
    ctx = RAIZ / ".claude" / "skills" / "contexto" / "scripts" / "contexto.py"
    if ctx.is_file():
        try:
            spec = importlib.util.spec_from_file_location("contexto", ctx)
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)
            return modulo.estado(raiz)
        except Exception:
            pass
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(CAMPANHA), "--raiz", str(raiz),
                        "estado", "--json"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    try:
        return json.loads(r.stdout) if r.returncode == 0 else {"ativa": False}
    except Exception:
        return {"ativa": False}


def main():
    ap = argparse.ArgumentParser(description="Registra o resultado de uma acao resolvida.")
    ap.add_argument("--ato", help="arquivo JSON com o ato resolvido")
    ap.add_argument("--stdin", action="store_true", help="le o JSON do stdin")
    ap.add_argument("--dry-run", action="store_true", help="mostra os comandos, nao escreve")
    args = ap.parse_args()

    # o bloco da mesa devolve acento para o terminal e para arquivo redirecionado; na
    # codepage do console isso derruba o print no meio da fila de lançamentos
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ato = carregar_ato(args)
    problemas = validar(ato)
    if problemas:
        print("O ato nao pode ser registrado:")
        for p in problemas:
            print(f"  - {p}")
        print("\nDevolva para quem montou o ato: esta skill confere numero, nao inventa fato.")
        return 2

    quem = nome_de(ato)
    print(f"## Registrar - {quem or 'sem autor'}"
          + (f" (cap. {ato['capitulo']})" if ato.get("capitulo") else ""))

    falhas = 0
    for rotulo, comando in lancamentos(ato):
        ok, msg = executar(comando, args.dry_run)
        print(f"[{'ok ' if ok else 'ERRO'}] {rotulo}: {msg}")
        falhas += 0 if ok else 1

    resto = avisos(ato)
    cache = reacoes_de(ato, RAIZ)
    if cache:
        if cache[0] == "sem-capitulo":
            print(f"[aviso] {cache[1]}")
        else:
            caminho, entradas = cache
            if args.dry_run:
                print(f"[dry-run] reacoes: {len(entradas)} entrada(s) em {caminho.name}")
            else:
                novas, total = mescla_reacoes(caminho, entradas, str(ato.get("local", "")))
                print(f"[ok ] reacoes: {novas} entrada(s) nova(s) em {caminho.name} "
                      f"({total} no cache, fusao por pj+npc)")
    if resto:
        print("\n### Avisos")
        for v in resto:
            print(f"- {v}")

    plano = plano_roll6(ato)
    if plano:
        print("\n### Plano do roll6 (executa pelo MCP, nesta ordem)")
        for c in plano:
            print(f"- {c}")

    bloco = bloco_mesa(ato)
    if bloco.strip():
        print("\n### Bloco da mesa")
        print("```")
        print(bloco)
        print("```")
    elif ato.get("reacoes"):
        # só reação no ato: não há o que ler na mesa. Faixa, número e motivo ficam com o
        # Mestre — e imprimir um bloco vazio aqui só convidaria alguém a colar nada.
        print("\n### Bloco da mesa")
        print("(vazio por decisão: reação rolada não vai para o log da mesa nem ao roll6.)")
    if args.dry_run:
        print("\n(dry-run: nada foi escrito)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
