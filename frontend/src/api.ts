// A conversa com o backend, e a sessão guardada no aparelho.
//
// Um lugar só sabe montar pedido, pôr o token e traduzir erro. As telas chamam
// `api.get`/`api.post` e nunca `fetch` — assim "o token expirou, volte para o login"
// é uma regra escrita uma vez.

const BASE = '/api'
const CHAVE = 'ficha-facil.sessao'

export type Usuario = { id: string; email: string; criado_em: string }
export type Sessao = { usuario: Usuario; token: string; salvo_em: string }

/**
 * A sessão fica no `localStorage`, e vale um mês.
 *
 * Um mês é o que o backend assina (`SESSAO_HORAS=720`), e guardar por mais tempo aqui
 * só produziria um token que o servidor recusa — o aparelho lembraria de algo que
 * deixou de valer. Guardar por menos jogaria fora sessão boa. Então o prazo é um só,
 * e é o do servidor; o que fica aqui é uma cópia com a data para poder expirar sozinho
 * mesmo offline.
 *
 * `localStorage` é legível por qualquer script desta origem. Para um app pessoal, com
 * um backend que só serve o dono, é troca aceitável: cookie `HttpOnly` seria mais
 * seguro contra XSS, mas exige o backend emitir e ler cookie, e CORS com credenciais.
 * Quando o app sair da máquina do João, é a primeira coisa a revisitar.
 */
export const VALIDADE_MS = 30 * 24 * 3600_000

export function lerSessao(): Sessao | undefined {
  try {
    const cru = localStorage.getItem(CHAVE)
    if (!cru) return undefined
    const s = JSON.parse(cru) as Sessao
    if (!s?.token || !s?.usuario) return undefined
    if (Date.now() - new Date(s.salvo_em).getTime() > VALIDADE_MS) {
      localStorage.removeItem(CHAVE)
      return undefined
    }
    return s
  } catch {
    // localStorage pode estar bloqueado (aba anônima, política do navegador). Sem
    // sessão guardada o app ainda funciona: só pede login a cada visita.
    return undefined
  }
}

export function gravarSessao(usuario: Usuario, token: string): Sessao {
  const s: Sessao = { usuario, token, salvo_em: new Date().toISOString() }
  try {
    localStorage.setItem(CHAVE, JSON.stringify(s))
  } catch {
    /* sem persistência, a sessão vale só enquanto a aba estiver aberta */
  }
  return s
}

export function apagarSessao(): void {
  try {
    localStorage.removeItem(CHAVE)
  } catch {
    /* nada a fazer */
  }
}

/** Erro que veio do backend, com o código dele — as telas decidem o que mostrar. */
export class ErroDaApi extends Error {
  status: number
  codigo: string
  detalhe?: unknown

  constructor(status: number, codigo: string, mensagem: string, detalhe?: unknown) {
    super(mensagem)
    this.name = 'ErroDaApi'
    this.status = status
    this.codigo = codigo
    this.detalhe = detalhe
  }
}

let aoPerderSessao: (() => void) | undefined
/** O App registra aqui o que fazer quando o token deixa de valer. */
export function quandoPerderSessao(f: () => void): void {
  aoPerderSessao = f
}

async function pedir<T>(metodo: string, caminho: string, corpo?: unknown): Promise<T> {
  const sessao = lerSessao()
  const r = await fetch(BASE + caminho, {
    method: metodo,
    headers: {
      'content-type': 'application/json',
      ...(sessao ? { authorization: `Bearer ${sessao.token}` } : {}),
    },
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  })

  const texto = await r.text()
  const dados = texto ? JSON.parse(texto) : undefined

  if (!r.ok) {
    // 401 em qualquer rota significa a mesma coisa: a sessão acabou. Tratar aqui evita
    // cada tela ter de lembrar disso — e evita a tela em branco de quem só mostra erro.
    if (r.status === 401 && sessao) {
      apagarSessao()
      aoPerderSessao?.()
    }
    throw new ErroDaApi(r.status, dados?.erro ?? 'erro', dados?.mensagem ?? r.statusText, dados?.detalhe)
  }
  return dados as T
}

