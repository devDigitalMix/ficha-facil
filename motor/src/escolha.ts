// Motor de escolha — passo 4 do PLANO-MOTOR.
//
// O passo 3 aceita a escolha já resolvida e lista as que faltam. Este passo é quem
// **oferece as opções** e **recusa a inválida**. É o coração do app: criar
// personagem e subir de nível são, os dois, resolver escolhas.
//
// A regra de sempre: nenhum id de conteúdo aqui. O que uma escolha oferece está em
// `de` — `chaves`, `todo_o_catalogo`, `filtro`, `de_variantes` — e é o dado que diz.
//
// A parte que só o motor sabe fazer são os FILTROS DE RUNTIME. O `validar.py` os
// lista em `FILTROS_DE_RUNTIME` e não os avalia, de propósito: eles dependem do
// personagem, não do catálogo. Aqui eles finalmente são avaliados — e um filtro que
// não devolve nada vira problema declarado, não uma lista vazia silenciosa.

import type { Contexto } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { catalogo, lerJson } from './dataset.ts'
import type { Efeito, Pendencia } from './colecao.ts'
import { avaliar } from './formula.ts'

type Item = Record<string, unknown> & { id: string; nome?: string }

/** Um catálogo pode estar em `catalogos/` ou ser uma coleção da raiz de `dados/`. */
const RAIZ = new Set(['acoes', 'caracteristicas', 'classes', 'condicoes', 'subclasses'])

const cache = new Map<string, Item[]>()
function itensDe(cat: string): Item[] {
  if (!cache.has(cat)) {
    const doc = RAIZ.has(cat)
      ? lerJson<{ itens: Item[] }>(`${cat}.json`)
      : catalogo<Item>(cat)
    cache.set(cat, doc.itens)
  }
  return cache.get(cat)!
}

export type Opcao = { id: string; nome?: string }

export type Oferta = {
  escolha_id: string
  rotulo: string
  quantidade: number
  opcoes: Opcao[]
  /** Filtros que este motor ainda não sabe avaliar — declarados, não escondidos. */
  nao_avaliados: string[]
  reescolhivel: boolean
  /**
   * Escolha que só pode ser oferecida depois de outra: os truques do Iniciado em
   * Magia dependem da lista escolhida. Enquanto isso não estiver resolvido, oferecer
   * o catálogo inteiro seria oferecer o que o jogador não pode pegar.
   */
  bloqueada_por?: string
  /** Catálogo de onde saíram as opções, para quem quiser descrever cada uma. */
  catalogo?: string
  /** Os que o livro recomenda, na ordem em que ele os lista. */
  recomendados?: string[]
}

/** Variáveis que uma escolha resolvida definiu, para outra escolha ler. */
export type Variaveis = Record<string, string>

/**
 * O que cada FONTE acumulou.
 *
 * Uma fonte é um conjunto que o personagem monta e do qual depois escolhe: o livro
 * de magias do Mago é o caso do livro (p. 147). Quem alimenta a fonte declara
 * `alimenta: "<fonte>"` na escolha; quem tira dela declara `de: { fonte: "<fonte>" }`.
 * Nenhum lado cita o outro por id — é o mesmo desenho das portas.
 */
export type Fontes = Record<string, string[]>

/**
 * O que há de errado com uma escolha resolvida.
 *
 * `tipo` existe para quem consome distinguir duas coisas que não são a mesma:
 * escolher uma opção proibida é **defeito** — a construção não pode ser aceita —,
 * mas ter escolhido menos do que agora se pede é **pendência**. Subir de nível
 * produz a segunda o tempo todo: a Clériga que preparava 9 magias no nível 5 passa
 * a preparar 10 no 6, e isso não torna a ficha dela inválida, torna incompleta.
 *
 * Sem esta distinção o backend teria de adivinhar pela frase da queixa.
 */
export type TipoDeProblema =
  | 'opcao_invalida'
  | 'incompleta'
  | 'excedente'
  | 'repetida'
  | 'dependencia_nao_resolvida'

export type Problema = {
  escolha_id: string
  tipo: TipoDeProblema
  queixa: string
  /** Só em 'incompleta' e 'excedente': quantas faltam (ou sobram, negativo). */
  faltam?: number
}

