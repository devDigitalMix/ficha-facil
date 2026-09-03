// Entrar ou criar conta. Um formulário só, com um botão que troca o modo.
//
// Dois formulários separados fariam a pessoa digitar o e-mail de novo ao descobrir
// que ainda não tem conta — e é justamente aí que ela desiste.

import { useState, type FormEvent } from 'react'
import { api, ErroDaApi, gravarSessao, type Sessao, type Usuario } from './api.ts'

type Resposta = { usuario: Usuario; token: string }

export function Entrar({ aoEntrar }: { aoEntrar: (s: Sessao) => void }) {
  const [modo, setModo] = useState<'entrar' | 'criar'>('entrar')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [ocupado, setOcupado] = useState(false)

  async function enviar(e: FormEvent) {
    e.preventDefault()
    setErro('')
    setOcupado(true)
    try {
      const r = await api.post<Resposta>(modo === 'criar' ? '/contas' : '/sessoes', { email, senha })
      aoEntrar(gravarSessao(r.usuario, r.token))
    } catch (e) {
      // A mensagem do backend já é a certa: ele diz "e-mail ou senha não conferem"
      // sem distinguir os dois casos, de propósito. Reescrever aqui desfaria isso.
      setErro(e instanceof ErroDaApi ? e.message : 'não consegui falar com o servidor')
    } finally {
      setOcupado(false)
    }
  }

  return (
    <div className="pagina">
      <div className="painel" style={{ marginTop: 40 }}>
        <h2>{modo === 'criar' ? 'Criar conta' : 'Entrar'}</h2>
        {erro && <p className="erro">{erro}</p>}
        <form onSubmit={enviar}>
          <label>
            <span>E-mail</span>
            <input
              type="email" value={email} autoComplete="email" required
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          <label>
            <span>Senha{modo === 'criar' ? ' — pelo menos 10 caracteres' : ''}</span>
            <input
              type="password" value={senha} required
              autoComplete={modo === 'criar' ? 'new-password' : 'current-password'}
              onChange={(e) => setSenha(e.target.value)}
            />
          </label>
          <button className="principal" type="submit" disabled={ocupado} style={{ width: '100%' }}>
            {ocupado ? 'um momento…' : modo === 'criar' ? 'Criar conta' : 'Entrar'}
          </button>
        </form>
        <p style={{ textAlign: 'center', marginBottom: 0 }}>
          <button
            className="discreto"
            onClick={() => { setModo(modo === 'criar' ? 'entrar' : 'criar'); setErro('') }}
          >
            {modo === 'criar' ? 'Já tenho conta' : 'Criar uma conta'}
          </button>
        </p>
      </div>
      <p className="fraco" style={{ textAlign: 'center' }}>
        Você fica conectado neste aparelho por 30 dias.
      </p>
    </div>
  )
}
