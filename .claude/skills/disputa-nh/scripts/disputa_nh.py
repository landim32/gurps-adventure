#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Disputa de Habilidades de GURPS 3ed — MB, cap. 12.

    disputa_nh.py --a "Comam" --a-pericia "Furtividade" \
                  --b "Guarda do portao" --b-nh 12 --b-oque "Audicao"

Os dois lados rolam. Ganha quem passou pela maior margem, ou falhou pela menor; margem
igual e empate, e ninguem venceu.

Quem acha o NH e a skill `teste-nh`; quem rola o dado e a skill `roll`. Aqui so se compara.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

CAMPANHA_PY = Path(".claude/skills/gerenciar-campanha/scripts/campanha.py")
SKILLS = Path(__file__).resolve().parents[2]


def _carrega(nome, caminho):
    try:
        spec = importlib.util.spec_from_file_location(nome, caminho)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as erro:
        raise SystemExit(f"Não consegui carregar a skill {nome} ({caminho}): {erro}")


# A regra de achar NH mora na teste-nh; a de sortear dado, na roll. Nada disso e copiado.
tn = _carrega("teste_nh", SKILLS / "teste-nh" / "scripts" / "teste_nh.py")
_roll = _carrega("roll", SKILLS / "roll" / "scripts" / "roll.py")

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass


def monta_lado(pref, args, raiz):
    """Descobre o NH de um lado: da ficha, do pre-definido do livro, ou na mao."""
    def op(sufixo):
        return getattr(args, f"{pref}_{sufixo}") if sufixo else getattr(args, pref)

    nome, notas, avisos = op(""), [], []
    if not nome:
        raise SystemExit(f"Falta --{pref}: o nome de quem disputa.")

    nh_na_mao, pericia = op("nh"), op("pericia")
    atributo, rotulo = op("atributo"), op("oque")
    d = tn.ler_ficha(nome, raiz)
    quem = (d or {}).get("nome", nome)
    atrib = {k: v.get("valor") for k, v in ((d or {}).get("atributos") or {}).items()}

    if nh_na_mao:
        nh = nh_na_mao
        rotulo = rotulo or "habilidade"
        if not d:
            notas.append("NH informado pelo Mestre (sem ficha no repositório)")
    elif not d:
        raise SystemExit(f"Sem ficha para «{nome}». Passe --{pref}-nh e --{pref}-oque.")
    elif atributo:
        a = atributo.upper()
        nh, rotulo = int(atrib.get(a, 0)), a
    elif pericia:
        achou = tn.acha_pericia(d, pericia)
        if achou:
            nh, rotulo = achou
        else:
            entrada = tn.busca_no_livro(pericia, raiz)
            if not entrada:
                raise SystemExit(f"«{quem}» não tem «{pericia}» e não achei a perícia no "
                                 f"livro. Confira o nome ou passe --{pref}-nh.")
            calc, erro = tn.calcula_predefinido(entrada, atrib)
            if not calc:
                raise SystemExit(f"«{quem}» não tem {entrada['nome']} e {erro}.")
            nh, origem = calc
            rotulo = f"{entrada['nome']} (sem treino)"
            avisos.append(f"{quem} NÃO tem {entrada['nome']} ({entrada['tipo']}). "
                          f"Usando o pré-definido **{origem}** = {nh}.")
            if entrada["modificadores"]:
                notas.append(f"Modificadores do livro: {entrada['modificadores']}")
    else:
        raise SystemExit(f"Diga o que {nome} está usando: --{pref}-pericia, "
                         f"--{pref}-atributo ou --{pref}-nh.")

    mod = op("mod")
    tem_sorte = bool(d) and tn.nivel_vantagem(d, "sorte") is not None
    return {"nome": quem, "rotulo": rotulo, "nh": nh, "mod": mod, "efetivo": nh + mod,
            "notas": notas, "avisos": avisos, "sorte": op("sorte"),
            "tem_sorte": tem_sorte}


