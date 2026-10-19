# -*- coding: utf-8 -*-
"""
Tabelas de combate a distancia — GURPS 3a Edicao, Modulo Basico.

Fontes:
  `21-quadros-e-tabelas.md` — Tabela de Parametro Velocidade/Distancia e Tamanho
    (pag. 201) e Tabela de Armas de Longo Alcance Antigas/Medievais (pag. 207).
  `11-combate-avancado.md` — ARMAS DE LONGO ALCANCE (pags. 115-119).
  `10-combate-basico.md` — Bloqueio contra projetil.
"""

# Tabela da pag. 201. Cada linha: (medida linear em metros, mod vel/dist, mod tamanho).
# O livro manda "escolher o menor valor da tabela MAIOR do que o resultado real".
ESCALA = [
    (0.003, +15, -15), (0.005, +14, -14), (0.008, +13, -13), (0.012, +12, -12),
    (0.017, +11, -11), (0.025, +10, -10), (0.038, +9, -9),   (0.051, +8, -8),
    (0.075, +7, -7),   (0.15, +6, -6),    (0.30, +5, -5),    (0.45, +4, -4),
    (0.60, +3, -3),    (0.90, +2, -2),    (1.3, +1, -1),     (2.0, 0, 0),
    (3.0, -1, +1),     (4.5, -2, +2),     (7.0, -3, +3),     (9.0, -4, +4),
    (13.5, -5, +5),    (20.0, -6, +6),    (30.0, -7, +7),    (45.0, -8, +8),
    (70.0, -9, +9),    (90.0, -10, +10),  (135.0, -11, +11), (200.0, -12, +12),
    (300.0, -13, +13), (450.0, -14, +14), (700.0, -15, +15), (1000.0, -16, +16),
    (1350.0, -17, +17), (2000.0, -18, +18), (3000.0, -19, +19), (4500.0, -20, +20),
    (7000.0, -21, +21), (10000.0, -22, +22), (16000.0, -23, +23),
]


def mod_velocidade_distancia(soma_m):
    """Distancia + velocidade, em metros. Devolve (modificador, medida da tabela)."""
    for medida, mod_vd, _ in ESCALA:
        if soma_m <= medida:
            return mod_vd, medida
    return ESCALA[-1][1], ESCALA[-1][0]


def mod_tamanho(metros):
    """Maior dimensao do alvo, em metros. Humano (2 m) da zero."""
    for medida, _, mod_tam in ESCALA:
        if metros <= medida:
            return mod_tam, medida
    return ESCALA[-1][2], ESCALA[-1][0]


