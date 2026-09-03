// Teste negativo do motor.
//
// Os personagens de ouro passam. Isso não prova nada por si: um teste que nunca
// reprova é um teste que aceita qualquer coisa. Aqui cada defeito plausível é
// plantado de propósito **na construção** — que é a entrada de verdade desde o
// passo 3 — e se cobra que a ficha MUDE. Se não mudar, o golden não estava
// conferindo aquilo.
//
// É o raciocínio dos oito testes negativos do dataset, aplicado ao código.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { coletar, type Construcao } from '../src/colecao.ts'
import { montarContexto, type Estado } from '../src/contexto.ts'
import { montarFicha, type Ficha } from '../src/ficha.ts'
import { vocabularioDeRuntime } from '../src/dataset.ts'
import { ErroDoMotor } from '../src/tipos.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))
const VOCAB = vocabularioDeRuntime()

type Golden = { construcao: Construcao; estado?: Estado; estado_sem_furia?: Estado }

function ouro(nome: string): Golden {
  return JSON.parse(readFileSync(join(AQUI, '..', 'ouro', `${nome}.json`), 'utf-8'))
}

function copia<T>(x: T): T {
  return JSON.parse(JSON.stringify(x)) as T
}

function montar(g: Golden, c: Construcao) {
  const col = coletar(c)
  const { contexto } = montarContexto(col, c.atributos_base, g.estado ?? g.estado_sem_furia ?? {}, VOCAB)
  return { ficha: montarFicha(contexto, VOCAB), pendencias: col.pendencias.map((p) => p.escolha_id) }
}

type Defeito = {
  nome: string
  golden: string
  plantar: (c: Construcao) => void
  campo: (r: { ficha: Ficha; pendencias: string[] }) => unknown
}

const DEFEITOS: Defeito[] = [
  {
    nome: 'a escolha de perícias da classe some',
    golden: 'monge-1',
    plantar: (c) => {
      delete c.escolhas!.monge_pericias_iniciais
    },
    campo: (r) => r.pendencias.sort(),
  },
  {
    nome: 'o antecedente muda (outros atributos, outras perícias)',
    golden: 'monge-1',
    plantar: (c) => {
      // o Soldado oferece Força, Destreza e Constituição — não Sabedoria
      c.antecedente = 'soldado'
      c.escolhas!.soldado_aumento = {
        escolhido: 'um_em_2_e_outro_em_1',
        distribuicao: { DES: 2, CON: 1 },
      }
      delete c.escolhas!.guia_aumento
    },
    campo: (r) => r.ficha.modificadores,
  },
  {
    nome: 'o aumento do antecedente vai para outro atributo (a CA do Monge usa Sabedoria)',
    golden: 'monge-1',
    plantar: (c) => {
      // +1 em Destreza e +2 em Constituição: a Destreza mal se mexe e a Sabedoria
      // não sobe, então a CA do Monge cai
      c.escolhas!.guia_aumento = {
        escolhido: 'um_em_2_e_outro_em_1',
        distribuicao: { CON: 2, DES: 1 },
      }
    },
    campo: (r) => r.ficha.classe_de_armadura.valor,
  },
  {
    nome: 'a espécie muda (o Deslocamento base vem dela)',
    golden: 'barbaro-5',
    plantar: (c) => {
      // das dez espécies, só o Golias não anda 9 m — é a que serve de defeito aqui
      c.especie = 'golias'
    },
    campo: (r) => r.ficha.deslocamento_m,
  },
  {
    nome: 'o nível cai de 5 para 4 (muda o degrau do Bônus de Proficiência e os PV)',
    golden: 'barbaro-5',
    plantar: (c) => {
      c.niveis[0].nivel = 4
    },
    campo: (r) => [r.ficha.bonus_de_proficiencia, r.ficha.pontos_de_vida_maximos.valor],
  },
  {
    nome: 'a subclasse deixa de ser escolhida',
    golden: 'barbaro-5',
    plantar: (c) => {
      delete c.escolhas!.barbaro_escolha_de_subclasse
    },
    campo: (r) => r.pendencias.sort(),
  },
  {
    nome: 'o Aumento no Valor de Atributo vai para outro atributo',
    golden: 'barbaro-5',
    plantar: (c) => {
      c.escolhas!['avatributo_um@4'] = 'CON'
    },
    campo: (r) => [r.ficha.modificadores.FOR, r.ficha.pontos_de_vida_maximos.valor],
  },
  {
    nome: 'a perícia escolhida na classe não é mais Percepção',
    golden: 'barbaro-5',
    plantar: (c) => {
      c.escolhas!.barbaro_pericias_iniciais = ['atletismo', 'intimidacao']
    },
    campo: (r) => r.ficha.percepcao_passiva.valor,
  },
]

