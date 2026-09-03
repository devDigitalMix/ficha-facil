// Pontos de Vida máximos: de onde eles vêm, e por que a parcela vazia sumiu.
//
// Estes testes existem por causa de dois defeitos que conviveram muito tempo sem
// se denunciar, porque nenhum dos dois fazia a conta ESTOURAR — os dois faziam a
// conta dar um número plausível e errado:
//
//   1. `bonus_de_caracteristicas` entrava fixo em 0. A fórmula do livro era
//      respeitada à risca, com uma parcela sempre vazia; a Tenacidade Anã ia para
//      o lixo em silêncio, e o Anão tinha a vida de um humano.
//   2. modificador cujo valor é FÓRMULA (e o da Tenacidade Anã é: 'nivel_do_
//      personagem') virava `Number(...)` → NaN → descartado. Não era um problema
//      dos Pontos de Vida: eram 31 modificadores no dataset inteiro, calados.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { montar } from '../src/motor.ts'
import type { Construcao } from '../src/colecao.ts'

const OURO = join(dirname(fileURLToPath(import.meta.url)), '..', 'ouro')

/** O Bárbaro de ouro, com a espécie trocada — o resto do personagem é o mesmo. */
function comEspecie(especie: string): Construcao {
  const g = JSON.parse(readFileSync(join(OURO, 'barbaro-5.json'), 'utf8'))
  return { ...g.construcao, especie }
}

const pv = (especie: string) => montar(comEspecie(especie)).ficha!.pontos_de_vida_maximos

test('a Tenacidade Anã soma 1 Ponto de Vida por nível — e some com a espécie', () => {
  const anao = pv('anao')
  const humano = pv('humano')
  assert.equal(
    anao.valor - humano.valor,
    5,
    'o personagem é de nível 5: a Tenacidade Anã vale +5, não +0 nem +1',
  )
})

test('a parcela dos bônus de característica diz o valor, não um zero decorativo', () => {
  const rotulos = pv('anao').parcelas.map((p) => p.rotulo)
  const bonus = pv('anao').parcelas.find((p) => p.rotulo === 'bônus de características')
  assert.ok(bonus, `esperava a parcela dos bônus; vieram: ${rotulos.join(', ')}`)
  assert.equal(bonus!.valor, 5)
})

test('a proveniência dos Pontos de Vida é legível: o rótulo vem do dataset', () => {
  // Sem isto a ficha mostrava "38 = 10 (pontos_de_vida_no_nivel_1) + …", que é o
  // identificador da chave, não uma frase. O catálogo já declarava o rótulo bom.
  for (const p of pv('humano').parcelas) {
    assert.ok(
      !/^[a-z0-9]+(_[a-z0-9]+)+$/.test(p.rotulo),
      `parcela com identificador cru em vez de rótulo: '${p.rotulo}'`,
    )
  }
})

test('parcela zerada e condicional não aparece; a que é "sempre" aparece', () => {
  const parcelas = pv('humano').parcelas
  const rotulos = parcelas.map((p) => p.rotulo)
  assert.ok(
    rotulos.includes('Pontos de Vida do nível 1'),
    'a parcela do nível 1 é `sempre`: some nunca',
  )
  assert.ok(
    !rotulos.includes('reduções do máximo'),
    'sem dreno nenhum, "+ 0 (reduções do máximo)" é ruído na ficha',
  )
  assert.ok(
    !rotulos.includes('bônus de características'),
    'o humano do golden não tem característica que aumente o máximo',
  )
})

test('as parcelas somam o valor, sempre', () => {
  for (const especie of ['anao', 'humano']) {
    const r = pv(especie)
    const soma = r.parcelas.reduce((s, p) => s + (typeof p.valor === 'number' ? p.valor : 0), 0)
    assert.equal(soma, r.valor, `${especie}: as parcelas têm de explicar o número inteiro`)
  }
})

// ------------------------------------------------ e a mesma exigência para o resto

/**
 * Proveniência que não fecha com o próprio número é pior que proveniência nenhuma.
 *
 * A CA da Clériga de ouro saía "16 = 13 + 1 (Destreza) + 2 + 2 (escudo)", que dá 18:
 * o `min(mod:DES, 2)` do teto da armadura punha os DOIS operandos na explicação,
 * quando só um deles entrou na conta. `max`, `min` e `menos` têm todos essa forma.
 */
test('em toda a ficha, as parcelas numéricas explicam o número', () => {
  for (const arquivo of ['barbaro-5.json', 'clerigo-5.json', 'monge-1.json']) {
    const g = JSON.parse(readFileSync(join(OURO, arquivo), 'utf8'))
    const ficha = montar(g.construcao, g.estado ?? {}).ficha!
    const campos: [string, { valor: number; parcelas: { rotulo: string; valor: unknown }[] }][] = [
      ['CA', ficha.classe_de_armadura],
      ['Pontos de Vida', ficha.pontos_de_vida_maximos],
      ['Iniciativa', ficha.iniciativa],
      ['Percepção passiva', ficha.percepcao_passiva],
    ]
    for (const [nome, r] of campos) {
      const soma = r.parcelas.reduce(
        (s, p) => s + (typeof p.valor === 'number' ? p.valor : 0),
        0,
      )
      assert.equal(soma, r.valor, `${arquivo} · ${nome}: as parcelas somam ${soma}, e o valor é ${r.valor}`)
    }
  }
})
