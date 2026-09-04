# Pendências do dataset — Ficha Fácil

Registro vivo do que ficou de fora de propósito, do que depende de capítulo futuro e do que depende
de decisão sua. Atualizado a cada lote.

Última atualização: **2026-09-02**, após a auditoria e a rodada de conserto. Antes disso, o capítulo 4 — **o escopo do dataset está fechado**. O que
resta são as coisas adiadas de propósito, listadas abaixo.

---

## 1. Criaturas e blocos de estatísticas — adiado por decisão

**Decisão (2026-09-01):** criaturas ficam fora do escopo por enquanto.

**O que isso afeta hoje**

| onde                        | o que acontece                                                                                                                                                                                                                            |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Druida — Forma Selvagem     | O app **não oferece seletor de formas**. Ao subir de nível ele apenas informa quantas formas o personagem conhece, o ND máximo e se já pode voar. O jogador escolhe as Feras fora do app.                                                 |
| Bruxo — Pacto da Corrente   | As formas especiais de familiar (Diabrete, Pseudodragão, Quasit, Sprite…) estão citadas como texto, sem bloco de estatísticas.                                                                                                            |
| Guardião — Senhor das Feras | **Não afeta.** Os três blocos (Fera da Terra, do Céu e do Mar) são impressos no capítulo 3 e foram extraídos para o catálogo próprio `feras_companheiras`. Não são bestiário: derivam do nível e do modificador de Sabedoria do Guardião. |
| Ap. B inteiro               | Não extraído.                                                                                                                                                                                                                             |

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

## 3b. Capítulo 3 (Classes) — RESOLVIDO

Fechado em 2026-09-01 com o Guardião e o Paladino (ver `revisao-fase10-guardiao-paladino.md`).
**12 classes, 48 subclasses, 388 características.** Não sobrou classe do livro.

- As listas de magia das duas já estavam preenchidas desde o capítulo 7 (guardião 61, paladino 51):
  nenhuma magia precisou ser extraída, e todos os ids das tabelas de magia de subclasse resolveram.
- Catálogos novos: `feras_companheiras` (3), `dadivas_de_faeria` (6), `opcoes_de_presa_do_cacador`
  (2), `opcoes_de_taticas_defensivas` (2), `efeitos_da_torrente_do_vigilante` (2) e
  `opcoes_de_estilo_de_luta_de_classe` (2, completo: Combatente Druídico e Combatente Abençoado).
- `efeitos_de_canalizar_divindade` foi de 2 para 9 itens e ganhou o campo `classe`: o recurso do
  Paladino é separado do recurso do Clérigo, só o nome é comum.
- Tipos de efeito novos: `conceder_companheiro` e `reserva_de_cura`. Alvo novo:
  `tamanho_da_emanacao`.
- O validador ganhou a quarta família de catálogo, `CATALOGOS_DE_BLOCO_DE_ESTATISTICAS`, que cobra
  bloco completo em vez de `efeitos`.

**As duas decisões suas, já tomadas em 2026-09-01:**

- **Predador Implacável** (Guardião 13) — **resolvido.** Saiu de `substituir_regra` (remendo, e por
  isso dúvida) para o primitivo próprio `imunidade_a_quebra_de_concentracao`, com `causa: "dano"` e
  escopo na Marca do Predador. `caracteristicas.json` ficou **sem nenhum `substituir_regra`**; os
  dois que restam no dataset estão em catálogos de fases anteriores.
- **Maestria em Arma do Guardião e do Paladino** — **fica como o livro: 2 tipos de arma fixos, do
  nível 1 ao 20.** Conferido três vezes: as tabelas das p. 118 e 168 não têm coluna de Maestria (o
  Guerreiro tem, indo de 3 a 5), e os níveis 20 das duas classes são Matador de Inimigos Favoritos
  e Característica de Subclasse. **Regra da mesa pendente:** o João considera dar +2 no nível 20.
  Não entra no dado; espera a camada de `overrides` da mesa, que o esquema prevê (§1.5) e que ainda
  não existe como arquivo — ver seção 8.

---

## 3c. Capítulo 4 (Origens) — RESOLVIDO

Fechado em 2026-09-01 (ver `revisao-fase11-capitulo4.md`). **16 antecedentes e 10 espécies, com 38
traços.** Era o último capítulo do escopo, e o que bloqueava a criação de personagem.

- Catálogos novos: `antecedentes` (16), `especies` (10), e seis de linhagem — `heranca_draconica`
  (10), `linhagens_elficas` (3), `linhagens_gnomicas` (2), `ancestralidades_gigantes` (6),
  `revelacoes_celestiais` (3), `legados_inferos` (3).
- Campo novo `nivel_de_personagem`: até aqui todo nível do dataset era de classe. Três traços
  dependem do nível de personagem (Revelação Celestial 3, Voo Dracônico 5, Forma Grande 5) — e num
  futuro multiclasse essa conta não é a mesma.
- Tamanho pode ser escolha do jogador (Aasimar, Humano, Tiferino: Médio ou Pequeno).
- Sentido novo: `sismiconsciencia`. Tipos de efeito novos: `alterar_tamanho`, `alterar_descanso`.
  Alvo novo: `capacidade_de_carga`.
- Duas famílias novas no validador, `CATALOGOS_DE_ESPECIE` e `CATALOGOS_DE_ANTECEDENTE`, que cobram
  a forma fixa do antecedente e o cabeçalho + traços da espécie.
- Conferência que passou: **as 18 perícias do livro aparecem em algum antecedente.**

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

| primitivo                   | onde vive                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------- |
| mãos ocupadas               | `maos_ocupadas` em 49 itens; `maos_alternativas` nas armas Versáteis                  |
| consumo de munição          | `consumo` em 9 armas, com id da munição e recuperação pós-combate                     |
| teto por ação               | `limite_por_acao` em 6 armas com Recarga                                              |
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

