// Erros do backend, com o status que cada um vira.
//
// A regra do motor — "desconhecido é erro, nunca zero" — vale aqui na forma HTTP:
// pedido malformado é 400, personagem que não existe é 404, e construção que o motor
// recusa é 422. O que NUNCA acontece é responder 200 com uma ficha inventada.

export class ErroHttp extends Error {
  // Campos declarados na mão: o Node roda TypeScript apagando os tipos, e nesse modo
  // "parameter property" (o `private` no argumento do construtor) não existe.
  status: number
  codigo: string
  detalhe?: unknown

  constructor(status: number, codigo: string, mensagem: string, detalhe?: unknown) {
    super(mensagem)
    this.name = 'ErroHttp'
    this.status = status
    this.codigo = codigo
    this.detalhe = detalhe
  }
}

export const naoEncontrado = (o: string) =>
  new ErroHttp(404, 'nao_encontrado', `não existe: ${o}`)

export const pedidoInvalido = (msg: string, detalhe?: unknown) =>
  new ErroHttp(400, 'pedido_invalido', msg, detalhe)

/** Construção que o motor recusa: a sintaxe está certa, as regras é que não fecham. */
export const construcaoInvalida = (msg: string, detalhe?: unknown) =>
  new ErroHttp(422, 'construcao_invalida', msg, detalhe)
