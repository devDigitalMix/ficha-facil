// Onde os personagens ficam.
//
// A interface existe para que trocar o lugar de guardar seja trocar esta peça, e não
// reescrever o backend. São três implementações: arquivo (rodar sem banco), memória
// (testes) e Mongo (`mongo.ts`, produção).
//
// **Por que os métodos devolvem Promise.** A primeira versão era síncrona, porque
// arquivo e memória são síncronos. Mongo não é — e fingir que é significaria bloquear
// o laço de eventos ou mentir no tipo. O roteador já aceitava manipulador assíncrono
// (`Manipulador = (p) => Resposta | Promise<Resposta>`), então o custo foi um `await`
// em cada chamada, e nenhuma mudança de desenho.

import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { randomUUID } from 'node:crypto'
import type { Personagem } from './personagem.ts'

export interface Armazem {
  criar(p: Omit<Personagem, 'id'>): Promise<Personagem>
  ler(id: string): Promise<Personagem | undefined>
  gravar(p: Personagem): Promise<Personagem>
  /** Só os do dono: listar sem dono seria listar os de todo mundo. */
  listar(usuarioId: string): Promise<Personagem[]>
  apagar(id: string): Promise<boolean>
  /** Fecha conexão, quando houver. Arquivo e memória não têm o que fechar. */
  fechar?(): Promise<void>
}

const seguro = (id: string) => /^[a-zA-Z0-9_-]{1,64}$/.test(id)

/** "Meus personagens", ordenado por último acesso — o mais recente no topo. */
export function porUltimoAcesso(a: Personagem, b: Personagem): number {
  return a.ultimo_acesso < b.ultimo_acesso ? 1 : -1
}

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

  async criar(p: Omit<Personagem, 'id'>): Promise<Personagem> {
    const completo = { ...p, id: randomUUID() } as Personagem
    await this.gravar(completo)
    return completo
  }

  async ler(id: string): Promise<Personagem | undefined> {
    if (!seguro(id)) return undefined
    const caminho = this.caminho(id)
    if (!existsSync(caminho)) return undefined
    return JSON.parse(readFileSync(caminho, 'utf-8')) as Personagem
  }

  async gravar(p: Personagem): Promise<Personagem> {
    const caminho = this.caminho(p.id)
    // gravação atômica: um processo morto no meio deixa o arquivo antigo intacto,
    // nunca meio arquivo
    const temporario = `${caminho}.${process.pid}.tmp`
    writeFileSync(temporario, JSON.stringify(p, null, 2), 'utf-8')
    renameSync(temporario, caminho)
    return p
  }

  async listar(usuarioId: string): Promise<Personagem[]> {
    if (!existsSync(this.raiz)) return []
    return readdirSync(this.raiz)
      .filter((n) => n.endsWith('.json'))
      .map((n) => JSON.parse(readFileSync(join(this.raiz, n), 'utf-8')) as Personagem)
      .filter((p) => p.usuario_id === usuarioId)
      .sort(porUltimoAcesso)
  }

  async apagar(id: string): Promise<boolean> {
    const caminho = this.caminho(id)
    if (!existsSync(caminho)) return false
    rmSync(caminho)
    return true
  }
}

/** Para os testes: some quando o processo acaba, e não toca em disco. */
export class ArmazemNaMemoria implements Armazem {
  mapa = new Map<string, Personagem>()

  async criar(p: Omit<Personagem, 'id'>): Promise<Personagem> {
    const completo = { ...p, id: randomUUID() } as Personagem
    this.mapa.set(completo.id, JSON.parse(JSON.stringify(completo)) as Personagem)
    return completo
  }

  async ler(id: string): Promise<Personagem | undefined> {
    const p = this.mapa.get(id)
    return p ? (JSON.parse(JSON.stringify(p)) as Personagem) : undefined
  }

  async gravar(p: Personagem): Promise<Personagem> {
    this.mapa.set(p.id, JSON.parse(JSON.stringify(p)) as Personagem)
    return p
  }

  async listar(usuarioId: string): Promise<Personagem[]> {
    return [...this.mapa.values()].filter((p) => p.usuario_id === usuarioId).sort(porUltimoAcesso)
  }

  async apagar(id: string): Promise<boolean> {
    return this.mapa.delete(id)
  }
}
