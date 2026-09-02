// O avaliador de fórmula, incluindo o que ele se recusa a fazer.
//
// Metade destes testes é negativa. É a mesma regra do dataset: um avaliador que
// nunca reprovou nada não prova que sabe avaliar — prova que aceita tudo.

import { test } from 'node:test'
import assert from 'node:assert/strict'

import { avaliar, modificadorDeAtributo, bonusDeProficiencia } from '../src/formula.ts'
import { condicaoVale } from '../src/condicao.ts'
import { ErroDoMotor, type Contexto } from '../src/tipos.ts'
import { vocabularioDeRuntime } from '../src/dataset.ts'

const VOCAB = vocabularioDeRuntime()

const CTX: Contexto = {
  nivel_do_personagem: 5,
  niveis_por_classe: { barbaro: 5 },
  atributos: { FOR: 19, DES: 14, CON: 14, INT: 8, SAB: 12, CAR: 10 },
  colunas: { dano_da_furia: 2, dado_de_artes_marciais: '1d6' },
  proficiencias: { salvaguardas: ['FOR', 'CON'], pericias: ['percepcao'] },
  predicados_ativos: ['ativo:furia'],
}

// ------------------------------------------------------------------ o básico

test('modificador de atributo arredonda para baixo, inclusive no negativo', () => {
  assert.equal(modificadorDeAtributo(19), 4)
  assert.equal(modificadorDeAtributo(10), 0)
  assert.equal(modificadorDeAtributo(9), -1)
  assert.equal(modificadorDeAtributo(1), -5)
})

test('Bônus de Proficiência sobe de quatro em quatro níveis', () => {
  const bp = (n: number) => bonusDeProficiencia({ ...CTX, nivel_do_personagem: n })
  assert.deepEqual([1, 4, 5, 8, 9, 17, 20].map(bp), [2, 2, 3, 3, 4, 6, 6])
})

test('a fórmula é árvore e resolve aninhada', () => {
  const r = avaliar([{ op: 'div_arred_baixo', args: [{ op: 'soma', args: ['19', '-10'] }, '2'] }], CTX)
  assert.equal(r.valor, 4)
})

test('termos do contexto: mod, prof, nível de classe, coluna', () => {
  assert.equal(avaliar(['mod:FOR'], CTX).valor, 4)
  assert.equal(avaliar(['prof'], CTX).valor, 3)
  assert.equal(avaliar(['nivel_classe:barbaro'], CTX).valor, 5)
  assert.equal(avaliar(['coluna:dano_da_furia'], CTX).valor, 2)
})

// -------------------------------------------------------- o motor não rola dado

test('dado fica simbólico, e não vira número', () => {
  const r = avaliar(['1d20', 'mod:DES'], CTX)
  assert.equal(r.valor, 2, 'a parte fixa')
  assert.deepEqual(r.dados, ['1d20'], 'o dado sai à parte, para a ficha mostrar')
})

test('coluna que é dado também fica simbólica', () => {
  const r = avaliar(['coluna:dado_de_artes_marciais', 'mod:DES'], CTX)
  assert.deepEqual(r.dados, ['1d6'])
  assert.equal(r.valor, 2)
})

// ------------------------------------------------------------------ condições

test('soma_se só soma quando a condição vale', () => {
  const f = [{ op: 'soma_se', condicao: { todas: ['ativo:furia'] }, args: ['coluna:dano_da_furia'] }]
  assert.equal(avaliar(f, CTX).valor, 2)
  const semFuria = { ...CTX, predicados_ativos: [] }
  assert.equal(avaliar(f, semFuria).valor, 0)
})

test('a proficiência em perícia sai do contexto, não de uma flag solta', () => {
  assert.equal(condicaoVale('proficiente_em:pericia:percepcao', CTX, VOCAB), true)
  assert.equal(condicaoVale('proficiente_em:pericia:furtividade', CTX, VOCAB), false)
})

test('condição composta aninha, um operador por objeto', () => {
  const c = { todas: ['ativo:furia', { nao: 'armadura:pesada' }] }
  assert.equal(condicaoVale(c, CTX, VOCAB), true)
})

test('comparação usa a forma da fase 13', () => {
  const c = { comparar: ['nivel_do_personagem'], op: 'gt', com: ['1'] }
  assert.equal(condicaoVale(c, CTX, VOCAB), true)
  assert.equal(condicaoVale({ ...c, op: 'lt' }, CTX, VOCAB), false)
})

// --------------------------------------------------- o que o motor SE RECUSA a fazer

test('termo desconhecido é erro, não zero', () => {
  assert.throws(() => avaliar(['bonus_magico_qualquer'], CTX), ErroDoMotor)
})

test('operação desconhecida é erro', () => {
  assert.throws(() => avaliar([{ op: 'raiz_quadrada', args: ['4'] }], CTX), ErroDoMotor)
})

test('div_arred_baixo com aridade errada é erro', () => {
  assert.throws(() => avaliar([{ op: 'div_arred_baixo', args: ['9'] }], CTX), ErroDoMotor)
})

test('predicado fora do vocabulário declarado é erro, não falso', () => {
  assert.throws(() => condicaoVale('ficou_com_raiva', CTX, VOCAB), ErroDoMotor)
})

test('dois operadores lógicos no mesmo objeto é erro', () => {
  assert.throws(
    () => condicaoVale({ todas: ['ativo:furia'], nao: 'armadura:pesada' } as never, CTX, VOCAB),
    ErroDoMotor,
  )
})

test('comparar com dado é erro: o motor é puro', () => {
  assert.throws(
    () => condicaoVale({ comparar: ['1d20'], op: 'gte', com: ['10'] }, CTX, VOCAB),
    ErroDoMotor,
  )
})

test('atributo ausente no contexto é erro', () => {
  const semSab = { ...CTX, atributos: { FOR: 10 } }
  assert.throws(() => avaliar(['mod:SAB'], semSab), ErroDoMotor)
})

test('nível numa classe que o personagem não tem é erro', () => {
  assert.throws(() => avaliar(['nivel_classe:monge'], CTX), ErroDoMotor)
})

// ------------------------------------- o caso que o Monge e o Bárbaro existem para pegar

test('cálculos de CA base concorrem: fica o maior, e eles NÃO se somam', () => {
  const ctx: Contexto = {
    ...CTX,
    atributos: { FOR: 12, DES: 17, CON: 13, INT: 10, SAB: 14, CAR: 8 },
    calculos_de_ca_base: [
      { id: 'sem_armadura', formula: ['10', 'mod:DES'] },
      { id: 'ca_defesa_sem_armadura', formula: ['10', 'mod:DES', 'mod:SAB'] },
    ],
  }
  const r = avaliar([{ op: 'max_entre_calculos_de_base', args: ['calculos_de_base_ativos'] }], ctx)
  assert.equal(r.valor, 15, 'somar os dois daria 28; o maior é 15')
  assert.equal(
    r.parcelas.find((p) => p.rotulo === 'cálculo de base usado')?.valor,
    'ca_defesa_sem_armadura',
  )
})

test('sem nenhum cálculo de CA base é erro, não CA 0', () => {
  assert.throws(
    () => avaliar([{ op: 'max_entre_calculos_de_base', args: [] }], CTX),
    ErroDoMotor,
  )
})
