# Volume 1 — A Âncora Quebrada · elenco

Quem aparece no volume e **onde está a referência visual de cada um**. É a folha de modelo
que segura a semelhança de um quadro para o outro: o retrato dá o rosto, a folha dá o
corpo, a roupa e as armas de três ângulos.

**Estado:** os `npc.md` estão escritos, os 23 prompts estão gravados com `--so-prompt` e
**o cenário do volume está gerado** — `cenario-salao.png`, 1 chamada, a única imagem do
passo 5. Faltam os avatares (passo 6) e as folhas de modelo (passo 7), **uma por vez**.

Conferência: `python .claude/skills/quadro-hq/scripts/gerar_quadro.py elenco --roteiro campanha/hq/vol-01-a-ancora-quebrada/roteiro.json`

---

## Personagens de jogador — 5

O retrato já existe na pasta de cada um (vem da skill `criar-personagem-gurps`). Falta só
a folha de modelo.

| Slug | Quadros | Retrato que serve de referência | Folha de modelo | Falta |
|---|---|---|---|---|
| `negrum-carneiriums` | 30 | `personagens/negrum-carneiriums/foto.png` | `personagens/negrum-carneiriums/modelo-hq.png` | **modelo** |
| `nelsowned` | 23 | `personagens/nelsowned/foto.png` (+ `corpo-inteiro.png`) | `personagens/nelsowned/modelo-hq.png` | **modelo** |
| `irmao-kaelric` | 15 | `personagens/irmao-kaelric/foto.png` (+ `corpo-inteiro.png`) | `personagens/irmao-kaelric/modelo-hq.png` | **modelo** |
| `jah-kagadu` | 15 | `personagens/jah-kagadu/**foto.jpg**` | `personagens/jah-kagadu/modelo-hq.png` | **modelo** |
| `comam-obabaroy` | 11 | `personagens/comam-obabaroy/foto.png` (+ `foto-corpo.png`) | `personagens/comam-obabaroy/modelo-hq.png` | **modelo** |

> **O retrato do Jah é `.jpg`, e isso está resolvido.** A `imagem_de_referencia()` da skill
> `quadro-hq` tenta cada nome em `.png`, `.jpg` e `.jpeg`, nessa ordem. O comando `elenco`
> confirma: _"PJ jah-kagadu — só retrato (foto.jpg)"_, e o prompt gravado em
> `personagens/jah-kagadu/modelo-hq-prompt.md` lista o `foto.jpg` como referência.
> **Não se cria `foto.png` e não se duplica arquivo na pasta dele.**

## NPCs — 9, todos com pasta em `campanha/npcs/<slug>/`

Nenhum tem nada ainda: precisam de **avatar** (retrato) e de **folha de modelo**. A
descrição física de cada um está no `npc.md`, tirada do `npcs.md` do plano e do `npcs.md`
da pasta de jogo do capítulo — **o anotado ganha do planejado**.

| Slug | Quem é | Quadros | Por que precisa de modelo |
|---|---|---|---|
| `hoel-meia-orelha` | O taberneiro | 29 | É o segundo personagem mais presente do volume, e precisa de **dois estados** (vivo e morto) sendo reconhecivelmente o mesmo homem. **Avatar fixado** — ver a nota da meia orelha, abaixo |
| `bronwyn` | A filha de Giles | 16 | Carrega a linha inteira do NelsOwned; o colar de ouro sai do pescoço dela na pág. 13 |
| `donnwulf` | O pedreiro | 12 | O braço entalado tem de ser o mesmo braço da pág. 4 à pág. 11 |
| `giles-mao-de-prata` | O mercador de lã | 7 | Anéis em quatro dedos, e a bolsa que sai do cinto dele na pág. 5 |
| `osric-de-bannock` | O guarda do castelo | 6 | **Volta no capítulo 3**, mandando no portão: o rosto se reusa |
| `morto-vivo-tropeiro` | O da frente | 6 | Aparece nas págs. 15 a 18; o caneco preso na mão é a marca dele |
| `morto-vivo-apostador` | O do círculo | 5 | É o que pega fogo no braseiro e começa o incêndio |
| `morto-vivo-vulto` | O quarto, anônimo | 5 | Perde a perna na pág. 17 e continua se arrastando |
| `wat` | O menino do estábulo | 4 | **Dois estados** (vivo na pág. 5, morto na 15). A página 15 inteira depende de o rosto ser reconhecível |