/** Pendência é o que o jogador ainda tem de fazer; o resto é defeito de construção. */
export function ehPendencia(p: Problema): boolean {
  return p.tipo === 'incompleta' || p.tipo === 'dependencia_nao_resolvida'
}

// ------------------------------------------------------------------ quantidade

/**
 * Quantas opções esta escolha pede.
 *
 * O dado usa quatro formas: número, `coluna:<x>` (a tabela da classe),
 * `quantidade_por_nivel` e uma lista (a escolha de N coisas diferentes).
 */
export function quantidadeDe(e: Efeito, ctx: Contexto): number {
  const q = e.quantidade

  if (typeof q === 'number') return q
  if (Array.isArray(q)) return q.length

  if (typeof q === 'string') {
    if (q.startsWith('coluna:') || q.startsWith('coluna_conjuracao:')) {
      const chave = q.slice(q.indexOf(':') + 1)
      const v = ctx.colunas?.[chave]
      if (typeof v === 'number') return v
      throw new ErroDoMotor(`a coluna '${chave}' não dá um número para a quantidade`)
    }
    // formas que dependem de estado de jogo, não da ficha: quem chama decide
    throw new ErroDoMotor(`quantidade '${q}' depende de estado de jogo, não da ficha`)
  }

  const porNivel = e.quantidade_por_nivel as Record<string, number> | undefined
  if (porNivel) {
    const niveis = Object.keys(porNivel)
      .map(Number)
      .filter((n) => n <= ctx.nivel_do_personagem)
      .sort((a, b) => a - b)
    if (niveis.length) return porNivel[String(niveis[niveis.length - 1])]
    return 0
  }

  throw new ErroDoMotor(`escolha '${e.id}' sem quantidade que o motor saiba ler`)
}

// ------------------------------------------------------------------ opções

const RUNTIME = new Set([
  'circulo_com_espaco_disponivel',
  'proficiente',
  'ainda_nao_especialista',
  'com_proficiencia',
  'pre_requisitos_atendidos',
  'nd_maximo',
  'sem_deslocamento_de_voo',
  'exceto',
  'alguma',
  'id',
])

/** Casa um item contra uma chave de filtro de catálogo. */
function casaCampo(item: Item, k: string, v: unknown): boolean {
  const igual = (a: unknown, b: unknown) => (Array.isArray(b) ? b.includes(a as never) : a === b)

  switch (k) {
    case 'nivel':
      return item.nivel === v
    case 'nivel_minimo':
      return typeof item.nivel === 'number' && item.nivel >= (v as number)
    case 'nivel_maximo':
      return typeof item.nivel === 'number' && item.nivel <= (v as number)
    case 'circulo_maximo':
      return typeof item.nivel === 'number' && item.nivel <= (v as number)
    case 'lista': {
      const minhas = new Set((item.listas as string[]) ?? [])
      const alvo = typeof v === 'string' ? [v] : (v as string[])
      return alvo.some((l) => minhas.has(l))
    }
    case 'alguma_propriedade': {
      const tem = new Set(
        ((item.propriedades as { propriedade: string }[]) ?? []).map((p) => p.propriedade),
      )
      return (v as string[]).some((p) => tem.has(p))
    }
    default:
      return igual(item[k], v)
  }
}

/** Filtros que dependem do personagem — os que o validador delega ao motor. */
function casaRuntime(item: Item, k: string, v: unknown, ctx: Contexto): boolean {
  switch (k) {
    case 'id':
      return Array.isArray(v) ? v.includes(item.id) : item.id === v
    case 'exceto': {
      const fora = Array.isArray(v) ? (v as string[]) : [v as string]
      return !fora.includes(item.id)
    }
    case 'proficiente':
    case 'com_proficiencia': {
      const tem = proficienteEm(item.id, ctx)
      return tem === Boolean(v)
    }
    case 'ainda_nao_especialista':
      // especialização ainda não é estado que o motor guarde; oferecer a mais é
      // melhor que esconder — e o problema fica declarado em `nao_avaliados`
      return true
    case 'nd_maximo': {
      const nd = (item.nivel_de_desafio as { valor?: number } | undefined)?.valor
      return typeof nd === 'number' ? nd <= (v as number) : true
    }
    case 'sem_deslocamento_de_voo': {
      const desl = (item.deslocamentos as { tipo: string }[]) ?? []
      const voa = desl.some((d) => d.tipo === 'voo')
      return v ? !voa : true
    }
    case 'alguma': {
      const ramos = v as Record<string, unknown>[]
      return ramos.some((r) => Object.entries(r).every(([k2, v2]) => casaUma(item, k2, v2, ctx)))
    }
    default:
      return true
  }
}

