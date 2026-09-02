// A ficha estática: o que o passo 2 do PLANO-MOTOR fecha.
//
// Entra um Contexto, sai a parte da ficha que não depende de escolha em aberto nem
// de efeito ainda não coletado: modificadores, Bônus de Proficiência, CA, Pontos de
// Vida máximos, Iniciativa, Percepção Passiva, salvaguardas, testes de perícia e
// Deslocamento. Cada número vem com a proveniência, porque é o que o app promete
// mostrar ("CA 17 = 10 + 3 DES + 4 SAB").
//
// O que este arquivo NÃO faz: coletar efeito (passo 3) e resolver escolha (passo 4).
// Enquanto isso não existe, o Contexto vem pronto — dos personagens de ouro.

import type { Contexto, Resultado } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { avaliar, bonusDeProficiencia, modificadorDeAtributo } from './formula.ts'
import { calcular } from './derivados.ts'
import { condicaoVale, type Vocabulario } from './condicao.ts'
import { separar, ataqueComArma, ataqueDesarmado, type Ataque } from './equipamento.ts'

const ATRIBUTOS = ['FOR', 'DES', 'CON', 'INT', 'SAB', 'CAR']

export type Ficha = {
  modificadores: Record<string, number>
  bonus_de_proficiencia: number
  classe_de_armadura: Resultado
  pontos_de_vida_maximos: Resultado
  iniciativa: Resultado
  percepcao_passiva: Resultado
  salvaguardas: Record<string, number>
  testes_de_pericia: Record<string, number>
  deslocamento_m: number
  /** O Ataque Desarmado sempre entra; as armas equipadas, se houver. */
  ataques: Ataque[]
  /** Só para quem conjura. Fora isso, ausente — e não zero. */
  conjuracao?: {
    atributo: string
    cd_para_evitar_sua_magia: Resultado
    jogada_de_ataque_magico: Resultado
    /** Espaços por círculo, do círculo 1 para cima; zero não entra. */
    espacos: Record<number, number>
    magias_preparadas: number
    truques: number
  }
}

export function montarFicha(
  ctx: Contexto,
  vocabulario?: Vocabulario,
  equipamentoEquipado: string[] = [],
): Ficha {
  const bp = bonusDeProficiencia(ctx)

  const modificadores: Record<string, number> = {}
  for (const a of ATRIBUTOS) {
    const v = ctx.atributos?.[a]
    if (v === undefined) throw new ErroDoMotor(`atributo ausente no contexto: '${a}'`)
    modificadores[a] = modificadorDeAtributo(v)
  }

  const salvaguardas: Record<string, number> = {}
  const profSalv = new Set(ctx.proficiencias?.salvaguardas ?? [])
  for (const a of ATRIBUTOS) salvaguardas[a] = modificadores[a] + (profSalv.has(a) ? bp : 0)

  return {
    modificadores,
    bonus_de_proficiencia: bp,
    classe_de_armadura: calcular('classe_de_armadura', ctx, {}, vocabulario),
    pontos_de_vida_maximos: pontosDeVidaMaximos(ctx, vocabulario),
    iniciativa: calcular('iniciativa', ctx, {}, vocabulario),
    percepcao_passiva: calcular('percepcao_passiva', ctx, {}, vocabulario),
    salvaguardas,
    testes_de_pericia: {},
    deslocamento_m: deslocamento(ctx, vocabulario),
    ataques: ataques(ctx, equipamentoEquipado, vocabulario),
    conjuracao: conjuracao(ctx, vocabulario),
  }
}

/**
 * Os ataques da ficha.
 *
 * O Ataque Desarmado entra sempre — todo mundo tem, e é ele que o Monge transforma.
 * As armas equipadas entram depois, cada uma com o atributo que ela usa e se o
 * personagem é proficiente com ela.
 */
