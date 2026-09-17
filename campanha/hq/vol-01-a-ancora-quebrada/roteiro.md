# Volume 1 — A Âncora Quebrada · roteiro

**22 páginas · 127 quadros.** Recorte em [`00-recorte.md`](00-recorte.md), cenas em [`01-cenas.md`](01-cenas.md).
**Estado:** proposto — aguardando aprovação antes de fixar o elenco e gastar imagem.

Este arquivo é o roteiro legível. A fonte que os scripts leem é [`roteiro.json`](roteiro.json), gerado do mesmo material: cada quadro leva a caixa em % da página, o enquadramento, a luz, o que se vê (pt-BR), o `visual` em inglês para o gerador, o elenco por slug, o cenário de referência e os balões com posição.

## Como este roteiro trata a fala

**Balão de fala só onde houve fala registrada.** As falas vêm do que o Mestre narrou ou do que o jogador declarou no grupo, enxugadas para caber no balão. Onde o registro não tem fala, o quadro usa **recordatório** com o texto da própria narração — nunca diálogo inventado para tapar buraco.

**O ânglico do Negrum (NH 8)** sai curto, sem conectivo e sem conjugação difícil: "TU. BRAÇO. EU E TU." É a mesma frase que na mesa foi "desafiar o Donnwulf para queda de braço" — o sotaque é interpretação, não fato novo.

**O som do assassinato** é a sílaba TUM, repetida e encolhendo: corpo 120 na pág. 11 q4, 84 no q5, 58 no q6 e 34 na pág. 12 q1, onde vira minúscula. O golpe fica sempre fora de campo.

**Estilo fixo do volume** (vai em todo prompt):

> Hand-drawn comic art in pencil and ink on warm buff toned paper: firm dark ink contour lines, fine graphite hatching and crosshatching for all modelling and shadow, over a restrained wash of sepia and warm grey with only a slight flesh tint. The buff paper tone is the lightest value in every panel and shows through everywhere; highlights are bare paper, never white paint. Muted, almost monochrome warm palette — no flat digital colour, no vivid saturation, no glossy rendering. FIRELIGHT IS RENDERED AS VALUE, NOT AS HUE: the nearer the fire, the more paper is left bare and the sparser the hatching; the further from it, the denser and blacker the ink, until the far corners are solid shadow. Medieval realism, tech level 3, no gunpowder. Setting: Wallace, a pastoral frontier town of Caithness on the edge of the Great Desert in Yrth — sheep pens, wool, dust and stone. THIS TOWN IS LANDLOCKED: no sea, no harbour, no docks, no ships, no boats, no masts, no rigging, no ship's wheel, no nets, no fishing gear anywhere in any panel; the iron anchor over the tavern door is an old joke, not a sign of the sea. Night, fine cold rain outside; tavern interior lit by a stone hearth, hanging oil lanterns and table candles.

---

## Página 1 — A âncora numa terra sem mar

_Cena 1 · A âncora numa terra sem mar · 5 quadros_

### 1.1 · plano geral, câmera baixa na estrada, leve contra-plongée

**Caixa:** `[0, 0, 100, 30]` · **Luz:** crepúsculo azul frio contra tochas amarelas na muralha

**O que se vê.** A caravana entrando por Wallace pouco antes do anoitecer: quatro carroças cobertas, bois, a muralha de pedra crescendo à frente e o castelo do Lorde William lá em cima, na ladeira, já com luz nas seteiras. Chove fininho.

- **narracao** · em `[26, 16]`
  > WALLACE. Fronteira oeste de Caithness, na orla do Grande Deserto.

### 1.2 · plano médio, na altura do peito

**Caixa:** `[0, 30, 50, 24]` · **Luz:** lanterna de carroça, luz baixa e quente

**O que se vê.** Os cinco descendo das carroças na rua dos currais: lama até o tornozelo, capuzes, poeira de quatro dias de estrada na roupa. Os carroceiros ficam, enrolados nas mantas.

**Elenco:** `comam-obabaroy`, `irmao-kaelric`, `jah-kagadu`, `negrum-carneiriums`, `nelsowned`

- **narracao** · em `[50, 13]`
  > Quatro dias de estrada, poeira até nos dentes. Os carroceiros ficaram dormindo junto às carroças.

### 1.3 · plano fechado, câmera dentro do curral

**Caixa:** `[50, 30, 50, 24]` · **Luz:** escuro azulado, um facho amarelo vindo da porta da taberna

**O que se vê.** Os currais na chuva: cães presos às estacas, todos uivando ao mesmo tempo, os focinhos apontados para o mesmo lado — o oeste. As ovelhas amontoadas no canto oposto.

- **narracao** · em `[52, 15]`
  > Os cães dos currais uivam faz um tempo. Ninguém reparou ainda.

### 1.4 · plano médio baixo, de fora para dentro

**Caixa:** `[0, 54, 55, 46]` · **Luz:** a luz amarela da porta contra a chuva escura

**O que se vê.** A porta da taberna vista da rua: madeira grossa, uma fresta de luz amarela por baixo, fumaça saindo pela chaminé, e o Irmão Kaelric abaixando a cabeça para caber na soleira.

**Elenco:** `irmao-kaelric`, `negrum-carneiriums`, `nelsowned`

_Sem balão._

### 1.5 · contra-plongée forte, quase de baixo

**Caixa:** `[55, 54, 45, 46]` · **Luz:** contraluz: a âncora escura contra o brilho da porta

**O que se vê.** A âncora de ferro pendurada sobre a porta, enorme e enferrujada, a chuva escorrendo dela; atrás, o céu preto. Lá de dentro vem música.

- **narracao** · em `[30, 14]`
  > A Âncora Quebrada. A semanas de viagem de qualquer água navegável.
- **canto** · em `[62, 80]`
  > ♪  ♪  ♪

---

## Página 2 — Quem está na casa

_Cena 1 · A âncora numa terra sem mar · 7 quadros_

### 2.1 · plano geral do salão, câmera na altura dos ombros, profundidade

**Caixa:** `[0, 0, 100, 42]` · **Luz:** lareira grande da parede oeste, à esquerda do quadro; lanternas de óleo penduradas; âmbar quente

**O que se vê.** O salão cheio: NelsOwned de pé em cima de um banco perto da lareira, cantando de braços abertos; quarenta gargantas errando o refrão alto e felizes, canecos batendo na mesa no tempo certo, moedas de cobre chovendo no assoalho de serragem.

**Elenco:** `nelsowned` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[27, 17]`
  > Está cheia, quente, e cheira a caldo de carneiro, lenha molhada e cerveja derramada.
- **canto** — NelsOwned · em `[66, 30]`, apontando para `[36, 48]`
  > ♪  ♪  ♪

### 2.2 · close, três quartos

**Caixa:** `[0, 42, 33, 19]` · **Luz:** lanterna do balcão, por cima

**O que se vê.** Hoel Meia-Orelha atrás do balcão, enchendo canecos sem olhar para eles; cinquenta anos, corpulento, o pano de secar no ombro esquerdo, e o olhar de quem não se impressiona com nada.

**Elenco:** `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[52, 16]`
  > O dono. Hoel Meia-Orelha.

### 2.3 · plano médio

**Caixa:** `[33, 42, 34, 19]` · **Luz:** velas da mesa, por baixo

**O que se vê.** Giles Mão-de-Prata de pé na mesa comprida do tapete vermelho, caneco erguido, anéis em quatro dedos, contando pela terceira vez que a filha vai casar. Bronwyn, ao lado, não levantou os olhos do prato.

**Elenco:** `giles-mao-de-prata`, `bronwyn` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Giles · em `[52, 18]`, apontando para `[40, 48]`
  > ...E A MINHA FILHA CASA EM CARRICK!

### 2.4 · plano médio, de cima do círculo

**Caixa:** `[67, 42, 33, 19]` · **Luz:** lareira oeste atrás, silhuetas quentes

**O que se vê.** Donnwulf derrubando mais um braço contra a mesa redonda e gritando o próprio nome; o círculo de apostadores berrando junto, umas quarenta moedas de prata na madeira.

**Elenco:** `donnwulf` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — Donnwulf · em `[46, 20]`, apontando para `[40, 52]`
  > DONNWULF!

### 2.5 · close lateral, perfil

**Caixa:** `[0, 61, 50, 20]` · **Luz:** meia-luz, o rosto metade na sombra

**O que se vê.** Osric de Bannock no balcão, a poucos banquetos do grupo: capa ainda nos ombros, a cota de malha aparecendo por baixo, bebendo rápido e olhando o copo.

**Elenco:** `osric-de-bannock` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[58, 16]`
  > Um guarda do castelo. Não falou com ninguém a noite toda.

