// A ficha em sessão: vida, espaços, escolhas pendentes e histórico.
//
// Toda alteração passa por `PATCH /estado`, que é o único caminho que gera evento.
// A tela nunca calcula nada da ficha — ela mostra o que o motor devolveu. O "10 + 3
// DES + 4 SAB" que aparece ao tocar num número é a `parcelas` do próprio motor.

import { useCallback, useEffect, useState } from 'react'
import {
  api, ErroDaApi, lerCatalogo,
  type Estado, type ItemDoCompendio, type MagiaNaFicha as MagiaDaFicha,
  type Personagem, type Recurso as RecursoDaFicha, type Resultado,
} from './api.ts'
import { Escolhas, type Valor } from './Escolhas.tsx'
import { Historico } from './Historico.tsx'

export function Ficha({ id, aoVoltar }: { id: string; aoVoltar: () => void }) {
  const [p, setP] = useState<Personagem>()
  const [erro, setErro] = useState('')
  /** A última coisa que aconteceu, para o clique não sumir sem resposta. */
  const [aviso, setAviso] = useState('')
  const [aba, setAba] = useState<'ficha' | 'detalhes' | 'escolhas' | 'historico'>('ficha')
  const [versaoDoHistorico, recarregarHistorico] = useState(0)

  const carregar = useCallback(async () => {
    try {
      setP(await api.get<Personagem>(`/personagens/${id}`))
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : 'não consegui carregar')
    }
  }, [id])

  useEffect(() => { void carregar() }, [carregar])

  async function mudarEstado(mudanca: Estado & { motivo?: { magia_id: string } }) {
    setErro('')
    try {
      const r = await api.patch<Personagem>(`/personagens/${id}/estado`, mudanca)
      setP((atual) => (atual ? { ...atual, estado: r.estado, ficha: r.ficha } : atual))
      recarregarHistorico((v) => v + 1)
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : 'não consegui gravar')
    }
  }

  /**
   * Conjurar: gasta o espaço e diz QUAL magia foi, para o histórico não dizer só
   * "gastou um espaço de 3º".
   */
  /**
   * Conjurar: a tela diz QUAL magia, e o servidor diz o que aquilo custou.
   *
   * Antes esta função gastava um espaço sempre — e saía cedo no truque, que é por
   * que clicar em "usar" num truque não fazia absolutamente nada. Quem sabe se a
   * magia custa espaço, um uso do talento ou nada é o motor, lendo o dataset.
   */
  async function conjurar(magia: MagiaDaFicha, comEspaco = false) {
    setErro('')
    try {
      const r = await api.post<Personagem & { eventos?: { resumo: string }[] }>(
        `/personagens/${id}/conjurar`,
        { magia_id: magia.id, ...(comEspaco ? { com_espaco: true } : {}) },
      )
      setP((atual) => (atual ? { ...atual, estado: r.estado, ficha: r.ficha } : atual))
      recarregarHistorico((v) => v + 1)
      // O aviso é o feedback que faltava: truque não muda número nenhum na tela, e
      // sem uma palavra o jogador não sabia se tinha clicado.
      setAviso(r.eventos?.[0]?.resumo ?? `conjurou ${magia.nome}`)
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : 'não consegui conjurar')
    }
  }

  /** Devolve o que o servidor disse ter voltado, para a tela poder mostrá-lo. */
  async function descansar(tipo: string): Promise<string[] | undefined> {
    setErro('')
    try {
      const r = await api.post<Personagem & { descanso?: { o_que_voltou: string[] } }>(
        `/personagens/${id}/descanso`, { tipo })
      setP((atual) => (atual ? { ...atual, estado: r.estado, ficha: r.ficha } : atual))
      recarregarHistorico((v) => v + 1)
      return r.descanso?.o_que_voltou ?? []
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : 'não consegui registrar o descanso')
      return undefined
    }
  }

  async function responder(escolhas: Record<string, Valor>) {
    setErro('')
    try {
      setP(await api.post<Personagem>(`/personagens/${id}/escolhas`, { escolhas }))
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : 'o motor recusou essa escolha')
    }
  }

  if (erro && !p) return <div className="pagina"><p className="erro">{erro}</p></div>
  if (!p) return <div className="pagina"><p className="vazio">carregando…</p></div>

  const faltam = p.checklist.length
  const nivel = p.construcao.niveis.reduce((s, n) => s + n.nivel, 0)

  return (
    <div className="pagina">
      <div className="espalha" style={{ marginBottom: 12 }}>
        <button className="discreto" onClick={aoVoltar}>← meus personagens</button>
        <span className={`marca ${p.status}`}>{p.status}</span>
      </div>

      <h2 style={{ margin: '0 0 2px' }}>{p.nome}</h2>
      <p className="fraco" style={{ marginTop: 0 }}>
        {p.construcao.especie} · {p.construcao.niveis.map((n) => `${n.classe} ${n.nivel}`).join(' / ')}
        {p.construcao.niveis.length > 1 && ` · nível ${nivel}`}
      </p>

      {erro && <p className="erro">{erro}</p>}
      {aviso && (
        <p className="aviso-de-acao" onAnimationEnd={() => setAviso('')}>{aviso}</p>
      )}
      {p.aviso_de_versao && <p className="aviso">{p.aviso_de_versao}</p>}
      {p.erro_de_ficha && (
        <p className="erro">
          Não consegui montar a ficha: {p.erro_de_ficha.mensagem}
          <br /><span className="fraco">{p.erro_de_ficha.o_que_fazer}</span>
        </p>
      )}

      <div className="linha" style={{ marginBottom: 12 }}>
        <button className="pilula" aria-pressed={aba === 'ficha'} onClick={() => setAba('ficha')}>
          Ficha
        </button>
        <button className="pilula" aria-pressed={aba === 'detalhes'} onClick={() => setAba('detalhes')}>
          Detalhes
        </button>
        <button className="pilula" aria-pressed={aba === 'escolhas'} onClick={() => setAba('escolhas')}>
          Escolhas{faltam ? ` (${faltam})` : ''}
        </button>
        <button className="pilula" aria-pressed={aba === 'historico'} onClick={() => setAba('historico')}>
          Histórico
        </button>
      </div>

      {aba === 'ficha' && p.ficha && (
        <>
          <Vida ficha={p.ficha} estado={p.estado} aoMudar={mudarEstado} />
          <Descanso personagemId={id} aoDescansar={descansar} />
          <Numeros ficha={p.ficha} />
          <Espacos ficha={p.ficha} estado={p.estado} aoMudar={mudarEstado} />
          <Recursos ficha={p.ficha} estado={p.estado} aoMudar={mudarEstado} />
          {/* Ataques antes das magias: a lista de magias fica comprida, e o ataque
              é o que se procura mais vezes na mesa. */}
          <Ataques ficha={p.ficha} />
          <Magias ficha={p.ficha} estado={p.estado} aoConjurar={conjurar} />
          <Inventario estado={p.estado} aoMudar={mudarEstado} />
        </>
      )}

      {aba === 'detalhes' && p.ficha && (
        <Detalhes ficha={p.ficha} construcao={p.construcao} />
      )}

      {aba === 'escolhas' && (
        <Escolhas
          itens={p.checklist} antecedente={p.construcao.antecedente}
          personagemId={id} aoResponder={responder}
        />
      )}

      {aba === 'historico' && <Historico personagemId={id} versao={versaoDoHistorico} />}
    </div>
  )
}

