// Onde os usuários ficam.
//
// Mesma forma do `Armazem` de personagens: interface, e três implementações que o
// resto do backend não distingue. A busca por e-mail é a única consulta que existe
// além da leitura por id, e é a que o login usa.

import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { randomUUID } from 'node:crypto'
import type { Usuario } from './usuario.ts'

export interface ArmazemDeUsuarios {
  criar(u: Omit<Usuario, 'id'>): Promise<Usuario>
  ler(id: string): Promise<Usuario | undefined>
  porEmail(email: string): Promise<Usuario | undefined>
  gravar(u: Usuario): Promise<Usuario>
}

/** Dois cadastros com o mesmo e-mail. Vira 409, não 500. */
export class EmailJaUsado extends Error {
  constructor(email: string) {
    super(`já existe conta para ${email}`)
    this.name = 'EmailJaUsado'
  }
}

export class UsuariosNaMemoria implements ArmazemDeUsuarios {
  mapa = new Map<string, Usuario>()

  async criar(u: Omit<Usuario, 'id'>): Promise<Usuario> {
    if (await this.porEmail(u.email)) throw new EmailJaUsado(u.email)
    const completo = { ...u, id: randomUUID() }
    this.mapa.set(completo.id, { ...completo })
    return completo
  }

  async ler(id: string) {
    const u = this.mapa.get(id)
    return u ? { ...u } : undefined
  }

  async porEmail(email: string) {
    for (const u of this.mapa.values()) if (u.email === email) return { ...u }
    return undefined
  }

  async gravar(u: Usuario) {
    this.mapa.set(u.id, { ...u })
    return u
  }
}

/** Um JSON por usuário, para rodar sem banco. Mesma gravação atômica dos personagens. */
export class UsuariosEmArquivos implements ArmazemDeUsuarios {
  raiz: string

  constructor(raiz: string) {
    this.raiz = raiz
    mkdirSync(raiz, { recursive: true })
  }

  caminho(id: string): string {
    if (!/^[a-zA-Z0-9_-]{1,64}$/.test(id)) throw new Error(`id de usuário inválido: '${id}'`)
    return join(this.raiz, `${id}.json`)
  }

  todos(): Usuario[] {
    if (!existsSync(this.raiz)) return []
    return readdirSync(this.raiz)
      .filter((n) => n.endsWith('.json'))
      .map((n) => JSON.parse(readFileSync(join(this.raiz, n), 'utf-8')) as Usuario)
  }

  async criar(u: Omit<Usuario, 'id'>): Promise<Usuario> {
    if (await this.porEmail(u.email)) throw new EmailJaUsado(u.email)
    const completo = { ...u, id: randomUUID() }
    await this.gravar(completo)
    return completo
  }

  async ler(id: string): Promise<Usuario | undefined> {
    if (!/^[a-zA-Z0-9_-]{1,64}$/.test(id)) return undefined
    const caminho = this.caminho(id)
    if (!existsSync(caminho)) return undefined
    return JSON.parse(readFileSync(caminho, 'utf-8')) as Usuario
  }

  async porEmail(email: string): Promise<Usuario | undefined> {
    return this.todos().find((u) => u.email === email)
  }

  async gravar(u: Usuario): Promise<Usuario> {
    const caminho = this.caminho(u.id)
    const temporario = `${caminho}.${process.pid}.tmp`
    writeFileSync(temporario, JSON.stringify(u, null, 2), 'utf-8')
    renameSync(temporario, caminho)
    return u
  }
}
