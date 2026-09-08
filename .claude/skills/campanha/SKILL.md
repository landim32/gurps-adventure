---
name: campanha
description: >
  Cria e conduz a campanha de GURPS em andamento: escreve o plano dividido em capítulos
  no padrão de Caravana para Ein Arris, mantém tudo em campanha/ com um README.md que
  indexa, e registra o histórico do que de fato aconteceu na mesa (cada acontecimento
  numa pasta de evento, com ilustração). Sempre gera a imagem de abertura do capítulo.
  Só existe uma campanha ativa por vez; ao terminar, ela é arquivada em
  historico/campanhas/. É por esta skill que as outras registram o que aconteceu.
  Use when the user asks to "criar uma campanha", "começar campanha",
  "registrar o que aconteceu", "anotar na campanha", "encerrar a campanha", ou
  /campanha.
---

# Gerenciar a campanha

Duas coisas diferentes moram aqui, e a diferença é o que faz a skill funcionar:

- **O plano** — a campanha como foi imaginada. Capítulos escritos antes, no padrão do
  livro.
- **O histórico** — a campanha como de fato aconteceu na mesa. Escrito depois, evento a
  evento, e quase sempre diferente do plano.

Os dois convivem sem se contaminar. O plano não é reescrito quando os jogadores fogem
dele; o que muda é o histórico, que registra que fugiram.

**Cada capítulo tem duas pastas de mesmo nome, uma em cada lado:**

| Pasta | O quê | Quando é mexida |
|---|---|---|
| `campanha/plano/03-fechem-os-portoes/` | o que se **imaginou** para a cena | na criação da campanha, e só |
| `campanha/03-fechem-os-portoes/` | o que a mesa **fez** com isso | enquanto aquele for o capítulo atual |

O mesmo nome dos dois lados é proposital: dá para abrir os dois arquivos lado a lado e ver
o que sobrou do plano. E a separação física é o que garante que ninguém "corrija" o plano
depois do fato — o plano é o registro do que se pretendia, e vale como documento
justamente por isso.

**Mapas com tokens e o que a partida produziu** vão para a pasta de jogo — é lá que a
`atualizar-mapa` grava. **Ilustrações da cena planejada** (abertura, batidas do capítulo)
vão para a pasta do **plano**.

## Estrutura

```
campanha/                     a campanha ATIVA (só existe uma)
  README.md                   informações básicas + índice (gerado)

  plano/                      O QUE FOI PLANEJADO — escrito na criação
    README.md                 Descrição do Cenário
    npcs.md                   NPCs de toda a campanha
    01-<capitulo>/
      README.md               a cena como foi imaginada
      npcs.md                 quem aparece nela
      inicio.png              ilustração de abertura (sem PJs)
      <batida>.png            ilustração de um momento planejado

  01-<capitulo>/              O QUE ESTÁ ACONTECENDO — mexido durante o jogo
    README.md                 a cena como foi + narração lida + acontecimentos
    <mapa>-mesa.png           o mapa daquele capítulo, com as posições
    <mapa>-movimentos.json    o histórico das movimentações

historico/campanhas/
  <slug-da-campanha>/         campanhas encerradas, inteiras
```

**Uma campanha ativa por vez.** O script recusa criar uma segunda enquanto houver
`campanha/README.md` — encerre a atual antes. Isso não é burocracia: é o que garante que
"a campanha" numa conversa qualquer signifique sempre a mesma coisa, e que as outras
skills saibam onde escrever sem perguntar.

## O script

```
python .claude/skills/campanha/scripts/campanha.py <comando>
```

