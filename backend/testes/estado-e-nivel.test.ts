// Estado, subir de nível e escolhas.
//
// A fronteira estado × derivado é a decisão que o dataset já tinha tomado
// (`valores_derivados`, e PV atual fora da base). Aqui ela vira regra de HTTP: o
// PATCH aceita o que a mesa muda e recusa o que a regra calcula.

import { test, after } from 'node:test'
import assert from 'node:assert/strict'
import { subir, ouro } from './ajuda.ts'

const c = await subir()
after(() => c.fechar())

const clerigo = ouro('clerigo-5')
const criar = async (nome = 'Ysolde') =>
  (await c.pedir('POST', '/personagens', { nome, construcao: clerigo.construcao })).corpo

test('o PATCH aceita estado', async () => {
  const p = await criar()
  const r = await c.pedir('PATCH', `/personagens/${p.id}/estado`, {
    pontos_de_vida_atuais: 12,
    condicoes: ['amedrontado'],
    espacos_gastos: { '1': 2 },
  })
  assert.equal(r.status, 200)
  assert.equal(r.corpo.estado.pontos_de_vida_atuais, 12)
  assert.deepEqual(r.corpo.estado.condicoes, ['amedrontado'])
})

test('o PATCH recusa derivado — guardar derivado é criar uma segunda verdade', async () => {
  const p = await criar()
  const r = await c.pedir('PATCH', `/personagens/${p.id}/estado`, { classe_de_armadura: 30 })
  assert.equal(r.status, 400)
  assert.match(r.corpo.mensagem, /não são estado/)
  const depois = await c.pedir('GET', `/personagens/${p.id}`)
  assert.equal(depois.corpo.ficha.classe_de_armadura.valor, 16, 'a CA continua sendo calculada')
})

test('o PATCH recusa construção: mudar quem o personagem é passa por /escolhas', async () => {
  const p = await criar()
  const r = await c.pedir('PATCH', `/personagens/${p.id}/estado`, { especie: 'anao' })
  assert.equal(r.status, 400)
})

test('subir de nível muda os Pontos de Vida e diz o que falta completar', async () => {
  const p = await criar()
  const antes = p.ficha.pontos_de_vida_maximos.valor
  const r = await c.pedir('POST', `/personagens/${p.id}/subir-nivel`, {})
  assert.equal(r.status, 200)
  assert.equal(r.corpo.nivel, 6)
  assert.ok(r.corpo.ficha.pontos_de_vida_maximos.valor > antes)

  // A Clériga preparava 9 magias no 5 e passa a preparar 10 no 6. Isso é pendência,
  // não defeito: subir de nível não pode ser recusado por causa dele.
  const completar = r.corpo.escolhas_a_completar
  assert.equal(completar.length, 1)
  assert.equal(completar[0].escolha_id, 'clerigo_preparadas')
  assert.equal(completar[0].tipo, 'incompleta')
  assert.equal(completar[0].faltam, 1)
})

test('subir de nível numa classe que não é do personagem é recusado, e explica por quê', async () => {
  const p = await criar()
  const r = await c.pedir('POST', `/personagens/${p.id}/subir-nivel`, { classe: 'mago' })
  assert.equal(r.status, 400)
  assert.match(r.corpo.mensagem, /multiclasse/i)
  assert.equal((await c.pedir('GET', `/personagens/${p.id}`)).corpo.construcao.niveis.length, 1)
})

test('não passa do nível 20', async () => {
  const alto = JSON.parse(JSON.stringify(clerigo.construcao))
  alto.niveis[0].nivel = 20
  const p = (await c.pedir('POST', '/personagens', { nome: 'Veterana', construcao: alto })).corpo
  const r = await c.pedir('POST', `/personagens/${p.id}/subir-nivel`, {})
  assert.equal(r.status, 400)
  assert.match(r.corpo.mensagem, /nível 20/)
})

test('completar a escolha pendente zera a pendência', async () => {
  const p = await criar()
  await c.pedir('POST', `/personagens/${p.id}/subir-nivel`, {})
  const preparadas = [...clerigo.construcao.escolhas.clerigo_preparadas, 'bencao']
  const r = await c.pedir('POST', `/personagens/${p.id}/escolhas`, {
    escolhas: { clerigo_preparadas: preparadas },
  })
  assert.equal(r.status, 200)
  assert.equal(r.corpo.pendencias_de_escolha.length, 0)
})

