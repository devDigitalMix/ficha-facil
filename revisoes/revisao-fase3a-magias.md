# Fase 3a — Capítulo 7, primeiro terço das magias (p. 239–343)

Validador: **0 erros, 0 avisos**. JSON Schema: todos passam. Teste negativo: **18 defeitos
plantados, 18 pegos**.

## O que saiu

| | antes | agora |
|---|---|---|
| magias no catálogo | 367 | **391** |
| magias detalhadas | 0 | **130** |
| listas de magia preenchidas | 4 de 8 | **8 de 8** |

**391 é o número certo:** o capítulo 7 tem exatamente 391 entradas, e o catálogo agora tem uma
magia para cada uma. Nem sobra nem falta.

## O que cada magia detalhada tem

Cada uma das 130 traz, direto da entrada do livro:

- **tempo de conjuração** — tipo (ação, Ação Bônus, reação, tempo), se é Ritual, e o gatilho quando
  é reação;
- **alcance** — tipo (pessoal, toque, distância, à vista, ilimitado) e a distância **em metros como
  número**, não como texto;
- **componentes** — V, S, M separados, com a descrição do material, o **custo em PO** quando há
  (25 das 130) e se ele é consumido;
- **duração** — tipo, se exige Concentração, e o tempo **em minutos como número**;
- **descrição curta** — o que a magia faz, escrita por mim em paráfrase.

E, quando o texto deixa claro, também: **dano** (dado + tipo + bônus fixo), **salvaguarda**
(atributo e se sucesso dá metade), **área** (forma, medida e metros), **ataque mágico** (corpo a
corpo ou à distância), **cura**, **condições citadas** e o **aprimoramento** (de truque ou por
espaço superior).

**Contagens para você conferir:** por círculo, do 0 ao 9 — **9/23/22/15/13/22/13/3/6/4**. Dentro
delas: 35 com dano, 57 com salvaguarda, 26 com área, 4 com cura, 3 com ataque mágico, 50 com
Concentração, 12 rituais, 56 com aprimoramento, 69 com componente material específico.

O terço vai de **Acalmar Emoções** a **Duelo Compelido**, em ordem alfabética. A próxima começa em
Elementalismo.

## Sobre a descrição: eu escrevi, não copiei

Combinamos que o texto do livro não é copiado em bloco. As 130 descrições são **paráfrases minhas**,
escritas depois de ler cada entrada — curtas, com os números que o jogador precisa na mesa. Os
campos estruturados (alcance, duração, dano, salvaguarda) são fatos da tabela e esses sim vêm
literais, porque um número não tem como ser parafraseado.

Se em alguma delas você achar que faltou informação para jogar, me diga qual — é o tipo de ajuste
que quero fazer nas primeiras 130 antes de escrever as outras 261 no mesmo molde.

## As quatro listas que faltavam vieram de graça

A entrada de cada magia no capítulo 7 declara **todas** as classes que a têm. Isso preencheu
sozinho as listas que faltavam:

```
mago 242 · feiticeiro 150 · bardo 140 · druida 135 · clerigo 117 · bruxo 91 · guardiao 61 · paladino 51
```

Não aceitei isso de cara: conferi cada uma das quatro novas contra a **tabela de lista da própria
classe** no capítulo 3. Bateram. As poucas diferenças que apareceram no primeiro cruzamento eram
falhas do meu conferidor (linhas de tabela grudadas em número de página e cabeçalho), não do dado —
fui checar magia por magia no PDF e todas estavam lá.

Isso destrava o **Segredos Mágicos do Bardo** antes mesmo de eu extrair o Bardo, e fecha a pendência
das listas incompletas.

## Quatro divergências do livro

**1 e 2. Escola diferente entre a lista de classe e a entrada da magia.** *Consagrar* aparece como
Evocação na lista do Clérigo (p. 84) e como **Abjuração** na entrada (p. 264). *Esfera Flamejante* é
Evocação nas listas de Druida (p. 95) e Mago (p. 150) e **Invocação** na entrada (p. 279). Vale a
entrada, como fizemos no Remeter, com nota nas duas.

