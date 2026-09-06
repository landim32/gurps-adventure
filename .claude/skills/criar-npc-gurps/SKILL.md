---
name: criar-npc-gurps
description: >
  Cria NPCs de GURPS 3ª Edição (figurantes, aliados, vilões, patronos) a partir de uma
  descrição e um orçamento de pontos. Monta o personagem usando a skill
  criar-personagem-gurps, mas entrega só um bloco Markdown compacto no estilo Farvaro
  (sem Planilha, JSON nem retrato). Use when the user asks to "criar um NPC",
  "gerar um figurante", "NPC de GURPS", "stat block de NPC", ou /criar-npc-gurps.
  Não use para PCs ou quando pedirem ficha/imagem da Planilha — nesse caso use
  criar-personagem-gurps.
---

# Criar NPC de GURPS 3ª Edição

## Usar a skill `criar-personagem-gurps`

**Primeiro passo obrigatório:** leia `.claude/skills/criar-personagem-gurps/SKILL.md` e
siga-a para montar o personagem (fontes em `livros/`, custos, arquétipos, raças, línguas,
armadura, derivados, fechamento de pontos). Não reproduza nem resuma essas regras aqui.

Exceções desta skill sobre a de personagem:

- Se o usuário **não** disser os pontos, use **50** (não 100) e avise.
- Não gere `personagem.json`, `ficha.jpg`, `foto-prompt.md` nem pasta em `personagens/`.
  Não rode `preencher_ficha.py`.
- Vários NPCs no mesmo pedido: um bloco por pessoa, cada um fechado em pontos.

## Entrega

Mostre o bloco na resposta. Se o usuário pedir para gravar, escreva `npcs/<slug>.md`
(slug como na skill de personagem).

Formato **exato** (prosa contínua, ponto-e-vírgula entre itens; sem tabelas; sem custos
dentro do bloco, só o total na primeira linha):

```markdown
### Nome
<idade>; <cabelos, olhos, pele>; <altura>, <peso>.; <N> pontos.
ST n, DX n, IQ n, HT n. Velocidade Básica n,nn; Deslocamento n. Esquiva n; Aparar n[; Bloqueio n]. Usa <armadura> (DP n, RD n). Vantagens: <lista>. Desvantagens: <lista>. Peculiaridades: <lista>. Perícias: <Nome NH>; <Nome NH>. Línguas: <Nome NH>[(pré-definido)|(nativa)]. Armas: <Nome> : <dano> <tipo>[; <dano> <tipo>].
---
```

Exemplo canônico:

```markdown
### Farvaro
Pouco mais de 40 anos; cabelos finos e castanhos, olhos castanhos, pele de tom lívido; 1,70 m, 75 kg.; 50 pontos.
ST 10, DX 11, IQ 13, HT 10. Velocidade Básica 5,25; Deslocamento 5. Esquiva 5; Aparar 5. Usa roupas leves de couro (DP 1, RD 1). Vantagens: Alfabetizado. Desvantagens: Preguiça, Fanfarronice, Covardia. Peculiaridades: Costuma cantarolar e desafina; Ignora os que estão “abaixo dele”; Gosta de jogo e apostas estranhas, principalmente com trouxas. Acha que é um bom navegador mas não é. Perícias: Administração 13; Cavalgar Camelos 11; Diplomacia 14; Jogos 14; Equitação 11; Faca 11; Comércio 16; Prestidigitação 12. Línguas: Ayunês simplificado dos mercadores 6 (pré-definido), Lantranês 13 (pré-definido), Nômico 12, Shandassês 12. Armas: Facão : 1D-2 corte; 1D-2 perfuração.
---
```

- Duas linhas de prosa após o `### Nome`, depois `---`. Decimal com vírgula (`5,25`).
- Omita um campo só se não existir (sem Bloqueio sem escudo; sem a palavra "Vantagens" se a lista for vazia).
- Perícias: `Nome NH`, separadas por `; `. Línguas no campo próprio, não em Perícias.
- Armas: dano já com a ST do NPC. Armadura: uma frase com DP/RD do tronco.

Depois do bloco, uma linha: pontos gastos = orçamento, arquétipo/raça e livro.
