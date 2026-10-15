---
name: criar-animacao
description: >
  Cria uma animação de personagem no formato "roll6-animation" (JSON) para a biblioteca de
  animações do Roll6, que a toca nos tokens com modelo 3D de esqueleto Mixamo. A partir de uma
  descrição do movimento ou de uma imagem de pose, escreve os giros de cada osso por instante,
  grava em animacoes/, valida com as regras exatas do Roll6 e, se o usuário pedir, envia para a
  biblioteca pelo MCP. Use when the user asks "/criar-animacao", "criar animação para o token",
  "animação 3D do personagem", "animação no formato do Roll6", "animação de ataque/corrida/morte",
  "fazer o orc acenar".
---

# Criar animação

O Roll6 anima os modelos 3D dos tokens com dados simples: para cada **osso** de um esqueleto
**Mixamo**, uma lista de **instantes** e, em cada instante, um **giro em graus** sobre a pose de
descanso do osso, num arquivo JSON que qualquer usuário envia para a **biblioteca de animações**
(menu do usuário › "Animações", ou a ferramenta MCP `create_animation`).

O Roll6 **não tem animação própria**: um modelo toca os clips do próprio `.glb` ou as animações
da biblioteca escolhidas no token (aba "Animação"). Sem nenhuma das duas, ele fica parado — e
deitado de costas quando caído. Por isso, para um modelo sem clips, é esta skill que dá vida a ele.

A animação só funciona em modelos cujo esqueleto usa os nomes do Mixamo (`Hips`, `Spine`,
`LeftUpLeg`… com ou sem `mixamorig:`). Em outro esqueleto ela não é oferecida no token.

Os arquivos gerados ficam em `animacoes/<slug>.json` na raiz deste repositório.

## Tipos e estados do token

Toda animação da biblioteca tem um **tipo**. Por enquanto cada estado do token aceita **só o seu**
tipo; os outros quatro ficam guardados para estados que ainda vão existir — **avise o usuário**
quando o tipo pedido não aparece nos tokens.

| Tipo | `type` no arquivo | Estado do token | `loop` padrão |
|---|---|---|---|
| Parado | `idle` | **Parado** | `true` |
| Andando | `walk` | **Caminhando** | `true` |
| Correndo | `run` | — (só guardado) | `true` |
| Agachado | `crouch` | — (só guardado) | `true` |
| Derrotado | `defeated` | **Caído** (toca uma vez e fica no último quadro) | `false` |
| Atacando | `attack` | — (só guardado) | `false` |
| Defendendo | `defend` | — (só guardado) | `true` |

No token a escolha vira `animation:{animationId}` (`modelIdleClip`, `modelWalkClip`,
`modelDownClip`). O Roll6 recusa uma animação de outro tipo no estado.

## O formato (regras do Roll6, não negociáveis)

```json
{
  "format": "roll6-animation",
  "version": 1,
  "name": "Aceno",
  "type": "idle",
  "description": "Acena com a mão direita acima da cabeça.",
  "duration": 1,
  "loop": true,
  "tracks": [
    { "bone": "RightArm", "times": [0, 0.5, 1], "degrees": [[0, 0, -150], [0, 0, -150], [0, 0, -150]] },
    { "bone": "RightForeArm", "times": [0, 0.25, 0.5, 0.75, 1], "degrees": [[0, 0, 0], [0, 0, 30], [0, 0, 0], [0, 0, -30], [0, 0, 0]] },
    { "bone": "Spine", "times": [0, 0.5, 1], "degrees": [[0, 0, -3], [0, 0, -5], [0, 0, -3]] }
  ],
  "hipsLift": { "times": [0, 0.5, 1], "values": [0, 0.003, 0], "of": "height" }
}
```

| Campo | Regra |
|---|---|
| `format` / `version` | exatamente `"roll6-animation"` / `1` |
| `name`, `type`, `description` | opcionais; só **sugestões** para o envio (nome ≤ 100 caracteres; `type` em inglês, tabela acima) |
| `duration` | segundos, maior que 0 e **até 30** |
| `loop` | `true` = ciclo (faça a **primeira chave igual à última**); `false` = toca uma vez e fica parado no último quadro |
| `tracks` | **1 a 64** trilhas, cada osso **uma vez só** |
| `bone` | um dos ossos aceitos (abaixo), sem o prefixo `mixamorig:` |
| `times` | 1 a 600 números, **começando em 0**, estritamente crescentes, o último **≤ `duration`** |
| `degrees` | **um `[x, y, z]` por instante**, cada valor entre −360 e 360 |
| `hipsLift` | opcional: sobe/desce o quadril. `times` com as mesmas regras; `values` um por instante, entre −2 e 2; `of` = `"height"` (padrão: fração da altura do modelo) ou `"hips"` (fração da altura do quadril acima do ponto mais baixo — para movimentos que terminam no chão) |
| Tamanho | até **1 MB**. Campos desconhecidos são ignorados |

### Ossos aceitos (52)

