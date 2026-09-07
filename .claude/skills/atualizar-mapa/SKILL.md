---
name: atualizar-mapa
description: >
  Põe personagens e NPCs num mapa de cenário já com grid hexagonal, cada um no hexágono
  pedido e olhando para onde foi pedido ("Comam Obabaroy em I5 olhando para H5").
  Personagens dos jogadores ganham aura azul translúcida; NPCs, aura vermelha. Usa o
  token-hex.png da pasta de cada personagem. Use when the user asks to "atualizar o
  mapa", "colocar o Fulano em I5", "montar a cena", "posicionar os personagens",
  "mover o NPC para K7", "desfazer o movimento", ou /atualizar-mapa. Grava a imagem na
  pasta do capítulo atual da campanha (skill gerenciar-campanha) e mantém um histórico
  de todas as movimentações, que permite voltar atrás.
---

# Atualizar o mapa da mesa

Pega um cenário de `cenarios/` que já tenha grid e coloca gente nele: cada figura no seu
hexágono, virada para onde deve, com **aura azul** se for personagem de jogador e
**aura vermelha** se for NPC.

É a skill do meio da partida — "o orc entra pela porta em K11 e encara o Comam", "o
Cerdic recua para D8" — e o resultado é uma imagem nova da mesa a cada mudança.

## O que precisa existir antes

| Precisa | De onde vem |
|---|---|
| A arte do cenário **com grid** e o **índice `.json` de hexágonos** | skill `add-grid-hex` |
| `personagens/<slug>/token-hex.png` para cada PJ | skill `token-hex-gurps` |
| `tokens/<slug>.png` para os NPCs | skill `token-organizator` |
| Saber **em que capítulo a mesa está** | skill `gerenciar-campanha` |

**O índice de hexágonos é o que torna isso possível**: ele guarda o centro em pixels de
cada `A1`, `C5`, `I5`, então colar no hexágono certo não envolve medir nada. Se o cenário
ainda não tiver esse `.json` ao lado da imagem, rode a `add-grid-hex` primeiro — e leia
aquela skill se tiver dúvida sobre escala, origem ou rotulagem.

Cenário antigo, gerado antes do índice existir, **não** pode ser reprocessado por cima:
a arte já tem o grid queimado e aplicá-lo de novo desenharia dois. Volte à arte limpa
(`cenario/apenas-imagem/` ou o original) e gere de novo.

## O comando

```
python .claude/skills/atualizar-mapa/scripts/atualizar_mapa.py \
  --indice cenarios/<slug>.json \
  --pj  "Comam Obabaroy em I5 olhando para H5" \
  --npc "lobo-negro em L7 olhando para I5"
```

A frase é a mesma que se fala na mesa: **`<quem> em <hex> olhando para <hex>`**. O
`olhando para` é opcional; sem ele a figura entra como o arquivo está. Repita `--pj` e
`--npc` quantas vezes quiser.

**`--indice` também é opcional.** Sem ele, a skill usa o cenário que o **plano do capítulo
atual declara** no cabeçalho (`**Mapa:** cenarios/taberna3.json`), e imprime qual pegou.
Isso vem da `gerenciar-campanha`:

```
campanha.py mapa --capitulo 1 --mapa cenarios/taberna3.json
```

Com o cenário declarado no plano e o capítulo marcado, montar a cena não precisa de nenhum
caminho na linha de comando — nem de entrada, nem de saída.

| Opção | Para quê |
|---|---|
| `--remover I5` | Tira quem está nesse hexágono (repetível) |
| `--limpar` | Esvazia o mapa inteiro |
| `--saida` | Força o caminho da imagem; sem ele, ver "Onde a imagem é gravada" |
| `--alpha-aura` | Opacidade da aura, 0-255 (padrão 110) |
| `--raiz` | Raiz do projeto, se não for o diretório atual |

**A arte com grid nunca é sobrescrita.** A mesa sai num arquivo à parte e é redesenhada
do zero a cada chamada, a partir do mapa limpo mais a ocupação registrada — colocar
alguém duas vezes no mesmo hexágono substitui, não empilha.

## Onde a imagem é gravada

A skill **pergunta à `gerenciar-campanha`** onde estamos e grava o mapa na **pasta de jogo
do capítulo atual** — `campanha/NN-capitulo/`, não a do plano.

A distinção importa: `campanha/plano/NN-.../` guarda o que foi **imaginado** para a cena e
não se mexe depois; `campanha/NN-.../` guarda o que a mesa **está fazendo** com isso. Um
mapa com tokens posicionados é registro de jogo, então é ali que ele vive.

```
campanha/plano/03-fechem-os-portoes/   ← planejado, intocado
  README.md
  npcs.md

campanha/03-fechem-os-portoes/         ← em jogo, é aqui que gravamos
  README.md                   como a cena foi + acontecimentos
  taberna3-mesa.png           ← o mapa da mesa
  taberna3-movimentos.json    ← o histórico das movimentações
```