| onde                                     | divergência                                                                                                   | resolução                                                                                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Monge, níveis 6 e 10                     | tabela diz "Ataques Potencializados"/"Autocura"; título diz "Golpes Potencializados"/"Restauro Pessoal"       | vale o título; nome da tabela guardado em `nome_na_tabela`                                                                  |
| Monge, Passo da Sombra Aprimorado        | redação ambígua sobre o requisito de luz                                                                      | ruling seu: gastando 1 Ponto de Foco, os dois requisitos caem                                                               |
| Guerreiro, Gato Por Lebre                | parágrafo do bônus de CA aparecia solto por quebra de coluna                                                  | é parte da manobra                                                                                                          |
| Mago, Ilusionista                        | Criaturas Espectrais cita Invocar Fera, fora da lista do Mago                                                 | acesso concedido pela subclasse                                                                                             |
| Bruxo, patronos                          | "Magias Psíquicas" e "Mente Desperta" impressas sob o título do Ínfero                                        | são do Grande Antigo                                                                                                        |
| Bruxo, Fome de Hadar                     | escola grafada "Conjuração"; no resto do livro é "Invocação"                                                  | normalizado, com nota na magia                                                                                              |
| Druida, lista de magias                  | Visão no Escuro caía no 3º círculo por cabeçalho colado                                                       | corrigido no parser; é 2º círculo (cap. 7, p. 342)                                                                          |
| Clérigo, Domínio da Luz                  | tabela lista "Mãos Ardentes", magia inexistente                                                               | é Mãos Flamejantes (p. 303); nome guardado em `nomes_alternativos`                                                          |
| Clérigo, Domínio da Guerra               | concede Manto do Cruzado, que a entrada declara de Paladino                                                   | acesso concedido pela subclasse                                                                                             |
| "Remeter"                                | Evocação na lista do Clérigo, Adivinhação na entrada e na lista do Mago                                       | vale a entrada: Adivinhação                                                                                                 |
| Consagrar                                | Evocação na lista do Clérigo (p. 84), Abjuração na entrada (p. 264)                                           | vale a entrada: Abjuração                                                                                                   |
| Esfera Flamejante                        | Evocação nas listas de Druida e Mago, Invocação na entrada (p. 279)                                           | vale a entrada: Invocação                                                                                                   |
| Tempestade Radiante                      | "Jallarzi" na lista do Bruxo e na entrada, "Jallazar" na do Mago                                              | vale a entrada; as duas grafias tinham virado DUAS magias no catálogo, fundidas em uma                                      |
| Animar Mortos                            | o círculo é impresso com `3°` (sinal de grau) em vez de `3º`                                                  | erro tipográfico do livro; o parser aceita os dois                                                                          |
| Armaduras                                | a tabela diz "Couro"/"Couro Batido"; as classes dizem "Armadura de Couro"/"de Couro Batido"                   | mesmo item, com as duas formas em `nomes_alternativos`                                                                      |
| Munição                                  | a tabela de Armas diz "Flecha"/"Virote"; a de Munição vende "Flechas"/"Virotes", e "Bala" serve a duas linhas | resolvido pelo id real, decidindo pela arma                                                                                 |
| Veículos                                 | a tabela imprime "Aeronau" (p. 230)                                                                           | mantido como impresso, marcado como dúvida                                                                                  |
| Bárbaro, níveis 13 e 17                  | tabela diz "Golpe Brutal Aprimorado"; títulos dizem "Fortalecido"                                             | vale o título; duas seções tituladas ⇒ duas características (`_13` e `_17`)                                                 |
| Ladino, nível 1                          | tabela diz "Especialização" e "Gíria dos Ladrões"; títulos dizem "Especialista" e "Gíria do Ladrão"           | vale o título; nome da tabela em `nome_na_tabela`                                                                           |
| Paladino, Juramento da Vingança, nível 3 | a tabela concede "Marca do Caçador", magia inexistente no cap. 7                                              | é Marca do Predador (p. 303), nome 2024 da Hunter's Mark; resolvido pelo id real, com nota                                  |
| Guardião e Paladino, magias de subclasse | 41 das magias concedidas não estão na lista da própria classe                                                 | é o desenho: a subclasse concede acesso, como o Ilusionista com Invocar Fera. Marcado com `acesso_concedido_pela_subclasse` |
| Paladino, níveis 13 e 17                 | a tabela imprime "—"                                                                                          | níveis sem característica; `caracteristicas: []`, e a progressão mantém as 20 linhas                                        |
| Gnomo das Rochas (p. 191)                | o traço cita o truque "Consertar"                                                                             | a entrada do cap. 7 é Reparar; resolvido pelo id real, com nota                                                             |
| Elfo Silvestre (p. 190)                  | a tabela diz "Passos Sem Rastro" (plural)                                                                     | a magia é Passo Sem Rastro, como no cap. 7 e na lista do Guardião                                                           |
| Fazendeiro (p. 182)                      | o pacote diz "Balde de Ferro"                                                                                 | no cap. 6 o item é Balde; id real, nome impresso na nota                                                                    |
| Drow e Elfo Silvestre (p. 190)           | "aumenta para 36 m" / "aumenta para 10,5 m"                                                                   | é substituição, não soma: `empilha: maior_valor`                                                                            |

---

## 7. Conteúdo do livro que faltava e foi recuperado

| onde                     | o que faltava                                                                                                      | quando               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------ | -------------------- |
| Druida, Círculo da Terra | as **4 tabelas de Magias de Círculo Druídico** (p. 98), 24 magias — o terreno escolhido não concedia magia nenhuma | varredura das opções |
| 11 catálogos de opção    | 37 opções tinham só texto, sem efeitos executáveis                                                                 | varredura das opções |
| catálogo de magias       | 24 magias do cap. 7 nunca tinham entrado (as de Bardo, Feiticeiro, Guardião e Paladino)                            | fase 3a              |
| catálogo de itens        | o capítulo 6 inteiro, exceto as 38 armas sem detalhe                                                               | fase 4               |

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

**Falta do livro** (registro da época; capítulo 5 fechou na fase 9 e as duas classes na fase 10)

- ~~Classes: **Guardião** (p. 117) e **Paladino** (p. 167).~~
- ~~**Capítulos 4 e 5**: origens, espécies, antecedentes e talentos.~~

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

- ~~`auditar_descricoes.py` só pega fatos verificáveis por termo.~~ **Resolvido em 2026-09-03
  (fase 20):** as 391 entradas foram relidas uma a uma com `revisar_magias.py`, que põe o corpo do
  capítulo 7 ao lado da paráfrase. 89 reescritas, 23 delas com regra de 2014. O `auditar` continua
  como está — ele pega o que dá para pegar por termo — mas ganhou uma **guarda de nome**: falha se
  alguma magia do catálogo não tiver entrada no capítulo 7, que era o buraco por onde quatro
  magias passavam sem conferência nenhuma.
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

- ~~Classes: **Guardião** (p. 117) e **Paladino** (p. 167).~~ Fechadas na fase 10.
- **Capítulo 4**: origens, espécies e antecedentes. **É o único capítulo do escopo que falta.**

---

## Fase 10 — Guardião e Paladino (ver `revisao-fase10-guardiao-paladino.md`)

**Fechado nesta fase**

- Guardião (p. 117-125): 34 características, 4 subclasses. Paladino (p. 167-175): 34 e 4.
  **Capítulo 3 completo.**
- Paladino é a primeira classe com característica de subclasse no **nível 20** (3, 7, 15, 20) e a
  única com níveis vazios na tabela (13 e 17).
- Feras do Companheiro Primal em catálogo próprio, sem reabrir o Apêndice B.
- Canalizar Divindade do Paladino como recurso separado do Clérigo, no catálogo compartilhado.
- `reserva_de_cura` (Mãos Consagradas) e `conceder_companheiro` como tipos novos.
- Aura de Proteção como emanação única que as demais características só engrossam.
- `teste_negativo_guardiao_paladino.py`: 18 de 18 defeitos plantados pegos.

**Corrigido de lotes anteriores**

- **`impedir` com `alvo` em lista derrubava o validador** (`TypeError: unhashable type: 'list'`),
  em vez de conferir item a item — o esquema sempre permitiu array ali.
- **`operacao` era um enum só de dano**, e `alterar_condicao` usa o mesmo campo. Ampliado, com
  `allOf` condicional separando o que vale para dano e o que vale para condição.
- **`jsonschema` do ambiente era 3.2.0**, sem `Draft202012Validator`: `checar_schema.py` vinha
  falhando em silêncio desde que virou script do projeto. Atualizado para 4.26.

**Aberto**

