// Avaliador de fórmula.
//
// Fórmula no dataset é ÁRVORE, nunca string a parsear. Este arquivo é o que torna
// essa decisão de esquema útil: um interpretador pequeno, sem regex, sem eval.
//
// Duas coisas que ele NÃO faz, de propósito:
//   1. não joga dado — o motor é puro (PLANO-MOTOR §1). '1d20' sai simbólico, em
//      `dados`, e é assim que a ficha mostra "Iniciativa +3" e "dano 1d12 + 4";
//   2. não conhece id de conteúdo. 'mod:DES' ele resolve porque DES é atributo;
//      'nivel_classe:monge' porque a classe está no contexto. Nenhum nome de
//      classe, magia ou característica aparece neste código.

import type { Contexto, Formula, Operacao, Resultado, Termo } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { condicaoVale, type Vocabulario } from './condicao.ts'

const DADO = /^(\d*)d(\d+)$/

/** Os operadores são os declarados em catalogos/valores_derivados.json → operacoes. */
export const OPERADORES = [
  'soma', 'menos', 'mult', 'max', 'min',
  'div_arred_baixo', 'div_arred_cima',
  'soma_se', 'max_entre_calculos_de_base', 'menor_ou_igual',
] as const

export function modificadorDeAtributo(valor: number): number {
  return Math.floor((valor - 10) / 2)
}

function vazio(): Resultado {
  return { valor: 0, dados: [], parcelas: [] }
}

function juntar(a: Resultado, b: Resultado): Resultado {
  return {
    valor: a.valor + b.valor,
    dados: [...a.dados, ...b.dados],
    parcelas: [...a.parcelas, ...b.parcelas],
  }
}

/**
 * Resolve um termo folha.
 *
 * Termo desconhecido é ERRO. A tentação é devolver 0 e seguir — e aí uma ficha
 * sai com a CA errada e ninguém sabe por quê. O projeto inteiro é construído
 * sobre "chave inexistente é erro de build"; aqui vale o mesmo.
 */
function resolverTermo(t: string, ctx: Contexto): Resultado {
  // número literal, inclusive negativo
  if (/^-?\d+(\.\d+)?$/.test(t)) {
    return { valor: Number(t), dados: [], parcelas: [{ rotulo: t, valor: Number(t) }] }
  }

  // dado: fica simbólico
  if (DADO.test(t)) return { valor: 0, dados: [t], parcelas: [{ rotulo: t, valor: t }] }

  if (t.startsWith('mod:')) {
    let atr = t.slice(4)
    // o livro escreve "modificador do atributo de conjuração" porque ele muda de
    // classe para classe; quem diz qual é o dado, não este código
    if (atr === 'atributo_de_conjuracao') {
      const real = ctx.atributo_de_conjuracao
      if (!real) {
        throw new ErroDoMotor('a fórmula pede o atributo de conjuração e o personagem não conjura')
      }
      atr = real
    }
    const bruto = ctx.atributos?.[atr]
    if (bruto === undefined) throw new ErroDoMotor(`atributo ausente no contexto: '${atr}'`)
    const m = modificadorDeAtributo(bruto)
    return { valor: m, dados: [], parcelas: [{ rotulo: `${atr} ${bruto >= 0 ? '' : ''}`.trim() || atr, valor: m }] }
  }

  if (t === 'prof' || t === 'bonus_de_proficiencia') {
    const bp = bonusDeProficiencia(ctx)
    return { valor: bp, dados: [], parcelas: [{ rotulo: 'Bônus de Proficiência', valor: bp }] }
  }

  if (t === 'nivel_do_personagem') {
    return {
      valor: ctx.nivel_do_personagem,
      dados: [],
      parcelas: [{ rotulo: 'nível', valor: ctx.nivel_do_personagem }],
    }
  }

  if (t.startsWith('nivel_classe:')) {
    const classe = t.slice('nivel_classe:'.length)
    const n = ctx.niveis_por_classe?.[classe]
    if (n === undefined) throw new ErroDoMotor(`o personagem não tem níveis em '${classe}'`)
    return { valor: n, dados: [], parcelas: [{ rotulo: `nível de ${classe}`, valor: n }] }
  }

  if (t.startsWith('coluna:')) {
    const chave = t.slice('coluna:'.length)
    const v = ctx.colunas?.[chave]
    if (v === undefined) throw new ErroDoMotor(`coluna ausente no contexto: '${chave}'`)
    if (typeof v === 'string') {
      // coluna de dado (o dado de Artes Marciais, o de Superioridade…)
      if (!DADO.test(v)) throw new ErroDoMotor(`coluna '${chave}' não é número nem dado: '${v}'`)
      return { valor: 0, dados: [v], parcelas: [{ rotulo: chave, valor: v }] }
    }
    return { valor: v, dados: [], parcelas: [{ rotulo: chave, valor: v }] }
  }

  if (t === 'dado_de_vida_da_classe') {
    const v = ctx.dado_de_vida_da_classe
    if (v === undefined) throw new ErroDoMotor('dado de vida da classe ausente no contexto')
    return { valor: v, dados: [], parcelas: [{ rotulo: 'Dado de Vida (valor máximo)', valor: v }] }
  }

  if (ctx.extras_dados && t in ctx.extras_dados) {
    const d = ctx.extras_dados[t]
    return { valor: 0, dados: [d], parcelas: [{ rotulo: t, valor: d }] }
  }

  if (ctx.extras && t in ctx.extras) {
    const v = ctx.extras[t]
    return { valor: v, dados: [], parcelas: [{ rotulo: t, valor: v }] }
  }

  throw new ErroDoMotor(`termo de fórmula desconhecido: '${t}'`)
}

