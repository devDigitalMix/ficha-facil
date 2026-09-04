// Equipamento equipado — a última peça da ficha de combate.
//
// Até aqui o motor sabia tudo sobre o personagem e nada sobre o que ele está
// vestindo ou empunhando. Isso deixava três buracos, e os três eram do tipo que
// não aparece: a CA com armadura nunca era calculada, o `soma_se segurando:escudo`
// da fórmula de CA nunca ficava verdadeiro, e o bônus de ataque de uma arma estava
// escrito à mão nos personagens de ouro sem ninguém conferir.
//
// Nada aqui conhece id de item. A armadura diz a própria CA em `ca`, a arma diz o
// próprio dano em `dano`, e a regra de qual atributo usar está em
// `valores_derivados/atributo_de_ataque_da_arma`.

import type { Contexto, CalculoDeCaBase, Formula, Resultado } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { catalogo, nomeDeEntidade, trilhaLegivel } from './dataset.ts'
import { derivado, calcular } from './derivados.ts'
import type { Vocabulario } from './condicao.ts'

type Item = Record<string, unknown> & { id: string; nome?: string }

type CaDeArmadura = {
  base?: number
  bonus?: number
  soma_modificador_destreza?: boolean
  teto_do_modificador?: number
  id?: string
}
type Dano = { formula_dado?: string | null; valor_fixo?: number | null; tipo_dano?: string }
type Propriedade = { propriedade: string }

let cache: Item[] | null = null
function itens(): Item[] {
  if (!cache) cache = catalogo<Item>('itens').itens
  return cache
}

export function item(id: string): Item {
  const i = itens().find((x) => x.id === id)
  if (!i) throw new ErroDoMotor(`item inexistente: '${id}'`)
  return i
}

export type Equipado = {
  armadura?: Item
  escudo?: Item
  armas: Item[]
  outros: Item[]
}

/**
 * Um escudo se reconhece pela FORMA, não pelo nome: ele dá um `bonus` de CA, e a
 * armadura dá uma `base`. Testar `grupo === 'escudo'` seria pôr um id de conteúdo
 * dentro do motor — e a lint pegou exatamente isso na primeira versão.
 */
function ehEscudo(i: Item): boolean {
  const ca = i.ca as CaDeArmadura | undefined
  return i.categoria === 'armadura' && typeof ca?.bonus === 'number' && ca.base === undefined
}

/**
 * O item que este item TAMBÉM é.
 *
 * A tabela de Focos Druídicos (p. 225) imprime "Cajado de madeira (também um
 * Bastão)": o foco é, ao mesmo tempo, a arma Cajado — e é por isso que o Druida
 * conjura Bordão Místico segurando ele. `tambem_e` é uma referência, não uma cópia:
 * os números continuam vindo de um lugar só.
 */
export function comoArma(i: Item): Item {
  const outro = i.tambem_e
  if (typeof outro !== 'string') return i
  const alvo = item(outro)
  // O nome e o id continuam sendo os do item que está na mão — o jogador equipou o
  // Cajado de madeira, e é isso que a ficha tem de dizer.
  return { ...alvo, id: i.id, nome: i.nome, tambem_e: outro }
}

/** Separa o que está equipado pelo que o próprio item diz ser. */
export function separar(ids: string[]): Equipado {
  const eq: Equipado = { armas: [], outros: [] }
  for (const id of ids) {
    const i = comoArma(item(id))
    if (ehEscudo(i)) {
      if (eq.escudo) throw new ErroDoMotor('duas peças de escudo equipadas ao mesmo tempo')
      eq.escudo = i
    } else if (i.categoria === 'armadura') {
      if (eq.armadura) throw new ErroDoMotor('duas armaduras vestidas ao mesmo tempo')
      eq.armadura = i
    } else if (i.categoria === 'arma') {
      eq.armas.push(i)
    } else {
      eq.outros.push(i)
    }
  }
  return eq
}

/**
 * A CA que a armadura oferece, como mais um cálculo de base concorrente.
 *
 * Ela não substitui a do Monge nem a do Bárbaro: concorre com elas, e o maior
 * ganha (Ap. C, p. 363). É por isso que ela entra pela mesma porta.
 */
export function calculoDaArmadura(armadura: Item): CalculoDeCaBase {
  const ca = armadura.ca as CaDeArmadura | undefined
  if (!ca || typeof ca.base !== 'number') {
    throw new ErroDoMotor(`a armadura '${armadura.id}' não diz qual CA ela dá`)
  }
  const formula: Formula = [String(ca.base)]
  if (ca.soma_modificador_destreza) {
    ;(formula as unknown[]).push(
      typeof ca.teto_do_modificador === 'number'
        ? { op: 'min', args: ['mod:DES', String(ca.teto_do_modificador)] }
        : 'mod:DES',
    )
  }
  return { id: ca.id ?? `ca_${armadura.id}`, nome: armadura.nome as string | undefined, formula }
}