### 2.6 · plano médio, da mesa do canto

**Caixa:** `[50, 61, 50, 20]` · **Luz:** uma vela só, sombra atrás dela

**O que se vê.** Teressy na mesa do canto, de costas para a parede, capa boa e botas gastas de estrada, bebendo devagar, com uma bolsa de couro entre os pés. Ao fundo, o Comam no terceiro caneco.

**Elenco:** `comam-obabaroy` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[58, 17]`
  > Não largou a bolsa nem para aplaudir.

### 2.7 · faixa larga, plano médio de costas

**Caixa:** `[0, 81, 100, 19]` · **Luz:** lareira oeste à frente dele

**O que se vê.** O Negrum levantando da mesa e indo na direção do círculo do braço-de-ferro, de costas para a câmera, ombros enormes, a cabeça raspada; o círculo ao fundo abrindo para ele.

**Elenco:** `negrum-carneiriums`, `donnwulf` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Negrum · em `[62, 26]`, apontando para `[36, 38]`
  > TU. BRAÇO. EU E TU.

---

## Página 3 — Dois minutos de nada

_Cena 2 · O braço-de-ferro · 5 quadros_

### 3.1 · plano médio largo

**Caixa:** `[0, 0, 100, 26]` · **Luz:** lareira oeste lateral, quente

**O que se vê.** O círculo abrindo para deixar o Negrum passar; bancos arrastados, canecos batendo. Donnwulf mede os ombros dele de cima a baixo, ri alto, cospe na palma da mão e estende o braço.

**Elenco:** `donnwulf`, `negrum-carneiriums` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Donnwulf · em `[46, 20]`, apontando para `[36, 46]`
  > SENTA AÍ, ENTÃO.

### 3.2 · close extremo nas mãos

**Caixa:** `[0, 26, 50, 22]` · **Luz:** luz rasante da lareira oeste, contraste alto

**O que se vê.** As duas mãos se agarrando em cima da madeira: a do pedreiro calejada e quadrada, a do Negrum quase o dobro do tamanho.

**Elenco:** `donnwulf`, `negrum-carneiriums`

- **onomatopeia** · em `[70, 24]`, corpo 70
  > TUM

### 3.3 · plano médio do círculo

**Caixa:** `[50, 26, 50, 22]` · **Luz:** âmbar, fumaça da lareira oeste no ar

**O que se vê.** Um freguês conta até três com a mão no ar; o círculo berra; as moedas de prata em cima da mesa. Ao fundo, o Comam de costas, bebendo, sem olhar.

**Elenco:** `comam-obabaroy` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** · em `[34, 20]`
  > TRÊS!

### 3.4 · plano médio frontal, simétrico

**Caixa:** `[0, 48, 100, 30]` · **Luz:** contraluz da lareira oeste atrás dos dois, rostos em meia-sombra

**O que se vê.** Os dois braços travados no meio, verticais, e nada acontecendo. O suor na madeira, a veia no pescoço do pedreiro subindo, as moedas de prata tremendo em cima da mesa.

**Elenco:** `donnwulf`, `negrum-carneiriums` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[50, 12]`
  > Um minuto. Dois. Os dois braços travam no meio e ficam ali.

### 3.5 · duplo close no mesmo quadro

**Caixa:** `[0, 78, 100, 22]` · **Luz:** dura, de cima

**O que se vê.** À esquerda, o rosto de Donnwulf indo do vermelho ao roxo, o sorriso de deboche virando careta. À direita, o cotovelo dele escorregando no suor da madeira.

**Elenco:** `donnwulf`

- **narracao** · em `[70, 22]`
  > E então o cotovelo dele escorrega no suor da madeira.

---

## Página 4 — O estalo

_Cena 2 · O braço-de-ferro · 6 quadros_

### 4.1 · close extremo, ângulo baixo

**Caixa:** `[0, 0, 100, 30]` · **Luz:** clarão da lareira oeste, sombra dura

**O que se vê.** O braço cai contra a madeira num ângulo que braço nenhum faz, e fica ali, torto. A prata rola da mesa para o assoalho.

**Elenco:** `donnwulf`

- **onomatopeia** · em `[70, 30]`, corpo 150
  > CRAC

### 4.2 · plano geral do salão, plongée leve

**Caixa:** `[0, 30, 50, 22]` · **Luz:** âmbar, mas os rostos endurecidos

**O que se vê.** Quarenta rostos virando ao mesmo tempo; os canecos param no ar. O berro do pedreiro apaga o resto do salão.

**Elenco:** `donnwulf` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — Donnwulf · em `[46, 26]`, apontando para `[40, 62]`
  > AAAAARGH!

### 4.3 · plano médio, do balcão

**Caixa:** `[50, 30, 50, 22]` · **Luz:** lanterna do balcão atrás dele

**O que se vê.** Hoel larga o pano de secar, sai de trás do balcão empurrando gente e grita para o menino do estábulo.

**Elenco:** `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — Hoel · em `[60, 22]`, apontando para `[46, 48]`
  > WAT! O BARBEIRO! CORRE!

### 4.4 · plano médio

**Caixa:** `[0, 52, 50, 22]` · **Luz:** lareira oeste, mas o quadro mais frio que os anteriores

**O que se vê.** Donnwulf branco, dobrado sobre o próprio braço, a mão boa procurando onde segurar e sem achar lugar que não doa. O círculo de apostadores virou um semicírculo de gente calada.

**Elenco:** `donnwulf` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[70, 18]`
  > Ninguém ri.

### 4.5 · close, de baixo para cima

**Caixa:** `[50, 52, 50, 22]` · **Luz:** quente, chapada

**O que se vê.** Donnwulf procurando o Negrum por cima do ombro estragado, os olhos molhados, a voz rouca e sem raiva nenhuma.

**Elenco:** `donnwulf`, `negrum-carneiriums`

- **fala** — Donnwulf · em `[58, 22]`, apontando para `[40, 62]`
  > NÃO FOI TUA CULPA, GRANDÃO. ESSE BRAÇO JÁ VINHA AVISANDO.

### 4.6 · plano geral de fora, à chuva

**Caixa:** `[0, 74, 100, 26]` · **Luz:** azul escuro da chuva contra o amarelo das janelas

**O que se vê.** Do lado de fora, na rua dos currais: os cães todos uivando ao mesmo tempo, focinhos para o mesmo lado, e a taberna iluminada ao fundo, ruidosa, indiferente.

- **narracao** · em `[62, 20]`
  > Estão uivando faz um tempo. Ninguém aqui dentro reparou.

---

## Página 5 — O furto e o bis

_Cena 3 · O furto e o bis · 6 quadros_

### 5.1 · por cima do ombro do Jah

**Caixa:** `[0, 0, 50, 26]` · **Luz:** todos contra a luz da lareira oeste

**O que se vê.** O salão inteiro de pé e virado para a mesa redonda. Giles está entre eles, meio levantado, o caneco esquecido na mão, o corpo virado para a frente — e o cinto, portanto, virado para o Jah.

**Elenco:** `jah-kagadu`, `giles-mao-de-prata` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[58, 15]`
  > Por três segundos ninguém na casa está olhando para outra coisa.

### 5.2 · close extremo nas mãos

**Caixa:** `[50, 0, 50, 26]` · **Luz:** dura e lateral, quase sem cor

**O que se vê.** Os dedos do Jah no nó simples da bolsa de couro presa ao cinto de Giles. A bolsa sai do laço com o peso morno de quem tem muita prata dentro.

**Elenco:** `jah-kagadu`, `giles-mao-de-prata`

_Sem balão._

### 5.3 · plano médio, dois planos de profundidade

**Caixa:** `[0, 26, 50, 24]` · **Luz:** âmbar de novo, a casa relaxando

**O que se vê.** Em primeiro plano o Jah já a dois passos, indo na direção do balcão, a bolsa sumindo debaixo da capa. Ao fundo, Giles tornando a sentar e levando a mão à cintura sem pensar, franzindo a testa.

**Elenco:** `jah-kagadu`, `giles-mao-de-prata` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[62, 17]`
  > Alguém lhe enche o caneco. Ele não chega a entender o que sentiu.

### 5.4 · plano médio, contra-plongée leve

