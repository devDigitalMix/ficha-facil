# Fase 11 — Capítulo 4: origens dos personagens

Extraído em 2026-09-01. Antecedentes p. 177-185, espécies p. 186-197.
**16 antecedentes, 10 espécies, 38 traços.** Com isso o escopo do dataset está fechado.

`validar.py`: **0 erros, 0 avisos**. `checar_schema.py`: 75 arquivos, todos passam.
`teste_negativo_origens.py`: **26 de 26** defeitos plantados pegos. Os quatro testes negativos
anteriores continuam em 18/18, 11/11, 16/16 e 18/18.

---

## Antecedente é uma máquina regular — e por isso vira tabela

Todo antecedente de 2024 tem a mesma forma: três atributos, um talento de Origem, duas perícias,
uma ferramenta e um pacote de equipamento contra 50 PO. Escrevi os 16 como **uma tabela montada por
função**, não como 16 blocos copiados — que é exatamente onde erro de digitação se esconde.

A regularidade virou regra do validador (`CATALOGOS_DE_ANTECEDENTE`), que cobra a forma inteira:
três atributos válidos, duas perícias que existem, talento que seja mesmo da **categoria origem**,
todo item do pacote existindo em `itens` ou `ferramentas`, e a opção B sendo 50 PO.

O aumento de atributo é a parte que o app precisa acertar. O livro dá três atributos e duas formas
de distribuir — +2 num e +1 noutro, ou +1 nos três, teto 20. Virou uma `escolha` entre os dois
modos, que já existiam em `modos_de_aumento_de_atributo` desde o capítulo 5.

Três antecedentes fixam a lista do Iniciado em Magia — Acólito (Clérigo), Guia (Druida), Sábio
(Mago). O talento é o mesmo, repetível, com uma escolha de lista dentro: o antecedente **não
duplica o talento, ele pré-resolve a escolha** (`escolhas_predefinidas`). O atributo de conjuração e
os truques continuam com o jogador.

Conferência que valeu a pena: **as 18 perícias do livro aparecem em algum antecedente.** Nenhuma
ficou órfã, o que é um bom sinal de que nenhuma linha foi lida errado.

## Espécie não é regular — então o formato é outro

Cada espécie é um punhado de traços próprios. O formato é `tracos[]`, cada traço com id, nome,
página e efeitos — e não uma lista solta de efeitos no topo, que **perderia o nome do traço**, que é
justamente o que a ficha mostra ao jogador. Virou a quinta família do validador
(`CATALOGOS_DE_ESPECIE`), que cobra o cabeçalho (tipo de criatura, tamanho, deslocamento em número)
e que todo traço tenha nome, descrição, fonte e efeitos.

**Quatro espécies têm linhagem**, e cada uma virou catálogo de opção próprio, como Metamagia e
Manobras antes delas:

| catálogo | itens | o que faz |
|---|---|---|
| `heranca_draconica` | 10 | dez dragões, cinco tipos de dano; define sopro **e** resistência |
| `linhagens_elficas` | 3 | Alto Elfo, Drow, Elfo Silvestre — benefício no nível 1, magias nos 3 e 5 |
| `linhagens_gnomicas` | 2 | Gnomo das Rochas e do Bosque |
| `ancestralidades_gigantes` | 6 | os seis benefícios do Golias, com usos por Bônus de Proficiência |
| `revelacoes_celestiais` | 3 | as três formas do Aasimar, escolhidas **a cada transformação** |
| `legados_inferos` | 3 | Abissal, Ctônico, Infernal |

## Três coisas novas no esquema

**`nivel_de_personagem`.** Até aqui, todo nível no dataset era de classe. Revelação Celestial (3),
Voo Dracônico (5) e Forma Grande (5) dependem do nível de **personagem** — que num futuro
multiclasse não é a mesma conta. Campo novo, com faixa validada.

**Tamanho pode ser escolha.** Aasimar, Humano e Tiferino deixam o jogador escolher Médio ou Pequeno
na criação. O campo aceita `{"fixo": ...}` ou `{"escolha": [...]}`, e o validador confere as duas
formas contra o catálogo `tamanhos`.

**Sentido novo: `sismiconsciencia`**, para o Conhecimento de Pedras do Anão. Tipos de efeito novos:
`alterar_tamanho` (Forma Grande) e `alterar_descanso` (o Transe do Elfo, que fecha um Descanso Longo
em 4 horas). Alvo novo: `capacidade_de_carga`, que já era valor derivado e agora pode ser alterado —
o Porte Poderoso do Golias conta um tamanho maior.

---

## O furo que o teste negativo encontrou

`magias_por_nivel` — o campo em que linhagens e legados declaram as magias dos níveis 3 e 5 — **não
é um efeito**, então o andador de efeitos do validador nunca passava por ele. Um id de magia errado
ali entrava calado, e ninguém saberia até um jogador élfico de nível 3 abrir o app e não achar
Detectar Magia.

O teste plantou `detectar_magias` (com S) e o validador deixou passar. Agora existe uma varredura
própria, em todos os catálogos e coleções, que confere id de magia e faixa de nível. É o mesmo tipo
de defeito silencioso do `efeito_por_item_escolhido` na fase 9 e do filtro booleano na fase 7:
**campo que não é efeito não era conferido por ninguém.**

---

## Divergências do livro

| onde | divergência | resolução |
|---|---|---|
| Gnomo das Rochas (p. 191) | o traço cita o truque **"Consertar"** | a entrada do cap. 7 é **Reparar**; resolvido pelo id real, com nota no traço |
| Elfo Silvestre (p. 190) | a tabela de linhagem diz **"Passos Sem Rastro"** (plural) | a magia é **Passo Sem Rastro**, como na lista do Guardião e no cap. 7 |
| Fazendeiro (p. 182) | o pacote diz **"Balde de Ferro"** | no cap. 6 o item é **Balde**; mantido o id real, com o nome impresso na nota |
| Acólito (p. 178) | o pacote traz **"Símbolo Sagrado"** | é categoria com três formas (p. 225), não item — mesma resolução do Clérigo e do Paladino |
| Drow (p. 190) e Elfo Silvestre | "**aumenta para** 36 metros" / "**aumenta para** 10,5 metros" | é substituição, não soma: `empilha: maior_valor`, com nota. Diferente da Visão Umbrosa do Guardião, que soma |

---

## Aberto

- **Dois traços ficaram como `efeito_narrativo`** por não terem primitivo: a Agilidade Pequenina
  (mover pelo espaço de criatura maior sem parar nele) e a Furtividade Natural (esconder-se
  encoberto apenas por criatura maior). Ambos dependem de geometria de combate que a base não
  modela.
- **O Transe do Elfo** tem duas partes: o Descanso Longo em 4 horas virou o primitivo
  `alterar_descanso`, mas "magia não pode forçá-lo a dormir" continua narrativo — não é imunidade à
  condição Inconsciente, e a base não tem "sono mágico" como categoria própria.
- **O dispositivo mecânico do Gnomo das Rochas** usa `fabricar_item` com CA, PV e duração
  declarados, mas o efeito que ele produz é "um efeito de Prestidigitação Arcana à escolha" — que só
  resolve quando o motor souber enumerar os efeitos daquela magia.