| Comando | O que faz |
|---|---|
| `estado` | Mostra a campanha ativa. `--json` para consumo por outra skill |
| `criar --nome "..."` | Monta a estrutura. Aceita `--mestre --cenario --pontos --premissa` |
| `capitulo --titulo "..."` | Nova pasta de capítulo no plano. Aceita `--mapa` e `--local` |
| `mapa --capitulo 1 --mapa ...` | Declara o cenário da cena **no plano** |
| `atual --capitulo 3` | Marca **em que capítulo a mesa está** — outras skills leem isso |
| `evento --titulo "..."` | Abre uma cena de jogo **que não está no plano** |
| `acontecimento --texto "..."` | Anota um fato no **capítulo atual**, com data e hora. `--imagem` grava no plano |
| `anotar --npc/--pj/--coisa "..." --texto "..."` | Anota uma **mudança que fica**: ferimento, item, relação, informação |
| `mundo` | Regera `campanha/mundo.md`, o estado consolidado. `--mostrar` imprime |
| `bolsa --pj/--npc "..." --valor +50` | Lança dinheiro em `campanha/bolsa.md`. Sem argumentos, mostra os saldos |
| `saude --pj/--npc "..." --pv -3` | Lança dano, Fadiga e ferimento em `campanha/saude.md`. Sem argumentos, mostra o estado |
| `imagem-inicial --arquivo ...` | Grava a ilustração de abertura **no plano** (`inicio.png`). `--prompt` se não houver geração |
| `indexar` | Regera os índices do README |
| `encerrar` | Arquiva em `historico/campanhas/`. Aceita `--desfecho` |

O script cuida do que dá errado quando se faz à mão: **numeração** (01-, 02-), **data e
hora**, o **índice que desatualiza** e a **regra de uma campanha por vez**. O que é
trabalho de escrever — o plano, a prosa de cada cena — é seu.

Os índices do `README.md` são gerados entre marcadores `<!-- indice:plano -->` e
`<!-- indice:historico -->`, a partir do que existe em disco. **Não edite dentro dos
marcadores**; edite os arquivos e rode `indexar`. O resto do README é livre.

## Escrever o plano

O padrão é o de **`livros/gurps-mb-3ed/23-caravana-para-ein-arris.md`**. Leia aquele
arquivo antes de escrever o primeiro capítulo — é curto e o formato só se entende vendo.
O que importa copiar de lá:

1. **Descrição do Cenário** (`plano/README.md`): o que *qualquer* personagem saberia
   antes de começar — geografia, quem manda, economia, religião, nível tecnológico, se há
   magia. É a única parte que pode ser **lida em voz alta aos jogadores**. Diga isso
   explicitamente no texto, como o livro diz: *"o resto da aventura é para seus olhos
   apenas"*.
2. **Capítulos numerados como cenas encadeadas**, não como uma linha do tempo rígida:
   `## 1. Introdução`, `## 2. Contratação`, `## 3. A Cena Obrigatória na Taverna`. Cada
   um é uma situação, e a ordem é a provável, não a obrigatória.
3. **Testes com o número na mão**: a perícia, o NH, o que acontece no sucesso, na falha e
   na **falha crítica**. É o que permite arbitrar a cena sem improvisar no meio.
4. **NPCs com ficha**, com pontos e atributos — o livro põe `Guerreiro I - 65 pontos` e
   resolve. Onde eles moram é assunto da seção seguinte.
5. **O que fazer se os jogadores fizerem outra coisa.** O livro trata disso o tempo todo
   ("Perdidos no Deserto", "Atrasados em Tatsori"). Um plano que só funciona no trilho
   não sobrevive à primeira sessão.

Ambiente é **Yrth** (`livros/gurps-fantasy-3ed/`), como manda o CLAUDE.md: ancore reinos,
cidades e culturas no que já existe antes de inventar.

### O plano não conhece os PJs

**Nenhum personagem de jogador entra no plano** — nem pelo nome, nem pela ficha, nem
como se a presença dele fosse certa. A lista de quem vai jogar muda no planejamento, e o
mesmo plano pode ser reusado com outra mesa.

Escreva "os personagens", "um por jogador", "quem tiver Reflexos em Combate". Ordem de
combate, Deslocamento e Velocidade Básica **saem na mesa**, das fichas de quem sentou —
não monte tabela de sequência com nomes. Ilustração do plano: o lugar e os NPCs, nunca
um PJ.

O grupo da *esta* mesa mora no `campanha/README.md` (Personagens), que é da partida, não
do plano.

### Cada capítulo é uma pasta

`capitulo --titulo "..."` cria `plano/NN-<slug>/` com dois arquivos:

- **`README.md`** — a cena: o que acontece, a tabela de testes, o que fazer se os
  jogadores fizerem outra coisa.
