---
name: perguntar
description: >
  Responde a uma pergunta que um jogador fez sobre as regras ou sobre o lugar onde o
  personagem dele está — "o que eu vejo nessa sala?", "o que tem lá fora?", "quanto de dano
  faz uma espada larga?". Só responde: não rola dado, não age, não muda nada no ambiente nem
  no registro. Pensa a resposta do ponto de vista do personagem (escuro, porta fechada,
  distância) e nunca vaza o plano da campanha. Pergunta sobre uma criatura (o que é, hábitos,
  ataques, fraquezas) exige um teste de Naturalista do personagem, e pergunta sobre magia
  exige um teste de IQ + Aptidão Mágica; só se responde se ele passar. A saída é só a
  resposta, em Markdown.
---

# Responder a pergunta de um jogador

Um jogador pergunta; a skill **responde e para**. É consulta, não jogada — com uma exceção:
pergunta sobre criatura passa por um teste de Naturalista (seção 3a) e pergunta sobre magia,
por um de IQ + Aptidão Mágica (seção 3b).

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

## 3a. Pergunta sobre criatura: teste de Naturalista

**É a única rolagem desta skill.** Se a pergunta é sobre **o que uma criatura é ou sabe fazer**
— que bicho é, hábitos, como ataca, fraqueza, o que come, se é perigosa —, o conhecimento
vem da perícia **Naturalista** (Mental/Difícil, pré-definido IQ-6; `livros/gurps-mb-3ed/06-pericias.md`),
e o personagem **só responde se passar no teste**:

```bash
python .claude/skills/teste-nh/scripts/teste_nh.py --quem Krag --pericia Naturalista --mod 3 --motivo "território conhecido"
```

- **Quem rola é o personagem que perguntou**, com o NH da ficha (ou o pré-definido IQ-6 se não
  tem a perícia). Use o que o script imprimir; não role de novo nem de cabeça.
- **Modificadores do livro:** +3 em território conhecido, até −5 em ambiente muito estranho.
  Sem motivo para modificar, rola sem `--mod`. Criatura mágica ou de outro mundo fica a critério
  do Mestre; na dúvida, aplique o redutor e diga o motivo.
- **Passou:** responde o que a pergunta pediu, pela regra da seção 2 (só o que o personagem
  sabe) e do livro (`15-animais.md`, `09-criaturas.md` do Fantasy), conferido, nunca de memória.
  Sucesso decisivo pode render um detalhe a mais; vale o bom senso do Mestre.
- **Falhou:** a resposta é só **"Você não sabe."** Nada de pista, meia verdade nem "parece
  perigosa". Falha crítica: o Mestre pode dar uma informação errada, mas a skill não inventa;
  trate como falha comum e avise na linha da conta.
- **O que não precisa do teste:** o que se **vê de relance** (tamanho, cor, asas, jaula, o
  que ela está fazendo) continua sendo descrição da seção 3. O teste cobre o que exige
  **conhecimento**.
- **Cada pergunta nova sobre a mesma criatura** é nova tentativa (`--tentativa 2` = −1,
  `3` = −2), a menos que o Mestre diga o contrário.

## 3b. Pergunta sobre magia: teste de IQ + Aptidão Mágica

Se a dúvida é **sobre magia** — o que uma mágica faz, que efeito mágico é aquele, como um
encantamento ou objeto mágico funciona, como se desfaz —, o personagem rola **IQ + o nível de
Aptidão Mágica** dele (0 se não tem a vantagem) e **só responde se passar**:

```bash
python .claude/skills/teste-nh/scripts/teste_nh.py --quem Sae'Varyn --atributo IQ --mod 3 --motivo "Aptidão Mágica 3"
```

- **Quem rola é o personagem que perguntou.** O `--mod` é o nível de Aptidão Mágica da ficha
  (`campanha/CONTEXTO.md` ou `acao.py contexto`); sem a vantagem, sem `--mod`. Use o que o
  script imprimir; não role de novo nem de cabeça.
- **Mana:** o −5 da mana baixa vale só para **lançar**; para saber algo sobre magia, não entra.
  Se o Mestre disser o contrário, aplique e diga o motivo.
- **Passou / falhou / falha crítica / tentativa repetida:** igual à seção 3a. Passou, responde
  pelo livro de Magia (`livros/gurps-magia-3ed/`), conferido, filtrado pelo que o personagem
  sabe; falhou, **"Você não sabe."** com a conta; nova pergunta sobre o mesmo assunto é nova
  tentativa (−1, −2...).
- **Mágica que o personagem conhece** (está na ficha dele) é conhecimento dele: responde sem
  teste o que ela faz. O teste cobre a magia que ele **não** tem.
- **Criatura mágica** (pergunta sobre criatura *e* sobre magia): rola só um teste, o da
  natureza da dúvida. Hábitos e anatomia, Naturalista; o poder mágico dela, IQ + Aptidão Mágica.

## 4. O que a skill nunca faz

- **Não age e não muda nada.** As únicas rolagens permitidas são o teste de Naturalista
  (seção 3a) e o de IQ + Aptidão Mágica (seção 3b), ambos pelo `teste-nh`, sem `--gravar`.
  Nenhuma outra (`roll`, `disputa-nh`), nenhum movimento de peça,
  nenhum `campanha.py` (acontecimento, anotação, bolsa, saúde), nenhuma escrita no roll6,
  nenhum arquivo gravado. Se a pergunta embute uma ação ("vou olhar atrás da porta"),
  responda só que isso é uma ação a declarar.
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

Pergunta sobre criatura traz, **abaixo da resposta**, a linha da conta do teste, no formato
das outras jogadas (a mesa vê todas as rolagens):

```
Basilisco: o olhar dele machuca quem o vê, e quanto mais perto, pior. Olhar para o lado ou tapar os olhos ajuda.
> Naturalista NH 9 (IQ 15 −6 pré-definido) = *9*
> 3d [3, 4, 1] = *8* → sucesso por 1
```

```
Você não sabe.
> Naturalista NH 9 (IQ 15 −6 pré-definido) = *9*
> 3d [5, 4, 3] = *12* → falhou por 3
```

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
