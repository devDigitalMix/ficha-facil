// O histórico: o que aconteceu, com o número daquele momento.
//
// **Por que o evento guarda valor derivado, se o personagem nunca guarda.**
//
// O documento do personagem guarda construção e estado, nunca a ficha, porque a ficha
// se recalcula e guardá-la criaria uma segunda verdade que envelhece. O evento é o
// contrário: ele é o **passado**, e o passado não se recalcula. Se a linha diz
// "recuperou 8 de vida · PV 20/26", esse 26 tem de continuar 26 mesmo depois de o
// personagem subir de nível, ganhar Constituição ou de uma regra do dataset mudar —
// senão o histórico deixa de ser o que aconteceu e vira o que aconteceria hoje.
//
// Então: proveniência é do agora e se recalcula; histórico é do passado e se congela.
// São a mesma informação em tempos diferentes, e por isso moram em lugares diferentes.
//
// O TEXTO, esse, não é congelado. O evento guarda números; `resumo()` os formata na
// hora de ler. Assim melhorar uma frase melhora o histórico inteiro, e nenhum número
// muda por causa disso.

export const TIPOS_DE_EVENTO = [
  'dano_sofrido',
  'vida_recuperada',
  'temporarios_alterados',
  'espaco_gasto',
  'espaco_recuperado',
  'recurso_gasto',
  'recurso_recuperado',
  'magia_conjurada',
  'descanso',
  'item_ganho',
  'item_perdido',
  'item_equipado',
  'item_desequipado',
] as const

export type TipoDeEvento = (typeof TIPOS_DE_EVENTO)[number]

type Base = {
  id: string
  personagem_id: string
  usuario_id: string
  /** ISO-8601. Ordena o histórico, do mais recente para o mais antigo. */
  em: string
}

export type Evento = Base &
  (
    | { tipo: 'dano_sofrido' | 'vida_recuperada'
        quantidade: number; pv_antes: number; pv_depois: number; pv_maximo: number }
    | { tipo: 'temporarios_alterados'; antes: number; depois: number }
    | { tipo: 'espaco_gasto' | 'espaco_recuperado'
        circulo: number; quantidade: number
        /** Quantos daquele círculo sobraram, e de quantos. */
        restantes: number; total: number
        /** Só quando quem pediu disse qual magia era. */
        magia_id?: string; magia_nome?: string }
    | { tipo: 'recurso_gasto' | 'recurso_recuperado'
        recurso_id: string; quantidade: number; gastos_depois: number }
    /**
     * Conjurar não é sempre uma mudança de estado.
     *
     * Um truque não gasta nada, e a magia que um talento dá de graça pode não gastar
     * espaço: pelo diff de estado, não aconteceu nada — e a queixa do João foi
     * exatamente essa, "clico em usar num truque mas não fala nada". O evento então
     * é dito por quem conjurou, não deduzido da diferença, e guarda o que aquilo
     * custou naquele momento.
     */
    | { tipo: 'magia_conjurada'
        magia_id: string; magia_nome: string; circulo: number
        /** 'nenhum' | 'espaco' | 'recurso' | 'sem_espaco' — o custo daquele momento. */
        custo: string
        /** Só quando gastou espaço. */
        circulo_gasto?: number; restantes?: number; total?: number
        /** Só quando gastou um recurso (o uso de graça, Pontos de Feitiçaria…). */
        recurso_id?: string; recurso_nome?: string; usos_restantes?: number; usos_totais?: number }
    | { tipo: 'descanso'; descanso_id: string; descanso_nome: string; o_que_voltou: string[] }
    | { tipo: 'item_ganho' | 'item_perdido'
        item_id: string; item_nome?: string; quantidade: number; quantidade_depois: number }
    | { tipo: 'item_equipado' | 'item_desequipado'; item_id: string; item_nome?: string }
  )

/**
 * A linha que o jogador lê.
 *
 * Formatada a partir dos números do evento, e de nada além deles — o que garante que
 * a mesma linha saia igual daqui a um ano. Onde não há denominador (recursos, cujo
 * máximo a ficha ainda não expõe), a frase simplesmente não o promete.
 */
export function resumo(e: Evento): string {
  switch (e.tipo) {
    case 'dano_sofrido':
      return `sofreu ${e.quantidade} de dano · PV ${e.pv_depois}/${e.pv_maximo}`
    case 'vida_recuperada':
      return `recuperou ${e.quantidade} de vida · PV ${e.pv_depois}/${e.pv_maximo}`
    case 'temporarios_alterados': {
      const d = e.depois - e.antes
      return d > 0
        ? `ganhou ${d} Ponto${d > 1 ? 's' : ''} de Vida Temporário${d > 1 ? 's' : ''} (${e.depois})`
        : `perdeu ${-d} Ponto${-d > 1 ? 's' : ''} de Vida Temporário${-d > 1 ? 's' : ''} (${e.depois})`
    }
    case 'espaco_gasto': {
      const oQue = e.magia_nome ?? e.magia_id
      const acao = oQue
        ? `conjurou ${oQue} com espaço de ${e.circulo}º`
        : `gastou ${e.quantidade} espaço${e.quantidade > 1 ? 's' : ''} de ${e.circulo}º`
      return `${acao} · ${e.restantes}/${e.total} restantes`
    }
    case 'espaco_recuperado':
      return `recuperou ${e.quantidade} espaço${e.quantidade > 1 ? 's' : ''} de ${e.circulo}º` +
        ` · ${e.restantes}/${e.total} restantes`
    case 'recurso_gasto':
      return `gastou ${e.quantidade} de ${e.recurso_id}`
    case 'recurso_recuperado':
      return `recuperou ${e.quantidade} de ${e.recurso_id}`
    case 'magia_conjurada': {
      const oQue = e.circulo === 0 ? 'lançou o truque' : 'conjurou'
      if (e.custo === 'espaco') {
        return `${oQue} ${e.magia_nome} com espaço de ${e.circulo_gasto}º` +
          ` · ${e.restantes}/${e.total} restantes`
      }
      if (e.custo === 'recurso') {
        const nome = e.recurso_nome ?? e.recurso_id
        return `${oQue} ${e.magia_nome} sem gastar espaço` +
          ` · ${nome} ${e.usos_restantes}/${e.usos_totais}`
      }
      return `${oQue} ${e.magia_nome}${e.circulo === 0 ? '' : ' sem gastar espaço'}`
    }
    case 'item_ganho':
      return `pegou ${e.quantidade}× ${e.item_nome ?? e.item_id}` +
        (e.quantidade_depois > e.quantidade ? ` · agora ${e.quantidade_depois}` : '')
    case 'item_perdido':
      return `perdeu ${e.quantidade}× ${e.item_nome ?? e.item_id}` +
        (e.quantidade_depois > 0 ? ` · restam ${e.quantidade_depois}` : '')
    case 'item_equipado':
      return `equipou ${e.item_nome ?? e.item_id}`
    case 'item_desequipado':
      return `guardou ${e.item_nome ?? e.item_id}`
    case 'descanso':
      return e.o_que_voltou.length
        ? `${e.descanso_nome}: ${e.o_que_voltou.join(', ')}`
        : `${e.descanso_nome}, sem nada a recuperar`
  }
}

/** O evento como o app o recebe: os números, mais a linha pronta. */
export const paraOCliente = (e: Evento) => ({ ...e, resumo: resumo(e) })
