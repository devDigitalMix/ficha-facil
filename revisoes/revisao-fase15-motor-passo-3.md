# Fase 15 — o coletor de efeitos, e o que ele achou no dataset

Feita em 2026-09-02. É o passo 3 da ordem do `PLANO-MOTOR.md`: coletor de efeitos,
condições e empilhamento. Com ele, o campo `contexto` dos personagens de ouro
**deixou de ser escrito à mão** — a ficha agora sai da construção, ponta a ponta.

`testes/rodar_todos.py`: **14 de 14 passos limpos.** O motor em 40 de 40
(`node --test`), o dataset em `validar.py` 0/0, `checar_schema.py` 76/76, os oito
testes negativos intactos e `reconstruir.py --comparar` em 62/62 geradores sem
nenhuma diferença.

---

## O caminho ficou inteiro

Antes, o motor recebia um `contexto` pronto que eu tinha escrito à mão. Agora:

```
construção  →  coletar()        percorre espécie, antecedente, classe, subclasse,
                                talentos; expande cada escolha resolvida
            →  montarContexto() decide o que cada efeito faz com a ficha, dado o ESTADO
            →  montarFicha()    as contas do livro
```

Os dois goldens continuam com o mesmo `esperado` de ontem, e batem. Isso era o teste
combinado: se a ficha mudasse quando o contexto parou de ser manual, um dos dois
lados estava errado.

## Três decisões que valem mais que o código

**Escolha não resolvida é pendência, não erro.** Um Monge de nível 1 tem seis
escolhas em aberto e nenhuma delas muda a CA. Quem exige tudo resolvido não monta
meia ficha; quem ignora em silêncio perde o "subir de nível sem esquecer nada". Elas
voltam numa lista — que **é** o checklist da Fase A, e já está sob teste:

| personagem | escolhas em aberto |
|---|---|
| Kaida, Monge 1 | 6 (a perícia do Humano, o talento do Humano, três do Iniciado em Magia e a ferramenta do Monge) |
| Torvar, Bárbaro 5 | 5 (as duas do Humano, a ferramenta do Soldado, as maestrias em arma e a perícia extra do Conhecimento Primordial) |

As maestrias em arma e a perícia do Conhecimento Primordial são exatamente o tipo de
coisa que se esquece ao subir de nível. Elas aparecem sozinhas.

**Efeito aninhado não é achatado.** Os efeitos dentro da Fúria só valem em Fúria.
Cada efeito coletado carrega as **portas** que precisam estar abertas, e o estado diz
quais estão. Achatar faria o Bárbaro andar por aí com Resistência a dano Cortante.

**Subclasse e talento não têm campo próprio na construção.** No dado eles são
escolhas como qualquer outra, e o efeito que produzem — `conceder_subclasse`,
`conceder_talento` — é quem puxa a entidade inteira. Um campo `subclasse` à parte
seria a mesma informação em dois lugares, e um deles acabaria mentindo.

## O defeito que o motor achou no dataset

Este é o achado da fase, e ele é do tipo que só aparece quando alguém tenta **usar** o
dado.

Os 16 antecedentes apontavam a escolha de aumento de atributo para
`modos_de_aumento_de_atributo` — que é o catálogo do **talento** Aumento no Valor de
Atributo, com "um atributo em +2" e "dois atributos em +1".

A regra do antecedente é outra. Página 177:

> "Um antecedente apresenta três dos valores de atributo do seu personagem. Aumente
> um em 2 e outro em 1, ou aumente todos os três em 1."

As duas se parecem e não são a mesma coisa. **"Todos os três em 1" não existia no
catálogo**, e "dois atributos em +1" não é o que o antecedente oferece. Na prática:
um personagem legítimo — +1 em Destreza, Constituição e Sabedoria pelo Guia — não
tinha como ser montado, e um ilegítimo tinha.

Ninguém pegou antes porque **nada consumia a escolha**. O validador confere se o
catálogo referenciado existe, e ele existe. Foi preciso alguém tentar montar um
personagem para a diferença aparecer — que é o argumento do `PLANO-MOTOR.md` §8 na
prática: até ontem, tipo de efeito nenhum jamais tinha sido executado.

Consertado em `geradores/gerar_ajustes_aumento_de_antecedente.py`: catálogo próprio
`modos_de_aumento_do_antecedente`, com os dois modos certos e a página, e os 16
antecedentes repontados.

**De brinde, um disfarce a menos.** Os modos do talento carregavam um
`efeito_narrativo` de fachada cujo texto dizia "os efeitos reais estão em
efeitos_nomeados do talento" — placeholder para satisfazer a regra de que opção tem
efeitos. O item nunca foi opção: é vocabulário, o nome de uma forma de distribuir. Os
dois catálogos de modo passaram a VOCABULÁRIO no validador e a fachada saiu.

## Dois geradores que não podiam ser rodados duas vezes

`gerar_normalizacao_vocabulario.py` e o ajuste novo falhavam ao rodar sobre dado já
tratado: a checagem "toda origem declarada tem de aparecer" não distinguia *tabela
mentindo* de *já foi feito*. Agora distinguem — casar **em parte** continua sendo erro
de build; não casar em **nada** quer dizer que já rodou, e sai limpo. Sem isso o
`reconstruir.py` não podia rodá-los.

## A asserção que eu escrevi fraca

Depois que tudo passou, quebrei o motor de propósito. Três defeitos plantados:

| defeito plantado | reprovou? |
|---|---|
| escolha não resolvida some sem virar pendência | sim, 4 testes |
| aumentos de atributo aplicados depois do resto | sim, 8 testes |
| ignorar as portas (achatar os efeitos aninhados) | **não** |

O terceiro passou. O teste "o Bárbaro em Fúria não é o mesmo" comparava a
**quantidade** de efeitos incidentes, e mesmo com as portas ignoradas o Bárbaro parado
ainda ficava com menos que o furioso — por causa das condições. Contagem é asserção
fraca.

Trocada por uma literal: **parado, nenhum efeito atrás de porta pode incidir.** Com
ela, o defeito reprova. Vale como lição de método: o teste de mutação não serve só
para achar buraco no código — serve para achar teste que só parece que confere.

## O que vem

Passo 4: o **motor de escolha**. Hoje as escolhas resolvidas são aceitas como vêm; o
passo 4 é quem oferece as opções (resolvendo `de.chaves`, `de.filtro`,
`de.todo_o_catalogo`, `de.de_variantes` e os filtros de runtime) e recusa a inválida.
Ele destrava criar personagem e subir de nível — a Fase A inteira.

Também ficou visível o que ainda não é consumido: 14 tipos de efeito coletados no
Bárbaro parado e 22 em Fúria não entram na ficha estática (dano adicional,
resistências, vantagem, recursos com recarga). Não é dívida escondida — sai em
`nao_consumidos`, e é a fila do passo seguinte.

Continuam de antes: os `efeito_narrativo`, a releitura das 391 paráfrases de magia e
das 112 de criatura, e as três decisões do `BACKLOG.md` §B6.
