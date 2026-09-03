// Contas, sessão e — o que mais importa — isolamento entre usuários.
//
// A pergunta que estes testes existem para responder não é "dá para entrar?", e sim
// **"o personagem de uma pessoa aparece para outra?"**. Antes das contas, o
// `GET /personagens` listava os de todo mundo; um teste que só provasse o login
// passaria sem provar isso.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { subir, ouro, SEGREDO_DE_TESTE, SENHA_DE_TESTE } from './ajuda.ts'
import { criarToken, hashDeSenha, lerToken, senhaConfere, normalizarEmail } from '../src/usuario.ts'

const semToken = { authorization: '' }

// ------------------------------------------------------------------ cadastro

test('cadastro devolve token que já serve para pedir', async () => {
  const c = await subir()
  try {
    const eu = await c.pedir('GET', '/eu')
    assert.equal(eu.status, 200)
    assert.equal(eu.corpo.email, 'jogador@exemplo.test')
    assert.equal(eu.corpo.senha_hash, undefined, 'o hash da senha não pode sair daqui')
  } finally {
    await c.fechar()
  }
})

test('e-mail é guardado em minúsculas, e entrar com outra caixa funciona', async () => {
  const c = await subir()
  try {
    const criado = await c.pedir('POST', '/contas',
      { email: '  Maiuscula@Exemplo.TEST ', senha: SENHA_DE_TESTE }, semToken)
    assert.equal(criado.status, 201)
    assert.equal(criado.corpo.usuario.email, 'maiuscula@exemplo.test')

    const entrou = await c.pedir('POST', '/sessoes',
      { email: 'MAIUSCULA@exemplo.test', senha: SENHA_DE_TESTE }, semToken)
    assert.equal(entrou.status, 200, 'quem digita com outra caixa é a mesma pessoa')
  } finally {
    await c.fechar()
  }
})

test('e-mail repetido é 409, não 500', async () => {
  const c = await subir()
  try {
    const r = await c.pedir('POST', '/contas',
      { email: 'jogador@exemplo.test', senha: SENHA_DE_TESTE }, semToken)
    assert.equal(r.status, 409)
    assert.equal(r.corpo.erro, 'email_ja_usado')
  } finally {
    await c.fechar()
  }
})

test('senha curta e e-mail sem arroba são recusados', async () => {
  const c = await subir()
  try {
    const curta = await c.pedir('POST', '/contas',
      { email: 'x@y.test', senha: 'curta' }, semToken)
    assert.equal(curta.status, 400)
    const semArroba = await c.pedir('POST', '/contas',
      { email: 'sem-arroba', senha: SENHA_DE_TESTE }, semToken)
    assert.equal(semArroba.status, 400)
  } finally {
    await c.fechar()
  }
})

// -------------------------------------------------------------------- sessão

test('senha errada e e-mail inexistente respondem a MESMA coisa', async () => {
  // Se "essa conta não existe" fosse diferente de "senha errada", a rota viraria um
  // jeito de descobrir quais e-mails estão cadastrados.
  const c = await subir()
  try {
    const senhaErrada = await c.pedir('POST', '/sessoes',
      { email: 'jogador@exemplo.test', senha: 'outra senha longa' }, semToken)
    const naoExiste = await c.pedir('POST', '/sessoes',
      { email: 'ninguem@exemplo.test', senha: SENHA_DE_TESTE }, semToken)
    assert.equal(senhaErrada.status, 401)
    assert.equal(naoExiste.status, 401)
    assert.deepEqual(senhaErrada.corpo, naoExiste.corpo, 'as duas respostas têm de ser iguais')
  } finally {
    await c.fechar()
  }
})

test('sem token, com token forjado e com token expirado: 401', async () => {
  const c = await subir()
  try {
    assert.equal((await c.pedir('GET', '/personagens', undefined, semToken)).status, 401)

    // assinado com outro segredo
    const forjado = criarToken(c.usuario.id, 'segredo-de-outra-pessoa', 1)
    assert.equal(
      (await c.pedir('GET', '/personagens', undefined, { authorization: `Bearer ${forjado}` })).status,
      401,
    )

    // válido, mas vencido
    const vencido = criarToken(c.usuario.id, SEGREDO_DE_TESTE, -1)
    assert.equal(
      (await c.pedir('GET', '/personagens', undefined, { authorization: `Bearer ${vencido}` })).status,
      401,
    )
  } finally {
    await c.fechar()
  }
})

// ---------------------------------------------------------------- isolamento