**Caixa:** `[50, 26, 50, 24]` · **Luz:** penumbra alta, a luz vindo de baixo

**O que se vê.** O Irmão Kaelric encostado numa coluna do salão com o caneco na mão, altíssimo, a cabeça quase nas vigas, olhando a bagunça toda de cima.

**Elenco:** `irmao-kaelric` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **pensamento** — Kaelric · em `[66, 22]`, apontando para `[44, 30]`
  > QUANTA AÇÃO VÃ E MUNDANA NESTE LUGAR. INCLUSIVE EU.

### 5.5 · plano médio largo, câmera na plateia

**Caixa:** `[0, 50, 100, 28]` · **Luz:** lareira oeste e lanternas, o quadro mais claro da página

**O que se vê.** NelsOwned de pé no banco, pedindo silêncio com a mão erguida; a casa protesta, ri, bate o pé no assoalho. Hoel grita do balcão. Ao fundo, o Comam bebendo, imune a tudo.

**Elenco:** `nelsowned`, `hoel-meia-orelha`, `comam-obabaroy` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — NelsOwned · em `[22, 16]`, apontando para `[31, 44]`
  > A ÚLTIMA!
- **fala** — Hoel · em `[68, 20]`, apontando para `[72, 64]`
  > CANTA AQUELA QUE TODO MUNDO SABE E A RODADA É MINHA!

### 5.6 · plano médio, panorâmico

**Caixa:** `[0, 78, 100, 22]` · **Luz:** quente no centro, frio no canto da porta

**O que se vê.** O chapéu passando de mão em mão e voltando leve; tapas nas costas do trovador. E no canto do quadro, sem ninguém reparar, Wat saindo pela porta dos fundos com um saco na cabeça contra a chuva.

**Elenco:** `nelsowned`, `wat` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[46, 18]`
  > O chapéu volta pesando pouco. Wat sai pelos fundos atrás do barbeiro.

---

## Página 6 — A xavecada

_Cena 4 · A xavecada · 5 quadros_

### 6.1 · plano médio, lateral à mesa

**Caixa:** `[0, 0, 100, 26]` · **Luz:** velas da mesa, quentes

**O que se vê.** NelsOwned chega pelo lado da mesa boa com dois canecos que ninguém pediu e faz a mesura de palco inteira: chapéu, joelho, o braço aberto.

**Elenco:** `nelsowned`, `bronwyn` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — NelsOwned · em `[50, 20]`, apontando para `[36, 60]`
  > AAAAH... MINHA SENHORA.

### 6.2 · close

**Caixa:** `[0, 26, 50, 24]` · **Luz:** vela por baixo, o pai em silhueta

**O que se vê.** Bronwyn olha primeiro para o pai, que está de costas, contando a história do noivado pela quarta vez para quem já ouviu três.

**Elenco:** `bronwyn`, `giles-mao-de-prata`

_Sem balão._

### 6.3 · close frontal

**Caixa:** `[50, 26, 50, 24]` · **Luz:** a luz mais macia da página

**O que se vê.** Bronwyn rindo. Uma risada curta, de quem foi pega desprevenida.

**Elenco:** `bronwyn`

- **narracao** · em `[40, 18]`
  > É a primeira vez que ela ri esta noite.

### 6.4 · plano médio, os dois de cotovelo na mesa

**Caixa:** `[0, 50, 100, 28]` · **Luz:** íntima, um círculo de vela

**O que se vê.** Os dois de cotovelo na mesa, conversa baixa; ele fazendo rima com o nome dela, ela dizendo que é péssimo. Ao fundo, o Comam com a cabeça apoiada no braço, quase dormindo.

**Elenco:** `nelsowned`, `bronwyn`, `comam-obabaroy` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Bronwyn · em `[58, 20]`, apontando para `[62, 58]`
  > É HORRÍVEL. FAÇA OUTRA.

### 6.5 · plano médio com profundidade

**Caixa:** `[0, 78, 100, 22]` · **Luz:** a vela dela acesa, o pai na penumbra

**O que se vê.** Ela para de sorrir e pergunta, sem rodeio nenhum. Atrás dela, no fundo do quadro, Giles vira a cabeça na direção dos dois. Uma vez só.

**Elenco:** `bronwyn`, `nelsowned`, `giles-mao-de-prata` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Bronwyn · em `[42, 20]`, apontando para `[34, 58]`
  > QUANTO TEMPO UM TROVADOR FICA NUMA CIDADE ANTES DE SEGUIR VIAGEM?
- **narracao** · em `[86, 20]`
  > Só uma.

---

## Página 7 — O desafio

_Cena 5 · O desafio · 6 quadros_

### 7.1 · contra-plongée, de baixo do banco

**Caixa:** `[0, 0, 100, 24]` · **Luz:** lareira oeste atrás, ele quase em silhueta

**O que se vê.** O Negrum em cima do banco onde o trovador cantou, braço aberto, gritando a vitória para o salão inteiro. A taberna ri com ele.

**Elenco:** `negrum-carneiriums` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — Negrum · em `[64, 22]`, apontando para `[46, 34]`
  > NINGUÉM AQUI TEM FORÇA! NINGUÉM!

### 7.2 · plano médio, close no rosto gritando

**Caixa:** `[0, 24, 50, 22]` · **Luz:** dura, de baixo

**O que se vê.** Ele escolhendo mal as palavras, alto demais, no ânglico arranhado dele.

**Elenco:** `negrum-carneiriums`

- **grito** — Negrum · em `[60, 26]`, apontando para `[46, 44]`
  > HOMEM DA CASA SE ACHA BOM? VEM! VEM ATÉ A MORTE!

### 7.3 · três closes em fileira dentro do mesmo quadro

**Caixa:** `[50, 24, 50, 22]` · **Luz:** cada rosto um pouco mais escuro que o anterior

**O que se vê.** Três rostos em fileira deixando de rir, um depois do outro: um perto do banco, um na mesa comprida, um no fundo do salão.

**Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[50, 16]`
  > O riso morre por partes. Perto do banco. Na mesa comprida. No fundo.

### 7.4 · close extremo nas mãos

**Caixa:** `[0, 46, 50, 24]` · **Luz:** lanterna do balcão, luz de cima

**O que se vê.** As mãos de Hoel dobrando o pano de secar devagar, como quem tem todo o tempo do mundo, e deixando-o em cima da madeira do balcão.

**Elenco:** `hoel-meia-orelha`

_Sem balão._

### 7.5 · plano médio, seguindo o movimento

**Caixa:** `[50, 46, 50, 24]` · **Luz:** ele entrando na luz da lareira oeste

**O que se vê.** Hoel contorna o balcão sem pressa nenhuma e para a dois passos do banco, de frente para o salão.

**Elenco:** `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Hoel · em `[62, 22]`, apontando para `[48, 52]`
  > NA MINHA CASA NINGUÉM MORRE.

### 7.6 · contra-plongée desde o chão, o banco à direita

**Caixa:** `[0, 70, 100, 30]` · **Luz:** a lareira oeste forte de um lado, os dois meio pretos contra ela

**O que se vê.** Hoel arregaçando as mangas: antebraços de quem carrega barril há vinte anos. O Negrum olha de cima, do banco. A roda já se abre em volta dos dois.

**Elenco:** `hoel-meia-orelha`, `negrum-carneiriums` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Hoel · em `[46, 18]`, apontando para `[36, 52]`
  > MAS SE O FORASTEIRO QUER APRENDER ALGUMA COISA, EU ENSINO AGORA. DE GRAÇA.

---

## Página 8 — A aposta e a banca

_Cena 6 · A aposta e a banca · 6 quadros_

### 8.1 · plano geral, plongée média

**Caixa:** `[0, 0, 100, 24]` · **Luz:** lanternas altas, o chão de serragem à mostra

**O que se vê.** A roda se abre sozinha: bancos arrastados, canecos recolhidos, alguém tirando as moedas de cima da mesa. Ninguém está segurando ninguém.

**Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 16]`
  > Ninguém está segurando ninguém.

### 8.2 · plano médio

**Caixa:** `[0, 24, 50, 22]` · **Luz:** quente, ele suado

**O que se vê.** Donnwulf sentado num banco, o braço direito já entalado numa tala de madeira e amarrado ao peito por gente da casa, rindo e gritando a aposta dele.

**Elenco:** `donnwulf` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — Donnwulf · em `[62, 22]`, apontando para `[42, 58]`
  > APOSTO NO TABERNEIRO!

### 8.3 · plano médio, câmera baixa

