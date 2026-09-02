# Fase 13 — o vocabulário de runtime

Feita em 2026-09-02, antes da primeira linha do motor. Não entrou conteúdo novo do
livro: esta fase conserta o **jeito de escrever** o que já estava lá.

`validar.py`: 0 erros, 0 avisos · `checar_schema.py`: 75/75 ·
`teste_negativo_vocabulario.py`: **14 de 14**, mais 1 caso de folga que tem de passar ·
os sete testes negativos anteriores seguem em 7/17/18/18/26/11/16 ·
`reconstruir.py --comparar`: **61/61 geradores, 0 diferenças** — nem de conteúdo,
nem de formatação.

---

## O defeito

Os 103 tipos de efeito sempre foram catálogo declarado, validado, com teste
negativo. **O que aparece dentro deles nunca foi.** O predicado de uma condição, o
gatilho que dispara o efeito, a duração, o custo — tudo isso cresceu solto por doze
fases, cada lote escrevendo do seu jeito, sem nada conferindo.

O resultado é o pior tipo de defeito: o que não parece defeito. Ninguém olhando o
Bárbaro desconfia de `gatilho: "entrar_em_furia"`, e ninguém olhando a Fúria dos
Selvagens desconfia de `momento: "ao_entrar_em_furia"`. Só que são o mesmo evento
com dois nomes, e no motor isso vira ou dois `case` fazendo a mesma coisa, ou —
o mais provável — um efeito que **nunca dispara**, porque quem implementou tratou
um dos dois e não sabia do outro.

O `PLANO-MOTOR.md` §5 já tinha levantado seis pares. Varrendo com ferramenta em vez
de com o olho, eram muitos mais.

## O que foi fundido

| vocabulário | antes | depois | fusões declaradas |
|---|---|---|---|
| predicado de condição | 204 | **178** | 22 + 3 negações + 12 comparações |
| gatilho (e `momento`) | 153 | **127** | 28 + 3 vindas de `custo` |
| duração | 34 | **13** símbolos + forma de tempo | 20 + 7 |
| custo | 13 | **9** | 1 + 3 que eram gatilho |
| fase | não existia | **3** | — |

**625 ocorrências reescritas em 75 arquivos.** Tudo por tabela explícita em
`geradores/gerar_normalizacao_vocabulario.py`, que é onde se lê o porquê de cada
fusão — não num diff.

### Os campeões

**Oito grafias para "até o fim do turno atual".** `ate_o_fim_do_turno`,
`ate_o_fim_deste_turno`, `este_turno`, `neste_turno`, `mesmo_turno`,
`resto_do_turno`, `resto_do_turno_atual` e o próprio `ate_o_fim_do_turno_atual`.
Nenhuma delas errada; todas juntas, impossíveis de implementar sem esquecer uma.

**Quatro nomes para o mesmo turno seguinte.** `ate_o_fim_do_proximo_turno_dela`,
`_dele`, `_do_alvo` e `_do_aliado`. O referente nunca precisou estar no nome da
duração: ele já está no campo `beneficiario` do efeito. Viraram
`ate_o_fim_do_proximo_turno_do_beneficiario`.

**`dispersar` e `dispensar`.** Erro de digitação, os dois para "encerrar a forma".

**`criacao` + `ao_adquirir_o_talento` + `ao_adquirir`.** Três nomes para "quando
isto entra na ficha". O segundo era pior que redundante: citava o *tipo de
conteúdo* no vocabulário do motor, e o motor não pode saber o que é um talento.
Sozinho ele respondia por 70 das 119 ocorrências que hoje são `ao_adquirir`.

## Três coisas que não eram fusão, e sim erro de modelagem

**1. O campo `momento` era o `gatilho` com outro nome.** Em 264 ocorrências, os dois
campos coexistiam — e só **7 objetos** usavam os dois ao mesmo tempo. Ou seja: 257
vezes alguém escolheu um dos dois no chute. O campo `momento` foi **revogado**. O
evento vai em `gatilho`; a fase dentro da resolução daquele evento — "depois da
jogada", "antes da jogada" — vai num campo novo e minúsculo, `fase`, com três
valores. O validador agora acusa quem reintroduzir `momento`.

**2. Duração de tempo era prosa.** `"1 minuto"`, `"10 minutos"`, e duas que o motor
não teria como executar: `"minutos iguais ao nível de Bruxo"` e `"nivel de
Feiticeiro em minutos"` — a mesma coisa escrita de dois jeitos, em português
corrido, dentro de um campo de dado. Agora é objeto:

```json
"duracao": {"quantidade": ["nivel_classe:bruxo"], "unidade": "minuto"}
```

A quantidade é fórmula, pela mesma regra do resto do projeto. São 473 ocorrências
na forma nova.

**3. Comparação era texto dentro do id.** Havia **oito sintaxes**:
`"alcance >= 3m"` (com espaços), `"recurso:pontos_de_foco.atual<=3"` (sem),
`"valor_de_atributo:DES>=16"`, `"usos_atuais_menores_que:2"` (por extenso),
`"nivel_maior_que_1"`, e mais. Um parser de condição teria de entender todas.
Viraram uma forma só, com os dois lados em fórmula:

```json
{"comparar": ["valor_de_atributo:DES"], "op": "gte", "com": ["16"]}
```

E `custo` guardava duas coisas diferentes: o que a característica **custa** (uma
Ação, a Reação, seu movimento) e **quando** ela se usa. As manobras do Guerreiro
carregavam a segunda no campo da primeira — `custo: "no_acerto"`. Janela de uso é
gatilho, e foi para lá.

## Uma coisa que eu quase fundi, e não devia

`arma:a_distancia` e `ataque:a_distancia` parecem o mesmo predicado escrito de dois
jeitos. Não são. O primeiro diz que a **arma** é de ataque à distância; o segundo,
que **este ataque** foi feito à distância — e ele é usado justamente com
`arma:propriedade:arremesso`, para a arma corpo a corpo arremessada.

Foi o único caso em que abrir a página salvou uma fusão errada, e vale como método:
**nenhuma fusão foi feita pelo nome; todas foram conferidas no uso.**

## A lista fechada

O que impede tudo isso de voltar é `dados/vocabulario_de_runtime.json`, escrito por
`geradores/gerar_vocabulario_de_runtime.py`.

Ele **não é derivado do dado**. Isso é o ponto: catálogo derivado da saída aceita
qualquer coisa que a saída contenha, e não pega sinônimo nenhum — ele os
*abençoaria*. A lista é declarada à mão, e o validador falha quando o dado usa um
token que não está nela. Quem inventar um termo novo tem de passar por aqui, e ao
passar vê se ele já não existe com outro nome.

Doze famílias têm o argumento conferido contra outro catálogo — `condicao:<id de
condicoes>`, `magia_da_escola:<id de escolas_de_magia>`, `alvo_de_tamanho_ate:<id
de tamanhos>` — de modo que `condicao:sonolento` é erro de build, e não um efeito
que nunca dispara.

O teste negativo cobre as catorze formas do defeito, mais um caso de **folga** que
tem de passar: declarar um predicado que ainda ninguém usa não é erro. A lista
existe para barrar o que o dado usa sem declarar, não para engessar quem for
escrever a próxima característica.

## O que isto dá ao motor

Antes desta fase, a superfície de implementação do motor era desconhecida:
descobrir o que ele precisava interpretar era ler os 75 arquivos e torcer. Agora é
um arquivo:

```
152 predicados + 12 famílias · 127 gatilhos · 3 fases · 13 durações
símbolicas + a forma de tempo · 9 custos · 5 modos de empilhamento
3 operadores lógicos · 6 operadores de comparação
```

Essa é a lista do que o motor precisa saber fazer. Não é pequena, mas é **finita e
conferida**, e cada item aparece uma vez só.

## Ferramenta nova

`inventariar_vocabulario.py` — conta e mostra onde. Não julga. É o que se roda antes
de declarar um token novo, e o que se roda quando alguém desconfia:

```bash
python3 inventariar_vocabulario.py              # o resumo
python3 inventariar_vocabulario.py gatilho      # a lista, com contagem
python3 inventariar_vocabulario.py gatilho falha  # onde 'falha' é usado
```

Foi contando com ela — e não lendo — que apareceram as oito grafias de "fim do
turno". A mesma lição do Zumbi na fase 12: **a conferência que conta vale mais que
a leitura do resultado.**

## O que continua aberto

Nada desta fase. Continuam em aberto, de antes: os 168 `efeito_narrativo` (§6 do
`PLANO-MOTOR.md`), a releitura das 391 paráfrases de magia e das 112 de criatura, e
as três decisões do `BACKLOG.md` §B6.
