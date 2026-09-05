# GURPS 3ª Edição — Módulo Básico (Biblioteca Élfica)

Documentação em Markdown do PDF `gurps-3e-modulo-basico-biblioteca-elfica.pdf` (**257 páginas**), organizada em duas fases: uma extração bruta página por página (Fase 1) e uma consolidação por capítulo/tema (Fase 2), ambas concluídas.

## Aviso importante sobre direitos autorais

GURPS 3ª Edição é uma obra comercial protegida por direitos autorais (Steve Jackson Games / Devir), ainda em circulação. Por isso, **o conteúdo da pasta `capitulos/` (Fase 2) não é uma transcrição verbatim do livro** — é um resumo paráfraseado e, em trechos longos de conteúdo de referência (listas de mágicas, perícias psíquicas, animais, tabelas extensas de armas/armaduras, e as duas aventuras completas), condensado em forma de visão geral. Números de jogo, mecânicas e nomes de regras foram preservados por serem fatos de sistema, não prosa autoral; a redação em si é uma reescrita, não uma cópia do original. Para o texto exato do livro, consulte a edição impressa/oficial.

## Estrutura da documentação

- **`capitulos/`** — Fase 2, concluída: 25 arquivos organizados por capítulo/tema (veja a tabela abaixo), cobrindo as 257 páginas do livro em prosa parafraseada e condensada.
- **`_paginas_fase1/`** — Fase 1, arquivada: os arquivos originais `pagina-NNN.md` (001-257) produzidos na primeira passada de conversão, mantidos como registro histórico do processo.
- **`_raw/`** — texto bruto extraído via `pdftotext -layout -enc UTF-8` (uma página por arquivo), preserva o alinhamento de colunas/tabelas do PDF. Útil como referência para tabelas.
- **`_raw_plain/`** — texto bruto extraído via `pdftotext -enc UTF-8` (sem `-layout`), com ordem de leitura correta para prosa em colunas duplas. Foi a fonte primária de leitura da Fase 2.

## Status: Fase 1 — transcrição bruta (concluída, 257/257 páginas)

Cada página do PDF foi convertida em um arquivo `pagina-NNN.md`, **sem reorganizar** capítulos, renumerar seções ou consolidar o material entre páginas. A consolidação por capítulo/tema (Fase 2) só deve começar depois que todas as páginas estiverem extraídas — o que já é o caso.

As páginas foram tratadas em dois níveis de acabamento, por razão de escala (257 páginas):

