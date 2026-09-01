# Fase 5 — As contas da ficha viram dado (cap. 1, cap. 7 e Ap. C)

Validador: **0 erros, 0 avisos**. JSON Schema: todos passam. Teste negativo: **11 defeitos
plantados, 11 pegos**. E uma verificação nova: um script que **monta o bônus de ataque lendo só o
dado**, sem nenhuma regra de D&D escrita dentro dele.

## O problema que isto resolve

Você perguntou como o app saberia somar +3 no ataque com o Arco Curto. O dataset tinha as peças —
a arma, a proficiência da classe, o bônus por nível — mas **não tinha a conta**. O backend teria
que chumbar em código que ataque à distância usa Destreza, que Acuidade deixa escolher, que
proficiência entra quando a arma passa no filtro da classe. Exatamente o que o projeto evita.

Agora tem.

## Catálogo novo: `valores_derivados` (17 itens)

Cada um traz a **fórmula em árvore**, as **parcelas rotuladas** e a **fonte**:

```
modificador_de_atributo · bonus_de_proficiencia · teste_de_atributo · salvaguarda
jogada_de_ataque_com_arma · jogada_de_ataque_magico · jogada_de_ataque_desarmado
dano_de_arma · dano_desarmado · classe_de_armadura · cd_para_evitar_sua_magia
iniciativa · percepcao_passiva · pontos_de_vida_no_nivel_1 · pontos_de_vida_por_nivel
capacidade_de_carga · atributo_de_ataque_da_arma
```

As **parcelas** são a parte que o backend vai agradecer. Em vez de devolver `+6` e o front ter que
adivinhar de onde veio, cada derivado lista os termos com rótulo e condição:

```
jogada_de_ataque_com_arma
  d20                                        sempre
  modificador de atributo                    sempre
  bônus de proficiência                      se proficiente_com_a_arma
  bônus mágico da arma                       se arma_magica
  outros bônus e penalidades                 sempre
```

É o log de proveniência que a gente tinha previsto no plano do app ("CA 17 = 10 + 3 DES + 4 SAB"),
só que definido no dado em vez de montado à mão em cada tela. O validador cobra: **parcela sem
rótulo, ou que não seja "sempre" e não diga quando entra, é erro.**

O `atributo_de_ataque_da_arma` é o item que responde a sua pergunta: corpo a corpo usa Força, à
distância usa Destreza, ataque mágico usa o atributo de conjuração — com as exceções de Acuidade
(escolha entre Força e Destreza, **o mesmo nas duas jogadas**), Arremesso (mantém o atributo da
arma) e arma improvisada (**não soma proficiência**).

## As 10 propriedades de arma saíram do texto

Estavam só com `descricao_curta` — o mesmo defeito que a varredura tirou dos catálogos de opção, e
que eu não tinha pego porque `propriedades_de_arma` estava classificada como vocabulário. **Estava
errado:** Acuidade, Pesada, Leve e Versátil são regras mecânicas.

Todas as 10 têm efeitos agora. Acuidade dá a escolha de atributo; Pesada dá Desvantagem abaixo de
13; Leve concede o ataque de Ação Bônus sem modificador no dano; Versátil troca o dado ao empunhar
com as duas mãos; Alcance dá Desvantagem além do alcance normal e impede o ataque além do máximo.

Movi `propriedades_de_arma` e `maestrias_de_arma` para fora da lista de vocabulário do validador —
agora propriedade sem efeitos é erro, como em qualquer catálogo de regra.

**Quatro ficaram com `substituir_regra` e marca de dúvida**, e quero ser claro sobre o porquê:
Duas Mãos e Versátil precisam de um primitivo de **mãos ocupadas**, Munição precisa de **inventário
consumível**, e Recarga precisa de **teto por ação**. Nenhum dos três existe no esquema ainda. Estão
declarados como dúvida em vez de fingir que estão resolvidos.

## A proficiência com armas deixou de ser string

O Ladino tinha isto:

```
"chave": "categoria:marcial+propriedade:acuidade_ou_leve"
```

Um filtro codificado em texto que nada validava e que o backend teria que interpretar com um parser
próprio. Virou filtro estruturado, e **o validador resolve contra o catálogo**:

```
monge      arma simples                              14 armas
monge      arma marcial com Leve                      3 armas
guerreiro  arma simples / arma marcial            14 / 24 armas
ladino     arma marcial com Acuidade ou Leve          5 armas
```

Filtro que não devolve nenhuma arma agora é erro — era defeito silencioso.

## A prova de que fecha

Escrevi `verificar_derivacao.py`: ele lê os catálogos e monta a conta, **sem uma linha de regra de
D&D dentro**. Até o cálculo do modificador vem da fórmula do catálogo, não de um `(valor-10)//2`
escrito no script.

```
Ladino nível 5, Destreza 16, com Arco Curto:
   d20
   modificador de atributo: DES 16 (arma a distancia)  +3
   bônus de proficiência (nível 5)                     +3
   => jogada de ataque: 1d20 +6
   => dano: 1d6 +3 perfurante

Mesmo Ladino com Machado Grande (Marcial, sem Acuidade nem Leve):
   modificador de atributo: FOR 10 (arma corpo a corpo)  +0
   bônus de proficiência: não proficiente                +0
   => jogada de ataque: 1d20 +0
```

O segundo caso é o que mostra que a coisa funciona de verdade: o script **descobriu sozinho** que
o Ladino não é proficiente com Machado Grande, porque o filtro da classe não bate com a arma.

## Estado geral

```
8 classes · 32 subclasses · 265 características · 48 catálogos · 69 tipos de efeito
124 itens de catálogo com efeitos executáveis
391 magias, 130 detalhadas · 8 de 8 listas · 170 itens · 25 ferramentas
17 valores derivados com fórmula, parcelas e fonte
```

## O que ainda o backend não consegue derivar sozinho

Sendo direto sobre o que falta, para você não descobrir na hora de implementar:

- **Mãos ocupadas** — Duas Mãos, Versátil e Escudo dependem disso, e não há primitivo.
- **Inventário consumível** — Munição gasta uma peça por ataque; nada modela isso.
- **Teto por ação** — Recarga limita a um disparo por ação mesmo com Ataque Extra.
- **CA quando há mais de um cálculo de base** — a regra ("escolha um, não some") está gravada em
  `classe_de_armadura`, mas quem oferece cada cálculo (armadura, Defesa sem Armadura do Monge, do
  Bárbaro) precisa ser reunido pelo backend na hora.

São quatro primitivos, não quatro exceções — dá para resolver de uma vez quando o backend começar.

## Próximo passo

Faltam **261 magias** para detalhar, as **quatro classes** (Bardo, Feiticeiro, Guardião, Paladino)
e os **capítulos 4 e 5**. O capítulo 5 fecha os quatro talentos hoje marcados como pendentes.
