// Os endpoints da seção 7 do PLANO-MOTOR.
//
// O backend é fino de propósito: ele guarda a construção, serve o compêndio e chama
// o motor. Nenhuma regra de D&D mora aqui — se aparecer uma, ela está no lugar errado,
// porque o motor é que sabe aplicar regra e o dataset é que sabe qual regra é.

import { createServer, type Server } from 'node:http'
import {
  montar, ehPendencia, descansar, tiposDeDescanso,
  type Construcao, type Estado,
} from '../../motor/src/motor.ts'
import { Roteador, type Pedido, type Resposta } from './http.ts'
import { ErroHttp, construcaoInvalida, naoEncontrado, pedidoInvalido } from './erros.ts'
import { indice, lerColecao, lerItem } from './compendio.ts'
import { versaoDoDataset } from './versao.ts'
import { ArmazemEmArquivos, type Armazem } from './armazem.ts'
import { STATUS, CAMPOS_DE_ESTADO, type Personagem, type StatusDePersonagem } from './personagem.ts'
import { EmailJaUsado, type ArmazemDeUsuarios } from './usuarios.ts'
import { aoMudarEstado, LIMITE_PADRAO, type ArmazemDeEventos, type Motivo } from './eventos.ts'
import { paraOCliente as eventoParaOCliente } from './evento.ts'
import {
  conferirTamanhoDaSenha, criarToken, hashDeSenha, lerToken, normalizarEmail,
  paraOCliente, senhaConfere, type Usuario,
} from './usuario.ts'

const agora = () => new Date().toISOString()

/** Compêndio: imutável entre builds, então cache longo com o ETag da versão. */
function respostaDeCompendio(pedido: Pedido, corpo: unknown): Resposta {
  const etag = `"${versaoDoDataset()}"`
  const cabecalhos = { etag, 'cache-control': 'public, max-age=31536000, immutable' }
  if (pedido.cabecalhos['if-none-match'] === etag) return { status: 304, cabecalhos }
  return { corpo, cabecalhos }
}

function exigirObjeto(corpo: unknown, onde: string): Record<string, unknown> {
  if (!corpo || typeof corpo !== 'object' || Array.isArray(corpo)) {
    throw pedidoInvalido(`${onde} precisa ser um objeto JSON`)
  }
  return corpo as Record<string, unknown>
}

function validarConstrucao(c: unknown): Construcao {
  const o = exigirObjeto(c, 'construcao')
  for (const campo of ['especie', 'antecedente'] as const) {
    if (typeof o[campo] !== 'string') throw pedidoInvalido(`construcao.${campo} é obrigatório`)
  }
  if (!Array.isArray(o.niveis) || o.niveis.length === 0) {
    throw pedidoInvalido('construcao.niveis precisa ter ao menos uma classe')
  }
  for (const n of o.niveis as unknown[]) {
    const l = exigirObjeto(n, 'construcao.niveis[]')
    if (typeof l.classe !== 'string' || typeof l.nivel !== 'number') {
      throw pedidoInvalido('cada nível precisa de { classe, nivel }')
    }
    if (!Number.isInteger(l.nivel) || l.nivel < 1 || l.nivel > 20) {
      throw pedidoInvalido(`nível fora da faixa 1-20: ${l.nivel}`)
    }
  }
  const attrs = exigirObjeto(o.atributos_base, 'construcao.atributos_base')
  for (const [a, v] of Object.entries(attrs)) {
    if (typeof v !== 'number' || !Number.isInteger(v)) {
      throw pedidoInvalido(`atributo '${a}' precisa ser inteiro`)
    }
  }
  return o as unknown as Construcao
}

