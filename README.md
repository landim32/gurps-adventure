# GURPS Adventure — mesa de RPG assistida por IA

Este repositório é uma **mesa de GURPS 3ª Edição** (edição brasileira, Devir) preparada para
ser operada com o [Claude Code](https://claude.com/claude-code). A ideia é simples: os três
livros do sistema estão transcritos em Markdown dentro de `livros/`, e a IA usa esse material
como base de conhecimento para atuar como **assistente de mesa ou como Mestre do jogo**.

Não é um projeto de software — é conteúdo de RPG mais um punhado de automação. O único código
executável é um script que preenche a planilha de personagem.

## O que a IA faz aqui

- **Cria e edita personagens e NPCs** a partir de uma descrição em texto e um orçamento de
  pontos, calculando todos os custos e estatísticas derivadas.
- **Tira dúvidas de regra**, sempre conferindo nos livros — custos, níveis de habilidade,
  pré-requisitos e tabelas saem da transcrição, não da memória do modelo.
- **Escreve aventuras**, encontros, masmorras e tabelas de acaso.
- **Mestra partidas**: narra cenas, interpreta NPCs, arbitra testes e conduz combates.

Todo o conteúdo é em **português**, com a terminologia da edição brasileira (perícia, NH,
Vantagem/Desvantagem, Peculiaridade, DP/RD, Fadiga, Deslocamento, Carga, GDP/Balanço).

**Toda aventura se passa em Yrth**, o mundo do suplemento *GURPS Fantasy*. Lugares, reinos,
culturas, religiões e criaturas saem do que já existe no cenário antes de qualquer invenção.

![Mapa de Ytarria](livros/gurps-fantasy-3ed/banestorm_world.jpg)

*Ytarria, o continente conhecido de Yrth. Mapa em [`livros/gurps-fantasy-3ed/banestorm_world.jpg`](livros/gurps-fantasy-3ed/banestorm_world.jpg).*

## A pasta `livros/` — a base de conhecimento

O coração do projeto. São **~43.000 linhas de Markdown** com a transcrição literal dos
livros, organizada capítulo a capítulo, com um `README.md` em cada pasta mapeando arquivo →
capítulo. As referências internas dos originais (`pág. 86`, `MB pág. 21`) foram preservadas,
mas os números de página não viram títulos de seção — a navegação é por capítulo.

`livros/README.md` é o índice mestre dos volumes.

### `gurps-mb-3ed/` — Módulo Básico (~17.000 linhas, 24 capítulos)

O livro de regras. É a referência para praticamente tudo.

| Arquivos | Conteúdo |
|---|---|
| `02-criacao-de-personagem.md` | Atributos básicos, aparência, altura/peso, riqueza, status, reputação |
| `03-vantagens.md`, `04-desvantagens.md`, `05-peculiaridades.md` | As três listas com custo em pontos de cada traço |
| `06-pericias.md` | Todas as perícias, com dificuldade, nível pré-definido e pré-requisitos (o maior arquivo do acervo) |
| `07-equipamento-e-carga.md` | Dinheiro, armas, armaduras, dano básico por ST, níveis de Carga |
| `08-personagem-avancado.md` | Completar a ficha, evolução do personagem, personagens aleatórios |
| `09-testes-de-habilidade.md` | Testes, disputas, sucesso decisivo, falha crítica, testes de sentidos |
| `10-combate-basico.md`, `11-combate-avancado.md` | Os dois sistemas de combate — o avançado traz mapa hexagonal, localização de acertos e combate de perto |
| `12-ferimentos-doencas-fadiga.md` | Dano, recuperação, venenos, doenças |
| `13-combate-montado-veiculo.md`, `14-voo.md` | Combate a cavalo/em veículo e regras de voo |
| `15-animais.md` | Animais comuns e criaturas, com fichas de referência |
| `16-magia.md`, `17-psiquismo.md` | Resumo do sistema de magia e os poderes psíquicos |
| `18-o-mestre.md`, `19-cenarios.md`, `20-escrevendo-aventuras.md` | O ofício de mestrar: preparar sessões, montar cenários e escrever aventuras |
| `21-quadros-e-tabelas.md` | Todas as tabelas de consulta: armas, armaduras peça por peça, equipamento, reações, partes do corpo |
| `22-uma-noite-de-trabalho.md`, `23-caravana-para-ein-arris.md` | As duas aventuras que acompanham o livro |
| `24-glossario-e-apendices.md` | Glossário do sistema |

### `gurps-magia-3ed/` — Magia (~9.200 linhas, 113 páginas)

O suplemento completo de magia, muito além do resumo do Módulo Básico.

| Arquivos | Conteúdo |
|---|---|
| `02-principios-de-magia.md` | Como a magia funciona: mana, Aptidão Mágica, energia, tempo de conjuração, choque de retorno |
| `03-objetos-encantados.md` | Criação de itens mágicos e gemas de energia |
| `04` a `09-lista-*.md` | **As ~420 mágicas**, agrupadas por escola: animais, corpo, empatia, os quatro elementos, encantamentos, alimentos, cura, ilusão, reconhecimento, luz, quebrar, meta-mágicas, mente, movimentação, necromancia, plantas, proteção e som |
| `10-relacao-e-improviso.md` | Relação geral das mágicas e regras de magia improvisada |
| `11-magia-arcana.md`, `12-alquimia.md` | Runas, magia arcana e o sistema de alquimia com suas poções |
| `13-personagens.md` | Vantagens/desvantagens exclusivas de magos, **tipos de mago** (Aprendiz, Mago de Combate, Necromante…), equipar um mago e um catálogo racial ampliado (Gnomos, Goblins, Halflings, Orcs, Minotauros, licantropos) |
| `14-entidades-magicas.md`, `15-mundos-magicos.md` | Elementais, demônios e outras entidades; como calibrar o nível de magia de um mundo |

### `gurps-fantasy-3ed/` — Fantasy: o mundo de Yrth (~7.600 linhas)

O cenário oficial das aventuras deste repositório. O mapa de Ytarria é
[`livros/gurps-fantasy-3ed/banestorm_world.jpg`](livros/gurps-fantasy-3ed/banestorm_world.jpg).

| Arquivos | Conteúdo |
|---|---|
| `banestorm_world.jpg` | Mapa colorido de Ytarria |
| `02-historia.md` | O Cataclismo e a história de Yrth — como humanos de várias épocas da Terra foram parar lá |
| `03-cultura.md` | Sociedade, guildas, leis, religiões e vida cotidiana |
| `04` a `07-reinos-*.md` | Os reinos de Ytarria: Mégalos, Araterre, Caithness, os reinos islâmicos (al-Haz, al-Wazif, Cardiel), Sahud, os nômades, Zarak (anões), as terras élficas e órquicas |
| `08-personagens.md` | **Os arquétipos de personagem** (Cavaleiro, Mercenário, Ladrão, Clérigo, Trovador, Ranger, Nobre, Espião e mais uma dúzia), empregos e salários, e as raças de Yrth |
| `09-criaturas.md` | Bestiário do cenário |
| `10-campanhas.md` | Como estruturar campanhas em Yrth |

### `gurps-cyberpunk-3ed/` — Cyberpunk (~9.500 linhas, 128 páginas)

Suplemento de alta tecnologia (NT8): cyberwear, netrunning, equipamento e campanha.

| Arquivos | Conteúdo |
|---|---|
| `02-personagens.md` | Tipos de personagem, vantagens/desvantagens/perícias novas, tabela de empregos |
| `03-cyberwear.md` | Membros biônicos, implantes, chips, órgãos sensoriais |
| `04-tecnologia-e-equipamento.md` | Células de energia, armas, blindagem, drogas, tabela de armas |
| `05-netrunning.md` | Rede, cyberdecks, programas, gelo, combate no ciberespaço |
| `06-criacao-do-mundo.md` | Corporações, crime, GC, legalidade, sociedade |
| `07-a-campanha.md` | Como mestrar cyberpunk |

### Sobre a origem do material

A transcrição foi feita a partir dos PDFs da edição brasileira. `backup/` guarda o material
bruto desse processo (extrações do `pdftotext`, páginas da primeira passada e os PDFs
originais) — é histórico, não fonte de consulta. Os dois PDFs maiores ficam fora do
versionamento por excederem o limite de 100 MB do GitHub.

Este é material de uma obra comercial protegida por direitos autorais (Steve Jackson Games /
Devir). O acervo existe aqui para uso próprio na mesa; não redistribua os textos.

## Personagens

Cada personagem vive em `personagens/<nome-em-kebab-case>/` com quatro arquivos:

| Arquivo | O que é |
|---|---|
| `personagem.json` | Os dados estruturados — **a fonte da verdade**, usada para reeditar o personagem depois |
| `personagem.md` | A ficha em texto, legível, com todas as tabelas de custo e as notas de regra |
| `ficha.jpg` | A planilha oficial de GURPS preenchida, em imagem |
| `foto-prompt.md` | Um prompt pronto para gerar o retrato do personagem num gerador de imagens |

Se você colocar uma imagem (`foto.png`) na pasta do personagem, ela é encaixada
automaticamente no quadro de retrato da ficha.

**Quem usa magia ganha um grimório.** Personagens com Aptidão Mágica e mágicas compradas
recebem mais dois arquivos na mesma pasta: `grimorio.md` (a lista de mágicas em texto) e
`grimorio.jpg` — a Ficha para Grimório oficial preenchida com nome e classe da mágica, NH,
tempo de execução, duração, custo para fazer e para manter. Na planilha do personagem, a
lista de perícias traz só uma linha remetendo ao grimório, com a contagem e o total de
pontos, para não estourar o espaço da coluna.

A criação é feita pela skill `criar-personagem-gurps` (em `.claude/skills/`), que segue as
regras dos livros: monta a armadura peça por peça pelo Sistema Avançado de Combate, respeita
o limite de -40 pontos em desvantagens e, quando você cita um arquétipo ("um mercenário", "um
cavaleiro"), segue o que o livro descreve para aquele tipo.

Exemplos de pedido:

```
crie um personagem: mercenário anão de 150 pontos, especialista em machados, veterano e rabugento
edite o Comam: troque as picaretas por um machado de guerra e suba Tática
```

### Regerar as imagens

Requer Python 3 com [Pillow](https://python-pillow.org/):

```bash
python .claude/skills/criar-personagem-gurps/scripts/preencher_ficha.py \
  --data personagens/<slug>/personagem.json \
  --template ficha-de-personagem.jpg \
  --output personagens/<slug>/ficha.jpg

python .claude/skills/criar-personagem-gurps/scripts/preencher_grimorio.py \
  --data personagens/<slug>/personagem.json \
  --template grimorio.jpg \
  --output personagens/<slug>/grimorio.jpg
```

Os scripts escrevem sobre `ficha-de-personagem.jpg` e `grimorio.jpg` imitando escrita à mão,
com as coordenadas de cada campo calibradas sobre o formulário. O da ficha aceita
`--foto <caminho>` para escolher o retrato e `--sem-foto` para omiti-lo. O do grimório lê o
mesmo JSON, não faz nada se o personagem não tiver mágicas e pagina sozinho acima de 45
(`grimorio-2.jpg`, `grimorio-3.jpg`…).

## Aventuras

A campanha em andamento fica em **`campanha/`**, com o `README.md` indexando tudo: as
informações básicas, os personagens, o **plano** dividido em capítulos e o **histórico** do
que de fato aconteceu na mesa. Quando termina, ela é arquivada inteira em
`historico/campanhas/`. Só existe uma campanha ativa por vez, e quem cuida disso é a skill
`campanha`.

Pontos de vida, Fadiga e ferimento que fica moram em **`campanha/saude.md`**; o dinheiro de
cada um fica em **`campanha/bolsa.md`**, com extrato e saldo: a ficha do
personagem não é mexida por causa de moeda, nem por nada que a mesa produza — ela só muda
quando o usuário pede.

O que os jogadores declaram fazer entra pela skill `acao`: ela lê a ficha de quem age e o
estado da cena, decide o que a ação exige pelas regras, chama quem resolve o dado, narra o
desfecho e registra o que mudou.

O que a mesa muda no mundo — um NPC ferido, um item que trocou de dono, uma promessa — é
anotado por `campanha.py anotar` no `npcs.md`, `grupo.md` ou `lugares.md` da pasta de jogo
do capítulo, e consolidado em **`campanha/mundo.md`**: é ali que se lê como as coisas estão
agora, sem reler o histórico inteiro.

O plano segue o formato de *Caravana para Ein Arris*
(`livros/gurps-mb-3ed/23-caravana-para-ein-arris.md`): uma Descrição do Cenário que pode ser
lida aos jogadores, e depois capítulos como cenas encadeadas, com os testes e as
consequências de falha explícitos — inclusive falha crítica — para que cada cena possa ser
arbitrada sem improviso.

A campanha atual, **Tormento Vil**, foi adaptada de uma aventura escrita pelo dono do
projeto. Dela vem também um conjunto de **regras de combate autônomo** que vale como padrão
ao mestrar: teste de reação entre cada jogador e cada NPC; NPCs usam armas de longo alcance
primeiro e só partem para o combate de perto quando a munição acaba; miram no personagem mais
próximo, depois no de pior reação, depois em quem lhes causou mais dano; e os pontos de
impacto são decididos nos dados.

## Estrutura do repositório

```
livros/           transcrição dos três livros (base de conhecimento)
personagens/      um diretório por personagem, com ficha em JSON, Markdown e imagem
.claude/skills/   as skills de criação e os scripts da ficha e do grimório
backup/           material bruto da transcrição (histórico)
screenshots/      referências visuais
ficha-de-personagem.jpg   planilha oficial em branco, usada como modelo
grimorio.jpg      ficha para grimório em branco, usada como modelo
CLAUDE.md         instruções para a IA que opera o repositório
```
