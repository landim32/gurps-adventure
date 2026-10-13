---
name: validar-movimento
description: >
  Confere o movimento que cada personagem fez no roll6 contra as regras do MB 3ª ed. antes de
  resolver as ações: acha o Deslocamento que vale hoje (ficha, Carga atual, perna mutilada,
  Fadiga, PV, posição), o teto de hexágonos da manobra declarada (Defesa Total, Apontar,
  Ataque Total, Avançar e Atacar... ou os pontos de movimento do Deslocamento, com virada,
  lado/trás, terreno e água), e diz onde a peça deve ficar quando passou do limite. Não rola
  dado, não resolve ação, não toca em ficha e não escreve na mesa; só o `campanha/terreno.json`
  quando se pede. Use when the user asks "/validar-movimento", "ele andou mais do que podia",
  "confere o deslocamento do turno", ou quando a processar-turno chega ao passo de movimento.
---

# Validar movimento

Folha de cálculo da `processar-turno`: **decisão fica no roteador, o número fica aqui**. Ela
recebe o que a mesa registrou (de onde a peça saiu, onde parou, olhando para onde) e devolve
o que o livro permite. **Prioridade da mesa: não prejudicar o personagem além do que o MB e a
ordem do Mestre mandam.** Na dúvida de regra, a folha escolhe a leitura legal que preserva
mais progresso e **diz que escolheu** — quem decide é o Mestre.

## Como se usa

```bash
# o turno em andamento do roll6 (leitura), todos os personagens que se moveram
python .claude/skills/validar-movimento/scripts/validar_movimento.py turno [--json]
python .../validar_movimento.py turno --manobra "Negrum Carneiriums=deslocamento"   # refaz com a manobra decidida
python .../validar_movimento.py turno --peso-atual '{"comam": 18.5}'                 # Carga de hoje

# uma conta avulsa, sem o roll6
python .../validar_movimento.py calcular --de 5,10 --look-de 3 --para 6,11 --look-para 2 \
    --manobra defesa-total --desl 1 --mapa oasis-1 [--json]

# terreno: água pela imagem do mapa + as decisões do Mestre
python .../validar_movimento.py terreno --mapa oasis-1 --imagem cenarios/oasis.jpg --colunas 17 --linhas 22 --gravar
python .../validar_movimento.py terreno --mapa oasis-1 --decidir "9,12=margem"
```

Manobras (`--manobra`): `deslocamento`, `defesa-total`, `ataque-total`, `apontar`, `atacar`,
`preparar`, `finta`, `aguardar`, `concentrar`, `posicao`.

## O que ela confere

| Fator | Regra (MB) | Onde |
|---|---|---|
| **Manobra** | só o **Deslocamento** gasta pontos de movimento; as outras têm teto fixo: Defesa Total, Avançar e Atacar/Preparar/Fintar/Aguardar/Concentrar **1 hex**; Ataque Total **o maior entre 2 e metade do Desl.**, só para a frente; Apontar **o menor entre 2 m e metade do Desl.**; Mudança de Posição **0** | `11-combate-avancado.md`, "Manobras" e "Custos em Pontos de Movimento" |
| **Pontos do Deslocamento** | frente 1, lado/trás 2, virar 1 por lado; no fim, grátis se gastou metade ou menos, senão **1 lado** grátis; sempre se pode andar 1 hex | idem, "Mudança de Direção" |
| **Deslocamento da ficha** | parte do valor da ficha e troca só a parte da **Carga** se o peso mudou (Leve -1 ... Muito Pesada -4) | `07-equipamento-e-carga.md`, "Carga" |
| **Perna mutilada ("coxo")** | -3 no Deslocamento (lido do `status` da peça: "Coxo", "perna mutilada", "perna incapacitada") | `04-desvantagens.md`; pé incapacitado: teto 3 |
| **Fadiga** | ST efetiva (a Fadiga atual) **<= 3**: Deslocamento pela metade, arredondada para baixo, **depois** das reduções acima | `12-ferimentos-doencas-fadiga.md`, "Fadiga" |
| **PV** | **1 a 3** restantes: metade (uma vez só se Fadiga e PV baixos coincidirem — a folha avisa); **0 ou menos**: teste de HT no início do turno | idem, "Danos gerais" |
| **Posição** | agachado +1/2, ajoelhado +2, rastejando +2 por hex; deitado: **1 hex**; sentado: não anda | `11`, "Custos em Pontos de Movimento" |
| **Terreno e água** | água de 30 cm custa o dobro; **água funda: 1 hex por turno** (a rota é cortada na entrada) e teste de **Natação** (modificadores em `09-testes-de-habilidade.md`); obstruído/piso ruim +1; passar por hex de amigo +1 | `campanha/terreno.json` |
| **Outro mapa** | movimento registrado em outro `mapId` não vale: a peça deste mapa não saiu do lugar | `get_turn_state` |
| **Montaria, veículo, voo** | **não calcula**: avisa para usar `13` e `14` à mão | `13-combate-montado-veiculo.md`, `14-voo.md` |

