# Fase 6 — Capítulo 7 completo e os quatro primitivos

Validador: **0 erros, 0 avisos**. JSON Schema: todos passam. Teste negativo: **17 defeitos
plantados, 17 pegos** (12 de magia, 5 dos primitivos). `verificar_derivacao.py`: continua fechando
a conta lendo só o dado.

## Primeiro, corrigindo o que eu disse

Eu tinha dito que faltavam quatro primitivos no esquema, como se fossem trabalho do backend.
**Revendo, três dos quatro eram trabalho de dado que eu tinha adiado** — e o quarto era metade e
metade. O backend precisa aplicar a regra, mas quem diz quantas mãos uma arma ocupa, quanta munição
um ataque gasta e quantos disparos cabem numa ação é o dado. Deixar isso para o código seria
devolver a regra para o lugar de onde a gente vem tirando ela.

Os quatro estão resolvidos:

| primitivo | como ficou |
|---|---|
| **mãos ocupadas** | 49 itens declaram `maos_ocupadas`; arma Versátil traz `maos_alternativas` com o dado maior para duas mãos |
| **consumo de munição** | 9 armas declaram `consumo` com o id da munição, quanto gasta por ataque e a recuperação depois do combate |
| **teto por ação** | 6 armas com Recarga declaram `limite_por_acao` |
| **cálculos de CA concorrentes** | 15 cálculos de CA base — armaduras e as Defesas sem Armadura — marcados com `concorre_como`, para o backend juntar os candidatos e o jogador escolher um |

As quatro propriedades saíram de `substituir_regra` (a saída de emergência) para um tipo novo e
específico: **`declara_campo_no_item`**. E isso virou checagem: **item que tem a propriedade e não
traz o campo é erro**. Testei tirando o `consumo` do Arco Longo — pegou.

## Capítulo 7 completo

| | antes | agora |
|---|---|---|
| magias detalhadas | 130 | **391 — todas** |

**Contagens para conferir.** Por círculo, do 0 ao 9: **34/64/63/52/41/48/34/21/18/16**. Dentro
delas: 122 com dano reconhecido, 160 com salvaguarda, 82 com área, 24 com ataque mágico, 8 com
cura, 153 com aprimoramento, 161 com Concentração, 31 rituais.

**Componentes materiais:** 214 magias têm componente Material. Destas, **148 podem ser substituídas
por Bolsa de Componentes ou Foco de Conjuração**, e **66 exigem o material de verdade** — as que têm
custo em PO ou são consumidas. Essa marca agora é calculada dentro do próprio gerador, não num
passo à parte que eu poderia esquecer de rodar (foi o que aconteceu no meio deste lote, e o número
zerou até eu perceber).

As 261 descrições novas são **paráfrases minhas**, como as 130 primeiras. Ler 391 entradas e
resumir cada uma é o grosso do trabalho deste lote, e é onde eu mais quero seu olho: se alguma
estiver faltando informação para jogar, me diga qual.

## Três coisas que apareceram no caminho

**1. Um tipo de alcance que eu não conhecia.** *Sonho* (p. 331) tem `Alcance: Especial` — o alcance
está no corpo da magia. Eu tinha cinco tipos de alcance e ele não era nenhum; o validador acusou na
hora, porque "distância" sem metros é erro. Virou o sexto tipo.

**2. Blocos de estatísticas contaminando o corpo de três magias.** *Invocar Aberração*, *Invocar
Barragem* e *Invocar Elementais Menores* têm o bloco de uma criatura invocada impresso na mesma
coluna, e o texto delas começava com "Inseto Gigante Fera Grande, Sem Alinhamento CA 11…". Fui
buscar o texto certo de cada uma antes de escrever a descrição.

**3. Três nomes com caixa diferente entre o parser e as minhas descrições** — *Invocar Morto-Vivo*,
*Pele-Casca* e *Proteção Contra Energia*. O gerador **falha e diz qual falta** em vez de gravar uma
magia detalhada sem descrição, que é o defeito que ele existe para impedir. Foram três execuções e
três correções.

## Estado geral

```
8 classes · 32 subclasses · 265 características · 48 catálogos · 70 tipos de efeito
391 magias, TODAS detalhadas · 8 de 8 listas de magia preenchidas
170 itens · 25 ferramentas · 17 valores derivados
```

O capítulo 7 e o capítulo 6 estão fechados. O que falta do livro é: as **quatro classes** (Bardo
p. 59, Feiticeiro p. 103, Guardião p. 117, Paladino p. 167) e os **capítulos 4 e 5** — origens,
espécies, antecedentes e talentos. O capítulo 5 fecha os quatro talentos que hoje estão declarados
como pendentes.

## O que o backend recebe agora

Para uma magia qualquer, tudo em campo estruturado: círculo, escola, as classes que a têm, tempo de
conjuração com tipo e ritual, alcance com a distância em metros como número, componentes V/S/M com
o material, o custo em PO e se um foco substitui, duração com Concentração e tempo em minutos, dano
com dado e tipo, salvaguarda com atributo, área com forma e medida, condições citadas, o
aprimoramento por espaço superior ou por nível, a página do livro, e a descrição em uma ou duas
frases.

Para uma arma: dano, maestria, propriedades decompostas, mãos ocupadas, munição que consome, teto
por ação, peso, custo em três moedas. Mais os 17 valores derivados com as parcelas rotuladas para o
log de proveniência.
