// O registro do personagem.
//
// Guarda a CONSTRUÇÃO e o ESTADO — nunca a ficha. É a decisão que faz o dataset
// valer a pena: corrigir uma regra em `dados/` corrige todos os personagens de uma
// vez, porque a ficha se recalcula. Guardar a ficha seria criar uma segunda verdade,
// que envelhece em silêncio.
//
// `versao_do_dataset` é o carimbo de contra qual base ele foi construído. Não serve
// para migrar nada sozinho: serve para o app poder dizer "esta ficha foi feita numa
// base diferente" em vez de quebrar quando uma escolha aponta para um id que sumiu.

import type { Construcao, Estado } from '../../motor/src/motor.ts'

export type Personagem = {
  id: string
  /**
   * Quem é o dono. Todo personagem tem um, sem exceção — não existe personagem
   * órfão, e é isso que faz "meus personagens" ser meus e não de todo mundo.
   */
  usuario_id: string
  nome: string
  /** ativo · reserva · morto · aposentado — a lista do PLANO-APP, seção Fase A. */
  status: StatusDePersonagem
  construcao: Construcao
  estado: Estado & EstadoDeJogo
  versao_do_dataset: string
  criado_em: string
  /** Ordena "Meus personagens": o mais recente no topo. */
  ultimo_acesso: string
}

export const STATUS = ['ativo', 'reserva', 'morto', 'aposentado'] as const
export type StatusDePersonagem = (typeof STATUS)[number]

/**
 * Estado de jogo: o que o motor NÃO calcula porque não dá para calcular.
 *
 * A separação vem do dataset (`valores_derivados` e a decisão de deixar PV atual
 * fora da base), não de gosto de arquitetura. Tudo aqui é coisa que acontece na
 * mesa; nada aqui é derivável da construção.
 */
export type EstadoDeJogo = {
  pontos_de_vida_atuais?: number
  pontos_de_vida_temporarios?: number
  /** De onde vieram os temporários: eles não se somam, o maior vence. */
  fonte_dos_temporarios?: string
  /** Espaços gastos por círculo: { "1": 2 } são dois espaços de 1º já usados. */
  espacos_gastos?: Record<string, number>
  /** Usos gastos, por id de recurso: { "furia": 1 }. */
  recursos_gastos?: Record<string, number>
  /** Ids de condição ativas agora. */
  condicoes?: string[]
  /** Em que magia está concentrado, se estiver. */
  concentracao?: string | null
  /** O que o personagem carrega: id do item → quantidade. */
  inventario?: Record<string, number>
  /** O que está vestido ou na mão, dentre o que ele carrega. */
  equipado?: string[]
}

export const CAMPOS_DE_ESTADO = [
  'predicados_ativos',
  'portas_abertas',
  'pontos_de_vida_atuais',
  'pontos_de_vida_temporarios',
  'fonte_dos_temporarios',
  'espacos_gastos',
  'recursos_gastos',
  'condicoes',
  'concentracao',
  // O que se carrega e o que está na mão mudam NA MESA — pegar uma corda, sacar o
  // escudo — e por isso são estado, como os Pontos de Vida, e não construção.
  'inventario',
  'equipado',
] as const
