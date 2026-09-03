// De efeitos coletados para Contexto — a outra metade do passo 3.
//
// A coleta responde "quais efeitos incidem"; aqui se responde "o que eles fazem
// com a ficha". A separação importa: a lista de efeitos é a mesma para o Bárbaro
// em Fúria e fora dela — o que muda é o ESTADO, e é aqui que ele entra.

import type { Contexto, Condicao, CalculoDeCaBase, Formula, Recurso } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { condicaoVale, type Vocabulario } from './condicao.ts'
import { avaliar } from './formula.ts'
import { derivado } from './derivados.ts'
import { trilhaLegivel } from './dataset.ts'
import type { Colecao, Efeito, EfeitoColetado } from './colecao.ts'
import { separar, calculoDaArmadura, bonusDoEscudo, type Equipado } from './equipamento.ts'

/** O que o jogador está fazendo agora. Não é derivado: é estado de jogo. */
export type Estado = {
  /** Predicados que valem neste instante: 'ativo:furia', 'segurando:escudo'… */
  predicados_ativos?: string[]
  /** Efeitos-pai ligados: a Fúria abre a porta 'furia' para o que está dentro dela. */
  portas_abertas?: string[]
}

export type ContextoMontado = {
  contexto: Contexto
  /** Efeitos que o passo 2 não consome — ficam para os passos seguintes. */
  nao_consumidos: EfeitoColetado[]
}

const CATEGORIA_DE_PROFICIENCIA: Record<string, keyof NonNullable<Contexto['proficiencias']>> = {
  salvaguarda: 'salvaguardas',
  pericia: 'pericias',
  ferramenta: 'ferramentas',
}

