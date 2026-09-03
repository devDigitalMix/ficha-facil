// O armazém em arquivos — o que os outros testes não exercitam, porque usam o de
// memória. O que importa aqui é o que só o disco tem: gravação atômica, id que não
// pode virar caminho, e sobreviver a reabrir o diretório.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { ArmazemEmArquivos } from '../src/armazem.ts'
import type { Personagem } from '../src/personagem.ts'

const modelo = (nome: string) =>
  ({
    nome,
    status: 'ativo',
    construcao: {
      especie: 'humano',
      antecedente: 'acolito',
      niveis: [{ classe: 'clerigo', nivel: 1 }],
      atributos_base: { FOR: 10, DES: 10, CON: 10, INT: 10, SAB: 10, CAR: 10 },
    },
    estado: {},
    versao_do_dataset: 'aaaaaaaaaaaa',
    criado_em: new Date().toISOString(),
    ultimo_acesso: new Date().toISOString(),
  }) as Omit<Personagem, 'id'>

function comDiretorio<T>(f: (raiz: string) => T): T {
  const raiz = mkdtempSync(join(tmpdir(), 'ficha-facil-armazem-'))
  try {
    return f(raiz)
  } finally {
    rmSync(raiz, { recursive: true, force: true })
  }
}

test('grava, lê de volta e sobrevive a reabrir o diretório', () => {
  comDiretorio((raiz) => {
    const a = new ArmazemEmArquivos(raiz)
    const p = a.criar(modelo('Vesna'))
    assert.ok(p.id)

    // uma instância nova, como um processo que reiniciou
    const b = new ArmazemEmArquivos(raiz)
    const lido = b.ler(p.id)!
    assert.equal(lido.nome, 'Vesna')
    assert.equal(lido.construcao.niveis[0].classe, 'clerigo')
  })
})

test('não deixa lixo temporário para trás', () => {
  comDiretorio((raiz) => {
    const a = new ArmazemEmArquivos(raiz)
    const p = a.criar(modelo('Torvar'))
    a.gravar({ ...p, nome: 'Torvar, o Alto' })
    const arquivos = readdirSync(raiz)
    assert.deepEqual(arquivos, [`${p.id}.json`], 'só o JSON final pode ficar')
  })
})

test('id que tenta virar caminho não lê nem grava', () => {
  comDiretorio((raiz) => {
    const a = new ArmazemEmArquivos(raiz)
    // um arquivo fora do diretório do armazém, para provar que não dá para alcançá-lo
    const fora = join(raiz, '..', 'segredo.json')
    writeFileSync(fora, JSON.stringify({ id: 'segredo', nome: 'não devia sair' }), 'utf-8')
    try {
      for (const id of ['../segredo', '..%2Fsegredo', '/etc/passwd', 'com espaço', '']) {
        assert.equal(a.ler(id), undefined, `'${id}' não pode ler nada`)
      }
      assert.throws(() => a.gravar({ ...modelo('X'), id: '../fuga' } as Personagem))
    } finally {
      rmSync(fora, { force: true })
    }
  })
})

test('lista pelo último acesso, do mais recente para o mais antigo', () => {
  comDiretorio((raiz) => {
    const a = new ArmazemEmArquivos(raiz)
    const antiga = a.criar({ ...modelo('Antiga'), ultimo_acesso: '2020-01-01T00:00:00.000Z' })
    const nova = a.criar({ ...modelo('Nova'), ultimo_acesso: '2026-01-01T00:00:00.000Z' })
    assert.deepEqual(a.listar().map((p) => p.id), [nova.id, antiga.id])
  })
})

test('apagar devolve se havia o que apagar', () => {
  comDiretorio((raiz) => {
    const a = new ArmazemEmArquivos(raiz)
    const p = a.criar(modelo('Efêmera'))
    assert.equal(a.apagar(p.id), true)
    assert.equal(a.apagar(p.id), false)
    assert.equal(a.ler(p.id), undefined)
  })
})
