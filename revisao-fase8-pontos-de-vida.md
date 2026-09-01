# Fase 8 — Pontos de Vida máximos e temporários

Validador: **0 erros, 0 avisos**. JSON Schema: **58 arquivos, todos passam**. Testes negativos:
**11 de 11** (lote novo) e **18 de 18** (lote anterior, sem regressão). `verificar_derivacao.py`:
continua fechando.

Você pediu para poder alterar PV máximos e temporários, deixando os PV atuais no backend, e
lembrou que magias e a Forma Selvagem também dão temporários. É isso que está feito. **Mas o
trabalho descobriu oito descrições de magia erradas minhas, e a raiz delas** — está tudo abaixo,
sem enfeite.

## 1. O que você pediu

### `pontos_de_vida_maximos` (novo)

A conta inteira, com as parcelas rotuladas para o log de proveniência:

```
Pontos de Vida do nível 1              sempre
Pontos de Vida dos níveis seguintes    se nível > 1
bônus de características               se tem característica que aumenta o máximo
bônus temporário (magia ou efeito)     se efeito ativo que aumenta o máximo
reduções do máximo                     se efeito ativo que reduz o máximo
```

Mais as quatro regras que o livro dá em volta da conta, cada uma com a página: o **mínimo de 1 por
nível** (p. 42), o **recálculo retroativo** quando o modificador de Constituição sobe — sobe 1 por
nível JÁ ALCANÇADO, não só no nível atual (p. 42) —, a **morte quando o máximo chega a 0** (p. 28)
e a **cura que não ultrapassa o teto**, com o excedente perdido (p. 27).

Os dois derivados que já existiam (`pontos_de_vida_no_nivel_1` e `pontos_de_vida_por_nivel`)
estavam **sem parcelas**. Ganharam as parcelas e a tabela **Pontos de Vida Fixos por Classe** da
p. 42 com os números impressos (7/6/5/4), em vez de eu deduzir do Dado de Vida.

### `pontos_de_vida_temporarios` (novo, e separado de propósito)

Não é uma parcela do máximo — somar as duas coisas é o erro clássico. É derivado próprio, com as
cinco regras do capítulo 1 (p. 28-29) gravadas:

- somem primeiro, e o resto do dano sai dos PV;
- **não acumulam — e o JOGADOR escolhe** se mantém os que tem ou fica com os novos. Não é
  automático nem é "o maior valor"; deixei explícito porque é fácil o backend implementar errado;
- não somam aos PV, a cura não os restaura, e recebê-los não é cura;
- com 0 PV, receber temporários **não** devolve a consciência;
- acabam ao se esgotarem ou no fim de um Descanso Longo.

Os PV **atuais** ficaram de fora, como você disse — são estado de jogo, não derivado. Isso está
escrito na nota do derivado para ninguém "completar" a base depois.

### Quem concede temporários já está declarado

**Forma Selvagem**: os PV temporários iguais ao nível de Druida estavam num **campo solto**
(`regras_enquanto_multimorfado.pv_temporarios`) em vez de um efeito — o backend teria de conhecer o
nome do campo. Virou efeito `pontos_de_vida_temporarios` de verdade. O Círculo da Lua, que já
usava efeito, continua substituindo por três vezes o nível.

**Magias**: 16 magias mexem em PV máximos ou temporários e nenhuma declarava isso em campo
estruturado, só na paráfrase. Agora todas têm bloco `pontos_de_vida`:

| concedem temporários | mexem no máximo |
|---|---|
| Armadura de Agathys, Vitalidade Vazia, Heroísmo, Palavra de Poder: Fortificar, Polimorfia, Polimorfia Total, Metamorfose, Formas Animais | Auxílio (+5, e nos atuais), Banquete de Heróis (+2d10), Moléstia (reduz, com piso 1), Aura de Vida (impede redução), Restauração Maior (remove redução), Simulacro (metade, na duplicata) |

Mais Mão de Bigby (os PV da mão saem do seu máximo) e Sinal de Esperança (cura sempre máxima — não
mexe no teto, e por isso ficou em campo separado).

**Uma fora**: *Convocar Celestial* dá 1d10 temporários, mas isso está no bloco de estatísticas do
Espírito Celestial, e blocos de criatura estão fora do escopo por decisão sua. Fica anotado.

### E a ligação que faltava

O buraco apareceu porque um alvo apontava para um derivado inexistente e nada reclamava. Agora
`alvos.json` declara `derivado_id`, **8 alvos** apontam para o derivado que os monta, e o validador
cobra a promessa. Também declarei as **10 operações de fórmula** válidas dentro do próprio
catálogo — antes cada gerador podia inventar um `op` e ninguém via.

## 2. O que eu achei sem procurar, e é mais grave

