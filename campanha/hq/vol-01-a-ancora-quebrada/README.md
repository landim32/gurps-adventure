# Volume 1 — A Âncora Quebrada

**Campanha:** Tormento Vil · **Capítulo de origem:** [1. Encontro na Taberna](../../01-encontro-na-taberna/)
**22 páginas · 127 quadros · 17 cenas**
**Estado: passo 7 de 10 (Avatares), aberto — 1 de 11 feito. O volume está em espera,
por decisão do usuário.**

> **A fila de passos foi renumerada.** Os esboços passaram a ser o **passo 5**, antes de
> qualquer gasto: 1 abrir · 2 recorte · 3 cenas · 4 roteiro · **5 esboços** · 6 elenco e
> cenário · 7 avatares · 8 folhas de modelo · 9 a arte · 10 fechar. Os cinco primeiros não
> gastam nada. Este volume fez o 6 e parte do 7 **antes** do 5, e o 5 foi fechado depois,
> em 16/09/2026 — o que ele denunciou já está corrigido no roteiro.

> **Este arquivo é o ponto de retomada do volume.** Ele existe para que outra sessão — ou
> a mesma daqui a um mês — continue sem repetir chamada nem refazer decisão já tomada.
> No **passo 10** ele é reescrito como o README definitivo do volume (o que é, de que
> capítulos saiu, como refazer). Até lá, o que vale é o que está aqui.

---

## Onde o volume está

| Passo | O quê | Estado |
|---|---|---|
| 1 | Abrir o volume | ✅ concluído e aprovado |
| 2 | Recorte e sinopse → [`00-recorte.md`](00-recorte.md) | ✅ aprovado, **com uma errata posterior** (ver abaixo) |
| 3 | Lista de cenas → [`01-cenas.md`](01-cenas.md) | ✅ aprovada, com as três dúvidas decididas |
| 4 | Roteiro → [`roteiro.md`](roteiro.md) + [`roteiro.json`](roteiro.json) | ✅ aprovado |
| 5 | Esboços → [`esbocos/`](esbocos/) — 22 páginas, Pillow, custo zero | ✅ concluído. **17 correções de layout + 1 errata de contagem**, todas já aplicadas ao roteiro |
| 6 | Elenco e cenário → [`elenco.md`](elenco.md), os 9 `npc.md`, `cenario-salao.png` | ✅ concluído |
| **7** | **Avatares** | **▶ ABERTO — 1 de 11 feito, 10 faltam** |
| 8 | Folhas de modelo | ⬜ não começado |
| 9 | A arte dos 127 quadros | ⬜ não começado |
| 10 | Montar, fechar, registrar e **commitar** | ⬜ não começado |

**Nada foi commitado.** O commit é do passo 10 e de nenhum outro.

## O que falta no passo 7 — a fila dos avatares

**11 imagens de avatar no total; 1 feita, 10 restantes.** A ordem é a da presença em
quadro: se o crédito acabar no meio, que tenha acabado depois do mais presente.

| # | Slug | Quadros | Estado |
|---|---|---|---|
| 1 | `hoel-meia-orelha` — **vivo** | 29 | ✅ **feito e aprovado** — não refazer |
| 2 | `hoel-meia-orelha` — **morto** | — | ⬜ arquivo à parte (a skill só grava `avatar.png`; gerar como foi feito o cenário) |
| 3 | `bronwyn` | 16 | ⬜ **é a próxima da fila** |
| 4 | `donnwulf` | 12 | ⬜ |
| 5 | `giles-mao-de-prata` | 7 | ⬜ |
| 6 | `osric-de-bannock` | 6 | ⬜ |
| 7 | `morto-vivo-tropeiro` | 6 | ⬜ |
| 8 | `morto-vivo-apostador` | 5 | ⬜ |
| 9 | `morto-vivo-vulto` | 5 | ⬜ |
| 10 | `wat` — **vivo** | 4 | ⬜ |
| 11 | `wat` — **rasgado** | — | ⬜ arquivo à parte |

Os dois estados do Hoel e do Wat estão **aprovados pelo usuário**. Os PJs **não têm avatar
gerado**: o retrato deles já existe em `personagens/<slug>/`, e o do Jah é `foto.jpg` — a
skill acha sozinha, não se cria `foto.png`.

