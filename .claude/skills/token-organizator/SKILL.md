---
name: token-organizator
description: >
  Organiza uma pasta de imagens soltas em tokens de RPG prontos para o mapa: identifica
  quais imagens são tokens (figuras de personagem vistas de cima), deixa o fundo
  transparente quando necessário, gira a figura para encarar o sul, renomeia com nome
  descritivo, move para tokens/ e mantém o catálogo em dia. Use when the user asks to
  "organizar os tokens", "importar tokens dessa pasta", "catalogar tokens", "renomear os
  tokens", "orientar os tokens para o sul", ou /token-organizator.
---

# Organizar tokens

Pega uma pasta de imagens soltas — downloads, um pacote baixado, capturas — e transforma
no acervo de tokens da mesa: só o que é token, com fundo transparente, nome que diz o que
é e catálogo atualizado.

**Esta skill não baixa nada.** Ela parte de arquivos que já estão no disco. Ponha as
imagens numa pasta qualquer e aponte a skill para ela.

O trabalho se divide assim, e a divisão é proposital:

| Etapa | Quem faz |
|---|---|
| Inventariar a pasta de origem | `scripts/triar.py` |
| **Dizer o que é token** | **Você, olhando as imagens** |
| Recortar o fundo quando faz falta | `scripts/remover_fundo.py` |
| **Ver para onde a figura olha** | **Você, olhando as imagens** |
| Girar para o sul | `scripts/orientar.py` |
| Nomear e mover | Você |
| Regerar o catálogo | `scripts/catalogar.py` |

Reconhecer token é trabalho de visão, não de heurística: numa mesma pasta convivem o
token, a página de ficha do monstro, o logo do site e um retrato de rosto. Só olhando dá
para separar. Não invente regra de tamanho ou de nome de arquivo para adivinhar isso.

## Como fica organizado

```
tokens/
  CATALOGO.md     tabela legível, gerada — não editar à mão
  tokens.json     os metadados de cada token (fonte da verdade)
  <nome>.png      os tokens, em kebab-case descritivo
```

## 1. Inventariar a pasta

```
python .claude/skills/token-organizator/scripts/triar.py --origem <pasta>
```

Lista cada imagem com dimensões, tamanho e se **já tem transparência**, e resolve duas
chatices de pasta de download:

- **Duplicados exatos**, agrupados por conteúdo — a mesma arte baixada duas vezes com
  nomes diferentes. Importe só um de cada.
- **Já importados**: marca o que é byte a byte igual a algo que já está em `tokens/`,
  para não entrar de novo.

Opções: `--recursivo` para entrar em subpastas, `--min-lado` (padrão 150 px) para marcar
o que é pequeno demais para servir, `--tokens` se a pasta de destino não for `tokens/`.

## 2. Olhar e classificar

**Leia cada imagem** e decida. É token quando:

- A figura está vista **de cima** (ortogonal ou quase), como se olhada do teto — cabeça e
  ombros dominam, os pés aparecem por baixo.
- É **uma figura só**, isolada, sem cenário em volta.
- O fundo é liso, transparente, ou um disco/moldura de token.

**Não** é token, por mais que esteja na mesma pasta: página de ficha ou stat block, capa
de livro, mapa, arte de cena com fundo, retrato em três quartos ou de frente, logo,
avatar, propaganda. Retrato de rosto **não serve** — é bonito, mas na mesa fica de lado.

Diga ao usuário o que entrou e o que ficou de fora, com o motivo em uma linha cada. Se
nada for token, diga isso — não force a barra importando um retrato qualquer.

## 3. Recortar o fundo (quando necessário)

```
python .claude/skills/token-organizator/scripts/remover_fundo.py \
  --imagem <origem>/<arquivo> --saida tokens/<nome-descritivo>.png
```

É este comando que também **move e renomeia**: ele lê da pasta de origem e grava já com o
nome final em `tokens/`. O original fica onde estava.

