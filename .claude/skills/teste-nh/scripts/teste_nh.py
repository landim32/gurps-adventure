#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de habilidade de GURPS 3ed — MB, cap. 12 ("Testes de Habilidade").

    teste_nh.py --quem "Comam" --pericia "Furtividade" --mod -3
    teste_nh.py --quem "Jah Kagadu" --atributo DX --mod +2
    teste_nh.py --quem "Kaelric" --vontade --mod -2
    teste_nh.py --quem "Jah" --sentido visao
    teste_nh.py --quem "Morto-Vivo 1" --nh 12 --oque "Briga"     # NPC sem ficha

Acha o NH na ficha; nao tendo a pericia, busca o nivel pre-definido em
livros/gurps-mb-3ed/06-pericias.md e avisa. Os dados sao rolados pela skill `roll`.
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

CAMPANHA_PY = Path(".claude/skills/gerenciar-campanha/scripts/campanha.py")
LIVRO_PERICIAS = Path("livros/gurps-mb-3ed/06-pericias.md")

# Quem rola dado neste repositorio e a skill `roll`, uma so.
ROLL_PY = Path(__file__).resolve().parents[2] / "roll" / "scripts" / "roll.py"
try:
    _spec = importlib.util.spec_from_file_location("roll", ROLL_PY)
    _roll = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_roll)
except Exception as erro:
    raise SystemExit(f"Não consegui carregar a skill roll ({ROLL_PY}): {erro}")

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

ATRIBUTOS = ("ST", "DX", "IQ", "HT")
# Regra geral do pre-definido quando a entrada do livro nao traz a linha (MB, cap. 7)
POR_DIFICULDADE = {"f": 4, "m": 5, "d": 6}


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")


def classificar(total, nh):
    """Sucesso decisivo e falha critica — MB, cap. 12."""
    if total <= 4:
        return "sucesso decisivo"
    if total == 5 and nh >= 15:
        return "sucesso decisivo"
    if total == 6 and nh >= 16:
        return "sucesso decisivo"
    if total == 18:
        return "falha crítica"
    if total == 17:
        return "falha crítica" if nh < 16 else "falha"
    if total >= nh + 10:
        return "falha crítica"
    return "sucesso" if total <= nh else "falha"