/**
 * Chama o motor e recusa só o que é defeito.
 *
 * Há duas coisas em `problemas`, e tratá-las igual foi o primeiro erro deste arquivo:
 *
 * - **defeito** — escolheu uma opção que não podia, repetiu, escolheu demais. A
 *   construção não pode ser aceita: 422, e nada é gravado.
 * - **pendência** — escolheu de menos, ou depende de outra escolha ainda não feita.
 *   Isso é o estado NORMAL de quem acabou de subir de nível: a Clériga que preparava
 *   9 magias no nível 5 passa a preparar 10 no 6. Recusar seria impedir de subir de
 *   nível quem fez tudo certo.
 *
 * As pendências saem na resposta, junto do checklist, porque são a mesma pergunta:
 * o que ainda falta você decidir.
 */
function montarComRegras(construcao: Construcao, estado: Estado) {
  const r = montar(construcao, estado)
  const defeitos = r.problemas.filter((p) => !ehPendencia(p))
  if (defeitos.length) {
    throw construcaoInvalida(
      `o motor recusou ${defeitos.length} escolha(s) desta construção`,
      defeitos,
    )
  }
  return { ...r, pendencias_de_escolha: r.problemas.filter(ehPendencia) }
}

/**
 * Ler um personagem nunca pode explodir por culpa do dataset.
 *
 * O `PLANO-MOTOR` §7 pede que a base mudar de um jeito que invalide uma escolha faça
 * o app **avisar em vez de quebrar**. Se o motor não conseguir montar — um id que
 * sumiu, uma regra que mudou —, a leitura devolve o personagem como está, sem ficha,
 * dizendo o que houve. O jogador continua vendo quem ele é e pode corrigir a escolha;
 * o que ele não pode é receber 500 e perder o personagem de vista.
 *
 * Vale só para LEITURA. Escrever (criar, subir de nível, escolher) continua recusando:
 * ali o cliente está propondo mudança, e propor mudança inválida é erro dele.
 */
function fichaDoPersonagem(p: Personagem, tolerante = false) {
  const versaoAtual = versaoDoDataset()
  if (tolerante) {
    try {
      return montarResposta(p, versaoAtual)
    } catch (e) {
      return {
        id: p.id,
        nome: p.nome,
        status: p.status,
        construcao: p.construcao,
        estado: p.estado,
        ficha: null,
        versao_do_dataset: p.versao_do_dataset,
        erro_de_ficha: {
          mensagem: (e as Error).message,
          detalhe: e instanceof ErroHttp ? e.detalhe : undefined,
          o_que_fazer:
            p.versao_do_dataset === versaoAtual
              ? 'a base não mudou desde a criação: isto é defeito, não desatualização'
              : `este personagem foi construído contra o dataset ${p.versao_do_dataset} e a base ` +
                `atual é ${versaoAtual}. Reveja as escolhas apontadas.`,
        },
      }
    }
  }
  return montarResposta(p, versaoAtual)
}

function montarResposta(p: Personagem, versaoAtual: string) {
  const r = montarComRegras(p.construcao, p.estado)
  return {
    id: p.id,
    nome: p.nome,
    status: p.status,
    construcao: p.construcao,
    estado: p.estado,
    ficha: r.ficha,
    /** O checklist é a tela de subir de nível: rótulo, quantidade e as opções. */
    checklist: r.checklist,
    /** Escolhas já feitas que ficaram incompletas — subir de nível produz estas. */
    pendencias_de_escolha: r.pendencias_de_escolha,
    versao_do_dataset: p.versao_do_dataset,
    ...(p.versao_do_dataset === versaoAtual
      ? {}
      : {
          aviso_de_versao:
            `este personagem foi construído contra o dataset ${p.versao_do_dataset}, ` +
            `e a base atual é ${versaoAtual}. A ficha acima foi recalculada com a base ` +
            `atual; confira as escolhas se algo parecer diferente.`,
        }),
  }
}

/**
 * O estado tem tipo, e aceitar qualquer coisa é guardar lixo que só aparece depois —
 * num `pontos_de_vida_atuais: "muito"` que quebra a soma três telas adiante.
 */