O script **detecta sozinho se a imagem já tem transparência** e, nesse caso, não mexe em
nada — só apara a sobra em volta. Rode-o em todo token, mesmo nos que já parecem
recortados: é ele que decide se há o que fazer.

Quando precisa recortar, ele torna transparente a região de cor uniforme **ligada à
borda** da imagem. É preenchimento por conexão, não limiar por cor, e a diferença
importa: numa cota de malha cinza-clara sobre fundo branco, o limiar comeria a armadura;
o preenchimento não, porque o cinza da armadura não encosta na borda.

| Opção | Para quê |
|---|---|
| `--tolerancia` (30) | Quanto a cor pode se afastar do fundo e ainda contar como fundo |
| `--sombra` | Remove também a sombra projetada cinza — veja abaixo |
| `--margem` (8) | Folga em px ao aparar; `--sem-recorte` mantém o enquadramento |
| `--sem-suavizar` | Não graduar o alpha na borda |
| `--forcar` | Recortar mesmo que já haja alpha |

**A sombra projetada** é o caso que mais dá trabalho: ela é cinza, está longe do branco e
sobrevive ao preenchimento normal como um borrão opaco, com halo branco em volta.
`--sombra` roda um segundo preenchimento que anda só por pixel **dessaturado e claro**.
Funciona porque, nesse estilo de arte, a figura tem **contorno preto** e a sombra não: o
preenchimento come a sombra e para na tinta do contorno. É o que protege até uma ponta de
lança cinza encostada no fundo. Se a arte não tiver contorno marcado, não use — vai
vazar.

Confira o resultado: o script imprime quanto removeu e avisa em dois extremos (acima de
92%, vazou para dentro da figura; abaixo de 10%, o fundo não era uniforme). **Olhe a
imagem depois**, de preferência composta sobre um fundo colorido — halo branco e sombra
sobrevivente só aparecem assim, nunca sobre o xadrez de transparência.

Fundo que não é uniforme (cena, textura, degradê) não sai com este script. Diga isso ao
usuário em vez de entregar um recorte ruim.

## 4. Orientar para o sul

**Todo token do acervo encara o sul.** Sul é a **borda de baixo da imagem**: rosto, peito
e a arma empunhada à frente apontam para lá. Um acervo com direções misturadas obriga o
Mestre a girar token por token na hora da partida — padronizar uma vez resolve para
sempre, e a partir daí girar um token na mesa passa a significar de fato "o personagem
virou".

**Olhe cada token e decida para onde ele olha.** Não existe script que faça isso: é
julgamento visual. Use nesta ordem, que é a mais confiável:

1. **O rosto**, quando aparece — a direção do queixo e do nariz.
2. **Os ombros e o peito**, que costumam ser perpendiculares ao olhar.
3. **A ponta dos pés.**
4. **A arma empunhada à frente** e o escudo (que fica do lado, não à frente).

Se a figura estiver perfeitamente a pino e só se vir o alto da cabeça, use os ombros e os
pés. Cabelo comprido ou capuz caindo para trás também denunciam a direção.

Estime o ângulo em graus e corrija:

```
python .claude/skills/token-organizator/scripts/orientar.py \
  --imagem tokens/<nome>.png --girar 45
```

`--girar` é em graus, **positivo = sentido horário**. Sem `--girar`, o script só relata o
enquadramento e não escreve nada. Ele gira com o canto expandido (não corta membro
nenhum), reapara a sobra transparente e grava por cima, salvo `--saida`.

Quanto girar, para as direções comuns:

| A figura olha para | `--girar` |
|---|---|
| Sul (base) | 0 — já está certo |
| Sudoeste | 45 |
| Oeste (esquerda) | 90 |
| Noroeste | 135 |
| Norte (topo) | 180 |
| Nordeste | 225 |
| Leste (direita) | 270 |
| Sudeste | 315 |

**Confira depois de girar.** Estimativa de ângulo erra fácil em 15 ou 20 graus, e o erro
só aparece olhando o resultado. Uma segunda passada com o ajuste fino é normal.