- 10 efeitos como `efeito_narrativo` (7 nas características, 3 nas opções de Canalizar Divindade).
- As duas decisões da seção 3b foram tomadas no mesmo dia: Predador Implacável virou primitivo, e a
  Maestria fica como o livro.

**Falta do livro**

- ~~**Capítulo 4**: origens, espécies e antecedentes.~~ Fechado na fase 11.

---

## 8. Camada de overrides da mesa — ainda não existe

O esquema declara desde a v0 que toda entidade aceita `override` da mesa, aplicado **por último**,
sem tocar no dado original (esquema-v1 §1.5, e a ordem de resolução em §6). Isso nunca virou
arquivo nem regra de validação: hoje é só princípio.

A primeira regra da mesa a esperar por ela já apareceu (2026-09-01): **+2 tipos de arma na Maestria
do Guardião e do Paladino no nível 20**. O dado continua como o livro; a regra fica aqui até a
camada existir.

Quando for construída, decidir de saída:

- onde mora — arquivo de campanha, ou campo no personagem (o esquema-v0 desenhou como
  `overrides[]` na ficha, o que resolve o caso do personagem mas não o da mesa inteira);
- o que pode ser sobrescrito — só valores derivados, ou também colunas de progressão e quantidade
  de escolha (a regra acima é justamente uma quantidade de escolha, o caso mais difícil);
- se o log de proveniência mostra o override ("Maestria 4 = 2 do livro + 2 da regra da mesa"), que
  é o que impede a mesa de esquecer o que combinou.

---

## Fase 11 — Capítulo 4, origens (ver `revisao-fase11-capitulo4.md`)

**Fechado nesta fase**

- 16 antecedentes e 10 espécies, com 38 traços. **Escopo do dataset fechado.**
- Antecedente escrito como tabela montada por função, não 16 blocos copiados — e a forma fixa do
  livro virou regra do validador.
- Quatro espécies com linhagem, cada uma em catálogo de opção próprio.
- `teste_negativo_origens.py`: 26 de 26 defeitos plantados pegos.

**Corrigido de lotes anteriores**

- **`magias_por_nivel` não era conferido por ninguém.** Linhagens e legados declaram as magias dos
  níveis 3 e 5 nesse campo, que **não é um efeito** — então o andador de efeitos nunca passava por
  ele, e um id de magia errado entrava calado. O teste negativo plantou `detectar_magias` (com S) e
  o validador deixou passar. Agora existe varredura própria, em todos os catálogos e coleções.

**Aberto**

- 2 traços como `efeito_narrativo` (Agilidade Pequenina e Furtividade Natural), ambos dependendo de
  geometria de combate que a base não modela.
- "Magia não pode forçá-lo a dormir" (Transe) continua narrativo: não é imunidade à condição
  Inconsciente, e não há "sono mágico" como categoria.
- O dispositivo mecânico do Gnomo das Rochas só resolve quando o motor souber enumerar os efeitos
  de Prestidigitação Arcana.

---

## 9. O que sobrou, e é tudo adiado de propósito

Com o capítulo 4, nenhum capítulo do escopo está em aberto. O que resta:

| o quê                                       | por quê                                                            | onde está registrado |
| ------------------------------------------- | ------------------------------------------------------------------ | -------------------- |
| Criaturas (Ap. B)                           | decisão de escopo; a Fase C do mestre reabre                       | seção 1              |
| Multiclasse                                 | decisão da Fase 0; os dados já vêm sendo gravados em `multiclasse` | seção 4              |
| Apêndice A (Multiverso)                     | fora do escopo                                                     | seção 4              |
| Camada de overrides da mesa                 | princípio declarado, nunca construído                              | seção 8              |
| Releitura das 391 magias contra a paráfrase | proposta minha, decisão sua                                        | fase 8               |
| Pente-fino no glossário (Ap. C)             | termos sem marcador entre colchetes                                | seção 5              |

**A Fase A do app está destravada.**

---

## 10. Auditoria de 2026-09-02 — o que a varredura achou

Varri o dataset inteiro atrás de marcas de pendência: `revisao: duvida`, `pendente: true`,
`substituir_regra`, catálogo declarado vazio e `efeito_narrativo`.

**Resolvido na hora (ver `geradores/gerar_ajustes_maestria.py`)**

Três marcas eram **restos da fase 2**, de quando o catálogo de itens ainda não existia:

- `maestria_em_arma` (Guerreiro) com `revisao: duvida` dizendo que o catálogo "só existe a partir do
  cap. 6". O capítulo 6 entrou na fase 4; o filtro resolve 38 armas.
- `maestria_em_arma_barbaro` e `maestria_em_arma_ladino` com `pendente: true` no bloco `de`.

A segunda não era cosmética: **`pendente: true` no bloco `de` desliga a checagem de filtro vazio**
(regra 5 do esquema). Enquanto estivesse lá, um filtro que parasse de devolver itens viraria
silêncio em vez de erro. Conferido antes de remover: sem as marcas, o validador segue limpo.

**Também resolvido: os 29 geradores que não rodavam**

Ancoravam o caminho em `<pasta do script>/dados`; os dados vivem em `dados/`, na raiz. Todos
reancorados. Junto veio o `reconstruir.py`, que declara a **ordem** de execução e reconstrói o
dataset num diretório separado — nunca em `dados/` — com `--comparar` para conferir contra o
versionado.

**O que a reconstrução revelou — e que foi consertado no mesmo dia**

Com o caminho corrigido, 37 dos 51 geradores rodavam e **22 arquivos saíam diferentes** do
versionado: o dataset não era reproduzível a partir das próprias fontes. As causas e o conserto:

| causa                                                                                                      | conserto                                                                                                        |
| ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| seis geradores liam intermediários de sessões antigas (`/tmp/claude-0/cap6.txt`, `/tmp/lista_druida.json`) | `geradores/extrair_texto.py` regera o texto do PDF em `intermediarios/`, e `caminhos.py` resolve tudo pela raiz |
| três apontavam o PDF por caminho absoluto de outra máquina                                                 | `caminhos.pdf()` acha por glob na raiz                                                                          |
| `beneficios_do_terceiro_olho.json` não tinha gerador nenhum                                                | `gerar_beneficios_do_terceiro_olho.py`                                                                          |
| correções das fases 2 a 9 feitas à mão, sem virar código                                                   | `gerar_ajustes_historicos.py` + `ajustes_historicos.json`                                                       |

Hoje: **58 de 58 geradores rodam e a comparação dá 0 diferenças de conteúdo.** O comando é
`python3 reconstruir.py /tmp/rb --comparar`, e ele nunca escreve em `dados/`.

Vale registrar um detalhe: os totais de `listas_de_magia` não são copiados pelo patch — são
recalculados a partir de `magias.json` e conferidos. A conferência falhou na primeira execução
(117 contra 118, porque o patch das magias ainda não tinha removido as quatro entradas espúrias do
parser), o que é a prova de que ela serve para alguma coisa.

**Também fechado na mesma rodada**

- 169 itens e 25 ferramentas ganharam `descricao_curta` derivada do próprio dado — o Compêndio do
  app prometia texto que não existia.
- 97 itens em 21 catálogos de opção passaram a declarar `fonte`, como manda o princípio 3.
- `emite_luz` virou o primitivo `emitir_luz`; `maestria_liberada` foi migrado para
  `conceder_maestria_de_arma`, que já existia — havia duas maneiras de dizer a mesma coisa.
