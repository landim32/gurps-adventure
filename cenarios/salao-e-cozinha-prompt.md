# Salão do Trono e cozinha do castelo — prompt do mapa (vista de cima)

Mapa de batalha para o roll6: o **Salão do Trono** (24 × 24 m, 16 pilastras, estrado, mezanino) ao lado da **cozinha**, com o **açougue** (um quarto dentro da cozinha). **O problema de sempre dos geradores é desenhar paredes, pilastras, móveis e portas de lado** (fachada, tijolinhos, pernas de mesa, portas de frente). Este prompt repete a regra de propósito, em vários lugares, e traz uma lista de erros e uma mensagem de correção.

**Formato para o roll6:** paisagem, **2420 × 1697 px** (40 colunas × 24 linhas de hexágonos, raio 40 px, 1 hexágono ≈ 1 m). Se o gerador só aceitar proporções fixas, use 10:7 ou 3:2 e eu redimensiono. **A grade é do roll6: a imagem sai sem hexágonos.** Se preferir dois mapas separados (salão e cozinha), é só dizer e eu divido o prompt.

**Planta:** o Salão fica à direita (leste), quadrado. A cozinha fica à esquerda (oeste). Entre os dois há uma passagem estreita de criados com uma porta em cada ponta. O açougue é um quarto pequeno no canto noroeste da cozinha.

## Prompt (inglês, rende melhor)

```
STRICT TOP-DOWN BATTLE MAP. ORTHOGRAPHIC VIEW FROM DIRECTLY ABOVE, LOOKING STRAIGHT DOWN AT EXACTLY 90 DEGREES, like an architect's floor plan or a satellite photo of an interior with the roof removed, painted by hand. The camera is perpendicular to the floor. There is NO perspective, NO tilt, NO angle, NO horizon, NO vanishing point, NO isometric, NO three-quarter view, NO dollhouse cutaway view. Everything is a flat plan view.

THIS IS THE MOST IMPORTANT RULE: you must NEVER see the side of anything. Not the inner face of a wall, not the front of a pillar, not the legs of a table, not the back of a chair seen from the side, not the front of a stove, not a door seen from the front. Only the TOP surface of each object is visible, as if every object were flattened onto the floor plan. No wall faces, no brick rows, no windows, no arches in profile, no hanging objects seen from the side.

How to draw each thing from directly above:
- WALLS: only the flat TOP of the wall, drawn as a thick solid band of dark stone (about 1 m thick) with a darker outline. NO wall face visible at all, no bricks on the faces, no shading that suggests a vertical surface.
- PILLARS: perfect SQUARES of stone (about 1.5 m wide), seen from the top, with a thin darker outline. NO column shaft, NO capital, NO shadow suggesting height.
- DOORS: a gap in the wall band, with the door leaf shown as a thin rectangle lying in plan view (closed: across the gap; open: swung to one side as a thin line with its hinge dot). NO door seen from the front, NO door handle in elevation. Doors are at least 2 m wide.
- STAIRS: parallel lines (the steps) seen from above, with a darker end where they go down. NO stair side profile.
- TABLES: rectangles of wood (or circles) seen from above, with a white cloth, small round plates, cups and bread as tiny top-down icons. NO legs visible.
- BENCHES: long thin rectangles. CHAIRS and THRONE: the seat seen from above as a rounded rectangle with the back as a thick line on one side; NO front view of a chair.
- BARRELS: circles (the round lid seen from above, with a few curved lines), NOT cylinders seen from the side. SACKS: lumpy rounded shapes seen from above. BASKETS: small circles with weave pattern.
- STOVES AND FIREPLACES: a rectangle of dark iron or stone seen from the top, with glowing orange circles for the fire holes and a few embers. NO front opening, NO chimney seen from the side.
- BRAZIERS: circles of iron with an orange glow and flame seen from above.
- POTS AND CAULDRONS: circles seen from above with steam as soft swirls. HANGING RACKS (pans, sausages, hooks): drawn only as small circles and dots where things hang, with a thin line for the rail. NEVER hanging objects seen from the side.
- BALCONY / GALLERY (mezzanine): a band 3 m wide running along the four inside walls of the hall, drawn as a slightly lighter wooden floor with a thin balustrade line on its inner edge and small square posts. It is seen only from above.
- Shadows are short, soft, and fall straight down under the object; they must NEVER suggest a side face.

Subject: the throne hall and the kitchen of a medieval frontier castle on the night of a banquet, seen from above, with the roof removed.

LEFT SIDE (west): the KITCHEN, a stone-floored room about 14 m wide and 12 m tall. Along its north wall, two big iron stoves with glowing fire holes and a large hearth. In the middle, a long wooden work table with cutting boards, knives, bowls and a half-cut loaf, seen from above. Along the west wall, wash tubs (circles), barrels, sacks and baskets. Round pots and cauldrons on the stoves with steam. A sturdy wooden table with a roast on a platter. In the south-west corner, a stairway going down (steps seen from above, dark at the bottom) to the pantry. In the north-west corner, a small room about 6 m by 6 m: the BUTCHER'S ROOM (the "açougue"), with a thick butcher's block (a round wooden stump seen from above), a long stone slab table with a cleaver rack, a salt barrel, a drain grate in the floor, and rows of small hook dots on the rail where meat hangs (dots only, no side view). The butcher's room has one door to the kitchen. The kitchen has a door to the outside yard on its west wall and a door on its east wall into a narrow servants' passage (2 m wide, 6 m long) that leads east to the hall.

RIGHT SIDE (east): the THRONE HALL, a square room 24 m by 24 m with a dark flagstone floor. Sixteen square stone pillars (1.5 m each) in 4 rows of 4, spaced 5 m apart, in the middle of the hall. The gallery band (3 m wide) runs around the four walls. At the north end of the hall, a raised dais: three nested rectangles with steps (lighter and darker bands), a heavy stone-and-dark-wood throne seen from above, and a long wooden table in front of it. Long banquet tables with white cloths run along the pillar rows, with benches, plates, cups and candles as tiny top-down icons, always leaving open walkways at least 2 m wide. In the four corners and near the dais, round iron braziers with orange glow. On the south wall, a great double door (two thin door leaves, open, swung inward) in the middle; in the south-west and south-east corners, two small servants' doors; on the north wall, one door on each side of the dais: the left one leads to a stair (steps seen from above) and the right one is a heavy iron door. The south-west servants' door connects to the servants' passage that leads west to the kitchen. A worn rug runs from the great door toward the dais.

Style: hand-painted fantasy battle map, warm torch and candle lighting, detailed stone and wood texture, the same look as a professional virtual tabletop (VTT) map. Landscape, 10:7.

Strictly NO characters, NO people, NO animals, NO text, NO labels, NO signature, NO grid lines, NO hexagons, NO border, NO UI, NO watermark. The map fills the whole canvas edge to edge; do not fade to black or add a vignette.

REMINDER: perfectly vertical top-down, 90 degrees. If any wall face, pillar side, table leg, stove front, door front, or hanging object seen from the side is visible, the image is WRONG.
```

