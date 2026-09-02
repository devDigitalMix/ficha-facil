# Fase 9 — Capítulo 5: Talentos

Validador: **0 erros, 0 avisos**. JSON Schema: **61 arquivos, todos passam**. Teste negativo:
**16 de 16** (lote novo), **18/18** e **11/11** sem regressão nos anteriores.
`verificar_derivacao.py`: continua fechando.

```
75 talentos — origem 10 · geral 43 · estilo de luta 10 · dádiva épica 12
NENHUM talento pendente. As quatro categorias fechadas.
```

## As quatro pendências, fechadas

| pendência | como ficou |
|---|---|
| **Aumento no Valor de Atributo** | Escolha entre "+2 num atributo" e "+1 em dois", cada uma com o teto de 20 declarado |
| **Dádiva da Proeza em Combate** | Talento completo: um erro de ataque vira acerto, uma vez até o início do seu próximo turno |
| **Dádiva do Ataque Irresistível** | Dano Contundente/Cortante/Perfurante ignora Resistência; num 20 natural soma o **valor** do atributo aumentado (não o modificador) |
| **Dádiva Épica** | **Deixou de ser talento.** Era um marcador que eu inventei para as classes poderem apontar antes do capítulo 5. Agora a categoria `epico` existe com 12 talentos de verdade, e a característica de nível 19 escolhe dentro dela |

## O que o capítulo obrigou a arrumar no esquema

### 1. O aumento de atributo embutido no talento

Quase todo talento Geral traz "Aumente seu valor de Força **ou** Destreza em 1, até no máximo
20". Isso é uma **escolha**, não um número — modelada como `escolha` sobre o catálogo de
atributos, com o teto declarado (20 nos Gerais, **30 nas Dádivas Épicas**). O validador agora
recusa `aumento_atributo` sem teto: o livro sempre dá um.

### 2. Duas regras de Estilo de Luta que eu tinha deixado como texto

Isso é de um lote antigo e eu não tinha percebido:

- **Combate com Armas Grandes** — "trate qualquer 1 ou 2 num dado de dano como 3" estava em
  `efeito_narrativo`, um parágrafo para o backend interpretar. Virou
  `tratar_dado_de_dano_minimo`, que o Adepto Elemental deste capítulo também usa (1 vira 2).
- **Combate com Duas Armas** — "soma o modificador ao dano do ataque adicional" também era texto.
  Virou `modificador` com a condição estruturada.

### 3. Pré-requisito virou dado, não frase

Todo talento declara `pre_requisitos` como lista estruturada — nível de personagem, valor de
atributo com o mínimo, característica, treinamento com armadura. **Lista vazia quando não há**,
porque silêncio não é o mesmo que "nenhum": o validador cobra o campo, e cobra que todo talento
Geral declare nível 4 e toda Dádiva Épica declare nível 19.

## Tipos de efeito novos (16)

Nenhum destes cabia no que existia:

```
tratar_dado_de_dano_minimo   ignorar_resistencia          ignorar_cobertura
alterar_custo_de_acao        fabricar_item                desconto_em_compra
conceder_inspiracao_heroica  trocar_iniciativa            transformar_erro_em_acerto
conceder_maestria_de_arma    nao_gastar_espaco_de_magia   redirecionar_dano
redirecionar_ataque          aplicar_veneno               ignorar_propriedade_de_arma
alterar_teto_de_modificador_na_ca
```

`alterar_custo_de_acao` é o que faz Analítico e Mente Aguçada funcionarem sem exceção em código:
a ação Procurar (ou Analisar) passa a caber numa Ação Bônus, apontando para a ação real do
catálogo — e o validador cobra que a ação e o custo existam.

Também entraram **3 alvos** (`dado_de_dano_da_arma`, `dado_de_dano_do_ataque_desarmado`,
`dado_de_cura`) e **2 impedimentos** (`desvantagem_por_inimigo_adjacente`,
`desvantagem_por_alcance_maximo`) — esses dois resolvem, em campo, os vários "estar a 1,5 metro
de um inimigo não impõe Desvantagem" que aparecem em três talentos diferentes.

## Três catálogos auxiliares

Onde o livro dá uma escolha de duas opções dentro do talento, virou catálogo em vez de texto:
`modos_de_aumento_de_atributo`, `efeitos_do_ataque_em_investida` (Agressor: +1d8 no dano **ou**
empurrar 3 m) e `efeitos_do_golpe_de_escudo` (Mestre em Escudos: empurrar **ou** derrubar).

## Onde ficou texto, e por quê

**11 efeitos ainda são `efeito_narrativo` nos 75 talentos.** São os que dependem de julgamento na
mesa ou de um primitivo que a base não tem: levantar-se de Caído por 1,5 m, saltar com corrida
curta, mimetismo do Ator, Saque Rápido, componentes Somáticos com as mãos ocupadas, "errar
escondido não revela sua posição", Correr em Terreno Difícil, e o Socar e Imobilizar. Estão
marcados, não escondidos — se algum deles importar para o app, me diga qual e eu modelo o
primitivo.

## Duas coisas que apareceram no caminho

**O gerador do Guerreiro podia desfazer este capítulo.** `gerar_guerreiro_catalogos.py` reescrevia
o cabeçalho de `talentos.json` para "PARCIAL" e recriava o marcador `dadiva_da_proeza_em_combate`.
Rodado fora de ordem, apagava o capítulo 5. Tirei essa parte: agora ele só mantém os dez de Estilo
de Luta, e o dono do catálogo é `gerar_talentos.py`.

**Um furo no próprio validador.** O andador pulava `efeito_por_item_escolhido` inteiro — e como o
aumento de atributo mora exatamente ali, um `aumento_atributo` sem teto passava batido. Foi o
único defeito que escapou na primeira rodada do teste negativo. Corrigido: o efeito entra na lista
de efeitos vistos, mesmo que a checagem de chaves continue com a escolha-mãe.

O validador também ganhou duas correções que valem para tudo: `alterar_dano` agora aceita tipo de
dano derivado (`mesmo_do_ataque`), e filtro por `escola`, `categoria` ou `classe` aceita **lista**
de valores — sem isso, "magia de Ilusão ou Necromancia" resolvia para vazio.

## Checagens novas

| checagem | o que pega |
|---|---|
| categoria de talento | fora de origem/geral/estilo_de_luta/epico |
| `pre_requisitos` | campo ausente; tipo desconhecido; atributo inexistente; mínimo faltando; talento Geral ou Épico sem nível declarado |
| `aumento_atributo` | sem teto, ou com atributo que não existe |
| `alterar_custo_de_acao` | ação ou custo fora do catálogo |
| `ignorar_cobertura` | grau de cobertura inventado |
| `ignorar_resistencia` | sem tipo de dano, ou com tipo inventado |

## Estado geral

```
10 de 12 classes · 40 subclasses · 320 características · 56 catálogos · 96 tipos de efeito
391 magias · 170 itens · 19 valores derivados · 75 talentos
```

Falta do livro: **Guardião** (p. 117), **Paladino** (p. 167) e o **capítulo 4** — origens,
espécies e antecedentes.

Uma nota de passagem: a legenda da p. 212 usa "aeronau" no mesmo sentido em que o texto ao lado
usa "nave aérea". Isso reforça que o "Aeronau" da p. 230 é decisão do tradutor, não truncamento —
mas continua sendo pergunta sua se o app deve mostrar esse nome.
