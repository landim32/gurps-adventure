---
name: add-grid-hex
description: >
  Sobrepõe o grid hexagonal de combate do GURPS 3ª Edição a qualquer mapa visto de cima,
  na proporção correta de 1 hexágono = 1 metro, com cada hexágono rotulado por letra e
  número (A1, C5, F2) e o traço quase transparente para não competir com a arte. Grava
  um índice JSON de cada hexágono (centro em pixels) para a skill atualizar-mapa colar
  os tokens. Lê a escala do sidecar que a skill cenario-rpg grava, ou recebe a largura
  em metros na linha de comando. Use when the user asks to "adicionar grid", "grid
  hexagonal", "hexágonos no mapa", "colocar a grade", "numerar os hexágonos",
  ou /add-grid-hex.
---

# Grid hexagonal de 1 metro sobre um mapa

Pega uma imagem de mapa vista de cima e devolve a mesma imagem com o grid de combate do
GURPS por cima: hexágonos de 1 metro, rotulados `A1`, `C5`, `F2`, translúcidos.

Funciona com **qualquer** arte top-down — a que a skill `cenario-rpg` gerou, um mapa
comprado, um desenho escaneado. A única coisa que ela precisa saber é **quantos metros
de largura o mapa tem**.

Entrada e saída padrão:

| | |
|---|---|
| Entrada | `cenario/apenas-imagem/<slug>.png` (e o `<slug>.json` ao lado, se existir) |
| Saída | `cenario/com-grid/<slug>.png` — arte com o grid |
| | `cenario/com-grid/<slug>.json` — índice de cada hexágono (centros em pixels, ocupação) |

Qualquer caminho serve; esses são só o padrão do projeto. O JSON do índice é o que a
skill `atualizar-mapa` lê para colar personagens no hex certo sem medir na mão.

## A regra do hexágono (MB, cap. 14)

> Lembre-se que cada hexágono representa **1 metro**. […] Cada figura deve ocupar um
> hexágono e "estar de frente" para um dos hexágonos adjacentes.
> — `livros/gurps-mb-3ed/11-combate-avancado.md`

O que isso obriga:

- **1 hex = 1 metro**, medido de centro a centro entre vizinhos. Todos os 6 vizinhos
  ficam à mesma distância, então andar um hex vale um metro em qualquer direção.
- **Topo chato, colunas verticais.** A direção no GURPS aponta para um *lado* do
  hexágono, e cada figura tem 3 hexágonos frontais — logo o "para frente" precisa ser
  uma aresta, não um vértice. Com o topo chato, o topo é aresta, que é o que a skill
  `token-hex-gurps` assume ao gerar os tokens ("frente = topo do hex").
- **Uma figura por hexágono** (até 4 amistosos apertados, se não estiverem fazendo
  nada); **deitado ocupa 2**; hexágono cortado por parede conta como inteiro.

Consulte `11-combate-avancado.md` se precisar arbitrar movimento, cobertura ou linha de
tiro sobre o mapa já com grid.

## Rotulagem

Colunas viram **letras** da esquerda para a direita (A, B, … Z, AA, AB…), linhas viram
**números** de cima para baixo, e as colunas ímpares descem meia linha — que é o encaixe
natural do hexágono de topo chato. O rótulo fica no centro do hexágono.

## O comando

```
python .claude/skills/add-grid-hex/scripts/aplicar_grid.py \
  --imagem cenario/apenas-imagem/<slug>.png \
  --saida  cenario/com-grid/<slug>.png \
  --metros-largura 15
```

A escala vem de três lugares, nesta ordem de precedência:

1. `--metro-px N` — pixels por metro, direto.
2. `--metros-largura M` — largura do cenário em metros; o script divide pela largura da
   imagem.
3. **O sidecar `<imagem>.json`**, campo `largura_m` — é o que a `cenario-rpg` grava. Se
   ele existir, o comando funciona sem nenhum argumento de escala. O script informa de
   onde tirou a escala.

