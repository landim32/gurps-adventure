---
name: combate
description: >
  Resolve uma troca de golpes inteira pelo Sistema Avançado de Combate de GURPS 3ª Edição:
  jogada de ataque com o redutor do ponto de impacto e o bônus da manobra, golpe fulminante
  ou erro crítico nas tabelas, defesa ativa mais passiva do alvo, avaliação de dano com RD,
  bônus por tipo de dano, tetos do local e testes de queda e atordoamento. Entrega o texto
  para o WhatsApp e grava no capítulo. Use when the user asks "ataque total no pescoço do
  morto-vivo", "ele ataca com a espada", "o orc golpeia o Kaelric", "aparar", "esquiva",
  ou /combate.
---

# Combate

**Sempre o Sistema Avançado** (MB, cap. 14) — nunca o Básico. É a decisão de projeto da
casa: armadura peça por peça, DP e RD por região, ponto de impacto escolhido.

Uma execução do script resolve **uma troca de golpes**, do ataque às consequências.

```
python .claude/skills/combate/scripts/combate.py \
  --atacante "Comam" --pericia "Espadas de Lâmina Larga" --arma "Cimitarra" \
  --manobra ataque-total-bonus --local pescoco \
  --alvo "Morto-Vivo 1" --alvo-ht 11 --alvo-esquiva 5 --alvo-rd 1 --alvo-dp 1 \
  --alvo-defesa esquiva --alvo-hipoalgia
```

## A sequência que ele executa

| # | Passo | Regra |
|---|---|---|
| 1 | **NH efetivo** | NH da perícia + bônus da manobra + redutor do local + condições adversas + ferimento da rodada anterior |
| 2 | **Jogada de ataque** | 3d. Recusa a jogada se o NH efetivo cair a 3 ou menos |
| 3 | **Golpe fulminante** | 3-4 sempre; 5 com NH 15+; 6 com NH 16+. **Sem jogada de defesa** e sorteio na Tabela de Golpes Fulminantes — ou na **Tabela na Cabeça**, se o alvo era cabeça, cérebro ou olhos. O efeito sorteado sai no bloco da mesa: ver **Explicar o crítico** |
| 4 | **Erro crítico** | 18 sempre; 17 com NH abaixo de 16; margem de 10 ou mais. Sorteia na Tabela de Erros Críticos e o golpe acaba ali — com o efeito dito por extenso |
| 5 | **Defesa** | Defesa ativa escolhida + Reflexos em Combate + DP da peça daquele local + DP do escudo + recuar (+3). 3 ou 4 sempre defende; 17 ou 18 é falha desastrosa |
| 6 | **Dano** | Rola o dano, tira a RD **daquela região**, aplica o bônus do tipo de dano |
| 7 | **Local** | Multiplicadores e tetos: vitais, cérebro, membros |
| 8 | **Consequências** | Redutor por ferimento, teste de queda, atordoamento, nocaute |

## Traduzir a declaração

O trabalho é seu: a frase da mesa vira opções. Do exemplo *"Comam dá um ataque total por
corte no pescoço do morto-vivo 1 com sua cimitarra, ganhando +4; o morto-vivo tenta
esquiva"*:

| Na frase | Vira |
|---|---|
| "ataque total... ganhando +4" | `--manobra ataque-total-bonus` |
| "por corte" | `--modo balanco` (a ficha já diz que balanço da cimitarra é corte) |
| "no pescoço" | `--local pescoco` |
| "com sua cimitarra" | `--arma "Cimitarra"` — e a perícia correspondente em `--pericia` |
| "o morto-vivo tenta esquiva" | `--alvo-defesa esquiva` |

**Pergunte só o que muda o resultado.** Manobra, local e defesa do alvo importam sempre; o
resto costuma sair da ficha.

## O atacante

| Opção | Para quê |
|---|---|
| `--atacante` | Nome; nome parcial resolve |
| `--pericia` | Perícia da arma — o NH sai da ficha |
| `--nh` | NH na mão, para NPC sem ficha |
| `--arma` | Item da ficha: pega dano e tipo sozinho |
| `--dano` / `--tipo` | Na mão: `2D+2`, `corte`/`perf`/`cont` |
| `--modo balanco\|estocada` | Arma com dois valores (`2D/1D+1`): qual dos dois |
| `--manobra` | Ver a tabela abaixo |
| `--local` | Ponto de impacto, ou `aleatorio` |
| `--de-cima` | Ataque de cima: -3 no sorteio do local, o que puxa para cabeça e braços |
| `--condicao` | `escuridao`, `agachado`, `apoio-ruim`, `hex-inimigo`… repita quantas vezes precisar |
| `--ferimento N` | Pontos de vida que **o atacante** perdeu na rodada anterior |
| `--mod N` | Qualquer outro modificador que você arbitre |