- **`npcs.md`** — quem aparece **nesta cena**.

Pasta e não arquivo solto porque um capítulo acumula coisa: a tabela de encontros, o texto
que se lê em voz alta, o desenho da planta. Tudo isso mora junto da cena a que pertence,
em vez de espalhado.

### O cabeçalho do capítulo

O `README.md` de cada capítulo abre com um bloco de metadados, no mesmo formato do README
da campanha:

```markdown
# 1. Encontro na Taberna

**Mapa:** `cenarios/taberna3.json`
**Local:** Taberna do porto, Wallace (Caithness)
```

**Em que cenário a cena se passa é informação de plano**, não de jogo: foi decidido ao
escrever a campanha, muito antes de alguém sentar à mesa. Por isso mora aqui, e não na
pasta de jogo — que guarda o mapa *com as posições*, resultado da partida.

Declare na criação do capítulo, ou depois:

```
campanha.py capitulo --titulo "Encontro na Taberna" \
  --mapa cenarios/taberna3.json --local "Taberna do porto, Wallace"

campanha.py mapa --capitulo 1 --mapa cenarios/taberna3.json \
  --local "Taberna do porto, Wallace (Caithness)"
```

`--mapa` aponta para o **índice `.json` de hexágonos** que a `add-grid-hex` grava, não para
a imagem: é dele que se colam os tokens. O comando avisa se o arquivo não existe ainda
(útil ao planejar antes de desenhar) ou se não é um `.json`.

O ganho prático: a **`atualizar-mapa` dispensa o `--indice`**. Marcado o capítulo atual,
ela lê daqui qual cenário usar. Um cenário por cena, decidido uma vez.

Vale para qualquer outro campo que a cena precise fixar de antemão — `**Hora:**`,
`**Clima:**`, `**Iluminação:**`. O cabeçalho é livre; `Mapa` e `Local` são só os dois que
o script conhece e mantém.

### Onde cada NPC mora

| Onde | Quem |
|---|---|
| `plano/npcs.md` | Quem **atravessa a campanha** |
| `plano/NN-capitulo/npcs.md` | Quem **só aparece naquele capítulo** |

O critério, para não ficar na dúvida a cada NPC: **ficha consultada em três ou mais
capítulos, ou NPC que muda ao longo da campanha, mora no `npcs.md` da raiz.** O resto fica
no capítulo.

O "que muda" é o caso mais importante e o mais fácil de errar. Um vilão que aparece
poderoso no capítulo 4 e exausto no capítulo 8 tem **as duas fichas lado a lado no
`npcs.md` da campanha** — é a comparação entre elas que conta a história, e separá-las em
dois capítulos esconde justamente isso.

O `npcs.md` de cada capítulo tem duas seções:

- **Da campanha** — quem vem do `npcs.md` da raiz, com link, e **o que muda aqui**:
  quantos são, em que estado, o que sabem, como se comportam nesta cena. Não repita a
  ficha; diga a diferença.
- **Só deste capítulo** — ficha completa, porque não existe em outro lugar.

Assim o Mestre abre a pasta do capítulo e tem tudo à mão, sem ficha duplicada em quinze
arquivos que depois divergem entre si.

As **regras de combate autônomo** da casa (teste de reação por NPC; longo alcance primeiro;
alvo mais próximo, depois pior reação, depois quem causou mais dano; ponto de impacto nos
dados) estão no `CLAUDE.md` e valem como padrão — repita-as no `plano/README.md` da
campanha, para o Mestre não precisar procurar.

## Registrar o histórico

Marcado o capítulo atual, o registro é uma linha:

```
campanha.py acontecimento \
  --texto "Teste de Reação do anão: 6 — muito ruim. Ele parte para cima." \
  --imagem caminho/da/ilustracao.png
```

A ilustração é copiada para `plano/NN-.../`; o log na pasta de jogo só aponta para ela.

Sem `--evento`, o fato vai para o **capítulo atual** — é o caso normal durante a sessão.
Passe `--evento` (número ou nome da pasta) só para anotar em outra cena, corrigindo algo
depois.

