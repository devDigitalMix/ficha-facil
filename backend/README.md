# Backend

Guarda personagens, serve o compêndio e chama o motor. **Uma dependência**: o driver
oficial do MongoDB. Fora ela, é `node:http`, `node:fs` e o TypeScript rodando direto
com os tipos apagados — o motor continua sem dependência nenhuma.

```bash
cd backend
npm install       # só o driver do Mongo
npm run teste     # 82 testes (4 pulam sem um Mongo — veja abaixo)
npm run servir    # http://localhost:8787, lendo .env se existir
```

## Configuração

Tudo sai do ambiente, e **nada é obrigatório**: sem arquivo nenhum o backend sobe, guarda
os personagens em arquivo e assina a sessão com um segredo gerado na hora. Isso é de
propósito — dá para clonar e rodar sem cadastrar nada em lugar nenhum.

`.env.exemplo` lista os nomes que existem, com o que cada um muda ao ser preenchido.
Para começar:

```bash
cp .env.exemplo .env      # e preencha o que quiser usar
```

O `.env` não vai para o git; o `.env.exemplo` vai, e é a documentação das variáveis.
Os dois marcadores dentro dele dizem o que já é lido hoje (servidor, armazém, Mongo e
contas) e o que ainda não existe no código (as imagens no S3).

## O que ele faz — e o que ele não faz

Ele é **fino de propósito**. Nenhuma regra de D&D mora aqui: o motor sabe aplicar
regra, o dataset sabe qual regra é, e o backend só liga uma coisa na outra. Se
aparecer um `if` sobre classe, magia ou nível neste diretório, está no lugar errado.

| rota | o que faz |
|---|---|
| `GET /saude` | responde, e diz contra qual dataset |
| `GET /compendio` | o índice: que coleções existem, de que família, com quantos itens |
| `GET /compendio/{nome}` | a coleção inteira |
| `GET /compendio/{nome}/{id}` | um item |
| `GET /personagens` | a lista, com o mais recente no topo |
| `POST /personagens` | cria a partir de uma construção |
| `GET /personagens/{id}` | estado + ficha calculada + proveniência + checklist (tolerante: avisa em vez de quebrar) |
| `PATCH /personagens/{id}/estado` | só estado |
| `POST /personagens/{id}/subir-nivel` | sobe, e diz o que abriu e o que falta completar |
| `POST /personagens/{id}/escolhas` | resolve escolhas pendentes |
| `DELETE /personagens/{id}` | apaga |

## Quatro decisões que valem explicar

**O personagem guarda a construção, não a ficha.** A ficha se recalcula a cada
leitura. É o que faz o dataset valer a pena: corrigir uma regra em `dados/` corrige
todos os personagens de uma vez. Guardar a ficha seria criar uma segunda verdade, que
envelhece calada. `POST /personagens` devolve a ficha, mas não é isso que fica no
disco — o teste `o personagem guarda a construção, nunca a ficha` cobra.

**Estado é o que a mesa muda; o resto é derivado.** O `PATCH` aceita Pontos de Vida
atuais, temporários, espaços gastos, recursos gastos, condições e concentração — e
**recusa** qualquer outra coisa com 400. Tentar gravar a CA é erro, não conveniência:
a CA é uma conta, e uma conta guardada é uma conta que um dia diverge da regra.

**Escolha incompleta não é escolha errada.** Subir de nível produz a primeira o tempo
todo — a Clériga que preparava 9 magias no nível 5 passa a preparar 10 no 6. Recusar
isso impediria de subir de nível quem fez tudo certo. Então:

- **defeito** (opção proibida, repetida, escolha demais) → `422`, e nada é gravado;
- **pendência** (falta escolher, ou depende de outra escolha) → `200`, e sai na
  resposta junto do checklist.

Essa distinção não estava no motor; foi acrescentada por causa deste backend
(`tipo` em `Problema`, e `ehPendencia`).

**Ler nunca explode; escrever recusa.** Se a base mudar de um jeito que o motor não
consegue montar — um id que sumiu —, o `GET` devolve `200` com o personagem, `ficha:
null` e um `erro_de_ficha` dizendo o que houve e contra qual versão ele foi feito. O
jogador continua vendo quem ele é e pode corrigir a escolha. Já `POST` e `PATCH`
continuam recusando com `422`: ali quem propõe a mudança é o cliente, e proposta
inválida é erro dele.