export function bonusDoEscudo(escudo: Item): number {
  const ca = escudo.ca as CaDeArmadura | undefined
  if (!ca || typeof ca.bonus !== 'number') {
    throw new ErroDoMotor(`o escudo '${escudo.id}' não diz qual bônus ele dá`)
  }
  return ca.bonus
}

// ------------------------------------------------------------------ ataques

export type Ataque = {
  arma: string
  nome: string
  atributo: string
  proficiente: boolean
  jogada: Resultado
  dano: Resultado
  tipo_dano?: string
  /** Por que este atributo, e não outro — a proveniência da escolha. */
  porque_o_atributo: string
}

function propriedades(arma: Item): Set<string> {
  return new Set(((arma.propriedades as Propriedade[]) ?? []).map((p) => p.propriedade))
}

/**
 * Qual atributo a arma usa.
 *
 * A regra mora em `valores_derivados/atributo_de_ataque_da_arma`: corpo a corpo usa
 * Força, à distância usa Destreza, e Acuidade deixa escolher entre as duas — com o
 * MESMO atributo valendo para o ataque e para o dano.
 *
 * Com Acuidade o motor devolve o maior modificador, e diz que foi ele que escolheu.
 * Escolher o pior seria absurdo, e deixar em aberto travaria a ficha; o que não pode
 * é a ficha não contar qual foi.
 */
export function atributoDaArma(arma: Item, ctx: Contexto): { atributo: string; porque: string } {
  const vd = derivado('atributo_de_ataque_da_arma') as unknown as {
    por_alcance_da_arma?: Record<string, string>
  }
  const porAlcance = vd.por_alcance_da_arma ?? {}
  const alcance = arma.alcance as string
  const padrao = porAlcance[alcance]
  if (!padrao) throw new ErroDoMotor(`alcance de arma sem regra de atributo: '${alcance}'`)

  if (propriedades(arma).has('acuidade')) {
    const forca = ctx.atributos.FOR ?? 0
    const destreza = ctx.atributos.DES ?? 0
    const escolhido = destreza > forca ? 'DES' : 'FOR'
    return {
      atributo: escolhido,
      porque: `Acuidade deixa escolher entre Força e Destreza; o motor usou ${escolhido}, ` +
        `que é o maior modificador`,
    }
  }
  return {
    atributo: padrao,
    porque: alcance === 'corpo_a_corpo' ? 'arma corpo a corpo usa Força' : 'arma à distância usa Destreza',
  }
}

/**
 * Proficiência com a arma.
 *
 * A classe não lista armas uma a uma: ela concede "armas Simples" ou "armas Marciais
 * com a propriedade Leve", que no dado são FILTROS. Guardar os filtros e testar a
 * arma contra eles é o que evita explodir 170 itens dentro da ficha.
 */
export type FiltroDeArma = Record<string, unknown>

export function proficienteComArma(arma: Item, filtros: FiltroDeArma[]): boolean {
  return filtros.some((f) =>
    Object.entries(f).every(([k, v]) => {
      if (k === 'categoria') return arma.categoria === v
      if (k === 'grupo') return Array.isArray(v) ? v.includes(arma.grupo) : arma.grupo === v
      if (k === 'alguma_propriedade') {
        const tem = propriedades(arma)
        return (v as string[]).some((p) => tem.has(p))
      }
      if (k === 'id') return Array.isArray(v) ? v.includes(arma.id) : arma.id === v
      return arma[k] === v
    }),
  )
}

/** O ataque e o dano de uma arma equipada. */
export function ataqueComArma(
  arma: Item,
  ctx: Contexto,
  filtros: FiltroDeArma[],
  vocabulario?: Vocabulario,
): Ataque {
  const { atributo, porque } = atributoDaArma(arma, ctx)
  const proficiente = proficienteComArma(arma, filtros)
  const dano = arma.dano as Dano | undefined
  if (!dano) throw new ErroDoMotor(`a arma '${arma.id}' não diz o dano que causa`)

  // O contexto ganha os dois termos que as fórmulas do livro pedem por indireção:
  // "o atributo de ataque da arma" e "o dado de dano da arma".
  const ctxDaArma: Contexto = {
    ...ctx,
    atributos: { ...ctx.atributos, atributo_de_ataque_da_arma: ctx.atributos[atributo] ?? 0 },
    predicados_ativos: [
      ...(ctx.predicados_ativos ?? []),
      ...(proficiente ? ['proficiente_em:arma_do_ataque'] : []),
    ],
    extras_dados: {
      ...(ctx.extras_dados ?? {}),
      ...(typeof dano.formula_dado === 'string' ? { dado_de_dano_da_arma: dano.formula_dado } : {}),
    },
  }

  const jogada = calcular('jogada_de_ataque_com_arma', ctxDaArma, {}, vocabulario)

  // Dano de valor fixo sem dado (a Zarabatana causa 1) NÃO soma o modificador de
  // atributo — está na nota do próprio valor derivado, p. 29.
  const temDado = typeof dano.formula_dado === 'string' && dano.formula_dado.length > 0
  const danoResultado = temDado
    ? calcular('dano_de_arma', ctxDaArma, {}, vocabulario)
    : {
        valor: dano.valor_fixo ?? 0,
        dados: [],
        parcelas: [{ rotulo: 'dano fixo', valor: dano.valor_fixo ?? 0 }],
      }

  return {
    arma: arma.id,
    nome: (arma.nome as string) ?? arma.id,
    atributo,
    proficiente,
    jogada,
    dano: danoResultado,
    tipo_dano: dano.tipo_dano,
    porque_o_atributo: porque,
  }
}

