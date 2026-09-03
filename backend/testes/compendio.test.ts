// O compêndio é estático e imutável entre builds. Estes testes existem para provar
// que ele se comporta como tal — em especial o ETag, que é o que evita reenviar as
// 391 magias a cada abertura de tela.

import { test, after } from 'node:test'
import assert from 'node:assert/strict'
import { subir } from './ajuda.ts'

const c = await subir()
after(() => c.fechar())

test('saúde diz a versão do dataset', async () => {
  const r = await c.pedir('GET', '/saude')
  assert.equal(r.status, 200)
  assert.equal(r.corpo.ok, true)
  assert.match(r.corpo.versao_do_dataset, /^[0-9a-f]{12}$/)
})

test('o índice lista coleções e catálogos, com o total de cada um', async () => {
  const r = await c.pedir('GET', '/compendio')
  assert.equal(r.status, 200)
  const porNome = new Map(r.corpo.colecoes.map((x: any) => [x.nome, x]))
  assert.equal(porNome.get('classes')!.familia, 'colecao')
  assert.equal(porNome.get('classes')!.total, 12)
  assert.equal(porNome.get('magias')!.familia, 'catalogo')
  assert.equal(porNome.get('magias')!.total, 391)
})

test('uma coleção sai inteira, e um item sai sozinho', async () => {
  const todas = await c.pedir('GET', '/compendio/classes')
  assert.equal(todas.corpo.itens.length, 12)

  const uma = await c.pedir('GET', '/compendio/classes/paladino')
  assert.equal(uma.status, 200)
  assert.equal(uma.corpo.nome, 'Paladino')
  assert.equal(uma.corpo.dado_de_vida, 10)
})

test('o ETag é a versão do dataset, e quem já a tem recebe 304', async () => {
  const primeira = await c.pedir('GET', '/compendio/magias')
  const etag = primeira.cabecalhos.get('etag')!
  assert.ok(etag)
  assert.match(primeira.cabecalhos.get('cache-control')!, /immutable/)

  const segunda = await c.pedir('GET', '/compendio/magias', undefined, { 'if-none-match': etag })
  assert.equal(segunda.status, 304)
  assert.equal(segunda.corpo, undefined, '304 não manda corpo — é o ponto do 304')
})

test('coleção e item inexistentes são 404, não corpo vazio', async () => {
  assert.equal((await c.pedir('GET', '/compendio/dragoes')).status, 404)
  assert.equal((await c.pedir('GET', '/compendio/classes/necromante')).status, 404)
})

test('método errado na rota certa é 405, e não 404', async () => {
  const r = await c.pedir('POST', '/compendio/classes', {})
  assert.equal(r.status, 405)
})
