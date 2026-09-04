// Coletor de efeitos — passo 3 do PLANO-MOTOR.
//
// Entra uma CONSTRUÇÃO (o que o jogador escolheu), sai a lista de efeitos que
// incidem sobre ele, cada um sabendo de onde veio. É o que faz o campo `contexto`
// dos personagens de ouro parar de ser escrito à mão.
//
// Três coisas que este arquivo trata com cuidado, porque errar nelas é errar calado:
//
// 1. **Escolha não resolvida não é erro — é pendência.** Um Monge de nível 1 tem
//    umas seis escolhas em aberto, e a maioria não muda a CA. Quem exige tudo
//    resolvido não consegue montar meia ficha; quem ignora silenciosamente perde
//    o "subir de nível sem esquecer nada". Então elas voltam numa lista, que é
//    exatamente o checklist que a Fase A promete.
//
// 2. **Efeito aninhado nem sempre é condição.** Os efeitos dentro da Fúria só valem
//    em Fúria — achatar faria o Bárbaro andar por aí com Resistência a dano Cortante.
//    Mas os 56 `melhorar_caracteristica` aninham por ESTRUTURA, não por condição: o
//    `alvo` diz onde aplicar, não quando. Qual é qual está DECLARADO em
//    `tipos_de_efeito.json`; o motor lê, não adivinha. Adivinhar pelo formato foi o
//    defeito da primeira versão desta peça, e ele desligava as 56 caladas.
//
// 3. **Nada aqui conhece id de conteúdo.** O coletor percorre o dado; quem é
//    Monge e quem é Bárbaro está em `dados/`.

import type { Condicao, Formula } from './tipos.ts'
import { ErroDoMotor } from './tipos.ts'
import { catalogo, lerJson, porId } from './dataset.ts'

// ------------------------------------------------------------------ entrada

export type Construcao = {
  especie: string
  antecedente: string
  niveis: { classe: string; nivel: number }[]
  atributos_base: Record<string, number>
  /**
   * Escolhas já resolvidas, por id da escolha.
   *
   * Subclasse e talento entram AQUI, não em campo próprio: no dado eles são
   * escolhas como qualquer outra, e o efeito que elas produzem (`conceder_subclasse`,
   * `conceder_talento`) é quem faz o trabalho. Um campo `subclasse` à parte seria
   * a mesma informação em dois lugares — e um deles acabaria mentindo.
   */
  escolhas?: Record<string, EscolhaResolvida>
  equipamento_equipado?: string[]
}

export type EscolhaResolvida =
  | string
  | string[]
  | { escolhido: string; distribuicao?: Record<string, number> }

export type Efeito = Record<string, unknown> & { tipo?: string; id?: string }

export type EfeitoColetado = {
  efeito: Efeito
  /** De onde veio, em texto legível: "classe monge / nível 1 / defesa_sem_armadura". */
  origem: string
  /** Ids de efeitos-pai que precisam estar ativos para este valer. */
  portas: string[]
}

export type Pendencia = {
  escolha_id: string
  rotulo: string
  origem: string
  quantidade: unknown
}

export type Colecao = {
  efeitos: EfeitoColetado[]
  pendencias: Pendencia[]
  /**
   * Toda escolha encontrada, resolvida ou não, pelo id. A conferência e o checklist
   * precisam do efeito original — as opções saem do `de`, e a pendência sozinha só
   * guarda o rótulo.
   */
  escolhas: Map<string, { efeito: Efeito; origem: string }>
  /** Colunas da tabela de classe no nível alcançado. */
  colunas: Record<string, number | string>
  nivel_do_personagem: number
  niveis_por_classe: Record<string, number>
  dado_de_vida_da_classe: number
  pv_por_nivel_da_classe: number
  deslocamento_base_m: number
}

// ------------------------------------------------------------------ o dado

