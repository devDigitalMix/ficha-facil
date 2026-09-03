// Sobe o servidor numa porta livre e devolve um cliente curto.
// Cada teste tem o seu, com armazém em memória: nada em disco, nada compartilhado.

import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { criarServidor } from '../src/servidor.ts'
import { ArmazemNaMemoria, type Armazem } from '../src/armazem.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))

export type Cliente = {
  base: string
  armazem: Armazem
  pedir(metodo: string, caminho: string, corpo?: unknown, cabecalhos?: Record<string, string>):
    Promise<{ status: number; corpo: any; cabecalhos: Headers }>
  fechar(): Promise<void>
}

export async function subir(): Promise<Cliente> {
  const armazem = new ArmazemNaMemoria()
  const servidor = criarServidor(armazem)
  await new Promise<void>((r) => servidor.listen(0, r))
  const porta = (servidor.address() as { port: number }).port
  const base = `http://127.0.0.1:${porta}`
  return {
    base,
    armazem,
    async pedir(metodo, caminho, corpo, cabecalhos = {}) {
      const r = await fetch(base + caminho, {
        method: metodo,
        headers: { 'content-type': 'application/json', ...cabecalhos },
        body: corpo === undefined ? undefined : JSON.stringify(corpo),
      })
      const texto = await r.text()
      return {
        status: r.status,
        corpo: texto ? JSON.parse(texto) : undefined,
        cabecalhos: r.headers,
      }
    },
    fechar: () => new Promise<void>((r) => servidor.close(() => r())),
  }
}

export function ouro(nome: string) {
  return JSON.parse(readFileSync(join(AQUI, '..', '..', 'motor', 'ouro', `${nome}.json`), 'utf-8'))
}
