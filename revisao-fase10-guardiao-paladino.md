# Fase 10 — Guardião e Paladino: as 12 classes fechadas

Extraídas em 2026-09-01. Guardião p. 117-125, Paladino p. 167-175. Com elas, o capítulo 3 do
livro está inteiro no dataset: **12 classes, 48 subclasses, 388 características**.

`validar.py`: **0 erros, 0 avisos**. `checar_schema.py`: 67 arquivos, todos passam.
`teste_negativo_guardiao_paladino.py`: **18 de 18** defeitos plantados pegos.

---

## O que entrou

| | Guardião | Paladino |
|---|---|---|
| características | 34 | 34 |
| subclasses | Andarilho Feérico, Caçador, Senhor das Feras, Vigilante das Sombras | Juramento da Devoção, da Glória, da Vingança, dos Anciões |
| níveis de subclasse | 3, 7, 11, 15 | **3, 7, 15, 20** |
| conjuração | meio-conjurador, SAB, lista `guardiao` (61 magias, já preenchida) | meio-conjurador, CAR, lista `paladino` (51, já preenchida) |
| foco | Foco Druídico (ramo de visco) | Símbolo Sagrado (amuleto, emblema ou relicário) |

As duas listas de magia **já estavam prontas** desde o capítulo 7 — não foi preciso extrair magia
nenhuma. Todos os ids das cinco tabelas de magia de subclasse resolveram contra o catálogo.

O Paladino é a **primeira classe com característica de subclasse no nível 20**, e a segunda (depois
do Feiticeiro no 18) a fugir do 3/7/11/15. A regra do validador que cobra "toda subclasse precisa
ter característica em todo nível marcado pela classe" pegou isso sozinha durante a extração.

Também é a única classe com **níveis vazios na tabela**: 13 e 17 não concedem nada. Ficaram como
`caracteristicas: []` — a progressão continua com as 20 linhas que o esquema exige.

---

## Decisões deste lote

### 1. As três feras do Companheiro Primal entram — e não reabrem o Apêndice B

O Senhor das Feras traz **três blocos de estatísticas impressos no capítulo 3**: Fera da Terra, do
Céu e do Mar. Sem eles a subclasse não funciona, e adiá-los seria adiar uma subclasse inteira.

A decisão de adiar criaturas (PENDENCIAS §1) continua valendo: `criaturas.json` segue vazio com
`preenchida: false`, e a Forma Selvagem segue com o aviso de ND. As três feras moram em catálogo
próprio, **`feras_companheiras`**, porque não são bestiário: CA, PV e Golpe da Fera são escritos em
função do nível e do modificador de Sabedoria do Guardião, e só existem dentro da subclasse.

Isso obrigou uma família nova no validador. Um bloco de estatísticas não tem `efeitos` — a mecânica
dele mora em atributos, PV, traços e ações. Em vez de espremer a ficha da criatura dentro de um
campo que não foi feito para ela, o validador ganhou
`CATALOGOS_DE_BLOCO_DE_ESTATISTICAS`, que cobra o bloco estar completo: atributos válidos, PV, CA,
deslocamentos de tipo conhecido, sentidos de tipo conhecido, tamanho e tipo de criatura do catálogo,
e pelo menos uma ação. A regra pegou um erro meu no mesmo minuto em que nasceu — eu tinha escrito
`pequena`/`media`, e o catálogo `tamanhos` diz `pequeno`/`medio`.

### 2. Canalizar Divindade do Paladino é outro recurso, não o do Clérigo

Mesmo nome, coisas diferentes: recurso próprio (`canalizar_divindade_paladino`, 2 usos e 3 a partir
do nível 11), coluna própria, CD saindo da Conjuração do Paladino, e opção base Sentido Divino em
vez de Centelha Divina.

As opções das duas classes moram no mesmo catálogo `efeitos_de_canalizar_divindade`, agora separadas
pelo campo `classe` — as 2 do Clérigo mais **7 do Paladino** (Sentido Divino, Repudiar Inimigos, e
as cinco das subclasses). Cada característica que abre uma opção nova a libera com
`expandir_opcoes_de_escolha`, apontando para a escolha `canalizar_divindade_paladino_opcao`. Era
exatamente o caso que o catálogo previa quando nasceu marcado `parcial`.

### 3. Mãos Consagradas é uma reserva, não um recurso com usos

Cinco vezes o nível de Paladino em Pontos de Vida, gastos livremente em cura ou a 5 por condição
removida. Não é `recurso_com_recarga` (que conta usos) nem `reserva_de_dados` (que rola dado): é um
pote numérico. Tipo de efeito novo, **`reserva_de_cura`**. Toque Restaurador, no nível 14, apenas
`melhorar_caracteristica` em cima dela.