**3. Uma magia estava duplicada no catálogo desde antes deste lote.** A lista do Bruxo (p. 74)
escreve *Tempestade Radiante de **Jallarzi***; a do Mago (p. 152) escreve ***Jallazar***. Eram duas
entradas para a mesma magia, e a diferença de grafia escondeu isso da checagem antiga. A entrada do
capítulo 7 (p. 342) diz Jallarzi — fundi as duas nessa, somando as listas e guardando a outra
grafia em `nomes_alternativos`.

**4. Um erro de tipografia no próprio livro.** *Animar Mortos* (p. 244) imprime o círculo com **`3°`
(sinal de grau)** em vez de `3º` (ordinal), única em 391 entradas. O parser não a enxergava. Aceita
os dois agora.

## O parser e o que ele ensinou

Escrevi `parse_magias.py` para ler as entradas, e ele nasceu com **seis defeitos que os spot-checks
pegaram** — anoto porque valem para os próximos dois terços:

1. **Componente material cortado na quebra de linha.** *Bola de Fogo* entrava com "M (uma bola de
   guano de morcego e" — parêntese aberto. Agora o campo continua até fechar.
2. **Custo em PO não lido**, porque o livro escreve "no valor de 1.000 **ou mais** PO" e o número não
   encosta no "PO". Eram 66 magias sem custo; hoje o custo entra com a marca de que é mínimo.
3. **Dano com bônus fixo no meio** — *Mísseis Mágicos* causa "1d4 + 1 pontos de dano Energético", e o
   "+ 1" quebrava o reconhecimento.
4. **Cura escrita ao contrário** — *Curar Ferimentos* diz "recupera Pontos de Vida igual a 2d8", não
   "2d8 Pontos de Vida".
5. **Duração colada no começo do corpo** — *Augúrio* entrou com duração "InstantâneaVocê recebe um
   presságio…". Onze magias tinham isso.
6. **Nome de magia que termina com o nome de outra.** *Flecha Relâmpago* casava com *Relâmpago* e
   sobrescrevia a escola e a lista dela. A regra agora só procura nome conhecido quando o nome está
   de fato **colado** no fim do parágrafo anterior.

Também tirei os **créditos de artista em caixa alta** que o PDF joga no meio das colunas, e cada
magia agora aponta para a **página da própria entrada**, não para a página da tabela de lista de
onde o nome tinha saído.

## O validador ficou responsável pelas magias

Antes ele conferia magia só como referência: existe ou não existe. Agora, para toda magia marcada
`detalhada`:

- **campo obrigatório ausente** é erro — descrição, tempo de conjuração, alcance, componentes,
  duração;
- **nome duplicado depois de normalizar** acento, caixa e pontuação é erro (foi essa checagem que
  desenterrou o Jallarzi/Jallazar);
- **tempo de conjuração, alcance, duração e forma de área** precisam ser de um tipo conhecido;
- alcance do tipo distância **precisa ter a distância em metros**;
- **concentração e ritual** precisam bater entre o campo da magia e o campo dentro da duração — dois
  lugares dizendo a mesma coisa é onde o dado costuma mentir;
- **tipo de dano, atributo de salvaguarda, escola, círculo (0–9), lista de classe e condição citada**
  precisam existir nos catálogos;
- fórmula de dado precisa ter a forma `NdN`;
- magia sem nenhum componente (V, S ou M) é erro;
- a **contagem de detalhadas** declarada no catálogo precisa bater com a real.

Plantei 18 defeitos, um para cada regra. Pegou os 18.

## Estado geral

```
8 classes · 32 subclasses · 265 características · 47 catálogos · 69 tipos de efeito
391 magias, 130 detalhadas · 8 de 8 listas de magia preenchidas
```

## Próximo passo

Faltam **261 magias** para detalhar, de Elementalismo em diante. O parser e o validador já estão
prontos; o trabalho por lote é ler as entradas e escrever as descrições. Sugiro o segundo terço
(mais 130) no próximo lote.

Continuam de pé: as quatro classes que faltam (Bardo, Feiticeiro, Guardião, Paladino), o capítulo 6
(equipamento), os capítulos 4 e 5, e o pente-fino no glossário.