### O parser cortava o fim de 55 magias

Ao ler o texto de Moléstia notei que ele acabava no meio da frase. A causa: o parser encontrava o
nome da próxima magia e cortava **a linha inteira** onde ele estava. Funciona quando a linha só
tem o nome — mas quando a última frase da magia está colada no nome da próxima
(`…abaixo de 1.Montaria Fantasmagórica`), o corte engolia o fim do corpo. **55 das 391.**

Custou mecânica de verdade: *Moléstia* estava **sem os 14d6**, *Palavra de Poder: Matar* sem os
12d12, *Fonte do Luar* sem a condição Cego, *Onda Destrutiva* sem o "metade em caso de sucesso", e
onze magias com o texto de aprimoramento cortado. Corrigido — sobraram 12 corpos truncados, todos
por outro motivo (tabela no meio da entrada), nenhum perdendo mecânica.

No mesmo caminho, o regex de dano só aceitava "X pontos de dano Y". O livro também escreve **"14d6
de dano Necrótico"**, seco. Por isso Moléstia ficava sem dano mesmo com o texto inteiro.

### Oito descrições minhas estavam erradas — e o padrão é o que você me avisou

Aqui eu preciso ser direto: **em oito magias eu escrevi o que eu "lembrava" de D&D 2014 em vez do
que a página 2024 diz.** É exatamente o erro que a instrução do projeto manda evitar, e eu o
cometi.

| magia | eu escrevi | o livro 2024 diz |
|---|---|---|
| **Nevasca** | 3d8 de dano Contundente e salvaguarda de Constituição | **Nenhum dano.** Salvaguarda de Destreza ou fica Caído e perde a Concentração |
| **Nuvem Fétida** | fica Incapacitado | fica **Envenenado** até o fim do turno, e assim não pode ação nem Ação Bônus |
| **Presença Régia de Yolande** | condição Amedrontado | condição **Caído**, e você pode empurrar até 3 m |
| **Polimorfia** | "fica Enfeitiçado quanto ao comportamento" | **não há Enfeitiçado.** Recebe PV temporários iguais aos PV da forma, e a magia acaba quando zeram |
| **Sentido Feral** | "fica Cego e Surdo aos seus próprios sentidos" | **não existe essa cláusula.** Você percebe pelos dois |
| **Moléstia** | "Não afeta Constructo nem Morto-vivo" | não reduz o máximo do alvo **abaixo de 1** |
| **Muralha de Vento** | 3d8 | **4d8**, metade em caso de sucesso |
| **Muralha Prismática** | 10d6 por camada, "Índigo" | **12d6** por camada, e a camada 6 chama-se **Anil** |

Todas as oito são valores de 2014. As oito estão corrigidas.

### E uma ferramenta para isso não depender da minha atenção

Escrevi `auditar_descricoes.py`: ele pega **termo por termo** os fatos verificáveis de cada
paráfrase — dados de dano, atributo da salvaguarda, condições nomeadas, distâncias — e cobra que
apareçam na entrada da magia no PDF, comparando com a página **e** com o corpo isolado pelo parser.

Rodando agora nas 391: **6 magias para conferir à mão**, e conferi as seis — são falso positivo
(uso figurado de "invisível" em Aprisionamento e Limpar a Mente, e magias de várias seções em que
a salvaguarda mora num trecho que o parser separa). Foi assim que as oito apareceram.

**Sendo honesto sobre o alcance dele:** ele só vê o que é verificável por termo. Uma paráfrase que
inverte "em caso de sucesso" e "se falhar", ou que erra uma duração, passa. Se você quiser, o passo
seguinte é eu reler as 391 entradas contra a paráfrase, uma a uma — é o tipo de trabalho que só a
leitura pega, e depois desses oito casos eu acho que vale.

## 3. Checagens novas no validador

| checagem | o que pega |
|---|---|
| `derivado_id` em `alvos` | alvo prometendo um valor derivado que não existe — **o defeito desta fase** |
| `operacoes` declaradas | `op` de fórmula fora do vocabulário |
| `pontos_de_vida_temporarios` | efeito que concede temporários sem dizer quantos |
| bloco `pontos_de_vida` de magia | temporários sem quantidade; máximo alterado sem dizer se aumenta, reduz, impede ou remove |

## 4. Estado geral

```
10 de 12 classes · 40 subclasses · 320 características · 53 catálogos · 80 tipos de efeito
391 magias, todas detalhadas · 16 com bloco de Pontos de Vida
19 valores derivados (era 17) · 10 operações de fórmula declaradas
26 alvos, 8 ligados ao derivado que os monta
```

Falta do livro: **Guardião** (p. 117), **Paladino** (p. 167) e os **capítulos 4 e 5**.
