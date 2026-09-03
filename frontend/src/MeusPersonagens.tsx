// Meus personagens, e a criação de um novo.
//
// A criação é o mínimo que o backend aceita: nome, espécie, antecedente, classe e os
// seis atributos. Todo o resto — perícias, truques, talento de origem, magias
// preparadas — é **escolha**, e escolha se responde no checklist da ficha, que é
// gerado pelo dataset. Duplicar isso aqui seria escrever à mão o que o motor já sabe.

import { useEffect, useState } from 'react'
import { api, ATRIBUTOS, ErroDaApi, STATUS, type NaLista, type Opcao, type Personagem } from './api.ts'

const quando = (iso: string) =>
  new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })

export function MeusPersonagens({ aoAbrir }: { aoAbrir: (id: string) => void }) {
  const [itens, setItens] = useState<NaLista[]>()
  const [criando, setCriando] = useState(false)
  const [erro, setErro] = useState('')

  async function carregar() {
    try {
      setItens((await api.get<{ itens: NaLista[] }>('/personagens')).itens)
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : 'não consegui carregar a lista')
    }
  }

  useEffect(() => { void carregar() }, [])

  if (criando) {
    return (
      <Novo
        aoCancelar={() => setCriando(false)}
        aoCriar={(id) => { setCriando(false); aoAbrir(id) }}
      />
    )
  }

  return (
    <div className="pagina">
      <div className="espalha" style={{ marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Meus personagens</h2>
        <button className="principal" onClick={() => setCriando(true)}>Novo</button>
      </div>

      {erro && <p className="erro">{erro}</p>}
      {!itens && <p className="vazio">carregando…</p>}
      {itens && !itens.length && (
        <p className="vazio">Nenhum personagem ainda. Toque em “Novo” para começar.</p>
      )}

      {itens?.map((p) => (
        <button className="cartao" key={p.id} onClick={() => aoAbrir(p.id)}>
          <div className="espalha">
            <span className="nome">{p.nome}</span>
            <span className={`marca ${p.status}`}>{p.status}</span>
          </div>
          <div className="fraco">
            {p.especie} · {p.niveis.map((n) => `${n.classe} ${n.nivel}`).join(' / ')}
            {' · '}visto em {quando(p.ultimo_acesso)}
          </div>
        </button>
      ))}
    </div>
  )
}

// ------------------------------------------------------------ criar personagem

/**
 * A distribuição padrão do livro (p. 38), na ordem em que o jogador costuma querer.
 * É só um ponto de partida editável — o backend aceita qualquer inteiro, e conferir
 * regra de criação é trabalho do motor, não desta tela.
 */
const PADRAO = [15, 14, 13, 12, 10, 8]

function Novo({ aoCriar, aoCancelar }: { aoCriar: (id: string) => void; aoCancelar: () => void }) {
  const [catalogos, setCatalogos] = useState<Record<string, Opcao[]>>({})
  const [nome, setNome] = useState('')
  const [especie, setEspecie] = useState('')
  const [antecedente, setAntecedente] = useState('')
  const [classe, setClasse] = useState('')
  const [status, setStatus] = useState<Personagem['status']>('ativo')
  const [valores, setValores] = useState<Record<string, number>>(
    Object.fromEntries(ATRIBUTOS.map((a, i) => [a, PADRAO[i]])),
  )
  const [erro, setErro] = useState('')
  const [ocupado, setOcupado] = useState(false)

  useEffect(() => {
    void Promise.all(
      ['especies', 'antecedentes', 'classes'].map((c) =>
        api.get<{ itens: Opcao[] }>(`/compendio/${c}`).then((r) => [c, r.itens] as const)),
    ).then((pares) => setCatalogos(Object.fromEntries(pares)))
      .catch(() => setErro('não consegui carregar o compêndio'))
  }, [])

  const pronto = nome.trim() && especie && antecedente && classe

  async function criar() {
    setErro('')
    setOcupado(true)
    try {
      const p = await api.post<Personagem>('/personagens', {
        nome: nome.trim(),
        status,
        construcao: {
          especie, antecedente,
          niveis: [{ classe, nivel: 1 }],
          atributos_base: valores,
        },
      })
      aoCriar(p.id)
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : 'não consegui criar')
    } finally {
      setOcupado(false)
    }
  }

  return (
    <div className="pagina">
      <button className="discreto" onClick={aoCancelar} style={{ marginBottom: 8 }}>← voltar</button>
      <div className="painel">
        <h2>Novo personagem</h2>
        {erro && <p className="erro">{erro}</p>}

        <label>
          <span>Nome</span>
          <input value={nome} onChange={(e) => setNome(e.target.value)} />
        </label>

        {([
          ['Espécie', 'especies', especie, setEspecie],
          ['Antecedente', 'antecedentes', antecedente, setAntecedente],
          ['Classe', 'classes', classe, setClasse],
        ] as const).map(([rotulo, catalogo, valor, definir]) => (
          <label key={catalogo}>
            <span>{rotulo}</span>
            <select value={valor} onChange={(e) => definir(e.target.value)}>
              <option value="">escolha…</option>
              {(catalogos[catalogo] ?? []).map((o) => (
                <option key={o.id} value={o.id}>{o.nome}</option>
              ))}
            </select>
          </label>
        ))}

        <label>
          <span>Situação</span>
          <select value={status} onChange={(e) => setStatus(e.target.value as Personagem['status'])}>
            {STATUS.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>

        <h3>Atributos</h3>
        <div className="numeros">
          {ATRIBUTOS.map((a) => (
            <label key={a} style={{ marginBottom: 0 }}>
              <span style={{ textAlign: 'center' }}>{a}</span>
              <input
                type="number" min={1} max={20} value={valores[a]} style={{ textAlign: 'center' }}
                onChange={(e) => setValores({ ...valores, [a]: Number(e.target.value) || 0 })}
              />
            </label>
          ))}
        </div>
        <p className="fraco">
          O aumento do antecedente entra depois, como escolha — não some aqui.
        </p>

        <button className="principal" disabled={!pronto || ocupado} onClick={criar} style={{ width: '100%' }}>
          {ocupado ? 'criando…' : 'Criar'}
        </button>
      </div>
    </div>
  )
}
