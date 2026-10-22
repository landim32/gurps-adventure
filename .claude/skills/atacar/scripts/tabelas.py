#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tabelas do Sistema Avancado de Combate — MB, cap. 14, e os quadros do cap. 24.

So dados, sem logica: partes do corpo, golpes fulminantes, erros criticos e manobras.
Transcrito de livros/gurps-mb-3ed/21-quadros-e-tabelas.md e 11-combate-avancado.md.
"""

# ---------------------------------------------------------------- partes do corpo
# "redutor" sai do NH do atacante. "rd_natural" e a RD que a propria carne/osso da.
# "mult" substitui o multiplicador normal do tipo de dano quando indicado.
# "teto" limita o dano que aquele local aceita: o excedente e desperdicado.
LOCAIS = {
    "cerebro": {
        "nome": "Cérebro", "redutor": -7, "aleatorio": "4 ou menos",
        "rd_natural": 2, "mult_todos": 4, "teto": None,
        "armadura": "cabeca",
        "obs": "O crânio dá RD 2, somada à armadura. O que passa é multiplicado por 4, "
               "seja qual for o tipo de dano. Atordoa se a perda passar de HT/3; "
               "nocauteia se passar de HT/2. Não há teto de dano no cérebro.",
    },
    "cabeca": {
        "nome": "Cabeça", "redutor": -5, "aleatorio": "5",
        "rd_natural": 0, "teto_mult_ht": 3,
        "armadura": "cabeca",
        "obs": "Golpe fulminante na cabeça usa a Tabela de Golpes Fulminantes na Cabeça. "
               "Exige teste de HT para não ser nocauteado.",
    },
    "olhos": {
        "nome": "Olhos", "redutor": -9, "aleatorio": None,
        "rd_natural": 0, "mult_todos": 4, "teto": None,
        "armadura": "cabeca",
        "obs": "Mais de 2 pontos de dano cegam o olho. Golpe perfurante ou projétil "
               "menor que 2,5 cm atinge o cérebro automaticamente, mas ainda contra a "
               "RD do crânio.",
    },
    "olhos-viseira": {
        "nome": "Olhos (pela viseira)", "redutor": -10, "aleatorio": None,
        "rd_natural": 0, "mult_todos": 4, "teto": None,
        "armadura": None,
        "obs": "Pela viseira a armadura não protege — nem o elmo, nem a RD do crânio.",
    },
    "braco": {
        "nome": "Braço", "redutor": -2, "aleatorio": "8 (o da arma)",
        "rd_natural": 0, "teto_div_ht": 2, "incapacita": True,
        "armadura": "bracos",
        "obs": "Dano maior que HT/2 incapacita o braço; o excedente é desperdiçado. "
               "Perfurante não ganha bônus de dano em membro.",
    },
    "braco-escudo": {
        "nome": "Braço do escudo", "redutor": -4, "aleatorio": "6",
        "rd_natural": 0, "teto_div_ht": 2, "incapacita": True,
        "armadura": "bracos", "obs": "Como o braço, e mais difícil de alcançar.",
    },
    "mao": {
        "nome": "Mão", "redutor": -4, "aleatorio": "7",
        "rd_natural": 0, "teto_div_ht": 3, "incapacita": True,
        "armadura": "maos",
        "obs": "Dano maior que HT/3 incapacita a mão. Perfurante não ganha bônus.",
    },
    "mao-escudo": {
        "nome": "Mão do escudo", "redutor": -8, "aleatorio": None,
        "rd_natural": 0, "teto_div_ht": 3, "incapacita": True,
        "armadura": "maos", "obs": "Como a mão, atrás do escudo.",
    },
    "tronco": {
        "nome": "Tronco", "redutor": 0, "aleatorio": "9 a 11",
        "rd_natural": 0, "teto_perf_ht": 1,
        "armadura": "tronco",
        "obs": "Nada de especial. Golpe de ponta ou bala que passe de HT de dano "
               "atravessa a vítima e o excesso se perde.",
    },
    "orgaos-vitais": {
        "nome": "Órgãos vitais", "redutor": -3, "aleatorio": "17 ou mais",
        "rd_natural": 0, "mult_perf": 3, "teto_mult_ht": 3,
        "armadura": "tronco",
        "obs": "Só se alcança com arma perfurante — o dano que passa da armadura é "
               "triplicado. Exceção: soco ou pontapé no plexo/virilha conta como "
               "golpe contundente nos vitais. Contundente nos vitais exige teste de "
               "HT para não nocautear.",
    },
    # REGRA DA CASA (CLAUDE.md): o pescoco da 4a edicao (MB Campanhas, p. 552). A 3a
    # edicao nao tem este local; o Mestre adotou o da 4a. Nao entra no sorteio de 3d.
    "pescoco": {
        "nome": "Pescoço", "redutor": -5, "aleatorio": None,
        "rd_natural": 0, "mult_tipo": {"cont": 1.5, "corte": 2.0},
        "armadura": "pescoco",
        "obs": "Regra da casa (GURPS 4ª ed.): -5 para acertar; contusão ×1,5 e corte ×2 "
               "sobre o que passar da armadura; perfuração e os demais com o "
               "multiplicador normal do tipo. Contusão pela frente acima de HT/2 esmaga a "
               "traqueia (sufocamento); corte acima de 3×HT pode decapitar.",
    },
    "perna": {
        "nome": "Perna", "redutor": -2, "aleatorio": "13, 14",
        "rd_natural": 0, "teto_div_ht": 2, "incapacita": True,
        "armadura": "pernas",
        "obs": "Dano maior que HT/2 incapacita a perna. Perfurante não ganha bônus.",
    },
    "perna-distante": {
        "nome": "Perna distante", "redutor": -2, "aleatorio": "12",
        "rd_natural": 0, "teto_div_ht": 2, "incapacita": True,
        "armadura": "pernas", "obs": "Como a perna.",
    },
    "pe": {
        "nome": "Pé", "redutor": -4, "aleatorio": "15, 16",
        "rd_natural": 0, "teto_div_ht": 3, "incapacita": True,
        "armadura": "pes",
        "obs": "Dano maior que HT/3 incapacita o pé. Perfurante não ganha bônus.",
    },
}

APELIDOS = {
    "pescoço": ("pescoco", None), "garganta": ("pescoco", None), "nuca": ("pescoco", None),
    "cabeça": ("cabeca", None), "crânio": ("cerebro", None), "cranio": ("cerebro", None),
    "peito": ("tronco", None), "corpo": ("tronco", None), "torso": ("tronco", None),
    "barriga": ("tronco", None), "vitais": ("orgaos-vitais", None),
    "olho": ("olhos", None), "braços": ("braco", None), "bracos": ("braco", None),
    "pernas": ("perna", None), "mãos": ("mao", None), "maos": ("mao", None),
    "pés": ("pe", None), "pes": ("pe", None), "cabeco": ("cabeca", None),
}

# Sorteio de local aleatorio: 3d, MB pag. 203
ALEATORIO = [(4, "cerebro"), (5, "cabeca"), (6, "braco-escudo"), (7, "mao"),
             (8, "braco"), (11, "tronco"), (12, "perna-distante"), (14, "perna"),
             (16, "pe"), (18, "orgaos-vitais")]

# ---------------------------------------------------------- golpes fulminantes
# "dano": multiplicador sobre o dano basico. "ignora_armadura": passa por cima da RD.
FULMINANTE = {
    3: {"txt": "Nocauteia se atingiu o tronco (teste de HT a cada 30 min para acordar); "
               "em qualquer outro lugar, triplo do dano.", "dano": 3, "nocaute_tronco": True},
    4: {"txt": "O golpe ultrapassa a armadura e provoca dano normal.", "ignora_armadura": True},
    5: {"txt": "Triplo do dano normal.", "dano": 3},
    6: {"txt": "Dobro do dano normal.", "dano": 2},
    7: {"txt": "Dano normal, e a vítima fica atordoada até passar num teste de HT.",
        "atordoa": True},
    8: {"txt": "Em braço, perna, mão ou pé: dano normal e o membro fica incapacitado "
               "seja qual for o dano — mas é choque nevrálgico, que passa em seis turnos "
               "(se o dano bastar para inutilizar de vez, não passa). Em outro lugar, "
               "dano normal.", "incapacita_membro": True},
    9: {"txt": "Dano normal apenas."},
    10: {"txt": "Dano normal apenas."},
    11: {"txt": "Dano normal apenas."},
    12: {"txt": "Como o 8: membro incapacitado por choque nevrálgico, que passa em "
                "seis turnos.", "incapacita_membro": True},
    13: {"txt": "O golpe ultrapassa a armadura e provoca dano normal.", "ignora_armadura": True},
    14: {"txt": "Em braço, perna, mão ou pé: dano normal e o membro fica incapacitado, "
                "seja qual for o dano. Em outro lugar, dano normal.",
         "incapacita_membro": True, "permanente": True},
    15: {"txt": "A arma do oponente cai, e ele ainda recebe o dano normal.",
         "derruba_arma": True},
    16: {"txt": "Dobro do dano normal.", "dano": 2},
    17: {"txt": "Triplo do dano normal.", "dano": 3},
    18: {"txt": "Nocauteia se atingiu o tronco (teste de HT a cada 30 min); em qualquer "
               "outro lugar, triplo do dano.", "dano": 3, "nocaute_tronco": True},
}

FULMINANTE_CABECA = {
    3: {"txt": "O oponente é MORTO instantaneamente!", "morte": True},
    4: {"txt": "O oponente é nocauteado. Teste de HT a cada 30 minutos para acordar.",
        "nocaute": True},
    5: {"txt": "O oponente é nocauteado. Teste de HT a cada 30 minutos para acordar.",
        "nocaute": True},
    6: {"txt": "Atingido nos dois olhos: cego. Use as regras de incapacitação (um teste "
               "por olho). Fica atordoado e luta com DX-10 pelo resto da batalha.",
        "atordoa": True},
    7: {"txt": "Uma das vistas cegada. Regras de incapacitação para saber se cura. Fica "
               "atordoado e luta com DX-2 pelo resto da batalha.", "atordoa": True},
    8: {"txt": "Desequilibrado: no próximo turno se defende normalmente, mas não faz "
               "mais nada. O golpe provoca dano normal."},
    9: {"txt": "Dano normal na cabeça apenas."},
    10: {"txt": "Dano normal na cabeça apenas."},
    11: {"txt": "Dano normal na cabeça apenas."},
    12: {"txt": "Arma contundente: dano normal e surdez por 24 h. Arma cortante ou "
                "perfurante: só 1 ponto de vida, mas a face fica marcada.",
         "especial_tipo": True},
    13: {"txt": "Arma contundente: dano normal e surdez talvez permanente (regras de "
                "incapacitação). Cortante ou perfurante: só 2 pontos de vida, e a face "
                "fica muito marcada.", "especial_tipo": True},
    14: {"txt": "Dano normal na cabeça. A vítima vacila e deixa cair a arma.",
         "derruba_arma": True},
    15: {"txt": "Dano normal na cabeça, e a vítima fica atordoada.", "atordoa": True},
    16: {"txt": "Dano normal na cabeça, e a vítima fica atordoada.", "atordoa": True},
    17: {"txt": "Dano normal na cabeça, e a vítima fica atordoada.", "atordoa": True},
    18: {"txt": "Dano normal na cabeça, e a vítima fica atordoada.", "atordoa": True},
}

ERRO_CRITICO = {
    3: "Sua arma se QUEBRA e fica inutilizada. Maças, manguais, marretas e outras armas "
       "contundentes sólidas, armas mágicas e armas finamente trabalhadas são exceção: "
       "role de novo, e só quebra se sair «arma quebrada» outra vez.",
    4: "Sua arma se QUEBRA e fica inutilizada (mesma exceção do 3).",
    5: "Você atinge a SI MESMO num braço ou perna (1d: 1-3 esquerdo, 4-6 direito), dano "
       "cheio. Se era arma perfurante ou de longo alcance, role de novo.",
    6: "Você atinge a si mesmo num braço ou perna, mas só METADE do dano.",
    7: "Perdeu o equilíbrio: não faz nada até o próximo turno, e todas as defesas ativas "
       "ficam com -2 até lá.",
    8: "A arma gira na mão. Um turno extra para prepará-la de novo.",
    9: "Você DERRUBOU a arma. Arma barata teria se quebrado.",
    10: "Você DERRUBOU a arma. Arma barata teria se quebrado.",
    11: "Você DERRUBOU a arma. Arma barata teria se quebrado.",
    12: "A arma gira na mão. Um turno extra para prepará-la de novo.",
    13: "Perdeu o equilíbrio: não faz nada até o próximo turno, com -2 em todas as "
        "defesas ativas até lá.",
    14: "A arma VOA da sua mão e cai a 1d metros (50% para frente, 50% para trás). Quem "
        "estiver no ponto de queda faz teste de DX ou leva metade do dano da arma. Se o "
        "ataque era perfurante, você apenas derrubou a arma.",
    15: "Você ESTIROU O OMBRO: o braço da arma fica inútil pelo resto do encontro. Não "
        "precisa largar a arma, mas não pode usá-la para atacar nem defender por 30 min.",
    16: "Você CAIU! (Com arma de longo alcance, use o 7 no lugar.)",
    17: "Sua arma se QUEBRA (veja o 3).",
    18: "Sua arma se QUEBRA (veja o 3).",
}

DESARMADO_ERRO = ("Combatente desarmado ignora «arma quebrada», «arma derrubada» e «arma "
                  "gira na mão»: em vez disso sofre 1d-3 de dano na mão ou pé que golpeou.")

# ------------------------------------------------------------------- manobras
# "nh": bonus no NH do ataque. "dano": bonus no dano. "defesa_ativa": se pode defender.
MANOBRAS = {
    "ataque": {
        "nome": "Ataque (Avançar e Atacar)", "nh": 0, "dano": 0, "defesa_ativa": True,
        "obs": "Avança um hexágono em qualquer direção e usa a arma. Defende normalmente.",
    },
    "ataque-total-bonus": {
        "nome": "Ataque Total (+4 no NH)", "nh": 4, "dano": 0, "defesa_ativa": False,
        "obs": "Sem NENHUMA defesa ativa até o próximo turno — só a passiva. Move-se "
               "até 2 hexágonos ou metade do Deslocamento, o que for maior, e não pode "
               "mudar de direção no fim.",
    },
    "ataque-total-dano": {
        "nome": "Ataque Total (+2 no dano)", "nh": 0, "dano": 2, "defesa_ativa": False,
        "obs": "NH normal, 2 pontos a mais de dano se acertar. Sem defesa ativa.",
    },
    "ataque-total-duplo": {
        "nome": "Ataque Total (dois ataques)", "nh": 0, "dano": 0, "defesa_ativa": False,
        "obs": "Dois ataques no mesmo inimigo, só com duas armas preparadas ou uma arma "
               "que não fica despreparada. Rode o comando duas vezes. Sem defesa ativa.",
    },
    "ataque-total-finta": {
        "nome": "Ataque Total (finta e ataque)", "nh": 0, "dano": 0, "defesa_ativa": False,
        "obs": "A finta é uma Disputa Rápida — resolva com a skill fintar e traga o "
               "redutor como --alvo-defesa-mod negativo. Sem defesa ativa.",
    },
    "aguardar": {
        "nome": "Aguardar", "nh": 0, "dano": 0, "defesa_ativa": True,
        "obs": "Ataque normal quando o oponente entra no raio de ação. Defende normalmente.",
    },
    # MB, p. 105, "Golpe Molinete": quem gasta a rodada numa manobra Deslocamento só golpeia
    # de Molinete, e isso tem de ser DECLARADO. O golpe leva o PIOR entre -5 e NH máximo 9,
    # não escolhe parte do corpo (o atacar.py sorteia) e só vale para arma de mão.
    "movimento-e-ataque": {
        "nome": "Deslocamento e golpe Molinete", "nh": -5, "dano": 0, "defesa_ativa": True,
        "nh_maximo": 9, "local_sorteado": True,
        "obs": "Golpe Molinete (MB, p. 105): o pior entre -5 e NH máximo 9; o ponto de impacto é "
               "sorteado, não escolhido; só arma de mão. Defesa e dano normais.",
    },
    "precipitado": {
        "nome": "Ataque precipitado", "nh": -4, "dano": 0, "defesa_ativa": True,
        "obs": "-4 por atacar com a mão inábil. Sem penalidade para ambidestros.",
    },
}

# Manobra do lado que se defende
MANOBRAS_DEFESA = {
    "normal": {"nome": "manobra normal", "defesas": 1, "mod": 0},
    "defesa-total": {"nome": "Defesa Total", "defesas": 2, "mod": 0,
                     "obs": "Duas jogadas de defesa DIFERENTES contra o mesmo ataque. "
                            "Nunca mais de dois aparar por arma nem dois bloqueios."},
    "ataque-total": {"nome": "Ataque Total no turno passado", "defesas": 0, "mod": 0,
                     "obs": "Quem fez Ataque Total não tem defesa ativa nenhuma."},
    "atordoado": {"nome": "atordoado", "defesas": 1, "mod": -4,
                  "obs": "Atordoado: -4 em todas as defesas ativas e não faz mais nada."},
    "surpreendido": {"nome": "surpreendido / não sabe do ataque", "defesas": 0, "mod": 0,
                     "obs": "Sem defesa ativa: golpe pelas costas, emboscada, "
                            "inconsciente. A defesa passiva continua valendo."},
}

# ----------------------------------------------------------- tipos de dano
TIPOS_DANO = {
    "cont": {"nome": "contusão", "mult": 1.0, "como": "sem bônus"},
    "corte": {"nome": "corte", "mult": 1.5, "como": "+50% do que passar da armadura"},
    "perf": {"nome": "perfuração", "mult": 2.0, "como": "dobra o que passar da armadura"},
}

# ------------------------------------------------- armas que precisam ser preparadas
# MB, cap. 14, "Preparar" (p. 104) e a Tabela de Armas de Mao (cap. 24, p. 206):
#   - espada, faca, bastao, lanca: balanceadas, nao precisam ser preparadas de novo;
#   - arma de mao DESBALANCEADA (machado, maca, mangual, picareta, martelo, malho...)
#     fica DESPREPARADA depois de usada para ATACAR ou para APARAR; 1 turno para
#     prepara-la de novo (so se ataca em turnos alternados);
#   - arma de haste (alcance 3): 2 turnos para preparar apos golpe em balanco, 1 apos
#     golpe de ponta; NAO fica despreparada ao aparar (apara-se com o fuste);
#   - cimitarra de uma mao: 1 turno para preparar apos golpear (nao apos aparar).
# Preparacao Rapida por ST (p. 104): ST 5 acima da ST minima da arma = 1 turno a menos
# (machado ataca todo turno; haste em turnos alternados); 10 acima = ataca todo turno.
# "aparar": se usar a arma para aparar tambem a deixa despreparada.
FAMILIAS_DESBALANCEADAS = {
    "machado-maca": {"nome": "Machado/Maça", "turnos": 1, "aparar": True, "st_min": 12},
    "machado-2-maos": {"nome": "Machado/Maça de duas mãos", "turnos": 1, "aparar": True,
                       "st_min": 13},
    "mangual": {"nome": "Mangual", "turnos": 1, "aparar": True, "st_min": 12},
    "arma-de-haste": {"nome": "Arma de haste", "turnos": 2, "turnos_gdp": 1, "aparar": False,
                      "st_min": 12},
    "cimitarra": {"nome": "Cimitarra (uma mão)", "turnos": 1, "aparar": False, "st_min": 11},
}

# palavra no nome do item -> (familia, ST minima da tabela). A mais longa que casar vence.
ARMAS_DESBALANCEADAS = {
    "machadinha": ("machado-maca", 7), "machado de arremesso": ("machado-maca", 12),
    "machado": ("machado-maca", 12), "maca pequena": ("machado-maca", 11),
    "maca": ("machado-maca", 12), "picareta": ("machado-maca", 11),
    "cutelo": ("machado-maca", 12),
    "morningstar": ("mangual", 12), "mangual": ("mangual", 13),
    "martelo de combate": ("machado-2-maos", 13), "martelo": ("machado-2-maos", 13),
    "malho": ("machado-2-maos", 14), "foice de guerra": ("machado-2-maos", 12),
    "falcione": ("arma-de-haste", 11), "acha": ("arma-de-haste", 12),
    "alabarda": ("arma-de-haste", 13),
    "cimitarra": ("cimitarra", 11),
}


def _slug(txt):
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", str(txt or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def arma_desbalanceada(nome_arma, pericia="", modo="balanco"):
    """None se a arma e balanceada; senao {familia, nome, turnos, aparar, st_min}.

    Decide pela PERICIA quando ela e de familia desbalanceada (Machado/Maça, Mangual, Arma
    de Haste), e pelo NOME do item para a ST minima e para o resto (cimitarra de uma mao,
    maca empunhada por quem tem a pericia em outro nome). Espada de duas maos e balanceada
    mesmo chamada cimitarra."""
    n, per = _slug(nome_arma), _slug(pericia)
    duas_maos = "2-mao" in n or "duas-mao" in n or "2-mao" in per or "duas-mao" in per
    familia = None
    if "haste" in per:
        familia = "arma-de-haste"
    elif "mangual" in per:
        familia = "mangual"
    elif "machado" in per or "maca" in per:
        familia = "machado-2-maos" if duas_maos else "machado-maca"
    # a ST minima vem do item; a palavra mais longa que casar e a que vale
    st_min, fam_item = None, None
    for chave, (fam, st) in sorted(ARMAS_DESBALANCEADAS.items(), key=lambda kv: -len(kv[0])):
        if _slug(chave) in n:
            st_min, fam_item = st, fam
            break
    if familia is None and fam_item:
        if fam_item == "cimitarra" and (duas_maos or "duas-mao" in per or "espadas-de-duas" in per):
            return None     # cimitarra de duas maos: identica ao montante, balanceada
        familia = fam_item if not (fam_item == "machado-maca" and duas_maos) else "machado-2-maos"
    if familia is None:
        return None
    if fam_item == "machado-maca" and familia == "machado-2-maos":
        st_min = None   # «machado» a duas maos: vale a ST minima da familia (13), nao a de uma mao
    f = dict(FAMILIAS_DESBALANCEADAS[familia])
    f["familia"] = familia
    f["st_min"] = st_min if st_min is not None else f["st_min"]
    if familia == "arma-de-haste" and modo in ("estocada", "gdp"):
        f["turnos"] = f["turnos_gdp"]
    return f


def turnos_para_preparar(desb, st, extra=0):
    """Quantos turnos de Preparar a arma cobra depois de usada, ja com a Preparacao Rapida
    por ST (p. 104). `extra` e o turno a mais do erro critico «a arma gira na mao»."""
    if not desb:
        return 0
    bonus = 0
    if st and desb.get("st_min"):
        bonus = max(0, (int(st) - int(desb["st_min"])) // 5)
    return max(0, int(desb["turnos"]) - bonus) + int(extra or 0)


# A PROJECAO (MB, p. 106: 1 hexagono a cada 8 pontos de dano antes da RD, so corte,
# contusao e bala) e grandeza da folha `causar-dano`, e o teste de DX de quem e projetado
# e da `arbitrar-ferimento`. Nada dela mora aqui.

# Condicoes adversas mais usadas — MB, cap. 13
REDUTORES = {
    "iluminacao-ruim": (-1, "iluminação ruim (-1 a -9, escolha o grau)"),
    "escuridao": (-10, "escuridão total"),
    "apoio-ruim": (-2, "apoio ruim para os pés"),
    "cego": (-6, "cego"),
    "subitamente-cego": (-10, "subitamente cego"),
    "zarolho": (-1, "zarolho (arma de mão; -3 com longo alcance)"),
    "fogo": (-2, "roupas pegando fogo"),
    "rastejando": (-4, "rastejando"),
    "agachado": (-2, "agachado"),
    "sentado": (-2, "sentado"),
    "escudo-grande": (-2, "atacando com escudo grande"),
    "hex-inimigo": (-4, "atacando através do hexágono de um inimigo"),
}
