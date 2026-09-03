// O armazém no Mongo.
//
// Divide-se em duas partes de propósito:
//
// 1. **O que não precisa de banco** — a tradução entre o `_id` do Mongo e o `id` que o
//    resto do backend usa, e a recusa de id que não é ObjectId. É onde mora a lógica,
//    e é o defeito que mais custa caro: um id vindo da URL que faz o driver lançar
//    transforma "personagem inexistente" (404) em "erro interno" (500). Foi exatamente
//    esse defeito que a fase 19 consertou no `porId` do motor.
//
// 2. **O que só um Mongo de verdade prova** — gravar, ler de volta, ordenar, apagar.
//    Roda contra o banco apontado por `MONGODB_URI_TESTE`; sem ela, os testes pulam em
//    vez de fingir que passaram. Para rodar:
//
//        MONGODB_URI_TESTE='mongodb+srv://…' npm run teste
//
//    A suíte usa um banco com nome aleatório e o DERRUBA no fim, para nunca tocar em
//    dado de verdade nem depender de o banco estar limpo.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { ObjectId } from 'mongodb'
import { ArmazemMongo, ehObjectId, paraFora, type Documento } from '../src/mongo.ts'
import type { Personagem } from '../src/personagem.ts'

const DONO = 'dono-de-teste'

const modelo = (nome: string, ultimo_acesso = new Date().toISOString(), usuario_id = DONO) =>
  ({
    usuario_id,
    nome,
    status: 'ativo',
    construcao: {
      especie: 'humano',
      antecedente: 'acolito',
      niveis: [{ classe: 'clerigo', nivel: 1 }],
      atributos_base: { FOR: 10, DES: 10, CON: 10, INT: 10, SAB: 10, CAR: 10 },
    },
    estado: {},
    versao_do_dataset: 'aaaaaaaaaaaa',
    criado_em: new Date().toISOString(),
    ultimo_acesso,
  }) as Omit<Personagem, 'id'>

// --------------------------------------------------------- sem banco nenhum

test('id que não é ObjectId é recusado, e não vira exceção do driver', () => {
  for (const id of ['', '../fuga', 'segredo', '/etc/passwd', 'com espaço', 'z'.repeat(24)]) {
    assert.equal(ehObjectId(id), false, `'${id}' não pode passar por ObjectId`)
  }
  assert.equal(ehObjectId(new ObjectId().toHexString()), true)
})

test('só passa id que volta idêntico — a ida-e-volta é a checagem', () => {
  // Escrevi este teste primeiro afirmando que `ObjectId.isValid('personagem12')` era
  // `true`, porque foi assim em versões antigas do driver: 12 caracteres eram lidos
  // como bytes crus, e o id de volta saía com outros 24 dígitos. No driver 7 isso
  // mudou e só hex de 24 passa. O teste estava errado, não o código.
  //
  // A lição é a de sempre neste projeto: não afirmar de memória o que dá para
  // conferir. Então o que se testa aqui é a PROPRIEDADE que o armazém garante —
  // id que entra é id que volta —, e não o comportamento interno do driver, que
  // pode mudar de novo na próxima versão.
  const id = new ObjectId().toHexString()
  assert.equal(ehObjectId(id), true)
  assert.equal(new ObjectId(id).toHexString(), id, 'ida-e-volta preserva o id')

  // E o que a ida-e-volta protege: qualquer coisa que o `isValid` viesse a aceitar
  // mas que não voltasse igual seria recusada aqui, mesmo sem esta suíte saber
  // qual seria essa coisa.
  assert.equal(ehObjectId(id.toUpperCase()), false, 'maiúsculas voltam diferentes')
})

test('paraFora troca _id por id e não deixa _id vazar', () => {
  const _id = new ObjectId()
  const doc = { ...modelo('Vesna'), _id } as Documento
  const p = paraFora(doc)
  assert.equal(p.id, _id.toHexString())
  assert.equal((p as Record<string, unknown>)._id, undefined, '_id não pode sair do armazém')
  assert.equal(p.nome, 'Vesna')
  assert.equal(p.construcao.niveis[0].classe, 'clerigo')
})

/**
 * A checagem do id tem de acontecer ANTES de falar com o banco.
 *
 * Este teste nasceu de um teste de mutação: tirar o `if (!ehObjectId(id))` de `ler` e
 * `apagar` não reprovava nada, porque o único teste que pegaria isso estava atrás do
 * `MONGODB_URI_TESTE` e pulava. Um teste que só roda na máquina de quem configurou o
 * banco não protege o dia a dia.
 *
 * A armadilha abaixo é uma coleção que explode se alguém a tocar. Se a checagem sair,
 * a explosão vira 500 — que é exatamente o defeito que se quer impedir.
 */
