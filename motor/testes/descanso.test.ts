// Descanso curto e longo.
//
// A regra do livro está no dataset; o que se testa aqui é que o motor a LÊ, e que
// não inventou nenhuma por conta própria. As duas armadilhas do 2024, ambas
// diferentes do 2014, estão cobertas: o Descanso Longo devolve TODOS os Dados de
// Vida (não metade), e os Pontos de Vida Temporários atravessam o Curto.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { montar, descansar, tiposDeDescanso } from '../src/motor.ts'

const OURO = join(dirname(fileURLToPath(import.meta.url)), '..', 'ouro')
const ouro = (n: string) => JSON.parse(readFileSync(join(OURO, n), 'utf8')).construcao

function montado(arquivo: string) {
  const r = montar(ouro(arquivo))
  return {
    ctx: r.contexto,
    ficha: {
      pontos_de_vida_maximos: r.ficha!.pontos_de_vida_maximos.valor,
      recursos: r.ficha!.recursos,
    },
  }
}

test('o Descanso Longo devolve todos os Pontos de Vida', () => {
  const { ctx, ficha } = montado('barbaro-5.json')
  const r = descansar('descanso_longo', ctx, ficha, { pontos_de_vida_atuais: 3 })
  assert.equal(r.pontos_de_vida_atuais, ficha.pontos_de_vida_maximos)
})

test('o Descanso Curto não devolve Ponto de Vida nenhum sozinho', () => {
  // Quem cura no Curto é o Dado de Vida que o jogador decide gastar — decisão de
  // jogador não é efeito automático de descanso (p. 365).
  const { ctx, ficha } = montado('barbaro-5.json')
  const r = descansar('descanso_curto', ctx, ficha, { pontos_de_vida_atuais: 3 })
  assert.equal(r.pontos_de_vida_atuais, undefined)
})

test('os Pontos de Vida Temporários atravessam o Curto e caem no Longo', () => {
  const { ctx, ficha } = montado('barbaro-5.json')
  const estado = { pontos_de_vida_temporarios: 7 }
  assert.equal(descansar('descanso_curto', ctx, ficha, estado).pontos_de_vida_temporarios, undefined)
  assert.equal(descansar('descanso_longo', ctx, ficha, estado).pontos_de_vida_temporarios, 0)
})

test('o recurso volta no descanso que ELE declara, e só nele', () => {
  const { ctx, ficha } = montado('barbaro-5.json')
  const furias = ficha.recursos.find((r) => r.recarga.some((x) => x.gatilho === 'descanso_curto'))
  assert.ok(furias, 'o Bárbaro tem Fúrias, que recuperam 1 no Curto e todas no Longo')

  // No Curto volta a quantidade declarada (1), não tudo.
  const curto = descansar('descanso_curto', ctx, ficha, { recursos_gastos: { [furias!.id]: 3 } })
  assert.equal(curto.recursos_gastos?.[furias!.id], 2)

  const longo = descansar('descanso_longo', ctx, ficha, { recursos_gastos: { [furias!.id]: 3 } })
  assert.equal(longo.recursos_gastos?.[furias!.id], 0)
})

test('os espaços de magia voltam no descanso que a classe declara', () => {
  const { ctx, ficha } = montado('clerigo-5.json')
  const gastos = { '1': 2, '2': 1 }
  const longo = descansar('descanso_longo', ctx, ficha, { espacos_gastos: gastos })
  assert.deepEqual(longo.espacos_gastos, { '1': 0, '2': 0 })
  // A Clériga não é Bruxa: no Curto os espaços dela não voltam.
  const curto = descansar('descanso_curto', ctx, ficha, { espacos_gastos: gastos })
  assert.equal(curto.espacos_gastos, undefined)
})

test('descansar não mexe no que já está cheio', () => {
  const { ctx, ficha } = montado('barbaro-5.json')
  const r = descansar('descanso_longo', ctx, ficha, {})
  assert.equal(r.pontos_de_vida_atuais, undefined)
  assert.equal(r.recursos_gastos, undefined)
  assert.deepEqual(r.o_que_voltou, [], 'sem nada gasto, não há o que registrar no histórico')
})

test('descanso que não existe é erro, não um descanso que não faz nada', () => {
  const { ctx, ficha } = montado('barbaro-5.json')
  assert.throws(() => descansar('descanso_medio', ctx, ficha, {}))
})

test('os dois descansos do livro declaram o que recuperam', () => {
  const tipos = tiposDeDescanso()
  assert.equal(tipos.length, 2)
  for (const t of tipos) {
    assert.ok(t.recupera, `'${t.id}' sem 'recupera': o motor não teria de onde tirar a regra`)
  }
  const longo = tipos.find((t) => t.id === 'descanso_longo')!
  assert.equal(
    longo.recupera!.dados_de_vida,
    'todos',
    'em 2024 o Descanso Longo devolve TODOS os Dados de Vida, não metade (p. 366)',
  )
})

test('o que o descanso recupera e o motor não aplica sai DECLARADO, não em silêncio', () => {
  // A fase 21 inteira foi sobre efeito descartado sem uma palavra. `recupera` do
  // Longo declara quatro coisas que não são estado que o app guarde — Dados de
  // Vida, Exaustão e as duas reduções. Elas não podem simplesmente não acontecer.
  const { ctx, ficha } = montado('barbaro-5.json')
  const longo = descansar('descanso_longo', ctx, ficha, {})
  assert.ok(
    longo.nao_aplicado.includes('dados_de_vida'),
    'o livro devolve todos os Dados de Vida (p. 366) e o motor ainda não os guarda',
  )
  assert.ok(longo.nao_aplicado.includes('exaustao'))

  // O Curto declara "nenhum"/"mantem": isso É aplicar — não mexer é o que ele faz.
  assert.deepEqual(descansar('descanso_curto', ctx, ficha, {}).nao_aplicado, [])
})
