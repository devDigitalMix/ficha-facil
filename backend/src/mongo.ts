// O armazém no MongoDB Atlas.
//
// Implementa a mesma interface `Armazem` que o arquivo e a memória. O resto do backend
// não fica sabendo qual está em uso — é o que permite os testes rodarem sem banco e o
// servidor rodar sem Atlas quando `MONGODB_URI` está vazio.
//
// **O que o documento guarda: construção e estado, nunca a ficha.** É a decisão que faz
// o dataset valer a pena — corrigir uma regra em `dados/` corrige todos os personagens
// de uma vez, porque a ficha se recalcula a cada leitura. Guardar a ficha seria criar
// uma segunda verdade, que envelhece em silêncio: as 89 paráfrases de magia corrigidas
// na fase 20 não exigiram migração nenhuma, e é por isso.
//
// **O id.** O `_id` do Mongo é ObjectId; o resto do backend trabalha com `id` string,
// porque ele vem da URL. A tradução mora aqui e em nenhum outro lugar: `paraFora`
// devolve o documento com `id` e sem `_id`.

import { MongoClient, ObjectId, type Collection, type Db } from 'mongodb'
import type { Armazem } from './armazem.ts'
import type { Personagem } from './personagem.ts'
import { EmailJaUsado, type ArmazemDeUsuarios } from './usuarios.ts'
import type { Usuario } from './usuario.ts'
import { LIMITE_PADRAO, type ArmazemDeEventos, type Pagina } from './eventos.ts'
import type { Evento } from './evento.ts'

/** O documento como o Mongo o guarda: `_id` no lugar de `id`. */
export type Documento = Omit<Personagem, 'id'> & { _id: ObjectId }

export const ehObjectId = (id: string) => ObjectId.isValid(id) && String(new ObjectId(id)) === id

export function paraFora(d: Documento): Personagem {
  const { _id, ...resto } = d
  return { id: _id.toHexString(), ...resto } as Personagem
}

export class ArmazemMongo implements Armazem {
  cliente: MongoClient
  banco: Db
  personagens: Collection<Documento>

  constructor(cliente: MongoClient, nomeDoBanco: string) {
    this.cliente = cliente
    this.banco = cliente.db(nomeDoBanco)
    this.personagens = this.banco.collection<Documento>('personagens')
  }

  /**
   * Abre a conexão e garante os índices.
   *
   * `createIndex` é idempotente: chamar toda subida é barato e evita o índice existir
   * só na máquina de quem lembrou de criar à mão.
   */
  static async conectar(uri: string, nomeDoBanco: string): Promise<ArmazemMongo> {
    const cliente = new MongoClient(uri)
    await cliente.connect()
    const armazem = new ArmazemMongo(cliente, nomeDoBanco)
    await armazem.garantirIndices()
    return armazem
  }

  async garantirIndices(): Promise<void> {
    // É literalmente a consulta de "Meus personagens": os do dono, do mais recente
    // para o mais antigo.
    await this.personagens.createIndex({ usuario_id: 1, ultimo_acesso: -1 })
  }

  async criar(p: Omit<Personagem, 'id'>): Promise<Personagem> {
    const doc = { ...p, _id: new ObjectId() } as Documento
    await this.personagens.insertOne(doc)
    return paraFora(doc)
  }

  /**
   * Um id que não é ObjectId é ausência, não erro.
   *
   * O id vem da URL, então qualquer coisa chega aqui. Deixar o driver lançar
   * transformaria "personagem inexistente" (404) em "erro interno" (500), que é a
   * mesma classe de defeito que a fase 19 consertou no `porId` do motor.
   */
  async ler(id: string): Promise<Personagem | undefined> {
    if (!ehObjectId(id)) return undefined
    const doc = await this.personagens.findOne({ _id: new ObjectId(id) })
    return doc ? paraFora(doc) : undefined
  }

  async gravar(p: Personagem): Promise<Personagem> {
    if (!ehObjectId(p.id)) throw new Error(`id de personagem inválido: '${p.id}'`)
    const { id, ...resto } = p
    await this.personagens.replaceOne(
      { _id: new ObjectId(id) },
      resto as Omit<Documento, '_id'>,
      { upsert: true },
    )
    return p
  }

  async listar(usuarioId: string): Promise<Personagem[]> {
    // Bate exatamente com o índice { usuario_id: 1, ultimo_acesso: -1 }.
    const docs = await this.personagens
      .find({ usuario_id: usuarioId })
      .sort({ ultimo_acesso: -1 })
      .toArray()
    return docs.map(paraFora)
  }

  async apagar(id: string): Promise<boolean> {
    if (!ehObjectId(id)) return false
    const r = await this.personagens.deleteOne({ _id: new ObjectId(id) })
    return r.deletedCount === 1
  }

  async fechar(): Promise<void> {
    await this.cliente.close()
  }
}

