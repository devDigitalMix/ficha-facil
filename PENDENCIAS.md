# Pendências do dataset — Ficha Fácil

Registro vivo do que ficou de fora de propósito, do que depende de capítulo futuro e do que depende
de decisão sua. Atualizado a cada lote.

Última atualização: **2026-09-01**, após o capítulo 7 completo e os quatro primitivos.

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

## 2. Capítulo 6 (Equipamento) — RESOLVIDO

Extraído em 2026-09-01. `itens` tem 170 entradas completas e `ferramentas` as 25 com atributo,
custo, teste de Usar Objeto e Fabricação. Fechou:

- **`equipamento_inicial` das 8 classes** — todos os ids resolvem, e o validador cobra isso.
- **Maestria em Arma (Guerreiro)** — escolhe do catálogo completo, com a maestria de cada arma.
- **Listas de Fabricação das ferramentas** — 87 itens resolvidos; os 11 restantes são descrições
  genéricas do próprio livro ("qualquer arma Corpo a Corpo", "Foco Arcano"), declaradas em
  `nao_resolvidos`.

Duas dúvidas abertas para você decidir:

- **"Aeronau"** (tabela de veículos, p. 230) parece "Aeronave" truncado. Mantive como impresso,
  com `revisao: duvida`.
- **"Kit de Explorador"** (Druida, p. 92) não existe no capítulo 6; lá só há "Kit de Explorador de
  Masmorras" (p. 226). Tratei como o mesmo kit; o `equipamento_inicial` do Druida está marcado
  como dúvida.

**Componentes materiais de magia:** o capítulo 6 ajuda menos do que parecia — das 69 magias
detalhadas com material, só 9 citam algo da tabela de equipamento. O que ele resolve é a regra da
p. 237: cada magia agora declara `substituivel_por_foco_ou_bolsa` (44 sim, 25 exigem o material).

## 3. Depende do capítulo 5

- **`talentos`** — parcial. Completo só na categoria Estilo de Luta (10). `iniciado_em_magia` foi
  extraído como exemplo trabalhado. Faltam as categorias Origem, Geral e Dádiva Épica (cap. 5).
  Os quatro talentos já citados pelas classes (Aumento no Valor de Atributo e os três de Dádiva
  Épica) estão declarados com `pendente: true` — o validador cobra essa marca, então stub sem
  efeitos e sem declaração vira erro.
- **Compreensão Superior** (Terceiro Olho, do Adivinhador, p. 155) — "ler qualquer idioma" não tem
  primitivo no esquema; está como `substituir_regra` com `revisao: duvida`. Provável que ganhe efeito
  próprio junto com os talentos do cap. 5.
- **`magias`** — **391 entradas, TODAS detalhadas.** Capítulo 7 fechado. Cada magia traz tempo de
  conjuração, alcance com metros, componentes com custo e se um foco substitui, duração com
  Concentração, dano, salvaguarda, área, condições citadas, aprimoramento, página e a descrição em
  paráfrase.
  Cada magia tem círculo, escola e os marcadores C/R/M; o texto completo (alcance, duração,
  componentes, efeitos) vem com o cap. 7.
- **`listas_de_magia`** — **8 de 8 preenchidas.** A entrada de cada magia no capítulo 7 declara as
  classes que a têm; cada lista nova foi conferida contra a tabela da própria classe no capítulo 3.
  mago 242 · feiticeiro 150 · bardo 140 · druida 135 · clerigo 117 · bruxo 91 · guardiao 61 ·
  paladino 51.
  Enquanto uma lista está `preenchida: false`, filtros que apontam para ela geram **aviso**, não erro.

---

## 4. Fases adiadas

- **Multiclasse** — decisão da Fase 0. Os dados de multiclasse já vêm sendo gravados no campo
  `multiclasse` de cada classe (Guerreiro, Mago, Bruxo, Druida), então a fase será de regras, não de
  re-extração.
- **Apêndice A (Multiverso)** — fora do escopo.

---

## 4b. Primitivos — RESOLVIDOS

Eu tinha listado quatro primitivos como se fossem trabalho do backend. Três eram declaração de
dado, e o quarto era metade e metade. Todos fechados em 2026-09-01:

| primitivo | onde vive |
|---|---|
| mãos ocupadas | `maos_ocupadas` em 49 itens; `maos_alternativas` nas armas Versáteis |
| consumo de munição | `consumo` em 9 armas, com id da munição e recuperação pós-combate |
| teto por ação | `limite_por_acao` em 6 armas com Recarga |
| cálculos de CA concorrentes | `concorre_como: calculo_de_ca_base` em 15 cálculos (armaduras e Defesas sem Armadura) |