- O validador ganhou `FILTROS_DE_RUNTIME`: chave de filtro fora da lista agora é erro, em vez de
  ser ignorada em silêncio. `teste_negativo_auditoria.py` cobra.
- `.gitignore`, `README.md`, `esquema-v0.md` marcado como histórico, `.VSCodeCounter` e o zip de
  515 KB fora da árvore.

O que sobrou está em **`BACKLOG.md`** — principalmente B11, migrar os ajustes históricos para os
geradores de origem, que é dívida paga mas ainda mal endereçada.

**Deliberadamente aberto, e já registrado em outras seções**

| o quê                         | quantos                                | onde                                                                              |
| ----------------------------- | -------------------------------------- | --------------------------------------------------------------------------------- |
| `efeito_narrativo` no dataset | 132                                    | fases 9, 10 e 11 — cada um marcado, nenhum escondido                              |
| `substituir_regra`            | 1 (Compreensão Superior)               | seção 3                                                                           |
| `revisao: duvida`             | 4                                      | Aeronau, Kit de Explorador do Druida, instrumentos do Bardo, Compreensão Superior |
| `pendente: true`              | 1 (Forma Selvagem) + `criaturas` vazio | seção 1                                                                           |
| `conflito_2014`               | 0                                      | —                                                                                 |

---

## Revisão externa — 2026-09-02

**Consertado**

- **Reprodutibilidade (B10).** `reconstruir.py --comparar` acusava 1 diferença de conteúdo: Raio
  Guia e Dominar Fera saíam com `nivel: null` numa reconstrução do zero, e o validador reprovava.
  Causa em dois geradores (`gerar_bruxo_magias.py` gravando `'nivel': None`, e
  `gerar_magias_detalhadas.py` não tratando o círculo como autoridade da entrada do cap. 7).
  Agora: 58/58 geradores, **0 diferenças de conteúdo**.
- **Golpe Astuto / Envenenar (B11).** A `revisao: duvida` com "id depende do cap. 6" era dívida
  vencida desde a fase 4. Virou `pre_requisitos: [{"tipo": "ferramenta", "chave":
"kit_de_veneno"}]`, e o validador passou a resolver chave de pré-requisito.
- **Instrumentos musicais do Bardo.** A dúvida dizia que o livro não enumerava; **enumera** — linha
  "Variantes:" da entrada de Instrumento Musical (p. 221), com custo e peso. As dez variantes
  ganharam custo e peso, e Bardo e Músico passaram a escolher 3 de 10 com `de_variantes: true`. O
  contorno `quantidade_de_instrumentos` foi removido. Kit de Jogos ganhou as 4 variantes do mesmo
  jeito.

**Conferido, sem mudança**

