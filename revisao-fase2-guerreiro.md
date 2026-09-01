# Fase 2b — Guerreiro (cap. 3, p. 127–135)

Validador: **0 erros, 0 avisos**. JSON Schema: todos os arquivos passam.

## O que saiu

| coleção | antes | agora |
|---|---|---|
| `classes.json` | 1 | **2** (Monge, Guerreiro) |
| `caracteristicas.json` | 42 | **78** |
| `subclasses.json` | 4 | **8** |
| catálogos | 26 | **31** |

Catálogos novos: `manobras` (**20**), `talentos` com a categoria **Estilo de Luta completa (10)**,
`estados` (3), `itens` parcial (**38 armas**), `listas_de_magia` (1).

**Contagens para conferir:** d10 · salvaguardas Força e Constituição · atributo primário Força **ou**
Destreza · subclasse em **3, 7, 10, 15 e 18** · 4 subclasses · 20 manobras · 10 talentos de Estilo de
Luta · Recuperar Fôlego 2/3/4 · Maestria em Armas 3/4/5/6.

## O Guerreiro estreou o que faltava do esquema

Três tipos de efeito do v1 original, previstos lá na Fase 0 e nunca usados, finalmente rodaram:

- **`conceder_slot`** e **`preparar_magias`** — no Cavaleiro Místico, com a tabela Conjuração inteira
  (níveis 3 a 20, magias preparadas e espaços por círculo) gravada como dado.
- **`desbloquear_magias`** de verdade — apontando para a lista do Mago por **filtro**, não por lista
  de chaves. Quando o capítulo 7 chegar, a escolha passa a funcionar sozinha, sem eu reeditar nada.

Também estreou `recurso_com_recarga` com **dado** e com **recarga assimétrica** — Recuperar Fôlego
devolve *um* uso no Descanso Curto e *todos* no Longo; os Dados de Energia Psiônica do Combatente
Psíquico fazem o mesmo, e ainda escalam de d6 a d12 por tabela própria.

## Três coisas que o validador me obrigou a arrumar

Não são detalhes de arrumação — eram erros de modelagem que só apareceram com a segunda classe:

**1. "Ataque Extra" existe em Monge e Guerreiro, com texto idêntico.** Eu tinha criado uma cópia por
classe e o validador acusou id duplicado. Virou **característica genérica**, concedida por cada
classe no nível da própria progressão, com um campo `concedida_por` listando classe, nível e página.
Isso vai importar de verdade na fase de multiclasse, onde Ataque Extra não acumula.

**2. Mesmo problema, maior, em três características compartilhadas.** Aumento no Valor de Atributo,
Dádiva Épica e o marcador de subclasse estavam presos ao Monge e carregando *os níveis do Monge* —
mas o Guerreiro concede ASI em 4/6/8/12/14/16 e subclasse em 3/7/10/15/18. Tornei as três genéricas e
**tirei os níveis de dentro delas**: agora os níveis vivem só na progressão de cada classe, que passa
a ser a única fonte da verdade. Dádiva Épica ganhou `recomendado_por_classe`, porque o livro
recomenda talentos diferentes (Ataque Irresistível para o Monge, Proeza em Combate para o Guerreiro).

**3. Maestria em Arma escolhe de um catálogo que não existia.** Criei `itens.json` parcial com as
**38 armas** da tabela do capítulo 6 — só nome, grupo e alcance, que é o que a escolha precisa
referenciar. Dano, propriedades, maestria, peso e custo entram na fase do capítulo 6.

## Uma lacuna minha da Fase 1

**"Sangrando" me escapou.** É um termo do glossário (p. 375) — *metade ou menos dos Pontos de Vida* —
e o Sobrevivente do Campeão depende dele. Na Fase 1 eu varri o glossário filtrando pelos marcadores
entre colchetes ([Condição], [Ação], [Risco]), e Sangrando não tem marcador nenhum. Criei o catálogo
`estados.json` com ele, mais Estável e Surpresa, que estavam na mesma situação.

Vale um pente-fino no glossário atrás de outros termos sem marcador antes de fecharmos o dataset —
posso fazer isso num lote curto quando você quiser.

## Uma dúvida de leitura

**Manobra "Gato Por Lebre".** Na extração do PDF, o parágrafo *"Jogue o Dado de Superioridade. Até o
início do seu próximo turno, você ou a outra criatura (à sua escolha) adquire um bônus de CA igual ao
número do resultado"* aparece solto entre "Gato Por Lebre" e "Golpe do Comandante", por causa da
quebra de coluna. Li como continuação de Gato Por Lebre — é o que faz sentido mecânico (a manobra
gasta um dado mas, sem isso, não faria nada com o resultado) e alfabético. Marquei `duvida`:
**confere no livro impresso se esse parágrafo é mesmo parte de Gato Por Lebre.**

## Referências ainda pendentes (todas declaradas)

- `equipamento_inicial` do Guerreiro: `duvida`, ids de item dependem do cap. 6 (mesma situação do Monge).
- `maestria_em_arma`: `duvida`, aponta para o catálogo parcial de itens.
- `listas_de_magia/mago`: existe como chave com `"preenchida": false`.

## Verificação

Rodei o motor de mentirinha para um Guerreiro nível 10 Cavaleiro Místico e conferi que a subclasse
entra em 3, 7 e 10 sem atropelar as características de classe dos mesmos níveis.

Teste negativo com cinco defeitos plantados — manobra apontando para condição fantasma, Guerreiro
concedendo característica do Monge, subclasse sem característica num nível marcado, escolha pedindo
99 manobras de um catálogo de 20, e a órfã resultante: **pegou os cinco.**

## Próximo passo

Sugiro o **Bruxo** (p. 69) ou o **Mago** (p. 147). O Mago preenche a lista de magias que o Cavaleiro
Místico já aponta — fecharia essa pendência. O Bruxo é o caso mais esquisito de conjuração do livro
(espaços de Pacto, que recarregam em Descanso Curto e sobem de círculo juntos) e testaria o
`conceder_slot` no limite. Se o objetivo é destravar pendências, Mago; se é achar buraco no esquema
cedo, Bruxo.
