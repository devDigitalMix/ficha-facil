# Plano do motor de efeitos e do backend

Escrito em 2026-09-02, antes de qualquer linha de código do motor. O `PLANO-APP.md` diz **o que o
app faz**; este arquivo diz **como o dado vira ficha**. É a peça que falta entre os dois.

---

## 1. O que o motor é, e o que ele não é

O motor recebe uma **construção** (as escolhas que o jogador fez) e devolve uma **ficha** (todos os
valores derivados, com proveniência). Só isso.

Ele **não** conhece classe, magia nem monstro. A regra do projeto — "nenhuma entidade conhece as
outras" — só vale se ela valer também no código: se aparecer um `if classe == 'monge'` no motor,
o dataset inteiro perdeu o sentido. O teste é simples e deve virar lint: **nenhum id de conteúdo
pode aparecer como literal no código do motor.** Ids de conteúdo moram em `dados/`.

O que o motor sabe são os 103 **tipos de efeito**, os operadores de fórmula e o vocabulário de
runtime da seção 5.

### Fronteira com o backend

| camada | responsabilidade |
|---|---|
| **dataset** | o que as regras dizem |
| **motor** | aplicar as regras a uma construção; puro, sem I/O, sem banco |
| **backend** | guardar personagens, autenticar, sincronizar party, servir o compêndio |
| **app** | mostrar, e coletar as escolhas |

O motor é uma biblioteca pura. Mesma entrada, mesma saída, sempre — sem relógio, sem aleatório,
sem banco. É o que torna possível testar de verdade (seção 8) e o que permite rodá-lo no cliente
depois, se a Fase B pedir.

---

## 2. Estado × derivado — a divisão que já está no dado

O dataset já separa as duas coisas, e o motor tem de manter a separação:

**Estado** (o backend guarda, o motor recebe): PV atuais, PV temporários e de qual fonte, espaços
de magia gastos, recursos gastos, condições ativas, itens equipados, magias preparadas hoje,
concentração em curso.

**Derivado** (o motor calcula, ninguém guarda): CA, PV máximos, bônus de ataque, CDs, iniciativa,
percepção passiva, capacidade de carga, deslocamento, proficiências, lista de ações disponíveis.

Isso não é preferência de arquitetura: é o que `valores_derivados` (19 itens) e a decisão de deixar
PV atual fora da base já estabeleceram. **Guardar um derivado é criar a chance de ele divergir da
regra.** O único caso em que se guarda derivado é cache com invalidação explícita, e não vamos
precisar disso tão cedo.

---

## 3. O pipeline

```
construção  →  [1] resolver escolhas
            →  [2] coletar efeitos
            →  [3] filtrar por condição
            →  [4] empilhar
            →  [5] avaliar fórmulas
            →  ficha + log de proveniência
```

**[1] Resolver escolhas.** Percorre espécie, antecedente, classe (nível a nível), talentos e itens,
juntando as `escolha` que cada um abre. Para cada uma, resolve o `de` (chaves, filtro ou catálogo
inteiro) contra os catálogos e confere que o que o jogador escolheu está no conjunto permitido.
Escolha não resolvida é erro de construção, não silêncio.

**[2] Coletar efeitos.** Cada característica, traço, item equipado, talento e opção escolhida
contribui seus `efeitos`. Aqui entram os três tipos que mexem em outros efeitos e por isso precisam
de uma **segunda passada**: `melhorar_caracteristica`, `expandir_opcoes_de_escolha` e
`alterar_quantidade_de_escolha`. A ordem é: coletar tudo → aplicar as melhorias → recoletar.

**[3] Filtrar por condição.** Cada efeito traz `condicao` (árvore de `todas`/`alguma`/`nao`). O
motor avalia contra o contexto. Efeito sem condição está sempre ativo.

**[4] Empilhar.** `empilha` tem cinco valores e cada um é uma regra: `soma`, `maior_valor`,
`substitui`, `substitui_se_maior`, `unico`. Cálculos de CA base são o caso especial — vários
concorrem (`concorre_como: calculo_de_ca_base`) e **o jogador escolhe um**, não se somam.

**[5] Avaliar fórmulas.** Árvore com 10 operadores declarados em `valores_derivados.operacoes`.
Termos folha resolvem contra a ficha: `mod:CAR`, `prof`, `nivel_classe:bardo`, `coluna:truques`,
`deslocamento`, literais.

### Ordem de aplicação

Onde a ordem muda o resultado, ela precisa ser declarada, não emergente. A regra: **substituição
antes de soma; teto por último.** Ex.: a Defesa sem Armadura substitui o cálculo de base, os
modificadores somam em cima, e um teto (armadura Média limitando DES) corta no fim.

