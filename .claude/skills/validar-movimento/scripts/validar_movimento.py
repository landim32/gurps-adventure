#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validar-movimento — quanto o personagem podia andar, e onde ele deve ficar.

    validar_movimento.py turno [--turno N] [--json] [--manobra "Nome=defesa-total"]
    validar_movimento.py calcular --de 5,10 --look-de 3 --para 6,11 --look-para 2 \
        --manobra defesa-total --desl 1 [--mapa oasis-1]
    validar_movimento.py terreno --mapa oasis-1 [--imagem cenarios/oasis.jpg] [--gravar]
    validar_movimento.py terreno --mapa oasis-1 --decidir "9,12=margem" --decidir "7,10=funda"

Regras (MB 3ª ed., `11-combate-avancado.md`, "Movimento", "Manobras" e "Custos em Pontos de
Movimento"; `07-equipamento-e-carga.md`, "Carga"; `12-ferimentos-doencas-fadiga.md`):

* Só a manobra **Deslocamento** gasta pontos de movimento (frente 1, lado/trás 2, virar 1 por
  lado, posição, terreno). Nas outras o livro dá um teto fixo de hexágonos.
* O Deslocamento vem da ficha, ajustado pela Carga *atual*, pela perna mutilada (-3), pela
  Fadiga (ST efetiva <= 3: metade) e por PV 1 a 3 (metade). Sempre se pode andar 1 hexágono.
* Passou do limite: a peça fica no ponto legal mais avançado da rota, e quem chama recalcula a
  ação a partir dali. A folha não rola dado, não fala com a mesa e não escreve nada além do
  `campanha/terreno.json` quando pedido.

Geometria (odd-q, `look` 0-5) é da `calcular-alcance`; aqui só se importa o arquivo dela.
"""
import argparse
import heapq
import importlib.util
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
RAIZ = Path(__file__).resolve().parents[4]
ALCANCE_PY = SKILLS / "calcular-alcance" / "scripts" / "calcular_alcance.py"
CONTEXTO_PY = SKILLS / "contexto" / "scripts" / "contexto.py"
ROLL6_PY = SKILLS / "roll6" / "scripts" / "roll6.py"
TERRENO_JSON = Path("campanha") / "terreno.json"

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _carregar(nome, caminho):
    espec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(mod)
    return mod


_alc = _carregar("calcular_alcance", ALCANCE_PY)
vizinho, hexes_entre, para_rotulo = _alc.vizinho, _alc.hexes_entre, _alc.para_rotulo

NOME_LOOK = {0: "N", 1: "NE", 2: "SE", 3: "S", 4: "SO", 5: "NO"}

# ---------------------------------------------------------------- manobras
# código -> (rótulo, regra do livro). O teto de hexágonos sai de `teto_hex`.
MANOBRAS = {
    "deslocamento": ("Deslocamento", "MB 11, Deslocamento e Custos em Pontos de Movimento: gasta o Deslocamento todo, "
                                     "frente 1, lado/trás 2, virar 1 por lado, mais posição e terreno."),
    "defesa-total": ("Defesa Total", "MB 11, Defesa Total: 1 hexágono em qualquer direção."),
    "ataque-total": ("Ataque Total", "MB 11, Ataque Total: até 2 hexágonos ou metade do Deslocamento (o maior), "
                                     "só para a frente, sem virar no fim."),
    "apontar": ("Apontar", "MB 11, Apontar: 2 m ou metade do Deslocamento, o menor."),
    "atacar": ("Avançar e Atacar", "MB 11, Avançar e Atacar: 1 hexágono em qualquer direção."),
    "preparar": ("Avançar e Preparar", "MB 11, Avançar e Preparar: 1 hexágono antes ou depois de sacar a arma."),
    "finta": ("Avançar e Fintar", "MB 11, Avançar e Fintar: 1 hexágono em qualquer direção."),
    "aguardar": ("Avançar e Aguardar", "MB 11, Avançar e Aguardar: 1 hexágono (ou ficar parado)."),
    "concentrar": ("Avançar e se Concentrar", "MB 11, Avançar e se Concentrar: 1 hexágono."),
    "posicao": ("Mudança de Posição", "MB 11, Mudança de Posição: não se desloca no turno."),
}
# ordem de proposta quando a declaração mistura manobras (a mais restritiva e explícita primeiro)
PRIORIDADE = ["defesa-total", "ataque-total", "apontar", "finta", "preparar", "atacar", "aguardar",
              "concentrar", "posicao", "deslocamento"]
PADROES = {
    "defesa-total": r"defesa total",
    "ataque-total": r"ataque total",
    "apontar": r"\bmir(a|o|ar|ando|ei)\b|\bapont",
    "aguardar": r"aguard",
    "preparar": r"\bprepar|\bsac(o|a|ar|ue|ando)\b|saque|desembainh|empunh|\bpego\b|\bapanh",
    "finta": r"\bfint",
    "concentrar": r"concentr|conjur|\blanco\b.*m[aá]gica",
    "atacar": r"\batac|\bgolpe|arremess|\batir|dispar|flecha|\bbato\b|\bacerto\b|\bataco\b",
    "posicao": r"levant|ajoelh|\bdeit|agach|\bsent(o|ar)\b|muda(r)? de posi",
    "deslocamento": r"\bs[oó] (me )?(ando|movo|movi|mover|move)\b|\bapenas (me )?(ando|anda|move|movo)\b|"
                    r"\bdesloc|\bcorr(o|er|endo)\b|\bvou (em dire|ate|at[eé])|\bando\b|\bmoveu\b|\bmovo\b|"
                    r"\bso (ando|move)\b",
}


def simples(texto):
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t.lower()).strip()


def classificar_manobra(textos):
    """[declarações] -> {"proposta", "candidatas", "ambigua", "trechos"}."""
    achadas, trechos = [], {}
    for t in textos:
        s = simples(t)
        for cod, pad in PADROES.items():
            if re.search(pad, s):
                if cod not in achadas:
                    achadas.append(cod)
                trechos.setdefault(cod, t.strip())
    achadas = [c for c in PRIORIDADE if c in achadas]
    # "Ataque Total" com "arremesso" ou "finta" é só o ataque dentro do Ataque Total
    if "ataque-total" in achadas:
        achadas = [c for c in achadas if c not in ("atacar", "finta")] or achadas
    if "apontar" in achadas:
        achadas = [c for c in achadas if c not in ("preparar", "atacar")] or achadas
    mistura = [c for c in achadas if c != "deslocamento"]
    ambigua = "deslocamento" in achadas and bool(mistura)
    if len(mistura) > 1 and not (set(mistura) <= {"ataque-total", "finta", "atacar"}):
        ambigua = ambigua or len(set(mistura) - {"preparar"}) > 1
    return {"proposta": achadas[0] if achadas else None, "candidatas": achadas,
            "ambigua": ambigua, "trechos": trechos}


def teto_hex(cod, desl):
    """Hexágonos que a manobra permite (None = pontos de movimento, só o Deslocamento)."""
    if cod == "deslocamento":
        return None
    if cod == "posicao":
        return 0
    if cod == "ataque-total":
        return max(2, desl // 2)
    if cod == "apontar":
        return max(1, min(2, desl // 2))
    return 1


# ---------------------------------------------------------------- Deslocamento
CARGA_NIVEIS = ("nenhuma", "leve", "media", "pesada", "muito_pesada")


def nivel_carga(peso, limites):
    """Pontos de Movimento perdidos para um peso: 0 nenhuma ... 4 muito pesada (5 = não anda)."""
    if peso is None or not limites:
        return 0
    for i, chave in enumerate(CARGA_NIVEIS):
        if peso <= float(limites.get(chave, 0)):
            return i
    return 5


def deslocamento_atual(ficha, pv, fadiga, status="", peso=None, ajuste_peso=0.0, extras=None):
    """O Deslocamento que vale hoje e a conta, linha por linha.

    Parte do Deslocamento da ficha (que já tem a raça e a Carga da criação) e só troca a parte
    da Carga se o peso mudou. Depois: perna mutilada, teto de pé incapacitado, Fadiga, PV.
    """
    extras = extras or {}
    conta, avisos = [], []
    base = int(ficha.get("deslocamento") or int(float(ficha.get("velocidade_basica") or 0)))
    conta.append(f"Deslocamento da ficha: {base}")
    limites = ficha.get("carga")
    peso_ficha = ficha.get("peso_total")
    if peso is None and ajuste_peso:
        peso = (peso_ficha or 0) + ajuste_peso
    if peso is not None and limites and peso_ficha is not None:
        antes, agora = nivel_carga(peso_ficha, limites), nivel_carga(peso, limites)
        if agora != antes:
            base -= agora - antes
            conta.append(f"Carga {peso:g} kg (nível {agora}) contra {peso_ficha:g} kg da ficha "
                         f"(nível {antes}): {-(agora - antes):+d}")
    elif limites and peso_ficha is not None:
        avisos.append(f"Carga lida da ficha ({peso_ficha:g} kg): confira itens largados ou pegos "
                      f"na campanha (--peso-atual).")
    s = simples(status)
    coxo = extras.get("perna_mutilada") or bool(re.search(r"\bcox[oa]\b|perna mutilad|perna.*incapacit", s))
    if coxo:
        base -= 3
        conta.append("Perna mutilada (coxo): -3 (MB, Perna Mutilada)")
    pe = extras.get("pe_incapacitado") or bool(re.search(r"\bpe\b.*incapacit|incapacit.*\bpe\b", s))
    if pe and base > 3:
        base = 3
        conta.append("Pé incapacitado: teto 3 (MB, Ferimentos)")
    metade = []
    if fadiga is not None and fadiga <= 3:
        metade.append(f"Fadiga {fadiga} (ST efetiva <= 3)")
    if pv is not None and 1 <= pv <= 3:
        metade.append(f"PV {pv} (1 a 3 restantes)")
    if metade:
        base = max(base, 0) // 2
        conta.append("Metade, arredondada para baixo: " + " e ".join(metade))
        if len(metade) > 1:
            avisos.append("Fadiga e PV baixos juntos: apliquei a metade uma só vez; o livro não diz que "
                          "acumula. Confirme com o Mestre.")
    if pv is not None and pv <= 0:
        avisos.append("PV 0 ou menos: teste de HT no início do turno para seguir consciente.")
    limite = max(1, base)
    if base < 1:
        conta.append("Sempre se pode andar 1 hexágono por turno (MB, Custos em Pontos de Movimento)")
    return {"valor": limite, "bruto": base, "conta": conta, "avisos": avisos}


# ---------------------------------------------------------------- terreno
def ler_terreno(raiz, mapa):
    f = Path(raiz) / TERRENO_JSON
    if not f.is_file():
        return {}
    try:
        return (json.loads(f.read_text(encoding="utf-8")).get(mapa) or {})
    except Exception:
        return {}


# tipo -> (custo extra por hexágono no Deslocamento, descrição)
TIPOS_TERRENO = {
    "terra": (0, "terra firme"),
    "margem": (0, "água rasa de margem, tratada como terra (decisão do Mestre)"),
    "rasa": (1, "água de 30 cm: custa o dobro (MB, Piso Ruim)"),
    "funda": (0, "água funda: 1 hexágono por turno e teste de Natação (MB, Piso Ruim e Natação)"),
    "ruim": (1, "piso ruim: +1 por hexágono"),
    "obstruido": (1, "obstruído: +1 por hexágono"),
    "incerta": (0, "água provável, ainda não decidida — tratada como terra, confirme com o Mestre"),
}


def tipo_do_hex(terreno, x, y):
    h = (terreno.get("hexes") or {}).get(f"{x},{y}")
    return (h or {}).get("tipo", "terra")


def classificar_imagem(imagem, colunas, linhas):
    """% de pixels de água por hexágono (azul-esverdeado mais forte que o vermelho)."""
    from PIL import Image
    im = Image.open(imagem).convert("RGB")
    w, h = im.size
    raio = w / (1.5 * colunas + 0.5)      # largura = raio x (1,5 C + 0,5)
    res = {}
    for c in range(colunas):
        for r in range(linhas):
            cx = raio + 1.5 * raio * c
            cy = math.sqrt(3) * raio * (r + 0.5 + 0.5 * (c & 1))
            n = a = 0
            for dx in (-15, -8, 0, 8, 15):
                for dy in (-15, -8, 0, 8, 15):
                    px, py = int(cx + dx), int(cy + dy)
                    if 0 <= px < w and 0 <= py < h:
                        p = im.getpixel((px, py))
                        n += 1
                        a += 1 if (p[2] > p[0] + 5 and p[1] > p[0]) else 0
            res[f"{c},{r}"] = round(100 * a / n) if n else 0
    return res


# ---------------------------------------------------------------- rota
def giro(a, b):
    d = (b - a) % 6
    return min(d, 6 - d)


def rota_minima(inicio, look_ini, fim, desl, terreno=None, extra_hex=0.0, ocupados=None, proibidos=None):
    """Dijkstra em (x, y, look) com as regras da manobra Deslocamento.

    Devolve (custo, [(x, y, look, custo_acumulado)]) para o melhor caminho até `fim`, ou None.
    Custo de entrar: frente 1 (virando para ele), lado/trás 2 sem virar, mais terreno e posição.
    """
    terreno = terreno or {}
    ocupados = ocupados or {}
    proibidos = proibidos or set()
    estado0 = (inicio[0], inicio[1], look_ini)
    dist, ant = {estado0: 0.0}, {}
    fila = [(0.0, estado0)]
    teto = max(desl * 3, hexes_entre(inicio, fim) * 3 + 6)
    while fila:
        custo, est = heapq.heappop(fila)
        if custo > dist.get(est, 1e9):
            continue
        x, y, look = est
        if (x, y) == tuple(fim):
            caminho, cur = [], est
            while cur in ant:
                caminho.append((cur[0], cur[1], cur[2], dist[cur]))
                cur = ant[cur]
            caminho.append((cur[0], cur[1], cur[2], 0.0))
            return custo, list(reversed(caminho))
        if custo > teto:
            continue
        passos = []
        for d in range(6):
            nx, ny = vizinho(x, y, d)
            if (nx, ny) in proibidos:
                continue
            extra = TIPOS_TERRENO.get(tipo_do_hex(terreno, nx, ny), (0, ""))[0] + extra_hex
            if (nx, ny) in ocupados:
                extra += 1
            rel = (d - look) % 6
            if rel in (0, 1, 5):                      # hexágonos da frente
                passos.append(((nx, ny, d), 1 + extra))          # entra virando para ele
                if rel != 0:
                    passos.append(((nx, ny, look), 2 + extra))   # passo lateral mantendo a direção
            else:                                     # lado ou trás
                passos.append(((nx, ny, look), 2 + extra))
        passos.append(((x, y, (look + 1) % 6), 1))     # virar um lado
        passos.append(((x, y, (look - 1) % 6), 1))
        for novo, c in passos:
            nc = custo + c
            if nc < dist.get(novo, 1e9):
                dist[novo], ant[novo] = nc, est
                heapq.heappush(fila, (nc, novo))
    return None


def custo_frente_final(custo, desl, look_chegada, look_pedido):
    """Virar no fim: grátis se gastou metade ou menos; senão, só um lado grátis (MB, Mudança de Direção)."""
    if look_pedido is None:
        return 0, "sem frente pedida"
    lados = giro(look_chegada, look_pedido)
    if lados == 0:
        return 0, "frente igual à da chegada"
    if custo <= desl / 2:
        return 0, f"{lados} lado(s) grátis: gastou metade ou menos dos pontos"
    extra = max(0, lados - 1)
    return extra, f"{lados} lado(s): 1 grátis (gastou mais da metade), {extra} a pagar"


def linha_reta(a, b):
    """Hexágonos de a até b (inclusive a), interpolação em cubo."""
    def cubo(p):
        q = p[0]
        r = p[1] - (p[0] // 2)
        return q, r, -q - r
    n = hexes_entre(a, b)
    ca, cb = cubo(a), cubo(b)
    fora = []
    for i in range(n + 1):
        t = i / n if n else 0
        f = [ca[k] + (cb[k] - ca[k]) * t + (1e-6 if k == 0 else -1e-6 if k == 1 else 0) for k in range(3)]
        rq, rr, rs = round(f[0]), round(f[1]), round(f[2])
        dq, dr, ds = abs(rq - f[0]), abs(rr - f[1]), abs(rs - f[2])
        if dq > dr and dq > ds:
            rq = -rr - rs
        elif dr > ds:
            rr = -rq - rs
        fora.append((rq, rr + (rq // 2)))
    return fora


def custo_posicao(posicao):
    """Extra por hexágono e teto de hexágonos pela posição (MB, Custos em Pontos de Movimento)."""
    p = simples(posicao)
    if "sentad" in p:
        return 0.0, 0, "sentado: não consegue se deslocar"
    if "deitad" in p or "caid" in p or "rolando" in p:
        return 0.0, 1, "deitado/caído: só 1 hexágono por turno (rastejando de bruços ou rolando)"
    if "ajoelh" in p:
        return 2.0, None, "ajoelhado: +2 por hexágono"
    if "rastej" in p:
        return 2.0, None, "rastejando: +2 por hexágono"
    if "agachad" in p:
        return 0.5, None, "agachado: +1/2 por hexágono"
    return 0.0, None, ""


# ---------------------------------------------------------------- validar
def validar(p):
    """Núcleo: um personagem, uma manobra. `p` é um dict (ver `calcular` e `turno`)."""
    ini, fim = tuple(p["de"]), tuple(p["para"])
    look_ini, look_fim = p.get("look_de"), p.get("look_para")
    cod = p["manobra"]
    desl = int(p["desl"])
    terreno = p.get("terreno") or {}
    ocupados = {tuple(k): v for k, v in (p.get("ocupados") or [])}
    avisos = list(p.get("avisos") or [])
    extra_pos, teto_pos, texto_pos = custo_posicao(p.get("posicao"))
    if texto_pos:
        avisos.append(texto_pos)
    rotulo, regra = MANOBRAS[cod]
    res = {"manobra": cod, "manobra_rotulo": rotulo, "regra": regra, "deslocamento": desl,
           "de": list(ini), "para_declarado": list(fim), "look_declarado": look_fim,
           "custo_roll6": p.get("custo_roll6"), "avisos": avisos}

    if ini == fim:
        res.update(veredito="sem_movimento", posicao_valida=list(ini), look_valido=look_fim,
                   corrigido=False, custo=0, rota=[list(ini)])
        return res

    dist_hex = hexes_entre(ini, fim)
    teto = teto_hex(cod, desl)
    if teto_pos is not None and teto is not None:
        teto = min(teto, teto_pos)

    # terreno
    tipos = {}
    for pt in linha_reta(ini, fim):
        t = tipo_do_hex(terreno, *pt)
        if t != "terra":
            tipos[f"{pt[0]},{pt[1]}"] = t
    res["terreno_na_rota"] = tipos

    if cod == "deslocamento":
        r = rota_minima(ini, look_ini if look_ini is not None else 0, fim, desl, terreno,
                        extra_hex=extra_pos, ocupados=ocupados)
        if r is None:
            res.update(veredito="impossivel", posicao_valida=list(ini), look_valido=look_ini,
                       corrigido=True, custo=None, rota=[list(ini)])
            avisos.append("Sem rota até o destino.")
            return res
        custo, caminho = r
        look_cheg = caminho[-1][2]
        extra_giro, txt_giro = custo_frente_final(custo, desl, look_cheg, look_fim)
        total = custo + extra_giro
        # a rota por hexágono: tira os giros no lugar (mesma casa em sequência)
        passos = []
        for c in caminho:
            if not passos or (passos[-1][0], passos[-1][1]) != (c[0], c[1]):
                passos.append(c)
            else:
                passos[-1] = c                       # fica com o estado depois de girar
        res.update(custo=total, custo_andar=custo, custo_virar_no_fim=extra_giro, texto_virar=txt_giro,
                   rota=[[c[0], c[1]] for c in passos])
        # limites que cortam a rota: posição (deitado) e água funda (1 hexágono por turno)
        corte, porque = None, ""
        if teto_pos is not None:
            corte, porque = teto_pos, "a posição só deixa andar " + str(teto_pos) + " hexágono(s)"
        if tipo_do_hex(terreno, *ini) == "funda":
            corte, porque = (1 if corte is None else min(corte, 1)), "já está em água funda: 1 hexágono por turno"
        for i, c in enumerate(passos[1:], start=1):
            if tipo_do_hex(terreno, c[0], c[1]) == "funda" and i < len(passos) - 1:
                if corte is None or i < corte:
                    corte, porque = i, "a rota entra em água funda no hexágono " + str(i) + ": ali o turno acaba"
                break
        if corte is not None and len(passos) - 1 > corte:
            ponto = passos[corte]
            res.update(veredito="corrigir", corrigido=True, posicao_valida=[ponto[0], ponto[1]],
                       look_valido=ponto[2], custo=ponto[3], motivo=porque)
        elif total <= desl + 1e-9:
            res.update(veredito="ok", corrigido=False, posicao_valida=list(fim),
                       look_valido=look_fim if look_fim is not None else look_cheg)
        elif custo <= desl + 1e-9:
            # chega ao destino; só a frente pedida não cabe: vira o que os pontos que sobram pagam
            lados_livres = (6 if custo <= desl / 2 else 1) + int(desl - custo + 1e-9)
            falta = giro(look_cheg, look_fim)
            passo = min(lados_livres, falta)
            frente = look_cheg
            if passo:
                horario = (look_fim - look_cheg) % 6 <= 3
                frente = (look_cheg + (passo if horario else -passo)) % 6
            res.update(veredito="corrigir", corrigido=True, posicao_valida=list(fim), look_valido=frente,
                       custo=custo + max(0, passo - (6 if custo <= desl / 2 else 1)),
                       motivo=f"chega ao destino, mas virar {falta} lado(s) no fim não cabe nos pontos; "
                              f"vira só {passo}")
        else:
            ponto = passos[0]
            for c in passos:
                if c[3] <= desl + 1e-9:
                    ponto = c
            res.update(veredito="corrigir", corrigido=True, posicao_valida=[ponto[0], ponto[1]],
                       look_valido=ponto[2], custo=ponto[3],
                       motivo=f"a rota custa {custo:g} pontos e o Deslocamento é {desl}")
        if tuple(res.get("posicao_valida") or ()) and tipo_do_hex(terreno, *res["posicao_valida"]) == "funda":
            res["natacao"] = True
        if tipo_do_hex(terreno, *ini) == "funda":
            res["natacao"] = True
        return res

    # manobras com teto fixo de hexágonos
    custo = dist_hex
    res.update(custo=custo, teto_hex=teto)
    reta = linha_reta(ini, fim)
    res["rota"] = [list(c) for c in reta]
    if teto == 0:
        res.update(veredito="corrigir", corrigido=True, posicao_valida=list(ini), look_valido=look_ini,
                   motivo="a manobra não permite deslocamento")
    elif dist_hex <= teto:
        res.update(veredito="ok", corrigido=False, posicao_valida=list(fim),
                   look_valido=look_fim if look_fim is not None else look_ini)
    else:
        ponto = reta[teto]
        res.update(veredito="corrigir", corrigido=True, posicao_valida=list(ponto), look_valido=look_fim,
                   motivo=f"{rotulo} permite {teto} hexágono(s) e a peça andou {dist_hex}")
    if tuple(res["posicao_valida"]) in ocupados:
        avisos.append(f"O hexágono final está ocupado por {ocupados[tuple(res['posicao_valida'])]}: "
                      "só amigos dividem hexágono (até 4).")
    if tipo_do_hex(terreno, *res["posicao_valida"]) == "funda":
        res["natacao"] = True
    return res


# ---------------------------------------------------------------- modo turno
def _roll6():
    return _carregar("roll6", ROLL6_PY)


def _contexto():
    return _carregar("contexto", CONTEXTO_PY)


def entradas_de_movimento(entradas, character_id, map_id):
    """Movimentos do personagem neste mapa, na ordem, e os que foram parar em outro mapa."""
    mov, fora = [], []
    for e in entradas:
        if e.get("characterId") != character_id or e.get("turnType") != 1:
            continue
        (mov if e.get("mapId") == map_id else fora).append(e)
    return mov, fora


def turno(args):
    raiz = Path(args.raiz).resolve()
    roll6, ctx = _roll6(), _contexto()
    mapa = roll6.mapeamento(raiz)
    if not mapa:
        raise SystemExit("Sem campanha/roll6.json — a campanha ativa não está ligada ao roll6.")
    cid = mapa["campaignId"]
    c = roll6.cliente()
    dados = c.chamar("get_turn_data", {"campaignId": cid, "turnNo": args.turno})
    em_andamento = dados["turnNo"] == dados["currentTurn"]
    entradas = (c.chamar("get_turn_state", {"campaignId": cid})["entries"] if em_andamento
                else roll6.lista(c.chamar("list_turn_entries", {"campaignId": cid, "turnNo": dados["turnNo"]})))
    map_id = dados.get("mapId")
    indice = next((i for i, l in (mapa.get("mapas") or {}).items() if l.get("mapId") == map_id), None)
    terreno = ler_terreno(raiz, indice) if indice else {}
    forcadas = {}
    for f in args.manobra or []:
        nome, _, cod = f.partition("=")
        forcadas[simples(nome)] = cod.strip()
    ocupados = {}
    for ch in dados["characters"]:
        if ch.get("x") is not None:
            ocupados[(ch["x"], ch["y"])] = ch["name"]
    for n in dados["npcs"]:
        if n.get("x") is not None:
            ocupados[(n["x"], n["y"])] = n["name"]
    saida = []
    for ch in dados["characters"]:
        nome = ch["name"]
        mov, fora = entradas_de_movimento(entradas, ch["characterId"], map_id)
        acoes = [e["description"] for e in entradas
                 if e.get("characterId") == ch["characterId"] and e.get("turnType") == 2 and e.get("description")]
        item = {"nome": nome, "characterId": ch["characterId"], "acoes": acoes,
                "movimentos": [{"de": [e["beforeX"], e["beforeY"]], "para": [e["x"], e["y"]],
                                "look_de": e.get("beforeLook"), "look_para": e.get("look"),
                                "pontos_roll6": e.get("moved"), "mapId": e.get("mapId")} for e in mov],
                "outro_mapa": [{"mapId": e.get("mapId"), "de": [e["beforeX"], e["beforeY"]],
                                "para": [e["x"], e["y"]]} for e in fora]}
        avisos = []
        if fora:
            avisos.append(f"Movimento registrado em outro mapa ({sorted({e.get('mapId') for e in fora})}); "
                          f"a peça do mapa {map_id} não saiu de lugar. Avise o jogador.")
        if not mov:
            item.update(veredito="sem_movimento", avisos=avisos)
            saida.append(item)
            continue
        ficha = ctx.ler_ficha(nome, raiz) or {}
        d = deslocamento_atual(ficha, ch.get("currentLife"), ch.get("currentEnergy"), ch.get("status") or "",
                               peso=args.peso_atual.get(simples(nome)) if args.peso_atual else None) \
            if ficha else {"valor": int(ch.get("move") or 1), "conta": ["sem ficha local: usei o move do roll6"],
                           "avisos": ["Sem ficha local."]}
        status_posicao = (ch.get("status") or "")
        postura = {1: "em pe", 2: "caido", 3: "fora de combate"}.get(ch.get("posture"), "em pe")
        man = classificar_manobra(acoes)
        cod = forcadas.get(simples(nome)) or man["proposta"]
        item.update(manobra_detectada=man, deslocamento=d)
        if cod is None:
            cod = "deslocamento"
            avisos.append("Sem manobra reconhecida na declaração: tratei como Deslocamento. Confirme.")
        if cod not in MANOBRAS:
            raise SystemExit(f"Manobra desconhecida: {cod}. Use uma de: {', '.join(MANOBRAS)}")
        primeiro, ultimo = mov[0], mov[-1]
        ocup = [[list(k), v] for k, v in ocupados.items() if v != nome]
        parametros = {"de": [primeiro["beforeX"], primeiro["beforeY"]], "look_de": primeiro.get("beforeLook"),
                      "para": [ultimo["x"], ultimo["y"]], "look_para": ultimo.get("look"),
                      "manobra": cod, "desl": d["valor"], "terreno": terreno,
                      "posicao": ("agachado" if re.search(r"agachad", simples(status_posicao))
                                  else "ajoelhado" if re.search(r"ajoelhad", simples(status_posicao))
                                  else "caido" if postura == "caido" else ""),
                      "ocupados": ocup, "avisos": avisos + d.get("avisos", []),
                      "custo_roll6": sum(int(e.get("moved") or 0) for e in mov)}
        if len(mov) > 1:
            parametros["avisos"].append(f"{len(mov)} movimentos no turno; tratei início do 1º e fim do último.")
        r = validar(parametros)
        item.update(r)
        item["desl_conta"] = d["conta"]
        if man["ambigua"]:
            item["avisos"].append("A declaração mistura Deslocamento com outra manobra: pergunte ao Mestre "
                                  "(--manobra \"Nome=codigo\" refaz a conta).")
            item["alternativas"] = {}
            for alt in man["candidatas"]:
                if alt == cod:
                    continue
                pa = dict(parametros, manobra=alt)
                ra = validar(pa)
                item["alternativas"][alt] = {"veredito": ra["veredito"], "posicao_valida": ra["posicao_valida"],
                                             "custo": ra.get("custo")}
        saida.append(item)
    return {"campaignId": cid, "turno": dados["turnNo"], "mapId": map_id, "indice_local": indice,
            "terreno_arquivo": (TERRENO_JSON.as_posix() if terreno else None), "personagens": saida}


def rotulo(xy, look=None):
    return f"({xy[0]},{xy[1]})" + (f" olhando {NOME_LOOK.get(look)}" if look is not None else "")


def imprimir_turno(r):
    print(f"VALIDAR MOVIMENTO · campanha {r['campaignId']} · turno {r['turno']} · mapa {r['mapId']}"
          + (f" ({r['indice_local']})" if r.get("indice_local") else "")
          + ("" if r.get("terreno_arquivo") else " · sem terreno.json (água e terreno não conferidos)"))
    for p in r["personagens"]:
        print(f"\n## {p['nome']}")
        for a in p.get("acoes", []):
            print(f"  declarou: {a}")
        for o in p.get("outro_mapa", []):
            print(f"  ! movimento no mapa {o['mapId']}: {o['de']} -> {o['para']} (não vale aqui)")
        if p["veredito"] == "sem_movimento":
            print("  sem movimento neste mapa")
            for a in p.get("avisos", []):
                print(f"  ! {a}")
            continue
        for linha in p.get("desl_conta", []):
            print(f"    - {linha}")
        print(f"  manobra: {p['manobra_rotulo']}  ({p['regra']})")
        print(f"  Deslocamento válido: {p['deslocamento']}"
              + (f" · teto {p['teto_hex']} hex" if p.get("teto_hex") is not None else ""))
        print(f"  andou: {rotulo(p['de'])} -> {rotulo(p['para_declarado'], p.get('look_declarado'))}; "
              f"custo {p.get('custo')} (roll6 contou {p.get('custo_roll6')})")
        if p.get("texto_virar"):
            print(f"  virar no fim: {p['texto_virar']}")
        if p.get("terreno_na_rota"):
            print("  terreno na rota: " + ", ".join(f"({k}) {v}" for k, v in p["terreno_na_rota"].items()))
        if p["veredito"] == "ok":
            print("  VEREDITO: OK, vale o destino")
        elif p["veredito"] == "sem_movimento":
            print("  VEREDITO: sem movimento")
        else:
            print(f"  VEREDITO: CORRIGIR -> {rotulo(p['posicao_valida'], p.get('look_valido'))}"
                  f" ({p.get('motivo', '')})")
        if p.get("natacao"):
            print("  ! termina em água funda: teste de Natação (MB, Natação), 1 hexágono por turno")
        for a in p.get("avisos", []):
            print(f"  ! {a}")
        for cod, alt in (p.get("alternativas") or {}).items():
            print(f"  alternativa se for {MANOBRAS[cod][0]}: {alt['veredito']} -> {alt['posicao_valida']}")


# ---------------------------------------------------------------- modo calcular
def calcular(args):
    raiz = Path(args.raiz).resolve()
    terreno = ler_terreno(raiz, args.mapa) if args.mapa else {}

    def xy(t):
        a, b = t.split(",")
        return [int(a), int(b)]
    p = {"de": xy(args.de), "para": xy(args.para), "look_de": args.look_de, "look_para": args.look_para,
         "manobra": args.manobra, "desl": args.desl, "terreno": terreno, "posicao": args.posicao,
         "ocupados": [[xy(o.split("=")[0]), o.split("=")[1]] for o in (args.ocupado or [])]}
    return validar(p)


# ---------------------------------------------------------------- modo terreno
def terreno_cmd(args):
    raiz = Path(args.raiz).resolve()
    f = raiz / TERRENO_JSON
    tudo = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}
    m = tudo.setdefault(args.mapa, {"hexes": {}})
    if args.imagem:
        m["imagem"] = args.imagem
    if args.colunas:
        m["colunas"] = args.colunas
    if args.linhas:
        m["linhas"] = args.linhas
    if args.imagem or m.get("imagem"):
        pct = classificar_imagem(raiz / m["imagem"], int(m["colunas"]), int(m["linhas"]))
        m["agua_pct"] = {k: v for k, v in pct.items() if v >= 10}
        for k, v in pct.items():
            ja = m["hexes"].get(k)
            if ja and ja.get("decidido"):
                continue
            if v >= 70:
                m["hexes"][k] = {"tipo": "funda", "pct": v, "decidido": False}
            elif v >= 15:
                m["hexes"][k] = {"tipo": "incerta", "pct": v, "decidido": False}
            else:
                m["hexes"].pop(k, None)
    for d in args.decidir or []:
        k, _, tipo = d.partition("=")
        if tipo not in TIPOS_TERRENO:
            raise SystemExit(f"Tipo desconhecido: {tipo}. Use: {', '.join(TIPOS_TERRENO)}")
        pct = (m.get("agua_pct") or {}).get(k.strip())
        m["hexes"][k.strip()] = {"tipo": tipo, "pct": pct, "decidido": True,
                                 "obs": "decisão do Mestre"}
    if args.gravar or args.decidir:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(tudo, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        print(f"gravado em {TERRENO_JSON.as_posix()} ({args.mapa}: {len(m['hexes'])} hexágonos marcados)")
    incertas = sorted(k for k, v in m["hexes"].items() if v.get("tipo") == "incerta")
    fundas = sorted(k for k, v in m["hexes"].items() if v.get("tipo") == "funda")
    print(f"{args.mapa}: {len(fundas)} hexágono(s) de água funda, {len(incertas)} incerto(s) (margem?).")
    if incertas:
        print("Incertos (decida com --decidir \"x,y=margem|rasa|funda|terra\"): " + "; ".join(
            f"({k}) {m['hexes'][k].get('pct')}%" for k in incertas))
    return m


def main():
    ap = argparse.ArgumentParser(description="Valida o movimento dos personagens pelas regras do MB.")
    ap.add_argument("--raiz", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("turno", help="Valida os movimentos do turno em andamento do roll6")
    t.add_argument("--turno", type=int, default=None)
    t.add_argument("--manobra", action="append", help='"Nome=codigo" força a manobra de um personagem')
    t.add_argument("--peso-atual", type=json.loads, default=None, help='{"jah": 14.5}: peso carregado hoje')
    t.add_argument("--json", action="store_true")
    c = sub.add_parser("calcular", help="Uma conta avulsa, sem o roll6")
    c.add_argument("--de", required=True)
    c.add_argument("--para", required=True)
    c.add_argument("--look-de", type=int, default=None)
    c.add_argument("--look-para", type=int, default=None)
    c.add_argument("--manobra", required=True, choices=sorted(MANOBRAS))
    c.add_argument("--desl", type=int, required=True)
    c.add_argument("--posicao", default="")
    c.add_argument("--mapa", default=None)
    c.add_argument("--ocupado", action="append", help='"x,y=Nome"')
    c.add_argument("--json", action="store_true")
    g = sub.add_parser("terreno", help="Classifica a água do mapa pela imagem e guarda as decisões do Mestre")
    g.add_argument("--mapa", required=True)
    g.add_argument("--imagem")
    g.add_argument("--colunas", type=int)
    g.add_argument("--linhas", type=int)
    g.add_argument("--decidir", action="append")
    g.add_argument("--gravar", action="store_true")
    a = ap.parse_args()
    if a.cmd == "turno":
        r = turno(a)
        print(json.dumps(r, ensure_ascii=False, indent=2)) if a.json else imprimir_turno(r)
    elif a.cmd == "calcular":
        r = calcular(a)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            imprimir_turno({"campaignId": "-", "turno": "-", "mapId": a.mapa, "indice_local": None,
                            "personagens": [dict(r, nome="(avulso)", acoes=[], desl_conta=[])]})
    else:
        terreno_cmd(a)


if __name__ == "__main__":
    main()
