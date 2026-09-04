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

import type { Contexto, Parcela, Recurso, Resultado } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { avaliar, bonusDeProficiencia, modificadorDeAtributo } from './formula.ts'
import { calcular, derivado } from './derivados.ts'
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
/**
 * O que conjurar esta magia custa — a pergunta que o jogador faz na mesa.
 *
 * Existe porque o botão "usar" gastava espaço de magia sempre, inclusive para
 * truque (que não gasta nada) e para a magia que um talento dá de graça uma vez por
 * dia. `porque` é a trilha legível de quem paga a conta, para a tela poder dizer
 * "de graça pelo Iniciado em Magia" em vez de só "grátis".
 */
export type CustoDeConjuracao =
  | { tipo: 'nenhum'; porque: string }
  | { tipo: 'espaco'; circulo_minimo: number }
  | { tipo: 'recurso'; recurso_id: string; porque: string; tambem_com_espaco?: boolean }
  /** Sem espaço, mas o dado não declarou com que frequência: não se inventa limite. */
  | { tipo: 'sem_espaco'; porque: string; limite_nao_declarado: true }

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
  /** O que gastar para conjurá-la. */
  custo: CustoDeConjuracao
  /**
   * O que o jogador precisa para JOGAR a magia, já com os números resolvidos:
   * a jogada de ataque com o bônus dele, a CD da salvaguarda, o dado de dano ou de
   * cura já crescido pelo nível, o alcance e a área.
   *
   * Existe porque a linha "Mísseis Mágicos" sozinha não serve na mesa — a queixa foi
   * "eu quero o nome, o número e tipo de dados que lanço, a salvaguarda, a distância
   * e a área; ao invés de dizer + mod SAB, ele diria já +2".
   */
  jogo: {
    /** 'corpo_a_corpo' | 'a_distancia', quando a magia é um ataque. */
    ataque?: string
    jogada_de_ataque?: Resultado
    salvaguarda?: { atributo: string; cd: number; em_sucesso?: string }
    dano?: { formula: string; tipo?: string }
    cura?: { formula: string }
    alcance?: string
    area?: string
    tempo_de_conjuracao?: string
    duracao?: string
    concentracao?: boolean
    ritual?: boolean
  }
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
  /**
   * O número de cada perícia, com o atributo e o domínio.
   *
   * Vinha vazio — "poder ver o número que tenho em arcanismo" era a queixa, e não
   * havia de onde tirar: a ficha declarava o campo e devolvia `{}`.
   */
  testes_de_pericia: Record<string, TesteDePericia>
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
  /** O que ele fala, com que ferramentas sabe trabalhar e que armaduras sabe usar. */
  proficiencias: { idiomas: string[]; ferramentas: string[]; armaduras: string[] }
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
    testes_de_pericia: testesDePericia(ctx),
    // As proficiências que não viram número: idioma, ferramenta, armadura. A ficha
    // as repassa porque o jogador precisa saber o que fala e o que sabe vestir —
    // eram justamente as que caíam caladas antes de o contexto guardá-las.
    proficiencias: {
      idiomas: [...(ctx.proficiencias?.idiomas ?? [])],
      ferramentas: [...(ctx.proficiencias?.ferramentas ?? [])],
      armaduras: [...(ctx.proficiencias?.armaduras ?? [])],
    },
    deslocamento_m: deslocamento(ctx, vocabulario),
    ataques: ataques(ctx, equipamentoEquipado, vocabulario),
    magias: magias(ctx, vocabulario),
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
const circuloDa = (m: { nivel?: number }) => (typeof m.nivel === 'number' ? m.nivel : 0)

/** O id do recurso que conta os usos de uma magia conjurada de graça. */
export const recursoDeConjuracao = (magia: string) => `conjuracao_livre:${magia}`

/**
 * O que custa conjurar esta magia.
 *
 * A ordem é a da mesa: truque não custa nada; uma concessão de "conjurar sem espaço"
 * manda no resto; senão, gasta-se um espaço do círculo dela para cima.
 *
 * Quando a concessão tem frequência por descanso, o custo é o RECURSO que a passada
 * de recursos criou para ela — assim o app tem o que mostrar (1/1) e o que gastar, e
 * o descanso a devolve pela recarga declarada, sem ninguém escrever regra nova.
 */
