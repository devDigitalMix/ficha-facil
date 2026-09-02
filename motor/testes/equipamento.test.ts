// Equipamento equipado.
//
// Os três personagens de ouro cobrem o caminho feliz. Estes testes cobrem o que
// eles não conseguem cobrir sem virar outra pessoa: o teto de Destreza da armadura
// Média só morde com Destreza alta, e a falta de proficiência só aparece com uma
// arma que a classe não concede.
//
// Os dois casos foram escritos DEPOIS do teste de mutação mostrar que sem eles o
// motor podia ignorar o teto e dar proficiência com tudo, e nada reprovava.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { montar } from '../src/motor.ts'
import type { Construcao } from '../src/colecao.ts'
import { separar } from '../src/equipamento.ts'
import { ErroDoMotor } from '../src/tipos.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))

function clerigaCom(mudancas: Partial<Construcao>): Construcao {
  const g = JSON.parse(
    readFileSync(join(AQUI, '..', 'ouro', 'clerigo-5.json'), 'utf-8'),
  ) as { construcao: Construcao }
  return { ...JSON.parse(JSON.stringify(g.construcao)), ...mudancas }
}

test('a armadura Média respeita o teto do modificador de Destreza', () => {
  // Cota de Malha Parcial: base 13, Destreza até 2. Com Destreza 18 (+4), a CA é
  // 13 + 2 + 2 (Escudo) = 17, e não 13 + 4 + 2 = 19.
  const c = clerigaCom({
    atributos_base: { FOR: 12, DES: 18, CON: 14, INT: 10, SAB: 15, CAR: 8 },
    equipamento_equipado: ['cota_de_malha_parcial', 'escudo'],
  })
  const r = montar(c, {})
  assert.equal(
    r.ficha.classe_de_armadura.valor,
    17,
    'sem o teto daria 19 — a armadura Média corta a Destreza em +2',
  )
})

test('armadura sem teto soma a Destreza inteira', () => {
  // Couro Batido é Leve: base 12, sem teto. Com Destreza 18 dá 12 + 4 = 16.
  // Sem este par, "respeitar o teto" poderia ser "ignorar a Destreza sempre".
  const c = clerigaCom({
    atributos_base: { FOR: 12, DES: 18, CON: 14, INT: 10, SAB: 15, CAR: 8 },
    equipamento_equipado: ['couro_batido'],
  })
  assert.equal(montar(c, {}).ficha.classe_de_armadura.valor, 16)
})

test('a armadura concorre com a Defesa sem Armadura; não somam', () => {
  // O Monge de nível 1 tem CA 15 pela Defesa sem Armadura. De Couro Batido
  // (12 + 3 de Destreza = 15) ele empata — e o que não pode é dar 30.
  const g = JSON.parse(
    readFileSync(join(AQUI, '..', 'ouro', 'monge-1.json'), 'utf-8'),
  ) as { construcao: Construcao }
  const c: Construcao = JSON.parse(JSON.stringify(g.construcao))
  c.equipamento_equipado = ['couro_batido']
  const r = montar(c, {})
  assert.ok(
    r.ficha.classe_de_armadura.valor <= 15,
    `CA ${r.ficha.classe_de_armadura.valor}: os cálculos de base estão somando`,
  )
})

test('a Defesa sem Armadura do Monge deixa de valer quando ele veste armadura', () => {
  // A condição está no dado ({nao: 'armadura:qualquer'}); o motor só precisa dizer
  // que há armadura vestida. É por isso que o equipamento vira predicado.
  const g = JSON.parse(
    readFileSync(join(AQUI, '..', 'ouro', 'monge-1.json'), 'utf-8'),
  ) as { construcao: Construcao }
  const c: Construcao = JSON.parse(JSON.stringify(g.construcao))
  c.equipamento_equipado = ['placas']
  const r = montar(c, {})
  const usado = r.ficha.classe_de_armadura.parcelas.find((p) => p.rotulo === 'cálculo de base usado')
  assert.notEqual(usado?.valor, 'ca_defesa_sem_armadura', 'de Placas, a Defesa sem Armadura cai')
  assert.equal(r.ficha.classe_de_armadura.valor, 18, 'Placas dá 18 e não soma Destreza')
})

test('arma que a classe não concede sai SEM proficiência', () => {
  // O Clérigo é proficiente com armas Simples. O Machado Grande é Marcial: o ataque
  // sai sem o Bônus de Proficiência, e a ficha diz isso em vez de somar calada.
  const c = clerigaCom({ equipamento_equipado: ['machado_grande'] })
  const r = montar(c, {})
  const ataque = r.ficha.ataques.find((a) => a.arma === 'machado_grande')
  assert.ok(ataque)
  assert.equal(ataque.proficiente, false, 'Clérigo não tem armas Marciais')
  assert.equal(ataque.jogada.valor, 1, '+1 = só o modificador de Força, sem os 3 de proficiência')
})

test('a arma de Acuidade usa o maior entre Força e Destreza, e diz qual usou', () => {
  const c = clerigaCom({
    atributos_base: { FOR: 8, DES: 18, CON: 14, INT: 10, SAB: 15, CAR: 8 },
    equipamento_equipado: ['adaga'],
  })
  const ataque = montar(c, {}).ficha.ataques.find((a) => a.arma === 'adaga')
  assert.ok(ataque)
  assert.equal(ataque.atributo, 'DES', 'com Força 8 e Destreza 18, a Acuidade escolhe Destreza')
  assert.match(ataque.porque_o_atributo, /Acuidade/)
})

test('arma à distância usa Destreza mesmo com Força alta', () => {
  const c = clerigaCom({
    atributos_base: { FOR: 18, DES: 12, CON: 14, INT: 10, SAB: 15, CAR: 8 },
    equipamento_equipado: ['funda'],
  })
  const ataque = montar(c, {}).ficha.ataques.find((a) => a.arma === 'funda')
  assert.ok(ataque)
  assert.equal(ataque.atributo, 'DES')
})

// ------------------------------------------------------- o que o motor recusa

test('duas armaduras vestidas ao mesmo tempo é erro', () => {
  assert.throws(() => separar(['couro_batido', 'placas']), ErroDoMotor)
})

test('dois escudos é erro', () => {
  assert.throws(() => separar(['escudo', 'escudo']), ErroDoMotor)
})

test('item que não existe é erro', () => {
  assert.throws(() => separar(['armadura_de_mitril_do_rei']), ErroDoMotor)
})

// ------------------------------------------------------------------ folga

test('folga: equipar uma mochila não muda CA nem ataque', () => {
  const semNada = montar(clerigaCom({ equipamento_equipado: [] }), {})
  const comMochila = montar(clerigaCom({ equipamento_equipado: ['mochila'] }), {})
  assert.equal(
    comMochila.ficha.classe_de_armadura.valor,
    semNada.ficha.classe_de_armadura.valor,
  )
  assert.equal(comMochila.ficha.ataques.length, semNada.ficha.ataques.length)
})
