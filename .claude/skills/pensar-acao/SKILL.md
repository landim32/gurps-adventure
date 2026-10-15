---
name: pensar-acao
description: >
  Lê a cena atual (o roll6 primeiro, o repositório como apoio) e sugere 3 ações que um
  personagem pode declarar nela — por padrão o Gorbag, o Moedor, do André —, cada uma
  amarrada a uma desvantagem, peculiaridade, vantagem ou perícia da ficha, com a fala em
  personagem, o teste que o Mestre provavelmente pede e o risco. Só sugere: não rola dado,
  não declara nada no roll6, não escreve em lugar nenhum e não lê o que é segredo do Mestre.
  Use when the user asks "/pensar-acao", "o que o Gorbag pode fazer", "sugira ações",
  "me dá ideias para a cena", "o que meu personagem faria agora".
---

# Pensar ação

Quem usa esta skill é **um jogador** decidindo o que declarar. O que ela entrega são
**três ideias que o personagem faria**, e não a jogada certa para a mesa. Interpretar as
desvantagens é o que dá ao personagem os pontos que ele recebeu por elas. Por isso pelo
menos duas das três sugestões têm de **custar alguma coisa** ao personagem.

## De quem

- Sem argumento: **Gorbag, o Moedor** (André).
- Com argumento (`/pensar-acao Krag`, `/pensar-acao Bruno`): o personagem que a folha
  `contexto` resolver. Ela aceita nome de jogador ou de personagem, inteiro ou em parte.

## 1. A ficha

```
python .claude/skills/contexto/scripts/contexto.py contexto --quem "<nome>"
```

Isso dá atributos, defesas, Deslocamento e as perícias com NH. Depois leia:

- o bloco do personagem em `campanha/CONTEXTO.md`: aparência, reação fixa, vantagens,
  **desvantagens com o teste de cada uma**, peculiaridades, línguas e mágicas;
- `personagens/<slug>/personagem.md` só quando precisar de equipamento ou de uma nota de
  arbitragem que o CONTEXTO não traz.

## 2. A cena

**O roll6 é onde a mesa joga.** Ache a campanha ativa com `list_my_table_campaigns`. Se
`campanha/roll6.json` existir, ele diz qual é. Depois:

| Chamada MCP | Para quê |
|---|---|
| `get_turn_history` (`limit` 3–5) | As últimas narrações do Mestre: onde estão, quem está ali, o que acabou de acontecer |
| `get_turn_summary` (sem `turnNo`) | O turno em curso: quem já declarou o quê, e **as posições** de PJs e NPCs no mapa |
| `list_chat_messages` (`kind` `text,poll`, `limit` 30) | O que a mesa combinou fora da narração: respostas do Mestre, decisões em grupo, enquetes abertas |

O resultado do chat pode ser grande. Se vier salvo em arquivo, filtre com `jq`.

No repositório, leia `campanha/mundo.md`, `saude.md` e `bolsa.md` quando existirem, para
saber como o personagem **está**: ferido, sem dinheiro, devendo a alguém.

### O que esta skill NÃO lê

Ela pensa como o jogador, então lê só o que o personagem pode saber:

- **nada de `campanha/plano/`** (o plano secreto do Mestre);
- **nada de `reacoes.json` nem `segredos.json`**: reação de NPC é segredo, e o jogador
  descobre pelo jeito que o NPC trata ele;
- nada de `create_campaign_plan`/`get_campaign_plan` no roll6.

Se uma sugestão depender de algo que o personagem não tem como saber, ela não serve.

## 3. As três sugestões

Monte as três com estas regras:

1. **Cada uma é amarrada a um traço da ficha**, dito pelo nome: desvantagem,
   peculiaridade, vantagem ou perícia com NH.
2. **Pelo menos duas puxam desvantagem ou peculiaridade.** Uma só pode ser "a jogada
   esperta".
3. **As três são diferentes entre si**: uma social ou de interpretação, uma que avança o
   objetivo do grupo, e uma de risco ou de humor. Nunca três variações de "ameaçar alguém".
4. **Usam o que está na cena**: um NPC do salão, um objeto, o fogo da lareira, a conversa
   pendente. Nada genérico que serviria em qualquer taberna.
5. **Respeitam o momento**: em combate, a sugestão é uma manobra que cabe no turno,
   dentro do Deslocamento e do alcance. Fora de combate, pode ser uma conversa inteira.
6. **Não contrariam o que a mesa já decidiu**: líder eleito, plano combinado, ordem do Mestre.

Para cada uma, entregue:

- **Título curto** e o **traço** que a move;
- **a declaração pronta para colar no roll6**, em personagem e na voz dele (o Gorbag fala
  de si na terceira pessoa);
- **o teste provável**, com o NH da ficha (`Intimidação 11`, `Vontade 9 contra a Gula`).
  O Mestre é quem decide; isto é só para o jogador não ser pego de surpresa;
- **o risco**, numa linha: o que dá errado se falhar, ou o que a desvantagem cobra.

Feche com **uma linha de recomendação**: qual das três você declararia agora e por quê.

## Formato da resposta

```
*Cena:* Gota Seca, Ferrier, noite. Krag está no balcão com o Marden; o forasteiro de
capuz olha para vocês.

*1. Afiar o cutelo no balcão* — Afia o cutelo enquanto falam · Intimidação 11
> "Gorbag escuta. Marden fala. Gorbag não pergunta duas vezes."
Teste provável: Intimidação 11 (o Mestre pode dar bônus pelo tamanho)
Risco: falhou, o taberneiro se assusta e se fecha, ou chama a guarda.

*2. ...*

*3. ...*

*Eu iria de:* 1. Ajuda o Krag e mantém o Gorbag como líder sem gastar nada.
```

Nada de bloco para o WhatsApp: a sugestão é para o jogador, não para a mesa.

## O que nunca faz

- **Não rola dado.** Teste é da `teste-nh`, quando o Mestre pedir.
- **Não declara a ação no roll6** (`act_in_turn`, `send_chat_message`). Quem declara é o
  jogador, depois de escolher.
- **Não escreve em arquivo nenhum** e não chama a `registrar-acao`.
- **Não revela segredo do Mestre**, nem como palpite.