def rola(lado, efetivo):
    """Uma jogada do lado. Devolve (total, dados, margem, resultado, jogadas)."""
    jogadas = [(sum(x), x) for x in (_roll.d6(3) for _ in range(3 if lado["sorte"] else 1))]
    total, dados = min(jogadas, key=lambda j: j[0])
    return total, dados, efetivo - total, tn.classificar(total, efetivo), jogadas


def encurta(a, b):
    """MB: disputa longa entre NH altos — baixa o maior para 14 e tira o mesmo do outro."""
    maior = max(a, b)
    if maior <= 14:
        return a, b, 0
    dif = maior - 14
    return a - dif, b - dif, dif


def registrar(raiz, texto):
    script = raiz / CAMPANHA_PY
    if not script.is_file():
        return False, "gerenciar-campanha não encontrada"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(script), "--raiz", str(raiz),
                        "acontecimento", "--texto", texto], capture_output=True,
                       text=True, encoding="utf-8", timeout=30, env=env)
    return r.returncode == 0, (r.stdout or r.stderr).strip()


def linha_lado(lado, efetivo, total, dados, margem, resultado):
    """Duas linhas por lado — no celular isso se le melhor que uma linha comprida."""
    veredito = {
        "sucesso decisivo": f"_SUCESSO DECISIVO, por {margem}_",
        "falha crítica": f"_FALHA CRÍTICA, por {abs(margem)}_",
        "sucesso": f"_passou por {margem}_",
        "falha": f"_falhou por {abs(margem)}_",
    }[resultado]
    return [f"*{lado['nome']}* — {lado['rotulo']}, precisa tirar {efetivo} ou menos",
            f"3d: {' + '.join(map(str, dados))} = *{total}* → {veredito}"]


