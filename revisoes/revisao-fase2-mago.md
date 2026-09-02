# Fase 2c — Mago (cap. 3, p. 147–157)

Validador: **0 erros, 0 avisos**. JSON Schema: todos os arquivos passam.

Você tinha razão: o Mago acrescentou bastante. Foi o maior lote até agora.

## O que saiu

| coleção | antes | agora |
|---|---|---|
| `classes.json` | 2 | **3** (Monge, Guerreiro, Mago) |
| `caracteristicas.json` | 78 | **105** (28 do Mago) |
| `subclasses.json` | 8 | **12** |
| `magias.json` | 9 | **243** |

**A lista de magias do Mago está completa: 242 magias**, cada uma com círculo, escola e os marcadores
C (Concentração), R (Ritual) e M (componente Material específico).

Contagens por círculo, para você bater no livro:

| círculo | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| magias | 20 | 31 | 39 | 32 | 29 | 29 | 22 | 15 | 13 | 12 |

Por escola: Transmutação 42 · Evocação 40 · Invocação 39 · Abjuração 27 · Ilusão 28 ·
Encantamento 23 · Adivinhação 22 · Necromancia 21.

**A pendência do Cavaleiro Místico fechou.** Ele já apontava para `listas_de_magia/mago` por filtro;
a lista agora está `"preenchida": true` e a escolha dele funciona sem eu ter tocado no dado do
Guerreiro. Era exatamente o que a modelagem por filtro prometia.

### A lista não foi transcrita à mão

Escrevi um **parser** (`parse_lista_mago.py`) que lê as páginas 150–153 direto do PDF e monta as 242
entradas. Transcrever 242 nomes e escolas na mão era garantia de erro. O parser imprime tudo que não
casa com o padrão em vez de descartar em silêncio — foi assim que peguei dois nomes que a quebra de
coluna do PDF tinha partido ("Tempestade Radiante de Jallazar" e "Santuário Particular de
Mordenkainen"). Rodei também uma checagem de ids duplicados e de nomes suspeitos: zero duplicados, e
os únicos nomes curtos são "Luz" e "Voo", que são assim mesmo.

O texto completo de cada magia — alcance, duração, componentes, efeitos — vem na fase do capítulo 7.
Por ora cada entrada tem o que a lista de classe fornece.

## Precisa da sua decisão

### Nove tipos de efeito novos (v1.3)

O Mago tem mecânicas que nenhuma classe anterior tinha:

`livro_de_magias` · `conjurar_como_ritual` · `recuperar_espacos_de_magia` ·
`adicionar_magia_ao_livro` · `conjurar_sem_espaco` · `trocar_magia_preparada` · `barreira_de_dano` ·
`substituir_resultado_de_d20` · `dano_maximizado`

Dois merecem comentário:

- **`livro_de_magias`** — é a diferença real entre o Mago e os outros conjuradores. Guarda capacidade
  (100 páginas), as seis magias iniciais, o ganho de duas por nível e as regras de cópia (2 h e 50 PO
  por círculo para uma magia nova; 1 h e 10 PO para copiar do próprio livro). O `preparar_magias` do
  Mago aponta para o livro como fonte, não para a lista da classe — que é o que o distingue do
  Clérigo e do Druida, que preparam direto da lista.
- **`barreira_de_dano`** — a Proteção Arcana do Abjurador não é PV temporário: é uma reserva separada
  com PV próprios, que absorve dano antes de você, aplica Resistência e Vulnerabilidade antes de
  descontar, e continua existindo em 0 sem absorver mais nada. Ia ficar torto forçando em
  `pontos_de_vida_temporarios`.

O catálogo está com **57 tipos** no total.

## O que o validador pegou desta vez

**Prodígio Maior estava modelado errado.** Eu tinha dobrado o nível 14 do Adivinhador dentro do
Prodígio, como fiz com Indomável no Guerreiro. O validador reclamou que o Adivinhador não tinha
característica no nível 14 — que é um nível marcado de subclasse. Separei em característica própria
que usa `melhorar_caracteristica`.

Isso me deu a regra que faltava, e vale daqui pra frente: **se o livro dá um título próprio à
melhoria ("Nível 14: Prodígio Maior"), ela é característica separada; se a melhoria está no meio do
texto da característica original (como o "a partir do nível 13" do Indomável), ela é nível repetido.**
Antes eu decidia caso a caso.

**O validador ficou mais rigoroso:** agora confere que toda magia citada em `desbloquear_magias`,
`conjurar_sem_espaco` e `preparar_magias` existe no catálogo, e que a lista referenciada existe —
mas só quando a lista é a *fonte* das magias, não quando o efeito já nomeia quais são.

## Uma coisa estranha no livro

**Criaturas Espectrais (Ilusionista, nível 6) cita "Invocar Fera", que não está na lista do Mago.**
Conferi: Invocar Fera está no capítulo 7 (p. 294) como magia de **Druida e Guardião**. A subclasse
diz "Você sempre tem as magias Convocar Feérico e Invocar Fera preparadas" — Convocar Feérico está na
lista do Mago (3º círculo), Invocar Fera não está.

A leitura mais provável é que a subclasse concede acesso a ela, como fazem várias subclasses do
livro. Coloquei Invocar Fera no catálogo com `listas: ["druida", "guardiao"]` e uma nota dizendo por
que ela está lá, e marquei a característica como `duvida`. **Se você concordar que é acesso concedido
pela subclasse, eu fecho a dúvida.**

## Verificação

Simulei um Mago nível 10 Evocador: características de classe e de subclasse nos lugares certos,
5 truques, 15 magias preparadas, espaços 4/3/3/3/2. Teste negativo com magia fantasma, lista fantasma
e progressão truncada: pegou os três.

## Estado geral

```
3 classes · 12 subclasses · 105 características · 31 catálogos · 57 tipos de efeito
243 magias (lista do Mago completa)
```

## Próximo passo

O **Bruxo** (p. 69) continua sendo o teste mais duro que resta para a conjuração — espaços de Pacto
recarregam em Descanso Curto e sobem de círculo todos juntos, o que não cabe na tabela de conjurador
pleno nem na parcial. Se ele passar, o modelo de conjuração aguenta o livro inteiro.

Alternativa: o **Clérigo** ou o **Druida**, que preparam magias direto da lista (sem livro) e
testariam o outro modo de preparação — mais rápido, e cada um traz sua lista completa.
