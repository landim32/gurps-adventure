#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resolve uma troca de golpes pelo Sistema Avancado de Combate — MB, cap. 14.

    combate.py --atacante "Comam" --pericia "Espadas de Lâmina Larga" \
               --arma "Cimitarra" --modo balanco \
               --manobra ataque-total-bonus --local pescoco \
               --alvo "Morto-Vivo 1" --alvo-ht 11 --alvo-esquiva 5 --alvo-rd 1 \
               --alvo-defesa esquiva

Faz, nesta ordem: jogada de ataque (com o redutor do local e o bonus da manobra),
golpe fulminante ou erro critico, jogada de defesa do alvo (ativa + passiva), avaliacao
de dano, RD, bonus por tipo de dano, tetos do local e teste de queda/atordoamento.

Os dados sao rolados pela skill `roll`. As fichas sao lidas pela `teste-nh`.
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CAMPANHA_PY = Path(".claude/skills/gerenciar-campanha/scripts/campanha.py")
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


T = _carrega("tabelas", AQUI / "tabelas.py")
tn = _carrega("teste_nh", SKILLS / "teste-nh" / "scripts" / "teste_nh.py")
_roll = _carrega("roll", SKILLS / "roll" / "scripts" / "roll.py")

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

RE_DP_RD = re.compile(r"DP\s*(\d+)(?:\s*/\s*RD\s*(\d+))?", re.I)
REGIOES = {"cabeca": ("cabeç", "cabec", "elmo", "capacete", "camal"),
           "tronco": ("tronco", "torso", "peito"),
           "bracos": ("braço", "braco"),
           "maos": ("mão", "mao"),
           "pernas": ("perna",),
           "pes": ("pé", "pe)", "pés", "pes)")}


# ------------------------------------------------------------------ utilidades
def local_pedido(txt):
    """Resolve o nome do local, com apelidos. Devolve (chave, dados, aviso)."""
    k = tn.slug(txt)
    aviso = None
    if k in T.APELIDOS:
        k, aviso = T.APELIDOS[k]
    if k not in T.LOCAIS:
        alvo = k.replace("-", "")
        for chave in T.LOCAIS:
            if chave.replace("-", "").startswith(alvo):
                k = chave
                break
    if k not in T.LOCAIS:
        raise SystemExit(f"Local «{txt}» não existe. Use: " + ", ".join(sorted(T.LOCAIS)))
    return k, T.LOCAIS[k], aviso


def local_aleatorio(de_cima=False):
    dados = _roll.d6(3)
    total = sum(dados) - (3 if de_cima else 0)
    for teto, chave in T.ALEATORIO:
        if total <= teto:
            return chave, dados, total
    return "orgaos-vitais", dados, total


def protecao(ficha, regiao, perfurante):
    """DP e RD daquela regiao, lidos das pecas de armadura da ficha."""
    if not ficha or not regiao:
        return 0, 0, None
    for o in ficha.get("armas_objetos") or []:
        if (o.get("categoria") or "").lower() != "armadura":
            continue
        nome = (o.get("item") or "").lower()
        if not any(p in nome for p in REGIOES.get(regiao, ())):
            continue
        tipo = o.get("tipo") or ""
        # "DP3/RD4 (DP1/RD2 perf)" — o segundo par vale contra perfurante
        pares = RE_DP_RD.findall(tipo)
        if not pares:
            continue
        i = 1 if (perfurante and len(pares) > 1 and "perf" in tipo.lower()) else 0
        dp, rd = pares[i]
        return int(dp), int(rd or 0), o.get("item")
    return 0, 0, None


def escudo_dp(ficha):
    for o in ficha.get("armas_objetos") or []:
        if "escudo" in (o.get("item") or "").lower() or "broquel" in (o.get("item") or "").lower():
            m = RE_DP_RD.search(o.get("tipo") or "")
            if m:
                return int(m.group(1)), o.get("item")
    return 0, None


