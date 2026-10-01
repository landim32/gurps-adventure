---
name: processar-turno
description: >
  Processa um turno jogado no roll6 (a mesa virtual): lê pelo MCP get_turn_data o que cada
  personagem declarou, onde está e como está; se todos os personagens aprovados agiram,
  resolve o turno como a skill acao faz — cada declaração pelas regras de GURPS 3ª Edição,
  chamando roll, teste-nh, disputa-nh, atacar, atacar-distancia, iniciativa e reacao —,
  decide e resolve os NPCs, mostra o resultado ao Mestre e espera a aprovação dele (salvo
  aviso de que não precisa), registra tudo no repositório (log, anotações, saúde, bolsa)
  e fecha o turno com o MCP process_turn, com PV, Fadiga, status, posições e a
  narração. Use when the user asks "processe o turno", "processar turno", "feche o turno
  do roll6", "resolva o turno", "todo mundo jogou", ou /processar-turno.
---

# Processar o turno do roll6

O jogo acontece no **roll6**: cada jogador move a peça dele e declara a ação ali
(`act_in_turn`). Esta skill é o Mestre fechando a rodada. Ela lê a mesa inteira, resolve
tudo pelas regras, **mostra o resultado ao Mestre e espera a aprovação dele**, grava no
repositório e devolve o resultado ao roll6 numa chamada só, `process_turn`, que
**encerra o turno e abre o seguinte**.

É a skill `acao` aplicada à mesa inteira de uma vez. Tudo o que ela manda vale aqui:
regra conferida no livro, dado rolado pelas skills, falha crítica decidida antes,
registro em camadas e ficha intocada. **Leia a `acao/SKILL.md` antes da primeira
vez.** Leia também a skill `roll6`, que explica o mapeamento `campanha/roll6.json`, e
chame o `get_roll6_guide` uma vez por sessão.

## 1. Contexto: quem jogou e o que diverge

```bash
python .claude/skills/processar-turno/scripts/processar_turno.py contexto
```

Uma chamada ao `get_turn_data` e ao `get_turn_state`, cruzada com o repositório, mostra:

- **VEREDITO**: `PRONTO` (todo personagem aprovado declarou ação), `FALTAM AÇÕES de: ...`
  ou `SÓ LEITURA` (turno já encerrado, `--turno N`).
- **Cada personagem**: `characterId`, PV e Fadiga no roll6, hex local (`P7`) e xy,
  frente, status, **as ações declaradas**, os movimentos, a ficha local e as reações dos
  NPCs com ele.
- **Cada NPC no mapa**: `mapNpcId`, PV, hex, status, o nome dele no `saude.md`, as
  ações que o Mestre já lançou (ou o aviso `SEM AÇÃO NEM MOVIMENTO`) e **a reação mais
  recente dele com cada personagem**, de todos os capítulos. Essas reações são só locais
  e nunca vão ao roll6.
- **Divergências** entre roll6 e repositório: PV, Fadiga, e personagem do turno sem ficha
  em `personagens/`. Posição **não é mais comparada** — desde que a `atualizar-mapa` saiu,
  não há espelho local contra o qual divergir.
- **A lista de arquivos** a ler: `mundo.md`, o plano do capítulo, os `npcs.md`,
  `grupo.md`, `lugares.md`, o log do capítulo e o `reacoes.json`.

### Se faltar alguém

**Não processe.** Diga quem falta e pare. Mover a peça não é declarar ação: quem só se
moveu aparece à parte, e o Mestre decide se isso basta. Só siga com pendentes se o
Mestre mandar ("processe assim mesmo"). Nesse caso, quem não declarou faz a manobra
**Aguardar**, ou o que o Mestre disser, e isso vai dito na narração.

### Se houver divergência

Junte **todas** as divergências e pergunte **uma vez**, antes de rolar qualquer coisa.
É a mesma regra do WhatsApp no `CLAUDE.md`. A precedência:

- **O que os jogadores fizeram neste turno no roll6 manda**: movimento, declaração,
  frente. É a mesa, como a exportação do WhatsApp.
- **O estado que vem de antes do turno manda no repositório**: PV, Fadiga, estado,
  itens. Se o roll6 discorda sem uma mudança registrada no turno que explique, o roll6
  está errado.