**Caixa:** `[50, 24, 50, 22]` · **Luz:** lanterna acima dele, foco de palco

**O que se vê.** O Jah de pé em cima de um banco, a mão erguida com as moedas, gritando para a casa inteira ouvir.

**Elenco:** `jah-kagadu` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — Jah · em `[64, 22]`, apontando para `[46, 40]`
  > APOSTO CINQUENTA NO HOEL!

### 8.4 · close nas moedas, fundo desfocado

**Caixa:** `[0, 46, 50, 24]` · **Luz:** brilho metálico contra fundo escuro

**O que se vê.** As moedas caindo na madeira. Atrás, fora de foco, o rosto do Negrum virando na direção do grito.

**Elenco:** `negrum-carneiriums`

- **onomatopeia** · em `[62, 40]`, corpo 60
  > CLINC

### 8.5 · plano médio, de frente para a plateia

**Caixa:** `[50, 46, 50, 24]` · **Luz:** âmbar, plateia em meia-sombra

**O que se vê.** O Jah com meio corpo em cima do banco, chamando nome por nome, apontando para os fregueses, prometendo pagar em dobro.

**Elenco:** `jah-kagadu` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Jah · em `[58, 20]`, apontando para `[40, 54]`
  > PAGO EM DOBRO! ALGUÉM TEM CORAGEM DE DIZER O CONTRÁRIO COM DINHEIRO NA MÃO?

### 8.6 · plano médio baixo, quase à altura da mesa

**Caixa:** `[0, 70, 100, 30]` · **Luz:** lanterna baixa sobre as moedas

**O que se vê.** Um tropeiro de mão grande põe o dedo na mesa, em cima do bolo de moedas, e diz o que metade da casa estava pensando. Ao fundo, na roda, alguém já está contando até três.

**Elenco:** `jah-kagadu` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — tropeiro · em `[40, 18]`, apontando para `[36, 52]`
  > O DINHEIRO FICA AQUI. NA MADEIRA. À VISTA DE TODO MUNDO.
- **narracao** · em `[82, 22]`
  > Na roda, alguém já conta até três.

---

## Página 9 — O corredor dos fundos

_Cena 7 · O corredor dos fundos · 5 quadros_

### 9.1 · plano médio, o corredor em perspectiva

**Caixa:** `[0, 0, 100, 26]` · **Luz:** uma lamparina só, o resto em penumbra azulada

**O que se vê.** O corredor dos fundos: parede de tábua, uma lamparina pendurada, a porta do estábulo no fim, cheiro de palha, chuva fina entrando pela fresta. Os dois chegando.

**Elenco:** `nelsowned`, `bronwyn`

- **narracao** · em `[70, 16]`
  > Foi ela quem escolheu o lugar. Nem a rua, nem o quarto de cima.

### 9.2 · plano médio, os dois no degrau

**Caixa:** `[0, 26, 50, 24]` · **Luz:** lamparina lateral, sombras compridas

**O que se vê.** Bronwyn senta no degrau da porta do estábulo e fala sem parar; ele senta ao lado, escutando, pela primeira vez calado.

**Elenco:** `bronwyn`, `nelsowned`

- **fala** — Bronwyn · em `[56, 20]`, apontando para `[40, 62]`
  > MINHA MÃE MORREU QUANDO EU TINHA NOVE ANOS.

### 9.3 · close na nuca e na mão

**Caixa:** `[50, 26, 50, 24]` · **Luz:** o ouro pegando a única luz do corredor

**O que se vê.** A mão dela subindo ao pescoço e tocando o colar de ouro por baixo da gola: trabalho antigo, pesado, bom demais para a filha de um mercador de lã usar num dia comum.

**Elenco:** `bronwyn`

- **fala** — Bronwyn · em `[66, 22]`, apontando para `[48, 54]`
  > GUARDO O COLAR DELA.

### 9.4 · plano médio largo, os dois sentados

**Caixa:** `[0, 50, 100, 26]` · **Luz:** quente e pequena, o corredor todo escuro em volta

**O que se vê.** Os dois no degrau. Ela fala da égua que ela mesma domou e que o pai vendeu, e do homem de Carrick de quem ela sabe o nome, a idade e mais nada.

**Elenco:** `bronwyn`, `nelsowned`

- **fala** — Bronwyn · em `[58, 18]`, apontando para `[40, 62]`
  > DO HOMEM DE CARRICK EU SEI O NOME E A IDADE. MAIS NADA.

### 9.5 · close baixo, ela olhando as próprias mãos

**Caixa:** `[0, 76, 100, 24]` · **Luz:** a lamparina tremendo

**O que se vê.** Ela para, olha para as próprias mãos e pergunta. Ao fundo, fora de foco, a porta do estábulo, fechada. E lá dentro, longe, o salão inteiro grita ao mesmo tempo.

**Elenco:** `bronwyn`

- **fala** — Bronwyn · em `[46, 22]`, apontando para `[36, 58]`
  > É VERDADE QUE TROVADOR CONHECE AS ESTRADAS TODAS?
- **off** · em `[84, 20]`
  > UUUUH!

---

## Página 10 — A briga

_Cena 8 · A briga · 6 quadros_

### 10.1 · plano geral da roda, plongée

**Caixa:** `[0, 0, 100, 22]` · **Luz:** lanternas altas, sombras curtas

**O que se vê.** Os dois no meio da roda, a casa em volta em duas fileiras; Hoel de mangas arregaçadas e punhos baixos, o Negrum com o peito nu e o queixo erguido.

**Elenco:** `hoel-meia-orelha`, `negrum-carneiriums` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

_Sem balão._

### 10.2 · close, o punho passando

**Caixa:** `[0, 22, 50, 20]` · **Luz:** rasante, muito contraste

**O que se vê.** O soco do Negrum passando a um palmo da cara do taberneiro, que jogou a cabeça para trás no último instante.

**Elenco:** `negrum-carneiriums`, `hoel-meia-orelha`

- **onomatopeia** · em `[60, 26]`, corpo 62
  > FVUM

### 10.3 · plano médio

**Caixa:** `[50, 22, 50, 20]` · **Luz:** lareira oeste lateral

**O que se vê.** Hoel revida com um direto de velho brigão; o Negrum apara com o antebraço.

**Elenco:** `hoel-meia-orelha`, `negrum-carneiriums`

- **onomatopeia** · em `[50, 26]`, corpo 58
  > TAP!

### 10.4 · plano médio, os dois travados

**Caixa:** `[0, 42, 50, 22]` · **Luz:** quente, poeira de serragem no ar

**O que se vê.** O encontrão: o Negrum joga o ombro no peito do taberneiro; os dois ficam travados, sapateando na serragem. Nenhum cai.

**Elenco:** `negrum-carneiriums`, `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[78, 18]`
  > Ninguém cai.

### 10.5 · close

**Caixa:** `[50, 42, 50, 22]` · **Luz:** dura, o suor brilhando

**O que se vê.** O punho do velho entrando limpo no tronco do gigante — e o gigante quase sem sentir. A casa berra mesmo assim.

**Elenco:** `hoel-meia-orelha`, `negrum-carneiriums`

- **off** · em `[24, 22]`
  > UUUUH!

### 10.6 · contra-plongée forte, quadro grande

**Caixa:** `[0, 64, 100, 36]` · **Luz:** clarão da lareira oeste por trás, os dois quase em silhueta

**O que se vê.** O punho do Negrum subindo por dentro, curto, em cheio na cara do taberneiro. A cabeça de Hoel vai para trás; os joelhos somem debaixo do corpo.

**Elenco:** `negrum-carneiriums`, `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[62, 34]`, corpo 140
  > CROC!
- **narracao** · em `[18, 14]`
  > A briga acabou aqui.

---

## Página 11 — O assassinato

_Cena 9 · O assassinato · 6 quadros_

### 11.1 · plano geral rasante, câmera quase no chão

**Caixa:** `[0, 0, 100, 24]` · **Luz:** lanternas altas, o chão em sombra

**O que se vê.** Hoel desaba de lado na serragem, entre um banco virado e a pilha de moedas da banca, e não se mexe. Por dois segundos ninguém grita.

**Elenco:** `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 16]`
  > Por dois segundos ninguém grita. É a taberna dele.

### 11.2 · plano médio

**Caixa:** `[0, 24, 50, 22]` · **Luz:** quente, mas o rosto duro

**O que se vê.** Donnwulf é o primeiro a se levantar, o braço entalado colado ao peito, começando a dizer alguma coisa que ninguém escuta.