def acha_arma(ficha, nome):
    alvo = tn.slug(nome)
    for o in ficha.get("armas_objetos") or []:
        if (o.get("categoria") or "").lower() not in ("armas", "arma"):
            continue
        if tn.slug(o.get("item", "")).startswith(alvo) or alvo in tn.slug(o.get("item", "")):
            return o
    return None


def escolhe_dano(arma, modo):
    """'2D/1D+1' com tipo 'corte/cont' -> o par do modo pedido."""
    danos = [d.strip() for d in (arma.get("dano") or "").split("/")]
    tipos = [t.strip() for t in (arma.get("tipo") or "").split("/")]
    i = 0
    if modo in ("estocada", "gdp") and len(danos) > 1:
        i = 1
    dano = danos[min(i, len(danos) - 1)]
    tipo = tipos[min(i, len(tipos) - 1)] if tipos else "cont"
    return dano, tn.slug(tipo)[:5]


def tipo_dano_chave(txt):
    s = tn.slug(txt)
    if s.startswith("cort"):
        return "corte"
    if s.startswith("perf") or s.startswith("estoc"):
        return "perf"
    return "cont"


def registrar(raiz, texto):
    script = raiz / CAMPANHA_PY
    if not script.is_file():
        return False, "gerenciar-campanha não encontrada"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(script), "--raiz", str(raiz),
                        "acontecimento", "--texto", texto], capture_output=True,
                       text=True, encoding="utf-8", timeout=30, env=env)
    return r.returncode == 0, (r.stdout or r.stderr).strip()


