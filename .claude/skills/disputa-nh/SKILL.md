---
name: disputa-nh
description: >
  Resolve uma Disputa de Habilidades de GURPS 3ª Edição entre dois lados — personagem
  contra NPC, personagem contra personagem, ou contra um NPC virtual cujo NH o Mestre
  informa. Acha o NH de cada lado na ficha ou no livro, rola os dois, compara as margens e
  entrega o resultado pronto para colar no WhatsApp. Use when the user asks "disputa de
  Furtividade contra a Audição do guarda", "quem ganha o braço-de-ferro", "ele consegue
  passar sem ser visto", "disputa de ST", ou /disputa-nh.
---

# Disputa de Habilidades

Quando o teste não é contra a dificuldade da situação, mas **contra alguém**. Os dois lados
rolam; compara-se a margem.

```
python .claude/skills/disputa-nh/scripts/disputa_nh.py \
  --a "Comam" --a-pericia "Furtividade" \
  --b "Guarda do portão" --b-nh 12 --b-oque "Audição"
```

```
*Comam Obabaroy* — Furtividade (sem treino), precisa tirar 9 ou menos
3d: 5 + 4 + 5 = *14* → _falhou por 5_

*Guarda do portão* — Audição, precisa tirar 12 ou menos
3d: 1 + 1 + 5 = *7* → _passou por 5_

*Guarda do portão vence.*
```

## A regra (MB, cap. 12)

**Os dois fazem seu teste, com todos os modificadores que couberem.** Depois:

| Situação | Quem ganha |
|---|---|
| Um passa, o outro falha | Quem passou |
| **Os dois passam** | Quem passou pela **maior margem** |
| **Os dois falham** | Quem falhou pela **menor** |
| **Margem igual** | **Ninguém venceu** — os dois agarraram a arma ao mesmo tempo |

O script compara sempre a margem, que resolve os quatro casos de uma vez: sucesso tem
margem positiva, falha tem negativa, e a maior ganha.

## Os dois tipos

**`--tipo rapida`** (padrão) — um lance decide. É o caso normal: agarrar a arma antes do
outro, passar sem ser ouvido, dois atiradores mirando a mosca.

**`--tipo normal`** — dura vários turnos: braço-de-ferro, corrida a pé, dois eruditos
procurando a mesma nota numa biblioteca. Aqui **só decide quando um passa e o outro falha**;
os dois passando ou os dois falhando significa que **nada mudou de posição** e se tenta de
novo. O script repete sozinho e diz em quantas rodadas foi.

Quanto tempo vale cada rodada é decisão sua: em combate, um segundo; na biblioteca, pode ser
um dia.

**O encurtamento é só da normal.** Se os dois NH passam de 14, uma disputa normal pode durar
para sempre — então o livro manda baixar o maior para 14 e tirar a mesma diferença do outro
(17 × 17 vira 14 × 14; 19 × 16 vira 14 × 11). O script faz isso sozinho na normal e avisa;
`--sem-encurtar` desliga. **Na rápida não se encurta** — lá um lance decide de qualquer
jeito.

## Montando os dois lados

Cada lado tem o mesmo conjunto de opções, com prefixo `--a-` ou `--b-`:

| Opção | Para quê |
|---|---|
| `--a` | Nome de quem disputa |
| `--a-pericia` | Perícia ou mágica — busca na ficha |
| `--a-atributo ST\|DX\|IQ\|HT` | Disputa de atributo puro (braço-de-ferro é **ST**) |
| `--a-nh` + `--a-oque` | **NPC virtual**: o Mestre diz o NH e o nome da habilidade |
| `--a-mod` | Bônus ou redutor da situação, só daquele lado |
| `--a-sorte` | Vantagem Sorte: aquele lado rola 3 vezes e fica com o melhor |

O NH sai da ficha quando o lado é um personagem do repositório (nome parcial resolve:
`Comam`, `Kaelric`). **Não tendo a perícia**, o script busca o nível pré-definido no
`06-pericias.md` e avisa em letra grande — é a mesma máquina da `teste-nh`, não uma cópia.

**NPC vai por `--b-nh`**, e o número sai do `npcs.md` do capítulo ou da sua cabeça. É para
isso que a opção existe: o guarda anônimo do portão não precisa de ficha para ter Audição 12.

Os modificadores são **por lado**, e quase nunca são iguais nos dois: quem se esconde leva o
redutor da Carga e do terreno; quem escuta leva o do barulho da taberna.

## Quem disputa contra quem

Vale qualquer combinação — **PJ × NPC**, **PJ × PJ** (dois personagens brigando pela mesma
adaga), **NPC × NPC** (dois NPCs correndo, com o grupo assistindo). O script não distingue
lado de jogador e lado de Mestre; quem decide o que significa é você.

A disputa também **não precisa ser da mesma perícia dos dois lados** — quase nunca é.
Furtividade contra Audição, Manha contra Percepção, Lábia contra Vontade, ST contra ST.

## Mostrar

O bloco **PARA O WHATSAPP** sai sempre, com os dois lados e o veredito, em formatação de
WhatsApp (`*negrito*`, `_itálico_`). **Repasse num bloco de código** para o usuário copiar
de uma vez. Mostrar ou não à mesa é decisão do Mestre.

Numa disputa normal, o bloco traz **a rodada que decidiu** e diz quantas foram — a mesa não
precisa das dez rolagens do meio, mas precisa saber que a queda de braço durou.

Fora do bloco, uma linha ao Mestre: o que a vitória mudou na cena.

## Nunca invente o dado

Quem sorteia é a skill `roll`, e esta chama aquela. **Relate o que saiu**, número por
número — dos dois lados, inclusive do que perdeu. Não rode de novo porque o NPC ganhou.

## Registrar

`--gravar` anota uma linha no capítulo atual pela `gerenciar-campanha`. Use quando a disputa
mudou o rumo — o grupo passou ou não passou pelo portão — e deixe de fora o braço-de-ferro
de taberna que não decidiu nada.
