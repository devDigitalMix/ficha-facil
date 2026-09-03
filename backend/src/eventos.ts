// Onde o histórico fica, e como ele nasce.
//
// **Append-only.** Nunca se edita nem se apaga um evento: corrigir é gravar outro.
// Um histórico que pode ser reescrito não é histórico.
//
// Os eventos são DERIVADOS DA DIFERENÇA de estado, num lugar só (`aoMudarEstado`).
// A alternativa — cada rota lembrar de gravar o seu — é a que apodrece: basta um
// caminho novo esquecer a chamada para o histórico ficar com buracos silenciosos.
// Aqui, se o estado mudou, o evento existe; se não mudou, não existe evento.

import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { randomUUID } from 'node:crypto'
import type { Evento } from './evento.ts'
import type { EstadoDeJogo } from './personagem.ts'

export type Pagina = { itens: Evento[]; proximo?: string }

export interface ArmazemDeEventos {
  registrar(novos: Omit<Evento, 'id'>[]): Promise<Evento[]>
  /** Do mais recente para o mais antigo. `antesDe` é o `em` do último já visto. */
  listar(personagemId: string, opcoes?: { limite?: number; antesDe?: string }): Promise<Pagina>
}

export const LIMITE_PADRAO = 50

/** Mais recente primeiro; empate desempatado pelo id, para a ordem ser estável. */
export function maisRecentePrimeiro(a: Evento, b: Evento): number {
  if (a.em !== b.em) return a.em < b.em ? 1 : -1
  return a.id < b.id ? 1 : -1
}

function paginar(todos: Evento[], opcoes?: { limite?: number; antesDe?: string }): Pagina {
  const limite = Math.min(Math.max(opcoes?.limite ?? LIMITE_PADRAO, 1), 200)
  let lista = [...todos].sort(maisRecentePrimeiro)
  if (opcoes?.antesDe) lista = lista.filter((e) => e.em < opcoes.antesDe!)
  const itens = lista.slice(0, limite)
  // Só promete "tem mais" quando tem mesmo: cursor à toa faz o app pedir página vazia.
  const proximo = lista.length > limite ? itens[itens.length - 1].em : undefined
  return { itens, proximo }
}

export class EventosNaMemoria implements ArmazemDeEventos {
  lista: Evento[] = []

  async registrar(novos: Omit<Evento, 'id'>[]): Promise<Evento[]> {
    const completos = novos.map((e) => ({ ...e, id: randomUUID() }) as Evento)
    this.lista.push(...completos)
    return completos
  }

  async listar(personagemId: string, opcoes?: { limite?: number; antesDe?: string }) {
    return paginar(this.lista.filter((e) => e.personagem_id === personagemId), opcoes)
  }
}

/** Um JSON por evento, para rodar sem banco. Não escala, e não precisa: é o modo local. */
export class EventosEmArquivos implements ArmazemDeEventos {
  raiz: string

  constructor(raiz: string) {
    this.raiz = raiz
    mkdirSync(raiz, { recursive: true })
  }

  async registrar(novos: Omit<Evento, 'id'>[]): Promise<Evento[]> {
    const completos = novos.map((e) => ({ ...e, id: randomUUID() }) as Evento)
    for (const e of completos) {
      const caminho = join(this.raiz, `${e.id}.json`)
      const temporario = `${caminho}.${process.pid}.tmp`
      writeFileSync(temporario, JSON.stringify(e, null, 2), 'utf-8')
      renameSync(temporario, caminho)
    }
    return completos
  }

  async listar(personagemId: string, opcoes?: { limite?: number; antesDe?: string }) {
    if (!existsSync(this.raiz)) return { itens: [] }
    const todos = readdirSync(this.raiz)
      .filter((n) => n.endsWith('.json'))
      .map((n) => JSON.parse(readFileSync(join(this.raiz, n), 'utf-8')) as Evento)
      .filter((e) => e.personagem_id === personagemId)
    return paginar(todos, opcoes)
  }
}

// ------------------------------------------------------- de onde vêm os eventos

/** O retrato do momento, que o evento congela. Vem da ficha, recalculada agora. */
export type Retrato = {
  pv_maximo: number
  /** Espaços por círculo que o personagem TEM (não os gastos). */
  espacos: Record<string, number>
}

