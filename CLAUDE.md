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
  **Conjuradores ganham mais dois**: `grimorio.md` e `grimorio.jpg` — as mágicas ficam no
  array `magias[]` do JSON, e a lista de perícias da ficha recebe só uma linha de remissão
  ao grimório.
- Ao editar um personagem, **recalcule tudo do zero**: mudar um atributo altera Fadiga, Pontos
  de Vida, Dano Básico, Velocidade, Carga e o NH/custo de toda perícia baseada nele.
- Decisões de projeto já firmadas: **Sistema Avançado de Combate** (armadura montada peça por
  peça, com DP/RD discriminados por região), arquétipos dos livros seguidos como base
  obrigatória quando citados, e limite de -40 pontos em desvantagens.

### Gerar as imagens (ficha e grimório)

Os dois únicos comandos executáveis do repositório (Python 3 + Pillow; não há build, lint
nem testes):

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

Opcionais da ficha: `--foto <caminho>` para escolher o retrato explicitamente, `--sem-foto`
para omiti-lo. O do grimório lê o mesmo JSON e não faz nada se não houver `magias[]`; acima
de 45 mágicas, pagina sozinho (`grimorio-2.jpg`…).

Os scripts escrevem sobre `ficha-de-personagem.jpg` e `grimorio.jpg` (ambas 2481×3508 px)
imitando escrita à mão. As coordenadas foram calibradas por análise de pixel e **cada campo é
ancorado pela baseline da linha impressa** — por isso trocar fonte ou corpo não desalinha
nada. Se precisar reposicionar algo, ajuste as constantes no topo do script (`HEADER`,
`ATTR_BOXES`, `DERIVED`, `CARGA_LINES`, `DEFESA_PASSIVA`, `DEFESAS_ATIVAS`, `REACAO`,
`VANTAGENS`, `PECULIARIDADES`, `ARMAS`, `PERICIAS`, `RESUMO`, `FOTO_BOX`; no grimório,
`TITULAR`, `LINHAS`, `COLUNAS`) e confira o resultado gerando a ficha de um personagem real.

## Mestrando e escrevendo aventuras

A campanha ativa vive em `campanha/` e é conduzida pela skill `campanha` — o
plano em `campanha/plano/`, dividido em capítulos no padrão de
`livros/gurps-mb-3ed/23-caravana-para-ein-arris.md`, e o que de fato aconteceu na mesa em
`campanha/historico/`. Campanhas encerradas ficam em `historico/campanhas/`.

### A mesa acontece no WhatsApp: `campanha/whatsapp/`

O jogo é jogado no grupo de WhatsApp, de forma assíncrona, e o dono do projeto exporta a
conversa de tempos em tempos para `campanha/whatsapp/`. **Essa exportação é a fonte da
verdade sobre o que aconteceu na mesa** — acima do que já estiver escrito no histórico da
campanha, que é sempre uma reconstrução.

Arquivo novo chega solto na pasta, no padrão `AAAA-MM-DD.txt`; depois de incorporado ao
histórico, vai para `campanha/whatsapp/processados/` e ganha uma linha na tabela do
`campanha/whatsapp/README.md`, que explica o fluxo por inteiro. **As exportações são
cumulativas** — cada uma traz a conversa inteira desde o início do grupo, então compare com
a última processada e trabalhe do ponto em que divergem.

**A regra de precedência: o WhatsApp manda, salvo erro de cenário ou de regra.** Decisão de
jogador, jogada, resultado e fala vêm da exportação, mesmo contradizendo o repositório — se
os dois discordam sobre o que a mesa fez, o repositório está errado e se corrige. A exceção
são enganos do próprio Mestre contra os livros ou contra Yrth: esses se corrigem no sentido
inverso, e a correção fica registrada como **errata** numa anotação, para que o texto
arquivado não siga ensinando o erro. Qualquer divergência que não seja claramente uma
dessas duas coisas: **pergunte ao usuário antes de mexer em arquivo.**

Ao processar uma exportação, **leia o arquivo inteiro antes de escrever qualquer coisa** —
uma correção do Mestre solta no meio da madrugada desmente blocos publicados na véspera — e
**junte todas as divergências para perguntar de uma vez só**, em vez de interromper a cada
achado. As mensagens `<Mídia oculta>` são imagens que não vieram na exportação; o que elas
mostravam costuma estar descrito no texto em volta.