function armazemComArmadilha(): ArmazemMongo {
  const armadilha = new Proxy({}, {
    get: (_, prop) => () => {
      throw new Error(`o armazém chamou '${String(prop)}' com um id que nem devia ter consultado`)
    },
  })
  const cliente = { db: () => ({ collection: () => armadilha }) }
  return new ArmazemMongo(cliente as never, 'nao_existe')
}

test('id malformado nem chega a consultar o banco', async () => {
  const a = armazemComArmadilha()
  for (const id of ['', '../fuga', 'segredo', 'com espaço']) {
    assert.equal(await a.ler(id), undefined, `ler('${id}') tinha de parar antes do driver`)
    assert.equal(await a.apagar(id), false, `apagar('${id}') tinha de parar antes do driver`)
  }
})

test('id válido, esse sim, vai ao banco', async () => {
  // O par do teste acima: sem ele, "nunca consultar" passaria como conserto.
  const a = armazemComArmadilha()
  await assert.rejects(() => a.ler(new ObjectId().toHexString()), /nem devia ter consultado/)
})

// ------------------------------------------------------- contra um Mongo real

const URI = process.env.MONGODB_URI_TESTE
const bancoDeTeste = `ficha_facil_teste_${Math.random().toString(36).slice(2, 10)}`
const seTemBanco = { skip: URI ? false : 'defina MONGODB_URI_TESTE para rodar contra um Mongo' }

test('grava, lê de volta, lista e apaga', seTemBanco, async () => {
  const a = await ArmazemMongo.conectar(URI!, bancoDeTeste)
  try {
    const p = await a.criar(modelo('Vesna'))
    assert.ok(ehObjectId(p.id), 'o id devolvido tem de servir de volta na URL')

    const lido = (await a.ler(p.id))!
    assert.equal(lido.nome, 'Vesna')
    assert.equal(lido.construcao.niveis[0].classe, 'clerigo')

    await a.gravar({ ...lido, nome: 'Vesna, a Alta' })
    assert.equal((await a.ler(p.id))!.nome, 'Vesna, a Alta', 'gravar substitui, não duplica')
    assert.equal((await a.listar(DONO)).length, 1, 'e continua sendo um só')

    assert.equal(await a.apagar(p.id), true)
    assert.equal(await a.apagar(p.id), false, 'apagar duas vezes não mente na segunda')
    assert.equal(await a.ler(p.id), undefined)
  } finally {
    await a.banco.dropDatabase()
    await a.fechar()
  }
})

test('lista pelo último acesso, do mais recente para o mais antigo', seTemBanco, async () => {
  const a = await ArmazemMongo.conectar(URI!, `${bancoDeTeste}_ordem`)
  try {
    const antiga = await a.criar(modelo('Antiga', '2020-01-01T00:00:00.000Z'))
    const nova = await a.criar(modelo('Nova', '2026-01-01T00:00:00.000Z'))
    await a.criar(modelo('De outra pessoa', '2027-01-01T00:00:00.000Z', 'outro-dono'))
    assert.deepEqual((await a.listar(DONO)).map((p) => p.id), [nova.id, antiga.id],
      'o mais recente é de outro dono e não pode aparecer')
  } finally {
    await a.banco.dropDatabase()
    await a.fechar()
  }
})

test('id inexistente ou malformado é ausência, nunca erro', seTemBanco, async () => {
  const a = await ArmazemMongo.conectar(URI!, `${bancoDeTeste}_ausencia`)
  try {
    assert.equal(await a.ler(new ObjectId().toHexString()), undefined, 'válido mas não existe')
    assert.equal(await a.ler('../fuga'), undefined, 'nem chega a consultar')
    assert.equal(await a.apagar('../fuga'), false)
  } finally {
    await a.banco.dropDatabase()
    await a.fechar()
  }
})

test('o índice de "Meus personagens" é criado na conexão', seTemBanco, async () => {
  const a = await ArmazemMongo.conectar(URI!, `${bancoDeTeste}_indice`)
  try {
    const indices = await a.personagens.indexes()
    const achado = indices.find((i) => i.key.usuario_id === 1 && i.key.ultimo_acesso === -1)
    assert.ok(achado, 'sem ele, listar personagens do dono vira varredura da coleção')
  } finally {
    await a.banco.dropDatabase()
    await a.fechar()
  }
})
