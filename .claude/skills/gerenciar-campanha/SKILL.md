---
name: gerenciar-campanha
description: >
  Cria e conduz a campanha de GURPS em andamento: escreve o plano dividido em capítulos
  no padrão de Caravana para Ein Arris, mantém tudo em campanha/ com um README.md que
  indexa, e registra o histórico do que de fato aconteceu na mesa (cada acontecimento
  numa pasta de evento). Só existe uma campanha ativa por vez; ao terminar, ela é
  arquivada em historico/campanhas/. É por esta skill que as outras registram o que
  aconteceu. Use when the user asks to "criar uma campanha", "começar campanha",
  "registrar o que aconteceu", "anotar na campanha", "encerrar a campanha", ou
  /gerenciar-campanha.
---

# Gerenciar a campanha

Duas coisas diferentes moram aqui, e a diferença é o que faz a skill funcionar:

- **O plano** — a campanha como foi imaginada. Capítulos escritos antes, no padrão do
  livro.
- **O histórico** — a campanha como de fato aconteceu na mesa. Escrito depois, evento a
  evento, e quase sempre diferente do plano.

Os dois convivem sem se contaminar. O plano não é reescrito quando os jogadores fogem
dele; o que muda é o histórico, que registra que fugiram.

## Estrutura

```
campanha/                     a campanha ATIVA (só existe uma)
  README.md                   informações básicas + índice (gerado)
  plano/
    README.md                 Descrição do Cenário
    npcs.md                   NPCs de toda a campanha
    01-<capitulo>/            uma PASTA por capítulo
      README.md               a cena
      npcs.md                 quem aparece nesta cena
  historico/
    01-<evento>/
      README.md               introdução + lista de acontecimentos

historico/campanhas/
  <slug-da-campanha>/         campanhas encerradas, inteiras
```

**Uma campanha ativa por vez.** O script recusa criar uma segunda enquanto houver
`campanha/README.md` — encerre a atual antes. Isso não é burocracia: é o que garante que
"a campanha" numa conversa qualquer signifique sempre a mesma coisa, e que as outras
skills saibam onde escrever sem perguntar.

## O script

```
python .claude/skills/gerenciar-campanha/scripts/campanha.py <comando>
```

| Comando | O que faz |
|---|---|
| `estado` | Mostra a campanha ativa. `--json` para consumo por outra skill |
| `criar --nome "..."` | Monta a estrutura. Aceita `--mestre --cenario --pontos --premissa` |
| `capitulo --titulo "..."` | Novo arquivo de capítulo no plano, já com o esqueleto |
| `atual --capitulo 3` | Marca **em que capítulo a mesa está** — outras skills leem isso |
| `evento --titulo "..."` | Nova pasta de evento no histórico, com o README de introdução |
| `acontecimento --evento 1 --texto "..."` | Anota um fato, com data e hora |
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

### Cada capítulo é uma pasta

`capitulo --titulo "..."` cria `plano/NN-<slug>/` com dois arquivos:

- **`README.md`** — a cena: o que acontece, a tabela de testes, o que fazer se os
  jogadores fizerem outra coisa.
- **`npcs.md`** — quem aparece **nesta cena**.

Pasta e não arquivo solto porque um capítulo acumula coisa: o mapa do combate, a tabela de
encontros, o texto que se lê em voz alta, o desenho da planta. Tudo isso mora junto da
cena a que pertence, em vez de espalhado.

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

Um **evento** é uma cena que aconteceu: uma briga, uma negociação, uma viagem, uma
descoberta. Ganha pasta numerada e um README com introdução; os fatos vão sendo
acrescentados por baixo, com data e hora.

```
campanha.py evento --titulo "Confusão na taberna" \
  --onde "Taberna do porto, Mégalos" --quem "Comam Obabaroy, Cerdic" \
  --capitulo 02 --resumo "O que era para ser uma conversa virou briga."

campanha.py acontecimento --evento 1 \
  --texto "Teste de Reação do anão: 6 — muito ruim. Ele parte para cima."
```

`--evento` aceita o número (`1`) ou o nome da pasta.

**O que merece virar acontecimento:** decisão de jogador, resultado de dado que mudou o
rumo, dano relevante, NPC que morreu ou mudou de lado, item ganho ou perdido, informação
descoberta, promessa feita. Registre o **resultado do dado quando ele importou** — é o
que permite reconstruir a cena meses depois e o que dá peso ao que aconteceu.

**O que não merece:** cada rolagem de uma luta longa, conversa sem consequência,
descrição de cenário. O histórico é para consultar, não para transcrever.

Escreva no passado e em terceira pessoa, curto — uma linha por acontecimento. O detalhe
longo vai no corpo do README do evento, acima da lista.

## O capítulo atual

`atual --capitulo 3` grava `**Capítulo atual:** 03` no README e é como **outras skills
sabem onde gravar o que produzem**. A `atualizar-mapa`, por exemplo, põe a imagem da mesa
em `campanha/plano/03-.../` em vez de deixá-la solta em `cenarios/`.

**Marque o capítulo ao começar a sessão.** É um comando só, e sem ele as outras skills
gravam num lugar genérico e avisam.

`estado --json` devolve `capitulo_atual` (o número) e `capitulo_atual_pasta` (o caminho
pronto para usar), ou `null` nos dois se ninguém marcou.

## Contrato para as outras skills

Outras skills registram na campanha **por aqui**, nunca escrevendo direto nos arquivos.
Ao escrever uma skill nova que deva alimentar a campanha, inclua isto nela:

> **Registrar na campanha.** Se houver campanha ativa
> (`campanha.py estado --json` devolve `"ativa": true`), registre o que esta skill
> produziu de relevante:
> ```
> python .claude/skills/gerenciar-campanha/scripts/campanha.py acontecimento \
>   --evento <n> --texto "<uma linha, no passado>"
> ```
> Não havendo campanha ativa, siga sem registrar — não crie campanha por conta própria.

E, se a skill **produz arquivo** (imagem, mapa, tabela), grave-o na pasta do capítulo
atual, lendo `capitulo_atual_pasta` do mesmo `estado --json`. Sem capítulo marcado, grave
no lugar genérico e **diga por quê** — a `atualizar-mapa` imprime uma linha `Destino:` em
toda execução, e é um bom padrão a copiar.

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
inteira para `historico/campanhas/<slug>/` — plano e histórico juntos, do jeito que
ficaram. Depois disso o repositório fica sem campanha ativa e pronto para a próxima.

Campanha arquivada é **leitura**, não material de trabalho: não edite o que já foi
arquivado. Se um personagem ou um NPC voltar numa campanha nova, copie o que interessa
para a campanha nova em vez de reabrir a antiga.
