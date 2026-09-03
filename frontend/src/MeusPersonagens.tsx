// Meus personagens, e a criação de um novo.
//
// A criação é o mínimo que o backend aceita: nome, espécie, antecedente, classe e os
// seis atributos. Todo o resto — perícias, truques, talento de origem, magias
// preparadas — é **escolha**, e escolha se responde no checklist da ficha, que é
// gerado pelo dataset. Duplicar isso aqui seria escrever à mão o que o motor já sabe.

import { useEffect, useState } from 'react'
import {
  api, ATRIBUTOS, ErroDaApi, STATUS,
  type Atributo, type NaLista, type Opcao, type Personagem,
} from './api.ts'

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

/**
 * A ordem em que a distribuição padrão é aplicada, para a classe escolhida.
 *
 * Quem manda são os campos que a PRÓPRIA classe declara — `atributo_primario`
 * (p. 38: "seu atributo primário deve ter o valor mais alto") e depois as
 * salvaguardas em que ela é treinada. Nenhum nome de classe aparece aqui, e uma
 * classe nova é ordenada certo sem tocar nesta tela.
 *
 * Constituição vem logo depois porque Ponto de Vida é de todo mundo; o resto fica
 * na ordem da ficha. É sugestão, não regra — a tela deixa mudar tudo.
 */
function ordemDosAtributos(classe?: Classe): Atributo[] {
  const ordem: Atributo[] = []
  const juntar = (lista: readonly string[] = []) => {
    for (const a of lista) {
      if (ATRIBUTOS.includes(a as Atributo) && !ordem.includes(a as Atributo)) {
        ordem.push(a as Atributo)
      }
    }
  }
  juntar(classe?.atributo_primario)
  juntar(classe?.salvaguardas_primarias)
  juntar(['CON'])
  juntar(ATRIBUTOS)
  return ordem
}

/** A distribuição padrão já encaixada na ordem que a classe pede. */
function recomendados(classe?: Classe): Record<string, number> {
  const valores: Record<string, number> = {}
  ordemDosAtributos(classe).forEach((a, i) => { valores[a] = PADRAO[i] })
  return valores
}

/** O que esta tela usa de uma classe do compêndio. */
type Classe = Opcao & {
  atributo_primario?: string[]
  salvaguardas_primarias?: string[]
}

function Novo({ aoCriar, aoCancelar }: { aoCriar: (id: string) => void; aoCancelar: () => void }) {
  const [catalogos, setCatalogos] = useState<Record<string, Opcao[]>>({})
  const [nome, setNome] = useState('')
  const [especie, setEspecie] = useState('')
  const [antecedente, setAntecedente] = useState('')
  const [classe, setClasse] = useState('')
  const [status, setStatus] = useState<Personagem['status']>('ativo')
  const [valores, setValores] = useState<Record<string, number>>(recomendados())
  /** Enquanto o jogador não mexeu, trocar de classe reordena a sugestão. */
  const [mexeuNosAtributos, setMexeuNosAtributos] = useState(false)
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
  const classeEscolhida = (catalogos.classes as Classe[] | undefined)?.find((c) => c.id === classe)

  /**
   * Escolher a classe já arruma os atributos — mas só enquanto o jogador não os
   * tiver mexido. Reescrever por cima do que alguém digitou seria pior do que não
   * sugerir nada.
   */
  function escolherClasse(id: string) {
    setClasse(id)
    if (mexeuNosAtributos) return
    const nova = (catalogos.classes as Classe[] | undefined)?.find((c) => c.id === id)
    setValores(recomendados(nova))
  }

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
          ['Classe', 'classes', classe, escolherClasse],
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
                onChange={(e) => {
                  setMexeuNosAtributos(true)
                  setValores({ ...valores, [a]: Number(e.target.value) || 0 })
                }}
              />
            </label>
          ))}
        </div>
        <div className="espalha">
          <p className="fraco" style={{ margin: 0 }}>
            {classeEscolhida
              ? `Sugestão para ${classeEscolhida.nome}: ${PADRAO.join(', ')} na ordem ` +
                `${ordemDosAtributos(classeEscolhida).join(' › ')}. Pode mudar tudo.`
              : 'Escolha a classe e a distribuição se arruma sozinha.'}
          </p>
          {mexeuNosAtributos && classeEscolhida && (
            <button
              className="discreto"
              onClick={() => {
                setValores(recomendados(classeEscolhida))
                setMexeuNosAtributos(false)
              }}
            >
              usar a sugestão
            </button>
          )}
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