# Tabela de Armas de Longo Alcance Antigas/Medievais, pag. 207, mais a pistola .45
# da pag. 116 para o caso de campanha moderna.
#   dano  — formula da tabela: GDP/BAL do atirador com o ajuste da arma
#   teto  — "Dano max." da coluna de observacoes; None quando nao ha
#   meia / max — expressoes na ST que governa a arma (besta: a ST DA ARMA)
#   bloqueavel — escudo pode bloquear (flecha, virote, pedra de funda: sim; bala: nao)
ARMAS = {
    "machadinha":     {"nome": "Machadinha", "pericia": "Arremesso de Machado",
                       "tr": 11, "prec": 1, "meia": "ST*1.5", "max": "ST*2.5",
                       "dano": "BAL", "tipo": "corte", "teto": None, "bloqueavel": True},
    "machado":        {"nome": "Machado de arremesso", "pericia": "Arremesso de Machado",
                       "tr": 10, "prec": 2, "meia": "ST*1", "max": "ST*1.5",
                       "dano": "BAL+2", "tipo": "corte", "teto": None, "bloqueavel": True},
    "arco-curto":     {"nome": "Arco curto", "pericia": "Arco",
                       "tr": 12, "prec": 1, "meia": "ST*10", "max": "ST*15",
                       "dano": "GDP", "tipo": "perf", "teto": "1D+3", "bloqueavel": True},
    "arco":           {"nome": "Arco médio", "pericia": "Arco",
                       "tr": 13, "prec": 2, "meia": "ST*15", "max": "ST*20",
                       "dano": "GDP+1", "tipo": "perf", "teto": "1D+4", "bloqueavel": True},
    "arco-longo":     {"nome": "Arco longo", "pericia": "Arco",
                       "tr": 15, "prec": 3, "meia": "ST*15", "max": "ST*20",
                       "dano": "GDP+2", "tipo": "perf", "teto": "1D+4", "bloqueavel": True},
    "arco-composto":  {"nome": "Arco composto", "pericia": "Arco",
                       "tr": 14, "prec": 3, "meia": "ST*20", "max": "ST*25",
                       "dano": "GDP+3", "tipo": "perf", "teto": "1D+4", "bloqueavel": True},
    "besta":          {"nome": "Besta", "pericia": "Besta",
                       "tr": 12, "prec": 4, "meia": "ST*20", "max": "ST*25",
                       "dano": "GDP+4", "tipo": "perf", "teto": "3D", "bloqueavel": True,
                       "st_da_arma": True},
    "besta-de-bala":  {"nome": "Besta de bala", "pericia": "Besta",
                       "tr": 12, "prec": 2, "meia": "ST*20", "max": "ST*25",
                       "dano": "GDP+4", "tipo": "cont", "teto": None, "bloqueavel": True,
                       "st_da_arma": True},
    "facao":          {"nome": "Facão arremessado", "pericia": "Arremesso de Faca",
                       "tr": 12, "prec": 0, "meia": "ST-2", "max": "ST+5",
                       "dano": "GDP", "tipo": "perf", "teto": "1D+2", "bloqueavel": True},
    "faca":           {"nome": "Faca pequena arremessada", "pericia": "Arremesso de Faca",
                       "tr": 11, "prec": 0, "meia": "ST-5", "max": "ST*1",
                       "dano": "GDP-1", "tipo": "perf", "teto": "1D+1", "bloqueavel": True},
    "adaga":          {"nome": "Adaga arremessada", "pericia": "Arremesso de Faca",
                       "tr": 12, "prec": 0, "meia": "ST-5", "max": "ST*1",
                       "dano": "GDP-1", "tipo": "perf", "teto": "1D", "bloqueavel": True},
    "funda":          {"nome": "Funda", "pericia": "Funda",
                       "tr": 12, "prec": 0, "meia": "ST*6", "max": "ST*10",
                       "dano": "BAL", "tipo": "cont", "teto": None, "bloqueavel": True},
    "fustibalo":      {"nome": "Fustíbalo", "pericia": "Funda",
                       "tr": 14, "prec": 1, "meia": "ST*10", "max": "ST*15",
                       "dano": "BAL+1", "tipo": "cont", "teto": None, "bloqueavel": True},
    "dardo":          {"nome": "Dardo", "pericia": "Arremesso de Lança",
                       "tr": 10, "prec": 3, "meia": "ST*1.5", "max": "ST*2.5",
                       "dano": "GDP+1", "tipo": "perf", "teto": None, "bloqueavel": True},
    "lanca":          {"nome": "Lança arremessada", "pericia": "Arremesso de Lança",
                       "tr": 11, "prec": 2, "meia": "ST*1", "max": "ST*1.5",
                       "dano": "GDP+3", "tipo": "perf", "teto": None, "bloqueavel": True},
    "pedra":          {"nome": "Pedra", "pericia": "Arremesso",
                       "tr": 12, "prec": 0, "meia": "ST*2", "max": "ST*3.5",
                       "dano": "GDP-1", "tipo": "cont", "teto": None, "bloqueavel": True},
    "frasco-de-oleo": {"nome": "Frasco de óleo", "pericia": "Arremesso",
                       "tr": 13, "prec": 0, "meia": "", "max": "ST*3.5",
                       "dano": "", "tipo": "cont", "teto": None, "bloqueavel": True,
                       "obs": "Fogo: ver MB, cap. 15 («Queimaduras»), pág. 121."},
    "zarabatana":     {"nome": "Zarabatana", "pericia": "Zarabatana",
                       "tr": 10, "prec": 1, "meia": "", "max": "ST*4",
                       "dano": "", "tipo": "perf", "teto": None, "bloqueavel": True,
                       "obs": "Dardo sem dano próprio: vale o veneno (MB, pág. 49)."},
    "pistola":        {"nome": "Pistola calibre .45", "pericia": "Pistola",
                       "tr": 10, "prec": 2, "meia": "175", "max": "1700",
                       "dano": "2D+", "tipo": "cont", "teto": None, "bloqueavel": False},
}

