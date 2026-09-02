// O motor de escolha — passo 4.
//
// Os passos 2 e 3 calculam a ficha de quem já escolheu. Este é quem OFERECE as
// opções e RECUSA a inválida. Criar personagem e subir de nível são, os dois,
// resolver escolhas — então é aqui que a Fase A do app se apoia.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { montar } from '../src/motor.ts'
import { opcoesDe } from '../src/escolha.ts'
import { catalogo } from '../src/dataset.ts'
import type { Construcao } from '../src/colecao.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))

function ouro(nome: string) {
  return JSON.parse(readFileSync(join(AQUI, '..', 'ouro', `${nome}.json`), 'utf-8')) as {
    construcao: Construcao
    estado?: Record<string, unknown>
    estado_sem_furia?: Record<string, unknown>
  }
}

function copia<T>(x: T): T {
  return JSON.parse(JSON.stringify(x)) as T
}

// ------------------------------------------------------- o checklist tem conteúdo

test('o checklist traz as opções, não só o rótulo', () => {
  const g = ouro('monge-1')
  const r = montar(g.construcao, g.estado)
  assert.ok(r.checklist.length > 0, 'o Monge de nível 1 tem escolhas em aberto')
  for (const c of r.checklist) {
    assert.ok(c.rotulo.length > 0, `escolha '${c.escolha_id}' sem rótulo`)
    assert.ok(c.quantidade >= 1, `escolha '${c.escolha_id}' pede zero opções`)
    assert.ok(
      c.opcoes.length >= c.quantidade,
      `escolha '${c.escolha_id}' oferece ${c.opcoes.length} para escolher ${c.quantidade}`,
    )
    assert.ok(c.origem.length > 0, 'toda escolha diz de onde veio')
  }
})

test('uma escolha que depende de outra é filtrada pela outra, não oferecida inteira', () => {
  // O Iniciado em Magia do antecedente já fixou a lista (Druida). Os truques têm de
  // sair DAQUELA lista — oferecer os 34 truques do jogo seria oferecer o que o
  // jogador não pode pegar.
  const g = ouro('monge-1')
  const r = montar(g.construcao, g.estado)
  const truques = r.checklist.find((c) => c.escolha_id.includes('truques'))
  assert.ok(truques, 'o Iniciado em Magia tem uma escolha de truques')
  assert.ok(
    truques.opcoes.length > 0 && truques.opcoes.length < 30,
    `esperava os truques de uma lista só, veio ${truques.opcoes.length}`,
  )
  assert.deepEqual(truques.nao_avaliados, [], 'a variável da lista tem de ter resolvido')
})

test('sem a escolha de que depende, a dependente vem bloqueada e diz por quê', () => {
  const g = ouro('monge-1')
  const c = copia(g.construcao)
  // tira a predefinição que o antecedente fazia da lista
  const semLista: Construcao = { ...c, antecedente: 'artesao' }
  semLista.escolhas = {
    artesao_aumento: { escolhido: 'todos_os_tres_em_1', distribuicao: { FOR: 1, DES: 1, INT: 1 } },
    monge_pericias_iniciais: ['acrobacia', 'furtividade'],
  }
  const r = montar(semLista, g.estado)
  const dependentes = r.checklist.filter((x) => x.bloqueada_por)
  for (const d of dependentes) {
    assert.equal(d.opcoes.length, 0, 'escolha bloqueada não oferece opção')
    assert.ok(d.bloqueada_por!.length > 0, 'e diz de qual escolha ela depende')
  }
})

test('escolha de categoria oferece as VARIANTES, não a categoria', () => {
  // Era o defeito: "Escolha um tipo de Kit de Jogos — 1 opção".
  const g = ouro('barbaro-5')
  const r = montar(g.construcao, g.estado_sem_furia)
  const kit = r.checklist.find((c) => c.rotulo.toLowerCase().includes('tipo de'))
  assert.ok(kit, 'o Soldado escolhe um tipo de kit')
  assert.ok(kit.opcoes.length > 1, `uma escolha de uma opção só não é escolha (${kit.opcoes.length})`)
})

test('a quantidade pode vir da coluna da tabela de classe', () => {
  const g = ouro('barbaro-5')
  const r = montar(g.construcao, g.estado_sem_furia)
  const maestrias = r.checklist.find((c) => c.escolha_id.includes('maestria'))
  assert.ok(maestrias, 'o Bárbaro escolhe maestrias em arma')
  assert.equal(maestrias.quantidade, 3, 'no nível 5 a coluna Maestria em Armas diz 3')
})

// ------------------------------------------------------------- e o que ele recusa

test('as construções de ouro não têm problema nenhum', () => {
  for (const nome of ['monge-1', 'barbaro-5']) {
    const g = ouro(nome)
    const r = montar(g.construcao, g.estado ?? g.estado_sem_furia)
    assert.deepEqual(r.problemas, [], `${nome} devia estar limpo`)
  }
})

test('escolher o que não está entre as opções vira problema', () => {
  const g = ouro('barbaro-5')
  const c = copia(g.construcao)
  c.escolhas!.barbaro_pericias_iniciais = ['atletismo', 'arcanismo'] // Bárbaro não tem Arcanismo
  const r = montar(c, g.estado_sem_furia)
  assert.ok(
    r.problemas.some((p) => p.queixa.includes('arcanismo')),
    'o motor tem de recusar a perícia que a classe não oferece',
  )
})

