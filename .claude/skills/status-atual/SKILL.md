---
name: status-atual
description: >
  Mostra como está cada personagem agora: dinheiro na bolsa, pontos de vida, Fadiga,
  membro incapacitado, ferimento que ficou e o que mais estiver anotado na campanha —
  tudo num bloco só, pronto para colar no WhatsApp. Lê o que a mesa produziu
  (campanha/bolsa.md, campanha/saude.md, campanha/mundo.md) e as fichas; não rola nada,
  não escreve nada e não toca na ficha de ninguém.
  Use when the user asks "status atual", "como está o grupo", "quanto cada um tem",
  "quem está ferido", "PV de todo mundo", "resumo do grupo", ou /status-atual.
---

# Status de todo mundo, num bloco só

Meia hora de mesa e ninguém lembra mais quem levou dano, quem gastou moeda e quem está
com o braço na tipoia. Esta skill junta isso e devolve **um texto pronto para o grupo**.

```
python .claude/skills/status-atual/scripts/status_atual.py
```

Sai assim:

```
*STATUS DO GRUPO* — Tormento Vil
_1. Encontro na Taberna · Taberna do porto, Wallace (Caithness)_

*Negrum Carneiriums* (Bruno)
PV 11/12 · Fadiga 15/15 · $300
_Procurado por assassinato em Wallace_
```

**Repasse o bloco num bloco de código**, para o usuário copiar de uma vez.

## De onde vem cada número

| No bloco | Fonte | Quem mantém |
|---|---|---|
| PV e Fadiga | `campanha/saude.md`, comparado com o máximo da ficha | skill `campanha` (`saude`) |
| Dinheiro | `campanha/bolsa.md` | skill `campanha` (`bolsa`) |
| Ferimento, membro incapacitado, nocaute, morte | os `--estado` do `saude.md` | skill `campanha` (`saude`) |
| Nome, jogador, máximos, defesas | `personagens/<slug>/personagem.json` | skill `criar-personagem-gurps` |
| Capítulo e local | `campanha/README.md` e o plano do capítulo | skill `campanha` |

**Nada é inventado e nada é gravado.** Se um número parecer errado, o conserto é no
arquivo de origem, não aqui — e é a skill `campanha` que escreve nele.

Personagem que ainda não tem lançamento nenhum aparece **inteiro**, com os máximos da
ficha e sem linha de dinheiro. É o esperado no começo da campanha.

## As opções

| Opção | Para quê |
|---|---|
| `--npcs` | Acrescenta uma seção com os **NPCs que têm estado anotado** — o pedreiro de braço quebrado, o taberneiro morto. Não vai para os jogadores por padrão |
| `--combate` | Acrescenta Deslocamento, Esquiva, Aparar e Bloqueio de cada um. Use quando a mesa está em luta |
| `--nota "Nome: texto"` | Uma condição que **não é número**, lida do `mundo.md`. Repita quantas vezes precisar |

### O que o script não sabe sozinho

`saude.md` guarda o corpo; `bolsa.md` guarda o dinheiro. **Tudo o mais que pesa sobre um
personagem — estar sendo procurado, dever um favor, carregar dinheiro que é de outro,
estar jurado de morte — mora nas anotações do `mundo.md`, em texto livre**, e o script não
tenta adivinhar o que é relevante.

Por isso, antes de entregar o bloco: **leia `campanha/mundo.md`** e passe o que a mesa
precisa lembrar como `--nota`:

```
python .claude/skills/status-atual/scripts/status_atual.py \
  --nota "Negrum: procurado por assassinato em Wallace" \
  --nota "Jah: com $39 da banca, que são de terceiros"
```

Uma linha por personagem, curta. O nome pode ser parcial (`Negrum`, `Jah`) — casa com o
nome completo da ficha.

## O que fica de fora do bloco

O texto vai **para os jogadores**, então valem as proibições da skill `narrar`:

- **Nada que só o Mestre sabe.** Um NPC que planeja trair o grupo não entra como nota.
- **Nada de NPC** sem `--npcs`, e mesmo com a opção: pense se a mesa deveria saber que o
  taberneiro está morto antes de alguém ir conferir.
- **Nada de ficha alheia**: perícia, ponto gasto, custo de vantagem. O bloco é estado de
  jogo, não planilha.

Fora do bloco, uma linha ou duas ao Mestre: quem está perto de cair, quem tem dinheiro de
terceiros na mão, que ferimento vai atrapalhar a próxima cena.

## Quando usar

- **Abrindo a sessão**, para a mesa lembrar onde parou.
- **Depois de um combate**, junto com os lançamentos de `saude`.
- **Quando um jogador pergunta** "quanto eu tenho mesmo?" — é mais rápido que abrir ficha.
- **Antes de uma compra ou de uma aposta**, para ninguém gastar o que não tem.

Se algum número estiver errado no bloco, o problema é que a mesa aconteceu e ninguém
lançou: rode `campanha.py saude` ou `campanha.py bolsa` e gere de novo.
