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

import { montar, ehPendencia } from '../src/motor.ts'
import { opcoesDe, checklist } from '../src/escolha.ts'
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
  // O id leva o nível da concessão: uma característica repetível abre a mesma
  // escolha em cada nível em que chega, e sem o sufixo elas se sobrescreveriam.
  const escolhaDeTalento = r.colecao.escolhas.get('asi_escolha_de_talento@4')
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

test('uma característica repetível abre uma escolha POR NÍVEL, e não uma só', () => {
  // O defeito que este teste guarda: `escolhas` é indexado por id, e o Aumento no
  // Valor de Atributo chega no 4, 8, 12 e 16 com o mesmo id declarado. Sem qualificar
  // pelo nível, o do 8 sobrescrevia o do 4 — e o personagem nunca conseguia dois
  // talentos diferentes. Apareceu quando o backend tentou subir uma Clériga até o 20
  // e o motor acusou que a Sabedoria passaria de 20: era o MESMO aumento, aplicado
  // cinco vezes.
  const g = ouro('clerigo-5')
  const c = JSON.parse(JSON.stringify(g.construcao)) as typeof g.construcao
  c.niveis[0].nivel = 8
  for (const k of Object.keys(c.escolhas)) {
    if (k.startsWith('asi_') || k.startsWith('avatributo')) delete c.escolhas[k]
  }
  const r = montar(c, {})
  const asi = r.checklist.filter((x) => x.escolha_id.startsWith('asi_')).map((x) => x.escolha_id)
  assert.deepEqual(asi, ['asi_escolha_de_talento@4', 'asi_escolha_de_talento@8'])

  // e as duas podem ser respondidas com talentos DIFERENTES
  c.escolhas['asi_escolha_de_talento@4'] = 'aumento_no_valor_de_atributo'
  c.escolhas['avatributo_modo@4'] = 'dois_atributos_em_1'
  c.escolhas['avatributo_dois@4'] = ['SAB', 'CON']
  c.escolhas['asi_escolha_de_talento@8'] = 'atleta'
  const r2 = montar(c, {})
  // Só os DEFEITOS têm de sumir. A Clériga de nível 8 prepara 12 magias e o golden
  // traz 9: isso é pendência de subir de nível, não construção inválida.
  const defeitos = r2.problemas.filter((p) => !ehPendencia(p))
  assert.deepEqual(defeitos, [], 'dois aumentos diferentes é construção válida')
  assert.equal(
    r2.checklist.filter((x) => x.escolha_id.startsWith('asi_')).length,
    0,
    'nenhum aumento fica pendente depois de respondidos os dois',
  )
})

// ------------------------------------------------- fontes: o livro de magias

/** Um Mago cru de nível N, sem escolha nenhuma respondida. */
function mago(nivel = 1, escolhas: Record<string, unknown> = {}): Construcao {
  return {
    especie: 'humano',
    antecedente: 'acolito',
    niveis: [{ classe: 'mago', nivel }],
    atributos_base: { FOR: 10, DES: 14, CON: 12, INT: 15, SAB: 13, CAR: 8 },
    escolhas,
  } as unknown as Construcao
}

const doChecklist = (r: ReturnType<typeof montar>, id: string) =>
  r.checklist.find((c) => c.escolha_id === id)

test('o livro de magias do Mago é uma escolha, e as preparadas saem DELE', () => {
  // O defeito relatado: "não estava aparecendo as magias para preparar". O livro
  // nascia vazio porque as seis magias iniciais nunca viravam escolha, e preparar
  // filtrava por um campo `no_livro` que magia nenhuma tem.
  const vazio = montar(mago(), {})
  const livro = doChecklist(vazio, 'mago_livro')
  assert.ok(livro, 'o livro tem de aparecer no checklist do nível 1')
  assert.equal(livro.quantidade, 6, 'seis magias no nível 1 (p. 147)')
  assert.ok(livro.opcoes.length > 6)
  assert.ok(
    livro.opcoes.every((o) =>
      catalogo<{ id: string; nivel: number }>('magias').itens
        .find((m) => m.id === o.id)!.nivel === 1),
    'no nível 1 só há espaço de 1º círculo, então só 1º círculo entra no livro',
  )

  // Enquanto o livro está vazio, preparar não oferece nada — e DIZ por quê, em vez
  // de devolver lista vazia calada, que era o sintoma.
  const preparar = doChecklist(vazio, 'mago_preparadas')
  assert.ok(preparar)
  assert.deepEqual(preparar.opcoes, [])
  assert.equal(preparar.bloqueada_por, 'livro_de_magias')

  // Com o livro escrito, preparar oferece exatamente o que está no livro.
  const seis = livro.opcoes.slice(0, 6).map((o) => o.id)
  const cheio = montar(mago(1, { mago_livro: seis }), {})
  const preparar2 = doChecklist(cheio, 'mago_preparadas')!
  assert.equal(preparar2.bloqueada_por, undefined)
  assert.deepEqual(preparar2.opcoes.map((o) => o.id).sort(), [...seis].sort())
  assert.equal(preparar2.quantidade, 4)
  assert.deepEqual(cheio.problemas, [], 'livro respondido não é problema nenhum')
})

test('o livro cresce com o nível de Mago, e junto o círculo que cabe nele', () => {
  const n3 = montar(mago(3), {})
  const livro = doChecklist(n3, 'mago_livro')!
  assert.equal(livro.quantidade, 10, 'seis no 1 mais duas por nível: 6 + 2×2')
  const circulos = new Set(
    livro.opcoes.map((o) =>
      catalogo<{ id: string; nivel: number }>('magias').itens.find((m) => m.id === o.id)!.nivel),
  )
  assert.deepEqual([...circulos].sort(), [1, 2], 'no nível 3 o Mago tem espaços de 2º')
})

