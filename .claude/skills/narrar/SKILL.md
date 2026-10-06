---
name: narrar
description: >
  Narra a história para os jogadores a partir do que está planejado na campanha: lê o
  plano do capítulo atual, os NPCs e o que já aconteceu, e escreve o texto que o Mestre
  vai ler à mesa. O texto sai formatado para colar no WhatsApp e fica arquivado no
  capítulo atual da campanha. Use when the user asks to "narre", "narrar a cena",
  "descreva a taberna", "conta o que eles veem", "texto para os jogadores", ou /narrar.
---

# Narrar a cena

Escreve o texto que vai **para os jogadores** — o que eles veem, ouvem e cheiram — a
partir do que a campanha planejou.

Duas regras mandam em tudo o mais:

1. **É a mesa que lê.** O texto vai para o WhatsApp, num celular, entre uma mensagem e
   outra. Formato e tamanho não são detalhe.
2. **Só o lado dos jogadores.** O plano é escrito para o Mestre e está cheio de coisa que
   os personagens não sabem. Narrar é filtrar.

## 1. Ler o contexto

```
python .claude/skills/narrar/scripts/narrar.py contexto
```

Lista os arquivos do capítulo atual, na ordem em que devem ser lidos, marcando os que
ainda não existem. **Leia todos os que existirem antes de escrever uma linha.**

| Arquivo | Para quê |
|---|---|
| `campanha/README.md` | quem são os personagens e seus jogadores — narre para *eles* |
| `campanha/plano/README.md` | a Descrição do Cenário: **o que os PJs já sabem do mundo** |
| `campanha/plano/NN-.../README.md` | a cena como foi planejada |
| `campanha/plano/NN-.../npcs.md` | quem está em cena, e como cada um se comporta |
| `campanha/plano/npcs.md` | quem atravessa a campanha |
| `campanha/NN-.../README.md` | **o que já aconteceu e o que já foi narrado** nesta cena |
| `campanha/NN-.../reacoes.json` | **como cada NPC já reagiu a cada personagem** (skill `reacao`) |

O último é o que evita o erro mais comum: narrar de novo o que a mesa já ouviu. Leia a
seção **Narração** dele antes de escrever qualquer coisa.

