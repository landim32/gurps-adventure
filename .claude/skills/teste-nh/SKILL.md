---
name: teste-nh
description: >
  Faz um teste de habilidade de GURPS 3ª Edição para um personagem ou NPC: acha o NH na
  ficha (ou o nível pré-definido no livro, quando ele não tem a perícia), aplica os bônus e
  redutores pedidos, rola 3d pela skill roll e diz o resultado com sucesso decisivo e falha
  crítica. Use when the user asks "teste Furtividade do Comam com -3", "role um teste de
  DX", "ele consegue?", "teste de Vontade", "teste de Visão", ou /teste-nh.
---

# Teste de habilidade

**3d contra o NH efetivo. Passa quem tira igual ou menos.** É o teste mais comum do
sistema, e o inverso da reação — aqui número baixo é bom.

```
python .claude/skills/teste-nh/scripts/teste_nh.py --quem "Comam" --pericia "Furtividade" --mod -3
```

```
Comam Obabaroy — Furtividade (sem treino)
  Modificadores do livro: menos seu nível de Carga; -5 para se esconder em uma área sem
  “esconderijos” naturais; -5 para se mover silenciosamente se estiver correndo...
  NH 9 - 3 = **6**
  3d [6, 1, 1] = 8

Falha, tirou 8 com um NH de 6.  (margem -2)

Comam Obabaroy NÃO tem Furtividade (Física/Média). Usando o pré-definido **DX-5** = 9.
```

## De onde sai o NH

Três caminhos, nesta ordem:

1. **Da ficha**, quando o personagem tem a perícia — `personagens/<slug>/personagem.json`.
   Nome parcial resolve: `Comam` acha `comam-obabaroy`, `Kaelric` acha `irmao-kaelric`.
2. **Do livro**, quando ele **não** tem. O script busca a entrada em
   `livros/gurps-mb-3ed/06-pericias.md`, lê a linha `**Pré-definido:**`, escolhe a melhor
   opção entre os atributos do personagem e **avisa em letra grande** que foi sem treino.
   O atributo conta **no máximo 20** nesse cálculo. Perícia sem pré-definido não pode ser
   tentada — o script recusa e diz por quê.
3. **Na mão**, para NPC: `--nh 12 --oque "Briga"`. NPC não tem JSON; a ficha dele está em
   prosa no `npcs.md` do capítulo — **leia lá antes** de inventar um número.

O script também imprime a linha **Modificadores** da entrada do livro, quando existe. Leia:
é ali que estão os redutores que a mesa esquece (Carga na Furtividade, escuridão na Visão).

| Opção | Para quê |
|---|---|
| `--pericia` | Nome da perícia ou mágica |
| `--atributo ST\|DX\|IQ\|HT` | Teste de atributo puro |
| `--vontade` | Teste de Vontade: IQ ± Força de Vontade / Vontade Fraca |
| `--sentido visao\|audicao\|olfato` | IQ + Prontidão + sentido aguçado |
| `--nh` / `--oque` | NPC sem ficha |
| `--mod` | O bônus ou redutor da situação |
| `--tentativa N` | 2ª tentativa = -1, 3ª = -2… |
| `--sorte` | Vantagem Sorte: rola 3 vezes e fica com o melhor |
| `--defesa` | É defesa ativa (vale mesmo com NH efetivo ≤ 3) |
| `--gravar` | Registra no capítulo atual da campanha |

## Sucesso decisivo e falha crítica

O script já classifica, mas saiba o que ele está aplicando (MB, cap. 12):

| Resultado | É |
|---|---|
| **3 ou 4** | Sucesso decisivo, sempre |
| **5** | Sucesso decisivo **se o NH efetivo for 15+** |
| **6** | Sucesso decisivo **se o NH efetivo for 16+** |
| **17** | Falha crítica se o NH efetivo for **menor que 16**; falha comum se for 16+ |
| **18** | Falha crítica, sempre |
| **10 ou mais acima do NH efetivo** | Falha crítica (tirar 16 com NH 6, por exemplo) |

Num **ataque**, sucesso decisivo é **Golpe Fulminante** e falha crítica é **Erro Crítico** —
os dois têm tabela própria (MB, pág. 202), não são arbitrados. Fora de combate, quem decide
a consequência é o Mestre: quanto melhor o resultado, maior o prêmio; quanto pior, pior.

## Os modificadores

**O NH da ficha já é final.** Ele foi calculado na criação com os bônus permanentes
embutidos (Voz, Talento Musical, Aptidão Mágica). **Não some de novo** — é o erro mais fácil
de cometer aqui.

Some só o que é **da situação**:

