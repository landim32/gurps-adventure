#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resolve uma finta — MB, cap. 14 (Avancado: "Avancar e Fintar", pag. 105; Basico: "Finta").

    fintar.py --fintador "Negrum" --pericia "Machado/Maça" \
              --alvo "Edric Halloway" --alvo-nh 14 --alvo-oque "Escudo"

A finta e uma Disputa Rapida: o NH do fintador com a arma contra o NH do alvo com o escudo
ou a arma (ou a DX dele, se ele nao tem nenhum dos dois ou se a DX for maior). Se o fintador
vence, a margem — ou a diferenca das margens, quando os dois passam — sai da defesa ativa do
alvo no PROXIMO ataque do fintador, so dele, por uma rodada.

Quem acha o NH e a skill `teste-nh`; quem rola o dado e a skill `roll`; o ataque que cobra o
redutor e a skill `atacar`. Aqui so se compara e se devolve o redutor. Nao escreve em lugar
nenhum, a nao ser com --gravar, que entrega o ato a `registrar-acao`.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]


def _carrega(nome, caminho):
    try:
        spec = importlib.util.spec_from_file_location(nome, caminho)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as erro:
        raise SystemExit(f"Não consegui carregar {nome} ({caminho}): {erro}")


# Como a arma de longe faz: a finta e irma do ataque e consome o que ele ja sabe — ficha,
# NH, dado, veredito, entrega ao registrador. Nada disso e copiado.
C = _carrega("atacar", SKILLS / "atacar" / "scripts" / "atacar.py")
tn, _roll = C.tn, C._roll
dados_txt, veredito, com_motivo = C.dados_txt, C.veredito, C.com_motivo

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

MANOBRAS = {
    "avancar-e-fintar": ("Avançar e Fintar",
                         "Move 1 hex e simula o ataque. As armas continuam preparadas. "
                         "A defesa ativa do fintador é normal."),
    "ataque-total": ("Ataque Total (finta e ataque)",
                     "A finta vale para o ataque do mesmo Ataque Total (MB, opção b). "
                     "Sem defesa ativa até o próximo turno."),
}


def tem_escudo(ficha):
    return any("escudo" in (o.get("item") or "").lower()
               or "broquel" in (o.get("item") or "").lower()
               for o in (ficha or {}).get("armas_objetos") or [])


def lado_fintador(args, raiz):
    """(nome, ficha, nh_base, rotulo)."""
    f = tn.ler_ficha(args.fintador, raiz)
    nome = (f or {}).get("nome", args.fintador)
    if args.nh:
        return nome, f, args.nh, args.pericia or ("Escudo" if args.com_escudo else "arma")
    if not f:
        raise SystemExit(f"Sem ficha para «{args.fintador}»: passe --nh.")
    pericia = args.pericia or ("Escudo" if args.com_escudo else "")
    if not pericia:
        raise SystemExit("Diga com que o fintador finta: --pericia (a da arma, ou «Finta "
                         "(Katana)» se ele a tem em Manobras), --com-escudo, ou --nh.")
    achou = tn.acha_pericia(f, pericia)
    if not achou:
        raise SystemExit(f"«{nome}» não tem a perícia «{pericia}». Passe --nh, ou confira "
                         f"o nome na ficha (a finta de arte marcial está na categoria Manobras).")
    return nome, f, achou[0], achou[1]


def lado_alvo(args, raiz):
    """(nome, nh, rotulo, candidatos) — o NH com que o alvo resiste.

    MB: o NH com o escudo OU a arma; contra a DX se ele nao tem nenhum dos dois, ou se a DX
    e maior. Na pratica: o maior entre escudo, arma e DX.
    """
    f = tn.ler_ficha(args.alvo, raiz)
    nome = (f or {}).get("nome", args.alvo)
    if args.alvo_nh:
        return nome, args.alvo_nh, args.alvo_oque or "defesa", []
    if not f:
        raise SystemExit(f"Sem ficha para «{args.alvo}»: passe --alvo-nh (e --alvo-oque).")
    atrib = {k: v.get("valor") for k, v in (f.get("atributos") or {}).items()}
    cand = []
    dx = int(atrib.get("DX") or 0)
    if dx:
        cand.append(("DX", dx))
    if args.alvo_pericia:
        a = tn.acha_pericia(f, args.alvo_pericia)
        if not a:
            raise SystemExit(f"«{nome}» não tem «{args.alvo_pericia}». Passe --alvo-nh.")
        cand.append((a[1], a[0]))
    if tem_escudo(f) and not args.sem_escudo:
        a = tn.acha_pericia(f, "Escudo")
        cand.append(("Escudo", a[0] if a else max(dx - 4, 0)))
    nh, rotulo = max(((n, r) for r, n in cand), key=lambda x: x[0])
    return nome, nh, rotulo, cand