const TIPO_DO_ESTADO: Record<string, (v: unknown) => boolean> = {
  predicados_ativos: (v) => Array.isArray(v) && v.every((x) => typeof x === 'string'),
  portas_abertas: (v) => Array.isArray(v) && v.every((x) => typeof x === 'string'),
  condicoes: (v) => Array.isArray(v) && v.every((x) => typeof x === 'string'),
  pontos_de_vida_atuais: (v) => Number.isInteger(v),
  pontos_de_vida_temporarios: (v) => Number.isInteger(v) && (v as number) >= 0,
  fonte_dos_temporarios: (v) => typeof v === 'string',
  espacos_gastos: (v) => ehMapaDeInteiros(v),
  recursos_gastos: (v) => ehMapaDeInteiros(v),
  concentracao: (v) => v === null || typeof v === 'string',
}

function ehMapaDeInteiros(v: unknown): boolean {
  return (
    !!v &&
    typeof v === 'object' &&
    !Array.isArray(v) &&
    Object.values(v as Record<string, unknown>).every((n) => Number.isInteger(n) && (n as number) >= 0)
  )
}

function conferirTiposDoEstado(corpo: Record<string, unknown>): void {
  for (const [campo, valor] of Object.entries(corpo)) {
    const eDoTipo = TIPO_DO_ESTADO[campo]
    if (eDoTipo && !eDoTipo(valor)) {
      throw pedidoInvalido(`'${campo}' recebeu um valor que não é do tipo esperado`, { valor })
    }
  }
}

/**
 * O contexto opcional de uma mudança de estado.
 *
 * Hoje só carrega a magia conjurada. O nome vem do compêndio na hora de gravar, e
 * fica congelado no evento junto do id: se a magia for renomeada no dataset — como
 * as quatro da fase 20 —, a linha antiga continua dizendo o nome de quando aconteceu.
 * Id que não existe não é erro: o evento fica sem nome e a frase cai para "gastou um
 * espaço de 3º", que continua verdadeira.
 */
function lerMotivo(bruto: unknown): Motivo | undefined {
  if (!bruto || typeof bruto !== 'object') return undefined
  const magia_id = (bruto as { magia_id?: unknown }).magia_id
  if (typeof magia_id !== 'string' || !magia_id) return undefined
  try {
    const magia = lerItem('magias', magia_id) as { nome?: string }
    return { magia_id, magia_nome: magia.nome }
  } catch {
    return { magia_id }
  }
}

export type OpcoesDeSessao = { segredo: string; horas: number }