// ----------------------------------------------------------------------- vida

function Vida({
  ficha, estado, aoMudar,
}: {
  ficha: NonNullable<Personagem['ficha']>
  estado: Estado
  aoMudar: (m: Estado) => Promise<void>
}) {
  const [quanto, setQuanto] = useState(1)
  const [deOndeVem, setDeOndeVem] = useState(false)
  const maximo = ficha.pontos_de_vida_maximos.valor
  // Personagem sem PV marcado está com a vida cheia — a mesma convenção do backend.
  const atual = estado.pontos_de_vida_atuais ?? maximo
  const temporarios = estado.pontos_de_vida_temporarios ?? 0
  const fracao = Math.max(0, Math.min(1, atual / maximo))

  /** Dano come os temporários primeiro; cura não passa do máximo. */
  function aplicar(sinal: 1 | -1) {
    const n = Math.max(1, quanto)
    if (sinal === -1) {
      const dosTemporarios = Math.min(temporarios, n)
      const resto = n - dosTemporarios
      void aoMudar({
        pontos_de_vida_atuais: Math.max(0, atual - resto),
        ...(dosTemporarios ? { pontos_de_vida_temporarios: temporarios - dosTemporarios } : {}),
      })
    } else {
      void aoMudar({ pontos_de_vida_atuais: Math.min(maximo, atual + n) })
    }
  }

  return (
    <div className="painel">
      <div className="espalha">
        <h2 style={{ margin: 0 }}>Pontos de Vida</h2>
        {/* O máximo é clicável como a CA e a Iniciativa: ele TAMBÉM é uma conta, e
            até aqui era o único número da ficha que não dizia de onde vinha. */}
        <strong
          style={{ fontSize: 20, cursor: 'pointer' }}
          onClick={() => setDeOndeVem((v) => !v)}
          title="de onde vem o máximo"
        >
          {atual}/<span className="clicavel">{maximo}</span>
          {temporarios > 0 && <span className="fraco"> +{temporarios}</span>}
        </strong>
      </div>
      {deOndeVem && (
        <Proveniencia rotulo="máximo" resultado={ficha.pontos_de_vida_maximos} />
      )}
      <div className="barra"><i className={fracao <= 0.3 ? 'baixo' : ''} style={{ width: `${fracao * 100}%` }} /></div>
      <div className="linha">
        <button onClick={() => aplicar(-1)} aria-label="tirar vida">− dano</button>
        <input
          type="number" min={1} value={quanto} style={{ width: 80, textAlign: 'center' }}
          onChange={(e) => setQuanto(Math.max(1, Number(e.target.value) || 1))}
        />
        <button onClick={() => aplicar(1)} aria-label="dar vida">+ cura</button>
        <button
          className="discreto"
          onClick={() => void aoMudar({ pontos_de_vida_temporarios: temporarios + Math.max(1, quanto) })}
        >
          + temporários
        </button>
      </div>
    </div>
  )
}

