# Varredura — opções de catálogo que eram só texto

Validador: **0 erros, 0 avisos**. JSON Schema: todos passam. Teste negativo: **15 defeitos
plantados, 15 pegos**.

Isto não é uma classe nova; é o conserto de um padrão que estava inconsistente desde o Monge e que
só apareceu quando você perguntou do Golpe Astuto.

## O que estava errado

Um catálogo de opções tem duas partes: o texto que o jogador lê e os **efeitos que o app executa**.
As manobras do Guerreiro (20) e as invocações do Bruxo (28) sempre tiveram as duas. Todo o resto
tinha só a primeira.

Na prática: o Druida escolhia a constelação Dragão e o app não sabia que ela trata 9 ou menos como
10. O Clérigo escolhia Ordem Divina Protetor e não ganhava proficiência nenhuma. O Monge acertava
com a Mão Espalmada e não havia salvaguarda a pedir. Tudo estava escrito — em português, para
humano ler.

**37 opções em onze catálogos** ganharam efeitos executáveis, na mesma forma das manobras:

| catálogo | classe | opções |
|---|---|---|
| `efeitos_de_golpe_astuto` | Ladino | 7 |
| `efeitos_de_golpe_brutal` | Bárbaro | 4 |
| `opcoes_de_furia_dos_selvagens` | Bárbaro | 3 |
| `opcoes_de_aspecto_dos_selvagens` | Bárbaro | 3 |
| `opcoes_de_poder_dos_selvagens` | Bárbaro | 3 |
| `efeitos_da_mao_espalmada` | Monge | 3 |
| `efeitos_dos_passos_feericos` | Bruxo | 4 |
| `beneficios_do_terceiro_olho` | Mago | 3 |
| `ordens_divinas` + `efeitos_de_canalizar_divindade` + `opcoes_de_golpes_abencoados` | Clérigo | 6 |
| `ordens_primais` + `opcoes_de_furia_elemental` + `constelacoes` | Druida | 7 |
| `terrenos_druidicos` | Druida | 4 |

## O buraco que a varredura encontrou

O pior caso não era falta de efeito: era **conteúdo do livro que nunca foi extraído**.

O Círculo da Terra escolhe um terreno, e cada terreno concede uma **tabela de Magias de Círculo
Druídico** (p. 98) — quatro tabelas, quatro níveis cada, **24 magias no total**. Essas tabelas nunca
entraram. A característica `magias_do_circulo_da_terra` mandava aplicar o efeito do terreno
escolhido, e o terreno tinha id, nome e uma linha de resistência. Mais nada.

Um Druida do Círculo da Terra nível 9 no app teria perdido as seis magias sempre preparadas do seu
terreno, silenciosamente. As quatro tabelas estão extraídas agora, com as 24 magias conferidas
contra o catálogo — todas existem.

As descrições dos quatro terrenos também estavam **em branco**, o que no compêndio apareceria como
item vazio. Preenchidas.

## Uma decisão que registro para você conferir

A resistência do terreno (Árido → Ígneo, e assim por diante) continua vindo do mapa dentro da
**Proteção Natural**, como estava, e não foi duplicada como efeito do terreno. Motivo: dois lugares
concedendo a mesma resistência é convite a aplicar duas vezes. O terreno guarda o campo
`resistencia` como dado, e quem aplica é a característica de nível 10 — que é o que o livro diz.

## Quatro furos no validador, todos fechados

A varredura só apareceu porque o validador **não cobrava** isso. Fechei o que faltava:

**1. Ele não sabia distinguir catálogo de vocabulário de catálogo de opção.** Perícias e idiomas não
têm efeitos e nunca terão; constelações e ordens divinas precisam ter. Agora a lista de catálogos de
vocabulário está declarada no código, e **opção sem efeitos é erro** — salvo se marcada
`pendente: true`.

**2. Tipo de efeito digitado errado passava batido.** A varredura de efeitos só checava dicionários
cujo tipo *já era válido* — ou seja, um `modificador_fantasma` era simplesmente ignorado, e o erro
"tipo de efeito desconhecido" era código morto. Agora tudo que está dentro de uma lista `efeitos`
**tem** de ser um efeito de tipo conhecido. Testei em catálogo, em característica e em efeito
aninhado: pega nos três.

**3. Tipo de dano só era conferido em `alterar_dano`.** Um `dano` com tipo inventado passava — e eu
acabara de escrever vários. Agora vale para qualquer efeito, incluindo as listas de
`escolher_tipo_dano` (o Golpe Divino escolhe entre Necrótico e Radiante).

**4. Tipo de deslocamento e sentido não eram conferidos** (a Pantera dá escalada, a Coruja dá visão
no escuro).

Os quatro talentos que ainda dependem do capítulo 5 — Aumento no Valor de Atributo e os três de
Dádiva Épica — eram **stubs sem descrição nenhuma**. Agora estão marcados `pendente: true`, com
texto dizendo de onde a definição virá. O validador cobra essa marca: stub silencioso virou erro.

## Uma dúvida que deixei declarada

**Compreensão Superior** (Terceiro Olho, do Adivinhador) diz "você pode ler qualquer idioma". Não há
primitivo para isso no esquema — não é proficiência em idioma, é compreensão universal. Ficou como
`substituir_regra` com `revisao: duvida`, que é a saída de emergência do esquema, e o item está
marcado como dúvida. Provavelmente ganha um efeito próprio quando o capítulo 5 entrar, porque os
talentos costumam ter algo parecido.

## Estado geral

```
8 classes · 32 subclasses · 265 características · 47 catálogos · 69 tipos de efeito
114 itens de catálogo com efeitos executáveis (eram 59)
368 magias — listas de Mago, Bruxo, Druida e Clérigo completas
```

Nenhum catálogo de opção tem mais item só com texto.