## O alvo

**Personagem do repositório é automático**: o script lê esquiva/aparar/bloqueio de
`defesas_ativas`, soma **+1 se tiver Reflexos em Combate** (as fichas guardam o valor sem
esse bônus), acha a **peça de armadura daquela região** pelo nome do item — "Cota de malha
(tronco)", "Camal (cabeça)" — e usa o par `DP1/RD2 perf` quando o golpe é perfurante.

A **DP do escudo entra em qualquer ponto de impacto** — no livro ela é um bônus na jogada
de defesa, limitado por *direção* (frente e lado do escudo), não por parte do corpo. Se na
sua cena o escudo não deveria valer — golpe pelas costas, alvo deitado sobre ele —, passe
`--alvo-dp` com o valor certo e o script usa o seu número.

**NPC não tem ficha em JSON.** Leia o `npcs.md` do capítulo e passe na mão:

| Opção | |
|---|---|
| `--alvo-ht` | **Passe sempre.** Sem HT não há teste de queda, nocaute nem teto de local |
| `--alvo-esquiva` / `--alvo-aparar` / `--alvo-bloqueio` | A defesa ativa |
| `--alvo-dp` / `--alvo-rd` | Defesa passiva e RD naquele local |
| `--alvo-defesa` | Qual das três ele usa, ou `nenhuma` |
| `--alvo-defesa-mod` | Ataque lateral (-2), finta, o que for |
| `--alvo-manobra` | `defesa-total`, `ataque-total` (sem defesa), `atordoado` (-4), `surpreendido` |
| `--recuar` | **+3** em qualquer defesa, uma vez por rodada |
| `--alvo-hipoalgia` | Sem redutor por ferimento — é o caso dos mortos-vivos desta campanha |

## Manobras

| `--manobra` | O que faz |
|---|---|
| `ataque` | Avançar e Atacar. Defende normalmente |
| `ataque-total-bonus` | **+4 no NH**, e **nenhuma defesa ativa** até o próximo turno |
| `ataque-total-dano` | NH normal, **+2 no dano**, sem defesa ativa |
| `ataque-total-duplo` | Dois ataques — **rode o comando duas vezes**. Só com duas armas preparadas |
| `ataque-total-finta` | A finta é Disputa Rápida: resolva na `disputa-nh` e traga a margem como `--alvo-defesa-mod` negativo |
| `aguardar` | Ataque normal quando o inimigo entra no alcance |
| `movimento-e-ataque` | Golpe de molinete de quem gastou a rodada andando |
| `precipitado` | -4, ataque com a mão inábil |

**O Ataque Total é a decisão mais cara da mesa** e a que mais se esquece: quem escolhe não
tem defesa ativa nenhuma até o próximo turno. Diga isso ao jogador **antes** de rolar, e
lembre-se dele quando o inimigo revidar — `--alvo-manobra ataque-total`.

## Pontos de impacto

| `--local` | Redutor | O que muda no dano |
|---|---|---|
| `tronco` | 0 | Nada. Golpe de ponta acima de HT trespassa e o excesso se perde |
| `orgaos-vitais` | -3 | **Perfurante ×3.** Só se alcança com arma perfurante |
| `cerebro` | -7 | RD 2 do crânio somada à armadura, e o que passa é **×4**, de qualquer tipo |
| `cabeca` | -5 | Golpe fulminante vai à tabela própria. Teste de HT contra nocaute |
| `olhos` | -9 | ×4; mais de 2 pontos cegam o olho |
| `olhos-viseira` | -10 | Como acima, e **a armadura não protege** |
| `braco` / `perna` | -2 | Teto **HT/2**; passou disso, membro incapacitado e o resto se perde |
| `mao` / `pe` | -4 | Teto **HT/3** |
| `braco-escudo` | -4 | Como o braço |
| `mao-escudo` | -8 | Como a mão |
| `aleatorio` | — | Sorteia 3d na Tabela de Partes do Corpo |

**Perfurante em membro não ganha bônus de dano** — flecha no pé é incômodo, flecha na
cabeça mata. O script aplica sozinho.

**«Pescoço» não existe** na Tabela de Partes do Corpo da 3ª edição. Quem pedir pescoço cai
em **Cabeça (-5)**, e o script avisa. Se a mesa quiser decapitação, é arbitragem do Mestre,
e diga que é.

## O que esta skill não faz

Ela resolve **o golpe**, não o combate inteiro. Continua com você, ou com outra skill:

