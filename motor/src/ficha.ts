// A ficha estática: o que o passo 2 do PLANO-MOTOR fecha.
//
// Entra um Contexto, sai a parte da ficha que não depende de escolha em aberto nem
// de efeito ainda não coletado: modificadores, Bônus de Proficiência, CA, Pontos de
// Vida máximos, Iniciativa, Percepção Passiva, salvaguardas, testes de perícia e
// Deslocamento. Cada número vem com a proveniência, porque é o que o app promete
// mostrar ("CA 17 = 10 + 3 DES + 4 SAB").
//
// O que este arquivo NÃO faz: coletar efeito (passo 3) e resolver escolha (passo 4).
// Enquanto isso não existe, o Contexto vem pronto — dos personagens de ouro.

import type { Contexto, Recurso, Resultado } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { avaliar, bonusDeProficiencia, modificadorDeAtributo } from './formula.ts'
import { calcular } from './derivados.ts'
import { catalogo, entidadesDaTrilha, trilhaLegivel } from './dataset.ts'
import { condicaoVale, type Vocabulario } from './condicao.ts'
import { separar, ataqueComArma, ataqueDesarmado, type Ataque } from './equipamento.ts'

const ATRIBUTOS = ['FOR', 'DES', 'CON', 'INT', 'SAB', 'CAR']

/**
 * Uma magia como a ficha a mostra.
 *
 * A ficha NÃO descreve a magia: quem quiser o texto busca em `magias.json` pelo
 * id, como já faz com talento e item. O que está aqui é o que só o motor sabe —
 * de onde ela veio, em que modo, com que atributo, e se gasta espaço.
 */
export type MagiaNaFicha = {
  id: string
  nome: string
  /** 0 é truque. É por ele que se sabe qual espaço a magia gasta. */
  circulo: number
  /** 'conhecida' | 'no_livro' | 'preparada' | 'sempre_preparada' … */
  modo: string
  /** Legível: "Iniciado em Magia", não `talento iniciado_em_magia`. */
  origem: string
  atributo_de_conjuracao?: string
  nao_conta_para_o_limite?: boolean
  /** Truque e magia sempre preparada estão prontos; o resto depende do modo. */
  pronta_para_conjurar: boolean
}

/**
 * Uma característica, traço ou talento que o personagem tem.
 *
 * A ficha não decide o que é digno de aparecer: aparece o que INCIDE, e o que
 * incide é o que a coleta encontrou. `de` é a trilha legível ("Draconato", "Acólito
 * · Iniciado em Magia") para quem lê saber por que aquilo está ali.
 */
export type CaracteristicaNaFicha = {
  id: string
  nome: string
  /** 'caracteristica' | 'traco' | 'talento' — de que arquivo do dataset ela veio. */
  familia: string
  descricao_curta?: string
  fonte?: unknown
  de: string
}

export type Ficha = {
  /**
   * A PONTUAÇÃO de cada atributo, já com tudo somado: os aumentos do antecedente,
   * os do talento, os do Aumento no Valor de Atributo. É o que vai na ficha ao
   * lado do modificador — quem joga confere os dois, e só o modificador não deixa
   * conferir nada.
   */
  atributos: Record<string, number>
  modificadores: Record<string, number>
  bonus_de_proficiencia: number
  classe_de_armadura: Resultado
  pontos_de_vida_maximos: Resultado
  iniciativa: Resultado
  percepcao_passiva: Resultado
  salvaguardas: Record<string, number>
  testes_de_pericia: Record<string, number>
  deslocamento_m: number
  /** O Ataque Desarmado sempre entra; as armas equipadas, se houver. */
  ataques: Ataque[]
  /**
   * As magias do personagem, de todas as fontes: as da classe e as que um talento
   * ou antecedente destravou. Vazia para quem não tem nenhuma.
   */
  magias: MagiaNaFicha[]
  /**
   * O que se gasta e volta num descanso: Fúrias, Ataque de Sopro, Canalizar
   * Divindade. O máximo já vem calculado; quanto se gastou é estado do personagem.
   */
  recursos: Recurso[]
  /** As características, traços e talentos que este personagem de fato tem. */
  caracteristicas: CaracteristicaNaFicha[]
  /** Só para quem conjura. Fora isso, ausente — e não zero. */
  conjuracao?: {
    atributo: string
    cd_para_evitar_sua_magia: Resultado
    jogada_de_ataque_magico: Resultado
    /** Espaços por círculo, do círculo 1 para cima; zero não entra. */
    espacos: Record<number, number>
    magias_preparadas: number
    truques: number
  }
}