| Vem de | Exemplo |
|---|---|
| A cena | escuridão parcial, correndo em vez de andando, alvo pequeno |
| A linha *Modificadores* da perícia | menos o nível de Carga na Furtividade |
| Vantagem de efeito situacional | **Empatia com Animais +4** em perícias com animais; **Prontidão** nos sentidos |
| Equipamento | ferramenta certa ou improvisada |
| Tentativa repetida | -1 na segunda, -2 na terceira (`--tentativa`) |

**Sorte** (`--sorte`) é rolar três vezes e ficar com o melhor, **uma vez por hora de jogo**
— Sorte Extraordinária, a cada 30 minutos. O script avisa quando o personagem tem a
vantagem e você não usou; controlar o intervalo é seu, não dele.

## Casos com regra própria

**Vontade.** Vontade = IQ ± Força de Vontade / Vontade Fraca, e **qualquer resultado 14 ou
mais é falha**, mesmo que o NH seja mais alto. Se o personagem tem Vontade Fraca, o IQ conta
no máximo 14 antes de subtrair.

**Sentidos.** Visão, Audição e Olfato/Paladar são testes de **IQ**, com Prontidão e o
sentido aguçado somados. Escuridão total é -10 em ações que dependam de ver, ou impossível.

**NH efetivo 3 ou menos:** o livro não permite a jogada, **salvo em defesa ativa**. O script
recusa e manda usar `--defesa` se for o caso.

**Sucesso automático.** Coisa trivial não se testa. Achar a loja da esquina não pede teste;
acertar um alvo à queima-roupa pede, porque a arma pode falhar. Se nem falha crítica nem
sucesso decisivo fazem sentido ali, **não role**.

## Quando o teste na verdade é uma disputa

Muita coisa que parece teste simples é **Disputa de Habilidades** (MB, cap. 12) — os dois
lados rolam:

> "Se você estiver se movendo silenciosamente e alguém estiver escutando especificamente
> intrusos, o GM fará uma Disputa entre sua Furtividade e a Audição de seu oponente."

**Para isso existe a skill `disputa-nh`** — ela rola os dois lados, compara as margens e
entrega o bloco pronto. Use esta aqui só quando o teste for mesmo contra a dificuldade da
situação, e não contra alguém.

A margem sai impressa em toda rolagem, o que permite comparar na mão se for preciso: ganha
quem passou pela maior margem, ou falhou pela menor; margem igual é empate.

## Mostrar na tela

O script imprime um bloco **PARA O WHATSAPP** já em formatação de WhatsApp (`*negrito*`,
`_itálico_`). **Repasse esse bloco num bloco de código** para o usuário copiar de uma vez:

```
*Comam Obabaroy* — Furtividade (sem treino)
NH 9 - 3 = *6* (precisa tirar 6 ou menos)
3d: 6 + 2 + 2 = *10*

*Falha* por 4.
```

**Todo teste gera o bloco**, inclusive os de sentido e os da seção seguinte. Mostrar ou não
à mesa é decisão do Mestre, não do script — ele entrega o texto pronto e cala a boca.

O NH aparece porque o jogador conhece a própria ficha. Fora do bloco cabe uma linha ao
Mestre: o que a falha custou, que teste vem agora, se vale segunda tentativa.

## Rolagem que o jogador não pode ver

O livro é claro (MB, cap. 12, "Situações em que o Mestre joga os dados"): quem rola é o
Mestre, **em segredo**, quando o personagem não deveria saber se foi bem sucedido —
Detectar Mentiras, Meteorologia, perícias científicas, Empatia — e nos testes de sentidos e
Noção do Perigo, porque só perguntar "façam um teste de Visão" já entrega que há algo ali.

Nesses casos, dê ao jogador o **resultado interpretado**, nunca o número: numa falha de
Detectar Mentiras, o Mestre escolhe entre mentir ou não dizer nada — e quanto pior a falha,
maior a mentira.

O bloco sai igual nesses casos — **quem decide se ele vai para a mesa é o Mestre.** Quando
for um desses testes, vale lembrá-lo numa linha ao lado do bloco, e nada além disso.

## Nunca invente o dado

Quem sorteia é a skill `roll`, e esta chama aquela. **Relate o que saiu**, número por
número. Não escreva um resultado sem ter rodado o comando, não rode de novo porque saiu
ruim, e não arredonde a favor de ninguém.

Se o usuário quiser um valor específico para testar uma regra, ele pede — e aí **diga na
resposta que foi escolhido, não rolado**.

## Registrar

`--gravar` anota uma linha no capítulo atual pela `gerenciar-campanha`. Use **só quando o
dado mudou o rumo** — a luta inteira não vira histórico. O critério está na
`gerenciar-campanha`: decisão de jogador, dado que mudou o rumo, dano relevante, informação
descoberta.
