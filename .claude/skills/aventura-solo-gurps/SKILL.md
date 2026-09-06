---
name: aventura-solo-gurps
description: >
  Cria ou edita aventuras solo de GURPS 3ª Edição no formato de Uma Noite de
  Trabalho: parágrafos numerados fora de ordem, escolhas e testes de 3d6, sem
  Mestre. O usuário descreve a premissa em poucos parágrafos; a skill monta o
  texto jogável completo. Use when the user asks to "criar uma aventura solo",
  "aventura solo de GURPS", "gamebook GURPS", "parágrafos numerados", "editar
  a aventura solo X", ou /aventura-solo-gurps. Não use para aventuras com GM
  e grupo — isso é texto de campanha, não este formato.
---

# Aventura solo de GURPS 3ª Edição

O modelo canônico é `livros/gurps-mb-3ed/22-uma-noite-de-trabalho.md`. **Leia-o**
antes de escrever a primeira aventura desta skill (e de novo se for editar uma
existente). Não copie o enredo nem as regras do Módulo Básico para cá.

Uma aventura solo é um livro-jogo: um jogador, um personagem, 3 dados, sem
Mestre. O texto ensina a mecânica na primeira vez que ela aparece.

## Pedido

O usuário dá **poucos parágrafos** (premissa, lugar, o que o PC está fazendo,
tom). Extraia:

- Objetivo (roubar, fugir, entregar, investigar…)
- Lugar (mapa mental de 4–8 cômodos/zonas com **hubs** a que se volta)
- Tipo de PC esperado (ladrão, guerreiro, mago…) e perícias que a aventura testa
- Ameaças (1–2 NPCs ou perigos)
- Cenário: **Yrth**, salvo o usuário pedir outro (Cyberpunk, etc.)

Se faltar tom ou objetivo, invente o que for coerente com Yrth e siga — não
pergunte. Avise as premissas no resumo final.

Tamanho: **80–120 parágrafos** por padrão. Se pedirem “do tamanho de Uma Noite
de Trabalho”, **150–185**. Curta pedida explicitamente: **40–60**.

## Regras de jogo — consultar, não inventar

Testes, combate, carga, dano, perícias e desvantagens saem de `livros/`. Use
Grep/Read no MB (`09-testes-de-habilidade.md`, `10-combate-basico.md`,
`06-pericias.md`, `04-desvantagens.md`, `21-quadros-e-tabelas.md`). Preços e
peso de tesouro nas tabelas de equipamento. Lugares e culturas de Yrth em
`livros/gurps-fantasy-3ed/` (mapa: `banestorm_world.jpg`).

**NPCs:** monte com a skill `criar-npc-gurps` (leia o SKILL.md dela). No texto
da luta, só o que o jogador precisa (ST/DX/IQ/HT, arma, NH, dano, Esquiva/Aparar,
RD). O bloco Farvaro completo vai num apêndice no fim do arquivo.

Combate padrão: **Sistema Básico** (como o parágrafo 76 do modelo), com opção
de usar o Avançado. A primeira luta explica o turno uma vez; as outras só
dizem “lute; se vencer vá para N, se cair vá para M, se fugir vá para P”.

## Grafo

Antes de numerar, desenhe o grafo (não precisa mostrá-lo ao usuário):

- **Começo** único (depois da Introdução, o jogador vai ao parágrafo 1).
- **Hubs**: cômodos a que se volta, cada opção de busca **uma vez**.
- **Testes** 3d6: sucesso e falha para destinos *diferentes*.
- **Portões** de vantagem/desvantagem (Pacifismo, Alfabetizado, Alcoolismo,
  fobias…): o texto manda ir a outro número sem escolha, como no modelo.
- **Luta** (um bloco de combate, vários jeitos de entrar).
- **Fins**: pelo menos um sucesso (casa com o butim), um fracasso (captura,
  morte, fuga de mãos vazias). O último número é o acerto de contas (tabela
  de tesouro + pontos de personagem), como o 185 do modelo.

Numeração **embaralhada**: o parágrafo 2 não é a continuação do 1. O jogador
nunca lê em ordem. Depois de escrever, confira:

1. Todo “vá para N / desvie para N / volte para N” existe.
2. Todo parágrafo (exceto fins) tem pelo menos uma saída.
3. Todo parágrafo é alcançável a partir do 1.
4. Não há laço sem saída.

## Forma do arquivo

Mostre a aventura na resposta. Grave em `aventuras/<slug>.md` (slug kebab-case,
igual à skill de personagem). Edição: releia esse arquivo, aplique a mudança,
**reconcilie todos os números citados** e grave no mesmo caminho.

```markdown
# <Título>

**Aventura Solo**

<uma linha: um jogador, sem Mestre, 3d6, personagem de ~N pontos / tipo>

## Como Jogar

A aventura é dividida em parágrafos numerados. Não os leia em ordem. Comece
pelo **1** e salte para o número que o texto indicar.

A maioria dos parágrafos tem duas ou mais saídas. Às vezes você escolhe;
outras, o destino depende de 3 dados (teste de perícia, atributo ou sentido).
Nível pré-definido: use o do Módulo Básico se a perícia não estiver na ficha.

Você precisará de lápis, papel, 3d6 e uma Planilha de Personagem. Ladrões
levam pouco peso; a sacola desta aventura carrega até <N> kg (padrão 25).
Anote o que pegar. O que já levou não está mais no cômodo se você voltar.
Busca, Visão ou IQ num aposento: **uma** tentativa, salvo o texto dizer o
contrário.

Combate: Sistema Básico, salvo você preferir o Avançado.

## Introdução

<2ª pessoa, presente, 1–3 parágrafos. Fecha com “Vá para o parágrafo 1.”>

### 1
<…>
```

Cada parágrafo:

```markdown
### N
<prosa curta, 2ª pessoa.>
Se <condição>, vá para A. Caso contrário, vá para B.
```

- Frases de salto iguais às do modelo: “vá para N”, “desvie para N”, “volte para N”.
- Primeira ocorrência de um teste: uma ou duas frases ensinando (3d6 ≤ NH;
  o que é jogada condicionada). As seguintes só dizem “teste Furtividade”.
- Referências de página do MB em itálico, opcionais, no estilo *Veja a pág. 86*.
- Tesouro: nome, peso em kg, valor em $ quando o jogador puder saber.
- Parágrafo de combate: iniciativa, sequência de um turno, dano da ameaça,
  HT 0 → teste de HT para ficar de pé, depois os três destinos (vence / cai / foge).
- Último parágrafo: tabela Item / Valor / Receptador (metade é o padrão do
  modelo) e **Vivência** — pontos de personagem (sobreviver, tesouro, luta,
  penalidade por assassinato; mínimo 0), no mesmo espírito do 185.

Tom: português direto de ficha/aventura da edição brasileira. Sem floreio.
Não escreva um conto linear disfarçado de parágrafos.

## Edição

1. Ache `aventuras/<slug>.md` (ou o caminho que o usuário der).
2. Aplique o pedido (novo cômodo, outro NPC, tesouro, trecho que não fecha).
3. Se um número mudar, atualize **todas** as referências a ele.
4. Rode de novo a conferência do grafo.
5. Diga o que mudou.

## Depois de gravar

Uma linha: título, slug, quantos parágrafos, hubs, ameaça (e de qual livro veio
o NPC), pontos de personagem no acerto de contas, caminho do arquivo.
