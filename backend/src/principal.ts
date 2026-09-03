// Sobe o servidor. É o único arquivo do backend que fala com o mundo.

import { join } from 'node:path'
import { criarServidor } from './servidor.ts'
import { ArmazemEmArquivos } from './armazem.ts'
import { versaoDoDataset } from './versao.ts'

const porta = Number(process.env.PORTA ?? 8787)
const dados = process.env.PERSONAGENS ?? join(process.cwd(), 'personagens')

criarServidor(new ArmazemEmArquivos(dados)).listen(porta, () => {
  console.log(`ficha-fácil backend em http://localhost:${porta}`)
  console.log(`dataset ${versaoDoDataset()} · personagens em ${dados}`)
})
