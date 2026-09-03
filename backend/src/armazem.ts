// Onde os personagens ficam.
//
// Um arquivo JSON por personagem, num diretório. Não é banco porque ainda não
// precisa ser: o compêndio é estático e o personagem é um documento pequeno que se
// lê inteiro. A interface existe para que trocar por banco depois seja trocar esta
// peça, e não reescrever o backend.
//
// Escrita é atômica (arquivo temporário + rename): um processo morto no meio de uma
// gravação deixa o personagem antigo intacto, nunca meio arquivo.

import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { randomUUID } from 'node:crypto'
import type { Personagem } from './personagem.ts'

export interface Armazem {
  criar(p: Omit<Personagem, 'id'>): Personagem
  ler(id: string): Personagem | undefined
  gravar(p: Personagem): Personagem
  listar(): Personagem[]
  apagar(id: string): boolean
}

const seguro = (id: string) => /^[a-zA-Z0-9_-]{1,64}$/.test(id)

export class ArmazemEmArquivos implements Armazem {
  raiz: string

  constructor(raiz: string) {
    this.raiz = raiz
    mkdirSync(raiz, { recursive: true })
  }

  caminho(id: string): string {
    // id vem da URL: sem esta checagem, '../../etc/passwd' seria um id válido
    if (!seguro(id)) throw new Error(`id de personagem inválido: '${id}'`)
    return join(this.raiz, `${id}.json`)
  }

  criar(p: Omit<Personagem, 'id'>): Personagem {
    const completo = { ...p, id: randomUUID() } as Personagem
    this.gravar(completo)
    return completo
  }

  ler(id: string): Personagem | undefined {
    if (!seguro(id)) return undefined
    const caminho = this.caminho(id)
    if (!existsSync(caminho)) return undefined
    return JSON.parse(readFileSync(caminho, 'utf-8')) as Personagem
  }

  gravar(p: Personagem): Personagem {
    const caminho = this.caminho(p.id)
    const temporario = `${caminho}.${process.pid}.tmp`
    writeFileSync(temporario, JSON.stringify(p, null, 2), 'utf-8')
    renameSync(temporario, caminho)
    return p
  }

  listar(): Personagem[] {
    if (!existsSync(this.raiz)) return []
    const todos = readdirSync(this.raiz)
      .filter((n) => n.endsWith('.json'))
      .map((n) => JSON.parse(readFileSync(join(this.raiz, n), 'utf-8')) as Personagem)
    // "Meus personagens", ordenado por último acesso — o mais recente no topo
    return todos.sort((a, b) => (a.ultimo_acesso < b.ultimo_acesso ? 1 : -1))
  }

  apagar(id: string): boolean {
    const caminho = this.caminho(id)
    if (!existsSync(caminho)) return false
    rmSync(caminho)
    return true
  }
}

/** Para os testes: some quando o processo acaba, e não toca em disco. */
export class ArmazemNaMemoria implements Armazem {
  mapa = new Map<string, Personagem>()

  criar(p: Omit<Personagem, 'id'>): Personagem {
    const completo = { ...p, id: randomUUID() } as Personagem
    this.mapa.set(completo.id, completo)
    return completo
  }

  ler(id: string) {
    const p = this.mapa.get(id)
    return p ? (JSON.parse(JSON.stringify(p)) as Personagem) : undefined
  }

  gravar(p: Personagem) {
    this.mapa.set(p.id, JSON.parse(JSON.stringify(p)) as Personagem)
    return p
  }

  listar() {
    return [...this.mapa.values()].sort((a, b) => (a.ultimo_acesso < b.ultimo_acesso ? 1 : -1))
  }

  apagar(id: string) {
    return this.mapa.delete(id)
  }
}