**Elenco:** `donnwulf` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Donnwulf · em `[69, 18]`, apontando para `[46, 48]`
  > EI... EI, GRANDÃO, ACABOU—

### 11.3 · plano médio de costas

**Caixa:** `[50, 24, 50, 22]` · **Luz:** ele entrando na sombra

**O que se vê.** O Negrum andando na direção do corpo caído, visto de costas, os punhos ainda fechados, os ombros subindo e descendo.

**Elenco:** `negrum-carneiriums`, `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[70, 18]`
  > E não está com cara de quem vai ajudar a levantar.

### 11.4 · plano médio; o golpe cortado pela borda do quadro

**Caixa:** `[0, 46, 100, 26]` · **Luz:** o chão claro, os rostos em meia-sombra

**O que se vê.** O Negrum ajoelhado ao lado do corpo. O golpe está fora de campo, cortado pela borda do quadro — o que se vê é a roda de gente parada, e os tropeiros a três passos que não chegam.

**Elenco:** `negrum-carneiriums` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[30, 22]`, corpo 120
  > TUM

### 11.5 · três closes no mesmo quadro

**Caixa:** `[0, 72, 50, 28]` · **Luz:** cada rosto com sua própria luz baixa

**O que se vê.** Três rostos: Osric levantando devagar, a mão indo para o cinto onde não há espada e parando no meio do caminho; uma mulher levando a mão à boca; o Jah parado, sem ar.

**Elenco:** `osric-de-bannock`, `jah-kagadu`

- **onomatopeia** · em `[50, 22]`, corpo 84
  > TUM
- **off** · em `[50, 78]`
  > HOEL!

### 11.6 · close, o fundo desfocado

**Caixa:** `[50, 72, 50, 28]` · **Luz:** uma vela perto dele, o fundo sumindo no escuro

**O que se vê.** O Irmão Kaelric de cabeça baixa, o rosário enrolado nas mãos enormes, rezando. Atrás dele, desfocada, a casa emudecendo. Ele não está vendo.

**Elenco:** `irmao-kaelric` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[76, 24]`, corpo 58
  > TUM

---

## Página 12 — Quarenta pessoas viram

_Cena 9 · O assassinato · 5 quadros_

### 12.1 · plano médio baixo, câmera no nível do corpo

**Caixa:** `[0, 0, 100, 30]` · **Luz:** fria pela primeira vez na noite; a lareira oeste ficou para trás

**O que se vê.** O Negrum enfim se levanta. As mãos dele. O corpo no assoalho, imóvel, e a serragem em volta.

**Elenco:** `negrum-carneiriums`, `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[80, 26]`, corpo 34
  > tum.

### 12.2 · plano geral, plongée

**Caixa:** `[0, 30, 50, 22]` · **Luz:** lanternas altas, todos os rostos iguais de pálidos

**O que se vê.** Quarenta pessoas em silêncio, de pé, olhando. Ninguém grita. Ninguém corre. Ninguém sai.

**Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[40, 16]`
  > Ninguém grita. Ninguém corre.

### 12.3 · close frontal

**Caixa:** `[50, 30, 50, 22]` · **Luz:** chapada, sem sombra para se esconder

**O que se vê.** O rosto do Negrum: sem triunfo nenhum. Ele está entendendo onde está e o que acabou de fazer.

**Elenco:** `negrum-carneiriums`

_Sem balão._

### 12.4 · plongée alta, quase do teto

**Caixa:** `[0, 52, 100, 24]` · **Luz:** de cima, o corpo no centro do foco

**O que se vê.** O salão visto de cima: o corpo no meio do assoalho, a roda aberta em volta, as moedas da banca espalhadas ao lado da cabeça do homem — e ninguém olhando para elas.

**Elenco:** `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 16]`
  > O dono d'A Âncora Quebrada está morto no assoalho da própria casa. Quarenta pessoas viram.

### 12.5 · plano geral de fora, na chuva

**Caixa:** `[0, 76, 100, 24]` · **Luz:** azul de chuva, nenhuma luz quente

**O que se vê.** Os currais, lá fora: os cães calados. Todos. Orelhas em pé, focinhos ainda virados para o mesmo lado, e nenhum som.

- **narracao** · em `[66, 20]`
  > Os cães pararam de uivar. Todos. Ao mesmo tempo.

---

## Página 13 — O colar

_Cena 10 · O colar · 6 quadros_

### 13.1 · plano médio, corredor

**Caixa:** `[0, 0, 100, 24]` · **Luz:** lamparina única, muito quente contra o azul da fresta

**O que se vê.** No corredor dos fundos o barulho do salão chega abafado. Os dois de pé, muito perto um do outro, entre a parede de tábua e a porta do estábulo.

**Elenco:** `nelsowned`, `bronwyn`

- **narracao** · em `[24, 16]`
  > Ali atrás, o barulho do salão chega abafado.

### 13.2 · close

**Caixa:** `[0, 24, 50, 22]` · **Luz:** metade do rosto na luz da lamparina

**O que se vê.** Bronwyn levanta a cabeça e olha para o corredor: o coro do salão mudou de som.

**Elenco:** `bronwyn`

- **off** · em `[76, 22]`
  > UUUUH!

### 13.3 · close na parede e na lamparina

**Caixa:** `[50, 24, 50, 22]` · **Luz:** a chama tremendo, sombras balançando

**O que se vê.** Pancada do outro lado da tábua, madeira arrastando, mais grito. A lamparina do corredor treme no gancho.

- **onomatopeia** · em `[30, 62]`, corpo 76
  > TRUM!

### 13.4 · plano médio, os dois já de pé

**Caixa:** `[0, 46, 100, 24]` · **Luz:** a lamparina firme outra vez, e o corredor muito quieto

**O que se vê.** E então acaba. Não devagar: de uma vez. Ele já está de pé; ela também, com a mão no braço dele.

**Elenco:** `nelsowned`, `bronwyn`

- **narracao** · em `[78, 18]`
  > E então acaba. Não devagar: de uma vez.

### 13.5 · close dos dois, mãos no centro do quadro

**Caixa:** `[0, 70, 60, 30]` · **Luz:** o ouro como única coisa clara do quadro

**O que se vê.** Ela leva a mão à nuca, desafivela o colar e põe no peito dele, fechando os dedos dele por cima. É ouro pesado, trabalho antigo.

**Elenco:** `bronwyn`, `nelsowned`

- **fala** — Bronwyn · em `[58, 18]`, apontando para `[38, 56]`
  > ERA DA MINHA MÃE. FICA COM ELE. NÃO É PAGAMENTO DE NADA — EU SÓ QUERO QUE VOCÊ TENHA.

### 13.6 · plano fechado no corredor vazio

**Caixa:** `[60, 70, 40, 30]` · **Luz:** contraluz: o corredor preto e a porta clara

**O que se vê.** O corredor vazio na direção do salão, a luz da porta lá no fim — e lá dentro alguém finalmente grita.

- **grito** · em `[50, 30]`
  > AAAAH!

---

## Página 14 — O guarda

_Cena 11 · O guarda · 6 quadros_

### 14.1 · plano médio, balcão de perfil

**Caixa:** `[0, 0, 100, 24]` · **Luz:** lanterna do balcão; o resto do salão em sombra e silêncio

**O que se vê.** O Kaelric de pé ao lado do banquinho de Osric, falando baixo; o guarda sentado, sem interromper, olhando o caneco.

**Elenco:** `irmao-kaelric`, `osric-de-bannock` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Kaelric · em `[54, 18]`, apontando para `[36, 40]`
  > O TABERNEIRO CHAMOU PRA BRIGA. MEU COMPANHEIRO ACEITOU, POR HONRA DE GUERREIRO.

### 14.2 · plano médio

**Caixa:** `[0, 24, 50, 22]` · **Luz:** quente de um lado só

**O que se vê.** O templário oferecendo a Ordem, a mão no peito, sobre a cruz vermelha.

**Elenco:** `irmao-kaelric`

- **fala** — Kaelric · em `[64, 22]`, apontando para `[42, 40]`
  > A ORDEM SE PÕE À DISPOSIÇÃO DO LORDE WILLIAM. NÃO FICAREMOS NO CAMINHO DELE.

### 14.3 · close, o olhar percorrendo

**Caixa:** `[50, 24, 50, 22]` · **Luz:** meia-luz, os olhos na sombra

**O que se vê.** Osric olha para o hábito no peito do templário, e depois para o corpo no assoalho. Não interrompeu uma vez sequer.

**Elenco:** `osric-de-bannock`

- **narracao** · em `[72, 20]`
  > Ele não interrompe uma vez sequer. É por isso que dói mais.

### 14.4 · close frontal de Osric

**Caixa:** `[0, 46, 100, 24]` · **Luz:** frontal e dura

**O que se vê.** Osric de frente, a voz baixa e sem raiva nenhuma — o que é pior.

**Elenco:** `osric-de-bannock`

- **fala** — Osric · em `[66, 20]`, apontando para `[44, 56]`
  > O TABERNEIRO CHAMOU PRA BRIGA, É VERDADE. E A BRIGA ACABOU QUANDO ELE CAIU.

### 14.5 · plano médio

**Caixa:** `[0, 70, 50, 30]` · **Luz:** ele saindo da luz do balcão

**O que se vê.** Osric empurra o caneco para o meio do balcão sem beber e pega a capa do gancho.

**Elenco:** `osric-de-bannock`, `irmao-kaelric` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Osric · em `[56, 20]`, apontando para `[42, 52]`
  > O SENHOR É HOMEM DE DEUS, IRMÃO. SABE O NOME DAQUILO MELHOR DO QUE EU.

### 14.6 · plano fechado na porta da frente

**Caixa:** `[50, 70, 50, 30]` · **Luz:** a fresta preta contra a madeira quente

**O que se vê.** A porta da frente batendo e ficando entreaberta. A chuva lá fora, a fresta escura, e ninguém a fecha.

**Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **off** — Osric · em `[50, 20]`
  > DIGA AO SEU COMPANHEIRO QUE EU VOU AO CASTELO AGORA.
- **narracao** · em `[78, 78]`
  > Ninguém a fechou.

---

## Página 15 — A porta

_Cena 12 · A porta · 5 quadros_

### 15.1 · plano geral do salão, silêncio

**Caixa:** `[0, 0, 100, 24]` · **Luz:** lanternas baixas, a lareira oeste já morrendo

**O que se vê.** O salão ainda em silêncio, o corpo no chão, as pessoas sem saber o que fazer com as mãos. E de fora, longe, na direção do mercado, muitos gritos ao mesmo tempo.

**Elenco:** `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 16]`
  > Gritos longe, na direção do mercado. Não é grito de briga.
- **off** · em `[80, 18]`
  > AAAAAH!

### 15.2 · close na porta

**Caixa:** `[0, 24, 50, 22]` · **Luz:** o preto da rua invadindo o quadro

**O que se vê.** A porta entreaberta desde que o guarda saiu se abre de vez, empurrada pelo ombro de alguém.

**Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[72, 30]`, corpo 96
  > BRAM!

