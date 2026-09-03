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
  /**
   * Dados de dano que substituem o padrão, com de onde vêm.
   *
   * Pode haver MAIS DE UM válido ao mesmo tempo: o Combate Desarmado dá 1d6, e 1d8
   * com as mãos livres — e nas mãos livres os dois valem. Quem consome escolhe; a
   * lista não é ordenada por preferência.
   */
  dados_de_dano?: { dado: string; escopo: string[]; origem?: string }[]
  calculos_de_ca_base?: CalculoDeCaBase[]
  predicados_ativos?: string[]
  dado_de_vida_da_classe?: number
  pv_por_nivel_da_classe?: number
  deslocamento_base_m?: number
  /** SAB para o Clérigo, CAR para o Bardo… vem do efeito de conjuração da classe. */
  atributo_de_conjuracao?: string
  modificadores_ativos?: Record<string, ModificadorAtivo[]>
  /** Magias que algum efeito destravou, e em que condição. */
  magias_desbloqueadas?: MagiaDesbloqueada[]
  /** Recursos com recarga: Fúrias, Ataque de Sopro, Canalizar Divindade… */
  recursos?: Recurso[]
  /** Em que descanso os espaços de magia voltam. Curto para o Bruxo, longo no resto. */
  recarga_dos_espacos?: { gatilho: string; quantidade: number | 'todos' }[]
  /**
   * As trilhas de origem dos efeitos que INCIDEM neste personagem.
   *
   * É por elas que a ficha sabe quais características ele tem, sem que ninguém
   * mantenha uma segunda lista: quem tem um efeito coletado tem a característica.
   */
  origens_ativas?: string[]
  /** Valores soltos que o chamador injeta para uma conta pontual. */
  extras?: Record<string, number>
  /** O mesmo, para termos que são DADO e não número ('1d12' da arma equipada). */
  extras_dados?: Record<string, string>
}

/**
 * Uma magia que o personagem alcançou, e por qual porta.
 *
 * `modo` é o que separa uma da outra na ficha, e vem do dataset sem tradução:
 * 'conhecida' (um truque), 'no_livro' (escrita, ainda não preparada),
 * 'preparada' (escolhida no descanso), 'sempre_preparada' (o talento a dá pronta),
 * 'disponivel_para_preparar' (a lista da classe está aberta).
 *
 * `origem` é a trilha de onde ela veio — é o que deixa a ficha dizer "Curar
 * Ferimentos (sempre preparada — Iniciado em Magia)" em vez de só listar o nome.
 */
export type MagiaDesbloqueada = {
  magia: string
  modo: string
  origem: string
  /** O atributo com que ESTA magia é conjurada; pode não ser o da classe. */
  atributo_de_conjuracao?: string
  /** Magia dada por talento não ocupa uma das vagas de preparação da classe. */
  nao_conta_para_o_limite?: boolean
  /** A lista de onde ela veio ('mago', 'clerigo'…), quando o efeito diz. */
  lista?: string
}

/**
 * Um recurso com recarga: uma coisa que se gasta e volta num descanso.
 *
 * O `maximo` já vem CALCULADO — 'prof' vira 3, `coluna:furias` vira 4 — porque a
 * fórmula precisa do contexto e a ficha não deve avaliar nada. Quanto se gastou é
 * ESTADO, e mora no personagem, não aqui.
 */
export type Recurso = {
  id: string
  nome: string
  maximo: number
  /** Quando ele volta, e quanto: `descanso_curto` (tudo), ou parcial. */
  recarga: { gatilho: string; quantidade: number | 'todos' }[]
  origem: string
}

/**
 * Um cálculo de CA base. `nome` é para a ficha dizer "Cota de Malha" em vez de
 * `ca_cota_de_malha_parcial`; sem ele, a proveniência cai no id.
 */
export type CalculoDeCaBase = { id: string; nome?: string; formula: Formula }
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

export class ErroDoMotor extends Error {
  // `name` precisa ser posto na mão: `class X extends Error {}` deixa name como
  // 'Error', e quem classifica erro por nome (o backend, para responder 422 em vez
  // de 500) não enxerga nada. Custou um 500 dizendo que a culpa era do servidor
  // quando o cliente é que tinha mandado uma espécie que não existe.
  constructor(mensagem: string) {
    super(mensagem)
    this.name = 'ErroDoMotor'
  }
}