def ler_ficha(nome, raiz):
    """Aceita nome parcial: 'Comam' acha comam-obabaroy, 'Kaelric' acha irmao-kaelric."""
    base = raiz / "personagens"
    if not base.is_dir():
        return None
    alvo = slug(nome)
    achado = None
    for f in sorted(base.glob("*/personagem.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for s in (slug(f.parent.name), slug(d.get("nome", ""))):
            peso = 0 if s == alvo else (1 if s.startswith(alvo) else
                                        (2 if alvo in s.split("-") or alvo in s else None))
            if peso is not None and (achado is None or peso < achado[0]):
                achado = (peso, d)
    return achado[1] if achado else None


def acha_pericia(d, nome):
    """Melhor NH entre pericias e magias cujo nome case com o pedido."""
    alvo = slug(nome)
    melhor = None
    for p in (d.get("pericias") or []) + (d.get("magias") or []):
        s = slug(p.get("nome", ""))
        if s == alvo or s.startswith(alvo) or alvo in s:
            nh = int(p.get("nh") or 0)
            if melhor is None or nh > melhor[0]:
                melhor = (nh, p.get("nome"))
    return melhor


def nivel_vantagem(d, prefixo):
    """'Prontidão +2' -> 2. 'Sorte' -> 0 (existe, sem nivel)."""
    alvo = slug(prefixo)
    for v in d.get("vantagens_desvantagens") or []:
        nome = v.get("nome", "")
        if slug(nome).startswith(alvo):
            m = re.search(r"([+-]?\d+)\s*$", nome.strip())
            return int(m.group(1)) if m else 0
    return None


def busca_no_livro(nome, raiz):
    """Entrada da pericia no MB: dificuldade, pre-definido e a linha de Modificadores."""
    livro = raiz / LIVRO_PERICIAS
    if not livro.is_file():
        return None
    texto = livro.read_text(encoding="utf-8")
    blocos = re.split(r"^### ", texto, flags=re.M)[1:]
    alvo = slug(nome)
    achado = None
    for b in blocos:
        cab = b.splitlines()[0]
        m = re.match(r"^(.+?)\s*\((.+?)\)\s*$", cab)
        if not m:
            continue
        s = slug(m.group(1))
        peso = 0 if s == alvo else (1 if s.startswith(alvo) else (2 if alvo in s else None))
        if peso is None:
            continue
        if achado is None or peso < achado[0]:
            achado = (peso, m.group(1).strip(), m.group(2).strip(), b)
        if peso == 0:
            break
    if not achado:
        return None
    _, nome_livro, tipo, bloco = achado
    m = re.search(r"^\*\*Pré-definido:\*\*\s*(.+?)\s*$", bloco, re.M)
    mods = re.search(r"Modificadores:\s*(.+?)(?:\n|$)", bloco)
    return {"nome": nome_livro, "tipo": tipo,
            "predefinido": m.group(1) if m else "",
            "modificadores": mods.group(1).strip() if mods else ""}


def calcula_predefinido(entrada, atrib):
    """Melhor nivel pre-definido a partir dos atributos. Atributo conta no maximo 20."""
    txt = entrada["predefinido"]
    opcoes = []
    for a, menos in re.findall(r"\b(ST|DX|IQ|HT)\s*-\s*(\d+)", txt):
        base = min(int(atrib.get(a, 0)), 20)      # MB, cap. 12: atributo conta no maximo 20 no pre-definido
        opcoes.append((base - int(menos), f"{a}-{menos}"))
    if opcoes:
        return max(opcoes), None
    if re.search(r"nenhum|sem n[íi]vel|não tem|nao tem", txt, re.I):
        return None, (f"o livro diz «{txt}»: sem treino não dá para tentar, "
                      f"por mais esperto ou ágil que o personagem seja")
    if txt:
        return None, f"pré-definido «{txt}» depende de outra perícia; passe --nh na mão"
    # sem a linha no livro: regra geral por dificuldade (MB, cap. 7)
    m = re.search(r"(Física|Mental)\s*/\s*(\w+)", entrada["tipo"], re.I)
    if m:
        base_attr = "DX" if m.group(1).lower().startswith("f") else "IQ"
        menos = POR_DIFICULDADE.get(slug(m.group(2))[0])
        if menos:
            base = min(int(atrib.get(base_attr, 0)), 20)
            return (base - menos, f"{base_attr}-{menos} (regra geral)"), None
    return None, "não achei o pré-definido; passe --nh na mão"


def registrar(raiz, texto):
    script = raiz / CAMPANHA_PY
    if not script.is_file():
        return False, "gerenciar-campanha não encontrada"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(script), "--raiz", str(raiz),
                        "acontecimento", "--texto", texto], capture_output=True,
                       text=True, encoding="utf-8", timeout=30, env=env)
    return r.returncode == 0, (r.stdout or r.stderr).strip()