export const api = {
  get: <T,>(caminho: string) => pedir<T>('GET', caminho),
  post: <T,>(caminho: string, corpo?: unknown) => pedir<T>('POST', caminho, corpo),
  patch: <T,>(caminho: string, corpo?: unknown) => pedir<T>('PATCH', caminho, corpo),
  apagar: <T,>(caminho: string) => pedir<T>('DELETE', caminho),
}

// ------------------------------------------------------------------- os tipos

/** Uma parcela pode se abrir: os PV do nível 1 são o Dado de Vida mais a Constituição. */
export type Parcela = { rotulo: string; valor: number | string; parcelas?: Parcela[] }
export type Resultado = { valor: number; dados: string[]; parcelas: Parcela[] }

export type Opcao = {
  id: string
  nome: string
  /** Por que o personagem já tem esta opção por outro caminho, quando já tem. */
  ja_tem?: string
}
export type ItemDoChecklist = {
  escolha_id: string
  rotulo: string
  quantidade: number
  opcoes: Opcao[]
  origem?: string
  reescolhivel?: boolean
  /** Catálogo de onde vieram as opções — é onde a tela busca a descrição de cada uma. */
  catalogo?: string
  /** Os que o livro recomenda. */
  recomendados?: string[]
  /** Fonte ou escolha que precisa vir antes: sem ela não há o que oferecer. */
  bloqueada_por?: string
}

/**
 * Um item de catálogo, como o compêndio o devolve.
 *
 * A tela não conhece magia nem talento: ela conhece **campos**, e desenha os que o
 * item tiver. Um catálogo novo com `descricao_curta` já aparece descrito sem que
 * ninguém escreva uma linha aqui — e um campo que só magia tem simplesmente não
 * aparece nos outros.
 */
export type ItemDoCompendio = {
  id: string
  nome?: string
  descricao_curta?: string
  nivel?: number
  escola?: string
  categoria?: string
  ritual?: boolean
  concentracao?: boolean
  tempo_de_conjuracao?: { texto?: string }
  alcance?: { texto?: string }
  duracao?: { texto?: string }
  componentes?: { texto?: string }
  dano?: { formula_dado?: string; tipo_dano?: string; bonus_fixo?: number }
  grupo?: string
  peso_kg?: number
  /** O item diz se ele se veste ou se segura; a tela não decide por categoria. */
  equipavel?: boolean
  /** O item que este item TAMBÉM é (o foco druídico que é o Cajado). */
  tambem_e?: string
  custo?: { valor?: number; moeda?: string }
  [campo: string]: unknown
}

/**
 * O compêndio, buscado uma vez por catálogo e guardado enquanto a aba viver.
 *
 * `magias.json` tem 391 entradas e o backend o serve com ETag imutável, então a
 * segunda visita nem chega a baixar. O que esta memória evita é o terceiro pedido
 * na mesma tela: três escolhas de magia abririam três buscas iguais.
 */
const catalogosEmMemoria = new Map<string, Promise<Map<string, ItemDoCompendio>>>()

export function lerCatalogo(nome: string): Promise<Map<string, ItemDoCompendio>> {
  const guardado = catalogosEmMemoria.get(nome)
  if (guardado) return guardado
  const busca = api
    .get<{ itens: ItemDoCompendio[] }>(`/compendio/${nome}`)
    .then((r) => new Map(r.itens.map((i) => [i.id, i])))
    .catch((e) => {
      // Falhou: esquece, para a próxima tela poder tentar de novo em vez de herdar
      // um erro guardado para sempre.
      catalogosEmMemoria.delete(nome)
      throw e
    })
  catalogosEmMemoria.set(nome, busca)
  return busca
}

export type Ataque = {
  arma: string; nome: string; atributo: string; proficiente: boolean
  jogada: Resultado; dano: Resultado; tipo_dano?: string; porque_o_atributo: string
}

