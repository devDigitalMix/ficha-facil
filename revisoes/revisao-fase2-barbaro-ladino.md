# Fase 2g — Bárbaro (p. 51–57) e Ladino (p. 137–145)

Validador: **0 erros, 0 avisos**. JSON Schema: todos passam. Teste negativo: **10 defeitos plantados,
10 pegos**.

As duas juntas, como você pediu. São as duas únicas classes sem conjuração alguma na classe base —
o que fez o lote testar outra parte do modelo: recurso com dois gatilhos de recarga (Fúria), dado que
escala por nível (Ataque Furtivo) e, principalmente, **características que mexem numa escolha que
outra característica já concedeu**.

## O que saiu

| coleção | antes | agora |
|---|---|---|
| `classes.json` | 6 | **8** |
| `caracteristicas.json` | 194 | **265** |
| `subclasses.json` | 24 | **32** |
| catálogos | 42 | **47** |
| `tipos_de_efeito` | 67 | **69** |

Catálogos novos: `efeitos_de_golpe_brutal` (4), `opcoes_de_furia_dos_selvagens` (3),
`opcoes_de_aspecto_dos_selvagens` (3), `opcoes_de_poder_dos_selvagens` (3),
`efeitos_de_golpe_astuto` (7).

## Contagens para você conferir no livro

**Bárbaro** — d12 · salvaguardas Força e Constituição · subclasse em **3, 6, 10, 14** · 35
características · colunas **Fúrias** (2→6), **Dano da Fúria** (+2→+4) e **Maestria em Arma** (2→4) ·
4 trilhas: Árvore do Mundo (4), Berserker (4), Coração Selvagem (5), Fanático (5).

**Ladino** — d8 · salvaguardas Destreza e Inteligência · subclasse em **3, 9, 13, 17** · 36
características · coluna **Ataque Furtivo** 1d6→10d6 · 4 subclasses com 5 características cada:
Adaga Espiritual, Assassino, Ladrão, Trapaceiro Arcano.

As trilhas com 5 e as subclasses de Ladino com 5 não são erro: elas têm **duas características no
nível 3** (Coração Selvagem tem Arauto da Fauna *e* Fúria dos Selvagens; o Assassino tem Assassinar
*e* Ferramentas de Assassino, e assim por diante). Conferi título a título contra o texto do livro.

## O problema novo deste lote: melhorar uma escolha sem duplicá-la

Bárbaro e Ladino têm o mesmo desenho repetido quatro vezes: uma característica concede uma escolha
(Golpe Brutal no nível 9, Golpe Astuto no nível 5), e características posteriores **mexem naquela
escolha** — umas acrescentam opções, outras mudam quantas você pode aplicar de uma vez.

Eu tinha escrito isso como `efeito_narrativo`, ou seja, **texto**. Funciona para ler, não para o app
executar: o seletor não teria como saber que Golpe Atordoante abriu no nível 13. Reescrevi com dois
tipos de efeito novos, que são a coisa em si:

- **`expandir_opcoes_de_escolha`** — libera chaves específicas de um catálogo numa escolha já
  concedida. Usado por Golpe Brutal Fortalecido (13), Golpes Sujos (14) e Furtividade Suprema.
- **`alterar_quantidade_de_escolha`** — muda quantos itens a escolha permite. Usado por Golpe Brutal
  Fortalecido (17, dois efeitos por uso) e Golpe Astuto Aprimorado (11, idem).

Os dois apontam para a escolha pelo `escolha_id`, e **o validador agora casa os dois lados**: se
alguém alterar uma escolha que não existe, é erro. Testei com um id fantasma — pegou.

## Uma opção que não é liberada por nível

O **Ataque Escondido** é uma opção de Golpe Astuto, mas não chega por nível: chega pela
**Furtividade Suprema**, do Ladrão. Eu tinha marcado `nivel_minimo: 9` no catálogo, o que estava
errado — pelo nível, qualquer Ladino de 9 pegaria, inclusive um Assassino.

Troquei por `apenas_se_concedido: true`, e criei a checagem correspondente: **opção marcada assim
que nenhuma característica concede vira erro**. É a mesma ideia do catálogo vazio dizendo-se
preenchido — o dado não pode mentir sobre si.

## Duas divergências do livro

**1. Golpe Brutal, níveis 13 e 17.** A tabela (p. 52) chama os dois de "Golpe Brutal **Aprimorado**";
os títulos no corpo dizem "Golpe Brutal **Fortalecido**" nos dois. Adotei o título do corpo, como
combinamos no Monge, e guardei o nome da tabela em `nome_na_tabela`.

Mas há um detalhe que mudei durante a revisão: são **duas seções tituladas distintas com o mesmo
nome** e conteúdos diferentes — a de 13 abre opções, a de 17 dobra o dano e o número de efeitos. Pela
regra que fixamos no Prodígio Maior (título no livro ⇒ característica própria), viraram **duas
características**, `golpe_brutal_fortalecido_13` e `_17`, e não uma repetida.

**2. Ladino, nível 1.** A tabela diz "Especialização" e "Gíria dos Ladrões"; os títulos dizem
"Especialista" e "Gíria do Ladrão". Mesmo tratamento: vale o título, nome da tabela guardado.

## Duas coisas que este lote consertou no que já estava pronto

O validador conferia o campo `alvo` só em três tipos de efeito — nos demais, um alvo inventado
passava batido. Ampliei a checagem, e ela imediatamente acusou **seis alvos que não existiam no
catálogo**, todos anteriores a este lote:

- Crítico Aprimorado e Crítico Superior (Campeão) apontavam para `ataque_com_arma` e
  `ataque_desarmado` — legítimos, mas nunca cadastrados. Adicionados a `alvos.json` como recortes de
  `jogada_de_ataque`.
- Prodígio (Adivinhador) usava `seu_teste_d20`, que era o `teste_d20` já existente com outro nome, e
  `teste_d20_de_criatura_a_vista`, que faltava. Normalizei o primeiro e cadastrei o segundo.

Vale reparar que `alvo` tem **dois sentidos** no esquema: em `melhorar_caracteristica` é o id de uma
característica, em `dano` é a descrição de quem sofre. A checagem vale só para os tipos em que `alvo`
é uma jogada da ficha — está declarado no código, com o motivo.

O JSON Schema também pegou **duas condições compostas ambíguas** (o Golpe Brutal e o próprio Ataque
Furtivo), que misturavam `todas` e `nao` no mesmo objeto sem dizer como combinam. Normalizei para um
operador por objeto, aninhando: `todas: [a, b, {nao: c}]`. O sentido não mudou; o que mudou é que
agora só existe uma leitura possível.

## Estado geral

```
8 classes · 32 subclasses · 265 características · 47 catálogos · 69 tipos de efeito
368 magias — listas de Mago (242), Bruxo (91), Druida (135) e Clérigo (117) completas
```

## Próximo passo

Faltam quatro classes: **Bardo** (p. 59), **Feiticeiro** (p. 103), **Guardião** (p. 117) e
**Paladino** (p. 167) — todas com conjuração, todas trazendo uma lista de magias nova. Com as quatro,
as oito listas ficam preenchidas.

O **Bardo** continua sendo o mais interessante pelo lado do esquema: Segredos Mágicos é acesso a
listas alheias em escala, e agora que `expandir_opcoes_de_escolha` existe, provavelmente é ele que a
generaliza.

Pendências inalteradas em `PENDENCIAS.md`: criaturas adiadas, capítulos 5, 6 e 7, e o pente-fino no
glossário.
