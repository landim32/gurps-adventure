---
name: resolver-defesa
description: >
  Monta e rola a defesa ativa de quem foi acertado — Esquiva, Aparar ou Bloqueio — somando
  Reflexos em Combate, a DP da armadura da região atingida e a DP do escudo, o redutor da
  manobra do defensor, o bônus de recuar e o modificador da situação (atordoado, caído,
  escuro). Decide também o que acontece quando não há defesa ativa: a DP passiva rolada.
  Devolve ainda a RD da região e a peça de onde ela veio, que a cascata de dano precisa.
  Não rola o ataque, não calcula dano, não escreve em lugar nenhum. Use when the user asks
  "/resolver-defesa", ou quando `atacar` e `atacar-distancia` chegam no ponto de defender.
---

# Resolver defesa

A mesma defesa, dos dois lados do alcance. Antes desta folha, o corpo a corpo e a arma de
longe tinham cada um a sua cópia de ~110 linhas do mesmo cálculo — e elas já tinham
começado a divergir em silêncio: uma somava a DP do escudo em qualquer região, a outra só
onde havia armadura; uma aceitava `--recuar`, a outra não; uma avisava que a segunda defesa
da Defesa Total precisa ser diferente, a outra fazia a segunda tentativa sem dizer por quê.
Uma regra, uma casa.

```
python .claude/skills/resolver-defesa/scripts/resolver_defesa.py \
  --alvo "Morto 3" --defesa aparar --defesa-valor 9 \
  --local '{"nome":"Tronco","armadura":"tronco"}' --tipo corte \
  --md '{"nome":"Normal","defesas":1,"mod":0}'
```

## O número, na ordem em que se compõe

| Termo | De onde vem | Nota |
|---|---|---|
| base da defesa | `--defesa-valor`, ou a flag do chamador, ou `defesas_ativas` da ficha | a fonte vai escrita na linha (`da ficha` / `informada pelo Mestre`) |
| +1 | Reflexos em Combate, lida pela folha `contexto` | só +1: defesa ativa não é teste de reação |
| +DP da armadura da região | `protecao(ficha, região, perfurante)` | região sem armadura não soma a da loriga do tronco |
| +DP do escudo | `escudo_dp(ficha)` | corpo a corpo: só vale onde a armadura vale. `--escudo-sempre` é o regime do projétil |
| +3 | `--recuar` | MB, cap. 14 |
| mod da manobra | `md` (Defesa Total −2, Ataque Total sem defesa…) | o nome da manobra sai na linha |
| `--mod` | o que a mesa arbitrou (atordoado, caído, escuro) | sempre com `--mod-motivo` |

## A jogada

`3d ≤ 4` **defende sempre**, e o atacante vai à Tabela de Erros Críticos. `3d ≥ 17` é falha
desastrosa na defesa. No meio, defende quem tira menos que o número composto. A Defesa Total
dá duas tentativas, e a segunda precisa ser uma defesa **diferente** — a folha lembra isso,
não decide por você.

Sem defesa ativa, quem protege é a DP passiva: `DP total` rolada em 3d, com 3 ou 4 valendo
de qualquer jeito.

## O que sai e o que volta

Devolve `saida` (terminal), `mec` (as linhas do bloco da mesa, na ordem) e `resultado`:

```json
{"defendeu": true, "total_defesa": 12, "rd_local": 2, "rd_total": 4, "peca": "Loriga de couro",
 "dp_local": 2, "dp_escudo": 3, "nome_escudo": "Escudo médio", "dp_total_passivo": 5,
 "ht_alvo": 12, "alvo": "Morto 3", "defesa_final": "aparar"}
```

`defendeu` encerra o golpe ali — quem chamou imprime "sem dano" e para. Os campos de RD
vão direto para a `causar-dano`, que não calcula proteção.

## Opções que são decisão de mesa, não bug

| Flag | Quem usa | Por quê |
|---|---|---|
| `--escudo-sempre` | `atacar-distancia` | contra projétil a mesa sempre somou a DP do escudo, blindada a região ou não |
| `--dp-informado-zera-escudo` | `atacar-distancia` | quem informa a DP por cima está descrevendo o total, não pedindo para somar o escudo de novo |
| `--projetil` | as duas, no texto | ajusta a redação ("vale contra projétil") e o lembrete do crítico |

Essas três não são unanimidade entre os dois lados — são o que a mesa ainda não unificou.
Se um dia você decidir um regime só, é aqui que se muda, uma vez.

## O que esta folha nunca faz

Não rola o ataque, não avalia dano (é a `causar-dano`), não decide queda nem atordoamento
(`arbitrar-ferimento`), não escolhe a defesa pelo NPC, e não escreve em lugar nenhum.

## Dependências

`roll` (o dado), `contexto` (ler vantagem da ficha). Os dados de região e de manobra entram
no payload, resolvidos por quem chamou.
