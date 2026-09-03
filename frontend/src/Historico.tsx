// O histórico. O backend já manda a linha pronta em `resumo` — com o número daquele
// momento congelado —, então esta tela não formata nada: ela lista e pagina.

import { useCallback, useEffect, useState } from 'react'
import { api, type Evento } from './api.ts'

type Pagina = { itens: Evento[]; proximo?: string }

const quando = (iso: string) =>
  new Date(iso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })

export function Historico({ personagemId, versao }: { personagemId: string; versao: number }) {
  const [itens, setItens] = useState<Evento[]>([])
  const [proximo, setProximo] = useState<string>()
  const [carregando, setCarregando] = useState(true)

  const primeiraPagina = useCallback(async () => {
    setCarregando(true)
    try {
      const r = await api.get<Pagina>(`/personagens/${personagemId}/historico?limite=30`)
      setItens(r.itens)
      setProximo(r.proximo)
    } finally {
      setCarregando(false)
    }
  }, [personagemId])

  // `versao` muda a cada alteração de estado: é como a aba se mantém em dia sem
  // precisar adivinhar quando algo aconteceu.
  useEffect(() => { void primeiraPagina() }, [primeiraPagina, versao])

  async function mais() {
    if (!proximo) return
    const r = await api.get<Pagina>(
      `/personagens/${personagemId}/historico?limite=30&antes_de=${encodeURIComponent(proximo)}`)
    setItens((atual) => [...atual, ...r.itens])
    setProximo(r.proximo)
  }

  if (carregando && !itens.length) return <p className="vazio">carregando…</p>
  if (!itens.length) {
    return <p className="vazio">Nada aconteceu ainda. Marque dano, cura ou uma magia e a linha aparece aqui.</p>
  }

  return (
    <div className="painel">
      <ul className="historico">
        {itens.map((e) => (
          <li key={e.id}>
            <div>{e.resumo}</div>
            <div className="quando">{quando(e.em)}</div>
          </li>
        ))}
      </ul>
      {proximo && (
        <button className="discreto" onClick={() => void mais()} style={{ width: '100%' }}>
          ver mais
        </button>
      )}
    </div>
  )
}
