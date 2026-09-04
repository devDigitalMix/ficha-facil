// Conjurar: o cliente diz qual magia, o motor diz o que custa.
//
// As duas queixas que criaram esta rota: "tem magias que posso usar uma vez por dia
// mas não gastam [espaço]" e "clico em usar num truque e não fala nada". As duas
// vinham do mesmo lugar — o app decidia o custo, e só sabia um jeito de pagar.
//
// Se algum teste daqui precisar citar o nome de uma classe ou de um talento para
// saber quanto custa, a regra vazou do motor para o backend.

import { test, after } from 'node:test'
import assert from 'node:assert/strict'
import { subir } from './ajuda.ts'

const c = await subir()
after(() => c.fechar())

/** Clériga de nível 1 com Iniciado em Magia pelo traço Versátil do Humano. */
const construcao = {
  especie: 'humano',
  antecedente: 'acolito',
  niveis: [{ classe: 'clerigo', nivel: 1 }],
  atributos_base: { FOR: 10, DES: 14, CON: 12, INT: 12, SAB: 15, CAR: 13 },
  escolhas: {
    humano_versatil: 'iniciado_em_magia',
    'iniciado_em_magia_lista@humano_versatil': 'mago',
    'iniciado_em_magia_atributo@humano_versatil': 'INT',
    'iniciado_em_magia_truques@humano_versatil': ['luz', 'raio_de_gelo'],
    'iniciado_em_magia_magia_1@humano_versatil': 'misseis_magicos',
  },
}

const criar = async (nome = 'Ysolde') =>
  (await c.pedir('POST', '/personagens', { nome, construcao })).corpo

test('truque não gasta nada E aparece no histórico', async () => {
  const p = await criar()
  const antes = JSON.stringify(p.estado)

  const r = await c.pedir('POST', `/personagens/${p.id}/conjurar`, { magia_id: 'luz' })
  assert.equal(r.status, 200)
  assert.equal(r.corpo.conjurou.custo.tipo, 'nenhum')
  assert.equal(JSON.stringify((await c.armazem.ler(p.id))!.estado), antes, 'nada mudou de estado')

  const h = await c.pedir('GET', `/personagens/${p.id}/historico`)
  const linha = h.corpo.itens[0]
  assert.equal(linha.tipo, 'magia_conjurada')
  assert.match(linha.resumo, /Luz/, 'a linha diz o que foi conjurado')
})

test('a magia que o talento dá de graça gasta o USO, e não um espaço', async () => {
  const p = await criar('Nael')
  const r = await c.pedir('POST', `/personagens/${p.id}/conjurar`, { magia_id: 'misseis_magicos' })
  assert.equal(r.status, 200)
  assert.equal(r.corpo.conjurou.custo.tipo, 'recurso')

  const guardado = (await c.armazem.ler(p.id))!
  assert.deepEqual(guardado.estado.espacos_gastos, undefined, 'nenhum espaço foi gasto')
  const recurso = r.corpo.conjurou.custo.recurso_id
  assert.equal(guardado.estado.recursos_gastos?.[recurso], 1)

  // O segundo uso é recusado — e a recusa diz que dá para gastar espaço.
  const de_novo = await c.pedir('POST', `/personagens/${p.id}/conjurar`, { magia_id: 'misseis_magicos' })
  assert.equal(de_novo.status, 400)
  assert.equal(de_novo.corpo.detalhe.pode_com_espaco, true)

  // …e gastando espaço, funciona.
  const comEspaco = await c.pedir('POST', `/personagens/${p.id}/conjurar`,
    { magia_id: 'misseis_magicos', com_espaco: true })
  assert.equal(comEspaco.status, 200)
  assert.equal((await c.armazem.ler(p.id))!.estado.espacos_gastos!['1'], 1)
})

test('magia comum gasta um espaço, e o histórico diz quantos sobraram', async () => {
  let p = await criar('Vesna')
  // Recém-criada, ela ainda não preparou nada: preparar é escolha, e escolha se
  // responde. Pega as duas primeiras que o próprio checklist oferece.
  const escolha = p.checklist.find((x: { escolha_id: string }) => x.escolha_id === 'clerigo_preparadas')
  assert.ok(escolha, 'a Clériga tem magias a preparar')
  p = (await c.pedir('POST', `/personagens/${p.id}/escolhas`, {
    escolhas: {
      clerigo_preparadas: escolha.opcoes.slice(0, escolha.quantidade)
        .map((o: { id: string }) => o.id),
    },
  })).corpo

  const preparada = p.ficha.magias.find(
    (m: { circulo: number; pronta_para_conjurar: boolean; custo: { tipo: string } }) =>
      m.circulo === 1 && m.pronta_para_conjurar && m.custo.tipo === 'espaco',
  )
  assert.ok(preparada, 'a Clériga tem magia de 1º círculo preparada')

  const r = await c.pedir('POST', `/personagens/${p.id}/conjurar`, { magia_id: preparada.id })
  assert.equal(r.status, 200)
  assert.equal((await c.armazem.ler(p.id))!.estado.espacos_gastos!['1'], 1)

  const h = await c.pedir('GET', `/personagens/${p.id}/historico`)
  assert.match(h.corpo.itens[0].resumo, /restantes/)
})

test('não dá para conjurar o que não está na ficha, nem o que não está preparado', async () => {
  const p = await criar('Erro')
  const inexistente = await c.pedir('POST', `/personagens/${p.id}/conjurar`, { magia_id: 'bola_de_fogo' })
  assert.equal(inexistente.status, 404)

  const naoPreparada = p.ficha.magias.find(
    (m: { pronta_para_conjurar: boolean }) => !m.pronta_para_conjurar,
  )
  if (naoPreparada) {
    const r = await c.pedir('POST', `/personagens/${p.id}/conjurar`, { magia_id: naoPreparada.id })
    assert.equal(r.status, 400)
  }
})

test('o descanso deixa linha no histórico', async () => {
  const p = await criar('Cansada')
  await c.pedir('POST', `/personagens/${p.id}/conjurar`, { magia_id: 'misseis_magicos' })
  await c.pedir('POST', `/personagens/${p.id}/descanso`, { tipo: 'descanso_longo' })

  const h = await c.pedir('GET', `/personagens/${p.id}/historico`)
  const descanso = h.corpo.itens.find((e: { tipo: string }) => e.tipo === 'descanso')
  assert.ok(descanso, 'descansar sem deixar rastro é o jogador não saber por que voltou')
  assert.match(descanso.resumo, /Descanso Longo/)
})
