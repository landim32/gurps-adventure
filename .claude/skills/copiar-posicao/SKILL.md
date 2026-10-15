---
name: copiar-posicao
description: >
  Copia a pose de uma imagem para um modelo 3D (.glb, esqueleto Mixamo) por tentativa e erro:
  põe o modelo com o mesmo enquadramento e o mesmo zoom da imagem, ajusta os giros do esqueleto,
  renderiza, compara a silhueta com a referência e repete até a pose ficar igual. No fim grava a
  animação no formato "roll6-animation" (mesmas regras da skill criar-animacao) e a última
  imagem do modelo já na pose. Use when the user asks "/copiar-posicao", "copiar a pose da imagem
  para o modelo", "colocar o .glb na mesma posição da foto", "animação exatamente como a imagem",
  "ajustar o esqueleto até ficar igual à imagem".
---

# Copiar posição

Irmã da `criar-animacao`: ela **estima** os giros olhando a imagem; esta **mede**. O modelo 3D é
posto no mesmo enquadramento da imagem, desenhado, comparado, corrigido — e assim por diante até
a silhueta casar. O formato de saída, os ossos, os eixos e os sinais são os da `criar-animacao`
(leia a tabela de eixos e a receita das mãos no `SKILL.md` dela antes de escrever giros).

## Entrada

1. **Uma imagem** da pose (foto, arte, render). Fundo liso ou PNG com alfa dão a melhor silhueta;
   com fundo complexo o script recorre ao GrabCut e a máscara pode errar (veja `*-comparacao.png`).
2. **Um modelo `.glb`** com esqueleto Mixamo (`Hips`, `Spine`, `LeftArm`… com ou sem `mixamorig:`).
   Confira antes: `python .claude/skills/copiar-posicao/scripts/renderizar.py modelo.glb --info`
   (diz se é Mixamo e se a esquerda do personagem está em +X, como o Roll6 espera).
3. Nome e **tipo** da animação (`idle`, `defend`, `crouch` repetem; `defeated`, `attack` tocam
   uma vez). `walk` e `run` são movimento, não pose: use a `criar-animacao`.

## Scripts (só numpy, Pillow e OpenCV; sem OpenGL)

| Script | O que faz |
|---|---|
| `scripts/renderizar.py <glb> <ref> <pose.json> --saida <base> [--esqueleto]` | deforma o modelo pela pose, desenha do tamanho da imagem, **ajusta posição e zoom à silhueta da referência**, grava `<base>.png` e `<base>-comparacao.png` (referência \| modelo \| sobreposição) e imprime a **IoU** e o desvio dos centros |
| `scripts/otimizar.py <glb> <ref> <pose.json> --saida <pose-otim.json>` | **refina** uma pose já escrita: mexe um giro por vez, mantém o que sobe a **nota** (IoU − erro médio dos `alvos`), passos de 12°, 6° e 3°. Não acha a pose do zero e **não substitui olhar a imagem** |
| `scripts/gerar.py <pose.json> --nome … --tipo … --modelo <glb> --ref <img>` | monta a animação, valida com o `validar.py` da `criar-animacao`, grava `animacoes/<slug>.json` e a imagem final `animacoes/<slug>.png` |
| `scripts/glb.py` | biblioteca: lê o .glb e deforma a malha com a convenção do formato |

Na sobreposição: **verde** = só a referência (o modelo ficou curto ali), **vermelho** = só o modelo
(passou), **cinza** = os dois. Com `--esqueleto` as juntas saem desenhadas com o nome do osso.

### O arquivo de pose

```json
{
  "camera": {"yaw": 0, "pitch": 0, "fov": 30, "ajuste": "altura"},
  "graus": {"Spine": [12, 5, 0], "RightArm": [-40, 0, -12], "RightForeArm": [-115, 0, 0]},
  "hipsLift": -0.05, "hipsLiftDe": "height",
  "alvos": {"RightHandMiddle2": [515, 285], "RightForeArm": [290, 470], "LeftLeg": [820, 1010]},
  "descricao": "uma linha para a biblioteca"
}
```

`graus` e `hipsLift` são os mesmos números que vão para a animação. `camera`, `alvos`, `excluir` e
`limites` só existem para casar a pose e **não vão** para o arquivo final.

- **`excluir`**: polígonos `[[x, y], ...]` (pixels da imagem) tirados da silhueta da referência — a
  arma, o escudo ou o cenário que o modelo não tem. Sem isso a IoU puxa os ossos para cobri-los.
- **`limites`**: `{"Spine": [[-5, 5], [-15, 15], [-10, 10]]}` aperta a faixa de X, Y e Z de um osso no
  `otimizar.py`. **Use no tronco e na cabeça**: o modelo quase nunca tem as proporções da imagem, e a
  busca compensa inclinando o corpo para a frente, o que fica torto (o ogro saiu "caindo para a frente").

**`alvos` são a parte mais importante.** A silhueta sozinha não separa um braço levantado de um
braço cruzado sobre o peito (os dois ficam dentro do contorno). Marque na imagem, em **pixels da
imagem de referência**, onde cada junta deve cair: `*HandMiddle2` (centro do punho), `*Hand` (pulso),
`*ForeArm` (cotovelo), `*Leg` (joelho), `*Foot` (tornozelo), `Hips`, `Neck`, `HeadTop_End`. Lembre
que `Right*` é o lado **direito do personagem** — numa imagem de frente, a esquerda de quem olha.
O `renderizar.py` desenha cruz verde no ponto marcado e losango magenta onde a junta caiu, e imprime
o erro em pixels de cada uma. Meça os pontos na imagem (Read nela) em vez de chutar.

## Fluxo