**Ao gerar:** uma imagem por vez, prompt à vista, um sim, uma chamada, a conferência contra
o `npc.md`. Passe sempre `--descricao` limpa e `--estilo` (o partido sépia), senão o script
despeja o `npc.md` cru dentro do prompt. Detalhe a vigiar na Bronwyn: **o colar de ouro
pesado no pescoço**, de que a página 13 inteira depende.

---

## O que já está fixado e NÃO se refaz

**1. O partido gráfico: lápis e nanquim sobre papel tonalizado, sépia quase monocromática.**
Está na chave `estilo` do [`roteiro.json`](roteiro.json), 1.222 caracteres, e é herdado
pelos 127 quadros. Contém a regra que torna o volume viável: *FIRELIGHT IS RENDERED AS
VALUE, NOT AS HUE* — perto do fogo o papel fica nu, longe dele a hachura adensa até o
preto. Testada e aprovada no cenário.

**2. O cenário `cenario-salao.png`, em sépia — aprovado com duas falhas conhecidas.**
Referência de **75 dos 127 quadros**. Acertou: balcão e lareira grande à direita, tapete e
mesa comprida no meio, escada à esquerda, porta dupla ao fundo, boca do corredor dos
fundos, nenhuma âncora dentro, salão vazio, sem mar, sem letra, e o partido sépia igual ao
do elenco. **Falhou em dois itens vizinhos: a segunda lareira e o braseiro de ferro.**
Ver o gatilho abaixo. A conferência inteira está em
[`cenario-salao-prompt.md`](cenario-salao-prompt.md).

**3. O avatar do Hoel, com as duas orelhas — e a meia orelha é dita, não desenhada.**
O gerador recusou a mutilação em **três métodos diferentes** (`/generations` direto;
`/generations` com a cabeça virada para expor a orelha; `/edits` com a imagem como
referência e a forma descrita sem palavra de violência). Nas três acertou todo o resto.
**Não recomece a tentativa** — nem aqui, nem na folha de modelo do passo 8, nem no volume
2. O apelido é dito em dois recordatórios, `p2q2` e `p19q6`, ambos tirados da narração do
Mestre. O registro completo está no [`npc.md` do Hoel](../../npcs/hoel-meia-orelha/npc.md)
e em [`elenco.md`](elenco.md).

**4. A errata do `00-recorte.md`.** A seção *Tom* dizia "a paleta esfria e escurece"; num
volume de matiz única e quente isso é impossível, e a frase passou a "a página escurece: o
papel vai sendo tomado pela hachura, os claros encolhem". A errata está marcada e datada
dentro do próprio arquivo — o recorte é aprovado e não se mexe nele de novo sem o usuário.

**5. A errata da contagem na página 15 — "E o terceiro é pequeno".** O esboço revelou um
erro que tinha passado pelo recorte, pelas cenas e pelo roteiro: eu enfileirei **três**
mortos no quadro 4 (tropeiro, apostador e o vulto) e mantive, no quadro 5, o recordatório
literal do Mestre, que chama o Wat de **terceiro**. Desenhado, o erro salta aos olhos.

**A frase do Mestre estava certa; quem errou fui eu.** A narração de 07/09/2026 23:35 —
literal na exportação do WhatsApp e no `README.md` do capítulo — enumera **dois** antes do
menino: *"O da frente é um tropeiro… Atrás dele vem um dos apostadores… E o terceiro é
pequeno."* O quarto que entra existe ("São quatro"), mas **o Mestre nunca o descreve nem o
conta**. Fui eu que o pus na fileira ao decupar a cena.

**Por isso o conserto não foi mexer na narração** — que é registro e é literal —, **e sim
consertar o quadro**: o `p15q4` passou de "três figuras em fileira" para **"dois na luz e
um quarto na sombra"**. O vulto continua em cena, atrás, menor e sem rosto, que é
exatamente o papel dele. Com isso "E o terceiro é pequeno" volta a ser verdade.
Registrado como errata dentro do [`01-cenas.md`](01-cenas.md), que é de onde o engano veio.

---

## ⚠️ O gatilho do canto sudeste — para quem for fazer o passo 9