| O quê | Onde |
|---|---|
| Quem age primeiro, surpresa | skill **`iniciativa`** (e a ordem de turnos é fixa, por Deslocamento) |
| Finta | skill **`disputa-nh`** — a margem vira `--alvo-defesa-mod` negativo |
| Onde cada um está, alcance, hexágono frontal ou lateral | skill **`atualizar-mapa`** |
| Um teste solto no meio da luta | skill **`teste-nh`** |
| Armas de longo alcance, combate de perto, agarrar, desarmar | MB, cap. 14 — arbitre e use `--mod` |
| Somar os pontos de vida perdidos ao longo da luta | você; o script resolve um golpe por vez |

**Alcance e direção não são conferidos pelo script.** Confira no mapa antes: ataque pelo
hexágono lateral dá -2 na defesa do alvo, pelas costas não há defesa ativa nenhuma, e
escudo só protege da frente e do lado dele.

## Nunca invente o dado

Quem sorteia é a skill `roll`, e esta chama aquela — inclusive nas tabelas de golpe
fulminante e erro crítico. **Relate o que saiu**, número por número, do ataque, da defesa e
do dano. Não rode de novo porque o jogador levou 24 pontos.

Se a mesa quiser um resultado escolhido para testar uma regra, **diga que foi escolhido**.

## Explicar o crítico

Um `3d = 15` não diz nada a quem está na mesa. **Golpe fulminante e erro crítico só estão
resolvidos quando a mesa souber o que a tabela mandou acontecer** — e o efeito costuma
importar mais que o dano: um soco que tira 1 ponto de vida e derruba a espada do oponente
decidiu a luta, e não foi o ponto de vida.

O script já traz as duas linhas no bloco do WhatsApp:

```
*GOLPE FULMINANTE!* Sem defesa possível.
Tabela de Golpes Fulminantes: 3d = *15*
_A arma do oponente cai, e ele ainda recebe o dano normal._
```

```
*ERRO CRÍTICO!* Tabela de Erros Críticos: 3d = *9*
_Você DERRUBOU a arma. Arma barata teria se quebrado._
```

**Repasse as duas**, e depois diga na narração o que isso é no mundo: a espada girando na
serragem, o punho que escorrega, o elmo que sai. Número sem consequência a mesa esquece;
consequência a mesa lembra a campanha inteira.

### Quando o efeito não se aplica

As tabelas presumem gente armada, e a mesa nem sempre está. **Traduza o efeito para a cena
e diga que está arbitrando** — é decisão do Mestre, não do livro:

| A tabela diz | O caso | O que fazer |
|---|---|---|
| "a arma do oponente cai" | alvo de mãos limpas | Não há arma: fica só o dano. Se ele estivesse **segurando** alguém, perde o agarrão; se carregava tocha ou lampião, é isso que cai |
| "derrubou a arma" | atacante desarmado | O golpe se perde: ele passa direto e fica desequilibrado |
| "a armadura é ignorada" | alvo sem armadura | Nada muda; o dano já entrava inteiro |
| efeito em membro | membro já incapacitado | O excedente se perde, como manda a regra de teto do local |

Nunca invente um efeito **pior** que o da tabela para compensar. O crítico já é o presente
que o dado deu; o trabalho é só encaixá-lo na cena.

## Mostrar e gravar

O bloco **PARA O WHATSAPP** sai sempre, com o essencial: quem atacou quem, onde, o que saiu
e quanto doeu. **Repasse num bloco de código.** Mostrar ou não é decisão do Mestre.

Fora do bloco, uma ou duas linhas ao Mestre: quem está atordoado, quem perdeu a defesa
ativa até o próximo turno, quem precisa testar HT no começo do turno.

`--gravar` registra no capítulo atual pela skill `campanha`. Numa luta longa, **não
grave golpe a golpe** — grave o que mudou o rumo: o membro que ficou inutilizado, o nocaute,
a morte, a arma quebrada.

**O corpo vai para `campanha/saude.md`.** O script resolve um golpe por vez e não soma
nada: quem mantém o placar da luta é você, e o lugar dele não é a ficha.

```
campanha.py saude --pj "Negrum Carneiriums" --pv -3 --motivo "Machadada do orc (cap. 04)"
campanha.py saude --npc "Donnwulf" --estado "Braço direito incapacitado (Maneta até curar)"
```

**A ficha do personagem não é tocada por causa de dano** — ela guarda o PV e a Fadiga
máximos, e só muda a pedido do usuário. Lance ao fim da luta o que ainda valia: os pontos
de vida perdidos que não foram curados, a Fadiga que sobrou, e `--estado` para o que dura
(membro incapacitado, nocaute, osso quebrado).

O que não é corpo continua na anotação (`campanha.py anotar`): arma quebrada, armadura
arruinada, quem fugiu e para onde, quem morreu. Dano que o alvo cura sozinho até a próxima
cena não precisa de registro nenhum. Detalhes na skill `campanha`, seções **A saúde** e
**O estado do mundo**.
