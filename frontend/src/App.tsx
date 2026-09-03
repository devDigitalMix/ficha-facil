// A casca: quem está logado, e em que tela.
//
// Sem biblioteca de rotas. São três telas, e a navegação é `useState` — trazer um
// roteador agora seria uma dependência para resolver um `if`. Quando houver link
// compartilhável ou botão voltar do navegador, aí ele se paga.

import { useEffect, useState } from 'react'
import { apagarSessao, lerSessao, quandoPerderSessao, type Sessao } from './api.ts'
import { Entrar } from './Entrar.tsx'
import { MeusPersonagens } from './MeusPersonagens.tsx'
import { Ficha } from './Ficha.tsx'

export function App() {
  const [sessao, setSessao] = useState<Sessao | undefined>(lerSessao)
  const [abertoId, setAbertoId] = useState<string>()

  // O token pode vencer no meio do uso. Quando o backend responde 401, `api.ts`
  // avisa aqui — e a pessoa cai no login em vez de numa tela quebrada.
  useEffect(() => {
    quandoPerderSessao(() => { setSessao(undefined); setAbertoId(undefined) })
  }, [])

  function sair() {
    apagarSessao()
    setSessao(undefined)
    setAbertoId(undefined)
  }

  if (!sessao) return <Entrar aoEntrar={setSessao} />

  return (
    <>
      <header className="topo">
        <h1>Ficha Fácil</h1>
        <span className="quem">{sessao.usuario.email}</span>
        <button className="discreto" onClick={sair}>sair</button>
      </header>
      {abertoId
        ? <Ficha id={abertoId} aoVoltar={() => setAbertoId(undefined)} />
        : <MeusPersonagens aoAbrir={setAbertoId} />}
    </>
  )
}
