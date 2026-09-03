// A porta de entrada do motor.
//
// Junta os quatro passos numa chamada só, que é o que o backend e o app vão usar:
// entra a construção mais o estado de jogo, sai a ficha, o checklist e as queixas.
//
// Continua puro: mesma entrada, mesma saída, sem relógio, sem aleatório, sem banco.

import {
  coletar,
  normalizarEscolhidos,
  type Construcao,
  type Colecao,
  type EfeitoColetado,
} from './colecao.ts'
import { montarContexto, type Estado } from './contexto.ts'
import { montarFicha, testeDePericia, type Ficha } from './ficha.ts'
import {
  conferirEscolha,
  checklist,
  type ItemDeChecklist,
  type Problema,
  ehPendencia,
  type Variaveis,
  type Fontes,
} from './escolha.ts'
import { vocabularioDeRuntime } from './dataset.ts'
import type { Contexto } from './tipos.ts'

export type Resultado = {
  ficha: Ficha
  contexto: Contexto
  /** As escolhas em aberto, já com as opções: é a tela de subir de nível. */
  checklist: ItemDeChecklist[]
  /** Escolhas resolvidas que não deveriam ter sido feitas assim. */
  problemas: Problema[]
  /** Efeitos coletados que a ficha estática ainda não consome. */
  nao_consumidos: EfeitoColetado[]
  colecao: Colecao
}

let vocab: ReturnType<typeof vocabularioDeRuntime> | null = null

export function montar(construcao: Construcao, estado: Estado = {}): Resultado {
  if (!vocab) vocab = vocabularioDeRuntime()

  const colecao = coletar(construcao)
  const equipado = construcao.equipamento_equipado ?? []
  const { contexto, nao_consumidos } = montarContexto(
    colecao,
    construcao.atributos_base,
    estado,
    vocab,
    equipado,
  )

  // A conferência vem DEPOIS do contexto, e não durante a coleta: as opções de uma
  // escolha podem depender do nível e dos atributos, e os atributos dependem de
  // outra escolha. Conferir no meio do caminho seria conferir contra meia ficha.
  const problemas: Problema[] = []
  const efeitosDeEscolha = new Map(
    [...colecao.escolhas].map(([id, { efeito }]) => [id, efeito]),
  )

  // Uma escolha pode definir uma variável que outra lê: o Iniciado em Magia escolhe
  // a lista, e os truques saem daquela lista. Sem isto o app ofereceria os 34 truques
  // do jogo inteiro no lugar dos do Druida.
  const variaveis: Variaveis = {}
  for (const [id, resolvida] of Object.entries(construcao.escolhas ?? {})) {
    const e = efeitosDeEscolha.get(id)
    const nome = e?.define_variavel as string | undefined
    const valor =
      typeof resolvida === 'string'
        ? resolvida
        : Array.isArray(resolvida)
          ? undefined
          : (resolvida as { escolhido?: string }).escolhido
    if (valor === undefined) continue
    if (nome) variaveis[nome] = valor
    variaveis[id] = valor
    variaveis[`escolhido_em:${id}`] = valor
  }
  // As FONTES: conjuntos que uma escolha alimenta e outra consome. O livro de magias
  // do Mago é o caso do livro — "escolha quatro magias do seu livro" (p. 148) só faz
  // sentido depois que o livro tem magias. Quem alimenta declara `alimenta`; quem
  // consome declara `de: { fonte }`. Nenhum id de conteúdo entra aqui.
  const fontes: Fontes = {}
  for (const [id, { efeito }] of colecao.escolhas) {
    const alvo = efeito.alimenta as string | undefined
    if (!alvo) continue
    const resolvida = construcao.escolhas?.[id]
    if (resolvida === undefined) continue
    ;(fontes[alvo] ??= []).push(...normalizarEscolhidos(resolvida))
  }

  for (const [id, resolvida] of Object.entries(construcao.escolhas ?? {})) {
    const e = efeitosDeEscolha.get(id)
    if (!e) {
      problemas.push({
        escolha_id: id,
        tipo: 'opcao_invalida',
        queixa: 'escolha resolvida que este personagem não tem — sobrou de outra construção?',
      })
      continue
    }
    problemas.push(...conferirEscolha(e, resolvida, contexto, variaveis, fontes))
  }

  return {
    ficha: montarFicha(contexto, vocab, equipado),
    contexto,
    checklist: checklist(colecao.pendencias, efeitosDeEscolha, contexto, variaveis, fontes),
    problemas,
    nao_consumidos,
    colecao,
  }
}

export { testeDePericia, ehPendencia }
export type { Construcao, Estado, Ficha, ItemDeChecklist, Problema }
export type { TipoDeProblema } from './escolha.ts'
