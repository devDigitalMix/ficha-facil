# Fase 16 — o motor de escolha, e a fase 15 consertada

Feita em 2026-09-02. Duas coisas: o conserto do que a pergunta "o que é isso de
porta?" revelou, e o passo 4 do `PLANO-MOTOR.md` — o motor de escolha.

`testes/rodar_todos.py`: **15 de 15 passos limpos.** Motor em 56 de 56, dataset em
`validar.py` **0 erros e 0 avisos**, `checar_schema.py` 76/76, os nove testes
negativos e `reconstruir.py --comparar` em 66/66 geradores sem diferença.

---

## Primeiro: as portas estavam erradas

"Porta" é o nome que dei, na fase 15, para o seguinte: alguns efeitos vêm dentro de
outros, e os que estão dentro da Fúria só valem em Fúria. Cada efeito coletado
carrega as portas que precisam estar abertas, e o estado diz quais estão.

A regra que escrevi era "todo aninhamento é uma porta, com o nome do `id` do pai ou,
na falta dele, do `tipo`". Contando: **81 efeitos aninham, e 56 deles são
`melhorar_caracteristica`**. Duas coisas ruins de uma vez:

1. Sem `id`, as 56 caíam na mesma porta chamada `melhorar_caracteristica`. Abrir uma
   abriria as 56.
2. Pior, e é o que acontecia: **porta fechada por padrão = as 56 nunca incidiam.**
   Melhoria de característica sumia calada.

E o erro é mais fundo que a colisão de nome: `melhorar_caracteristica` **não é uma
porta**. O `alvo` dela diz a QUAL característica os efeitos se aplicam — é
redirecionamento, não condição. A Fúria liga e desliga; "melhorar Torrente de Golpes"
não.

Nenhum dos dois personagens de ouro pegava, porque nenhum tem melhoria que mexa em CA
ou Pontos de Vida.

**O conserto não foi adivinhar melhor: foi parar de adivinhar.** O
`catalogos/tipos_de_efeito.json` passou a declarar, para cada um dos nove tipos que
aninham, `efeitos_aninhados: "condicionados"` ou `"estruturais"`. O motor lê. O
validador cobra a declaração, cobra `id` em quem condiciona, e cobra que dois
condicionantes não tenham o mesmo id. Cinco condicionantes não tinham id e ganharam o
da entidade que os carrega.

`testes/teste_negativo_efeitos_aninhados.py`: 5 de 5 defeitos pegos, mais um caso de
folga — efeito estrutural **não** precisa de id, e cobrar isso dele seria voltar ao
defeito pelo outro lado.

## O passo 4: quem oferece as opções

Até ontem a escolha resolvida era aceita como viesse, e a pendente era só um rótulo.
Agora `motor/src/escolha.ts` resolve o campo `de` — `chaves`, `todo_o_catalogo`,
`filtro`, `de_variantes`, `tambem_de` — e devolve a lista real. O checklist de subir
de nível deixou de ser uma lista de nomes e virou a tela:

```
[ ] Escolha uma perícia (1) — 18 opções          <- espécie humano / habil
[ ] Escolha um talento de Origem (1) — 10 opções <- espécie humano / versatil
[ ] Escolha dois truques (2) — 13 opções         <- antecedente guia / talento
[ ] Escolha uma ferramenta (1) — 18 opções       <- classe monge
```

**Os filtros de runtime finalmente rodam.** O `validar.py` lista onze chaves em
`FILTROS_DE_RUNTIME` e não as avalia, de propósito: dependem do personagem, não do
catálogo. O motor avalia — pré-requisito de talento, nível de desafio da Forma
Selvagem, ausência de voo, proficiência que o personagem já tem. As que dependem de
estado de jogo que o motor ainda não guarda (espaço de magia gasto, especialização)
voltam em `nao_avaliados`, ditas em voz alta em vez de recortar errado em silêncio.

**Variável de escolha.** Uma escolha pode definir uma variável que outra lê: o
Iniciado em Magia escolhe a lista, e os truques saem daquela lista. Sem isso o app
ofereceria os 34 truques do jogo no lugar dos 13 do Druida. E uma escolha que
`depende_de` outra ainda não feita volta **bloqueada**, dizendo de qual — uma lista
completa ali seria pior que uma lista vazia.

