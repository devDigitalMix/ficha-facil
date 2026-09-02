# Fase 7 — Bardo e Feiticeiro

Validador: **0 erros, 0 avisos**. JSON Schema: **58 arquivos, todos passam**. Teste negativo:
**18 defeitos plantados, 18 pegos**. `verificar_derivacao.py`: continua fechando a conta lendo só
o dado.

```
10 de 12 classes · 40 subclasses · 320 características · 53 catálogos · 80 tipos de efeito
```

## Bardo (p. 59-67)

26 características, 4 colégios (Bravura, Dança, Conhecimento, Glamour), cada um com
características em 3, 6 e 14.

O que exigiu esquema novo foram os **Segredos Mágicos** (nível 10). O acesso a listas alheias não
é uma escolha nova nem um punhado de chaves soltas: é o **filtro da escolha que já existe** que se
alarga. Então `expandir_opcoes_de_escolha` ganhou uma segunda forma — além de `chaves`, aceita
`filtro` — e a característica passa a dizer:

```json
{"tipo": "expandir_opcoes_de_escolha", "escolha_id": "bardo_preparadas",
 "catalogo": "magias", "modo": "substitui_filtro",
 "filtro": {"lista": ["bardo", "clerigo", "druida", "mago"], "nivel_minimo": 1,
            "circulo_com_espaco_disponivel": true}}
```

O validador resolve as duas formas, então filtro que não devolve magia nenhuma é erro, não
silêncio.

A **Inspiração de Bardo** virou catálogo (`usos_da_inspiracao_de_bardo`) em vez de três textos
soltos: o uso padrão vem da classe, e o Colégio da Bravura acrescenta o defensivo e o ofensivo. O
catálogo está marcado `expansivel_por_subclasse`.

## Feiticeiro (p. 103-114)

29 características, 4 origens (Aberrante, Dracônica, Mecânica, Selvagem). **Atenção a um detalhe
que difere das outras classes: o Feiticeiro ganha característica de subclasse em 3, 6, 14 e 18** —
tem o nível 18 que a maioria não tem. Isso agora está declarado na classe
(`niveis_de_caracteristica_de_subclasse`) e cobrado pelo validador.

### O que era novo de verdade: modificar a magia no ato de conjurar

Até aqui, nada no dataset mexia numa magia **enquanto ela é conjurada**. A Metamagia mexe em seis
coisas diferentes, e nenhuma cabia nos tipos que existiam. Entraram cinco tipos novos —
`alterar_tempo_de_conjuracao`, `alterar_alcance_da_magia`, `alterar_duracao_da_magia`,
`alterar_circulo_efetivo`, `dispensar_concentracao` — e um catálogo, `opcoes_de_metamagia`, com as
10 opções e o **custo em Pontos de Feitiçaria declarado por opção**.

Duas opções (Buscadora e Potencializada) dizem explicitamente que empilham com outra Metamagia na
mesma conjuração; elas trazem `empilha_com_outra_metamagia: true`, e o teto normal de 1 opção por
magia está na própria escolha. A Feitiçaria Encarnada (nível 7) sobe esse teto para 2 enquanto a
Feitiçaria Inata estiver ativa, usando `alterar_quantidade_de_escolha` — não uma exceção no código.

E porque o catálogo declara `recurso: "pontos_de_feiticaria"`, o validador passou a **cobrar o
custo**: opção sem `custo_em_pontos_de_feiticaria`, ou com custo zero, é erro. Testei tirando o
custo da Magia Sutil — pegou.

### Os Pontos de Feitiçaria e a troca nos dois sentidos

`fonte_de_magia` declara o recurso (`coluna:pontos_de_feiticaria`, recarga no Descanso Longo) e as
**duas conversões**, cada uma com seu custo de ação:

- espaço → pontos, livre, pontos iguais ao círculo do espaço;
- pontos → espaço, Ação Bônus, com a tabela de custo por círculo e o **nível mínimo de Feiticeiro**
  de cada linha, teto no 5º círculo, e `espaco_criado.expira_em: "descanso_longo"`.

A tabela de custo saiu do livro inteira (2/3/5/6/7 pontos para os círculos 1 a 5; níveis mínimos
2/3/5/7/9). Sem ela o backend teria de chumbar a conta.

### A tabela de 1d100 é catálogo de opção, não texto

O **Surto de Magia Selvagem** tem 25 linhas. Poderia ter virado um bloco de texto — só que no
nível 18 o **Surto Controlado deixa o jogador ESCOLHER a linha**, e aí ela deixa de ser sorteio e
vira escolha de verdade. Então virou catálogo com efeitos por linha, cada uma com sua
`faixa_1d100`, e a última (97–00) marcada `escolhivel_no_surto_controlado: false`, que é
exatamente o que o livro exclui.

