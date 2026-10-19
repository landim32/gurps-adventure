---
name: causar-dano
description: >
  Resolve o que o dano faz depois que o golpe passou pela defesa: rola (ou recebe) o dado
  da arma, soma Ataque Total, aplica o dano mínimo de corte e perfuração antes da armadura
  (MB, pág. 74), o teto da arma e o ½D de projétil, o multiplicador do golpe fulminante, a
  RD do local atingido mais a RD natural do crânio, o multiplicador do tipo de dano e do
  local, o teto do local (HT/, HT×, HT) com o que se desperdiça, o membro incapacitado e os
  efeitos terminais do pescoço (traqueia esmagada, decapitação). Não rola ataque, não
  resolve defesa, não decide queda nem atordoamento, não escreve em lugar nenhum. Use when
  the user asks "/causar-dano", ou quando `atacar` e `atacar-distancia` precisam saber
  quanto o alvo perdeu.
---

# Causar dano

Uma bala de .25 atravessa uma placa de metal e mata um homem de armadura completa; uma espada
longa bate sem força nenhuma no peito. **O número do dado é a última coisa que decide o
estrago.** Esta folha é a única dona dessa conta no repositório — o `atacar` e o
`atacar-distancia` chamam a mesma, e por isso um golpe de frente e uma flecha não podem mais
divergir no meio do caminho.

```
python .claude/skills/causar-dano/scripts/causar_dano.py \
  --alvo "Morto 3" --tipo perf --formula "2D+2" --rd-total 4 --rd-local 4 \
  --ht-alvo 12 --local '{"nome":"Cabeça","rd_natural":2,"mult_tipo":{"corte":1.5}}'
```

Chamada de dentro de outra skill, é `calcular(payload)` — o mesmo dicionário, sem subprocesso.

## A ordem, que é a regra

| # | Passo | Onde está no livro |
|---|---|---|
| 1 | dado da arma + bônus de Ataque Total | — |
| 2 | **dano mínimo**: corte e perfuração que acertam fazem ao menos 1 ponto **básico** | MB, pág. 74 |
| 3 | teto da arma e ½D (só projétil) | arma por arma |
| 4 | ×2 (ou mais) do golpe fulminante | MB, pág. 105 |
| 5 | menos a RD **do local atingido**, somando a RD natural do crânio; e o golpe que ignora armadura não passa por aqui | MB, pág. 75 |
| 6 | multiplicador: do local se houver, senão do tipo (contusão ×1, corte ×1,5, perfuração ×2, bala ×½) | cap. 14 + regra da casa |
| 7 | teto do local, e o que se **desperdiça** quando o excesso atravessa a vítima | cap. 14 |
| 8 | membro incapacitado, e o pescoço: traqueia acima de HT/2, decapitação acima de 3×HT | casa (4ª ed.) |

O **passo 2 antes do 5 é o erro que a mesa mais comete**: o mínimo de 1 vale sobre o dado,
não sobre o que sobra da armadura. Corte fraco contra malha ainda faz 1 ponto *básico*, que a
RD pode anular inteiramente.

## O que esta folha não faz

- **Não rola ataque nem resolve defesa.** Ela só é chamada depois de um golpe que passou.
- **Não decide queda, atordoamento, nocaute, sufocação nem choque** — isso é a
  `arbitrar-ferimento`. Ela devolve o `ferimento`, e com o resto no payload a folha irmã
  decide o que fazer dele.
- **Não rola dado por conta própria quando alguém já rolou**: com `--dado`, a cascata parte
  do número informado; sem ele, chama a `roll`. É assim que se testa a regra sem depender
  de sorte, e não é licença para escolher o resultado na mesa.
- **Não escreve em lugar nenhum.** Devolve linhas e números; quem lança é a `registrar-acao`.

## O que ela devolve

```json
{
  "saida":  ["\nDANO: 2D", "  RD 4 → 2 ponto(s) atravessam", "**Morto 3 perde 4 ponto(s) de vida.**"],
  "mec":    ["Dano: 2D: [5, 1] = *6*", "RD 4 → 2 passam", "Perfuração: ×2 → *4*"],
  "resultado": {
    "basico": 6, "passou": 2, "ferimento": 4, "perdido": 0,
    "membro_incapacitado": false, "armadura_segurou": false, "ignora_armadura": false
  }
}
```

`saida` é o que se imprime na mesa do Mestre, `mec` é o que vai para o bloco do WhatsApp na
ordem em que aconteceu, `resultado` é o número que a `registrar-acao` lança em `saude.md`.
`armadura_segurou` é caso de encerrar o golpe ali: quem chamou decide a saída e para de
contar.

## Payload, campo por campo

| Campo | O que é | Omissão |
|---|---|---|
| `alvo`, `chave`, `ht_alvo` | quem apanha, qual entrada de `LOCAIS` foi atingida, a HT dele | sem HT não há teto de local nem teste de queda: a folha diz isso na saída |
| `tipo` | `cont`, `corte`, `perf`, `bal` | — |
| `formula`, `dado` | dado da arma, ou o resultado já rolado | sem `dado`, rola pela `roll` |
| `bonus_dano` | Ataque Total e manobras que somam dano | 0 |
| `mult_dano`, `ignora_armadura` | o que o golpe fulminante fez | 1, `false` |
| `rd_total`, `rd_local`, `peca` | RD que conta, RD exibida, de onde veio | 0 |
| `local` | a entrada de `LOCAIS` já resolvida por quem chamou | `{}` = tronco sem regra |
| `teto_arma`, `teto_arma_rotulo` | projétil limitado pela arma, não por quem atira | sem teto |
| `meia_dano`, `meia_de` | passou do Meio Dano | `false` |
| `efeito` | o que a Tabela de Golpes Fulminantes decidiu | `{}` |
| `frontal` | golpe pela frente (pescoço) | `true` |
| `trespassa_por`, `nota_membro` | texto: “o projétil trespassa”, nota da flecha no pé | golpe, sem nota |

## Dependências

`roll` (dado), e as tabelas de local chegam **prontas no payload** — a folha não conhece
`LOCAIS`, quem conhece é quem chamou. Assim ela não tem de saber se a espada é uma cimitarra
ou um virote, e a mesa continua capaz de auditar cada linha da conta.