## Prompt negativo (se o gerador tiver campo próprio)

```
perspective, angled view, isometric, three-quarter view, side view, front view, elevation, dollhouse view, cutaway view, wall face, brick wall seen from the front, interior wall faces, pillar shaft, column capital, windows, arches seen from the front, doors seen from the front, door handles, table legs, chair front, stove front, chimney, hanging meat seen from the side, barrel side, cylinder, stairs in profile, horizon, sky, vanishing point, depth of field, tilt-shift, cinematic camera, low angle, high angle, characters, people, animals, text, labels, grid, hexagons, border, vignette, watermark
```

## Se o resultado vier de lado

Mande esta mensagem de correção junto com a imagem errada:

```
This is wrong: I can see the inner faces of the walls / the sides of the pillars / table legs / the front of the stoves / doors from the front. Redraw it as a strict orthographic floor plan from directly above (90 degrees, camera pointing straight down at the floor). Walls are only flat thick bands seen from their top. Pillars are squares. Barrels are circles. Tables are rectangles. Doors are thin leaves lying in plan view. NOTHING is seen from the side. No perspective at all. Keep the same layout: kitchen on the left with the butcher's room in its north-west corner and the stairway in the south-west corner, a narrow servants' passage in the middle, and the throne hall on the right with 16 square pillars, a gallery band around the walls, the dais at the north end and the great double door at the south.
```

## Notas para a máscara 3D (skill `criar-mascara`)

- Paredes do salão, da cozinha, do açougue e da passagem: `parede` (altura inteira).
- Pilastras: `parede`. Balaustrada do mezanino: `balcao`, só se o grupo for subir; senão, vazio.
- Fogões e lareira: `estante`. Mesa de corte e mesa do estrado: `mesa`. Mesas do banquete: `mesa`. Bancos: vazios (pequenos demais).
- Barris: `muro-alto`. Cepo e laje do açougue: `mesa`/`balcao`.
- Portas e passagem de criados: vazias, com **pelo menos 2/3 de hexágono** de largura.

## Perguntas em aberto

- Se o mezanino (a galeria de 3 m) entra desenhado no mesmo mapa, ou fica para um mapa à parte, porque tem 2 arqueiros à noite e músicos na festa.
- Se a escada da cozinha leva ao porão (despensa, adega) e se vale um mapa dele.
- Se a mesa do banquete fica posta (cena da festa) ou vazia (cena de dia).
