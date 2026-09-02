// Tipos do motor. Nenhum id de conteúdo aparece aqui — é a regra do PLANO-MOTOR §1:
// se um `if classe === 'monge'` entrar no motor, o dataset perdeu o sentido.

/** Uma fórmula é árvore, nunca string a parsear (esquema v1). */
export type Formula = Termo | Termo[]
export type Termo = string | number | Operacao
export type Operacao = {
  op: string
  args?: Termo[]
  condicao?: Condicao
}

/** Condição: um operador lógico por objeto, aninhando. */
export type Condicao = string | Condicao[] | ObjetoDeCondicao
export type ObjetoDeCondicao =
  | { todas: Condicao[] }
  | { alguma: Condicao[] }
  | { nao: Condicao }
  | Comparacao
export type Comparacao = { comparar: Formula; op: string; com: Formula }

export type Atributo = 'FOR' | 'DES' | 'CON' | 'INT' | 'SAB' | 'CAR'

/**
 * O que o motor precisa saber sobre o personagem para calcular um derivado.
 *
 * No passo 2 este objeto vem pronto (os personagens de ouro o trazem à mão).
 * No passo 3 ele passa a ser PRODUZIDO pela coleta de efeitos a partir da
 * construção — e nada abaixo desta linha muda por causa disso.
 */
export type Contexto = {
  nivel_do_personagem: number
  niveis_por_classe: Record<string, number>
  atributos: Record<string, number>
  colunas?: Record<string, number | string>
  proficiencias?: {
    salvaguardas?: string[]
    pericias?: string[]
    ferramentas?: string[]
    /** Armas não vêm em lista: a classe concede "Simples" ou "Marciais com Leve",
     *  que no dado são filtros. Guardar o filtro evita explodir 170 itens na ficha. */
    armas?: Record<string, unknown>[]
  }
  /** Trocas de atributo declaradas por efeito (o Monge põe Destreza no lugar de Força). */
  substituicoes_de_atributo?: { de: string; para: string; aplica_a: string[]; escopo: string[] }[]
  /** Dado de dano que um efeito põe no lugar do padrão, por escopo. */
  dados_de_dano?: { dado: string; escopo: string[] }[]
  calculos_de_ca_base?: CalculoDeCaBase[]
  predicados_ativos?: string[]
  dado_de_vida_da_classe?: number
  pv_por_nivel_da_classe?: number
  deslocamento_base_m?: number
  /** SAB para o Clérigo, CAR para o Bardo… vem do efeito de conjuração da classe. */
  atributo_de_conjuracao?: string
  modificadores_ativos?: Record<string, ModificadorAtivo[]>
  /** Valores soltos que o chamador injeta para uma conta pontual. */
  extras?: Record<string, number>
  /** O mesmo, para termos que são DADO e não número ('1d12' da arma equipada). */
  extras_dados?: Record<string, string>
}

export type CalculoDeCaBase = { id: string; formula: Formula }
export type ModificadorAtivo = { de: string; valor: number; empilha?: string }

/**
 * O resultado de uma conta. O motor é PURO: ele nunca joga dado.
 * O que é dado fica simbólico em `dados`, e é assim que a ficha mostra
 * "Iniciativa +3" ou "dano 1d12 + 4".
 */
export type Resultado = {
  valor: number
  dados: string[]
  parcelas: Parcela[]
}

export type Parcela = { rotulo: string; valor: number | string }

export class ErroDoMotor extends Error {}
