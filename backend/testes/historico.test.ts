// O histórico.
//
// O que estes testes existem para garantir, além de "grava e lê":
//
// 1. **O número congelado.** "PV 20/26" tem de continuar 26 depois de o personagem
//    subir de nível. É a diferença entre histórico e proveniência, e é a única coisa
//    aqui que um refactor descuidado quebra sem parecer que quebrou.
// 2. **Nada de evento fantasma.** PATCH que reenvia o mesmo valor não gera linha.
// 3. **Isolamento.** O histórico é de quem é dono do personagem, como tudo o mais.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { subir, ouro } from './ajuda.ts'
import { aoMudarEstado } from '../src/eventos.ts'
import { resumo, type Evento } from '../src/evento.ts'

const clerigo = () => ouro('clerigo-5').construcao

async function comClerigo() {
  const c = await subir()
  const r = await c.pedir('POST', '/personagens', { nome: 'Vesna', construcao: clerigo() })
  assert.equal(r.status, 201, JSON.stringify(r.corpo))
  return { c, id: r.corpo.id as string, pvMaximo: r.corpo.ficha.pontos_de_vida_maximos.valor as number }
}

// --------------------------------------------------------------------- vida

test('o exemplo do João: recuperar vida sai com o PV do momento', async () => {
  const { c, id, pvMaximo } = await comClerigo()
  try {
    await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 12 })
    const r = await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 20 })
    assert.equal(r.status, 200)

    const [e] = r.corpo.eventos
    assert.equal(e.tipo, 'vida_recuperada')
    assert.equal(e.quantidade, 8)
    assert.equal(e.pv_antes, 12)
    assert.equal(e.pv_depois, 20)
    assert.equal(e.pv_maximo, pvMaximo)
    assert.equal(e.resumo, `recuperou 8 de vida · PV 20/${pvMaximo}`)
  } finally {
    await c.fechar()
  }
})

test('dano é dano, cura é cura — o sinal decide', async () => {
  const { c, id } = await comClerigo()
  try {
    await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 30 })
    const r = await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 24 })
    const [e] = r.corpo.eventos
    assert.equal(e.tipo, 'dano_sofrido')
    assert.equal(e.quantidade, 6)
    assert.match(e.resumo, /^sofreu 6 de dano · PV 24\//)
  } finally {
    await c.fechar()
  }
})

test('o PV máximo do evento NÃO muda quando o personagem sobe de nível', async () => {
  // É o coração da coisa. O evento é o passado: se subir de nível reescrevesse o
  // denominador das linhas antigas, o histórico deixaria de dizer o que aconteceu.
  const { c, id, pvMaximo } = await comClerigo()
  try {
    await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 12 })
    await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 20 })

    const subiu = await c.pedir('POST', `/personagens/${id}/subir-nivel`, { classe: 'clerigo' })
    assert.equal(subiu.status, 200, JSON.stringify(subiu.corpo).slice(0, 200))
    const novoMaximo = subiu.corpo.ficha.pontos_de_vida_maximos.valor as number
    assert.ok(novoMaximo > pvMaximo, 'subir de nível tem de aumentar o PV máximo')

    const h = await c.pedir('GET', `/personagens/${id}/historico`)
    const cura = h.corpo.itens.find((e: Evento) => e.tipo === 'vida_recuperada')
    assert.equal(cura.pv_maximo, pvMaximo, 'o denominador antigo tem de continuar o antigo')
    assert.equal(cura.resumo, `recuperou 8 de vida · PV 20/${pvMaximo}`)
  } finally {
    await c.fechar()
  }
})

// ------------------------------------------------------------------ magias

test('gastar espaço com magia nomeada diz o nome da magia', async () => {
  const { c, id } = await comClerigo()
  try {
    const r = await c.pedir('PATCH', `/personagens/${id}/estado`, {
      espacos_gastos: { '3': 1 },
      motivo: { magia_id: 'bola_de_fogo' },
    })
    assert.equal(r.status, 200, JSON.stringify(r.corpo))
    const [e] = r.corpo.eventos
    assert.equal(e.tipo, 'espaco_gasto')
    assert.equal(e.circulo, 3)
    assert.equal(e.magia_nome, 'Bola de Fogo')
    assert.equal(e.total, 2, 'a Clériga de nível 5 tem 2 espaços de 3º')
    assert.equal(e.restantes, 1)
    assert.equal(e.resumo, 'conjurou Bola de Fogo com espaço de 3º · 1/2 restantes')
  } finally {
    await c.fechar()
  }
})