// `efeitos_nomeados` aparece nas duas formas no dado: uma lista de efeitos, ou um
// objeto `{ efeitos: [...] }`. As duas dizem a mesma coisa; o motor aceita ambas.
type Nomeados = Efeito[] | { efeitos?: Efeito[] }
type Entidade = {
  id: string
  efeitos?: Efeito[]
  efeitos_nomeados?: Record<string, Nomeados>
  /** Característica que a classe concede mais de uma vez (o Aumento no Valor de Atributo). */
  repetivel?: boolean
  /** 'todo_personagem' é o que vem da criação (cap. 2), e não de espécie ou classe. */
  escopo?: string
}

function listaDeEfeitos(n: Nomeados | undefined): Efeito[] | undefined {
  if (!n) return undefined
  return Array.isArray(n) ? n : n.efeitos
}

/**
 * `condicionados` → o que está dentro só vale com o pai ativo, e o `id` do pai nomeia
 * a porta. `estruturais` → vale sempre. Quem não declara é erro de build (validar.py).
 */
let aninhamentoCache: Record<string, string | undefined> | null = null
function modoDeAninhamento(tipo: string): string | undefined {
  if (!aninhamentoCache) {
    aninhamentoCache = Object.fromEntries(
      catalogo<{ id: string; efeitos_aninhados?: string }>('tipos_de_efeito').itens.map(
        (i) => [i.id, i.efeitos_aninhados],
      ),
    )
  }
  return aninhamentoCache[tipo]
}

function caracteristicas() {
  return lerJson<{ itens: (Entidade & { nivel?: number })[] }>('caracteristicas.json').itens
}

// ------------------------------------------------------------------ coleta

class Coletor {
  efeitos: EfeitoColetado[] = []
  pendencias: Pendencia[] = []
  escolhas = new Map<string, { efeito: Efeito; origem: string }>()
  // sem parameter property: o strip-only mode do Node não a apaga
  readonly construcao: Construcao
  readonly nivel: number
  constructor(construcao: Construcao, nivel: number) {
    this.construcao = construcao
    this.nivel = nivel
  }

  private escolhaResolvida(id: string): EscolhaResolvida | undefined {
    return this.construcao.escolhas?.[id]
  }

