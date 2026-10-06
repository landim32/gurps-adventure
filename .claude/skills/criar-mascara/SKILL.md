---
name: criar-mascara
description: >
  Cria a Máscara 3D de uma imagem de cenário para enviar ao Roll6, que a usa na vista 3D estilo
  Wolfenstein. O tom de cada ponto é a ALTURA da parede: preto = parede inteira, branco = vazio,
  cinza = parede mais baixa (balcão, mesa, mureta). Lê a imagem, entende cada elemento do cenário e
  julga a altura dele, desenha a grade de coordenadas, descreve as formas num JSON com a altura de
  cada uma, renderiza o PNG em tons de cinza, confere numa prévia colorida pela altura e valida
  tamanho, tons, salas fechadas e portas estreitas. Use when the user asks "/criar-mascara",
  "criar a máscara 3D do mapa", "máscara de paredes para o Roll6", "vista 3D do cenário",
  "altura das paredes", "paredes baixas na máscara".
---

# Criar máscara 3D

A máscara é uma imagem em tons de cinza do **mesmo tamanho** do cenário. O Roll6 a lê **por
pixel** (aba "3D" de "Imagem do cenário") e usa o **tom como altura da parede** naquele ponto:

| Tom | Altura da parede |
|---|---|
| **preto** (0) | **inteira** (paredes, colunas, fachadas) |
| **cinza** | proporcional: um cinza de 50% (tom 128) dá metade da altura |
| **branco** (255) | **vazio** (piso, porta, passagem) |

Ela **só afeta a vista 3D**: não bloqueia peças no 2D. Parede mais baixa que os olhos da câmera
(~50%) deixa **ver por cima** dela; mais alta esconde o que está atrás.

Os cenários do repositório ficam em `cenarios/` (a campanha joga no Roll6, que é o espelho da
mesa; ver a skill `roll6`). A máscara sai ao lado da imagem: `<nome>-mascara.png`.

> **Versão do Roll6.** Os tons de cinza como altura vêm da feature 036 do Roll6. Num Roll6 que
> ainda não a tem, o cinza escuro vira parede inteira e o claro vira vazio (limiar em 50%): nesse
> caso gere com `renderizar.py --legado` (só preto e branco, altura ≥ 50% vira preto) e avise o
> usuário de que as alturas intermediárias não aparecem.

## O formato (regras do Roll6, não negociáveis)

| Regra | Valor |
|---|---|
| Tons | altura = 1 − tom/255. **Abaixo de 5% de altura (tom ≥ 243) vira vazio**; a partir de 95% (tom ≤ 12) vale parede inteira. Qualquer tom entre os dois é aceito |
| Tamanho | **o mesmo da imagem do cenário**, em pixels. O Roll6 recusa proporção que difira mais de 1% |
| Arquivo | PNG, até 10 MB, 1 canal ou RGB, **sem transparência** (pixel transparente conta como vazio) |
| Grade | hexágonos flat-top, 40 px do centro ao canto (80 px de largura). Mapa de C colunas x L linhas: largura = 40 x (1,5 C + 0,5), altura = 40 x raiz(3) x (L + 0,5) |
| Aberturas | portas e corredores com **pelo menos 2/3 de hexágono** (≥ 55 px quando o hexágono tem 80 px): a câmera tem raio de 1/3 de hexágono e não atravessa parede |
| Câmera | **qualquer** parede, mesmo baixa, bloqueia a câmera (ela só observa; peças não são afetadas) |
| Parede fina | a máscara é reduzida a no máximo **512 células** no lado maior, e cada célula fica com a **mediana** do tom dos seus pixels: parede com menos de ~4 px (na escala de 1220 px de largura) some. Engrosse |
| Bordas | cada forma entra com **um tom só** e sem antialiasing. Dois tons vizinhos formam um degrau; não faça gradiente (é ruído para o Roll6) |

A máscara não precisa seguir a grade, porque é lida em pixels. A grade hexagonal entra só como
régua na prévia.

## A escala de alturas

Uma **pessoa em pé** (1,7 m) tem **53%** da altura da parede inteira (~3,2 m); os olhos da câmera
ficam em ~50%. Para julgar um elemento, compare-o com uma pessoa e use a escala (`scripts/niveis.py`
imprime a tabela; cada forma do JSON aceita `"nivel"`, `"metros"` ou `"altura"`):