for (const d of DEFEITOS) {
  test(`negativo: ${d.nome}`, () => {
    const g = ouro(d.golden)
    const sadio = montar(g, copia(g.construcao))
    const c = copia(g.construcao)
    d.plantar(c)
    const doente = montar(g, c)
    assert.notDeepEqual(
      d.campo(doente),
      d.campo(sadio),
      'a ficha não mudou com o defeito plantado — o golden não está conferindo isto',
    )
  })
}

// --------------------------------------- o que o motor tem de RECUSAR, não contornar

test('negativo: aumento de atributo sem dizer quais atributos sobem é erro', () => {
  const g = ouro('monge-1')
  const c = copia(g.construcao)
  c.escolhas!.guia_aumento = { escolhido: 'um_em_2_e_outro_em_1' }
  assert.throws(() => montar(g, c), ErroDoMotor)
})

test('negativo: aumentar um atributo fora dos três do antecedente é erro', () => {
  const g = ouro('monge-1')
  const c = copia(g.construcao)
  c.escolhas!.guia_aumento = { escolhido: 'um_em_2_e_outro_em_1', distribuicao: { FOR: 2, INT: 1 } }
  assert.throws(() => montar(g, c), ErroDoMotor)
})

test('negativo: passar de 20 num atributo é erro', () => {
  const g = ouro('barbaro-5')
  const c = copia(g.construcao)
  c.atributos_base.FOR = 19
  assert.throws(() => montar(g, c), ErroDoMotor)
})

test('negativo: multiclasse é recusada, e não calculada errado', () => {
  const g = ouro('monge-1')
  const c = copia(g.construcao)
  c.niveis.push({ classe: 'barbaro', nivel: 2 })
  assert.throws(() => montar(g, c), ErroDoMotor)
})

test('negativo: id de conteúdo que não existe é erro', () => {
  const g = ouro('monge-1')
  const c = copia(g.construcao)
  c.especie = 'anao_das_montanhas_de_ferro'
  assert.throws(() => montar(g, c))
})

// ------------------------------------------------------------------ folga

test('negativo (folga): mexer no Carisma não mexe na CA nem nos Pontos de Vida', () => {
  const g = ouro('barbaro-5')
  const sadio = montar(g, copia(g.construcao))
  const c = copia(g.construcao)
  c.atributos_base.CAR += 4
  const outro = montar(g, c)
  assert.equal(outro.ficha.classe_de_armadura.valor, sadio.ficha.classe_de_armadura.valor)
  assert.equal(
    outro.ficha.pontos_de_vida_maximos.valor,
    sadio.ficha.pontos_de_vida_maximos.valor,
  )
})

test('negativo (folga): resolver uma escolha que não mexe na ficha só tira ela do checklist', () => {
  const g = ouro('monge-1')
  const sadio = montar(g, copia(g.construcao))
  const c = copia(g.construcao)
  c.escolhas!.monge_ferramenta_inicial = 'ferramentas_de_ladrao'
  const outro = montar(g, c)
  assert.equal(outro.ficha.classe_de_armadura.valor, sadio.ficha.classe_de_armadura.valor)
  assert.ok(
    !outro.pendencias.includes('monge_ferramenta_inicial'),
    'a escolha resolvida tem de sair do checklist',
  )
})