### 15.3 · plano médio em contraluz

**Caixa:** `[50, 24, 50, 22]` · **Luz:** contraluz total: quatro formas pretas

**O que se vê.** Quatro silhuetas na soleira, a chuva atrás delas, entrando juntas e depressa, sem tropeçar em nada.

**Elenco:** `morto-vivo-tropeiro`, `morto-vivo-apostador`, `morto-vivo-vulto`, `wat` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[42, 20]`
  > Entra um cheiro que não é de chuva nem de estrume. Doce, parado, errado.

### 15.4 · plano médio, dois na luz e um quarto na sombra

**Caixa:** `[0, 46, 100, 26]` · **Luz:** eles saindo do escuro para a luz das lanternas

**O que se vê.** O da frente é um tropeiro que bebia ali até uma hora atrás — ainda tem o caneco preso na mão. Atrás dele vem um dos apostadores do círculo do braço-de-ferro. São esses dois que a luz da lanterna pega. O quarto fica para trás, na escuridão da soleira, sem rosto e sem nome.

**Elenco:** `morto-vivo-tropeiro`, `morto-vivo-apostador`, `morto-vivo-vulto` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[61, 13]`
  > Não dizem palavra nenhuma. É o silêncio deles que faz a casa recuar um passo.

### 15.5 · close baixo, à altura dos olhos de uma criança

**Caixa:** `[0, 72, 100, 28]` · **Luz:** a luz das lanternas nele, e tudo em volta apagando

**O que se vê.** Wat, o menino do estábulo, o mesmo que saiu correndo para buscar o barbeiro. A camisa dele está aberta do ombro à cintura. Ele olha para o grupo com uma cara que ainda é a cara dele, e vem andando.

**Elenco:** `wat` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[78, 18]`
  > E o terceiro é pequeno.

---

## Página 16 — A paralisia

_Cena 12 · A porta · 6 quadros_

### 16.1 · plano geral, plongée

**Caixa:** `[0, 0, 100, 22]` · **Luz:** lanternas, mas a cor já mais fria que nas páginas anteriores

**O que se vê.** O salão inteiro parado. Os quatro avançam pelo meio das mesas, e cada um foi escolhendo alguém: não se defendem, não desviam, não param.

**Elenco:** `morto-vivo-tropeiro`, `morto-vivo-apostador`, `morto-vivo-vulto`, `wat` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 16]`
  > Nenhum se defende. Nenhum desvia. Cada um escolheu alguém neste salão.

### 16.2 · close extremo nos olhos

**Caixa:** `[0, 22, 50, 22]` · **Luz:** dura e fria, sem sombra macia

**O que se vê.** O Jah: os olhos abertos, o corpo que não obedece. Ele vê tudo e não consegue mexer nada.

**Elenco:** `jah-kagadu`

- **sussurro** — Jah · em `[72, 24]`, apontando para `[50, 58]`
  > QUE PORRA... É ESSA?...

### 16.3 · plano médio, contra-plongée

**Caixa:** `[50, 22, 50, 22]` · **Luz:** a luz vindo de trás dos mortos, nele por reflexo

**O que se vê.** O Irmão Kaelric dá um passo à frente com o escudo grande erguido, estupefato, a boca aberta.

**Elenco:** `irmao-kaelric` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — Kaelric · em `[70, 22]`, apontando para `[46, 40]`
  > QUE DEUS NOS AJUDE!

### 16.4 · close nas costas e na mão

**Caixa:** `[0, 44, 50, 22]` · **Luz:** rasante, os músculos das costas em relevo

**O que se vê.** A mão do Negrum subindo às costas, para o punho do montante. Ele não está paralisado.

**Elenco:** `negrum-carneiriums`

_Sem balão._

### 16.5 · plano médio, da quina do corredor

**Caixa:** `[50, 44, 50, 22]` · **Luz:** ele na sombra do corredor, o salão claro à frente

**O que se vê.** O NelsOwned voltando ao salão pela boca do corredor dos fundos, o machado grande ainda nas costas, e parando na quina da parede ao ver o que está acontecendo.

**Elenco:** `nelsowned` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

_Sem balão._

### 16.6 · plano médio, cômico e cruel

**Caixa:** `[0, 66, 100, 34]` · **Luz:** quente em cima dele, fria atrás

**O que se vê.** O Comam de cara na mesa, roncando, um caneco virado ao lado e uma poça de cerveja molhando a manga dele. Ao fundo, desfocados, os mortos andando entre as mesas.

**Elenco:** `comam-obabaroy` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[62, 26]`, corpo 64
  > ZZZZZZ

---

## Página 17 — A melê (1)

_Cena 13 · A melê · 6 quadros_

### 17.1 · plano médio, movimento diagonal

**Caixa:** `[0, 0, 100, 24]` · **Luz:** as brasas do braseiro sudeste, a lâmina pegando o brilho

**O que se vê.** O Negrum saca o montante das costas no mesmo movimento em que avança — a lâmina saindo por cima do ombro.

**Elenco:** `negrum-carneiriums` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[72, 26]`, corpo 72
  > SHIIING

### 17.2 · plano médio baixo

**Caixa:** `[0, 24, 55, 24]` · **Luz:** dura, a lâmina clara no escuro

**O que se vê.** O corte na perna do morto que vinha por cima dele: a perna sai.

**Elenco:** `negrum-carneiriums`, `morto-vivo-vulto`

- **onomatopeia** · em `[56, 30]`, corpo 100
  > TCHAC!

### 17.3 · close no chão

**Caixa:** `[55, 24, 45, 24]` · **Luz:** chão claro, o resto preto

**O que se vê.** O morto caído sem a perna — e continuando a vir, se arrastando pelo assoalho na direção das botas do Negrum, sem pressa e sem parar.

**Elenco:** `morto-vivo-vulto`