export function montarContexto(
  col: Colecao,
  atributosBase: Record<string, number>,
  estado: Estado = {},
  vocabulario?: Vocabulario,
  equipamentoEquipado: string[] = [],
): ContextoMontado {
  const abertas = new Set(estado.portas_abertas ?? [])
  const equipados: Equipado = separar(equipamentoEquipado)

  // O que está vestido e empunhado é predicado como qualquer outro: é assim que a
  // Defesa sem Armadura do Monge sabe que não vale, sem o motor conhecer o Monge.
  const ativos = [...(estado.predicados_ativos ?? [])]
  if (equipados.armadura) {
    ativos.push('armadura:qualquer', `armadura:${equipados.armadura.grupo}`)
  }
  if (equipados.escudo) ativos.push('segurando:escudo')
  if (!equipados.armas.length) ativos.push('sem_arma_na_mao')

  const atributos = { ...atributosBase }
  const proficiencias = {
    salvaguardas: [] as string[],
    pericias: [] as string[],
    ferramentas: [] as string[],
    armas: [] as Record<string, unknown>[],
  }
  const substituicoes: NonNullable<Contexto['substituicoes_de_atributo']> = []
  const dadosDeDano: NonNullable<Contexto['dados_de_dano']> = []
  const calculos: CalculoDeCaBase[] = [calculoPadrao()]
  // A armadura entra como mais um cálculo CONCORRENTE, não como substituto: ela
  // disputa com a Defesa sem Armadura do Monge e do Bárbaro, e o maior ganha.
  if (equipados.armadura) calculos.push(calculoDaArmadura(equipados.armadura))
  const modificadores: Record<string, { de: string; valor: number; empilha?: string }[]> = {}
  const naoConsumidos: EfeitoColetado[] = []
  const magias: NonNullable<Contexto['magias_desbloqueadas']> = []
  /** Recursos cuja fórmula de máximo só dá para avaliar com o contexto pronto. */
  const recursosPendentes: { coletado: EfeitoColetado; efeito: Efeito }[] = []
  const recursos: NonNullable<Contexto['recursos']> = []
  const recargaDosEspacos: NonNullable<Contexto['recarga_dos_espacos']> = []

  /**
   * Anota uma magia destravada por um efeito.
   *
   * `desbloquear_magias` e `preparar_magias` são dois nomes para a mesma coisa
   * quando trazem um campo `magia`: o dataset usa um ou outro conforme a fase em
   * que o trecho foi escrito. A ficha não deve saber dessa diferença, então ela
   * morre aqui.
   *
   * Sem `magia` não há o que anotar: é a forma "regra da classe", não a forma
   * "esta magia aqui".
   */
  function anotarMagia(c: EfeitoColetado, e: Efeito): void {
    const magia = e.magia
    if (typeof magia !== 'string') return
    const atributo = e.atributo_conjuracao ?? e.atributo_de_conjuracao
    magias.push({
      magia,
      modo: (e.modo as string) ?? 'conhecida',
      origem: c.origem,
      // `$alguma_coisa` é variável de escolha que ninguém resolveu: melhor sem
      // atributo (a ficha cai no da classe) do que com um cifrão na tela.
      ...(typeof atributo === 'string' && !atributo.startsWith('$')
        ? { atributo_de_conjuracao: atributo }
        : {}),
      ...(e.nao_conta_para_o_limite || e.nao_conta_para_o_limite_de_preparadas
        ? { nao_conta_para_o_limite: true }
        : {}),
      ...(typeof e.lista_id === 'string' ? { lista: e.lista_id } : {}),
    })
  }

  /** Modificadores cujo valor é fórmula: só dá para avaliar com o contexto pronto. */
  const pendentes: {
    coletado: EfeitoColetado
    alvo: string
    formula: Formula
    empilha?: string
  }[] = []
  let atributoDeConjuracao: string | undefined

  // O contexto parcial serve para avaliar as condições dos próprios efeitos:
  // o que depende de atributo já tem os atributos, porque os aumentos vêm antes.
  const parcial = (): Contexto => ({
    nivel_do_personagem: col.nivel_do_personagem,
    niveis_por_classe: col.niveis_por_classe,
    atributos,
    colunas: col.colunas,
    proficiencias,
    predicados_ativos: ativos,
    atributo_de_conjuracao: atributoDeConjuracao,
    substituicoes_de_atributo: substituicoes,
    dados_de_dano: dadosDeDano,
    extras: equipados.escudo ? { bonus_do_escudo: bonusDoEscudo(equipados.escudo) } : undefined,
  })

  const aplicaveis = col.efeitos.filter((c) => c.portas.every((p) => abertas.has(p)))

  // 1ª passada: aumentos de atributo. Têm de vir antes de tudo, senão a CA e os
  // Pontos de Vida saem calculados com o valor de antes.
  for (const c of aplicaveis) {
    if (c.efeito.tipo === 'aumento_atributo') aplicarAumento(c, atributos)
  }

  // 2ª passada: o resto
  for (const c of aplicaveis) {
    const e = c.efeito
    if (e.tipo === 'aumento_atributo') continue

    if (!vale(e.condicao as Condicao | undefined, parcial(), vocabulario)) {
      continue
    }

    switch (e.tipo) {
      case 'conceder_proficiencia': {
        const destino = CATEGORIA_DE_PROFICIENCIA[e.categoria as string]
        const chave = e.chave as string

        // Arma vem como FILTRO ("armas Simples", "Marciais com a propriedade Leve"),
        // não como lista. Guarda-se o filtro.
        if (e.categoria === 'arma') {
          const filtro = (e.de as { filtro?: Record<string, unknown> } | undefined)?.filtro
          if (filtro) proficiencias.armas.push(filtro)
          else if (typeof chave === 'string') proficiencias.armas.push({ id: chave })
          else naoConsumidos.push(c)
          break
        }

        if (!destino || typeof chave !== 'string') {
          naoConsumidos.push(c)
          break
        }
        if (!proficiencias[destino].includes(chave)) proficiencias[destino].push(chave)
        break
      }

      case 'substituir_atributo': {
        const de = e.de as string | undefined
        const para = e.para as string | undefined
        if (!de || !para) {
          naoConsumidos.push(c)
          break
        }
        substituicoes.push({
          de,
          para,
          aplica_a: (e.aplica_a as string[]) ?? [],
          escopo: (e.escopo as string[]) ?? [],
        })
        break
      }

      case 'dado_de_dano': {
        const coluna = e.coluna as string | undefined
        const dado = coluna ? col.colunas?.[coluna] : (e.formula_dado as string | undefined)
        if (typeof dado !== 'string') {
          naoConsumidos.push(c)
          break
        }
        dadosDeDano.push({ dado, escopo: (e.escopo as string[]) ?? [], origem: c.origem })
        break
      }

      case 'ca_base': {
        const id = (e.id as string) ?? c.origem
        calculos.push({ id, formula: e.formula as Formula })
        break
      }

      case 'modificador': {
        const alvo = e.alvo as string
        const valor = Array.isArray(e.valor) ? Number(e.valor[0]) : Number(e.valor)
        if (Number.isFinite(valor)) {
          ;(modificadores[alvo] ??= []).push({
            de: c.origem,
            valor,
            empilha: e.empilha as string | undefined,
          })
          break
        }
        // Valor que não é número é FÓRMULA — 'nivel_do_personagem' da Tenacidade
        // Anã, '{mult 2 nível}' do Vigoroso, 'mod:CAR' de uma invocação. Ela não pode
        // ser avaliada aqui: a fórmula precisa do contexto pronto, e o contexto
        // ainda está sendo montado. Fica para a 3ª passada.
        //
        // Antes, tudo isso virava `Number(...)` → NaN → descartado em silêncio, e
        // o Anão andava a vida inteira com os Pontos de Vida de um humano.
        pendentes.push({
          coletado: c,
          alvo,
          formula: (Array.isArray(e.valor) ? e.valor : [e.valor]) as Formula,
          empilha: e.empilha as string | undefined,
        })
        break
      }

      case 'preparar_magias': {
        // Quem PREPARA magias é a classe conjuradora, e é o atributo dela que a ficha
        // mostra. Um personagem pode ter mais de uma FONTE de magia — a Clériga com
        // Iniciado em Magia tem duas — mas o talento apenas desbloqueia; ele não
        // prepara, e não manda na CD do Clérigo. Foi essa distinção que consertou o
        // atributo saindo como `$atributo_do_talento`.
        //
        // Duas fontes que preparam com atributos diferentes seriam multiclasse, que
        // está fora de escopo. Se aparecer, é erro — o motor não escolhe uma no
        // escuro.
        //
        // O efeito tem DUAS formas no dataset, e é preciso separá-las: com
        // `formula_quantidade` ele é a regra de preparação da CLASSE (quantas, de
        // que fonte, com que atributo); com `magia` ele é um talento entregando
        // UMA magia pronta. A segunda forma não manda no atributo da ficha.
        anotarMagia(c, e)
        if (typeof e.magia === 'string') break

        const a = e.atributo_conjuracao
        if (typeof a !== 'string') break
        if (atributoDeConjuracao && atributoDeConjuracao !== a) {
          throw new ErroDoMotor(
            `duas fontes preparam magias com atributos diferentes ('${atributoDeConjuracao}' ` +
              `e '${a}', em ${c.origem}) — o motor não escolhe uma sozinho`,
          )
        }
        atributoDeConjuracao = a
        naoConsumidos.push(c)
        break
      }

      case 'desbloquear_magias':
        // desbloquear não é preparar: o Iniciado em Magia dá acesso a magias, com o
        // atributo dele, e isso não vira a conjuração da ficha.
        //
        // Mas ACESSO é o que a ficha precisa mostrar. Enquanto este efeito só caía
        // em `nao_consumidos`, o truque escolhido no talento existia na construção,
        // aparecia no histórico, e não aparecia em lugar nenhum da ficha — que era
        // a queixa: "as magias que peguei pelo antecedente não aparecem".
        anotarMagia(c, e)
        naoConsumidos.push(c)
        break

      case 'conceder_slot':
        // Os espaços em si já vêm pela tabela da classe, em `colunas`. O que falta
        // é QUANDO eles voltam — e isso muda de classe para classe: o Bruxo
        // recupera no Descanso Curto, todo o resto só no Longo. Sem guardar esta
        // linha, um botão de descanso teria de saber quem é o Bruxo.
        for (const g of normalizarRecarga(
          Array.isArray(e.recarga) ? e.recarga : [e.recarga],
        )) {
          if (!recargaDosEspacos.some((x) => x.gatilho === g.gatilho)) recargaDosEspacos.push(g)
        }
        naoConsumidos.push(c)
        break

      case 'recurso_com_recarga':
        // O máximo é fórmula ('prof', `coluna:furias`, `max(1, mod:SAB)`) e por isso
        // fica para a 3ª passada, como os modificadores. Eram 88 no dataset, e
        // nenhum chegava à ficha: o Sopro do Draconato existia no livro, existia no
        // JSON, e não existia na tela de quem ia usá-lo.
        recursosPendentes.push({ coletado: c, efeito: e })
        break

      case 'escolha_resolvida':
        break // dado da ficha, sem efeito mecânico próprio

      default:
        naoConsumidos.push(c)
    }
  }

  const contexto: Contexto = {
    ...parcial(),
    calculos_de_ca_base: calculos,
    dado_de_vida_da_classe: col.dado_de_vida_da_classe,
    pv_por_nivel_da_classe: col.pv_por_nivel_da_classe,
    deslocamento_base_m: col.deslocamento_base_m,
    modificadores_ativos: modificadores,
    magias_desbloqueadas: magias,
    recursos,
    recarga_dos_espacos: recargaDosEspacos,
    // Só o que INCIDE: um efeito atrás de uma porta fechada (a Fúria desligada) não
    // conta, e é por isso que esta lista sai de `aplicaveis` e não de `col.efeitos`.
    origens_ativas: [...new Set(aplicaveis.map((c) => c.origem))],
    atributo_de_conjuracao: atributoDeConjuracao,
    substituicoes_de_atributo: substituicoes,
    dados_de_dano: dadosDeDano,
    extras: equipados.escudo ? { bonus_do_escudo: bonusDoEscudo(equipados.escudo) } : undefined,
  }
  // 3ª passada: os modificadores que vieram como fórmula. Agora o contexto existe,
  // então 'nivel_do_personagem', 'mod:CAR' e 'prof' têm com o que ser resolvidos.
  //
  // Fórmula que o avaliador não sabe resolver NÃO derruba a ficha: volta para
  // `nao_consumidos`, como antes. O que mudou é que agora só cai ali o que
  // realmente não dá para resolver — e não tudo, como acontecia.
  for (const pen of pendentes) {
    let r
    try {
      r = avaliar(pen.formula, contexto, vocabulario)
    } catch {
      naoConsumidos.push(pen.coletado)
      continue
    }
    // Modificador que é DADO ('2d4', o dado de Superioridade) não vira número: o
    // motor não rola. Ele fica para quem sabe mostrar dado na ficha.
    if (r.dados.length) {
      naoConsumidos.push(pen.coletado)
      continue
    }
    ;(modificadores[pen.alvo] ??= []).push({
      de: pen.coletado.origem,
      valor: r.valor,
      empilha: pen.empilha,
    })
  }

  for (const pen of recursosPendentes) {
    const recurso = montarRecurso(pen.efeito, pen.coletado, contexto, vocabulario)
    if (recurso) recursos.push(recurso)
    else naoConsumidos.push(pen.coletado)
  }

  proficiencias.salvaguardas.sort()
  proficiencias.pericias.sort()
  proficiencias.ferramentas.sort()

  return { contexto, nao_consumidos: naoConsumidos }
}

