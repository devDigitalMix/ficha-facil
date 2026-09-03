// O que um descanso devolve.
//
// A regra NÃO mora aqui. O que devolve cada coisa está declarado em três lugares
// do dataset, e este arquivo só os lê e os junta:
//
//   • `catalogos/tipos_de_descanso.json` → `recupera`: os Pontos de Vida e os
//     Dados de Vida, que são do descanso e de mais ninguém;
//   • cada `recurso_com_recarga` → a sua própria `recarga` (a Fúria volta no
//     Longo, o Bruxo recupera o Ataque de Sopro no… enfim: cada um diz o seu);
//   • o `conceder_slot` da classe → quando os espaços de magia voltam, que é
//     Descanso Curto para o Bruxo e Longo para todo o resto.
//
// Por isso não existe aqui nenhum `if` sobre classe, espécie ou característica —
// e um descanso novo, ou uma característica que recarregue em outro gatilho,
// funciona sem tocar neste arquivo.

import type { Contexto, Recurso } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { catalogo, porId } from './dataset.ts'

export type TipoDeDescanso = {
  id: string
  nome: string
  recupera?: {
    pontos_de_vida?: string
    pontos_de_vida_temporarios?: string
    dados_de_vida?: string
    [outro: string]: unknown
  }
}

/**
 * O ESTADO que o personagem passa a ter depois do descanso.
 *
 * Só os campos que mudam — quem chama funde com o estado atual. Devolver o estado
 * inteiro faria este código decidir sobre coisas que ele não sabe (condições,
 * concentração), e apagá-las por omissão.
 */
export type EfeitoDoDescanso = {
  pontos_de_vida_atuais?: number
  pontos_de_vida_temporarios?: number
  espacos_gastos?: Record<string, number>
  recursos_gastos?: Record<string, number>
  /** Para o histórico dizer o que aconteceu, em vez de "estado mudou". */
  o_que_voltou: string[]
}

export function tiposDeDescanso(): TipoDeDescanso[] {
  return catalogo<TipoDeDescanso>('tipos_de_descanso').itens
}

/**
 * Aplica um descanso a um estado.
 *
 * `gastosAtuais` é o que o personagem já tinha gasto; `pvMaximo` e os recursos vêm
 * da ficha recalculada, nunca do que estava guardado — o teto pode ter mudado
 * desde o último descanso.
 */
export function descansar(
  tipoId: string,
  ctx: Contexto,
  ficha: { pontos_de_vida_maximos: number; recursos: Recurso[] },
  estadoAtual: {
    pontos_de_vida_atuais?: number
    pontos_de_vida_temporarios?: number
    espacos_gastos?: Record<string, number>
    recursos_gastos?: Record<string, number>
  },
): EfeitoDoDescanso {
  const tipo = porId(tiposDeDescanso(), tipoId, 'catalogos/tipos_de_descanso.json')
  const recupera = tipo.recupera
  if (!recupera) {
    throw new ErroDoMotor(`o descanso '${tipoId}' não declara o que recupera`)
  }

  const saida: EfeitoDoDescanso = { o_que_voltou: [] }

  // ------------------------------------------------------------- Pontos de Vida
  if (recupera.pontos_de_vida === 'todos') {
    const antes = estadoAtual.pontos_de_vida_atuais ?? ficha.pontos_de_vida_maximos
    if (antes < ficha.pontos_de_vida_maximos) {
      saida.pontos_de_vida_atuais = ficha.pontos_de_vida_maximos
      saida.o_que_voltou.push(
        `Pontos de Vida: ${antes} → ${ficha.pontos_de_vida_maximos}`,
      )
    }
  }

  // Os temporários "duram até se esgotarem ou até você completar um Descanso
  // Longo" (p. 33): o Curto os mantém, e é o dado que diz isso, não este código.
  if (recupera.pontos_de_vida_temporarios === 'perde' && estadoAtual.pontos_de_vida_temporarios) {
    saida.pontos_de_vida_temporarios = 0
    saida.o_que_voltou.push('perdeu os Pontos de Vida Temporários')
  }

  // -------------------------------------------------------- espaços de magia
  const gastosDeEspaco = estadoAtual.espacos_gastos ?? {}
  if (
    Object.values(gastosDeEspaco).some((n) => n > 0) &&
    (ctx.recarga_dos_espacos ?? []).some((r) => r.gatilho === tipoId)
  ) {
    saida.espacos_gastos = {}
    for (const circulo of Object.keys(gastosDeEspaco)) saida.espacos_gastos[circulo] = 0
    saida.o_que_voltou.push('espaços de magia')
  }

  // ---------------------------------------------------------------- recursos
  const gastosDeRecurso = { ...(estadoAtual.recursos_gastos ?? {}) }
  const devolvidos: string[] = []
  for (const recurso of ficha.recursos) {
    const gasto = gastosDeRecurso[recurso.id] ?? 0
    if (gasto <= 0) continue
    const regra = recurso.recarga.find((r) => r.gatilho === tipoId)
    if (!regra) continue
    const volta = regra.quantidade === 'todos' ? gasto : Math.min(gasto, regra.quantidade)
    if (volta <= 0) continue
    gastosDeRecurso[recurso.id] = gasto - volta
    devolvidos.push(volta === gasto ? recurso.nome : `${recurso.nome} (${volta} de ${gasto})`)
  }
  if (devolvidos.length) {
    saida.recursos_gastos = gastosDeRecurso
    saida.o_que_voltou.push(...devolvidos)
  }

  return saida
}