  /**
   * Percorre uma lista de efeitos.
   *
   * `portas` são os ids dos efeitos-pai que precisam estar ativos. A Fúria abre
   * uma porta chamada 'furia'; o que está dentro dela só vale com ela aberta.
   */
  coletar(
    efeitos: Efeito[] | undefined,
    origem: string,
    portas: string[] = [],
    dono?: Entidade,
    sufixo = '',
  ): void {
    for (const cru of efeitos ?? []) {
      // `$escolhido_em:<escolha>` é o dado apontando para o que o jogador escolheu
      // em OUTRA escolha. Os filtros já sabiam resolver isso; os efeitos, não — e o
      // `conjurar_sem_espaco` do Iniciado em Magia, que diz "esta magia, a que você
      // escolheu ali, uma vez por Descanso Longo", chegava com um cifrão no lugar do
      // id e era descartado. Era por isso que a magia do talento cobrava espaço.
      const e = this.resolverReferencias(cru, sufixo)

      if (e.tipo === 'escolha') {
        this.resolverEscolha(e, origem, portas, dono, sufixo)
        continue
      }

      // `aplicar_efeito_nomeado` aponta para efeitos que moram em OUTRO lugar, e há
      // dois lugares possíveis — que a primeira versão tratava como um só:
      //
      // 1. **No próprio dono** (`{ chave }`), quando a entidade declara um bloco
      //    `efeitos_nomeados`. É o caso das Manobras do Guerreiro, das Invocações do
      //    Bruxo, dos Golpes Astutos do Ladino: 27 dos 37 usos.
      // 2. **Num catálogo** (`{ catalogo, chave }`), quando as opções são itens de um
      //    catálogo próprio e cada item traz os `efeitos` dele. São 10 usos, e é como
      //    o livro organiza herança, linhagem, ancestralidade e legado.
      //
      // Ignorar o `catalogo` fazia o motor procurar no dono uma chave que nunca
      // esteve lá, e derrubava **cinco das dez espécies** — Draconato, Elfo, Gnomo,
      // Golias e Tiferino — além do Aasimar, do Guardião, do Paladino e do Vigilante.
      // O erro dizia "não existe em '(sem dono)'", que é verdade e não ajuda.
      if (e.tipo === 'aplicar_efeito_nomeado') {
        const chave = e.chave as string
        const nomeDoCatalogo = e.catalogo as string | undefined

        const nomeados = nomeDoCatalogo
          ? listaDeEfeitos(
              (catalogo<Entidade>(nomeDoCatalogo).itens.find((i) => i.id === chave) as
                | { efeitos?: Efeito[] }
                | undefined)?.efeitos,
            )
          : listaDeEfeitos(dono?.efeitos_nomeados?.[chave])

        if (!nomeados) {
          throw new ErroDoMotor(
            nomeDoCatalogo
              ? `'${chave}' não é um item de '${nomeDoCatalogo}', ou não traz efeitos (${origem})`
              : `efeito nomeado '${chave}' não existe em '${dono?.id ?? '(sem dono)'}' (${origem})`,
          )
        }
        this.efeitos.push({ efeito: e, origem, portas })
        // O dono passa a ser o ITEM do catálogo quando é dele que os efeitos vêm:
        // um `aplicar_efeito_nomeado` aninhado dentro dele tem de resolver ali.
        const novoDono = nomeDoCatalogo
          ? catalogo<Entidade>(nomeDoCatalogo).itens.find((i) => i.id === chave)
          : dono
        this.coletar(nomeados, `${origem} / ${chave}`, portas, novoDono, sufixo)
        continue
      }

      this.efeitos.push({ efeito: e, origem, portas })

      // efeitos aninhados: a porta é este efeito
      const dentro = e.efeitos as Efeito[] | undefined
      if (Array.isArray(dentro)) {
        const tipo = e.tipo as string
        const modo = modoDeAninhamento(tipo)
        if (modo === undefined) {
          throw new ErroDoMotor(
            `o tipo '${tipo}' traz efeitos dentro e não declara em tipos_de_efeito.json ` +
              `se eles são 'condicionados' ou 'estruturais' (${origem})`,
          )
        }
        if (modo === 'condicionados') {
          const porta = e.id as string
          if (!porta) {
            throw new ErroDoMotor(
              `efeito '${tipo}' condiciona o que traz dentro mas não tem id para ` +
                `nomear a condição (${origem})`,
            )
          }
          this.coletar(dentro, `${origem} / ${porta}`, [...portas, porta], dono, sufixo)
        } else {
          // estrutural: herda as portas do pai, sem criar uma nova
          this.coletar(dentro, `${origem} / ${tipo}`, portas, dono, sufixo)
        }
      }

      if (e.tipo === 'conceder_talento' && typeof e.talento_id === 'string') {
        // o id do talento entra na trilha: sem ele, a proveniência termina no id da
        // ESCOLHA ('guerreiro_estilo_de_luta') e não na coisa escolhida
        this.talento(e.talento_id, `${origem} / talento ${e.talento_id}`, portas, sufixo,
          e.escolhas_predefinidas as Record<string, EscolhaResolvida> | undefined)
      }

      if (e.tipo === 'conceder_subclasse' && typeof e.chave === 'string') {
        this.subclasse(e.chave, portas)
      }
    }
  }

