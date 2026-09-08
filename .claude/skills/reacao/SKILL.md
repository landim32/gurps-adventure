---
name: reacao
description: >
  Rola o teste de reação de cada NPC do local diante de cada personagem, pela regra do
  Módulo Básico: pega os modificadores das fichas e do npcs.md do capítulo, rola 3d por
  par, classifica na Tabela de Reações e guarda o resultado no capítulo atual, para que a
  atitude de cada NPC continue valendo pelo resto da cena. Use when the user asks
  "role as reações", "como os NPCs reagem", "teste de reação do grupo", "o que o taberneiro
  acha deles", ou /reacao.
---

# Testes de reação

Um teste **por par NPC × personagem** — é a regra da casa que está no `CLAUDE.md`
("teste de reação entre cada jogador e cada NPC") aplicada de uma vez para o local inteiro.

**3 dados, sem NH e sem atributo.** Soma-se os modificadores e lê-se a faixa; quanto maior,
melhor. É o inverso de todo o resto do sistema.

## Isto é segredo do Mestre

O livro é explícito (MB, pág. 180): a jogada é feita **sem que os jogadores saibam o
resultado** — eles não podem saber se o velho fazendeiro simpático está dando um conselho
sincero ou mandando-os para uma armadilha.

**Nada daqui vai para o WhatsApp.** Esta skill não gera bloco para colar; o que sai da tela
é para o Mestre. O que a mesa recebe é a *interpretação* do NPC, pela `narrar` — o jogador
descobre que Donnwulf o detesta porque Donnwulf age como quem detesta, nunca porque leu um 3.

## 1. Antes de rolar: ler os modificadores

Os do **personagem** o script tira sozinho do campo `reacao` da ficha
(`personagens/<slug>/personagem.json`) — é a caixa *Reação* da planilha, onde já estão
Aparência, Carisma, Voz, Status. Vale o primeiro número com sinal; se houver parte
condicional (`"-2 (porte); +2 cristãos"`), o script **avisa na tela** e a decisão é sua.

Os do **NPC** estão em prosa no `npcs.md` do capítulo, na linha `**Reação:**`. Leia antes
de montar o comando — é o passo que a skill não faz por você:

| O que está escrito lá | Como entra no comando |
|---|---|
| "-1 de saída (não quer conversa)" | `--npcs "Osric de Bannock:-1"` |
| "+2 para quem brindar ao noivado" | `--mod "Giles>NelsOwned:+2:brindou ao noivado"` |
| "neutra com todos" | só o nome, sem nada |

A diferença importa: **`:-1` é a atitude do NPC com todo mundo**; `--mod` é o que aquele
personagem em particular fez para merecer melhor ou pior.

Some também o que o livro manda e não está em ficha nenhuma: **abordagem boa vale +1 ou
mais, abordagem desastrada -1 ou -2**; perícia apropriada à ocasião (Manha no submundo,
Burocracia com funcionário); preconceito racial; **especialista em Diplomacia, NH ≥ 20,
vale +2 em qualquer reação**. Tudo isso entra como `--mod`, com o motivo escrito — o motivo
fica gravado e é o que explica o número seis meses depois.

## 2. Rolar

```
python .claude/skills/reacao/scripts/reacao.py --local "A Âncora Quebrada" \
  --npcs "Hoel Meia-Orelha, Osric de Bannock:-1, Giles Mão-de-Prata, Donnwulf" \
  --mod "Giles>NelsOwned:+2:brindou ao noivado" \
  --mod "Donnwulf>Comam:-3:recusou o braço-de-ferro"
```

| Opção | Para quê |
|---|---|
| `--npcs` | Quem está no local. `:-1` para a atitude de saída |
| `--pjs` | Padrão: **todos os personagens da campanha**, na ordem do README |
| `--mod` | `NPC>Personagem:+2:motivo` — repita quantas vezes precisar |
| `--contexto` | `geral` (padrão), `combate`, `comercio`, `ajuda`, `informacao`, `lealdade` |
| `--local` | Onde a cena se passa; entra no registro |
| `--listar` | Só mostra o que já foi rolado neste capítulo |
| `--tudo` | Mostra também as neutras, com a conta |
| `--refazer` | Rola de novo pares que já têm resultado |
| `--nao-gravar` | Não escreve nada — para experimentar |