export function criarRoteador(
  armazem: Armazem,
  usuarios: ArmazemDeUsuarios,
  eventos: ArmazemDeEventos,
  sessao: OpcoesDeSessao,
): Roteador {
  const r = new Roteador()

  // ------------------------------------------------------------------- contas

  /**
   * Quem está pedindo.
   *
   * Sem token, ou com token que não presta, é 401 — e a mensagem é a mesma nos dois
   * casos, de propósito. Distinguir "assinatura inválida" de "expirado" ajuda mais
   * quem está tentando adivinhar do que quem esqueceu de entrar.
   */
  const exigirUsuario = async (p: Pedido): Promise<Usuario> => {
    const cabecalho = p.cabecalhos.authorization ?? ''
    const token = cabecalho.startsWith('Bearer ') ? cabecalho.slice(7).trim() : ''
    const id = token ? lerToken(token, sessao.segredo) : undefined
    const usuario = id ? await usuarios.ler(id) : undefined
    if (!usuario) throw new ErroHttp(401, 'nao_autenticado', 'entre para continuar')
    return usuario
  }

  const comToken = (u: Usuario) => ({
    usuario: paraOCliente(u),
    token: criarToken(u.id, sessao.segredo, sessao.horas),
    expira_em_horas: sessao.horas,
  })

  r.rota('POST', '/contas', async (p) => {
    const corpo = exigirObjeto(p.corpo, 'o corpo')
    const email = normalizarEmail(corpo.email)
    const senha = conferirTamanhoDaSenha(corpo.senha)
    try {
      const u = await usuarios.criar({
        email,
        senha_hash: hashDeSenha(senha),
        criado_em: agora(),
      })
      return { status: 201, corpo: comToken(u) }
    } catch (e) {
      if (e instanceof EmailJaUsado) {
        throw new ErroHttp(409, 'email_ja_usado', 'já existe uma conta com esse e-mail')
      }
      throw e
    }
  })

  r.rota('POST', '/sessoes', async (p) => {
    const corpo = exigirObjeto(p.corpo, 'o corpo')
    const email = normalizarEmail(corpo.email)
    const senha = typeof corpo.senha === 'string' ? corpo.senha : ''
    const u = await usuarios.porEmail(email)

    // A MESMA resposta para "e-mail não existe" e "senha errada". Responder
    // "essa conta não existe" entrega ao curioso quais e-mails estão cadastrados.
    const naoConfere = new ErroHttp(401, 'credenciais_invalidas', 'e-mail ou senha não conferem')
    if (!u || !senhaConfere(senha, u.senha_hash)) throw naoConfere

    u.ultimo_login = agora()
    await usuarios.gravar(u)
    return { corpo: comToken(u) }
  })

  r.rota('GET', '/eu', async (p) => ({ corpo: paraOCliente(await exigirUsuario(p)) }))

  r.rota('GET', '/saude', () => ({
    corpo: { ok: true, versao_do_dataset: versaoDoDataset() },
  }))

  // ------------------------------------------------------------------ compêndio
  r.rota('GET', '/compendio', (p) =>
    respostaDeCompendio(p, { versao_do_dataset: versaoDoDataset(), colecoes: indice() }))

  r.rota('GET', '/compendio/:nome', (p) =>
    respostaDeCompendio(p, lerColecao(p.parametros.nome)))

  r.rota('GET', '/compendio/:nome/:id', (p) =>
    respostaDeCompendio(p, lerItem(p.parametros.nome, p.parametros.id)))

  // ---------------------------------------------------------------- personagens
  r.rota('GET', '/personagens', async (pedido) => ({
    corpo: {
      itens: (await armazem.listar((await exigirUsuario(pedido)).id)).map((p) => ({
        id: p.id,
        nome: p.nome,
        status: p.status,
        niveis: p.construcao.niveis,
        especie: p.construcao.especie,
        ultimo_acesso: p.ultimo_acesso,
      })),
    },
  }))

  r.rota('POST', '/personagens', async (p) => {
    const dono = await exigirUsuario(p)
    const corpo = exigirObjeto(p.corpo, 'o corpo')
    if (typeof corpo.nome !== 'string' || !corpo.nome.trim()) {
      throw pedidoInvalido('nome é obrigatório')
    }
    const construcao = validarConstrucao(corpo.construcao)
    const status = (corpo.status ?? 'ativo') as StatusDePersonagem
    if (!STATUS.includes(status)) {
      throw pedidoInvalido(`status precisa ser um de: ${STATUS.join(', ')}`)
    }
    const estado = (corpo.estado ?? {}) as Personagem['estado']
    montarComRegras(construcao, estado) // recusa antes de gravar, nunca depois
    const criado = await armazem.criar({
      usuario_id: dono.id,
      nome: corpo.nome.trim(),
      status,
      construcao,
      estado,
      versao_do_dataset: versaoDoDataset(),
      criado_em: agora(),
      ultimo_acesso: agora(),
    })
    return { status: 201, corpo: fichaDoPersonagem(criado), cabecalhos: { location: `/personagens/${criado.id}` } }
  })

  /**
   * O personagem, se ele existe E é seu.
   *
   * Personagem de outra pessoa responde **404, não 403**. Um 403 confirmaria que
   * aquele id existe, o que transforma a rota num oráculo para descobrir ids
   * alheios. Para quem não é dono, o personagem simplesmente não existe.
   */
  const exigirPersonagem = async (pedido: Pedido): Promise<Personagem> => {
    const dono = await exigirUsuario(pedido)
    const id = pedido.parametros.id
    const p = await armazem.ler(id)
    if (!p || p.usuario_id !== dono.id) throw naoEncontrado(`personagem '${id}'`)
    return p
  }

  r.rota('GET', '/personagens/:id', async (p) => {
    const personagem = await exigirPersonagem(p)
    // "ordenado por último acesso, o mais recente no topo" (PLANO-APP, Fase A)
    personagem.ultimo_acesso = agora()
    await armazem.gravar(personagem)
    return { corpo: fichaDoPersonagem(personagem, true) }
  })

  r.rota('DELETE', '/personagens/:id', async (p) => {
    // Passa por `exigirPersonagem` de propósito: apagar direto pelo id apagaria o
    // personagem de outra pessoa.
    const personagem = await exigirPersonagem(p)
    if (!(await armazem.apagar(personagem.id))) throw naoEncontrado(`personagem '${personagem.id}'`)
    return { status: 204 }
  })

  // Só ESTADO. Construção não entra aqui: mudar quem o personagem é passa por
  // /escolhas ou /subir-nivel, que conferem contra as regras.
  r.rota('PATCH', '/personagens/:id/estado', async (p) => {
    const personagem = await exigirPersonagem(p)
    const bruto = exigirObjeto(p.corpo, 'o corpo')

    // `motivo` NÃO é estado: ele não é gravado no personagem e não muda ficha
    // nenhuma. Serve só para o evento poder dizer "conjurou Bola de Fogo" em vez
    // de "gastou um espaço de 3º". Sai do corpo antes da checagem justamente para
    // não ser recusado como campo desconhecido — e para não entrar no estado.
    const { motivo: motivoBruto, ...corpo } = bruto
    const motivo = lerMotivo(motivoBruto)

    const permitidos = new Set<string>(CAMPOS_DE_ESTADO)
    const recusados = Object.keys(corpo).filter((k) => !permitidos.has(k))
    if (recusados.length) {
      throw pedidoInvalido(
        `estes campos não são estado: ${recusados.join(', ')}. ` +
        `Estado é o que a mesa muda; o resto é derivado ou é construção.`,
        { aceitos: [...permitidos] },
      )
    }
    conferirTiposDoEstado(corpo)

    return { corpo: await gravarEstado(personagem, corpo, motivo) }
  })

  /**
   * Descansar.
   *
   * Não é um PATCH com os campos certos porque quem sabe QUAIS são os campos
   * certos é o motor, lendo o dataset: o Bruxo recupera espaços no Descanso Curto
   * e o Bárbaro recupera uma Fúria, e nenhuma dessas duas frases pode morar no
   * cliente. O app diz "descansei"; o que isso significa é resposta do motor.
   */
  r.rota('POST', '/personagens/:id/descanso', async (p) => {
    const personagem = await exigirPersonagem(p)
    const corpo = exigirObjeto(p.corpo, 'o corpo')
    const tipo = corpo.tipo
    if (typeof tipo !== 'string') {
      throw pedidoInvalido('informe `tipo`: qual descanso foi feito', {
        aceitos: tiposDeDescanso().map((t) => t.id),
      })
    }

    const montado = montarComRegras(personagem.construcao, personagem.estado)
    const efeito = descansar(tipo, montado.contexto, {
      pontos_de_vida_maximos: montado.ficha.pontos_de_vida_maximos.valor as number,
      recursos: montado.ficha.recursos,
    }, personagem.estado)

    const { o_que_voltou, ...mudanca } = efeito
    const resposta = await gravarEstado(personagem, mudanca as Partial<Personagem['estado']>)
    return { corpo: { ...resposta, descanso: { tipo, o_que_voltou } } }
  })

  /**
   * Grava uma mudança de estado, com o evento que ela gera.
   *
   * Um caminho só para os dois jeitos de mexer no estado (o PATCH campo a campo e
   * o descanso): a ordem — recalcular, registrar, gravar o personagem, gravar os
   * eventos — é a parte fácil de errar, e errá-la de dois jeitos diferentes seria
   * pior ainda.
   */
  async function gravarEstado(
    personagem: Personagem,
    corpo: Partial<Personagem['estado']>,
    motivo?: Motivo,
  ) {
    const antes = personagem.estado
    const depois = { ...personagem.estado, ...corpo }

    // O retrato do momento vem da ficha recalculada AGORA, e é ele que o evento
    // congela: o "26" de "PV 20/26" tem de continuar 26 quando o personagem subir
    // de nível.
    const ficha = montar(personagem.construcao, depois).ficha
    const registros = aoMudarEstado(antes, depois, {
      pv_maximo: ficha.pontos_de_vida_maximos.valor as number,
      espacos: ficha.conjuracao?.espacos ?? {},
    }, motivo)

    personagem.estado = depois
    personagem.ultimo_acesso = agora()
    await armazem.gravar(personagem)

    // Grava DEPOIS do personagem: um evento sobre uma mudança que não chegou a
    // acontecer seria pior do que uma mudança sem evento.
    const gravados = await eventos.registrar(registros.map((e) => ({
      ...e,
      personagem_id: personagem.id,
      usuario_id: personagem.usuario_id,
      em: agora(),
    })))

    return { ...fichaDoPersonagem(personagem), eventos: gravados.map(eventoParaOCliente) }
  }

  r.rota('GET', '/personagens/:id/historico', async (p) => {
    const personagem = await exigirPersonagem(p)
    const limite = p.consulta.get('limite')
    const pagina = await eventos.listar(personagem.id, {
      limite: limite ? Number(limite) : LIMITE_PADRAO,
      antesDe: p.consulta.get('antes_de') ?? undefined,
    })
    return { corpo: { itens: pagina.itens.map(eventoParaOCliente), proximo: pagina.proximo } }
  })

  r.rota('POST', '/personagens/:id/subir-nivel', async (p) => {
    const personagem = await exigirPersonagem(p)
    const corpo = (p.corpo ?? {}) as { classe?: string }
    const niveis = personagem.construcao.niveis
    const classe = corpo.classe ?? (niveis.length === 1 ? niveis[0].classe : undefined)
    if (!classe) {
      throw pedidoInvalido('diga em qual classe subir: este personagem tem mais de uma')
    }
    const linha = niveis.find((n) => n.classe === classe)
    if (!linha) {
      // Multiclasse é decisão adiada da Fase 0 e o dataset a registra sem aplicá-la.
      throw pedidoInvalido(
        `'${classe}' não é uma classe deste personagem. Começar uma classe nova é ` +
        `multiclasse, que está adiada (PENDENCIAS, seção 4).`,
      )
    }
    if (linha.nivel >= 20) throw pedidoInvalido(`${classe} já está no nível 20`)

    const antes = montar(personagem.construcao, personagem.estado)
    // Sobe num RASCUNHO. Se o motor recusar, o personagem guardado não pode ter sido
    // tocado — e depender de o armazém ter devolvido uma cópia seria depender de um
    // detalhe da implementação do armazém.
    const rascunho: Construcao = JSON.parse(JSON.stringify(personagem.construcao))
    rascunho.niveis.find((n) => n.classe === classe)!.nivel = linha.nivel + 1
    const depois = montarComRegras(rascunho, personagem.estado)
    personagem.construcao = rascunho
    personagem.ultimo_acesso = agora()
    await armazem.gravar(personagem)

    // O que interessa ao jogador é a DIFERENÇA: o que chegou agora e o que abriu
    // para escolher. É o "subir de nível sem esquecer nada" do PLANO-APP.
    const jaTinha = new Set(antes.checklist.map((c) => c.escolha_id))
    const antesIncompletas = new Set(
      antes.problemas.filter(ehPendencia).map((p) => p.escolha_id),
    )
    return {
      corpo: {
        classe,
        nivel: linha.nivel + 1,
        /** O que este nível abriu de novo — o checklist de subir de nível. */
        escolhas_novas: depois.checklist.filter((c) => !jaTinha.has(c.escolha_id)),
        /** E o que já era escolhido mas agora pede mais: mais uma magia preparada. */
        escolhas_a_completar: depois.pendencias_de_escolha.filter(
          (p) => !antesIncompletas.has(p.escolha_id),
        ),
        checklist: depois.checklist,
        pendencias_de_escolha: depois.pendencias_de_escolha,
        ficha: depois.ficha,
      },
    }
  })

  /**
   * A prévia: o que ESTA escolha abriria, sem gravar nada.
   *
   * O jogador escolhia um talento no escuro. O Iniciado em Magia só revela que pede
   * lista, atributo e três magias **depois** de gravado — e para descobrir o que ele
   * faz era preciso primeiro aceitá-lo. A prévia monta a mesma construção com as
   * escolhas propostas e devolve o checklist resultante, sem tocar no armazém.
   *
   * Cabe aqui e não numa tela porque o motor é puro: montar de novo é barato e a
   * resposta é a verdade, não um palpite do frontend sobre o que o talento faz.
   *
   * Pendência não é erro numa prévia — ela é justamente o que se quer ver. Defeito
   * continua sendo 422: propor o inválido é erro do cliente aqui como em qualquer
   * outro lugar.
   */
  r.rota('POST', '/personagens/:id/escolhas/previa', async (p) => {
    const personagem = await exigirPersonagem(p)
    const corpo = exigirObjeto(p.corpo, 'o corpo')
    const escolhas = exigirObjeto(corpo.escolhas ?? corpo, 'escolhas')
    const r = montarComRegras(
      {
        ...personagem.construcao,
        escolhas: { ...(personagem.construcao.escolhas ?? {}), ...(escolhas as never) },
      },
      personagem.estado,
    )
    return {
      corpo: {
        checklist: r.checklist,
        pendencias_de_escolha: r.pendencias_de_escolha,
        /** O que sumiu do checklist é o que estas escolhas responderam. */
        respondidas: Object.keys(escolhas),
      },
    }
  })

  r.rota('POST', '/personagens/:id/escolhas', async (p) => {
    const personagem = await exigirPersonagem(p)
    const corpo = exigirObjeto(p.corpo, 'o corpo')
    const escolhas = exigirObjeto(corpo.escolhas ?? corpo, 'escolhas')
    const construcao: Construcao = {
      ...personagem.construcao,
      escolhas: { ...(personagem.construcao.escolhas ?? {}), ...(escolhas as never) },
    }
    // Confere ANTES de gravar: escolha inválida não entra no personagem nem por um
    // instante. O motor devolve o que está errado, e o app mostra.
    montarComRegras(construcao, personagem.estado)
    personagem.construcao = construcao
    // A versão NÃO é re-carimbada aqui: ela diz contra qual base o personagem foi
    // construído. Re-carimbar faria o `aviso_de_versao` sumir ao responder uma
    // escolha qualquer, escondendo justamente o que ele existe para mostrar.
    personagem.ultimo_acesso = agora()
    await armazem.gravar(personagem)
    return { corpo: fichaDoPersonagem(personagem) }
  })

  return r
}

export function criarServidor(
  armazem: Armazem,
  usuarios: ArmazemDeUsuarios,
  eventos: ArmazemDeEventos,
  sessao: OpcoesDeSessao,
): Server {
  const roteador = criarRoteador(armazem, usuarios, eventos, sessao)
  return createServer((req, res) => {
    void roteador.atender(req, res)
  })
}

export { ArmazemEmArquivos }
