// Sobe o servidor numa porta livre e devolve um cliente curto.
// Cada teste tem o seu, com armazém em memória: nada em disco, nada compartilhado.

import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { criarServidor } from '../src/servidor.ts'
import { ArmazemNaMemoria, type Armazem } from '../src/armazem.ts'
import { UsuariosNaMemoria, type ArmazemDeUsuarios } from '../src/usuarios.ts'
import { EventosNaMemoria, type ArmazemDeEventos } from '../src/eventos.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))

export const SEGREDO_DE_TESTE = 'segredo-de-teste-nao-usar-em-lugar-nenhum'
export const SENHA_DE_TESTE = 'uma senha longa o bastante'

export type Cliente = {
  base: string
  armazem: Armazem
  usuarios: ArmazemDeUsuarios
  eventos: ArmazemDeEventos
  /** O dono que os pedidos usam por padrão, já autenticado. */
  usuario: { id: string; email: string }
  token: string
  /** Cria outra conta e devolve o token dela — para os testes de isolamento. */
  outroUsuario(email?: string): Promise<{ id: string; token: string }>
  pedir(metodo: string, caminho: string, corpo?: unknown, cabecalhos?: Record<string, string>):
    Promise<{ status: number; corpo: any; cabecalhos: Headers }>
  fechar(): Promise<void>
}

export async function subir(): Promise<Cliente> {
  const armazem = new ArmazemNaMemoria()
  const usuarios = new UsuariosNaMemoria()
  const eventos = new EventosNaMemoria()
  const servidor = criarServidor(armazem, usuarios, eventos, { segredo: SEGREDO_DE_TESTE, horas: 1 })
  await new Promise<void>((r) => servidor.listen(0, r))
  const porta = (servidor.address() as { port: number }).port
  const base = `http://127.0.0.1:${porta}`

  const cru = async (metodo: string, caminho: string, corpo?: unknown,
                     cabecalhos: Record<string, string> = {}) => {
    const r = await fetch(base + caminho, {
      method: metodo,
      headers: { 'content-type': 'application/json', ...cabecalhos },
      body: corpo === undefined ? undefined : JSON.stringify(corpo),
    })
    const texto = await r.text()
    return { status: r.status, corpo: texto ? JSON.parse(texto) : undefined, cabecalhos: r.headers }
  }

  // Toda rota de personagem exige dono, então o cliente já nasce com um. Os testes
  // que querem provar o contrário passam o cabeçalho na mão.
  const conta = await cru('POST', '/contas',
    { email: 'jogador@exemplo.test', senha: SENHA_DE_TESTE })
  const token = conta.corpo.token as string

  return {
    base,
    armazem,
    usuarios,
    eventos,
    usuario: conta.corpo.usuario,
    token,
    async outroUsuario(email = `outro-${Math.random().toString(36).slice(2)}@exemplo.test`) {
      const r = await cru('POST', '/contas', { email, senha: SENHA_DE_TESTE })
      return { id: r.corpo.usuario.id as string, token: r.corpo.token as string }
    },
    async pedir(metodo, caminho, corpo, cabecalhos = {}) {
      const r = await fetch(base + caminho, {
        method: metodo,
        headers: {
          'content-type': 'application/json',
          // O teste que quer pedir SEM token manda `authorization: ''`.
          authorization: `Bearer ${token}`,
          ...cabecalhos,
        },
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