- **A posição no roll6 é a posição.** Não existe mais a outra para conferir: cavalo, objeto
  e peça que só o roll6 conhece simplesmente estão onde o roll6 diz.

## 2. Ler antes de decidir qualquer número

Leia os arquivos da lista, **a ficha de cada personagem que age** (a ficha local; sem
ficha local, o `characterSheet` que vem no `get_participation`) e a ficha de cada NPC
envolvido. As fichas de NPC estão no `npcs.md` do plano e da mesa, ou no `get_npc`. Leia
também as **notas da participação** (`get_participation` → `sheet`): item perdido,
desvantagem adquirida. O que está anotado na pasta de jogo ganha do plano, e as erratas
do Mestre ganham de tudo.

## 3. Montar a rodada antes de rolar

Escreva para si o plano da rodada inteira:

1. **Ordem.** Vale a ordem que o capítulo já fixou. Sem ordem fixada, é Velocidade
   Básica, a maior primeiro. Em começo de luta, surpresa e primeira ação saem da skill
   `iniciativa`.
2. **Cada declaração vira regra**, pela régua da `acao`:

   | Declaração | Resolve com |
   |---|---|
   | nada de difícil | nada, só narra |
   | difícil contra o mundo | `teste-nh` |
   | alguém resiste ou percebe | `disputa-nh` |
   | golpe corpo a corpo | `atacar` |
   | tiro ou arremesso | `atacar-distancia` |
   | primeira impressão de NPC | `reacao` |
   | dado avulso | `roll` |

   Declaração condicional ("se possível, golpeio o Morto 4") é resolvida se a condição
   se cumpre: veja alcance, arma preparada e posição. Se não se cumpre, vira a manobra
   que faz sentido, e isso é dito.
3. **Os NPCs.** Ação ou movimento que o Mestre lançou no roll6 é o que vale. **NPC sem
   ação nem movimento** (o contexto marca `SEM AÇÃO NEM MOVIMENTO`): **você decide o que
   ele faz e o que ele fala**, pelo procedimento da seção "Decidir pelo NPC", logo abaixo.
4. **Fases da cena.** Cena com fase própria, como o teste de Cavalgar ou de Carreiro de
   uma perseguição, segue o precedente do capítulo, **salvo ordem do Mestre**.
5. **Estado herdado.** Status do turno anterior que cobra agora entra na conta:
   - teste de HT de quem está atordoado;
   - redutor de choque, que vale só neste turno;
   - arma despreparada que precisa de Preparar;
   - Precisão acumulada de quem apontou;
   - Ataque Total do turno passado, que deixa sem defesa.
6. **Falha crítica decidida antes**, para cada ação que rola.
7. **Aviso vem antes.** Se alguma declaração esbarra numa regra (alcance, manobra que não
   cabe, NH que o livro não deixa rolar) ou é ambígua, **junte todas e pergunte ao Mestre
   de uma vez** (`AskUserQuestion`), com o caminho que o livro oferece. Decidido, a
   conversa acabou: o Mestre manda sobre a regra, e a decisão vira **errata** no registro.

### Decidir pelo NPC

Um NPC sem ordem não fica parado: ele age como a criatura que é, com o que sabe, o que
sente pelos personagens e o que a cena lhe oferece. Decida **antes de rolar**, junto com
o resto do plano da rodada, e na ordem de turno dele. As declarações dos personagens que
agem antes já estão resolvidas quando a vez dele chega.

**Ele se defende sempre.** Atacado, usa a melhor defesa ativa que tem naquele momento:
- **Bloqueio**, se o escudo está no braço e ainda não foi usado na rodada;
- **Aparar**, se a arma está preparada e não é desbalanceada recém-usada;
- **Esquiva** nos outros casos;
- **Recuar** (+3) quando cabe e não o tira de algo que ele precisa guardar.

Defender não gasta o turno dele. Só não defende quem não pode: surpreendido, caído sem
defesa, em Ataque Total, inconsciente.

**Primeiro o que o estado impõe**, antes de qualquer escolha:
- **Arma despreparada:** Preparar.
- **Caído ou de bruços:** levantar, que são dois turnos de bruços a de pé, e em pé pode
  atacar no mesmo turno pela exceção do livro.