**Todo acontecimento relevante sai com ilustração** (seção Imagens, abaixo). Sem ferramenta
de geração, passe `--prompt` no lugar de `--imagem` — o prompt fica colado na mesma linha
do fato.

**Cena que os jogadores inventaram**, fora do plano, ganha pasta própria:

```
campanha.py evento --titulo "O interrogatório no estábulo" \
  --onde "Estábulo dos fundos, Wallace" --quem "Comam, Jah" \
  --capitulo 02 --resumo "Nada disso estava no plano."
```

Ela nasce em `campanha/NN-.../` com o próximo número livre — contado sobre o plano *e*
sobre as cenas já jogadas, para não colidir com capítulo nenhum. Capítulo que **está** no
plano não precisa disto: `atual --capitulo N` já abre a pasta dele.

**O que merece virar acontecimento:** decisão de jogador, resultado de dado que mudou o
rumo, dano relevante, NPC que morreu ou mudou de lado, item ganho ou perdido, informação
descoberta, promessa feita. Registre o **resultado do dado quando ele importou** — é o
que permite reconstruir a cena meses depois e o que dá peso ao que aconteceu.

**O que não merece:** cada rolagem de uma luta longa, conversa sem consequência,
descrição de cenário. O histórico é para consultar, não para transcrever.

Escreva no passado e em terceira pessoa, curto — uma linha por acontecimento. O detalhe
longo vai no corpo do README da pasta de jogo, acima da lista.

## O estado do mundo

O log de acontecimentos responde *o que aconteceu*. Ele **não** responde *como as coisas
estão agora* — e é essa a pergunta que o Mestre faz toda vez que um NPC volta à cena. Ler
quarenta linhas de log antes de abrir a boca do taberneiro não funciona.

Por isso **toda mudança que sobrevive à cena é anotada**, além do acontecimento:

```
campanha.py anotar --npc "Donnwulf" --tag ferimento \
  --texto "Braço direito quebrado na queda de braço. Maneta até curar; a fratura é
           permanente por decisão do Mestre."
```

| Quem mudou | Opção | Vai para |
|---|---|---|
| Um NPC | `--npc "Donnwulf"` | `campanha/NN-.../npcs.md` |
| Um personagem de jogador | `--pj "Negrum Carneiriums"` | `campanha/NN-.../grupo.md` |
| Um lugar, um objeto, uma informação que correu | `--coisa "A Âncora Quebrada"` | `campanha/NN-.../lugares.md` |

Os três arquivos moram na **pasta de jogo** do capítulo, ao lado do README — nunca no
plano, que guarda o que foi *imaginado* e não se mexe. Cada sujeito vira uma seção `##`,
e cada mudança uma linha datada. O script cria o arquivo na primeira anotação, já com o
link de volta para o `npcs.md` do plano.

`--tag` classifica em uma palavra: `ferimento`, `morte`, `item`, `relação`, `informação`,
`promessa`, `lugar`. Serve para varrer depois — não é lista fechada.

### O consolidado

Toda anotação regera **`campanha/mundo.md`**, que junta os três arquivos de **todos os
capítulos**, agrupados por sujeito e marcados com o capítulo de origem. É o arquivo a ler
para saber em que estado o mundo está — e é ele que resolve o problema de o braço quebrado
no capítulo 1 continuar quebrado no capítulo 7.

Ele é **gerado**: não edite entre os marcadores. Corrija no arquivo do capítulo e rode
`campanha.py mundo`. `estado --json` devolve o caminho dele em `mundo`, e os três arquivos
do capítulo atual em `capitulo_atual_estado`.

### O que anotar, e o que não

**Anote** o que valeria uma correção de ficha se o NPC tivesse ficha: ferimento que fica,
morte, item que trocou de dono, dinheiro ganho ou perdido, dívida, promessa, segredo
revelado, relação que mudou de patamar, porta arrombada que segue arrombada, cavalo que
morreu. Escreva a **consequência mecânica** junto quando houver — *"Maneta (um braço) até
curar"* vale mais que *"quebrou o braço"*.