def decide(margem_a, res_a, margem_d, res_d):
    """O que a Disputa Rapida entrega: (funcionou, redutor, por_que).

    MB: o fintador falhou, ou os dois passaram e a margem do alvo foi igual ou maior: falhou.
    O alvo falhou: o redutor e a margem do fintador. Os dois passaram e o fintador por mais:
    o redutor e a diferenca das margens.
    """
    ok_a = res_a in ("sucesso", "sucesso decisivo")
    ok_d = res_d in ("sucesso", "sucesso decisivo")
    if not ok_a:
        return False, 0, "o fintador errou a jogada"
    if not ok_d:
        return True, margem_a, "o alvo falhou"
    dif = margem_a - margem_d
    if dif > 0:
        return True, dif, "os dois passaram, e o fintador por margem maior"
    return False, 0, "os dois passaram e a margem do alvo foi igual ou maior"


def main():
    ap = argparse.ArgumentParser(description="Finta (MB cap. 14): Disputa Rápida.")
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--fintador", required=True)
    ap.add_argument("--pericia", default="", help="Perícia da arma, ou «Finta (arma)»")
    ap.add_argument("--nh", type=int, default=0, help="NH na mão (NPC sem ficha)")
    ap.add_argument("--com-escudo", action="store_true",
                    help="Finta com o escudo (só depois de já ter atacado com ele; usa Escudo)")
    ap.add_argument("--manobra", default="avancar-e-fintar", choices=sorted(MANOBRAS))
    ap.add_argument("--mod", type=int, default=0, help="Modificador extra na finta")
    ap.add_argument("--mod-motivo", default="", help="Por que o --mod")
    ap.add_argument("--impedimento", default="",
                    help="Por que a finta não vale: «no escuro», «de costas», «fora de alcance»")
    ap.add_argument("--alvo", required=True)
    ap.add_argument("--alvo-nh", type=int, default=0, help="NH do alvo na mão (NPC)")
    ap.add_argument("--alvo-oque", default="", help="Rótulo do --alvo-nh: «Escudo», «Aparar»")
    ap.add_argument("--alvo-pericia", default="", help="Perícia da arma do alvo, na ficha")
    ap.add_argument("--sem-escudo", action="store_true",
                    help="O escudo do alvo não conta (às costas, arma de duas mãos)")
    ap.add_argument("--alvo-mod", type=int, default=0)
    ap.add_argument("--alvo-mod-motivo", default="")
    ap.add_argument("--json", action="store_true",
                    help="Só o resultado em JSON, para outra skill ler")
    ap.add_argument("--gravar", action="store_true")
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()
    nome_m, obs_m = MANOBRAS[args.manobra]
    fintador, _, nh_a, rot_a = lado_fintador(args, raiz)
    alvo, nh_d, rot_d, cand = lado_alvo(args, raiz)

    saida, mec, avisos = [], [], []
    mec.append(f"_{nome_m}_")

    if args.impedimento:
        txt = (f"Finta impossível: {args.impedimento}. O livro só deixa fintar quem "
               f"*poderia* ter atingido o alvo com um ataque, e que o alvo possa ver.")
        if args.json:
            print(json.dumps({"fintador": fintador, "alvo": alvo, "possivel": False,
                              "funcionou": False, "redutor": 0, "motivo": txt},
                             ensure_ascii=False))
        else:
            print(txt)
        return

    partes_a = []
    if args.mod:
        partes_a.append(com_motivo(args.mod, args.mod_motivo))
    ef_a = nh_a + args.mod
    partes_d = []
    if args.alvo_mod:
        partes_d.append(com_motivo(args.alvo_mod, args.alvo_mod_motivo))
    ef_d = nh_d + args.alvo_mod

    da, dd = _roll.d6(3), _roll.d6(3)
    ta, td = sum(da), sum(dd)
    ra, rd = tn.classificar(ta, ef_a), tn.classificar(td, ef_d)
    ma, md = ef_a - ta, ef_d - td

    funcionou, redutor, porque = decide(ma, ra, md, rd)

    # ---- terminal
    p = saida.append
    p("=" * 70)
    p(f"{fintador} finta {alvo} — {nome_m}")
    p(f"  {obs_m}")
    p(f"  Finta: {rot_a} NH {nh_a}" + (f" {args.mod:+d}" if args.mod else "") + f" = **{ef_a}**")
    p(f"  Defesa: {alvo} com {rot_d} NH {nh_d}" + (f" {args.alvo_mod:+d}" if args.alvo_mod else "")
      + f" = **{ef_d}**")
    if cand:
        p("  (contra o melhor entre " + ", ".join(f"{r} {n}" for r, n in cand) + ")")
    p("=" * 70)
    p(f"\nFINTA:  3d [{', '.join(map(str, da))}] = {ta} contra {ef_a} — {ra.upper()}")
    p(f"DEFESA: 3d [{', '.join(map(str, dd))}] = {td} contra {ef_d} — {rd.upper()}")
    if funcionou:
        p(f"\nA FINTA FUNCIONOU ({porque}). A defesa ativa de {alvo} sofre -{redutor} "
          f"no PRÓXIMO ataque de {fintador}, e só nele, por uma rodada.")
        p(f"  Cobre no `atacar`: --alvo-defesa-mod -{redutor} --alvo-defesa-mod-motivo "
          f"\"finta de {fintador}, margem {redutor}\"")
    else:
        p(f"\nA finta falhou ({porque}). Sem redutor.")
    for r, quem in ((ra, fintador), (rd, alvo)):
        if r in ("sucesso decisivo", "falha crítica"):
            avisos.append(f"{quem} tirou {r}: o livro não tem tabela de crítico para a finta. "
                          f"O número acima não muda; se o efeito importa, é arbitragem do "
                          f"Mestre, e diga que é.")
    avisos.append("A finta vale uma rodada e só para o ataque de quem a fez — aliados não "
                  "aproveitam. Se o fintador perder o alvo de vista, perde o bônus. Se aparar "
                  "depois com arma desbalanceada, que fica despreparada, o próximo ataque não "
                  "sai e a finta se perde.")

    # ---- bloco da mesa
    cp = (", " + ", ".join(partes_a)) if partes_a else ""
    cd_ = (", " + ", ".join(partes_d)) if partes_d else ""
    mec.append(f"Finta: {rot_a} NH {nh_a}{cp} = *{ef_a}*")
    mec.append(f"3d {dados_txt(da)} = *{ta}* → {veredito(ra, ta, ef_a)}")
    mec.append(f"Defesa de {alvo}: {rot_d} NH {nh_d}{cd_} = *{ef_d}*")
    mec.append(f"3d {dados_txt(dd)} = *{td}* → {veredito(rd, td, ef_d)}")
    if funcionou:
        mec.append(f"*Finta funcionou:* defesa ativa de {alvo} *-{redutor}* contra o próximo "
                   f"ataque de {fintador}")
    else:
        mec.append("*A finta falhou.* Sem redutor.")
    w = [f"*{fintador}* finta *{alvo}*"] + mec[1:] if False else \
        [f"*{fintador}* finta *{alvo}*"] + mec

    status = (f"Fintado por {fintador}: -{redutor} na defesa ativa contra o próximo ataque "
              f"dele" if funcionou else "")

    if args.json:
        print(json.dumps({
            "fintador": fintador, "alvo": alvo, "possivel": True, "funcionou": funcionou,
            "redutor": redutor, "motivo": porque, "status_tatico": status,
            "finta": {"nh": ef_a, "dados": da, "total": ta, "resultado": ra},
            "defesa": {"nh": ef_d, "dados": dd, "total": td, "resultado": rd,
                       "usou": rot_d},
            "atacar": (f"--alvo-defesa-mod -{redutor} --alvo-defesa-mod-motivo "
                       f"\"finta de {fintador}, margem {redutor}\"") if funcionou else "",
            "whatsapp": "\n".join(w), "avisos": avisos[:-1],
        }, ensure_ascii=False, indent=2))
    else:
        print("\n".join(saida))
        for a in avisos:
            print(f"\nATENÇÃO: {a}")
        risco = "-" * 70
        print("\n" + risco)
        print("PARA O WHATSAPP (copie o bloco abaixo):")
        print(risco)
        print("\n".join(w))
        print(risco)

    if args.gravar:
        txt = (f"{fintador} fintou {alvo} ({nome_m}): " + (
            f"funcionou, -{redutor} na defesa ativa dele no próximo ataque" if funcionou
            else "falhou"))
        ok, msg = C.entregar({"resumo": txt + "."})
        print(("\nEntregue à registrar-acao:\n        " + msg) if ok
              else f"\nAVISO: não gravei — {msg}")


if __name__ == "__main__":
    main()