- **Atordoado:** teste de HT, e só isso.
- **Arma na bainha:** sacar.
- **Arqueiro:** sacar, encaixar, apontar e só então atirar, pelo procedimento fixado
  pelo Mestre.
- **Cavalo exausto:** não passa de Deslocamento 2.

Se o estado consome o turno, a decisão acabou.

**Depois, o alvo.** Entre os personagens ao alcance, ou alcançáveis com o movimento do
turno, nesta ordem:

1. **O indefeso ganha de tudo.** Caído, atordoado, sem defesa ativa (Ataque Total no
   turno anterior), desarmado, inconsciente, preso, de costas: se ele está ao alcance, é
   ele, **mesmo que a reação com ele seja melhor** que a com o vizinho armado.
2. **O mais próximo.** Conte em hexágonos, pelo mapa do roll6.
3. **Empate de distância: o de pior reação**, o `total` mais baixo no contexto.
4. **Ainda empatado: quem causou mais dano** a ele ou aos dele nesta luta. Depois disso,
   dado (`roll.py 1d`).
5. **Arma de longo alcance primeiro**, enquanto houver munição e o alvo estiver fora do
   corpo a corpo. Ninguém ao alcance: ele **se move** na direção do alvo escolhido pelas
   mesmas regras, gastando o Deslocamento dele, e ataca se chegar (Avançar e Atacar), ou
   só se aproxima.

**O golpe.** Manobra pelo temperamento: Ataque normal por padrão; **Ataque Total** para
criatura sem autopreservação contra alvo indefeso, ou quando a ficha e o plano pedem.
Ataque Total deixa o NPC sem defesa até o próximo turno, e isso vai no status dele.
O local do golpe sai nos dados.

**Quem não é hostil** (Lorde William, um guarda vivo, um aliado) não entra nessa régua.
Ele age pelo que o plano do capítulo e o `npcs.md` dizem dele, e a reação com cada
personagem dá o tom:
- **Boa ou melhor:** ajuda, avisa, cobre.
- **Neutra:** faz o que já fazia e responde seco.
- **Fraca ou pior:** recusa, cobra, atrapalha, sem sabotar o que o plano diz que ele
  não sabota.

Fugir, render-se ou mudar de lado segue a mesma lógica, à luz do que ele quer.

**O que ele fala**, se fala. Morto-vivo não fala, e animal não fala. Quem fala diz uma
frase curta, no tom da reação dele com quem ouve e com o que acabou de acontecer: o
grito de comando, o aviso, a provocação, a súplica. A fala entra na narração. Nunca diz
números nem o que só o Mestre sabe.

**Reação que ainda não existe:**
- **NPC com mente** (vivo, inteligente) e sem reação rolada com algum personagem de
  quem a decisão depende: role pela skill `reacao` **antes de decidir**. Ela grava no
  `reacoes.json` do capítulo. Nunca role de novo um par que já tem, e a anotação da
  pasta de jogo ganha do número (William e NelsOwned: Fraca).
- **Sem mente e hostil por natureza** (os mortos de Vurkash, um animal acuado): a
  reação é **Hostil com todos** e não se rola. O desempate do passo 3 pula direto para
  o passo 4.

**Diga ao Mestre, no resumo, o que cada NPC fez e por quê**, com a regra que decidiu:
"atacou o NelsOwned, caído, em vez do Negrum ao lado". Isso é para o Mestre, não para a
mesa.

### As reações são segredo

**As reações ficam só no repositório** (`campanha/*/reacoes.json` e as anotações). Os
personagens não podem saber o que um NPC sente por eles, e o roll6 é visto por todos.
Portanto:

- **Não vão** para `process_turn` (nem no `status`, nem na `narration`), nem para
  `act_in_turn`, `create_turn_entry`, notas da participação, ficha de NPC no roll6 ou
  bloco do WhatsApp.
- **A narração mostra o comportamento, nunca o motivo:** "o morto passa pelo Negrum e
  crava a espada no trovador caído", e não "ataca o NelsOwned porque ele está indefeso
  e tem reação pior".
- **Não escreva** faixa, total, "reação Fraca", "não gosta de você" nem nada que
  permita reconstruir o número.
- O `processar_turno.py contexto` mostra as reações no terminal, marcadas
  `[LOCAL, não vai ao roll6]`: são para você e para o Mestre.