  /**
   * Troca `$escolhido_em:<id>` pelo que foi escolhido naquela escolha.
   *
   * Escolha ainda não respondida fica como está: o efeito então não se aplica, e
   * aparece em `nao_consumidos` — que é a verdade, e não um id inventado.
   */
  private resolverReferencias(e: Efeito, sufixo = ''): Efeito {
    const troca = (v: unknown): unknown => {
      if (typeof v === 'string' && v.startsWith('$escolhido_em:')) {
        const alvo = v.slice('$escolhido_em:'.length)
        // O mesmo talento vindo de duas portas tem escolhas qualificadas
        // (`..._magia_1@humano_versatil`). A referência é escrita sem o sufixo, e
        // tem de achar a DESTA porta — senão o Iniciado em Magia do Humano aponta
        // para a magia que o Acólito escolheu.
        const resolvida =
          (sufixo ? this.escolhaResolvida(`${alvo}${sufixo}`) : undefined) ??
          this.escolhaResolvida(alvo)
        if (resolvida === undefined) return v
        const ids = normalizarEscolhidos(resolvida)
        return ids.length === 1 ? ids[0] : ids
      }
      if (Array.isArray(v)) return v.map(troca)
      if (v && typeof v === 'object') {
        return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, troca(x)]))
      }
      return v
    }
    return troca(e) as Efeito
  }

  private resolverEscolha(
    e: Efeito,
    origem: string,
    portas: string[],
    dono?: Entidade,
    sufixo = '',
  ): void {
    const declarado = e.id as string
    if (!declarado) throw new ErroDoMotor(`escolha sem id em ${origem}`)
    // Uma característica repetível abre a MESMA escolha em cada nível em que chega.
    // Sem qualificar, o Aumento no Valor de Atributo do nível 8 sobrescreve o do 4 —
    // e o personagem nunca consegue pegar dois talentos diferentes. O sufixo é o
    // nível da concessão, então o id continua legível: 'asi_escolha_de_talento@8'.
    const id = sufixo ? `${declarado}${sufixo}` : declarado
    this.escolhas.set(id, { efeito: { ...e, id }, origem })

    const resolvida = this.escolhaResolvida(id)
    if (resolvida === undefined) {
      this.pendencias.push({
        escolha_id: id,
        rotulo: (e.rotulo as string) ?? id,
        origem,
        quantidade: e.quantidade,
      })
      return
    }

    const modelo = e.efeito_por_item_escolhido as Efeito | undefined
    const escolhidos = normalizarEscolhidos(resolvida)

    for (const escolhido of escolhidos) {
      if (!modelo) {
        // A escolha não gera efeito por item (o tamanho do Humano, por exemplo):
        // ela é um dado da ficha, e quem a consome é o construtor do contexto.
        this.efeitos.push({
          efeito: { tipo: 'escolha_resolvida', escolha_id: id, escolhido },
          origem,
          portas,
        })
        continue
      }
      const concreto = substituirEscolhido(modelo, escolhido)
      if (typeof resolvida === 'object' && !Array.isArray(resolvida) && resolvida.distribuicao) {
        concreto.distribuicao = resolvida.distribuicao
      }
      // Passa pelo coletor, e não direto para a lista: o efeito que a escolha
      // produz pode ser `conceder_talento` ou `conceder_subclasse`, que abrem
      // outra entidade inteira. Empurrar direto os deixava mudos — foi assim que
      // o Aumento no Valor de Atributo do Bárbaro não aumentou nada.
      // O sufixo continua: o talento que este Aumento concedeu abre escolhas
      // próprias, e elas pertencem a ESTE aumento, não ao do nível seguinte.
      //
      // E há um segundo jeito de o mesmo talento chegar duas vezes, que a primeira
      // versão não previa: **fontes diferentes**. O Humano pega um talento de Origem
      // pelo traço Versátil, e o antecedente já concede um — escolher Iniciado em
      // Magia nos dois dava TRÊS escolhas com id repetido, todas gravando na mesma
      // chave. O livro permite o acúmulo ("pode adquirir este talento mais de uma
      // vez, mas deve escolher uma lista de magias diferente a cada vez", p. 201),
      // então recusar seria errado: o que faltava era o id distinguir a fonte.
      //
      // O qualificador é o id DESTA escolha, e só entra quando ainda não há sufixo —
      // quando há, ele já distingue (o Aumento do nível 8 é '@8'). Assim o id não
      // depende da ordem em que o motor percorre, e nada que já funcionava muda de
      // nome.
      this.coletar([concreto], `${origem} / ${id}`, portas, dono,
        this.sufixoParaTalento(concreto, sufixo, id))
    }
  }

  /**
   * Um talento repetível concedido por uma escolha ganha o id dessa escolha como
   * qualificador. Talento que não é repetível não precisa: se ele chegasse duas
   * vezes, o problema seria outro, e mascará-lo com um sufixo o esconderia.
   */
  private sufixoParaTalento(concreto: Efeito, sufixo: string, idDaEscolha: string): string {
    if (sufixo) return sufixo
    if (concreto.tipo !== 'conceder_talento' || typeof concreto.talento_id !== 'string') return sufixo
    const t = catalogo<Entidade & { repetivel?: boolean }>('talentos').itens
      .find((x) => x.id === concreto.talento_id)
    return t?.repetivel ? `@${idDaEscolha}` : sufixo
  }

  private talento(
    id: string,
    origem: string,
    portas: string[],
    sufixo = '',
    predefinidas?: Record<string, EscolhaResolvida>,
  ): void {
    const t = porId(catalogo<Entidade>('talentos').itens, id, 'catalogos/talentos.json')
    // `escolhas_predefinidas` são escolhas que a origem já fixou (o antecedente
    // que trava a lista do Iniciado em Magia). Valem como se o jogador tivesse
    // escolhido — e é isso que o esquema quis dizer com o campo.
    if (predefinidas) {
      this.construcao.escolhas = { ...(this.construcao.escolhas ?? {}), ...predefinidas }
    }
    // O sufixo segue para dentro: as escolhas DO TALENTO concedido por um Aumento
    // no Valor de Atributo também precisam saber de qual dos aumentos vieram.
    this.coletarComNomeados(t, origem, portas, sufixo)
  }

  /**
   * O nível de cada característica de subclasse sai da PRÓPRIA característica.
   *
   * A primeira versão casava `caracteristicas` com `niveis_de_caracteristica` por
   * posição. Funcionou para a Trilha da Árvore do Mundo por coincidência — ela tem
   * quatro de cada — e é errado em **42 das 48 subclasses**, que têm mais
   * características do que níveis: `niveis_de_caracteristica` é o RESUMO de em que
   * níveis a subclasse dá algo, não o mapa de qual dá o quê. O Domínio da Vida, com
   * cinco características em três níveis, é quem denunciou.
   */
  private subclasse(id: string, portas: string[]): void {
    const sub = porId(
      lerJson<{ itens: Subclasse[] }>('subclasses.json').itens,
      id,
      'subclasses.json',
    )
    for (const idCar of sub.caracteristicas ?? []) {
      const car = porId(caracteristicas(), idCar, `caracteristicas.json (subclasse ${sub.id})`)
      const n = car.nivel
      if (typeof n !== 'number') {
        throw new ErroDoMotor(
          `a característica '${idCar}' da subclasse '${sub.id}' não diz em que nível chega`,
        )
      }
      if (n > this.nivel) continue
      this.coletarComNomeados(
        car,
        `subclasse ${sub.id} / nível ${n} / ${idCar}`,
        portas,
        car.repetivel ? `@${n}` : '',
      )
    }
  }

  /** Coleta os efeitos de uma entidade, com ela mesma como dona dos nomeados. */
  coletarComNomeados(ent: Entidade, origem: string, portas: string[] = [], sufixo = ''): void {
    this.coletar(ent.efeitos, origem, portas, ent, sufixo)
  }
}

