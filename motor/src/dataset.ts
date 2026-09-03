// Carrega o dataset. O motor lê `dados/` como dado imutável — nunca escreve nele.

import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import type { Vocabulario } from './condicao.ts'
import { ErroDoMotor } from './tipos.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))
export const RAIZ_DADOS = join(AQUI, '..', '..', 'dados')

// `dados/` é imutável em tempo de execução — o motor só lê. Reler e reparsear a cada
// chamada custava 49 ms por ficha no backend, quase tudo em `magias.json`. Memorizar
// não fere a pureza: a mesma entrada continua dando a mesma saída, e a única coisa
// que muda é não pagar o disco duas vezes pelo mesmo arquivo.
//
// Quem mexer em `dados/` no meio de um processo (os testes que plantam defeito)
// chama `esquecerDataset()`.
const memoria = new Map<string, unknown>()

export function lerJson<T = unknown>(...partes: string[]): T {
  const caminho = join(RAIZ_DADOS, ...partes)
  const guardado = memoria.get(caminho)
  if (guardado !== undefined) return guardado as T
  const lido = JSON.parse(readFileSync(caminho, 'utf-8')) as T
  memoria.set(caminho, lido)
  return lido
}

/** Esquece o que foi lido. Para testes que mexem em `dados/` com o processo de pé. */
export function esquecerDataset(): void {
  memoria.clear()
}

export function catalogo<T = Record<string, unknown>>(nome: string): { itens: T[] } {
  return lerJson(`catalogos`, `${nome}.json`)
}

export function vocabularioDeRuntime(): Vocabulario {
  return lerJson('vocabulario_de_runtime.json')
}

/**
 * Um item de catálogo por id; ausência é erro, nunca `undefined` silencioso.
 *
 * Lança `ErroDoMotor` e não `Error`: id que não existe é quase sempre construção
 * errada — alguém pediu uma espécie que o livro não tem — e quem chama precisa poder
 * distinguir isso de defeito interno. Como `Error` puro, virava 500 no backend.
 */
export function porId<T extends { id: string }>(itens: T[], id: string, ondeVim: string): T {
  const achado = itens.find((i) => i.id === id)
  if (!achado) throw new ErroDoMotor(`id inexistente em ${ondeVim}: '${id}'`)
  return achado
}


/**
 * O que o dataset sabe sobre um id, sem que o motor saiba o que é o id.
 *
 * `familia` é a única distinção que este arquivo faz, e ela é ESTRUTURAL: de que
 * arquivo o item veio. É o que deixa a ficha listar "as características e talentos
 * deste personagem" sem citar nenhuma delas — e sem confundir uma característica
 * com a classe que a contém.
 */
export type Entidade = {
  id: string
  nome: string
  descricao_curta?: string
  fonte?: unknown
  familia:
    | 'caracteristica' | 'traco' | 'talento'
    | 'classe' | 'subclasse' | 'especie' | 'antecedente'
    | 'item' | 'magia' | 'atributo'
}

const entidades = new Map<string, Entidade>()

type ItemComNome = {
  id: string
  nome?: string
  descricao_curta?: string
  fonte?: unknown
  tracos?: ItemComNome[]
}

function indexarEntidades(): Map<string, Entidade> {
  if (entidades.size) return entidades
  const fontes: [Entidade['familia'], { itens: ItemComNome[] }][] = [
    ['caracteristica', lerJson('caracteristicas.json')],
    ['classe', lerJson('classes.json')],
    ['subclasse', lerJson('subclasses.json')],
    ['talento', catalogo('talentos')],
    // A espécie entra depois dos talentos porque os TRAÇOS dela vêm junto, e é o
    // traço que a ficha lista — o Ataque de Sopro, não o Draconato.
    ['especie', catalogo('especies')],
    ['antecedente', catalogo('antecedentes')],
    // Os atributos entram para a proveniência dizer "Destreza" e não "DES". Com
    // família própria: eles não são característica, e não devem aparecer na lista
    // de "o que este personagem sabe fazer".
    ['atributo', catalogo('atributos')],
    ['item', catalogo('itens')],
    ['magia', catalogo('magias')],
  ]
  for (const [familia, doc] of fontes) {
    for (const i of doc.itens) {
      guardar(familia, i)
      // Traço de espécie NÃO é item de catálogo: ele mora dentro da espécie. Sem
      // descer até ele, o Ataque de Sopro do Draconato aparecia na ficha como
      // `espécie draconato / ataque_de_sopro`.
      for (const t of i.tracos ?? []) guardar('traco', t)
    }
  }
  return entidades
}

function guardar(familia: Entidade['familia'], i: ItemComNome): void {
  if (!i.nome || entidades.has(i.id)) return
  entidades.set(i.id, {
    id: i.id,
    nome: i.nome,
    familia,
    ...(i.descricao_curta ? { descricao_curta: i.descricao_curta } : {}),
    ...(i.fonte !== undefined ? { fonte: i.fonte } : {}),
  })
}

/** O que o dataset diz sobre este id, ou nada — e ninguém inventa. */
export function entidade(id: string): Entidade | undefined {
  return indexarEntidades().get(id)
}

/**
 * O nome de uma entidade, por id, para a ficha mostrar em vez do id.
 *
 * Não conhece nenhum id de conteúdo: recebe um e devolve o `nome` que o dado
 * declara. Sem achar, devolve `undefined` — quem chama decide o que dizer.
 */
export function nomeDeEntidade(id: string): string | undefined {
  return entidade(id)?.nome
}

/**
 * Palavras que a COLETA escreve na trilha de origem para dizer que tipo de coisa
 * vem a seguir. Não são id de conteúdo — são a gramática da própria trilha —, e
 * é por isso que podem aparecer neste arquivo.
 */
const PREFIXOS_DA_TRILHA = /^(talento|classe|subclasse|espécie|especie|antecedente|item) /

/** Um trecho da trilha sem a palavra estrutural que o antecede. */
export function idNaTrilha(parte: string): string {
  return parte.trim().replace(PREFIXOS_DA_TRILHA, '')
}

/**
 * A trilha de origem traduzida em entidades, do mais geral ao mais específico.
 *
 * A coleta guarda `antecedente acolito / talento iniciado_em_magia /
 * iniciado_em_magia_truques`, que é ótimo para depurar e ilegível na ficha. O que
 * não tem nome declarado (o id de uma escolha) sai fora, em vez de virar
 * "guerreiro estilo de luta" na tela, que foi como este defeito apareceu.
 */
export function entidadesDaTrilha(origem: string): Entidade[] {
  const saida: Entidade[] = []
  for (const parte of origem.split(' / ')) {
    const e = entidade(idNaTrilha(parte))
    if (e && !saida.some((x) => x.id === e.id)) saida.push(e)
  }
  return saida
}

/** O mesmo, só os nomes — que é o que a maioria de quem chama quer. */
export function trilhaLegivel(origem: string): string[] {
  return entidadesDaTrilha(origem).map((e) => e.nome)
}
