#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resolve uma troca de golpes pelo Sistema Avancado de Combate — MB, cap. 14.

    atacar.py --atacante "Comam" --pericia "Espadas de Lâmina Larga" \
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

SKILLS = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
REGISTRAR_PY = SKILLS / "registrar-acao" / "scripts" / "registrar_acao.py"


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
cd = _carrega("causar_dano", SKILLS / "causar-dano" / "scripts" / "causar_dano.py")
dv = _carrega("resolver_defesa",
              SKILLS / "resolver-defesa" / "scripts" / "resolver_defesa.py")
af = _carrega("arbitrar_ferimento",
              SKILLS / "arbitrar-ferimento" / "scripts" / "arbitrar_ferimento.py")

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

# A conta que vai para a mesa: cada numero com o motivo dele. Preenchida ao longo do
# golpe e despejada no bloco do WhatsApp por _fecha().
MEC = []


def dados_txt(dados):
    return "[" + ", ".join(map(str, dados)) + "]"


def com_motivo(valor, motivo):
    """«-2 escuro» a partir de --mod -2 --mod-motivo escuro; motivo que ja traz os sinais
    («-1 escuro, -1 fumaça») vale como veio."""
    m = (motivo or "").strip()
    return m if m[:1] in "+-" else f"{valor:+d} {m or 'situação'}"


def veredito(resultado, total, alvo_nh):
    """«sucesso por 3», «FALHA CRÍTICA (por 8)» — o que a mesa precisa ler do dado."""
    margem = alvo_nh - total
    return {"sucesso decisivo": f"*SUCESSO DECISIVO* (por {margem})",
            "sucesso": f"sucesso por {margem}",
            "falha": f"falha por {abs(margem)}",
            "falha crítica": f"*FALHA CRÍTICA* (por {abs(margem)})"}[resultado]