/**
 * O Ataque Desarmado, que todo mundo tem.
 *
 * Por padrão é 1 + Força (Ap. C, p. 361). O Monge troca as duas coisas: o atributo,
 * por um `substituir_atributo`, e o dado, por um `dado_de_dano` que vem da coluna
 * Artes Marciais. As duas trocas são efeito no dado — o motor não sabe quem é Monge.
 */
/**
 * De onde veio o dado, em uma frase curta.
 *
 * `origem` é a trilha que o coletor montou ("classe guerreiro / nível 1 /
 * estilo_de_luta / …"). O último trecho que não é um id de escolha é o que nomeia a
 * coisa; na falta de qualquer um, o rótulo genérico é honesto e não inventa nome.
 */
function rotuloDoDado(origem?: string): string {
  if (!origem) return 'dado de dano'
  // O trecho MAIS ESPECÍFICO da trilha: quem concedeu o dado é a característica,
  // não a classe que a contém. Aqui, ao contrário da lista de magias, a trilha
  // inteira só faria a parcela crescer sem dizer nada de novo. Um id que não
  // nomeia nada não vira rótulo — melhor o genérico do que
  // 'guerreiro_estilo_de_luta' na cara de quem joga.
  const nomes = trilhaLegivel(origem)
  const ultimo = nomes[nomes.length - 1]
  return ultimo ? `dado de ${ultimo}` : 'dado de dano'
}

export function ataqueDesarmado(
  ctx: Contexto,
  trocas: { de: string; para: string }[],
  dadoDeDano: { dado: string; origem?: string } | undefined,
  vocabulario?: Vocabulario,
): Ataque {
  // Mesmo cuidado do dado: se mais de um efeito troca o atributo do Ataque
  // Desarmado, quem decide não pode ser a ordem de declaração. Vale o que dá o
  // maior modificador — que é o que qualquer jogador escolheria.
  const candidatas = trocas.filter((t) => t.de === 'FOR')
  const troca = candidatas.reduce<{ de: string; para: string } | undefined>(
    (melhor, t) =>
      melhor === undefined || (ctx.atributos[t.para] ?? 0) > (ctx.atributos[melhor.para] ?? 0)
        ? t
        : melhor,
    undefined,
  )
  const atributo = troca?.para ?? 'FOR'

  const ctxDesarmado: Contexto = {
    ...ctx,
    atributos: { ...ctx.atributos, FOR_do_desarmado: ctx.atributos[atributo] ?? 0 },
  }
  const bp = calcular('jogada_de_ataque_desarmado', { ...ctxDesarmado, atributos: { ...ctxDesarmado.atributos, FOR: ctx.atributos[atributo] ?? 0 } }, {}, vocabulario)

  const modificador = Math.floor(((ctx.atributos[atributo] ?? 0) - 10) / 2)
  const dano: Resultado = dadoDeDano
    ? {
        valor: modificador,
        dados: [dadoDeDano.dado],
        parcelas: [
          // O rótulo era 'dado de Artes Marciais' fixo — o nome da característica do
          // MONGE, aparecendo na ficha de um Guerreiro com Combate Desarmado. Agora
          // sai de onde o dado veio.
          { rotulo: rotuloDoDado(dadoDeDano.origem), valor: dadoDeDano.dado },
          // O NOME do atributo, como na proveniência dos derivados: "Força", não "FOR".
          { rotulo: nomeDeEntidade(atributo) ?? atributo, valor: modificador },
        ],
      }
    : calcular('dano_desarmado', { ...ctx, atributos: { ...ctx.atributos, FOR: ctx.atributos[atributo] ?? 0 } }, {}, vocabulario)

  return {
    arma: 'ataque_desarmado',
    nome: 'Ataque Desarmado',
    atributo,
    proficiente: true,
    jogada: bp,
    dano,
    tipo_dano: (derivado('dano_desarmado') as unknown as { tipo_dano?: string }).tipo_dano,
    porque_o_atributo: troca
      ? `um efeito troca ${troca.de} por ${troca.para} no Ataque Desarmado`
      : 'Ataque Desarmado usa Força',
  }
}