/**
 * Condição que o motor ainda não sabe decidir não derruba a ficha inteira: o
 * efeito simplesmente não entra, e isso é visível em `nao_consumidos`. A dureza
 * fica onde ela protege — no vocabulário e nos termos de fórmula.
 */
function vale(c: Condicao | undefined, ctx: Contexto, vocabulario?: Vocabulario): boolean {
  try {
    return condicaoVale(c, ctx, vocabulario)
  } catch {
    return false
  }
}

function aplicarAumento(c: EfeitoColetado, atributos: Record<string, number>): void {
  const e = c.efeito
  const permitidos = (e.atributos as string[]) ?? Object.keys(atributos)
  const limite = (e.limite as number) ?? 20
  // Duas formas no dado: a do antecedente distribui entre três atributos; a do
  // talento aumenta UM atributo nomeado. As duas viram a mesma distribuição.
  let dist = e.distribuicao as Record<string, number> | undefined
  if (!dist && typeof e.atributo === 'string' && typeof e.valor === 'number') {
    dist = { [e.atributo]: e.valor }
  }
  if (!dist) {
    throw new ErroDoMotor(
      `aumento de atributo sem distribuição em ${c.origem} — a escolha precisa dizer ` +
        `quais atributos sobem e quanto`,
    )
  }
  for (const [atr, quanto] of Object.entries(dist)) {
    if (!permitidos.includes(atr)) {
      throw new ErroDoMotor(`${c.origem}: '${atr}' não está entre os atributos permitidos`)
    }
    const novo = (atributos[atr] ?? 0) + quanto
    if (novo > limite) {
      throw new ErroDoMotor(`${c.origem}: ${atr} passaria de ${limite} (iria a ${novo})`)
    }
    atributos[atr] = novo
  }
}

