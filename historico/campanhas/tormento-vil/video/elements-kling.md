# Elements do Kling — elenco do filme *Tormento Vil 1*

Personagens criados como **Element de imagem** no Kling (criados em 10/11/2026). Para usar numa
geração, escreva `<<<id>>>` no prompt e passe `elements: [{"id": "...", "bindName": "Nome"}]`.
Elements de imagem funcionam em `image_to_image` (inclusive `kling-image-o1`) e nos modelos de
`image_to_video` que aceitam `elements`. `text_to_image` e `text_to_video` não aceitam element.

| Personagem | Element ID | Capa | Imagens secundárias |
|---|---|---|---|
| Comam Obabaroy | `326313412310127` | `historico/personagens/comam-obabaroy/foto.png` | `foto-corpo.png`, `tokens/comam/comam-front.png`, `tokens/comam/comam-back.png` |
| Irmão Kaelric | `326313414316891` | `historico/personagens/irmao-kaelric/foto.png` (recortada, sem a marca "Made with AI") | `corpo-inteiro.png` |
| Jah Kagadu | `326313418650992` | `historico/personagens/jah-kagadu/foto.jpg` | recorte do rosto da mesma foto |
| Negrum Carneiriums | `326313426317293` | `historico/personagens/negrum-carneiriums/foto-old.png` (de tanga, como na ficha) | `tokens/negrum/negrum.png`, `negrum-front.png`, `negrum-back.png` |
| NelsOwned | `326313431668218` | `historico/personagens/nelsowned/foto.png` | `corpo-inteiro.png`, `foto-original.png` |

## Como gerar imagens que saiam fiéis (aprendido em 10/11/2026)

- **O element sozinho não segura o rosto.** Com só o `<<<id>>>` no prompt, o Kling devolveu
  pessoas genéricas (o Kaelric virou um monge careca). O que funciona:
  1. `kling-image-o1` (o `kling-image-v3_0_omni` mistura personagens quando há mais de um);
  2. **a foto do personagem como imagem de referência** (`image_2`, `image_3`…) e o prompt
     dizendo "o homem de 图片2…", com o element junto como apoio;
  3. o cenário como `image_1` **sem nenhum personagem**: use `cenas/01/00-taberna-vazia.png`
     para a Âncora Quebrada. Um cenário com gente passa traços para os outros (a barba ruiva
     com contas do NelsOwned foi parar no Kaelric);
  4. no `bindName`, o nome exato do element no Kling (`Irmão Kaelric`, `Comam Obabaroy`…).
- Peça o estilo das ilustrações dos elements (pintura de fantasia sombria), não
  "fotorrealista".
- Sem a palavra "sheep"/"shepherd" no prompt da taberna: o modelo põe ovelha dentro do salão.

Notas de continuidade:

- **NelsOwned** perde a **mão esquerda** no cap. 6 (Maneta, amputada). As imagens do element
  mostram as duas mãos; da fuga para o deserto em diante, peça no prompt "sem a mão esquerda,
  coto enfaixado".
- **Negrum** foi criado com a tanga da ficha. A `foto.png` com armadura de escamas é posterior e
  não entrou: no cap. 7 ele **não vestiu** a armadura dos reptantes.
- **Jah** só tinha uma imagem utilizável; a secundária é o recorte do rosto da própria foto.