# ------------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser(description="Troca de golpes, Sistema Avançado (MB cap. 14).")
    ap.add_argument("--raiz", default=".")
    # atacante
    ap.add_argument("--atacante", required=True)
    ap.add_argument("--pericia", default="", help="Perícia da arma")
    ap.add_argument("--nh", type=int, default=0, help="NH na mão (NPC sem ficha)")
    ap.add_argument("--arma", default="", help="Item da ficha")
    ap.add_argument("--dano", default="", help="Dano na mão: 2D+2")
    ap.add_argument("--tipo", default="", help="corte, perf ou cont")
    ap.add_argument("--modo", default="balanco", choices=["balanco", "estocada", "gdp"])
    ap.add_argument("--manobra", default="ataque", choices=sorted(T.MANOBRAS))
    ap.add_argument("--local", default="tronco", help="Ponto de impacto, ou «aleatorio»")
    ap.add_argument("--de-cima", action="store_true", help="Ataque vindo de cima (-3 no sorteio)")
    ap.add_argument("--mod", type=int, default=0, help="Modificador extra no ataque")
    ap.add_argument("--condicao", action="append", choices=sorted(T.REDUTORES),
                    help="Condição adversa; pode repetir")
    ap.add_argument("--ferimento", type=int, default=0,
                    help="Pontos de vida perdidos na rodada anterior (redutor no ataque)")
    # alvo
    ap.add_argument("--alvo", required=True)
    ap.add_argument("--alvo-ht", type=int, default=0)
    ap.add_argument("--alvo-defesa", default="esquiva",
                    choices=["esquiva", "aparar", "bloqueio", "nenhuma"])
    ap.add_argument("--alvo-defesa-valor", type=int, default=0, help="Sobrepõe a ficha")
    ap.add_argument("--alvo-esquiva", type=int, default=0)
    ap.add_argument("--alvo-aparar", type=int, default=0)
    ap.add_argument("--alvo-bloqueio", type=int, default=0)
    ap.add_argument("--alvo-dp", type=int, default=-1, help="Defesa passiva na mão")
    ap.add_argument("--alvo-rd", type=int, default=-1, help="RD do local, na mão")
    ap.add_argument("--alvo-defesa-mod", type=int, default=0,
                    help="Finta, ataque lateral (-2), etc.")
    ap.add_argument("--alvo-manobra", default="normal", choices=sorted(T.MANOBRAS_DEFESA))
    ap.add_argument("--alvo-hipoalgia", action="store_true",
                    help="O alvo tem Hipoalgia: sem redutor por ferimento")
    ap.add_argument("--recuar", action="store_true", help="O alvo recua: +3 na defesa")
    ap.add_argument("--gravar", action="store_true")
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()
    saida, avisos = [], []
    p = saida.append

    # ---------------------------------------------------------- quem ataca
    fa = tn.ler_ficha(args.atacante, raiz)
    atacante = (fa or {}).get("nome", args.atacante)
    manobra = T.MANOBRAS[args.manobra]

    nh_base, rotulo = args.nh, args.pericia or "ataque"
    if not nh_base:
        if not fa:
            raise SystemExit(f"Sem ficha para «{args.atacante}»: passe --nh e --dano.")
        achou = tn.acha_pericia(fa, args.pericia) if args.pericia else None
        if not achou:
            raise SystemExit(f"«{atacante}» não tem a perícia «{args.pericia}». "
                             f"Passe --nh, ou confira o nome na ficha.")
        nh_base, rotulo = achou

    # arma e dano
    arma_nome, dano_txt, tipo = args.arma, args.dano, tipo_dano_chave(args.tipo)
    if not dano_txt:
        if not fa:
            raise SystemExit("Passe --dano (ex.: 2D+2) para quem não tem ficha.")
        arma = acha_arma(fa, args.arma) if args.arma else None
        if not arma:
            raise SystemExit(f"Não achei a arma «{args.arma}» em {atacante}. "
                             f"Passe --dano e --tipo.")
        arma_nome = arma["item"]
        dano_txt, tipo_bruto = escolhe_dano(arma, args.modo)
        tipo = tipo_dano_chave(args.tipo or tipo_bruto)

    # ---------------------------------------------------------- ponto de impacto
    if tn.slug(args.local) in ("aleatorio", "aleatoria", "random"):
        chave, dados_loc, tot = local_aleatorio(args.de_cima)
        local = T.LOCAIS[chave]
        aviso_local = (f"Ponto de impacto sorteado: 3d [{', '.join(map(str, dados_loc))}]"
                       + (" -3 (de cima)" if args.de_cima else "") + f" = {tot} → "
                       + local["nome"])
        avisos.append(aviso_local)
    else:
        chave, local, aviso_local = local_pedido(args.local)
        if aviso_local:
            avisos.append(aviso_local)

    # ---------------------------------------------------------- NH do ataque
    partes, mod = [], 0
    if local["redutor"]:
        mod += local["redutor"]
        partes.append(f"{local['redutor']:+d} {local['nome']}")
    if manobra["nh"]:
        mod += manobra["nh"]
        partes.append(f"{manobra['nh']:+d} {manobra['nome']}")
    for c in args.condicao or []:
        v, txt = T.REDUTORES[c]
        mod += v
        partes.append(f"{v:+d} {txt}")
    if args.ferimento:
        mod -= args.ferimento
        partes.append(f"-{args.ferimento} ferimento da rodada anterior")
    if args.mod:
        mod += args.mod
        partes.append(f"{args.mod:+d} situação")
    nh_ef = nh_base + mod

    p("=" * 70)
    p(f"{atacante} ataca {args.alvo} — {local['nome']}")
    p(f"  Manobra: {manobra['nome']}")
    p(f"  {manobra['obs']}")
    p(f"  Arma: {arma_nome or '—'} · dano {dano_txt} · {T.TIPOS_DANO[tipo]['nome']}")
    p(f"  {rotulo}: NH {nh_base}" + (f" {mod:+d} = **{nh_ef}**" if mod else " = **%d**" % nh_ef))
    if partes:
        p(f"    ({'; '.join(partes)})")
    p("=" * 70)

    if nh_ef <= 3:
        p(f"NH efetivo {nh_ef}: o livro não permite a jogada (MB, cap. 12). "
          f"O golpe é impossível como declarado.")
        print("\n".join(saida))
        return

    # ---------------------------------------------------------- jogada de ataque
    da = _roll.d6(3)
    ta = sum(da)
    res_ataque = tn.classificar(ta, nh_ef)
    p(f"\nATAQUE: 3d [{', '.join(map(str, da))}] = {ta} contra {nh_ef} — {res_ataque.upper()}")

    acertou = res_ataque in ("sucesso", "sucesso decisivo")
    fulminante = res_ataque == "sucesso decisivo"
    efeito = {}
    mult_dano, ignora_armadura = 1, False

    if res_ataque == "falha crítica":
        de = _roll.d6(3)
        te = sum(de)
        p(f"\nERRO CRÍTICO — Tabela de Erros Críticos, 3d [{', '.join(map(str, de))}] = {te}")
        p(f"  {T.ERRO_CRITICO[te]}")
        p(f"\n  {T.DESARMADO_ERRO}" if not arma_nome else "")
        p(f"\n{atacante} não acertou nada. O golpe acabou aqui.")
        _fecha(saida, avisos, args, raiz, atacante, args.alvo, local,
               f"errou feio ({res_ataque})", None)
        return

    if res_ataque == "falha":
        p(f"\n{atacante} erra o golpe. {args.alvo} nem precisa se defender.")
        _fecha(saida, avisos, args, raiz, atacante, args.alvo, local, "errou", None)
        return

    if fulminante:
        de_cabeca = chave in ("cabeca", "cerebro", "olhos", "olhos-viseira")
        tab = T.FULMINANTE_CABECA if de_cabeca else T.FULMINANTE
        df = _roll.d6(3)
        tf = sum(df)
        efeito = tab[tf]
        nome_tab = "Golpes Fulminantes na Cabeça" if de_cabeca else "Golpes Fulminantes"
        p(f"\nGOLPE FULMINANTE — sem jogada de defesa!")
        p(f"  Tabela de {nome_tab}: 3d [{', '.join(map(str, df))}] = {tf}")
        p(f"  {efeito['txt']}")
        mult_dano = efeito.get("dano", 1)
        ignora_armadura = efeito.get("ignora_armadura", False)
        if efeito.get("morte"):
            p(f"\n{args.alvo} MORREU. Não há jogada de dano.")
            _fecha(saida, avisos, args, raiz, atacante, args.alvo, local,
                   "golpe fulminante na cabeça: morte instantânea", None,
                   fulminante=True, nh_ef=nh_ef, ataque=ta, arma=arma_nome,
                   extra_w=["*O golpe MATA na hora.*"])
            return

    # ---------------------------------------------------------- defesa
    fd = tn.ler_ficha(args.alvo, raiz)
    alvo = (fd or {}).get("nome", args.alvo)
    md = T.MANOBRAS_DEFESA[args.alvo_manobra]
    ht_alvo = args.alvo_ht or int(((fd or {}).get("atributos") or {})
                                  .get("HT", {}).get("valor") or 0)

    dp_local, rd_local, peca = protecao(fd, local.get("armadura"), tipo == "perf")
    if args.alvo_dp >= 0:
        dp_local, peca = args.alvo_dp, peca or "informado pelo Mestre"
    if args.alvo_rd >= 0:
        rd_local = args.alvo_rd
    rd_total = rd_local + local.get("rd_natural", 0)

    if not fulminante:
        if md["defesas"] == 0 or args.alvo_defesa == "nenhuma":
            p(f"\nDEFESA: {alvo} não tem defesa ativa — {md['nome']}.")
            if md.get("obs"):
                p(f"  {md['obs']}")
            defendeu = False
            dp_escudo, nome_escudo = (escudo_dp(fd) if fd else (0, None))
            dp_total = dp_local + (dp_escudo if local.get("armadura") else 0)
            if dp_total:
                dd = _roll.d6(3)
                td = sum(dd)
                p(f"  Só a defesa passiva vale: DP {dp_total}"
                  + (f" ({peca}" + (f" + {nome_escudo}" if dp_escudo else "") + ")" if peca else ""))
                p(f"  3d [{', '.join(map(str, dd))}] = {td} contra {dp_total} — "
                  + ("DEFENDEU" if td <= dp_total or td <= 4 else "não segurou"))
                defendeu = td <= dp_total or td <= 4
        else:
            base = args.alvo_defesa_valor
            fonte = "informada pelo Mestre"
            if not base:
                na_mao = {"esquiva": args.alvo_esquiva, "aparar": args.alvo_aparar,
                          "bloqueio": args.alvo_bloqueio}[args.alvo_defesa]
                if na_mao:
                    base, fonte = na_mao, "informada pelo Mestre"
                elif fd:
                    base = int((fd.get("defesas_ativas") or {}).get(args.alvo_defesa) or 0)
                    fonte = "da ficha"
            if not base:
                raise SystemExit(f"Não sei a {args.alvo_defesa} de {alvo}. Passe "
                                 f"--alvo-{args.alvo_defesa} ou --alvo-defesa-valor.")

            reflexos = bool(fd) and tn.nivel_vantagem(fd, "reflexos-em-combate") is not None
            dp_escudo, nome_escudo = (escudo_dp(fd) if fd else (0, None))
            dp_total = dp_local + (dp_escudo if local.get("armadura") else 0)

            comp, total_def = [f"{args.alvo_defesa} {base} ({fonte})"], base
            if reflexos:
                total_def += 1
                comp.append("+1 Reflexos em Combate")
            if dp_total:
                total_def += dp_total
                alvo_peca = peca or "armadura"
                comp.append(f"+{dp_local} DP {alvo_peca}" if dp_local else "")
                if dp_escudo and local.get("armadura"):
                    comp.append(f"+{dp_escudo} DP {nome_escudo}")
            if args.recuar:
                total_def += 3
                comp.append("+3 recuar")
            if md["mod"]:
                total_def += md["mod"]
                comp.append(f"{md['mod']:+d} {md['nome']}")
            if args.alvo_defesa_mod:
                total_def += args.alvo_defesa_mod
                comp.append(f"{args.alvo_defesa_mod:+d} situação")

            p(f"\nDEFESA de {alvo}: " + " ".join(c for c in comp if c) + f" = **{total_def}**")
            if md.get("obs"):
                p(f"  {md['obs']}")

            defendeu = False
            for tentativa in range(1, md["defesas"] + 1):
                dd = _roll.d6(3)
                td = sum(dd)
                ok = (td <= 4) or (td <= total_def and td < 17)
                marca = "DEFENDEU" if ok else "falhou"
                extra = ""
                if td <= 4:
                    extra = "  ← 3 ou 4 sempre defende, e o atacante vai à Tabela de Erros Críticos"
                if td >= 17:
                    extra = "  ← 17 ou 18 é falha desastrosa na defesa (MB, cap. 14)"
                rot = f"  Defesa {tentativa}" if md["defesas"] > 1 else "  Jogada"
                p(f"{rot}: 3d [{', '.join(map(str, dd))}] = {td} — {marca}{extra}")
                if ok:
                    defendeu = True
                    break
                if md["defesas"] > 1 and tentativa < md["defesas"]:
                    p("    (Defesa Total: a segunda tem de ser uma defesa DIFERENTE)")

        if defendeu:
            p(f"\n{alvo} se defendeu. Sem dano.")
            _fecha(saida, avisos, args, raiz, atacante, alvo, local, "defendeu o golpe",
                   None, nh_ef=nh_ef, ataque=ta, arma=arma_nome,
                   extra_w=[f"*{alvo} se defendeu.* Sem dano."])
            return
    else:
        dp_escudo = 0

    # ---------------------------------------------------------- dano
    p(f"\nDANO: {dano_txt}" + (f" ×{mult_dano}" if mult_dano > 1 else "")
      + (f" +{manobra['dano']} (ataque total)" if manobra["dano"] else ""))
    total_bruto, linha = _roll.rolar(dano_txt)
    p(f"  {linha.replace('**', '')}")
    basico = total_bruto + manobra["dano"]
    if manobra["dano"]:
        p(f"  +{manobra['dano']} do Ataque Total = {basico}")
    if mult_dano > 1:
        basico *= mult_dano
        p(f"  ×{mult_dano} pelo golpe fulminante = {basico}")

    if ignora_armadura:
        passou = basico
        p(f"  O golpe fulminante IGNORA a armadura: {passou} pontos entram inteiros.")
    else:
        passou = max(0, basico - rd_total)
        detalhe_rd = f"RD {rd_local}" + (f" ({peca})" if peca else "")
        if local.get("rd_natural"):
            detalhe_rd += f" + RD {local['rd_natural']} do crânio"
        p(f"  {detalhe_rd} → {passou} ponto(s) atravessam")

    if passou <= 0:
        p(f"\nA armadura segurou tudo. {alvo} não perde ponto de vida nenhum.")
        _fecha(saida, avisos, args, raiz, atacante, alvo, local,
               "não passou da armadura", 0, nh_ef=nh_ef, ataque=ta, arma=arma_nome,
               fulminante=fulminante)
        return

    # multiplicador do tipo de dano / do local
    ferimento, explica = passou, []
    if local.get("mult_todos"):
        ferimento = passou * local["mult_todos"]
        explica.append(f"×{local['mult_todos']} por atingir {local['nome'].lower()} "
                       f"(vale para qualquer tipo de dano)")
    elif tipo == "perf" and local.get("mult_perf"):
        ferimento = passou * local["mult_perf"]
        explica.append(f"×{local['mult_perf']} — perfurante nos órgãos vitais")
    elif local.get("incapacita") and tipo == "perf":
        explica.append("perfurante em membro NÃO ganha bônus de dano (MB, cap. 14)")
    else:
        m = T.TIPOS_DANO[tipo]["mult"]
        if m != 1.0:
            ferimento = int(passou * m)
            explica.append(f"{T.TIPOS_DANO[tipo]['nome']}: {T.TIPOS_DANO[tipo]['como']}")
    for e in explica:
        p(f"  {e} → {ferimento}")

    # tetos do local
    perdido = 0
    if ht_alvo:
        teto = None
        if local.get("teto_div_ht"):
            teto = ht_alvo // local["teto_div_ht"]
            rotulo_teto = f"HT/{local['teto_div_ht']}"
        elif local.get("teto_mult_ht"):
            teto = ht_alvo * local["teto_mult_ht"]
            rotulo_teto = f"HT×{local['teto_mult_ht']}"
        elif local.get("teto_perf_ht") and tipo == "perf":
            teto = ht_alvo
            rotulo_teto = "HT"
        if teto is not None and ferimento > teto:
            perdido = ferimento - teto
            p(f"  Teto do local ({rotulo_teto} = {teto}): {perdido} ponto(s) "
              f"desperdiçados — o golpe trespassa")
            ferimento = teto
            if local.get("incapacita"):
                p(f"  ⇒ {local['nome'].upper()} INCAPACITADO: {alvo} perde o uso do membro "
                  f"na hora, e fica ATORDOADO automaticamente.")

    if efeito.get("incapacita_membro") and local.get("incapacita"):
        p(f"  ⇒ Pelo golpe fulminante, o membro fica incapacitado seja qual for o dano.")

    p(f"\n**{alvo} perde {ferimento} ponto(s) de vida.**"
      + (f" (mais {perdido} desperdiçados)" if perdido else ""))
    if local.get("obs"):
        p(f"  {local['obs']}")

    # ---------------------------------------------------------- queda e atordoamento
    if ht_alvo:
        p(f"\nCONSEQUÊNCIAS (HT {ht_alvo}):")
        # Hipoalgia (Limiar de Dor Alto) elimina o redutor por ferimento — e e justamente
        # o que os mortos-vivos desta campanha tem.
        hipo = args.alvo_hipoalgia or (bool(fd) and
                                       tn.nivel_vantagem(fd, "hipoalgia") is not None)
        if hipo:
            p(f"  {alvo} tem Hipoalgia: **não** sofre o redutor por ferimento. Continua "
              f"atacando com o NH cheio.")
        else:
            p(f"  No próximo turno, {alvo} ataca com -{ferimento} (redutor por ferimento).")
        if ferimento > ht_alvo // 2:
            dq = _roll.d6(3)
            tq = sum(dq)
            ok = tq <= ht_alvo
            p(f"  Perdeu mais da metade da HT num golpe só: teste de HT para não cair.")
            p(f"    3d [{', '.join(map(str, dq))}] = {tq} contra {ht_alvo} — "
              + ("continua de pé" if ok else "CAIU"))
            p(f"  Caindo ou não, {alvo} fica ATORDOADO: -4 em todas as defesas ativas no "
              f"turno seguinte, e testa HT no início de cada turno para se recuperar.")
        elif efeito.get("atordoa"):
            p(f"  {alvo} fica ATORDOADO pelo golpe fulminante: -4 nas defesas ativas, "
              f"e testa HT a cada turno para sair.")
        if chave in ("cabeca", "cerebro") or (chave == "orgaos-vitais" and tipo == "cont"):
            dn = _roll.d6(3)
            tnk = sum(dn)
            p(f"  Golpe na cabeça (ou contundente nos vitais): teste de HT contra nocaute.")
            p(f"    3d [{', '.join(map(str, dn))}] = {tnk} contra {ht_alvo} — "
              + ("aguentou" if tnk <= ht_alvo else "NOCAUTEADO"))
        if chave == "cerebro":
            if ferimento > ht_alvo // 2:
                p(f"  Perda acima de HT/2 pelo crânio: NOCAUTEADO.")
            elif ferimento > ht_alvo // 3:
                p(f"  Perda acima de HT/3 pelo crânio: ATORDOADO.")
    else:
        p(f"\nSem a HT de {alvo} não dá para testar queda, atordoamento nem os tetos do "
          f"local. Passe --alvo-ht (está no npcs.md).")

    _fecha(saida, avisos, args, raiz, atacante, alvo, local,
           f"acertou {local['nome'].lower()}", ferimento, fulminante=fulminante,
           dano_txt=dano_txt, arma=arma_nome, nh_ef=nh_ef, ataque=ta, tipo=tipo)