**A versão do dataset fica gravada no personagem.** É o resumo do conteúdo de
`dados/` — muda quando o dado muda, e por nada mais. Serve de `ETag` do compêndio
(com `immutable`, então quem já tem a versão recebe `304` em vez das 391 magias de
novo) e de carimbo no personagem. Se a base mudar, a ficha continua sendo servida,
com um `aviso_de_versao` junto: **avisa, não quebra.**

## Erros

| status | quando |
|---|---|
| `400` | o pedido está malformado, ou tenta gravar o que não é estado |
| `404` | não existe |
| `405` | a rota existe, o método não |
| `413` | corpo acima de 1 MB |
| `422` | a sintaxe está certa e as **regras** é que não fecham — o motor recusou |
| `500` | o que não foi previsto |

O que nunca acontece é `200` com uma ficha inventada. É a regra do motor
("desconhecido é erro, nunca zero") na forma HTTP.

## Contas

E-mail e senha, próprios. Três rotas: `POST /contas` cadastra, `POST /sessoes` entra, e
`GET /eu` diz quem é o portador do token. Todas as rotas de `/personagens` exigem
`Authorization: Bearer <token>`.

Tudo com `node:crypto`, sem dependência nova:

- **Senha**: hash scrypt com sal por usuário, guardado como
  `scrypt$N$r$p$sal$hash` — os parâmetros vão junto, para que endurecê-los depois não
  invalide as senhas já gravadas. A comparação é `timingSafeEqual`.
- **Token**: assinado (HMAC-SHA256), **não** criptografado. Ele diz em claro quem é o
  usuário e até quando vale; o que a assinatura impede é forjar. Nada secreto entra nele.
- **Sem coleção de sessões.** O token é autossuficiente, o que também significa que
  não há como revogar um. Para o uso de hoje basta; quando precisar, o caminho é um
  `token_valido_a_partir_de` no usuário — uma linha, sem coleção nova.

Duas respostas são deliberadamente **iguais** onde seria natural diferenciá-las, e as
duas por não entregar informação a quem está tentando adivinhar:

| situação | resposta | por quê |
|---|---|---|
| e-mail não cadastrado × senha errada | o mesmo 401, com o mesmo corpo | diferenciar entrega quais e-mails existem |
| personagem de outra pessoa | **404**, não 403 | um 403 confirmaria que aquele id existe |

`SESSAO_SEGREDO` vazia não impede subir: o servidor gera um segredo por execução e
avisa no log. É seguro — 32 bytes de verdade —, mas as sessões morrem a cada reinício.

## Histórico

`GET /personagens/:id/historico` — do mais recente para o mais antigo, paginado por
`?limite=` e `?antes_de=` (o `proximo` que a página anterior devolveu).

Os eventos **não são gravados por cada rota**: eles são derivados da **diferença de
estado**, num lugar só (`aoMudarEstado`). A alternativa — cada caminho lembrar de
gravar o seu — é a que apodrece, porque basta um caminho novo esquecer a chamada para
o histórico ficar com buracos silenciosos. Aqui, se o estado mudou o evento existe, e
se não mudou não existe: um `PATCH` que reenvia o mesmo valor não gera linha nenhuma.

**Por que o evento guarda valor derivado, se o personagem nunca guarda.** O personagem
guarda construção e estado porque a ficha se recalcula. O evento é o oposto: ele é o
**passado**, e o passado não se recalcula. `recuperou 8 de vida · PV 20/38` tem de
continuar dizendo 38 depois de o personagem subir de nível — senão o histórico deixa
de ser o que aconteceu e vira o que aconteceria hoje. Há um teste só para isso.

O **texto**, esse, não é congelado: o evento guarda números, e `resumo()` os formata na
leitura. Melhorar uma frase melhora o histórico inteiro sem mexer em número nenhum.

