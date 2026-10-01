---
name: calcular-alcance
description: >
  Mede a distância entre dois pontos do mapa hexagonal do roll6 — quantos hexágonos, quantos
  metros, e em que lado o alvo está a partir de quem atira. Aceita rótulos ("P7"), pares
  "x,y", ou nomes de peça combinados com a saída de `list_map_tokens`. Informa a linha da
  tabela de escala que o modificador de velocidade/distância vai usar e se o alvo está no
  ângulo de visão de quem mira. Não rola dado, não resolve ataque, defesa nem dano, não
  escreve em lugar nenhum, e não fala com o roll6: recebe as posições. Use when the user asks
  "/calcular-alcance", "a que distância está", "ele está na minha frente ou de lado".
---

# Calcular alcance

O mapa é o do roll6: **flat-top, “odd-q”** — colunas ímpares deslocadas meia célula para
baixo, posição = (`x` coluna, `y` linha) desde 0, frente (`look`) de 0 a 5 começando no
topo e girando no sentido horário. Numa grade assim **não existe “leste”**: as seis
vizinhas são topo, baixo, e os quatro cantos. Quem conta hexágonos de cabeça erra aqui, e
erra justamente nos tiros longos.

```
python .claude/skills/calcular-alcance/scripts/calcular_alcance.py --de Q30 --para P11
python .../calcular_alcance.py --de 16,29 --para 15,6 --frente 3
python .claude/skills/roll6/scripts/roll6.py chamar list_map_tokens \
     '{"campaignId":1,"mapId":2}' \
  | python .../calcular_alcance.py --tokens - --de "Comam Obabaroy" --para "Morto 5"
```

`--tokens` aceita o JSON cru do `list_map_tokens`: a folha resolve nome → casa, e é assim
que se usa no meio do turno sem ninguém copiar coordenada. Ela **não** chama o MCP — quem
consulta é você, que é leitura.

## O que ela devolve

| Campo | O que é |
|---|---|
| `hexagonos` | distância em hexágonos, pela métrica cúbica do odd-q |
| `metros` | `hexagonos × 1 m` (mudável com `--metro-por-hex`) |
| `linha_tabela`, `mod_velocidade_distancia` | a linha da escala da página 201 e o modificador que dela vem — a mesma função que a `atacar-distancia` usa, para não haver duas contas |
| `lado`, `lado_nome` | o rumo de quem atira para o alvo, em `look` |
| `angulo_visao`, `giro`, `fora_do_angulo` | dado o `--frente` de quem atira: frontal, lateral (uma de 60°), na traseira, ou por trás |
| `lado_ambiguo`, `aviso_lado` | quando o alvo cai exatamente entre dois cones — ver abaixo |

## O leste que não existe

Alvo na linha exata entre dois cones empata no cálculo do rumo. A folha **não escolhe em
silêncio**: devolve `lado` com o candidato, e `lado_ambiguo` com os dois, mais o aviso de que
a mesa arbitra. Isso importa porque um “lateral” vira “frontal” conforme o cone, e é exatamente
o tipo de decisão que não deve sair de um critério escondido num laço.

Caso vizinho nunca empata — as seis casas ao redor são sempre um cone só, o que a prova de
propriedades confere casa a casa na grade.

## O que esta folha nunca faz

Não rola dado (é a `roll`), não decide o ataque (`atacar`, `atacar-distancia`), não resolve
defesa (`resolver-defesa`), não conta dano (`causar-dano`), não grava nada. Devolve número
para o Mestre arbitrar — quem escreve o que a mesa viu é a `registrar-acao`, e quem mexe no
roll6 é a `processar-turno`.

## Prova de geometria, não de confiança

A grade foi conferida por propriedades, não por exemplinho: para toda casa de uma grade 12×12,
os seis `look` levam a seis vizinhos distintos a exatamente 1 hexágono; **voltar pelo lado
oposto devolve a casa de origem** (o que pegaria paridade errada); `look_de` casa com a mesa
de vizinhos em todas as adjacências; andar N passos na mesma frente dá distância N; e o
vai-e-vem de rótulo bate com `rotulo_para_xy`/`xy_para_rotulo` do roll6, inclusive em
coluna dupla (`AA4`).
