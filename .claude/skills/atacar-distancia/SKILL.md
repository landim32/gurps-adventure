---
name: atacar-distancia
description: >
  Resolve um disparo ou arremesso pelas regras de armas de longo alcance de GURPS 3ª
  Edição: NH efetivo pela sequência de cinco passos do livro (tamanho do alvo,
  velocidade/distância, Precisão de quem apontou, condições e Tiro Rápido), Meio Dano e
  Alcance Máximo, defesa por Esquiva ou Bloqueio mais a DP do escudo, golpe fulminante e
  erro crítico, dano com RD da região e tetos do local. Entrega o texto para o WhatsApp e
  grava no capítulo. Use when the user asks "ele atira com o arco", "Comam saca a besta e
  dispara", "arremessa a faca no guarda", "tiro à distância", "ele mira e atira",
  ou /atacar-distancia.
---

# Combate à distância

A irmã da skill `atacar`. Aquela resolve o golpe de perto; esta resolve **o tiro** —
arco, besta, funda, faca arremessada, pedra, lança, e a pistola de uma campanha moderna.

Uma execução do script resolve **um disparo**, do NH efetivo às consequências.

```
python .claude/skills/atacar-distancia/scripts/atacar_distancia.py \
  --atacante "Comam" --arma besta --arma-st 12 --dano "1D+6" --tipo perf \
  --distancia 8 --apontou 1 \
  --alvo "Morto-Vivo 3" --alvo-ht 11 --alvo-esquiva 5 --alvo-rd 2 --alvo-dp 2 \
  --alvo-hipoalgia --local tronco
```

## A sequência que ele executa

É a do MB, cap. 14, seção **«Ataques Com Armas de Longo Alcance»** (pág. 118), na ordem:

| # | Passo | Regra |
|---|---|---|
| 1 | **NH básico** com a perícia da arma | da ficha, ou `--nh` |
| 2 | **Tamanho do alvo** | Tabela da pág. 201. Homem (2 m) dá **0** |
| 3 | **Velocidade + distância** | **a soma dos dois vira um número só** e vai à mesma tabela |
| 4 | **Precisão da arma** | só para quem apontou pelo menos um turno; **nunca passa do NH básico** |
| 5 | **Condições** | turnos extras apontando (+1 cada, teto +3), apoio, escuridão, Tiro Rápido |
| 6 | **Alcance** | além do **Máximo** não há tiro; além do **½D** o dano cai à metade |
| 7 | **Jogada de ataque** | 3d. Recusa a jogada se o NH efetivo cair a 3 ou menos |
| 8 | **Fulminante / erro crítico** | as mesmas tabelas da skill `atacar` |
| 9 | **Defesa** | **Esquiva ou Bloqueio** + Reflexos em Combate + DP da peça + **DP do escudo** |
| 10 | **Dano, local, consequências** | igual ao corpo a corpo: RD da região, tipo de dano, tetos, queda, nocaute |

**A ordem importa em um ponto só, e é o que mais se erra:** o TR é comparado com o NH
**já ajustado** por tamanho, distância e condições — não com o NH básico. Por isso o
script só decide o Tiro Rápido no fim.

## Traduzir a declaração

| Na frase | Vira |
|---|---|
| "Comam saca a besta e atira no morto do meio" | `--arma besta --alvo "Morto-Vivo 2"` |
| "ele passou o turno mirando" | `--apontou 1` (dois turnos: `--apontou 2`) |
| "atira na hora, sem mirar" | omita `--apontou` — o script cobra o Tiro Rápido se couber |
| "ele está a uns oito metros" | `--distancia 8` — conte no mapa, é 1 hexágono = 1 metro |
| "apoiado na ameia" | `--apoiada` |
| "mira na cabeça" | `--local cabeca` |
| "o guarda levanta o escudo" | `--alvo-defesa bloqueio` |
| "ele se joga de lado" | `--alvo-defesa esquiva` (o padrão) |

**Pergunte só o que muda o resultado**: se apontou, a distância, e o que o alvo faz.
O resto sai da ficha e do catálogo.

## O catálogo de armas

`--arma <modelo>` traz TR, Precisão, ½D, Máximo e se dá para bloquear, direto da
**Tabela de Armas de Longo Alcance Antigas/Medievais** (`21-quadros-e-tabelas.md`,
pág. 207):