Disso saiu uma checagem nova que vale para qualquer tabela aleatória: **as faixas têm de cobrir o
dado inteiro, sem buraco e sem sobreposição**. Testei apagando uma linha (buraco de 49 a 52),
sobrepondo duas e encurtando a última para 99 — os três foram pegos.

Sendo honesto sobre o conteúdo dessas 25 linhas: **19 têm efeito mecânico de verdade** (cura,
dano, condições, resistência, teleporte, ação adicional, dano maximizado, +2 de CA). As outras 6
dependem de decisão do Mestre ou de uma subtabela aleatória — a criatura amigável de 1d4, a magia
aleatória de 1d10, o desvio astral. Nessas eu gravei o efeito narrativo **com os dados
estruturados junto** (a tabela 1d10 traz os ids das magias, não os nomes soltos), para o app poder
sortear e apontar para a magia certa mesmo sem resolver o efeito sozinho.

### Um achado no meio do caminho

Modelando a **Implosão de Distorção** (Aberrante, nível 18) eu precisei de um puxão como efeito.
Ao criar `movimento_forcado`, ficou claro que os **empurrões que já estavam no dataset estavam
escritos como texto** — `efeito_narrativo` com a frase "empurra o alvo até 4,5 metros". Eram dois:
a Técnica da Mão Espalmada do Monge e a Ira do Mar do Druida do Círculo do Mar. Migrei os dois
(`gerar_ajustes_movimento_forcado.py`), para a regra não ficar em dois formatos. O validador agora
cobra `direcao` ∈ {empurrar, puxar} e `distancia_m` ou `destino`.

### Onde eu simplifiquei uma conta do livro, e por quê

A **Resiliência Dracônica** diz "seus PV máximos aumentam em 3, e aumentam em 1 sempre que você
atinge outro nível de Feiticeiro". Como a característica chega no nível 3, isso é **exatamente o
nível de Feiticeiro**: 3 no nível 3, 4 no nível 4, 15 no nível 15. Gravei a conta fechada
(`["nivel_classe:feiticeiro"]`) com a nota dizendo de onde ela veio. Se você preferir as duas
parcelas separadas para o log de proveniência, é uma linha para mudar — me diga.

## O que o Schema pegou que o validador não pegava

Escrevi `checar_schema.py`, que antes era passo solto que eu rodava de memória a cada lote. Ele
achou coisa de verdade **no Bardo, já entregue**:

- as 4 subclasses do Bardo não declaravam `niveis_de_caracteristica`, campo que o schema exige —
  as 4 do Feiticeiro também não. Preenchidos ([3,6,14] e [3,6,14,18]);
- a **Evasão Liderada** (Colégio da Dança) tinha uma condição composta misturando `todas` e `nao`
  no mesmo objeto — o mesmo defeito que eu tinha corrigido em outros lugares e deixei escapar
  aqui. Normalizada para um operador por objeto.

E o próprio validador ganhou uma correção que valia para todo o dataset: **`resolver_filtro`
ignorava filtros por campo booleano**. `{"escolhivel_no_surto_controlado": true}` era simplesmente
descartado, e um filtro que não devolvesse nada nenhum passaria batido. Agora qualquer campo
simples que os itens declarem é filtrável, e filtro vazio volta a ser erro. Foi o único defeito do
teste negativo que passou na primeira rodada.

## Checagens novas no validador

| checagem | o que pega |
|---|---|
| cobertura de tabela aleatória | buraco, sobreposição ou faixa que não fecha no dado |
| catálogo com `recurso` | item sem custo declarado, ou com custo zero |
| `movimento_forcado` | direção fora de {empurrar, puxar}, ou sem distância nem destino |
| `rolar_na_tabela` | apontar para catálogo que não declara `dado_da_tabela` |
| níveis de subclasse | subclasse divergindo da classe, ou característica num nível não declarado |
| filtro por campo direto | filtro que não devolve nenhum item (antes era ignorado) |

## O que falta do livro

- **Duas classes**: Guardião (p. 117) e Paladino (p. 167).
- **Capítulos 4 e 5** — origens, espécies, antecedentes e talentos. O capítulo 5 fecha os quatro
  talentos hoje marcados como pendentes.
- Varredura do glossário atrás de termos sem marcador de colchete.
- Duas decisões suas ainda abertas: "Aeronau" (p. 230), que parece ser "Aeronave" truncado, e o
  "Kit de Explorador" do Druida (p. 92), que tratei como "Kit de Explorador de Masmorras".
