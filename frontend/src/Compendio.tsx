// O compêndio: tudo que existe, para procurar antes de escolher.
//
// Pedido do João em 2026-09-04: "adicionar algo como uma tela para ver todos os itens,
// separados pelas categorias, isso poderia ajudar também a achar o item correto".
//
// **Esta tela não sabe o que é um item.** Ela recebe o nome de uma coleção, busca o
// que o backend serve, agrupa pelo campo que a própria coleção usa para se dividir e
// desenha o que cada entrada tiver. Trocar `itens` por `magias` mostraria as magias
// agrupadas por círculo sem uma linha nova aqui — é o mesmo princípio do checklist.

import { useEffect, useMemo, useState } from 'react'
import { lerCatalogo, type ItemDoCompendio } from './api.ts'

/**
 * Por qual campo esta coleção se divide.
 *
 * Não é lista de conteúdo: são os campos de AGRUPAMENTO que o dataset usa, na ordem
 * em que fazem sentido. A coleção que não tiver nenhum deles aparece numa lista só,
 * e não quebrada — o que é a resposta honesta para "não sei como dividir isto".
 */
const CAMPOS_DE_GRUPO = ['categoria', 'nivel', 'raridade', 'escola', 'grupo']

const titulo = (v: string) => v.replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase())

export function Compendio({ colecao = 'itens', aoVoltar }: {
  colecao?: string
  aoVoltar: () => void
}) {
  const [tudo, setTudo] = useState<Map<string, ItemDoCompendio>>()
  const [erro, setErro] = useState('')
  const [busca, setBusca] = useState('')
  const [grupoAberto, setGrupoAberto] = useState('')
  const [aberto, setAberto] = useState('')

  useEffect(() => {
    let vivo = true
    void lerCatalogo(colecao)
      .then((m) => { if (vivo) setTudo(m) })
      .catch(() => { if (vivo) setErro('não consegui carregar o compêndio') })
    return () => { vivo = false }
  }, [colecao])

  const grupos = useMemo(() => {
    if (!tudo) return []
    const itens = [...tudo.values()]
    const campo = CAMPOS_DE_GRUPO.find((c) => itens.some((i) => i[c] !== undefined))
    const por = new Map<string, ItemDoCompendio[]>()
    for (const i of itens) {
      const chave = campo && i[campo] !== undefined ? String(i[campo]) : 'sem categoria'
      const lista = por.get(chave) ?? []
      lista.push(i)
      por.set(chave, lista)
    }
    for (const lista of por.values()) {
      lista.sort((a, b) => (a.nome ?? a.id).localeCompare(b.nome ?? b.id, 'pt-BR'))
    }
    return [...por.entries()].sort(([a], [b]) => a.localeCompare(b, 'pt-BR'))
  }, [tudo])

  const procurando = busca.trim().length >= 2
  const achados = procurando && tudo
    ? [...tudo.values()]
        .filter((i) => (i.nome ?? i.id).toLowerCase().includes(busca.trim().toLowerCase()))
        .sort((a, b) => (a.nome ?? a.id).localeCompare(b.nome ?? b.id, 'pt-BR'))
    : []

  return (
    <div className="pagina">
      <button className="discreto" onClick={aoVoltar} style={{ marginBottom: 8 }}>← voltar</button>

      <div className="painel">
        <h2>Compêndio</h2>
        {erro && <p className="erro">{erro}</p>}
        <label>
          <span>Procurar</span>
          <input value={busca} placeholder="couro, cajado, corda…"
            onChange={(e) => setBusca(e.target.value)} />
        </label>
        {!tudo && <p className="vazio">carregando…</p>}
        {tudo && !procurando && (
          <p className="fraco" style={{ fontSize: 12, margin: 0 }}>
            {tudo.size} entradas em {grupos.length} categorias.
          </p>
        )}
      </div>

      {procurando && (
        <div className="painel">
          <h2>{achados.length} resultado(s)</h2>
          {achados.map((i) => (
            <Entrada key={i.id} item={i} aberto={aberto === i.id}
              aoAbrir={() => setAberto(aberto === i.id ? '' : i.id)} />
          ))}
          {!achados.length && <p className="vazio">Nada com esse nome.</p>}
        </div>
      )}

      {!procurando && grupos.map(([grupo, itens]) => (
        <div className="painel" key={grupo}>
          <button className="linha-de-pericia" style={{ borderTop: 'none' }}
            onClick={() => setGrupoAberto(grupoAberto === grupo ? '' : grupo)}
            aria-expanded={grupoAberto === grupo}
          >
            <strong>{titulo(grupo)}</strong>
            <span className="fraco">{itens.length}</span>
          </button>
          {grupoAberto === grupo && itens.map((i) => (
            <Entrada key={i.id} item={i} aberto={aberto === i.id}
              aoAbrir={() => setAberto(aberto === i.id ? '' : i.id)} />
          ))}
        </div>
      ))}
    </div>
  )
}

/** Uma entrada: nome, os campos que ela tiver, e a descrição ao toque. */
function Entrada({ item, aberto, aoAbrir }: {
  item: ItemDoCompendio; aberto: boolean; aoAbrir: () => void
}) {
  const etiquetas = [
    item.grupo ? titulo(String(item.grupo)) : undefined,
    item.dano?.formula_dado
      ? `${item.dano.formula_dado} ${String(item.dano.tipo_dano ?? '').replace(/_/g, ' ')}`.trim()
      : undefined,
    typeof item.peso_kg === 'number' ? `${item.peso_kg} kg` : undefined,
    item.custo?.valor ? `${item.custo.valor} ${String(item.custo.moeda ?? '').toUpperCase()}` : undefined,
    item.equipavel ? 'equipável' : undefined,
  ].filter(Boolean)

  return (
    <div className="item">
      <button className="linha-de-magia" onClick={aoAbrir} aria-expanded={aberto}>
        <strong>{item.nome ?? item.id}</strong>
        {etiquetas.length > 0 && <span className="numeros-de-magia">{etiquetas.join(' · ')}</span>}
      </button>
      {aberto && (
        <p className="descricao">
          {item.descricao_curta ?? 'sem resumo no compêndio.'}
          {item.tambem_e && (
            <>
              <br />
              <span className="fraco">também conta como: {item.tambem_e.replace(/_/g, ' ')}</span>
            </>
          )}
        </p>
      )}
    </div>
  )
}
