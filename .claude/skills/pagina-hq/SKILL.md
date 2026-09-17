---
name: pagina-hq
description: >
  Monta as páginas da HQ a partir do roteiro: divide a página em quadros, desenha o
  esboço de planejamento (figuras geométricas no lugar dos personagens e os balões já no
  tamanho final), e depois monta a página de verdade com a arte gerada, moldura, calha e
  letreiramento. Fecha o volume num PDF. Tudo em Pillow, sem IA. Use when the user asks
  to "montar as páginas", "esboçar a página", "layout da HQ", "diagramar", "fechar o
  volume em PDF", ou /pagina-hq.
---

# A página da HQ

Duas passagens sobre o mesmo `roteiro.json`:

```
# 1. o esboço — antes de gastar um centavo de IA
python .claude/skills/pagina-hq/scripts/esboco.py --roteiro campanha/hq/vol-01-.../roteiro.json

# 2. a página final — depois que a arte existe
python .claude/skills/pagina-hq/scripts/montar_pagina.py --roteiro ... \
    --pdf campanha/hq/vol-01-.../volume.pdf
```

Ambos aceitam `--pagina N` (repetível) para trabalhar uma página só, `--saida` para
mandar a imagem para outro lugar e `--raiz` quando não se está na raiz do projeto.
`montar_pagina.py` aceita ainda `--sem-baloes`, que monta só a arte.

A página é **A4 a 300 dpi (2480×3508)** — a mesma medida da planilha de personagem, então
HQ e ficha saem na mesma impressora.

## O esboço é o artefato mais importante

Ele desenha, **sem IA**, o que a página vai ser: cada quadro na sua caixa, cada
personagem em círculo, retângulo e linha, e **os balões de verdade, no tamanho final**,
desenhados pela skill `baloes-hq`. Um balão que não cabe no esboço também não cabe
depois.

É onde se resolve, de graça, o que custaria caro resolver depois:

- o quadro comporta três figuras ou só duas?
- o balão do Hoel está cobrindo o rosto do Negrum?
- a página vira na hora certa — o susto está no último quadro, ou já foi entregue no
  primeiro?
- a leitura corre de cima para baixo e da esquerda para a direita, sem tropeço?

Cada figura tem `quem`, `em` (onde os **pés** tocam o chão, em % do quadro), `altura`
(em % da altura do quadro), `pose` e `olhando`.

| Pose | Como sai |
|---|---|
| `de pé` (padrão) | cabeça, tronco, braços, pernas |
| `sentado` | menor, pernas dobradas para o lado de quem olha |
| `caído` | deitado, da esquerda para a direita |
| `correndo` | pernas abertas, braços em movimento |
| `montado` | figura sobre a elipse do cavalo |
| `close` | só a cabeça, grande, com os eixos do rosto |
| `multidão` | fileira de círculos, sem corpo |
| `objeto` | retângulo cruzado — mesa, carroça, caixote |

`olhando`: `esquerda`, `direita`, `frente` ou `costas`. A linha fina de horizonte em cada
quadro serve para conferir se todo mundo está pisando no mesmo chão.

## A montagem final

Cada quadro recebe a arte de `quadros/pNNqMM.png` (o caminho que a skill `quadro-hq`
grava no roteiro), **cortada para preencher a caixa sem deformar** — o corte é um pouco
acima do centro, que é onde costuma estar a cabeça. Depois vêm a moldura preta e os
balões.

**O letreiramento é aplicado na página, nunca no quadro solto.** Duas razões: a letra
sai no mesmo corpo em todos os quadros (quadro estreito e quadro largo letreirados com a
mesma régua), e o arquivo em `quadros/` continua limpo — dá para regerar a arte sem
perder o texto, e para exportar a versão sem balões.

Quadro que ainda não tem arte não impede nada: entra uma caixa hachurada com o número e
o que o roteiro diz que se vê ali. Dá para montar o volume inteiro no primeiro dia e ir
substituindo quadro a quadro.

## A caixa de cada quadro

No roteiro, `caixa: [x, y, largura, altura]` em **% da área útil da página**. Sem
`caixa`, a página cai numa grade automática conforme o número de quadros (1 a 7).

Variar a caixa é o que dá ritmo: faixa larga para estabelecer o lugar, quadros
pequenos e iguais para diálogo rápido, um quadro só ocupando a página inteira para o
momento que importa. **Entre 4 e 7 quadros por página** é o que uma página A4 comporta
sem virar mosaico.

## O volume fechado

`--pdf caminho.pdf` junta as páginas montadas num PDF de 300 dpi, na ordem do número da
página. É o arquivo que se manda para o grupo ou para a gráfica.
