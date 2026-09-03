// A lista de magias da ficha, e as marcas que ela põe nas escolhas.
//
// A queixa que originou este arquivo: "no Mago, as magias que peguei por
// antecedente/talento não aparecem entre as preparáveis — só as da lista da
// classe". Eram dois problemas com o mesmo sintoma:
//
//   1. o efeito `desbloquear_magias` caía em `nao_consumidos` e ninguém o lia, de
//      modo que a magia do talento não existia em NENHUM lugar da ficha;
//   2. a tela de escolha não tinha como avisar que uma opção já era conhecida por
//      outro caminho — e gastar as duas escolhas do Iniciado em Magia em truques
//      que a classe já dava é um erro que não dá para desfazer.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { montar } from '../src/motor.ts'

const OURO = join(dirname(fileURLToPath(import.meta.url)), '..', 'ouro')

/** A Clériga de ouro tem Iniciado em Magia pelo antecedente: é o caso da queixa. */
function clerigaDeOuro() {
  return JSON.parse(readFileSync(join(OURO, 'clerigo-5.json'), 'utf8')).construcao
}

test('a magia vinda do talento aparece na ficha, e não só as da classe', () => {
  const magias = montar(clerigaDeOuro()).ficha!.magias
  const doTalento = magias.filter((m) => m.origem.includes('Iniciado em Magia'))
  assert.ok(
    doTalento.length >= 3,
    `esperava os dois truques e a magia de 1º círculo do talento; vieram ${doTalento.length}`,
  )
  assert.ok(
    magias.some((m) => m.origem.includes('Conjuração')),
    'as da classe continuam lá — o conserto não pode ter trocado uma fonte pela outra',
  )
})

test('cada magia diz de onde veio, com nome e não com id', () => {
  for (const m of montar(clerigaDeOuro()).ficha!.magias) {
    assert.ok(
      !/[a-z]_[a-z]/.test(m.origem),
      `origem com id cru em vez de nome: '${m.origem}' (magia ${m.id})`,
    )
    assert.ok(m.nome && m.nome !== m.id, `magia sem nome legível: '${m.id}'`)
    assert.equal(typeof m.circulo, 'number')
  }
})

test('a magia sempre preparada do talento não ocupa vaga de preparação', () => {
  const magias = montar(clerigaDeOuro()).ficha!.magias
  const sempre = magias.find((m) => m.modo === 'sempre_preparada')
  assert.ok(sempre, 'o Iniciado em Magia dá uma magia de 1º círculo sempre preparada')
  assert.equal(sempre!.nao_conta_para_o_limite, true)
  assert.equal(sempre!.pronta_para_conjurar, true)
})

test('truque e magia preparada estão prontos; nada mais é prometido', () => {
  for (const m of montar(clerigaDeOuro()).ficha!.magias) {
    if (['conhecida', 'preparada', 'sempre_preparada'].includes(m.modo)) {
      assert.equal(m.pronta_para_conjurar, true, `${m.nome} (${m.modo}) devia estar pronta`)
    } else {
      assert.equal(m.pronta_para_conjurar, false, `${m.nome} (${m.modo}) NÃO está pronta`)
    }
  }
})

test('a escolha avisa quando a opção já vem de outra porta', () => {
  const c = clerigaDeOuro()
  delete c.escolhas['iniciado_em_magia_truques'] // volta ao checklist
  const item = montar(c).checklist.find((i) => i.escolha_id === 'iniciado_em_magia_truques')
  assert.ok(item, 'a escolha esquecida tem de voltar para o checklist')
  const marcadas = item!.opcoes.filter((o) => o.ja_tem)
  assert.ok(marcadas.length > 0, 'a Clériga já tem truques da classe que estão nesta lista')
  for (const o of marcadas) {
    assert.ok(o.ja_tem!.includes('Clérigo'), `marca sem dizer de onde: '${o.ja_tem}'`)
  }
  assert.ok(
    item!.opcoes.length > marcadas.length,
    'marcar não é filtrar: a opção repetida continua escolhível',
  )
})

test('escolha reescolhível não marca as próprias opções como repetidas', () => {
  // As magias que a Clériga preparou vieram de `clerigo_preparadas`. Se a marca não
  // excluísse a própria escolha, a lista voltaria inteira marcada no descanso
  // seguinte — o aviso viraria ruído e ninguém mais o leria.
  const c = clerigaDeOuro()
  delete c.escolhas['clerigo_preparadas']
  const item = montar(c).checklist.find((i) => i.escolha_id === 'clerigo_preparadas')
  assert.ok(item)
  const daPropriaEscolha = item!.opcoes.filter((o) => o.ja_tem?.includes('Conjuração'))
  assert.equal(daPropriaEscolha.length, 0)
})