// ------------------------------------------------------------------- usuários

type DocumentoDeUsuario = Omit<Usuario, 'id'> & { _id: ObjectId }

export class UsuariosMongo implements ArmazemDeUsuarios {
  colecao: Collection<DocumentoDeUsuario>

  constructor(banco: Db) {
    this.colecao = banco.collection<DocumentoDeUsuario>('usuarios')
  }

  /**
   * Índice ÚNICO em `email`.
   *
   * A checagem em código ("já existe conta com esse e-mail?") não basta: dois
   * cadastros simultâneos passam os dois pela checagem antes de qualquer um gravar.
   * Quem garante de verdade é o banco, e por isso o índice é único e o erro de chave
   * duplicada vira `EmailJaUsado` em vez de 500.
   */
  async garantirIndices(): Promise<void> {
    await this.colecao.createIndex({ email: 1 }, { unique: true })
  }

  async criar(u: Omit<Usuario, 'id'>): Promise<Usuario> {
    const doc = { ...u, _id: new ObjectId() } as DocumentoDeUsuario
    try {
      await this.colecao.insertOne(doc)
    } catch (e) {
      if ((e as { code?: number }).code === 11000) throw new EmailJaUsado(u.email)
      throw e
    }
    const { _id, ...resto } = doc
    return { id: _id.toHexString(), ...resto }
  }

  async ler(id: string): Promise<Usuario | undefined> {
    if (!ehObjectId(id)) return undefined
    return this.deDocumento(await this.colecao.findOne({ _id: new ObjectId(id) }))
  }

  async porEmail(email: string): Promise<Usuario | undefined> {
    return this.deDocumento(await this.colecao.findOne({ email }))
  }

  async gravar(u: Usuario): Promise<Usuario> {
    if (!ehObjectId(u.id)) throw new Error(`id de usuário inválido: '${u.id}'`)
    const { id, ...resto } = u
    await this.colecao.replaceOne({ _id: new ObjectId(id) }, resto as Omit<DocumentoDeUsuario, '_id'>)
    return u
  }

  deDocumento(d: DocumentoDeUsuario | null): Usuario | undefined {
    if (!d) return undefined
    const { _id, ...resto } = d
    return { id: _id.toHexString(), ...resto }
  }
}

// -------------------------------------------------------------------- eventos

type DocumentoDeEvento = Omit<Evento, 'id'> & { _id: ObjectId }

export class EventosMongo implements ArmazemDeEventos {
  colecao: Collection<DocumentoDeEvento>

  constructor(banco: Db) {
    this.colecao = banco.collection<DocumentoDeEvento>('eventos')
  }

  /** É a consulta do histórico: os de um personagem, do mais recente para trás. */
  async garantirIndices(): Promise<void> {
    await this.colecao.createIndex({ personagem_id: 1, em: -1 })
  }

  async registrar(novos: Omit<Evento, 'id'>[]): Promise<Evento[]> {
    if (!novos.length) return []
    const docs = novos.map((e) => ({ ...e, _id: new ObjectId() }) as DocumentoDeEvento)
    await this.colecao.insertMany(docs)
    return docs.map(({ _id, ...resto }) => ({ id: _id.toHexString(), ...resto }) as Evento)
  }

  async listar(personagemId: string, opcoes?: { limite?: number; antesDe?: string }): Promise<Pagina> {
    const limite = Math.min(Math.max(opcoes?.limite ?? LIMITE_PADRAO, 1), 200)
    const filtro: Record<string, unknown> = { personagem_id: personagemId }
    if (opcoes?.antesDe) filtro.em = { $lt: opcoes.antesDe }
    // Pede um a mais do que cabe: é como se sabe que há próxima página sem contar
    // a coleção inteira.
    const docs = await this.colecao
      .find(filtro).sort({ em: -1, _id: -1 }).limit(limite + 1).toArray()
    const temMais = docs.length > limite
    const itens = docs.slice(0, limite)
      .map(({ _id, ...resto }) => ({ id: _id.toHexString(), ...resto }) as Evento)
    return { itens, proximo: temMais ? itens[itens.length - 1].em : undefined }
  }
}

/**
 * Abre uma conexão só, e devolve os armazéns que moram nela.
 *
 * Personagens e usuários são coleções do mesmo banco: abrir dois `MongoClient`
 * seria dobrar o pool de conexões para nada.
 */
export async function conectarMongo(uri: string, nomeDoBanco: string) {
  const cliente = new MongoClient(uri)
  await cliente.connect()
  const personagens = new ArmazemMongo(cliente, nomeDoBanco)
  const usuarios = new UsuariosMongo(personagens.banco)
  const eventos = new EventosMongo(personagens.banco)
  await personagens.garantirIndices()
  await usuarios.garantirIndices()
  await eventos.garantirIndices()
  return { personagens, usuarios, eventos, fechar: () => cliente.close() }
}