## 4. Resolver

Uma ação por vez, na ordem, com os scripts das skills:

```bash
python .claude/skills/teste-nh/scripts/teste_nh.py ...
python .claude/skills/disputa-nh/scripts/disputa_nh.py ...
python .claude/skills/atacar/scripts/atacar.py ...
python .claude/skills/atacar-distancia/scripts/atacar_distancia.py ...
python .claude/skills/roll/scripts/roll.py 3d
```

- **Relate o que o script imprimiu.** Não role de cabeça nem de novo, e não role reação
  que já está no `reacoes.json`.
- **Confira o que o script não sabe.** Veja se ele pegou toda a RD e toda a DP da ficha;
  RD e DP naturais de raça, como a do Anão, costumam ficar de fora. Corrija à mão e diga.
- **O resultado de uma ação muda a seguinte.** Quem caiu não ataca, e o escudo que já
  bloqueou está usado nesta rodada.
- **Guarde os blocos de WhatsApp das skills.** A mesa recebe **um bloco só** no fim, e
  cada bloco guardado vira a **conta** da ação dele na narração (seção 7).
- **Passe o motivo de cada modificador** ao script — `--mod -2 --mod-motivo "escuro"`,
  `--alvo-defesa-mod -4 --alvo-defesa-mod-motivo "atordoado"`, `--motivo` no `teste-nh` —,
  senão a conta sai com "situação" e o jogador não entende de onde veio o número.

## 4a. Aprovação do Mestre antes de gravar e de fechar

**Nada vai ao roll6 sem o Mestre aprovar** — nem `process_turn`, nem
`update_participation`, `create_npc`, `place_npc_on_map` ou qualquer outra chamada que
escreva. E, para o repositório não ter de ser desfeito, o registro da seção 5 também
espera a aprovação. Resolvido o turno, pare e mostre ao Mestre, numa mensagem só:

1. **O texto de resultado**, exatamente como vai para a `narration` e para o WhatsApp
   (seção 7, item 1): cada ação em prosa com a conta logo abaixo.
2. **O resumo mecânico** (seção 7, item 2), com o que cada NPC fez e por quê — é aqui
   que as reações aparecem, marcadas como locais.
3. **O que vai mudar no roll6**: PV, Fadiga, `status` e posição de cada peça que muda
   (a lista que vai virar `characters[]` e `npcs[]` do `process_turn`), e as chamadas
   que vêm depois dele (notas da participação, NPC novo).

E termine perguntando se pode fechar o turno. Então:

- **Aprovou** ("pode mandar", "ok", "fecha"): siga para a seção 5 e depois a 6.
- **Mandou mudar** (outro NPC como alvo, um modificador que ele arbitra diferente, um
  trecho da narração): aplique, **re-role só o que a mudança invalidou** — o que não
  mudou fica com o dado que saiu — e mostre de novo o que mudou. Decisão sobre regra
  vira **errata** no registro. Se ele pedir para refazer uma jogada que a regra não
  invalidou, é decisão do Mestre: faça e registre.
- **Recusou ou mandou parar**: nada é gravado nem enviado. O turno fica aberto no roll6.

**Sem aprovação só quando o Mestre avisar** — "processe sem me mostrar", "pode fechar
direto", "sem aprovação". O aviso vale para o pedido em que foi dado (um turno, ou os
turnos que ele disser, como "feche os próximos três sem aprovação"); o turno seguinte
volta a pedir aprovação. Mesmo sem aprovação, **pare e pergunte** se aparecer algo que a
seção 3 já manda perguntar (divergência, declaração que esbarra em regra) — o aviso
dispensa a revisão do resultado, não as dúvidas de regra.

## 5. Registrar no repositório, sem empurrar ao roll6 ainda

Tudo vai para o roll6 de uma vez, no `process_turn`. Nada no repo empurra estado sozinho
desde que o `campanha.py saude` parou de sincronizar e o mapa local saiu de cena — por isso
não há mais o que desligar aqui; o bloco abaixo só escreve no repositório:

```bash
C=.claude/skills/campanha/scripts/campanha.py
python $C acontecimento --texto "TURNO N (roll6) — ..."   # uma linha por turno, completa
python $C saude --pj "Nome" --pv -3 --motivo "..."        # e --estado/--curar para o que fica
python $C saude --npc "Morto 5" --pv -7 --motivo "..."
python $C anotar --pj/--npc/--coisa "..." --tag ... --texto "..."   # o que sobrevive à cena
python $C bolsa --pj "Nome" --valor +50 --motivo "..."
```

