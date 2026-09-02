# Fase 14 — o motor começa: avaliador de fórmula e ficha estática

Feita em 2026-09-02, logo depois da fase 13. É o passo 2 da ordem sugerida do
`PLANO-MOTOR.md`, e a primeira linha de código do motor.

`node --test`: **33 de 33** — 20 de fórmula e condição, 3 de ouro, 9 de sensibilidade dos
goldens e 1 de lint. Zero dependências, zero passo de build.
O dataset segue em `validar.py` 0/0 e `reconstruir.py --comparar` 61/61 sem diferença.

---

## Duas decisões suas, tomadas antes de escrever

**TypeScript.** O motor roda no navegador e no servidor. A Fase A do `PLANO-APP.md`
fica offline-first, a Fase B sincroniza só estado, e recalcular a CA não precisa de
ida à rede. O toolchain do dado continua em Python — as duas coisas não se encostam:
o Python escreve `dados/`, o TypeScript só lê.

**Personagens de ouro primeiro.** As fichas de referência foram montadas e conferidas
contra o livro **antes** do motor existir. É a mesma ideia dos oito testes negativos do
dataset: o alvo existe antes do código que tem de acertá-lo.

## Zero dependências, e por quê

O Node roda TypeScript direto, apagando os tipos — nativo no 24, e no 22.6+ com
`--experimental-strip-types`. Os testes são `node:test` e `node:assert`. Não há
`npm install`, não há build, não há framework.

Isso não é ascetismo: é o mesmo motivo de `validar.py` não usar biblioteca de
validação. A cadeia de confiança do projeto é curta de propósito, e o motor é a peça
que vai sobreviver mais tempo.

## O que fecha

Passo 2 é a **ficha estática**: modificadores, Bônus de Proficiência, Classe de
Armadura, Pontos de Vida máximos, Iniciativa, Percepção Passiva, salvaguardas, testes
de perícia e Deslocamento — cada um com a proveniência, que é o que o app promete
mostrar ("CA 15 = 10 + 3 Destreza + 2 Sabedoria").

O que **não** entra aqui, de propósito: coletar efeito a partir da construção (passo 3)
e resolver escolha (passo 4).

## Três regras que o código segue à risca

**Nenhum id de conteúdo aparece no motor.** O `PLANO-MOTOR.md` §1 pedia que isso virasse
lint, e virou: `lint-sem-id-de-conteudo.test.ts` carrega todos os ids de `dados/` — classes,
subclasses, características, magias, itens, talentos, criaturas, espécies, antecedentes — e
reprova se algum aparecer como literal no código, ignorando comentários (explicar por que o
Monge é o caso difícil é justamente o que se quer escrito). Plantei `'defesa_sem_armadura'`
numa constante para conferir que ele acusa; acusou. O motor resolve `mod:DES` porque DES é
atributo, e `nivel_classe:x` porque a classe está no contexto — nunca porque conhece a classe.

**Desconhecido é erro, nunca zero.** Termo que não resolve, operação que não existe,
predicado fora do vocabulário fechado da fase 13: tudo lança `ErroDoMotor`. Devolver 0 e
seguir produz ficha errada que ninguém percebe — exatamente o defeito que a fase 13
passou uma fase inteira tirando do dado. Seria uma pena reintroduzi-lo no código na
semana seguinte.

**O motor não joga dado.** `avaliar` devolve `{ valor, dados, parcelas }`: a parte fixa
vai em `valor`, e o dado fica **simbólico**. Por isso a Iniciativa sai `+3` com `1d20` ao
lado, e o dano do machado `1d12 + 4`. Pureza aqui não é elegância — é o que faz o teste
ser possível, e é o que mantém o jogo no dado, na mesa.

## Os dois personagens de ouro

**Kaida, Monge 1.** A ficha mais simples que ainda quebra o caso interessante: a CA do
Monge é 10 + Destreza + Sabedoria e **concorre** com o cálculo padrão em vez de somar.
Somando, dá 17 em vez de 15, e nenhuma outra conta pega isso.

**Torvar, Bárbaro 5 (Trilha da Árvore do Mundo).** Outra CA concorrente — esta ainda
deixa usar Escudo, diferente da do Monge. Pontos de Vida de cinco níveis (50 = 14 no
primeiro + 4 × 9), com o valor fixo da tabela da p. 42 e não a média deduzida do d12. Um
Aumento no Valor de Atributo do nível 4 mexendo na Força depois da criação. E a Fúria
ligando resistências, vantagem e dano condicional de uma vez — por isso a ficha vem em
duas versões, com e sem Fúria: o motor tem de dar respostas diferentes para o mesmo
personagem.

O campo `contexto` dos dois é **provisório e está marcado como tal**: hoje escrito à mão,
no passo 3 passa a ser produzido pela coleta de efeitos a partir da `construcao`. O
`esperado` não muda — é ele que é o teste, e ele continuará valendo quando o contexto
deixar de ser manual.

## Os goldens passaram de primeira, e isso não vale nada sozinho

Foi o resultado da primeira execução: 23 de 23. Um teste que nunca reprovou não prova que
confere — prova que aceita. Então duas camadas em cima:

**Sensibilidade dos goldens** (`negativo.test.ts`): oito defeitos plantados no contexto,
cobrando que a ficha **mude**. Se o Dado de Vida virar o de outra classe e os Pontos de
Vida não mudarem, o golden não estava conferindo Pontos de Vida. Mais um caso de folga que
tem de passar — mexer no Carisma não pode mexer na CA — porque sem ele um motor que
devolvesse lixo aleatório passaria em todos os outros.

**Mutação do motor**, à mão: quebrar o código de propósito e ver os goldens caírem.

| defeito plantado no motor | quem reprovou |
|---|---|
| somar os cálculos de CA base em vez de escolher um | os **dois** goldens, e o teste de fórmula |
| esquecer a Constituição nos níveis seguintes | o Bárbaro |

É a conferência que vale mais que ler o resultado — a mesma lição do Zumbi na fase 12.

## O que vem

Passo 3 do plano: **coletor de efeitos + condições + empilhamento**. É ele que faz o campo
`contexto` dos goldens parar de ser escrito à mão. Depois dele, passo 4, o motor de escolha
— que destrava criar personagem e subir de nível, a Fase A inteira.

Nada desta fase ficou em aberto. Continuam de antes: os 168 `efeito_narrativo`, a releitura
das 391 paráfrases de magia e das 112 de criatura, e as três decisões do `BACKLOG.md` §B6.
