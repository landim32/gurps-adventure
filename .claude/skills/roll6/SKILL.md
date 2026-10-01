---
name: roll6
description: >
  Mantém o roll6 — a mesa virtual onde a campanha também é jogada — em dia com o
  repositório: personagens, NPCs, tokens, mapas com o grid alinhado, plano da campanha,
  PV, Fadiga, status e posições. Explica o que é sincronizado sozinho pelo script de
  saúde e o que cada skill precisa empurrar pelo MCP depois de gravar no
  repositório. Use when the user asks "atualize o roll6", "sincronize com o MCP", "suba
  para o roll6", "crie no roll6", "ponha no mapa do roll6", ou /roll6 — e sempre que outra
  skill mandar sincronizar.
---

# roll6 — o espelho da mesa

O jogo acontece em dois lugares: no **repositório** (fonte da verdade, com o histórico e
as regras) e no **roll6**, a mesa virtual que os jogadores veem. **Toda mudança que a mesa
produz entra primeiro no repositório e, em seguida, no roll6.** Nunca o contrário: se os
dois discordarem, o repositório ganha e o roll6 é corrigido.

O acesso é o servidor MCP `roll6` (ferramentas `mcp__roll6__*`). Leia o guia uma vez por
sessão antes de mexer em mapa, peça ou turno: `get_roll6_guide`.

## O mapeamento: `campanha/roll6.json`

Liga a campanha ativa à do roll6. É o primeiro arquivo a ler.

```json
{
  "campaignId": 1,
  "mapas": { "cenarios/com-grid/estrada.json": {"mapId": 2, "modelo": 2} },
  "apelidos": { "Sir William": "Lorde William de Wallace" }
}
```

- **`mapas`**: índice local do grid em `cenarios/` → mapa do roll6. Esses índices `.json`
  são referência histórica de alinhamento — nenhuma skill os gera hoje. Só mapas
  **alinhados** (ver abaixo) entram aqui, porque a sincronização conta com coluna/linha
  iguais entre o índice e o mapa do roll6.
- **`apelidos`**: quando o nome no repositório não é o do roll6 — o `saude.md` tem "Morto
  4 (arqueiro montado)", o roll6 tem "Morto 4". Nome sem apelido é comparado como está
  (sem acento e sem caixa).
- Campanha nova, mapa novo, NPC com nome diferente: **atualize este arquivo na hora**.

## O que já é automático

| Quando | O script | Empurra |
|---|---|---|
| `campanha.py saude --pj ...` | `campanha.py` | `update_participation`: PV e Fadiga atuais; o **status** só quando o lançamento tem `--estado`/`--curar` (senão o status tático da mesa fica) |
| `campanha.py saude --npc ...` | `campanha.py` | `update_map_npc` de cada ocorrência com aquele nome, em todos os mapas da campanha: PV = total do NPC + o acumulado do `saude.md` |

**Posição e frente não têm sincronização automática** — o mapa local não é mais desenhado
por skill. Quem move peça no MCP é o `processar-turno`, no `process_turn` que fecha o
turno; para consultar, `list_map_tokens` (peças com posição e frente) e `get_map` (tamanho
da grade). Fora do fechamento de turno, mover é só por pedido explícito do usuário.

O script **nunca falha por causa do roll6**: se não conectar, imprime `roll6: ...` e
segue. **Leia essas linhas** e resolva o que elas apontarem — nome sem peça, mapa sem
ligação, peça que saiu do mapa.

**O que o script não faz sozinho, de propósito:** apagar peça, tirar NPC da campanha,
apagar qualquer coisa. Antes de `delete_map_token`/`delete_map_npc`, que não têm volta,
confirme com o usuário.

Desligar a sincronização por uma execução: `ROLL6_DESLIGADO=1`.

## O que cada skill empurra pelo MCP

Depois de gravar no repositório, a skill faz a sua parte no roll6. As ferramentas são as
do MCP; `roll6.py` cobre o que precisa de arquivo local (imagem, documento, grid).