**Não anote** o que passa com a cena: quem estava sentado onde, humor de momento, resultado
de dado sem consequência. Reação já rolada não entra aqui — mora no `reacoes.json` da skill
`reacao`; anote só quando a atitude **mudou** por algo que aconteceu em jogo.

**Fato e consequência são dois registros.** O `acontecimento` conta a história em uma linha
e entra no log; o `anotar` deixa o mundo diferente. Quando os dois cabem, rode os dois — a
duplicação é de propósito, porque servem a leituras diferentes.

### A bolsa

Dinheiro tem arquivo próprio, `campanha/bolsa.md`, porque não é um fato que aconteceu uma
vez: é um **saldo**, e saldo se consulta.

```
campanha.py bolsa --pj "Jah Kagadu" --valor +300 --motivo "Bolsa furtada de Giles (cap. 01)"
campanha.py bolsa --npc "Giles Mão-de-Prata" --valor -300 --motivo "Furtada por Jah Kagadu"
campanha.py bolsa                # a tabela de saldos; --mostrar imprime o extrato
```

Cada lançamento é uma linha datada com sinal e motivo; o **saldo de cada um é recalculado
a partir das linhas**, então dá para corrigir um erro editando o arquivo e rodando
`bolsa` de novo. Vale para NPC também — o mercador que perdeu a bolsa tem o lado dele.

**Todo PJ abre a bolsa com o saldo inicial**, no momento em que entra na campanha:

```
campanha.py bolsa --pj "Jah Kagadu" --valor +690 --inicial \
  --motivo "Saldo inicial: Riqueza Média ($1.000) menos $310 de equipamento da ficha"
```

A conta é a do livro (`02-criacao-de-personagem.md`, "Quantidade Inicial de Recursos"):
**recursos iniciais do nível de Riqueza menos o custo do equipamento da ficha**
(`custo_total` no `personagem.json`).

| Riqueza | Recursos, em cenário de fantasia |
|---|---|
| Falido | $0 |
| Pobre | $200 (1/5) |
| Batalhador | $500 (1/2) |
| **Média** (padrão) | **$1.000** |
| Confortável | $2.000 (2×) |
| Rico | $5.000 (5×) |

`--inicial` põe o lançamento **no começo do extrato** mesmo que seja registrado depois dos
outros, para o histórico do dinheiro se ler de cima para baixo. NPC não precisa disso,
salvo quando o dinheiro dele estiver em jogo — o mercador que carrega $300 no cinto
merece o lançamento, o resto da taberna não.

**A ficha do personagem não é mexida por causa de moeda.** `personagem.json`,
`personagem.md` e `ficha.jpg` só mudam quando o usuário pedir; até lá, o que a mesa
ganhou e gastou mora aqui. Quando o pedido vier, quem edita é a
`criar-personagem-gurps`, que recalcula peso e Carga.

### A saúde

Pontos de vida e Fadiga mudam a cada rodada de combate, e ferimento sério dura capítulos.
Os dois moram em **`campanha/saude.md`**, pela mesma razão da bolsa: são **estado**, não
fato acontecido.

```
campanha.py saude --pj "Negrum Carneiriums" --pv -3 --motivo "Machadada do orc (cap. 04)"
campanha.py saude --pj "Irmão Kaelric" --fadiga -2 --motivo "Correu de armadura completa"
campanha.py saude --npc "Donnwulf" --estado "Braço direito incapacitado (Maneta até curar)"
campanha.py saude --npc "Donnwulf" --curar "braço direito"     # quando sarar
campanha.py saude                    # a tabela; --mostrar imprime o histórico
```

`--pv` e `--fadiga` vão **com sinal**: negativo é dano ou cansaço, positivo é cura ou
descanso. O total é recalculado a partir dos lançamentos e comparado com o **máximo da
ficha** — por isso a tabela mostra `11/12`, e não `-1`. NPC sem ficha aparece só com o
acumulado.

`--estado` é para o que **não passa com a cena**: membro incapacitado, osso quebrado,
cegueira, doença, veneno em curso. Escreva a **consequência mecânica** junto — *"Maneta
(um braço) até curar"* vale mais que *"quebrou o braço"*. Quando sarar, `--curar` com
parte do texto encerra o estado, que sai da tabela mas fica no histórico.