# Apelidos que a mesa costuma falar.
APELIDOS_ARMA = {
    "arco-medio": "arco", "arco medio": "arco", "besta-leve": "besta",
    "machado-de-arremesso": "machado", "faca-pequena": "faca",
    "lanca-arremessada": "lanca", "virote": "besta", "flecha": "arco",
}

CONDICOES = {
    "escuridao":        (-10, "escuridão total"),
    "penumbra":         (-3, "iluminação ruim (escolha de -1 a -9)"),
    "hex-obstruido":    (-2, "hex obstruído ou piso ruim — apontar parado cancela"),
    "atras-de-alguem":  (-4, "uma figura humana na linha de tiro (some -4 por figura)"),
    "alvo-semi":        (-3, "alvo semi-exposto"),
    "alvo-parcial":     (-4, "só cabeça e ombros do alvo expostos"),
    "alvo-so-cabeca":   (-5, "só a cabeça do alvo exposta"),
    "alvo-deitado":     (-4, "alvo deitado, sem cobertura"),
    "chuva":            (-2, "chuva forte, fumaça ou neblina"),
    "zarolho":          (-3, "zarolho (com arma de longo alcance)"),
    "luneta-tiro-rapido": (-1, "luneta, no tiro rápido — ela é desajeitada"),
}

APOIO = (+1, "arma apoiada, com pelo menos um turno apontando")
TIRO_RAPIDO = (-4, "Tiro Rápido: disparou sem apontar e o NH efetivo não alcançou o TR")
RELAMPAGO = (-2, "ataque relâmpago: não viu o alvo no início do turno")
AS_CEGAS = (-10, "atirando às cegas, fora do ângulo de visão")
ERRATICO_MAX = -4

# Textos das regras que o Mestre precisa repassar, por situacao.
NOTAS = {
    "meia": "Passou do Meio Dano (½D): o dano sai pela METADE, arredondando para baixo.",
    "max": "Além do Alcance Máximo: o projétil não chega. O ataque não acontece.",
    "prec_alem_meia": ("Além do ½D o Modificador de Precisão NÃO vale — MB: «ignore o "
                       "modificador de precisão quando o alvo estiver a uma distância "
                       "maior do que ½D»."),
    "prec_teto": "O bônus de Precisão nunca passa do NH básico com a arma.",
    "apontar_extra": "Cada turno apontando além do primeiro dá +1, até o teto de +3.",
    "apontar_andando": ("Apontar andando: no máximo +1, e só até 2 m/s (ou metade do "
                        "Deslocamento). Arqueiro não aponta andando; besteiro sim."),
    "apontar_ferido": ("Quem é ferido enquanto aponta precisa de um teste de Vontade "
                       "para não perder a pontaria. Perder o alvo de vista cancela tudo."),
    "as_cegas": ("Atirando às cegas valem as duas regras, e usa-se a PIOR: -10 no NH, ou "
                 "resultado 9 ou menos nos dados. Não há bônus por apontar."),
    "bloqueio_sim": ("Flecha, virote e pedra de funda PODEM ser bloqueadas com escudo "
                     "preparado (MB, pág. 98)."),
    "bloqueio_nao": ("Bala e arma de feixe NÃO podem ser bloqueadas — chegam rápido "
                     "demais. A defesa PASSIVA do escudo continua valendo."),
    "sem_aparar": ("Não se apara projétil: contra arma de longo alcance o alvo tem "
                   "Esquiva, e Bloqueio quando o projétil é lento o bastante."),
    "dp_escudo": ("A defesa passiva do escudo vale contra TODAS as armas de projétil "
                  "(MB, pág. 98)."),
    "extraviado": ("Tiro que erra segue viagem: veja «Atingindo o Alvo Errado» "
                   "(MB, pág. 117) se houver alguém na linha de tiro."),
    "angulo": ("Com arma de longo alcance só se atira no ângulo de visão — os hexágonos "
               "à frente. Fora dele, é tiro às cegas."),
    "para_baixo": ("Atirando para baixo: -1 m de distância efetiva a cada 2 m de "
                   "elevação, nunca abaixo de metade da distância real."),
    "para_cima": "Atirando para cima: +1 m de distância efetiva por metro de subida.",
    "erratico": ("Movimento errático: até -4, a critério do Mestre. Alvo que não se "
                 "desvia da reta pelo menos o próprio tamanho por segundo não conta."),
}
