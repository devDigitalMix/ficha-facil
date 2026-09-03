// A versão do dataset.
//
// O compêndio é imutável entre builds, então ele pode ser servido com cache longo —
// mas só se houver como dizer "mudou". A versão é o resumo do conteúdo de `dados/`:
// muda quando qualquer byte do dado muda, e não muda por nada mais (nem relógio, nem
// número de build). É o ETag do compêndio e o carimbo que fica gravado no personagem.
//
// Guardar a versão no personagem é o que permite ao app avisar em vez de quebrar
// quando uma escolha antiga aponta para um id que não existe mais.

import { createHash } from 'node:crypto'
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { RAIZ_DADOS } from '../../motor/src/dataset.ts'

function arquivosDeDados(raiz: string): string[] {
  const achados: string[] = []
  for (const nome of readdirSync(raiz).sort()) {
    const caminho = join(raiz, nome)
    if (statSync(caminho).isDirectory()) achados.push(...arquivosDeDados(caminho))
    else if (nome.endsWith('.json')) achados.push(caminho)
  }
  return achados
}

let cache: string | null = null

/** Resumo estável do conteúdo de `dados/`. Doze hexadecimais bastam para o que isto faz. */
export function versaoDoDataset(): string {
  if (cache) return cache
  const h = createHash('sha256')
  for (const caminho of arquivosDeDados(RAIZ_DADOS)) {
    // o caminho relativo entra no resumo: renomear um catálogo é mudança de dataset
    h.update(caminho.slice(RAIZ_DADOS.length))
    h.update(readFileSync(caminho))
  }
  cache = h.digest('hex').slice(0, 12)
  return cache
}

/** Só para os testes: força o recálculo depois de mexer no dado. */
export function esquecerVersao(): void {
  cache = null
}