RE_DP_RD = re.compile(r"DP\s*(\d+)(?:\s*/\s*RD\s*(\d+))?", re.I)
REGIOES = {"cabeca": ("cabeç", "cabec", "elmo", "capacete", "camal"),
           "pescoco": ("pescoç", "pescoc", "gorjal", "camal", "gola"),
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


def efeitos_pescoco(chave, tipo, ferimento, ht, alvo, frontal=True):
    """Regras especiais do pescoço — regra da casa, GURPS 4ª ed. (MB Campanhas, p. 552).

    Devolve [(linha do terminal, linha da mesa)]. Nas fichas desta campanha os PV são a HT.
    """
    if chave != "pescoco" or not ht:
        return []
    meia = f"{ht / 2:g}".replace(".", ",")
    out = []
    if tipo == "cont" and frontal and ferimento > ht / 2:
        out.append((f"  ⇒ TRAQUEIA ESMAGADA: contusão pela frente acima de HT/2 ({meia}). "
                    f"Lesão incapacitante: {alvo} está SUFOCANDO (regra da casa, 4ª ed.).",
                    f"*TRAQUEIA ESMAGADA* (contusão pela frente > HT/2 = {meia}) — "
                    f"{alvo} está *sufocando*"))
    if tipo == "corte" and ferimento > 3 * ht:
        out.append((f"  ⇒ DECAPITAÇÃO POSSÍVEL: corte acima de 3×HT ({3 * ht}) num golpe só. "
                    f"O Mestre pode declarar {alvo} decapitado: morte automática.",
                    f"*Corte acima de 3×HT ({3 * ht})* — o Mestre pode declarar "
                    f"*DECAPITAÇÃO*"))
    return out


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


RE_FORMULA = re.compile(r"^(GDP|BAL|GDB)\s*([+-]\s*\d+)?$", re.I)
RE_DADO = re.compile(r"^(\d+)D\s*([+-]\s*\d+)?$", re.I)


def resolve_formula(dano, ficha):
    """'BAL+1' -> '2D+2' pelo dano básico da ficha. O que não for fórmula volta igual."""
    m = RE_FORMULA.match((dano or "").strip())
    base = (ficha or {}).get("dano_basico") or {}
    if not m:
        return dano
    chave = "gdp" if m.group(1).upper() == "GDP" else "bal"
    d = RE_DADO.match((base.get(chave) or "").strip())
    if not d:
        return dano
    soma = int((d.group(2) or "0").replace(" ", "")) + int((m.group(2) or "0").replace(" ", ""))
    return f"{d.group(1)}D" + (f"{soma:+d}" if soma else "")


def escolhe_dano(arma, modo, ficha=None):
    """'2D/1D+1' com tipo 'corte/cont' -> o par do modo pedido. Fórmulas GDP/BAL da
    ficha ('BAL+1') viram dado pelo dano básico de quem ataca."""
    danos = [d.strip() for d in (arma.get("dano") or "").split("/")]
    tipos = [t.strip() for t in (arma.get("tipo") or "").split("/")]
    i = 0
    if modo in ("estocada", "gdp") and len(danos) > 1:
        i = 1
    dano = resolve_formula(danos[min(i, len(danos) - 1)], ficha)
    tipo = tipos[min(i, len(tipos) - 1)] if tipos else "cont"
    return dano, tn.slug(tipo)[:5]


def tipo_dano_chave(txt):
    s = tn.slug(txt)
    if s.startswith("cort"):
        return "corte"
    if s.startswith("perf") or s.startswith("estoc"):
        return "perf"
    return "cont"


def entregar(ato):
    """Passa o ato à `registrar-acao` — esta skill não escreve em lugar nenhum.

    O log do golpe carrega o efeito da tabela quando houve critico, porque e isso que muda
    o rumo da cena — nao o total de dano.
    """
    if not REGISTRAR_PY.is_file():
        return False, "skill registrar-acao nao encontrada"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(REGISTRAR_PY), "--stdin"],
                       input=json.dumps(ato, ensure_ascii=False),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=60, env=env)
    linhas = [l for l in (r.stdout or "").splitlines() if l.startswith("[")]
    return r.returncode == 0, "\n        ".join(linhas) or (r.stderr or "").strip()


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
    ap.add_argument("--nao-frontal", action="store_true",
                    help="Golpe no pescoço vindo do lado ou de trás: sem esmagar a traqueia")
    ap.add_argument("--mod", type=int, default=0, help="Modificador extra no ataque")
    ap.add_argument("--mod-motivo", default="",
                    help="Por que o --mod: «alvo atrás da mesa», «escuro»")
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
    ap.add_argument("--alvo-dp", type=int, default=-1,
                   help="DP da armadura da região, por cima da ficha")
    ap.add_argument("--alvo-escudo-dp", type=int, default=-1,
                    help="DP do escudo do alvo, quando a peça não está na ficha")
    ap.add_argument("--alvo-rd", type=int, default=-1, help="RD do local, na mão")
    ap.add_argument("--alvo-defesa-mod-motivo", default="",
                    help="Por que o --alvo-defesa-mod: «atordoado», «caído»")
    ap.add_argument("--alvo-defesa-mod", type=int, default=0,
                    help="Finta, ataque lateral (-2), etc.")
    ap.add_argument("--alvo-manobra", default="normal", choices=sorted(T.MANOBRAS_DEFESA))
    ap.add_argument("--alvo-hipoalgia", action="store_true",
                    help="O alvo tem Hipoalgia: sem redutor por ferimento")
    ap.add_argument("--recuar", action="store_true", help="O alvo recua: +3 na defesa")
    ap.add_argument("--sem-escudo", action="store_true",
                    help="O escudo da ficha NÃO vale nesta troca: está às costas, o alvo "
                         "empunha arma de duas mãos, o golpe vem por trás")
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
        dano_txt, tipo_bruto = escolhe_dano(arma, args.modo, fa)
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
        partes.append(com_motivo(args.mod, args.mod_motivo))
    nh_ef = nh_base + mod
    MEC.append(f"_{manobra['nome']}_ · " + (f"{arma_nome}, " if arma_nome else "") + f"{dano_txt} "
               f"{T.TIPOS_DANO[tipo]['nome'].lower()}")
    if tn.slug(args.local) in ("aleatorio", "aleatoria", "random"):
        MEC.append(aviso_local)
    MEC.append("Ataque: " + (f"{rotulo} " if rotulo != "ataque" else "") + f"NH {nh_base}"
               + (", " + ", ".join(partes) if partes else "") + f" = *{nh_ef}*")

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
    MEC.append(f"3d {dados_txt(da)} = *{ta}* → {veredito(res_ataque, ta, nh_ef)}")

    acertou = res_ataque in ("sucesso", "sucesso decisivo")
    fulminante = res_ataque == "sucesso decisivo"
    # o que a tabela de criticos disse, para repetir no bloco da mesa
    critico_txt, critico_total = "", None
    efeito = {}
    mult_dano, ignora_armadura = 1, False

    if res_ataque == "falha crítica":
        de = _roll.d6(3)
        te = sum(de)
        p(f"\nERRO CRÍTICO — Tabela de Erros Críticos, 3d [{', '.join(map(str, de))}] = {te}")
        p(f"  {T.ERRO_CRITICO[te]}")
        MEC.append(f"*ERRO CRÍTICO!* Tabela de Erros Críticos: 3d {dados_txt(de)} = *{te}*")
        MEC.append(f"_{T.ERRO_CRITICO[te]}_")
        p(f"\n  {T.DESARMADO_ERRO}" if not arma_nome else "")
        p(f"\n{atacante} não acertou nada. O golpe acabou aqui.")
        _fecha(saida, avisos, args, raiz, atacante, args.alvo, local,
               f"errou feio ({res_ataque})", None, nh_ef=nh_ef, ataque=ta,
               arma=arma_nome, critico_tipo="erro", critico_total=te,
               critico_txt=T.ERRO_CRITICO[te])
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
        critico_txt, critico_total = efeito["txt"], tf
        nome_tab = "Golpes Fulminantes na Cabeça" if de_cabeca else "Golpes Fulminantes"
        p(f"\nGOLPE FULMINANTE — sem jogada de defesa!")
        p(f"  Tabela de {nome_tab}: 3d [{', '.join(map(str, df))}] = {tf}")
        p(f"  {efeito['txt']}")
        MEC.append("*GOLPE FULMINANTE!* Sem defesa possível.")
        MEC.append(f"Tabela de {nome_tab}: 3d {dados_txt(df)} = *{tf}*")
        MEC.append(f"_{efeito['txt']}_")
        mult_dano = efeito.get("dano", 1)
        ignora_armadura = efeito.get("ignora_armadura", False)
        if efeito.get("morte"):
            p(f"\n{args.alvo} MORREU. Não há jogada de dano.")
            _fecha(saida, avisos, args, raiz, atacante, args.alvo, local,
                   "golpe fulminante na cabeça: morte instantânea", None,
                   fulminante=True, nh_ef=nh_ef, ataque=ta, arma=arma_nome,
                   critico_tipo="fulminante", critico_total=tf,
                   critico_txt=efeito["txt"],
                   extra_w=["*O golpe MATA na hora.*"])
            return

    # ---------------------------------------------------------- defesa
    # Quem apanhou tem número, dado e motivo numa folha só — a mesma que a arma de longe
    # usa, para um pavês não somar DP de um jeito contra uma espada e de outro contra um
    # virote. A folha devolve também o que a cascata de dano precisa: RD da região, a peça
    # de onde veio, e o escudo.
    fd = tn.ler_ficha(args.alvo, raiz)
    alvo = (fd or {}).get("nome", args.alvo)
    ht_alvo = args.alvo_ht or int(((fd or {}).get("atributos") or {})
                                  .get("HT", {}).get("valor") or 0)
    na_mao = args.alvo_defesa_valor or {
        "esquiva": args.alvo_esquiva, "aparar": args.alvo_aparar,
        "bloqueio": args.alvo_bloqueio}.get(args.alvo_defesa, 0)
    dfe = dv.calcular({
        "alvo": alvo, "ficha": fd, "local": local, "tipo": tipo, "ht_alvo": ht_alvo,
        "defesa": args.alvo_defesa, "defesa_valor": na_mao,
        "md": T.MANOBRAS_DEFESA[args.alvo_manobra],
        "mod": args.alvo_defesa_mod, "mod_motivo": args.alvo_defesa_mod_motivo,
        "recuar": args.recuar, "sem_escudo": args.sem_escudo,
        "frontal": not args.nao_frontal,
        "dp_informado": args.alvo_dp if args.alvo_dp >= 0 else None,
        "escudo_dp_informado": (args.alvo_escudo_dp if args.alvo_escudo_dp >= 0 else None),
        "rd_informado": args.alvo_rd if args.alvo_rd >= 0 else None,
        "ignora_defesa": fulminante,
    })
    for linha in dfe["saida"]:
        p(linha)
    for aviso in dfe["avisos"]:
        avisos.append(aviso)
    MEC.extend(dfe["mec"])
    rdef = dfe["resultado"]
    rd_local, rd_total, peca = rdef["rd_local"], rdef["rd_total"], rdef["peca"]
    dp_escudo, nome_escudo = rdef["dp_escudo"], rdef["nome_escudo"]
    if rdef["defendeu"]:
        p(f"\n{alvo} se defendeu. Sem dano.")
        _fecha(saida, avisos, args, raiz, atacante, alvo, local, "defendeu o golpe",
               None, nh_ef=nh_ef, ataque=ta, arma=arma_nome,
               extra_w=[f"*{alvo} se defendeu.* Sem dano."])
        return


    # ---------------------------------------------------------- dano
    # A cascata inteira é da folha `causar-dano`: dado, mínimo antes da armadura,
    # fulminante, RD, multiplicador do tipo e do local, teto do local, membro, pescoço.
    dano = cd.calcular({
        "alvo": alvo, "tipo": tipo, "formula": dano_txt, "bonus_dano": manobra["dano"],
        "mult_dano": mult_dano, "ignora_armadura": ignora_armadura,
        "rd_total": rd_total, "rd_local": rd_local, "peca": peca,
        "local": local, "chave": chave, "ht_alvo": ht_alvo,
        "frontal": not args.nao_frontal, "efeito": efeito,
    })
    for linha in dano["saida"]:
        p(linha)
    MEC.extend(dano["mec"])
    ferimento, perdido = dano["resultado"]["ferimento"], dano["resultado"]["perdido"]
    if dano["resultado"]["armadura_segurou"]:
        _fecha(saida, avisos, args, raiz, atacante, alvo, local,
               "não passou da armadura", 0, nh_ef=nh_ef, ataque=ta, arma=arma_nome,
               fulminante=fulminante)
        return

    # ---------------------------------------------------------- consequências
    # Queda, atordoamento, nocaute e o crânio exposto: a mesma folha dos dois lados do
    # alcance. Devolve também o estado tático pronto (caiu, atordoado, nocauteado), que é
    # o que vai para o ato entregue à registrar-acao.
    fer = af.calcular({
        "alvo": alvo, "ferimento": ferimento, "ht_alvo": ht_alvo, "chave": chave,
        "tipo": tipo, "efeito": efeito, "ficha": fd, "hipoalgia": args.alvo_hipoalgia,
    })
    for linha in fer["saida"]:
        p(linha)
    MEC.extend(fer["mec"])


    _fecha(saida, avisos, args, raiz, atacante, alvo, local,
           f"acertou {local['nome'].lower()}", ferimento, fulminante=fulminante,
           critico_tipo="fulminante" if fulminante else "",
           critico_total=critico_total, critico_txt=critico_txt,
           dano_txt=dano_txt, arma=arma_nome, nh_ef=nh_ef, ataque=ta, tipo=tipo)


