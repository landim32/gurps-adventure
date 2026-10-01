---
name: registrar-acao
description: >
  Única skill autorizada a escrever o que uma ação resolvida mudou no mundo: o
  acontecimento do capítulo, as anotações de NPC, do grupo e do lugar, o dinheiro na
  bolsa, o corpo em saúde, o arquivo no roll6 e a narração no log da mesa. Recebe o
  "ato resolvido" em JSON de qualquer skill de resolução (acao, atacar, atacar-distancia,
  disputa-nh, arbitrar-ferimento, processar-turno), confere o que veio incompleto, e
  aplica. Nenhuma outra skill toca arquivo depois de rolar dado. Use when the user asks
  "/registrar-acao", ou quando uma ação foi resolvida e precisa ficar registrada.
---

# Registrar o que a ação mudou

Uma jogada resolvida gera quatro tipos de consequência, e elas costumam ser esquecidas na
ordem errada. Esta skill é o único ponto por onde alguma delas vira arquivo.

**Regra de casa, dura:** quem decide regra e quem rola dado **não escreve**. `acao`,
`atacar`, `atacar-distancia`, `teste-nh`, `disputa-nh`, `reacao`, `iniciativa`,
`causar-dano`, `calcular-alcance`, `arbitrar-ferimento` e `roll` devolvem resultado. Esta
skill recebe o resultado e grava. Foi assim que se evitou o turno em que oito personagens
narraram oito vezes e gravaram oito `process_turn`.

## Como chamar

A skill que resolveu monta o **ato resolvido** em JSON e passa para cá — por arquivo ou
stdin:

```
python .claude/skills/registrar-acao/scripts/registrar_acao.py --ato .qwen/tmp/ato.json
```

```
python .claude/skills/acao/scripts/acao.py ... --json | python .claude/skills/registrar-acao/scripts/registrar_acao.py --stdin
```

Sem `--aplicar`? Está aplicado: gravar é o trabalho desta skill. `--dry-run` mostra os
comandos sem tocar em nada, e é o que se usa quando o Mestre quer ver a conta antes.

## O contrato do ato

```json
{
  "quem":      { "tipo": "pj", "nome": "Jah Kagadu" },
  "capitulo":  1,
  "declaracao": "vou aproveitar a comoção e furtar a bolsa do Giles",
  "resumo":    "Jah furtou a bolsa de Giles na comoção: Punga 13-2 contra Percepção 10, passou por 4.",
  "jogadas":   [ { "titulo": "Punga", "linha": "Punga 13 -2 (mesa) = 11, 3d [4,3,2] = 9, sucesso por 2" } ],
  "anotacoes": [
    { "tipo": "npc",   "nome": "Giles Mão-de-Prata", "tag": "item", "texto": "Perdeu a bolsa de $300." },
    { "tipo": "pj",    "nome": "Jah Kagadu",         "tag": "item", "texto": "Está com a bolsa de $300." },
    { "tipo": "npc",   "nome": "Giles Mão-de-Prata", "tag": "relação", "texto": "Passou a desconfiar do forasteiro." }
  ],
  "dinheiro":  [
    { "tipo": "pj",  "nome": "Jah Kagadu",         "valor":  300, "motivo": "Bolsa furtada de Giles (cap. 01)" },
    { "tipo": "npc", "nome": "Giles Mão-de-Prata", "valor": -300, "motivo": "Furtada por Jah Kagadu" }
  ],
  "corpo":     [
    { "tipo": "pj", "nome": "Negrum Carneiriums", "pv": -3, "fadiga": -1,
      "estado": null, "motivo": "Machadada do orc (cap. 04)" }
  ],
  "narracao":  { "texto": "*Rodada 4 — o salão em chamas* …" },
  "roll6":     {
    "participations": [ { "campanhaCharacterId": 7, "characterStatus": "Montante pronto em Q30." } ],
    "npcs":           [ { "mapNpcId": 3, "currentLife": 8, "characterStatus": "Caído, sem escudo." } ],
    "turno":          null
  }
}
```