export function ataques(
  ctx: Contexto,
  equipamentoEquipado: string[],
  vocabulario?: Vocabulario,
): Ataque[] {
  const eq = separar(equipamentoEquipado)
  const filtros = ctx.proficiencias?.armas ?? []

  const trocas = (ctx.substituicoes_de_atributo ?? [])
    .filter((t) => t.aplica_a.includes('ataque_desarmado') && t.escopo.includes('jogada_de_ataque'))
    .map((t) => ({ de: t.de, para: t.para }))
  const dadoDesarmado = (ctx.dados_de_dano ?? []).find((d) =>
    d.escopo.includes('ataque_desarmado'),
  )?.dado

  return [
    ataqueDesarmado(ctx, trocas, dadoDesarmado, vocabulario),
    ...eq.armas.map((a) => ataqueComArma(a, ctx, filtros, vocabulario)),
  ]
}

/**
 * A parte de magia da ficha.
 *
 * Ausente para quem não conjura — e ausente, não zerada: um Bárbaro com "CD de
 * magia 11" na ficha é pior que um Bárbaro sem a linha.
 */
export function conjuracao(ctx: Contexto, vocabulario?: Vocabulario): Ficha['conjuracao'] {
  const atributo = ctx.atributo_de_conjuracao
  if (!atributo) return undefined

  const espacos: Record<number, number> = {}
  for (let circulo = 1; circulo <= 9; circulo++) {
    const n = ctx.colunas?.[`espacos_${circulo}`]
    if (typeof n === 'number' && n > 0) espacos[circulo] = n
  }
  const numero = (chave: string) => {
    const v = ctx.colunas?.[chave]
    return typeof v === 'number' ? v : 0
  }

  return {
    atributo,
    cd_para_evitar_sua_magia: calcular('cd_para_evitar_sua_magia', ctx, {}, vocabulario),
    jogada_de_ataque_magico: calcular('jogada_de_ataque_magico', ctx, {}, vocabulario),
    espacos,
    magias_preparadas: numero('magias_preparadas'),
    truques: numero('truques'),
  }
}

/** O teste de uma perícia: modificador do atributo + Bônus de Proficiência se proficiente. */
export function testeDePericia(ctx: Contexto, pericia: string, atributo: string): number {
  const bruto = ctx.atributos?.[atributo]
  if (bruto === undefined) throw new ErroDoMotor(`atributo ausente no contexto: '${atributo}'`)
  const proficiente = (ctx.proficiencias?.pericias ?? []).includes(pericia)
  return modificadorDeAtributo(bruto) + (proficiente ? bonusDeProficiencia(ctx) : 0)
}

/**
 * Pontos de Vida máximos.
 *
 * A fórmula é a do livro; o que o motor faz é preencher as parcelas que ela pede.
 * `soma_dos_niveis_seguintes` usa o VALOR FIXO da tabela por classe (p. 42), com o
 * piso de 1 por nível — que existe para o modificador de Constituição negativo.
 */
export function pontosDeVidaMaximos(ctx: Contexto, vocabulario?: Vocabulario): Resultado {
  const dadoDeVida = ctx.dado_de_vida_da_classe
  const porNivel = ctx.pv_por_nivel_da_classe
  if (dadoDeVida === undefined || porNivel === undefined) {
    throw new ErroDoMotor('contexto sem Dado de Vida ou sem valor fixo por nível da classe')
  }
  const modCon = modificadorDeAtributo(ctx.atributos.CON)

  const nivel1 = dadoDeVida + modCon
  const niveisSeguintes = Math.max(0, ctx.nivel_do_personagem - 1) * Math.max(1, porNivel + modCon)

  return calcular(
    'pontos_de_vida_maximos',
    ctx,
    {
      pontos_de_vida_no_nivel_1: nivel1,
      soma_dos_niveis_seguintes: niveisSeguintes,
      bonus_de_caracteristicas: 0,
      bonus_temporarios_de_maximo: 0,
      reducoes_de_maximo: 0,
    },
    vocabulario,
  )
}

/** Deslocamento: a base da espécie mais os modificadores ativos que somam. */
export function deslocamento(ctx: Contexto, vocabulario?: Vocabulario): number {
  const base = ctx.deslocamento_base_m
  if (base === undefined) throw new ErroDoMotor('contexto sem deslocamento de base')
  const mods = ctx.modificadores_ativos?.deslocamento ?? []
  let total = base
  for (const m of mods) {
    if (m.empilha === 'substitui') total = m.valor
    else total += m.valor
  }
  return total
}

/** Reexportado para quem quiser avaliar uma fórmula solta contra este contexto. */
export { avaliar, condicaoVale }