Demais opções:

| Opção | Padrão | Para quê |
|---|---|---|
| `--origem X,Y` | `0,0` | Centro do hexágono A1, para alinhar o grid a um canto de parede |
| `--cor` | `#FFFFFF` | Cor do traço e do rótulo |
| `--opacidade` | `0,25` | 0 a 1 |
| `--espessura` | 1 px a cada 45 px de hex | Espessura do traço |
| `--tamanho-rotulo` | 26% do hexágono | Corpo do rótulo |
| `--sem-rotulos` | — | Só o grid, sem letras e números |
| `--indice` | o `.json` ao lado da saída | Caminho do índice de hexágonos |

## Calibrar a escala

**Calibre olhando o resultado, não o que foi pedido** — geradores de imagem erram
proporção o tempo todo, e mapa comprado raramente vem com a escala escrita.

Rode, olhe a imagem e confira um objeto de tamanho conhecido:

| Objeto | Deve ocupar |
|---|---|
| Porta simples | ~1 hexágono |
| Porta dupla | ~2 hexágonos |
| Mesa redonda de taverna com as cadeiras | ~2 hexágonos |
| Cama | 1 × 2 hexágonos |
| Corredor | 1 a 2 hexágonos de largura |

Errou? Ajuste `--metros-largura` e rode de novo. Duas ou três passadas resolvem. Se o
mapa veio da `cenario-rpg`, **corrija também o `largura_m` no JSON dela**, senão a
próxima execução volta ao valor errado.

## Legibilidade

- O rótulo leva um contorno escuro fino de 1 px, para continuar legível tanto na madeira
  clara quanto na pedra escura **sem** precisar de mais opacidade. É por isso que o
  padrão de 0,25 funciona nos dois casos.
- Em arte clara (pedra clara, areia, neve) troque para `--cor "#101018"`. Branco some.
- O script **recusa** hexágono menor que 12 px, em que o rótulo não caberia. Se der esse
  erro, a saída é arte com mais resolução ou um recorte menor do cenário — não diminuir
  a fonte.
- Acima de uns 25 × 25 hexágonos o mapa fica poluído para usar na mesa. Prefira recortar
  o ambiente que importa.

## Índice de hexágonos

`aplicar_grid.py` grava, **sempre**, um JSON ao lado da imagem. Fonte da verdade para
colar tokens; não edite os centros à mão — mude origem/escala e rode o grid de novo.

```json
{
  "mapa": "taberna.png",
  "metro_px": 48.0,
  "token_1hex_px": 48,
  "orientacao": "topo-chato",
  "hexagonos": {
    "C5": { "coluna": 2, "linha": 4, "cx": 144.0, "cy": 216.0, "bbox": [116, 192, 172, 240] }
  },
  "ocupacao": {}
}
```

Cada chave em `hexagonos` é o rótulo do grid (`A1`, `C5`). `cx`/`cy` são o centro em
pixels. `token_1hex_px` é o tamanho de uma figura humana (1 hex = 1 m). `ocupacao`
começa vazio; a skill `atualizar-mapa` preenche e desenha a mesa.

Reaplicar o grid **conserva** a ocupação dos hexágonos que ainda existem.

Para montar a cena (personagens nos hexágonos), use a skill **`atualizar-mapa`** — ela
lê este índice. Não cole tokens à mão nem meça pixels.

## Depois de aplicar

Se o cenário tiver ficha da `cenario-rpg`, **volte ao `<slug>.json` e preencha o que só
existe agora**: o bloco `grid` (colunas, linhas, `metro_px`, origem) e o campo
`hexagonos` de cada área e de cada acesso, com os intervalos reais (`C3–F8`). Isso é
descrição para o Mestre (salão = `C3–F8`); o JSON do índice é outra coisa — coordenadas
para colar tokens.

Informe ao usuário a escala final em px/m, as dimensões em metros, o tamanho do grid
(colunas × linhas), o caminho da imagem **e o do índice**.