def main():
    ap = argparse.ArgumentParser(description="Teste de habilidade de GURPS 3ed.")
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--quem", required=True, help="Personagem ou NPC")
    ap.add_argument("--pericia", default="", help="Nome da perícia ou mágica")
    ap.add_argument("--atributo", default="", choices=["", *ATRIBUTOS, *[a.lower() for a in ATRIBUTOS]])
    ap.add_argument("--vontade", action="store_true", help="Teste de Vontade (IQ ± Vontade)")
    ap.add_argument("--sentido", default="", choices=["", "visao", "audicao", "olfato"])
    ap.add_argument("--nh", type=int, default=0, help="NH na mão (NPC sem ficha)")
    ap.add_argument("--oque", default="", help="Rótulo do teste, quando se passa --nh")
    ap.add_argument("--mod", type=int, default=0, help="Bônus ou redutor da situação")
    ap.add_argument("--tentativa", type=int, default=1,
                    help="2ª tentativa = -1, 3ª = -2... (MB, tentativas repetidas)")
    ap.add_argument("--sorte", action="store_true",
                    help="Vantagem Sorte: rola 3 vezes e fica com o melhor")
    ap.add_argument("--defesa", action="store_true",
                    help="É jogada de defesa ativa: vale mesmo com NH efetivo ≤ 3")
    ap.add_argument("--gravar", action="store_true", help="Registra no capítulo atual")
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()
    d = ler_ficha(args.quem, raiz)
    quem = (d or {}).get("nome", args.quem)
    atrib = {k: v.get("valor") for k, v in ((d or {}).get("atributos") or {}).items()}

    nh, rotulo, notas, avisos = args.nh, args.oque, [], []

    # ---- de onde sai o NH ----
    if args.nh:
        rotulo = rotulo or "teste"
    elif not d:
        raise SystemExit(f"Sem ficha para «{args.quem}». Passe --nh e --oque "
                         f"(NPC não tem personagem.json; a ficha dele está no npcs.md).")
    elif args.vontade:
        iq = int(atrib.get("IQ", 0))
        forca = nivel_vantagem(d, "forca-de-vontade") or 0
        fraca = nivel_vantagem(d, "vontade-fraca") or 0
        base = min(iq, 14) if fraca else iq      # MB: teto de 14 ao subtrair Vontade Fraca
        nh = base + forca - fraca
        rotulo = "Vontade"
        notas.append(f"Vontade = IQ {iq}" + (f" +{forca} Força de Vontade" if forca else "")
                     + (f" -{fraca} Vontade Fraca (IQ conta no máximo 14)" if fraca else ""))
        avisos.append("Em teste de Vontade, **qualquer resultado 14 ou mais é falha**.")
    elif args.sentido:
        iq = int(atrib.get("IQ", 0))
        pront = nivel_vantagem(d, "prontidao") or 0
        agucado = {"visao": "visao-agucada", "audicao": "ouvido-agucado",
                   "olfato": "olfato"}[args.sentido]
        agudo = nivel_vantagem(d, agucado) or 0
        nh = iq + pront + agudo
        rotulo = "Teste de " + {"visao": "Visão", "audicao": "Audição",
                                "olfato": "Olfato/Paladar"}[args.sentido]
        notas.append(f"Sentido = IQ {iq}" + (f" +{pront} Prontidão" if pront else "")
                     + (f" +{agudo} sentido aguçado" if agudo else ""))
    elif args.atributo:
        a = args.atributo.upper()
        nh, rotulo = int(atrib.get(a, 0)), a
    elif args.pericia:
        achou = acha_pericia(d, args.pericia)
        if achou:
            nh, rotulo = achou
        else:
            entrada = busca_no_livro(args.pericia, raiz)
            if not entrada:
                raise SystemExit(f"«{args.quem}» não tem «{args.pericia}» e não achei a "
                                 f"perícia no livro. Confira o nome ou passe --nh.")
            calc, erro = calcula_predefinido(entrada, atrib)
            if not calc:
                raise SystemExit(f"«{quem}» não tem {entrada['nome']} e {erro}.")
            nh, origem = calc
            rotulo = f"{entrada['nome']} (sem treino)"
            avisos.append(f"{quem} NÃO tem {entrada['nome']} ({entrada['tipo']}). "
                          f"Usando o nível pré-definido **{origem}** = {nh}.")
            if entrada["modificadores"]:
                notas.append(f"Modificadores do livro: {entrada['modificadores']}")
    else:
        raise SystemExit("Diga o que testar: --pericia, --atributo, --vontade, "
                         "--sentido ou --nh.")

    # ---- modificadores ----
    mod, detalhe = args.mod, []
    if args.mod:
        detalhe.append(f"{args.mod:+d} situação")
    if args.tentativa > 1:
        p = args.tentativa - 1
        mod -= p
        detalhe.append(f"-{p} {args.tentativa}ª tentativa")
    efetivo = nh + mod

    if efetivo <= 3 and not args.defesa:
        print(f"{quem} — {rotulo}: NH {nh} {mod:+d} = {efetivo}")
        raise SystemExit("NH efetivo 3 ou menos: o livro não permite a jogada "
                         "(MB, cap. 12), salvo em defesa ativa. Use --defesa se for o caso.")

    # ---- rolagem ----
    tem_sorte = d and nivel_vantagem(d, "sorte") is not None
    vezes = 3 if args.sorte else 1
    if args.sorte and not tem_sorte:
        avisos.append(f"ATENÇÃO: {quem} não tem a vantagem Sorte na ficha.")

    jogadas = []
    for _ in range(vezes):
        dados = _roll.d6(3)
        jogadas.append((sum(dados), dados))
    total, dados = min(jogadas, key=lambda j: j[0])    # melhor = menor
    resultado = classificar(total, efetivo)
    margem = efetivo - total

    # ---- saida ----
    print("=" * 62)
    print(f"{quem} — {rotulo}")
    for n in notas:
        print(f"  {n}")
    print(f"  NH {nh}" + (f" {'+' if mod > 0 else '-'} {abs(mod)} = **{efetivo}**"
                          if mod else f" = **{efetivo}**"))
    if detalhe:
        print(f"  ({'; '.join(detalhe)})")
    if args.sorte:
        print("  Sorte: " + ", ".join(str(j[0]) for j in jogadas) + " — vale o melhor")
    print(f"  3d [{', '.join(map(str, dados))}] = {total}")
    print("=" * 62)

    frase = {
        "sucesso decisivo": f"SUCESSO DECISIVO! Tirou {total} com um NH de {efetivo}.",
        "sucesso": f"Sucesso, tirou {total} com um NH de {efetivo}.",
        "falha": f"Falha, tirou {total} com um NH de {efetivo}.",
        "falha crítica": f"FALHA CRÍTICA! Tirou {total} com um NH de {efetivo}.",
    }[resultado]
    print(frase + f"  (margem {margem:+d})")

    if resultado == "sucesso decisivo":
        print("  Num ataque isto é um Golpe Fulminante: use a Tabela de Golpes "
              "Fulminantes (MB, pág. 202). Fora de combate, quem decide o bônus é o Mestre.")
    if resultado == "falha crítica":
        print("  Num ataque isto é um Erro Crítico: use a Tabela de Erros Críticos "
              "(MB, pág. 202). Fora de combate, quem decide a consequência é o Mestre.")
    if efetivo > 18:
        print("  NH efetivo acima de 18: só 17 ou 18 falham, e 18 é sempre falha crítica.")
    if tem_sorte and not args.sorte:
        print(f"  {quem} tem **Sorte** e ainda pode usá-la: --sorte rola 3 vezes e fica "
              f"com o melhor (uma vez por hora de jogo).")

    for a in avisos:
        print(f"\n{a}")

    # ---- bloco para o WhatsApp ----
    # Sai sempre. Mostrar ou nao a mesa e decisao do Mestre, nao do script.
    w = [f"*{quem}* — {rotulo}"]
    if mod:
        w.append(f"NH {nh} {'+' if mod > 0 else '-'} {abs(mod)} = *{efetivo}* "
                 f"(precisa tirar {efetivo} ou menos)")
    else:
        w.append(f"NH *{efetivo}* (precisa tirar {efetivo} ou menos)")
    if args.sorte:
        w.append("_Sorte:_ rolou " + ", ".join(str(j[0]) for j in jogadas)
                 + " — vale o melhor")
    w.append(f"3d: {' + '.join(map(str, dados))} = *{total}*")
    w.append("")
    w.append({
        "sucesso decisivo": f"*SUCESSO DECISIVO!* (por {margem})",
        "sucesso": f"*Sucesso* por {margem}.",
        "falha": f"*Falha* por {abs(margem)}.",
        "falha crítica": f"*FALHA CRÍTICA!* (por {abs(margem)})",
    }[resultado])

    risco = "-" * 66
    print("\n" + risco)
    print("PARA O WHATSAPP (copie o bloco abaixo):")
    print(risco)
    print("\n".join(w))
    print(risco)

    if args.gravar:
        ok, msg = registrar(raiz, f"{quem}, {rotulo} contra {efetivo}: tirou {total} — "
                                  f"{resultado}.")
        print("\nRegistrado no capítulo atual." if ok else f"\nAVISO: não gravei — {msg}")


if __name__ == "__main__":
    main()