A ordem de decisão é esta:

| Situação | Onde grava |
|---|---|
| `--saida` foi passado | Onde você mandou — sempre vence |
| Campanha ativa **com** capítulo atual | `campanha/NN-capitulo/` (a pasta de jogo) |
| Campanha ativa **sem** capítulo atual | Ao lado do índice, com aviso para rodar `campanha.py atual` |
| Sem campanha ativa | Ao lado do índice |

A pasta de jogo é criada pela própria `campanha.py atual --capitulo N`, então basta marcar
o capítulo antes de montar a cena e ela já existe.

O script **imprime o motivo** da escolha em toda execução (`Destino: capítulo 03 da
campanha`). Se a imagem não apareceu onde você esperava, é essa linha que explica.

**Marque o capítulo antes de montar a cena:**

```
python .claude/skills/gerenciar-campanha/scripts/campanha.py atual --capitulo 3
```

**Esta skill nunca cria campanha.** Sem campanha ativa ela grava ao lado do índice e segue
— é o contrato da `gerenciar-campanha` e vale aqui.

## Histórico de movimentações e rollback

Cada execução acrescenta um passo a `<mapa>-movimentos.json`, ao lado da imagem:

```json
{
  "mapa": "taberna3.png",
  "movimentos": [
    { "n": 3, "quando": "06/09/2026 20:47:41",
      "acoes": ["moveu Comam Obabaroy I5 -> J8, olhando K11 (aresta S), aura azul"],
      "ocupacao": { "...": "o mapa inteiro DEPOIS deste passo" } }
  ]
}
```

**O passo guarda a ocupação inteira depois dele, não o que mudou.** Voltar atrás é só
restaurar o instantâneo do passo desejado — não é preciso inverter operação nenhuma, e não
há como uma sequência de desfazeres divergir do que de fato aconteceu.

| Comando | O que faz |
|---|---|
| `--movimentos` | Lista o histórico, passo a passo, e sai sem mexer em nada |
| `--desfazer` | Volta um passo |
| `--voltar N` | Restaura o estado logo depois do passo N (`--voltar 0` esvazia o mapa) |

**Voltar atrás também vira um passo no histórico** — fica registrado que houve um rollback,
e é possível desfazer o desfazer. O histórico é um log, não uma pilha que se consome.

A skill distingue **colocar** de **mover**: se a pessoa já estava no mapa em outro
hexágono, ela sai de lá e o histórico registra `moveu Fulano I5 -> J8`. É por isso que o
log serve para reconstruir o combate turno a turno, e não só para consertar erro de
digitação.

## Quem vai onde

- **PJ** (`--pj`): o nome vira slug e o script busca `personagens/<slug>/token-hex.png`.
  "Comam Obabaroy" → `personagens/comam-obabaroy/token-hex.png`. Se não achar, ele lista
  as pastas que existem em `personagens/` — quase sempre é só gerar o token com a
  `token-hex-gurps`.
- **NPC** (`--npc`): busca `tokens/<slug>.png`, depois `npcs/<slug>.png`. Use o nome do
  arquivo no catálogo (`lobo-negro`, `orc-machado-duas-maos`). Se não achar, ele lista o
  que há no acervo.
- Nos dois casos, um **caminho de arquivo** também serve, para um token avulso.

## A direção vem do hexágono alvo

"Olhando para H5" é mais natural na mesa do que "olhando para sudoeste", e é assim que a
skill trabalha: ela mede o ângulo entre os dois centros e encaixa na **aresta** mais
próxima do hexágono — `N`, `NE`, `SE`, `S`, `SW`, `NW`.

Isso vale para alvo **distante**, não só vizinho: "olhando para a porta" a seis hexágonos
dá a mesma aresta que o vizinho naquela direção. É útil para apontar todo mundo para o
mesmo ponto de interesse.

As seis arestas são as seis direções que o GURPS permite (MB, cap. 14: a figura encara um
*lado* do hexágono e tem 3 hexágonos frontais). Não existe meia-direção.

**A rotação assume que o token encara o sul** — a borda de baixo da imagem —, que é o
padrão do acervo em `tokens/`. Token que não siga isso entra virado errado: conserte no
acervo com a `token-organizator` (etapa "Orientar para o sul"), não compensando o ângulo
aqui, senão o mesmo token entra certo num mapa e errado no outro.

## Criaturas de mais de um hexágono

> O movimento de uma criatura que ocupa mais de um hex é **controlado por sua cabeça**.
> […] movimente a criatura para a frente como se sua cabeça fosse uma figura normal de 1
> hex. O resto do corpo segue a cabeça.
> — MB, `15-animais.md`, "Criaturas que Ocupam Mais de um Hexágono"

Daí saem as três decisões da skill:

