# Entrada do Castelo de Ferrier — prompt do mapa (vista de cima)

Mapa de batalha para o roll6. **O problema de sempre dos geradores é desenhar a muralha, as torres e os objetos de lado** (fachada, tijolinhos, arcos em perfil, barris vistos de frente). Este prompt repete a regra de propósito, em vários lugares, e traz uma lista de erros e uma mensagem de correção.

**Formato para o roll6:** quase quadrado, **1220 × 1143 px** (20 colunas × 16 linhas de hexágonos, raio 40 px). Se o gerador só aceitar proporções fixas, use 16:15 ou 1:1 e eu redimensiono. **A grade é do roll6: a imagem sai sem hexágonos.**

## Prompt (inglês, rende melhor)

```
STRICT TOP-DOWN BATTLE MAP. ORTHOGRAPHIC VIEW FROM DIRECTLY ABOVE, LOOKING STRAIGHT DOWN AT EXACTLY 90 DEGREES, like a satellite photo or an architect's floor plan painted by hand. The camera is perpendicular to the ground. There is NO perspective, NO tilt, NO angle, NO horizon, NO sky, NO vanishing point, NO isometric, NO three-quarter view, NO bird's-eye-at-an-angle. Everything is a flat plan view.

THIS IS THE MOST IMPORTANT RULE: you must NEVER see the side of anything. Not the face of a wall, not the front of a tower, not the staves of a barrel, not the legs of a table, not the side of a cart. Only the TOP surface of each object is visible, as if each object were flattened.

How to draw each thing from directly above:
- WALLS: only the flat TOP of the wall, drawn as a thick solid band of light stone with a darker outline. The battlements (merlons) are small rectangular notches along the edge of that band, seen from above. NO brick rows on the wall face, NO windows, NO doors drawn in elevation, NO arrow slits seen from the front, NO wall face visible at all.
- TOWERS: seen from above they are CIRCLES. Show only the circular stone platform on top with a ring of small notches for the battlements. NO conical roof seen from the side, NO tower body, NO windows.
- THE DRY MOAT: a straight trench seen from above, a band of bare earth and stone about 6 m wide, with darker shading at the edges to show it is deep. NO moat wall face.
- THE DRAWBRIDGE: seen from above as a rectangle of wooden planks laid across the moat, with iron strips and two small round winches at its ends. It is DOWN (lowered), crossing the moat.
- THE GATE: a wide gap in the wall band, seen from above as the open passage floor (stone paving) between two thick wall bands, with two small iron-bracketed lanterns glowing on the sides. NO arch seen from the front.
- BARRELS: circles (the round lid seen from above, with a few curved lines for the wood), NOT cylinders seen from the side.
- TABLES: rectangles of wood seen from above. NO legs visible.
- CARTS: a flat plan view, a rectangle with two thin rectangles for the wheels at its sides and the shafts as two lines. NO side view of a cart.
- LAMPS AND TORCHES: small glowing dots with a soft warm pool of light on the ground.
- ROOFS OF HOUSES (in the corners): seen from above as flat shapes with tile lines; NO house walls visible.
- Shadows are short, soft, and fall straight down under the object; they must NEVER suggest a side face.

Subject: the main entrance of a medieval frontier castle at night, seen from above. A dirt road comes from the south (bottom of the image) and runs north (up) to the castle. Crossing the road from west to east at about the middle of the image is the dry moat, with the lowered wooden drawbridge. Immediately north of the moat is the castle wall (a thick light-stone band running west to east across the image) with the gate in the middle. Over the gate is the biggest round tower (a large circle). A smaller round tower (a circle) is at each end of the wall, near the left and right edges. Inside the gate, north of the wall, is a bit of the stone-paved courtyard.

Details on the ground: a big wooden table (a rectangle) just inside the gate on the left, with knives, an axe, a pruning sickle and belts lying on it as small top-down icons, and a small rack beside it; a short row of stone lanterns on iron hooks lighting the gate; at the south end of the bridge, on the dirt road, a handcart seen from above, three round barrel lids, two wicker baskets seen from above as small circles with weave patterns; patches of grass, a puddle, scattered straw and cart-wheel ruts on the road; flat tiled house roofs in the bottom-left and bottom-right corners, seen from above only. The road, bridge and gate passage are wide and clear so tokens can stand and walk there, with at least 2/3 of a hex of free width everywhere.

Style: hand-painted fantasy battle map, warm night lighting from lanterns, detailed stone and dirt texture, same look as a professional virtual tabletop (VTT) map. Landscape-ish, nearly square, 16:15.

Strictly NO characters, NO people, NO animals, NO text, NO labels, NO signature, NO grid lines, NO hexagons, NO border, NO UI, NO watermark. The map fills the whole canvas edge to edge; do not fade to black or add a vignette.

REMINDER: perfectly vertical top-down, 90 degrees. If any wall face, tower side, barrel side, table leg or cart side is visible, the image is WRONG.
```

## Prompt negativo (se o gerador tiver campo próprio)

```
perspective, angled view, isometric, three-quarter view, side view, front view, elevation, wall face, brick wall seen from the front, castle facade, tower side, conical roof, windows, arches seen from the front, doors seen from the front, barrel side, cylinder, table legs, cart side view, horizon, sky, clouds, vanishing point, depth of field, tilt-shift, cinematic camera, low angle, high angle, characters, people, animals, text, labels, grid, hexagons, border, vignette, watermark
```

## Se o resultado vier de lado

Mande esta mensagem de correção junto com a imagem errada:

```
This is wrong: I can see the face of the wall / the side of the towers / the sides of objects. Redraw it as a strict orthographic plan view from directly above (90 degrees, camera pointing straight down at the ground). Walls are only flat thick bands seen from their top, with notches for battlements. Towers are circles. Barrels are circles. Tables are rectangles. NOTHING is seen from the side. No perspective at all. Keep the same layout: road from the south, dry moat with the lowered drawbridge, wall band with the gate and the big round tower in the middle, a small round tower at each end.
```

## Notas para a máscara 3D (skill `criar-mascara`)

- Faixa da muralha e torres: `parede` (altura inteira). Torre do portão: `parede`.
- A passagem do portão fica vazia, com pelo menos 2/3 de hexágono de largura.
- Mesa do armeiro: `mesa`. Barris: `muro-alto`. Carrinho: `rocha-grande` ou `muro-alto`.
- A ponte e a estrada ficam vazias. O fosso seco é piso, sem altura.
- Telhados dos cantos: `parede`.

## Perguntas em aberto

- Se o mapa inclui um trecho do pátio dentro do portão ou só a entrada.
- Se a fila de funcionários e o armeiro devem aparecer no desenho ou ficar para as peças do roll6.
