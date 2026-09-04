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

test('a proveniência dos Pontos de Vida diz de onde vem cada ponto', () => {
  // A queixa do João: "eu clico na vida e no máximo ele diz 'vida no nível 1 +
  // característica'. Eu quero saber por que tenho 11". Cada parcela que é ela mesma
  // uma conta passou a se abrir — com os rótulos que o catálogo já declarava.
  const anao = montar({
    especie: 'anao',
    antecedente: 'acolito',
    niveis: [{ classe: 'clerigo', nivel: 1 }],
    atributos_base: { FOR: 12, DES: 12, CON: 16, INT: 10, SAB: 15, CAR: 10 },
  } as unknown as Parameters<typeof montar>[0])

  const pv = anao.ficha!.pontos_de_vida_maximos
  const nivel1 = pv.parcelas.find((p) => /nível 1/.test(p.rotulo))
  assert.ok(nivel1?.parcelas?.length, 'os Pontos de Vida do nível 1 têm de se abrir')
  assert.deepEqual(
    nivel1!.parcelas!.map((p) => p.valor),
    [8, 3],
    'o Dado de Vida do Clérigo (d8) e o modificador de Constituição (+3)',
  )

  // E o bônus de característica diz QUEM o deu — que é a resposta útil.
  const bonus = pv.parcelas.find((p) => /caracter/i.test(p.rotulo))
  assert.ok(bonus?.parcelas?.length, 'o bônus tem de dizer de onde veio')
  assert.match(bonus!.parcelas![0].rotulo, /Tenacidade/)

  // A soma das parcelas abertas continua sendo a parcela de cima.
  for (const p of pv.parcelas) {
    if (!p.parcelas) continue
    const soma = p.parcelas.reduce((s, x) => s + Number(x.valor), 0)
    assert.equal(soma, Number(p.valor), `'${p.rotulo}': as partes têm de somar o todo`)
  }
})

test('acima do nível 1, a conta separa o que veio de cada nível', () => {
  const barbaro = montar({
    especie: 'humano',
    antecedente: 'acolito',
    niveis: [{ classe: 'barbaro', nivel: 3 }],
    atributos_base: { FOR: 16, DES: 14, CON: 16, INT: 10, SAB: 12, CAR: 10 },
  } as unknown as Parameters<typeof montar>[0])

  const seguintes = barbaro.ficha!.pontos_de_vida_maximos.parcelas
    .find((p) => /níveis seguintes/.test(p.rotulo))
  assert.ok(seguintes?.parcelas?.length)
  assert.deepEqual(seguintes!.parcelas!.map((p) => p.valor), [14, 6])
})
