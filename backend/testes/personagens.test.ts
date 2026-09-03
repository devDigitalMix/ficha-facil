// O ciclo de vida do personagem.
//
// A asserção que mais importa neste arquivo é a de que o backend **não grava o que o
// motor recusa**. Um backend que aceita e depois mostra erro deixa o personagem num
// estado que nenhuma regra do livro produz.

import { test, after } from 'node:test'
import assert from 'node:assert/strict'
import { subir, ouro } from './ajuda.ts'

const c = await subir()
after(() => c.fechar())

const clerigo = ouro('clerigo-5')
const novo = (extra: Record<string, unknown> = {}) => ({
  nome: 'Ysolde',
  construcao: clerigo.construcao,
  ...extra,
})

test('cria a partir de uma construção e devolve a ficha do livro', async () => {
  const r = await c.pedir('POST', '/personagens', novo())
  assert.equal(r.status, 201)
  assert.match(r.cabecalhos.get('location')!, /^\/personagens\//)
  assert.equal(r.corpo.ficha.classe_de_armadura.valor, clerigo.esperado.classe_de_armadura.valor)
  assert.equal(
    r.corpo.ficha.pontos_de_vida_maximos.valor,
    clerigo.esperado.pontos_de_vida_maximos.valor,
  )
  assert.equal(r.corpo.versao_do_dataset.length, 12)
  assert.equal(r.corpo.aviso_de_versao, undefined)
})

test('o personagem guarda a construção, nunca a ficha', async () => {
  const { corpo } = await c.pedir('POST', '/personagens', novo())
  const guardado = c.armazem.ler(corpo.id)!
  assert.ok(guardado.construcao, 'a construção fica')
  assert.equal((guardado as any).ficha, undefined, 'a ficha, não — ela se recalcula')
})

test('a proveniência vem junto do número', async () => {
  const { corpo } = await c.pedir('POST', '/personagens', novo())
  const ca = corpo.ficha.classe_de_armadura
  assert.ok(Array.isArray(ca.parcelas) && ca.parcelas.length > 1,
    'CA 16 = 13 + 1 + 2 precisa chegar como parcelas, não só como 16')
})

test('recusa a construção com escolha inválida, e não grava nada', async () => {
  const quebrada = JSON.parse(JSON.stringify(clerigo.construcao))
  quebrada.escolhas.clerigo_pericias_iniciais = ['voar', 'nadar']
  const r = await c.pedir('POST', '/personagens', { nome: 'Torto', construcao: quebrada })
  assert.equal(r.status, 422)
  assert.equal(r.corpo.erro, 'construcao_invalida')
  assert.ok(r.corpo.detalhe.some((d: any) => d.tipo === 'opcao_invalida'))
  assert.ok(!c.armazem.listar().some((p) => p.nome === 'Torto'), 'não pode ter sido gravado')
})

test('recusa corpo malformado antes de chegar no motor', async () => {
  for (const [corpo, oQue] of [
    [{ construcao: clerigo.construcao }, 'sem nome'],
    [{ nome: 'X' }, 'sem construção'],
    [{ nome: 'X', construcao: { especie: 'humano' } }, 'sem níveis'],
    [{ nome: 'X', construcao: { ...clerigo.construcao, niveis: [{ classe: 'clerigo', nivel: 21 }] } },
      'nível fora da faixa'],
  ] as const) {
    const r = await c.pedir('POST', '/personagens', corpo)
    assert.equal(r.status, 400, `${oQue} deveria dar 400`)
  }
})

test('lista os personagens com o mais recente no topo', async () => {
  const c2 = await subir()
  try {
    const a = await c2.pedir('POST', '/personagens', { nome: 'Primeira', construcao: clerigo.construcao })
    await c2.pedir('POST', '/personagens', { nome: 'Segunda', construcao: clerigo.construcao })
    await c2.pedir('GET', `/personagens/${a.corpo.id}`) // tocar na primeira a traz para o topo
    const r = await c2.pedir('GET', '/personagens')
    assert.equal(r.corpo.itens[0].nome, 'Primeira')
  } finally {
    await c2.fechar()
  }
})

test('personagem inexistente é 404, e id com travessia de caminho também', async () => {
  assert.equal((await c.pedir('GET', '/personagens/nao-existe')).status, 404)
  assert.equal((await c.pedir('GET', '/personagens/..%2F..%2Fetc%2Fpasswd')).status, 404)
})

test('apaga', async () => {
  const { corpo } = await c.pedir('POST', '/personagens', novo({ nome: 'Efêmera' }))
  assert.equal((await c.pedir('DELETE', `/personagens/${corpo.id}`)).status, 204)
  assert.equal((await c.pedir('GET', `/personagens/${corpo.id}`)).status, 404)
})

test('id inexistente na construção é 422, e não 500', async () => {
  // 500 diz "a culpa é minha"; aqui a culpa é de quem mandou uma espécie que o livro
  // não tem. A primeira versão respondia 500 por duas razões somadas: `ErroDoMotor`
  // não definia `name`, e `porId` lançava `Error` puro.
  const base = {
    especie: 'humano',
    antecedente: 'acolito',
    niveis: [{ classe: 'clerigo', nivel: 1 }],
    atributos_base: { FOR: 12, DES: 12, CON: 12, INT: 12, SAB: 12, CAR: 12 },
  }
  for (const [campo, valor] of [
    ['especie', 'gnomo_do_espaco'],
    ['antecedente', 'pirata_lunar'],
  ] as const) {
    const r = await c.pedir('POST', '/personagens', {
      nome: 'Impossível',
      construcao: { ...base, [campo]: valor },
    })
    assert.equal(r.status, 422, `${campo} inexistente deveria ser 422`)
    assert.equal(r.corpo.erro, 'motor_recusou')
    assert.match(r.corpo.mensagem, new RegExp(valor))
  }
})

test('classe inexistente também é 422', async () => {
  const r = await c.pedir('POST', '/personagens', {
    nome: 'Impossível',
    construcao: {
      especie: 'humano',
      antecedente: 'acolito',
      niveis: [{ classe: 'necromante', nivel: 1 }],
      atributos_base: { FOR: 12, DES: 12, CON: 12, INT: 12, SAB: 12, CAR: 12 },
    },
  })
  assert.equal(r.status, 422)
})