/** Contexto opcional de quem pediu a mudança: hoje, qual magia foi conjurada. */
export type Motivo = { magia_id?: string; magia_nome?: string }

const numero = (v: unknown) => (typeof v === 'number' ? v : 0)
const mapa = (v: unknown) => (v && typeof v === 'object' ? (v as Record<string, number>) : {})

/**
 * A diferença entre dois estados, em eventos.
 *
 * Só o que mudou vira evento. Um PATCH que reenvia o mesmo valor não gera linha
 * nenhuma — o histórico é do que aconteceu, não do que foi pedido.
 */
export function aoMudarEstado(
  antes: EstadoDeJogo,
  depois: EstadoDeJogo,
  retrato: Retrato,
  motivo?: Motivo,
): Omit<Evento, 'id' | 'personagem_id' | 'usuario_id' | 'em'>[] {
  const eventos: Omit<Evento, 'id' | 'personagem_id' | 'usuario_id' | 'em'>[] = []

  // ------------------------------------------------------------------ vida
  //
  // **Personagem sem PV atual está com a vida cheia.** É convenção do backend, não
  // regra do livro: o estado começa vazio, e a primeira vez que alguém marca dano
  // precisa ter um "antes" para comparar. Tratar como cheio é o que bate com o que
  // a ficha mostra de um personagem recém-criado — e a alternativa, não gerar evento
  // nenhum na primeira marcação, faria o primeiro dano de toda campanha sumir do
  // histórico.
  if (depois.pontos_de_vida_atuais !== undefined) {
    const pv_antes = antes.pontos_de_vida_atuais ?? retrato.pv_maximo
    const pv_depois = depois.pontos_de_vida_atuais
    if (pv_depois !== pv_antes) {
      const delta = pv_depois - pv_antes
      eventos.push({
        tipo: delta < 0 ? 'dano_sofrido' : 'vida_recuperada',
        quantidade: Math.abs(delta),
        pv_antes,
        pv_depois,
        pv_maximo: retrato.pv_maximo,
      })
    }
  }

  // ---------------------------------------------------------- temporários
  const tAntes = numero(antes.pontos_de_vida_temporarios)
  const tDepois = numero(depois.pontos_de_vida_temporarios)
  if (depois.pontos_de_vida_temporarios !== undefined && tAntes !== tDepois) {
    eventos.push({ tipo: 'temporarios_alterados', antes: tAntes, depois: tDepois })
  }

  // -------------------------------------------------------------- espaços
  if (depois.espacos_gastos !== undefined) {
    const gAntes = mapa(antes.espacos_gastos)
    const gDepois = mapa(depois.espacos_gastos)
    for (const circulo of Object.keys({ ...gAntes, ...gDepois }).sort()) {
      const de = numero(gAntes[circulo])
      const para = numero(gDepois[circulo])
      if (de === para) continue
      const total = numero(retrato.espacos[circulo])
      eventos.push({
        tipo: para > de ? 'espaco_gasto' : 'espaco_recuperado',
        circulo: Number(circulo),
        quantidade: Math.abs(para - de),
        restantes: Math.max(total - para, 0),
        total,
        // A magia só é anotada quando um espaço foi GASTO: recuperar espaço não
        // conjura nada, e carimbar a magia ali seria mentira.
        ...(para > de && motivo?.magia_id
          ? { magia_id: motivo.magia_id, magia_nome: motivo.magia_nome }
          : {}),
      })
    }
  }

  // ------------------------------------------------------------- recursos
  if (depois.recursos_gastos !== undefined) {
    const rAntes = mapa(antes.recursos_gastos)
    const rDepois = mapa(depois.recursos_gastos)
    for (const recurso of Object.keys({ ...rAntes, ...rDepois }).sort()) {
      const de = numero(rAntes[recurso])
      const para = numero(rDepois[recurso])
      if (de === para) continue
      eventos.push({
        tipo: para > de ? 'recurso_gasto' : 'recurso_recuperado',
        recurso_id: recurso,
        quantidade: Math.abs(para - de),
        gastos_depois: para,
      })
    }
  }

  return eventos
}
