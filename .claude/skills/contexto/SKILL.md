---
name: contexto
description: >
  Folha única de contexto da mesa: de quem é a ação (resolve nome de jogador OU de
  personagem, inteiro ou em parte), a ficha lida como dados, as perícias e o NH que ele de
  fato tem, as vantagens com nível, o veredito de uma rolagem (sucesso decisivo / falha
  crítica), a entrada da perícia no livro, o estado da campanha, as reações já roladas com
  cada NPC e a lista de arquivos a ler antes de arbitrar. Não rola dado, não decide regra,
  não escreve em lugar nenhum. Use when the user asks "/contexto", ou quando qualquer outra
  skill precisar de quem age e de como as coisas estão.
---

# Contexto

Uma pergunta, seis respostas. É o que toda skill de ação precisa antes de arbitrar, e era
reimplementado **seis vezes** no repo — seis políticas de resolução de nome, quatro cópias
do leitor de estado, seis `slug()`. Esta folha é a dona.

```
python .claude/skills/contexto/scripts/contexto.py contexto --quem Bruno
python .../contexto.py contexto --quem "Jah" --json
python .../contexto.py quem  --nome Kaelric --json      # só a ficha, em JSON cru
python .../contexto.py estado --json                    # campanha atual, mapas, arquivos
python .../contexto.py classificar --total 17 --nh 16    # veredito de uma rolagem
python .../contexto.py reacoes --pj "Jah Kagadu" --todos
```

## O que ela sabe

| Pergunta | Resposta |
|---|---|
| De quem é a ação? | `--quem` aceita **jogador ou personagem**, inteiro ou em parte: `Bruno` → Negrum, `Kaelric` → Irmão Kaelric, `nels` → NelsOwned. Ambíguo ou inexistente: erro com a lista do que existe, para a skill não adivinhar. |
| O que ele sabe fazer? | A lista de perícias e magias com NH, e `pericia(d, "Escudo")` devolve o melhor NH entre as que casam com o nome. O resto é pré-definido. |
| Como está a mesa? | `estado()` numa forma só: sem campanha ativa, `{"ativa": False}` — sempre. As cópias antigas divergiam (`{}` em uma delas), e aí quem consultava não distinguia "sem campanha" de "campanha sem chave". |
| O que este dado significa? | `classificar(total, nh)` é a dona da regra de **sucesso decisivo e falha crítica** (MB, cap. 12): 3-4 sempre decisivo; 5 com NH 15+; 6 com NH 16+; 18 sempre crítico; 17 crítico abaixo de NH 16; falha por 10+ sempre crítica. |
| O que o livro diz da perícia? | `busca_no_livro("Escudo")` → dificuldade, pré-definido e linha de modificadores, direto de `06-pericias.md`. |
| Como os NPCs já o viram? | `reacoes_do_pj()` lê o `reacoes.json` do capítulo — ou de todos, com o mais novo vencendo (`--todos`). **Não se rola reação de novo.** |
| O que ler antes? | `arquivos_de_contexto()` na ordem certa: ficha, `mundo.md`, plano do capítulo, NPCs do plano, NPCs da mesa (que ganham do plano), grupo, lugares, README da cena, NPCs da campanha. |

## Como as outras skills consomem

**Precisa do número, uma vez:** subprocesso com `--json` e lê a saída.
**Precisa da função a cada jogada:** importa, como já se faz com `roll`:

```python
import importlib.util
from pathlib import Path

CTX_PY = Path(__file__).resolve().parents[2] / "contexto" / "scripts" / "contexto.py"
_spec = importlib.util.spec_from_file_location("contexto", CTX_PY)
ctx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ctx)

d = ctx.ler_ficha("Kaelric", RAIZ)
nh, nome = ctx.pericia(d, "Escudo")
veredito = ctx.classificar(17, nh)
```

API exportada: `simples`, `slug`, `raiz_de`, `estado`, `fichas`, `achar_personagem`,
`ler_ficha`, `atributos`, `pericia`, `nivel_vantagem`, `classificar`, `margem`,
`busca_no_livro`, `reacoes_do_pj`, `arquivos_de_contexto`, `CAMPANHA_PY`, `ATRIBUTOS`.

**Restrição que prende todo o grafo:** o `parents[2]` acima sobe exatamente de
`<skill>/scripts/x.py` até `.claude/skills/`. Skill nenhuma pode ser aninhada dentro de
outra — `calcular-alcance` é **irmã** de `atacar`, não filha. Árvore é o grafo de chamadas,
não o diretório.

## O que esta folha nunca faz

- **Não rola dado.** Quem rola é a `roll`, uma só.
- **Não decide que tipo de ação é nem qual perícia usar** — isso é do roteador (`acao`).
- **Não escreve em lugar nenhum.** Nem ficha, nem log, nem `reacoes.json`.
- **Não arbitra modificador.** Ela entrega o número e a regra; o motivo de cada bônus é de
  quem está arbitrando a cena.

## Dependências

Nenhuma. É folha. `campanha` é lida por subprocesso (`estado --json`), `livros/` é lida como
texto. Quem a consome: `acao`, `narrar`, `reacao`, `iniciativa`, `teste-nh`, `disputa-nh`,
`atacar`, `causar-dano`, `arbitrar-ferimento`, `processar-turno`.
