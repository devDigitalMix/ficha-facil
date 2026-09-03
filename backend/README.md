# Backend

Guarda personagens, serve o compêndio e chama o motor. **Zero dependências**, como o
motor: `node:http`, `node:fs`, e o TypeScript rodando direto com os tipos apagados.

```bash
cd backend
npm run teste     # 40 testes
npm run servir    # http://localhost:8787
```

`PORTA` e `PERSONAGENS` (o diretório onde os personagens ficam) saem do ambiente.

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

## Onde os personagens ficam

Um JSON por personagem, num diretório. Não é banco porque ainda não precisa ser: o
compêndio é estático e o personagem é um documento pequeno que se lê inteiro. A
escrita é atômica (temporário + `rename`), então um processo morto no meio de uma
gravação deixa o personagem anterior intacto em vez de meio arquivo.

`Armazem` é uma interface — trocar por banco é trocar essa peça, não reescrever o
backend. `ArmazemNaMemoria` existe para os testes: nada em disco, nada compartilhado
entre eles.

## Desempenho

A ficha sai em ~2 ms e o catálogo de magias em ~12 ms. A ficha custava 49 ms antes de
`dataset.ts` memorizar a leitura de `dados/` — quase tudo era reler e reparsear
`magias.json` a cada pedido. O dado é imutável em execução, então memorizar não fere a
pureza do motor; `ouro.test.ts` monta cada golden duas vezes e compara, que é o teste
que pegaria alguém mutando uma entidade do dataset.

O catálogo grande ainda é serializado a cada pedido novo. Com `ETag` + `immutable`
isso acontece uma vez por cliente por versão, o que basta; se um dia não bastar,
guardar o texto já serializado é uma linha.
