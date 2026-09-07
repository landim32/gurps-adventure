---
name: cenario-rpg
description: >
  Cria ou edita cenários de RPG vistos de cima (taberna, masmorra, praça, acampamento,
  navio, cripta) para GURPS 3ª Edição, ambientados em Yrth. Produz a arte top-down
  limpa — sem grid, sem texto, sem personagens — em cenario/apenas-imagem/, junto com o
  prompt usado e a descrição das áreas com as regras que valem em cada uma (cobertura,
  iluminação, custo de movimento, linha de tiro). O grid hexagonal é aplicado depois,
  pela skill add-grid-hex. Use when the user asks to "criar um cenário", "desenhar a
  taberna", "planta da masmorra", "mapa do acampamento", "editar o cenário X", ou
  /cenario-rpg.
---

# Cenário de RPG visto de cima

Transforma uma descrição em texto ("uma taberna de dois ambientes com pátio", "a cripta
sob a capela", "o convés de um navio pirata") na **arte de um mapa de combate**, mais a
ficha do lugar para o Mestre.

Esta skill **não desenha o grid**. Ela entrega a arte limpa e a escala em metros; quem
põe os hexágonos é a skill **`add-grid-hex`**. A separação é proposital: a arte é cara de
gerar e o grid é barato de refazer, então dá para reajustar escala, cor e opacidade
quantas vezes for preciso sem tocar na imagem.

Produz em `cenario/apenas-imagem/`:

| Arquivo | O que é |
|---|---|
| `<slug>.png` | A arte top-down limpa — **sem grid, sem texto, sem personagens** |
| `<slug>.json` | Escala (`largura_m`, `altura_m`), dados do lugar e as áreas com suas regras. **Fonte da verdade para editar depois** — e é daqui que a `add-grid-hex` lê a escala sozinha |
| `<slug>-prompt.md` | O prompt de imagem, pronto para colar num gerador |
| `<slug>.md` | A ficha do cenário para o Mestre ler na mesa |

O slug é kebab-case, como em `personagens/`: "Taberna do Javali Manco" →
`taberna-do-javali-manco`.

`screenshots/taberna.jpg` é a **referência de estilo** (arte de terceiros, do Patreon
Mimosa20): madeira e pedra desenhadas de cima, luz quente das lanternas, mobília com
sombra própria. Use como alvo visual — nunca reproduza nem redistribua a arte em si.

## Fontes de regras (`livros/`)

| Preciso de... | Arquivo |
|---|---|
| **NT, viagem, clima, leis, economia, empregos** — o que existe no mundo | `livros/gurps-mb-3ed/19-cenarios.md` |
| Cobertura e esconderijo (redutores de -2 a -6) | `livros/gurps-mb-3ed/11-combate-avancado.md`, "Cobertura e Esconderijo" |
| Custos em pontos de movimento, obstruções, posições | idem, "Custos em Pontos de Movimento" |
| Linha de tiro, disparo através de hex ocupado | idem, "Alvejando" |
| Escuridão (-10 total; tocha ou lanterna reduz para -3) | `livros/gurps-mb-3ed/09-testes-de-habilidade.md` e `11-combate-avancado.md` |
| Preço e peso da mobília e do que estiver no lugar | `livros/gurps-mb-3ed/21-quadros-e-tabelas.md` |
| Reinos, cidades, cultura de Yrth — onde o lugar fica | `livros/gurps-fantasy-3ed/02-historia.md` a `07-reinos-oriente.md` |
| Mapa de Ytarria | `livros/gurps-fantasy-3ed/banestorm_world.jpg` |
| Criaturas que possam morar ali | `livros/gurps-fantasy-3ed/09-criaturas.md`, `livros/gurps-mb-3ed/15-animais.md` |

**Cuidado com um engano fácil:** o capítulo "Cenários" do Módulo Básico
(`19-cenarios.md`) *não* trata de mapas de combate — ele é sobre construir o **mundo**:
Níveis Tecnológicos, viagem e terreno, clima, leis, economia, empregos. Consulte-o para
decidir o que existe no lugar (NT 3 → iluminação a vela e lampião, vidro plano é luxo,
fechaduras simples) e para preço e disponibilidade. As regras que se aplicam *dentro* do
mapa — cobertura, movimento, linha de tiro — estão no cap. 14,
`11-combate-avancado.md`.

**Toda aventura se passa em Yrth**: ancore o lugar num reino, cidade ou região que já
exista no *Fantasy* antes de inventar.

## Fluxo de trabalho

### 1. Entender o pedido

Extraia — e invente o que faltar, informando no resumo final:

- **Que lugar é** e **onde fica em Yrth**. Isso define materiais, NT e o que existe lá:
  uma taberna do porto de Mégalos não se parece com uma casa de chá em Sahud.
- **Dimensões em metros.** Se o usuário não disser, estime pelo uso e diga qual
  estimativa adotou. Referências: porta simples 1 m, porta dupla 1,8 m, corredor 1,5 m,
  mesa redonda de taverna 1,2 m, cama 1 × 2 m, balcão 0,8 m de profundidade, escada 1 m
  de largura, cela de masmorra 2 × 3 m, baia de estábulo 1,5 × 3 m.
- **Ambientes**: quantos, e o que separa um do outro.
- **Momento**: dia, noite, lareira acesa, às escuras. Muda a luz da arte *e* os
  redutores de visão.

Um cenário de combate raramente precisa passar de **20 × 20 metros**. Acima disso os
rótulos do grid ficam ilegíveis e a mesa não usa. Se o pedido for maior, escolha o
ambiente que importa ou gere mais de um cenário.

### 2. Fechar a escala antes de gerar a arte

Decida **largura e altura em metros** primeiro, porque a arte precisa nascer na
proporção certa: 15 × 20 m pede uma imagem 3:4, não uma quadrada.

Escolha a resolução para que cada hexágono caia entre **40 e 60 px** quando a
`add-grid-hex` rodar — abaixo de 40 o rótulo não se lê. Para 15 m de largura, isso é
uma imagem de 600 a 900 px de largura, ou mais.

### 3. Escrever `<slug>-prompt.md`

Um parágrafo em **inglês** (rende resultado mais consistente na maioria dos geradores),
seguido de uma linha de estilo. Monte nesta ordem:

1. **Câmera, sempre no início:** *"Top-down orthographic battle map for a tabletop RPG,
   viewed from directly above, no perspective distortion"*. Nada de isométrico, nada de
   três quartos, nada de ponto de fuga.
2. **O lugar**: tipo, tamanho aproximado em metros, quantos ambientes e como se ligam.
3. **Piso e paredes de cada ambiente**, com o material (tábua corrida, pedra irregular,
   terra batida, palha) — é o que dá leitura ao mapa.
4. **Mobília e obstáculos**, item a item e onde ficam. Tudo que vira cobertura ou
   bloqueio precisa aparecer desenhado, senão o Mestre descreve algo que ninguém vê.
5. **Luz**: as fontes (lareira, lanternas, velas, luar pela janela) e a direção da
   sombra. Luz quente e localizada é o que faz o mapa parecer o da referência.
6. **Estilo e fechamento:** *"hand-drawn digital illustration, rich warm colors, clean
   linework, soft drop shadows under furniture, **no grid, no text, no labels, no
   characters, no tokens**"*.

O fechamento é obrigatório. Grid desenhado na arte briga com o grid de verdade, e
figuras desenhadas atrapalham os tokens da `token-hex-gurps`.

### 4. Gerar e salvar a arte

Gere a imagem se houver ferramenta de geração disponível na sessão. **Se não houver**,
entregue o `<slug>-prompt.md` ao usuário, peça que gere num gerador de imagens e salve o
resultado como `cenario/apenas-imagem/<slug>.png` — é o mesmo fluxo do retrato em
`criar-personagem-gurps`. Não invente que a imagem existe.

Com a arte na mão, **confira a proporção**: geradores erram tamanho relativo o tempo
todo. Ache um objeto de tamanho conhecido, veja quantos metros ele ocuparia na escala
que você definiu, e ajuste `largura_m` no JSON até bater. Uma porta simples tem 1 m; uma
mesa de taverna com as cadeiras, cerca de 2 m. Se a arte saiu com proporção diferente da
pedida, é o `largura_m` que muda — não force a arte.

### 5. Escrever o JSON e o Markdown

Grave o `<slug>.json` (esquema abaixo) e o `<slug>.md`. Confirme ao usuário: nome, onde
fica em Yrth, dimensões em metros, os caminhos gerados e **o comando da `add-grid-hex`**
para pôr o grid.

## Descrevendo as áreas (`<slug>.md` e o JSON)

Divida o cenário em **áreas nomeadas**. Para cada uma, registre o que o Mestre vai
precisar arbitrar sem parar para pensar:

| Campo | O que anotar |
|---|---|
| O que é | Uma frase: salão principal, balcão, despensa, pátio |
| Movimento | Custo extra em pontos, se houver: mobília apertada, escada, entulho, água |
| Cobertura | O redutor do MB para quem se protege ali: -2 ramagem, -3 corpo semi-exposto (agachado atrás de uma mesa), -4 cabeça e ombros (atrás do balcão), -5 só a cabeça |
| Luz | Redutor de visão: 0 bem iluminado, -3 luz de tocha ou lanterna, até -10 escuridão total |
| Bloqueio | O que corta linha de tiro (paredes, balcão alto, biombo) e o que não corta (mesa baixa, vaso de planta) |
| Notas | Porta que abre para dentro, tábua que range, lareira acesa (dano por fogo), janela que dá para o beco |

As **coordenadas de hexágono ficam de fora nesta etapa** — elas só existem depois que a
`add-grid-hex` rodar, porque dependem da origem e da escala do grid. Descreva as áreas
por posição ("parede norte", "canto sudeste", "os dois terços de baixo"). Quando o grid
existir, volte e anote os intervalos (`C3–F8`) no JSON e no MD.

Aponte também as **entradas e saídas**, que é a primeira coisa que os jogadores
perguntam. E, quando fizer sentido, uma linha sobre o que acontece se a briga começar:
onde estão os NPCs, o que eles derrubam, por onde fogem.

Mesas, cadeiras e balcões **derrubados** viram cobertura móvel — registre isso, porque é
o que os jogadores vão querer fazer.

## Esquema do JSON (`<slug>.json`)

```json
{
  "nome": "Taberna do Javali Manco",
  "local": "Mégalos, bairro do porto (Yrth)",
  "nt": 3,
  "momento": "noite, lareira e lanternas acesas",
  "arte": "taberna-do-javali-manco.png",
  "largura_m": 15.0,
  "altura_m": 20.0,
  "grid": null,
  "areas": [
    {
      "nome": "Salão principal",
      "hexagonos": null,
      "posicao": "centro e dois terços de baixo",
      "descricao": "Piso de tábua corrida, oito mesas redondas com cadeiras",
      "movimento": "+1 ponto para entrar em hex de mesa ou cadeira",
      "cobertura": "-3 agachado atrás de uma mesa; -4 se a mesa for derrubada",
      "luz": "0 (lanternas)",
      "bloqueio": "nenhum — as mesas são baixas e não cortam linha de tiro",
      "notas": "Derrubar uma mesa leva 1 turno e cria cobertura móvel"
    }
  ],
  "acessos": [
    {"posicao": "parede sul, ao centro", "hexagonos": null,
     "descricao": "Porta dupla para a rua, abre para dentro"}
  ]
}
```

`largura_m` é o campo que a **`add-grid-hex` lê sozinha** — mantenha-o correto, é o
contrato entre as duas skills. `grid` e os campos `hexagonos` ficam `null` até o grid
ser aplicado.

## Editando um cenário existente

1. Leia `cenario/apenas-imagem/<slug>.json` — é a fonte da verdade, não a imagem.
2. Mudanças que **não** exigem arte nova (corrigir a escala, mudar a luz de dia para
   noite na descrição, renomear áreas, ajustar cobertura, anotar as coordenadas depois
   do grid): edite o JSON e o MD e pronto.
3. Mudanças que **exigem** arte nova (derrubar uma parede, acrescentar um ambiente,
   trocar a mobília): reescreva o `<slug>-prompt.md`, gere ou peça a imagem nova, e
   depois reaplique o grid com a `add-grid-hex`.
4. Se `largura_m` mudar, **todas as coordenadas de hexágono mudam** — reaplique o grid e
   reescreva os intervalos. Não deixe rótulo velho apontando para hexágono errado.
