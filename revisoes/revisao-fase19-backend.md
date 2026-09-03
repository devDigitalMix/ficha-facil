# Fase 19 — Backend

Escrito em 2026-09-02. É o passo 5 do `PLANO-MOTOR.md`: os endpoints da seção 7, com o motor
por trás. `backend/`, TypeScript, **zero dependências** — `node:http` e mais nada.

`testes/rodar_todos.py --rapido`: **16 de 16 passos limpos**. Motor 72/72, backend 40/40.

---

## O que ficou pronto

Os sete endpoints do plano, mais três que o uso pedia (saúde, listar, apagar). O backend é fino
de propósito: **nenhuma regra de D&D mora nele.** O motor sabe aplicar regra, o dataset sabe qual
regra é, e o backend liga uma coisa na outra. As decisões que valem registrar:

**O personagem guarda a construção, não a ficha.** A ficha se recalcula a cada leitura. É o que
faz o dataset valer a pena — corrigir uma regra em `dados/` corrige todos os personagens de uma
vez. Um teste cobra isso olhando o que ficou no armazém.

**Estado é o que a mesa muda; o resto é derivado.** O `PATCH` aceita PV, temporários, espaços
gastos, recursos, condições e concentração, e recusa qualquer outra coisa com 400 — inclusive
tentativa de gravar CA. A fronteira não é gosto de arquitetura: é o que `valores_derivados` e a
decisão de deixar PV atual fora da base já tinham estabelecido.

**A versão do dataset é o resumo do conteúdo de `dados/`.** Serve de ETag do compêndio (com
`immutable`: quem já tem a versão recebe 304 em vez das 391 magias de novo) e de carimbo no
personagem. Base diferente não quebra a ficha — ela vem com `aviso_de_versao` junto.

---

## O que o backend achou no motor

Três defeitos, todos encontrados por tentar usar o motor de verdade em vez de por leitura.

### 1. Escolha repetível compartilhava id — e o nível 8 sobrescrevia o 4

O pior dos três. `construcao.escolhas` é indexado por id, e o Aumento no Valor de Atributo chega
no 4, 8, 12 e 16 **com o mesmo id declarado**. Resultado: um personagem nunca conseguia dois
talentos diferentes, e o segundo aumento reaplicava o primeiro.

Apareceu quando um teste tentou subir uma Clériga até o nível 20 e o motor acusou que a Sabedoria
passaria de 20. A mensagem parecia um erro de regra; era o mesmo aumento aplicado cinco vezes.

O id agora leva o nível da concessão: `asi_escolha_de_talento@4`, `@8`. Só características
declaradas `repetivel` são qualificadas — as outras 200 e tantas escolhas do dataset continuam com
o id nu, que é mais legível. O sufixo **propaga para dentro**: o talento que o aumento concede abre
escolhas próprias (`avatributo_modo`, `avatributo_dois`), e elas pertencem àquele aumento, não ao
do nível seguinte. Foram cinco pontos de propagação — efeito nomeado, efeito aninhado, talento
concedido, efeito por item escolhido — e o teste só ficou verde quando o último entrou.

São **cinco** as características repetíveis que abrem escolha: Aumento no Valor de Atributo,
Arcana Mística, Especialista (Ladino), Especialista (Bardo) e Metamagia. Todas estavam quebradas.

### 2. `ErroDoMotor` não definia `name` — e todo erro do motor virava 500

`class ErroDoMotor extends Error {}` deixa `name` como `'Error'`. O backend classificava por nome
para responder 422, e nunca casava. Somado a `porId` lançar `Error` puro, pedir uma espécie que o
livro não tem respondia **500** — o servidor assumindo uma culpa que era do cliente.

Corrigido nos dois lados: `ErroDoMotor` define `name`, `porId` passou a lançá-lo, e o backend
classifica por `instanceof` em vez de comparar string. Nome é string, e string se digita errado.

### 3. Incompleta não é inválida

O motor devolvia todo problema de escolha com a mesma cara. Mas subir de nível produz escolha
incompleta o tempo todo — a Clériga que preparava 9 magias no nível 5 passa a preparar 10 no 6 — e
recusar isso impediria de subir de nível quem fez tudo certo.

`Problema` ganhou `tipo` (`opcao_invalida`, `incompleta`, `excedente`, `repetida`,
`dependencia_nao_resolvida`) e `faltam`. O backend recusa defeito com 422 e devolve pendência com
200, junto do checklist. Sem isso ele teria de adivinhar pela frase da queixa.

---

## Desempenho: 49 ms → 2,4 ms por ficha

Quase todo o tempo era reler e reparsear `dados/` a cada pedido, com `magias.json` respondendo pela
maior parte. `dataset.ts` passou a memorizar a leitura.

Isso não fere a pureza do motor — `dados/` é imutável em execução, mesma entrada continua dando
mesma saída — mas cria um risco novo: a leitura passa a devolver **o mesmo objeto**, e qualquer
código que mutasse uma entidade do dataset envenenaria as montagens seguintes. O teste que guarda
isso monta cada golden duas vezes e compara. Passou, o que também é uma informação: nada no motor
muta o dado que lê.

---

## Ler nunca explode

O `PLANO-MOTOR` §7 pede que a base mudar de um jeito que invalide uma escolha faça o app **avisar
em vez de quebrar**. A primeira versão não fazia isso: um id que sumisse derrubava o `GET` inteiro,
e o jogador perdia o personagem de vista justamente quando precisava corrigir a escolha.

Agora a leitura é tolerante — devolve `200`, o personagem, `ficha: null` e um `erro_de_ficha` com
o que houve e contra qual versão ele foi construído. **A escrita não é**: `POST` e `PATCH`
continuam recusando com 422, porque ali quem propõe a mudança é o cliente.

---

## Aberto

- **Autenticação.** O `PLANO-MOTOR` lista "autenticar" entre as responsabilidades do backend, e
  não há nada hoje. Não inventei esquema: quem vai usar, de onde, e se há mais de uma pessoa por
  personagem são decisões do João. Enquanto isso, o serviço só serve para rodar local.
- **Escrita concorrente.** `PATCH` é ler-modificar-gravar sem trava: dois pedidos simultâneos no
  mesmo personagem perdem um. Não morde hoje (uma pessoa, um cliente), mas morde na Fase B, em que
  mestre e jogador mexem na mesma ficha. A solução — número de revisão no personagem e `If-Match` —
  é pequena, e o lugar dela é junto do desenho da sincronização, não antes.
- **CORS.** Não há. A Fase A vai precisar, e a resposta depende de onde o app for servido.
- **Serialização do catálogo grande.** `magias.json` é serializado a cada pedido novo (~12 ms). Com
  ETag + `immutable` isso acontece uma vez por cliente por versão. Se um dia não bastar, guardar o
  texto já serializado é uma linha.
