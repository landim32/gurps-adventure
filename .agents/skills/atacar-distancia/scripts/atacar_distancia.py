#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Um disparo ou arremesso — ARMAS DE LONGO ALCANCE, MB cap. 14 (pags. 115-119).

A sequencia e a do livro, secao «Ataques Com Armas de Longo Alcance»:
  (1) NH basico com a arma
  (2) modificador de TAMANHO do alvo
  (3) modificador de VELOCIDADE/DISTANCIA (a soma dos dois vira um numero so)
  (4) modificador de PRECISAO, se apontou pelo menos um turno (teto: o NH basico)
  (5) condicoes — Tiro Rapido, turnos extras apontando, apoio, escuridao...
Depois: jogada de ataque, fulminante/erro critico, defesa (Esquiva, ou Bloqueio se o
projetil for lento, sempre somada a DP do escudo), dano com Meio Dano e Alcance Maximo,
RD da regiao, tipo de dano, tetos do local e consequencias.

Os dados sao rolados pela skill `roll`; as fichas sao lidas pela `teste-nh`; as tabelas
de local, critico e tipo de dano sao as mesmas da skill `atacar`.
"""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent


def _carrega(nome, caminho):
    try:
        spec = importlib.util.spec_from_file_location(nome, caminho)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as erro:
        raise SystemExit(f"Não consegui carregar {nome} ({caminho}): {erro}")


TD = _carrega("tabelas_distancia", AQUI / "tabelas_distancia.py")
C = _carrega("atacar", SKILLS / "atacar" / "scripts" / "atacar.py")
T = C.T

# A conta que vai para a mesa, cada numero com o motivo — ver atacar.py.
MEC = []
dados_txt, veredito = C.dados_txt, C.veredito
tn = C.tn
_roll = C._roll
cd = C.cd                      # a mesma folha de dano do corpo a corpo — uma cascata só

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ------------------------------------------------------------------ utilidades
def acha_modelo(txt):
    """«besta», «arco longo», «Faca Pequena» -> a entrada do catalogo."""
    k = tn.slug(txt)
    k = TD.APELIDOS_ARMA.get(k, k)
    if k in TD.ARMAS:
        return k, TD.ARMAS[k]
    for chave in TD.ARMAS:
        if chave.startswith(k) or k.startswith(chave):
            return chave, TD.ARMAS[chave]
    return None, {}


def resolve_alcance(expr, st):
    """«ST*20», «ST-5», «ST+5», «175» -> metros. Sem ST, devolve None."""
    expr = str(expr).strip()
    if not expr:
        return None
    m = re.fullmatch(r"ST\s*([*+\-/])\s*([\d.]+)", expr, re.I)
    if m:
        if not st:
            return None
        op, n = m.group(1), float(m.group(2))
        return {"*": st * n, "/": st / n, "+": st + n, "-": st - n}[op]
    if re.fullmatch(r"ST", expr, re.I):
        return float(st) if st else None
    try:
        return float(expr)
    except ValueError:
        return None


def teto_dano(teto):
    """«Dano max. 1D+4» da tabela da pag. 207 -> o maior valor que a arma alcanca."""
    if not teto:
        return None
    try:
        n, mod, _ = _roll.parse(teto)
    except Exception:
        return None
    return n * 6 + mod


def main():
    ap = argparse.ArgumentParser(
        description="Disparo ou arremesso — armas de longo alcance (MB cap. 14).")
    ap.add_argument("--raiz", default=".")
    # quem atira
    ap.add_argument("--atacante", required=True)
    ap.add_argument("--pericia", default="", help="Perícia da arma (Besta, Arco…)")
    ap.add_argument("--nh", type=int, default=0, help="NH na mão, para NPC sem ficha")
    ap.add_argument("--arma", default="",
                    help="Modelo do catálogo (besta, arco-longo, lanca…) ou item da ficha")
    ap.add_argument("--dano", default="", help="Dano já pronto, na mão: 1D+6")
    ap.add_argument("--tipo", default="", help="corte, perf ou cont")
    ap.add_argument("--tr", type=int, default=0,
                    help="Tiro Rápido, se a arma não estiver no catálogo")
    ap.add_argument("--prec", type=int, default=0, help="Precisão, idem")
    ap.add_argument("--meia", default="", help="½D em metros ou «ST*20»")
    ap.add_argument("--maximo", default="", help="Alcance máximo, idem")
    ap.add_argument("--arma-st", type=int, default=0,
                    help="ST que governa alcance e dano. BESTA: a ST DA ARMA")
    ap.add_argument("--bloqueavel", default="", choices=["", "sim", "nao"],
                    help="O projétil pode ser bloqueado com escudo?")
    # a situacao do tiro
    ap.add_argument("--distancia", type=float, required=True, help="Metros até o alvo")
    ap.add_argument("--apontou", type=int, default=0,
                    help="Turnos apontando. 1 já dá a Precisão; cada extra dá +1, até +3")
    ap.add_argument("--apoiada", action="store_true", help="Arma apoiada: +1 se apontou")
    ap.add_argument("--alvo-tamanho", type=float, default=2.0,
                    help="Maior dimensão do alvo em metros (humano = 2, que dá 0)")
    ap.add_argument("--alvo-velocidade", type=float, default=0.0,
                    help="m/s do alvo. Contra alvo humano com defesa ativa, deixe 0")
    ap.add_argument("--elevacao", type=float, default=0.0,
                    help="Metros que o ATIRADOR está acima do alvo (negativo: abaixo)")
    ap.add_argument("--erratico", type=int, default=0, help="Movimento errático: 0 a -4")
    ap.add_argument("--relampago", action="store_true", help="Ataque relâmpago")
    ap.add_argument("--as-cegas", action="store_true",
                    help="Tiro fora do ângulo de visão")
    ap.add_argument("--local", default="tronco", help="Ponto de impacto, ou «aleatorio»")
    ap.add_argument("--nao-frontal", action="store_true",
                    help="Tiro no pescoço vindo do lado ou de trás: sem esmagar a traqueia")
    ap.add_argument("--mod", type=int, default=0)
    ap.add_argument("--mod-motivo", default="",
                    help="Por que o --mod: «fumaça», «alvo atrás da carroça»")
    ap.add_argument("--condicao", action="append", choices=sorted(TD.CONDICOES))
    # o alvo
    ap.add_argument("--alvo", required=True)
    ap.add_argument("--alvo-ht", type=int, default=0)
    ap.add_argument("--alvo-defesa", default="esquiva",
                    choices=["esquiva", "bloqueio", "nenhuma"])
    ap.add_argument("--alvo-esquiva", type=int, default=0)
    ap.add_argument("--alvo-bloqueio", type=int, default=0)
    ap.add_argument("--alvo-dp", type=int, default=-1,
                    help="DP da armadura da região, por cima da ficha")
    ap.add_argument("--alvo-escudo-dp", type=int, default=-1,
                    help="DP do escudo do alvo, quando a peça não está na ficha")
    ap.add_argument("--alvo-rd", type=int, default=-1)
    ap.add_argument("--alvo-defesa-mod", type=int, default=0)
    ap.add_argument("--alvo-defesa-mod-motivo", default="",
                    help="Por que o --alvo-defesa-mod: «atordoado», «caído»")
    ap.add_argument("--alvo-manobra", default="normal", choices=sorted(T.MANOBRAS_DEFESA))
    ap.add_argument("--alvo-hipoalgia", action="store_true")
    ap.add_argument("--gravar", action="store_true")
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()
    saida, avisos = [], []
    p = saida.append

    # ---------------------------------------------------------- quem atira
    fa = tn.ler_ficha(args.atacante, raiz)
    atacante = (fa or {}).get("nome", args.atacante)
    st_atirador = int(((fa or {}).get("atributos") or {}).get("ST", {}).get("valor") or 0)

    chave_arma, modelo = acha_modelo(args.arma) if args.arma else (None, {})

    nh_base, rotulo = args.nh, args.pericia or modelo.get("pericia") or "ataque"
    if not nh_base:
        if not fa:
            raise SystemExit(f"Sem ficha para «{args.atacante}»: passe --nh e --dano.")
        achou = tn.acha_pericia(fa, args.pericia or modelo.get("pericia", ""))
        if not achou:
            raise SystemExit(f"«{atacante}» não tem a perícia «{rotulo}». Passe --nh, "
                             f"ou confira o nome na ficha.")
        nh_base, rotulo = achou

    tr = args.tr or modelo.get("tr", 0)
    prec = args.prec or modelo.get("prec", 0)
    bloqueavel = ((args.bloqueavel == "sim") if args.bloqueavel
                  else modelo.get("bloqueavel", True))

    # A ST que governa alcance e dano: a da besta e da ARMA, nao a de quem atira.
    st_alcance = args.arma_st or st_atirador
    if modelo.get("st_da_arma") and not args.arma_st:
        avisos.append("Besta: alcance e dano saem da ST DA ARMA, não da de quem atira. "
                      f"Sem --arma-st usei a ST de {atacante} ({st_atirador}) — confira "
                      f"na ficha qual é a besta.")

    meia = resolve_alcance(args.meia or modelo.get("meia", ""), st_alcance)
    maxima = resolve_alcance(args.maximo or modelo.get("max", ""), st_alcance)

    # ---------------------------------------------------------- arma e dano
    arma_nome = modelo.get("nome") or args.arma
    dano_txt, tipo = args.dano, C.tipo_dano_chave(args.tipo or modelo.get("tipo", ""))
    if not dano_txt:
        item = C.acha_arma(fa, args.arma) if (fa and args.arma) else None
        if item:
            arma_nome = item["item"]
            dano_txt, tipo_bruto = C.escolhe_dano(item, "balanco", fa)
            tipo = C.tipo_dano_chave(args.tipo or tipo_bruto)
        else:
            raise SystemExit(
                f"Não sei o dano de «{args.arma or '—'}». Passe --dano (ex.: 1D+4) e "
                f"--tipo, ou ponha o item na ficha de {atacante}. A fórmula da tabela "
                f"da pág. 207 para {arma_nome or 'esta arma'} é "
                f"«{modelo.get('dano') or '—'}»: some ao GDP/Balanço da ST que governa "
                f"a arma.")
    teto_d = teto_dano(modelo.get("teto"))

    # ---------------------------------------------------------- ponto de impacto
    if tn.slug(args.local) in ("aleatorio", "aleatoria", "random"):
        chave, dados_loc, tot = C.local_aleatorio(False)
        local = T.LOCAIS[chave]
        avisos.append(f"Ponto de impacto sorteado: 3d "
                      f"[{', '.join(map(str, dados_loc))}] = {tot} → {local['nome']}")
    else:
        chave, local, aviso_local = C.local_pedido(args.local)
        if aviso_local:
            avisos.append(aviso_local)

    p("=" * 70)
    p(f"{atacante} atira em {args.alvo} — {local['nome']}")
    p(f"  Arma: {arma_nome or '—'} · dano {dano_txt} · {T.TIPOS_DANO[tipo]['nome']}"
      + (f" · teto {modelo['teto']}" if modelo.get("teto") else ""))
    if tr or prec:
        p(f"  TR {tr} · Prec +{prec}"
          + (f" · ½D {meia:.0f} m" if meia else " · ½D —")
          + (f" · Máx {maxima:.0f} m" if maxima else " · Máx —")
          + (f"   (ST {st_alcance})" if st_alcance else ""))
    if modelo.get("obs"):
        p(f"  {modelo['obs']}")

    # ---------------------------------------------------------- distancia efetiva
    distancia = args.distancia
    if args.elevacao > 0:
        desconto = args.elevacao / 2.0
        distancia = max(args.distancia / 2.0, args.distancia - desconto)
        p(f"\nAtirando de cima ({args.elevacao:g} m acima do alvo): {args.distancia:g} m "
          f"- {desconto:g} = {distancia:g} m de distância efetiva")
    elif args.elevacao < 0:
        distancia = args.distancia + abs(args.elevacao)
        p(f"\nAtirando para cima (o alvo está {abs(args.elevacao):g} m acima): "
          f"{args.distancia:g} + {abs(args.elevacao):g} = {distancia:g} m de distância "
          f"efetiva")

    if maxima and distancia > maxima:
        p("=" * 70)
        p(f"\nALCANCE MÁXIMO: {maxima:.0f} m, e o alvo está a {distancia:g} m.")
        p(f"  {TD.NOTAS['max']}")
        _fecha(saida, avisos, args, raiz, atacante, args.alvo, local, arma_nome,
               distancia, "fora de alcance", None,
               extra_w=[f"_Alcance máximo {maxima:.0f} m; o alvo está a {distancia:g} m._",
                        "*O tiro não sai.*"])
        return

    alem_da_meia = bool(meia) and distancia > meia

    # ---------------------------------------------------------- NH efetivo
    comp, nh = [], nh_base

    mt, medida_t = TD.mod_tamanho(args.alvo_tamanho)
    if mt:
        nh += mt
        comp.append(f"{mt:+d} tamanho do alvo ({args.alvo_tamanho:g} m → linha dos "
                    f"{medida_t:g} m)")

    soma_vd = distancia + args.alvo_velocidade
    mvd, medida_vd = TD.mod_velocidade_distancia(soma_vd)
    nh += mvd
    detalhe = f"{distancia:g} m"
    if args.alvo_velocidade:
        detalhe += f" + {args.alvo_velocidade:g} m/s = {soma_vd:g}"
    comp.append(f"{mvd:+d} velocidade/distância ({detalhe} → linha dos {medida_vd:g} m)")

    if args.as_cegas:
        nh += TD.AS_CEGAS[0]
        comp.append(f"{TD.AS_CEGAS[0]:+d} {TD.AS_CEGAS[1]}")
        avisos.append(TD.NOTAS["as_cegas"])
    elif args.apontou >= 1:
        if alem_da_meia:
            comp.append("+0 Precisão — cancelada além do ½D")
            avisos.append(TD.NOTAS["prec_alem_meia"])
        elif prec:
            bonus = min(prec, nh_base)
            nh += bonus
            comp.append(f"+{bonus} Precisão da arma"
                        + (f" (limitada ao NH básico {nh_base})" if bonus < prec else ""))
        extras = min(max(args.apontou - 1, 0), 3)
        if extras:
            nh += extras
            comp.append(f"+{extras} por {extras} turno(s) extra(s) apontando (teto +3)")
        if args.apoiada:
            nh += TD.APOIO[0]
            comp.append(f"{TD.APOIO[0]:+d} {TD.APOIO[1]}")

    for c in args.condicao or []:
        v, nome = TD.CONDICOES[c]
        nh += v
        comp.append(f"{v:+d} {nome}")
    if args.relampago:
        nh += TD.RELAMPAGO[0]
        comp.append(f"{TD.RELAMPAGO[0]:+d} {TD.RELAMPAGO[1]}")
    if args.erratico:
        v = max(TD.ERRATICO_MAX, -abs(args.erratico))
        nh += v
        comp.append(f"{v:+d} movimento errático")
    if local["redutor"]:
        nh += local["redutor"]
        comp.append(f"{local['redutor']:+d} {local['nome']}")
    if args.mod:
        nh += args.mod
        comp.append(C.com_motivo(args.mod, args.mod_motivo))

    # Tiro Rapido: so quando NAO apontou. O TR e comparado com o NH ja ajustado.
    if args.apontou < 1 and not args.as_cegas:
        if args.relampago:
            nh += TD.TIRO_RAPIDO[0]
            comp.append("-4 Tiro Rápido (o ataque relâmpago sempre o sofre)")
        elif tr and nh < tr:
            ajustado = nh
            nh += TD.TIRO_RAPIDO[0]
            comp.append(f"-4 Tiro Rápido (NH ajustado {ajustado} não alcançou o TR {tr})")
        elif tr:
            comp.append(f"Tiro Rápido sem penalidade: NH ajustado {nh} ≥ TR {tr}")

    p("=" * 70)
    p(f"\nNH EFETIVO — {rotulo}: NH básico {nh_base}")
    for c in comp:
        p(f"    {c}")
    p(f"  ⇒ **{nh}**")
    MEC.append(f"_{arma_nome or 'disparo'}_ · {dano_txt} "
               f"{T.TIPOS_DANO[tipo]['nome'].lower()} · {distancia:g} m")
    MEC.append("Ataque: " + (f"{rotulo} " if rotulo != "ataque" else "") + f"NH {nh_base}"
               + (", " + ", ".join(comp) if comp else "") + f" = *{nh}*")
    if alem_da_meia:
        MEC.append(f"_Além do ½D ({meia:.0f} m): dano pela metade_")
    if alem_da_meia:
        p(f"\n  {TD.NOTAS['meia']} (½D = {meia:.0f} m)")
    p("=" * 70)

    if nh <= 3:
        p(f"\nNH efetivo {nh}: o livro não permite a jogada (MB, cap. 12). O tiro é "
          f"impossível como declarado — aponte mais turnos, chegue mais perto, ou não "
          f"atire.")
        print("\n".join(saida))
        for a in avisos:
            print(f"\nATENÇÃO: {a}")
        return

    # ---------------------------------------------------------- jogada de ataque
    da = _roll.d6(3)
    ta = sum(da)
    res = tn.classificar(ta, nh)
    # Tiro as cegas: vale a PIOR das duas regras — o -10 ja entrou, e ainda o teto de 9.
    if args.as_cegas and ta > 9 and res in ("sucesso", "sucesso decisivo"):
        res = "falha"
        avisos.append("Tiro às cegas: o dado passou de 9, então o tiro erra mesmo tendo "
                      "ficado dentro do NH — usa-se sempre a pior das duas regras.")
    p(f"\nATAQUE: 3d [{', '.join(map(str, da))}] = {ta} contra {nh} — {res.upper()}")
    MEC.append(f"3d {dados_txt(da)} = *{ta}* → {veredito(res, ta, nh)}")

    fulminante = res == "sucesso decisivo"
    critico_txt, critico_total, efeito = "", None, {}
    mult_dano, ignora_armadura = 1, False

    if res == "falha crítica":
        de = _roll.d6(3)
        te = sum(de)
        p(f"\nERRO CRÍTICO — Tabela de Erros Críticos, 3d "
          f"[{', '.join(map(str, de))}] = {te}")
        p(f"  {T.ERRO_CRITICO[te]}")
        MEC.append(f"*ERRO CRÍTICO!* Tabela de Erros Críticos: 3d {dados_txt(de)} = *{te}*")
        MEC.append(f"_{T.ERRO_CRITICO[te]}_")
        p(f"\n{atacante} não acertou nada. O tiro acabou aqui.")
        _fecha(saida, avisos, args, raiz, atacante, args.alvo, local, arma_nome, distancia,
               "errou feio (falha crítica)", None, nh=nh, ataque=ta,
               critico_tipo="erro", critico_total=te, critico_txt=T.ERRO_CRITICO[te])
        return

    if res == "falha":
        p(f"\n{atacante} erra o tiro. {args.alvo} nem precisa se defender.")
        avisos.append(TD.NOTAS["extraviado"])
        _fecha(saida, avisos, args, raiz, atacante, args.alvo, local, arma_nome, distancia,
               "errou o tiro", None, nh=nh, ataque=ta)
        return

    if fulminante:
        de_cabeca = chave in ("cabeca", "cerebro", "olhos", "olhos-viseira")
        tab = T.FULMINANTE_CABECA if de_cabeca else T.FULMINANTE
        df = _roll.d6(3)
        tf = sum(df)
        efeito = tab[tf]
        critico_txt, critico_total = efeito["txt"], tf
        nome_tab = "Golpes Fulminantes na Cabeça" if de_cabeca else "Golpes Fulminantes"
        p("\nGOLPE FULMINANTE — sem jogada de defesa!")
        p(f"  Tabela de {nome_tab}: 3d [{', '.join(map(str, df))}] = {tf}")
        p(f"  {efeito['txt']}")
        MEC.append("*GOLPE FULMINANTE!* Sem defesa possível.")
        MEC.append(f"Tabela de {nome_tab}: 3d {dados_txt(df)} = *{tf}*")
        MEC.append(f"_{efeito['txt']}_")
        mult_dano = efeito.get("dano", 1)
        ignora_armadura = efeito.get("ignora_armadura", False)
        if efeito.get("morte"):
            p(f"\n{args.alvo} MORREU. Não há jogada de dano.")
            _fecha(saida, avisos, args, raiz, atacante, args.alvo, local, arma_nome,
                   distancia, "tiro fulminante na cabeça: morte instantânea", None,
                   nh=nh, ataque=ta, fulminante=True, critico_tipo="fulminante",
                   critico_total=tf, critico_txt=efeito["txt"],
                   extra_w=["*O tiro MATA na hora.*"])
            return

    # ---------------------------------------------------------- defesa
    # O número, o escudo e o dado vêm da mesma folha do corpo a corpo — um regime só. O que
    # é de cá é a troca de quem não pode bloquear o projétil para Esquiva, porque só este
    # lado sabe o que a arma é bloqueável.
    dv = C.dv
    fd = tn.ler_ficha(args.alvo, raiz)
    alvo = (fd or {}).get("nome", args.alvo)
    ht_alvo = args.alvo_ht or int(((fd or {}).get("atributos") or {})
                                  .get("HT", {}).get("valor") or 0)
    defesa = args.alvo_defesa
    if defesa == "bloqueio" and not bloqueavel:
        defesa = "esquiva"
        avisos.append(TD.NOTAS["bloqueio_nao"])
        p(f"\n{alvo} não pode BLOQUEAR este projétil. Fica a Esquiva — e a DP do "
          f"escudo, que vale do mesmo jeito.")
    elif defesa == "bloqueio":
        avisos.append(TD.NOTAS["bloqueio_sim"])
    na_mao = {"esquiva": args.alvo_esquiva, "bloqueio": args.alvo_bloqueio}.get(defesa, 0)
    dfe = dv.calcular({
        "alvo": alvo, "ficha": fd, "local": local, "tipo": tipo, "ht_alvo": ht_alvo,
        "defesa": defesa, "defesa_valor": na_mao,
        "md": T.MANOBRAS_DEFESA[args.alvo_manobra],
        "mod": args.alvo_defesa_mod, "mod_motivo": args.alvo_defesa_mod_motivo,
        "projetil": True, "frontal": not args.nao_frontal,
        "dp_informado": args.alvo_dp if args.alvo_dp >= 0 else None,
        "rd_informado": args.alvo_rd if args.alvo_rd >= 0 else None,
        "escudo_dp_informado": (args.alvo_escudo_dp if args.alvo_escudo_dp >= 0 else None),
        "ignora_defesa": fulminante,
    })
    for linha in dfe["saida"]:
        p(linha)
    MEC.extend(dfe["mec"])
    rdef = dfe["resultado"]
    rd_local, rd_total, peca = rdef["rd_local"], rdef["rd_total"], rdef["peca"]
    dp_escudo, nome_escudo = rdef["dp_escudo"], rdef["nome_escudo"]
    if rdef["defendeu"]:
        p(f"\n{alvo} se defendeu. Sem dano.")
        _fecha(saida, avisos, args, raiz, atacante, alvo, local, arma_nome, distancia,
               "defendeu o tiro", None, nh=nh, ataque=ta,
               extra_w=[f"*{alvo} se defendeu.* Sem dano."])
        return


    # ---------------------------------------------------------- dano
    # A cascata é da folha `causar-dano`, a mesma do corpo a corpo. O que é só de projétil
    # entra no payload: o teto da arma, o ½D além da metade do alcance, e o fato de que é o
    # projétil que trespassa quando o teto do local corta o resto.
    dano = cd.calcular({
        "alvo": alvo, "tipo": tipo, "formula": dano_txt,
        "mult_dano": mult_dano, "ignora_armadura": ignora_armadura,
        "rd_total": rd_total, "rd_local": rd_local, "peca": peca,
        "local": local, "chave": chave, "ht_alvo": ht_alvo,
        "frontal": not args.nao_frontal, "efeito": efeito,
        "teto_arma": teto_d, "teto_arma_rotulo": (modelo or {}).get("teto"),
        "meia_dano": alem_da_meia, "meia_de": meia,
        "trespassa_por": "projétil", "nota_membro": True,
    })
    for linha in dano["saida"]:
        p(linha)
    MEC.extend(dano["mec"])
    ferimento, perdido = dano["resultado"]["ferimento"], dano["resultado"]["perdido"]
    if dano["resultado"]["armadura_segurou"]:
        _fecha(saida, avisos, args, raiz, atacante, alvo, local, arma_nome, distancia,
               "não passou da armadura", 0, nh=nh, ataque=ta, fulminante=fulminante,
               critico_tipo="fulminante" if fulminante else "",
               critico_total=critico_total, critico_txt=critico_txt)
        return


    # ---------------------------------------------------------- consequências
    # A mesma folha do corpo a corpo. O que muda é a palavra: aqui é tiro, não golpe.
    fer = C.af.calcular({
        "alvo": alvo, "ferimento": ferimento, "ht_alvo": ht_alvo, "chave": chave,
        "tipo": tipo, "efeito": efeito, "ficha": fd, "hipoalgia": args.alvo_hipoalgia,
        "projetil": True,
    })
    for linha in fer["saida"]:
        p(linha)
    MEC.extend(fer["mec"])


    _fecha(saida, avisos, args, raiz, atacante, alvo, local, arma_nome, distancia,
           f"acertou {local['nome'].lower()}", ferimento, nh=nh, ataque=ta,
           fulminante=fulminante, critico_tipo="fulminante" if fulminante else "",
           critico_total=critico_total, critico_txt=critico_txt)


def _fecha(saida, avisos, args, raiz, atacante, alvo, local, arma, distancia, desfecho,
           ferimento, nh=0, ataque=0, fulminante=False, extra_w=None, critico_tipo="",
           critico_total=None, critico_txt=""):
    """Imprime tudo, monta o bloco do WhatsApp e registra na campanha."""
    print("\n".join(l for l in saida if l))
    for a in avisos:
        print(f"\nATENÇÃO: {a}")

    # A conta inteira, na ordem em que aconteceu: NH e cada modificador com o motivo,
    # o dado, a defesa, o dano, a RD, os testes de HT. E o que a mesa le.
    w = [f"*{atacante}* atira em *{alvo}* — {local['nome'].lower()}"] + MEC
    for linha in extra_w or []:
        w.append(linha)
    if ferimento is None:
        if not extra_w:
            w.append(f"*{desfecho.capitalize()}.*")
    elif ferimento == 0:
        w.append("*A armadura segurou o tiro.* Nenhum dano.")
    else:
        w.append(f"*{alvo} perde {ferimento} ponto(s) de vida.*")

    risco = "-" * 70
    print("\n" + risco)
    print("PARA O WHATSAPP (copie o bloco abaixo):")
    print(risco)
    print("\n".join(w))
    print(risco)

    if args.gravar:
        txt = (f"{atacante} atirou em {alvo} a {distancia:g} m "
               f"({local['nome'].lower()}): {desfecho}")
        if critico_txt:
            rotulo = "golpe fulminante" if critico_tipo == "fulminante" else "erro crítico"
            txt += f" — {rotulo} ({critico_total}): {critico_txt.rstrip('.')}"
        if ferimento:
            txt += f", {ferimento} pontos de vida"
        ok, msg = C.entregar({"resumo": txt + "."})
        print(("\nEntregue à registrar-acao:\n        " + msg) if ok
              else f"\nAVISO: não gravei — {msg}")


if __name__ == "__main__":
    main()
