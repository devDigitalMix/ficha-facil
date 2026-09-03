// A ficha em sessão: vida, espaços, escolhas pendentes e histórico.
//
// Toda alteração passa por `PATCH /estado`, que é o único caminho que gera evento.
// A tela nunca calcula nada da ficha — ela mostra o que o motor devolveu. O "10 + 3
// DES + 4 SAB" que aparece ao tocar num número é a `parcelas` do próprio motor.

import { useCallback, useEffect, useState } from 'react'
import { api, ErroDaApi, type Estado, type Personagem, type Resultado } from './api.ts'
import { Escolhas, type Valor } from './Escolhas.tsx'
import { Historico } from './Historico.tsx'

export function Ficha({ id, aoVoltar }: { id: string; aoVoltar: () => void }) {
  const [p, setP] = useState<Personagem>()
  const [erro, setErro] = useState('')
  const [aba, setAba] = useState<'ficha' | 'escolhas' | 'historico'>('ficha')
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
          <Numeros ficha={p.ficha} />
          <Espacos ficha={p.ficha} estado={p.estado} aoMudar={mudarEstado} />
          <Ataques ficha={p.ficha} />
        </>
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
        <strong style={{ fontSize: 20 }}>
          {atual}/{maximo}{temporarios > 0 && <span className="fraco"> +{temporarios}</span>}
        </strong>
      </div>
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

      {/* A proveniência vem pronta do motor: a tela não recalcula, só escreve. */}
      {aberto && (
        <p className="proveniencia">
          {aberto} ={' '}
          {(campos.find(([r]) => r === aberto)![1] as Resultado).parcelas
            .map((x) => `${x.valor} (${x.rotulo})`)
            .join(' + ')}
        </p>
      )}

      <h3>Atributos</h3>
      <div className="numeros">
        {Object.entries(ficha.modificadores).map(([a, m]) => (
          <div className="numero" key={a}>
            <div className="valor">{m >= 0 ? `+${m}` : m}</div>
            <div className="rotulo">{a}</div>
          </div>
        ))}
      </div>
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