- **O acontecimento** segue o padrão do log: o que cada um declarou, o NH e de onde saiu
  cada modificador, o que tirou, a defesa, o dano e o estado final. As erratas do Mestre
  levam a palavra **ERRATA**.
- **As posições da mesa vivem no roll6** — o mapa local não é mais desenhado por skill.
  Os movimentos dos jogadores e os que a resolução causou, como empurrão, queda ou fuga,
  entram no `process_turn` da seção 6; os índices `.json` de hexágonos que ainda existem
  em `cenarios/` ficaram como referência histórica de alinhamento, nada os gera mais.
- **A ficha não é tocada**, como na `acao`.

## 6. Fechar o turno: `process_turn`

Monte a chamada com **só o que mudou**:

```json
{
  "campaignId": 1,
  "characters": [
    {"characterId": 7, "currentLife": 3, "status": "Caído, atordoado: -4 nas defesas; machado despreparado"},
    {"characterId": 4, "clearStatus": true}
  ],
  "npcs": [
    {"mapNpcId": 11, "currentLife": -2, "status": "DESTRUÍDO — caído em Q44"},
    {"mapNpcId": 12, "x": 15, "y": 9, "look": 4}
  ],
  "narration": "…"
}
```

- **`currentLife` e `currentEnergy`** saem do `saude.md` já atualizado: PJ é o máximo
  mais o acumulado, NPC é o total mais o acumulado. Nunca passam do total.
- **`status`** é o estado tático que vale **até o fim do próximo turno**, em até 260
  caracteres:
  - arma preparada ou despreparada;
  - caído, de joelhos, atordoado (com o teste que falta);
  - redutor de choque do próximo turno;
  - apontando, com a Precisão acumulada;
  - sem defesa ativa por Ataque Total, Defesa Total;
  - montado ou a pé, cavalo exausto, desarmado.

  Tire o que já passou. `clearStatus: true` quando não sobrou nada.
- **`x`, `y` e `look`** só para quem a resolução moveu. O que o jogador já moveu no roll6
  está lá. Posição local para o roll6: `roll6.rotulo_para_xy("P7")` → `(15, 6)`. Frente:
  N 0, NE 1, SE 2, S 3, SW 4, NW 5.
- **`narration`**, até 10.000 caracteres: o bloco do WhatsApp da rodada, **com a conta
  de cada ação logo abaixo do parágrafo dela** — NH de partida, cada bônus e redutor com o
  motivo, dado e margem, defesa do alvo montada e rolada, dano com RD e multiplicador,
  testes de HT, sucesso decisivo e falha crítica. Fica no log do turno para todos, e é
  ali que o jogador confere o que o dado fez: **prosa sem a conta não vai ao roll6.** O
  formato está no `CLAUDE.md`, em *A narração mostra a conta de cada jogada*. Passando de
  10.000 caracteres, corte a prosa, nunca a conta.

**Chamar `process_turn` não tem volta.** Ele valida tudo e grava junto, ou recusa tudo.
Por isso ele só sai **depois da aprovação da seção 4a** (ou do aviso do Mestre de que
não precisa), e a aprovação vale para **uma** chamada, a deste turno. A chamada enviada é
a que o Mestre aprovou: se algo mudou depois da aprovação, mostre de novo. Se o usuário
pediu só para simular ou ver, mostre a chamada montada e **não** envie. Se voltar erro 400,
nada foi gravado e o turno não andou: corrija o item apontado (`characters[0].currentLife`,
`npcs[1].x`, ...) e envie de novo. **Qualquer outra falha** (conexão, resposta que não
chegou, erro ao imprimir): **não reenvie antes de conferir** com `get_turn_data`. Se o
`currentTurn` já andou, o turno foi fechado e reenviar fecharia o seguinte.

Envie pelo MCP (`process_turn`) ou, se a sessão ainda não carregou a ferramenta, pelo
cliente: `roll6.py chamar process_turn "$(cat turno.json)"`.