| `nivel` | altura | tom | exemplos |
|---|---|---|---|
| `parede` | 100% | 0 | paredes, colunas, pilares, fachadas, troncos grossos, penhascos (≥ 3,2 m) |
| `rocha-grande` | 78% | 56 | rochedo, estátua grande, árvore caída, carroça (~2,5 m) |
| `estante` | 63% | 94 | estante, armário, lareira, tapeçaria (~2 m) |
| `muro-alto` | 53% | 120 | muro à altura de uma pessoa, barril grande, cerca alta (~1,7 m) |
| `parapeito` | 40% | 153 | parapeito, mureta de jardim, mesa de mapa alta (~1,3 m) |
| `balcao` | 33% | 171 | balcão de taverna, muro baixo, altar, sarcófago (~1,05 m) |
| `mesa` | 23% | 196 | mesa, bancada, cama (~0,75 m) |
| `banco` | 14% | 219 | banco, baú, caixote (~0,45 m) |
| `degrau` | 8% | 235 | degrau baixo, soleira (~0,25 m) |
| `vazio` | 0% | 255 | piso, tapete, porta aberta, arco, passagem |

Use valores entre os níveis quando o desenho pedir (`"metros": 1.4`, `"altura": 0.45`). Quando
duas formas se sobrepõem, vale a **mais alta** (o tom mais escuro).

## Scripts

Cada um é independente, usa só biblioteca padrão e Pillow, e tem `--help`.

| Script | O que faz |
|---|---|
| `scripts/niveis.py` | a escala de alturas; converte tom ↔ altura (`--tom 171`, `--altura 0.33`) |
| `scripts/grade.py` | cópia da imagem com grade de coordenadas em pixels (e a hexagonal, com `--colunas`/`--linhas`); `--recorte` e `--ampliar` para olhar de perto |
| `scripts/detectar.py` | acha elementos por cor, luminosidade ou pouca saturação e dá a eles **uma altura** (`--nivel`, `--metros`, `--altura`); `--acrescentar` soma várias detecções no mesmo JSON |
| `scripts/renderizar.py` | lê o JSON e desenha o PNG em tons de cinza, sem antialiasing, com o tamanho exato; `--legado` gera só preto e branco |
| `scripts/previa.py` | cenário com a máscara por cima, **colorida pela altura** (vermelho = inteira, amarelo = baixa) e com legenda; grade hexagonal opcional |
| `scripts/validar.py` | tamanho, tons usados e suas alturas, salas fechadas, passagem mais estreita, paredes finas, ruído |

## Fluxo

Em rodadas curtas, **com verificação visual a cada uma**. Não tente acertar tudo de uma vez.

1. **Entrada.** Pergunte o que faltar: o caminho da imagem; colunas x linhas da grade, se o mapa
   do Roll6 já existe; e o que o usuário quer ver como volume. **Por padrão** têm altura:
   paredes e pilares (inteira) e obstáculos contínuos que o jogador precisa ver como volume
   (balcão, estante, lareira, árvore, rocha, mureta, mesa grande). São vazios: piso, tapete, porta
   aberta, arco, escada, e coisas pequenas e soltas (banco, caixote, cadeira) **a menos que o
   usuário peça**: toda parede, mesmo baixa, bloqueia a câmera, então um monte de móveis pequenos
   deixa a câmera presa.
2. **Olhar a imagem.** Leia a imagem com a ferramenta de leitura e gere a grade:
   `python .claude/skills/criar-mascara/scripts/grade.py --imagem cenarios/X.png --saida X-grade.png [--colunas C --linhas L]`.
   Leia a grade, e olhe de perto os cantos duvidosos com `--recorte x0,y0,x1,y1 --ampliar 2`.
3. **Inventariar e julgar a altura.** Antes de qualquer JSON, escreva a **tabela de elementos** do
   cenário (um item por parede, móvel ou objeto, agrupando os iguais) e decida a altura de cada
   um olhando o desenho, comparando com uma pessoa (53%) e com os vizinhos:

   | # | Elemento | Onde (px) | O que indica a altura | Nível |
   |---|---|---|---|---|
   | 1 | parede de pedra do perímetro | contorno | muralha, muito mais alta que uma pessoa | `parede` |
   | 2 | balcão da taverna | x 300-620, y 380-420 | tampo na altura da cintura | `balcao` |
   | 3 | estante com garrafas | x 40-180, y 20-60 | passa da cabeça de uma pessoa | `estante` |
   | 4 | tapete | centro | chão | vazio |
   | 5 | porta | x 360-470, y 505 | passagem aberta | abertura |

   Pistas de altura: **sombra** projetada (longa = alto), **perspectiva** e o lado visível do
   objeto, **comparação com uma figura ou móvel conhecido** (cadeira, pessoa, barril), a
   **função** (balcão e mesa têm altura de uso; parede é alta; árvore passa de tudo) e o estilo do
   mapa (mapas vistos de cima mostram o topo: use sombra e função). **Quando a altura for
   ambígua, pergunte ou diga o que assumiu e por quê**; mostre a tabela ao usuário antes de
   seguir se houver itens duvidosos.