## Recuar (regra da mesa)

Declaração com **recua / recuo / recuar / recuando / recuei / recuou** (inclusive "recou", erro
comum) é a manobra Recuar. A folha **não** põe esse hexágono na conta de pontos nem no teto da
manobra. Ela devolve `recuar` com `trecho`, `bonus_defesa` (+3), `de`, `para` (1 hexágono
atrás: frente + 3, a partir da posição **final** validada do turno), `look` (não muda), `valido`,
`motivos` e `avisos`. `valido: false` quando o hexágono de trás está ocupado, está fora do mapa,
ou o personagem está ajoelhado, sentado ou atordoado. Água funda e terreno incerto saem como aviso.
`validar_movimento.py recuar --de x,y --look N [--mapa] [--ocupado "x,y=Nome"]` faz a mesma conta
avulsa (serve para NPC, quando o Mestre manda). Quem aplica o movimento no fim do turno e o +3 é a
`processar-turno` (seção 1b).

## O que ela devolve (por personagem)

`veredito` (`ok`, `corrigir`, `sem_movimento`, `impossivel`), `manobra` e a declaração que a
originou, `deslocamento` com a conta linha a linha, `custo` contra o que o roll6 contou,
`rota` por hexágono, `posicao_valida` e `look_valido` (onde a peça **deve** ficar), `motivo`,
`natacao`, `terreno_na_rota`, `alternativas` quando a declaração mistura manobras, e `avisos`.

O custo do roll6 (`gastou N pontos`) **não é o do livro**: ele conta tudo como Deslocamento.
Quem vale é o custo da folha para a **manobra declarada**.

## Regras de decisão (o que o roteador faz com o resultado)

1. **Manobra ambígua** (a declaração mistura Deslocamento com Defesa Total, Apontar, Ataque
   Total...): a folha propõe a mais restritiva e mostra as `alternativas`. **Pergunte ao Mestre**
   e refaça com `--manobra`. Decidido, a conversa acabou, e vira errata.
2. **`corrigir`**: a peça fica em `posicao_valida`, o `process_turno` leva `x`, `y` e `look` dela, e
   a **narração avisa** ("volta ao ponto onde ela o deixa"), salvo ordem expressa do Mestre.
3. **Reavaliar a ação a partir do ponto corrigido**, nunca invalidá-la só porque a peça não
   chegou: refaça distância e ângulo com `calcular-alcance`, confira alvo e arma. Se a ação
   **não pode** ser feita dali, **não rola**; o resumo ao Mestre diz isso. Defesa Total só
   substitui quando é legal (a manobra comprometida não o impede) e o Mestre não mandou outra
   coisa — **proponha, não presuma**.
4. **Água funda**: a peça entra, o turno dela acaba ali, e o roteador pede o teste de Natação
   pela `teste-nh` (`--nh` = DX-4 ou o NH da ficha; +3 se entrou de propósito; -2 por nível de
   Carga; -3 se coxo). Falhou: o Mestre diz se volta um hexágono.
5. **Terreno incerto** (`incerta` no `terreno.json`): a folha trata como terra e **avisa**. Leve
   ao Mestre; a decisão dele entra com `terreno --decidir`, e vale para os turnos seguintes.

## O que ela não faz

- Não decide a manobra por conta própria quando há dúvida, não rola dado, não resolve a ação.
- Não escreve em ficha, `saude.md`, `bolsa.md` nem no roll6. `terreno.json` só com `--gravar` ou
  `--decidir`.
- Não vê terreno que não esteja no `terreno.json`: sem ele, água e obstáculos não são conferidos
  (a saída diz isso no cabeçalho).
- Não substitui o juízo do Mestre: o MB manda usar o bom senso (`18-o-mestre.md`), e a decisão
  dele, registrada como errata, ganha do cálculo.

## Limites conhecidos

- A rota é a **mais barata** entre o início e o fim registrados (o roll6 só guarda os dois
  pontos); com vários movimentos no turno, vale o início do primeiro e o fim do último.
- A água é lida da **cor da imagem** (`terreno --imagem`): serve de triagem, e o que fica entre
  15% e 70% de água sai como `incerta` para o Mestre decidir.
- Fadiga e PV baixos juntos: aplica uma metade só.
