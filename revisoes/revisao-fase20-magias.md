# Fase 20 — as 391 magias, uma por uma

Feita em 2026-09-03, depois do backend (fase 19). A releitura completa das paráfrases de magia contra o texto do
capítulo 7, magia por magia, lendo os dois lado a lado.

`testes/rodar_todos.py`: **todos os passos limpos.** Motor em 70 de 70, `validar.py` com
0 erros e 0 avisos, `checar_schema.py` 76/76, dez testes negativos e `reconstruir.py
--comparar` em 67/67 sem diferença de conteúdo. O backend da fase 19 não foi tocado: esta
fase não mexe em nada que ele leia além do texto que ele serve.

**89 paráfrases reescritas de 391.** Vinte e três delas carregavam regra de **2014**.

---

## Por que uma releitura, e não mais auditoria automática

O `auditar_descricoes.py` compara **fatos verificáveis por termo**: se a paráfrase diz
"3d8" e o livro diz "4d8", ele pega. Ele encontrou oito magias assim, e a partir daí
passou a dar 6 achados em 391 — todos falsos positivos.

O que ele não pega é o que só a leitura pega:

- **regra de 2014 escrita com a segurança de quem lembra bem** — os números batem, a
  mecânica é de outra edição;
- **inversão de gatilho** — "começa o turno" onde o livro diz "termina o turno";
- **nome de efeito trocado** — "Mão Agarradora" onde o livro diz "Mão Esmagadora";
- **invenção plausível** — "Identificar não detecta itens amaldiçoados", que é verdade
  em 2014 e simplesmente não está escrito em 2024.

Nenhum desses tem termo para conferir. A única forma de pegá-los era ler.

## A bancada

`revisar_magias.py` põe lado a lado, em doze lotes de 35 magias ordenadas por círculo e
nome, o **corpo extraído do capítulo 7** e a **paráfrase escrita à mão**, com os campos
estruturados (alcance, duração, concentração, ritual) no cabeçalho, porque a paráfrase às
vezes os contradiz.

```
python3 revisar_magias.py        # quantos lotes, e o que tem em cada
python3 revisar_magias.py 3      # imprime o lote 3
```

A ferramenta não julga nada. O custo dela é o tempo de leitura — que é o preço, não um
problema a contornar.

## O defeito que a própria bancada revelou

No lote 2, "Benção" apareceu com `(SEM TEXTO DO LIVRO)`. Não era falta de texto: era o
**nome do catálogo não casar com a entrada do capítulo 7**.

| no catálogo | no capítulo 7 |
|---|---|
| Benção | **Bênção** (p. 248) |
| Pele-casca | **Pele-Casca** (p. 316) |
| Invocar Morto-vivo | **Invocar Morto-Vivo** (p. 296) |
| Proteção contra Energia | **Proteção Contra Energia** (p. 320) |

De onde veio: `parse_magias.ler_nomes` resolve o nome quebrado pela coluna usando a lista
de nomes conhecidos, que vem das **listas de magia das classes**. Quando a lista da classe
imprime com outra caixa ou sem o circunflexo, é a grafia da lista que ganha — e a entrada
do capítulo 7, que é onde a magia é definida, perde.

O efeito prático era pior do que uma letra: **essas quatro magias nunca tiveram corpo
extraído, então nunca passaram por conferência nenhuma.** Por sorte as paráfrases estavam
certas (`descricoes_magias.py` já usava a grafia do livro, e o casamento por id salvou o
conteúdo), mas isso foi sorte, não processo.

Consertado por `gerar_ajustes_nomes_de_magia.py`, e **fechado com uma guarda**: o
`auditar_descricoes.py` agora **falha** se qualquer magia do catálogo não tiver entrada no
capítulo 7. Um nome que não casa deixou de ser silêncio.

## As 23 regras de 2014

Esta é a lista que justifica a fase inteira. Cada uma parecia certa.

