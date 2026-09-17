# Avatares dos NPCs

Cada NPC que precisa de rosto ganha pasta própria aqui:

```
<slug>/
  npc.md          quem é e como é fisicamente — a descrição de onde sai o retrato
  avatar.png      o retrato de referência
  modelo-hq.png   a folha de modelo: frente, três quartos e costas
  *-prompt.md     o prompt de cada imagem, para poder refazer
```

O NPC é da campanha inteira, não de um volume de HQ: Hoel Meia-Orelha serve na taberna do
capítulo 1 e continua o mesmo Hoel no capítulo 9. Por isso a pasta fica aqui e não dentro
de `campanha/hq/`.

**A descrição física em `npc.md` vem do que já está registrado** — o `npcs.md` do capítulo
no plano, o `npcs.md` da pasta de jogo e o `campanha/mundo.md`. Quando os dois discordam,
**o que está anotado ganha do plano**: se a mesa arrancou a orelha dele, o retrato tem de
saber disso.

Quem cria e regera é a skill **`quadro-hq`**:

```
python .claude/skills/quadro-hq/scripts/gerar_quadro.py avatar \
    --quem hoel-meia-orelha --npc --descricao "taberneiro de Wallace, 50 anos, ..."
python .claude/skills/quadro-hq/scripts/gerar_quadro.py modelo --quem hoel-meia-orelha --npc
```

Não confunda com `tokens/`, na raiz do projeto: aquilo é miniatura vista de cima para o
mapa hexagonal (skills `token-hex-gurps` e `token-organizator`). Aqui é o rosto, para a
HQ.