---

## 4. O motor de escolha é o coração

`escolha` é o tipo de efeito **mais usado do dataset: 230 ocorrências**, contra 170 de
`conceder_proficiencia`. Não é um detalhe da criação de personagem — é o mecanismo pelo qual quase
todo conteúdo entra na ficha.

O que ele precisa saber fazer:

- resolver `de.chaves`, `de.filtro` e `de.todo_o_catalogo`;
- resolver `de.de_variantes` (escolher entre as variantes de um item, como os 10 instrumentos);
- resolver `filtro_adicional` que depende do personagem (`ja_proficiente`, `sem_especializacao`);
- resolver os **filtros de runtime** que o validador não avalia e delega ao motor —
  `circulo_com_espaco_disponivel`, `nd_maximo`, `pre_requisitos_atendidos`, `sem_deslocamento_de_voo`
  (a lista fechada está em `FILTROS_DE_RUNTIME`, no `validar.py`);
- aplicar `efeito_por_item_escolhido` com `{{escolhido}}` substituído;
- respeitar `quantidade` (número, `coluna:`, ou por nível), `reescolhivel` e `quantidade_de_trocas`;
- honrar `escolhas_predefinidas` (o antecedente que pré-resolve a lista do Iniciado em Magia).

**Subir de nível cai aqui inteiro.** A progressão da classe diz o que chega no nível; as escolhas
que abrem são as `escolha` daquelas características; e `aviso_ao_subir_de_nivel` vira item de
checklist. Isso é a Fase A do `PLANO-APP.md` — "subir de nível sem esquecer nada" — e sai de graça
se o motor de escolha for bem feito.

---

## 5. ~~O maior risco: o vocabulário de runtime nunca foi declarado~~ — FEITO em 2026-09-02

> **Resolvido na fase 13**, antes de o motor começar, que era o ponto. O relato está em
> `revisao-fase13-vocabulario.md`; a lista fechada em `dados/vocabulario_de_runtime.json`.
> O que a seção previa em seis pares de sinônimo era bem pior: **625 ocorrências** reescritas.
> Predicados 204 → 178, gatilhos 153 → 127, durações 34 → 13, custos 13 → 9. O campo `momento`
> foi revogado (era o `gatilho` com outro nome em 257 de 264 vezes), a duração de tempo virou
> objeto e a comparação, que tinha oito sintaxes, virou uma. O texto abaixo fica como estava,
> porque é o diagnóstico que motivou a fase.

Os 103 tipos de efeito são catálogo, validados, com teste negativo. **O vocabulário que aparece
DENTRO deles não é.** Levantando do dado:

| vocabulário | distintos | declarado? |
|---|---|---|
| predicados de condição | **203** | não |
| `momento` / `gatilho` | **153** | não |
| `duracao` | **34** | não |
| `custo` | 13 | parcialmente (`custos_de_acao` tem 4) |
| `empilha` | 5 | no schema |
| operadores de fórmula | 10 | sim, em `valores_derivados.operacoes` |

Os 203 predicados e 153 gatilhos cresceram ao longo de doze fases sem nada os conferindo. **É a
maior superfície de implementação do motor e a menos verificada do projeto.** E já tem sinônimo
acidental — seis pares confirmados:

| escrito de um jeito | e de outro |
|---|---|
| `falhou_na_salvaguarda` (6×) | `alvo_falhou_na_salvaguarda` (1×) |
| `manter_concentracao` (3×) | `para_manter_concentracao` (1×) |
| `entrar_em_furia` (3×) | `ao_entrar_em_furia` (2×) |
| `conjurar_magia_de_feiticeiro_com_espaco` (2×) | `apos_conjurar_magia_de_feiticeiro_com_espaco` (1×) |
| `realizar_jogada_de_ataque` (1×) | `voce_realiza_jogada_de_ataque` (1×) |
| `dispersar` (1×) | `dispensar` (1×) — provável erro de digitação |

Cada par desses vira, no motor, ou dois `case` fazendo a mesma coisa, ou um efeito que
silenciosamente nunca dispara.

**Passo zero do motor, antes de qualquer execução:** promover condições, gatilhos e durações a
catálogos declarados (`predicados.json`, `gatilhos.json`, `duracoes.json`), com o validador
cobrando que todo predicado usado exista — a mesma regra que já vale para tipo de efeito, alvo e
tipo de dano. Os sinônimos morrem na fusão, e o motor passa a ter uma lista fechada do que precisa
implementar em vez de descobrir por tentativa.