| magia | a paráfrase dizia (2014) | o livro de 2024 diz |
|---|---|---|
| **Reflexos** | cópia tem CA 10 + Destreza | role 1d6 por cópia; 3+ e a cópia é atingida |
| **Telecinese** | objeto de até 500 kg | objeto **Enorme ou menor** |
| **Localizar Criatura** | água corrente bloqueia | **chumbo** bloqueia |
| **Mão de Bigby** | nomes e efeitos de 2014 | quatro efeitos por **Ação Bônus** |
| **Passo Arbóreo** | salvaguarda para ficar na árvore | terminar cada turno **fora** dela |
| **Mau Olhado** | Doente = Desvantagem | Adoecer = condição **Envenenado** |
| **Gargalhada Nefasta** | Vantagem se INT ≤ 4 | Vantagem quando o dano acionou |
| **Dominar Fera** | gastar ação para controlar o turno | comandos **sem ação** pelo vínculo |
| **Símbolo** | efeito "Enlouquecer" | Atordoamento, Discórdia, Dor, Medo, Morte, Sono |
| **Transição Planar** | também bane uma criatura | só a viagem |
| **Tempestade de Fogo** | pode poupar a vegetação | não existe |
| **Convocar Relâmpagos** | dano sobe sob tempestade | não existe |
| **Tranca Arcana** | CD para forçar sobe 10 | senha destranca por 1 minuto |
| **Identificar** | não detecta maldição | não existe |
| **Simular Morte** | suspende doenças | não existe |
| **Encontrar o Caminho** | não pode se perder | sabe distância, direção e bifurcação |
| **Espinho Mental** | Desvantagem em testes | o alvo não se esconde nem fica Invisível para você |
| **Defensor da Fé** | Ação Bônus para mover | paira parado; some com 60 de dano |
| **Contato Extraplanar** | Desvantagem em INT | **Incapacitado** até o Descanso Longo |
| **Dissipar o Bem e o Mal** | função "Repelir" | **Quebrar Encantamento** |
| **Palavra Sagrada** | Cego por 1 minuto | banimento de 24 h para os quatro tipos |
| **Montaria Fantasmagórica** | 40 km a galope | 30 m de Deslocamento, 20 km/hora |
| **Alterar-se** | "bônus de acerto se for mágico" | usa o **modificador de conjuração** |

## Os três defeitos maiores fora dessa lista

**Proteger Fortaleza** (p. 321) — a paráfrase descrevia **outra magia**. Falava de
teleporte bloqueado e dano por tipo de criatura, que é **Proibição**. O que a magia faz é
névoa nos corredores, teias nas escadas, portas trancadas como Tranca Arcana e um efeito
mágico à escolha.

**Desejo** (p. 268) — a magia mais visível do livro, errada em três frentes: o dano do
estresse é **Necrótico** (dizia Energético), não há **Exaustão** nem "−4 em Força" (a
Força **se torna 3** por 2d4 dias), e faltavam dois dos sete efeitos — Criação de Objeto e
Reformar a Realidade.

**Invocar Animais** (p. 291) — dano **Cortante** e não Perfurante, o bando acompanha
**quando você se move** e não por Ação Bônus, e o alcance da salvaguarda é **3 m**, não 1,5.

## O padrão que se repetiu mais: começar × terminar

Nove magias trocavam o gatilho da salvaguarda de área. Onde o livro escreve **"termina o
turno"**, a paráfrase escrevia "começa o turno" — e a diferença muda quem toma dano em
cada rodada.

Guardiões Espirituais, Raio Lunar, Névoa Mortal, Nuvem Incendiária, Praga de Insetos,
Tempestade Radiante de Jallarzi, Tentáculos Negros de Evard, Fome de Hadar, Muralha de
Vento.

É um erro de leitura, não de memória, e é o mais fácil de repetir: as duas frases têm o
mesmo formato, e a errada soa razoável.

## Paráfrases por referência

Quatro entradas eram do tipo "Como *X*, mas contra Humanoides": Enfeitiçar Pessoa,
Paralisar Pessoa, Dominar Pessoa, Dominar Monstro. Duas delas apontavam para uma paráfrase
que **estava errada**, então herdavam o erro sem que nada acusasse.

As quatro foram reescritas autônomas. Uma paráfrase que depende de outra não é conferível
sozinha, e o motor não segue referência.

## O que isto não muda

O motor continua lendo o **campo estruturado**, não a paráfrase — como está no
`PLANO-MOTOR.md` §10. Nenhum número de combate mudou; nenhum teste do motor precisou ser
tocado. O que mudou é o texto que o jogador lê na ficha, que agora diz o que o livro de
2024 diz.

## O que vem

O backend fechou na fase 19; o passo seguinte é a **Fase A do app** (`PLANO-APP.md`).

Continuam de antes: os 168 `efeito_narrativo`, as **112 paráfrases de criatura** — que
nunca passaram por esta releitura e são o mesmo risco — e a regra de mesa do §B6.6
(Maestria em Arma no nível 20 do Guardião e do Paladino), que espera a camada de
overrides.
