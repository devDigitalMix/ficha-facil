// Carrega o dataset. O motor lê `dados/` como dado imutável — nunca escreve nele.

import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import type { Vocabulario } from './condicao.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))
export const RAIZ_DADOS = join(AQUI, '..', '..', 'dados')

export function lerJson<T = unknown>(...partes: string[]): T {
  return JSON.parse(readFileSync(join(RAIZ_DADOS, ...partes), 'utf-8')) as T
}

export function catalogo<T = Record<string, unknown>>(nome: string): { itens: T[] } {
  return lerJson(`catalogos`, `${nome}.json`)
}

export function vocabularioDeRuntime(): Vocabulario {
  return lerJson('vocabulario_de_runtime.json')
}

/** Um item de catálogo por id; ausência é erro, nunca `undefined` silencioso. */
export function porId<T extends { id: string }>(itens: T[], id: string, ondeVim: string): T {
  const achado = itens.find((i) => i.id === id)
  if (!achado) throw new Error(`id inexistente em ${ondeVim}: '${id}'`)
  return achado
}
