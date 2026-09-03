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

test('o Ataque Desarmado usa o MAIOR dado disponível, não o primeiro da lista', () => {
  // O Combate Desarmado dá 1d6, e 1d8 com as mãos livres — e com as mãos livres os
  // dois passam na condição. Pegar o primeiro mostrava 1d6 a quem tinha direito a
  // 1d8. A ordem na lista é a de declaração no dado, que não quer dizer nada.
  const base = {
    especie: 'humano',
    antecedente: 'soldado',
    niveis: [{ classe: 'guerreiro', nivel: 1 }],
    atributos_base: { FOR: 16, DES: 13, CON: 14, INT: 10, SAB: 12, CAR: 8 },
    escolhas: {
      humano_habil: 'atletismo',
      humano_versatil: 'alerta',
      guerreiro_pericias_iniciais: ['atletismo', 'percepcao'],
      guerreiro_estilo_de_luta: 'combate_desarmado',
      guerreiro_maestrias: ['espada_longa', 'azagaia', 'clava'],
    },
  }
  const desarmado = (equipado: string[]) =>
    montar({ ...base, equipamento_equipado: equipado }, {}).ficha.ataques.find(
      (a) => a.arma === 'ataque_desarmado',
    )!

  assert.deepEqual(desarmado([]).dano.dados, ['1d8'], 'mãos livres: 1d8')
  assert.deepEqual(desarmado(['espada_longa']).dano.dados, ['1d6'], 'com arma: 1d6')
  assert.deepEqual(desarmado(['escudo']).dano.dados, ['1d6'], 'com Escudo: 1d6')
})

test('a parcela do dado diz de onde ele vem, e não o nome de outra classe', () => {
  // O rótulo era 'dado de Artes Marciais' fixo — a característica do MONGE — e
  // aparecia assim na ficha de um Guerreiro com Combate Desarmado.
  const OURO = join(dirname(fileURLToPath(import.meta.url)), '..', 'ouro')
  const g = JSON.parse(readFileSync(join(OURO, 'monge-1.json'), 'utf-8'))
  const monge = montar(g.construcao, g.estado ?? {}).ficha.ataques.find(
    (a: { arma: string }) => a.arma === 'ataque_desarmado',
  )!
  assert.equal(monge.dano.parcelas?.[0].rotulo, 'dado de Artes Marciais')

  const guerreiro = montar(
    {
      especie: 'humano',
      antecedente: 'soldado',
      niveis: [{ classe: 'guerreiro', nivel: 1 }],
      atributos_base: { FOR: 16, DES: 13, CON: 14, INT: 10, SAB: 12, CAR: 8 },
      escolhas: {
        humano_habil: 'atletismo',
        humano_versatil: 'alerta',
        guerreiro_pericias_iniciais: ['atletismo', 'percepcao'],
        guerreiro_estilo_de_luta: 'combate_desarmado',
        guerreiro_maestrias: ['espada_longa', 'azagaia', 'clava'],
      },
    },
    {},
  ).ficha.ataques.find((a) => a.arma === 'ataque_desarmado')!
  assert.equal(guerreiro.dano.parcelas?.[0].rotulo, 'dado de Combate Desarmado')
})


// ------------------------------------------- o resto da regra do Combate Desarmado

const GUERREIRO_DESARMADO: Construcao = {
  especie: 'humano',
  antecedente: 'soldado',
  niveis: [{ classe: 'guerreiro', nivel: 1 }],
  atributos_base: { FOR: 16, DES: 13, CON: 14, INT: 10, SAB: 12, CAR: 8 },
  escolhas: {
    humano_habil: 'atletismo',
    humano_versatil: 'alerta',
    guerreiro_pericias_iniciais: ['atletismo', 'percepcao'],
    guerreiro_estilo_de_luta: 'combate_desarmado',
    guerreiro_maestrias: ['espada_longa', 'azagaia', 'clava'],
  },
}

const socoCom = (equipamento_equipado: string[]) =>
  montar({ ...GUERREIRO_DESARMADO, equipamento_equipado }, {}).ficha.ataques.find(
    (a) => a.arma === 'ataque_desarmado',
  )!

/**
 * "…se você não estiver segurando nenhuma arma OU Escudo" (p. 195).
 *
 * O teste acima já cobre arma sozinha e Escudo sozinho. Falta o caso das duas
 * juntas — que é o normal de um Guerreiro em mesa, e o único em que as duas
 * condições reprovam ao mesmo tempo. Uma condição que só é testada isolada pode
 * estar sendo avaliada com `ou` onde devia ser `e` sem ninguém perceber.
 */
test('arma E Escudo juntos continuam dando d6, não d8', () => {
  assert.deepEqual(socoCom(['espada_longa', 'escudo']).dano.dados, ['1d6'])
})

test('o Ataque Desarmado soma Força e nomeia o atributo por extenso', () => {
  const soco = socoCom([])
  assert.equal(soco.tipo_dano, 'contundente')
  assert.equal(soco.dano.valor, 3, 'Força 16 dá +3')
  assert.deepEqual(
    soco.dano.parcelas.map((p) => p.rotulo),
    ['dado de Combate Desarmado', 'Força'],
    'a proveniência usa o nome do atributo, como no resto da ficha',
  )
})
