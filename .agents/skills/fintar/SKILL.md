---
name: fintar
description: >
  Resolve uma finta pela regra de GURPS 3ª Edição (MB, cap. 14, "Avançar e Fintar"): a
  Disputa Rápida entre o NH do fintador com a arma e o NH do alvo com o escudo, a arma ou a
  DX, o que for melhor para ele. Devolve se a finta funcionou e o redutor que sai da defesa
  ativa do alvo no próximo ataque do fintador — o número que a skill `atacar` cobra com
  `--alvo-defesa-mod`. Confere a perícia na ficha (inclusive a manobra Finta de Artes
  Marciais), recusa a finta que o livro não permite, entrega o texto para o WhatsApp e
  devolve o resultado à `registrar-acao`. Use when the user asks "ele finta o guarda",
  "Negrum tenta uma finta", "avançar e fintar", "finta com o escudo", ou /fintar.
---

# Finta

**Sistema Avançado** (MB, cap. 14, pág. 105), como a `atacar`. Uma execução do script
resolve **uma finta**: a Disputa Rápida e o redutor que ela rende. O ataque que se segue é
outra execução, da skill **`atacar`**, no turno seguinte (ou no mesmo, se a manobra for
Ataque Total).

```
python .claude/skills/fintar/scripts/fintar.py \
  --fintador "Negrum" --pericia "Machado/Maça" \
  --alvo "Edric Halloway" --alvo-nh 14 --alvo-oque "Escudo"
```

## A regra, conferida no livro

*Módulo Básico*, `11-combate-avancado.md`, "Avançar e Fintar"; `10-combate-basico.md`,
"Finta"; `21-quadros-e-tabelas.md`, tabela de manobras.

| Passo | Regra |
|---|---|
| Quando se pode | Só se o fintador **poderia ter atingido** o alvo com um ataque normal ou total. Alcance, frente e visão contam |
| A manobra | **Avançar e Fintar**: 1 hex em qualquer direção, e a finta. Ou, dentro do **Ataque Total**, a opção (b): fintar e depois atacar. Não existe em combate de perto |
| A jogada | **Disputa Rápida**. O NH do fintador com a arma contra o NH do alvo **com o escudo ou a arma**; contra a **DX** dele se ele não tem nenhum dos dois ou se a DX for maior |
| Fintador errou | A finta falhou |
| Os dois passaram, margem do alvo **igual ou maior** | A finta falhou |
| Alvo falhou | A margem do fintador é subtraída da **defesa ativa** do alvo |
| Os dois passaram, fintador com margem maior | A **diferença** das margens é subtraída |
| Quanto vale | **Uma rodada**, só no **próximo ataque do fintador** (no Ataque Total com dois golpes, nos dois). **Aliados não aproveitam** |
| Armas | A finta **não** deixa a arma despreparada |
| Visão | De nada vale contra quem não vê o fintador: no escuro, por trás. O alvo que dá as costas depois **não** anula o bônus; o fintador que **perde o alvo de vista** perde |
| Estragos | Se o fintador apara depois com arma desbalanceada, deixando-a despreparada, **não ataca no turno seguinte** e a finta se perde |
| Com o escudo | Só depois de já ter **atacado com o escudo** uma vez. O NH é o de Escudo |

**Arte marcial.** `livros/gurps-artes-marciais-3ed/04-combate-manobras.md`, "Finta
(Difícil)", é a mesma finta, aperfeiçoável até **4 níveis** acima da perícia-base (pré-definido:
a perícia de combate). Quem a comprou a tem na categoria **Manobras** da ficha, uma por
arma (`Finta (Katana)`): passe `--pericia "Finta (Katana)"`.

## O fintador e o alvo

| Opção | Para quê |
|---|---|
| `--fintador` | Nome; nome parcial resolve |
| `--pericia` | Perícia da arma, ou `Finta (arma)` se a ficha a tem — o NH sai da ficha |
| `--nh` | NH na mão, para NPC sem ficha |
| `--com-escudo` | Finta com o escudo (usa **Escudo**). Só vale depois do primeiro ataque com ele |
| `--manobra` | `avancar-e-fintar` (padrão) ou `ataque-total` |
| `--mod` / `--mod-motivo "..."` | Qualquer modificador **na finta**, com o motivo que vai para a conta da mesa |
| `--impedimento "..."` | O livro não deixa fintar (`"no escuro"`, `"o alvo está de costas"`, `"fora de alcance"`). O script **recusa** e não rola |
| `--alvo` | Nome do alvo |
| `--alvo-nh` / `--alvo-oque` | NH do alvo na mão (NPC sem ficha) e o rótulo: `"Escudo"`, `"Espada curta"` |
| `--alvo-pericia` | A perícia da arma do alvo, lida na ficha. O escudo da ficha entra sozinho |
| `--sem-escudo` | O escudo do alvo **não conta**: está às costas, ou ele empunha duas mãos |
| `--alvo-mod` / `--alvo-mod-motivo` | Modificador no NH do alvo |

