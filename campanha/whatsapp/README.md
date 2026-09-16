# Exportações do grupo de WhatsApp

O jogo acontece no WhatsApp, de forma assíncrona. Este diretório guarda as exportações da
conversa do grupo — **a fonte da verdade sobre o que de fato aconteceu na mesa**.

## Como funciona

Arquivo novo chega solto aqui, com o nome no padrão `AAAA-MM-DD.txt` (a data da
exportação). Depois de processado, vai para `processados/` e ganha uma linha na tabela
abaixo.

```
campanha/whatsapp/
├── README.md              ← este índice
├── 2026-10-02.txt         ← chegou, ainda não processado
└── processados/
    └── 2026-09-16.txt     ← já incorporado ao histórico
```

**Uma exportação é cumulativa:** cada arquivo traz a conversa inteira desde o começo do
grupo, não só o trecho novo. Ao processar um arquivo novo, **compare com o último
processado** e trabalhe a partir do ponto em que os dois divergem — reler tudo do zero
gasta tempo e faz reescrever o que já está certo.

## Precedência

**O WhatsApp manda, salvo erro de cenário ou de regra.**

O que aconteceu na mesa — decisões dos jogadores, jogadas, resultados, quem disse o quê —
vem sempre da exportação, mesmo quando contradiz o que já estava escrito no repositório.
Se um jogador decidiu uma coisa no grupo e o repositório registra outra, **o repositório
está errado**.

A exceção são erros do próprio Mestre contra os livros ou contra o cenário de Yrth: esses
se corrigem, e a correção fica anotada como errata, para que o texto arquivado não continue
ensinando o erro. Divergência que não seja claramente uma dessas duas coisas, **pergunte ao
usuário antes de mexer** — não escolha sozinho qual versão vale.

## O que fazer com uma exportação nova

1. **Leia o arquivo inteiro** antes de escrever qualquer coisa. As contradições aparecem
   longe umas das outras: uma correção do Mestre às 6h da manhã pode desmentir um bloco
   inteiro publicado na véspera.
2. **Compare com o repositório** e junte *todas* as divergências antes de perguntar
   qualquer coisa — pergunte de uma vez, não a cada achado.
3. **Corrija o histórico**: `campanha/NN-.../README.md` (narrações e acontecimentos),
   `grupo.md`, `npcs.md`, `lugares.md`, e `saude.md` / `bolsa.md` pelo `campanha.py`.
4. **Ficha de personagem não se mexe** — vale a regra de sempre: só quando o usuário pedir.
5. **Mova o arquivo para `processados/`** e acrescente a linha na tabela.

Mensagens marcadas `<Mídia oculta>` são imagens que não vieram na exportação (mapas, fichas,
ilustrações). O que elas mostravam costuma estar descrito no texto em volta.

## Processadas

<!-- indice:whatsapp -->
| Arquivo | Período coberto | Processada em | O que trouxe |
|---|---|---|---|
| [`processados/2026-09-16.txt`](processados/2026-09-16.txt) | 07/09 16:49 → 16/09 07:34 | 16/09/2026 | Campanha inteira até aqui: capítulo 1 completo (a taberna, o braço-de-ferro, o furto da bolsa do Giles, a morte de Hoel Meia-Orelha, os quatro mortos que entraram pela porta, o incêndio) e o capítulo 2 até a rampa do castelo. **Duas correções grandes:** Donnwulf está vivo e ajudando o grupo, não é morto-vivo; e Wallace não tem porto — é cidade de pastores na orla do Grande Deserto. |
<!-- /indice:whatsapp -->