As quatro propriedades saíram de `substituir_regra` para o tipo `declara_campo_no_item`, e o
validador cobra: item com a propriedade e sem o campo é erro.

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
| Clérigo, Domínio da Luz | tabela lista "Mãos Ardentes", magia inexistente | é Mãos Flamejantes (p. 303); nome guardado em `nomes_alternativos` |
| Clérigo, Domínio da Guerra | concede Manto do Cruzado, que a entrada declara de Paladino | acesso concedido pela subclasse |
| "Remeter" | Evocação na lista do Clérigo, Adivinhação na entrada e na lista do Mago | vale a entrada: Adivinhação |
| Consagrar | Evocação na lista do Clérigo (p. 84), Abjuração na entrada (p. 264) | vale a entrada: Abjuração |
| Esfera Flamejante | Evocação nas listas de Druida e Mago, Invocação na entrada (p. 279) | vale a entrada: Invocação |
| Tempestade Radiante | "Jallarzi" na lista do Bruxo e na entrada, "Jallazar" na do Mago | vale a entrada; as duas grafias tinham virado DUAS magias no catálogo, fundidas em uma |
| Animar Mortos | o círculo é impresso com `3°` (sinal de grau) em vez de `3º` | erro tipográfico do livro; o parser aceita os dois |
| Armaduras | a tabela diz "Couro"/"Couro Batido"; as classes dizem "Armadura de Couro"/"de Couro Batido" | mesmo item, com as duas formas em `nomes_alternativos` |
| Munição | a tabela de Armas diz "Flecha"/"Virote"; a de Munição vende "Flechas"/"Virotes", e "Bala" serve a duas linhas | resolvido pelo id real, decidindo pela arma |
| Veículos | a tabela imprime "Aeronau" (p. 230) | mantido como impresso, marcado como dúvida |
| Bárbaro, níveis 13 e 17 | tabela diz "Golpe Brutal Aprimorado"; títulos dizem "Fortalecido" | vale o título; duas seções tituladas ⇒ duas características (`_13` e `_17`) |
| Ladino, nível 1 | tabela diz "Especialização" e "Gíria dos Ladrões"; títulos dizem "Especialista" e "Gíria do Ladrão" | vale o título; nome da tabela em `nome_na_tabela` |

---

## 7. Conteúdo do livro que faltava e foi recuperado

| onde | o que faltava | quando |
|---|---|---|
| Druida, Círculo da Terra | as **4 tabelas de Magias de Círculo Druídico** (p. 98), 24 magias — o terreno escolhido não concedia magia nenhuma | varredura das opções |
| 11 catálogos de opção | 37 opções tinham só texto, sem efeitos executáveis | varredura das opções |
| catálogo de magias | 24 magias do cap. 7 nunca tinham entrado (as de Bardo, Feiticeiro, Guardião e Paladino) | fase 3a |
| catálogo de itens | o capítulo 6 inteiro, exceto as 38 armas sem detalhe | fase 4 |

---

## Fase 7 — Bardo e Feiticeiro (ver `revisao-fase7-bardo-feiticeiro.md`)

**Fechado nesta fase**

- Bardo (p. 59-67): 26 características, 4 colégios.
- Feiticeiro (p. 103-114): 29 características, 4 origens. Único até agora com característica de
  subclasse no **nível 18** — declarado em `niveis_de_caracteristica_de_subclasse`.
- Catálogos novos: `usos_da_inspiracao_de_bardo` (3), `opcoes_de_metamagia` (10),
  `alteracoes_da_revelacao_em_carne` (4), `manifestacoes_da_ordem` (6, vocabulário),
  `surtos_de_magia_selvagem` (25, com faixa de 1d100).
- Tipos de efeito novos (8): `alterar_tempo_de_conjuracao`, `alterar_alcance_da_magia`,
  `alterar_duracao_da_magia`, `alterar_circulo_efetivo`, `dispensar_concentracao`,
  `dissipar_magias`, `rolar_na_tabela`, `movimento_forcado`.
- `checar_schema.py` passou a ser script do projeto (era passo solto rodado de memória).
- Empurrões que eram `efeito_narrativo` migrados para `movimento_forcado` (Mão Espalmada do Monge,
  Ira do Mar do Druida).

**Corrigido de lotes anteriores**

- Colégios do Bardo sem `niveis_de_caracteristica` (o schema exige).
- Evasão Liderada (Colégio da Dança) com condição composta misturando `todas` e `nao` no mesmo
  objeto.
- `resolver_filtro` do validador ignorava filtro por campo booleano — filtro vazio passava batido.

**Aberto**

- Resiliência Dracônica: o bônus de PV máximos está gravado como a conta fechada
  (`nivel_classe:feiticeiro`) em vez de "3 + 1 por nível seguinte". Decisão sua se quer as duas
  parcelas separadas para o log de proveniência.
- 6 das 25 linhas do Surto de Magia Selvagem dependem de decisão do Mestre ou de subtabela
  aleatória, e trazem `efeito_narrativo` com os dados estruturados junto.

**Falta do livro**

- Classes: **Guardião** (p. 117) e **Paladino** (p. 167).
- **Capítulos 4 e 5**: origens, espécies, antecedentes e talentos.