| `--arma` | TR | Prec | ½D | Máx | Dano |
|---|---|---|---|---|---|
| `machadinha` | 11 | +1 | ST×1,5 | ST×2,5 | BAL, corte |
| `machado` (de arremesso) | 10 | +2 | ST | ST×1,5 | BAL+2, corte |
| `arco-curto` | 12 | +1 | ST×10 | ST×15 | GDP, perf (teto 1D+3) |
| `arco` (médio) | 13 | +2 | ST×15 | ST×20 | GDP+1, perf (teto 1D+4) |
| `arco-longo` | 15 | +3 | ST×15 | ST×20 | GDP+2, perf (teto 1D+4) |
| `arco-composto` | 14 | +3 | ST×20 | ST×25 | GDP+3, perf (teto 1D+4) |
| `besta` | 12 | +4 | ST×20 | ST×25 | GDP+4, perf (teto 3D) |
| `besta-de-bala` | 12 | +2 | ST×20 | ST×25 | GDP+4, contusão |
| `facao` | 12 | 0 | ST-2 | ST+5 | GDP, perf (teto 1D+2) |
| `faca` (pequena) | 11 | 0 | ST-5 | ST | GDP-1, perf (teto 1D+1) |
| `adaga` | 12 | 0 | ST-5 | ST | GDP-1, perf (teto 1D) |
| `funda` | 12 | 0 | ST×6 | ST×10 | BAL, contusão |
| `fustibalo` | 14 | +1 | ST×10 | ST×15 | BAL+1, contusão |
| `dardo` | 10 | +3 | ST×1,5 | ST×2,5 | GDP+1, perf |
| `lanca` | 11 | +2 | ST | ST×1,5 | GDP+3, perf |
| `pedra` | 12 | 0 | ST×2 | ST×3,5 | GDP-1, contusão |
| `frasco-de-oleo` | 13 | 0 | — | ST×3,5 | fogo (MB, pág. 121) |
| `zarabatana` | 10 | +1 | — | ST×4 | só o veneno (MB, pág. 49) |
| `pistola` (.45) | 10 | +2 | 175 m | 1.700 m | **não se bloqueia** |

Arma fora do catálogo: passe `--tr`, `--prec`, `--meia` e `--maximo` na mão (as duas
últimas aceitam `ST*20`, `ST-5`, `175`).

### A ST da besta é da arma, não do atirador

> As *bestas* são uma exceção. O alcance e o dano são governados pela ST da *arma*.
> — MB, cap. 14

**Passe `--arma-st` com a ST da besta** sempre que houver besta na cena. Sem ela o script
usa a ST de quem atira e avisa que fez isso. Para arco, funda e arremesso, a ST é a do
atirador mesmo — mas `--arma-st` continua útil quando o atirador não tem ficha.

### O dano

O script **não calcula o dano a partir da fórmula da tabela** (GDP+4, BAL+2): ele espera
o valor pronto. Duas saídas:

- **`--arma` casando com um item da ficha** (`--arma "Besta"`) — pega dano e tipo de lá,
  como a skill `atacar` faz;
- **`--dano "1D+6" --tipo perf`** na mão. A fórmula está na tabela acima: pegue o GDP ou
  o Balanço da ST que governa a arma em `21-quadros-e-tabelas.md` e some o ajuste.

O **teto de dano** da coluna de observações (`Dano máx. 1D+4`) é aplicado sozinho quando
a arma vem do catálogo.

## Apontar

| Opção | O que faz |
|---|---|
| `--apontou 1` | Ganha a **Precisão** da arma e **elimina o -4 de Tiro Rápido** |
| `--apontou 2`, `3`, `4` | Cada turno além do primeiro dá **+1**, até o teto de **+3** |
| `--apoiada` | **+1**, mas só somado a pelo menos um turno apontando |

Três coisas que o script não sabe e você precisa arbitrar:

- **Apontando andando**: no máximo +1, e só até 2 m/s (ou metade do Deslocamento).
  **Arqueiro não aponta andando; besteiro sim.** Se a cena for essa, use `--mod`.
- **Ferido enquanto aponta**: teste de Vontade ou perde a pontaria (skill `teste-nh`).
- **Perdeu o alvo de vista**: todos os bônus de pontaria caem, sem teste nenhum.

**Além do ½D a Precisão não vale** — o livro cancela o bônus, e o script avisa quando
isso acontece. Ficar mirando um alvo longe demais não adianta.

## Os modificadores da situação

| Opção | Para quê |
|---|---|
| `--alvo-tamanho N` | Maior dimensão em metros. **Humano = 2, que dá zero** |
| `--alvo-velocidade N` | m/s. **Contra alvo humano com defesa ativa, deixe 0** — o livro manda desprezar |
| `--elevacao N` | Metros que o **atirador** está acima do alvo (negativo: abaixo) |
| `--erratico N` | Movimento imprevisível: até -4 |
| `--relampago` | Ataque relâmpago: -2, e o -4 de Tiro Rápido sempre |
| `--as-cegas` | Fora do ângulo de visão: -10 **e** teto de 9 nos dados, o pior dos dois |
| `--condicao` | `escuridao`, `penumbra`, `hex-obstruido`, `atras-de-alguem`, `alvo-parcial`, `alvo-so-cabeca`, `alvo-semi`, `alvo-deitado`, `chuva`, `zarolho`, `luneta-tiro-rapido`. Repita quantas vezes precisar |
| `--mod N` | Qualquer outro modificador que você arbitre |

