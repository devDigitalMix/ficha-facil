// A rota de descanso.
//
// O ponto desta rota é o cliente NÃO precisar saber o que um descanso faz. Ele diz
// "descansei, do tipo tal"; quem responde quais espaços voltam, quais recursos
// voltam e quantos Pontos de Vida voltam é o motor, lendo o dataset. Se algum dia
// um teste daqui precisar citar o nome de uma classe, a regra vazou para o backend.

import { test, after } from 'node:test'
import assert from 'node:assert/strict'
import { subir, ouro } from './ajuda.ts'

const c = await subir()
after(() => c.fechar())

const clerigo = ouro('clerigo-5')
const criar = async (nome = 'Ysolde') =>
  (await c.pedir('POST', '/personagens', { nome, construcao: clerigo.construcao })).corpo

test('o Descanso Longo devolve os Pontos de Vida e os espaços gastos', async () => {
  const p = await criar()
  const maximo = p.ficha.pontos_de_vida_maximos.valor
  await c.pedir('PATCH', `/personagens/${p.id}/estado`, {
    pontos_de_vida_atuais: 4,
    espacos_gastos: { '1': 3, '2': 2 },
  })

  const r = await c.pedir('POST', `/personagens/${p.id}/descanso`, { tipo: 'descanso_longo' })
  assert.equal(r.status, 200)
  assert.equal(r.corpo.estado.pontos_de_vida_atuais, maximo)
  assert.deepEqual(r.corpo.estado.espacos_gastos, { '1': 0, '2': 0 })
  assert.ok(
    r.corpo.descanso.o_que_voltou.length >= 2,
    'a resposta diz o que voltou, para o app não ter de comparar dois estados',
  )
})

test('o Descanso Curto não devolve os espaços de quem não os recupera nele', async () => {
  const p = await criar()
  await c.pedir('PATCH', `/personagens/${p.id}/estado`, { espacos_gastos: { '1': 3 } })
  const r = await c.pedir('POST', `/personagens/${p.id}/descanso`, { tipo: 'descanso_curto' })
  assert.equal(r.status, 200)
  assert.deepEqual(r.corpo.estado.espacos_gastos, { '1': 3 })
})

test('descansar entra no histórico como qualquer outra mudança de estado', async () => {
  const p = await criar()
  await c.pedir('PATCH', `/personagens/${p.id}/estado`, { pontos_de_vida_atuais: 4 })
  await c.pedir('POST', `/personagens/${p.id}/descanso`, { tipo: 'descanso_longo' })
  const h = await c.pedir('GET', `/personagens/${p.id}/historico`)
  assert.ok(h.corpo.itens.length >= 2, 'o dano e a cura do descanso são dois eventos')
})

test('descanso sem tipo é 400, e a resposta diz quais existem', async () => {
  const p = await criar()
  const r = await c.pedir('POST', `/personagens/${p.id}/descanso`, {})
  assert.equal(r.status, 400)
  assert.ok(r.corpo.detalhe.aceitos.includes('descanso_longo'))
})

test('descanso que o livro não tem é recusado, e não vira um descanso vazio', async () => {
  const p = await criar()
  const r = await c.pedir('POST', `/personagens/${p.id}/descanso`, { tipo: 'cochilo' })
  assert.equal(r.status, 422, 'id inexistente é construção inválida, não erro interno')
})

test('só o dono descansa o próprio personagem', async () => {
  const p = await criar()
  const outro = await c.outroUsuario('intruso@exemplo.test')
  const r = await c.pedir('POST', `/personagens/${p.id}/descanso`, { tipo: 'descanso_longo' },
    { authorization: `Bearer ${outro.token}` })
  assert.equal(r.status, 404)
})
