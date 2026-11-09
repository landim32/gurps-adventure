# Casa de apostas do mercado de Ferrier — prompt do mapa

Mapa de batalha visto de cima, no mesmo estilo da taberna *Gota Seca* (`cenarios/taberna.jpg`).

**Formato para o roll6:** paisagem, **1220 × 1005 px** (20 colunas × 14 linhas de hexágonos, raio 40 px). Se o gerador só der proporções fixas, use 5:4 e redimensione depois. **A grade é do roll6: a imagem sai sem hexágonos.**

## Prompt (inglês, rende melhor nos geradores)

```
Top-down battle map for a tabletop RPG, strictly 90 degrees overhead view, no perspective, no tilt. Hand-painted fantasy illustration, dark warm palette, detailed wood grain and cobblestone texture, soft shadows cast straight down, same look as a professional VTT tavern battle map. Night scene lit by oil lamps and a single lantern outside. Landscape, 5:4.

Subject: a small illegal gambling house in the market quarter of a medieval frontier town, and the street around it.

The house sits in the upper-middle of the image, rectangular, roughly 60% of the width and 55% of the height, with thick timber-and-plaster walls (clearly visible, thick, dark) and a tiled roof NOT drawn: show the interior with the roof removed. A single wide double door in the middle of the south wall (opening to the street), plus one small shuttered window on the east wall and a narrow back door in the north wall. Above the front door, on the outside, a single bone die nailed to the wall, no sign.

Interior, crowded but walkable with wide gaps between furniture: four round and square gambling tables with worn green felt and wood tops, scattered dice, coins, wooden cups and playing cards; one long table with a dice-throwing tray; a corner table under the only hanging oil lamp, with a small pile of coins on one side and a big pile on the other; rough stools and benches; a small counter with bottles and mugs in the northeast corner; a few barrels and a crate against the walls; a worn rug; a stained wooden floor with scattered coins and sawdust. Candle stubs and lamps casting warm pools of light.

Exterior (the rest of the image, about 40%): a muddy cobblestone market street running along the south and east sides, wide enough for a cart. Two closed market stalls with patched canvas awnings on either side of the house, a parked handcart with sacks, stacked barrels and crates, a puddle, a hitching post, a streetlamp lantern on a post near the door, hay and trash on the stones, a narrow alley on the west side between the house and a neighbouring wall, a distant glimpse of other stall roofs at the edges.

Strictly NO characters, NO people, NO animals, NO text, NO labels, NO signature, NO grid lines, NO hexagons, NO border, NO UI. Furniture is clearly separated from walls so tokens can stand between them. Do not fade the edges to black: the map fills the whole canvas.
```

## Notas para a máscara 3D (skill `criar-mascara`)

- Paredes da casa: altura inteira (`parede`).
- Balcão do canto: `balcao`.
- Mesas de aposta: `mesa`.
- Barris e caixotes: `banco` ou `estante`, só os que forem obstáculo contínuo.
- Barracas fechadas e carrinho: `rocha-grande` ou `muro-alto`.
- Portas e portão: vazios, com **pelo menos 2/3 de hexágono** de largura. Deixe a porta da frente larga.

## Perguntas em aberto

- Se a casa precisa de um segundo andar ou de um porão (por exemplo, uma sala de jogo privada).
- Se o mapa fica só com a rua em frente ou inclui o mercado maior ao redor.
