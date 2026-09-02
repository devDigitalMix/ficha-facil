// Avaliador de condição.
//
// A regra que dá sentido a esta peça: **predicado desconhecido é erro, nunca falso.**
// Tratar o que não se conhece como falso é exatamente o defeito que a fase 13 matou
// no dado — um efeito que nunca dispara e ninguém percebe. Aqui ele volta a ser
// possível se o motor for permissivo, então o motor não é permissivo.

import type { Condicao, Comparacao, Contexto } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { avaliar } from './formula.ts'

const OPERADORES_LOGICOS = ['todas', 'alguma', 'nao']
const COMPARADORES: Record<string, (a: number, b: number) => boolean> = {
  eq: (a, b) => a === b,
  ne: (a, b) => a !== b,
  lt: (a, b) => a < b,
  lte: (a, b) => a <= b,
  gt: (a, b) => a > b,
  gte: (a, b) => a >= b,
}

export type Vocabulario = {
  predicados: string[]
  familias_de_predicado: Record<string, string | null>
  operadores_logicos: string[]
  operadores_de_comparacao: string[]
}

/** Predicados que o motor sabe decidir sozinho, a partir do contexto. */
function decidirPeloContexto(p: string, ctx: Contexto): boolean | undefined {
  const ativos = new Set(ctx.predicados_ativos ?? [])
  if (ativos.has(p)) return true

  // proficiente_em:pericia:<id> — a proficiência está no contexto, não numa flag
  if (p.startsWith('proficiente_em:pericia:')) {
    const pericia = p.slice('proficiente_em:pericia:'.length)
    return (ctx.proficiencias?.pericias ?? []).includes(pericia)
  }
  if (p.startsWith('proficiente_em:salvaguarda:')) {
    const atr = p.slice('proficiente_em:salvaguarda:'.length)
    return (ctx.proficiencias?.salvaguardas ?? []).includes(atr)
  }
  return undefined
}

/**
 * Avalia uma condição.
 *
 * `vocabulario` é a lista fechada da fase 13. Quando ela é passada, um predicado
 * fora dela é erro de motor — o mesmo que o validador cobra do dado.
 */
export function condicaoVale(
  c: Condicao | undefined,
  ctx: Contexto,
  vocabulario?: Vocabulario,
): boolean {
  if (c === undefined) return true

  if (typeof c === 'string') {
    const decidido = decidirPeloContexto(c, ctx)
    if (decidido !== undefined) return decidido
    if (vocabulario && !predicadoDeclarado(c, vocabulario)) {
      throw new ErroDoMotor(`predicado não declarado no vocabulário: '${c}'`)
    }
    // Declarado, mas o contexto não o afirma: é falso, e isso é uma resposta,
    // não um silêncio — o predicado existe e simplesmente não vale agora.
    return false
  }

  if (Array.isArray(c)) return c.every((x) => condicaoVale(x, ctx, vocabulario))

  if ('comparar' in c) return compararVale(c as Comparacao, ctx, vocabulario)

  const chaves = Object.keys(c)
  if (chaves.length !== 1) {
    throw new ErroDoMotor(
      `condição composta tem de ter UM operador por objeto; veio ${JSON.stringify(chaves)}`,
    )
  }
  const [op] = chaves
  if (!OPERADORES_LOGICOS.includes(op)) {
    throw new ErroDoMotor(`operador lógico desconhecido: '${op}'`)
  }
  const v = (c as Record<string, unknown>)[op]
  if (op === 'nao') return !condicaoVale(v as Condicao, ctx, vocabulario)
  const lista = v as Condicao[]
  return op === 'todas'
    ? lista.every((x) => condicaoVale(x, ctx, vocabulario))
    : lista.some((x) => condicaoVale(x, ctx, vocabulario))
}

function predicadoDeclarado(p: string, v: Vocabulario): boolean {
  if (v.predicados.includes(p)) return true
  const prefixo = p.split(':')[0]
  return prefixo in v.familias_de_predicado
}

function compararVale(c: Comparacao, ctx: Contexto, vocabulario?: Vocabulario): boolean {
  const cmp = COMPARADORES[c.op]
  if (!cmp) throw new ErroDoMotor(`operador de comparação desconhecido: '${c.op}'`)
  const esq = avaliar(c.comparar, ctx, vocabulario)
  const dir = avaliar(c.com, ctx, vocabulario)
  if (esq.dados.length || dir.dados.length) {
    throw new ErroDoMotor('comparação com dado não rolado: o motor é puro e não joga dado')
  }
  return cmp(esq.valor, dir.valor)
}