// -------------------------------------------------------------------- números

function Numeros({ ficha }: { ficha: NonNullable<Personagem['ficha']> }) {
  const [aberto, setAberto] = useState('')
  const campos: [string, Resultado | number][] = [
    ['CA', ficha.classe_de_armadura],
    ['Iniciativa', ficha.iniciativa],
    ['Percepção', ficha.percepcao_passiva],
    ['Prof.', ficha.bonus_de_proficiencia],
    ['Desloc.', ficha.deslocamento_m],
  ]

  return (
    <div className="painel">
      <h2>Números</h2>
      <div className="numeros">
        {campos.map(([rotulo, v]) => {
          const ehResultado = typeof v === 'object'
          return (
            <div
              key={rotulo}
              className={`numero ${ehResultado ? 'clicavel' : ''}`}
              onClick={() => ehResultado && setAberto(aberto === rotulo ? '' : rotulo)}
            >
              <div className="valor">{ehResultado ? (v as Resultado).valor : v}</div>
              <div className="rotulo">{rotulo}</div>
            </div>
          )
        })}
      </div>

      {aberto && (
        <Proveniencia
          rotulo={aberto}
          resultado={campos.find(([r]) => r === aberto)![1] as Resultado}
        />
      )}

      <h3>Atributos</h3>
      <div className="numeros">
        {Object.entries(ficha.modificadores).map(([a, m]) => (
          <div className="numero" key={a}>
            {/* A PONTUAÇÃO acima, o modificador embaixo: a ficha de papel mostra as
                duas, e é pela pontuação que se confere um aumento de atributo. */}
            <div className="valor">{ficha.atributos?.[a] ?? '—'}</div>
            <div className="rotulo">
              {a} <span className="fraco">{m >= 0 ? `+${m}` : m}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * "CA = 10 + 3 (DES) + 2 (armadura)".
 *
 * A proveniência vem PRONTA do motor, em `parcelas`: a tela não recalcula nada,
 * só escreve. Vale para qualquer número da ficha — foi por isso que virou
 * componente: os Pontos de Vida máximos precisavam da mesma explicação, e ela
 * estava presa dentro do painel dos Números.
 */
function Proveniencia({ rotulo, resultado }: { rotulo: string; resultado: Resultado }) {
  const soma = (p: { valor: number | string }) =>
    (Number(p.valor) < 0 ? `− ${Math.abs(Number(p.valor))}` : `${p.valor}`)

  return (
    <div className="proveniencia">
      {rotulo} = {resultado.parcelas.map((x) => `${soma(x)} (${x.rotulo})`).join(' + ')}
      {/* A parcela que é ela mesma uma conta se abre embaixo: "11 de PV do nível 1"
          não responde por que são 11, e a pergunta era essa. */}
      {resultado.parcelas.some((p) => p.parcelas?.length) && (
        <ul className="detalhe-parcelas">
          {resultado.parcelas.filter((p) => p.parcelas?.length).map((p) => (
            <li key={p.rotulo}>
              {p.rotulo}: {p.parcelas!.map((x) => `${soma(x)} (${x.rotulo})`).join(' + ')}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

// -------------------------------------------------------------------- espaços

function Espacos({
  ficha, estado, aoMudar,
}: {
  ficha: NonNullable<Personagem['ficha']>
  estado: Estado
  aoMudar: (m: Estado) => Promise<void>
}) {
  if (!ficha.conjuracao) return null
  const gastos = estado.espacos_gastos ?? {}
  const circulos = Object.keys(ficha.conjuracao.espacos).sort()

  function mudar(circulo: string, delta: number) {
    const total = ficha.conjuracao!.espacos[circulo]
    const novo = Math.max(0, Math.min(total, (gastos[circulo] ?? 0) + delta))
    void aoMudar({ espacos_gastos: { ...gastos, [circulo]: novo } })
  }

  return (
    <div className="painel">
      <div className="espalha">
        <h2 style={{ margin: 0 }}>Espaços de magia</h2>
        <span className="fraco">CD {ficha.conjuracao.cd_para_evitar_sua_magia.valor}</span>
      </div>
      {circulos.map((c) => {
        const total = ficha.conjuracao!.espacos[c]
        const usados = gastos[c] ?? 0
        return (
          <div className="espalha" key={c} style={{ padding: '6px 0' }}>
            <span>{c}º círculo</span>
            <span className="linha">
              <button onClick={() => mudar(c, -1)} disabled={usados === 0}>−</button>
              <strong style={{ minWidth: 46, textAlign: 'center' }}>{total - usados}/{total}</strong>
              <button onClick={() => mudar(c, +1)} disabled={usados >= total}>gastar</button>
            </span>
          </div>
        )
      })}
    </div>
  )
}

// -------------------------------------------------------------------- ataques

function Ataques({ ficha }: { ficha: NonNullable<Personagem['ficha']> }) {
  if (!ficha.ataques?.length) return null
  return (
    <div className="painel">
      <h2>Ataques</h2>
      {ficha.ataques.map((a) => (
        <div className="espalha" key={a.arma} style={{ padding: '6px 0' }}>
          <span>
            {a.nome}
            {!a.proficiente && <span className="fraco"> · sem proficiência</span>}
          </span>
          <span>
            <strong>{a.jogada.valor >= 0 ? `+${a.jogada.valor}` : a.jogada.valor}</strong>{' '}
            <span className="fraco">
              {[...a.dano.dados, a.dano.valor > 0 ? `+${a.dano.valor}` : null]
                .filter(Boolean).join(' ')} {a.tipo_dano}
            </span>
          </span>
        </div>
      ))}
    </div>
  )
}

// -------------------------------------------------------------------- descanso

/**
 * Os botões de descanso.
 *
 * A tela NÃO sabe o que um descanso devolve — ela manda o tipo e mostra o que o
 * servidor respondeu ter voltado. É de propósito: quem sabe que o Bruxo recupera
 * espaços no Descanso Curto é o dataset, e essa frase não pode existir aqui.
 */
function Descanso({ personagemId, aoDescansar }: {
  personagemId: string
  aoDescansar: (tipo: string) => Promise<string[] | undefined>
}) {
  const [ocupado, setOcupado] = useState('')
  const [voltou, setVoltou] = useState<string[]>()

  async function descansar(tipo: string) {
    setOcupado(tipo)
    setVoltou(undefined)
    try {
      setVoltou((await aoDescansar(tipo)) ?? [])
    } finally {
      setOcupado('')
    }
  }

  return (
    <div className="painel" data-personagem={personagemId}>
      <div className="espalha">
        <h2 style={{ margin: 0 }}>Descanso</h2>
        <span className="linha">
          <button onClick={() => void descansar('descanso_curto')} disabled={!!ocupado}>
            {ocupado === 'descanso_curto' ? 'descansando…' : 'curto'}
          </button>
          <button onClick={() => void descansar('descanso_longo')} disabled={!!ocupado}>
            {ocupado === 'descanso_longo' ? 'descansando…' : 'longo'}
          </button>
        </span>
      </div>
      {voltou && (
        <p className="proveniencia">
          {voltou.length ? `voltou: ${voltou.join(' · ')}` : 'não havia nada gasto para voltar'}
        </p>
      )}
    </div>
  )
}

// -------------------------------------------------------------------- recursos

/**
 * O que se gasta e volta num descanso: Fúrias, Ataque de Sopro, Canalizar
 * Divindade. O máximo vem calculado do motor — o Sopro do Draconato mostra 3 usos
 * porque o Bônus de Proficiência dele é 3, e a tela não faz essa conta.
 */
function Recursos({ ficha, estado, aoMudar }: {
  ficha: NonNullable<Personagem['ficha']>
  estado: Estado
  aoMudar: (m: Estado) => Promise<void>
}) {
  if (!ficha.recursos?.length) return null
  const gastos = estado.recursos_gastos ?? {}

  function mudar(recurso: RecursoDaFicha, delta: number) {
    const novo = Math.max(0, Math.min(recurso.maximo, (gastos[recurso.id] ?? 0) + delta))
    void aoMudar({ recursos_gastos: { ...gastos, [recurso.id]: novo } })
  }

  return (
    <div className="painel">
      <h2>Usos</h2>
      {ficha.recursos.map((r) => {
        const usados = gastos[r.id] ?? 0
        return (
          <div className="espalha" key={r.id} style={{ padding: '6px 0' }}>
            <span>
              {r.nome}
              <br /><span className="fraco">{r.origem}</span>
            </span>
            <span className="linha">
              <button onClick={() => mudar(r, -1)} disabled={usados === 0}>−</button>
              <strong style={{ minWidth: 46, textAlign: 'center' }}>
                {r.maximo - usados}/{r.maximo}
              </strong>
              <button onClick={() => mudar(r, +1)} disabled={usados >= r.maximo}>usar</button>
            </span>
          </div>
        )
      })}
    </div>
  )
}

// --------------------------------------------------------------------- magias

/** Truque não gasta espaço; magia de talento pode vir com o atributo dela. */
const ROTULO_DO_MODO: Record<string, string> = {
  conhecida: 'conhecida',
  preparada: 'preparada',
  sempre_preparada: 'sempre preparada',
  no_livro: 'no livro — falta preparar',
  disponivel_para_preparar: 'disponível para preparar',
}

/**
 * As magias do personagem, de todas as fontes.
 *
 * `origem` é o que responde à queixa que originou este painel: as magias vindas
 * de antecedente e de talento não apareciam em lugar nenhum, e agora aparecem
 * dizendo de onde vêm. O resumo de cada uma vem do compêndio, como em toda
 * outra tela — a ficha guarda o id, e o texto se busca.
 */
function Magias({ ficha, estado, aoConjurar }: {
  ficha: NonNullable<Personagem['ficha']>
  estado: Estado
  aoConjurar: (magia: MagiaDaFicha, comEspaco?: boolean) => Promise<void>
}) {
  const [detalhes, setDetalhes] = useState<Map<string, ItemDoCompendio>>()
  const [aberta, setAberta] = useState('')

  useEffect(() => {
    if (!ficha.magias?.length) return
    let vivo = true
    void lerCatalogo('magias').then((m) => { if (vivo) setDetalhes(m) })
    return () => { vivo = false }
  }, [ficha.magias?.length])

  if (!ficha.magias?.length) return null
  const gastos = estado.espacos_gastos ?? {}
  const recursosGastos = estado.recursos_gastos ?? {}
  const espacos = ficha.conjuracao?.espacos ?? {}

  /** O menor círculo com espaço livre que ainda comporta a magia (p. 236). */
  function menorEspacoLivre(circulo: number): number | undefined {
    for (let c = Math.max(1, circulo); c <= 9; c++) {
      const total = espacos[c] ?? 0
      if (total > (gastos[String(c)] ?? 0)) return c
    }
    return undefined
  }

  /**
   * O que o botão faz, e se ele pode.
   *
   * A tela NÃO decide o custo — ela lê o que o motor mandou em `custo` e traduz em
   * um rótulo. Quando o uso de graça acabou e o livro deixa gastar espaço, o botão
   * passa a oferecer o espaço, porque o motor disse que dá.
   */
  function botao(m: MagiaDaFicha): { texto: string; titulo: string; pode: boolean; comEspaco: boolean } {
    if (!m.pronta_para_conjurar) {
      return { texto: 'usar', titulo: 'esta magia ainda não está preparada', pode: false, comEspaco: false }
    }
    if (m.custo.tipo === 'nenhum' || m.custo.tipo === 'sem_espaco') {
      return { texto: 'usar', titulo: `não gasta nada — ${m.custo.porque}`, pode: true, comEspaco: false }
    }
    if (m.custo.tipo === 'recurso') {
      const custo = m.custo
      const recurso = ficha.recursos?.find((r) => r.id === custo.recurso_id)
      const restam = (recurso?.maximo ?? 0) - (recursosGastos[custo.recurso_id] ?? 0)
      if (restam > 0) {
        return {
          texto: `usar (${restam} de graça)`,
          titulo: `sem gastar espaço — ${custo.porque}`,
          pode: true,
          comEspaco: false,
        }
      }
      const espaco = custo.tambem_com_espaco ? menorEspacoLivre(m.circulo) : undefined
      return espaco
        ? { texto: `usar (${espaco}º)`, titulo: `o uso de graça acabou; gasta um espaço de ${espaco}º`, pode: true, comEspaco: true }
        : { texto: 'sem uso', titulo: 'o uso de graça volta no descanso', pode: false, comEspaco: false }
    }
    const espaco = menorEspacoLivre(m.custo.circulo_minimo)
    return espaco
      ? { texto: `usar (${espaco}º)`, titulo: `gasta um espaço de ${espaco}º`, pode: true, comEspaco: false }
      : { texto: 'sem espaço', titulo: 'nenhum espaço livre que comporte esta magia', pode: false, comEspaco: false }
  }

  return (
    <div className="painel">
      <h2>Magias</h2>
      {ficha.magias.map((m) => {
        const b = botao(m)
        return (
          <div key={m.id} className="magia">
            <div className="espalha">
              <button
                className="linha-de-magia"
                onClick={() => setAberta(aberta === m.id ? '' : m.id)}
                aria-expanded={aberta === m.id}
              >
                <strong>{m.nome}</strong>
                <span className="numeros-de-magia">{numerosDeMesa(m).join(' · ')}</span>
              </button>
              <button disabled={!b.pode} title={b.titulo} onClick={() => void aoConjurar(m, b.comEspaco)}>
                {b.texto}
              </button>
            </div>
            {aberta === m.id && (
              <p className="descricao">
                {detalhes?.get(m.id)?.descricao_curta ?? 'sem resumo no compêndio.'}
                <br />
                <span className="fraco">
                  {[
                    m.circulo === 0 ? 'truque' : `${m.circulo}º círculo`,
                    ROTULO_DO_MODO[m.modo] ?? m.modo,
                    m.origem,
                    m.jogo.tempo_de_conjuracao,
                    m.jogo.duracao,
                    m.nao_conta_para_o_limite ? 'não ocupa vaga' : undefined,
                  ].filter(Boolean).join(' · ')}
                </span>
              </p>
            )}
          </div>
        )
      })}
    </div>
  )
}

/**
 * A linha que serve na mesa: já calculada, sem "+ mod SAB".
 *
 * Tudo aqui vem pronto do motor (`magia.jogo`) — a tela só junta com barras. Era a
 * queixa: "eu quero o nome, o número e tipo de dados que lanço para acertar, o mesmo
 * para cura ou dano, a salvaguarda que ele usa se tiver, e a distância e área".
 */
function numerosDeMesa(m: MagiaDaFicha): string[] {
  const j = m.jogo
  const partes: (string | undefined)[] = [
    j.jogada_de_ataque
      ? `${j.jogada_de_ataque.valor >= 0 ? '+' : ''}${j.jogada_de_ataque.valor}` +
        `${j.ataque === 'corpo_a_corpo' ? ' corpo a corpo' : ''}`
      : undefined,
    j.salvaguarda ? `CD ${j.salvaguarda.cd} ${j.salvaguarda.atributo}` : undefined,
    j.dano ? `${j.dano.formula}${j.dano.tipo ? ` ${j.dano.tipo.replace(/_/g, ' ')}` : ''}` : undefined,
    j.cura ? `cura ${j.cura.formula}` : undefined,
    j.alcance,
    j.area,
    j.concentracao ? 'concentração' : undefined,
    j.ritual ? 'ritual' : undefined,
  ]
  const numeros = partes.filter(Boolean) as string[]
  // Magia sem número nenhum (Luz, Taumaturgia) não fica com a linha vazia: diz o
  // que dá para dizer dela.
  return numeros.length ? numeros : [m.circulo === 0 ? 'truque' : `${m.circulo}º círculo`]
}

// -------------------------------------------------------------------- detalhes

const NOME_DA_FAMILIA: Record<string, string> = {
  caracteristica: 'Características',
  traco: 'Traços de espécie',
  talento: 'Talentos',
}

const sinal = (n: number) => `${n >= 0 ? '+' : ''}${n}`

// ----------------------------------------------------------------- inventário

/**
 * O que o personagem carrega, e o que está na mão.
 *
 * A tela não sabe o que uma armadura faz: ela manda o estado, e o motor devolve a
 * ficha com a CA já recalculada. Por isso equipar um escudo aqui muda o número lá em
 * cima sem uma linha de regra neste arquivo.
 *
 * O inventário inteiro vai a cada mudança, como os espaços gastos: é um mapa, e
 * mandar o mapa todo evita que duas telas discordem sobre o que sumiu.
 */
function Inventario({ estado, aoMudar }: {
  estado: Estado
  aoMudar: (m: Estado) => Promise<void>
}) {
  const [itens, setItens] = useState<Map<string, ItemDoCompendio>>()
  const [busca, setBusca] = useState('')
  const [aberto, setAberto] = useState('')

  useEffect(() => {
    let vivo = true
    void lerCatalogo('itens').then((m) => { if (vivo) setItens(m) })
    return () => { vivo = false }
  }, [])

  const inventario = estado.inventario ?? {}
  const equipado = new Set(estado.equipado ?? [])
  const carregados = Object.entries(inventario).filter(([, n]) => n > 0)

  const mudarQuantidade = (id: string, delta: number) => {
    const novo = Math.max(0, (inventario[id] ?? 0) + delta)
    const proximo = { ...inventario, [id]: novo }
    if (novo === 0) {
      delete proximo[id]
      // Largar o que está na mão tira da mão junto: o backend recusaria, e recusar
      // aqui uma coisa que o jogador claramente quis é pior que fazer as duas.
      if (equipado.has(id)) {
        void aoMudar({ inventario: proximo, equipado: [...equipado].filter((x) => x !== id) })
        return
      }
    }
    void aoMudar({ inventario: proximo })
  }

  const alternarEquipado = (id: string) => {
    const proximo = new Set(equipado)
    if (proximo.has(id)) proximo.delete(id)
    else proximo.add(id)
    void aoMudar({ equipado: [...proximo] })
  }

  const achados = busca.trim().length < 2 || !itens
    ? []
    : [...itens.values()]
        .filter((i) => (i.nome ?? i.id).toLowerCase().includes(busca.trim().toLowerCase()))
        .slice(0, 8)

  return (
    <div className="painel">
      <h2>Inventário</h2>

      <label>
        <span>Adicionar item</span>
        <input
          value={busca} placeholder="espada, corda, tocha…"
          onChange={(e) => setBusca(e.target.value)}
        />
      </label>
      {achados.length > 0 && (
        <div className="opcoes" style={{ marginBottom: 10 }}>
          {achados.map((i) => (
            <button
              key={i.id} className="opcao"
              onClick={() => { mudarQuantidade(i.id, 1); setBusca('') }}
            >
              <strong>{i.nome ?? i.id}</strong>
              <div className="etiquetas">
                {[i.categoria, i.grupo, typeof i.peso_kg === 'number' ? `${i.peso_kg} kg` : undefined]
                  .filter(Boolean).join(' · ')}
              </div>
            </button>
          ))}
        </div>
      )}

      {!carregados.length && <p className="vazio">Nada no inventário ainda.</p>}

      {carregados.map(([id, n]) => {
        const item = itens?.get(id)
        const equipavel = item?.categoria === 'arma' || item?.categoria === 'armadura'
        return (
          <div key={id} className="item">
            <div className="espalha">
              <button className="linha-de-magia" onClick={() => setAberto(aberto === id ? '' : id)}>
                <strong>{item?.nome ?? id}</strong>
                <span className="numeros-de-magia">
                  {[
                    n > 1 ? `${n}×` : undefined,
                    item?.categoria?.replace(/_/g, ' '),
                    equipado.has(id) ? 'equipado' : undefined,
                  ].filter(Boolean).join(' · ')}
                </span>
              </button>
              <span className="linha">
                <button onClick={() => mudarQuantidade(id, -1)} aria-label={`tirar ${item?.nome ?? id}`}>−</button>
                <button onClick={() => mudarQuantidade(id, +1)} aria-label={`pôr mais ${item?.nome ?? id}`}>+</button>
                {equipavel && (
                  <button
                    aria-pressed={equipado.has(id)}
                    onClick={() => alternarEquipado(id)}
                  >
                    {equipado.has(id) ? 'guardar' : 'equipar'}
                  </button>
                )}
              </span>
            </div>
            {aberto === id && (
              <p className="descricao">{item?.descricao_curta ?? 'sem resumo no compêndio.'}</p>
            )}
          </div>
        )
      })}
    </div>
  )
}

/**
 * As salvaguardas, todas as seis.
 *
 * Todas, e não só as proficientes: a mesa pede salvaguarda de Constituição para
 * manter concentração mesmo sem proficiência, e ter de fazer a conta de cabeça no
 * meio da luta é exatamente o que a ficha existe para evitar.
 */
function Salvaguardas({ ficha }: { ficha: NonNullable<Personagem['ficha']> }) {
  return (
    <div className="painel">
      <h2>Salvaguardas</h2>
      <div className="numeros">
        {Object.entries(ficha.salvaguardas).map(([a, v]) => {
          const proficiente = ficha.modificadores[a] !== v
          return (
            <div className={`numero ${proficiente ? 'proficiente' : ''}`} key={a}>
              <div className="valor">{sinal(v)}</div>
              <div className="rotulo">{a}</div>
            </div>
          )
        })}
      </div>
      <p className="fraco" style={{ fontSize: 12, margin: '6px 0 0' }}>
        Em destaque, as que somam o Bônus de Proficiência.
      </p>
    </div>
  )
}

/**
 * As perícias, com o número pronto.
 *
 * "Poder ver o número que tenho em arcanismo" era a queixa, e a lista mostra as 18
 * — não só as treinadas —, porque é justamente na que não se tem proficiência que a
 * conta não é óbvia. Tocar numa mostra de onde vem o número.
 */
function Pericias({ ficha }: { ficha: NonNullable<Personagem['ficha']> }) {
  const [aberta, setAberta] = useState('')
  const itens = Object.entries(ficha.testes_de_pericia ?? {})
    .sort(([, a], [, b]) => a.nome.localeCompare(b.nome, 'pt-BR'))

  if (!itens.length) return null
  return (
    <div className="painel">
      <h2>Perícias</h2>
      {itens.map(([id, t]) => (
        <div key={id}>
          <button
            className="linha-de-pericia" onClick={() => setAberta(aberta === id ? '' : id)}
            aria-expanded={aberta === id}
          >
            <span className={t.dominio !== 'nenhum' ? 'proficiente' : ''}>
              {t.nome} <span className="fraco">{t.atributo}</span>
            </span>
            <strong>{sinal(t.valor)}</strong>
          </button>
          {aberta === id && (
            <p className="proveniencia">
              {t.parcelas.map((x) => `${x.valor} (${x.rotulo})`).join(' + ')}
            </p>
          )}
        </div>
      ))}
    </div>
  )
}

/**
 * O que o personagem sabe fazer, por extenso.
 *
 * A ficha principal mostra os números; aqui ficam as características, os traços e
 * os talentos, com o resumo e a página do livro. A lista vem pronta do motor: é o
 * que INCIDE no personagem, não um catálogo filtrado por classe aqui na tela.
 */
function Detalhes({ ficha, construcao }: {
  ficha: NonNullable<Personagem['ficha']>
  construcao: Personagem['construcao']
}) {
  const porFamilia = new Map<string, typeof ficha.caracteristicas>()
  for (const c of ficha.caracteristicas ?? []) {
    const lista = porFamilia.get(c.familia) ?? []
    lista.push(c)
    porFamilia.set(c.familia, lista)
  }

  return (
    <>
      <Salvaguardas ficha={ficha} />
      <Pericias ficha={ficha} />

      <div className="painel">
        <h2>Proficiências</h2>
        <Lista rotulo="Idiomas" itens={(ficha.proficiencias?.idiomas ?? [])} />
        <Lista rotulo="Ferramentas" itens={(ficha.proficiencias?.ferramentas ?? [])} />
        <Lista rotulo="Armaduras" itens={(ficha.proficiencias?.armaduras ?? [])} />
        <div className="espalha" style={{ padding: '6px 0' }}>
          <span className="fraco">Espécie · antecedente</span>
          <span>{construcao.especie} · {construcao.antecedente}</span>
        </div>
      </div>

      {['talento', 'caracteristica', 'traco'].map((familia) => {
        const itens = porFamilia.get(familia)
        if (!itens?.length) return null
        return (
          <div className="painel" key={familia}>
            <h2>{NOME_DA_FAMILIA[familia] ?? familia}</h2>
            {itens.map((c) => (
              <div key={c.id} style={{ padding: '8px 0', borderTop: '1px solid var(--borda)' }}>
                <div className="espalha">
                  <strong>{c.nome}</strong>
                  {c.fonte?.pagina_livro && (
                    <span className="fraco">p. {c.fonte.pagina_livro}</span>
                  )}
                </div>
                {c.de && <div className="fraco">{c.de}</div>}
                {c.descricao_curta && <p className="descricao">{c.descricao_curta}</p>}
              </div>
            ))}
          </div>
        )
      })}
    </>
  )
}

function Lista({ rotulo, itens }: { rotulo: string; itens: string[] }) {
  if (!itens.length) return null
  return (
    <div className="espalha" style={{ padding: '6px 0' }}>
      <span className="fraco">{rotulo}</span>
      <span style={{ textAlign: 'right' }}>{itens.join(' · ')}</span>
    </div>
  )
}