**O `cenario-salao.png` não tem o braseiro de ferro nem a segunda lareira.** O gerador
trocou o braseiro por um caldeirão **duas vezes**, com prompts diferentes — na segunda com
a palavra *cauldron* proibida em letras maiúsculas — e a lareira menor simplesmente não
saiu. É o mesmo comportamento da orelha do Hoel: ele entende o pedido e substitui pelo
objeto mais comum.

Aquele canto carrega o clímax: é a alvenaria contra a qual o morto é projetado na página 18
e é o braseiro de onde o incêndio começa na página 21. Cerca de **18 quadros**, nas páginas
17, 18 e 21.

**A decisão, já tomada:** o canto fica por conta do texto de cada quadro, que já descreve o
braseiro e a lareira no `visual`. **Se o `p17q5` — o encontrão do Kaelric contra o braseiro,
o primeiro quadro do volume naquele canto — sair errado**, gere **uma** referência de
detalhe só do canto sudeste (lareira menor + braseiro de brasas vivas + a porta ao lado) e
use-a como `cenario` naqueles ~18 quadros. **1 chamada. Não regere o salão inteiro:** ele
acertou dez outros itens, incluindo o partido gráfico.

Este gatilho também está **dentro do `roteiro.json`**, no campo `nota` do quadro `p17q5`, e
aparece no `roteiro.md` com destaque. Ele não vaza para o prompt — foi conferido.

---

## As chamadas de imagem

### Gastas: 5

| # | O quê | Situação |
|---|---|---|
| 1 | `cenario-salao.png` em cor quente | **substituída** pela versão em sépia |
| 2 | Avatar do Hoel, 1ª tentativa | descartada — duas orelhas, e a sépia saiu por acaso |
| 3 | Avatar do Hoel, 2ª tentativa | descartada — duas orelhas, mas fixou o partido sépia |
| 4 | Avatar do Hoel, 3ª tentativa (`/edits`) | ✅ **em vigor** |
| 5 | `cenario-salao.png` em sépia | ✅ **em vigor** |

**Duas em vigor, três consumidas no aprendizado** — o partido gráfico e o limite do
gerador. Duas outras tentativas não chegaram a gastar: uma bateu no bug do `"n": "1"` (já
corrigido na skill) e outra num 429 de crédito esgotado.

### A projetar

| Passo | O quê | Chamadas |
|---|---|---|
| 5 | Esboços | **0** — Pillow puro, **feito** |
| 7 | Avatares restantes | **10** |
| 8 | Folhas de modelo — 5 PJs + 9 NPCs | **14** (ver ponto em aberto) |
| 9 | A arte dos quadros | **127** — a contagem **não mudou** com os esboços |
| — | Referência do canto sudeste, **se o gatilho disparar** | 0 ou 1 |
| | **Total a gastar** | **151, podendo ir a 154** |

**Ponto em aberto, para decidir no passo 8:** os dois estados extras (Hoel morto, Wat
rasgado) ganham **folha de modelo própria** ou basta o avatar? O Hoel morto fica de pé e
ataca nas páginas 19 e 20, o que pesa a favor; o Wat morto aparece em três quadros. Se os
dois ganharem folha, o passo 8 vai de 14 para 16 e o total a 153–156.

---

## Os arquivos do volume

```
vol-01-a-ancora-quebrada/
  README.md                  ← este arquivo: o estado e a retomada
  00-recorte.md              recorte, sinopse, tom, gancho · aprovado (com errata)
  01-cenas.md                17 cenas, 22 páginas · aprovada
  roteiro.md                 o roteiro legível, 127 quadros
  roteiro.json               a fonte da verdade dos scripts · estilo sépia fixado
  elenco.md                  quem aparece, onde está a referência, o gasto por passo
  cenario-salao.png          o salão em sépia · referência de 75 quadros
  cenario-salao-prompt.md    o prompt e a conferência item a item
  esbocos/pagina-NN.png      as 22 páginas em figuras geométricas · passo 5
```

Os NPCs moram fora daqui, em [`campanha/npcs/<slug>/`](../../npcs/), porque servem a
campanha inteira e se reusam no volume 2: **9 pastas com `npc.md` escrito**, todas com os
prompts de `avatar` e `modelo` já gravados por `--so-prompt`, e só o Hoel com `avatar.png`.

**A Teressy é figurante neste volume** — um quadro só, sem avatar e sem folha, descrita no
prompt do `p2q6`. Se ganhar peso num volume futuro, aí sim recebe pasta e modelo.
