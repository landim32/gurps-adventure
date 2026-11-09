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
Uma regra, uma casa — e o regime da defesa passiva, que era a última dessas divergências,
está fechado adiante (“O regime da defesa passiva”).

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
| +DP da armadura da região | `protecao(ficha, região, perfurante)` | só a peça que cobre aquela região; sem peça nomeada para a região, soma zero |
| +DP do escudo | `escudo_dp(ficha)`, ou `--escudo-dp` | vale em qualquer região, mas só de frente e do lado do escudo — `--nao-frontal` o tira |
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

## O regime da defesa passiva — um só, dos dois lados do alcance

| Peça | Onde vale | Fonte no livro |
|---|---|---|
| **DP da armadura** | só na **região que ela cobre**. Região sem peça sobre ela não soma nada: cota de malha nenhuma protege o olho | MB, pág. 72 e 99 — a DP da armadura vai na linha da região |
| **DP do escudo** | em **qualquer região** — o escudo não é peça de vestuário regional, é o que intercepta o golpe —, mas só contra ataque que venha da **frente ou do lado do escudo**. Por trás, não conta | MB, cap. 11: “seu escudo só o protege de ataques vindos de *sua frente* ou do *lado do escudo*”. MB, cap. 10: não vale contra “ataque dissimulado”, i.e., pelas costas |

De onde a folha tira cada número:

- **armadura da região**: casa o campo `armadura` do local atingido com o item de
  `categoria: armadura` da ficha (`DP4 / RD2`, ou `DP3` sozinho) e devolve `(DP, RD, peça)`;
- **escudo**: o item com “escudo”, “broquel” ou “pavês” na ficha; se a peça não vier com DP,
  cai no campo `defesa_passiva.escudo` da própria ficha; e `--escudo-dp` informa por cima,
  para NPC sem ficha;
- `--dp-informado` troca **só a DP da armadura** — não silencia mais o escudo, como a arma
  de longe fazia;
- `--sem-escudo` tira o escudo (mão nas rédeas, escudo caído, segunda mão ocupada);
- `--nao-frontal` tira a DP do escudo, mantendo a da armadura.

O que a mesa vai ver mudar: quem apanha **de frente** passou a somar a DP do escudo também em
cabeça e olhos, como sempre somou no torso; quem apanha **por trás** deixou de somar — regra
do capítulo 11 que estava escrita nos documentos e não no código. E um golpe no olho parou de
contar a DP da cota do tronco, que era o que a versão antiga fazia quando a região não tinha
peça nomeada.

Removidas na unificação: `--escudo-sempre` e `--dp-informado-zera-escudo`. Se você quiser
regimes diferentes por lado do alcance de novo, reabra as duas opções — não um `if` solto em
um dos dois chamadores.

## O que esta folha nunca faz

Não rola o ataque, não avalia dano (é a `causar-dano`), não decide queda nem atordoamento
(`arbitrar-ferimento`), não escolhe a defesa pelo NPC, e não escreve em lugar nenhum.

## Dependências

`roll` (o dado), `contexto` (ler vantagem da ficha). Os dados de região e de manobra entram
no payload, resolvidos por quem chamou.
