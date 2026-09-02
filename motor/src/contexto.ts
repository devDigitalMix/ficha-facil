// De efeitos coletados para Contexto — a outra metade do passo 3.
//
// A coleta responde "quais efeitos incidem"; aqui se responde "o que eles fazem
// com a ficha". A separação importa: a lista de efeitos é a mesma para o Bárbaro
// em Fúria e fora dela — o que muda é o ESTADO, e é aqui que ele entra.

import type { Contexto, Condicao, CalculoDeCaBase, Formula } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { condicaoVale, type Vocabulario } from './condicao.ts'
import { derivado } from './derivados.ts'
import type { Colecao, EfeitoColetado } from './colecao.ts'
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
        dadosDeDano.push({ dado, escopo: (e.escopo as string[]) ?? [] })
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
        if (!Number.isFinite(valor)) {
          naoConsumidos.push(c)
          break
        }
        ;(modificadores[alvo] ??= []).push({
          de: c.origem,
          valor,
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
        // atributo dele, e isso não vira a conjuração da ficha
        naoConsumidos.push(c)
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
    atributo_de_conjuracao: atributoDeConjuracao,
    substituicoes_de_atributo: substituicoes,
    dados_de_dano: dadosDeDano,
    extras: equipados.escudo ? { bonus_do_escudo: bonusDoEscudo(equipados.escudo) } : undefined,
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
