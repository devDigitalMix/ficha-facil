# Fase 4 — Capítulo 6, Equipamento (p. 213–233)

Validador: **0 erros, 0 avisos**. JSON Schema: todos passam. Teste negativo: **18 defeitos
plantados, 18 pegos**.

## O que saiu

| catálogo | antes | agora |
|---|---|---|
| `itens` | 38 armas, só nome e grupo | **170 itens completos** |
| `ferramentas` | 25, só o nome | **25 com atributo, custo, teste e fabricação** |

**Os 170 itens:** 38 armas · 79 de equipamento de aventura · 13 armaduras · 10 arreios e veículos
de tração · 10 focos de conjuração · 8 montarias · 7 veículos · 5 munições.

**Contagens para conferir:** armas — 14 Simples e 24 Marciais, 28 Corpo a Corpo e 10 à Distância.
Armaduras — 3 Leves, 5 Médias, 4 Pesadas e o Escudo.

Cada arma traz dano (dado e tipo), a maestria, as propriedades **decompostas** (Arremesso com os
dois alcances em metros, Versátil com o dado alternativo, Munição com o id da munição que usa),
peso e custo. Cada armadura traz a CA como estrutura — base, se soma Destreza e qual o teto —,
Força mínima, se dá Desvantagem em Furtividade e o tempo de vestir e despir.

O custo vem em três campos: valor, moeda e **o equivalente em peças de cobre**, para o app somar e
comparar sem converter nada na hora.

## As pendências do capítulo 6 estão fechadas

**O equipamento inicial das 8 classes** estava marcado como dúvida desde o Monge, porque os ids
apontavam para um catálogo que não existia. Agora **todas as referências resolvem**, e o validador
cobra isso: item citado por uma classe que não existe no catálogo é erro.

**A Maestria em Arma do Guerreiro** escolhe do catálogo de armas, que agora está completo com a
maestria de cada uma.

**A Fabricação das ferramentas** foi extraída: **87 itens resolvidos em ids**. Os 11 que sobraram
não são itens — são descrições genéricas do próprio livro ("qualquer arma Corpo a Corpo",
"armadura Média", "Foco Arcano", "Símbolo Sagrado"). Ficam declarados em `nao_resolvidos` com o
motivo, em vez de sumirem ou virarem uma chave inventada.

## Sobre os componentes materiais das magias: ajuda menos do que parece

Você imaginou que o capítulo 6 resolveria os materiais. Fui conferir: das **69 magias detalhadas
com componente Material, só 9 citam algo que existe na tabela de equipamento** — e parte desses 9
é coincidência de palavra ("um pedaço de couro curtido" batendo com a armadura Couro). O resto são
pérolas, incenso, guano de morcego: coisas que o livro descreve em texto e nunca colocou numa
tabela de preço.

O que o capítulo 6 **realmente** resolve é a regra que importa na mesa. A p. 237 diz: material sem
custo declarado e que não é consumido pode ser substituído por **Bolsa de Componentes** ou **Foco
de Conjuração** — e os dois agora existem como itens. Gravei isso em cada magia:

```
69 magias detalhadas com material
   44 substituíveis por foco ou bolsa
   25 exigem o material de verdade (têm custo em PO ou são consumidas)
```

Na prática, o app poderá dizer "você não precisa carregar isso, seu foco cobre" em dois terços dos
casos, e avisar do custo nos outros 25.

## Três divergências do livro

**1. Nomes diferentes entre a tabela e as páginas de classe.** A tabela de Armaduras imprime
**Couro**; as classes escrevem **Armadura de Couro**. Idem Couro Batido e Acolchoada. É o mesmo
item — registrei as duas formas em `nomes_alternativos`, como fizemos com as magias.

**2. Munição no singular e no plural.** A tabela de Armas diz que o Arco Longo usa **Flecha**; a
tabela de Munição vende **Flechas**. E **Bala** é ambíguo: existem "Balas, Arma de Fogo" e "Balas,
Funda". Resolvi pelo id real, decidindo pela arma — Funda usa balas de funda, Mosquete e Pistola
usam balas de arma de fogo. **Foi o validador que pegou**: eu tinha gravado a munição como o livro
escreve e as dez referências apontavam para o vazio.

**3. Um veículo com o nome truncado.** A tabela de Veículos (p. 230) imprime **"Aeronau"**.
Parece "Aeronave" cortado, mas não invento nome no lugar do livro: ficou como está impresso, com
`revisao: duvida`. **Decisão sua** se troco para Aeronave.

E um caso de nome curto: a página do Druida (p. 92) dá **"Kit de Explorador"**, que não existe no
capítulo 6 — lá só há **"Kit de Explorador de Masmorras"** (p. 226). Tratei como o mesmo kit e
deixei o `equipamento_inicial` do Druida marcado como dúvida para você confirmar.

## Uma coisa que virou escolha em vez de item

O Clérigo começa com **Símbolo Sagrado**, que no capítulo 6 **não é um item**: é uma categoria com
três formas (Amuleto, Emblema, Relicário, p. 225). Em vez de inventar um item genérico, o
equipamento inicial dele virou uma `escolha` entre as três — que é o que acontece na mesa.

Também apareceu o primeiro item que é **duas coisas ao mesmo tempo**: o **Cajado** é arma Simples
Corpo a Corpo e Foco Arcano. Ficou como um item só, com `tambem_e`, em vez de duplicado.

## Cinco defeitos do parser, todos pegos por conferência

As tabelas do PDF quebram de jeitos criativos:

1. **Coluna colada na anterior** — "Recarga" + "Lentidão" virando `RecargaLentidão`, o que fazia a
   Besta Leve perder a maestria.
2. **Cabeçalho da tabela colado no fim de uma linha** — `Kit de Curandeiro 1,5 kg 5 POItem Peso
   Custo`. Sem tratar, o Kit de Curandeiro sumia do catálogo.
3. **Cabeçalho de ferramenta colado no fim do parágrafo anterior** — `…, VirotesFerramentas de
   Ferreiro (20 PO)`. Duas ferramentas sumiam.
4. **Créditos de artista dentro da lista de Fabricação** — "Kit de Escalada WAYNE ENGLAND".
5. **Coluna Peso vazia colada no nome** — "Antitoxina —" virando o nome do item.

Conferi as 25 ferramentas contra o catálogo que já existia: **bateram exatamente**, nenhuma faltou
nem sobrou.

## O validador ficou responsável pelo equipamento

Checagens novas, todas testadas com defeito plantado: maestria, propriedade de arma, grupo de arma
e de armadura, tipo de dano, alcance, categoria de item, arma sem dano, armadura sem CA, munição e
recipiente de munição inexistentes, atributo de ferramenta, item de fabricação inexistente,
**item citado no equipamento inicial que não existe**, peso inválido, item sem custo nem
`custo_varia`, moeda inválida e — a que mais gosto — **custo incoerente**: se um item diz 2 PO mas
declara outro valor em peças de cobre, é erro.

## Estado geral

```
8 classes · 32 subclasses · 265 características · 47 catálogos · 69 tipos de efeito
391 magias, 130 detalhadas · 8 de 8 listas de magia preenchidas
170 itens · 25 ferramentas completas · nenhuma pendência do capítulo 6
```

## Próximo passo

Faltam **261 magias** para detalhar (de Elementalismo em diante), as **quatro classes** (Bardo,
Feiticeiro, Guardião, Paladino) e os **capítulos 4 e 5** (origens, espécies, antecedentes e
talentos). O capítulo 5 é o que fecha os quatro talentos que hoje estão declarados como pendentes.