### 4. A Aura de Proteção é uma só, e as outras características a engrossam

Aura de Coragem, Aura de Devoção, Aura de Vivacidade, Aura de Resistência, Destruição Protetora,
Resplendor Sagrado, Anjo Vingador e Campeão Ancestral **não recriam a aura**: todas apontam para
`aura_de_protecao` com `melhorar_caracteristica`. Aura Expandida troca o raio de 3 m por 9 m pelo
alvo novo `tamanho_da_emanacao`. Assim o app soma tudo numa emanação só, que é como a mesa joga.

### 5. Combatente Druídico e Combatente Abençoado, no mesmo catálogo

As duas classes oferecem uma opção **no lugar** do talento de Estilo de Luta. Nasceram juntas em
`opcoes_de_estilo_de_luta_de_classe`, e a característica de cada classe libera a sua chave na
própria escolha do talento com `expandir_opcoes_de_escolha` — o mesmo mecanismo do Golpe Brutal
Fortalecido. O livro diz "em vez de escolher um desses talentos": é uma escolha só, não duas.

---

## Corrigido de lotes anteriores

- **`impedir` com `alvo` em LISTA estourava o validador.** O esquema do efeito sempre permitiu
  `alvo` como array, mas o ramo do `impedir` só olhava string — uma lista levantava
  `TypeError: unhashable type: 'list'` e derrubava a validação inteira em vez de conferir item a
  item. Agora normaliza. O teste negativo planta `['acao', 'sesta']` e cobra o erro.
- **`operacao` era um enum só de dano.** `alterar_condicao` usa o mesmo campo (`imunidade`), e a
  redução de Exaustão do Incansável precisava de `reduzir_nivel`, que o esquema recusava. O enum foi
  ampliado e ganhou dois `allOf` condicionais: `alterar_dano` continua restrito às quatro operações
  de dano, e `alterar_condicao` às três que fazem sentido para condição.
- **`jsonschema` do ambiente era 3.2.0**, sem `Draft202012Validator` — `checar_schema.py` vinha
  falhando em silêncio ("não instalado") desde que virou script. Atualizado para 4.26.

---

## Divergências do livro encontradas neste lote

| onde | divergência | resolução |
|---|---|---|
| Juramento da Vingança, nível 3 | a tabela imprime **"Marca do Caçador"**, magia que não existe no cap. 7 | é a Marca do Predador (p. 303), nome 2024 da Hunter's Mark; resolvido pelo id real, com nota na característica |
| Guardião e Paladino, tabelas de magia de subclasse | 41 das magias concedidas **não estão na lista da própria classe** | é o desenho, não defeito: magia de subclasse concede acesso, como o Ilusionista com Invocar Fera e o Domínio da Guerra com Manto do Cruzado. Marcado com `acesso_concedido_pela_subclasse` |
| Paladino, níveis 13 e 17 | a tabela imprime "—" | níveis sem característica; `caracteristicas: []` |

---

## Aberto

- **10 efeitos ficaram como `efeito_narrativo`** — 7 nas características e 3 nas opções de
  Canalizar Divindade — por dependerem de julgamento na mesa ou de primitivo que a base não tem:
  emissão de luz (Arma Sagrada, Resplendor Sagrado), salto ampliado (Atleta Inigualável), movimento
  dentro da Reação (Vingador Implacável), não envelhecer (Sentinela Imortal), detecção por tipo de
  criatura (Sentido Divino), respirar ar e água e revelar Imunidades e Resistências (Conhecimento do
  Caçador), comando e ressurreição da fera (Companheiro Primal), e a Dádiva de Faéria, que é
  estética por definição. Marcados, não escondidos.
- **Maestria em Arma do Guardião e do Paladino** fica fixa em dois tipos de arma, do nível 1 ao 20,
  como está impresso — decisão do João no mesmo dia, depois de conferir. Ele considera dar +2 no
  nível 20 como regra da mesa; isso **não entra no dado** e espera a camada de `overrides`
  (PENDENCIAS §8).

## Resolvido ainda nesta fase

- **Predador Implacável saiu de `substituir_regra`.** Nasceu como remendo (e portanto dúvida, que é
  a regra do esquema) e virou o primitivo `imunidade_a_quebra_de_concentracao`, com `causa` e
  escopo por magia. Mesma migração que os empurrões fizeram na fase 7, quando ganharam
  `movimento_forcado`. Com isso, `caracteristicas.json` não tem mais nenhum `substituir_regra` —
  os dois restantes no dataset estão em catálogos de fases anteriores.