test('escolha inválida é recusada E não fica gravada', async () => {
  const p = await criar()
  const antes = (await c.armazem.ler(p.id))!.construcao.escolhas!.clerigo_truques
  const r = await c.pedir('POST', `/personagens/${p.id}/escolhas`, {
    escolhas: { clerigo_truques: ['bola_de_fogo', 'luz', 'orientacao', 'resistencia'] },
  })
  assert.equal(r.status, 422)
  const depois = (await c.armazem.ler(p.id))!.construcao.escolhas!.clerigo_truques
  assert.deepEqual(depois, antes, 'o personagem não pode ter mudado')
})

test('o aviso de versão aparece quando o personagem foi feito contra outra base', async () => {
  const p = await criar()
  const guardado = (await c.armazem.ler(p.id))!
  guardado.versao_do_dataset = 'aaaaaaaaaaaa'
  await c.armazem.gravar(guardado)
  const r = await c.pedir('GET', `/personagens/${p.id}`)
  assert.equal(r.status, 200, 'avisa, não quebra')
  assert.match(r.corpo.aviso_de_versao, /aaaaaaaaaaaa/)
})

test('o estado tem tipo: valor errado é recusado antes de virar lixo guardado', async () => {
  const p = await criar()
  for (const [corpo, oQue] of [
    [{ pontos_de_vida_atuais: 'muito' }, 'PV como texto'],
    [{ pontos_de_vida_temporarios: -3 }, 'temporários negativos'],
    [{ condicoes: 'amedrontado' }, 'condições como texto solto'],
    [{ espacos_gastos: { '1': 'dois' } }, 'espaços gastos como texto'],
    [{ predicados_ativos: [1, 2] }, 'predicados que não são texto'],
  ] as const) {
    const r = await c.pedir('PATCH', `/personagens/${p.id}/estado`, corpo)
    assert.equal(r.status, 400, `${oQue} deveria dar 400`)
  }
  const guardado = (await c.armazem.ler(p.id))!
  assert.equal(guardado.estado.pontos_de_vida_atuais, undefined, 'nada disso pode ter sido gravado')
})

test('subir de nível recusado não deixa o personagem meio subido', async () => {
  const alto = JSON.parse(JSON.stringify(clerigo.construcao))
  alto.niveis[0].nivel = 20
  const p = (await c.pedir('POST', '/personagens', { nome: 'No teto', construcao: alto })).corpo
  await c.pedir('POST', `/personagens/${p.id}/subir-nivel`, {})
  assert.equal((await c.armazem.ler(p.id))!.construcao.niveis[0].nivel, 20)
})

test('responder uma escolha não apaga o aviso de versão', async () => {
  // O aviso diz "este personagem foi construído contra outra base". Re-carimbar a
  // versão ao responder uma escolha qualquer faria ele sumir sem que nada tivesse
  // sido conferido — escondendo exatamente o que ele existe para mostrar.
  const p = await criar()
  const guardado = (await c.armazem.ler(p.id))!
  guardado.versao_do_dataset = 'bbbbbbbbbbbb'
  await c.armazem.gravar(guardado)
  const r = await c.pedir('POST', `/personagens/${p.id}/escolhas`, {
    escolhas: { humano_habil: 'atletismo' },
  })
  assert.equal(r.status, 200)
  assert.ok(r.corpo.aviso_de_versao, 'o aviso continua')
  assert.equal((await c.armazem.ler(p.id))!.versao_do_dataset, 'bbbbbbbbbbbb')
})

test('personagem que a base não monta mais é AVISADO, não quebrado', async () => {
  // O PLANO-MOTOR §7 pede que a base mudar de um jeito que invalide uma escolha faça
  // o app avisar em vez de quebrar. Um 500 aqui faria o jogador perder o personagem
  // de vista justamente quando ele precisa corrigir a escolha.
  const p = await criar()
  const guardado = (await c.armazem.ler(p.id))!
  guardado.construcao.especie = 'especie_que_sumiu_da_base'
  guardado.versao_do_dataset = 'cccccccccccc'
  await c.armazem.gravar(guardado)

  const r = await c.pedir('GET', `/personagens/${p.id}`)
  assert.equal(r.status, 200, 'ler continua funcionando')
  assert.equal(r.corpo.ficha, null, 'sem ficha, porque não dá para calcular')
  assert.equal(r.corpo.nome, 'Ysolde', 'mas o personagem continua visível')
  assert.match(r.corpo.erro_de_ficha.mensagem, /especie_que_sumiu_da_base/)
  assert.match(r.corpo.erro_de_ficha.o_que_fazer, /cccccccccccc/)
})