**O que não anotar:** o dano de um golpe que já foi curado na mesma cena, ou Fadiga que
volta com dez minutos de descanso. Lance o que ainda vale quando a cena acabar.

**A ficha não é mexida por causa de dano.** `personagem.json` guarda o PV e a Fadiga
**máximos** — o que o personagem tem quando está inteiro. O que a mesa gastou é daqui, e
some quando a campanha terminar. Ficha só muda a pedido do usuário, pela
`criar-personagem-gurps`.

### Antes de voltar a uma cena

Leia, nesta ordem: `campanha/mundo.md` (como as coisas estão), o `npcs.md` da pasta de jogo
do capítulo (o que mudou aqui) e só então o `npcs.md` do plano (como o NPC foi imaginado).
**O que está anotado ganha do plano** sempre que os dois discordarem — o plano é a intenção,
a anotação é o que a mesa fez com ela.

## Imagens do plano

Ilustração da **cena planejada**: o lugar e os NPCs. Mora em `plano/NN-.../`, junto do
README da cena — é material do plano, reusável. Antes de gerar, leia a skill **imagine**
(não copie as regras dela).

**Não desenhe personagem de jogador.** A ilustração tem de funcionar com qualquer grupo.

Duas obrigações:

1. **Imagem inicial**, sempre, ao **escrever** o capítulo no plano (`capitulo --titulo`).
   Estabelecimento: o lugar, a luz, os NPCs **antes** de qualquer fato. Não é o mapa
   top-down da `cenario-rpg`.
2. **Cada batida planejada relevante** (o que a seção de acontecimentos já filtra, quando
   ainda é plano — a porta que abre, o emboscada) ganha a sua.

Se `inicio.png` já existir na pasta do plano, derive a próxima ilustração com
`image_edit` a partir dela, para o lugar não mudar de cara.

**Prompt:** um único parágrafo **em inglês**, menos de 1.000 caracteres — o gerador ignora
o fim de prompts longos. `aspect_ratio` 16:9. A ordem que funciona:

1. **Estilo primeiro**, sempre o mesmo ao longo da campanha, para as imagens parecerem um
   conjunto: *"Digital illustration, fantasy RPG scene art, clean linework with warm soft
   coloring, hand-drawn look"*. Nunca "photo" nem "photorealistic".
2. **O lugar**, com a luz e a hora: taberna apertada de porto à noite, lareira, fumaça,
   lamparinas, chuva na janela. A luz é o que mais muda o clima da imagem.
3. **Duas ou três figuras, não a multidão inteira**, com os mesmos detalhes físicos que o
   `npcs.md` deu — se o taberneiro tem meia orelha e avental sujo lá, aqui também.
4. **O que está acontecendo**: o braço-de-ferro no meio do círculo, o guarda sozinho no
   canto bebendo rápido. Ação concreta vale mais que adjetivo.
5. **Enquadramento**: *"wide interior shot"*, *"eye-level"*, *"seen from the doorway"*.

Fora: **personagem de jogador**, retrato (a cena é o assunto; retrato de PJ tem lugar
próprio em `personagens/<slug>/foto-prompt.md`), texto na imagem (peça `"no text, no
lettering, no signage"` — todo gerador escreve garatuja), grid ou número, e nome de artista
vivo (descreva a técnica, não o autor).

Grave no plano:

```
campanha.py imagem-inicial --arquivo <png-gerado> --capitulo N
campanha.py acontecimento --texto "..." --imagem <png-gerado>
```

Cena inventada na mesa, sem pasta no plano: a ilustração cai na pasta de jogo, que é o
único lugar que ela tem.

**Se não houver como gerar imagem** (ferramenta ausente, bloqueio, falha), **não invente
que a figura existe.** Escreva o prompt e anexe-o ao texto:

```
campanha.py imagem-inicial --prompt "Digital illustration, ..." --capitulo N
campanha.py acontecimento --texto "..." --prompt "Digital illustration, ..."
```

O README do plano fica com o prompt colado, pronto para o Mestre colar num gerador. Mostre
o prompt também na resposta, em bloco de código.

## O capítulo atual

`atual --capitulo 3` faz três coisas:

1. Grava `**Capítulo atual:** 03` no README da campanha.
2. **Abre a pasta de jogo** `campanha/03-fechem-os-portoes/`, espelhando o nome da pasta
   do plano, com um README que já aponta de volta para o planejado.
3. Regera o índice.

É assim que **outras skills sabem onde gravar o que produzem**: a `atualizar-mapa`, por
exemplo, põe a imagem da mesa em `campanha/03-fechem-os-portoes/`.

**Marque o capítulo ao começar a sessão.** A ilustração de abertura já deveria estar no
plano; sem capítulo marcado, as outras skills gravam num lugar genérico e avisam.

`estado --json` devolve:

| Campo | O quê |
|---|---|
| `capitulo_atual` | O número (`"03"`) |
| `capitulo_atual_pasta` | `campanha/03-...` — **a pasta de jogo, onde se grava** |
| `capitulo_atual_plano` | `campanha/plano/03-...` — o planejado, para leitura |
| `capitulo_atual_mapa` | O índice de hexágonos que o plano declara para a cena |

Todos `null` se ninguém marcou. **Quem produz arquivo usa `capitulo_atual_pasta`**; o
`_plano` serve para consultar a cena, não para escrever nela.

## Contrato para as outras skills

Outras skills registram na campanha **por aqui**, nunca escrevendo direto nos arquivos.
Ao escrever uma skill nova que deva alimentar a campanha, inclua isto nela:

> **Registrar na campanha.** Se houver campanha ativa
> (`campanha.py estado --json` devolve `"ativa": true`), registre o que esta skill
> produziu de relevante:
> ```
> python .claude/skills/campanha/scripts/campanha.py acontecimento \
>   --texto "<uma linha, no passado>" \
>   --imagem <png>   # ou --prompt "..." se não houver geração
> ```
> A imagem (ou o prompt) segue a seção **Imagens do plano** desta skill. Não havendo
> campanha ativa, siga sem registrar — não crie campanha por conta própria.

E, se a skill **muda o mundo de forma duradoura** (ferimento que fica, morte, item que
trocou de dono, relação que virou), acrescente também:

> **Anotar a mudança.** Além do acontecimento, registre o que ficou diferente:
> ```
> python .claude/skills/campanha/scripts/campanha.py anotar \
>   --npc "<NPC>"   # ou --pj "<personagem>", ou --coisa "<lugar/objeto>"
>   --tag ferimento --texto "<o que mudou, com a consequência mecânica>"
> ```
> Isso vai para `campanha/NN-.../npcs.md` (ou `grupo.md`/`lugares.md`) e regera
> `campanha/mundo.md`. O acontecimento conta o fato; a anotação é o que o Mestre lê da
> próxima vez.

E, se a skill **produz arquivo** (imagem, mapa, tabela), grave-o na pasta do capítulo
atual (`campanha/NN-.../`, **não** a do plano), lendo `capitulo_atual_pasta` do mesmo
`estado --json`. Sem capítulo marcado, grave no lugar genérico e **diga por quê** — a
`atualizar-mapa` imprime uma linha `Destino:` em toda execução, e é um bom padrão a copiar.

Quem chama decide o que é relevante. Exemplos do que faz sentido: a `atualizar-mapa`
registrando o posicionamento inicial de um combate; a `criar-personagem-gurps`
registrando que um personagem entrou no grupo; uma skill de combate registrando o
desfecho.

**Nunca crie campanha automaticamente** dentro de outra skill. Sem campanha ativa, a
outra skill simplesmente não registra.

## Encerrar

```
campanha.py encerrar --desfecho "Como terminou, em um parágrafo."
```

Marca `Estado: encerrada`, carimba a data, acrescenta o desfecho e move `campanha/`
inteira para `historico/campanhas/<slug>/` — o plano e o que de fato aconteceu, lado a
lado, do jeito que ficaram. Depois disso o repositório fica sem campanha ativa e pronto para a próxima.

Campanha arquivada é **leitura**, não material de trabalho: não edite o que já foi
arquivado. Se um personagem ou um NPC voltar numa campanha nova, copie o que interessa
para a campanha nova em vez de reabrir a antiga.