test('um filtro `coluna:` é lido da tabela da classe, e não comparado como texto', () => {
  // O Bruxo prepara magias "de círculo não superior ao mostrado na coluna Círculo de
  // Magia". A comparação era feita contra a string 'coluna:circulo_dos_espacos', que
  // não é número nenhum — e a lista de preparadas do Bruxo saía vazia, do mesmo jeito
  // que a do Mago, por causa completamente diferente.
  const bruxo = montar(
    { ...mago(1), niveis: [{ classe: 'bruxo', nivel: 1 }] } as Construcao, {},
  )
  const preparar = doChecklist(bruxo, 'bruxo_preparadas')!
  assert.ok(preparar.opcoes.length > 0, 'o Bruxo de nível 1 tem o que preparar')
  assert.ok(
    preparar.opcoes.every((o) =>
      catalogo<{ id: string; nivel: number }>('magias').itens
        .find((m) => m.id === o.id)!.nivel === 1),
    'no nível 1 o círculo dos espaços é 1',
  )
})

test('escolha que neste nível pede zero não aparece no checklist', () => {
  // Não há hoje escolha que peça zero no dado — mas `quantidade_por_nivel` produz
  // exatamente isso para uma característica que só começa a dar opções mais tarde, e
  // "escolha 0 de 31" é linha morta na tela do jogador. Testado direto no checklist
  // porque nenhum personagem do dataset atual chega lá.
  const ctx = montar(mago(1), {}).contexto
  const e = {
    id: 'so_do_nivel_5', tipo: 'escolha', rotulo: 'Escolha uma perícia',
    quantidade_por_nivel: { 5: 1 },
    de: { catalogo: 'pericias', todo_o_catalogo: true },
  } as unknown as Parameters<typeof checklist>[1] extends Map<string, infer E> ? E : never
  const pendencia = { escolha_id: 'so_do_nivel_5', rotulo: 'x', origem: 'teste' }

  assert.deepEqual(
    checklist([pendencia], new Map([['so_do_nivel_5', e]]), ctx),
    [],
    'quantidade 0 não é pendência',
  )
  const ctx5 = montar(mago(5), {}).contexto
  assert.equal(
    checklist([pendencia], new Map([['so_do_nivel_5', e]]), ctx5).length,
    1,
    'no nível 5 a mesma escolha aparece',
  )
})

// ------------------------- efeito nomeado que mora num catálogo (defeito do João)

test('efeito nomeado com `catalogo` sai do catálogo, e não do dono', () => {
  // "efeito nomeado 'dragao_vermelho' não existe em '(sem dono)'": a herança do
  // Draconato declara `catalogo: heranca_draconica`, e o coletor procurava em
  // `dono.efeitos_nomeados`. Dez dos 37 usos faziam isso — seis espécies e três
  // classes ficavam intransponíveis na hora de responder a escolha.
  for (const especie of ['draconato', 'elfo', 'gnomo', 'golias', 'tiferino', 'aasimar']) {
    const cru = montar({ ...mago(), especie } as Construcao, {})
    const heranca = cru.checklist.find((c) => c.opcoes.length > 1 && /heranca|linhagem|legado|ancestralidade|revelacao/.test(c.escolha_id))
    if (!heranca) continue
    const r = montar(
      { ...mago(1, { [heranca.escolha_id]: heranca.opcoes[0].id }), especie } as Construcao, {},
    )
    assert.deepEqual(
      r.problemas.filter((p) => p.escolha_id === heranca.escolha_id),
      [],
      `${especie}: escolher a herança não pode explodir`,
    )
  }
})

test('talento repetível ganho por duas fontes abre duas escolhas, não uma repetida', () => {
  // React acusou "two children with the same key, iniciado_em_magia_truques": o
  // Humano concede um talento de Origem e o antecedente concede outro; escolhido o
  // mesmo talento repetível nos dois, as escolhas dele colidiam no mesmo id e a
  // gravação nunca terminava. O livro permite o repeat (p. 201) — então o conserto é
  // qualificar, não recusar.
  // O antecedente Acólito já concede Iniciado em Magia; o Humano concede outro
  // talento de Origem à escolha, e escolher o MESMO é o caso do defeito.
  const r = montar(mago(1, { humano_versatil: 'iniciado_em_magia' }), {})
  const ids = r.checklist.map((x) => x.escolha_id)
  assert.equal(new Set(ids).size, ids.length, 'nenhum id repetido no checklist')

  const iniciado = ids.filter((i) => i.startsWith('iniciado_em_magia_'))
  const doHumano = new Set(iniciado.filter((i) => i.endsWith('@humano_versatil')))
  const doAntecedente = iniciado.filter((i) => !i.endsWith('@humano_versatil'))
  assert.ok(doHumano.size > 0, 'o talento vindo do Humano tem escolhas próprias')
  for (const i of doAntecedente) {
    assert.ok(
      doHumano.has(`${i}@humano_versatil`),
      `'${i}' do antecedente precisa de um par qualificado pelo Humano`,
    )
  }
  // O do Humano abre uma escolha a mais: o Acólito já vem com a lista definida, e o
  // Humano ainda tem de escolher a dele.
  assert.ok(doHumano.size >= doAntecedente.length)
})