test('escolher menos do que a escolha pede vira problema', () => {
  const g = ouro('barbaro-5')
  const c = copia(g.construcao)
  c.escolhas!.barbaro_pericias_iniciais = ['atletismo']
  const r = montar(c, g.estado_sem_furia)
  assert.ok(r.problemas.some((p) => p.queixa.includes('pede 2')))
})

test('escolher a mesma opção duas vezes vira problema', () => {
  const g = ouro('barbaro-5')
  const c = copia(g.construcao)
  c.escolhas!.barbaro_pericias_iniciais = ['atletismo', 'atletismo']
  const r = montar(c, g.estado_sem_furia)
  assert.ok(r.problemas.some((p) => p.queixa.includes('duas vezes')))
})

test('escolha resolvida que este personagem não tem vira problema', () => {
  const g = ouro('monge-1')
  const c = copia(g.construcao)
  c.escolhas!.barbaro_pericias_iniciais = ['atletismo', 'percepcao']
  const r = montar(c, g.estado)
  assert.ok(
    r.problemas.some((p) => p.escolha_id === 'barbaro_pericias_iniciais'),
    'sobra de outra construção não pode passar calada',
  )
})

test('pré-requisito de talento é respeitado na oferta', () => {
  // A escolha de talento do nível 4 do Bárbaro filtra por `pre_requisitos_atendidos`.
  // Torvar tem Inteligência 8, Sabedoria 12 e Carisma 10, então todo talento que
  // exige 13 num deles está fora.
  //
  // Duas versões anteriores deste teste não provavam nada: olhavam o talento de
  // Origem do Humano e o nível exigido, e nos dois casos o recorte já era feito pela
  // CATEGORIA — o filtro de pré-requisito nunca chegava a morder. O teste de mutação
  // é que mostrou isso: desligar os pré-requisitos no motor não reprovava.
  const g = ouro('barbaro-5')
  const r = montar(g.construcao, g.estado_sem_furia)
  const escolhaDeTalento = r.colecao.escolhas.get('asi_escolha_de_talento')
  assert.ok(escolhaDeTalento, 'o nível 4 abre uma escolha de talento')

  const oferecidos = opcoesDe(escolhaDeTalento.efeito, r.contexto)
  assert.ok(oferecidos.opcoes.length > 0, 'tem de oferecer alguma coisa')

  type Pre = { tipo: string; minimo?: number; atributos?: string[] }
  const talentos = new Map(
    catalogo<{ id: string; pre_requisitos?: Pre[] }>('talentos').itens.map((t) => [t.id, t]),
  )
  const naoAtende = (p: Pre) => {
    if (p.tipo === 'nivel_de_personagem') return (p.minimo ?? 0) > r.contexto.nivel_do_personagem
    if (p.tipo === 'valor_de_atributo') {
      return !(p.atributos ?? []).some((a) => (r.contexto.atributos[a] ?? 0) >= (p.minimo ?? 0))
    }
    return false
  }

  const foraDoAlcance = oferecidos.opcoes.filter((o) =>
    (talentos.get(o.id)?.pre_requisitos ?? []).some(naoAtende),
  )
  assert.deepEqual(
    foraDoAlcance.map((o) => o.id),
    [],
    'talento cujo pré-requisito o personagem não atende não pode ser oferecido',
  )

  // e o teste tem de ter o que provar: se NENHUM talento fosse barrado, ele passaria
  // por vacuidade
  const barrados = [...talentos.values()].filter(
    (t) => t.pre_requisitos?.some(naoAtende) && !oferecidos.opcoes.some((o) => o.id === t.id),
  )
  assert.ok(
    barrados.length > 0,
    'nenhum talento foi barrado por pré-requisito — o teste não está provando nada',
  )
})

test('a conjuração da ficha é a da classe, não a do talento', () => {
  // A Clériga tem duas fontes de magia: a classe (Sabedoria, prepara) e o Iniciado
  // em Magia do Acólito (que só desbloqueia, com atributo próprio). A CD e o ataque
  // mágico da ficha são os da CLASSE. Antes desta distinção o motor pegava a
  // primeira fonte que aparecesse — e a primeira era a do talento, com o atributo
  // ainda numa variável.
  const g = ouro('clerigo-5')
  const r = montar(g.construcao, g.estado)
  assert.equal(r.ficha.conjuracao?.atributo, 'SAB')
  assert.equal(r.ficha.conjuracao?.cd_para_evitar_sua_magia.valor, 15)

  // e quem não conjura não ganha linha de magia nenhuma
  const b = ouro('barbaro-5')
  assert.equal(montar(b.construcao, b.estado_sem_furia).ficha.conjuracao, undefined)
})

// ------------------------------------------------------------------ folga

test('folga: resolver uma escolha do checklist tira ela do checklist e não cria problema', () => {
  const g = ouro('monge-1')
  const antes = montar(g.construcao, g.estado)
  const alvo = antes.checklist.find((c) => c.quantidade === 1 && c.opcoes.length > 1)
  assert.ok(alvo, 'precisa de uma escolha simples para o teste')

  const c = copia(g.construcao)
  c.escolhas![alvo.escolha_id] = alvo.opcoes[0].id
  const depois = montar(c, g.estado)

  assert.ok(!depois.checklist.some((x) => x.escolha_id === alvo.escolha_id))
  assert.deepEqual(
    depois.problemas.filter((p) => p.escolha_id === alvo.escolha_id),
    [],
    'escolher a primeira opção oferecida não pode virar problema',
  )
})
