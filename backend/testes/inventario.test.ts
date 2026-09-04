// O inventário: o que se carrega e o que está na mão.
//
// Os dois são ESTADO, e não construção: pegar uma corda e sacar o escudo acontecem
// na mesa e não mudam quem o personagem é. O que o backend confere aqui é coerência
// — equipar o que não se carrega é estado impossível, não jogada de regra. O que a
// armadura faz com a CA continua sendo do motor.

import { test, after } from 'node:test'
import assert from 'node:assert/strict'
import { subir, ouro } from './ajuda.ts'

const c = await subir()
after(() => c.fechar())

const clerigo = ouro('clerigo-5')
const criar = async (nome = 'Ysolde') =>
  (await c.pedir('POST', '/personagens', { nome, construcao: clerigo.construcao })).corpo

const patch = (id: string, corpo: unknown) => c.pedir('PATCH', `/personagens/${id}/estado`, corpo)

/**
 * O app manda o inventário INTEIRO a cada mudança, como faz com os espaços gastos.
 * Estes ajudantes escrevem isso sem repetir o merge em todo teste — e o personagem
 * de ouro já nasce com o equipamento da criação, que não pode ser apagado sem querer.
 */
const comItem = (p: { estado: { inventario?: Record<string, number> } }, id: string, n: number) =>
  ({ inventario: { ...(p.estado.inventario ?? {}), [id]: n } })
const equipando = (p: { estado: { equipado?: string[] } }, ...ids: string[]) =>
  ({ equipado: [...new Set([...(p.estado.equipado ?? []), ...ids])] })

test('pegar um item entra no inventário e no histórico, com o nome', async () => {
  const p = await criar()
  const r = await patch(p.id, {
    inventario: { ...(p.estado.inventario ?? {}), corda: 1, tocha: 5 },
  })
  assert.equal(r.status, 200)
  assert.equal(r.corpo.estado.inventario.corda, 1)
  assert.equal(r.corpo.estado.inventario.tocha, 5)

  const h = await c.pedir('GET', `/personagens/${p.id}/historico`)
  const linhas = h.corpo.itens.map((e: { resumo: string }) => e.resumo)
  assert.ok(linhas.some((l: string) => /Tocha/.test(l)), `histórico sem o nome do item: ${linhas}`)
})

test('equipar mexe na ficha — a CA muda porque o motor recalcula', async () => {
  const p = await criar()

  const semEscudo = await patch(p.id, {
    equipado: (p.estado.equipado ?? []).filter((x: string) => x !== 'escudo'),
  })
  const base = semEscudo.corpo.ficha.classe_de_armadura.valor
  const comEscudo = await patch(p.id, comItem(semEscudo.corpo, 'escudo', 1))
  const r = await patch(p.id, equipando(comEscudo.corpo, 'escudo'))
  assert.equal(r.status, 200)
  assert.equal(
    r.corpo.ficha.classe_de_armadura.valor,
    base + 2,
    'o escudo soma 2 na CA — e quem soma é o motor, não esta rota',
  )
  assert.ok(
    r.corpo.ficha.classe_de_armadura.parcelas.some((x: { rotulo: string }) => /escudo/i.test(x.rotulo)),
    'a proveniência da CA diz que o escudo entrou',
  )

  // …e desequipar volta.
  const voltou = await patch(p.id, {
    equipado: r.corpo.estado.equipado.filter((x: string) => x !== 'escudo'),
  })
  assert.equal(voltou.corpo.ficha.classe_de_armadura.valor, base)
})

test('não dá para equipar o que não está no inventário', async () => {
  const p = await criar()
  const antes = (await c.armazem.ler(p.id))!.estado.equipado
  const r = await patch(p.id, equipando(p, 'espada_longa'))
  assert.equal(r.status, 400)
  assert.deepEqual(r.corpo.detalhe.fora_do_inventario, ['espada_longa'])
  assert.deepEqual((await c.armazem.ler(p.id))!.estado.equipado, antes, 'nada foi gravado')
})

test('item que não existe no compêndio é recusado', async () => {
  const p = await criar()
  const r = await patch(p.id, { inventario: { espada_de_plasma: 1 } })
  assert.equal(r.status, 404)
})

test('quantidade zero é não ter: o item sai do inventário', async () => {
  const p = await criar()
  const com = await patch(p.id, comItem(p, 'tocha', 2))
  const r = await patch(p.id, comItem(com.corpo, 'tocha', 0))
  assert.equal(r.status, 200)
  assert.ok(!('tocha' in r.corpo.estado.inventario), 'zero não fica como linha morta')
})

test('largar o que está equipado é recusado antes de virar estado impossível', async () => {
  const p = await criar()
  const com = await patch(p.id, comItem(p, 'escudo', 1))
  const eq = await patch(p.id, equipando(com.corpo, 'escudo'))
  const r = await patch(p.id, comItem(eq.corpo, 'escudo', 0))
  assert.equal(r.status, 400, 'não dá para largar o escudo continuando com ele no braço')
})

test('a arma equipada aparece nos ataques, com o dano dela', async () => {
  const p = await criar()
  const com = await patch(p.id, comItem(p, 'maca', 1))
  const r = await patch(p.id, equipando(com.corpo, 'maca'))
  const ataque = r.corpo.ficha.ataques.find((a: { arma: string }) => a.arma === 'maca')
  assert.ok(ataque, 'equipou a maça e ela não virou ataque')
  assert.ok(ataque.dano.dados.length, 'o ataque tem de trazer o dado de dano')
})
