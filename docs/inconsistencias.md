# Revisão das skills — inconsistências

_Revisão de 03/10/2026 sobre a série de commits de 01/10 (de `156fb34` "contexto e
registrar-acao" até `8663e72`) e a alteração ainda não commitada em `narrar/SKILL.md`.
O mapa das skills está em [`skills.md`](skills.md)._

Cada item diz **o que está escrito**, **o que de fato acontece** e **onde**. Os marcados
como _verificado_ foram reproduzidos rodando o script. Nada foi corrigido: esta é a lista
para decidir o que mexer.

---

## Alta — comportamento errado ou segredo em risco

### 1. A reação vaza no "Bloco da mesa" da `registrar-acao` _(verificado)_

- **Escrito:** `registrar-acao/SKILL.md` — "Não leva reação para o roll6, nem para o bloco da
  mesa"; `CLAUDE.md` — reações nunca vão ao WhatsApp.
- **Acontece:** `reacao.py` (l. ~343) entrega um `resumo` com faixa e total —
  `"Testes de reação…: Guarda→Jah Kagadu Ruim (6)"`. A `registrar_acao.py` imprime o
  `resumo` dentro do `### Bloco da mesa` (`bloco_mesa()`, l. 161). Um `--dry-run` com esse
  ato mostra a faixa e o total no bloco que se cola no grupo.
- **E vai para o log:** o mesmo resumo vira acontecimento no `README.md` do capítulo, o
  arquivo que também guarda a seção **Narração** lida aos jogadores. Já está lá nos
  capítulos 01, 03 e 04.
- **Caminho:** a `reacao` mandar `resumo` sem faixa e total ("Reações roladas em X: N pares"),
  ou a `registrar-acao` omitir o bloco quando o ato traz `reacoes`.

### 2. `campanha.py` não resolve nome parcial, e cria personagem fantasma _(verificado nesta sessão)_

- **Escrito:** `CLAUDE.md` — "a folha `contexto` é a única fonte de quem age… Resolução de
  nome (de jogador ou de personagem, parcial)… Skill nova… **não reimplementa**".
- **Acontece:** `campanha.py saude/bolsa/anotar` comparam `slug(nome) == slug(quem)`, exato.
  `contexto.achar_personagem("Jah")` devolve Jah Kagadu, mas `campanha.py saude --pj "Jah"`
  abriu uma seção nova "### Jah" com PV `1`. O mesmo com "Kaelric". Foi preciso apagar à mão.
- **Caminho:** `campanha.py` resolver `--pj` pelo `contexto` (é PJ, tem ficha) e recusar
  nome que não casa, em vez de criar entrada.

### 3. `registrar-acao` promete inibir escrita por peça dentro do turno, e não inibe

- **Escrito:** `registrar-acao/SKILL.md` §4 — "se vier `roll6.turno`, esta skill inibe as
  escritas por peça e entrega só o fechamento".
- **Acontece:** `plano_roll6()` acrescenta a linha do `process_turn` **e continua** listando
  `update_participation`/`update_map_npc` de cada peça.
- **E os nomes não batem com o MCP:** o plano escreve `update_map_npc(…, characterStatus=…)`,
  mas a ferramenta recebe `status` e exige `name`. O ato usa `campanhaCharacterId`; o MCP,
  `campaignCharacterId`.

### 4. Notas da participação: as skills mandam "só a diferença", o MCP pede "a ficha inteira"

- **Escrito:** `roll6/SKILL.md` (tabela, linha `campanha`) e `campanha/SKILL.md` §roll6 —
  `update_participation` "com o `sheet` novo — só o que difere da ficha, nunca cópia da ficha".
- **Contrato do MCP:** a descrição de `update_participation` diz que o `sheet` é a cópia da
  ficha nesta campanha: "write the character's full sheet as it stands here, **not only the
  differences**".
- **Risco:** seguir a skill troca a ficha da participação por um rodapé de diferenças.

### 5. O bloco da mesa da `registrar-acao` joga a conta para o fim

- **Escrito:** `CLAUDE.md` — "repasse as linhas… **depois do parágrafo narrado**"; `narrar`
  — "não jogue a conta para o fim do bloco".
- **Acontece:** `bloco_mesa()` monta narração → resumo → **todas** as `jogadas[].linha`
  no final. Com mais de uma jogada, a conta descola do parágrafo dela.

---

## Média — texto desatualizado que contradiz o `CLAUDE.md` ou o código

### 6. "O `campanha.py saude` sincroniza sozinho com o roll6"

- `roll6/SKILL.md`, seção "O que já é automático", diz que `saude --pj/--npc` empurra
  `update_participation`/`update_map_npc`, e ensina `ROLL6_DESLIGADO=1`.
- `campanha/SKILL.md` §roll6: "**`saude`** sincroniza sozinho… Leia as linhas `roll6: ...`".
- **Código:** `cmd_saude` só escreve `saude.md` e imprime "o roll6 recebe vida e fadiga quando
  a processar-turno fecha o turno". O `CLAUDE.md` e as outras skills já dizem isso.

### 7. O "Contrato para as outras skills" da `campanha` manda escrever direto

- `campanha/SKILL.md` §"Contrato para as outras skills": skill nova deve chamar
  `campanha.py acontecimento`/`anotar` ela mesma, com `--imagem`. A descrição da skill diz
  "É por esta skill que as outras registram".
- Isso contradiz a fronteira da `registrar-acao` como **única** escritora depois do dado.
  Quem ler esta seção para escrever uma skill nova refaz o espalhamento que o refactor desfez.

### 8. A `acao` ainda ensina a registrar sozinha

- §4 "Registrar — **as três camadas**" lista **quatro** (a–d) e manda rodar `campanha.py`
  direto. A descrição diz "registra tudo".
- O `CLAUDE.md` diz o contrário: "Onde `acao` hoje descreve registrar as quatro camadas, ela
  passa a entregar o JSON". A própria seção roll6 da `acao` já fala em entregar o ato.
- `acao.py` (docstring): "o registro é da skill campanha".

### 9. A `processar-turno` grava por fora da `registrar-acao`

- `processar-turno/SKILL.md` §5 usa `campanha.py acontecimento/saude/anotar/bolsa` direto. A
  `registrar-acao` se apresenta como quem recebe o ato da `processar-turno`.
- `processar_turno.py` (docstring): "registrar é da skill campanha".
- ~~**Falta no fluxo:** a skill manda a narração para o `process_turn`, mas não manda
  arquivá-la no capítulo.~~ **Resolvido em 03/10:** a seção 6a da `processar-turno` torna
  a narração obrigatória, arquivada pelo `narrar.py gravar` e exibida na tela.
- **Falta também** `mantimentos.md`: o `CLAUDE.md` diz que o desconto do dia sai no mesmo
  momento em que o número é dito à mesa, mas nenhuma skill menciona o arquivo
  (`processar-turno`, `campanha`, `status-atual`).
- **Falta `posture`:** o `process_turn` aceita postura (1 de pé, 2 caído, 3 fora de
  combate). A skill nunca a cita. O NelsOwned segue "fora de combate" no roll6, mesmo
  acordado com 4 PV.

### 10. `--gravar` "pela skill `campanha`" e "esta skill registra no repositório"

- `teste-nh/SKILL.md:182`, `iniciativa/SKILL.md:114`, `atacar/SKILL.md:277`,
  `atacar-distancia/SKILL.md:246`: `--gravar` registra "pela skill `campanha`". O código
  entrega à `registrar-acao`.
- A seção roll6 de `roll`, `teste-nh`, `atacar`, `atacar-distancia` e `iniciativa` abre com
  "Esta skill **resolve e registra no repositório**". Em `atacar`, `atacar-distancia` e
  `iniciativa`, o parágrafo final se repete quase igual.
- A `roll` diz que "os scripts desta skill só gravam o acontecimento no capítulo, pela
  `registrar-acao`". O `roll.py` não grava nada.

### 11. A `reacao` grava por padrão; as outras, só com `--gravar`

- `teste-nh`, `disputa-nh`, `iniciativa`, `atacar` e `atacar-distancia`: opt-in (`--gravar`).
- `reacao`: grava sempre, e `--nao-gravar` desliga. Isso explica parte do item 1: rolar
  reação para ver já põe a faixa no log do capítulo.

### 12. "As skills se chamam por subprocesso com `--json`, sem import": o código faz o contrário

- **`CLAUDE.md`:** "As skills se chamam por subprocesso com saída JSON… sem `import` entre
  pastas de skill". A exceção é ler o formato de um arquivo alheio, além da importação do
  `d6()` da `roll`.
- **Código:**
  - `atacar` importa `teste_nh`, `resolver_defesa`, `causar_dano` e `arbitrar_ferimento`;
  - `atacar-distancia` importa o `atacar` inteiro;
  - `disputa-nh` importa `teste_nh`;
  - `processar_turno.py` importa `acao` (um roteador) para chegar ao `contexto`.

  Dos resolvedores, nenhum aceita `--json`.
- **Inversão de dono:** `calcular-alcance` (folha) importa a tabela de escala de
  `atacar-distancia/scripts/tabelas_distancia.py` (roteador). Pela "regra de colocação", a
  tabela de velocidade/distância é da folha que mede distância.
- **Caminho:** ou o `CLAUDE.md` passa a dizer que import por caminho entre folhas é o padrão,
  ou os scripts migram. Hoje a regra escrita não descreve o repositório.

### 13. Lista de consumidores do `contexto` desatualizada

- `contexto/SKILL.md` §Dependências cita `causar-dano`, que não importa `contexto`, e a
  `processar-turno`, que chega a ele pelo `acao`.
- Omite os que importam: `resolver-defesa`, `status-atual`, `roll6`, `registrar-acao`.
- Também omite que `atacar` e `disputa-nh` chegam a ele pelos apelidos do `teste_nh`.

### 14. `registrar-acao/SKILL.md` × `registrar_acao.py`

- **Ordem:** a SKILL diz "acontecimento → anotações → bolsa → saúde"; o código (e o
  `CLAUDE.md`) inclui a narração depois das anotações.
- **Caminho de exemplo:** `--ato .qwen/tmp/ato.json`, na SKILL e na docstring. É resto de
  outra ferramenta; não existe `.qwen/` neste repositório.
- **Dependência:** diz depender de `narrar` "que produz o texto que ela arquiva", mas quem
  arquiva a narração é o próprio `narrar.py`. Para a registradora vai só o resumo de uma linha.

### 15. A mudança não commitada do `narrar/SKILL.md`

- **Duplo asterisco:** o formato novo de linha pede `→ **SUCESSO por X**` (duplo asterisco).
  Na mesma seção, a tabela diz "Não use: `**duplo asterisco**`", e o `CLAUDE.md` usa
  `*11*`. As narrações 10 a 12 já saíram com `**`.
- **Uma linha × duas:** o formato novo junta NH e dado numa linha
  (`<o que> <quem>: … NH <n>, 3d [a,b,c] = <soma> → …`). O exemplo do `CLAUDE.md` e a saída
  dos scripts usam duas (`> Ataque: … = *11*` e `> 3d [3, 4, 1] = *8* → sucesso por 3`).
  "Repasse as linhas como o script imprimiu" e "uma linha = uma jogada" não cabem juntas.
- ~~**Reescrita que não existe** e **cópia manual** em `whatsapp/output/`.~~ **Resolvido
  em 03/10:** o `narrar.py gravar` agora salva a cópia sozinho e imprime o bloco na tela.
  A SKILL diz que cada `gravar` é uma narração nova, sem modo de reescrever.

### 16. `campanha/SKILL.md`: imagens e estrutura

- **Imagens:** a descrição diz "Sempre gera a imagem de abertura do capítulo", e o texto,
  "todo acontecimento relevante sai com ilustração". Na prática, o cap. 07 não tem
  `inicio.png`, e nenhum dos acontecimentos da travessia tem imagem ou `--prompt`. A
  `narrar` diz "esta skill não gera imagem". Falta decidir se a regra ainda vale.
- **Árvore desatualizada:** a "Estrutura" lista no jogo só o `README.md`. Faltam
  `npcs.md`, `grupo.md`, `lugares.md` e `reacoes.json` na pasta do capítulo, e `bolsa.md`,
  `saude.md`, `mundo.md`, `mantimentos.md`, `roll6.json` e `whatsapp/` na raiz.

### 17. `status-atual` manda corrigir o roll6 por fora do turno

- **Escrito:** "se o roll6 mostrar outra coisa… `roll6.py saude --pj` reempurra PV e Fadiga".
- **Conflito:** isso é estado de jogo escrito fora da `processar-turno`. O `CLAUDE.md` só
  admite esse caminho "quando chamado pelo caminho explícito". Falta dizer "**só com pedido
  do usuário**".

---

## Baixa — limpeza

| # | Onde | O quê |
|---|---|---|
| 18 | `contexto.py:30` | `RAZ = …parents[4]` definido e nunca usado (resto de `RAIZ`) |
| 19 | `status_atual.py:18` | `CAMPANHA_PY` relativo ao diretório de trabalho; os outros usam `parents[2]` |
| 20 | `campanha.py saude` | "noite sem cura" vira `FAD +0`/`PV +0` para caber no log. Um `--nota` sem número seria honesto |
| 21 | `acao.py` | `achar_personagem(raiz, quem)` só existe para inverter a ordem dos argumentos do `contexto` para o `processar_turno.py` — some se ele importar o `contexto` direto |
| 22 | `narrar.py` | `arquivos_de_contexto()` próprio, de propósito (lista de quem narra ≠ de quem arbitra), mas o `contexto/SKILL.md` diz que a lista "mora" lá |
| 23 | `processar_turno.py` | o veredito "FALTAM AÇÕES" aparece em todo turno da travessia, em que o Mestre dá as ordens no chat. Um `--ordens-do-mestre` evitaria a falsa pendência |

---

## Ordem sugerida

1. **Itens 1 e 11** — a reação no log e no bloco. É o único que expõe segredo de mesa.
2. **Item 2** — nome parcial no `campanha.py`. Já custou uma faxina no `saude.md`.
3. **Itens 6, 7, 8, 10** — texto que ensina o regime antigo. É o que faz a próxima sessão
   repetir o erro.
4. **Item 9** — a `processar-turno` baixar os mantimentos e tratar a postura (a narração
   já foi resolvida).
5. **Item 12** — decidir a regra (subprocesso × import) e alinhar texto ou código.
6. O resto, quando passar por perto.
