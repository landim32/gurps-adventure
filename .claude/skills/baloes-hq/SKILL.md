---
name: baloes-hq
description: >
  Desenha os balões de uma HQ — fala, grito, sussurro, pensamento, recordatório, voz de
  fora de quadro, voz sobrenatural, canto e onomatopeia — direto na imagem, com fonte de
  letreiramento de quadrinhos e traço feito em Pillow, sem IA nenhuma. O rabicho aponta
  para quem fala, o balão se prende dentro do quadro e o texto quebra sozinho.
  Use when the user asks to "colocar os balões", "letreirar", "balão de fala", "balão de
  grito", "onomatopeia", "o texto da HQ", ou /baloes-hq. É a skill que a `pagina-hq`
  chama para letreirar a página montada.
---

# Balões de HQ

Letreiramento **nunca** sai de gerador de imagem: toda IA escreve garatuja, erra acento
e não sabe quebrar linha. Aqui o balão é geometria e o texto é fonte de verdade —
legível impresso, igual em todas as páginas e refazível sem gastar nada.

```
python .claude/skills/baloes-hq/scripts/baloes.py \
  --imagem campanha/hq/vol-01-.../quadros/p03q02.png \
  --balao 'fala em 30,16 apontando para 44,55 de "Hoel": Senta aí, então.' \
  --balao 'onomatopeia em 72,64: CRAC!'
```

Para ver os nove tipos de uma vez: `--amostra --saida amostra.png`.

## A frase

```
<tipo> em <X>,<Y> [apontando para <X>,<Y>] [largura N] [corpo N] [de "Quem"]: <texto>
```

- **`em`** é o centro do balão; **`apontando para`** é a boca de quem fala. Ambos em
  **porcentagem do quadro** (0–100), nunca em pixels — a mesma frase serve no quadro
  solto e na página montada.
- **`largura`** é a largura máxima do bloco de texto, em % do quadro (padrão 30). É o
  que decide se o balão sai redondo ou comprido.
- **`corpo`** força o tamanho da letra; deixe de fora para o padrão do tipo.
- **`de "Quem"`** não muda o desenho — fica registrado no roteiro para saber de quem é
  a fala.
- Sem `apontando para`, o balão sai sem rabicho (é o certo para recordatório).
- `\n` no texto força quebra de linha.

## Os tipos

| Tipo | Forma | Quando |
|---|---|---|
| `fala` | elipse, caixa alta | diálogo normal |
| `grito` | estrela de pontas irregulares | berro, ordem, dor |
| `sussurro` | elipse de contorno picotado, itálico | cochicho, moribundo, conspiração |
| `pensamento` | nuvem, rabicho de bolhas | o que o personagem pensa e não diz |
| `narracao` | caixa creme, sem rabicho | voz do narrador, marcação de tempo e lugar |
| `off` | retângulo arredondado, rabicho longo | quem fala está fora do quadro |
| `eletronico` | contorno em zigue-zague, fundo azulado | morto-vivo, magia, voz que não é de gente |
| `canto` | elipse ondulada, notas musicais | o trovador cantando |
| `onomatopeia` | sem balão: letra com contorno grosso | CRAC, TUM, CLANG |

Apelidos aceitos: `berro`→grito, `recordatorio`/`legenda`→narracao, `radio`/`magia`→
eletronico, `som`/`sfx`→onomatopeia, e mais alguns (veja `APELIDOS` no script).

Cores e fonte de um balão podem ser trocadas caso a caso pelas chaves `fundo`, `traco`,
`tinta` e `fonte` quando o balão vem de JSON — útil para o vilão ter balão preto de
letra branca.

## Como colocar o balão no lugar certo

1. **O balão fica na parte morta do quadro** — céu, parede, sombra. Quem gera a arte
   (skill `quadro-hq`) deve deixar esse respiro de propósito.
2. **Ordem de leitura**: de cima para baixo e da esquerda para a direita. Quem fala
   primeiro tem o balão mais alto ou mais à esquerda; balão fora de ordem faz o leitor
   ler a resposta antes da pergunta.
3. **Nunca cobrir rosto, mão nem arma.** Se não couber, o quadro tem texto demais —
   corte a fala ou divida em dois balões, não diminua a letra.
4. **Máximo de 25 palavras por quadro**, somando tudo. A regra vem da prática: acima
   disso a página vira texto ilustrado.
5. O rabicho aponta para a **boca**, não para o meio do corpo.

## Chamada de dentro de outra skill

```python
import baloes
baloes.desenhar(img, {"tipo": "fala", "em": [30, 16], "apontando": [44, 55],
                      "texto": "Senta aí, então."},
                caixa=(x, y, w, h), ref_px=largura_pagina / 2)
```

`caixa` é o quadro dentro da página, em pixels — as porcentagens do balão se referem a
ela. `ref_px` é a largura que vale por 1000 no cálculo do corpo da letra: passando a
mesma para todos os quadros, a letra tem o mesmo tamanho na página inteira, venha de um
quadro largo ou de um estreito. É assim que a `pagina-hq` usa.

O contorno de todas as formas é feito por dilatação de máscara (`MaxFilter`), não
desenhando forma por forma: por isso o rabicho gruda no balão sem deixar linha
atravessada, e por isso nuvem e estrela saem do mesmo código.
