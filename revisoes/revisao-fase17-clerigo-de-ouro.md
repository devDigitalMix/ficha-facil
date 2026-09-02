# Fase 17 — a Clériga de ouro, e o que faltava para conjurar

Feita em 2026-09-02. Um terceiro personagem de ouro, um conjurador — e as três
coisas que faltavam no motor para ele existir.

`testes/rodar_todos.py`: **16 de 16 passos limpos.** Motor em 59 de 59, dataset em
`validar.py` 0 erros e 0 avisos, `checar_schema.py` 76/76, dez testes negativos e
`reconstruir.py --comparar` em 66/66 sem diferença.

---

## Irmã Vesna, Clériga 5 do Domínio da Vida

Os dois goldens anteriores não conjuram, e conjurar é metade do jogo. Esta ficha
cobre o que eles não tocavam:

| o que ela prova | valor |
|---|---|
| espaços por círculo | 4 / 3 / 2 |
| magias preparadas | 9 |
| truques | 4 |
| CD para evitar sua magia | **15** = 8 + 4 (Sabedoria) + 3 (BP) |
| jogada de ataque mágico | **+7** |
| Pontos de Vida | **38** = 10 no nível 1 + 4 × (5 + 2) |
| Percepção Passiva | **17** — a proficiência veio do traço Hábil do Humano, não da classe |

Os espaços, as preparadas e os truques saem da linha 5 da tabela de Clérigo (p. 82),
conferida no PDF; não são conta de ninguém.

E ela é o único golden **sem escolha em aberto**: os outros dois cobrem o checklist
com pendências, este cobre o extremo oposto — o motor não inventar pendência onde não
há.

## Três consertos que ela exigiu

**1. O filtro do círculo com espaço passou a ser avaliado.** A regra é "prepare
magias de um círculo para o qual você possui espaços de magia" (p. 85). Até ontem
`circulo_com_espaco_disponivel` voltava em `nao_avaliados` e o app ofereceria a lista
inteira. O motor sabe responder — os espaços estão na tabela da classe, e a tabela
está no contexto:

| | opções para preparar |
|---|---|
| sem o filtro | 108 (a lista de Clérigo inteira, até o 9º círculo) |
| com o filtro | **53** (15 do 1º + 17 do 2º + 21 do 3º) |

**2. A ficha ganhou a parte de magia.** `cd_para_evitar_sua_magia` e
`jogada_de_ataque_magico` usam, no livro, "o modificador do atributo de conjuração" —
uma indireção, porque o atributo muda de classe para classe. O contexto passou a
carregar qual é, e a fórmula resolve `mod:atributo_de_conjuracao` por ele. Quem não
conjura **não ganha a linha** — ausente, não zerada: um Bárbaro com "CD de magia 11"
na ficha é pior que um Bárbaro sem a linha.

**3. Preparar não é desbloquear.** A Clériga tem duas fontes de magia: a classe
(Sabedoria, prepara) e o Iniciado em Magia que o Acólito concede (que só desbloqueia,
com atributo próprio). A primeira versão pegava a primeira fonte que aparecesse — e a
primeira era a do talento, com o atributo ainda em variável (`$atributo_do_talento`),
o que derrubava a ficha. A regra agora é explícita: **a conjuração da ficha é a de
quem PREPARA**; duas fontes preparando com atributos diferentes seriam multiclasse,
que está fora de escopo, e viram erro em vez de escolha no escuro.

## O defeito que a Clériga achou: subclasse não casa por posição

O coletor da fase 15 casava `caracteristicas` com `niveis_de_caracteristica` **por
posição**. Funcionou para a Trilha da Árvore do Mundo, que tem quatro de cada — pura
coincidência.

O Domínio da Vida tem **cinco características em três níveis**, e o motor parou. Foi
contar: **42 das 48 subclasses** têm mais características do que níveis.
`niveis_de_caracteristica` é o RESUMO de em que níveis a subclasse dá algo, não o mapa
de qual dá o quê. O nível de verdade sempre esteve na própria característica.

O dado estava certo desde a fase 2 — a suposição do motor é que estava errada. E o
Bárbaro de ouro passava por sorte: se a Trilha da Árvore do Mundo tivesse uma
característica a mais, ele teria calculado errado sem ninguém notar.

`validar.py` passou a trancar a invariante de que o motor agora depende: toda
característica de subclasse tem nível, o nível declarado bate com a característica, e
ela pertence mesmo àquela subclasse. `testes/teste_negativo_subclasses.py` planta
cinco defeitos — inclusive o realista, "alguém corrigiu o nível e esqueceu o resumo" —
e um caso de folga que **tem** de passar: ter mais características do que níveis não é
defeito. Cobrar `len(niveis) == len(caracteristicas)` seria o erro do primeiro coletor
promovido a regra.

## O teste de mutação, de novo

Três defeitos plantados. O terceiro — voltar a casar subclasse por posição — reprovou
na hora. Os dois primeiros passaram:

| defeito | por quê passou | conserto |
|---|---|---|
| não filtrar pelo círculo com espaço | a contagem de 53 estava escrita no golden e **não era asserção nenhuma** | virou asserção do número exato |
| pegar o atributo de conjuração da primeira fonte | o guarda contra `$` era **código morto**: só a classe prepara, então nunca havia disputa | trocado por uma regra que o dado exercita — `desbloquear_magias` não define conjuração — e um teste que reprova quando ela cai |

O segundo é o mais interessante: eu tinha escrito uma defesa que parecia cuidado e era
enfeite. A mutação mostrou que ela não segurava nada, e o conserto foi trocar código
defensivo não testado por uma regra declarada e testada.

Terceira fase seguida em que a mutação acha teste fraco em vez de código errado.

## O que ficou declarado, e não escondido

**A Clériga está sem armadura de propósito.** Ela tem treinamento com armadura pela
Ordem Divina Protetora, mas calcular CA com armadura — a base da peça mais Destreza
até o teto dela — é caminho que o motor ainda não percorre, porque **equipamento
equipado ainda não é coletado**. Está escrito no golden, em `nota_do_equipamento`, em
vez de virar uma CA que parece certa.

É a próxima peça óbvia, e ela também destrava o resto: arma equipada, bônus de ataque
e dano por arma, e o Escudo na CA — que o Bárbaro tem direito de usar e nenhum golden
exercita.

## O que vem

Passo 5 do plano: o **backend**. E, antes ou junto, o equipamento equipado, que é o
que falta para a ficha de combate fechar.

Continuam de antes: os `efeito_narrativo`, a releitura das 391 paráfrases de magia e
das 112 de criatura, e as três decisões do `BACKLOG.md` §B6.
