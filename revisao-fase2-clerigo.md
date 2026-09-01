# Fase 2f — Clérigo (cap. 3, p. 81–89)

Validador: **0 erros, 0 avisos**. JSON Schema: todos passam.

## O que saiu

| coleção | antes | agora |
|---|---|---|
| `classes.json` | 5 | **6** |
| `caracteristicas.json` | 165 | **194** |
| `subclasses.json` | 20 | **24** |
| `magias.json` | 331 | **368** |

**Lista de magias do Clérigo completa: 117.** Catálogos novos: `ordens_divinas` (2),
`efeitos_de_canalizar_divindade` (2 da classe, expansível por subclasse),
`opcoes_de_golpes_abencoados` (2).

**Contagens para conferir:** d8 · salvaguardas Sabedoria e Carisma · subclasse em **3, 6 e 17** (só
três níveis, diferente de todas as classes anteriores) · Canalizar Divindade 2/3/4 · lista com
**9/15/17/21/10/15/11/9/5/5** do círculo 0 ao 9.

## O Iniciado em Magia está completo

Com o Clérigo, as **três listas** que o talento oferece estão preenchidas:

```
clerigo :  9 truques, 15 magias de 1º círculo
druida  : 13 truques, 18 magias de 1º círculo
mago    : 20 truques, 31 magias de 1º círculo
```

Seu bárbaro com Iniciado em Magia agora tem seletor funcionando nas três, sem eu ter tocado no
talento desde que o escrevi.

## Canalizar Divindade

Modelei como um recurso da classe alimentando **efeitos de um catálogo expansível**. A classe entra
com Centelha Divina e Expulsar Mortos-Vivos; cada domínio acrescenta os seus (Ataque Direcionado,
Invocar Duplicidade, Brilho do Amanhecer, Preservar a Vida). O catálogo é marcado
`expansivel_por_subclasse`, então o app monta a lista de opções somando classe + subclasse, sem saber
que existe um Domínio da Guerra.

O validador ganhou a checagem correspondente: toda opção base de Canalizar Divindade precisa existir
no catálogo declarado. Testei com um efeito fantasma — pegou.

## Três divergências do livro, todas encontradas pelo dado

Nenhuma delas eu teria visto lendo; foram o validador e a checagem cruzada que apontaram.

**1. "Mãos Ardentes" não existe.** A tabela Magias de Domínio da Luz (p. 87) lista *Mãos Ardentes*.
Procurei no capítulo 7 inteiro: **não há essa magia**. A que existe é **Mãos Flamejantes** (1º
círculo, Evocação, p. 303), que é a mesma coisa. Apontei a tabela para o id correto e registrei
"Mãos Ardentes" em `nomes_alternativos` da magia, para busca.

**2. Manto do Cruzado não é magia de Clérigo.** A tabela do Domínio da Guerra a concede no nível 5,
mas a entrada (p. 302) diz **Paladino**. Mesmo caso do Invocar Fera no Ilusionista: acesso concedido
pela subclasse. Adicionei ao catálogo com a lista de origem certa e nota.

**3. "Remeter" tem duas escolas diferentes no mesmo livro.** A lista do Clérigo (p. 84) diz
**Evocação**; a entrada do capítulo 7 (p. 326) e a lista do Mago (p. 151) dizem **Adivinhação**.
Mantive Adivinhação, que é o que a entrada da própria magia declara, com nota registrando a
divergência.

Vale reparar que a **checagem cruzada** que criei no lote do Druida — comparar cada lista parseada
contra o catálogo, conferindo círculo, escola e pertencimento — foi exatamente o que pegou o caso do
Remeter. Sem ela, o Clérigo teria entrado com uma escola errada e ninguém notaria.

## O parser ganhou um scanner de múltiplas colunas

A lista do Clérigo tem páginas em que **duas ou três colunas caem na mesma linha extraída**
("Infligir Ferimentos Necromancia — Palavra Curativa Abjuração — Perdição Encantamento C"). O parser
antigo casava uma magia por linha e perdia as demais — os truques e o 1º círculo inteiros estavam
sumindo.

Reescrevi para **varrer cada linha procurando todos os pares (escola, marcador)**, tomando como nome
o texto desde o fim do par anterior. Reprocessei Mago, Bruxo e Druida com o scanner novo: **os três
devolveram exatamente os mesmos números**. A checagem cruzada das quatro listas contra o catálogo
ficou limpa depois de resolvido o Remeter.

## Estado geral

```
6 classes · 24 subclasses · 194 características · 42 catálogos · 66 tipos de efeito
368 magias — listas de Mago (242), Bruxo (91), Druida (135) e Clérigo (117) completas
```

Quatro das oito listas de magia estão preenchidas. Faltam bardo, feiticeiro, guardião e paladino.

## Próximo passo

Faltam seis classes: **Bárbaro** (p. 51), **Bardo** (p. 59), **Feiticeiro** (p. 103), **Guardião**
(p. 117), **Ladino** (p. 137) e **Paladino** (p. 167).

O **Bardo** é o mais interessante do que resta pelo lado do esquema — Segredos Mágicos é o acesso a
listas alheias em escala, e ele traz mais uma lista completa. O **Bárbaro** e o **Ladino** são os
únicos sem conjuração nenhuma, então seriam lotes rápidos que testam outra parte do modelo (Fúria,
Ataque Furtivo).

As pendências seguem registradas em `PENDENCIAS.md` — criaturas adiadas, capítulos 5 e 6, e o
pente-fino no glossário.
