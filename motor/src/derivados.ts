// Valores derivados: as contas da ficha, tiradas de catalogos/valores_derivados.json.
//
// O motor não reescreve nenhuma delas. Ele avalia a fórmula que o livro deu, e o
// que a fórmula pede e ele não sabe resolver sozinho (os Pontos de Vida dos níveis
// seguintes, por exemplo) entra por `extras` — calculado por quem chama, com a
// regra também vinda do dataset. Assim, corrigir uma conta no livro é corrigir o
// JSON, não o código.

import type { Contexto, Formula, Resultado } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { avaliar } from './formula.ts'
import { catalogo, porId } from './dataset.ts'
import type { Vocabulario } from './condicao.ts'

export type ValorDerivado = {
  id: string
  nome: string
  formula: Formula
  parcelas?: { rotulo: string; chave: string; sempre?: boolean; condicao?: unknown }[]
  tabela_por_classe?: { dado_de_vida: number; classes: string[]; pv_por_nivel: number }[]
  calculo_padrao?: { id: string; base: number; soma_modificador?: string }
}

let cache: ValorDerivado[] | null = null

export function valoresDerivados(): ValorDerivado[] {
  if (!cache) cache = catalogo<ValorDerivado>('valores_derivados').itens
  return cache
}

export function derivado(id: string): ValorDerivado {
  return porId(valoresDerivados(), id, 'catalogos/valores_derivados.json')
}

/** Avalia um valor derivado pelo id, com o que o chamador injetar em `extras`. */
export function calcular(
  id: string,
  ctx: Contexto,
  extras: Record<string, number> = {},
  vocabulario?: Vocabulario,
): Resultado {
  const vd = derivado(id)
  if (!vd.formula) throw new ErroDoMotor(`valor derivado sem fórmula: '${id}'`)
  const comExtras: Contexto = { ...ctx, extras: { ...(ctx.extras ?? {}), ...extras } }
  return apresentar(vd, avaliar(vd.formula, comExtras, vocabulario))
}

/**
 * Troca o rótulo cru das parcelas pelo que o dataset escreveu.
 *
 * O avaliador não tem como saber o nome bonito de um extra: ele recebe a chave
 * `soma_dos_niveis_seguintes` e é isso que devolve. Mas o catálogo já declara
 * "Pontos de Vida dos níveis seguintes" em `parcelas`, e é essa a frase que a
 * ficha deve mostrar. Sem isto, a proveniência dos Pontos de Vida saía como uma
 * fileira de identificadores.
 *
 * A parcela declarada com `condicao` só aparece quando vale alguma coisa — é o
 * que as condições do catálogo dizem, cada uma à sua maneira ("tem característica
 * que aumenta o máximo", "nível > 1"). Zerada, ela é ruído: ninguém quer ler
 * "+ 0 (reduções do máximo)" numa ficha sem dreno nenhum. A marcada `sempre`
 * aparece mesmo zerada, porque ela É a conta.
 */
function apresentar(vd: ValorDerivado, r: Resultado): Resultado {
  const declaradas = vd.parcelas
  if (!declaradas?.length) return r
  const porChave = new Map(declaradas.map((p) => [p.chave, p]))
  return {
    ...r,
    parcelas: r.parcelas.flatMap((parcela) => {
      const d = porChave.get(parcela.rotulo)
      if (!d) return [parcela]
      if (!d.sempre && d.condicao !== undefined && parcela.valor === 0) return []
      return [{ ...parcela, rotulo: d.rotulo }]
    }),
  }
}

/**
 * A tabela Pontos de Vida Fixos por Classe (p. 42). Não é deduzida do Dado de
 * Vida: o livro imprime os valores, e o dataset os guarda.
 */
export function pvDaClasse(classe: string): { dado_de_vida: number; pv_por_nivel: number } {
  const linhas = derivado('pontos_de_vida_no_nivel_1').tabela_por_classe ?? []
  const linha = linhas.find((l) => l.classes.includes(classe))
  if (!linha) throw new ErroDoMotor(`classe sem linha na tabela de Pontos de Vida: '${classe}'`)
  return { dado_de_vida: linha.dado_de_vida, pv_por_nivel: linha.pv_por_nivel }
}
