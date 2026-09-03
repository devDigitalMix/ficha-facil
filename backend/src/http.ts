// Roteador mínimo sobre node:http. Zero dependências, como o motor.
//
// Um framework resolveria isto em menos linhas, mas traria árvore de dependência para
// um serviço que tem sete rotas. O que existe aqui é o que as sete rotas usam.

import type { IncomingMessage, ServerResponse } from 'node:http'
import { ErroHttp, pedidoInvalido } from './erros.ts'
import { ErroDoMotor } from '../../motor/src/tipos.ts'

export type Pedido = {
  metodo: string
  caminho: string
  parametros: Record<string, string>
  consulta: URLSearchParams
  corpo: unknown
  cabecalhos: IncomingMessage['headers']
}

export type Resposta = {
  status?: number
  corpo?: unknown
  cabecalhos?: Record<string, string>
}

type Manipulador = (p: Pedido) => Resposta | Promise<Resposta>
type Rota = { metodo: string; partes: string[]; manipulador: Manipulador }

const LIMITE_DO_CORPO = 1024 * 1024 // 1 MB: uma construção grande não passa de alguns KB

export class Roteador {
  rotas: Rota[] = []

  rota(metodo: string, molde: string, manipulador: Manipulador): this {
    this.rotas.push({ metodo, partes: molde.split('/').filter(Boolean), manipulador })
    return this
  }

  casar(metodo: string, caminho: string) {
    const partes = caminho.split('/').filter(Boolean)
    // guarda o que casou o caminho mas não o método, para responder 405 em vez de 404
    let caminhoExiste = false
    for (const r of this.rotas) {
      if (r.partes.length !== partes.length) continue
      const parametros: Record<string, string> = {}
      let bate = true
      for (let i = 0; i < r.partes.length; i++) {
        const molde = r.partes[i]
        if (molde.startsWith(':')) parametros[molde.slice(1)] = decodeURIComponent(partes[i])
        else if (molde !== partes[i]) { bate = false; break }
      }
      if (!bate) continue
      caminhoExiste = true
      if (r.metodo === metodo) return { rota: r, parametros }
    }
    return { rota: undefined, parametros: {}, caminhoExiste }
  }

  async atender(req: IncomingMessage, res: ServerResponse): Promise<void> {
    const url = new URL(req.url ?? '/', 'http://localhost')
    try {
      const { rota, parametros, caminhoExiste } = this.casar(req.method ?? 'GET', url.pathname)
      if (!rota) {
        if (caminhoExiste) throw new ErroHttp(405, 'metodo_nao_permitido',
          `${req.method} não é aceito em ${url.pathname}`)
        throw new ErroHttp(404, 'nao_encontrado', `rota inexistente: ${url.pathname}`)
      }
      const corpo = await lerCorpo(req)
      const r = await rota.manipulador({
        metodo: req.method ?? 'GET',
        caminho: url.pathname,
        parametros,
        consulta: url.searchParams,
        corpo,
        cabecalhos: req.headers,
      })
      responder(res, r)
    } catch (e) {
      responder(res, deErro(e))
    }
  }
}

async function lerCorpo(req: IncomingMessage): Promise<unknown> {
  if (req.method === 'GET' || req.method === 'HEAD') return undefined
  const pedacos: Buffer[] = []
  let tamanho = 0
  for await (const p of req) {
    tamanho += (p as Buffer).length
    if (tamanho > LIMITE_DO_CORPO) throw new ErroHttp(413, 'corpo_grande_demais',
      `o corpo passou de ${LIMITE_DO_CORPO} bytes`)
    pedacos.push(p as Buffer)
  }
  if (!pedacos.length) return undefined
  const texto = Buffer.concat(pedacos).toString('utf-8')
  try {
    return JSON.parse(texto)
  } catch {
    throw pedidoInvalido('o corpo não é JSON válido')
  }
}

function responder(res: ServerResponse, r: Resposta): void {
  const status = r.status ?? 200
  const cabecalhos: Record<string, string> = {
    'content-type': 'application/json; charset=utf-8',
    ...(r.cabecalhos ?? {}),
  }
  if (r.corpo === undefined || status === 304) {
    res.writeHead(status, cabecalhos)
    res.end()
    return
  }
  const texto = JSON.stringify(r.corpo)
  cabecalhos['content-length'] = String(Buffer.byteLength(texto))
  res.writeHead(status, cabecalhos)
  res.end(texto)
}

/**
 * Erro para resposta.
 *
 * O que o motor lança vira 422: a construção é sintaticamente válida e as regras é
 * que não fecham. O que não é reconhecido vira 500 — e nunca 200 com ficha inventada.
 */
export function deErro(e: unknown): Resposta {
  if (e instanceof ErroHttp) {
    return { status: e.status, corpo: { erro: e.codigo, mensagem: e.message, detalhe: e.detalhe } }
  }
  const mensagem = (e as Error)?.message ?? String(e)
  // `instanceof`, e não comparação de nome: nome é string e string se digita errado.
  // A primeira versão comparava `e.name === 'ErroDoMotor'` e nunca casava, porque a
  // classe não definia `name` — todo erro do motor saía como 500.
  if (e instanceof ErroDoMotor) {
    return { status: 422, corpo: { erro: 'motor_recusou', mensagem } }
  }
  return { status: 500, corpo: { erro: 'erro_interno', mensagem } }
}