**E ele recusa.** Escolher fora das opções, escolher de menos, escolher a mesma coisa
duas vezes, ou trazer uma escolha resolvida que este personagem nem tem: tudo vira
`problemas`, com a queixa por extenso. Não lança na primeira — quem monta personagem
quer ver todos os defeitos de uma vez.

## Três defeitos que o motor de escolha achou no dado

Ligar o motor é o que faz o dado ser usado, e usar é o que acha defeito.

**1. Cinquenta e três escolhas sem id.** Todas em `talentos.json`, todas o mesmo
"Escolha o atributo a aumentar" das Dádivas Épicas. Sem id, uma escolha não pode ser
resolvida (a construção guarda a resposta por id), não entra no checklist, e duas
iguais em talentos diferentes viram a mesma. Cada uma ganhou
`<id do talento>_atributo`, e o validador passou a cobrar id de toda escolha.

**2. Quatro escolhas com uma opção só.** "Escolha um tipo de Kit de Jogos: 1 opção."
O Kit de Jogos e o Instrumento Musical são categorias com `variantes`, e é entre as
variantes que se escolhe — as escolhas de Artista, Guarda, Nobre e Soldado filtravam
pelo id da categoria sem pedir `de_variantes`. O padrão certo já existia desde a
fase 7 em `bardo_instrumentos`; esses quatro ficaram para trás. Ninguém pegou porque
o validador cobrava "o filtro devolve algo", e devolvia: devolvia a categoria.

**3. Nove talentos com escolha que não é escolha.** A regra nova — *escolha tem de
ter o que escolher* — pegou de brinde nove talentos que pediam para escolher um
atributo entre um só. Ator não deixa escolher: o livro diz Carisma. Viraram
`aumento_atributo` direto, e o checklist parou de perguntar o que não é decisão de
ninguém.

A regra ficou no validador: oferecer **menos** que a quantidade pedida é erro;
oferecer **exatamente** a quantidade é aviso, com uma folga declarada para escolha
`reescolhivel`, que pode ter uma opção hoje e mais depois (a Inspiração de Bardo ganha
usos por melhoria de característica).

## O teste de mutação achou dois testes meus que não provavam nada

Quatro defeitos plantados no motor de escolha. Três reprovaram na hora. O quarto —
**ignorar os pré-requisitos de talento** — passou, e passou **duas vezes**:

| versão do teste | por que não provava nada |
|---|---|
| "o talento de Origem do Humano não pode oferecer o Aumento no Valor de Atributo" | o recorte já era feito pela **categoria**; o filtro de pré-requisito nunca chegava a morder |
| "a escolha de talento do nível 4 não pode oferecer talento de nível 19" | as Dádivas Épicas são categoria `epico`, e a categoria de novo já as excluía |

A terceira versão olha o que de fato barra: Torvar tem Inteligência 8, Sabedoria 12 e
Carisma 10, então todo talento que exige 13 num deles está fora. E ela carrega uma
asserção a mais — **se nenhum talento tiver sido barrado, o teste falha**, porque um
teste que passa por vacuidade é pior que teste nenhum.

É a segunda fase seguida em que a mutação encontra asserção fraca em vez de código
errado. Vale registrar como método: rodar a suíte verde não diz nada; quebrar o motor
e ver o que **não** reprova, diz.

## Dois geradores que não podiam rodar duas vezes

O ajuste dos antecedentes e o do vocabulário falhavam ao rodar sobre dado já tratado:
a checagem "toda origem declarada tem de aparecer" não distinguia *tabela mentindo* de
*já foi feito*. Agora distinguem — casar em **parte** continua erro de build; não casar
em **nada** quer dizer que já rodou, e sai limpo.

## O que vem

Passo 5: o **backend**, com os endpoints da §7 do plano. O motor já entrega tudo o que
eles precisam devolver — ficha com proveniência, checklist com opções, problemas — por
uma porta só, `montar(construcao, estado)`.

Antes disso vale um terceiro personagem de ouro: um **conjurador**. Os dois atuais não
exercitam preparação de magia, espaços por círculo nem o filtro
`circulo_com_espaco_disponivel`, que hoje volta em `nao_avaliados`. O Clérigo de
nível 5 é o candidato — é o nível mais baixo em que uma classe base melhora a própria
característica (Fulminar Mortos-Vivos), então ele testa o conserto das portas na ficha
inteira e não só na coleta.

Continuam de antes: os `efeito_narrativo`, a releitura das 391 paráfrases de magia e
das 112 de criatura, e as três decisões do `BACKLOG.md` §B6.