/**
 * O melhor de vários dados de dano — e de onde ele vem.
 *
 * Compara pela média (`n × (faces+1) / 2`), que é a ordem certa mesmo entre
 * quantidades diferentes: 2d4 (média 5) ganha de 1d8 (média 4,5). Comparar só as
 * faces erraria isso.
 */
export function maiorDado(
  candidatos: { dado: string; origem?: string }[],
): { dado: string; origem?: string } | undefined {
  let melhor: { dado: string; origem?: string } | undefined
  let melhorMedia = -Infinity
  for (const c of candidatos) {
    const m = /^(\d*)d(\d+)$/.exec(c.dado.trim())
    // dado que não é 'NdM' não entra na comparação; ele vira o escolhido só se
    // for o único, para não sumir calado
    const media = m ? (Number(m[1] || 1) * (Number(m[2]) + 1)) / 2 : -1
    if (media > melhorMedia) {
      melhorMedia = media
      melhor = c
    }
  }
  return melhor
}

export function montarFicha(
  ctx: Contexto,
  vocabulario?: Vocabulario,
  equipamentoEquipado: string[] = [],
): Ficha {
  const bp = bonusDeProficiencia(ctx)

  const atributos: Record<string, number> = {}
  const modificadores: Record<string, number> = {}
  for (const a of ATRIBUTOS) {
    const v = ctx.atributos?.[a]
    if (v === undefined) throw new ErroDoMotor(`atributo ausente no contexto: '${a}'`)
    atributos[a] = v
    modificadores[a] = modificadorDeAtributo(v)
  }

  const salvaguardas: Record<string, number> = {}
  const profSalv = new Set(ctx.proficiencias?.salvaguardas ?? [])
  for (const a of ATRIBUTOS) salvaguardas[a] = modificadores[a] + (profSalv.has(a) ? bp : 0)

  return {
    atributos,
    modificadores,
    bonus_de_proficiencia: bp,
    classe_de_armadura: calcular('classe_de_armadura', ctx, {}, vocabulario),
    pontos_de_vida_maximos: pontosDeVidaMaximos(ctx, vocabulario),
    iniciativa: calcular('iniciativa', ctx, {}, vocabulario),
    percepcao_passiva: calcular('percepcao_passiva', ctx, {}, vocabulario),
    salvaguardas,
    testes_de_pericia: {},
    deslocamento_m: deslocamento(ctx, vocabulario),
    ataques: ataques(ctx, equipamentoEquipado, vocabulario),
    magias: magias(ctx),
    // O contexto já os calculou: a ficha só os repassa, em ordem estável.
    recursos: [...(ctx.recursos ?? [])].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR')),
    caracteristicas: caracteristicas(ctx),
    conjuracao: conjuracao(ctx, vocabulario),
  }
}

/**
 * Os ataques da ficha.
 *
 * O Ataque Desarmado entra sempre — todo mundo tem, e é ele que o Monge transforma.
 * As armas equipadas entram depois, cada uma com o atributo que ela usa e se o
 * personagem é proficiente com ela.
 */
