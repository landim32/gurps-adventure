---
name: criar-npc
description: >
  Cria NPCs de GURPS 3ª Edição (figurantes, aliados, vilões, patronos) a partir de uma
  descrição e um orçamento de pontos. Monta o personagem usando a skill
  criar-personagem, mas entrega só um bloco Markdown compacto no estilo Farvaro
  (sem Planilha, JSON nem retrato). A primeira linha do bloco abre com altura, peso e
  idade, calculados pela mesma regra da criar-personagem. Use when the user asks to
  "criar um NPC", "gerar um figurante", "NPC de GURPS", "stat block de NPC",
  ou /criar-npc.
  Não use para PCs ou quando pedirem ficha/imagem da Planilha — nesse caso use
  criar-personagem.
---

# Criar NPC de GURPS 3ª Edição

## Usar a skill `criar-personagem`

**Primeiro passo obrigatório:** leia `.claude/skills/criar-personagem/SKILL.md` e
siga-a para montar o personagem (fontes em `livros/`, custos, arquétipos, raças, línguas,
armadura, derivados, fechamento de pontos). Não reproduza nem resuma essas regras aqui.

Exceções desta skill sobre a de personagem:

- Se o usuário **não** disser os pontos, use **50** (não 100) e avise.
- Não gere `personagem.json`, `ficha.jpg`, `foto-prompt.md` nem pasta em `personagens/`.
  Não rode `preencher_ficha.py`.
- Vários NPCs no mesmo pedido: um bloco por pessoa, cada um fechado em pontos.

Fora essas três, **não há regra sua**: atributos, custos, raça, arquétipo, línguas, armadura,
derivados, o teto de `2 × idade` e o fechamento de pontos são todos da `criar-personagem`.
Esta skill só troca o formato da saída.

### Altura, peso e idade no bloco

Abrem a primeira linha, **nessa ordem**, pelos mesmos números que a `criar-personagem`
calcula — tabela de ST → altura → peso, ajustada por raça e por Magreza / Excesso de Peso /
Obesidade / Gigantismo / Nanismo. As tabelas estão lá; não as reproduza aqui.

**Precedência, porque os dois casos acontecem:**

- NPC **que você monta** → a tabela manda. ST 10 é 1,75 m e 68,1 kg, não um número de ouvido.
- NPC **transcrito de livro ou aventura** → o bloco impresso do livro vence a tabela, e você
  copia os números dele. É o caso do Farvaro abaixo: 1,70 m e 75 kg com ST 10 divergem da
  média e estão assim no livro — não “corrija” um dado de fonte citando a tabela.

## Entrega

Mostre o bloco na resposta. Se o usuário pedir para gravar, escreva `npcs/<slug>.md`
(slug como na skill de personagem).

Formato **exato** (prosa contínua, ponto-e-vírgula entre itens; sem tabelas; sem custos
dentro do bloco, só o total na primeira linha):

```markdown
### Nome
<altura>; <peso>; <idade>; <cabelos, olhos, pele>. <N> pontos.
ST n, DX n, IQ n, HT n. Velocidade Básica n,nn; Deslocamento n. Esquiva n; Aparar n[; Bloqueio n]. Usa <armadura> (DP n, RD n)[; escudo <nome> (DP n)]. Vantagens: <lista>. Desvantagens: <lista>. Peculiaridades: <lista>. Perícias: <Nome NH>; <Nome NH>. Línguas: <Nome NH>[(pré-definido)|(nativa)]. Armas: <Nome> : <dano> <tipo>[; <dano> <tipo>].
---
```

Casa por casa do começo: `1,75 m; 68,1 kg; pouco mais de 40 anos; cabelos finos e castanhos,
olhos castanhos, pele lívida. 50 pontos.`

Exemplo canônico:

```markdown
### Farvaro
Pouco mais de 40 anos; cabelos finos e castanhos, olhos castanhos, pele de tom lívido; 1,70 m, 75 kg.; 50 pontos.
ST 10, DX 11, IQ 13, HT 10. Velocidade Básica 5,25; Deslocamento 5. Esquiva 5; Aparar 5. Usa roupas leves de couro (DP 1, RD 1). Vantagens: Alfabetizado. Desvantagens: Preguiça, Fanfarronice, Covardia. Peculiaridades: Costuma cantarolar e desafina; Ignora os que estão “abaixo dele”; Gosta de jogo e apostas estranhas, principalmente com trouxas. Acha que é um bom navegador mas não é. Perícias: Administração 13; Cavalgar Camelos 11; Diplomacia 14; Jogos 14; Equitação 11; Faca 11; Comércio 16; Prestidigitação 12. Línguas: Ayunês simplificado dos mercadores 6 (pré-definido), Lantranês 13 (pré-definido), Nômico 12, Shandassês 12. Armas: Facão : 1D-2 corte; 1D-2 perfuração.
---
```

- Duas linhas de prosa após o `### Nome`, depois `---`. Decimal com vírgula (`5,25`).
- O **Farvaro acima é transcrição literal** do livro (`23-caravana-para-ein-arris.md`, pág.
  236), inclusive a ordem antiga da primeira linha e o `.;` órfão de `75 kg.`. Ele vale como
  modelo de *conteúdo*, não de pontuação: ao emitir um bloco novo, use a ordem de cima
  (altura; peso; idade) e não replique o ponto sobrando.
- Omita um campo só se não existir (sem Bloqueio sem escudo; sem a palavra "Vantagens" se a lista for vazia).
- Perícias: `Nome NH`, separadas por `; `. Línguas no campo próprio, não em Perícias. Se o
  NPC é de arte marcial, as manobras reais dele (`04-combate-manobras.md`, “Manobras
  Realistas”) vão no fim da lista de perícias, prefixadas de `Manobras:` —
  `Manobras: Chave de Braço 13; Quedas 12`. Ele é o alvo do `atacar` igual a qualquer outro,
  e um bloco que esconde a manobra faz a mesa não saber que ela existe.
- Armas: dano já com a ST do NPC. Armadura: uma frase com DP/RD do tronco; **escudo vai à
  parte**, com o DP dele — é o que a `resolver-defesa` soma à defesa em qualquer região (só não
  vale contra ataque pelas costas), e um bloco que esconde o escudo perde o `Bloqueio` que
  anuncia.

Depois do bloco, uma linha: pontos gastos = orçamento, arquétipo/raça e livro.

## roll6 — a mesa virtual

NPC que vai entrar em cena existe também no roll6 (skill `roll6`):

- **Criar**: `create_npc` com token (`list_tokens` primeiro; se não houver, `roll6.py
  subir-imagem ... --formato png --lado 512` → `create_token`), `life` = PV, `energy` =
  Fadiga, `move` = Deslocamento e `sheet` = o bloco.
- **Pôr em cena**: `add_npc_to_campaign` → `place_npc_on_map`.
- **Um NPC por figura com nome**: Morto 1, Morto 3, Goblin do portão. Ocorrências
  múltiplas de um NPC só servem para figurante sem identidade.
- **Nome diferente do repositório**: grave o apelido em `campanha/roll6.json`.