4. **Descrever as formas em dados.** Escreva `<nome>-mascara.json` com formas em pixels da imagem
   original: `retangulo`, `poligono`, `linha` (com `espessura`), `circulo`, `elipse`, e `imagem`
   (um PNG detectado), cada uma com `"nivel"`, `"metros"` ou `"altura"` quando não for parede
   inteira, e `"nome"` para documentar. `aberturas` são as mesmas formas, desenhadas **depois das
   paredes** (portas, arcos): em branco por padrão, ou com altura para deixar um parapeito no vão.
   Exemplo com alturas em `exemplos/sala-4x4.json`.
   Quando as paredes forem bem definidas por cor ou contraste (tijolo escuro, traço grosso),
   comece pela detecção automática de **um tipo de elemento por vez** e junte no mesmo JSON:
   `detectar.py --imagem X.png --escuro 60 --nivel parede --saida det-paredes.png --saida-json X-mascara.json`
   e depois, para o balcão por cor,
   `detectar.py --imagem X.png --cor 150,100,60 --nivel balcao --saida det-balcao.png --saida-json X-mascara.json --acrescentar`.
   Parâmetros: `--cor R,G,B --tolerancia N`, `--escuro N`, `--claro N`, `--cinza S --luz-min --luz-max`,
   `--minimo` (mancha mínima, px) e `--fechar` (raio do fechamento de buracos).
5. **Renderizar.**
   `renderizar.py --json X-mascara.json --saida X-mascara.png --imagem cenarios/X.png`.
   O PNG sai em tons de cinza, com o tamanho exato da imagem, e o script lista os tons usados
   com a altura de cada um. Um tom que você não esperava aponta um erro no JSON.
6. **Prévia.** `previa.py --imagem cenarios/X.png --mascara X-mascara.png --saida X-previa.png
   [--colunas C --linhas L] --ampliar 2` e **leia a prévia**. Confira a cor de cada elemento
   contra a tabela do passo 3 (balcão amarelo-alaranjado, parede vermelha), ache parede que falta,
   vazamento (espaço que devia ser fechado), porta entupida e elemento com altura errada, corrija
   o JSON e renderize de novo. **No máximo 5 rodadas**; diga o que ainda ficou duvidoso.
7. **Validar.** `validar.py --mascara X-mascara.png --imagem cenarios/X.png [--colunas C --linhas L]`.
   Sai com código 1 em ERRO (formato, tamanho, transparência, > 10 MB). AVISO não muda o código,
   mas deve ser resolvido ou explicado: salas fechadas onde a câmera não chega, passagem menor
   que 2/3 de hexágono, parede que some na redução, tons quase brancos (viram vazio), tons demais
   (antialiasing). A lista de tons confere as alturas com a tabela do passo 3.
8. **Entregar.** Diga os caminhos de `X-mascara.png`, `X-mascara.json` e `X-previa.png`, a tabela
   final de elementos com a altura de cada um, e como usar: **no Roll6, abra o mapa, "Imagem do
   cenário" > aba 3D > Máscara 3D > enviar `X-mascara.png`, e salve o mapa.** A prévia da máscara
   no Roll6 mostra os tons de cinza como estão.

## O que esta skill não faz

- **Não envia nada ao Roll6.** Subir a máscara é feito pelo usuário na tela do mapa.
- **Não altera a imagem do cenário.**
- **Não decide sozinha** o que é parede nem a altura quando o desenho é ambíguo: pergunta, ou diz
  o que assumiu e por quê.

## Limites conhecidos

- A altura é um **julgamento visual** a partir de sombras, perspectiva e função do objeto; a
  detecção automática só acha manchas por cor ou contraste e **não mede altura**. Ela entra com
  uma altura fixa informada por quem a roda.
- A detecção pega bem paredes de cor ou contraste uniforme; **pedra texturizada, parede diagonal
  fina e desenho muito ornamentado** saem esburacados. Use a detecção só como ponto de partida e
  feche o resto com formas no JSON.
- Não há rampas nem gradientes: cada forma tem uma altura só. Uma escada é feita com degraus
  retangulares de alturas crescentes, e só vale a pena se a câmera for passar perto.
- A passagem mais estreita é uma estimativa por erosão numa grade reduzida, com erro de uns
  poucos pixels.
- O Roll6 reduz a máscara a 512 células com a mediana por célula, e o `validar.py` faz a mesma
  conta: o resultado pode diferir um pouco em parede que está na fronteira da célula.