- **O hexágono pedido é sempre o da cabeça.** "O cavalo em I5" põe a cabeça em I5.
- **O corpo se estende para trás**, no sentido oposto ao que a cabeça encara, em linha.
  É por isso que o cavalo de 3 hexágonos fica "com o cavaleiro no meio", como o livro
  descreve: cabeça, cavaleiro, garupa.
- **Sem direção não há corpo possível**, então uma criatura grande sem `olhando para`
  assume que encara o sul e o corpo sobe para o norte. Diga a direção.

O ângulo de visão e os hexágonos frontais também são os da cabeça, e são os mesmos de um
humano — o livro é explícito nisso.

### Tamanhos do livro

| Hexágonos | Criaturas (MB, `15-animais.md`) |
|---|---|
| menos de 1 | Gato, símios pequenos, enxames (o grupo inteiro ocupa um hexágono) |
| 1 | Humano, cão, **lobo**, caititu, basilisco |
| 2 | Urso em quatro patas (de pé para lutar vira 1), pantera, leão, javali, asno, mula pequena, águia gigante |
| 3 | **Cavalo**, com o cavaleiro no hexágono do meio |

O tamanho é propriedade da **criatura**, não da colocação, então mora no catálogo: campo
`hexes` na entrada dela em `tokens/tokens.json`. Sem esse campo, vale 1.

Para um caso avulso ou para sobrepor o catálogo, diga na própria frase:

```
--npc "cavalo em I5 olhando para I8 ocupando 3 hexes"
```

### A arte precisa ser comprida

Uma criatura de 3 hexágonos tem 3 metros de **comprimento** e cerca de 1 de largura. O
script escala o token pelo comprimento (o eixo vertical da imagem, já que o token encara
o sul), com teto na largura — sem esse teto, uma arte quadrada declarada com 3 hexágonos
viraria uma mancha de 3×3 hexágonos por cima dos vizinhos.

Quando é o teto de largura que manda, a figura entra mais curta do que devia e o script
**avisa com o número**: *"a arte de X é larga demais para 3 hexes — vai entrar com 41% do
comprimento"*. Isso não é um erro a ignorar: quer dizer que aquele token foi desenhado
para um hexágono só. Um cavalo de verdade precisa de arte desenhada comprida.

**A aura marca os hexágonos certos de qualquer forma** — ela cobre todos os hexágonos
ocupados, então mesmo com arte curta a mesa enxerga o espaço que a criatura toma, que é o
que importa para arbitrar movimento, alcance e linha de tiro.

### Os dois avisos de encaixe

- **Corpo saindo do mapa**: se não houver hexágono atrás da cabeça, a criatura entra com
  os hexágonos que couberam e o script diz quantos de quantos.
- **Corpo por cima de quem já estava lá**: o script nomeia os hexágonos invadidos. Ele
  não recusa — no meio de um combate isso às vezes é o que se quer, e há a regra de
  Derrubar e Atropelar (MB, `15-animais.md`) para resolver — mas avisa para não passar
  batido.

## As auras

A aura é um **hexágono translúcido alinhado ao grid**, desenhado sob a figura e com a
borda suavizada. Hexágono e não círculo porque assim ela diz também *qual hexágono* a
figura ocupa, que é a informação que mais se perde quando o mapa enche.

| | Cor | Quem |
|---|---|---|
| Azul | `#3B82F6` | Personagens dos jogadores |
| Vermelho | `#DC2626` | NPCs — aliados, neutros e inimigos |

Todas as auras são desenhadas **antes** de qualquer figura, para que a aura de um não
passe por cima do vizinho quando dois estão lado a lado.

Alpha padrão 110 (≈43%): dá para ler a cor e ainda ver o piso por baixo. Suba com
`--alpha-aura` em mapa muito carregado, desça em mapa claro. Para trocar a cor de um caso
específico (um PJ enfeitiçado, um NPC aliado), acrescente `"cor": "#RRGGBB"` na entrada
dele dentro de `ocupacao` no índice e redesenhe.

## O que fica gravado

A ocupação vive no próprio índice de hexágonos, o que permite redesenhar a mesa a
qualquer momento:

```json
"ocupacao": {
  "I5": {
    "tipo": "pj",
    "quem": "Comam Obabaroy",
    "token": "personagens/comam-obabaroy/token-hex.png",
    "frente": "SW",
    "olhando": "H5"
  }
}
```

Rodar o script sem `--pj`/`--npc` apenas redesenha o que já está lá — útil depois de
trocar o token de alguém ou mexer na arte do cenário.

## Conferir

Olhe a imagem depois. Três coisas que costumam sair erradas e só aparecem olhando:

1. **A figura virada para o lado errado** — quase sempre é token que não encara o sul no
   acervo (veja acima).
2. **Aura sob a mobília** — o token está no hexágono certo, mas o hexágono está em cima de
   uma mesa ou de uma parede. Isso é problema de posição, não do script: confira o hex
   pedido contra a arte.
3. **Criatura grande com a arte errada** — veja "Criaturas de mais de um hexágono".
