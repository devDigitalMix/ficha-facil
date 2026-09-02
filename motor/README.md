# Motor de efeitos

Biblioteca **pura**: entra uma construção, sai uma ficha. Mesma entrada, mesma saída,
sempre — sem relógio, sem aleatório, sem banco. É o que permite testá-la de verdade e
rodá-la no cliente depois, se a Fase B pedir.

O contrato está no `PLANO-MOTOR.md` da raiz. Este diretório é a implementação.

## Rodar

```bash
cd motor
npm run teste      # ou: node --experimental-strip-types --test "testes/*.test.ts"
```

**Zero dependências.** Nada de `npm install`: o Node roda o TypeScript direto,
apagando os tipos (nativo no Node 24, e no 22.6+ com `--experimental-strip-types`).
Não há passo de build, e não há framework de teste — `node:test` e `node:assert`.

## O que existe hoje

Passos 2, 3 e 4 do plano. Uma chamada só:

```ts
import { montar } from './src/motor.ts'
const r = montar(construcao, estado)
//  r.ficha       os números, com proveniência
//  r.checklist   as escolhas em aberto, com as OPÇÕES — é a tela de subir de nível
//  r.problemas   as escolhas resolvidas que não deviam ter sido feitas assim
//  r.ficha.ataques    o Ataque Desarmado e cada arma equipada, com o atributo e a
//                     proficiência; r.ficha.conjuracao, para quem conjura
```

Por dentro:

```
construção  →  coletar()        percorre espécie, antecedente, classe, subclasse e
                                talentos; expande as escolhas já resolvidas
            →  montarContexto() o que cada efeito faz com a ficha, dado o ESTADO
            →  montarFicha()    as contas do livro, com proveniência
            →  escolha.ts       oferece o que falta escolher, e recusa o inválido
```

A ficha estática fecha — modificadores, Bônus de Proficiência, CA, Pontos de Vida
máximos, Iniciativa, Percepção Passiva, salvaguardas, testes de perícia e Deslocamento.

**Escolha não resolvida é pendência, não erro.** Ela volta em `col.pendencias`, que é
o checklist de "subir de nível sem esquecer nada". Um Monge de nível 1 tem seis.

**Efeito aninhado nem sempre é condição.** O que está dentro da Fúria carrega a porta
`furia` e só incide com ela aberta — achatar faria o Bárbaro andar por aí com
Resistência a dano Cortante. Mas os 56 `melhorar_caracteristica` aninham por
ESTRUTURA: o `alvo` diz onde aplicar, não quando. Qual é qual está **declarado** em
`tipos_de_efeito.json`, e o motor lê. Adivinhar pelo formato foi o defeito da primeira
versão desta peça, e ele desligava as 56 caladas.

| arquivo | o que é |
|---|---|
| `src/formula.ts` | avalia a árvore de fórmula. Sem regex, sem `eval` |
| `src/condicao.ts` | avalia a condição contra o vocabulário fechado da fase 13 |
| `src/derivados.ts` | as contas do livro, lidas de `valores_derivados.json` |
| `src/ficha.ts` | monta a ficha estática a partir de um contexto |
| `src/colecao.ts` | percorre a construção e junta os efeitos, com origem e portas |
| `src/contexto.ts` | de efeitos coletados para contexto, dado o estado |
| `src/escolha.ts` | oferece as opções de cada escolha e recusa a inválida |
| `src/equipamento.ts` | armadura, escudo e armas: CA, ataque, dano e proficiência |
| `src/motor.ts` | a porta de entrada: `montar(construcao, estado)` |
| `src/dataset.ts` | lê `dados/`. Só lê |
| `ouro/` | personagens de ouro: fichas conferidas à mão contra o livro |
| `testes/` | fórmula, ouro e negativo |

## Duas regras que o código segue à risca

**Nenhum id de conteúdo aparece aqui.** Nada de `if (classe === 'monge')`. O motor
sabe resolver `mod:DES` porque DES é atributo, e `nivel_classe:x` porque a classe
está no contexto — nunca porque conhece a classe. Se um nome de classe, magia ou
característica entrar neste diretório, o dataset perdeu o sentido.

**Desconhecido é erro, nunca zero.** Termo que não resolve, operação que não existe,
predicado fora do vocabulário: tudo lança `ErroDoMotor`. A alternativa — devolver 0 e
seguir — produz uma ficha errada que ninguém percebe, que é o defeito que a fase 13
passou uma fase inteira eliminando do dado.

## O motor não joga dado

`avaliar` devolve `{ valor, dados, parcelas }`. A parte fixa vai em `valor`; o dado
fica **simbólico** em `dados`. É por isso que a Iniciativa sai como `+3` com `1d20` ao
lado, e o dano do machado como `1d12 + 4`. Quem rola é a mesa.

## Personagens de ouro

`ouro/*.json` são fichas montadas à mão e conferidas contra a página do livro. Cada
uma diz, em `por_que_existe`, qual caso ela quebra:

- **`monge-1`** — a CA do Monge é 10 + Destreza + Sabedoria, e ela **concorre** com o
  cálculo padrão em vez de somar. Somando, dá 17 em vez de 15.
- **`barbaro-5`** — outra CA concorrente (esta permite Escudo), Pontos de Vida de cinco
  níveis, um Aumento no Valor de Atributo aplicado depois da criação, e a Fúria ligando
  vários efeitos condicionais de uma vez.
- **`clerigo-5`** — conjuração: espaços por círculo, magias preparadas, CD e ataque
  mágico, e o filtro "de um círculo para o qual você possui espaços" (53 opções, não
  108). É a única ficha **sem escolha em aberto**, a única que exercita melhoria de
  característica no resultado final, e a única de armadura: CA 16 = 13 (Cota de Malha
  Parcial) + 1 (Destreza, com teto 2) + 2 (Escudo).

Um golden é uma pessoa, e uma pessoa não cobre tudo. `equipamento.test.ts` existe por
isso: o teto de Destreza da armadura Média só morde com Destreza alta, e a falta de
proficiência com arma só aparece com uma arma que a classe não concede. Os dois casos
foram escritos depois de a mutação mostrar que sem eles nada reprovava.

Cada golden traz a `construcao` (espécie, antecedente, níveis e as escolhas
resolvidas) e o `esperado`. Não há mais contexto escrito à mão: a ficha sai da
construção. Subclasse e talento entram como escolha, não como campo próprio — no dado
eles são escolhas, e `conceder_subclasse` / `conceder_talento` é quem puxa a entidade.

## Por que há um teste negativo

Os goldens passaram na primeira execução, o que não prova nada sozinho. `negativo.test.ts`
planta oito defeitos e cobra que a ficha **mude**; se não mudar, o golden não estava
conferindo aquilo. Mais um caso de folga, que tem de passar: mexer no Carisma não pode
mexer na CA — sem ele, um motor que devolvesse lixo passaria em todos os outros.

A conferência que importa de verdade é a de mutação, feita à mão a cada mudança grande:
quebrar o motor de propósito e ver os goldens reprovarem. Somar os cálculos de CA base
em vez de escolher um derruba os dois goldens; esquecer a Constituição nos níveis
seguintes derruba o Bárbaro; fazer escolha não resolvida sumir sem virar pendência
derruba quatro testes.

Foi assim que apareceu uma asserção fraca: ignorar as portas dos efeitos aninhados
**não** reprovava, porque o teste comparava a quantidade de efeitos incidentes em vez
de olhar as portas. Trocado por "parado, nenhum efeito atrás de porta pode incidir".
O teste de mutação também serve para achar teste que só parece que confere.