Duas ressalvas:

- **Rotação gira a sombra junto.** Um token com sombra projetada marcada passa a ter a luz
  vindo do lado errado, o que fica visível quando ele está ao lado de outro token não
  girado. Em token com sombra forte, tire a sombra antes (`remover_fundo.py --sombra`) e
  aí gire à vontade.
- **Cada rotação reamostra a imagem.** Gire uma vez, a partir do original — não vá
  ajustando de 10 em 10 graus sobre o resultado anterior, que borra o traço. Se errou,
  volte ao arquivo de origem e gire de novo com o ângulo certo.

Ângulo múltiplo de 90 não perde qualidade nenhuma; os demais perdem um pouco, e por isso
não vale girar um token que já esteja aceitavelmente no sul só para ganhar 5 graus.

## 5. Nomear

Nome em **kebab-case descrevendo o que se vê**, não o hash nem o nome original do
download: `guerreiro-lanca-e-escudo.png`, `orc-machado-duas-maos.png`,
`lobo-cinzento.png`, `esqueleto-arco.png`. Hash e `IMG_20240113_004.png` são inúteis na
hora de procurar um token no meio de cem.

Comece pelo **que a criatura é**, depois o traço que a distingue das outras do mesmo
tipo — assim os parentes ficam juntos em ordem alfabética (`orc-arqueiro`,
`orc-machado`, `orc-xama`).

## 6. Catalogar

Acrescente a entrada em `tokens/tokens.json`:

```json
{
  "arquivo": "guerreiro-lanca-e-escudo.png",
  "descricao": "Guerreiro humano de cota de malha, lança curta e escudo redondo",
  "categoria": "Humanoides",
  "tags": ["humano", "guerreiro", "lança", "escudo", "medieval"],
  "origem": "https://... ou 'pacote X' ou 'gerado pela skill token-hex-gurps'",
  "girado": 45,
  "notas": "o que foi feito no recorte, licença, o que mais valha lembrar"
}
```

`girado` guarda quantos graus foram aplicados para levar a figura ao sul (0 se já estava
certa). Serve para saber, depois, que aquele arquivo não é mais o original — e quanto foi
girado, caso apareça o original de novo.

Categorias sugeridas, para o catálogo não virar uma lista solta: `Personagens` (os PJs da
mesa), `Humanoides`, `Bestas`, `Mortos-vivos`, `Elementais e espíritos`, `Objetos e
marcadores`.

Depois regere o catálogo:

```
python .claude/skills/token-organizator/scripts/catalogar.py
```

Ele reescreve `tokens/CATALOGO.md` agrupado por categoria. **As dimensões são lidas dos
arquivos, nunca copiadas do JSON** — assim o catálogo não passa a mentir depois que
alguém redimensiona um token na mão. E ele aponta os dois desencontros possíveis:
arquivo em `tokens/` que ninguém catalogou, e entrada no JSON apontando para arquivo que
já não existe. **Não edite o `CATALOGO.md` à mão**: edite o JSON e rode de novo.

## Uso do material

A arte costuma ser de terceiros. Isto aqui é uma mesa de RPG doméstica: guardar token
para usar na própria partida é uso pessoal, e é para isso que a skill existe. Mantenha o
campo `origem` preenchido em cada entrada — é o que evita a dúvida de seis meses depois
sobre de onde veio aquela arte, e o que permite dar crédito. Não transforme o acervo em
redistribuição.

## Depois

O token sai com fundo transparente e proporção livre. Para colar num mapa, use a skill
`atualizar-mapa`: ela lê o índice JSON da `add-grid-hex` e escala o token para um
hexágono (1 m).

Para **gerar** um token novo a partir de uma ficha do projeto, em vez de importar um
pronto, use a skill `token-hex-gurps` — e depois catalogue o resultado por aqui, com
`origem` dizendo que foi gerado.