- **Corpo:** `Hips`, `Spine`, `Spine1`, `Spine2`, `Neck`, `Head` e, para `Left` e `Right`:
  `Shoulder`, `Arm`, `ForeArm`, `Hand`, `UpLeg`, `Leg`, `Foot`, `ToeBase`.
- **Dedos:** para `Left` e `Right`: `HandThumb1–3`, `HandIndex1–3`, `HandMiddle1–3`,
  `HandRing1–3`, `HandPinky1–3`.

Um osso que o modelo não tem é ignorado; os outros tocam normalmente.

### Eixos e sinais (o referencial do personagem)

Os giros são em graus, **sobre X, depois Y, depois Z**, no referencial **do personagem**: +X é a
**esquerda dele**, +Y é **para cima**, +Z é **para a frente**. Cada giro é aplicado no osso, sobre a
pose de descanso — não importa como o rig orientou os eixos locais.

| Giro | Efeito |
|---|---|
| X **positivo** num membro pendurado | ele vai **para trás** (a ponta vai para −Z) |
| X **negativo** em `*Arm` / `*UpLeg` | ergue o braço **à frente** / leva a coxa **à frente** |
| X **positivo** em `*Leg` | **dobra o joelho** |
| X **negativo** em `*ForeArm` | **dobra o cotovelo** |
| X positivo em `Spine`/`Spine1` | inclina o tronco **para a frente**; em `Neck` negativo, ergue a cabeça |
| Y positivo | vira a frente para a **esquerda** do personagem |
| Z positivo | ergue o lado **esquerdo** (+X): `LeftArm` +Z abre o braço esquerdo para o lado; `RightArm` **−Z** abre o direito; `LeftUpLeg` +Z afasta a perna esquerda |
| `Hips` X −90 com `hipsLift` `of: "hips"` até ≈ −0,8 | deitado de costas (`roll6-morte.json`) |

**Mãos:** sem trilhas de dedos a mão fica **aberta**, como na pose de descanso — e nenhuma mão fecha
sozinha. Os dedos partem da **pose T, com a palma para baixo**, então um dedo dobra em direção à
palma com **Z negativo na mão esquerda e Z positivo na direita** (a direita é o espelho: troque o
sinal de Y e Z). Receita do **punho esquerdo** (medida num rig Mixamo):

| Osso (esquerda) | Giro do punho fechado |
|---|---|
| `LeftHandIndex1`, `LeftHandMiddle1`, `LeftHandRing1`, `LeftHandPinky1` | `[0, 0, -70]` |
| `…2` dos mesmos dedos | `[0, 0, -90]` |
| `…3` dos mesmos dedos | `[0, 0, -60]` |
| `LeftHandThumb1` / `Thumb2` / `Thumb3` | `[0, 45, -20]` / `[0, 20, -30]` / `[0, 0, -40]` |

Multiplique tudo pelo quanto a mão fecha: **0,3 relaxada** (parado, andando, caído), **0,5 meio
fechada** (correndo), **0,85 segurando um cabo** (arma, escudo), **1 punho** (guarda, soco); 0 =
aberta (acenar, apontar). Mantenha o mesmo giro em **todas as chaves** — a mão é uma pose — a não
ser que ela abra ou feche durante o movimento (agarrar, soltar). São 15 trilhas por mão; elas
cabem no limite de 64 junto com o corpo.

**Braços:** antes da animação o Roll6 deixa os braços **pendurados relaxados**, um pouco afastados
do corpo, seja qual for a pose T ou A do rig. Os giros de `LeftArm`/`RightArm` partem desse braço
caído: X −90 aponta o braço para a frente, Z ±90 abre para o lado, ±150 leva acima da cabeça.

## Scripts

Só biblioteca padrão do Python.

| Script | O que faz |
|---|---|
| `scripts/validar.py <arquivo.json> [...]` | as regras **exatas** do Roll6 (mesmas chaves e mensagens de erro). `OK` ou `ERRO <chave>: <mensagem>` |
| `scripts/enviar.py <arquivo.json> [--nome …] [--tipo …]` | valida e envia pela ferramenta MCP `create_animation` (o mesmo acesso da skill `roll6`); imprime o `animationId` e o valor `animation:{id}` para o token |

`exemplos/` traz um arquivo pronto por tipo — **comece do mais parecido**. Os `roll6-*.json` são os
movimentos que o Roll6 tocava sozinho até a versão 0.28; hoje são só exemplos e, para usá-los num
token, envie-os para a biblioteca como qualquer outra animação:

| Arquivo | Tipo | O que é |
|---|---|---|
| `roll6-parado.json` | Parado | respiração (giros pequenos, 3 s, mãos relaxadas) |
| `roll6-guarda.json` | Parado | posição defensiva (guarda alta, joelhos dobrados, punhos fechados) |
| `aceno.json` | Parado | aceno com a mão direita aberta acima da cabeça, a esquerda relaxada |
| `roll6-caminhada.json` | Andando | caminhada (1 s, pernas em oposição, braços contra as pernas) |
| `correndo.json` | Correndo | passadas largas, joelhos altos, braços dobrados |
| `agachado.json` | Agachado | agachado atento, respirando |
| `roll6-morte.json` | Derrotado | queda de costas (1,4 s, uma vez) |
| `atacando-machado.json` | Atacando | golpe de machado com as duas mãos, de cima para baixo, segurando o cabo |
| `defendendo-escudo.json` | Defendendo | escudo erguido à frente do peito, arma atrás, as duas mãos segurando |