1. **Leia a imagem.** Anote a pose em palavras (tronco, cabeça, cada braço e antebraço, cada
   coxa e canela, abertura das pernas, para onde o corpo está virado) e **o ângulo de visão**: a
   imagem está de frente, de 3/4, de lado? vista de cima ou de baixo?
2. **Enquadramento.** Comece com `yaw` 0, `pitch` 0, `fov` 30 e `ajuste: "altura"`. O script já
   casa **posição e zoom** com a caixa da silhueta; você corrige só o **ângulo**: `yaw` (+ gira a
   câmera para a esquerda do personagem), `pitch` (+ sobe a câmera) e `fov` (menor = mais chato,
   maior = mais perspectiva). Se o corpo na imagem está virado e a câmera é frontal, prefira girar
   o corpo (`Hips` Y, `Spine` Y) a girar a câmera — a animação **só leva os giros do corpo**.
3. **Primeira pose** pela tabela de eixos da `criar-animacao`. Rode o `renderizar.py` e **olhe o
   `*-comparacao.png`** (Read na imagem): a IoU diz se melhorou, a imagem diz onde.
4. **Corrija em ciclos.** Uma ou duas mudanças por vez, nas partes **mais erradas** primeiro
   (pernas e tronco → braços → cabeça → mãos). Compare com a tentativa anterior: a IoU subiu,
   mantém; desceu, desfaz. Use `--esqueleto` quando não souber que osso mexer.
   - Os giros **somam pela corrente**: o giro de cada osso é carregado pelos ossos pai.
   - **Antebraço: não vale a regra "X negativo dobra o cotovelo" da `criar-animacao`.** O Roll6
     aplica o giro do antebraço no referencial da **pose T** do osso (a conta está em `glb.py`,
     lida do código do Roll6): num rig em T o antebraço aponta para ±X, então **X é torção**,
     **Y dobra o cotovelo para a frente (negativo na esquerda, positivo na direita)** e Z o dobra
     para o lado. Foi o erro que fez o "Orc Brigão" abrir os braços no Roll6 enquanto a prévia
     mostrava a guarda. Confirme sempre pela prévia, que repete a conta do Roll6.
   - **Dedos e mãos:** o desenho do modelo mostra os dedos que você girar; use a receita das mãos
     da `criar-animacao` para punho, segurar ou relaxar.
5. **Marque os alvos e refine.** Com 6 a 10 `alvos` (mãos, cotovelos, joelhos, pés, quadril, topo da
   cabeça), rode o `otimizar.py` a partir da sua pose e **olhe o resultado**: a nota pode subir
   escondendo um braço dentro do torso ou invertendo um cotovelo. Se o erro de um alvo não baixa,
   o ponto está mal marcado ou o modelo tem proporção diferente da imagem (braço mais curto, ombro
   mais largo) — aceite a diferença em vez de forçar um osso a 150°.
6. **Pare** quando a IoU estabilizar (alguns pontos abaixo de 1,0 é normal: a silhueta inclui
   escudo, armas e roupas que a imagem tem e o modelo não) e a sobreposição não mostrar membro
   fora do lugar. Mínimo de **3 rodadas**; passe de **8** só se ainda houver erro visível.
7. **Gere** com o `gerar.py` (passe `--modelo` e `--ref` para sair também a imagem final). Ele só
   entrega arquivo que passou no `validar.py`.
8. **Mostre ao usuário** a imagem final ao lado da referência e diga a IoU. A animação **só vai
   para o Roll6 se o usuário pedir** (`enviar.py` da `criar-animacao`).

## Limites (diga ao usuário)

- **IoU alta não prova que a pose está certa.** Chegou a 0,89 com os dois punhos escondidos na
  barriga. Confira sempre os `alvos` e a imagem lado a lado.
- **A silhueta é o critério, não a profundidade.** Um braço para a frente e um para o lado podem
  ter a mesma silhueta numa vista frontal. Leia o *interior* da imagem (sobreposição de partes,
  sombras) e, se ficar ambíguo, pergunte ou peça outra vista.
- **O desenho é uma prévia por software**, sem iluminação nem texturas fiéis; serve para
  comparar pose, não para conferir acabamento. Modelos de poucos polígonos ficam facetados.
- **O desenho repete a conta do Roll6** (lida do código dele, `loadModel-*.js` do site): Euler
  "XYZ" do three.js (R = Rx·Ry·Rz), o braço relaxado só entra no osso `*Arm` **e só se a animação
  tiver trilha para ele** (alvo `[±0,3, −1, 0,05]` em `BRACO_ALVO`), e cada giro age sobre a pose
  de descanso do osso e acumula pela hierarquia. Se o Roll6 mudar essa conta, ajuste `glb.py`.
- Exagero acima de ~120° fora de ombro e quadril pode rasgar a malha no Roll6.

## Erros comuns

- **Modelo de costas ou espelhado:** `--info` avisa quando a esquerda não está em +X. O Roll6
  assume +X = esquerda; nesse modelo as animações sairiam espelhadas.
- **Máscara da referência errada** (sombra, chão, cenário contado como corpo): o ajuste de zoom
  sai torto. Recorte a imagem ou use um PNG com alfa.
- **Ajustar a câmera para esconder um erro de pose:** a câmera não entra na animação.
- **Mudar tudo de uma vez:** perde-se a causa da melhora ou da piora.
- **Osso inventado:** só os 52 ossos da lista da `criar-animacao`.

## O que esta skill não faz

- Não estima profundidade nem reconstrói a pessoa da imagem: ela **ajusta o esqueleto do modelo
  dado** até a silhueta casar.
- Não anima movimento (de vídeo ou de quadros), só pose.
- Não edita o `.glb` nem escolhe a animação no token.
