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

Notas de continuidade:

- **NelsOwned** perde a **mão esquerda** no cap. 6 (Maneta, amputada). As imagens do element
  mostram as duas mãos; da fuga para o deserto em diante, peça no prompt "sem a mão esquerda,
  coto enfaixado".
- **Negrum** foi criado com a tanga da ficha. A `foto.png` com armadura de escamas é posterior e
  não entrou: no cap. 7 ele **não vestiu** a armadura dos reptantes.
- **Jah** só tinha uma imagem utilizável; a secundária é o recorte do rosto da própria foto.