Isso é trabalho de dataset, não de motor, e é a última dívida de extração.

---

## 6. Os 168 `efeito_narrativo`

São a regra que a base não executa. Distribuição:

| onde | quantos | quando importa |
|---|---|---|
| características de classe | 69 | Fase A |
| criaturas (Ap. B) | 43 | só Forma Selvagem e Fase C |
| talentos | 11 | Fase A |
| Surto de Magia Selvagem | 8 | Feiticeiro Selvagem |
| espécies | 7 | Fase A |
| resto (dádivas, invocações, manobras, condições, maestrias) | 30 | Fase A |

O motor **não tenta interpretá-los**. Ele os devolve como *avisos ativos* da ficha: texto com a
página, marcado como "resolve na mesa". Isso é fiel ao princípio do `PLANO-APP.md` — o jogo continua
na mesa — e evita a pior saída possível, que seria o motor adivinhar.

Alguns virarão primitivo quando doerem. O critério para promover: **o mesmo efeito narrativo
aparecer em três lugares diferentes.** Foi assim que nasceram `movimento_forcado`,
`tratar_dado_de_dano_minimo` e `assumir_bloco_de_estatisticas`.

---

## 7. Superfície do backend

```
GET  /compendio/{catalogo}            catálogo inteiro, cacheável (o dado é imutável entre versões)
GET  /compendio/{catalogo}/{id}
POST /personagens                     cria a partir de uma construção
GET  /personagens/{id}                estado + ficha calculada + proveniência
PATCH /personagens/{id}/estado        PV, recursos, condições, espaços — só estado
POST /personagens/{id}/subir-nivel    devolve o checklist e as escolhas a fazer
POST /personagens/{id}/escolhas       resolve escolhas pendentes
```

Notas que vêm do formato do dado:

- **O compêndio é estático.** `dados/` é imutável entre builds; serve com `ETag` da versão do
  dataset e cache longo. Não precisa de banco.
- **O personagem guarda a CONSTRUÇÃO, não a ficha.** Guardar os ids escolhidos e o estado; a ficha
  se recalcula. Assim, corrigir uma regra no dataset corrige todos os personagens — que é a razão
  de o dado existir.
- **Versão do dataset no personagem.** Se a base mudar de um jeito que invalide uma escolha (um id
  que sumiu), o personagem precisa saber contra qual versão foi construído para o app avisar em vez
  de quebrar.
- **A proveniência é resposta, não log.** `CA 17 = 10 + 3 DES + 4 SAB` sai do campo `parcelas` dos
  valores derivados; o backend devolve junto com o número.

---

## 8. Como saber que o motor está certo

O projeto já tem a cultura: validador + teste negativo + reconstrução. O motor precisa do
equivalente.

> Três existem desde 2026-09-02, em `motor/ouro/`: um Monge 1, um Bárbaro 5 e uma Clériga 5
> (`revisoes/revisao-fase17-clerigo-de-ouro.md`). O que falta desta lista continua valendo —
> o Mago 9, o Feiticeiro 10, o Druida 8 em Forma Selvagem e o Paladino 6.

**Personagens de ouro.** Um punhado de personagens montados à mão, com a ficha inteira conferida
contra o livro, virando teste de regressão. Sugestão de cobertura: um Monge nível 1 (CA sem
armadura), um Bárbaro 5 (fúria, resistências, várias camadas), um Mago 9 (livro, preparação,
espaços), um Feiticeiro 10 (Metamagia e conversão de recurso), um Druida 8 em Forma Selvagem (troca
de bloco de estatísticas), um Paladino 6 (aura que várias características engrossam), e um
multiclasse depois que multiclasse entrar.

**Teste negativo do motor**, no mesmo espírito dos sete que já existem: construção com escolha
inválida, com pré-requisito não atendido, com dois cálculos de CA base concorrendo, com efeito cuja
condição não bate — e cobrar que o motor recuse ou ignore, em vez de calcular errado calado.

**`verificar_derivacao.py` é o embrião disso** e prova hoje uma trilha só (bônus de ataque, sem uma
regra de D&D escrita no script). O motor deve tornar esse script obsoleto por generalização.

**Cobertura de tipos de efeito.** 102 dos 103 estão em uso no dataset e **nenhum jamais foi
executado**. Vale um relatório de cobertura: quais tipos os personagens de ouro exercitam. O que
ficar em zero é código não testado ou dado que ninguém consome.

---

## 9. Ordem sugerida

1. ~~**Declarar o vocabulário de runtime** (seção 5). Dataset, não motor. Sem isso o motor é escrito
   contra alvo móvel.~~ **Feito em 2026-09-02** — `revisao-fase13-vocabulario.md`.