**A ficha do personagem não se mexe sozinha.** `personagem.json`, `personagem.md` e
`ficha.jpg` só mudam quando o usuário **pedir explicitamente** ("lance na ficha",
"atualize o inventário do Jah", "ele subiu Furtividade"). O que a mesa produz — dinheiro
ganho ou gasto, item pegado, PV perdido, ferimento, mágica lançada — fica no registro da
campanha: **dinheiro em `campanha/bolsa.md`** (`campanha.py bolsa --pj "Nome" --valor
+50 --motivo "..."`), **pontos de vida, Fadiga e ferimento que fica em
`campanha/saude.md`** (`campanha.py saude --pj "Nome" --pv -3 --motivo "..."`, e
`--estado "Braço direito incapacitado (Maneta)"` para o que não passa com a cena), o
resto nas anotações. A ficha guarda o que o personagem **é**; a
campanha guarda como ele **está** e o que ele **tem agora**.

**Todo personagem de jogador abre a bolsa com o que sobrou da criação:** os recursos
iniciais do nível de Riqueza dele — em cenário de fantasia, **$1.000** para Riqueza Média,
o dobro para Confortável, metade para Batalhador, um quinto para Pobre
(`livros/gurps-mb-3ed/02-criacao-de-personagem.md`, "Quantidade Inicial de Recursos") —
**menos o custo do equipamento que está na ficha**. É um lançamento só, com `--inicial`,
feito quando o personagem entra na campanha. Sem ele os saldos mentem: ninguém chega à
primeira taberna sem um vintém no bolso.

**Como o grupo está agora** — dinheiro, PV, Fadiga, ferimentos — sai pela skill
`status-atual`, num bloco pronto para o WhatsApp.

**Declaração de jogador entra pela skill `acao`** — "Ricardo: vou tentar furtar o Giles".
Ela lê a ficha de quem age e o estado da cena, decide o que a ação exige, chama quem
resolve (`teste-nh`, `disputa-nh`, `atacar`, `atacar-distancia`, `reacao`, `roll`),
narra o desfecho e
registra as três camadas: o acontecimento, a anotação do que ficou diferente e a ficha,
quando a ficha mudou.

**O que a mesa muda no mundo fica gravado.** Fato acontecido vira uma linha no log
(`campanha.py acontecimento`); **consequência que sobrevive à cena vira anotação**
(`campanha.py anotar --npc/--pj/--coisa ... --texto "..."`), que cai no `npcs.md`,
`grupo.md` ou `lugares.md` da pasta de jogo do capítulo e regera `campanha/mundo.md`.
Ferimento que fica, morte, item que trocou de dono, dinheiro, dívida, promessa, segredo
revelado, relação que mudou: anote na hora, com a consequência mecânica junto. **Antes de
voltar a uma cena ou interpretar um NPC, leia `campanha/mundo.md`** — o que está anotado
ganha do plano quando os dois discordarem.

**Dado se rola pela skill `roll`**, nunca de cabeça:
`python .claude/skills/roll/scripts/roll.py 1d+1` (aceita `3d`, `2D-1`, `2Dx10`). Relate o
que o script imprimiu — não invente resultado, não role de novo porque saiu ruim. Skill
nova que precise de dado importa o `d6()` de lá em vez de chamar `random`.

As **regras de combate autônomo** vieram das duas aventuras originais do dono do projeto
(hoje só em `backup/`, fora do versionamento; a primeira delas virou a campanha
*Tormento Vil*) e valem como padrão ao mestrar:

- teste de reação entre cada jogador e cada NPC — é a skill `reacao`, que rola todos os
  pares de uma vez e guarda o resultado em `campanha/NN-.../reacoes.json`; **leia esse
  arquivo antes de interpretar qualquer NPC**, e nunca role de novo um par que já tem
  resultado;
- NPCs atacam primeiro com armas de longo alcance e só partem para o combate de perto quando a
  munição acaba;
- alvo prioritário: o personagem mais próximo; depois o de pior reação; depois, entre os que já
  acertaram alguém, o que causou mais dano;
- pontos de impacto decididos nos dados.

### O bloco do WhatsApp sai uma vez por rodada, não a cada jogada

**Durante um combate, não exiba o texto no formato do WhatsApp a cada golpe.** Uma luta tem
muitas rolagens e a mesa não lê quinze blocos seguidos — ela lê um, no fim, com a rodada
inteira.

