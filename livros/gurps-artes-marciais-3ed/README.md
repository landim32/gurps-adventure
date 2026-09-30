# GURPS Artes Marciais 3ª Edição (referência de regras em Markdown)

**Material de referência reescrito**, não transcrição literal. Diferente dos outros
volumes desta pasta, este livro **não** foi copiado 1:1 do PDF: *GURPS Artes
Marciais* (edição brasileira Devir de *GURPS Martial Arts*, Steve Jackson Games) é
obra protegida por direitos autorais, então o texto explicativo foi reescrito em
palavras próprias e apenas os **dados de jogo** — nomes, dificuldades, valores
pré-definidos, pré-requisitos, custos em pontos, redutores, dano, alcance, preços,
pesos e tabelas — foram transpostos com exatidão.

Fonte: `backup/gurps-3e-artes-marciais.pdf`, **150 páginas**, camada de texto OCR de
baixa qualidade.

## Paginação

| | |
|---|---|
| **página impressa = página do PDF + 4** | o PDF p. 40 é a pág. 44 do livro |
| Cabeçalhos dos arquivos | citam a página do **PDF** (`PDF p. NN`) |
| Referências internas do livro | mantidas como no original (`v. pág. NN`, `MB pág. NN`), na numeração **impressa** |

O PDF começa na página impressa 5: **capa, créditos e sumário original não estão no
arquivo**, por isso [`00-indice.md`](00-indice.md) é um índice reconstruído.

## Arquivos

| Arquivo | Conteúdo | PDF págs. | Impressas |
|---|---|---|---|
| [`00-indice.md`](00-indice.md) | Índice reconstruído do volume | — | — |
| [`01-historia-e-introducao.md`](01-historia-e-introducao.md) | 1. História das artes marciais + cronologia | 1–12 | 5–16 |
| [`02-personagens.md`](02-personagens.md) | 2. Personagens: pontuação, 11 arquétipos, novas vantagens e desvantagens | 13–26 | 17–30 |
| [`03-pericias.md`](03-pericias.md) | 2. Personagens: 46 perícias (24 novas realistas, 22 cinematográficas) | 27–36 | 31–40 |
| [`04-combate-manobras.md`](04-combate-manobras.md) | 3. Combate: regras gerais e 59 manobras | 37–55 | 41–59 |
| [`05-combate-regras-opcionais.md`](05-combate-regras-opcionais.md) | 3. Combate: torneios, chambara, ataques múltiplos, atordoamento, erros críticos | 56–65 | 60–69 |
| [`06-estilos-regras.md`](06-estilos-regras.md) | 4. Estilos: mecânica, custos, novos estilos em jogo | 66–72 | 70–76 |
| [`07-estilos-historicos-e-modernos.md`](07-estilos-historicos-e-modernos.md) | 4. Estilos: 39 estilos + graduações, chi, psiquismo, 5 NPCs | 73–95 | 77–99 |
| [`08-estilos-modernos-e-fantasticos.md`](08-estilos-modernos-e-fantasticos.md) | 4. Estilos: 23 estilos (reais, fantásticos e alienígenas) + 6 NPCs | 96–111 | 100–115 |
| [`09-armas-e-equipamentos.md`](09-armas-e-equipamentos.md) | 5. Armas & Equipamentos: ~122 entradas por cultura e por NT | 112–125 | 116–129 |
| [`10-tabela-de-armas.md`](10-tabela-de-armas.md) | 5. Tabela de Armas: 13 tabelas, 151 linhas | 126–131 | 130–135 |
| [`11-campanhas.md`](11-campanhas.md) | 6. Campanhas: cenários, temas, ideias de aventura, NPCs, pastelão | 132–150 | 136–154 |

A divisão dos arquivos 07/08 segue a paginação do PDF, não uma separação feita pelo
livro: estilos reais como Savate, Sumô, Tae Kwon Do e Wing Chun estão no 08. O
verbete Savate tem a descrição no 07 e o bloco de dados no 08.

## Como consultar

- **Montar um lutador:** `02` (pontuação e arquétipos) → `07`/`08` (custo do estilo e
  listas de perícias) → `03` (perícias e manobras cinematográficas) → `06` (regras de
  primárias/secundárias/opcionais e custo cinematográfico).
- **Dirigir uma luta:** `04` (manobras) e `05` (regras opcionais, torneios, ataques
  múltiplos) + o resumo "para a mesa" no fim de cada um.
- **Equipar:** `09` (descrições e efeitos especiais) e `10` (números de jogo).
- **Preparar campanha:** `11` (cenário por época e por gênero) e `01` (histórico).

## Confiabilidade dos números

A camada de texto do PDF é OCR ruim e erra dígitos. Os valores foram conferidos
renderizando as páginas como imagem (400–600 dpi) nas seções críticas: custos de
estilo, fichas de NPC, tabelas de armas e tabelas de rolagem. Mesmo assim:

- **`(?)`** no texto marca um valor ilegível ou ambíguo que precisa de revisão contra
  o PDF impresso — nunca foi inventado nada no lugar.
- **"—"** nas tabelas de armas marca célula que já vinha em branco no original.
- Cada arquivo tem uma seção ou nota final listando seus pontos incertos.
- Algumas inconsistências são **do livro impresso** e foram preservadas com nota (ex.:
  o texto de Saburo diz 70 pontos em DX/HT/IQ mas a ficha soma 65; o dano básico do
  Caveira vem impresso 1D GDP quando ST 13 daria 1D−1; duas frações de Aparar têm o
  glifo ausente na impressão).

## Fora do PDF

O arquivo termina na página 150 (impressa 154), no meio do Capítulo 6. Faltam:
glossário, bibliografia, índice remissivo e o *Plano de Campanha de Artes Marciais*
(pág. impressa 158). `backup/gurps-3e-artes-marciais-full.pdf` pode conter essas
páginas — não foi usado aqui.