export function ataques(
  ctx: Contexto,
  equipamentoEquipado: string[],
  vocabulario?: Vocabulario,
): Ataque[] {
  const eq = separar(equipamentoEquipado)
  const filtros = ctx.proficiencias?.armas ?? []

  const trocas = (ctx.substituicoes_de_atributo ?? [])
    .filter((t) => t.aplica_a.includes('ataque_desarmado') && t.escopo.includes('jogada_de_ataque'))
    .map((t) => ({ de: t.de, para: t.para }))
  // O MAIOR, não o primeiro.
  //
  // Mais de um dado pode valer ao mesmo tempo: o Combate Desarmado dá 1d6 e também
  // 1d8 com as mãos livres, e ambos passam na condição quando as mãos estão livres.
  // Pegar o primeiro da lista mostrava 1d6 a quem tinha direito a 1d8 — e a ordem
  // era a de declaração no dado, que não quer dizer nada. Os dois são
  // `substitui_a_criterio_do_jogador`: o critério razoável é o melhor disponível.
  const dadoDesarmado = maiorDado(
    (ctx.dados_de_dano ?? []).filter((d) => d.escopo.includes('ataque_desarmado')),
  )

  return [
    ataqueDesarmado(ctx, trocas, dadoDesarmado, vocabulario),
    ...eq.armas.map((a) => ataqueComArma(a, ctx, filtros, vocabulario)),
  ]
}

/**
 * As famílias que a aba de detalhes lista.
 *
 * Classe, subclasse, espécie e antecedente também aparecem nas trilhas, e ficam de
 * fora: quem o personagem É já está no cabeçalho da ficha. O que falta ver é o que
 * ele SABE FAZER.
 */
const FAMILIAS_DE_CARACTERISTICA = new Set(['caracteristica', 'traco', 'talento'])

/**
 * As características, traços e talentos do personagem.
 *
 * Não existe lista mantida à mão: elas saem das trilhas de origem dos efeitos que
 * incidem. Um talento novo no dataset aparece aqui sozinho, e uma característica
 * que só vale em Fúria não aparece com a Fúria desligada — que é a resposta certa,
 * porque a ficha mostra o personagem como ele está agora.
 */
export function caracteristicas(ctx: Contexto): CaracteristicaNaFicha[] {
  const porId = new Map<string, CaracteristicaNaFicha>()
  for (const origem of ctx.origens_ativas ?? []) {
    const trilha = entidadesDaTrilha(origem)
    for (const e of trilha) {
      if (!FAMILIAS_DE_CARACTERISTICA.has(e.familia) || porId.has(e.id)) continue
      // O "de" é a trilha ATÉ ela, sem ela: "Draconato", "Acólito · Iniciado em
      // Magia". Repetir o próprio nome no rótulo de origem não diria nada.
      const antes = trilha.slice(0, trilha.indexOf(e)).map((x) => x.nome)
      porId.set(e.id, {
        id: e.id,
        nome: e.nome,
        familia: e.familia,
        ...(e.descricao_curta ? { descricao_curta: e.descricao_curta } : {}),
        ...(e.fonte !== undefined ? { fonte: e.fonte } : {}),
        de: antes.join(' · '),
      })
    }
  }
  return [...porId.values()].sort(
    (a, b) => a.de.localeCompare(b.de, 'pt-BR') || a.nome.localeCompare(b.nome, 'pt-BR'),
  )
}

/**
 * Modos que já entregam a magia pronta para lançar.
 *
 * 'no_livro' NÃO está aqui de propósito: magia escrita no livro do Mago ainda
 * precisa ser preparada, e a ficha que a mostrasse como pronta mentiria. É o
 * outro lado da queixa "as magias do talento não aparecem" — o remédio não pode
 * ser mostrar tudo como se estivesse pronto.
 */
const MODOS_PRONTOS = new Set(['conhecida', 'preparada', 'sempre_preparada'])

/**
 * As magias do personagem, com de onde vieram.
 *
 * A queixa que originou isto: o truque e a magia pegos por Iniciado em Magia
 * existiam na construção e não apareciam em canto nenhum da ficha, porque o
 * efeito que os destrava caía em `nao_consumidos` e ninguém o lia. Agora todos
 * entram, e o `modo` diz em que condição cada um está — o que também resolve o
 * risco oposto: um truque de talento não é "preparável" e não deve aparecer
 * misturado com os que se preparam no descanso.
 *
 * Duas fontes podem dar a MESMA magia (o Clérigo que pega Curar Ferimentos por
 * Iniciado em Magia já a tinha na lista). Fica uma linha só, com o modo mais
 * forte — mas as origens somadas, porque o jogador precisa saber que gastou uma
 * escolha do talento à toa.
 */