export function custoDeConjuracao(
  magia: string,
  circulo: number,
  ctx: Contexto,
): CustoDeConjuracao {
  const livre = (ctx.conjuracoes_sem_espaco ?? []).find((c) => c.magias.includes(magia))
  if (livre) {
    const porque = origemLegivel(livre.origem)
    const tambem = livre.tambem_com_espaco && circulo > 0 ? { tambem_com_espaco: true } : {}
    if (livre.consome_recurso) {
      return { tipo: 'recurso', recurso_id: livre.consome_recurso, porque, ...tambem }
    }
    if (livre.frequencia && /^uma_vez_por_descanso/.test(livre.frequencia)) {
      return { tipo: 'recurso', recurso_id: recursoDeConjuracao(magia), porque, ...tambem }
    }
    if (livre.frequencia === 'a_vontade' || livre.frequencia === 'sem_limite') {
      return { tipo: 'nenhum', porque }
    }
    // O dado não diz com que frequência: dizer "à vontade" seria inventar permissão,
    // e cobrar espaço seria cobrar o que o livro dispensou. Fica declarado.
    return { tipo: 'sem_espaco', porque, limite_nao_declarado: true }
  }
  if (circulo === 0) return { tipo: 'nenhum', porque: 'truque' }
  return { tipo: 'espaco', circulo_minimo: circulo }
}

/** A magia como o catálogo a guarda — os campos que a linha de mesa usa. */
type MagiaDoCatalogo = {
  id: string
  nome?: string
  nivel?: number
  ataque?: string
  salvaguarda?: { atributo?: string; em_sucesso?: string }
  dano?: { formula_dado?: string; tipo_dano?: string; bonus_fixo?: number }
  cura?: { formula_dado?: string }
  alcance?: { texto?: string }
  area?: { forma?: string; metros?: number }
  tempo_de_conjuracao?: { texto?: string }
  duracao?: { texto?: string }
  concentracao?: boolean
  ritual?: boolean
  aprimoramento?: { tipo?: string; escala_por_nivel?: Record<string, string> }
}

/**
 * O dado do truque no nível deste personagem.
 *
 * O crescimento é do dado, não uma conta: o catálogo declara `escala_por_nivel`
 * ({5: '2d8', 11: '3d8', 17: '4d8'}), e aqui se escolhe a faixa. Truque cujo texto
 * não virou escala continua com o dado-base — mostrar o base é menos errado do que
 * inventar progressão.
 */
function danoDoTruque(m: MagiaDoCatalogo, nivel: number): string | undefined {
  const escala = m.aprimoramento?.escala_por_nivel
  const base = m.dano?.formula_dado ?? m.cura?.formula_dado
  if (!escala || !base) return base
  const faixas = Object.keys(escala).map(Number).filter((n) => n <= nivel).sort((a, b) => a - b)
  return faixas.length ? escala[String(faixas[faixas.length - 1])] : base
}

/** A linha de mesa: os números que o jogador usa, já resolvidos. */
function jogo(
  m: MagiaDoCatalogo,
  ctx: Contexto,
  conj: Ficha['conjuracao'],
  vocabulario?: Vocabulario,
): MagiaNaFicha['jogo'] {
  const circulo = circuloDa(m)
  const formula = circulo === 0
    ? danoDoTruque(m, ctx.nivel_do_personagem)
    : m.dano?.formula_dado ?? m.cura?.formula_dado
  const bonus = m.dano?.bonus_fixo ? ` + ${m.dano.bonus_fixo}` : ''

  return {
    ...(m.ataque ? { ataque: m.ataque } : {}),
    // O bônus é o da ficha: quem conjura já tem "jogada de ataque mágico" calculada,
    // e repetir a conta aqui seria ter duas verdades sobre o mesmo número.
    ...(m.ataque && conj ? { jogada_de_ataque: conj.jogada_de_ataque_magico } : {}),
    ...(m.salvaguarda?.atributo && conj
      ? {
          salvaguarda: {
            atributo: m.salvaguarda.atributo,
            cd: conj.cd_para_evitar_sua_magia.valor,
            ...(m.salvaguarda.em_sucesso ? { em_sucesso: m.salvaguarda.em_sucesso } : {}),
          },
        }
      : {}),
    ...(m.dano && formula
      ? { dano: { formula: `${formula}${bonus}`, ...(m.dano.tipo_dano ? { tipo: m.dano.tipo_dano } : {}) } }
      : {}),
    ...(m.cura && formula ? { cura: { formula } } : {}),
    ...(m.alcance?.texto ? { alcance: m.alcance.texto } : {}),
    ...(m.area?.forma
      ? { area: `${m.area.forma}${m.area.metros ? ` de ${m.area.metros} m` : ''}` }
      : {}),
    ...(m.tempo_de_conjuracao?.texto ? { tempo_de_conjuracao: m.tempo_de_conjuracao.texto } : {}),
    ...(m.duracao?.texto ? { duracao: m.duracao.texto } : {}),
    ...(m.concentracao ? { concentracao: true } : {}),
    ...(m.ritual ? { ritual: true } : {}),
  }
  void vocabulario
}