- **narracao** · em `[70, 22]`
  > Ele cai. E continua vindo.

### 17.4 · plano médio, contra-plongée

**Caixa:** `[0, 48, 50, 24]` · **Luz:** fogo do braseiro sudeste à direita, já visível

**O que se vê.** O Irmão Kaelric erguendo o escudo grande com as duas mãos e gritando, o corpo inteiro atrás dele.

**Elenco:** `irmao-kaelric` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — Kaelric · em `[70, 22]`, apontando para `[46, 40]`
  > PAI, DÊ-ME FORÇAS!

### 17.5 · plano médio lateral

**Caixa:** `[50, 48, 50, 24]` · **Luz:** brasas laranja do braseiro sudeste

**O que se vê.** O encontrão: o escudo no peito do morto, empurrando-o para trás, na direção do braseiro aceso do canto sudeste.

> ⚠️ **GATILHO DO CANTO SUDESTE — leia antes de gerar este quadro. O cenario-salao.png NÃO tem o braseiro de ferro nem a segunda lareira: o gerador trocou o braseiro por um caldeirão duas vezes, com prompts diferentes, e a lareira menor não saiu. Este é o PRIMEIRO quadro do volume que se passa naquele canto. Se ele sair errado — sem braseiro, ou com um caldeirão no lugar —, a decisão já tomada é gerar UMA referência de detalhe só do canto sudeste (lareira menor + braseiro de brasas vivas + a porta ao lado) e usá-la como `cenario` nos ~18 quadros das páginas 17, 18 e 21. 1 chamada. Não regerar o salão inteiro: ele acertou dez outros itens.**

**Elenco:** `irmao-kaelric`, `morto-vivo-apostador` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[52, 28]`, corpo 90
  > TUMP!

### 17.6 · plano médio, o braseiro no centro

**Caixa:** `[0, 72, 100, 28]` · **Luz:** a primeira luz de incêndio do volume

**O que se vê.** O morto caído atravessado em cima das brasas, a roupa seca pegando fogo. Não grita. Não se debate. Não sai de lá.

**Elenco:** `morto-vivo-apostador` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[24, 20]`
  > Ele não grita. E não sai de lá.

---

## Página 18 — A melê (2)

_Cena 13 · A melê · 6 quadros_

### 18.1 · plano médio, o chute em diagonal

**Caixa:** `[0, 0, 50, 24]` · **Luz:** lareira sudeste atrás, silhuetas quentes

**O que se vê.** O Negrum gira e crava o pé no peito de outro morto.

**Elenco:** `negrum-carneiriums`, `morto-vivo-tropeiro`

- **onomatopeia** · em `[56, 26]`, corpo 92
  > TUM!

### 18.2 · plano geral baixo

**Caixa:** `[50, 0, 50, 24]` · **Luz:** fogo da lareira sudeste bem atrás do impacto

**O que se vê.** O corpo voando para trás e batendo na alvenaria da lareira, que o para no meio do caminho.

**Elenco:** `morto-vivo-tropeiro` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[74, 30]`, corpo 100
  > CRAC!

### 18.3 · plongée, de cima do golpe

**Caixa:** `[0, 24, 50, 24]` · **Luz:** fogo da lareira sudeste por baixo, o golpe em sombra

**O que se vê.** A maça do Kaelric descendo no peito afundado do morto caído entre a lareira e o chão.

**Elenco:** `irmao-kaelric`, `morto-vivo-tropeiro` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[56, 28]`, corpo 94
  > TROC!

### 18.4 · close, o corte horizontal

**Caixa:** `[50, 24, 50, 24]` · **Luz:** lâmina clara, fundo preto

**O que se vê.** O montante do Negrum decepando o primeiro morto de vez: a cabeça sai.

**Elenco:** `negrum-carneiriums`

- **onomatopeia** · em `[52, 26]`, corpo 110
  > SHRAC!

### 18.5 · plano geral do canto sudeste

**Caixa:** `[0, 48, 100, 26]` · **Luz:** laranja de incêndio começando a dominar o quadro

**O que se vê.** O canto sudeste: três corpos parados no chão, um deles queimando em cima do braseiro. O Kaelric e o Negrum ofegando no meio da fumaça, sem baixar as armas.

**Elenco:** `irmao-kaelric`, `negrum-carneiriums` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 18]`
  > Não param quando feridos. Param quando são desmontados.

### 18.6 · close extremo, no outro canto do salão

**Caixa:** `[0, 74, 100, 26]` · **Luz:** fria, azulada, longe dos dois fogos

**O que se vê.** Longe da luta, no meio do salão: uma mão no assoalho fechando devagar entre as moedas da banca.

**Elenco:** `hoel-meia-orelha`

_Sem balão._

---

## Página 19 — Hoel se levanta

_Cena 14 · Hoel se levanta · 6 quadros_

### 19.1 · plano subjetivo, do chão, deitado

**Caixa:** `[0, 0, 100, 30]` · **Luz:** baixa e deitada, sombras compridas pelo assoalho

**O que se vê.** O ponto de vista do Jah, caído e travado: o assoalho de serragem rente aos olhos, os pés das pessoas ao longe — e o corpo do taberneiro a um passo dele.

**Elenco:** `jah-kagadu`, `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[24, 16]`
  > Jah, você continua sem conseguir se mexer. É por isso que você vê tudo.

### 19.2 · close extremo na mão

**Caixa:** `[0, 30, 50, 22]` · **Luz:** rasante, quase sem cor

**O que se vê.** A mão do taberneiro fecha. Não é o espasmo de quem ainda está morrendo: é uma mão fechando devagar, com vontade, apalpando o assoalho até achar apoio entre as moedas.

**Elenco:** `hoel-meia-orelha`

- **narracao** · em `[72, 22]`
  > Não é o espasmo de quem ainda está morrendo.

### 19.3 · close no peito

**Caixa:** `[50, 30, 50, 22]` · **Luz:** uma faixa de luz atravessando o peito

**O que se vê.** O peito do taberneiro enchendo sozinho, o avental subindo.

**Elenco:** `hoel-meia-orelha`

- **narracao** · em `[50, 22]`
  > É o ar entrando por conta própria num peito que ninguém está mandando encher.

### 19.4 · close extremo nos olhos

**Caixa:** `[0, 52, 50, 24]` · **Luz:** dura, o branco dos olhos como único claro

**O que se vê.** Os olhos de Hoel, abertos. Estavam fechados até agora.

**Elenco:** `hoel-meia-orelha`

- **narracao** · em `[74, 15]`
  > Estavam fechados até agora.

### 19.5 · plano médio, o corpo em esforço

**Caixa:** `[50, 52, 50, 24]` · **Luz:** baixa, sombra comprida do corpo

**O que se vê.** O corpo tentando lembrar como se senta: o ombro empurrando a madeira, o quadril girando meio dedo, o que sobrou do rosto arrastando pela serragem.

**Elenco:** `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[56, 20]`
  > De novo. E de novo. Sem pressa nenhuma, como quem tem a noite toda.

### 19.6 · plano médio baixo, os dois no mesmo quadro

**Caixa:** `[0, 76, 100, 24]` · **Luz:** fria à esquerda, o incêndio laranja bem ao longe

**O que se vê.** O rosto estragado do taberneiro virando na direção dos pés do Jah — e o Jah, caído a um passo, com os olhos abertos e os braços que não respondem.

**Elenco:** `hoel-meia-orelha`, `jah-kagadu` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 18]`
  > Vinte anos de estrada. Meia orelha. O homem que servia a sua cerveja sem você pedir.
- **narracao** · em `[80, 20]`
  > E os seus braços não respondem.

---

## Página 20 — O machado

_Cena 15 · O machado · 6 quadros_

### 20.1 · plano médio, contra-plongée

**Caixa:** `[0, 0, 100, 24]` · **Luz:** o incêndio ao fundo dando a única cor quente

**O que se vê.** Hoel de pé no meio do salão, gritando — e o som que sai dele não é voz de gente. Do outro lado, o NelsOwned chegando pelo corredor.

**Elenco:** `hoel-meia-orelha`, `nelsowned` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **eletronico** — Hoel · em `[58, 22]`, apontando para `[40, 44]`
  > AAAAAAAAH

### 20.2 · plano médio lateral

**Caixa:** `[0, 24, 50, 22]` · **Luz:** dura, poeira no ar

**O que se vê.** O chute do taberneiro morto acertando o peito do anão, que recua dois passos escorregando na serragem.

**Elenco:** `hoel-meia-orelha`, `nelsowned`

