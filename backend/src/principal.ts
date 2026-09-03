// Sobe o servidor. É o único arquivo do backend que fala com o mundo.
//
// Qual armazém entra é decidido AQUI e em nenhum outro lugar: `MONGODB_URI`
// preenchida usa o Atlas, vazia usa arquivo. É o que permite rodar e testar sem
// banco — e o que evita o backend inteiro saber onde os personagens moram.

import { join } from 'node:path'
import { randomBytes } from 'node:crypto'
import { criarServidor } from './servidor.ts'
import { ArmazemEmArquivos, type Armazem } from './armazem.ts'
import { UsuariosEmArquivos, type ArmazemDeUsuarios } from './usuarios.ts'
import { EventosEmArquivos, type ArmazemDeEventos } from './eventos.ts'
import { versaoDoDataset } from './versao.ts'

const porta = Number(process.env.PORTA ?? 8787)
const uri = process.env.MONGODB_URI?.trim()
const nomeDoBanco = process.env.MONGODB_BANCO?.trim() || 'ficha_facil'
const dados = process.env.PERSONAGENS ?? join(process.cwd(), 'personagens')
const horas = Number(process.env.SESSAO_HORAS ?? 720)

/**
 * O segredo da sessão.
 *
 * Sem `SESSAO_SEGREDO`, gera um a cada subida. Não é inseguro — são 32 bytes de
 * aleatoriedade de verdade —, mas os tokens morrem quando o processo reinicia, e
 * quem estava logado precisa entrar de novo. Serve para desenvolver; para valer,
 * defina a variável.
 */
function segredoDaSessao(): { segredo: string; efemero: boolean } {
  const doAmbiente = process.env.SESSAO_SEGREDO?.trim()
  if (doAmbiente) return { segredo: doAmbiente, efemero: false }
  return { segredo: randomBytes(32).toString('base64url'), efemero: true }
}

type Montado = {
  armazem: Armazem
  usuarios: ArmazemDeUsuarios
  eventos: ArmazemDeEventos
  onde: string
}

async function montarArmazens(): Promise<Montado> {
  if (!uri) {
    return {
      armazem: new ArmazemEmArquivos(dados),
      usuarios: new UsuariosEmArquivos(join(dados, 'usuarios')),
      eventos: new EventosEmArquivos(join(dados, 'eventos')),
      onde: `arquivos em ${dados}`,
    }
  }
  // import dinâmico: sem URI, o driver do Mongo nem é carregado
  const { conectarMongo } = await import('./mongo.ts')
  const { personagens, usuarios, eventos } = await conectarMongo(uri, nomeDoBanco)
  return { armazem: personagens, usuarios, eventos, onde: `mongo · banco ${nomeDoBanco}` }
}

const { armazem, usuarios, eventos, onde } = await montarArmazens()
const { segredo, efemero } = segredoDaSessao()

const servidor = criarServidor(armazem, usuarios, eventos, { segredo, horas }).listen(porta, () => {
  console.log(`ficha-fácil backend em http://localhost:${porta}`)
  console.log(`dataset ${versaoDoDataset()} · personagens: ${onde}`)
  if (efemero) {
    console.warn(
      'ATENÇÃO: SESSAO_SEGREDO não definida. Gerei uma para esta execução — ' +
      'todo mundo precisa entrar de novo a cada reinício do servidor.',
    )
  }
})

// Ctrl+C com conexão aberta deixa o processo pendurado; fechar os dois resolve.
for (const sinal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(sinal, () => {
    servidor.close(() => {
      void armazem.fechar?.().then(() => process.exit(0))
      if (!armazem.fechar) process.exit(0)
    })
  })
}