test('sem motivo, a linha diz o que sabe e não inventa magia', async () => {
  const { c, id } = await comClerigo()
  try {
    const r = await c.pedir('PATCH', `/personagens/${id}/estado`, { espacos_gastos: { '1': 2 } })
    const [e] = r.corpo.eventos
    assert.equal(e.magia_id, undefined)
    assert.equal(e.resumo, 'gastou 2 espaços de 1º · 2/4 restantes')
  } finally {
    await c.fechar()
  }
})

test('magia que não existe no compêndio não derruba o pedido', async () => {
  const { c, id } = await comClerigo()
  try {
    const r = await c.pedir('PATCH', `/personagens/${id}/estado`, {
      espacos_gastos: { '1': 1 },
      motivo: { magia_id: 'magia_que_nao_existe' },
    })
    assert.equal(r.status, 200)
    const [e] = r.corpo.eventos
    assert.equal(e.magia_id, 'magia_que_nao_existe')
    assert.equal(e.magia_nome, undefined, 'sem nome, mas o id fica registrado')
  } finally {
    await c.fechar()
  }
})

test('recuperar espaço não carimba magia nenhuma', async () => {
  const { c, id } = await comClerigo()
  try {
    await c.pedir('PATCH', `/personagens/${id}/estado`, {
      espacos_gastos: { '1': 3 }, motivo: { magia_id: 'bencao' },
    })
    const r = await c.pedir('PATCH', `/personagens/${id}/estado`, {
      espacos_gastos: { '1': 0 }, motivo: { magia_id: 'bencao' },
    })
    const [e] = r.corpo.eventos
    assert.equal(e.tipo, 'espaco_recuperado')
    assert.equal(e.magia_id, undefined, 'recuperar espaço não conjura nada')
    assert.equal(e.resumo, 'recuperou 3 espaços de 1º · 4/4 restantes')
  } finally {
    await c.fechar()
  }
})

// -------------------------------------------------------- o que NÃO vira evento

test('reenviar o mesmo valor não gera evento', async () => {
  const { c, id } = await comClerigo()
  try {
    await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 20 })
    const denovo = await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 20 })
    assert.deepEqual(denovo.corpo.eventos, [], 'o histórico é do que aconteceu, não do que foi pedido')

    const h = await c.pedir('GET', `/personagens/${id}/historico`)
    assert.equal(h.corpo.itens.length, 1, 'só a primeira marcação virou linha')
  } finally {
    await c.fechar()
  }
})

test('a primeira marcação de dano parte da vida cheia', async () => {
  // Este teste nasceu de uma falha: o personagem começa sem `pontos_de_vida_atuais`,
  // e a primeira versão só gerava evento quando havia um "antes". O resultado era o
  // primeiro dano de toda campanha sumir do histórico. A convenção — sem PV atual,
  // está cheio — é do backend, não do livro, e é o que bate com a ficha nova.
  const { c, id, pvMaximo } = await comClerigo()
  try {
    const r = await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 30 })
    const [e] = r.corpo.eventos
    assert.equal(e.tipo, 'dano_sofrido')
    assert.equal(e.pv_antes, pvMaximo)
    assert.equal(e.quantidade, pvMaximo - 30)
  } finally {
    await c.fechar()
  }
})

test('motivo não é estado: não fica gravado no personagem', async () => {
  const { c, id } = await comClerigo()
  try {
    await c.pedir('PATCH', `/personagens/${id}/estado`, {
      espacos_gastos: { '1': 1 }, motivo: { magia_id: 'bencao' },
    })
    const guardado = (await c.armazem.ler(id))!
    assert.equal((guardado.estado as Record<string, unknown>).motivo, undefined)
  } finally {
    await c.fechar()
  }
})

test('campo que não é estado continua sendo recusado', async () => {
  const { c, id } = await comClerigo()
  try {
    const r = await c.pedir('PATCH', `/personagens/${id}/estado`, { classe_de_armadura: 30 })
    assert.equal(r.status, 400, 'abrir uma porta para `motivo` não pode abrir para tudo')
  } finally {
    await c.fechar()
  }
})