- **onomatopeia** · em `[52, 28]`, corpo 88
  > TUMP!

### 20.3 · close

**Caixa:** `[50, 24, 50, 22]` · **Luz:** o incêndio à direita, o metal alaranjado

**O que se vê.** O NelsOwned firma os pés e puxa o machado grande das costas.

**Elenco:** `nelsowned`

- **onomatopeia** · em `[74, 26]`, corpo 64
  > SHING

### 20.4 · plano médio, os dois frente a frente

**Caixa:** `[0, 46, 100, 26]` · **Luz:** incêndio atrás, os dois em contraluz

**O que se vê.** O trovador com o machado erguido, gritando para o homem à frente dele — que ele viu servindo cerveja duas horas atrás.

**Elenco:** `nelsowned`, `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — NelsOwned · em `[46, 18]`, apontando para `[32, 62]`
  > HOEL! DIGA ALGO QUE NÃO ME FAÇA ACHAR QUE É UM ZUMBI, SENÃO ARRANCO SUA CABEÇA!

### 20.5 · close frontal

**Caixa:** `[0, 72, 45, 28]` · **Luz:** frontal e chapada, sem sombra que ajude

**O que se vê.** O taberneiro. Sem resposta. Sem cara nenhuma: a boca aberta, os olhos sem foco, serragem na barba.

**Elenco:** `hoel-meia-orelha`

_Sem balão._

### 20.6 · plano médio, o golpe descendo

**Caixa:** `[45, 72, 55, 28]` · **Luz:** clarão do incêndio, sombras violentas

**O que se vê.** O machado desce. A cabeça sai. O corpo cai em cima da própria serragem.

**Elenco:** `nelsowned`, `hoel-meia-orelha` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **onomatopeia** · em `[52, 24]`, corpo 120
  > SHRAC!
- **narracao** · em `[78, 78]`
  > E o anão não sabe que este homem já tinha sido morto uma vez esta noite.

---

## Página 21 — O fogo

_Cena 16 · O fogo · 6 quadros_

### 21.1 · plano geral, plongée

**Caixa:** `[0, 0, 100, 24]` · **Luz:** fumaça cinza no alto, laranja no canto sudeste

**O que se vê.** Nenhum morto de pé. Cinco corpos no assoalho, o dinheiro da banca espalhado, a porta da frente aberta para os gritos do mercado.

**Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 16]`
  > Nenhum morto de pé. Cinco corpos no assoalho.

### 21.2 · close no braseiro

**Caixa:** `[0, 24, 50, 22]` · **Luz:** laranja violento, tudo em volta preto

**O que se vê.** O corpo em cima do braseiro pegando fogo de vez, e do corpo o fogo passando para a serragem do assoalho.

- **onomatopeia** · em `[74, 30]`, corpo 86
  > FUUUM

### 21.3 · plano médio, o fogo correndo

**Caixa:** `[50, 24, 50, 22]` · **Luz:** incêndio como fonte principal

**O que se vê.** As chamas correndo pelo assoalho: serragem, bancos virados, mesas de madeira seca. Combustível por todo lado.

**Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 20]`
  > Serragem, bancos virados, madeira seca. Combustível por todo lado.

### 21.4 · plano médio, ele agachado

**Caixa:** `[0, 46, 50, 24]` · **Luz:** o incêndio à direita, fumaça cinza em cima

**O que se vê.** O Irmão Kaelric abaixando-se para ficar debaixo da fumaça, o escudo nas costas, chamando o grupo.

**Elenco:** `irmao-kaelric` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **fala** — Kaelric · em `[66, 22]`, apontando para `[44, 52]`
  > ESTE LUGAR VIROU UM VERDADEIRO INFERNO! VAMOS SAIR ANTES QUE SE ALASTRE!

### 21.5 · plano médio

**Caixa:** `[50, 46, 50, 24]` · **Luz:** o incêndio atrás dos dois

**O que se vê.** O Jah sacudindo o Comam pelos ombros e gritando na orelha dele.

**Elenco:** `jah-kagadu`, `comam-obabaroy` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **grito** — Jah · em `[52, 20]`, apontando para `[36, 54]`
  > ACORDA, SEU BÊBADO MALDITO! TÁ PEGANDO FOGO!

### 21.6 · close, o rosto amassado

**Caixa:** `[0, 70, 100, 30]` · **Luz:** laranja no rosto dele, o incêndio refletido

**O que se vê.** O Comam abrindo o olho bom: a cara amassada da mesa, a marca da madeira no rosto, o tapa-olho torto — e o incêndio refletido no olho dele.

**Elenco:** `comam-obabaroy`

- **narracao** · em `[78, 20]`
  > Ele dormiu o braço-de-ferro, o furto, o assassinato e a luta inteira.

---

## Página 22 — A porta dos fundos

_Cena 17 · A porta dos fundos · 6 quadros_

### 22.1 · plano geral, travessia da esquerda para a direita

**Caixa:** `[0, 0, 100, 24]` · **Luz:** incêndio atrás, o corredor escuro à frente

**O que se vê.** O grupo atravessando o salão pela fumaça, encurvado, na direção do corredor dos fundos. Atrás deles, a casa em chamas.

**Elenco:** `irmao-kaelric`, `jah-kagadu`, `negrum-carneiriums`, `nelsowned`, `comam-obabaroy` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[26, 16]`
  > A casa que os hospedava está queimando, e não há mais quem responda por ela.

### 22.2 · plano médio baixo

**Caixa:** `[0, 24, 50, 22]` · **Luz:** o incêndio lateral, as moedas brilhando

**O que se vê.** O Jah abaixado na fumaça, juntando do assoalho as moedas da banca — as que eram dos fregueses — e enfiando no bolso.

**Elenco:** `jah-kagadu` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[74, 20]`
  > O dinheiro era dos fregueses.

### 22.3 · plano médio

**Caixa:** `[50, 24, 50, 22]` · **Luz:** fumaça densa, tudo cinza e laranja

**O que se vê.** O Negrum levando o Comam, que mal se aguenta em pé, o braço dele por cima do próprio ombro.

**Elenco:** `negrum-carneiriums`, `comam-obabaroy` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

_Sem balão._

### 22.4 · close, ele parando

**Caixa:** `[0, 46, 50, 24]` · **Luz:** fumaça entre ele e tudo o mais

**O que se vê.** O NelsOwned para um instante e procura um rosto no salão cheio de fumaça e de gente saindo.

**Elenco:** `nelsowned` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

_Sem balão._

### 22.5 · plano médio, do outro lado do salão

**Caixa:** `[50, 46, 50, 24]` · **Luz:** a chuva azul da rua contra o incêndio

**O que se vê.** Do outro lado do salão, na porta da frente: Giles arrastando a filha para fora pelo pulso. Bronwyn olha para trás.

**Elenco:** `giles-mao-de-prata`, `bronwyn` · **Cenário:** `campanha/hq/vol-01-a-ancora-quebrada/cenario-salao.png`

- **narracao** · em `[44, 18]`
  > Ele não a acha. O colar continua no bolso dele, e ele não diz nada a ninguém.

### 22.6 · plano médio, de dentro para fora, sem balão

**Caixa:** `[0, 70, 100, 30]` · **Luz:** contraluz total: fumaça clara, figuras pretas, e nada do lado de fora

**O que se vê.** A porta dos fundos entreaberta, vista de dentro: a fumaça do salão sendo puxada para fora por ela, e cinco silhuetas contra o escuro.

**Elenco:** `comam-obabaroy`, `irmao-kaelric`, `jah-kagadu`, `negrum-carneiriums`, `nelsowned`

_Sem balão._

---

## Contagem

- **Páginas:** 22
- **Quadros:** 127
- **Média:** 5.8 quadros por página
- **Quadros com balão:** 114

**Quantos quadros cada um do elenco aparece:**

| Slug | Quadros |
|---|---|
| `negrum-carneiriums` | 30 |
| `hoel-meia-orelha` | 29 |
| `nelsowned` | 23 |
| `bronwyn` | 16 |
| `irmao-kaelric` | 15 |
| `jah-kagadu` | 15 |
| `donnwulf` | 12 |
| `comam-obabaroy` | 11 |
| `giles-mao-de-prata` | 7 |
| `osric-de-bannock` | 6 |
| `morto-vivo-tropeiro` | 6 |
| `morto-vivo-apostador` | 5 |
| `morto-vivo-vulto` | 5 |
| `wat` | 4 |

