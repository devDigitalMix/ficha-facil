// A regra do PLANO-MOTOR §1, virada em teste.
//
// "Nenhuma entidade conhece as outras" só vale se valer também no código: se um
// `if (classe === 'monge')` entrar no motor, o dataset inteiro perdeu o sentido —
// passa a existir uma regra que mora em dois lugares, e um deles não é conferido
// por ninguém.
//
// O teste é literal: **nenhum id de conteúdo pode aparecer como literal no código
// do motor.** Comentário não conta — explicar por que o Monge é o caso difícil é
// justamente o que se quer que esteja escrito.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { catalogo, lerJson, vocabularioDeRuntime } from '../src/dataset.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))
const SRC = join(AQUI, '..', 'src')

/** Tira comentários de linha e de bloco, e o conteúdo some junto. */
function semComentarios(codigo: string): string {
  return codigo
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/(^|[^:])\/\/.*$/gm, '$1')
}

function idsDeConteudo(): Set<string> {
  const ids = new Set<string>()
  const junta = (itens: { id?: string }[]) => {
    for (const i of itens) {
      // ids muito curtos colidem com palavras comuns do código ('acao', 'livre');
      // os que importam — nome de classe, de característica, de magia — são longos.
      if (i.id && i.id.length >= 6) ids.add(i.id)
    }
  }
  for (const nome of ['talentos', 'magias', 'itens', 'criaturas', 'especies', 'antecedentes']) {
    junta(catalogo<{ id: string }>(nome).itens)
  }
  for (const arq of ['classes.json', 'subclasses.json', 'caracteristicas.json']) {
    junta(lerJson<{ itens: { id: string }[] }>(arq).itens)
  }
  return ids
}

/**
 * O vocabulário de runtime da fase 13 é a ÚNICA lista que o motor tem direito de
 * conhecer: são os predicados, gatilhos e durações que ele implementa. Um deles pode
 * colidir com um id de conteúdo — 'segurando:escudo' contém o id do item 'escudo' —
 * e barrar isso seria proibir o motor de nomear o que ele executa.
 */
function vocabularioPermitido(): Set<string> {
  const v = vocabularioDeRuntime() as unknown as Record<string, unknown>
  const fora = new Set<string>()
  for (const chave of ['predicados', 'gatilhos', 'fases', 'duracoes', 'custos', 'empilhamentos']) {
    for (const t of (v[chave] as string[]) ?? []) fora.add(t)
  }
  for (const fam of Object.keys((v.familias_de_predicado as object) ?? {})) fora.add(fam)
  return fora
}

test('nenhum id de conteúdo aparece como literal no código do motor', () => {
  const ids = idsDeConteudo()
  const permitidos = vocabularioPermitido()
  assert.ok(ids.size > 500, 'a lista de ids não carregou direito')

  const achados: string[] = []
  for (const arq of readdirSync(SRC).filter((f) => f.endsWith('.ts'))) {
    const codigo = semComentarios(readFileSync(join(SRC, arq), 'utf-8'))
    // só literais entre aspas contam: `mod:DES` num template não é id de conteúdo
    for (const m of codigo.matchAll(/['"`]([a-z0-9_:.]+)['"`]/g)) {
      const literal = m[1]
      if (permitidos.has(literal)) continue
      for (const parte of literal.split(':')) {
        if (ids.has(parte)) achados.push(`${arq}: '${literal}'`)
      }
    }
  }

  assert.deepEqual(
    achados,
    [],
    'id de conteúdo no código do motor — a regra é que ele viva em dados/, não aqui',
  )
})