### A meia orelha do Hoel é dita, não desenhada

**Decisão do usuário, 16/09/2026, depois de três tentativas.** O gerador recusou a
mutilação em **três métodos diferentes**:

| # | Método | O que saiu |
|---|---|---|
| 1 | `/generations` com a descrição direta da mutilação | As duas orelhas inteiras |
| 2 | `/generations` com a cabeça em três quartos virada para expor a orelha, cabelo para trás, lateralidade dita duas vezes | Obedeceu ao enquadramento, virou a cabeça, iluminou aquela orelha — **e a desenhou inteira** |
| 3 | `/edits` com a imagem como referência e fidelidade alta, a forma descrita sem palavra de violência ("um semicírculo que para reto no alto, como uma moeda cortada ao meio") | Repôs o pano de secar pedido no mesmo parágrafo e **recusou a orelha de novo** |

Nas três ele acertou tudo o mais — idade, corpanzil, avental, sépia, enquadramento.
**Entende o pedido e não o executa.**

**Consequências no volume, já aplicadas:**

- **O avatar com as duas orelhas está aprovado** e é o que vale. Não se gasta mais chamada
  com isso — nem por `/edits`, nem por máscara, nem na folha de modelo do passo 7.
- **Dois quadros foram reescritos** para não prometerem o que não vai ser desenhado:
  `p2q2` (a apresentação do taberneiro) e `p20q5` (o close do morto antes da machadada).
  Nenhum outro dos 127 prometia a mutilação.
- **O apelido é dito em dois recordatórios**, e os dois já estavam no roteiro, tirados da
  narração do Mestre: `p2q2` — "O dono. Hoel Meia-Orelha." — e `p19q6` — "Vinte anos de
  estrada. Meia orelha. O homem que servia a sua cerveja sem você pedir." É por eles que o
  leitor fica sabendo.
- **O `npc.md` dele guarda o registro inteiro dos três métodos**, para que o volume 2 não
  recomece a tentativa do zero.

## Figurantes — sem modelo neste volume

Ficam descritos no prompt do quadro em que aparecem, e **não entram no campo `elenco`** do
roteiro (senão o comando `elenco` cobra modelo deles).

| Quem | Onde | Por quê |
|---|---|---|
| **Teressy**, a viajante do canto | pág. 2, quadro 6 | Aparece em **um quadro só** e nunca fala: ninguém na mesa chegou perto dela a noite inteira. Não paga duas chamadas. **Se ganhar peso num volume futuro** — ela tem gancho solto no plano, a bolsa que não larga — **aí sim recebe pasta em `campanha/npcs/teressy/`, avatar e folha de modelo** |
| O tropeiro de mão grande | pág. 8, quadro 6 | Uma fala, um quadro |
| O círculo de apostadores, os quarenta fregueses, as lavadeiras, o remendão | por todo o volume | Multidão desenhada, não elenco |
| O barbeiro | — | **Nunca chega.** Não aparece em quadro nenhum |

## O cenário

| Arquivo | O que é | Usado em |
|---|---|---|
| `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png` | O estabelecimento do salão, gerado para este volume | **75 dos 127 quadros** |
| `cenario-salao-prompt.md` | O prompt, com a geografia tirada de `cenarios/taberna3.png` | — |

**As ilustrações do plano não servem de referência.** `inicio.jpg` e
`mortos-vivos-na-porta.jpg` são a mesma taberna, mas anteriores à errata de cenário: as
duas mostram porto, mastros de navio e um leme na parede. Wallace não tem porto. O
`roteiro.json` não aponta para nenhuma das duas.

