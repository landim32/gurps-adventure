# HQ da campanha

Os volumes em quadrinhos do que aconteceu na mesa. Quem conduz é o agente
**`comic-artist`** (`.claude/agents/comic-artist.md`), com as skills `quadro-hq`
(arte), `baloes-hq` (letreiramento) e `pagina-hq` (esboço, montagem e PDF).

Cada volume tem **20 a 24 páginas** e vive na própria pasta:

```
vol-NN-<slug>/
  00-recorte.md      o que entra, o que fica de fora, sinopse, gancho
  01-cenas.md        as cenas na ordem, com quantas páginas cada uma leva
  roteiro.md         o roteiro legível — página, quadro, o que se vê, balões
  roteiro.json       o mesmo, estruturado: é o que os scripts leem
  elenco.md          quem aparece e onde está a referência visual de cada um
  esbocos/           o planejamento em figuras geométricas, sem IA
  quadros/           a arte de cada quadro, sem balão, mais o prompt usado
  paginas/           a página montada e letreirada
  volume.pdf         o volume fechado
```

Os avatares dos NPCs ficam em [`../npcs/`](../npcs/) — o NPC é da campanha inteira e se
reusa de um volume para o outro.

## Volumes

<!-- indice:hq -->
- **[Vol. 1 — A Âncora Quebrada](vol-01-a-ancora-quebrada/)** · capítulo 1, *Encontro na
  Taberna* · 22 páginas, 127 quadros · **EM ANDAMENTO: passo 6 de 10** (avatares, 1 de 11
  feito). O estado e o ponto de retomada estão no
  [`README.md` do volume](vol-01-a-ancora-quebrada/README.md) — **leia-o antes de
  continuar**, para não repetir chamada nem refazer decisão já tomada.
<!-- /indice:hq -->