---

## Fase 8 — Pontos de Vida (ver `revisao-fase8-pontos-de-vida.md`)

**Fechado nesta fase**

- `valores_derivados` 17 → 19: `pontos_de_vida_maximos` (com parcelas e as 4 regras do livro) e
  `pontos_de_vida_temporarios` (derivado próprio, com as 5 regras do cap. 1). PV **atuais** ficam
  no backend por decisão do usuário.
- `pontos_de_vida_no_nivel_1` e `pontos_de_vida_por_nivel` ganharam parcelas e a tabela Pontos de
  Vida Fixos por Classe (p. 42), com os números impressos.
- `alvos.json` declara `derivado_id`; 8 alvos ligados, e o validador cobra a promessa.
- 10 operações de fórmula declaradas em `valores_derivados.operacoes`.
- Forma Selvagem: PV temporários saíram de campo solto para efeito de verdade.
- 16 magias com bloco `pontos_de_vida` estruturado.

**Corrigido de lotes anteriores**

- **Parser cortava o fim de 55 magias** (nome da próxima colado na última frase). Custou: Moléstia
  sem 14d6, Palavra de Poder: Matar sem 12d12, Fonte do Luar sem Cego, Onda Destrutiva sem o
  "metade em caso de sucesso", 11 aprimoramentos truncados. Sobraram 12 corpos truncados, nenhum
  perdendo mecânica.
- Regex de dano não aceitava "14d6 de dano Necrótico" (sem "pontos").
- **Oito descrições minhas com regra de 2014 em vez de 2024**: Nevasca, Nuvem Fétida, Presença
  Régia de Yolande, Polimorfia, Sentido Feral, Moléstia, Muralha de Vento, Muralha Prismática.
  Todas corrigidas contra a página.
- `passo_revigorante` usava `formula_dado` onde o resto do dado usa `formula`.

**Aberto**

- `auditar_descricoes.py` só pega fatos verificáveis por termo (dados, salvaguarda, condições,
  distâncias). Inversão de "sucesso/falha" e erro de duração passam. **Proposta ao usuário: reler
  as 391 entradas contra a paráfrase, uma a uma.**
- Convocar Celestial dá 1d10 PV temporários, mas no bloco de estatísticas do Espírito Celestial —
  fora do escopo enquanto criaturas estiverem adiadas.

---

## Fase 9 — Capítulo 5, Talentos (ver `revisao-fase9-talentos.md`)

**Fechado nesta fase**

- **75 talentos**, quatro categorias completas: origem 10 · geral 43 · estilo de luta 10 ·
  dádiva épica 12. **Nenhum talento `pendente`.**
- As quatro pendências antigas: Aumento no Valor de Atributo, Dádiva da Proeza em Combate,
  Dádiva do Ataque Irresistível, e Dádiva Épica — que deixou de ser talento e virou a
  categoria `epico`; a característica de nível 19 escolhe dentro dela.
- 16 tipos de efeito novos, 3 alvos, 2 alvos de impedimento.
- 3 catálogos auxiliares: `modos_de_aumento_de_atributo`, `efeitos_do_ataque_em_investida`,
  `efeitos_do_golpe_de_escudo`.

**Corrigido de lotes anteriores**

- Combate com Armas Grandes e Combate com Duas Armas eram `efeito_narrativo`; viraram
  `tratar_dado_de_dano_minimo` e `modificador`.
- `gerar_guerreiro_catalogos.py` reescrevia o cabeçalho de `talentos.json` para PARCIAL e
  recriava um marcador pendente — rodado fora de ordem, desfazia o capítulo 5. Removido.
- **Furo no validador**: o andador pulava `efeito_por_item_escolhido`, então checagens por tipo
  não viam efeitos que moram ali (um `aumento_atributo` sem teto passou no teste negativo).
- `alterar_dano` não aceitava tipo de dano derivado (`mesmo_do_ataque`).
- Filtro por `escola`/`categoria`/`classe` não aceitava LISTA de valores — "Ilusão ou
  Necromancia" resolvia para vazio.

**Aberto**

- 11 efeitos de talento continuam `efeito_narrativo`: levantar-se de Caído por 1,5 m, salto com
  corrida curta, mimetismo do Ator, Saque Rápido, componentes Somáticos com mãos ocupadas, errar
  escondido sem revelar posição, Correr em Terreno Difícil, Socar e Imobilizar. Dependem de
  julgamento na mesa ou de primitivo que a base não tem. Marcados, não escondidos.
- "Aeronau": a legenda da p. 212 usa a palavra no mesmo sentido de "nave aérea" no texto ao lado
  — é escolha do tradutor, não truncamento. Continua sendo decisão do usuário se o app mostra.

**Falta do livro**

- Classes: **Guardião** (p. 117) e **Paladino** (p. 167).
- **Capítulo 4**: origens, espécies e antecedentes.