2. ~~**Avaliador de fórmula + valores derivados.** Fecha a ficha estática: atributos, CA, PV, ataque,
   CDs, iniciativa.~~ **Feito em 2026-09-02** — `motor/`, em TypeScript, zero dependências.
   Ver `revisao-fase14-motor-passo-2.md`. Decidido junto: **os personagens de ouro vêm primeiro**,
   e o motor nasce tendo de acertá-los.
3. ~~**Coletor de efeitos + condições + empilhamento.** A ficha passa a reagir ao que o personagem
   tem.~~ **Feito em 2026-09-02** — `revisoes/revisao-fase15-motor-passo-3.md`. A ficha sai da
   construção ponta a ponta, e escolha não resolvida virou pendência (o checklist de subir de nível).
4. ~~**Motor de escolha.** Destrava criar personagem e subir de nível — a Fase A inteira.~~
   **Feito em 2026-09-02** — `revisoes/revisao-fase16-motor-de-escolha.md`. O checklist deixou de
   ser lista de nomes e virou a tela: rótulo, quantidade e as opções de verdade.
5. ~~**Backend com os endpoints da seção 7.**~~ **Feito em 2026-09-02** — `backend/`, zero
   dependências, ver `revisoes/revisao-fase19-backend.md`. Ele achou três defeitos no motor, o
   pior deles em escolha de característica repetível: o Aumento do nível 8 sobrescrevia o do 4.
6. **Fase A do app.**

A releitura das 391 magias (`BACKLOG.md` §B6.5) roda em paralelo, em lotes. Ela não bloqueia nada
disto — ver seção 10.

---

## 10. Por que uma magia errada não trava o motor

Pergunta do João, e a resposta é boa: **o motor não lê a minha prosa.**

O que ele lê de uma magia são campos estruturados — `nivel`, `escola`, `dano`, `salvaguarda`,
`area`, `alcance`, `duracao`, `concentracao`, `componentes`, `aprimoramento`, `condicoes_citadas` —
e esses vêm do **parser lendo o livro**, não da paráfrase. A `descricao_curta` é texto de exibição.

As oito magias em que eu tinha escrito regra de 2014 provam o ponto: em todas, o campo estruturado
já estava certo enquanto a frase estava errada.

| magia | minha frase dizia | o campo estruturado tinha |
|---|---|---|
| Muralha de Vento | 3d8 | `dano: 4d8` ✓ |
| Muralha Prismática | 10d6 | `dano: 12d6` ✓ |
| Nevasca | 3d8 de dano | `dano: null` ✓ (a magia não causa dano) |
| Nuvem Fétida | Incapacitado | `condicoes_citadas: [envenenado]` ✓ |
| Presença Régia | Amedrontado | `condicoes_citadas: [caido]` ✓ |
| Polimorfia | Enfeitiçado | `condicoes_citadas: null` ✓ |

Então: **corrigir uma paráfrase é uma linha em `descricoes_magias.py` e um rebuild. Nunca toca o
motor.** É por isso que a releitura pode rodar em paralelo com o backend sem risco de retrabalho.

### Três ressalvas, para não vender facilidade demais

1. **O parser também erra.** Moléstia ficou sem os `14d6` por causa de um corte de bloco, e Raio
   Guia e Dominar Fera saíam sem círculo numa reconstrução. Erro de parser **é** erro do motor,
   porque o motor lê aquele campo. A diferença é que erro de parser é sistemático e o validador e a
   reconstrução pegam; erro de paráfrase é individual e só a leitura pega.
2. **Um bloco estruturado de magia é escrito à mão:** `pontos_de_vida`, nas 16 magias que mexem em
   PV máximos ou temporários. Esse não veio de parser e tem o mesmo risco da prosa — com a diferença
   de que o motor **vai** executá-lo.
3. **Característica de classe é hand-written até o fim.** As 388 características não têm parser: o
   que o motor executa ali fui eu que escrevi. É o que o validador, os sete testes negativos e os
   personagens de ouro existem para cobrir.

Resumindo o risco por origem:

| origem | o motor executa? | como se corrige |
|---|---|---|
| paráfrase de magia | não | uma linha + rebuild |
| campo estruturado de magia (parser) | sim | conserta o parser, rebuild, reconstrução confere |
| `pontos_de_vida` de magia (à mão) | sim | uma linha + rebuild |
| característica / talento / espécie (à mão) | sim | gerador + rebuild; coberto por teste negativo |
| bloco de criatura (parser + paráfrase) | números sim, prosa não | conforme a origem |