function casaUma(item: Item, k: string, v: unknown, ctx: Contexto): boolean {
  return RUNTIME.has(k) ? casaRuntime(item, k, v, ctx) : casaCampo(item, k, v)
}

/** O maior círculo para o qual o personagem tem espaço; 0 quando não tem nenhum. */
export function maiorCirculoComEspaco(ctx: Contexto): number {
  let maior = 0
  for (let c = 1; c <= 9; c++) {
    const n = ctx.colunas?.[`espacos_${c}`]
    if (typeof n === 'number' && n > 0) maior = c
  }
  return maior
}

function proficienteEm(id: string, ctx: Contexto): boolean {
  const p = ctx.proficiencias
  return Boolean(
    p?.pericias?.includes(id) || p?.ferramentas?.includes(id) || p?.salvaguardas?.includes(id),
  )
}

/**
 * O que esta escolha oferece.
 *
 * Devolve também `nao_avaliados`: as chaves de filtro que dependem de estado de jogo
 * que o motor ainda não guarda (espaços de magia gastos, especialização). Elas não
 * recortam a lista — e, por não recortarem, ficam ditas em voz alta em vez de virar
 * uma lista silenciosamente maior do que deveria.
 */
export function opcoesDe(
  e: Efeito,
  ctx: Contexto,
  variaveis: Variaveis = {},
  fontes: Fontes = {},
): Oferta {
  const id = e.id as string

  // Depende de outra escolha que ainda não foi feita: não se oferece nada, e se diz
  // por quê. Uma lista completa aqui seria pior que uma lista vazia.
  const dep = e.depende_de as string | undefined
  if (dep && !(nomeDaVariavelDe(dep) in variaveis) && !(dep in variaveis)) {
    return { ...oferta(e, ctx, [], []), bloqueada_por: dep }
  }
  const de = (e.de ?? {}) as Record<string, unknown>
  const cat = de.catalogo as string
  if (!cat) throw new ErroDoMotor(`escolha '${id}' não diz de que catálogo tira as opções`)

  let itens = itensDe(cat)
  const naoAvaliados: string[] = []

  // 0. a fonte: o conjunto que o personagem montou antes.
  //
  // "Escolha quatro magias DO SEU LIVRO DE MAGIAS" (p. 148) não é um recorte do
  // catálogo: é um recorte do que ficou resolvido nas escolhas que alimentam o
  // livro. Enquanto o livro está vazio, esta escolha não tem o que oferecer — e
  // dizer isso é melhor que devolver lista vazia calada, que foi exatamente o
  // sintoma relatado ("não aparecem as magias para preparar").
  const fonte = de.fonte as string | undefined
  if (fonte) {
    const dentro = new Set(fontes[fonte] ?? [])
    if (!dentro.size) return { ...oferta(e, ctx, [], []), bloqueada_por: fonte }
    itens = itens.filter((i) => dentro.has(i.id))
  }

  // 1. seleção direta por chaves
  if (Array.isArray(de.chaves)) {
    const chaves = new Set(de.chaves as string[])
    itens = itens.filter((i) => chaves.has(i.id))
    const faltando = [...chaves].filter((k) => !itens.some((i) => i.id === k))
    if (faltando.length) {
      throw new ErroDoMotor(`escolha '${id}': chave inexistente em '${cat}': ${faltando.join(', ')}`)
    }
  }

  // 2. união com outro catálogo
  if (typeof de.tambem_de === 'string') {
    itens = [...itens, ...itensDe(de.tambem_de)]
  }

  // 3. filtro
  for (const fonte of [de.filtro, de.filtro_adicional, e.filtro_adicional]) {
    if (!fonte || typeof fonte !== 'object') continue
    for (const [k, v] of Object.entries(fonte as Record<string, unknown>)) {
      let valor = v
      // `coluna:<x>` num filtro é a tabela da classe, exatamente como na quantidade.
      // Sem resolver aqui, o Bruxo comparava `nivel <= "coluna:circulo_dos_espacos"`
      // — falso para toda magia — e a lista de preparadas saía vazia.
      if (typeof v === 'string' && v.startsWith('coluna:')) {
        const n = ctx.colunas?.[v.slice('coluna:'.length)]
        if (typeof n !== 'number') {
          naoAvaliados.push(k)
          continue
        }
        valor = n
      }
      if (typeof v === 'string' && v.startsWith('$')) {
        const resolvido = variaveis[v.slice(1)]
        if (resolvido === undefined) {
          naoAvaliados.push(k) // a variável ainda não foi definida por ninguém
          continue
        }
        valor = resolvido
      }
      if (k === 'ainda_nao_especialista') {
        naoAvaliados.push(k)
        continue
      }
      if (k === 'circulo_com_espaco_disponivel') {
        // "de um círculo para o qual você possui espaços de magia" (p. 85). O motor
        // sabe responder: os espaços estão na tabela da classe, e a tabela está no
        // contexto. Era um dos filtros que o validador delegava e ninguém avaliava.
        const teto = maiorCirculoComEspaco(ctx)
        if (teto === 0) {
          naoAvaliados.push(k) // o personagem não tem espaço nenhum: não é recorte
          continue
        }
        itens = itens.filter(
          (i) => typeof i.nivel === 'number' && i.nivel >= 1 && i.nivel <= teto,
        )
        continue
      }
      if (k === 'pre_requisitos_atendidos') {
        itens = itens.filter((i) => preRequisitosAtendidos(i, ctx))
        continue
      }
      itens = itens.filter((i) => casaUma(i, k, valor, ctx))
    }
  }

  // 4. nível mínimo do próprio item (opções que só abrem em certo nível)
  if (de.respeitar_nivel_minimo) {
    itens = itens.filter(
      (i) => typeof i.nivel_minimo !== 'number' || i.nivel_minimo <= ctx.nivel_do_personagem,
    )
  }
  if (de.respeitar_pre_requisitos) {
    itens = itens.filter((i) => preRequisitosAtendidos(i, ctx))
  }

  // 5. variantes: a escolha não é entre itens, é entre as formas de um item
  if (de.de_variantes) {
    const variantes: Opcao[] = []
    for (const i of itens) {
      for (const v of (i.variantes as Item[]) ?? []) {
        variantes.push({ id: v.id, nome: v.nome as string })
      }
    }
    return oferta(e, ctx, variantes, naoAvaliados)
  }

  return oferta(
    e,
    ctx,
    itens.map((i) => ({ id: i.id, nome: i.nome as string })),
    naoAvaliados,
  )
}