// -------------------------------------------------------- leitura e isolamento

test('histórico vem do mais recente para o mais antigo, e pagina', async () => {
  const { c, id } = await comClerigo()
  try {
    for (const pv of [30, 28, 26, 24, 22]) {
      await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: pv })
    }
    const primeira = await c.pedir('GET', `/personagens/${id}/historico?limite=2`)
    assert.equal(primeira.corpo.itens.length, 2)
    assert.equal(primeira.corpo.itens[0].pv_depois, 22, 'o mais recente primeiro')
    assert.ok(primeira.corpo.proximo, 'há mais páginas')

    const segunda = await c.pedir(
      'GET', `/personagens/${id}/historico?limite=2&antes_de=${encodeURIComponent(primeira.corpo.proximo)}`)
    const idsDaPrimeira = new Set(primeira.corpo.itens.map((e: Evento) => e.id))
    for (const e of segunda.corpo.itens) {
      assert.ok(!idsDaPrimeira.has(e.id), 'a segunda página não repete a primeira')
    }
  } finally {
    await c.fechar()
  }
})

test('o histórico de outra pessoa é 404', async () => {
  const { c, id } = await comClerigo()
  try {
    await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 20 })
    const outro = await c.outroUsuario()
    const r = await c.pedir('GET', `/personagens/${id}/historico`, undefined,
      { authorization: `Bearer ${outro.token}` })
    assert.equal(r.status, 404)
  } finally {
    await c.fechar()
  }
})

// --------------------------------------------------- a diferença, sem servidor

test('aoMudarEstado só produz evento para o que mudou', () => {
  const retrato = { pv_maximo: 38, espacos: { '1': 4, '2': 3, '3': 2 } }
  const antes = { pontos_de_vida_atuais: 20, espacos_gastos: { '1': 1 }, recursos_gastos: {} }

  assert.deepEqual(aoMudarEstado(antes, { ...antes }, retrato), [], 'nada mudou, nada aconteceu')

  // Cada eixo tem um item que MUDOU e um que NÃO mudou, lado a lado. É o par que
  // importa: sem o que não mudou, "gerar evento para tudo" passaria despercebido —
  // e foi o que um teste de mutação mostrou, no eixo dos recursos.
  const comParado = {
    ...antes,
    recursos_gastos: { canalizar_divindade: 1, forma_selvagem: 2 },
  }
  const eventos = aoMudarEstado(comParado, {
    pontos_de_vida_atuais: 14,
    espacos_gastos: { '1': 1, '2': 1 },
    recursos_gastos: { canalizar_divindade: 2, forma_selvagem: 2 },
  }, retrato)

  assert.deepEqual(eventos.map((e) => e.tipo),
    ['dano_sofrido', 'espaco_gasto', 'recurso_gasto'])
  assert.equal(eventos.filter((e) => e.tipo === 'espaco_gasto').length, 1,
    'o círculo 1 não mudou e não pode ter virado evento')
  const recursos = eventos.filter((e) => e.tipo === 'recurso_gasto')
  assert.equal(recursos.length, 1, 'forma_selvagem não mudou e não pode ter virado evento')
  assert.equal((recursos[0] as { recurso_id: string }).recurso_id, 'canalizar_divindade')
})

test('resumo formata só com o que está no evento', () => {
  const base = { id: 'e1', personagem_id: 'p1', usuario_id: 'u1', em: '2026-09-03T00:00:00.000Z' }
  assert.equal(
    resumo({ ...base, tipo: 'vida_recuperada', quantidade: 8, pv_antes: 12, pv_depois: 20, pv_maximo: 26 }),
    'recuperou 8 de vida · PV 20/26')
  assert.equal(
    resumo({ ...base, tipo: 'temporarios_alterados', antes: 0, depois: 5 }),
    'ganhou 5 Pontos de Vida Temporários (5)')
  assert.equal(
    resumo({ ...base, tipo: 'temporarios_alterados', antes: 5, depois: 4 }),
    'perdeu 1 Ponto de Vida Temporário (4)')
  assert.equal(
    resumo({ ...base, tipo: 'recurso_gasto', recurso_id: 'furia', quantidade: 1, gastos_depois: 1 }),
    'gastou 1 de furia')
})
