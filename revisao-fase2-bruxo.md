# Fase 2d — Bruxo (cap. 3, p. 69–79)

Validador: **0 erros, 0 avisos**. JSON Schema: todos os arquivos passam.

O Bruxo passou. O modelo de conjuração aguentou o caso mais esquisito do livro.

## O que saiu

| coleção | antes | agora |
|---|---|---|
| `classes.json` | 3 | **4** |
| `caracteristicas.json` | 105 | **134** |
| `subclasses.json` | 12 | **16** |
| `magias.json` | 243 | **271** |

Catálogos novos: `invocacoes_misticas` (**28**), `efeitos_dos_passos_feericos` (4).
**Lista de magias do Bruxo completa: 91.**

**Contagens para conferir:** d8 · salvaguardas Sabedoria e Carisma · subclasse em **3, 6, 10, 14** ·
**28 invocações** (4 repetíveis, 23 com pré-requisito) · lista com **12/15/12/14/6/9/7/4/5/7** do
círculo 0 ao 9.

## Os espaços de Pacto couberam sem gambiarra

Era o teste. O `conceder_slot` ganhou `modo: "pacto"` e lê **duas** colunas da tabela em vez de nove:

```
nv  1: 1 espaço de 1º círculo      nv  9: 2 espaços de 5º círculo
nv  3: 2 espaços de 2º círculo     nv 11: 3 espaços de 5º círculo
nv  5: 2 espaços de 3º círculo     nv 17: 4 espaços de 5º círculo
```

Com `todos_do_mesmo_circulo: true` e recarga em **Descanso Curto ou Longo**. Nenhum código especial:
o motor lê `coluna_quantidade` e `coluna_circulo` do mesmo jeito que leria as nove colunas do Mago.

Sobre a sua pergunta da conversa passada: o Bruxo **prepara direto da lista** (`fonte_das_magias:
"lista_de_classe"`), com a restrição extra de que a magia não pode passar do círculo dos espaços — o
que o filtro expressa como `circulo_maximo: "coluna:circulo_dos_espacos"`. É o terceiro modo de
preparação que aparece: livro (Mago), lista com círculo por espaços (Cavaleiro Místico) e lista com
teto de círculo próprio (Bruxo).

## As invocações são um catálogo com pré-requisitos de verdade

As 28 invocações não são texto: cada uma tem efeitos e uma lista de pré-requisitos tipada — nível de
Bruxo, outra invocação, ou "ter um truque de Bruxo que cause dano". A escolha do jogador usa
`respeitar_pre_requisitos: true`, então o app filtra sozinho o que ele ainda não pode pegar.

Cadeias funcionam: Lâmina Devoradora exige Lâmina Sedenta, que exige Pacto da Lâmina. O validador
confere que todo pré-requisito de invocação aponta para uma invocação que existe — testei com um
pacto fantasma e ele pegou.

## Três coisas que valem sua conferência

**1. "Conjuração" vs "Invocação" como nome de escola.** A magia **Fome de Hadar** aparece na lista do
Bruxo com a escola escrita **"Conjuração"**; em todo o resto do livro essa escola é **"Invocação"**.
Normalizei para `invocacao` e registrei a divergência numa nota dentro da própria magia. É
inconsistência do livro, não da extração.

**2. Duas características do Grande Antigo estavam impressas na coluna do Ínfero.** Na extração,
"Magias Psíquicas" e "Mente Desperta" aparecem logo abaixo do título "Patrono Ínfero" — efeito da
quebra de coluna. Atribuí as duas ao **Grande Antigo**, com uma evidência forte: a característica
"Combatente Clarividente" (Grande Antigo, nível 6) diz *"ao formar uma ligação telepática com uma
criatura usando Mente Desperta"*. Se Mente Desperta fosse do Ínfero, o Grande Antigo referenciaria
algo que não tem. Confere no impresso, mas estou seguro.

**3. Pacto do Tomo escolhe de QUALQUER lista.** Três truques e duas magias de 1º círculo com marcador
Ritual, *"da lista de magias de qualquer classe"*. É o mesmo mecanismo do Iniciado em Magia que
modelamos: filtro sem `lista`, valendo o catálogo inteiro. Hoje ele oferece só o que já existe (Mago
e Bruxo, mais as parciais); vai crescendo sozinho a cada classe nova.

## Quatro tipos de efeito novos

`reserva_de_dados` (a poça de d6 da Luz Medicinal do Celestial) · `magias_de_patrono` (a tabela de
magias sempre preparadas, que não contam para o limite) · `alterar_tipo_de_dano_da_magia` ·
`dispensar_componentes`.

Catálogo em **61 tipos**.

## Verificação

Teste negativo com invocação apontando para pré-requisito inexistente, magia fantasma numa invocação
e círculo de Pacto igual a 9: **pegou os três**. A regra do círculo é nova — Magia de Pacto vai só do
1º ao 5º, e agora o validador sabe disso.

Também rodei o parser genérico de listas de magia sobre o **Mago** de novo: devolveu as mesmas 242
com as mesmas contagens por círculo do parser anterior. Dois parsers independentes chegando ao mesmo
número é a melhor evidência que eu tinha de que a lista está certa.

## Pendências

Continuam as quatro travadas pelo capítulo 6 (equipamento inicial das quatro classes, maestria em
arma) e **uma que depende de você**: Criaturas Espectrais, do Ilusionista, cita "Invocar Fera", que
não está na lista do Mago. É acesso concedido pela subclasse?

## Estado geral

```
4 classes · 16 subclasses · 134 características · 34 catálogos · 61 tipos de efeito
271 magias — listas do Mago (242) e do Bruxo (91) completas
```

## Próximo passo

Faltam oito classes. **Clérigo** (p. 81) ou **Druida** (p. 91) trazem o modo de preparação direto da
lista sem teto de círculo, que ainda não apareceu, e cada um traz sua lista completa — o que também
alimenta o Iniciado em Magia. O **Bardo** (p. 59) tem Segredos Mágicos, o caso de acesso a listas
alheias que a gente discutiu.

Também segue de pé o pente-fino no glossário atrás de termos sem marcador, no estilo do "Sangrando"
que me escapou.