test('o personagem de uma pessoa não aparece para outra', async () => {
  const c = await subir()
  try {
    const meu = await c.pedir('POST', '/personagens',
      { nome: 'Kaida', construcao: ouro('monge-1').construcao })
    assert.equal(meu.status, 201)

    const outro = await c.outroUsuario()
    const comOutro = { authorization: `Bearer ${outro.token}` }

    const lista = await c.pedir('GET', '/personagens', undefined, comOutro)
    assert.equal(lista.status, 200)
    assert.equal(lista.corpo.itens.length, 0, 'a lista do outro tem de vir vazia')

    // E ler pelo id direto: 404, NÃO 403. Um 403 confirmaria que o id existe.
    const lido = await c.pedir('GET', `/personagens/${meu.corpo.id}`, undefined, comOutro)
    assert.equal(lido.status, 404)
  } finally {
    await c.fechar()
  }
})

test('outra pessoa não altera, não sobe de nível e não apaga o meu personagem', async () => {
  const c = await subir()
  try {
    const meu = await c.pedir('POST', '/personagens',
      { nome: 'Kaida', construcao: ouro('monge-1').construcao })
    const id = meu.corpo.id as string
    const outro = await c.outroUsuario()
    const comOutro = { authorization: `Bearer ${outro.token}` }

    const tentativas = [
      await c.pedir('PATCH', `/personagens/${id}/estado`, { pontos_de_vida_atuais: 1 }, comOutro),
      await c.pedir('POST', `/personagens/${id}/subir-nivel`, {}, comOutro),
      await c.pedir('POST', `/personagens/${id}/escolhas`, { escolhas: {} }, comOutro),
      await c.pedir('DELETE', `/personagens/${id}`, undefined, comOutro),
    ]
    for (const r of tentativas) assert.equal(r.status, 404, 'nenhuma pode passar')

    // e o meu continua lá, inteiro
    const ainda = await c.pedir('GET', `/personagens/${id}`)
    assert.equal(ainda.status, 200)
    assert.equal(ainda.corpo.nome, 'Kaida')
  } finally {
    await c.fechar()
  }
})

test('cada um vê os seus, e só os seus', async () => {
  const c = await subir()
  try {
    await c.pedir('POST', '/personagens', { nome: 'Meu', construcao: ouro('monge-1').construcao })
    const outro = await c.outroUsuario()
    const comOutro = { authorization: `Bearer ${outro.token}` }
    await c.pedir('POST', '/personagens',
      { nome: 'Dele', construcao: ouro('monge-1').construcao }, comOutro)

    const minha = await c.pedir('GET', '/personagens')
    const dele = await c.pedir('GET', '/personagens', undefined, comOutro)
    assert.deepEqual(minha.corpo.itens.map((i: { nome: string }) => i.nome), ['Meu'])
    assert.deepEqual(dele.corpo.itens.map((i: { nome: string }) => i.nome), ['Dele'])
  } finally {
    await c.fechar()
  }
})

// ------------------------------------------------------- as peças, sem servidor

test('o hash da senha muda a cada vez, e ainda assim confere', () => {
  // Sal por usuário: duas pessoas com a mesma senha não podem ter o mesmo hash,
  // senão descobrir uma descobre a outra.
  const a = hashDeSenha('a mesma senha longa')
  const b = hashDeSenha('a mesma senha longa')
  assert.notEqual(a, b, 'sem sal, hashes iguais entregariam senhas iguais')
  assert.ok(senhaConfere('a mesma senha longa', a))
  assert.ok(senhaConfere('a mesma senha longa', b))
  assert.ok(!senhaConfere('a mesma senha longa!', a))
})

test('hash corrompido não confere e não explode', () => {
  for (const ruim of ['', 'lixo', 'scrypt$1$2$3', 'bcrypt$1$1$1$aa$bb']) {
    assert.equal(senhaConfere('a mesma senha longa', ruim), false, `'${ruim}'`)
  }
})

test('token só vale com o segredo certo, e caduca', () => {
  const t = criarToken('u1', SEGREDO_DE_TESTE, 1)
  assert.equal(lerToken(t, SEGREDO_DE_TESTE), 'u1')
  assert.equal(lerToken(t, 'outro segredo'), undefined)
  assert.equal(lerToken(criarToken('u1', SEGREDO_DE_TESTE, -1), SEGREDO_DE_TESTE), undefined)

  // mexer no conteúdo invalida a assinatura
  const [corpo, assinatura] = t.split('.')
  const outroCorpo = Buffer.from(JSON.stringify({ u: 'u2', exp: Date.now() + 3600_000 }))
    .toString('base64url')
  assert.equal(lerToken(`${outroCorpo}.${assinatura}`, SEGREDO_DE_TESTE), undefined)
})

test('token malformado é undefined, nunca exceção', () => {
  for (const t of ['', '.', 'sem-ponto', 'a.b', '....', 'YWJj.YWJj']) {
    assert.equal(lerToken(t, SEGREDO_DE_TESTE), undefined, `'${t}'`)
  }
})

test('normalizarEmail apara espaço e baixa a caixa', () => {
  assert.equal(normalizarEmail('  Joao@Exemplo.TEST  '), 'joao@exemplo.test')
  assert.throws(() => normalizarEmail('sem arroba'))
  assert.throws(() => normalizarEmail(42))
})
