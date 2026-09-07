---
name: token-hex-gurps
description: >
  Gera uma miniatura top-down (token) de um personagem ou NPC de GURPS para
  colar num mapa hexagonal (1 hex = 1 m). Lê a ficha em personagens/<slug>/
  (ou o bloco Farvaro de um NPC) e produz uma imagem 1:1 vista de cima.
  Use when the user asks to "token hex", "miniatura do mapa", "top-down do
  personagem", "token de combate", "figura para o hexágono", ou /token-hex-gurps.
---

# Token top-down para mapa hexagonal

Antes de gerar: leia as skills **imagine** e **game-asset-core** (não copie as
regras delas para cá). Se o mesmo personagem já tiver retrato, leia também
**game-character-consistency**.

O hexágono do GURPS é **1 metro**. A figura cabe em **um hex**; a imagem é
quadrada para sentar no hex sem distorcer.

## Fonte

1. Localize `personagens/<slug>/personagem.json` (slug kebab-case). JSON é a
   fonte da verdade. Se não houver pasta, aceite o bloco Farvaro de um NPC ou
   uma descrição curta.
2. Extraia só o que se **vê de cima**: `aparencia`, `raca`, `idade`,
   `armas_objetos` (armas visíveis + peças de armadura), vantagens/desvantagens
   com efeito visual (tapa-olho, cicatriz, nanismo, gigantismo, orelhas élficas,
   barba anã…). Ignore pontos, NH e custos.
3. Se existir retrato (`foto.png` / `foto` no JSON / `foto-prompt.md`), use-o
   como referência de identidade. Senão, derive o visual do JSON como a skill
   `criar-personagem-gurps` faz no `foto-prompt.md` — sem reler aquela skill
   inteira; o campo `aparencia` + equipamento bastam.

## Gerar

`aspect_ratio`: **1:1**.

- **Com retrato:** `image_edit` a partir da foto. Prompt: manter o mesmo
  personagem (rosto, cores, roupa, armas); mudar **só** a câmera para vista
  de cima.
- **Sem retrato:** `image_gen`.
- Vários personagens no mesmo pedido: uma imagem por pessoa, cada uma a partir
  da própria ficha/foto.

Prompt em inglês, 2–5 frases, nesta ordem:

1. **Câmera:** *true orthographic top-down view, camera exactly 90 degrees
   above the ground, looking straight down at the crown of the head*. O
   personagem fica em pé, cabeça no centro, pés apontando para baixo da imagem
   (frente GURPS = topo do hex). **O rosto não pode aparecer:** nada de olhos,
   sobrancelhas, nariz, boca, sorriso ou queixo; só o topo da cabeça, cabelo,
   elmo/capuz e a linha dos ombros podem ser vistos. Não é retrato, não é ¾,
   não é perspectiva de olho de gente. **Anatomia sem foreshortening:** trate a
   figura como uma silhueta plana observada de cima; tronco, coxas, pernas e
   pés mantêm larguras proporcionais e ficam alinhados no mesmo plano. As
   pernas não avançam, não parecem maiores nem ficam deslocadas para a frente;
   os pés são pequenos e vistos apenas por cima. A exigência de 90° vale para
   **todo** o corpo, não só para a cabeça: não mostre peito, abdômen, frente
   das coxas, canelas, solas ou laterais em perspectiva. Se a anatomia de uma
   pessoa em pé induzir uma pose ¾, gere uma ilustração de miniatura 2D plana
   (como uma peça de jogo de tabuleiro vista de cima), e não um humano 3D
   fotografado de cima.
2. **Sujeito:** raça, idade, cabelo/barba visíveis no topo da cabeça, compleição.
3. **Equipamento visto de cima:** elmo/capuz, ombros da armadura, escudo no
   braço, arma no chão ao lado ou ao longo do corpo (cimitarra, besta nas
   costas = retângulo no dorso). Material/cor, sem DP/RD.
4. **Estilo:** ilustração de token de RPG de mesa, traço limpo, cores chapadas,
   silhueta legível à distância. Mesmo tom do retrato se houver.
5. **Fundo:** cor lisa única, bem contrastante (verde-chroma `#00FF00` ou
   branco puro). Personagem isolado, sem chão, sem sombra projetada, sem
   hexágono desenhado, sem texto.

## Verificar e gravar

Descreva o que a imagem mostra **antes** de reler a ficha. Faça esta checagem
antes de aceitar: se qualquer parte do rosto (olhos, nariz, boca, barba sob o
queixo) estiver visível, a câmera não está a 90° e a imagem falhou. Falhou
(ângulo errado, retrato em vez de topo, fundo de cenário, arma sumiu)? Uma
tentativa de correção com `image_edit`, exigindo *no facial features visible;
only the crown of the head*. Se o ângulo continuar ¾, gere de novo com câmera
ainda mais explícita (*bird's-eye, exactly 90 degrees overhead, looking
straight down at the crown of the head; face fully hidden by geometry*).

Grave em `personagens/<slug>/token-hex.png` (NPC sem pasta:
`npcs/<slug>-token-hex.png`). Informe o caminho e o hex que ela ocupa (padrão:
1 hex, humano; Centauro/Gigante: diga 2–3 se o tamanho racial exigir).
