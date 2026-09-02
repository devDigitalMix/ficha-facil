// Efeito aninhado: condição ou estrutura?
//
// A primeira versão do coletor adivinhava pelo formato — todo aninhamento virava
// condição — e adivinhou errado. Dos 81 efeitos que aninham no dataset, **56 são
// `melhorar_caracteristica`**, que não condiciona nada: o `alvo` diz a qual
// característica os efeitos se aplicam. Tratados como condição, e sem `id` para
// nomeá-la, os 56 caíam no mesmo balde e ficavam desligados por padrão. Melhoria
// de característica sumia calada, e nenhum dos dois personagens de ouro pegava,
// porque nenhum deles tem melhoria que mexa em CA ou Pontos de Vida.
//
// Agora está DECLARADO em `catalogos/tipos_de_efeito.json` e o motor lê. Estes
// testes são a rede: se alguém voltar a adivinhar, eles caem.

import { test } from 'node:test'
import assert from 'node:assert/strict'

import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { coletar, type Construcao } from '../src/colecao.ts'
import { catalogo } from '../src/dataset.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))

/** Um Bardo de nível 5: no nível 5 ele ganha Fonte de Inspiração, que MELHORA a
 *  Inspiração de Bardo do nível 1. É a melhoria de característica em nível mais
 *  baixo que não depende de subclasse. */
const BARDO_5: Construcao = {
  especie: 'humano',
  antecedente: 'artista',
  niveis: [{ classe: 'bardo', nivel: 5 }],
  atributos_base: { FOR: 10, DES: 14, CON: 13, INT: 12, SAB: 8, CAR: 15 },
  escolhas: {
    artista_aumento: { escolhido: 'um_em_2_e_outro_em_1', distribuicao: { CAR: 2, DES: 1 } },
  },
}

test('todo tipo que aninha efeitos declara o que o aninhamento significa', () => {
  const declarado = new Map(
    catalogo<{ id: string; efeitos_aninhados?: string }>('tipos_de_efeito').itens.map((i) => [
      i.id,
      i.efeitos_aninhados,
    ]),
  )
  const validos = new Set(['condicionados', 'estruturais', undefined])
  for (const [id, modo] of declarado) {
    assert.ok(validos.has(modo), `tipo '${id}' declara efeitos_aninhados='${modo}'`)
  }
  // pelo menos os dois modos existem no catálogo: se um sumir, a distinção morreu
  const modos = new Set([...declarado.values()].filter(Boolean))
  assert.deepEqual([...modos].sort(), ['condicionados', 'estruturais'])
})

test('melhoria de característica incide SEM porta nenhuma', () => {
  const col = coletar(BARDO_5)
  const melhorias = col.efeitos.filter((c) => c.efeito.tipo === 'melhorar_caracteristica')
  assert.ok(melhorias.length > 0, 'o Bardo de nível 5 tem de trazer uma melhoria')

  // o que está DENTRO da melhoria é o que importa: ele não pode ficar atrás de porta
  const dentroDaMelhoria = col.efeitos.filter((c) => c.origem.includes('melhorar_caracteristica'))
  assert.ok(dentroDaMelhoria.length > 0, 'a melhoria tem de trazer efeitos dentro')
  for (const c of dentroDaMelhoria) {
    assert.deepEqual(
      c.portas,
      [],
      `'${c.origem}' ficou atrás de porta — melhoria de característica não é condição`,
    )
  }
})

test('efeito que É condição continua atrás da sua própria porta', () => {
  const barbaro: Construcao = {
    especie: 'humano',
    antecedente: 'soldado',
    niveis: [{ classe: 'barbaro', nivel: 1 }],
    atributos_base: { FOR: 15, DES: 14, CON: 13, INT: 8, SAB: 12, CAR: 10 },
    escolhas: {
      soldado_aumento: { escolhido: 'um_em_2_e_outro_em_1', distribuicao: { FOR: 2, CON: 1 } },
      barbaro_pericias_iniciais: ['atletismo', 'percepcao'],
    },
  }
  const col = coletar(barbaro)
  const resistencias = col.efeitos.filter(
    (c) => c.efeito.tipo === 'alterar_dano' && c.efeito.operacao === 'resistencia',
  )
  assert.ok(resistencias.length >= 3, 'a Fúria dá três Resistências')
  for (const c of resistencias) {
    assert.ok(
      c.portas.length > 0,
      'as Resistências da Fúria não podem incidir com a Fúria desligada',
    )
  }
})

test('na ficha inteira, a melhoria de característica chega ao resultado', () => {
  // O teste acima olha a COLETA. Este olha a ponta: a Clériga de nível 5 tem
  // Fulminar Mortos-Vivos, que melhora o Canalizar Divindade do nível 2. Se a
  // melhoria voltasse a ser tratada como condição, o efeito de dano dela sumiria
  // da ficha sem ninguém notar — foi exatamente o que aconteceu por um dia.
  const g = JSON.parse(
    readFileSync(join(AQUI, '..', 'ouro', 'clerigo-5.json'), 'utf-8'),
  ) as { construcao: Construcao; estado: Record<string, never> }

  const col = coletar(g.construcao)
  const daMelhoria = col.efeitos.filter((c) => c.origem.includes('melhorar_caracteristica'))
  assert.equal(daMelhoria.length, 1, 'a Clériga de nível 5 tem uma melhoria com um efeito')
  assert.deepEqual(daMelhoria[0].portas, [], 'e ele não pode estar atrás de porta')
  assert.equal(daMelhoria[0].efeito.tipo, 'dano', 'é o dano Radiante do Fulminar Mortos-Vivos')
})

test('cada porta tem nome próprio: duas condições não podem colidir', () => {
  // Era o defeito concreto: sem `id`, a porta virava o `tipo`, e os 56
  // `melhorar_caracteristica` compartilhavam uma porta só.
  const col = coletar(BARDO_5)
  const nomes = col.efeitos.flatMap((c) => c.portas)
  for (const n of nomes) {
    assert.ok(n.length > 0, 'porta sem nome')
    assert.ok(
      !['melhorar_caracteristica'].includes(n),
      'nenhuma porta pode se chamar como um tipo estrutural',
    )
  }
})

// O caso "alguém criou o décimo tipo e não passou pelo catálogo" é cobrado do lado do
// dataset, onde ele nasce: `testes/teste_negativo_efeitos_aninhados.py` planta um tipo
// que aninha sem declarar e um id de porta repetido, e cobra que `validar.py` acuse.
// Escrever isso aqui daria um teste que constrói o próprio erro e depois se
// parabeniza por encontrá-lo.