`PATCH …/estado` aceita um `motivo` opcional (`{ magia_id }`) que **não é estado**: não
é gravado no personagem e não muda ficha nenhuma. Serve para a linha dizer "conjurou
Bola de Fogo com espaço de 3º · 1/2 restantes" em vez de "gastou um espaço de 3º". O
nome da magia é resolvido no compêndio e congelado junto do id — se a magia for
renomeada no dataset, como as quatro da fase 20, a linha antiga continua com o nome de
quando aconteceu.

Duas convenções que são do backend, não do livro, e por isso estão escritas:

- **Personagem sem `pontos_de_vida_atuais` está com a vida cheia.** Sem isso, o
  primeiro dano de toda campanha não teria "antes" e sumiria do histórico.
- **Recursos não têm denominador.** "gastou 1 de furia", sem `1/3`, porque a ficha
  ainda não expõe o máximo dos recursos. PV e espaços têm.

## Onde os personagens ficam

`Armazem` é uma interface com três implementações, e **quem escolhe é o
`principal.ts`, em um lugar só**: `MONGODB_URI` preenchida usa o Atlas, vazia usa
arquivo. É o que permite os testes rodarem sem banco e o servidor subir sem o Atlas
no ar.

| implementação | quando | onde |
|---|---|---|
| `ArmazemMongo` / `UsuariosMongo` | `MONGODB_URI` preenchida | `src/mongo.ts` |
| `ArmazemEmArquivos` / `UsuariosEmArquivos` | sem URI — um JSON por registro, escrita atômica | `src/armazem.ts`, `src/usuarios.ts` |
| `ArmazemNaMemoria` / `UsuariosNaMemoria` | testes: nada em disco, nada compartilhado | idem |

Personagens e usuários dividem **uma** conexão (`conectarMongo`): são coleções do
mesmo banco, e dois clientes seriam dois pools para nada.

**Todo personagem tem dono.** `listar` exige o `usuario_id` — não existe listar sem
dono, porque listar sem dono é listar os de todo mundo. No Mongo isso bate exatamente
com o índice `{ usuario_id: 1, ultimo_acesso: -1 }`. A coleção `usuarios` tem índice
**único** em `email`: a checagem em código não basta, porque dois cadastros
simultâneos passam os dois por ela antes de qualquer um gravar.

O driver só é carregado quando há URI: o `import` do Mongo é dinâmico.

**Os métodos devolvem `Promise`.** A primeira versão era síncrona, porque arquivo e
memória são síncronos — mas Mongo não é, e fingir que é significaria bloquear o laço
de eventos ou mentir no tipo. O roteador já aceitava manipulador assíncrono, então o
custo foi um `await` por chamada e nenhuma mudança de desenho.

**O documento guarda construção e estado, nunca a ficha.** É a decisão que faz o
dataset valer a pena: corrigir uma regra em `dados/` corrige todos os personagens de
uma vez, porque a ficha se recalcula a cada leitura. As 89 paráfrases de magia
corrigidas na fase 20 não exigiram migração nenhuma, e é por isso.

### O id

O Mongo usa `ObjectId`; o resto do backend usa `id` string, porque ele vem da URL. A
tradução mora em `mongo.ts` e em nenhum outro lugar. **Id malformado é ausência (404),
nunca erro do driver (500)** — a checagem acontece antes de consultar, e um teste com
uma coleção-armadilha prova isso sem precisar de banco.

### Rodar os testes contra um Mongo de verdade

Quatro testes precisam de banco e **pulam** quando não há um, em vez de fingir que
passaram:

```bash
MONGODB_URI_TESTE='mongodb+srv://…' npm run teste
```

A suíte cria bancos com nome aleatório e os derruba no fim — não toca em dado de
verdade nem depende de o banco estar limpo.

## Desempenho

A ficha sai em ~2 ms e o catálogo de magias em ~12 ms. A ficha custava 49 ms antes de
`dataset.ts` memorizar a leitura de `dados/` — quase tudo era reler e reparsear
`magias.json` a cada pedido. O dado é imutável em execução, então memorizar não fere a
pureza do motor; `ouro.test.ts` monta cada golden duas vezes e compara, que é o teste
que pegaria alguém mutando uma entidade do dataset.

O catálogo grande ainda é serializado a cada pedido novo. Com `ETag` + `immutable`
isso acontece uma vez por cliente por versão, o que basta; se um dia não bastar,
guardar o texto já serializado é uma linha.