Nome parcial funciona: `Giles` acha `Giles Mão-de-Prata`.

**O contexto muda o que a faixa significa.** Um "Ruim" numa transação é o mercador pedindo
o dobro; num combate iminente é ele atacando, a menos que esteja em menor número. O script
imprime a coluna *Reação Geral*; para as outras, abra
`livros/gurps-mb-3ed/21-quadros-e-tabelas.md` na faixa que saiu.

## 3. O que mostrar ao usuário

O script já filtra, e **o seu resumo segue o mesmo peso**:

| Faixa | Como tratar |
|---|---|
| **Desastrosa, Muito Ruim, Muito Bom, Excelente** | **Muita ênfase.** Diga o que muda na cena: quem vai atrapalhar, quem vai ajudar, quem vira aliado ou inimigo |
| Ruim, Fraca, Boa | Uma linha cada, sem drama — é textura |
| **Neutra** | **Não comente.** O NPC está desinteressado e não há nada a dizer |

Uma reação extrema merece uma frase sua dizendo **o que fazer com ela**: um "Excelente" do
taberneiro é a bebida por conta da casa e um aviso sussurrado; um "Muito Ruim" do pedreiro
é o empurrão no ombro quando o personagem passa. Ligue o número à cena que está no plano,
não repita a linha genérica da tabela.

## 4. Isto tem memória

O resultado fica em **`campanha/NN-capitulo/reacoes.json`**, na pasta de jogo do capítulo
atual. Não é log: é **estado da cena**.

```
python .claude/skills/reacao/scripts/reacao.py --listar
```

**Rode isso antes de interpretar qualquer NPC** — antes de narrar, antes de responder por
ele, antes de decidir se ele ajuda. A reação já rolada manda no comportamento dele pelo
resto do capítulo.

**Par que já tem resultado não é rolado de novo.** Reação é a atitude do NPC, não um dado
por conversa; rolar de novo até sair bom é trapaça, e o script recusa sozinho. Quando os
personagens **mudam de abordagem** e o livro permite uma segunda tentativa (MB, pág. 180 —
subornar, oferecer mais, perguntar outra coisa), aí sim `--refazer`, **com a penalidade**:
`-2` na segunda tentativa, `-4` na terceira, e assim por diante, salvo se houve uma espera
conveniente. Passe como `--mod "NPC>Personagem:-2:segunda tentativa"`.

Se a primeira tentativa virou luta, **não há segunda**.

O script também registra um acontecimento no capítulo pela skill `campanha`, com os
destaques. Sem campanha ativa, ele avisa e grava em `campanha/reacoes.json`.

## Quando não rolar

> *"Os testes de reação têm como propósito dramatizar uma situação e NÃO controlá-la."*
> — MB, pág. 204

Se o encontro é importante para a aventura, **a reação é decidida antes, não sorteada**. O
plano do capítulo manda: quando ele diz que o NPC recebe os personagens de tal jeito, é
assim e ponto. Rola-se o resto.

**Reação pré-determinada com teto** também vale: um eremita pode ser "-3 com qualquer
estranho e **nunca melhor que neutra**". Saiu melhor que neutra, trate como neutra — e
**não role de novo**. O script não sabe disso; corte na mão e diga que cortou.

E há as **perícias que substituem a jogada**: quem tem Lábia, Sex-appeal ou Manha pode
testar a perícia em vez de depender do 3d, com os mesmos modificadores aplicados ao NH.
Nesse caso a rolagem é um teste de perícia comum — use a `roll` e a regra de sucesso
decisivo/falha crítica, não esta skill.

## Nunca invente o dado

Quem sorteia é a skill `roll`, e esta chama aquela. **Relate o que saiu**, número por
número. Não escreva um resultado sem ter rodado o comando, não rode de novo porque a mesa
merecia coisa melhor, e não arredonde a favor de ninguém.