Se houver mapa declarado no capítulo, os hexágonos dizem **onde as coisas estão** — use
para posicionar a descrição ("o balcão à sua esquerda", "a mesa comprida no meio do
salão"), nunca para citar coordenada. Jogador não quer ouvir "B5".

## 2. O que NÃO vai para o texto

Esta é a parte da skill que mais importa. O plano é escrito para o Mestre.

**Nunca narre:**

- **O que só o Mestre sabe.** Se o plano diz *"o Mestre sabe: era Vurkash, testando"*, isso
  não existe para os jogadores. Narre o que a testemunha conta, não o que é verdade.
- **Ficha, número, nome de regra.** Nada de "ST 14", "Morto-Vivo 1", "faça um teste de
  Furtividade". O Mestre pede o teste em voz alta, na hora; o texto narra o *mundo*.
  **Isto vale para a descrição de cena, não para o resultado de uma jogada.** Quando o
  texto conta o desfecho de um golpe, tiro, mágica ou teste que foi rolado, a prosa fica
  limpa como aqui manda, e **logo abaixo de cada parágrafo** entram as linhas da conta, com
  `> ` na frente — o que vai em cada linha é de `CLAUDE.md` (*A narração mostra a conta de
  cada jogada*), e a forma do bloco está em *Formatação para WhatsApp*, abaixo.
- **Nome de mecânica no lugar de coisa.** Não é "um Morto-Vivo 1 entra": é *"a porta se
  abre e um homem entra cambaleando — você reconhece o rosto"*.
- **O que vem nos próximos capítulos.** O plano inteiro está aberto para você; a mesa está
  no capítulo de hoje.
- **A intenção de um NPC**, salvo o que ele deixa transparecer. "Ela está com medo" pode
  ser narrado se dá para ver; "ela não quer dizer o que há na bolsa" é dedução do jogador.
- **Como os jogadores devem se sentir.** Não escreva "vocês ficam apavorados". Descreva o
  que apavora e deixe a mesa reagir.

**Na dúvida:** um personagem, parado ali, com os cinco sentidos, perceberia isso? Se não,
fica de fora.

## 3. Escrever

Segunda pessoa do plural — **"vocês"** —, presente. É a voz natural da mesa em português.

| | |
|---|---|
| Tamanho | **900 a 1.500 caracteres** de **prosa**. As linhas de conta (o `> ` de cada jogada) não entram nessa régua nem no corte de 2.000 |
| Parágrafos | 2 a 4, de 2 a 4 linhas. Bloco de texto no celular ninguém lê |
| A cena rolou dado? | Então a narração **não é texto puro**: o bloco leva a conta de cada ação, como manda *Formatação para WhatsApp* logo abaixo |
| Sentidos | Ao menos dois além da visão — cheiro e som resolvem quase toda cena |
| Concreto | Três detalhes específicos valem mais que dez adjetivos |
| Fecho | **Termine devolvendo o turno**: "O que vocês fazem?" |

**Um personagem citado pelo nome ganha uma linha só dele** quando faz sentido: alguém
cumprimenta o Comam, o taberneiro já sabe o que o Kaelric bebe. Isso faz o jogador sentir
que o personagem *mora* naquele lugar.

### Apresentar antes de nomear

**O erro mais fácil de cometer é escrever para quem já leu o plano.** Você leu; a mesa não.
Um nome solto não diz nada a quem nunca o ouviu — e o jogador não vai interromper para
perguntar quem é.

**Nada entra em cena só com o nome.** Nem lugar, nem pessoa, nem objeto.

| Errado | Certo |
|---|---|
| "*A Âncora Quebrada* está cheia esta noite" | "A taberna onde vocês estão — *A Âncora Quebrada*, no porto — está cheia esta noite" |
| "*Giles Mão-de-Prata* ergue o caneco" | "Um mercador gordo de anéis em quatro dedos ergue o caneco. Chamam-no de *Giles Mão-de-Prata*" |
| "*Donnwulf* derruba mais um" | "Um sujeito de ombros de pedreiro derruba mais um adversário e grita o próprio nome — *Donnwulf*" |

Na primeira aparição: **a descrição vem primeiro, o nome vem depois**, quase como uma
legenda. Da segunda vez em diante, o nome sozinho basta — a mesa já tem o rosto.

**Como saber se já foi apresentado:** está na seção Narração do README do capítulo em
jogo. É para isso que ela existe.

### Descrever gente

Todo NPC que aparece precisa de **três detalhes concretos**, e é o que basta. Escolha entre:

| | Exemplos |
|---|---|
| **Idade e corpo** | quarenta e poucos, gordo; magro de quem não come há dias; ombros de carregar pedra |
| **Uma marca** | falta metade da orelha; anéis em quatro dedos; uma cicatriz que fecha o olho |
| **Roupa** | capa boa e botas gastas de estrada; ainda de uniforme; avental sujo |
| **O que está fazendo** | bebe rápido e olhando o copo; não larga a bolsa nem para beber; olha o próprio prato |

**O que a pessoa está fazendo vale por dois adjetivos** — é o detalhe que mais diz e o que
o jogador mais lembra. "Bebe rápido, sozinho, ainda de capa" já é um personagem inteiro.

Puxe os detalhes do `npcs.md` do capítulo, que existe justamente para isso. Se um NPC não
tiver descrição lá, invente — e **anote no plano depois**, para não mudar na próxima cena.

**A reação já rolada manda no comportamento.** Se o `reacoes.json` diz que o pedreiro tirou
"Muito Ruim" com o Comam, ele não cumprimenta o Comam: dá as costas, ou fala com quem está
ao lado. Narre o comportamento, **nunca o número** — o jogador descobre que é malquisto
porque o sujeito age assim, não porque leu um 3.

**Não descreva todo mundo.** Três ou quatro pessoas por narração; o resto é multidão, e
multidão se descreve junto ("estivadores do porto, duas lavadeiras, gente demais para uma
noite de terça").

### O que os personagens já sabem

Eles moram no mundo. **Não explique o que seria óbvio para quem está ali:** que Caithness
é fronteira, que o castelo fica na parte alta, que cerveja é servida em caneco.

Mas **não presuma o que é específico**: o nome da taberna, quem é aquele mercador, por que
o guarda está bebendo. Isso se apresenta ou se descobre.

A régua: o que está na **Descrição do Cenário** (`plano/README.md`) todo personagem já
sabe — pode ser citado sem apresentar. O resto entra em cena pela primeira vez.

### Formatação para WhatsApp

**Um bloco só, a cena inteira.** A narração vai como **uma mensagem**, com a cena na ordem
em que aconteceu e o fecho no fim — **não** um bloco por golpe, por teste ou por personagem.
Quem quebra em blocos separados é a cena longa (seção 4), não a jogada. Ação isolada **fora
de combate** é a cena inteira dela: um bloco, com a conta daquela rolagem embaixo do
parágrafo (`acao`, §3 *Narrar o desfecho*).

O bloco tem esta cara, e é **a mesma do `processar-turno`** (a regra é de `CLAUDE.md`,
*A narração mostra a conta de cada jogada* — não se reescreve aqui):

```
*FIM DO DIA 1 — A TRAVESSIA*

O Comam ficou com as rédeas desde antes do sol, e não soltou até agora. A areia afunda
onde o casco acha, ele encurtou a rédea e passou.
> Carreiro: pré-definido Cavalgar 15 -2 = *13*
> 3d [2, 2, 2] = *6* → sucesso por 7 — *decisivo*

Trinta quilômetros, e nenhum volume virou na caçamba.
```

- **Título do bloco** em maiúsculas, entre asteriscos de um lado só: `*FIM DO DIA 1 — A TRAVESSIA*`.
- **Cada ação rolada** é um parágrafo de prosa e, **logo abaixo dele**, as linhas da conta
  daquela ação, cada uma começando com `> `, na ordem em que o script imprimiu: NH de
  partida e de onde veio, cada bônus e redutor com o motivo, o dado, a margem, a defesa do
  alvo, dano, RD, teto do local, teste de HT, o que a tabela de crítico mandou.
- **Uma linha = uma jogada.** Nada de emendar dois testes com `·` na mesma linha: o celular
  quebra onde quer e a mesa perde o resto da conta. Formato, nesta ordem:
  `<o que> <quem>: <perícia ou atributo> NH <n>, 3d [a,b,c] = <soma> → **SUCESSO por X**`
  (ou `**FALHA por X**`, `**SUCESSO CRÍTICO**`, `**FALHA CRÍTICA por X**`). O NH já sai com
  os redutores dentro, ou a linha diz `NH 9 (= 11 -2)` — nunca se deixa a mesa deduzindo de
  quanto era o alvo. **Conseqüência é outra linha** (`Kaelric: 3 → 4/12`, `DP 3`,
  `Deslocamento 6 → 5`), não o rabicho da primeira. Preço segue igual: uma peça por linha,
  `tabela → com ágio`, e a conta de carga em linha própria.
- **Repasse as linhas como o script as imprimiu.** Não resuma em "acertou o braço", não
  reordene, não jogue a conta para o fim do bloco. Rolagem que não passou por script
  (o `roll` solto, um teste arbitrado) ganha linha escrita no mesmo formato.
- **Ação sem dado não tem conta.** Andar, observar, conversar, preparar: só prosa.
- **Segredo do Mestre fica fora.** Reação rolada para o NPC, verificação resistida, o que
  havia debaixo da capa: nada disso vira linha `> `, nem no bloco, nem na linha ao Mestre.
- O que é descrição de cena continua sem número nenhum — a conta entra **porque houve
  jogada**, não para enfeitar.
- **Ao arquivar (`narrar.py gravar`), a linha do título fica no texto.** O cabeçalho
  `### Narração N — data` do arquivo já diz qual é a narração, e ainda assim o bloco
  arquivado começa com `*FIM DO DIA 1 — A TRAVESSIA*`: o que se arquiva é **a mensagem que
  foi lida**, não um resumo dela. Não "limpe" a linha por achar duplicado.

O WhatsApp não entende Markdown. Ele entende:

| Quer | Escreva |
|---|---|
| negrito | `*assim*` — um asterisco só |
| itálico | `_assim_` — um sublinhado só |
| riscado | `~assim~` |

**Não use:** `##` títulos, `**duplo asterisco**`, tabelas Markdown, listas com `-`, links
markdown, bloco de código **dentro da mensagem**. Tudo isso vira lixo na tela do celular.
As linhas `> ` da conta são a única marca herdada do Markdown que fica: o celular não as
renderiza, mas elas dizem visualmente "isto é a conta do parágrafo de cima", e é assim que
a mesa já lê o bloco da rodada.

Use o **negrito com parcimônia** — uma ou duas coisas por narração, no que a mesa precisa
não perder. Nas linhas de conta, o negrito vai **no número que decide** (`*11*`, `*6*`) e no
que a tabela mandou (`*Braço INCAPACITADO*`), porque é ali que o jogador confere. Itálico
serve bem para fala ouvida de longe ou para um pensamento.

Emoji: **não**, salvo se a mesa já usa esse tom.

## 4. Mostrar na tela

**Sempre exiba o texto final num bloco de código**, para o usuário selecionar e copiar de
uma vez. Sem comentário no meio do bloco, sem numeração de linha:

````
```
A taberna onde vocês estão — *A Âncora Quebrada*, a última antes do cais — está cheia...
```
````

Se a narração for longa, quebre em **mais de um bloco**, na ordem de envio — é assim que
vai ser colado, uma mensagem por vez.

Fora do bloco, e só depois dele, cabe uma linha ou duas ao Mestre: que teste pedir, que
NPC reage a quê, o que a cena está preparando.

A ordem da resposta é sempre esta: **a narração em bloco(s) de código → as linhas ao
Mestre.** Primeiro o que vai para a mesa, depois o que é do Mestre.

**Esta skill não gera imagem nem prompt de imagem.** Ilustração de cena é assunto da skill
`campanha`, que grava a do capítulo no plano; aqui sai texto, e só.

## 5. Arquivar

```
python .claude/skills/narrar/scripts/narrar.py gravar \
  --arquivo narracao.txt --resumo "Descreveu a taberna cheia e o guarda no balcão"
```

Grava na seção **Narração** do `campanha/NN-capitulo/README.md`, numerada e com hora, e
**registra um acontecimento** logo abaixo — assim o log da campanha mostra o que a mesa
ouviu e quando.

**E guarda a cópia colável em `campanha/whatsapp/output/` sozinho.** O mesmo `gravar`
escreve o bloco num `.txt`, para mandar no grupo sem recortar do README:

```
campanha/whatsapp/output/2026-10-02-0920-fim-do-dia-1-a-travessia.txt
└── AAAA-MM-DD-HHMM-<slug do título da narração>.txt
```

- **Conteúdo:** exatamente o texto passado ao `gravar` — o bloco de *Formatação para
  WhatsApp* (§3): o `*TÍTULO EM MAIÚSCULAS*`, a prosa e as linhas `> ` da conta. Por isso o
  texto passado **não leva** o `### Narração N`, a linha de resumo em itálico, o
  `== RECAP ==` nem cercas de código.
- **Nome:** a data e a hora do arquivamento, e o título da primeira linha (`*…*`) em
  minúsculas, sem acento e com hífen. Sem linha de título, o nome sai do `--resumo`.
- **É cópia, não fonte.** O arquivo do capítulo manda; se os dois divergirem, o README está
  certo. Não use esta pasta para o que *chega* do grupo — `campanha/whatsapp/*.txt` na raiz
  da pasta é importação a processar, e o `README.md` de lá diz isso.
- Cada `gravar` é uma narração nova (Narração N+1, cópia nova). Não há modo de reescrever.

**E mostra o bloco na tela.** Depois de gravar, o script imprime o texto inteiro entre as
linhas de `PARA O WHATSAPP`. **Repasse esse bloco ao usuário na resposta, dentro de um
bloco de código** — a narração tem de aparecer na conversa, não só no arquivo.

**Tudo do capítulo mora num arquivo só.** O README da pasta de jogo tem, em ordem: o que a
cena virou na mesa, a **Narração** (o que os jogadores ouviram, palavra por palavra) e os
**Acontecimentos** (o log de uma linha). Abrir um arquivo dá o capítulo inteiro — não é
preciso caçar a narração noutro lugar, e no fim da campanha é esse arquivo que se lê. A
cópia de `whatsapp/output/` não fere isso: ela é **o envelope do envio**, regenerável e sem
autoridade; quem se quer ler, lê o capítulo.

Narração nova entra **no fim da seção**, na ordem de leitura. A numeração continua sozinha.

`--texto` serve para narração curta; `--arquivo` evita brigar com aspas e quebras de linha
no terminal, e é o caminho normal. Grave o texto num `.txt` temporário e aponte para ele.

`--sem-acontecimento` pula a linha no log de acontecimentos (a narração e a cópia saem do
mesmo jeito) — para quando aquela narração já tem linha no log, como um texto refeito
depois de lido.

O script avisa se o texto passar de 4.000 caracteres, que é onde o WhatsApp começa a
cortar.

**Arquive sempre.** A seção Narração é o que impede a próxima de repetir o que a mesa já
ouviu — e, no fim da campanha, é o registro mais fiel do que os jogadores de fato
souberam, que quase nunca é o que estava no plano.

**O que a narração tornou verdade, anote.** Se o texto estabeleceu um fato que a mesa vai
cobrar depois — um NPC ferido, um item na mão de alguém, uma porta arrombada, um presságio
que já caiu —, registre com `campanha.py anotar --npc/--pj/--coisa` além de arquivar a
narração. Veja a skill `campanha`, seção **O estado do mundo**.

## Sem campanha ativa

O script recusa. Narrar sem campanha é possível — o usuário pode só querer um texto — mas
aí **não há onde arquivar**: escreva, mostre no bloco, e diga que não foi gravado por não
haver capítulo atual. Não crie campanha por conta própria.