export function magias(ctx: Contexto): MagiaNaFicha[] {
  const desbloqueadas = ctx.magias_desbloqueadas ?? []
  if (!desbloqueadas.length) return []

  const doCatalogo = new Map(
    catalogo<{ id: string; nome?: string; nivel?: number }>('magias').itens.map((m) => [m.id, m]),
  )

  const porMagia = new Map<string, MagiaNaFicha>()
  for (const d of desbloqueadas) {
    const item = doCatalogo.get(d.magia)
    if (!item) throw new ErroDoMotor(`magia desbloqueada que não existe no catálogo: '${d.magia}'`)
    const origem = origemLegivel(d.origem)
    const nova: MagiaNaFicha = {
      id: d.magia,
      nome: item.nome ?? d.magia,
      circulo: typeof item.nivel === 'number' ? item.nivel : 0,
      modo: d.modo,
      origem,
      ...(d.atributo_de_conjuracao ? { atributo_de_conjuracao: d.atributo_de_conjuracao } : {}),
      ...(d.nao_conta_para_o_limite ? { nao_conta_para_o_limite: true } : {}),
      pronta_para_conjurar: MODOS_PRONTOS.has(d.modo),
    }

    const anterior = porMagia.get(d.magia)
    if (!anterior) {
      porMagia.set(d.magia, nova)
      continue
    }
    porMagia.set(d.magia, {
      ...anterior,
      modo: anterior.pronta_para_conjurar ? anterior.modo : nova.modo,
      pronta_para_conjurar: anterior.pronta_para_conjurar || nova.pronta_para_conjurar,
      origem: anterior.origem.includes(origem) ? anterior.origem : `${anterior.origem}, ${origem}`,
      nao_conta_para_o_limite: anterior.nao_conta_para_o_limite || nova.nao_conta_para_o_limite,
    })
  }

  // Truques primeiro, depois por círculo e nome: a ordem em que a ficha de papel
  // as escreve, e a ordem em que se procura uma na mesa.
  return [...porMagia.values()].sort(
    (a, b) => a.circulo - b.circulo || a.nome.localeCompare(b.nome, 'pt-BR'),
  )
}

/**
 * "Clérigo · Conjuração", "Acólito · Iniciado em Magia".
 *
 * A trilha inteira, e não só o trecho mais específico: "Conjuração" sozinho não
 * diz de qual classe, e é justamente disso que a queixa tratava — o jogador
 * precisa ver de onde cada magia veio. Sem nenhum trecho nomeado, devolve-se a
 * trilha crua em vez de inventar um nome.
 */
function origemLegivel(origem: string): string {
  const nomes = trilhaLegivel(origem)
  return nomes.length ? nomes.join(' · ') : origem
}

/**
 * A parte de magia da ficha.
 *
 * Ausente para quem não conjura — e ausente, não zerada: um Bárbaro com "CD de
 * magia 11" na ficha é pior que um Bárbaro sem a linha.
 */
export function conjuracao(ctx: Contexto, vocabulario?: Vocabulario): Ficha['conjuracao'] {
  const atributo = ctx.atributo_de_conjuracao
  if (!atributo) return undefined

  const espacos: Record<number, number> = {}
  for (let circulo = 1; circulo <= 9; circulo++) {
    const n = ctx.colunas?.[`espacos_${circulo}`]
    if (typeof n === 'number' && n > 0) espacos[circulo] = n
  }
  const numero = (chave: string) => {
    const v = ctx.colunas?.[chave]
    return typeof v === 'number' ? v : 0
  }

  return {
    atributo,
    cd_para_evitar_sua_magia: calcular('cd_para_evitar_sua_magia', ctx, {}, vocabulario),
    jogada_de_ataque_magico: calcular('jogada_de_ataque_magico', ctx, {}, vocabulario),
    espacos,
    magias_preparadas: numero('magias_preparadas'),
    truques: numero('truques'),
  }
}

