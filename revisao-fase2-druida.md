# Fase 2e — Druida (cap. 3, p. 91–101)

Validador: **0 erros, 1 aviso** (a Forma Selvagem, explicada abaixo). JSON Schema: todos passam.

## O que saiu

| coleção | antes | agora |
|---|---|---|
| `classes.json` | 4 | **5** |
| `caracteristicas.json` | 134 | **165** |
| `subclasses.json` | 16 | **20** |
| `magias.json` | 271 | **331** |

**Lista de magias do Druida completa: 135.** Catálogos novos: `constelacoes` (3),
`terrenos_druidicos` (4), `ordens_primais` (2), `opcoes_de_furia_elemental` (2), `criaturas` (vazio).

**Contagens para conferir:** d8 · salvaguardas Inteligência e Sabedoria · subclasse em **3, 6, 10,
14** · Forma Selvagem 2/3/4 usos · lista com **13/18/23/17/21/15/10/6/8/4** do círculo 0 ao 9.

O Druida também confirma o que eu tinha te dito sobre preparação: ele é o caso **direto da lista sem
teto** — `fonte_das_magias: "lista_de_classe"`, sem livro, e trocando **quantas quiser** a cada
Descanso Longo (p. 92). Os três modos anteriores (livro do Mago, lista com círculo por espaços do
Cavaleiro Místico, lista com teto de Pacto do Bruxo) agora têm o quarto para comparar.

## Forma Selvagem

A característica virou um efeito próprio com três partes:

- **a tabela Formas de Feras** (nível 2: 4 formas, ND ¼, sem voo → nível 4: 6 formas, ND ½ → nível 8:
  8 formas, ND 1, com voo);
- **as regras enquanto multimorfado**, como dado e não como texto: o que você mantém (personalidade,
  memórias, fala, tipo de criatura, PV, Dados de Vida, INT/SAB/CAR, características de classe,
  idiomas, talentos, proficiências), o que é substituído, os PV temporários iguais ao nível, a
  proibição de conjurar e o que acontece com o equipamento;
- **a escolha das formas conhecidas**, reescolhível a cada Descanso Longo.

O Círculo da Lua entra por cima com `melhorar_caracteristica`, mudando ND máximo, CA e PV temporários
sem duplicar nada.

### O aviso: a Forma Selvagem escolhe de um catálogo vazio

As formas são blocos de estatísticas de **Fera do Apêndice B**, que ficou fora do escopo lá na Fase 0.
Criei o catálogo `criaturas` **declarado e vazio**, com `preenchida: false` e uma nota explicando por
quê. O filtro da escolha está escrito por inteiro (tipo Fera, ND máximo pela tabela, com ou sem voo),
então **o dado já está pronto** — se você decidir extrair as Feras de ND ≤ 1 do Apêndice B, o seletor
passa a funcionar sem eu reeditar o Druida.

Enquanto isso o validador emite **aviso, não erro**: é pendência conhecida. Testei o outro lado
também — marquei o catálogo como `preenchida: true` mantendo-o vazio, e aí ele vira **erro**, que é o
comportamento certo para um catálogo que mente sobre si mesmo.

**Decisão sua:** vale extrair as Feras de ND até 1 do Apêndice B só para alimentar a Forma Selvagem?
É um recorte pequeno de algo que combinamos deixar de fora.

## Um bug no parser que o próprio dado denunciou

Ao mesclar a lista do Druida, o catálogo discordou de si mesmo: **Visão no Escuro** aparecia como 2º
círculo (vindo da lista do Mago) e como 3º (vindo da lista do Druida). Fui conferir no capítulo 7
(p. 342): **é 2º círculo**.

A causa: na lista do Druida, o cabeçalho "Magias de Druida de 3º Círculo" vem **colado no fim da
linha da última magia do 2º círculo**, por causa da quebra de coluna. O parser via o cabeçalho, virava
o círculo, e só então processava a magia — jogando-a para o círculo errado.

Corrigi o parser para processar o que vem **antes** do cabeçalho ainda no círculo anterior. Reprocessei
as três listas: Mago e Bruxo ficaram idênticos (o bug só mordia quando a colagem acontecia), e o
Druida corrigiu para 2:23 / 3:17.

Também escrevi uma checagem cruzada que compara as três listas parseadas contra o catálogo,
conferindo círculo, escola e pertencimento de cada magia: **nenhuma divergência**. É essa checagem
que pegou o problema, e ela vale para todas as listas que vierem.

## Quatro tipos de efeito novos

`forma_selvagem` · `converter_recurso` (Ressurgimento Selvagem e Arquidruida trocam usos de Forma
Selvagem por espaços de magia e vice-versa) · `emanacao` (a Ira do Mar) · `tratar_resultado_minimo`
(a constelação do Dragão, que trata 9 ou menos como 10).

Catálogo em **65 tipos**.

## Duas checagens novas no validador

- **Magias dentro de tabelas de círculo/patrono** agora são conferidas contra o catálogo. Isso valeu
  retroativamente para as tabelas do Bruxo e do Mago, que passaram.
- **`alterar_dano` com tipo derivado**: a Proteção Natural muda a Resistência conforme o terreno
  escolhido, então não tem um tipo literal. Em vez de aceitar um valor solto, o dado declara
  `tipo_dano_derivado` com o mapa terreno → dano, e o validador confere **cada valor do mapa**.
  Testei com um dano fantasma no mapa — pegou.

## Estado geral

```
5 classes · 20 subclasses · 165 características · 39 catálogos · 65 tipos de efeito
331 magias — listas do Mago (242), Bruxo (91) e Druida (135) completas
```

Com a lista do Druida preenchida, o **Iniciado em Magia** agora oferece duas das três listas que ele
permite escolher. Falta o Clérigo.

## Próximo passo

**Clérigo** (p. 81) fecharia o Iniciado em Magia por completo e traz Canalizar Divindade. Ou o
**Bardo** (p. 59), com Segredos Mágicos — o acesso a listas alheias que a gente discutiu.

Continua de pé: o pente-fino no glossário atrás de termos sem marcador, e as quatro dúvidas de
equipamento inicial que só o capítulo 6 resolve.