- **Páginas 001–016** (agradecimentos, sumário/índice, introdução e início da Criação de Personagem): transcritas e formatadas manualmente em Markdown "limpo" (parágrafos, negrito, tabelas reconstituídas), preservando duas colunas do layout original quando existiam. Notas de transcrição sinalizam onde a extração automática deixou ambiguidades (ex.: pareamento de células de tabelas).
- **Páginas 017–257** (todo o restante do livro — perícias, combate, magia, psiquismo, o Mestre, cenários, as duas aventuras, glossário, índice remissivo, tabelas de armas/armaduras/equipamento etc.): geradas automaticamente a partir do texto extraído com `pdftotext -layout`, envolvido em bloco de código (` ``` `) dentro do arquivo `.md` para preservar fielmente o alinhamento de colunas, tabelas e margens do original. Este texto ainda não foi reescrito em Markdown estruturado — isso é trabalho da Fase 2.

Observações gerais:

- O livro completo é **GURPS 3ª Edição - Módulo Básico**, de Steve Jackson (edição brasileira, Devir), com 256-257 páginas + apêndice entre as págs. 200/201. Esta cópia é uma versão de fã ("fan-scan").
- As **páginas 214 a 217** ("Exemplos de Personagens") são fichas de personagem preenchidas, reproduzidas como imagem/diagramação — não têm texto extraível. Isso está sinalizado nos respectivos arquivos `.md`.
- A **página 012** é a Planilha de Personagem em branco (formulário/imagem); o texto extraído trouxe apenas pequenas chamadas de referência a outras páginas, não os rótulos dos campos do formulário.
- Os arquivos-fonte brutos (texto puro extraído via `pdftotext -layout -enc UTF-8`, um por página, `pagina-NNN.txt`) foram mantidos em `_raw/` como referência para conferência durante a Fase 2.

## Conteúdo por faixa de páginas (visão geral, conforme o índice do livro)

| Páginas | Conteúdo |
|---|---|
| 001 | Agradecimentos (versão digital) |
| 002–005 | Sumário/Índice completo do livro |
| 006–007 | Introdução (Steve Jackson) / Material Necessário para o Jogo |
| 008 | Suporte ao Sistema / O Que é Roleplaying? |
| 009 | Para Começar a Jogar Rapidamente |
| 010–018 | Criação de Personagem, Atributos Básicos, Aparência Física, Riqueza e Status |
| 019–025 | Cap. 4 Vantagens |
| 026–041 | Cap. 5 Desvantagens |
| 041 | Cap. 6 Peculiaridades |
| 042–070 | Cap. 7 Perícias |
| 071–077 | Cap. 8 Equipamento e Carga |
| 078–083 | Cap. 9 Completando seu Personagem / Cap. 10 Evolução do Personagem |
| 084–085 | Cap. 11 Personagens Aleatórios |
| 086–094 | Cap. 12 Testes de Habilidade |
| 095–101 | Cap. 13 Sistema Básico de Combate |
| 102–125 | Cap. 14 Sistema Avançado de Combate |
| 126–134 | Cap. 15 Ferimentos, Doenças e Fadiga |
| 135–138 | Cap. 16 Combate Montado ou em Veículo |
| 139 | Cap. 17 Vôo |
| 140–145 | Cap. 18 Animais |
| 146–164 | Cap. 19 Magia |
| 165–176 | Cap. 20 Psiquismo |
| 177–184 | Cap. 21 O Mestre |
| 185–195 | Cap. 22 Cenários |
| 196–200 | Cap. 23 Escrevendo suas Próprias Aventuras |
| ~200/201 | Apêndice (Novas Vantagens/Desvantagens/Perícias/Outras Regras) |
| 201–213 | Quadros e Tabelas (armas, armaduras, equipamento, exemplos de personagens) |
| 214–217 | Exemplos de Personagens (fichas — imagem, sem texto extraível) |
| 218–231 | Aventura "Uma Noite de Trabalho" |
| 232–249 | Aventura "Caravana para Ein Arris" |
| 250–251 | Glossário |
| 252–256 | Índice Remissivo |
| 257 | Das Peculiaridades da Versão Brasileira |

*(As transições exatas entre seções podem variar em 1-2 páginas em relação à tabela acima; confirmar contra o texto de cada página durante a Fase 2.)*

## Status: Fase 2 — organização por capítulo (concluída)

Todo o conteúdo das 257 páginas foi consolidado em `capitulos/`, reescrito em Markdown estruturado e organizado por tema em vez de por página. Índice dos arquivos:

| Arquivo | Conteúdo | Páginas do livro |
|---|---|---|
| `00-indice.md` | Sumário do livro original | 2-5 |
| `01-introducao.md` | Introdução, O Que É Roleplaying?, Começando Rápido | 6-9 |
| `02-criacao-de-personagem.md` | Atributos Básicos, Aparência Física, Riqueza e Status | 10-18 |
| `03-vantagens.md` | Cap. 4 Vantagens | 19-25 |
| `04-desvantagens.md` | Cap. 5 Desvantagens | 26-40 |
| `05-peculiaridades.md` | Cap. 6 Peculiaridades | 41 |
| `06-pericias.md` | Cap. 7 Perícias | 42-70 |
| `07-equipamento-e-carga.md` | Cap. 8 Equipamento e Carga | 71-77 |
| `08-personagem-avancado.md` | Caps. 9-11 Completando/Evolução/Aleatórios | 78-85 |
| `09-testes-de-habilidade.md` | Cap. 12 Testes de Habilidade | 86-94 |
| `10-combate-basico.md` | Cap. 13 Sistema Básico de Combate | 95-101 |
| `11-combate-avancado.md` | Cap. 14 Sistema Avançado de Combate | 102-125 |
| `12-ferimentos-doencas-fadiga.md` | Cap. 15 Ferimentos, Doenças e Fadiga | 126-134 |
| `13-combate-montado-veiculo.md` | Cap. 16 Combate Montado ou em Veículo | 135-138 |
| `14-voo.md` | Cap. 17 Vôo | 139 |
| `15-animais.md` | Cap. 18 Animais | 140-145 |
| `16-magia.md` | Cap. 19 Magia | 146-164 |
| `17-psiquismo.md` | Cap. 20 Psiquismo | 165-176 |
| `18-o-mestre.md` | Cap. 21 O Mestre | 177-184 |
| `19-cenarios.md` | Cap. 22 Cenários | 185-195 |
| `20-escrevendo-aventuras.md` | Cap. 23 Escrevendo Suas Próprias Aventuras | 196-200 |
| `21-quadros-e-tabelas.md` | Tabelas de combate, armas, armaduras, equipamento | 201-213 (214-217 sem texto extraível) |
| `22-uma-noite-de-trabalho.md` | Aventura solo (resumo — não verbatim) | 218-231 |
| `23-caravana-para-ein-arris.md` | Aventura em grupo (resumo — não verbatim) | 232-249 |
| `24-glossario-e-apendices.md` | Glossário, nota sobre o Índice Remissivo, nota da edição brasileira | 250-257 |

Notas sobre o processo de condensação:

- Listas longas de referência (as ~97 mágicas do Cap. 19, as perícias psíquicas do Cap. 20, os animais do Cap. 18, as tabelas de armas/armaduras/equipamento) foram condensadas em visões gerais por escola/categoria, em vez de reproduzir cada entrada individual com seus valores numéricos completos — para uso em mesa, consulte o livro original.
- As duas aventuras (`22` e `23`) são resumos de premissa/estrutura/NPCs principais, não a transcrição de cenas, diálogos ou (no caso da aventura solo) da árvore de parágrafos numerados.
- O Índice Remissivo original (págs. 252-256) não foi reproduzido — é uma lista pura de termos e números de página do livro impresso, sem equivalente útil nesta reorganização temática.
