---
name: iniciativa
description: >
  Resolve surpresa e iniciativa de GURPS 3ª Edição pela regra do Módulo Básico: lê as
  fichas dos envolvidos, aplica os modificadores (Reflexos em Combate, líder mais
  inteligente, Tática, grupo sem líder), rola os dados e anuncia o resultado. Entrega o
  texto pronto para colar no WhatsApp e grava no capítulo atual da campanha. Use when the
  user asks to "role iniciativa", "quem começa", "eles foram surpreendidos", "surpresa
  total", ou /iniciativa.
---

# Iniciativa e surpresa

Aplica **MB, cap. 14 — "Ataques de Surpresa e Iniciativa"** com os números das fichas de
verdade, e devolve o resultado pronto para a mesa.

## Antes de tudo: qual dos três casos é

Este é o passo que decide todo o resto, e é **julgamento do Mestre**, não do script.

| Caso | Quando | O que acontece |
|---|---|---|
| **Nenhuma** | Os dois lados se viram chegar | **Não se rola nada.** Vá para a ordem de turnos |
| **Parcial** | Ambos esperavam problema, ou cada um surpreendeu o outro | **Rola-se iniciativa**: um dado por lado |
| **Total** | Um lado não esperava nada — dormindo, ou algo que ninguém já viu | **1d de paralisia**, sem iniciativa |

**Iniciativa só existe na Surpresa Parcial.** É o erro mais comum: rolar "iniciativa" numa
emboscada total, ou rolar um dado por personagem. Nenhum dos dois é a regra.

E ela é rolada **por lado, uma vez** — não por personagem, e não por DX.

## O comando

```
python .claude/skills/iniciativa/scripts/iniciativa.py --surpresa parcial \
  --a "Personagens" --a-membros "Comam Obabaroy*, Irmão Kaelric, Jah Kagadu" \
  --b "Mortos-vivos" --b-membros "Morto-Vivo 1" --b-iq 8 --b-sem-lider
```

O **`*`** marca o líder do lado. Sem marcar ninguém, o primeiro da lista vira líder.

| Opção | Para quê |
|---|---|
| `--surpresa` | `nenhuma`, `parcial` (padrão) ou `total` |
| `--surpreendido a\|b` | Na surpresa total, que lado foi pego |
| `--a` / `--b` | Nome do lado, como aparece no texto |
| `--a-membros` / `--b-membros` | Nomes separados por vírgula; `*` no líder |
| `--a-iq` `--a-reflexos` `--a-tatica` | Para **NPC**, que não tem ficha em JSON |
| `--a-sem-lider` | Grupo sem ninguém no comando: **-2** |
| `--a-animais` | Anula o -2 acima; o livro isenta animais |
| `--gravar` | Registra o resultado no capítulo atual da campanha |

### O que vem da ficha sozinho

Membro que exista em `personagens/<slug>/personagem.json` tem lido automaticamente:
**IQ**, **Reflexos em Combate** e o NH de **Tática**. O script imprime o que leu de cada
um, para você conferir antes de acreditar no resultado.

**NPC não tem ficha em JSON** — a dele está em prosa no `npcs.md` do capítulo. Leia lá e
passe `--b-iq`, `--b-reflexos`, `--b-tatica` conforme o caso. Quem não recebe flag entra
sem modificador, e o script avisa na tela que aquele membro não tinha ficha.

## Os modificadores, e de onde saem

Todos do MB, cap. 14. O script aplica e **mostra a conta**:

| Modificador | Regra |
|---|---|
| **+2** | O **líder** tem Reflexos em Combate |
| **+1** | Alguém **do grupo** tem Reflexos em Combate — **não cumulativo** com o +2 |
| **+1** | Líder **mais inteligente** que o líder do outro lado |
| **+1 / +2** | Perícia tática: +1, ou **+2 se NH ≥ 20** |
| **-2** | Grupo **sem líder** — não se aplica a animais |

O GM pode somar o que achar justo (um lado mais alerta, por exemplo). Nesse caso, some
à mão e diga por quê — o script não inventa modificador que não está no livro.

## O que o resultado significa

**Parcial.** O lado de maior total ganha e age normalmente. O outro fica **mentalmente
atordoado**: teste de **IQ** no início de cada turno, com **+1 acumulativo a partir do
segundo turno**. **Empate: ninguém foi surpreendido.**

**Total.** O lado pego fica **paralisado por 1d segundos**. Quem tem **Reflexos em Combate
nunca fica paralisado**. Passada a paralisia, teste de **IQ** por turno (**+6** com
Reflexos); sucesso vale **pelo resto do combate**. Aqui **não há** o +1 acumulativo — ele é
exclusivo da Parcial. Se a mesa travar de vez, o Mestre pode conceder; é arbitragem, e
convém dizer à mesa que está concedendo.

**Atordoado não tem defesa ativa.** É a consequência que mais pesa, e a que mais se esquece.

## Nunca invente o dado

O script rola — pela skill **`roll`**, que é quem sorteia dado neste repositório. **Relate
o que ele imprimiu**, número por número. Não escreva um resultado sem ter rodado o comando,
não rode de novo porque o primeiro saiu ruim, e não arredonde a favor de ninguém.

Rolagem avulsa no meio da cena (dano, um teste qualquer) vai direto pela `roll`:
`python .claude/skills/roll/scripts/roll.py 2d-1`.

Se o usuário quiser um resultado específico para testar, ele pede — e aí diga na resposta
que foi escolhido, não rolado.

## Mostrar e gravar

O script já imprime um bloco **PARA O WHATSAPP** com o texto pronto, em formatação de
WhatsApp (`*negrito*`, `_itálico_`). **Repasse esse bloco num bloco de código** para o
usuário copiar de uma vez.

Se quiser mais cor, reescreva o texto — mas **mantendo todos os números** que o script
imprimiu. A skill `narrar` tem as regras de estilo, e valem aqui: nada de ficha, nada de
nome de mecânica, e o que só o Mestre sabe fica com o Mestre.

`--gravar` registra uma linha no capítulo atual pela `gerenciar-campanha`, como um
acontecimento. Use sempre que a rolagem valeu de verdade; deixe de fora quando for teste.

Fora do bloco, cabe uma linha ao Mestre: quem age primeiro, quem está atordoado e o que
isso muda na ordem de turnos.

## Ordem de turnos é outra coisa

Terminada a surpresa, quem age antes de quem **não** é decidido por iniciativa. É o
**Modo Realista** do MB, cap. 13: ordem fixa por **maior Deslocamento**, empate pela
**Velocidade Básica**, empate ainda nos dados — anotada uma vez no campo *Sequência* da
ficha e válida para o combate inteiro.

Essa ordem não muda de rodada em rodada, e esta skill não a calcula.