def _fecha(saida, avisos, args, raiz, atacante, alvo, local, desfecho, ferimento,
           fulminante=False, dano_txt="", arma="", nh_ef=0, ataque=0, tipo="cont",
           extra_w=None):
    """Imprime tudo, monta o bloco do WhatsApp e registra na campanha."""
    print("\n".join(l for l in saida if l))
    for a in avisos:
        print(f"\nATENÇÃO: {a}")

    w = [f"*{atacante}* ataca *{alvo}* — {local['nome'].lower()}"]
    if arma:
        w.append(f"_{arma}_")
    w.append("")
    if nh_ef:
        w.append(f"Ataque: 3d = *{ataque}* contra NH {nh_ef}")
    if fulminante:
        w.append("*GOLPE FULMINANTE!* Sem defesa possível.")
    for linha in extra_w or []:
        w.append(linha)
    if ferimento is None and not extra_w:
        w.append(f"*{desfecho.capitalize()}.*")
    elif ferimento == 0:
        w.append("*A armadura segurou o golpe.* Nenhum dano.")
    else:
        w.append(f"*{alvo} perde {ferimento} ponto(s) de vida.*")

    risco = "-" * 70
    print("\n" + risco)
    print("PARA O WHATSAPP (copie o bloco abaixo):")
    print(risco)
    print("\n".join(w))
    print(risco)

    if args.gravar:
        txt = f"{atacante} atacou {alvo} ({local['nome'].lower()}): {desfecho}"
        if ferimento:
            txt += f", {ferimento} pontos de vida"
        ok, msg = registrar(raiz, txt + ".")
        print("\nRegistrado no capítulo atual." if ok else f"\nAVISO: não gravei — {msg}")


if __name__ == "__main__":
    main()
