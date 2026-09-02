# Fase 12 — Apêndice B: blocos de estatísticas de criaturas

Extraído em 2026-09-02. Apêndice B, p. 346-359. **51 blocos, 112 traços e ações.**
Com ele cai a última exclusão de escopo que ainda tinha efeito no dado: o seletor de formas
da Forma Selvagem **liga**.

`validar.py`: 0 erros, 0 avisos · `checar_schema.py`: 75/75 · `teste_negativo_criaturas.py`:
**17 de 17** · os seis testes anteriores seguem em 7/18/18/26/11/16 ·
`reconstruir.py --comparar`: **59/59 geradores, 0 diferenças de conteúdo**.

---

## O que entrou

| tipo | quantas |
|---|---|
| Fera | 43 |
| Ínfero (Diabrete, Quasit) | 2 |
| Morto-Vivo (Esqueleto, Zumbi) | 2 |
| Celestial, Dragão, Aberração, Feérico | 1 cada |

Por Nível de Desafio: 15 em ND 0, 8 em 1/8, 12 em 1/4, 7 em 1/2, 8 em ND 1 e um em ND 4
(a Esfinge Maravilhosa).

Não é bestiário — é o que o próprio apêndice diz ser: as criaturas citadas nos capítulos de
classe, equipamento e magia. O Livro dos Monstros continua fora.

## Como foi feito, e por quê assim

**Parser, não digitação.** 51 blocos × ~15 campos é onde erro de digitação se esconde. Os
números — CA, PV, deslocamentos, atributos, perícias, sentidos, ND, bônus de ataque e dano —
saem de `parse_criaturas.py`. As frases não: são paráfrase à mão em `descricoes_criaturas.py`,
pela mesma regra das magias, e **o gerador falha se faltar alguma**.

**Ataque puro não tem paráfrase.** Quando a ação é só jogada, alcance e dano, a descrição é
DERIVADA do próprio dado estruturado e marcada `descricao_derivada` — 46 das 112 entradas.
Escrever à mão o que a máquina deduz é convite a divergência entre os dois.

**Efeito onde é efeito.** Nove traços viraram efeito executável: Ágil e Sobrevoo são `impedir`
de Ataque de Oportunidade; Resistência à Magia e Táticas de Grupo são `vantagem` com condição;
Fúria Sangrenta pendura a Vantagem no estado Sangrando; Animal de Carga é `modificador` em
`capacidade_de_carga` (o alvo que o capítulo 4 criou para o Golias); Saltador é
`substituir_atributo` de Força por Destreza no salto. O resto é `efeito_narrativo`, marcado.

## O seletor da Forma Selvagem ligou

Desde a fase 2, a escolha de formas do Druida apontava para o catálogo `criaturas` **por
filtro**, com `pendente: true` — escrita assim de propósito, para ligar sem reeditar o Druida
quando o apêndice chegasse. Chegou, e foi só tirar o `pendente`:

| nível de Druida | o filtro devolve |
|---|---|
| 2 (ND 1/4, sem voo) | **26 formas** |
| 4 (ND 1/2, sem voo) | **33 formas** |
| 8 (ND 1, voo liberado) | **42 formas** |

O `efeito_por_item_escolhido` deixou de ser `efeito_narrativo` e virou o tipo novo
**`assumir_bloco_de_estatisticas`**, que é o que o Druida faz de verdade: carregar a ficha de
outra criatura. O que ele mantém ao multimorfar já estava declarado em
`regras_enquanto_multimorfado` desde a fase 2.

O aviso ao subir de nível **ficou**, com o texto trocado: antes dizia que a escolha era fora do
app; agora diz que o app oferece as Feras do Apêndice B e que o Mestre pode liberar outras.

## Quatro contas do livro que não fecham

Esta é a parte que vale o seu olho. O bloco imprime, para cada atributo, o VALOR, o MODIFICADOR
e a SALVAGUARDA. Em quatro criaturas o modificador impresso não corresponde ao valor — e são
**dois fenômenos diferentes**:

| criatura | atributo | livro imprime | a conta dá | o que parece ser |
|---|---|---|---|---|
| Alce (p. 346) | Car 6 | mod −4, SG −2 | −2 | ruído de coluna: **o SG confirma a conta** |
| Camelo (p. 347) | Des 8 | mod −4, SG −1 | −1 | idem |
| Cabra (p. 347) | Int 2 | mod −5, SG −5 | −4 | **o livro discorda de si mesmo** |
| Cavalo Marinho Gigante (p. 349) | For 16 | mod +2, SG +2 | +3 | idem |

Nos dois primeiros o próprio bloco se corrige — a coluna de salvaguarda traz o número certo, o
que sugere falha de extração da coluna do meio. Nos dois últimos as duas colunas concordam entre
si e discordam do valor do atributo: aí é o livro.

**Resolução, igual nos quatro:** o valor do atributo é dado primário e o modificador é
**derivado** dele pela regra universal, que já mora em `valores_derivados/modificador_de_atributo`.
Então o modificador é recalculado, o impresso é preservado em `modificadores_impressos`, e cada
caso vira uma entrada em `divergencias_do_livro` com página e classificação. Nada se perde e nada
se inventa.

A proficiência em salvaguarda também deixou de ser adivinhada: ela sai da distância entre o SG
impresso e o modificador correto — zero é não proficiente, o Bônus de Proficiência é proficiente,
e qualquer outra distância vira divergência declarada em vez de palpite. Sete criaturas são
proficientes em alguma salvaguarda (Cabra e Cabra Gigante em Força, Camelo em Constituição, Gato
em Destreza, Mula e Pônei em Força, Zumbi em Sabedoria).

## Três defeitos que apareceram no caminho

**1. O Zumbi quase ganhou um traço fantasma.** O parser quebra as seções em entradas "Nome. texto",
e a frase "o zumbi tem 1 **Ponto de Vida**" virou uma entrada chamada "Ponto de Vida". A regra
ficou mais estrita: o nome só vale se a frase anterior tiver terminado. Foram **15 entradas
fantasma** removidas assim, de 127 para 112.

**2. O Zumbi também perdia metade de uma linha.** "Idiomas Compreende os idiomas que conhecia em
vida, mas…" — o campo continuava na linha seguinte e o parser pegava só a primeira. Agora cada
campo vai até o próximo rótulo.

**3. Uma criatura ficava de fora da varredura.** O cabeçalho do Esqueleto diz "Morto-Vivo" e o do
Zumbi diz "Morto-vivo", com v minúsculo. Achei porque contei `ND (XP` e deu **51**, enquanto o
casador de cabeçalho dava 50. É o tipo de conferência que vale mais que ler o resultado.

## Corrigido de lote anterior

O **Golpe da Fera** das três feras do Guardião (fase 10) não tinha `descricao_curta`. A checagem
nova de bloco de estatísticas acusou os três no minuto em que nasceu. Passou a ter descrição
derivada do próprio dado, como as criaturas do apêndice.

## Checagens novas no validador

`criaturas` deixou de ser catálogo de VOCABULÁRIO — o que fazia sentido enquanto estava vazio — e
entrou na família de BLOCO DE ESTATÍSTICAS, junto com `feras_companheiras`. Além das checagens que
já existiam ali (atributos, PV, CA, deslocamentos, sentidos, tamanho, tipo, pelo menos uma ação):

| checagem | o que pega |
|---|---|
| coerência do modificador | modificador que não bate com o valor do atributo |
| coerência da Iniciativa | passiva que não é 10 + bônus |
| perícia do bloco | perícia que não existe no catálogo |
| resistência / imunidade / vulnerabilidade | tipo de dano ou condição inventados |
| entrada de traço ou ação | sem `descricao_curta` |
| ação de ataque | sem bônus, sem dano, ou com tipo de dano inventado |
| nível de desafio | sem texto, XP ou Bônus de Proficiência |
| `assumir_bloco_de_estatisticas` | catálogo que não é de blocos, ou criatura inexistente |

## Estado geral

```
12 classes · 48 subclasses · 388 características · 70 catálogos · 103 tipos de efeito
391 magias · 170 itens · 75 talentos · 16 antecedentes · 10 espécies · 51 criaturas
```

O Apêndice B era a última exclusão de escopo que ainda amarrava dado. Continuam fora, por decisão:
o Apêndice A e a multiclasse.
