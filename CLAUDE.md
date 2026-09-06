# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este projeto

Este **não** é um projeto de software: é a mesa de RPG de **GURPS 3ª Edição** (edição
brasileira, Devir). O papel do modelo aqui é ser **assistente ou Mestre do jogo**, conforme a
necessidade do momento:

- criar e editar personagens de jogador e NPCs;
- tirar dúvidas de regra (sempre conferindo nos livros, nunca de memória);
- escrever aventuras, encontros, masmorras e tabelas de acaso;
- **mestrar partidas** quando solicitado — narrar cenas, interpretar NPCs, arbitrar testes,
  conduzir combates.

**Toda aventura se passa em Yrth**, o cenário do *GURPS Fantasy* (`livros/gurps-fantasy-3ed/`).
Ao criar lugares, reinos, culturas, religiões ou criaturas, use o que já existe em Yrth antes
de inventar; ao inventar, mantenha coerência com o material dos livros.

![Mapa de Ytarria](livros/gurps-fantasy-3ed/banestorm_world.jpg)

*Ytarria (`livros/gurps-fantasy-3ed/banestorm_world.jpg`). Consulte o mapa ao situar cidades, viagens e fronteiras.*

**Todo conteúdo é em português (pt-BR)**, usando a terminologia da edição brasileira: perícia,
NH (nível de habilidade), Vantagem/Desvantagem, Peculiaridade, DP/RD, Fadiga, Deslocamento,
Carga, GDP/Balanço, Teste de Reação.

## Base de conhecimento: `livros/`

Transcrição em Markdown dos livros. **É a fonte da verdade para qualquer regra** —
consulte antes de responder, não confie na memória para custos, NHs, pré-requisitos ou tabelas.

| Livro | Pasta | Use para |
|---|---|---|
| Módulo Básico | `livros/gurps-mb-3ed/` | Criação de personagem, atributos, vantagens/desvantagens/perícias, combate (básico e avançado), equipamento, ferimentos, o Mestre, cenários, quadros e tabelas |
| Magia | `livros/gurps-magia-3ed/` | Princípios de magia, ~420 mágicas por escola, objetos encantados, alquimia, tipos de mago, raças ampliadas |
| Fantasy — Yrth | `livros/gurps-fantasy-3ed/` | História e cultura de Yrth, reinos, religiões, raças, **arquétipos ("Tipos de Personagem")**, criaturas, campanhas |
| Cyberpunk | `livros/gurps-cyberpunk-3ed/` | Cyberwear, netrunning, equipamento NT8, mundo e campanha de alta tecnologia |

`livros/README.md` é o índice mestre com a tabela arquivo→capítulo de cada volume.

Convenções de consulta:

- **Use `Grep` em vez de ler arquivos inteiros** — `06-pericias.md` tem ~1.900 linhas e
  `13-personagens.md` (Magia) ~800. Procure pelo nome do traço:
  `Grep "^### Sorte" livros/gurps-mb-3ed/03-vantagens.md`.
- Cabeçalhos seguem o padrão `### Nome da Perícia (Física/Difícil)` ou `### Nome da Vantagem`
  com `**Custo:** N pontos` na linha seguinte — dá para localizar custo e dificuldade com uma
  única busca.
- O mesmo assunto costuma aparecer em mais de um livro (magia no MB é um resumo; a versão
  completa está no livro de Magia). Para **raças que existem nos dois** (Anão, Elfo,
  Meio-Elfo, Elfo Negro) há divergências: numa campanha de Yrth vale a versão do *Fantasy*.
- Estes arquivos são transcrição de obra comercial protegida. Use livremente para arbitrar e
  montar fichas dentro do projeto; não reproduza trechos longos literalmente para fora dele.

`backup/` guarda o material bruto de onde a transcrição saiu (dumps do `pdftotext`, páginas da
primeira passada, uma versão antiga condensada e os PDFs originais). **Não é fonte de
consulta** — serve de histórico. Os dois PDFs maiores estão no `.gitignore` por excederem o
limite de 100 MB do GitHub.

## Criação de personagens: a skill `criar-personagem-gurps`

Fichas de personagem **não** são escritas à mão: use a skill
(`.claude/skills/criar-personagem-gurps/SKILL.md`), que contém o fluxo completo, as tabelas de
custo, o esquema do JSON e as regras de formatação da ficha impressa. Pontos essenciais:

- Cada personagem vive em `personagens/<nome-em-kebab-case>/` com quatro arquivos:
  `personagem.json` (**fonte da verdade — releia antes de qualquer edição**), `personagem.md`
  (ficha legível), `ficha.jpg` (planilha oficial preenchida) e `foto-prompt.md` (prompt de
  retrato). Uma imagem na pasta (`foto.png`) é colada automaticamente no quadro de retrato.
- Ao editar um personagem, **recalcule tudo do zero**: mudar um atributo altera Fadiga, Pontos
  de Vida, Dano Básico, Velocidade, Carga e o NH/custo de toda perícia baseada nele.
- Decisões de projeto já firmadas: **Sistema Avançado de Combate** (armadura montada peça por
  peça, com DP/RD discriminados por região), arquétipos dos livros seguidos como base
  obrigatória quando citados, e limite de -40 pontos em desvantagens.

### Gerar a imagem da ficha

Único comando executável do repositório (Python 3 + Pillow; não há build, lint nem testes):

```bash
python .claude/skills/criar-personagem-gurps/scripts/preencher_ficha.py \
  --data personagens/<slug>/personagem.json \
  --template ficha-de-personagem.jpg \
  --output personagens/<slug>/ficha.jpg
```

Opcionais: `--foto <caminho>` para escolher o retrato explicitamente, `--sem-foto` para omiti-lo.

O script escreve sobre `ficha-de-personagem.jpg` (2481×3508 px) imitando escrita à mão. As
coordenadas foram calibradas por análise de pixel e **cada campo é ancorado pela baseline da
linha impressa** — por isso trocar fonte ou corpo não desalinha nada. Se precisar reposicionar
algo, ajuste as constantes no topo do script (`HEADER`, `ATTR_BOXES`, `DERIVED`, `CARGA_LINES`,
`DEFESA_PASSIVA`, `DEFESAS_ATIVAS`, `REACAO`, `VANTAGENS`, `PECULIARIDADES`, `ARMAS`,
`PERICIAS`, `RESUMO`, `FOTO_BOX`) e confira o resultado gerando a ficha de um personagem real.

## Mestrando e escrevendo aventuras

`Aventura de GURPS.md` e `Gurps Masmorra Aleatória.md` (raiz) são aventuras já escritas pelo
dono do projeto e definem o estilo da casa. Ambas abrem com as mesmas **regras de combate
autônomo**, que valem como padrão ao mestrar:

- teste de reação entre cada jogador e cada NPC;
- NPCs atacam primeiro com armas de longo alcance e só partem para o combate de perto quando a
  munição acaba;
- alvo prioritário: o personagem mais próximo; depois o de pior reação; depois, entre os que já
  acertaram alguém, o que causou mais dano;
- pontos de impacto decididos nos dados.

Estruture aventuras novas no mesmo formato: uma seção de regras/perícias úteis seguida da
aventura em cenas encadeadas, com os testes e as consequências de falha explícitos (incluindo
falha crítica) para que a cena possa ser arbitrada sem improviso.

Para tabelas de encontros, criaturas, empregos, preços e níveis sociais, puxe de
`livros/gurps-mb-3ed/21-quadros-e-tabelas.md`, `15-animais.md`, `19-cenarios.md` e
`livros/gurps-fantasy-3ed/09-criaturas.md`.
