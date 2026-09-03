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
  async function conjurar(magia: MagiaDaFicha, circulo: number) {
    if (magia.circulo === 0) return // truque não gasta espaço
    const gastos = p?.estado.espacos_gastos ?? {}
    await mudarEstado({
      espacos_gastos: { ...gastos, [circulo]: (gastos[circulo] ?? 0) + 1 },
      motivo: { magia_id: magia.id },
    })
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
          <Magias ficha={p.ficha} estado={p.estado} aoConjurar={conjurar} />
          <Ataques ficha={p.ficha} />
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
  return (
    <p className="proveniencia">
      {rotulo} ={' '}
      {resultado.parcelas.map((x) => `${x.valor} (${x.rotulo})`).join(' + ')}
    </p>
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
  aoConjurar: (magia: MagiaDaFicha, circulo: number) => Promise<void>
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
  const espacos = ficha.conjuracao?.espacos ?? {}

  /** O menor círculo com espaço livre que ainda comporta a magia (p. 236). */
  function menorEspacoLivre(circulo: number): number | undefined {
    for (let c = circulo; c <= 9; c++) {
      const total = espacos[c] ?? 0
      if (total > (gastos[String(c)] ?? 0)) return c
    }
    return undefined
  }

  return (
    <div className="painel">
      <h2>Magias</h2>
      {ficha.magias.map((m) => {
        const d = detalhes?.get(m.id)
        const espaco = m.circulo === 0 ? undefined : menorEspacoLivre(m.circulo)
        const podeConjurar = m.pronta_para_conjurar && (m.circulo === 0 || espaco !== undefined)
        return (
          <div key={m.id} style={{ padding: '8px 0', borderTop: '1px solid var(--borda)' }}>
            <div className="espalha">
              <span
                style={{ cursor: 'pointer' }}
                onClick={() => setAberta(aberta === m.id ? '' : m.id)}
              >
                <strong>{m.nome}</strong>
                <br />
                <span className="fraco">
                  {m.circulo === 0 ? 'truque' : `${m.circulo}º círculo`}
                  {' · '}{ROTULO_DO_MODO[m.modo] ?? m.modo}
                  {' · '}{m.origem}
                  {m.nao_conta_para_o_limite && ' · não ocupa vaga'}
                </span>
              </span>
              <button
                disabled={!podeConjurar}
                onClick={() => void aoConjurar(m, espaco ?? 0)}
                title={
                  m.pronta_para_conjurar
                    ? m.circulo === 0 ? 'truque não gasta espaço' : `gasta um espaço de ${espaco}º`
                    : 'esta magia ainda não está preparada'
                }
              >
                {m.circulo === 0 ? 'usar' : espaco ? `usar (${espaco}º)` : 'sem espaço'}
              </button>
            </div>
            {aberta === m.id && (
              <p className="descricao" style={{ marginTop: 6 }}>
                {d?.descricao_curta ?? 'sem resumo no compêndio.'}
                {d && (
                  <>
                    <br />
                    <span className="fraco">
                      {[
                        d.tempo_de_conjuracao?.texto, d.alcance?.texto, d.duracao?.texto,
                        d.concentracao ? 'concentração' : undefined,
                        d.ritual ? 'ritual' : undefined,
                        d.dano?.formula_dado
                          ? `${d.dano.formula_dado} ${d.dano.tipo_dano ?? ''}`.trim()
                          : undefined,
                      ].filter(Boolean).join(' · ')}
                    </span>
                  </>
                )}
              </p>
            )}
          </div>
        )
      })}
    </div>
  )
}

// -------------------------------------------------------------------- detalhes

const NOME_DA_FAMILIA: Record<string, string> = {
  caracteristica: 'Características',
  traco: 'Traços de espécie',
  talento: 'Talentos',
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
      <div className="painel">
        <h2>Proficiências</h2>
        <Lista rotulo="Salvaguardas" itens={
          Object.entries(ficha.salvaguardas)
            .filter(([a]) => ficha.modificadores[a] !== ficha.salvaguardas[a])
            .map(([a, v]) => `${a} ${v >= 0 ? '+' : ''}${v}`)
        } />
        <Lista rotulo="Perícias" itens={
          Object.entries(ficha.testes_de_pericia ?? {})
            .map(([p, v]) => `${p} ${v >= 0 ? '+' : ''}${v}`)
        } />
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