export function bonusDeProficiencia(ctx: Contexto): number {
  // 2 no nível 1, subindo 1 a cada quatro níveis (p. 22). A tabela do dataset diz
  // o mesmo; a conta fica aqui para o motor não depender de tabela para algo que
  // é uma regra fechada e universal.
  return 2 + Math.floor((ctx.nivel_do_personagem - 1) / 4)
}

export function avaliar(f: Formula, ctx: Contexto, vocabulario?: Vocabulario): Resultado {
  if (Array.isArray(f)) {
    return f.map((t) => avaliarTermo(t, ctx, vocabulario)).reduce(juntar, vazio())
  }
  return avaliarTermo(f, ctx, vocabulario)
}

function avaliarTermo(t: Termo, ctx: Contexto, vocabulario?: Vocabulario): Resultado {
  if (typeof t === 'number') {
    return { valor: t, dados: [], parcelas: [{ rotulo: String(t), valor: t }] }
  }
  if (typeof t === 'string') return resolverTermo(t, ctx)
  return aplicarOperacao(t, ctx, vocabulario)
}

function aplicarOperacao(o: Operacao, ctx: Contexto, vocabulario?: Vocabulario): Resultado {
  if (!OPERADORES.includes(o.op as (typeof OPERADORES)[number])) {
    throw new ErroDoMotor(`operação desconhecida: '${o.op}'`)
  }

  if (o.op === 'soma_se') {
    if (!condicaoVale(o.condicao, ctx, vocabulario)) return vazio()
    return avaliar(o.args ?? [], ctx, vocabulario)
  }

  if (o.op === 'max_entre_calculos_de_base') {
    return maiorCalculoDeBase(ctx, vocabulario)
  }

  const partes = (o.args ?? []).map((a) => avaliarTermo(a, ctx, vocabulario))
  const numeros = partes.map((p) => p.valor)
  const dados = partes.flatMap((p) => p.dados)
  const parcelas = partes.flatMap((p) => p.parcelas)

  const so = (v: number): Resultado => ({ valor: v, dados, parcelas })

  switch (o.op) {
    case 'soma':
      return so(numeros.reduce((a, b) => a + b, 0))
    case 'menos':
      return so(numeros.slice(1).reduce((a, b) => a - b, numeros[0] ?? 0))
    case 'mult':
      return so(numeros.reduce((a, b) => a * b, 1))
    case 'max':
      return so(Math.max(...numeros))
    case 'min':
      return so(Math.min(...numeros))
    case 'div_arred_baixo':
      exigirDois(o, numeros)
      return so(Math.floor(numeros[0] / numeros[1]))
    case 'div_arred_cima':
      exigirDois(o, numeros)
      return so(Math.ceil(numeros[0] / numeros[1]))
    case 'menor_ou_igual':
      // Sobrevivente da fase 13: nenhuma fórmula usa mais, porque comparação virou
      // {comparar, op, com}. Fica implementado enquanto estiver declarado.
      exigirDois(o, numeros)
      return so(numeros[0] <= numeros[1] ? 1 : 0)
    default:
      throw new ErroDoMotor(`operação declarada mas não implementada: '${o.op}'`)
  }
}

function exigirDois(o: Operacao, n: number[]): void {
  if (n.length !== 2) {
    throw new ErroDoMotor(`'${o.op}' tem aridade 2; veio com ${n.length} argumento(s)`)
  }
}

/**
 * Cálculos de CA base CONCORREM: o jogador fica com um, eles não se somam
 * (Ap. C, "Classe de Armadura", p. 363). É o caso que o Monge e o Bárbaro
 * quebram se o motor somar.
 */
function maiorCalculoDeBase(ctx: Contexto, vocabulario?: Vocabulario): Resultado {
  const calculos = ctx.calculos_de_ca_base ?? []
  if (!calculos.length) throw new ErroDoMotor('nenhum cálculo de CA base no contexto')
  const avaliados = calculos.map((c) => ({ id: c.id, r: avaliar(c.formula, ctx, vocabulario) }))
  const vencedor = avaliados.reduce((a, b) => (b.r.valor > a.r.valor ? b : a))
  return {
    valor: vencedor.r.valor,
    dados: vencedor.r.dados,
    parcelas: [
      ...vencedor.r.parcelas,
      { rotulo: 'cálculo de base usado', valor: vencedor.id },
    ],
  }
}