| Skill | No repositório | No roll6 |
|---|---|---|
| `criar-personagem-gurps` (novo) | pasta em `personagens/` | `subir-imagem` do `foto.png` (1024) → `image`; `subir-imagem` do `token-hex.png` (512) → `create_token` → `tokenId`; `subir-documento` da `ficha.jpg` (+ `grimorio.jpg` se houver, vira PDF) → `sheetFile`; `create_character` com `life` = PV, `energy` = Fadiga, `move` = Deslocamento, `sheet` = `personagem.md` (+ `grimorio.md`). Se ele entra na campanha: `invite_character` + `accept_invite` |
| `criar-personagem-gurps` (edição) | ficha regerada | `get_character` → `update_character` com **todos** os campos (os omitidos são apagados, inclusive `sheetFile`); ficha nova sobe de novo |
| `criar-npc-gurps` | bloco do NPC | `create_npc` (exige token) → `add_npc_to_campaign` → `place_npc_on_map` quando ele entra em cena. **Um NPC por figura com nome** (Morto 1, Morto 3…), não um genérico com várias ocorrências |
| `token-hex-gurps`, `token-organizator` | `tokens/` ou pasta do personagem | `subir-imagem --formato png --lado 512` → `create_token` (1 hex; cavalo e afins com `upSpace`) |
| `cenario-rpg` | arte do cenário | `subir-imagem` da arte **sem grid** (lado grande o bastante: 2048+) → `create_map_model` → `roll6.py alinhar` com o índice `.json` da cena em `cenarios/` (referência histórica — nada o gera mais) → `add_map_to_campaign` → ligar em `campanha/roll6.json` |
| `campanha` (plano) | `campanha/plano/` | `create_campaign_plan`/`update_campaign_plan`: uma entrada por capítulo (README + npcs.md), imagens por `subir-imagem` e `![](roll6-image:<fileName>)`, links internos viram texto |
| `campanha` (anotar item, desvantagem, dinheiro) | `grupo.md`, `bolsa.md` | **notas da participação**: `get_participation` → `update_participation` com o `sheet` novo — só o que difere da ficha (item perdido/ganho, desvantagem adquirida, saldo), nunca cópia da ficha |
| `acao` | log + saúde, entregando o ato à `registrar-acao` | **nada por conta própria**. O que ela decide entra no ato: PV/Fadiga (o `campanha.py saude` não sincroniza mais sozinho), **status tático** — arma preparada/despreparada, caído, de joelhos, atordoado, redutor de choque, apontando, Ataque Total sem defesa, cavalo exausto, até 260 caracteres — e o que muda de posição. Vai ao roll6 quando a `processar-turno` fecha o turno. Para saber onde cada um está, **consulte** `list_map_tokens` |
| `roll`, `teste-nh`, `disputa-nh`, `atacar`, `atacar-distancia`, `iniciativa`, `reacao` | acontecimento no capítulo | **nada** — resolvem e entregam o ato. Quem escreve é a `registrar-acao` no repositório, e ao roll6 só a `processar-turno`, no fechamento do turno. Reação nunca vai |
| `processar-turno` | log, saúde e anotações | **tudo numa chamada só**: `process_turn` com PV, Fadiga, status, posições e a narração — **com a conta de cada jogada abaixo do parágrafo dela** (NH, modificadores com motivo, dado, defesa, dano, HT, críticos) —, que fecha o turno; depois as notas da participação |
| `status-atual` | só lê | nada; mas se o roll6 divergir do `saude.md`, rode `roll6.py saude --pj/--npc` para corrigir |

## Grid: alinhar o mapa do roll6 ao grid local

O roll6 tem hexágono de raio fixo **40 px** e o hex (0,0) centrado em (40, 20·√3); a
imagem de fundo é desenhada em (−imageLeft, −imageTop) com o tamanho de exibição. O índice
local de grid (`.json` em `cenarios/`, referência histórica — nada o gera hoje) tem
hexágono de altura `metro_px` com A1 em `origem`. Alinhar é
escalar a arte por `40·√3 / metro_px` e deslocar — o script faz a conta:

```bash
python .claude/skills/roll6/scripts/roll6.py alinhar \
  --indice cenarios/com-grid/estrada.json --modelo 2 [--linhas-extras 12]
```

Depois disso **coluna/linha do roll6 = coluna/linha local**: `P7` → x 15, y 6 (letras são
a coluna, A = 0, AA = 26; o número é a linha, 1 = 0). `--linhas-extras` estende o grid
além da arte, para quem fica para trás numa corrida — no índice `.json` local essa gente
sai pela borda; no roll6 ela continua no lugar certo.

Frente: aresta local → `look` do roll6: N 0, NE 1, SE 2, S 3, SW 4, NW 5.

## Linha de comando

```bash
R=.claude/skills/roll6/scripts/roll6.py
python $R estado                                   # conexão + mapeamento
python $R chamar list_campaigns '{"mine": true}'   # qualquer ferramenta, JSON cru
python $R subir-imagem personagens/x/foto.png --lado 1024        # → fileName
python $R subir-documento personagens/x/ficha.jpg personagens/x/grimorio.jpg
python $R alinhar --indice cenarios/com-grid/<slug>.json --modelo N
python $R mapa  --indice cenarios/com-grid/<slug>.json            # reempurra a ocupação
python $R saude --pj "Jah Kagadu" [--com-estado]                  # reempurra PV/Fadiga
```

Use o MCP direto para chamadas pequenas; `roll6.py` para o que leva arquivo (a imagem em
base64 não cabe numa chamada de ferramenta) e para refazer uma sincronização.

## Regras

- **Repositório primeiro, roll6 depois.** A ficha, o `saude.md` e o plano
  continuam sendo a fonte; o roll6 é o que a mesa enxerga — e é onde as posições
  acontecem.
- **A regra da ficha vale lá também**: `update_character` só quando o usuário pediu
  mudança na ficha. PV, Fadiga, status e notas de campanha vão na **participação**.
- **Nada destrutivo sem confirmação** (`delete_*`, `remove_*`, `transfer_character`,
  `reset_turn`).
- **Não crie duplicata**: antes de `create_*`, liste (`list_my_characters`,
  `list_campaign_npcs`, `list_tokens --search`).
- **Relate o que foi para o roll6** junto com o que foi gravado no repositório, com os ids
  novos — e registre ids de mapa e apelidos em `campanha/roll6.json`.
