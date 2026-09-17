# Prompt — `cenario-salao.png`

**Versão em vigor:** sépia, gerada em 16/09/2026 · `gpt-image-1` · 1536×1024 · qualidade
`high` · **sem imagem de referência** (`/generations`) · **1 chamada**

**Versão anterior:** a mesma taberna em **cor quente**, gerada mais cedo no mesmo dia e
aprovada na época. Foi substituída quando o volume adotou o partido de lápis e nanquim
sobre papel tonalizado: uma referência colorida brigaria com os 75 quadros que a usam.

> **Nota de manutenção.** A `escrever_prompt()` da skill `quadro-hq` grava este arquivo
> sozinha depois de gerar, e ao fazê-lo apaga tudo o que estiver escrito aqui, deixando só
> o bloco do prompt. A documentação abaixo foi reposta à mão **depois** da geração; o bloco
> de código no fim é o prompt literal que foi enviado. Se este cenário for regerado,
> reponha a documentação de novo.

**O que é.** O estabelecimento do salão d'*A Âncora Quebrada*, gerado **para este volume**
e usado como referência de cenário em **75 dos 127 quadros**. Segura a geografia da taberna
de uma página para a outra, e agora também o partido gráfico.

**Por que não uso as ilustrações do plano.** `inicio.jpg` e `mortos-vivos-na-porta.jpg` são
a mesma taberna, mas anteriores à errata de cenário: as duas têm porto — mastros de navio
pelas janelas e pela porta aberta, um leme na parede. Wallace é feudo de pastores na orla
do Grande Deserto e **não tem porto** (*Fantasy*, pág. 72).

## A conferência desta versão

| O que a planta `cenarios/taberna3.png` manda | Saiu? |
|---|---|
| **Partido sépia igual ao do elenco** | ✅ Mesmo papel tonalizado, mesma hachura a grafite, mesma aguada contida do avatar do Hoel |
| **Fogo contado por valor** | ✅ O papel fica mais nu perto da lareira; a hachura adensa até o preto nos cantos longe dela |
| Balcão comprido à direita, com prateleiras de garrafas | ✅ |
| Lareira grande com fogo forte, na mesma parede direita | ✅ |
| Tapete no meio, com a mesa comprida e os bancos | ✅ — mas **sem vermelho**: num volume de matiz única não há como a cor aparecer. Ele se lê pela borda e pela textura |
| Escada | ✅ Inteira, em primeiro plano à esquerda, com corrimão e degraus |
| Porta dupla ao fundo, à esquerda | ✅ |
| **Boca do corredor dos fundos** _(conserto 2)_ | ✅ Vão em arco, escuro, levando para a sombra |
| **Nenhuma âncora dentro do salão** _(conserto 3)_ | ✅ Parede do fogão lisa; nenhuma âncora em lugar nenhum |
| Salão completamente vazio | ✅ Sem gente, sem bicho |
| Sem mar, mastro, leme, rede | ✅ |
| Sem letra nenhuma | ✅ |
| **Segunda lareira, menor, à esquerda** | ❌ **Não saiu.** Aquele canto tem escada, porta, nicho e o vão do corredor — lareira nenhuma |
| **Braseiro de ferro** _(conserto 1)_ | ❌ **Falhou pela segunda vez.** Saiu de novo um caldeirão fundo de três pés, e desta vez vazio, sem brasa nenhuma — apesar de o prompt dizer "wide shallow metal pan of glowing coals on three short iron legs, NOT a cooking cauldron and NOT a pot" |

**Duas observações que não estavam na lista:**

- **As paredes saíram de pedra**, não de tábua. O assoalho, as vigas, o mobiliário e a
  escada são de madeira, e é deles que o incêndio da página 21 se alimenta — mas o registro
  descreve a casa como de madeira. Os quadros das páginas 17, 18 e 21 já dizem no próprio
  `visual` de onde vem o fogo (serragem, bancos virados, mesas secas), então a discrepância
  não precisa ser corrigida na referência.
- **Não há janelas.** O prompt pedia janelinhas escuras; o gerador fechou as paredes. Sem
  prejuízo — e com a vantagem de não haver por onde um mar aparecer.

## O canto sudeste continua por resolver

Os dois itens que falharam são vizinhos, e são os dois que o volume mais precisa: **a
segunda lareira (L10–L11)** contra a qual o morto é projetado na página 18, e **o braseiro
de ferro (M11)**, de onde o incêndio começa na página 21. Cerca de **18 quadros** se passam
nesse canto, nas páginas 17, 18 e 21.

Por ora eles são carregados pelo texto de cada quadro, que já descreve os dois. Se o
primeiro quadro daquele canto sair errado no passo 9, a saída é gerar **uma referência de
detalhe só do canto sudeste** e usá-la como `cenario` naqueles quadros.

## O prompt enviado

```
Hand-drawn comic art in pencil and ink on warm buff toned paper: firm dark ink contour lines, fine graphite hatching and crosshatching for all modelling and shadow, over a restrained wash of sepia and warm grey with only a slight flesh tint. The buff paper tone is the lightest value in the image and shows through everywhere; highlights are bare paper, never white paint. Muted, almost monochrome warm palette — no flat digital colour, no vivid saturation, no glossy rendering. FIRELIGHT IS RENDERED AS VALUE, NOT AS HUE: the nearer the fire, the more paper is left bare and the sparser the hatching; the further from it, the denser and blacker the ink, until the far corners are solid shadow. Medieval realism, tech level 3, no gunpowder. Setting: Wallace, a pastoral frontier town of Caithness on the edge of the Great Desert in Yrth — sheep pens, wool, dust and stone. THIS TOWN IS LANDLOCKED: no sea, no harbour, no docks, no ships, no boats, no masts, no rigging, no ship's wheel, no nets, no fishing gear anywhere in the image. Establishing interior of a frontier tavern called The Broken Anchor, at night, COMPLETELY EMPTY OF PEOPLE — the room only, so it can be used as a background reference. Wide three-quarter view from the top of a wooden staircase in the far corner, looking down and across the whole room. Layout, exactly: a long timber BAR runs along the wall on the RIGHT, with shelves of bottles and jugs behind it, and immediately beside the bar on that same right-hand wall a BIG STONE FIREPLACE with a strong fire burning in it, a bench and a round table near its warmth; in the MIDDLE of the plank floor a RED CARPET carrying the house's long table and benches; on the LEFT, in the far corner, a SECOND AND SMALLER STONE HEARTH, and standing on the floor beside it a LOW IRON BRAZIER — a wide shallow metal pan of glowing coals on three short iron legs, NOT a cooking cauldron and NOT a pot; a heavy double FRONT DOOR in the far wall just to the left of that corner, shut, rain darkening the boards at its foot; and past the end of the bar, clearly visible, the dark open MOUTH OF A NARROW BACK CORRIDOR leading away into shadow. NO ANCHOR ANYWHERE INSIDE THIS ROOM: the tavern's iron anchor hangs outdoors over the front door and is not visible from in here — no anchor on the walls, no anchor carved in stone, no anchor over the fireplace. Sawdust on the floor, round tables and stools, hanging oil lanterns on chains, low ceiling beams, small dark windows showing nothing outside but night, fine rain, mud and low thatched roofs. Two sources of firelight, one strong on the right and one small on the left, the rest of the room falling away into dense hatched shadow. No people, no figures, no animals. no text, no lettering, no speech balloons, no captions, no signage, no watermark, no panel borders, no frame.
```
