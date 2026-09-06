---
name: criar-personagem-gurps
description: >
  Cria ou edita personagens de GURPS 3ª Edição a partir de uma descrição em texto e um
  orçamento de pontos, usando os três livros disponíveis em livros/ (Módulo Básico, Magia e
  Fantasy/Yrth). Se o pedido citar um dos "Tipos de Personagem" catalogados (Cavaleiro,
  Mercenário, Ladrão, Clérigo, Trovador, Ranger, Necromante, Mago de Combate, etc.), segue o
  que o livro descreve para aquele arquétipo. Calcula todos os custos e estatísticas
  derivadas, gera a ficha completa em Markdown e uma imagem da Planilha do Personagem
  preenchida — e, para usuários de magia, também a Ficha para Grimório com as mágicas.
  Use quando o usuário pedir para "criar um personagem de GURPS", "gerar uma
  ficha", "editar o personagem X", ou algo equivalente, normalmente citando pontos
  (ex.: "100 pontos") e uma descrição do conceito.
---

# Criar/Editar Personagem de GURPS 3ª Edição

Esta skill transforma uma descrição em texto ("um ladrão ágil e covarde", "uma maga élfica
nobre", "um guerreiro anão especialista em machados") mais um orçamento de pontos em uma
ficha de personagem de GURPS 3ª Edição completa, mecanicamente correta e pronta para jogar.

Ela produz sempre estes artefatos em `personagens/<nome-em-kebab-case>/`:

1. `personagem.md` — a ficha completa em Markdown (texto + todas as tabelas de custo).
2. `ficha.jpg` — a imagem oficial da Planilha do Personagem (`ficha-de-personagem.jpg`,
   na raiz do repositório) preenchida com os dados do personagem.
3. `foto-prompt.md` — um prompt pronto para gerar um retrato do personagem em um gerador de
   imagens estilo DALL-E (ver seção própria abaixo).

E, **somente quando o personagem for usuário de magia**, mais dois:

4. `grimorio.md` — a lista de mágicas em Markdown, com custo em pontos e notas de regra.
5. `grimorio.jpg` — a imagem oficial da Ficha para Grimório (`grimorio.jpg`, na raiz do
   repositório) preenchida — ver "Grimório" abaixo.

Se houver **uma imagem de retrato na pasta do personagem** (ex.: `foto.png`, gerada a partir
do `foto-prompt.md`), ela é colada automaticamente no quadro de retrato da ficha — ver
"Retrato na ficha" abaixo.

Um quarto arquivo, `personagem.json`, guarda os dados estruturados e **é o que permite editar
o personagem depois** — sempre releia esse arquivo antes de aplicar uma edição.

## Fontes de regras (`livros/`)

Este repositório contém a transcrição em Markdown de três livros de GURPS 3ª Edição
em `livros/`. **Consulte-os sempre que precisar do custo exato, da descrição ou dos
pré-requisitos de uma vantagem, desvantagem, perícia, mágica ou modelo racial** — não invente
valores de memória além do que está resumido abaixo nesta skill. Use Grep/Read diretamente
nos arquivos:

| Preciso de... | Arquivo |
|---|---|
| Lista de vantagens e custos | `livros/gurps-mb-3ed/03-vantagens.md` |
| Lista de desvantagens e custos (limite sugerido: -40 pts) | `livros/gurps-mb-3ed/04-desvantagens.md` |
| Peculiaridades (até 5, -1 pt cada) | `livros/gurps-mb-3ed/05-peculiaridades.md` |
| Lista de perícias, pré-requisitos, especializações | `livros/gurps-mb-3ed/06-pericias.md` |
| Armas e equipamento geral (custo/peso) | `livros/gurps-mb-3ed/07-equipamento-e-carga.md` e `21-quadros-e-tabelas.md` |
| Armaduras **peça por peça** (Sistema Avançado de Combate — sempre use esta tabela, não a de armadura completa) | `livros/gurps-mb-3ed/21-quadros-e-tabelas.md`, seções "Armaduras Antigas/Medievais" e "Armaduras Modernas e Ultra-Modernas" |
| Riqueza, Status, Reputação, Alfabetização | `livros/gurps-mb-3ed/02-criacao-de-personagem.md` (seção "Riqueza e Status") |
| Regras de combate — **esta skill sempre usa o Sistema Avançado**, não o Básico | `livros/gurps-mb-3ed/11-combate-avancado.md` (Cap. 14 completo: movimento, localização de acertos, combate de perto, armas de longo alcance) |
| Tabela de Partes do Corpo (localização de acerto, usada para mapear cada peça de armadura) | `livros/gurps-mb-3ed/21-quadros-e-tabelas.md`, seção "Partes do Corpo" |
| Magia — princípios, custo de mágicas como perícia | `livros/gurps-mb-3ed/16-magia.md` e `livros/gurps-magia-3ed/02-principios-de-magia.md` |
| Lista de mágicas por escola | `livros/gurps-magia-3ed/04-*.md` a `09-*.md` (uma mágica é sempre uma perícia Mental/Difícil ou Muito Difícil — use a tabela de custo de perícias mentais) |
| Psiquismo | `livros/gurps-mb-3ed/17-psiquismo.md` |
| **Arquétipos (“Tipos de Personagem”) medievais/fantasia** | `livros/gurps-fantasy-3ed/08-personagens.md`, seção "Tipos de Personagem" |
| **Arquétipos de mago (“Tipos de Personagens de Mágicos”)** | `livros/gurps-magia-3ed/13-personagens.md`, seção "Tipos de Personagens de Mágicos" |
| Vantagens/desvantagens/perícias exclusivas de magos (Aptidão Mágica seletiva, Abascanto, Uma Única Escola, Percepção do Corpo…) | `livros/gurps-magia-3ed/13-personagens.md` (caps. Vantagens/Desvantagens/Novas Perícias) |
| Modelos raciais — Yrth | `livros/gurps-fantasy-3ed/08-personagens.md`, seção "Personagens Não-Humanos" |
| Modelos raciais — lista ampliada (Gnomos, Goblins, Halflings, Orcs, Minotauros, Licantropos…) | `livros/gurps-magia-3ed/13-personagens.md`, seção "Personagens Não-Humanos" |
| Equipando um mago / empregos de mago | `livros/gurps-magia-3ed/13-personagens.md` (seções "Dinheiro e Equipamentos" e "Empregos para Mágicos") |
| **Mapa de Ytarria** (continente conhecido de Yrth; situar origem, viagens, fronteiras) | `livros/gurps-fantasy-3ed/banestorm_world.jpg` |
| **Línguas de Yrth** (quem fala o quê, dificuldade, níveis pré-definidos entre idiomas) | `livros/gurps-fantasy-3ed/03-cultura.md`, seção "Línguas" |
| Regras de línguas (custo, comunicação, o que cada NH significa) | `livros/gurps-mb-3ed/06-pericias.md`, seção "Perícias com Línguas" |
| Cultura, reinos, religiões de Yrth (para história/aparência) | `livros/gurps-fantasy-3ed/02-historia.md` a `07-reinos-oriente.md` |
| Animais e criaturas (para Empatia com Animais, montarias, etc.) | `livros/gurps-mb-3ed/15-animais.md`, `livros/gurps-fantasy-3ed/09-criaturas.md` |

Use `Grep` para procurar o nome de uma vantagem/desvantagem/perícia específica em vez de ler
o arquivo inteiro (ex.: `Grep "Sorte" livros/gurps-mb-3ed/03-vantagens.md`). É transcrição de
obra comercial protegida: use à vontade para arbitrar regras e montar fichas dentro do
projeto, mas não reproduza trechos longos literalmente para fora dele.

## Fluxo de trabalho

### 1. Entender o pedido

Extraia do pedido do usuário:

- **Nome do personagem** (se não for dado, invente um condizente com o conceito/cenário e
  confirme no resultado final — não precisa perguntar ao usuário).
- **Orçamento de pontos** (`pontos_gastar`). Se não for informado, use 100 (herói padrão,
  ver tabela de categorias em `02-criacao-de-personagem.md`) e avise isso no resumo final.
- **Local de origem** (reino, cidade ou povo de Yrth) — define a língua nativa obrigatória e
  ajuda na história. Se o usuário não disser, escolha algo coerente com o conceito e informe.
- **Idade** (`idade`, em anos) — **obrigatória**, porque ela limita quantos pontos podem ir
  para perícias (ver "Idade e o teto de perícias"). Se o usuário não disser, escolha uma idade
  coerente com o conceito *e* com o repertório que você pretende montar, e informe no resumo.
- **Conceito**: raça, profissão/arquétipo, cenário (medieval/fantasia de Yrth por padrão,
  já que é o cenário coberto por `livros/gurps-fantasy-3ed/`; ajuste para NT diferente se o
  usuário pedir algo moderno/sci-fi, usando as tabelas de `21-quadros-e-tabelas.md`).
- Traços de personalidade específicos mencionados (vantagens/desvantagens/peculiaridades
  óbvias a partir da descrição).

### 2. Escolher um modelo racial (se aplicável)

Se o personagem não for humano, aplique o modelo racial do livro correspondente:

- **Fantasy/Yrth** (`gurps-fantasy-3ed/08-personagens.md`): Centauro 65, Anão 30, Elfo 40,
  Elfo Negro 30, Meio-Elfo 30, Gigante 175.
- **Magia** (`gurps-magia-3ed/13-personagens.md`) — lista mais ampla, use para raças que não
  estão no Fantasy: Anões 30, Gnomos 20, Goblins 5, Hobgoblins -25, Halflings, Kobolds,
  Minotauros, Orcs, Meio-Orcs, Elfos, Elfos Negros, Meio-Elfos, Reptantes, além dos
  Transmutantes/licantropos (Homem-Lobo, Homem-Urso, Homem-Javali, Homem-Tigre, Homem-Águia,
  Homem-Cobra). **Sempre leia a entrada da raça antes de usar** — os custos e modificadores
  estão lá.
- **Módulo Básico** (`gurps-mb-3ed/02-criacao-de-personagem.md`): Elfo genérico, 40 pts.

Quando a mesma raça aparece em mais de um livro (Anão, Elfo, Meio-Elfo, Elfo Negro), há
pequenas divergências entre as versões (ex.: a escala de Carga dos Anões). **Numa campanha de
Yrth, prefira a versão do Fantasy**; fora dela, use a do Magia. Diga qual versão adotou no
resumo final.

O custo da raça entra como uma "vantagem" na lista de Vantagens/Desvantagens da ficha
(ex.: "Raça: Elfo, +40"). Modificadores de atributo raciais (ex.: Elfo +1 DX +1 IQ -1 ST) se somam ao valor
*final* do atributo, mas **não** alteram o custo em pontos desse atributo (o custo continua
sendo lido pelo valor pago na tabela, antes do bônus racial — releia o exemplo do Anão em
`08-personagens.md` se tiver dúvida).

### 3. Escolher arquétipo e montar Vantagens / Desvantagens / Perícias

**Se o pedido citar (ou descrever claramente) um dos arquétipos catalogados nos livros, o
arquétipo é a base obrigatória do personagem — não uma sugestão.** Antes de escolher
qualquer traço, abra a seção correspondente e siga o que ela descreve.

Arquétipos disponíveis:

- **Fantasy — “Tipos de Personagem”** (`gurps-fantasy-3ed/08-personagens.md`):
  Administrador, Assassino, Trovador, Clérigo, Artesão, Diplomata, Curandeiro, Cavaleiro,
  Mercenário, Mercador, Monge, Nobre, Ranger, Palatino, Escolástico, Espião, Escudeiro,
  Sibarita, Ladrão.
- **Magia — “Tipos de Personagens de Mágicos”** (`gurps-magia-3ed/13-personagens.md`):
  Aprendiz, Mago de Combate, João-de-Uma-Mágica-Só, Guarda-costas, Mago Amador, Recreador,
  Curandeiro, Mago Caipira, Mercador, Necromante, Escolástico, Espião, Sibarita, Ladrão,
  Mago Tradicional.
- **Módulo Básico — “Tipos de Personagens”** (`gurps-mb-3ed/02-criacao-de-personagem.md`),
  mais genéricos: Guerreiro, Ladrão/Espião, Mago, Clérigo, Assoldado, Mecânico, Ranger,
  Especialista.

Como seguir um arquétipo:

1. **Leia a entrada inteira** (`Grep`/`Read` no arquivo) antes de montar a ficha.
2. **Traços obrigatórios do texto viram obrigatórios na ficha** — quando a entrada diz que o
   personagem *precisa* de algo, isso não é opcional. Exemplos reais: o Clérigo precisa da
   vantagem Clericato; o Cavaleiro precisa de um Dever, Status 2, Riqueza no mínimo
   Confortável, ao menos 10 pontos de Poderes Legais e as perícias obrigatórias Espadas de
   Lâmina Larga e Lança de Justa; qualquer mago precisa de Aptidão Mágica.
3. **Priorize as listas de Vantagens / Desvantagens / Perícias da própria entrada** ao gastar
   os pontos; escolha entre elas as que combinam com a descrição dada pelo usuário. Só saia
   da lista quando o orçamento sobrar ou quando o conceito do usuário exigir algo que a
   entrada não cobre.
4. **Distribua os atributos conforme o texto** — várias entradas dizem quais atributos
   importam (ex.: Mago de Combate quer os quatro equilibrados; Ladrão/Espião quer IQ e DX).
5. **Respeite Status/Riqueza sugeridos** pela entrada (Nobre e Cavaleiro têm Status alto;
   Aprendiz costuma ter um Patrono; Artesão tem Status de guilda etc.).
6. **O pedido do usuário tem prioridade sobre o arquétipo em caso de conflito** — se ele
   descreve um cavaleiro pobre e sem honra, mantenha o pedido e ajuste o arquétipo, citando
   o desvio no resumo final.
7. Para magos, combine as duas fontes: o arquétipo de mago (Magia) define o perfil de
   mágicas, e as regras de mágicas/Aptidão Mágica continuam vindo de
   `gurps-magia-3ed/02-principios-de-magia.md` + listas de mágicas.

Se **nenhum** arquétipo for citado, use as entradas apenas como inspiração livre. Em todos os
casos, confira o custo exato de cada vantagem/desvantagem/perícia nos arquivos de regras
antes de anotar, e diga no resumo final qual arquétipo foi usado como base.

Limites a respeitar:
- Desvantagens: até -40 pontos no total (uma única desvantagem grave pode passar disso, ver
  `04-desvantagens.md`).
- Peculiaridades: até 5, -1 ponto cada.
- **Perícias na criação: no máximo 2× a idade em pontos** — ver a seção própria logo abaixo.
  Não é um detalhe de NPC jovem: um personagem com muitas mágicas estoura o teto fácil.
- Um mago precisa de Aptidão Mágica (vantagem, ver `16-magia.md`) antes de comprar mágicas.
  Mágicas são perícias Mental/Difícil (a maioria) ou Mental/Muito Difícil — use a tabela de
  custo de perícias mentais abaixo.

### Idade e o teto de perícias (obrigatório em todo personagem)

> O número máximo de pontos que um personagem em processo de criação pode usar para comprar
> Perícias é igual **ao dobro de sua idade**. […] Este limite **não** se aplica às perícias
> acrescentadas *após* a criação do personagem.
> — MB, `06-pericias.md`, e a mesma regra em `02-criacao-de-personagem.md`

O raciocínio do livro é que esse número representa todo o treinamento que a pessoa conseguiu
acumular até entrar em jogo. Portanto:

- **`pontos em perícias + pontos em mágicas ≤ 2 × idade`.** Mágicas *são* perícias e contam no
  mesmo teto — é justamente aí que o limite costuma estourar, porque um mago com 20 mágicas
  passa dos 70 pontos sem esforço.
- Vantagens, desvantagens, peculiaridades e atributos **não** entram nessa conta.
- Vale o inverso também, e é assim que se usa na prática: depois de fechar a lista de
  perícias, **a idade mínima do personagem é `ceil(pontos_em_perícias ÷ 2)`**. Se o conceito
  pedir alguém mais jovem do que isso, corte perícias ou realoque pontos para atributos e
  vantagens — não "arredonde" a regra.

**Escolha a idade junto com o repertório, não depois.** Um mago de 150 pontos com 98 em
mágicas e perícias precisa ter no mínimo 49 anos. Um espadachim de 20 anos não passa de 40
pontos em perícias, por mais que sobre orçamento.

Duas desvantagens ligadas à idade (`04-desvantagens.md`):

- **Idade**: -3 pontos por ano **acima de 50**. Exatamente 50 não custa nada. Acima disso, o
  personagem precisa fazer as jogadas de envelhecimento (`02-criacao-de-personagem.md`,
  "Idade e Envelhecimento") arriscando perder atributos — avise o usuário antes de adotar.
- **Juventude**: -2 pontos por ano abaixo da maioridade (máximo 3 anos, -6). Dá -2 de reação
  com adultos e precisa ser "recomprada" quando o personagem crescer.

Registre a idade em `idade` no JSON e cite-a no `personagem.md`. O formulário impresso não tem
campo de idade, então **mencione-a no texto de `aparencia`** ("50 anos, esquelético…") para que
ela apareça na ficha. Ao **editar** um personagem, reconfira o teto: subir uma perícia ou
comprar uma mágica nova pode passar do limite da idade dele.

Personagens não-humanos com expectativa de vida diferente (Elfos, Anões) seguem a mesma
aritmética — o teto é sobre a idade em anos, não sobre a maturidade relativa da raça. Se o
Mestre quiser flexibilizar isso para um elfo centenário, é decisão dele; a skill não assume.

### 4. Calcular tudo (ver fórmulas na seção seguinte)

Depois de escolher atributos, vantagens, desvantagens, peculiaridades e perícias, calcule:

1. Custo de cada atributo (tabela abaixo) → some para obter "Atributos".
2. Some os custos de Vantagens (positivos) e Desvantagens (negativos) separadamente para o
   Resumo, mas eles ficam juntos na mesma lista da ficha ("Vantagens, Desvantagens").
3. Peculiaridades: -1 cada.
4. Custo de cada perícia pela tabela de dificuldade (abaixo), a partir do atributo base +
   modificadores (Aptidão Mágica para mágicas, bônus raciais, etc.).
   **Inclua as línguas** — a nativa custa 0 e vem com NH = IQ; as demais seguem a tabela de
   perícias mentais (ver seção "Línguas").
   **Mágicas também são perícias e contam aqui**, mesmo morando no array `magias` em vez de
   `pericias` (ver seção "Grimório").
5. **Confira o teto da idade**: `soma(pericias[].custo) + soma(magias[].custo) ≤ 2 × idade`.
   Estourou? Ou envelheça o personagem (é quase sempre a saída melhor — mais anos explicam o
   repertório), ou corte perícias/mágicas. Acima de 50 anos entra a desvantagem Idade.
6. **Total gasto = Atributos + Vantagens + Desvantagens + Peculiaridades + Perícias.**
   Ajuste perícias/vantagens/atributos iterativamente até `Total gasto == pontos_gastar`
   (ou o mais próximo possível sem ultrapassar; nunca exceda o orçamento). Pontos sobrando
   devem preferencialmente ser investidos em subir o nível de mais uma perícia ou vantagem
   em vez de ficarem sem uso — respeitando o teto do item 5.
7. Estatísticas derivadas (Fadiga, Pontos de Vida, Dano Básico, Velocidade Básica,
   Deslocamento, Carga, Defesa Passiva, Defesas Ativas) — fórmulas na seção seguinte.
8. Equipamento: escolha itens condizentes com o conceito e o nível de Riqueza dentro do
   dinheiro inicial (`02-criacao-de-personagem.md`, seção Riqueza; preços em
   `21-quadros-e-tabelas.md`). Some o **peso total** (`peso_total`, em kg) e o **custo
   total** (`custo_total`, em $) e recalcule Deslocamento se a Carga mudar de faixa.
   **Armadura sempre montada peça por peça** — ver seção "Armadura peça por peça" abaixo.
9. Agrupe **perícias**, **equipamento** e **mágicas** por categoria (campo `categoria` em
   `pericias[]`, `armas_objetos[]` e `magias[]`) e ordene cada lista por esse campo — a ficha
   e o grimório desenham uma linha em branco a cada troca de categoria. Para equipamento, use
   `Armas` → `Munição` → `Armadura` → `Equipamento`; para mágicas, o **colégio**
   (Fogo, Proteção, Mente…).

### Línguas (obrigatório em todo personagem)

**Todo personagem tem pelo menos uma língua na ficha: a do seu local de origem.** Decida de
onde ele vem antes de montar as perícias e adicione uma segunda língua sempre que o conceito,
a raça, o arquétipo ou a profissão justificarem.

**Custo (MB, "Perícias com Línguas"):**

- A **língua nativa é grátis** e vem com **NH = IQ**. Subir além disso é barato e linear —
  IQ+1 custa 1 ponto, IQ+2 custa 2, IQ+3 custa 3 (não use a tabela normal de perícias mentais
  para a própria língua).
- **Outras línguas** são perícias mentais comuns: use a tabela de perícias mentais, quase
  sempre **Mental/Média** (o sahudês é **Mental/Difícil**). Não têm nível pré-definido, salvo
  entre idiomas aparentados (ver tabela abaixo).
- A vantagem **Facilidade para Línguas** (2 pontos/nível, `03-vantagens.md`) soma-se à IQ para
  efeito de aprender qualquer língua — vale a pena em diplomatas, mercadores e espiões.
- O que cada NH significa: 7-8 = vocabulário funcional com sotaque forte; 9-10 = como um
  falante nativo médio; 13-14 = domínio completo, sem sotaque. Um NH baixo é ótimo recurso de
  interpretação, não um defeito a evitar.

**Línguas de Yrth** (`03-cultura.md`) — todas Mental/Média, exceto onde indicado:

| Língua | Quem fala | Observações |
|---|---|---|
| **Ânglico** | Nações cristãs (Mégalos, Caithness, Cardiel…) | A língua franca das terras humanas; a maioria dos não-humanos que vive entre humanos também a fala |
| **Norlandês** | Povos do norte | Aparentado ao ânglico: pré-definido mútuo -3 |
| **Arlesiano** | Araterre | Dialeto do ânglico misturado com francês; pré-definido -2 a partir de ânglico ou francês. O *Arlesiano Antigo* das ilhas do sul é Arlesiano-2 / ânglico-4 |
| **Árabe** | Nações islâmicas (al-Haz, al-Wazif, parte de Cardiel) | Árabe clássico; escrita quase idêntica à da Terra |
| **Latim** | Escolásticos, clérigos cristãos e nobres megalanos | Língua de erudição e liturgia, não do dia a dia |
| **Ladino** | Comunidades judaicas | Ligado ao espanhol, escrito em caracteres hebraicos; pré-definido Espanhol-3 |
| **Hebraico** | Judeus (uso litúrgico/erudito) | Estudo dos textos religiosos |
| **Sahudês** | Sahud | **Mental/Difícil**; tão distante das raízes que ninguém da Terra o entende |
| **Anão, Élfico** | Raças Ancestrais | Cada uma tem a sua; muitos anões e elfos também falam ânglico |
| **Goblinês Arcaico** | Goblins (quase extinto) | Sobrevive na *língua dos mercadores goblins*, um jargão usado entre comerciantes da raça |

Halflings e kobolds perderam o idioma próprio e falam a língua humana local.

**Como escolher:**

1. **Língua de origem** — sempre presente, grátis, NH = IQ. Um mercenário de al-Haz fala
   Árabe; um cavaleiro de Caithness fala Ânglico; um anão de Zarak fala Anão.
2. **Segunda língua**, quando fizer sentido:
   - **Não-humano vivendo em terras humanas**: a língua da raça + o ânglico local.
   - **Quem cruza fronteiras** (mercenário, mercador, espião, diplomata, marinheiro): o
     ânglico como língua franca, mesmo que num NH baixo e com sotaque.
   - **Clérigo, monge, escolástico, nobre megalano**: Latim.
   - **Arquétipos que pedem explicitamente** — Diplomata, Mercador, Administrador, Nobre e
     Monge listam "qualquer Língua (geralmente várias)" em `08-personagens.md`.
   - **Judeu de Mégalos ou Tredroy**: Ladino, mais o hebraico se for estudioso.
3. Registre cada língua como uma perícia na lista, com `"categoria": "Línguas"` — elas ganham
   seu próprio bloco na ficha. Marque a nativa no nome: `"Árabe (nativa)"`.

### Armadura peça por peça (Sistema Avançado de Combate)

Esta skill **nunca** usa a regra simplificada de "armadura completa" do Sistema Básico
(uma única DP/RD para o corpo todo). Sempre monte a armadura região por região, usando as
tabelas de `21-quadros-e-tabelas.md` ("Armaduras Antigas/Medievais" ou "Armaduras Modernas e
Ultra-Modernas", conforme o NT do cenário):

- Escolha uma peça (ou nenhuma) para cada região relevante: **Cabeça**, **Tronco**, **Braços**
  (par ou unidade), **Mãos**, **Pernas** (par ou unidade), **Pés**. Nem toda região precisa de
  proteção — um personagem pode perfeitamente andar sem luvas ou capacete.
  Localização de acerto/mapeamento de áreas do corpo em
  `21-quadros-e-tabelas.md` → "Partes do Corpo" (cabeça=áreas 3-5, braços=6/8, mãos=7,
  tronco=9-11 e 17-18, pernas=12-14, pés=15-16).
- **Cada peça vestida vira sua própria linha em `armas_objetos`**, com `dano: "-"`,
  `tipo` mostrando `DP{n}/RD{n}` (e a exceção contra perfurante entre parênteses quando a
  tabela indicar, ex.: Cota de Malha → `DP3/RD4 (DP1/RD2 vs. perf.)`), custo e peso exatos
  da tabela. Nunca agregue várias peças numa linha só "armadura genérica".
- O campo único `defesa_passiva.armadura` da ficha (que só comporta um número, por limitação
  do formulário impresso) recebe a **DP da peça de tronco** — é a região mais atingida e a
  referência padrão quando o ataque não mira um local específico. `defesa_passiva.total` =
  `armadura + escudo`. As DP/RD das demais regiões (cabeça, braços, mãos, pernas, pés) ficam
  registradas apenas nas linhas de equipamento, para consulta quando um ataque específico
  mirar aquela região (redutor de NH da Tabela de Partes do Corpo).
- Se duas peças se sobrepõem na mesma região (ex.: laudel por baixo de loriga de couro),
  aplique as regras de "Armaduras Sobrepostas" (`07-equipamento-e-carga.md`) e registre o
  resultado combinado como uma única linha para aquela região (não duas linhas competindo
  pela mesma área).
- Some o peso de **todas** as peças (mais armas e demais itens) para `peso_total` e para
  recalcular a faixa de Carga/Deslocamento.

### Grimório (personagens usuários de magia)

**Se o personagem tiver Aptidão Mágica e ao menos uma mágica comprada, ele ganha um
grimório** — a Ficha para Grimório oficial (`grimorio.jpg`, na raiz do repositório),
preenchida do mesmo jeito que a Planilha do Personagem. Vale para magos, clérigos com
mágicas clericais, bardos com magia e qualquer outro conjurador; personagens sem mágicas
não têm grimório e nada é gerado.

As mágicas ficam no array `magias[]` do `personagem.json` — **não** em `pericias[]`, que
encheria a lista de perícias da ficha. Mas mecanicamente **elas continuam sendo perícias**:

- Cada mágica é uma perícia Mental/Difícil (a maioria) ou Mental/Muito Difícil — custo pela
  tabela de perícias mentais, com a **Aptidão Mágica somando ao NH** (não ao custo).
- O custo em pontos de cada mágica entra no campo `custo` da própria mágica e **soma em
  `resumo.pericias`** — o formulário impresso não tem uma linha "Mágicas" no Resumo.
- Na área de Perícias da ficha, o script escreve sozinho uma linha final
  `Mágicas (ver grimório)` com a quantidade e o total de pontos. Não escreva essa linha à mão.
- Respeite os **pré-requisitos** (`gurps-magia-3ed/`, entrada de cada mágica): não compre
  Bola de Fogo sem Criar Fogo. Registre o pré-requisito na coluna `obs`.

Preencha uma coluna do formulário por campo, consultando a entrada da mágica no livro:

| Coluna impressa | Campo | Conteúdo |
|---|---|---|
| Nome e Classe da Mágica | `nome` + `classe` | O script escreve `Nome (Classe)`. Abrevie a classe: `R` Regular, `A` Área, `M` Míssil, `B` Bloqueio, `I` Informação, `E` Especial, `Enc` Encantamento |
| NH | `nh` | Nível de habilidade final (IQ + níveis comprados + Aptidão Mágica) |
| Tempo op. | `tempo` | Tempo de execução (`1 seg`, `1-3 seg`, `10 seg`…); a maioria é 1 segundo |
| Duração | `duracao` | `1 min`, `instant.`, `permanente`… |
| Custo p/fazer | `custo_fazer` | Custo básico em energia (`2`, `1/dado`, `2/hex`) |
| Custo p/manter | `custo_manter` | Custo de manutenção (`metade`, `1`, `—` quando não se aplica) |
| Obs. | `obs` | Pré-requisito, resistência (`Resistida por HT`), dano, limites |
| Pág. | `pag` | Fonte: `M` (livro de Magia) ou `MB` (Módulo Básico) — a coluna é estreita |

Cabem **45 mágicas por página**; havendo mais, o script gera `grimorio-2.jpg` e assim por
diante sozinho.

### 5. Gerar os arquivos de saída

1. Escreva `personagens/<slug>/personagem.json` com o esquema descrito abaixo.
2. Escreva `personagens/<slug>/personagem.md` com a ficha completa em prosa/tabelas
   Markdown (histórico, atributos, vantagens, desvantagens, peculiaridades, perícias,
   equipamento, resumo de pontos).
3. Escreva `personagens/<slug>/foto-prompt.md` com o prompt de imagem (ver seção
   "Prompt de imagem do personagem" abaixo).
4. Rode o script para gerar a imagem da ficha (se já houver um retrato na pasta, ele é
   colado sozinho no quadro central):

   ```
   python .claude/skills/criar-personagem-gurps/scripts/preencher_ficha.py \
     --data personagens/<slug>/personagem.json \
     --template ficha-de-personagem.jpg \
     --output personagens/<slug>/ficha.jpg
   ```

5. **Só se o personagem tiver mágicas** (ver "Grimório" acima): escreva
   `personagens/<slug>/grimorio.md` e rode o script do grimório.

   ```
   python .claude/skills/criar-personagem-gurps/scripts/preencher_grimorio.py \
     --data personagens/<slug>/personagem.json \
     --template grimorio.jpg \
     --output personagens/<slug>/grimorio.jpg
   ```

   Sem mágicas no JSON o script não gera nada (só avisa) — não é preciso testar antes.

6. Confirme ao usuário: nome, conceito, **arquétipo e raça usados como base (e de qual
   livro)**, pontos gastos vs. orçamento, qualquer desvio consciente do arquétipo, e os
   caminhos dos arquivos gerados (ficha em Markdown, imagem da ficha, prompt de imagem e,
   para conjuradores, o grimório em Markdown e em imagem).

### Nome do arquivo (slug kebab-case)

Converta o nome do personagem para minúsculas, remova acentos, troque espaços e caracteres
não alfanuméricos por hífen único, sem hífen duplicado nas pontas. Ex.: "Dai Blackthorn" →
`dai-blackthorn`; "Kýra Åsvaldsdóttir" → `kyra-asvaldsdottir`.

## Editando um personagem existente

Se o usuário pedir para alterar um personagem já criado:

1. Localize `personagens/<slug>/personagem.json` (procure por nome aproximado se o slug
   exato não for óbvio).
2. Leia o JSON — ele é a fonte da verdade, não a imagem nem o Markdown.
3. Aplique a mudança pedida (trocar uma perícia, subir um atributo, adicionar uma
   vantagem, trocar equipamento etc.).
4. **Recalcule tudo do zero** a partir dos dados atualizados (não apenas o campo alterado —
   uma mudança de atributo, por exemplo, muda Fadiga, Pontos de Vida, Dano Básico,
   Velocidade, Carga e o custo/NH de toda perícia baseada naquele atributo). Para
   conjuradores, uma mudança de IQ ou de Aptidão Mágica muda o NH de **todas** as mágicas.
   **Reconfira o teto da idade** (`pericias + magias ≤ 2 × idade`): comprar uma mágica nova ou
   subir uma perícia pode estourá-lo. Se o personagem não tiver `idade` no JSON (fichas
   antigas), calcule a mínima necessária, escolha uma coerente com a história e grave o campo.
5. Regrave os quatro arquivos (json, md, jpg, foto-prompt.md) no mesmo lugar, sobrescrevendo.
   Só é preciso reescrever o `foto-prompt.md` se a edição mudou algo visual (aparência,
   raça, equipamento, vantagens/desvantagens físicas) — se for só um ajuste de perícia ou
   ponto, pode deixar o prompt como está.
   Se o personagem tiver mágicas, regrave também `grimorio.md` e rode de novo o
   `preencher_grimorio.py`. Um personagem que **passou a ter** mágicas ganha grimório agora;
   um que perdeu todas deixa de ter — apague os arquivos órfãos.
6. Informe ao usuário o que mudou e o novo total de pontos.

## Prompt de imagem do personagem (`foto-prompt.md`)

Depois de fechar a ficha, escreva em `personagens/<slug>/foto-prompt.md` um prompt pronto
para colar em um gerador de imagens estilo DALL-E, para um retrato do personagem. Estrutura
do arquivo:

```markdown
# Prompt de Imagem — <Nome do Personagem>

<o prompt em si, em inglês, um único parágrafo>

*Estilo:* desenho/ilustração (não fotorrealista).
```

Monte o prompt combinando, num único parágrafo em **inglês** (gera resultados mais
consistentes na maioria dos modelos de imagem):

1. **Estilo/mídia**, sempre no início: algo como *"Digital illustration, fantasy character
   concept art, clean linework with soft coloring, in the style of a hand-drawn RPG character
   portrait"* — adapte o adjetivo de estilo ao tom do personagem (sombrio, cômico, heroico),
   mas mantenha sempre "illustration"/"drawing"/"concept art", nunca "photo" ou
   "photorealistic".
2. **Sujeito**: gênero, raça (se não-humano, descreva os traços do modelo racial — orelhas
   pontudas e esguio para Elfo, baixo e atarracado com barba para Anão, etc.), idade
   aproximada e o que vem do campo `aparencia`.
3. **Traços físicos marcantes**: qualquer vantagem/desvantagem com efeito visual óbvio
   (Cicatriz, Hediondo/Elegante, Gigantismo/Nanismo, Albinismo, Coxeadura, etc.) e a
   compleição sugerida pelos atributos (ST alto → físico robusto; DX alto → postura ágil).
4. **Roupas e equipamento**: derive da lista `armas_objetos` — armas visíveis e o conjunto de
   peças de armadura vestidas (cabeça, tronco, braços, mãos, pernas, pés), descrevendo o
   material/aspecto de cada uma (couro, malha, placas...), cores ou insígnias mencionadas na
   história. Não é preciso citar DP/RD no prompt, só a aparência de cada peça.
5. **Expressão/pose**: sugerida pelas peculiaridades e pela história (ex.: postura alerta e
   desconfiada para um ladrão; postura orgulhosa para um nobre).
6. **Cenário/composição**: mantenha simples e neutro — *"plain neutral background, character
   reference sheet pose, portrait framing from the waist up, centered"* — para funcionar como
   um retrato de referência, a menos que a história sugira um cenário mais específico que
   valha a pena mostrar.

Não inclua números de jogo (pontos, NH, custos) no prompt — ele é só para a aparência visual.
Se o usuário pedir um estilo de imagem diferente (ex.: pixel art, aquarela, anime), substitua
apenas o item 1 mantendo o resto.

## Retrato na ficha

O quadro em branco no centro da Planilha do Personagem é a área de retrato. O script preenche
esse quadro **automaticamente** quando encontra uma imagem na pasta do personagem:

- **Detecção automática**: qualquer arquivo `.png`, `.jpg`, `.jpeg`, `.webp` ou `.bmp` na
  pasta `personagens/<slug>/`, ignorando a própria `ficha.jpg`. Nomes começando com `foto`,
  `retrato`, `imagem` ou `portrait` têm prioridade; havendo várias, usa a primeira em ordem
  alfabética.
- **Escolha explícita**: campo `"foto": "arquivo.png"` no `personagem.json` (caminho relativo
  à pasta do personagem) ou o argumento `--foto <caminho>` na linha de comando.
- **Desligar**: argumento `--sem-foto`.

A imagem é redimensionada para caber no quadro preservando a proporção e centralizada
(o quadro tem 784×1169 px, proporção ~2:3 — retratos verticais aproveitam melhor o espaço).
PNGs com transparência são colados usando o canal alfa. Se o arquivo não existir ou estiver
corrompido, o script apenas avisa e gera a ficha sem retrato.

Fluxo típico: gere a ficha → use o `foto-prompt.md` num gerador de imagens → salve o
resultado como `personagens/<slug>/foto.png` → rode o script de novo para a ficha sair com o
retrato. Ao editar um personagem que já tem retrato, ele é reaplicado sozinho.

## Fórmulas e tabelas mecânicas (Módulo Básico)

### Custo dos 4 atributos (ST, DX, IQ, HT) — idêntico para os quatro

| Nível | Custo | Nível | Custo | Nível | Custo |
|---|---|---|---|---|---|
| 1 | -80 | 8 | -15 | 15 | 60 |
| 2 | -70 | 9 | -10 | 16 | 80 |
| 3 | -60 | 10 | 0 | 17 | 100 |
| 4 | -50 | 11 | 10 | 18 | 125 |
| 5 | -40 | 12 | 20 | 19 | 150 |
| 6 | -30 | 13 | 30 | 20 | 175 |
| 7 | -20 | 14 | 45 | acima de 20 | +25/nível |

(Detalhe completo e tabela de "o que cada nível significa" em `02-criacao-de-personagem.md`.)

### Estatísticas derivadas

- **Fadiga** = ST. **Pontos de Vida** = HT.
- **Velocidade Básica** = (HT + DX) / 4 (não arredondar).
- **Deslocamento** = Velocidade Básica − penalidade de Carga, arredondado para baixo (ver
  Carga abaixo). Deslocamento nunca é reduzido a zero exceto casos extremos.
- **Esquiva** = Deslocamento. **Aparar** = NH da arma ÷ 2 (arredondado para baixo).
  **Bloqueio** = NH de Escudo ÷ 2 (arredondado para baixo).
- **Dano Básico** (Golpe de Ponta / GDP e Balanço / Bal), por ST — tabela completa em
  `07-equipamento-e-carga.md`; resumo:

  | ST | GDP | Bal | ST | GDP | Bal | ST | GDP | Bal |
  |---|---|---|---|---|---|---|---|---|
  | ≤4 | 0 | 0 | 10 | 1D-2 | 1D | 16 | 1D+1 | 2D+2 |
  | 5 | 1D-5 | 1D-5 | 11 | 1D-1 | 1D+1 | 17 | 1D+2 | 3D-1 |
  | 6 | 1D-4 | 1D-4 | 12 | 1D-1 | 1D+2 | 18 | 1D+2 | 3D |
  | 7 | 1D-3 | 1D-3 | 13 | 1D | 2D-1 | 19 | 2D-1 | 3D+1 |
  | 8 | 1D-3 | 1D-2 | 14 | 1D | 2D | 20 | 2D-1 | 3D+2 |
  | 9 | 1D-2 | 1D-1 | 15 | 1D+1 | 2D+1 | | | |

- **Carga** (kg até os quais cada nível se aplica) = ST × {1, 2, 3, 6, 10} para
  {Nenhuma, Leve, Média, Pesada, Muito Pesada}. Penalidade de Deslocamento: 0, -1, -2, -3, -4
  pontos respectivamente.
- **Defesa Passiva / Resistência a Dano**: sempre montada peça por peça pela tabela de
  `21-quadros-e-tabelas.md` (ver seção "Armadura peça por peça" acima) — nunca pela tabela de
  armadura completa do Sistema Básico. `defesa_passiva.armadura` na ficha = DP da peça de
  tronco; DP/RD de cada região ficam detalhados em `armas_objetos`.

### Custo de perícias

**Perícias Físicas** (base DX, ou ST/HT quando indicado):

| Nível final | Fácil | Médio | Difícil |
|---|---|---|---|
| Atributo-3 | — | — | ½ |
| Atributo-2 | — | ½ | 1 |
| Atributo-1 | ½ | 1 | 2 |
| Atributo | 1 | 2 | 4 |
| Atributo+1 | 2 | 4 | 8 |
| Atributo+2 | 4 | 8 | 16 |
| Atributo+3 | 8 | 16 | 24 |
| +1 nível além disso | +8 | +8 | +8 |

**Perícias Mentais** (base IQ, exceto Sex-Appeal que é HT):

| Nível final | Fácil | Médio | Difícil | Muito Difícil |
|---|---|---|---|---|
| IQ-3 | — | — | ½ | 1 |
| IQ-2 | — | ½ | 1 | 2 |
| IQ-1 | ½ | 1 | 2 | 4 |
| IQ | 1 | 2 | 4 | 8 |
| IQ+1 | 2 | 4 | 6 | 12 |
| IQ+2 | 4 | 6 | 8 | 16 |
| IQ+3 | 6 | 8 | 10 | 20 |
| +1 nível além disso | +2 | +2 | +2 | +4 |

Nível pré-definido (perícia não comprada): Fácil = Atributo-4, Médio = Atributo-5, Difícil =
Atributo-6 (salvo exceção listada em `06-pericias.md`; Muito Difícil geralmente não tem
pré-definido).

Para o campo "Tipo" da perícia na ficha, use a notação `{Atributo}/{Dificuldade}` abreviada,
ex.: `DX/F`, `IQ/M`, `DX/D`, `IQ/MD`.

## Esquema do JSON (`personagem.json`)

```json
{
  "nome": "string",
  "jogador": "string (ex.: 'IA (GURPS)')",
  "arquetipo": "string ou null (ex.: 'Cavaleiro (Fantasy)', 'Mago de Combate (Magia)')",
  "foto": "string ou ausente (nome do arquivo de retrato na pasta do personagem)",
  "raca": "string ou null (ex.: 'Anão (Fantasy)')",
  "idade": 30,
  "aparencia": "string curta (comece pela idade: '30 anos, magro, ...')",
  "historia": "string curta (cabe em 1 linha na ficha; o detalhe completo vai no .md)",
  "data_criacao": "DD/MM/AAAA",
  "sequencia": "string (normalmente '1')",
  "pontos_gastar": 100,
  "pontos_total": 100,
  "atributos": {
    "ST": {"valor": 10, "custo": 0},
    "DX": {"valor": 10, "custo": 0},
    "IQ": {"valor": 10, "custo": 0},
    "HT": {"valor": 10, "custo": 0}
  },
  "fadiga": 10,
  "pontos_vida": 10,
  "dano_basico": {"gdp": "1D-2", "bal": "1D"},
  "velocidade_basica": 5.0,
  "deslocamento": 5,
  "carga": {"nenhuma": 10, "leve": 20, "media": 30, "pesada": 60, "muito_pesada": 100},
  "defesa_passiva": {"armadura": 0, "escudo": 0, "total": 0},
  "defesas_ativas": {"esquiva": 5, "aparar": 0, "bloqueio": 0},
  "reacao": "0",
  "vantagens_desvantagens": [
    {"nome": "string", "custo": 10}
  ],
  "peculiaridades": ["string", "..."],
  "armas_objetos": [
    {"item": "string (arma)", "dano": "string", "tipo": "corte/perf/cont", "qtd": 1, "peso": 0.5, "categoria": "Armas"},
    {"item": "Aljava + 10 virotes", "dano": "-", "tipo": "-", "qtd": 1, "peso": 0.55, "categoria": "Munição"},
    {"item": "Capacete de couro (cabeça)", "dano": "-", "tipo": "DP2/RD2", "qtd": 1, "peso": 0.0, "categoria": "Armadura"},
    {"item": "Loriga de couro (tronco)", "dano": "-", "tipo": "DP2/RD2", "qtd": 1, "peso": 4.5, "categoria": "Armadura"},
    {"item": "Laudel (braços)", "dano": "-", "tipo": "DP1/RD1", "qtd": 1, "peso": 1.0, "categoria": "Armadura"},
    {"item": "Cesto/manopla (mãos)", "dano": "-", "tipo": "DP2/RD2", "qtd": 1, "peso": 0.0, "categoria": "Armadura"},
    {"item": "Laudel (pernas)", "dano": "-", "tipo": "DP1/RD1", "qtd": 1, "peso": 1.0, "categoria": "Armadura"},
    {"item": "Coturnos (pés)", "dano": "-", "tipo": "DP2/RD2", "qtd": 1, "peso": 1.5, "categoria": "Armadura"},
    {"item": "Rações (5 dias)", "dano": "-", "tipo": "-", "qtd": 1, "peso": 1.25, "categoria": "Equipamento"}
  ],
  "peso_total": 0.0,
  "custo_total": 1000,
  "pericias": [
    {"nome": "string", "nh": 12, "tipo": "DX/F", "custo": 1, "categoria": "Combate"},
    {"nome": "Ânglico (nativa)", "nh": 10, "tipo": "IQ/M", "custo": 0, "categoria": "Línguas"},
    {"nome": "Latim", "nh": 9, "tipo": "IQ/M", "custo": 1, "categoria": "Línguas"}
  ],
  "magias": [
    {"nome": "Criar Fogo", "classe": "A", "nh": 14, "tempo": "1 seg", "duracao": "1 min",
     "custo_fazer": "2/hex", "custo_manter": "1/hex", "obs": "Pré-req.: Atear Fogo",
     "pag": "M", "custo": 1, "categoria": "Fogo"}
  ],
  "resumo": {
    "atributos": 0, "vantagens": 0, "desvantagens": 0,
    "peculiaridades": 0, "pericias": 0, "total": 0
  }
}
```

Campos que controlam o agrupamento visual na ficha:

- **`vantagens_desvantagens`**: o script separa automaticamente pelo sinal do custo —
  primeiro as **Vantagens** (custo ≥ 0), depois **uma linha em branco**, depois as
  **Desvantagens** (custo < 0). Basta listá-las na ordem que preferir. As
  **Peculiaridades** já ficam num quadro próprio do formulário, logo abaixo.
- **`pericias[].categoria`**: agrupa as perícias na coluna da direita — sempre que a
  categoria muda de uma linha para a outra, o script pula **uma linha em branco**. Ordene a
  lista por categoria e use rótulos curtos e consistentes (ex.: `Combate`, `Físicas`,
  `Externas/Profissionais`, `Sociais`, `Ladinas`, `Mágicas`, `Médicas`). Se o campo for
  omitido em todas, nenhuma separação é feita.
- **`armas_objetos[].categoria`**: agrupa o equipamento do mesmo jeito — uma **linha em
  branco** a cada troca de categoria. Ordene a lista por categoria e use rótulos curtos e
  consistentes; o padrão recomendado é `Armas` → `Munição` → `Armadura` → `Equipamento`.
  Se o campo for omitido em todos os itens, nenhuma separação é feita.
- **`custo_total`**: soma em $ do equipamento, escrita na linha "TOTAIS:" ao lado do peso
  total em kg (como no modelo impresso: `TOTAIS: $ 1000    10,5 kg`).
- **`idade`**: não é desenhada na ficha (o formulário não tem esse campo), mas é o que valida
  o teto de perícias — `pericias + magias ≤ 2 × idade`. Repita a idade no início de
  `aparencia` para ela aparecer na imagem.
- **`magias`**: **omita o array inteiro** se o personagem não conjura. Existindo, ele
  alimenta o grimório (agrupado por `categoria`, o colégio da mágica) e faz o script
  acrescentar a linha `Mágicas (ver grimório)` ao fim das perícias da ficha, com a
  quantidade e a soma dos `custo`. Esses pontos precisam estar somados em `resumo.pericias`.

Limites físicos do formulário (não exceder, ou o excesso simplesmente não aparecerá na
imagem — mas pode continuar no `.md`): 15 linhas de Vantagens/Desvantagens **contando as
linhas em branco de separação**, 5 de Peculiaridades, ~24 de Armas e Objetos Pessoais,
~44 de Perícias (idem, contando os separadores). Como a armadura agora ocupa
uma linha por peça (até 6: cabeça, tronco, braços, mãos, pernas, pés), um personagem bem
equipado com várias armas pode somar 8-10 linhas só de equipamento — ainda bem dentro do
limite, mas vale considerar ao decidir quantas armas extras incluir. No grimório o limite é
de 45 mágicas por página, mas ali o excesso não se perde: gera uma página nova.

## O script `preencher_ficha.py`

Localizado em `scripts/preencher_ficha.py` desta skill. Requer Python 3 com Pillow (já
disponível no ambiente). Uso:

```
python .claude/skills/criar-personagem-gurps/scripts/preencher_ficha.py --data <json> --template <ficha-em-branco.jpg> --output <saida.jpg>
```

O preenchimento imita escrita à mão: a fonte padrão é **Segoe Script** (com fallback para
Segoe Print → Ink Free → Comic Sans → Arial), em corpo generoso, como numa ficha preenchida
a caneta.

As coordenadas de cada campo já estão calibradas contra `ficha-de-personagem.jpg` (2481×3508
px, a mesma imagem de referência do repositório) por análise de pixel direta sobre o
formulário em branco — não precisam ser recalibradas. Cada campo é definido como
`(x, baseline_y, corpo[, alinhamento[, largura_máxima]])`, onde **`baseline_y` é a própria
linha impressa do formulário** (o texto "senta" nela e cresce para cima). Por isso mudar a
fonte ou o corpo não desalinha nada. Constantes ajustáveis: `HEADER`, `ATTR_BOXES`,
`DERIVED`, `CARGA_LINES`, `DEFESA_PASSIVA`, `DEFESAS_ATIVAS`, `REACAO`, `VANTAGENS`,
`PECULIARIDADES`, `ARMAS`, `TOTAIS_KG`, `PERICIAS`, `RESUMO`.

Textos que não cabem na coluna encolhem automaticamente até `MIN_SIZE` (20 px) e, se ainda
assim não couberem, são truncados com reticências. Números decimais são escritos com vírgula
(2.5 → "2,5").

### Escreva rótulos curtos para a ficha

Como o formulário impresso tem colunas estreitas, mantenha **curtos os textos que vão para a
imagem** (o texto longo/explicativo fica no `personagem.md`, que não tem essa limitação):

| Campo | Limite prático | Exemplo bom | Exemplo que será truncado |
|---|---|---|---|
| `vantagens_desvantagens[].nome` | ~32 caracteres | `Hábito Detestável (risada)` | `Hábito Detestável (ri descontroladamente, até em combate)` |
| `peculiaridades[]` | ~32 caracteres | `Sorri sempre, até em perigo` | `Sempre sorri, até em momentos sérios ou perigosos` |
| `armas_objetos[].item` | ~24 caracteres | `Coura (tronco)`, `Elmo (cabeça)` | `Armadura de couro leve (Coura)` |
| `pericias[].nome` | ~26 caracteres | `Espadas de Lâmina Larga` | nomes com especialização muito longa |
| `aparencia` / `historia` | ~95 caracteres | uma linha de descrição | parágrafos inteiros |
| `magias[].obs` | ~30 caracteres | `Pré-req.: Atear Fogo` | a descrição inteira da mágica |

Para as peças de armadura, o padrão recomendado é `Nome curto (região)` — ex.: `Coura
(tronco)`, `Laudel (braços)`, `Coturnos (pés)` — com o DP/RD indo na coluna `tipo`.

## O script `preencher_grimorio.py`

Localizado em `scripts/preencher_grimorio.py`, ao lado do outro. Lê o **mesmo**
`personagem.json` (só o campo `nome` e o array `magias`) e desenha sobre `grimorio.jpg`:

```
python .claude/skills/criar-personagem-gurps/scripts/preencher_grimorio.py --data <json> --template grimorio.jpg --output <saida.jpg>
```

Mesma fonte manuscrita, mesmo encolhimento automático e mesma ancoragem por baseline do
`preencher_ficha.py` (do qual ele importa `draw_field`). As coordenadas foram calibradas por
análise de pixel sobre `grimorio.jpg` (2481×3508 px): 46 regras horizontais de y=325 a
y=3306 com passo de ~66,25 px e divisores verticais em x = 676, 842, 1061, 1280, 1499, 1737,
2217. Constantes ajustáveis: `TITULAR`, `LINHAS`, `COLUNAS`.

Comportamento: sem `magias` no JSON, apenas avisa e não escreve arquivo; com mais de 45
mágicas, pagina sozinho (`grimorio.jpg`, `grimorio-2.jpg`…), sem começar página com linha
em branco de separação.

## Estilo do `grimorio.md`

Só para conjuradores. Título (`# Grimório de <Nome>`), uma linha dizendo de onde vem a
Aptidão Mágica e qual o nível, e a tabela de mágicas com **as mesmas colunas do formulário**
(Mágica, Classe, NH, Tempo, Duração, Custo p/fazer, Custo p/manter, Custo em pontos,
Obs.), agrupada por colégio com um subtítulo por escola. Feche com o total de pontos gastos
em mágicas e, quando fizer sentido, um parágrafo curto de notas táticas — o que ele conjura
na abertura de um combate, o que exige preparação, quanto de Fadiga o repertório consome.

## Estilo do `personagem.md`

Estruture como uma ficha de personagem legível, nesta ordem: título com nome, uma linha de
resumo (raça/arquétipo/conceito/pontos, citando o livro de origem do arquétipo), Aparência, História (agora pode ser mais longa que na
imagem), tabela de Atributos com custo, Estatísticas Derivadas, tabela de Vantagens e
Desvantagens com custo, lista de Peculiaridades, tabela de Perícias (NH, Tipo, Custo),
tabela de Equipamento (Item, Dano, Tipo, Qtd, Peso, peso total), e por fim o quadro Resumo
de Pontos idêntico ao da ficha. Escreva em português, tom de ficha de RPG (direto, sem
floreios).