| Campo | Vai para | Obrigatório? |
|---|---|---|
| `resumo` | `campanha.py acontecimento --texto` — o log do capítulo | sim, sempre |
| `jogadas[].linha` | o bloco da mesa, junto da narração | só o que rolou dado |
| `anotacoes[]` | `campanha.py anotar` em `npcs.md`, `grupo.md` ou `lugares.md` | o que mudou de estado |
| `dinheiro[]` | `campanha.py bolsa` | tudo que saiu ou entrou de uma bolsa |
| `corpo[]` | `campanha.py saude` | o que **sobrevive à cena** |
| `narracao` | `campanha.py acontecimento --texto "[narração] …"` — narração **não** é `anotar`, que exige um sujeito, nem flag `--narracao`, que o script não tem | quando a entrada foi uma cena ou rodada |
| `reacoes[]` | `campanha/<cap>/reacoes.json`, com fusão por `(pj, npc)` — a rolagem mais nova substitui a anterior | quando a cena rolou reação nova |
| `capitulo` | vira `--evento` em `acontecimento` e `anotar`; ausente, o script usa o capítulo atual | só quando não é o capítulo atual |
| `roll6` | as chamadas MCP que **o Mestre executa depois** | em turno de mesa virtual |

As flags acima são as que `campanha.py` desta versão aceita. `--tempo`, `--ponto` e
`--narracao`, que aparecem em documentação mais antiga, **não existem** no `argparse`:
tentar usá-los faz o comando morrer. Se precisar de hora, ela vai dentro do texto.

## O que esta skill faz com o que recebeu

1. **Confere os dois lados.** Dinheiro que um ganhou o outro perdeu; item que um levou ficou
   faltando em alguém; PV que caiu num alvo de ataque subiu no outro. Metade disso é o que
   gera contradição de capítulo. Quando faltar um lado, **complete a linha e avise na saída**
   — não pergunte no meio, o Mestre está em cena. Exceção honesta: dádiva e compra têm dois
   lados explícitos no JSON; furto sem o lado de quem perdeu é erro de quem montou o ato.
2. **Escreve na ordem**: acontecimento → anotações → bolsa → saúde. A ordem importa porque
   as três últimas reescrevem tabelas geradas.
3. **Monta o bloco da mesa** com o `resumo`, as `jogadas[].linha` e a `narracao`, no formato
   do WhatsApp (`*negrito*`, `_itálico_`), com `> ` na frente das linhas de conta. Reação e
   rolagem secreta ficam **fora** do bloco, por definição.
4. **Devolve o plano do roll6** em texto, já com o nome de cada chamada MCP, os argumentos e
   o aviso do que precisa ser lido antes (`get_participation` para devolver o `sheet` sem
   alterar). O Python daqui não fala com o roll6; quem executa é o Mestre, na mesma resposta.
   Dentro de um turno do roll6, **um único `process_turn`** fecha tudo: se vier
   `roll6.turno`, esta skill inibe as escritas por peça e entrega só o fechamento.
5. **Diz o que não registrou**, e por quê. Jogada que não sobrevive à cena (Fadiga que volta
   no mesmo turno, arranhão que sara em dez minutos) não vai para saúde. Dizer isso em voz
   alta é melhor que silêncio.

## O que esta skill nunca faz

- **Não rola dado, não decide regra, não escolhe perícia.** Ela recebe número pronto.
- **Não mexe em ficha de personagem.** `personagem.json`, `personagem.md` e `ficha.jpg` só
  mudam quando o usuário pede, e aí é a skill `criar-personagem-gurps` que edita.
- **Não inventa acontecimento**: se o `resumo` que veio não fecha com as `jogadas`, ela
  devolve o erro para quem montou o ato em vez de consertar prosa.
- **Não leva reação para o roll6, nem para o bloco da mesa.** O `reacoes.json` que ela
  escreve é cache secreto do Mestre — é o único arquivo que ela mantém fora das tabelas do
  `campanha.py`, e é por decisão da mesa. Sem capítulo atual, **recusa** escrever: o cache
  antigo caía em `campanha/reacoes.json`, fora de qualquer capítulo, e lá ninguém mais lia.

## Dependências

`campanha` (toda a escrita em `campanha/`), `roll6` (só o plano de chamadas), `narrar` (que
produz o texto que ela arquiva). Nenhuma folha de cálculo é chamada daqui.