**A simplificação do livro para alvo humano**: só o modificador de *distância* importa.
Tamanho é 0, velocidade se despreza porque o alvo tem defesa ativa. Nas cenas da campanha
isso quer dizer que **`--distancia` costuma ser o único número que a mesa precisa dar.**

**Ficar parado para apontar cancela o -2 de hex obstruído** — não passe as duas coisas
juntas.

## A defesa contra projétil

> É *impossível* bloquear balas ou armas de feixe, pois elas chegam muito rápido para
> serem bloqueadas com um escudo. (No entanto, a defesa *passiva* do escudo ajuda contra
> *todas* as armas de projétil.)
> — MB, cap. 13

| | Vale? |
|---|---|
| **Esquiva** | Sempre |
| **Bloqueio** | Contra flecha, virote, pedra de funda e arma arremessada. **Nunca** contra bala ou feixe |
| **Aparar** | **Não existe** aqui — o script nem oferece a opção |
| **DP do escudo** | **Sempre**, inclusive contra bala, e mesmo quando o alvo não pode bloquear |

Pedir `--alvo-defesa bloqueio` contra uma arma que não se bloqueia **não é erro**: o
script troca para Esquiva, mantém a DP do escudo e explica por quê.

## O que muda em relação à skill `atacar`

Tudo o mais é igual — mesmas tabelas de ponto de impacto, de golpe fulminante, de erro
crítico e de tipo de dano, mesmos tetos de membro, mesmo `--alvo-hipoalgia`. As opções do
alvo são as mesmas daquela skill, menos `--alvo-aparar` e `--recuar`.

O que só existe aqui:

- **`½D`**: além dele o dano rolado **cai à metade, arredondando para baixo**, antes da RD.
- **`Máximo`**: além dele **não há jogada nenhuma** — o projétil não chega.
- **Teto de dano da arma** (arco nunca passa de 1D+4, besta de 3D).
- **Tiro Rápido** comparado com o NH efetivo.

E uma coisa que o script **não** faz: **tiro que erra vai para algum lugar**. Quando o
disparo falha, ele lembra de conferir *«Atingindo o Alvo Errado»* (MB, pág. 117) se havia
alguém na linha de tiro. Isso é arbitragem sua.

## Ângulo de visão e alcance são conferidos no mapa

O script recebe a distância pronta e acredita nela. Antes de rodar, olhe a cena na skill
`atualizar-mapa`:

- **conte os hexágonos** entre atirador e alvo — 1 hexágono é 1 metro;
- confira se o alvo está no **ângulo de visão** (os hexágonos à frente). Fora dele, é
  `--as-cegas`;
- conte quantas **figuras estão na linha de tiro**: cada uma é `--condicao atras-de-alguem`.

## Nunca invente o dado

Quem sorteia é a skill `roll`, e esta chama aquela — no ataque, na defesa, no dano e nas
tabelas de crítico. **Relate o que saiu**, número por número. Não role de novo porque o
tiro errou.

## Explicar o crítico

Vale palavra por palavra o que a skill `atacar` diz: **golpe fulminante e erro crítico só
estão resolvidos quando a mesa souber o que a tabela mandou acontecer.** O bloco do
WhatsApp já traz as duas linhas — repasse as duas.

Um erro crítico de arqueiro costuma pedir tradução: a Tabela de Erros Críticos fala em
arma quebrada e arma derrubada, e no arco isso é a **corda que arrebenta** ou o **arco que
cai**. Traduza para a cena e diga que está arbitrando.

## Esta skill não narra

**Entregue o resultado mecânico e pare.** Nada de prosa, nada de flecha cortando o ar. A
resposta é:

1. o **resultado mecânico**, em texto corrido;
2. **uma ou duas linhas ao Mestre**, sobre o que mudou na regra.

**O bloco do WhatsApp não sai a cada disparo.** Numa troca de tiros, guarde os blocos e
junte num só quando a rodada fechar — todos já jogaram, personagens e NPCs — ou quando o
Mestre disser que acabou. A regra está no `CLAUDE.md`, em *O bloco do WhatsApp sai uma vez
por rodada*, e vale igual para a skill `atacar`.

Quem escreve o texto da mesa é a skill `narrar`, e só quando o Mestre pedir.

## Mostrar e gravar

`--gravar` registra no capítulo atual pela skill `campanha`. Numa troca de tiros longa,
**não grave disparo a disparo** — grave o que mudou o rumo.

**O corpo vai para `campanha/saude.md`**, como no corpo a corpo:

```
campanha.py saude --npc "Morto-Vivo 3" --pv -10 --motivo "Virote do Comam (cap. 03)"
```

E o que não é corpo continua na anotação: **munição gasta**, flecha que se perdeu, arco
quebrado no erro crítico. Aljava vazia decide cena — anote.