test('escrever continua recusando o que a leitura tolera', async () => {
  // A tolerância é só da LEITURA. Propor mudança inválida é erro de quem propõe.
  const p = await criar()
  const guardado = (await c.armazem.ler(p.id))!
  guardado.construcao.especie = 'especie_que_sumiu_da_base'
  await c.armazem.gravar(guardado)
  const r = await c.pedir('POST', `/personagens/${p.id}/subir-nivel`, {})
  assert.equal(r.status, 422)
})

/** Um Mago cru: o golden do Clérigo já tem tudo respondido, e prévia precisa de pendência. */
const magoCru = {
  especie: 'humano', antecedente: 'acolito',
  niveis: [{ classe: 'mago', nivel: 1 }],
  atributos_base: { FOR: 10, DES: 14, CON: 12, INT: 15, SAB: 13, CAR: 8 },
}
const criarMago = async () =>
  (await c.pedir('POST', '/personagens', { nome: 'Nael', construcao: magoCru })).corpo

test('a prévia mostra o que a escolha abre, e não grava nada', async () => {
  // O jogador escolhia talento no escuro: o Iniciado em Magia só revela que pede
  // lista, atributo e magias DEPOIS de gravado. A prévia responde antes.
  const p = await criarMago()
  const antes = (await c.armazem.ler(p.id))!.construcao.escolhas ?? {}
  const alvo = p.checklist.find(
    (x: { escolha_id: string; quantidade: number; opcoes: unknown[] }) =>
      x.quantidade === 1 && x.opcoes.length > 1,
  )
  assert.ok(alvo, 'precisa de uma escolha simples')

  const r = await c.pedir('POST', `/personagens/${p.id}/escolhas/previa`, {
    escolhas: { [alvo.escolha_id]: alvo.opcoes[0].id },
  })
  assert.equal(r.status, 200)
  assert.deepEqual(r.corpo.respondidas, [alvo.escolha_id])
  assert.ok(
    !r.corpo.checklist.some((x: { escolha_id: string }) => x.escolha_id === alvo.escolha_id),
    'a escolha respondida sai do checklist da prévia',
  )
  assert.deepEqual(
    (await c.armazem.ler(p.id))!.construcao.escolhas ?? {},
    antes,
    'prévia não grava — o personagem tem de estar intacto',
  )
})

test('a prévia recusa o inválido do mesmo jeito que a gravação', async () => {
  const p = await criar()
  const r = await c.pedir('POST', `/personagens/${p.id}/escolhas/previa`, {
    escolhas: { clerigo_truques: ['bola_de_fogo', 'luz', 'orientacao', 'resistencia'] },
  })
  assert.equal(r.status, 422, 'propor o impossível é erro do cliente, com ou sem gravação')
})

test('a prévia de um talento revela as escolhas que ele traz junto', async () => {
  // O caso concreto do relato: escolher Iniciado em Magia tem de mostrar, ali mesmo,
  // que ele vai pedir lista, atributo de conjuração e magias.
  const p = await criarMago()
  const talento = p.checklist.find(
    (x: { opcoes: { id: string }[] }) => x.opcoes.some((o) => o.id === 'iniciado_em_magia'),
  )
  assert.ok(talento, 'o Humano oferece talento de Origem à escolha')
  const r = await c.pedir('POST', `/personagens/${p.id}/escolhas/previa`, {
    escolhas: { [talento.escolha_id]: 'iniciado_em_magia' },
  })
  assert.equal(r.status, 200)
  const novas = r.corpo.checklist.filter((x: { escolha_id: string }) =>
    x.escolha_id.startsWith('iniciado_em_magia_'))
  assert.ok(novas.length > 0, 'as escolhas do talento têm de aparecer na prévia')
})