def _fecha(saida, avisos, args, raiz, atacante, alvo, local, desfecho, ferimento,
           fulminante=False, dano_txt="", arma="", nh_ef=0, ataque=0, tipo="cont",
           extra_w=None, critico_tipo="", critico_total=None, critico_txt=""):
    """Imprime tudo, monta o bloco do WhatsApp e registra na campanha."""
    print("\n".join(l for l in saida if l))
    for a in avisos:
        print(f"\nATENÇÃO: {a}")

    # A conta inteira, na ordem em que aconteceu: NH e cada redutor com o motivo, o dado,
    # a defesa, o dano, a RD, o multiplicador, os testes de HT. E o que a mesa le.
    w = [f"*{atacante}* ataca *{alvo}* — {local['nome'].lower()}"] + MEC
    for linha in extra_w or []:
        w.append(linha)
    if ferimento is None:
        # golpe que nao chegou a causar dano: errou, ou o alvo defendeu
        if not extra_w:
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
        if critico_txt:
            # o efeito da tabela e o que muda o rumo; o log precisa dele
            rotulo = "golpe fulminante" if critico_tipo == "fulminante" else "erro crítico"
            txt += f" — {rotulo} ({critico_total}): {critico_txt.rstrip('.')}"
        if ferimento:
            txt += f", {ferimento} pontos de vida"
        ok, msg = entregar({"resumo": txt + "."})
        print(("\nEntregue à registrar-acao:\n        " + msg) if ok
              else f"\nAVISO: não gravei — {msg}")


if __name__ == "__main__":
    main()