### A casa tem duas fontes de fogo

Decisão da mesa, e ela vale para o enquadramento e para a luz de **32 quadros**:

| Fonte | Onde | O que acontece nela |
|---|---|---|
| **A lareira oeste** | parede oeste, ao lado do balcão | A grande, a que aquece o salão. É onde o NelsOwned canta em cima do banco e onde fica a mesa redonda do braço-de-ferro. Dá o âmbar das páginas 1 a 15 |
| **A lareira sudeste** | L10–L11 | Menor, de alvenaria. É a pedra em que o morto bate quando o Negrum o projeta (pág. 18) |
| **O braseiro de ferro** | M11, ao lado dela | Onde o Kaelric empurra o morto (pág. 17) e **de onde o incêndio começa** (pág. 21) |

**Nenhum quadro do roteiro diz mais só "lareira": todos dizem qual.** As 32 descrições de
luz foram revistas uma a uma — `lareira oeste` até a pág. 15, `lareira sudeste` e
`braseiro sudeste` nas 17 e 18, e `o incêndio` da 19 em diante, que não é nenhuma das
duas: é a casa queimando.

### Atenção ao tom da referência: ela é escura

O `cenario-salao.png` foi **aprovado com três ressalvas**, e uma delas pesa no resto do
volume: **a imagem é penumbra**, um salão vazio com dois pontos de fogo e as paredes
sumindo no escuro. As outras duas são menores — a âncora de ferro saiu **por dentro**, em
relevo acima da lareira grande, quando o registro a põe pendurada sobre a porta pelo lado
de fora; e no lugar do **braseiro de ferro** saiu um caldeirão baixo de tripé.

**O campo `luz` de cada quadro é que manda, não a referência.** O volume promete as
páginas 1 a 15 quentes e cheias — "âmbar quente", "o quadro mais claro da página" — e é
isso que vale quando os dois discordarem. A referência serve para a **geografia** (onde
fica o balcão, a lareira, o tapete, a porta), não para o tom.

**Isto tem de ser conferido no passo 9, no quadro 1 da página 1.** Se a arte sair escura
demais por arrasto da referência, é ali que se descobre — antes dos outros 126 quadros — e
aí se corrige o `estilo` do `roteiro.json` ou se deixa de mandar o cenário nos quadros
claros.

---

## O gasto, passo a passo

| Passo | O quê | Quantas | Estado |
|---|---|---|---|
| 5 | Estabelecimento do salão | 1 | **feita** |
| 6 | Avatares de NPC | 9 | a fazer, **uma por vez**, na ordem da presença |
| 7 | Folhas de modelo (9 NPCs + 5 PJs) | 14 | a fazer, **uma por vez** |
| 9 | A arte dos quadros | 127 | a fazer, **uma por vez** |
| | **Total do volume** | **151** | 1 feita, 150 a fazer |

**Ordem dos avatares e das folhas, por presença em quadro:** `hoel-meia-orelha` (29),
`bronwyn` (16), `donnwulf` (12), `giles-mao-de-prata` (7), `osric-de-bannock` (6),
`morto-vivo-tropeiro` (6), `morto-vivo-apostador` (5), `morto-vivo-vulto` (5), `wat` (4).
Se o crédito acabar no meio, que tenha acabado depois do Hoel e não depois de um figurante.

**Hoel e Wat têm dois estados**, e cada estado é uma imagem que se aprova sozinha: o
taberneiro vivo e o taberneiro morto; o menino inteiro e o menino rasgado. Isso pode levar
os 9 avatares a 11 — decisão do usuário quando chegarmos a cada um deles.

Os 23 prompts de personagem já estão gravados ao lado de onde a imagem vai cair
(`avatar-prompt.md` e `modelo-hq-prompt.md` em cada pasta). A descrição foi passada
explícita em `--descricao`: sem isso o script despeja os primeiros 1200 caracteres do
`npc.md` no prompt, com cabeçalho markdown e caminhos de arquivo dentro.
