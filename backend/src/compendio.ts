// O compêndio: `dados/` servido como está.
//
// Não passa por banco e não precisa. O dado é imutável entre builds, então a resposta
// leva o ETag da versão do dataset e cache longo — e o cliente que já tem a versão
// recebe 304 em vez do catálogo inteiro. Um `magias.json` tem 391 entradas; mandar
// isso de novo a cada abertura de tela seria desperdício por falta de um cabeçalho.
//
// Só lê. Se algum dia o backend escrever em `dados/`, a reconstrução deixa de provar
// qualquer coisa.

import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { RAIZ_DADOS } from '../../motor/src/dataset.ts'
import { naoEncontrado } from './erros.ts'

export type Colecao = {
  nome: string
  /** 'colecao' mora em dados/, 'catalogo' em dados/catalogos/. */
  familia: 'colecao' | 'catalogo'
  caminho: string
  total: number
}

function indexar(): Map<string, Colecao> {
  const mapa = new Map<string, Colecao>()
  const adicionar = (familia: Colecao['familia'], base: string, arquivo: string) => {
    if (!arquivo.endsWith('.json')) return
    const nome = arquivo.slice(0, -5)
    const caminho = join(base, arquivo)
    const doc = JSON.parse(readFileSync(caminho, 'utf-8')) as { itens?: unknown[] }
    // vocabulario_de_runtime não tem `itens`; entra assim mesmo, com total 0
    mapa.set(nome, { nome, familia, caminho, total: doc.itens?.length ?? 0 })
  }
  for (const a of readdirSync(RAIZ_DADOS)) {
    if (a === 'catalogos') continue
    adicionar('colecao', RAIZ_DADOS, a)
  }
  const dirCatalogos = join(RAIZ_DADOS, 'catalogos')
  for (const a of readdirSync(dirCatalogos)) adicionar('catalogo', dirCatalogos, a)
  return mapa
}

let cache: Map<string, Colecao> | null = null

export function colecoes(): Map<string, Colecao> {
  if (!cache) cache = indexar()
  return cache
}

export function esquecerIndice(): void {
  cache = null
}

/** O índice do compêndio: o que existe, de que família e com quantos itens. */
export function indice() {
  return [...colecoes().values()]
    .map(({ nome, familia, total }) => ({ nome, familia, total }))
    .sort((a, b) => a.nome.localeCompare(b.nome))
}

export function lerColecao(nome: string): unknown {
  const c = colecoes().get(nome)
  if (!c) throw naoEncontrado(`coleção '${nome}' no compêndio`)
  return JSON.parse(readFileSync(c.caminho, 'utf-8'))
}

export function lerItem(nome: string, id: string): unknown {
  const doc = lerColecao(nome) as { itens?: { id: string }[] }
  const achado = doc.itens?.find((i) => i.id === id)
  if (!achado) throw naoEncontrado(`'${id}' em '${nome}'`)
  return achado
}