**Personagem do repositório é automático**: o script lê a ficha, junta DX, a arma e o
escudo, e usa **o maior** dos três — é o que o livro manda (escudo ou arma, DX se ela for
maior). Lista os candidatos no terminal. **NPC não tem ficha em JSON**: leia o `npcs.md` do
capítulo e passe `--alvo-nh` com o rótulo.

## O que sai

- **O resultado mecânico**, em texto corrido, e o bloco **PARA O WHATSAPP**: o NH da finta
  com o motivo de cada modificador, o dado e a margem, a defesa do alvo montada e rolada, e
  a conclusão (`*Finta funcionou:* defesa ativa de X *-3* contra o próximo ataque de Y`).
- **O comando para a `atacar`**, pronto: `--alvo-defesa-mod -N --alvo-defesa-mod-motivo
  "finta de Y, margem N"`. É assim que o redutor entra no golpe seguinte.
- **`--json`** devolve só o resultado (`funcionou`, `redutor`, `status_tatico`, `atacar`,
  `whatsapp`), para a `processar-turno` ler por subprocesso.

**O redutor é do próximo ataque de quem fintou.** Guarde-o para o turno seguinte do
fintador: ele **vai no status tático** (`Fintado por Y: -N na defesa contra o próximo ataque
dele`, ao fim do turno da finta) e **sai** quando o ataque acontece, ou ao fim do turno
seguinte do fintador.

## Críticos

O livro **não tem tabela** de sucesso decisivo nem de falha crítica para a finta. O script
**diz** quando um dos lados tirou um dos dois, **não muda o número** e deixa o efeito para a
arbitragem do Mestre — dita em voz alta. Nunca invente um efeito pior para compensar.

## O que esta skill não faz

| O quê | Onde |
|---|---|
| O ataque que cobra o redutor | skill **`atacar`** (`--alvo-defesa-mod`) |
| Alcance, frente e visão do alvo | **`calcular-alcance`** e `list_map_tokens`. O script **não confere**: se não dá para atingir, passe `--impedimento` |
| Quem age primeiro | skill **`iniciativa`** |
| Finta com arma de longo alcance | não existe: o livro só trata da arma de mão |
| Um teste solto | **`teste-nh`**; disputas que não são finta, **`disputa-nh`** |

## Nunca invente o dado

Quem sorteia é a skill `roll`, e esta chama aquela. **Relate o que saiu**, dos dois lados.
Não role de novo porque a finta falhou. Se a mesa quiser um resultado escolhido para testar
uma regra, **diga que foi escolhido**.

## Esta skill não narra

Entregue o resultado mecânico e pare. A prosa é da skill **`narrar`**, e o bloco da mesa sai
**uma vez por rodada** (`CLAUDE.md`, *O bloco do WhatsApp sai uma vez por rodada*) — guarde
as linhas desta skill e junte-as com as do `atacar` que vier depois, **com a conta abaixo do
parágrafo**.

## Mostrar e gravar

`--gravar` entrega a finta à **`registrar-acao`**, que a grava no capítulo atual. Numa luta
longa, não grave finta a finta: grave a que decidiu o golpe seguinte. O redutor é estado
tático, não corpo: **não vai para `saude.md`**.

## roll6 — esta skill não grava lá

Esta skill **resolve e entrega o resultado à `registrar-acao`**; ela **não grava nada no
roll6** — nem PV, nem Fadiga, nem status, nem posição, nem entrada de turno —, a menos que o
usuário peça isso diretamente. Quem altera o roll6 é a **`processar-turno`**, ao fechar o
turno, e o `status_tatico` desta skill vai no `status` do alvo (até 260 caracteres).

## Dependências

`atacar` (ficha, NH, dado, veredito e a entrega ao registrador, como a `atacar-distancia`),
e por ela `teste-nh`, `contexto` e `roll`. Sem folha de cálculo própria: a finta compara
dois NH e devolve um número.
