---
name: quadro-hq
description: >
  Gera a arte dos quadros de uma HQ numa IA externa (OpenAI gpt-image-1), sempre com os
  avatares e as folhas de modelo do elenco como referência — personagens de jogador e
  NPCs — para o mesmo personagem ter a mesma cara em todos os quadros. Entrega a arte
  limpa, **sem balão nenhum**; o letreiramento é da skill `baloes-hq`. Também fixa o
  modelo de quem ainda não tem: avatar de NPC em campanha/npcs/<slug>/ e folha de modelo
  em modelo-hq.png. Use when the user asks to "gerar os quadros", "desenhar o quadro 3",
  "criar o avatar do NPC", "fixar o modelo do personagem", "arte da HQ", ou /quadro-hq.
---

# A arte dos quadros

Cada quadro é uma chamada paga a uma IA externa. O que essa skill faz de diferente de
colar um prompt num gerador é **mandar junto a referência de quem aparece** — é isso que
impede o Comam de trocar de rosto entre a página 4 e a 9, que é o defeito que denuncia
HQ feita por IA.

```
python .claude/skills/quadro-hq/scripts/gerar_quadro.py <comando> [opções]
```

| Comando | O que faz |
|---|---|
| `elenco --roteiro ...` | Lista quem aparece no volume e quem ainda não tem modelo. Sai com erro se faltar alguém — é a trava antes de gerar |
| `avatar --quem <slug> --npc --descricao "..."` | Retrato de referência de um NPC, em `campanha/npcs/<slug>/avatar.png` |
| `modelo --quem <slug> [--npc]` | Folha de modelo: três vistas do mesmo personagem (frente, 3/4, costas), em `modelo-hq.png` |
| `quadro --roteiro ... [--pagina N --quadro M \| --faltando]` | A arte dos quadros, em `<volume>/quadros/pNNqMM.png` |

Opções gerais (valem antes ou depois do subcomando): `--so-prompt` (escreve o prompt e
**não gasta**), `--forcar` (refaz o que já existe), `--qualidade low|medium|high`,
`--fidelidade alta|padrao`, `--modelo-ia`, `--chave-env` (padrão `OPENAI_API_KEY`),
`--raiz`.

## Onde mora a referência de cada um

```
personagens/<slug>/foto.png          retrato do PJ (vem da skill criar-personagem-gurps)
personagens/<slug>/modelo-hq.png     folha de modelo do PJ, para a HQ
campanha/npcs/<slug>/npc.md          quem o NPC é e como ele é fisicamente
campanha/npcs/<slug>/avatar.png      retrato do NPC
campanha/npcs/<slug>/modelo-hq.png   folha de modelo do NPC
```

**Todo NPC que aparece na HQ ganha pasta própria em `campanha/npcs/<slug>/`.** O NPC é
da campanha inteira, não de um volume: Hoel Meia-Orelha aparece na taberna do capítulo 1
e vai reaparecer; o avatar dele se reusa. O `npc.md` sai do que já está escrito no
`npcs.md` do capítulo (plano) e no `campanha/mundo.md` — **o que está anotado ganha do
plano**, como manda a skill `campanha`. Se o NPC tem meia orelha lá, tem meia orelha
aqui.

A ordem de preferência ao escolher a referência é `modelo-hq.png` → `avatar.png` →
`foto.png` → `foto-corpo.png`. Sem nenhuma delas o personagem sai inventado e o script
avisa.

## O que o prompt carrega

Montado pelo script a partir do roteiro, nesta ordem: **estilo do volume** (o mesmo do
começo ao fim), **quem é cada imagem de referência**, **o lugar**, **o que se vê**,
**o enquadramento**, **a luz**, e a trava de sempre — `no text, no lettering, no speech
balloons, no panel borders`. Balão e moldura entram depois, em Pillow.

O formato (paisagem, quadrado ou retrato) é escolhido pela caixa que o quadro ocupa na
página: um quadro de faixa larga pede 1536×1024, um quadro alto pede 1024×1536. Gerar no
formato errado faz a montagem cortar cabeça.

No roteiro, o campo `o_que_se_ve` é o que o usuário lê, em português. Se houver também
`visual`, em inglês, é ele que vai no prompt — o gerador responde melhor em inglês, e o
roteiro continua legível para a mesa.

## Regras de estilo (valem para o volume inteiro)

- **Estilo fixo**, declarado uma vez em `roteiro.json` (`"estilo"`), nunca mudado no meio
  do volume. O padrão segue o que a skill `campanha` já usa nas ilustrações de capítulo:
  *digital illustration, fantasy RPG comic book art, clean bold linework, warm soft
  coloring, hand-drawn look*. Nada de "photo" ou "photorealistic", e nunca o nome de um
  artista vivo — descreva a técnica.
- **Deixe respiro para o balão**: céu, parede, penumbra no alto do quadro. O roteiro já
  diz onde o balão vai cair; a arte tem de reservar aquele canto.
- **Yrth manda no cenário.** Nível tecnológico 3, sem pólvora, sem vidro plano barato;
  reino, cidade e povo conforme `livros/gurps-fantasy-3ed/`. Um guarda de Caithness não
  se veste como um de Mégalos.
- **Continuidade de lugar**: passando `"cenario"` no quadro (ou no roteiro inteiro), a
  arte do lugar entra como referência e a taberna continua a mesma taberna. A ilustração
  de abertura do capítulo (`campanha/plano/NN-.../inicio.png`) serve exatamente para
  isso.

## Custo e prudência

Cada quadro é dinheiro. Por isso:

1. **Só gere depois do roteiro e do esboço aprovados** — é a ordem que o agente
   `comic-artist` segue.
2. `--so-prompt` primeiro, quando houver dúvida sobre o texto do prompt: escreve o
   `.md` ao lado do quadro e não chama a IA.
3. O script diz quantas chamadas vai fazer antes de fazer.
4. Todo quadro gerado deixa o prompt gravado em `quadros/pNNqMM-prompt.md`; refazer
   depois é mudar uma frase, não reescrever tudo.
5. `--faltando` regenera só o que ainda não existe — repetir o comando não redesenha o
   que já foi aprovado.

Ao terminar, o script grava no `roteiro.json` o caminho da arte de cada quadro, que é o
que a `pagina-hq` procura para montar a página.
