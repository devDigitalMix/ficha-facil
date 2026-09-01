# Pendências do dataset — Ficha Fácil

Registro vivo do que ficou de fora de propósito, do que depende de capítulo futuro e do que depende
de decisão sua. Atualizado a cada lote.

Última atualização: **2026-09-01**, após o Druida.

---

## 1. Criaturas e blocos de estatísticas — adiado por decisão

**Decisão (2026-09-01):** criaturas ficam fora do escopo por enquanto.

**O que isso afeta hoje**

| onde | o que acontece |
|---|---|
| Druida — Forma Selvagem | O app **não oferece seletor de formas**. Ao subir de nível ele apenas informa quantas formas o personagem conhece, o ND máximo e se já pode voar. O jogador escolhe as Feras fora do app. |
| Bruxo — Pacto da Corrente | As formas especiais de familiar (Diabrete, Pseudodragão, Quasit, Sprite…) estão citadas como texto, sem bloco de estatísticas. |
| Ap. B inteiro | Não extraído. |

**Como está preparado para o futuro.** O catálogo `dados/catalogos/criaturas.json` existe, declarado
vazio com `"preenchida": false`. A escolha da Forma Selvagem já tem o **filtro completo** escrito —
tipo Fera, ND máximo lido da tabela Formas de Feras, com ou sem Deslocamento de Voo — e está marcada
`"resolucao": "manual"` e `"pendente": true`.

**Quando revisitarmos:** basta extrair as Feras do Apêndice B (o recorte mínimo é **ND ≤ 1**, que
cobre a Forma Selvagem até o nível 20 do Druida base; o Círculo da Lua vai além, com ND igual ao
nível de Druida ÷ 3). Preenchido o catálogo e trocado `preenchida` para `true`, o seletor passa a
funcionar **sem reeditar o Druida**. O validador cobra a coerência sozinho: catálogo vazio dizendo-se
preenchido vira erro.

**Texto que o app mostra ao subir de nível** (campo `aviso_ao_subir_de_nivel`):

> Você conhece {formas_conhecidas} formas Animais, de Nível de Desafio até {nd_maximo}{voo}.
> Escolha-as entre os blocos de estatísticas de Fera do Apêndice B ou do Livro dos Monstros, com o
> aval do Mestre.

---

## 2. Depende do capítulo 6 (Equipamento)

- **`equipamento_inicial` das 5 classes** — marcado `revisao: duvida`. Os ids (`cota_de_malha`,
  `foice`, `kit_de_erudito`…) apontam para itens que ainda não existem.
- **Maestria em Arma (Guerreiro)** — escolhe do catálogo `itens`, hoje parcial com as 38 armas da
  tabela p. 215 (só nome, grupo e alcance).
- **Listas de "Fabricação" das ferramentas** — não extraídas; apontam para dezenas de itens do cap. 6.

Resolve sozinho quando o capítulo 6 entrar.

---

## 3. Depende dos capítulos 5 e 7

- **`talentos`** — parcial. Completo só na categoria Estilo de Luta (10). `iniciado_em_magia` foi
  extraído como exemplo trabalhado. Faltam as categorias Origem, Geral e Dádiva Épica (cap. 5).
- **`magias`** — 331 entradas, com as listas de **Mago (242), Bruxo (91) e Druida (135)** completas.
  Cada magia tem círculo, escola e os marcadores C/R/M; o texto completo (alcance, duração,
  componentes, efeitos) vem com o cap. 7.
- **`listas_de_magia`** — 3 de 8 preenchidas. Faltam bardo, clerigo, feiticeiro, guardiao, paladino.
  Enquanto uma lista está `preenchida: false`, filtros que apontam para ela geram **aviso**, não erro.

---

## 4. Fases adiadas

- **Multiclasse** — decisão da Fase 0. Os dados de multiclasse já vêm sendo gravados no campo
  `multiclasse` de cada classe (Guerreiro, Mago, Bruxo, Druida), então a fase será de regras, não de
  re-extração.
- **Apêndice A (Multiverso)** — fora do escopo.

---

## 5. A fazer, sem depender de ninguém

- **Pente-fino no glossário (Ap. C)** atrás de termos **sem marcador entre colchetes**. Na Fase 1 eu
  varri filtrando por [Condição], [Ação], [Risco] etc., e termos como **"Sangrando"** escaparam — só
  apareceu porque o Campeão do Guerreiro depende dele. Já recuperei Sangrando, Estável e Surpresa no
  catálogo `estados`; falta varrer o resto do glossário procurando os que ainda não foram
  referenciados por nenhuma classe.

---

## 6. Divergências do próprio livro, já resolvidas e registradas

Ficam aqui como histórico — todas com nota dentro do dado.

| onde | divergência | resolução |
|---|---|---|
| Monge, níveis 6 e 10 | tabela diz "Ataques Potencializados"/"Autocura"; título diz "Golpes Potencializados"/"Restauro Pessoal" | vale o título; nome da tabela guardado em `nome_na_tabela` |
| Monge, Passo da Sombra Aprimorado | redação ambígua sobre o requisito de luz | ruling seu: gastando 1 Ponto de Foco, os dois requisitos caem |
| Guerreiro, Gato Por Lebre | parágrafo do bônus de CA aparecia solto por quebra de coluna | é parte da manobra |
| Mago, Ilusionista | Criaturas Espectrais cita Invocar Fera, fora da lista do Mago | acesso concedido pela subclasse |
| Bruxo, patronos | "Magias Psíquicas" e "Mente Desperta" impressas sob o título do Ínfero | são do Grande Antigo |
| Bruxo, Fome de Hadar | escola grafada "Conjuração"; no resto do livro é "Invocação" | normalizado, com nota na magia |
| Druida, lista de magias | Visão no Escuro caía no 3º círculo por cabeçalho colado | corrigido no parser; é 2º círculo (cap. 7, p. 342) |