export function normalizarEscolhidos(r: EscolhaResolvida): string[] {
  if (typeof r === 'string') return [r]
  if (Array.isArray(r)) return r
  return [r.escolhido]
}

/** Troca `{{escolhido}}` pelo id escolhido, em qualquer profundidade. */
function substituirEscolhido(modelo: Efeito, escolhido: string): Efeito {
  const troca = (v: unknown): unknown => {
    if (typeof v === 'string') return v.replace('{{escolhido}}', escolhido)
    if (Array.isArray(v)) return v.map(troca)
    if (v && typeof v === 'object') {
      return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, troca(x)]))
    }
    return v
  }
  return troca(JSON.parse(JSON.stringify(modelo))) as Efeito
}

// ------------------------------------------------------------------ entrada pública

type Classe = Entidade & {
  dado_de_vida: number
  proficiencias_iniciais?: Efeito[]
  progressao: { nivel: number; caracteristicas: string[]; colunas?: Record<string, number | string> }[]
  subclasses?: string[]
}
type Especie = Entidade & {
  deslocamento?: { tipo: string; metros: number }
  tracos?: (Entidade & { nome?: string })[]
  tamanho?: unknown
}
type Subclasse = Entidade & {
  classe?: string
  /** RESUMO de em que níveis a subclasse dá algo. Não é o mapa: o nível de cada
   *  característica está na própria característica. */
  niveis_de_caracteristica?: number[]
  caracteristicas?: string[]
}