Enquanto a rodada corre, entregue só **o resultado mecânico em texto corrido**: quem acertou
quem, onde, o que a defesa fez, quanto doeu, quem ficou atordoado, quem perdeu a defesa ativa
até o próximo turno. É informação para o Mestre arbitrar o golpe seguinte, não texto para
colar no grupo.

**O bloco formatado sai em dois momentos, e só neles:**

- quando **todos já jogaram** — personagens *e* NPCs —, e a rodada se fechou;
- quando o **Mestre disser** que acabou (a cena, a rodada, o combate).

Aí sim: **um bloco só**, com a rodada inteira na ordem em que aconteceu, e o fecho da cena
junto. As skills `atacar`, `atacar-distancia`, `teste-nh`, `disputa-nh` e `reacao` imprimem
um bloco cada uma — **guarde-os e junte no fim**, em vez de repassar um por vez.

Fora de combate a regra não vale: uma ação declarada isolada, um teste solto, uma reação —
esses saem no bloco na hora, porque a mesa está esperando aquele resultado.

Estruture aventuras novas no mesmo formato: uma seção de regras/perícias úteis seguida da
aventura em cenas encadeadas, com os testes e as consequências de falha explícitos (incluindo
falha crítica) para que a cena possa ser arbitrada sem improviso.

Para tabelas de encontros, criaturas, empregos, preços e níveis sociais, puxe de
`livros/gurps-mb-3ed/21-quadros-e-tabelas.md`, `15-animais.md`, `19-cenarios.md` e
`livros/gurps-fantasy-3ed/09-criaturas.md`.

## A HQ da campanha: o agente `comic-artist`

O que a mesa jogou vira história em quadrinhos pelo agente **`comic-artist`**
(`.claude/agents/comic-artist.md`), em volumes de **20 a 24 páginas**, guardados em
`campanha/hq/vol-NN-<slug>/`. Ele conduz o fluxo inteiro e **para para aprovação** em
cada etapa: recorte e sinopse (`00-recorte.md`), lista de cenas (`01-cenas.md`), roteiro
por página e quadro (`roteiro.md` + `roteiro.json`), fixação do modelo visual do elenco,
esboços. Só depois é que se gasta imagem.

Três skills fazem o trabalho, e a divisão entre elas é a ideia toda:

| Skill | Faz | Com quê |
|---|---|---|
| `quadro-hq` | a arte de cada quadro, **sem balão**, e o avatar/folha de modelo do elenco | IA externa (OpenAI `gpt-image-1`, chave em `OPENAI_API_KEY`) |
| `baloes-hq` | os balões — fala, grito, sussurro, pensamento, recordatório, off, voz sobrenatural, canto, onomatopeia | Pillow, sem IA nenhuma |
| `pagina-hq` | o esboço em figuras geométricas, a montagem da página A4/300 dpi e o PDF | Pillow, sem IA nenhuma |

**Letreiramento nunca sai de gerador de imagem** — toda IA escreve garatuja e erra
acento. E o balão é aplicado *na página montada*, não no quadro solto: assim a letra sai
do mesmo tamanho em todos os quadros e a arte em `quadros/` fica limpa para ser regerada
sem perder o texto.

**Avatares de NPC moram em `campanha/npcs/<slug>/`** (`npc.md`, `avatar.png`,
`modelo-hq.png`) — não dentro da pasta da HQ, porque o NPC serve a campanha inteira. Os
PJs usam o retrato que já existe em `personagens/<slug>/foto.png` mais a folha
`modelo-hq.png`. É a folha de modelo que segura a semelhança de um quadro para o outro.

A HQ **não altera nada do jogo**: não mexe em ficha, não inventa acontecimento, não rola
dado. Ela ilustra o que já está registrado — e, onde o registro for omisso, pergunta.

## Versionamento

Repositório pessoal da mesa, trabalhado por uma pessoa só: **commite e faça push direto na
`main`**, sem criar branch nem PR. Separe em **commits temáticos** — skill mexida, sessão
jogada, tokens, correção de histórico — em vez de um commit único que junta tudo.

A `main` no GitHub tem uma regra de proteção exigindo pull request, e ela **está correta e
é intencional**: existe para que ninguém além do dono do repositório empurre para lá. O
push dele passa por cima da regra por ser administrador, e o servidor responde com
`Bypassed rule violations for refs/heads/main`. **Isso é o comportamento esperado, não um
problema** — não trate como falha, não sugira ajustar a proteção e não mencione o aviso ao
relatar que o push foi feito.
