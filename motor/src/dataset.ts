// Carrega o dataset. O motor lê `dados/` como dado imutável — nunca escreve nele.

import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import type { Vocabulario } from './condicao.ts'
import { ErroDoMotor } from './tipos.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))
export const RAIZ_DADOS = join(AQUI, '..', '..', 'dados')

// `dados/` é imutável em tempo de execução — o motor só lê. Reler e reparsear a cada
// chamada custava 49 ms por ficha no backend, quase tudo em `magias.json`. Memorizar
// não fere a pureza: a mesma entrada continua dando a mesma saída, e a única coisa
// que muda é não pagar o disco duas vezes pelo mesmo arquivo.
//
// Quem mexer em `dados/` no meio de um processo (os testes que plantam defeito)
// chama `esquecerDataset()`.
const memoria = new Map<string, unknown>()

export function lerJson<T = unknown>(...partes: string[]): T {
  const caminho = join(RAIZ_DADOS, ...partes)
  const guardado = memoria.get(caminho)
  if (guardado !== undefined) return guardado as T
  const lido = JSON.parse(readFileSync(caminho, 'utf-8')) as T
  memoria.set(caminho, lido)
  return lido
}

/** Esquece o que foi lido. Para testes que mexem em `dados/` com o processo de pé. */
export function esquecerDataset(): void {
  memoria.clear()
}

export function catalogo<T = Record<string, unknown>>(nome: string): { itens: T[] } {
  return lerJson(`catalogos`, `${nome}.json`)
}

export function vocabularioDeRuntime(): Vocabulario {
  return lerJson('vocabulario_de_runtime.json')
}

/**
 * Um item de catálogo por id; ausência é erro, nunca `undefined` silencioso.
 *
 * Lança `ErroDoMotor` e não `Error`: id que não existe é quase sempre construção
 * errada — alguém pediu uma espécie que o livro não tem — e quem chama precisa poder
 * distinguir isso de defeito interno. Como `Error` puro, virava 500 no backend.
 */
export function porId<T extends { id: string }>(itens: T[], id: string, ondeVim: string): T {
  const achado = itens.find((i) => i.id === id)
  if (!achado) throw new ErroDoMotor(`id inexistente em ${ondeVim}: '${id}'`)
  return achado
}