export function coletar(c: Construcao): Colecao {
  if (c.niveis.length !== 1) {
    throw new ErroDoMotor('multiclasse está fora de escopo por decisão do projeto')
  }
  const { classe: idClasse, nivel } = c.niveis[0]

  const col = new Coletor(c, nivel)
  const CARS = caracteristicas()
  const carPorId = (id: string, origem: string) => porId(CARS, id, `caracteristicas.json (${origem})`)

  // --- o que TODO personagem tem
  //
  // O capítulo 2 concede coisas que não são de espécie, antecedente nem classe: todo
  // personagem sabe o Comum e mais dois idiomas (p. 37). Antes disso não havia onde
  // pendurar uma regra de criação — e o personagem nascia sem falar nada, enquanto a
  // escolha "mais um idioma" do Ladino oferecia o Comum como novidade.
  for (const car of CARS.filter((x) => x.escopo === 'todo_personagem')) {
    col.coletarComNomeados(car, `criação do personagem / ${car.id}`)
  }

  // --- espécie
  const esp = porId(catalogo<Especie>('especies').itens, c.especie, 'catalogos/especies.json')
  for (const t of esp.tracos ?? []) {
    col.coletar(t.efeitos, `espécie ${esp.id} / ${t.id}`)
  }

  // --- antecedente
  const ant = porId(
    catalogo<Entidade>('antecedentes').itens,
    c.antecedente,
    'catalogos/antecedentes.json',
  )
  col.coletar(ant.efeitos, `antecedente ${ant.id}`)

  // --- classe
  const classe = porId(
    lerJson<{ itens: Classe[] }>('classes.json').itens,
    idClasse,
    'classes.json',
  )
  col.coletar(classe.proficiencias_iniciais, `classe ${classe.id} / proficiências iniciais`)

  let colunas: Record<string, number | string> = {}
  for (const linha of classe.progressao) {
    if (linha.nivel > nivel) break
    colunas = { ...colunas, ...(linha.colunas ?? {}) }
    for (const idCar of linha.caracteristicas) {
      const car = carPorId(idCar, `classe ${classe.id} nível ${linha.nivel}`)
      col.coletarComNomeados(
        car,
        `classe ${classe.id} / nível ${linha.nivel} / ${idCar}`,
        [],
        car.repetivel ? `@${linha.nivel}` : '',
      )
    }
  }

  const pv = pvDaLinha(idClasse)

  return {
    efeitos: col.efeitos,
    pendencias: col.pendencias,
    escolhas: col.escolhas,
    colunas,
    nivel_do_personagem: nivel,
    niveis_por_classe: { [idClasse]: nivel },
    dado_de_vida_da_classe: classe.dado_de_vida,
    pv_por_nivel_da_classe: pv,
    deslocamento_base_m: esp.deslocamento?.metros ?? 9,
  }
}

function pvDaLinha(classe: string): number {
  const vd = catalogo<{
    id: string
    tabela_por_classe?: { classes: string[]; pv_por_nivel: number }[]
  }>('valores_derivados').itens
  const linhas = vd.find((v) => v.id === 'pontos_de_vida_no_nivel_1')?.tabela_por_classe ?? []
  const linha = linhas.find((l) => l.classes.includes(classe))
  if (!linha) throw new ErroDoMotor(`classe sem linha na tabela de Pontos de Vida: '${classe}'`)
  return linha.pv_por_nivel
}

export type { Condicao, Formula }