## Fluxo

1. **Entenda o pedido.** Qual movimento, qual **tipo** (pergunte se não estiver claro; confirme
   quando deduzir) e se repete. Lembre que só Parado, Andando e Derrotado aparecem nos tokens.
2. **Descrição → animação.**
   - Divida o movimento em **fases** (preparação, ação, recuperação; ou as metades de um ciclo).
   - Escolha os **instantes**: 4 a 8 chaves bastam. Ciclos: a última chave **igual** à primeira.
     Uma vez: termine na pose em que deve ficar (Derrotado termina no chão).
   - Para cada fase, escreva o giro de cada osso que se move, usando a tabela de sinais e o
     exemplo mais parecido como régua de amplitude. Mova poucos ossos com clareza: tronco
     (`Spine`), cabeça (`Neck`/`Head`), braços (`*Arm`, `*ForeArm`), pernas (`*UpLeg`, `*Leg`,
     `*Foot`). Use `hipsLift` para abaixar o corpo (agachar, golpear, cair).
   - Pares opostos (pernas numa corrida, braços contra as pernas) andam em **fase oposta**.
   - **Feche as mãos** de acordo com o que elas fazem (receita em "Mãos"): relaxada, segurando,
     punho ou aberta. Uma animação sem trilhas de dedos fica com a mão espalmada.
3. **Imagem de pose → animação.** A imagem é uma **pose de referência**, não um vídeo.
   - Leia a pose: inclinação do tronco, direção da cabeça, de cada braço e antebraço, de cada coxa
     e canela, afastamento das pernas, altura do corpo — e **cada mão**: aberta, relaxada, segurando
     algo ou fechada.
   - Converta em giros pela tabela de sinais (ex.: antebraço dobrado a 90° → `ForeArm` X −90;
     coxa à frente 30° → `UpLeg` X −30).
   - Escreva a animação que sai do **descanso** (todos os giros 0) e chega à pose em **0,4 a 0,8 s**,
     e a **mantém**. Nos tipos que repetem (Parado, Defendendo, Agachado), faça um ciclo já na pose,
     com uma **respiração** leve (±1 a 2° no tronco e um mínimo de `hipsLift`), primeira chave igual
     à última. Nos que tocam uma vez, termine na pose.
4. **Grave** em `animacoes/<slug>.json` (slug do nome, minúsculas e hífens), com `name`, `type` e
   uma `description` de uma linha.
5. **Valide** com `python .claude/skills/criar-animacao/scripts/validar.py animacoes/<slug>.json`
   e corrija até dar `OK`. **Nunca entregue um arquivo que não passou.**
6. **Explique** o movimento em um parágrafo (o que cada fase faz) e diga em que estado do token ele
   entra — ou que é só guardado, para os tipos sem estado.
7. **Envie só quando o usuário pedir:**
   `python .claude/skills/criar-animacao/scripts/enviar.py animacoes/<slug>.json --nome "…" --tipo …`.
   Passe adiante o `animationId` e o valor `animation:{id}`; para usá-lo num token, a ferramenta
   `update_token` (enviando todos os campos atuais, que ela substitui) ou o formulário do token,
   aba "Animação".

## Erros comuns

- **Sinal do joelho e do cotovelo:** joelho dobra com X **positivo**; cotovelo com X **negativo**.
  Invertido, o membro dobra para o lado errado.
- **Braços:** partem do braço **caído relaxado**, não da pose T. Para o braço à frente use X
  negativo; para o lado use Z (+ no esquerdo, − no direito).
- **Instantes:** sempre começando em **0**, crescentes, e o último **≤ `duration`**. Um `degrees`
  por instante, sempre `[x, y, z]`.
- **Ciclo com salto:** num `loop: true`, a última chave diferente da primeira dá um tranco a cada
  volta.
- **Exagero:** acima de ~120° fora de ombro e quadril a malha costuma rasgar. O Roll6 toca a
  animação completa e avisa quando ela deforma o modelo.
- **Mão aberta:** esquecer os dedos deixa a mão espalmada em todo movimento. Ponha sempre as 30
  trilhas de dedos (receita acima); só deixe aberta de propósito.
- **Dedo para trás:** na mão direita o sinal de Z é **positivo**; com o sinal da esquerda os dedos
  dobram para as costas da mão.
- **Osso inventado:** `LeftElbow`, `Chest`, `Pelvis` não existem — use a lista acima.

## O que esta skill não faz

- Não extrai movimento de vídeo ou de sequências de quadros: a imagem é uma pose.
- Não anima esqueletos que não sejam Mixamo, nem edita `.glb`.
- Não escolhe a animação no token sozinha: só envia, e diz o valor a usar.
