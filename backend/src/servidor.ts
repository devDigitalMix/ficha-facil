// Os endpoints da seção 7 do PLANO-MOTOR.
//
// O backend é fino de propósito: ele guarda a construção, serve o compêndio e chama
// o motor. Nenhuma regra de D&D mora aqui — se aparecer uma, ela está no lugar errado,
// porque o motor é que sabe aplicar regra e o dataset é que sabe qual regra é.

import { createServer, type Server } from 'node:http'
import { montar, ehPendencia, type Construcao, type Estado } from '../../motor/src/motor.ts'
import { Roteador, type Pedido, type Resposta } from './http.ts'
import { ErroHttp, construcaoInvalida, naoEncontrado, pedidoInvalido } from './erros.ts'
import { indice, lerColecao, lerItem } from './compendio.ts'
import { versaoDoDataset } from './versao.ts'
import { ArmazemEmArquivos, type Armazem } from './armazem.ts'
import { STATUS, CAMPOS_DE_ESTADO, type Personagem, type StatusDePersonagem } from './personagem.ts'

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

export function criarRoteador(armazem: Armazem): Roteador {
  const r = new Roteador()

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
  r.rota('GET', '/personagens', () => ({
    corpo: {
      itens: armazem.listar().map((p) => ({
        id: p.id,
        nome: p.nome,
        status: p.status,
        niveis: p.construcao.niveis,
        especie: p.construcao.especie,
        ultimo_acesso: p.ultimo_acesso,
      })),
    },
  }))

  r.rota('POST', '/personagens', (p) => {
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
    const criado = armazem.criar({
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

  const exigirPersonagem = (id: string): Personagem => {
    const p = armazem.ler(id)
    if (!p) throw naoEncontrado(`personagem '${id}'`)
    return p
  }

  r.rota('GET', '/personagens/:id', (p) => {
    const personagem = exigirPersonagem(p.parametros.id)
    // "ordenado por último acesso, o mais recente no topo" (PLANO-APP, Fase A)
    personagem.ultimo_acesso = agora()
    armazem.gravar(personagem)
    return { corpo: fichaDoPersonagem(personagem, true) }
  })

  r.rota('DELETE', '/personagens/:id', (p) => {
    if (!armazem.apagar(p.parametros.id)) throw naoEncontrado(`personagem '${p.parametros.id}'`)
    return { status: 204 }
  })

  // Só ESTADO. Construção não entra aqui: mudar quem o personagem é passa por
  // /escolhas ou /subir-nivel, que conferem contra as regras.
  r.rota('PATCH', '/personagens/:id/estado', (p) => {
    const personagem = exigirPersonagem(p.parametros.id)
    const corpo = exigirObjeto(p.corpo, 'o corpo')
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
    personagem.estado = { ...personagem.estado, ...corpo }
    personagem.ultimo_acesso = agora()
    armazem.gravar(personagem)
    return { corpo: fichaDoPersonagem(personagem) }
  })

  r.rota('POST', '/personagens/:id/subir-nivel', (p) => {
    const personagem = exigirPersonagem(p.parametros.id)
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
    armazem.gravar(personagem)

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

  r.rota('POST', '/personagens/:id/escolhas', (p) => {
    const personagem = exigirPersonagem(p.parametros.id)
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
    armazem.gravar(personagem)
    return { corpo: fichaDoPersonagem(personagem) }
  })

  return r
}

export function criarServidor(armazem: Armazem): Server {
  const roteador = criarRoteador(armazem)
  return createServer((req, res) => {
    void roteador.atender(req, res)
  })
}

export { ArmazemEmArquivos }