**Campanha do roll6 que não existe no repositório** (teste, one-shot:
`processar_turno.py contexto --campanha N`): **não registre com `campanha.py`**, que
gravaria na campanha ativa. Nesse caso o registro é só o
`process_turn`, e a ficha é a local, se houver (inclusive em `historico/personagens/`),
ou o `characterSheet` do `get_participation`.

Depois do `process_turn`, faça o que ele não faz:

- **Notas da participação**, se a rodada mudou item, desvantagem ou saldo:
  `get_participation` → `update_participation` com o `sheet` novo. Só a diferença para a
  ficha.
- **NPC que morreu** fica com vida ≤ 0 e status de destruído. **Não apague a peça** sem
  confirmação.
- **NPC novo em cena** (reforço, figurante que ganhou nome): `create_npc` →
  `add_npc_to_campaign` → `place_npc_on_map`, e o apelido em `campanha/roll6.json` se o
  nome local for outro.
- **Conferir**: `processar_turno.py contexto --turno N` do turno fechado não deve mostrar
  divergência nova entre roll6 e repositório.

## 7. Entregar

Os itens 1 e 2 são o que a seção 4a mostra ao Mestre para aprovar. Depois do
`process_turn`, repita o bloco do WhatsApp só se ele mudou desde a aprovação, e acrescente
o turno novo que o roll6 abriu e o item 3.

1. **Um bloco só para o WhatsApp**, com a rodada inteira na ordem em que aconteceu e o
   fecho da cena. Nada de bloco por golpe (`CLAUDE.md`). É o mesmo texto que foi na
   `narration`: cada ação é **um parágrafo de prosa seguido das linhas da conta**, com
   `> ` na frente, tiradas do bloco que o script imprimiu:

   ```
   *TURNO 4 — ARENA*

   Comam mete a cimitarra no braço da espada do goblin. O escudo sobe tarde. O corte
   leva o braço, o gládio cai na areia.
   > Ataque: Espadas de Lâmina Larga NH 13, -2 Braço = *11*
   > 3d [3, 4, 1] = *8* → sucesso por 3
   > Defesa de Goblin: bloqueio 5 +2 DP escudo = *7*
   > 3d [5, 4, 3] = *12* → falhou por 5
   > Dano: 2D: [4, 3] = *7*
   > RD 1 → 6 passam
   > Corte: +50% do que passar da armadura → *9*
   > Teto do local (HT/2 = 5): 4 desperdiçado(s)
   > *Braço INCAPACITADO* — Goblin fica atordoado
   > *Goblin perde 5 ponto(s) de vida.*
   ```

   NPC que agiu entra igual, com a conta dele. Ação sem dado (andar, preparar arma,
   aguardar) fica só na prosa. Reação e rolagem secreta nunca entram.
2. **O resumo mecânico para o Mestre**, em texto corrido:
   - o que cada personagem e cada NPC fez, com as rolagens;
   - as decisões que você tomou pelos NPCs;
   - o que foi corrigido à mão nos scripts;
   - o turno novo que o roll6 abriu (`turnNo` da resposta).
3. **O que foi gravado**: o acontecimento, as anotações, a saúde e as notas da
   participação.

## O que esta skill nunca faz

- **Processar com ação faltando** sem ordem do Mestre.
- **Enviar qualquer coisa ao roll6** (`process_turn` ou outra escrita) antes de o Mestre
  aprovar o resultado, salvo aviso dele de que não precisa de aprovação.
- **Rolar de cabeça** ou rolar de novo; inventar NH, RD ou DP.
- **Chamar `process_turn` duas vezes** para o mesmo turno, ou numa simulação.
- **Tocar na ficha** (`personagem.json`, `update_character`) sem pedido explícito.
- **Apagar** peça, ocorrência, entrada de turno ou NPC sem confirmação.
- **Contar ao jogador** o que o personagem não pode saber, seja na narração, seja no
  status.
- **Narrar jogada sem a conta**: parágrafo de golpe, tiro, mágica ou teste que não traga
  logo abaixo o NH, os modificadores com motivo, o dado e o resultado.
- **Levar reação ao roll6** ou ao WhatsApp, nem o motivo de uma escolha de NPC que a
  denuncie.
- **Deixar NPC parado** por falta de ordem: sem ação lançada, ele age pela seção "Decidir
  pelo NPC".
