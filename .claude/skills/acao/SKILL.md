---
name: acao
description: >
  Resolve a ação que um jogador declarou em texto livre — "vou tentar furtar a bolsa do
  mercador na confusão", "subo no telhado", "peço a bebida do guarda e puxo conversa".
  Lê a ficha de quem age e o estado da cena, decide o que a ação exige pelas regras de
  GURPS 3ª Edição, chama as skills que resolvem (teste-nh, disputa-nh, combate, reacao,
  roll), narra o desfecho para a mesa e registra tudo: acontecimento no capítulo,
  mudança anotada nos NPCs, no grupo e no lugar, e o dinheiro lançado na bolsa da
  campanha. Não mexe na ficha do personagem — só quando o usuário pedir.
  Use when the user asks "/acao", ou quando trouxer a declaração de um jogador —
  "Ricardo: vou tentar furtar o Giles", "o Comam ataca o morto-vivo", "eles saem pela
  janela", "o Kaelric tenta acalmar a taberna".
---

# A ação declarada por um jogador

O jogador diz o que quer fazer, em português, do jeito dele. Esta skill transforma isso em
**regra aplicada, dado rolado, cena narrada e mundo atualizado** — nessa ordem, sem pular
nenhuma.

O formato da entrada é livre. Tudo isto é a mesma coisa:

```
/acao Ricardo: Vou tentar aproveitar a comoção e o baque na mesa para furtar o que
estiver mais ao meu alcance do Giles Mão-de-Prata
/acao O Comam avança no morto-vivo que entrou primeiro
/acao Bruno pega as moedas do chão e devolve metade ao Donnwulf
```

**Quem age vem antes dos dois-pontos** — nome do jogador ou do personagem, tanto faz. Sem
nome, pergunte de quem é a ação antes de qualquer outra coisa.

## 1. Contexto, sempre

```
python .claude/skills/acao/scripts/acao.py contexto --quem Ricardo
```

Sai de uma vez: de quem é o personagem, atributos e defesas, **a lista das perícias que ele
de fato tem, com NH**, **como cada NPC da cena já reagiu a ele** (do `reacoes.json` — não
role de novo) e os arquivos do capítulo na ordem de leitura, incluindo o
**`campanha/mundo.md`**, que diz como as coisas estão agora.

**Leia os arquivos antes de decidir qualquer número.** O que está anotado na pasta de jogo
ganha do plano quando os dois discordarem: o pedreiro de braço quebrado não aceita outro
braço-de-ferro, por mais que o plano diga que ele é invicto.

## 2. Decidir o que a ação exige

Esta é a parte que a skill não pode automatizar, e é o trabalho de verdade. A régua:

| O que o jogador quer | O que rola | Skill |
|---|---|---|
| Nada de difícil, nada em jogo — pedir cerveja, olhar em volta, atravessar o salão | **Nada.** Narre e devolva o turno | — |
| Algo difícil contra o mundo, sem ninguém resistindo — escalar, saltar, decorar, lembrar | Teste de perícia ou atributo | `teste-nh` |
| Alguém do outro lado resiste, percebe ou disputa — furtar, esconder-se, enganar, braço-de-ferro | **Disputa**, dos dois lados | `disputa-nh` |
| Violência declarada | Troca de golpes inteira | `combate` |
| Primeira impressão com um NPC que ainda não tem reação rolada | Teste de reação | `reacao` |
| Começou luta e ninguém sabe quem age primeiro | Surpresa e ordem | `iniciativa` |
| Alguém se move no mapa da cena | Posição nova | `atualizar-mapa` |
| Um dado avulso que nenhuma das anteriores cobre | 3d, 1d, o que for | `roll` |

**Nunca role de cabeça, nunca invente NH.** As skills acima é que rolam; esta aqui decide
qual chamar e com que número.

### Escolher a perícia e o modificador

1. **A perícia sai da ficha**, da lista que o `contexto` imprimiu. Se ele não a tem, o teste
   é pelo **nível pré-definido** — `teste-nh` já resolve isso sozinho e avisa.
2. **O modificador sai do livro ou da cena, e você diz de onde veio.** Confira com `Grep`
   em `livros/`, não de memória (`Grep "^### Punga" livros/gurps-mb-3ed/06-pericias.md`).
   Escreva o porquê: *"-2 pela mesa cheia, +3 pela comoção do braço quebrado"*.
3. **A comoção é um modificador, não um passe livre.** Um jogador que descreve bem a
   situação ganha bônus — não ganha sucesso automático.
4. Bônus e redutores das **desvantagens e vantagens** valem: Sorte, Reflexos em Combate,
   Azar, Carga. O `teste-nh` e o `disputa-nh` já leem a ficha; confira se pegaram.

### Do outro lado da disputa

Quando alguém resiste, **o NH do outro lado sai do `npcs.md` do capítulo** (o do plano, e
depois o da pasta de jogo, que ganha). NPC sem ficha recebe o número do Mestre — é para isso
que `disputa-nh` tem `--b-nh`. Diga em voz alta qual foi e por quê.

**Furto num salão cheio não é só contra o dono da bolsa:** quem está ao lado também pode
ver. Uma disputa contra o alvo resolve a cena; se o jogador foi ousado, vale uma segunda
contra a testemunha mais perigosa — e a falha aí é *ser visto por outro*, que é uma
consequência diferente e melhor.

### Falha crítica é obrigação