- **Kit do Druida: estava errado, corrigido.** O Druida apontava para
  `kit_de_explorador_de_masmorras`; o certo é **`kit_de_aventureiro`**. O conteúdo dos dois kits
  (p. 226) resolve: Kit de Aventureiro = Saco de Dormir, sem Pé de Cabra nem Estrepes (Explorer's
  Pack, que é o que o Druida recebe); Kit de Explorador de Masmorras = Pé de Cabra e Estrepes, sem
  Saco de Dormir (Dungeoneer's Pack). E o livro escreve o nome inteiro sempre que quer o segundo
  numa linha de classe (Feiticeiro p. 103, Guerreiro p. 127). A `revisao` do equipamento do Druida
  deixou de ser `duvida`.
  Junto veio outro defeito: a nota dessa divergência estava presa ao ITEM, então o Guerreiro
  carregava uma explicação sobre a linha do Druida. Agora a nota é por (classe, item).
- A revisão da fase 10 diz que sobraram "dois" `substituir_regra`; há **um**
  (`beneficios_do_terceiro_olho/compreensao_superior`), como o BACKLOG já registra.

**Checagens novas no validador**

| checagem                            | o que pega                                                                             |
| ----------------------------------- | -------------------------------------------------------------------------------------- |
| `de_variantes` numa escolha         | item sem `variantes`, mais de uma chave, ou quantidade maior que o número de variantes |
| `variante` num efeito               | variante que o item apontado não declara                                               |
| `pre_requisitos` de item/ferramenta | chave que não existe no catálogo                                                       |

---

## Fase 12 — Apêndice B, criaturas (ver `revisao-fase12-apendice-b.md`)

**Fechado nesta fase**

- **51 blocos de estatísticas** (43 Feras + Diabrete, Quasit, Esqueleto, Zumbi, Esfinge
  Maravilhosa, Pseudodragão, Slaad Girino, Sprite), com 112 traços e ações.
- `criaturas.json` sai de `preenchida: false` e passa a ser catálogo de BLOCO DE ESTATÍSTICAS
  no validador, com nove checagens novas.
- **O seletor de formas da Forma Selvagem ligou**: o filtro que estava escrito desde a fase 2
  agora resolve — 26 formas no nível 2, 33 no 4 e 42 no 8. Tipo de efeito novo
  `assumir_bloco_de_estatisticas`.
- A decisão de escopo "criaturas ficam fora" (Fase 0, decisão 5) está **revogada pelo usuário**.

**Divergências do livro encontradas**

Quatro modificadores de atributo que não correspondem ao valor impresso, em dois sabores:
Alce (Car 6, mod −4 mas SG −2) e Camelo (Des 8, mod −4 mas SG −1) — o SG confirma a conta, e
cheira a ruído de coluna na extração; Cabra (Int 2, mod e SG −5) e Cavalo Marinho Gigante
(For 16, mod e SG +2) — as duas colunas concordam entre si e discordam do valor, ou seja, o
livro discorda de si mesmo. Nos quatro o modificador é recalculado pela regra, o impresso fica
em `modificadores_impressos` e o caso vira entrada em `divergencias_do_livro`.

**Corrigido de lote anterior**

- O Golpe da Fera das três feras do Guardião não tinha `descricao_curta`; a checagem nova de
  bloco de estatísticas acusou. Passou a ter descrição derivada.

**Defeitos de parser corrigidos (não reintroduzir)**

17. Entrada fantasma recortada do meio de uma frase ("Ponto de Vida", no Zumbi) — o nome de
    traço/ação só vale se a frase anterior terminou. 15 entradas fantasma a menos.
18. Valor de campo que continua na linha seguinte era truncado (Idiomas do Zumbi).
19. "Morto-Vivo" × "Morto-vivo" no cabeçalho: o casador de tipo perdia o Zumbi. Achado
    contando `ND (XP` — 51 — contra os 50 cabeçalhos casados.

**Ainda fora do escopo**

- Apêndice A (o multiverso) e multiclasse.

---

## Fase 19 — Backend (ver `revisoes/revisao-fase19-backend.md`)

**Fechado nesta fase**

- `backend/`: os sete endpoints do `PLANO-MOTOR` §7, mais saúde, listar e apagar. Zero
  dependências, como o motor. 35 testes.
- O personagem guarda a **construção**, nunca a ficha; o `PATCH` aceita só estado e recusa
  derivado; a versão do dataset vira ETag do compêndio e carimbo no personagem.
- `testes/rodar_todos.py` passou a incluir o backend: 16 passos.

**Corrigido no motor, achado pelo backend**

- **Escolha de característica repetível compartilhava id.** O Aumento no Valor de Atributo chega
  no 4, 8, 12 e 16 com o mesmo id declarado, e `escolhas` é indexado por id — então o do nível 8
  sobrescrevia o do 4 e o personagem nunca pegava dois talentos diferentes. Cinco características
  estavam nessa situação. O id passou a levar o nível da concessão (`asi_escolha_de_talento@8`), e
  o sufixo propaga para as escolhas do talento concedido.
- **`ErroDoMotor` não definia `name`**, e `porId` lançava `Error` puro: pedir uma espécie que o
  livro não tem respondia 500 em vez de 422.
- **Escolha incompleta era tratada como inválida.** `Problema` ganhou `tipo` e `faltam`; subir de
  nível deixou de ser recusado por produzir pendência.
- **`dataset.ts` passou a memorizar a leitura**: 49 ms → 2,4 ms por ficha. Um teste monta cada
  golden duas vezes para garantir que ninguém muta o dado que lê.

**Aberto** — `BACKLOG.md` §B14: autenticação, escrita concorrente (morde na Fase B), CORS, e a
serialização do catálogo grande.

---

## Fase 20 — Releitura das 391 magias (ver `revisoes/revisao-fase20-magias.md`)

**Fechado nesta fase**

- **89 paráfrases de magia reescritas de 391**, lendo o corpo do capítulo 7 ao lado de cada uma.
  **23 delas carregavam regra de 2014** — Reflexos, Telecinese, Localizar Criatura, Mão de Bigby,
  Passo Arbóreo, Mau Olhado, Dominar Fera, Símbolo, Desejo, entre outras. Os números batiam; a
  mecânica era de outra edição.
- **Proteger Fortaleza descrevia outra magia**: o texto que estava lá é o de Proibição.
- **Nove magias trocavam "começa o turno" por "termina o turno"** na salvaguarda de área — o
  padrão que mais se repetiu, e o mais fácil de repetir de novo.
- **Quatro paráfrases por referência** ("Como Dominar Fera, mas…") herdavam o erro da magia
  referida sem que nada acusasse. Reescritas autônomas.
- A bancada é `revisar_magias.py`: doze lotes de 35 magias, livro e paráfrase lado a lado. Ela não
  julga nada — o custo dela é o tempo de leitura, que é o preço, não um problema a contornar.

**Achado pela bancada, e o pior da fase**

- **Quatro magias nunca tiveram corpo extraído, e por isso nunca passaram por conferência
  nenhuma**: Bênção, Pele-Casca, Invocar Morto-Vivo e Proteção Contra Energia. O nome no catálogo
  não casava com a entrada do capítulo 7 — `parse_magias.ler_nomes` resolve o nome quebrado pela
  coluna usando a lista de nomes das **classes**, e quando a lista da classe imprime com outra
  caixa ou sem circunflexo, é a grafia dela que ganha. Consertado por
  `gerar_ajustes_nomes_de_magia.py`; as paráfrases estavam certas por sorte, não por processo.
- Fechado com guarda: `auditar_descricoes.py` agora **falha** se qualquer magia do catálogo ficar
  sem entrada no capítulo 7. Um nome que não casa deixou de ser silêncio.

**Aberto**

- As **112 paráfrases de criatura** (Apêndice B) nunca passaram por esta releitura. É exatamente o
  mesmo risco, no mesmo formato, e o `auditar_descricoes.py` não as cobre.

---

## Fase 21 — Os cinco achados do primeiro uso de verdade

O João criou um Monge Draconato e um Mago no app e relatou cinco coisas. Quatro eram defeito,
uma não era — e a que não era vale tanto quanto as outras, porque a resposta veio do livro.

**Fechado nesta fase**

- **`aplicar_efeito_nomeado` ignorava o campo `catalogo`** (`motor/src/colecao.ts`). O efeito era
  procurado sempre em `dono.efeitos_nomeados`, e **10 dos 37 usos** declaram um catálogo. Resultado:
  escolher a herança do Draconato explodia com _"efeito nomeado 'dragao_vermelho' não existe em
  '(sem dono)'"_, e o mesmo valia para Elfo, Gnomo, Golias, Tiferino, Aasimar, Guardião, Paladino e
  Vigilante — seis espécies e três classes intransponíveis na criação.
- **Talento repetível vindo de duas fontes colidia no mesmo id.** O Humano concede um talento de
  Origem e o antecedente já concede outro; escolhido Iniciado em Magia nos dois, as escolhas dele
  saíam com id repetido — o React acusava chave duplicada e a gravação nunca terminava. O livro
  **permite** a repetição (p. 201, "deve escolher uma lista de magias diferente a cada vez"), então
  o conserto é qualificar (`iniciado_em_magia_truques@humano_versatil`), não recusar.
- **O livro de magias do Mago nunca foi uma escolha.** `conjuracao_mago` declarava
  `livro_de_magias` com `magias_iniciais: {quantidade: 6}` como texto descritivo, e `mago_preparadas`
  filtrava por `no_livro: true` — um campo que magia nenhuma tem. O livro nascia vazio e preparar
  oferecia **zero** opções, que foi exatamente o relato. Agora `gerar_livro_de_magias.py` abre a
  escolha `mago_livro`, com o total vindo de uma coluna nova da tabela (`magias_no_livro` =
  6 + 2×(nível−1), lida pelo **nível de Mago**, não do personagem), e o filtro de círculo
  (`circulo_com_espaco_disponivel`) já produz "seis de 1º círculo" no nível 1 sem regra especial.
  As quatro escolhas que diziam "do livro" passaram a declarar `de: {fonte: "livro_de_magias"}`.
- **O Bruxo tinha zero opções pela causa oposta**: `circulo_maximo: "coluna:circulo_dos_espacos"`
  era comparado como texto. O motor agora resolve `coluna:` dentro de filtro, como já fazia na
  quantidade. Duas listas vazias, dois defeitos sem parentesco.
- **A tela das escolhas era um monte de pílulas com um nome cada.** Escolher 6 magias entre 31 sem
  ver alcance, dano ou descrição é escolher no escuro. Agora cada opção é uma linha com nome,
  etiquetas (círculo, escola, tempo, alcance, dano, duração — as que o item tiver) e a descrição
  curta. A tela desenha **campos**, não conteúdo: um catálogo novo com `descricao_curta` aparece
  descrito sem tocar no arquivo.
- **O talento era escolhido antes de se saber o que ele faz.** Novo `POST /personagens/:id/escolhas/previa`:
  monta a construção com a escolha proposta e devolve o checklist resultante **sem gravar nada**.
  A tela mostra as sub-escolhas ali mesmo, aninhadas, e o Confirmar grava tudo de uma vez. Cabe no
  backend porque o motor é puro — montar de novo é barato, e a resposta é a verdade em vez de um
  palpite do frontend sobre o que o talento faz.

**Não era defeito**

- A proficiência com ferramenta do Monge é **escolha do livro**: p. 159, "Proficiências com
  Ferramentas — Escolha um tipo de Ferramentas de Artesão ou Instrumento Musical". O dataset está
  certo; a estranheza é do livro.

**Guardas novas**

- `validar.py`: **toda fonte lida tem de ser alimentada por alguém** (`de: {fonte}` exige uma
  escolha com `alimenta`). É a mesma classe de erro de porta declarada e nunca aberta — e teria
  pego o livro vazio sozinho.
- `testes/rodar_todos.py` roda `tsc --noEmit` no frontend. O projeto não tinha **nenhuma**
  checagem de tipo em lugar nenhum, e foi assim que três testes passaram por engano na fase 19.
  Motor e backend rodam TS sem build e continuam sem; o frontend já compila, então ali a checagem
  não custa build novo.
- Teste de fumaça foi de 10 para **15 passos**: opções em coluna, o livro do Mago oferecendo 31
  magias descritas, preparar oferecendo exatamente o que está no livro, o talento revelando o que
  pede antes de gravar, e o talento com as sub-escolhas gravados numa vez só.

**Aberto**

- **Pendência de escolha incompleta não aparece na tela.** Um Mago de nível 3 com 6 magias no livro
  precisa de 10: isso vira `problema` do tipo `incompleta` (que o backend devolve em
  `pendencias_de_escolha`), e não item de checklist. O frontend só desenha o checklist. Some com a
  tela de subir de nível, que ainda não existe.
- O livro **não cobra lista diferente** a cada Iniciado em Magia repetido (p. 201). Continua aberto.

---

## Fase 22 — as sete queixas do João, e o que elas revelaram

O João usou o app e trouxe sete coisas. Cinco eram pedido de tela; duas eram defeito. Consertar as
duas destapou outras quatro que ninguém tinha visto, todas da mesma família: **o motor descartava
em silêncio o que não sabia ler na hora**.

### Os defeitos, na ordem em que apareceram

**1. Modificador com valor de FÓRMULA era jogado fora.** `contexto.ts` fazia
`Number(e.valor[0])`; para `["nivel_do_personagem"]` isso dá `NaN`, e o efeito ia para
`nao_consumidos` sem uma palavra. Eram **31 modificadores no dataset inteiro** — a Tenacidade Anã
(+1 PV por nível), o Vigoroso (+2 por nível), invocações do Bruxo, ordens do Clérigo e do Druida.
O Anão andava a vida inteira com os Pontos de Vida de um humano e a ficha fechava bonitinho.

Conserto: o modificador cuja fórmula não dá para avaliar no meio da montagem fica pendente e é
avaliado numa **3ª passada**, com o contexto pronto. Fórmula que o avaliador realmente não conhece
(`dado:superioridade`, `um_tamanho_acima`) continua indo para `nao_consumidos` — mas agora só ela.

**2. `bonus_de_caracteristicas` estava fixo em `0` em `ficha.ts`.** A fórmula do livro era
respeitada à risca, com uma parcela sempre vazia. Os dois defeitos juntos faziam a mesma coisa por
caminhos diferentes, e nenhum dos dois quebrava nada — só davam um número plausível e errado.

**3. `especies.json` escrevia `nivel_de_personagem`** onde a fórmula pede `nivel_do_personagem`.
Enquanto o valor era descartado, a diferença não aparecia. Corrigido no gerador.

**4. As parcelas de `min`/`max` somavam mais do que o valor.** A CA da Clériga de ouro saía
`16 = 13 + 1 (Destreza) + 2 + 2 (escudo)`, que dá 18: o teto de Destreza da armadura é
`min(mod:DES, 2)` e a explicação trazia os **dois** operandos, quando só um entrou na conta.
Agora `min`/`max` levam só as parcelas do operando escolhido, e `menos` inverte o sinal do que
subtrai. Teste novo: em toda a ficha, as parcelas numéricas têm de explicar o número.

**5. `desbloquear_magias` nunca era lido.** As magias vindas de talento e antecedente existiam na
construção, apareciam no histórico e não apareciam em canto nenhum da ficha. Era a queixa 1 do
João, e a causa não era o filtro das preparáveis: era que ninguém consumia o efeito.

**6. `recurso_com_recarga` nunca era lido.** **88 efeitos** no dataset, zero na ficha. O Ataque de
Sopro do Draconato existia no livro, existia no JSON, e não existia na tela de quem ia usá-lo.

### O que passou a existir

| na ficha          | o que é                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| `atributos`       | a PONTUAÇÃO, ao lado do modificador — não dava para conferir um aumento só com o modificador                  |
| `magias`          | todas as magias, de todas as fontes, com `modo`, `origem` legível e `pronta_para_conjurar`                    |
| `recursos`        | o que se gasta e volta num descanso, com o máximo já calculado                                                |
| `caracteristicas` | características, traços e talentos que INCIDEM, tiradas das trilhas de origem — sem segunda lista para manter |
| `opcao.ja_tem`    | aviso (não bloqueio) de que a opção já vem por outra porta                                                    |

Mais `descansar()` no motor e `POST /personagens/:id/descanso` no backend. **A regra do descanso
não mora no backend**: `tipos_de_descanso.json` ganhou `recupera`, cada recurso já declarava a sua
`recarga`, e o `conceder_slot` da classe diz quando os espaços voltam. Por isso não existe nenhum
`if` sobre Bruxo em lugar nenhum, e ele recupera espaços no Descanso Curto do mesmo jeito.

Duas correções de regra vieram da releitura do livro (p. 33 e p. 366), ambas diferentes do 2014:
o Descanso Longo devolve **todos** os Dados de Vida (não metade), e os Pontos de Vida Temporários
**atravessam** o Descanso Curto.

### Achado na revisão desta fase (2026-09-04)

- **O aviso `ja_tem` não avisava justamente no caso que ele existe para cobrir.** A comparação era
  `d.origem.includes(escolhaId)` — texto dentro de texto —, e `iniciado_em_magia_truques` casava
  com `iniciado_em_magia_truques@humano_versatil`. O talento repetido concluía que a magia tinha
  vindo dele mesmo e ficava calado: pegar Iniciado em Magia duas vezes e gastar as duas escolhas no
  mesmo truque passava sem uma palavra. Agora a trilha é comparada por **segmento inteiro**.
- **`descansar()` descartava em silêncio quatro coisas que o dataset declara.** O `recupera` do
  Descanso Longo traz `dados_de_vida`, `exaustao`, `reducoes_de_maximo` e `reducoes_de_atributo`;
  o motor lia só os Pontos de Vida e os temporários. É a mesma família dos 88 `recurso_com_recarga`
  desta fase — e o teste `os dois descansos do livro declaram o que recuperam` chegava a conferir
  que `dados_de_vida: "todos"` está lá, sem que nada o aplicasse. O efeito do descanso agora traz
  `nao_aplicado`, e `"nenhum"`/`"mantem"` não entram: não mexer É o que aquele descanso faz.

### Aberto

- **Proveniência da CA ainda tem literal cru**: `16 = 13 (13) + 1 (Destreza) + 2 (escudo)`. O "13"
  é a base da armadura e sai como número porque a fórmula não nomeia os termos literais. O
  `valores_derivados.json` já declara a parcela `{"rotulo": "base", "chave": "ca_base"}`; falta o
  `max_entre_calculos_de_base` emitir uma parcela com essa chave em vez de despejar as internas do
  cálculo vencedor. É o resto do passo 3 do `PLANO-FASE-A.md`.
- **Recurso cuja fórmula de máximo o avaliador não conhece** (`tabela:dados_de_energia.quantidade`)
  cai em `nao_consumidos` e some da ficha. São poucos, mas somem calados — a tela não mostra
  `nao_consumidos` para ninguém.
- **`conjurar_sem_espaco` continua irregular** (passo 1 do `PLANO-FASE-A.md`). Enquanto isso, o
  botão "usar" das magias gasta espaço sempre, e não sabe que a Invocação Mística conjura de graça.

---

## Fase 23 — as dez do João, e as que vieram junto

Dez itens relatados em 2026-09-04, entre defeito e melhoria. Consertar os dois erros de
montagem que ele viu (`pacto_da_lamina`, `padrao`) destapou **15**; e as três queixas sobre
magia — o custo, o truque mudo, a linha sem números — eram todas o mesmo buraco: o app
decidia o que uma magia custa.

### Uma família inteira: efeito nomeado que não dizia o catálogo

O erro que ele viu duas vezes valia para **15 lugares**, e derrubava a montagem de quase toda
classe assim que a escolha fosse respondida: Guerreiro (manobras), Bruxo (invocações), Bárbaro
(golpe brutal, fúria/aspecto/poder dos selvagens), Ladino (golpe astuto), Bardo (inspiração),
Feiticeiro (metamagia, surtos), Druida (passos feéricos), Vigilante (revelação em carne) e dois
talentos. É a fase 21 vista pelo outro lado: **lá o efeito declarava `catalogo` e o motor
ignorava; aqui o motor lê e o dado não declarava.** `gerar_ajustes_efeito_nomeado.py` aplica a
regra mecânica — se a escolha tira as opções de um catálogo e o efeito aplicado não diz de onde
vem, é daquele catálogo —, e o `validar.py` passou a **exigir que todo `aplicar_efeito_nomeado`
resolva**, estaticamente. Era checagem que dava para fazer sem personagem nenhum.

### Três chaves de filtro que não existiam, em nove escolhas

"A escolha de perícias de especialização não mostra nada nem a do tipo de arma": `ja_proficiente`
não é campo de `pericias` nem filtro de runtime — casava com nada, e a escolha ficava com **zero
opções, calada**. Junto vieram `sem_especializacao` e `sem_proficiencia_em_salvaguarda`, nas duas
Especializações de talento, no Acadêmico do Mago, no Especialista do Bardo, no Mestre das Armas e
no Resiliente. A fresta era do validador: ele conferia as chaves de `filtro` e **não as de
`filtro_adicional`**.

E `com_proficiencia` não valia para arma: a Maestria do Ladino ("dois tipos de arma com que você
tem proficiência", p. 137) procurava a adaga na lista de perícias. Agora usa o mesmo
`proficienteComArma` que a ficha usa para decidir se o ataque leva bônus — uma verdade só.

### Idioma e armadura eram concedidos para ninguém

`conceder_proficiencia` só sabia pousar em perícia, ferramenta e salvaguarda: os **14 de idioma e
armadura caíam calados** em `nao_consumidos`. Por isso a Gíria dos Ladrões não aparecia em canto
nenhum, e a escolha "mais um idioma" oferecia de volta o que o Ladino já falava.

### Bardo e Feiticeiro não tinham bloco de magia nenhum

Os dois guardavam os espaços como **lista numa coluna só** (`espacos_de_magia: [4, 3, 2]`)
enquanto o resto do dataset usa uma coluna por círculo — e nada lia aquela forma. Daí as 127
magias de Bardo oferecidas no nível 1 (o filtro de círculo não achava coluna, declarava-se
`nao_avaliado` e não recortava) e o painel de espaços inexistente. Puxando o fio: **nenhum dos
dois tinha `preparar_magias`**, então a ficha devolvia `conjuracao: undefined` — sem CD, sem
ataque mágico, sem espaço. O livro diz o atributo com todas as letras (p. 60 e p. 104).

O Bruxo era o mesmo sintoma pelo lado oposto: a tabela dele é mesmo diferente (Espaços de Pacto,
todos do mesmo círculo, p. 121), e quem tinha de aprender a ler era o motor. Fechado com o teste
que faz a pergunta para todas: **quem conjura tem com o que conjurar?**

### Conjurar deixou de ser "gastar espaço"

As três queixas de magia:

- _"tem magias que posso usar uma vez por dia mas não gastam"_ — os **41 `conjurar_sem_espaco`**
  do dataset nunca eram lidos. Pior: no Iniciado em Magia a magia vem de outra escolha
  (`$escolhido_em:iniciado_em_magia_magia_1`), e essa referência não era resolvida em efeito
  nenhum — só em filtro. Agora a magia do talento tem custo de **uso**, que é um recurso de 1 que
  volta no Descanso Longo, e o livro permite gastar espaço também quando o uso acabou.
- _"clico em usar num truque e não fala nada"_ — a função saía cedo no truque, e o histórico só
  registrava o que mudava de estado. Agora existe `POST /personagens/:id/conjurar`: o cliente diz
  **qual magia**, o motor diz o que custa, e o evento é **dito** por quem conjurou em vez de
  deduzido da diferença.
- _"quero o nome, o número e tipo de dados que lanço, a salvaguarda, a distância e a área, já
  calculado"_ — `magia.jogo` traz tudo resolvido: `+7`, `CD 14 DES`, `2d8 radiante`, `18 metros`,
  área e concentração. O crescimento do truque saiu da prosa para `escala_por_nivel` (17 dos 20;
  o Raio Místico não entra porque ele aumenta **feixes**, não dado).

Ataques passaram para antes das magias, como pedido.

### A vida agora diz por que é 11

A proveniência abre um nível: `12 = 11 (PV do nível 1) + 1 (bônus de características)`, e embaixo
`PV do nível 1: 8 (Dado de Vida) + 3 (Constituição)` e `bônus: 1 (Anão · Tenacidade Anã)`. Os
rótulos vêm dos `parcelas` que o catálogo **já declarava** — o motor não escreve frase nenhuma.

### Achado sem ninguém pedir

- **Duas cópias do mesmo talento roubavam a variável uma da outra.** O Acólito concede Iniciado em
  Magia e o Humano concede outro: as duas escolhas definiam `lista_do_talento`, e a segunda
  sobrescrevia a primeira — os truques oferecidos a uma vinham da lista da outra, e a construção
  era recusada. Variável e `depende_de` passaram a respeitar o `@sufixo` da porta.
- **`reconstruir.py --comparar` devolvia 0 mesmo com arquivos divergentes.** A conferência olha o
  código de saída: ela dizia "19 de 19 passos limpos" enquanto três arquivos de `dados/` já não
  eram o que os geradores produzem. Divergência agora é falha.

### Aberto

- **Não é defeito, é o livro**: a Gíria do Ladrão dá mesmo "outro idioma à sua escolha" (p. 137).
  O que estava errado era a lista oferecer o que ele já fala.
- **Comum não é concedido a ninguém.** Todo personagem sabe Comum e mais dois idiomas da tabela
  (p. 37), e isso é criação de personagem — capítulo 2, que o dataset ainda não cobre.
- A Especialização do Ladino mostra poucas opções até as perícias iniciais serem escolhidas. Está
  certo (ela só pode escolher entre as que já tem), mas a tela não explica a ordem.
- Três truques continuam com o crescimento só em prosa: Acudir os Moribundos, Badalar Fúnebre e
  Raio Místico.

---

## Fase 24 — a língua que sumiu, os números que faltavam e o inventário

### O Ladino não conseguia escolher idioma nenhum — e a causa era geral

Regressão da fase 23, e das boas de aprender: pus `com_proficiencia: false` na escolha
"mais um idioma" para ela não oferecer o que o personagem já fala. Só que, respondida
Dracônico, o personagem **passa a falar Dracônico** — e a conferência seguinte recusava a
própria resposta com 422. Na tela: "não me deixou escolher nenhuma língua".

Vale para qualquer escolha que filtre pelo que ela mesma concede. O conserto é o mesmo
que o aviso "você já tem" usa: a proficiência agora guarda **de onde veio**
(`proficiencias_com_origem`), e o filtro ignora o que veio desta mesma escolha.

### "Deveria ser retirado o Comum e o da raça?" — só o Comum, e ele não é da raça

O livro (p. 37): "O seu personagem sabe pelo menos três idiomas: **Comum e mais dois
idiomas** que você pode escolher da tabela Idiomas Comuns." E **nenhuma espécie concede
idioma em 2024** — conferido no dataset inteiro: espécie nenhuma cita idioma, antecedente
nenhum também. O Anão não dá Anão; isso é 2014.

Faltava o começo: o personagem nascia sem falar nada. Agora `escopo: "todo_personagem"`
existe como terceiro tipo de fonte, ao lado de espécie/antecedente/classe, e a criação
concede o Comum e abre a escolha dos outros dois — só entre os **comuns**, porque os raros
vêm por característica que os conceda (a Gíria do Ladrão, o Idioma Druídico).

### Salvaguardas e perícias, com o número

`testes_de_pericia` era um campo declarado que devolvia `{}`. Agora traz as 18 perícias —
**todas**, não só as treinadas, porque é justamente na que não se tem proficiência que a
conta não é óbvia — cada uma com valor, atributo e a conta que a explica ao toque. As seis
salvaguardas ganharam painel próprio, com destaque nas que somam proficiência.

Puxando esse fio: **Especialização não somava nada.** O `nivel_dominio` era jogado fora ao
guardar a proficiência, então a Especialização do Ladino, a do Bardo e a dos dois talentos
existiam no JSON e não existiam na conta. E havia quatro grafias para três ideias
(`proficiente`, `especialista`, `especializacao`, `treinado`). Normalizadas, e o quanto
cada uma vale virou catálogo (`niveis_de_dominio`, com `multiplicador_do_bonus`): o motor
lê, em vez de trazer "especialista dobra" escrito dentro de si — o lint de id de conteúdo,
aliás, foi quem cobrou isso.

### Inventário

`inventario` (id → quantidade) e `equipado` passaram a ser **estado**, e não construção:
pegar uma corda e sacar o escudo acontecem na mesa e não mudam quem o personagem é.
O que a criação vestia é materializado no inventário na primeira vez que a mesa mexe nele
— sem isso, o primeiro "equipar escudo" apagaria a armadura que veio da criação e a CA
cairia sozinha.

O backend confere **coerência** (o item existe, você equipa só o que carrega, quantidade
zero é não ter, largar o que está na mão tira da mão), e a regra continua no motor: equipar
um escudo muda a CA porque o motor recalcula, e a tela não sabe o que um escudo faz.
Quatro eventos novos no histórico: pegou, perdeu, equipou, guardou.

Teste de fumaça em **22 passos**: o escudo entra no inventário, é equipado, e a CA sobe de
10 para 12 num navegador de verdade.

### Aberto

- Dinheiro não existe: pegar um item não desconta moeda, e comprar não é uma operação.
- Peso e capacidade de carga não são calculados (o dado tem `peso_kg` em todo item).
- O que se equipa é decidido pela categoria (arma/armadura) na tela; foco de conjuração e
  munição ainda não têm tratamento próprio.

---

## Fase 25 — o cajado que é duas coisas, os nomes e o compêndio

### O foco druídico é TAMBÉM uma arma, e o livro diz isso

"Não deixa eu equipar o cajado de madeira, mas eu uso ele como um druida para usar o
Bordão Místico" (2026-09-04). Duas coisas faltavam, e a segunda é a interessante.

A primeira: a tela decidia o que é equipável por categoria (`arma` ou `armadura`), e o
foco de conjuração — que é justamente algo que se segura — ficava sem botão. Agora
**o item declara** `equipavel`, e uma categoria nova no livro entra no dado, não em três
telas.

A segunda estava na tabela de Focos Druídicos (p. 225):

    Cajado de madeira (também um Bastão)   2 kg   5 PO

O "(também um Bastão)" quer dizer que o foco **é** a arma Cajado — e é isso que faz o
Bordão Místico valer com ele. O dataset tinha perdido essa metade: o foco não tinha dano,
grupo nem maestria, e o Foco Arcano "Cajado" nem existia como entrada separada, porque
colide de id com a arma. Agora `cajado_de_madeira` declara `tambem_e: "cajado"` e a arma
declara `tambem_foco: "arcano"`. **`tambem_e` é referência, não cópia**: os números
continuam vindo de um lugar só, e o motor os resolve ao equipar, mantendo o nome e o id
do que está na mão.

### "A armadura de couro só aparece como Couro"

O livro imprime as armaduras de dois jeitos: a **tabela** (p. 219) usa a forma curta
— "Acolchoada", "Couro", "Couro Batido" — e a **ilustração da mesma seção** (p. 218) usa o
nome inteiro: "Armadura de Couro", "Armadura de Placas parcial". Os dois são o livro; o
que serve numa ficha é o inteiro. A forma curta ficou em `nome_curto`.

A regra do gerador é mecânica, e é o que a impede de virar gosto: **usa-se o nome da
ilustração só quando ele acrescenta o prefixo "Armadura"** — e há um `assert` que recusa
qualquer troca que não seja isso. Cinco armaduras mudaram; "Gibão de Peles", "Cota de
Malha" e "Couraça Peitoral" não são tocadas.

Os três focos com minúscula no meio ("Cajado de madeira", "Ramo de visco", "Varinha de
teixo") **não** foram mexidos: é assim que o livro os imprime na tabela da p. 225.

### Compêndio

Tela nova, e ela não sabe o que é um item: recebe o nome de uma coleção, agrupa pelo
primeiro campo de agrupamento que aquela coleção usar (`categoria`, `nivel`, `raridade`,
`escola`, `grupo`) e desenha os campos que cada entrada tiver. Apontar para `magias`
mostraria as magias por círculo sem uma linha nova. Busca por nome em cima, categorias
recolhíveis embaixo.

Teste de fumaça em **24 passos**: equipar o foco druídico e vê-lo virar ataque, e o
compêndio abrindo a categoria de armaduras com o nome inteiro na tela.

### Aberto

- `tambem_foco: "arcano"` está declarado e ninguém o lê ainda: quando o custo de
  conjuração olhar componentes materiais, é ele que vai dizer que o Cajado serve de foco.
- Continua sem dinheiro, sem peso carregado e sem munição.

### Anotações do João

- Revisitar a parte de itens para fazer melhorias
- Fazer o resto do compêndio
- Fazer sistema de level up
- Adicionar Imagens aos personagens
- Adicionar Update e Delete aos personagens
- Refazer Front end, visual mais moderno, limpo e descontraído (tons de azul), focado em mobile, com abas para separar as informações
-