export type MagiaNaFicha = {
  id: string
  nome: string
  /** 0 é truque: é por ele que se sabe qual espaço a magia gasta. */
  circulo: number
  modo: string
  origem: string
  atributo_de_conjuracao?: string
  nao_conta_para_o_limite?: boolean
  pronta_para_conjurar: boolean
  /** O que gastar para conjurar: nada, um espaço, ou um uso (o recurso do talento). */
  custo: CustoDeConjuracao
  /** Os números da mesa, já resolvidos pelo motor. */
  jogo: {
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

export type CustoDeConjuracao =
  | { tipo: 'nenhum'; porque: string }
  | { tipo: 'espaco'; circulo_minimo: number }
  | { tipo: 'recurso'; recurso_id: string; porque: string; tambem_com_espaco?: boolean }
  | { tipo: 'sem_espaco'; porque: string; limite_nao_declarado: true }

export type CaracteristicaNaFicha = {
  id: string
  nome: string
  /** 'caracteristica' | 'traco' | 'talento'. */
  familia: string
  descricao_curta?: string
  fonte?: { capitulo?: number | string; pagina_livro?: number }
  /** A trilha até ela: "Draconato", "Acólito · Iniciado em Magia". */
  de: string
}

export type Recurso = {
  id: string
  nome: string
  maximo: number
  recarga: { gatilho: string; quantidade: number | 'todos' }[]
  origem: string
}

export type Ficha = {
  /** A pontuação de cada atributo, já com todos os aumentos aplicados. */
  atributos: Record<string, number>
  modificadores: Record<string, number>
  bonus_de_proficiencia: number
  classe_de_armadura: Resultado
  pontos_de_vida_maximos: Resultado
  iniciativa: Resultado
  percepcao_passiva: Resultado
  salvaguardas: Record<string, number>
  testes_de_pericia: Record<string, TesteDePericia>
  deslocamento_m: number
  ataques: Ataque[]
  magias: MagiaNaFicha[]
  recursos: Recurso[]
  caracteristicas: CaracteristicaNaFicha[]
  proficiencias?: { idiomas: string[]; ferramentas: string[]; armaduras: string[] }
  conjuracao?: {
    atributo: string
    cd_para_evitar_sua_magia: Resultado
    jogada_de_ataque_magico: Resultado
    espacos: Record<string, number>
  }
}

export type TesteDePericia = {
  valor: number
  atributo: string
  /** Id do nível de domínio ('proficiente', 'especialista') ou 'nenhum'. */
  dominio: string
  parcelas: Parcela[]
  nome: string
}

export type Estado = {
  /** O que o personagem carrega: id do item → quantidade. */
  inventario?: Record<string, number>
  /** O que está vestido ou na mão. */
  equipado?: string[]
  pontos_de_vida_atuais?: number
  pontos_de_vida_temporarios?: number
  espacos_gastos?: Record<string, number>
  recursos_gastos?: Record<string, number>
  condicoes?: string[]
}

export type Nivel = { classe: string; nivel: number }

export type Personagem = {
  id: string
  nome: string
  status: 'ativo' | 'reserva' | 'morto' | 'aposentado'
  construcao: { especie: string; antecedente: string; niveis: Nivel[]; escolhas?: Record<string, unknown> }
  estado: Estado
  ficha: Ficha | null
  checklist: ItemDoChecklist[]
  pendencias_de_escolha: { escolha_id: string; faltam?: number }[]
  versao_do_dataset: string
  aviso_de_versao?: string
  erro_de_ficha?: { mensagem: string; o_que_fazer: string }
}

export type NaLista = {
  id: string; nome: string; status: Personagem['status']
  niveis: Nivel[]; especie: string; ultimo_acesso: string
}

export type Evento = {
  id: string
  tipo: string
  em: string
  resumo: string
  [campo: string]: unknown
}

export const ATRIBUTOS = ['FOR', 'DES', 'CON', 'INT', 'SAB', 'CAR'] as const
export type Atributo = (typeof ATRIBUTOS)[number]

export const STATUS: Personagem['status'][] = ['ativo', 'reserva', 'morto', 'aposentado']