/** O teste de uma perícia: modificador do atributo + Bônus de Proficiência se proficiente. */
export function testeDePericia(ctx: Contexto, pericia: string, atributo: string): number {
  const bruto = ctx.atributos?.[atributo]
  if (bruto === undefined) throw new ErroDoMotor(`atributo ausente no contexto: '${atributo}'`)
  const proficiente = (ctx.proficiencias?.pericias ?? []).includes(pericia)
  return modificadorDeAtributo(bruto) + (proficiente ? bonusDeProficiencia(ctx) : 0)
}

/**
 * Pontos de Vida máximos.
 *
 * A fórmula é a do livro; o que o motor faz é preencher as parcelas que ela pede.
 * `soma_dos_niveis_seguintes` usa o VALOR FIXO da tabela por classe (p. 42), com o
 * piso de 1 por nível — que existe para o modificador de Constituição negativo.
 */
export function pontosDeVidaMaximos(ctx: Contexto, vocabulario?: Vocabulario): Resultado {
  const dadoDeVida = ctx.dado_de_vida_da_classe
  const porNivel = ctx.pv_por_nivel_da_classe
  if (dadoDeVida === undefined || porNivel === undefined) {
    throw new ErroDoMotor('contexto sem Dado de Vida ou sem valor fixo por nível da classe')
  }
  const modCon = modificadorDeAtributo(ctx.atributos.CON)

  const nivel1 = dadoDeVida + modCon
  const niveisSeguintes = Math.max(0, ctx.nivel_do_personagem - 1) * Math.max(1, porNivel + modCon)

  return calcular(
    'pontos_de_vida_maximos',
    ctx,
    {
      pontos_de_vida_no_nivel_1: nivel1,
      soma_dos_niveis_seguintes: niveisSeguintes,
      // Tenacidade Anã (+1 por nível), Vigoroso (+2 por nível), Dádiva da Fortitude
      // (+40): todos entram por aqui. Estava fixo em 0, e por isso o Anão nascia
      // com a vida errada e ninguém via — a conta batia com a fórmula do livro,
      // mas com uma parcela sempre vazia.
      bonus_de_caracteristicas: somaDeModificadores(ctx, 'pontos_de_vida_maximos'),
      // Estes dois são ESTADO de jogo (uma magia em curso, um dreno), não derivado.
      // A fórmula os exige, então entram zerados até o estado saber informá-los.
      bonus_temporarios_de_maximo: 0,
      reducoes_de_maximo: 0,
    },
    vocabulario,
  )
}

/**
 * Aplica os modificadores ativos de um alvo sobre uma base.
 *
 * `empilha: 'substitui'` troca o valor em vez de somar — é o Passo Rápido do
 * Halfling contra um deslocamento de base. Os demais somam, na ordem em que a
 * coleta os encontrou.
 */
export function aplicarModificadores(ctx: Contexto, alvo: string, base: number): number {
  let total = base
  for (const m of ctx.modificadores_ativos?.[alvo] ?? []) {
    if (m.empilha === 'substitui') total = m.valor
    else total += m.valor
  }
  return total
}

/** Só o que os modificadores acrescentam a um alvo, sem base nenhuma. */
export function somaDeModificadores(ctx: Contexto, alvo: string): number {
  return aplicarModificadores(ctx, alvo, 0)
}

/** Deslocamento: a base da espécie mais os modificadores ativos que somam. */
export function deslocamento(ctx: Contexto, vocabulario?: Vocabulario): number {
  const base = ctx.deslocamento_base_m
  if (base === undefined) throw new ErroDoMotor('contexto sem deslocamento de base')
  return aplicarModificadores(ctx, 'deslocamento', base)
}

/** Reexportado para quem quiser avaliar uma fórmula solta contra este contexto. */
export { avaliar, condicaoVale }
