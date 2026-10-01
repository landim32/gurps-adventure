---
name: arbitrar-ferimento
description: >
  Decide o que o ferimento faz com quem o recebeu, depois da causar-dano: o redutor por
  ferimento do próximo turno (e a Hipoalgia que o anula), o teste de HT para não cair
  quando o golpe passou de metade da HT, o atordoamento que vem com a queda ou com o golpe
  fulminante, o teste de HT contra nocaute na cabeça ou com contundente nos órgãos vitais,
  e pelo crânio exposto a perda acima de HT/2 (nocaute) e HT/3 (atordoamento). Devolve o
  estado tático pronto — caiu, atordoado, nocauteado, redutor — para ir no ato da
  registrar-acao. Não rola ataque, não resolve defesa, não calcula dano, não escreve em
  lugar nenhum. Use when the user asks "/arbitrar-ferimento", ou quando uma atacante
  terminou de contar o dano.
---

# Arbitrar ferimento

O número de PV perdidos não é o fim do golpe. Aqui mora a pergunta que vem depois: **o que
esse ferimento faz com quem vai agir no próximo turno.** Estava copiada nas duas atacantes;
agora é uma folha, e uma decisão sobre corte na cabeça vale igual para uma espada e para um
virote.

```
python .claude/skills/arbitrar-ferimento/scripts/arbitrar_ferimento.py \
  --alvo "Morto 3" --ferimento 7 --ht-alvo 12 --chave cabeca --tipo cont
```

## A ordem, e o que cada teste decide

| # | Teste | Quando | Consequência |
|---|---|---|---|
| 1 | redutor por ferimento | sempre que houver dano | o próximo turno age com **-ferimento**; **Hipoalgia** anula |
| 2 | HT para não cair | `ferimento > HT/2` no mesmo golpe | **CAIU**; e, caindo ou não, **ATORDOADO** |
| 3 | atordoamento do fulminante | o efeito da tabela disse `atordoa` | **-4 nas defesas ativas** |
| 4 | HT contra nocaute | cabeça, crânio exposto, ou contundente nos vitais | **NOCAUTEADO** |
| 5 | pelo crânio exposto | perda acima de HT/2 (nocaute) ou de HT/3 (atordoamento) | direto, sem teste |

Recuperação do atordoamento é no início de cada turno: teste de HT, e enquanto durar os
**-4** ficam nas defesas ativas. A folha registra que ele existe; quem acompanha turno a
turno é a mesa (`--alvo-manobra atordoado` na jogada seguinte fecha o ciclo).

## O que volta

```json
{"hipoalgia": false, "redutor_ferimento": 7, "caiu": true,
 "atordoado": true, "nocauteado": false}
```

É isto que vai no `status tático` do ato entregue à `registrar-acao` — e é por isso que a
folha devolve estado, não só texto. `saida` é para o terminal do Mestre, `mec` para o bloco
da mesa, na ordem em que os testes aconteceram.

## Palavra de quem atira

O lado do projétil diz "tiro", não "golpe", e omite uma frase sobre NH cheio na Hipoalgia.
Isso é `--projetil`, não regra: a folha preserva a redação de cada atacante para que a
extração não mudasse uma linha do que a mesa já lia. Um regime só de redação, se você
quiser, é aqui.

## O que esta folha nunca faz

Não rola ataque, não resolve defesa (`resolver-defesa`), não calcula dano (`causar-dano`),
não escolhe alvo, não decide morte — decapitação e sufocação são da `causar-dano`, e
anunciar que alguém **morreu** é decisão do Mestre, não de script. Não escreve em lugar
nenhum.

## Dependências

`roll` (os dois testes de HT), `contexto` (ler Hipoalgia na ficha). Sem HT informada, a
folha diz que não há como testar queda, atordoamento nem tetos — e manda buscar o número,
em vez de rolar às cegas.
