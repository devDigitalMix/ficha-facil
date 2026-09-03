// Contas: o usuário, a senha e o token de sessão.
//
// Tudo com `node:crypto`, sem dependência nova. Três decisões que valem estar
// escritas, porque são o tipo de coisa que se erra por conveniência:
//
// 1. **A senha nunca é guardada** — só o hash scrypt, com sal próprio por usuário.
//    scrypt é deliberadamente caro em memória, que é o que torna força bruta ruim.
// 2. **A comparação é em tempo constante** (`timingSafeEqual`). Comparar hash com
//    `===` vaza, pelo tempo de resposta, quantos bytes iniciais bateram.
// 3. **O token é assinado, não criptografado.** Ele diz quem é o usuário e até
//    quando vale, em claro; o que a assinatura impede é forjar ou alterar. Nada
//    secreto entra nele.
//
// O token é sem estado: não há coleção de sessões, e sair de uma sessão específica
// não é possível. Para o uso de hoje — uma pessoa, um cliente — isso basta e evita
// uma coleção e um índice. Se um dia precisar revogar (senha vazada, aparelho
// perdido), o caminho é guardar um `token_valido_a_partir_de` no usuário e recusar
// token emitido antes: uma linha aqui, sem coleção nova.

import { createHmac, randomBytes, scryptSync, timingSafeEqual } from 'node:crypto'
import { ErroHttp } from './erros.ts'

export type Usuario = {
  id: string
  /** Sempre em minúsculas: quem digita `Joao@` na segunda vez é a mesma pessoa. */
  email: string
  senha_hash: string
  criado_em: string
  ultimo_login?: string
}

/** O que trafega para o cliente: o hash nunca sai daqui. */
export type UsuarioPublico = Pick<Usuario, 'id' | 'email' | 'criado_em'>

export const paraOCliente = (u: Usuario): UsuarioPublico =>
  ({ id: u.id, email: u.email, criado_em: u.criado_em })

// ------------------------------------------------------------------ e-mail

export function normalizarEmail(bruto: unknown): string {
  if (typeof bruto !== 'string') throw new ErroHttp(400, 'pedido_invalido', 'e-mail é obrigatório')
  const email = bruto.trim().toLowerCase()
  // Deliberadamente frouxo. Validar e-mail por expressão regular é um clássico de
  // recusar endereço legítimo; quem confere de verdade é o envio da mensagem, que
  // ainda não existe. O que importa aqui é ter arroba, ter os dois lados, e não ter
  // espaço no meio.
  if (!/^[^\s@]+@[^\s@]+$/.test(email)) {
    throw new ErroHttp(400, 'pedido_invalido', 'e-mail não parece um e-mail')
  }
  return email
}

/**
 * O mínimo de senha.
 *
 * Comprimento, e só. Regra de "uma maiúscula e um símbolo" empurra a pessoa para
 * `Senha1!` — curta, previsível e pior do que uma frase longa. O que protege é
 * tamanho, e é o que se cobra.
 */
export const TAMANHO_MINIMO_DA_SENHA = 10

export function conferirTamanhoDaSenha(bruta: unknown): string {
  if (typeof bruta !== 'string') throw new ErroHttp(400, 'pedido_invalido', 'senha é obrigatória')
  if (bruta.length < TAMANHO_MINIMO_DA_SENHA) {
    throw new ErroHttp(400, 'pedido_invalido',
      `a senha precisa de pelo menos ${TAMANHO_MINIMO_DA_SENHA} caracteres`)
  }
  return bruta
}

// -------------------------------------------------------------------- senha

const N = 16384, r = 8, p = 1, TAMANHO = 64

/** `scrypt$N$r$p$sal$hash`, tudo em base64url. O formato guarda os parâmetros junto
 *  do hash, para que aumentá-los depois não invalide as senhas já gravadas. */
export function hashDeSenha(senha: string): string {
  const sal = randomBytes(16)
  const hash = scryptSync(senha.normalize('NFKC'), sal, TAMANHO, { N, r, p })
  return ['scrypt', N, r, p, sal.toString('base64url'), hash.toString('base64url')].join('$')
}

export function senhaConfere(senha: string, guardado: string): boolean {
  const partes = guardado.split('$')
  if (partes.length !== 6 || partes[0] !== 'scrypt') return false
  const [, n, rr, pp, sal, hash] = partes
  const esperado = Buffer.from(hash, 'base64url')
  const obtido = scryptSync(senha.normalize('NFKC'), Buffer.from(sal, 'base64url'),
    esperado.length, { N: Number(n), r: Number(rr), p: Number(pp) })
  // tempo constante: `===` vazaria, pelo tempo, quantos bytes iniciais bateram
  return obtido.length === esperado.length && timingSafeEqual(obtido, esperado)
}

// -------------------------------------------------------------------- token

type Conteudo = { u: string; exp: number }

const b64 = (o: unknown) => Buffer.from(JSON.stringify(o), 'utf-8').toString('base64url')

const assinar = (corpo: string, segredo: string) =>
  createHmac('sha256', segredo).update(corpo).digest('base64url')

export function criarToken(usuarioId: string, segredo: string, horas: number): string {
  const corpo = b64({ u: usuarioId, exp: Date.now() + horas * 3600_000 } satisfies Conteudo)
  return `${corpo}.${assinar(corpo, segredo)}`
}

/**
 * Devolve o id do usuário, ou `undefined` se o token não presta.
 *
 * Não distingue "assinatura errada" de "expirado" para quem chama: os dois são
 * "entre de novo", e detalhar ajuda mais quem está atacando do que quem esqueceu.
 */
export function lerToken(token: string, segredo: string): string | undefined {
  const [corpo, assinatura] = token.split('.')
  if (!corpo || !assinatura) return undefined

  const esperada = Buffer.from(assinar(corpo, segredo), 'base64url')
  const recebida = Buffer.from(assinatura, 'base64url')
  if (esperada.length !== recebida.length || !timingSafeEqual(esperada, recebida)) return undefined

  try {
    const { u, exp } = JSON.parse(Buffer.from(corpo, 'base64url').toString('utf-8')) as Conteudo
    if (typeof u !== 'string' || typeof exp !== 'number' || Date.now() >= exp) return undefined
    return u
  } catch {
    return undefined
  }
}
