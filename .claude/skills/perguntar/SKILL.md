---
name: perguntar
description: >
  Responde a uma pergunta que um jogador fez sobre as regras ou sobre o lugar onde o
  personagem dele está — "o que eu vejo nessa sala?", "o que tem lá fora?", "quanto de dano
  faz uma espada larga?". Só responde: não rola dado, não age, não muda nada no ambiente nem
  no registro. Pensa a resposta do ponto de vista do personagem (escuro, porta fechada,
  distância) e nunca vaza o plano da campanha. A saída é só a resposta, em Markdown.
---

# Responder a pergunta de um jogador

Um jogador pergunta; a skill **responde e para**. É consulta, não jogada.

```
/perguntar Andre: o que eu vejo nessa sala?
/perguntar Krag, tem alguém na viela?
/perguntar Ricardo: javali ainda fala?
```

## 1. Quem pergunta

**Toda pergunta tem dono.** O nome (de jogador ou de personagem, parcial) vem antes dos
dois-pontos ou da vírgula. Sem nome, **pergunte de quem é** antes de qualquer outra coisa. Com
nome, resolva o personagem e o estado dele:

```bash
python .claude/skills/acao/scripts/acao.py contexto --quem Andre
```

Isso traz a ficha (atributos, perícias, vantagens e desvantagens) e a lista de arquivos da
campanha. Leia o que a pergunta exigir:

| A pergunta é sobre | Leia |
|---|---|
| o lugar, o que há em volta, quem está ali | `campanha/mundo.md` (estado atual, ganha do plano), `lugares.md`, `npcs.md` e o README da pasta de jogo do capítulo (o que já foi narrado), depois o plano da cena |
| o próprio personagem (o que ele sabe, vê, sente, pode fazer) | `campanha/CONTEXTO.md` e a ficha |
| regra | os livros em `livros/` (`Grep`), nunca de memória |
| onde o personagem está agora | `get_map` e `list_map_tokens` do roll6, só leitura |

## 2. A regra de ouro: só o que o personagem sabe

**O plano é do Mestre.** Leia-o para saber o que há, mas a resposta é **filtrada pelo que
aquele personagem, ali, naquele momento, perceberia com os cinco sentidos**. Não vaza:

- o que está atrás de porta fechada, parede, esquina ou longe demais para ver;
- segredo, armadilha, passagem oculta, tesouro escondido, intenção ou ficha de NPC;
- o que vem nos próximos capítulos, o objetivo da trama, o que o Mestre decidiu em segredo;
- reação rolada de NPC (`reacoes.json`), números de ficha de NPC, rolagens secretas;
- o que só o Mestre sabe, mesmo que o personagem desconfie.

Se a resposta honesta é "você não sabe", diga isso. **Na dúvida, não revele.**

## 3. Responder pelo contexto do personagem

Pense **onde ele está e o que pode perceber agora**:

| Pergunta | Resposta |
|---|---|
| "O que eu vejo nesta sala escura?" | Que **não vê nada**, porque está escuro (e o que ele ouve ou sente, se houver). |
| "O que tem depois da porta?" | Que **só saberá abrindo**. A porta está fechada. |
| "O que tem lá fora?" | Que **só saberá saindo**. |
| "O que eu vejo nesta sala?" (iluminada, ele dentro) | **Descreve** o que há, de acordo com o plano e com o que já mudou na mesa, só o que se percebe de relance. |
| "Quem está aqui?" | Quem ele **vê**, descrito sem nome que ele não saiba. |
| "Qual o dano da espada larga?" | Responde a regra, conferida no livro. |

Quando o personagem tem o sentido que resolve a dúvida (visão no escuro de raça, olfato
aguçado, Prontidão), isso entra na resposta. **O que exigir teste (perceber algo escondido,
ler uma mentira) não se responde aqui:** diga que isso é uma ação e que ele precisa declará-la.

## 4. O que a skill nunca faz

- **Não age e não muda nada.** Nenhuma rolagem (`roll`, `teste-nh`, `disputa-nh`), nenhum
  movimento de peça, nenhum `campanha.py` (acontecimento, anotação, bolsa, saúde), nenhuma
  escrita no roll6, nenhum arquivo gravado. Se a pergunta embute uma ação ("vou olhar
  atrás da porta"), responda só que isso é uma ação a declarar.
- **Não decide o desfecho de nada** nem antecipa o que acontecerá se o personagem fizer algo.
- **Não revela o plano**, nem por dedução óbvia ("tem alguém ali, mas você não sabe quem").
- **Não inventa** lugar ou coisa que não esteja no plano ou já narrado. Se o plano é omisso
  e a pergunta é banal, diga o que seria razoável ver e não avance além.
- **Não responde regra de cabeça.** Confira em `livros/` e responda o que o livro diz.

## 5. A saída

**Apenas a resposta, em Markdown.** Nenhuma introdução, nenhuma conclusão, nenhum
"claro!", nenhum aviso sobre a skill, nenhuma nota ao Mestre, nenhuma pergunta de volta
(exceto a de "quem pergunta", quando falta o nome). Segunda pessoa, direta ao personagem.
**Resumida e direta:** responda só o que a pergunta pediu, em **1 a 3 frases curtas** (até
umas 50 palavras). Comece pelo fato, sem rodeio, sem clima, sem adjetivo de enfeite e sem
repetir a pergunta. Cite só o que importa de relance; o detalhe vem se o jogador perguntar de
novo. Uma lista só quando a resposta for uma lista, de poucos itens curtos.

Exemplos de saída:

```
Você não vê nada: a sala está completamente escura.
```

```
Só saberá abrindo a porta.
```

```
Sala de pedra com dois braseiros, mesas postas ao longo das paredes e uma porta de madeira ao fundo.
```