/** O cálculo de CA que todo mundo tem: 10 + Destreza (Ap. C, p. 363). */
function calculoPadrao(): CalculoDeCaBase {
  const padrao = derivado('classe_de_armadura').calculo_padrao
  if (!padrao) throw new ErroDoMotor('valores_derivados não declara o cálculo padrão de CA')
  const formula: Formula = [String(padrao.base)]
  if (padrao.soma_modificador) (formula as string[]).push(`mod:${padrao.soma_modificador}`)
  return { id: padrao.id, formula }
}

/**
 * Um efeito `recurso_com_recarga` virado em linha da ficha.
 *
 * Devolve `undefined` quando não dá para saber o máximo — fórmula com um termo
 * que o avaliador não conhece, ou fórmula ausente. Aí o efeito volta para
 * `nao_consumidos`, que é o lugar declarado do que o motor ainda não sabe fazer.
 * Um recurso com "0 usos" na tela seria pior que a ausência dele: parece que
 * acabou, quando na verdade nunca foi contado.
 */
function montarRecurso(
  e: Efeito,
  c: EfeitoColetado,
  ctx: Contexto,
  vocabulario?: Vocabulario,
): Recurso | undefined {
  const id = e.id
  if (typeof id !== 'string' || e.formula_maximo === undefined) return undefined

  let maximo: number
  try {
    maximo = avaliar(e.formula_maximo as Formula, ctx, vocabulario).valor
  } catch {
    return undefined
  }
  if (!Number.isFinite(maximo) || maximo <= 0) return undefined

  return {
    id,
    // Metade dos recursos não declara `nome` (é o da característica que os contém).
    // A trilha de origem sabe o nome; usá-la evita id cru na ficha.
    nome: (e.nome as string) ?? trilhaLegivel(c.origem).pop() ?? id,
    maximo,
    recarga: normalizarRecarga(e.recarga),
    origem: trilhaLegivel(c.origem).join(' · ') || c.origem,
  }
}

/**
 * A recarga em uma forma só.
 *
 * O dataset escreve de duas maneiras: `["descanso_longo"]` (volta tudo) e
 * `[{gatilho, quantidade}]` (o Bruxo recupera 1 no curto e tudo no longo). A ficha
 * não deve conhecer as duas — a diferença morre aqui.
 */
function normalizarRecarga(bruta: unknown): Recurso['recarga'] {
  if (!Array.isArray(bruta)) return []
  const saida: Recurso['recarga'] = []
  for (const r of bruta) {
    if (typeof r === 'string') {
      saida.push({ gatilho: r, quantidade: 'todos' })
      continue
    }
    if (r && typeof r === 'object') {
      const o = r as Record<string, unknown>
      if (typeof o.gatilho !== 'string') continue
      const q = o.quantidade
      saida.push({
        gatilho: o.gatilho,
        quantidade: typeof q === 'number' ? q : 'todos',
      })
    }
  }
  return saida
}
