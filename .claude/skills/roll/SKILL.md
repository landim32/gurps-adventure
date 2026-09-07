---
name: roll
description: >
  Rola dados de GURPS no formato do livro — 1d+1, 3d, 2D-1, 2Dx10 — sorteando de 1 a 6 por
  dado e aplicando modificador e multiplicador. É o único lugar do repositório que sorteia
  número: toda outra skill que precise de dado chama esta. Use when the user asks to "role",
  "rola 3d", "1d+1", "joga os dados", "tira um dado", ou /roll.
---

# roll

```
python .claude/skills/roll/scripts/roll.py 1d+1
```

```
1d+1: [6] + 1 = **7**
```

Cada dado é um sorteio de **1 a 6**. Os dados saem entre colchetes, depois o modificador,
depois o total — para dar sempre para conferir a conta.

## O que ele aceita

| Escreva | É |
|---|---|
| `1d` | um dado |
| `1d+1` | um dado, mais 1 |
| `3d` | três dados somados |
| `2D-1` | maiúsculo tanto faz |
| `1d6+2` | o `6` é opcional e ignorado — todo dado aqui tem 6 faces |
| `2dx10` | multiplica o resultado por 10, como o GURPS escreve `2Dx10` |

Várias de uma vez, que ele soma tudo no fim:

```
python .claude/skills/roll/scripts/roll.py 3d 1d+2 2d-1
```

`--vezes N` repete cada fórmula N vezes — serve para uma rajada, ou para sortear vários
NPCs de uma vez.

**Não existe d20, d10 nem d8.** GURPS é d6 e o script recusa o resto em vez de fingir que
entendeu.

## Nunca invente o dado

Esta é a regra que faz a skill valer alguma coisa.

**Rode o comando e relate o que ele imprimiu**, número por número. Não escreva um resultado
sem ter rodado, não rode de novo porque o primeiro saiu ruim, e não arredonde a favor de
ninguém — nem do jogador, nem do monstro.

Se o usuário quiser um valor específico (para testar uma regra, para montar um exemplo),
ele pede — e aí **diga na resposta que o número foi escolhido, não rolado**.

## As outras skills rolam por aqui

Skill que precise de dado **não sorteia por conta própria**: usa esta. Assim existe um
único gerador no repositório, um único formato de saída e uma única regra sobre não
inventar resultado.

Em Python, importando a função:

```python
import importlib.util
from pathlib import Path

ROLL_PY = Path(__file__).resolve().parents[2] / "roll" / "scripts" / "roll.py"
_spec = importlib.util.spec_from_file_location("roll", ROLL_PY)
_roll = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_roll)

d6 = _roll.d6          # d6(3) -> [4, 1, 6]
```

`ROLL_PY` sobe até `.claude/skills/` a partir de `<skill>/scripts/x.py` — se o script
estiver noutra profundidade, ajuste o `parents[...]`.

| Função | Devolve |
|---|---|
| `d6(n=1)` | a lista dos dados, para quem precisa ver cada um |
| `rolar("2d-1")` | `(total, "2d-1: [6, 2] = 8 - 1 = **6**")` |

A `iniciativa` já faz assim. Quando escrever uma skill nova que role dado, copie o trecho
acima em vez de chamar `random` direto.

## O que ele não faz

Este comando **só rola**. Ele não sabe o que é NH, não diz se passou ou falhou, não conhece
sucesso decisivo nem falha crítica.

Quem interpreta o número é quem pediu a rolagem, com o livro na mão:

| Precisa de | Onde está |
|---|---|
| Sucesso decisivo e falha crítica | `livros/gurps-mb-3ed/09-testes-de-habilidade.md` |
| Disputa de Habilidades | mesmo arquivo, "Disputa de Habilidades" |
| Tabela de Reações (as oito faixas) | `livros/gurps-mb-3ed/21-quadros-e-tabelas.md` |
| Bônus de dano por tipo (corte +50%, perfuração ×2, **depois** da RD) | `livros/gurps-mb-3ed/07-equipamento-e-carga.md` |
| Surpresa e iniciativa | a skill `iniciativa` |