/** O nome da variável que uma escolha define, quando ela define alguma. */
export function nomeDaVariavelDe(escolhaId: string): string {
  return escolhaId
}

function oferta(e: Efeito, ctx: Contexto, opcoes: Opcao[], naoAvaliados: string[]): Oferta {
  const de = (e.de ?? {}) as Record<string, unknown>
  const recomendados = (e.recomendados ?? e.recomendadas) as string[] | undefined
  return {
    escolha_id: e.id as string,
    rotulo: (e.rotulo as string) ?? (e.id as string),
    quantidade: quantidadeDe(e, ctx),
    opcoes,
    nao_avaliados: [...new Set(naoAvaliados)],
    reescolhivel: Boolean(e.reescolhivel),
    // De onde vieram as opções, e quais o livro sugere. O motor não descreve magia
    // nem talento — quem quiser a descrição busca no compêndio, e para isso precisa
    // saber em que catálogo procurar. Sem este campo a tela teria de adivinhar pelo
    // id da escolha, que é exatamente o conhecimento de conteúdo que não pode subir.
    catalogo: typeof de.catalogo === 'string' ? de.catalogo : undefined,
    ...(recomendados?.length ? { recomendados } : {}),
  }
}

/** Pré-requisitos de talento: nível de personagem, nível de classe, valor de atributo. */
export function preRequisitosAtendidos(item: Item, ctx: Contexto): boolean {
  const pres = (item.pre_requisitos as Record<string, unknown>[]) ?? []
  return pres.every((p) => {
    switch (p.tipo) {
      case 'nivel_de_personagem':
        return ctx.nivel_do_personagem >= (p.minimo as number)
      case 'nivel_de_classe':
        return (ctx.niveis_por_classe[p.classe as string] ?? 0) >= (p.minimo as number)
      case 'valor_de_atributo': {
        const atrs = (p.atributos as string[]) ?? []
        return atrs.some((a) => (ctx.atributos[a] ?? 0) >= (p.minimo as number))
      }
      case 'treinamento_com_armadura':
      case 'caracteristica':
      case 'invocacao':
      case 'ferramenta':
      case 'magia_conhecida':
      case 'estado':
        // dependem do que o personagem TEM, e isso é o passo seguinte. Oferecer a
        // mais e deixar claro é melhor que esconder uma opção legítima.
        return true
      default:
        throw new ErroDoMotor(`pré-requisito de tipo desconhecido: '${String(p.tipo)}'`)
    }
  })
}