export function magias(ctx: Contexto, vocabulario?: Vocabulario): MagiaNaFicha[] {
  const desbloqueadas = ctx.magias_desbloqueadas ?? []
  if (!desbloqueadas.length) return []

  const conj = conjuracao(ctx, vocabulario)
  const doCatalogo = new Map(
    catalogo<MagiaDoCatalogo>('magias').itens.map((m) => [m.id, m]),
  )

  const porMagia = new Map<string, MagiaNaFicha>()
  for (const d of desbloqueadas) {
    const item = doCatalogo.get(d.magia)
    if (!item) throw new ErroDoMotor(`magia desbloqueada que não existe no catálogo: '${d.magia}'`)
    const origem = origemLegivel(d.origem)
    const nova: MagiaNaFicha = {
      id: d.magia,
      nome: item.nome ?? d.magia,
      circulo: circuloDa(item),
      modo: d.modo,
      origem,
      ...(d.atributo_de_conjuracao ? { atributo_de_conjuracao: d.atributo_de_conjuracao } : {}),
      ...(d.nao_conta_para_o_limite ? { nao_conta_para_o_limite: true } : {}),
      pronta_para_conjurar: MODOS_PRONTOS.has(d.modo),
      custo: custoDeConjuracao(d.magia, circuloDa(item), ctx),
      jogo: jogo(item, ctx, conj, vocabulario),
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

  // O Bruxo não tem uma coluna por círculo: tem "Espaços de Pacto" e "Círculo de
  // Magia", e TODOS os espaços dele são do mesmo círculo (p. 121). Ler só
  // `espacos_<n>` deixava a ficha dele com o painel de espaços vazio — ele
  // conjurava sem ter o que gastar, e a queixa foi exatamente essa.
  //
  // O `conceder_slot` de modo `pacto` já dizia em que colunas está a resposta; era
  // a ficha que só sabia perguntar de um jeito.
  const pacto = ctx.espacos_de_pacto
  if (pacto && pacto.quantidade > 0 && pacto.circulo > 0) {
    espacos[pacto.circulo] = (espacos[pacto.circulo] ?? 0) + pacto.quantidade
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
export type TesteDePericia = {
  valor: number
  /** O atributo que o livro manda usar nesta perícia. */
  atributo: string
  /** Id do nível de domínio (do catálogo), ou 'nenhum'. */
  dominio: string
  parcelas: Parcela[]
  nome: string
}

/**
 * Todas as perícias do livro, com o número de cada uma.
 *
 * Todas, e não só as proficientes: na mesa se rola Arcanismo mesmo sem proficiência,
 * e uma ficha que só mostra as treinadas obriga a fazer a conta de cabeça justamente
 * no caso em que ela não é óbvia.
 */
export function testesDePericia(ctx: Contexto): Record<string, TesteDePericia> {
  const saida: Record<string, TesteDePericia> = {}
  for (const p of catalogo<{ id: string; nome?: string; atributo: string }>('pericias').itens) {
    const d = testeDePericiaDetalhado(ctx, p.id, p.atributo)
    saida[p.id] = { ...d, nome: p.nome ?? p.id }
  }
  return saida
}

export function testeDePericia(ctx: Contexto, pericia: string, atributo: string): number {
  return testeDePericiaDetalhado(ctx, pericia, atributo).valor
}

/**
 * Quanto o Bônus de Proficiência vale em cada nível de domínio.
 *
 * Vem do catálogo, não daqui: "Especialização dobra o Bônus de Proficiência" é regra
 * do livro (p. 361) como qualquer outra, e o motor só a lê.
 */
function multiplicadorDoDominio(id: string): number {
  const n = catalogo<{ id: string; multiplicador_do_bonus?: number }>('niveis_de_dominio')
    .itens.find((x) => x.id === id)
  return n?.multiplicador_do_bonus ?? 0
}

/**
 * O domínio que o personagem tem numa perícia ou ferramenta, e o que ele multiplica.
 *
 * Entre dois graus, vale o que multiplica mais: quem é proficiente por duas portas e
 * especialista por uma terceira tem Especialização.
 */
export function dominioEm(ctx: Contexto, chave: string): { id: string; multiplicador: number } {
  let melhor = { id: 'nenhum', multiplicador: 0 }
  const considerar = (nivel: string) => {
    const m = multiplicadorDoDominio(nivel)
    if (m > melhor.multiplicador) melhor = { id: nivel, multiplicador: m }
  }
  for (const g of ctx.proficiencias_com_origem ?? []) {
    if (g.chave === chave && g.nivel_dominio) considerar(g.nivel_dominio)
  }
  // Proficiência sem nível declarado é proficiência simples — é o caso mais comum.
  if (
    melhor.multiplicador === 0 &&
    ((ctx.proficiencias?.pericias ?? []).includes(chave) ||
      (ctx.proficiencias?.ferramentas ?? []).includes(chave))
  ) {
    const padrao = catalogo<{ id: string; multiplicador_do_bonus?: number }>('niveis_de_dominio')
      .itens.find((x) => x.multiplicador_do_bonus === 1)
    if (padrao) melhor = { id: padrao.id, multiplicador: 1 }
  }
  return melhor
}

/**
 * O teste de uma perícia, com de onde vem o número.
 *
 * Especialização **dobra** o Bônus de Proficiência (p. 361), e isso não acontecia:
 * o nível de domínio era jogado fora ao guardar a proficiência, então a
 * Especialização do Ladino, a do Bardo e a dos dois talentos não somavam nada.
 */
export function testeDePericiaDetalhado(
  ctx: Contexto,
  pericia: string,
  atributo: string,
): Omit<TesteDePericia, 'nome'> {
  const bruto = ctx.atributos?.[atributo]
  if (bruto === undefined) throw new ErroDoMotor(`atributo ausente no contexto: '${atributo}'`)
  const mod = modificadorDeAtributo(bruto)
  const dominio = dominioEm(ctx, pericia)
  const extra = bonusDeProficiencia(ctx) * dominio.multiplicador
  const nomeDoDominio = catalogo<{ id: string; nome?: string }>('niveis_de_dominio')
    .itens.find((x) => x.id === dominio.id)?.nome

  return {
    valor: mod + extra,
    atributo,
    dominio: dominio.id,
    parcelas: [
      { rotulo: atributo, valor: mod },
      ...(extra ? [{ rotulo: nomeDoDominio ?? dominio.id, valor: extra }] : []),
    ],
  }
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
  const quantosSeguintes = Math.max(0, ctx.nivel_do_personagem - 1)
  const porNivelComCon = Math.max(1, porNivel + modCon)
  const niveisSeguintes = quantosSeguintes * porNivelComCon

  const r = calcular(
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

  // Cada parcela que é ela mesma uma conta se abre. Os rótulos vêm dos `parcelas`
  // que o catálogo já declarava para `pontos_de_vida_no_nivel_1` e
  // `pontos_de_vida_por_nivel` — o motor não escreve frase nenhuma aqui.
  const rotulos = (id: string) =>
    Object.fromEntries((derivado(id).parcelas ?? []).map((p) => [p.chave, p.rotulo]))
  const doNivel1 = rotulos('pontos_de_vida_no_nivel_1')
  const porNivelRot = rotulos('pontos_de_vida_por_nivel')

  const detalhe: Record<string, Parcela[]> = {
    pontos_de_vida_no_nivel_1: [
      { rotulo: doNivel1.dado_de_vida_da_classe ?? 'Dado de Vida', valor: dadoDeVida },
      { rotulo: doNivel1['mod:CON'] ?? 'Constituição', valor: modCon },
    ],
    ...(quantosSeguintes > 0
      ? {
          soma_dos_niveis_seguintes: [
            {
              rotulo: `${porNivelRot.rolagem_ou_valor_fixo_do_dado_de_vida ?? 'valor fixo por nível'}` +
                ` × ${quantosSeguintes} ${quantosSeguintes > 1 ? 'níveis' : 'nível'}`,
              valor: porNivel * quantosSeguintes,
            },
            {
              rotulo: `${porNivelRot['mod:CON'] ?? 'Constituição'} × ${quantosSeguintes}`,
              valor: modCon * quantosSeguintes,
            },
          ],
        }
      : {}),
    // Aqui o detalhe não vem do catálogo: vem de QUEM concedeu, que é a única
    // resposta útil para "de onde vieram esses 3 pontos".
    bonus_de_caracteristicas: (ctx.modificadores_ativos?.pontos_de_vida_maximos ?? []).map(
      (m) => ({ rotulo: trilhaLegivel(m.de).join(' · ') || m.de, valor: m.valor }),
    ),
  }

  return {
    ...r,
    parcelas: r.parcelas.map((p) => {
      const chave = (derivado('pontos_de_vida_maximos').parcelas ?? [])
        .find((d) => d.rotulo === p.rotulo)?.chave
      const dentro = chave ? detalhe[chave] : undefined
      return dentro?.length ? { ...p, parcelas: dentro } : p
    }),
  }
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
