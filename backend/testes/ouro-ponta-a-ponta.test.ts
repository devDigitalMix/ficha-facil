// Cada personagem de ouro passa pelo backend inteiro e sai com a ficha do livro.
//
// O `ouro.test.ts` do motor prova que a biblioteca acerta a conta. Este prova que
// nada se perde no caminho até o HTTP: serialização, validação de corpo, e a ficha
// que volta ser a mesma que o motor calculou.

import { test, after } from 'node:test'
import assert from 'node:assert/strict'
import { readdirSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { subir } from './ajuda.ts'

const OURO = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'motor', 'ouro')
const goldens = readdirSync(OURO)
  .filter((f) => f.endsWith('.json'))
  .map((f) => ({ arquivo: f, ...(JSON.parse(readFileSync(join(OURO, f), 'utf-8')) as any) }))

const c = await subir()
after(() => c.fechar())

test('há goldens para conferir', () => {
  assert.ok(goldens.length >= 3)
})

for (const g of goldens) {
  test(`${g.arquivo}: cria, lê e confere contra o esperado`, async () => {
    const criado = await c.pedir('POST', '/personagens', {
      nome: g.nome ?? g.arquivo,
      construcao: g.construcao,
      estado: g.estado ?? {},
    })
    assert.equal(criado.status, 201, JSON.stringify(criado.corpo).slice(0, 300))

    const lido = await c.pedir('GET', `/personagens/${criado.corpo.id}`)
    assert.equal(lido.status, 200)
    const ficha = lido.corpo.ficha

    for (const campo of ['classe_de_armadura', 'pontos_de_vida_maximos', 'iniciativa',
      'percepcao_passiva'] as const) {
      if (!g.esperado?.[campo]) continue
      assert.equal(ficha[campo].valor, g.esperado[campo].valor, `${g.arquivo}: ${campo}`)
    }
    if (g.esperado?.modificadores) {
      assert.deepEqual(ficha.modificadores, g.esperado.modificadores, `${g.arquivo}: modificadores`)
    }
    if (g.esperado?.deslocamento_m !== undefined) {
      assert.equal(ficha.deslocamento_m, g.esperado.deslocamento_m)
    }
    // A proveniência tem de chegar junto do número: é o "CA 17 = 10 + 3 + 4" que o
    // PLANO-MOTOR pede como resposta, e não como log.
    assert.ok(Array.isArray(ficha.classe_de_armadura.parcelas))
  })
}

test('o estado do golden atravessa o HTTP e continua mudando a ficha', async () => {
  // O Bárbaro em Fúria não é o mesmo Bárbaro: se o estado se perdesse na
  // serialização, a ficha voltaria igual e ninguém notaria.
  const b = goldens.find((g) => g.arquivo.startsWith('barbaro'))
  if (!b?.estado || !b?.estado_sem_furia) return

  const comFuria = await c.pedir('POST', '/personagens',
    { nome: 'Torvar em Fúria', construcao: b.construcao, estado: b.estado })
  const semFuria = await c.pedir('POST', '/personagens',
    { nome: 'Torvar parado', construcao: b.construcao, estado: b.estado_sem_furia })
  assert.equal(comFuria.status, 201)
  assert.equal(semFuria.status, 201)
  assert.notDeepEqual(
    comFuria.corpo.ficha,
    semFuria.corpo.ficha,
    'a Fúria tem de mudar alguma coisa na ficha',
  )
})