// ------------------------------------------------------------------ validação

/**
 * Confere uma escolha resolvida contra o que ela oferece.
 *
 * Devolve a lista de queixas — vazia quer dizer que está boa. Não lança: quem monta
 * personagem quer ver TODOS os problemas de uma vez, não o primeiro.
 */
export function conferirEscolha(
  e: Efeito,
  resolvida: unknown,
  ctx: Contexto,
  variaveis: Variaveis = {},
  fontes: Fontes = {},
): Problema[] {
  const id = e.id as string
  const problemas: Problema[] = []
  const of = opcoesDe(e, ctx, variaveis, fontes)
  if (of.bloqueada_por) {
    return [{
      escolha_id: id,
      tipo: 'dependencia_nao_resolvida',
      queixa: `depende de '${of.bloqueada_por}', que não foi resolvida`,
    }]
  }
  const validos = new Set(of.opcoes.map((o) => o.id))

  const escolhidos =
    typeof resolvida === 'string'
      ? [resolvida]
      : Array.isArray(resolvida)
        ? (resolvida as string[])
        : [(resolvida as { escolhido: string }).escolhido]

  for (const x of escolhidos) {
    if (!validos.has(x)) {
      problemas.push({
        escolha_id: id,
        tipo: 'opcao_invalida',
        queixa: `'${x}' não está entre as opções de '${of.rotulo}'`,
      })
    }
  }
  if (escolhidos.length !== of.quantidade) {
    const faltam = of.quantidade - escolhidos.length
    problemas.push({
      escolha_id: id,
      tipo: faltam > 0 ? 'incompleta' : 'excedente',
      faltam,
      queixa: `'${of.rotulo}' pede ${of.quantidade} e recebeu ${escolhidos.length}`,
    })
  }
  if (new Set(escolhidos).size !== escolhidos.length) {
    problemas.push({
      escolha_id: id,
      tipo: 'repetida',
      queixa: `'${of.rotulo}' recebeu a mesma opção duas vezes`,
    })
  }
  return problemas
}

// ------------------------------------------------------- checklist de subir de nível

export type ItemDeChecklist = Oferta & { origem: string }

/** As escolhas em aberto, já com as opções — é a tela de subir de nível. */
export function checklist(
  pendencias: Pendencia[],
  escolhasPorId: Map<string, Efeito>,
  ctx: Contexto,
  variaveis: Variaveis = {},
  fontes: Fontes = {},
): ItemDeChecklist[] {
  return pendencias
    .map((p) => {
      const e = escolhasPorId.get(p.escolha_id)
      if (!e) throw new ErroDoMotor(`pendência sem a escolha correspondente: '${p.escolha_id}'`)
      return { ...opcoesDe(e, ctx, variaveis, fontes), origem: p.origem }
    })
    // Escolha que neste nível pede zero não é pendência: a expansão do livro de
    // magias só começa no nível 2, e "escolha 0 magias" no nível 1 é ruído na tela.
    .filter((i) => i.quantidade > 0)
}

export { avaliar }