def main():
    ap = argparse.ArgumentParser(description="Disputa de Habilidades de GURPS 3ed.")
    ap.add_argument("--raiz", default=".")
    for p in ("a", "b"):
        ap.add_argument(f"--{p}", default="", help=f"Nome do lado {p.upper()}")
        ap.add_argument(f"--{p}-pericia", default="", help="Perícia ou mágica")
        ap.add_argument(f"--{p}-atributo", default="",
                        choices=["", "ST", "DX", "IQ", "HT", "st", "dx", "iq", "ht"])
        ap.add_argument(f"--{p}-nh", type=int, default=0, help="NH na mão (NPC virtual)")
        ap.add_argument(f"--{p}-oque", default="", help="Rótulo, quando se passa o NH")
        ap.add_argument(f"--{p}-mod", type=int, default=0, help="Bônus/redutor da situação")
        ap.add_argument(f"--{p}-sorte", action="store_true", help="Vantagem Sorte")
    ap.add_argument("--tipo", default="rapida", choices=["rapida", "normal"],
                    help="rapida: um lance decide. normal: repete até alguém se destacar")
    ap.add_argument("--rodadas", type=int, default=10, help="Teto de rodadas na normal")
    ap.add_argument("--sem-encurtar", action="store_true",
                    help="Não aplica a redução para NH acima de 14 na disputa normal")
    ap.add_argument("--gravar", action="store_true", help="Registra no capítulo atual")
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()
    A, B = monta_lado("a", args, raiz), monta_lado("b", args, raiz)

    ef_a, ef_b, dif = A["efetivo"], B["efetivo"], 0
    if args.tipo == "normal" and not args.sem_encurtar:
        ef_a, ef_b, dif = encurta(ef_a, ef_b)

    print("=" * 66)
    print(f"DISPUTA DE HABILIDADES ({'rápida' if args.tipo == 'rapida' else 'normal'})")
    for lado, ef in ((A, ef_a), (B, ef_b)):
        cabeca = f"  {lado['nome']} — {lado['rotulo']}: NH {lado['nh']}"
        if lado["mod"]:
            cabeca += f" {'+' if lado['mod'] > 0 else '-'} {abs(lado['mod'])}"
        cabeca += f" = **{lado['efetivo']}**"
        if dif:
            cabeca += f" → **{ef}** (encurtado)"
        print(cabeca)
        for n in lado["notas"]:
            print(f"      {n}")
    if dif:
        print(f"  NH altos dos dois lados: o livro manda baixar o maior para 14 e tirar "
              f"os mesmos {dif} do outro, para a disputa não durar para sempre.")
    print("=" * 66)

    rodadas, vencedor, empate = [], None, False
    for i in range(1, (args.rodadas if args.tipo == "normal" else 1) + 1):
        ta, da, ma, ra, ja = rola(A, ef_a)
        tb, db, mb, rb, jb = rola(B, ef_b)
        rodadas.append((i, (ta, da, ma, ra, ja), (tb, db, mb, rb, jb)))

        if args.tipo == "rapida":
            if ma > mb:
                vencedor = A
            elif mb > ma:
                vencedor = B
            else:
                empate = True
            break
        # normal: so decide quando um passa e o outro falha
        if (ma >= 0) != (mb >= 0):
            vencedor = A if ma >= 0 else B
            break

    for i, (ta, da, ma, ra, ja), (tb, db, mb, rb, jb) in rodadas:
        if args.tipo == "normal":
            print(f"\nRodada {i}")
        for lado, t, d, m, r, j in ((A, ta, da, ma, ra, ja), (B, tb, db, mb, rb, jb)):
            extra = ("  [Sorte: " + ", ".join(str(x[0]) for x in j) + "]") if lado["sorte"] else ""
            print(f"  {lado['nome']}: 3d [{', '.join(map(str, d))}] = {t} — {r}, "
                  f"margem {m:+d}{extra}")

    print()
    if empate:
        print("EMPATE — ninguém venceu. Os dois agarraram a arma ao mesmo tempo.")
    elif vencedor:
        perdedor = B if vencedor is A else A
        quantas = (f", em {len(rodadas)} rodada{'s' if len(rodadas) > 1 else ''}."
                   if args.tipo == "normal" else ".")
        print(f"**{vencedor['nome']} vence a disputa** contra {perdedor['nome']}{quantas}")
    else:
        print(f"Sem decisão em {args.rodadas} rodadas — os dois passaram ou os dois "
              f"falharam todas as vezes. Na disputa normal isso significa que nada mudou "
              f"de posição; continue com --rodadas maior, ou resolva na narrativa.")

    for lado in (A, B):
        for a in lado["avisos"]:
            print(f"\n{a}")
        if lado["tem_sorte"] and not lado["sorte"]:
            print(f"\n{lado['nome']} tem **Sorte** e não usou: --{'a' if lado is A else 'b'}"
                  f"-sorte rola 3 vezes e fica com o melhor (uma vez por hora de jogo).")

    # ---- bloco para o WhatsApp ----
    ult = rodadas[-1]
    w = [f"*{A['nome']}* × *{B['nome']}* — disputa de habilidades", ""]
    if args.tipo == "normal" and len(rodadas) > 1:
        w.append(f"_Decidido na rodada {ult[0]} de {len(rodadas)}._")
    w += linha_lado(A, ef_a, *ult[1][:4]) + [""] + linha_lado(B, ef_b, *ult[2][:4]) + [""]
    if empate:
        w.append("*Empate — ninguém levou a melhor.*")
    elif vencedor:
        w.append(f"*{vencedor['nome']} vence.*")
    else:
        w.append("*Ninguém se destacou — a situação continua como estava.*")

    risco = "-" * 66
    print("\n" + risco)
    print("PARA O WHATSAPP (copie o bloco abaixo):")
    print(risco)
    print("\n".join(w))
    print(risco)

    if args.gravar:
        desfecho = ("empate" if empate else
                    f"{vencedor['nome']} venceu" if vencedor else "sem decisão")
        ok, msg = registrar(raiz, f"Disputa {A['rotulo']} de {A['nome']} contra "
                                  f"{B['rotulo']} de {B['nome']}: {desfecho}.")
        print("\nRegistrado no capítulo atual." if ok else f"\nAVISO: não gravei — {msg}")


if __name__ == "__main__":
    main()