Toda ação declarada tem de ter uma resposta pronta para o 17 e o 18. Não improvise depois:
decida **antes de rolar** o que a falha crítica significa nesta cena, e diga na resposta ao
Mestre. É o que a campanha manda (`CLAUDE.md`) e é de onde saem as melhores cenas — o braço
quebrado do Donnwulf saiu de um 17.

## 3. Narrar o desfecho

O resultado vai para a mesa **em bloco de código, no formato do WhatsApp** (`*negrito*`,
`_itálico_`), curto: **3 a 8 linhas**, o suficiente para dizer o que aconteceu e devolver o
turno. Valem as mesmas proibições da skill `narrar` — nada de ficha, número, nome de regra
ou intenção de NPC que não dê para ver.

**O bloco dos dados é separado do bloco da narração.** As skills de rolagem já entregam o
texto pronto delas; repasse-o e depois narre. Mostrar a rolagem à mesa é decisão do Mestre,
mas ela existe.

Se o desfecho abriu uma cena inteira — a taberna virou briga, o grupo saiu para a rua —
chame a skill `narrar` em vez de escrever um parágrafo aqui, e arquive por lá.

## 4. Registrar — as três camadas

Nenhuma ação termina sem isto. A ordem importa, e **cada camada responde a uma pergunta
diferente**:

**a) O que aconteceu** — uma linha no log do capítulo:

```
python .claude/skills/campanha/scripts/campanha.py acontecimento \
  --texto "Jah Kagadu tentou furtar a bolsa de Giles na comoção: Punga 13-2 contra a
           Percepção 10 do mercador. Passou por 4; levou uma bolsa de moedas."
```

**b) O que ficou diferente** — a anotação, para quem for interpretar a cena depois:

```
campanha.py anotar --npc "Giles Mão-de-Prata" --tag item \
  --texto "Perdeu a bolsa de $300 no bolso do gibão, e ainda não notou."
campanha.py anotar --pj "Jah Kagadu" --tag item \
  --texto "Está com a bolsa de $300 de Giles. Ninguém viu."
```

Anote **os dois lados** — o que o NPC perdeu e o que o personagem ganhou. Um sem o outro é
como as contradições nascem. Se a relação mudou de patamar (o mercador passou a desconfiar,
o guarda passou a dever um favor), isso é outra anotação, com `--tag relação`.

**c) O dinheiro** — o que entrou ou saiu da bolsa vai para `campanha/bolsa.md`, com sinal
e motivo:

```
campanha.py bolsa --pj "Jah Kagadu" --valor +300 --motivo "Bolsa furtada de Giles (cap. 01)"
campanha.py bolsa --npc "Giles Mão-de-Prata" --valor -300 --motivo "Furtada por Jah Kagadu"
```

Os dois lados, aqui também: o que um ganhou o outro perdeu. O saldo é recalculado sozinho.

**d) O corpo** — dano, Fadiga e ferimento que fica vão para `campanha/saude.md`:

```
campanha.py saude --pj "Negrum Carneiriums" --pv -3 --motivo "Machadada do orc (cap. 04)"
campanha.py saude --npc "Donnwulf" --estado "Braço direito incapacitado (Maneta até curar)"
```

Lance o que **sobrevive à cena**: o arranhão que sara em dez minutos não precisa de linha.

**A ficha do personagem não é tocada.** `personagem.json`, `personagem.md` e `ficha.jpg`
só mudam quando o usuário **pedir** — "lance na ficha", "atualize o inventário dele". Sem
esse pedido, nada do que a mesa produziu entra lá: nem dinheiro, nem item, nem ponto de
vida, nem perícia nova. A ficha guarda o que o personagem *é*; a **bolsa** guarda o que ele
*tem*, a **saúde** guarda como ele *está*, e as anotações guardam o resto.

Quando o pedido vier, aí sim é a skill `criar-personagem-gurps` que edita — ela recalcula
peso, Carga e tudo o que depende do que mudou, e regera a `ficha.jpg`. **Nunca edite o
`personagem.json` à mão.**

## 5. Quando não rolar nada

Metade das declarações não precisa de dado, e rolar por tudo mata a cena:

- **Sucesso automático** quando a ação é banal para quem a faz: o ladrão com Furtividade 17
  atravessando um salão barulhento não testa nada.
- **Fracasso automático** quando é impossível: não se arromba um cofre anão com uma colher,
  por melhor que seja a descrição.
- **Pergunte em vez de rolar** quando a declaração é ambígua ou o jogador claramente não
  sabe de algo que o personagem saberia. É melhor uma pergunta que um dado errado.

**Nunca decida pelo jogador.** Se a ação, como declarada, leva a algo que ele talvez não
queira ("você mata o pedreiro"), descreva o ponto onde ele ainda pode escolher e devolva o
turno.

## 6. Ação de mais de um personagem

Uma declaração por vez, na ordem em que chegaram. Se a mesa toda agir junto, resolva um a
um e narre o conjunto no fim, num bloco só — a mesa lê melhor assim.

Se a ação de um depender do resultado do outro (o trovador distrai *para* o ladrão furtar),
resolva a distração primeiro: ela vira **modificador** da segunda ação, e você diz o valor
e o motivo.

## O que esta skill nunca faz

- **Não rola dado por conta própria** — sempre pelas skills, sempre relatando o que saiu.
- **Não rola de novo o que já foi rolado**, inclusive reação: o `reacoes.json` manda.
- **Não inventa NPC nem lugar** que não esteja no plano ou já anotado. Precisando de gente
  nova, tire da multidão que o `npcs.md` já descreve e anote quem passou a existir.
- **Não conta ao jogador o que o personagem não pode saber** — nem no texto da mesa, nem no
  bloco de dados.
