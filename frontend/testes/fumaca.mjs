// Teste de fumaça: o app inteiro, num navegador de verdade, contra o backend de verdade.
//
// Não é teste de unidade e não tenta ser: é a pergunta "isto funciona ponta a ponta?",
// que nenhum teste de componente responde. Ele percorre o caminho que o João vai
// percorrer — criar conta, criar personagem, responder escolha, marcar dano, ver o
// histórico, sair e voltar — e falha se qualquer passo não acontecer na tela.
//
// Sobe backend e frontend sozinho, em portas próprias, com armazém em arquivo num
// diretório temporário. Não toca em Mongo nem em dado de ninguém.
//
//     node testes/fumaca.mjs
//
// A saída é uma linha por passo. Qualquer passo que falhe derruba o processo com o
// que estava na tela no momento, que é o que faz a falha ser diagnosticável.

import { spawn } from 'node:child_process'
import { mkdtempSync, readdirSync, rmSync } from 'node:fs'
import { homedir, tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { existsSync } from 'node:fs'

let chromium
try {
  ;({ chromium } = await import('playwright'))
} catch {
  console.log('fumaça: playwright não instalado — pulando (npm install para rodar)')
  process.exit(0)
}

const AQUI = dirname(fileURLToPath(import.meta.url))
const RAIZ = join(AQUI, '..')
/**
 * Onde procurar um navegador.
 *
 * A primeira versão olhava um caminho só — o do contêiner em que ela foi escrita —,
 * então em qualquer outra máquina o teste se pulava dizendo que faltava instalar,
 * mesmo com o Chrome ali instalado. Agora varre os lugares usuais e aceita
 * `CHROME=` para o caso que a lista não cobrir.
 */
function acharNavegador() {
  if (process.env.CHROME) return process.env.CHROME
  const candidatos = [
    // o que `npx playwright install chromium` deixa, em qualquer versão
    ...buscarPlaywright(),
    '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/microsoft-edge',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  ]
  return candidatos.find((c) => existsSync(c)) ?? candidatos[candidatos.length - 1]
}

/** O cache do Playwright guarda por versão: `chromium-1194/`, `chromium-1201/`… */
function buscarPlaywright() {
  const raizes = [
    process.env.PLAYWRIGHT_BROWSERS_PATH,
    join(homedir(), '.cache', 'ms-playwright'),
    join(homedir(), 'Library', 'Caches', 'ms-playwright'),
    join(process.env.LOCALAPPDATA ?? '', 'ms-playwright'),
    '/opt/pw-browsers',
  ].filter(Boolean)
  const achados = []
  for (const raiz of raizes) {
    if (!existsSync(raiz)) continue
    for (const nome of readdirSync(raiz)) {
      if (!nome.startsWith('chromium')) continue
      achados.push(
        join(raiz, nome, 'chrome-linux', 'chrome'),
        join(raiz, nome, 'chrome-mac', 'Chromium.app', 'Contents', 'MacOS', 'Chromium'),
        join(raiz, nome, 'chrome-win', 'chrome.exe'),
      )
    }
  }
  return achados
}

const CHROME = acharNavegador()
const PORTA_BACK = 8899
const PORTA_FRONT = 5199

// Sem navegador, PULA em vez de fingir que passou — a mesma regra dos testes que
// precisam de Mongo. Um teste que só roda em uma máquina não protege as outras, mas
// um teste que mente é pior.
if (!existsSync(CHROME)) {
  console.log('fumaça: nenhum navegador encontrado — pulando.')
  console.log('  procurei no cache do Playwright e nos caminhos usuais de Chrome/Chromium.')
  console.log('  para rodar: npx playwright install chromium — ou CHROME=/caminho/do/chrome')
  process.exit(0)
}

const dados = mkdtempSync(join(tmpdir(), 'ficha-facil-fumaca-'))
const processos = []
let passos = 0

const passo = (t) => { passos++; console.log(`  ${passos}. ${t}`) }

function subir(nome, comando, argumentos, ambiente, pronto) {
  const p = spawn(comando, argumentos, {
    cwd: RAIZ,
    env: { ...process.env, ...ambiente },
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  processos.push(p)
  return new Promise((resolve, reject) => {
    const prazo = setTimeout(() => reject(new Error(`${nome} não subiu em 60s`)), 60_000)
    const olhar = (b) => {
      const texto = String(b)
      if (process.env.VERBOSO) process.stdout.write(`[${nome}] ${texto}`)
      if (pronto.test(texto)) { clearTimeout(prazo); resolve() }
    }
    p.stdout.on('data', olhar)
    p.stderr.on('data', olhar)
    p.on('exit', (c) => reject(new Error(`${nome} morreu com código ${c}`)))
  })
}

function encerrar() {
  for (const p of processos) { try { p.kill('SIGKILL') } catch { /* já morreu */ } }
  rmSync(dados, { recursive: true, force: true })
}

const email = `fumaca-${Date.now()}@exemplo.test`
const SENHA = 'uma senha bem longa'

try {
  console.log('subindo…')
  await subir('backend', 'node', [join(RAIZ, '..', 'backend', 'src', 'principal.ts')], {
    PORTA: String(PORTA_BACK),
    PERSONAGENS: dados,
    SESSAO_SEGREDO: 'segredo-do-teste-de-fumaca',
    MONGODB_URI: '',
  }, /backend em http/)

  // O binário direto, e não `npx`: o `npx` embrulha o Vite num `sh -c`, e é esse
  // filho que sobrevive ao encerrar e fica segurando a porta. A execução seguinte
  // então falhava com "porta em uso", parecendo defeito do app quando era lixo da
  // anterior. Uma camada a menos é uma camada a menos para vazar.
  await subir('vite', join(RAIZ, 'node_modules', '.bin', 'vite'),
    ['--port', String(PORTA_FRONT), '--strictPort'], {
      BACKEND: `http://localhost:${PORTA_BACK}`,
    }, /Local:\s+http/)

  const navegador = await chromium.launch({ executablePath: CHROME })
  const pagina = await navegador.newPage({ viewport: { width: 390, height: 844 } })
  pagina.on('pageerror', (e) => { throw new Error(`erro de JS na página: ${e.message}`) })
  const base = `http://localhost:${PORTA_FRONT}`

  console.log('percorrendo:')
  await pagina.goto(base)

  // ------------------------------------------------------------------ conta
  await pagina.getByRole('button', { name: 'Criar uma conta' }).click()
  await pagina.getByLabel(/E-mail/).fill(email)
  await pagina.getByLabel(/Senha/).fill(SENHA)
  await pagina.getByRole('button', { name: 'Criar conta' }).click()
  await pagina.getByText('Meus personagens').waitFor({ timeout: 10_000 })
  passo('criou conta e entrou')

  await pagina.getByText('Nenhum personagem ainda', { exact: false }).waitFor()
  passo('lista começa vazia')

  // ------------------------------------------------------------ personagem
  await pagina.getByRole('button', { name: 'Novo' }).click()
  await pagina.getByLabel('Nome').fill('Vesna')
  await pagina.getByLabel('Espécie').selectOption('humano')
  await pagina.getByLabel('Antecedente').selectOption('acolito')
  await pagina.getByLabel('Classe').selectOption('clerigo')
  await pagina.getByRole('button', { name: 'Criar' }).click()
  await pagina.getByRole('heading', { name: 'Vesna' }).waitFor({ timeout: 10_000 })
  passo('criou a Vesna e caiu na ficha dela')

  // ------------------------------------------------------------------ vida
  const pv = pagina.locator('.painel', { hasText: 'Pontos de Vida' })
  const antes = await pv.locator('strong').first().innerText()
  await pv.getByRole('button', { name: 'tirar vida' }).click()
  await pv.locator('strong').first().filter({ hasNotText: antes }).waitFor({ timeout: 5000 })
  const depois = await pv.locator('strong').first().innerText()
  if (antes === depois) throw new Error('o PV não mudou ao marcar dano')
  passo(`marcou dano: ${antes.trim()} → ${depois.trim()}`)

  // ------------------------------------------------------------ histórico
  await pagina.getByRole('button', { name: 'Histórico' }).click()
  await pagina.getByText(/sofreu 1 de dano · PV \d+\/\d+/).waitFor({ timeout: 5000 })
  const linha = await pagina.locator('.historico li').first().innerText()
  passo(`histórico mostra: ${linha.split('\n')[0]}`)

  // -------------------------------------------------------------- escolhas
  //
  // O número de escolhas pendentes muda quando o dataset ganha regra (os idiomas da
  // criação, por exemplo). O teste conta quantas HÁ e cobra que caia uma — o que
  // interessa é responder tirar do checklist, não o total ser 10.
  const quantasEscolhas = async () => {
    const t = await pagina.getByRole('button', { name: /^Escolhas/ }).innerText()
    return Number(/\((\d+)\)/.exec(t)?.[1] ?? 0)
  }
  const antesDeResponder = await quantasEscolhas()
  await pagina.getByRole('button', { name: /^Escolhas/ }).click()
  const pericia = pagina.locator('.painel', { hasText: 'Escolha uma perícia' }).first()

  // A opção é uma LINHA com nome, etiquetas e descrição — não uma pílula com um
  // nome só. O jogador reclamou de escolher no escuro; este passo é o que garante
  // que a descrição está mesmo na tela.
  const opcao = pericia.locator('.opcao', { hasText: 'Percepção' }).first()
  await opcao.waitFor({ timeout: 10_000 })
  const quantas = await pericia.locator('.opcao').count()
  if (quantas < 2) throw new Error('as opções não vieram em coluna')
  // Perícia não tem descrição no dataset; tem atributo, e a etiqueta sai dele.
  await pericia.locator('.opcao .etiquetas').first().waitFor({ timeout: 5000 })
  passo(`opções em coluna e etiquetadas: ${quantas}`)

  await opcao.click()
  await pericia.getByRole('button', { name: 'Confirmar' }).click()
  await pagina.getByRole('button', { name: new RegExp(`^Escolhas \\(${antesDeResponder - 1}\\)$`) })
    .waitFor({ timeout: 10_000 })
  passo(`respondeu uma escolha; o checklist caiu de ${antesDeResponder} para ${antesDeResponder - 1}`)

  // A distribuição do antecedente: dois passos, e o segundo só existe depois do
  // primeiro. É o caso que a tela genérica de "escolha N de uma lista" não cobre.
  const aumento = pagina.locator('.painel', { hasText: 'distribuir o aumento' }).first()
  await aumento.getByRole('button', { name: 'Um em +2 e outro em +1' }).click()
  await aumento.getByLabel('+2 em').selectOption('SAB')
  await aumento.getByLabel('+1 em').selectOption('INT')
  await aumento.getByRole('button', { name: 'Confirmar' }).click()
  await pagina.getByRole('button', { name: new RegExp(`^Escolhas \\(${antesDeResponder - 2}\\)$`) })
    .waitFor({ timeout: 10_000 })
  passo('distribuiu o aumento do antecedente (+2 SAB, +1 INT)')

  // ------------------------------------------------- o Mago: livro e prévia
  // Os dois defeitos que o João achou na mão: o livro de magias não existia como
  // escolha (e por isso não havia o que preparar), e o talento era escolhido antes
  // de se saber o que ele pede.
  await pagina.getByRole('button', { name: '← meus personagens' }).click()
  await pagina.getByRole('button', { name: 'Novo' }).click()
  await pagina.getByLabel('Nome').fill('Nael')
  await pagina.getByLabel('Espécie').selectOption('humano')
  await pagina.getByLabel('Antecedente').selectOption('acolito')
  await pagina.getByLabel('Classe').selectOption('mago')
  await pagina.getByRole('button', { name: 'Criar' }).click()
  await pagina.getByRole('heading', { name: 'Nael' }).waitFor({ timeout: 10_000 })
  await pagina.getByRole('button', { name: /^Escolhas/ }).click()

  const livro = pagina.locator('.painel', { hasText: 'livro de magias' }).first()
  await livro.waitFor({ timeout: 10_000 })
  const magias = await livro.locator('.opcao').count()
  if (magias < 6) throw new Error(`o livro ofereceu ${magias} magias`)
  await livro.locator('.opcao .descricao').first().waitFor({ timeout: 10_000 })
  const recomendadas = await livro.locator('.opcao', { hasText: 'recomendada' }).count()
  passo(`o livro oferece ${magias} magias descritas (${recomendadas} recomendadas)`)

  for (let i = 0; i < 6; i++) await livro.locator('.opcao').nth(i).click()
  await livro.getByRole('button', { name: 'Confirmar' }).click()
  const preparar = pagina.locator('.painel', { hasText: 'Prepare magias' }).first()
  await preparar.locator('.opcao').first().waitFor({ timeout: 10_000 })
  const paraPreparar = await preparar.locator('.opcao').count()
  if (paraPreparar !== 6) throw new Error(`preparar ofereceu ${paraPreparar}, esperado 6`)
  passo('escrito o livro, preparar magias oferece exatamente o que está nele')

  // A prévia: marcar o talento mostra, ali mesmo, o que ele vai pedir.
  const talento = pagina.locator('.painel', { hasText: 'talento' }).first()
  // O rótulo da própria escolha, para reencontrá-la depois de gravar. Procurar por
  // "Iniciado em Magia" não serve mais: desde que as opções avisam "já tem por…",
  // esse texto aparece em qualquer painel de magia que o talento já tenha dado.
  const rotuloDoTalento = await talento.locator('h2').first().innerText()
  await talento.locator('.opcao', { hasText: 'Iniciado em Magia' }).first().click()
  await talento.locator('.aninhado').first().waitFor({ timeout: 10_000 })
  const abre = await talento.locator('.aninhado h2').allInnerTexts()
  passo(`o talento revela o que pede antes de gravar: ${abre.join('; ')}`)

  // E dá para responder tudo ali dentro, numa gravação só. As sub-escolhas que
  // dependem de outra (os truques só existem depois da lista) vão aparecendo à
  // medida que a de cima é respondida — é a prévia rodando de novo.
  const confirmar = talento.getByRole('button', { name: /Confirmar|faltam/ })
  // Uma opção por volta, relendo a tela a cada vez: a prévia refaz o checklist a
  // cada resposta, então o painel de dois cliques atrás pode não existir mais.
  for (let volta = 0; volta < 30 && !(await confirmar.isEnabled()); volta++) {
    const livre = talento
      .locator('.aninhado')
      .locator('.opcao:not([aria-pressed="true"]):not([disabled])')
      .first()
    if (!(await livre.count())) { await pagina.waitForTimeout(400); continue }
    await livre.click().catch(() => {}) // sumiu entre o ver e o clicar: a volta seguinte reencontra
    await pagina.waitForTimeout(250)
  }
  if (!(await confirmar.isEnabled())) {
    throw new Error(`não deu para completar o talento na tela: ${await confirmar.innerText()}`)
  }
  await confirmar.click()
  // Some o painel que oferecia o talento. As sub-escolhas dele continuam legítimas:
  // o que a prévia tinha revelado até o clique foi gravado junto, e o que sobrou
  // virou pendência normal.
  await pagina
    .locator('.painel')
    .filter({ has: pagina.getByRole('heading', { name: rotuloDoTalento, exact: true }) })
    .first().waitFor({ state: 'detached', timeout: 10_000 })
  passo('talento e sub-escolhas gravados de uma vez só')

  // ------------------------------------------------- conjurar, e ver que conjurou
  // As duas queixas do dia 4: "clico em usar num truque e não fala nada" e "quero
  // os números já calculados, não '+ mod SAB'".
  await pagina.getByRole('button', { name: 'Ficha' }).click()
  const painelDeMagias = pagina.locator('.painel', { hasText: 'Magias' }).first()
  await painelDeMagias.locator('.magia').first().waitFor({ timeout: 10_000 })

  const comNumeros = await painelDeMagias.locator('.numeros-de-magia').allInnerTexts()
  const jogaveis = comNumeros.filter((t) => /\d/.test(t))
  if (!jogaveis.length) throw new Error('nenhuma magia trouxe número para jogar')
  passo(`linha de mesa pronta: ${jogaveis[0]}`)

  const truque = painelDeMagias.locator('.magia', { hasText: 'truque' }).first()
  const usar = (await truque.count())
    ? truque.getByRole('button', { name: /^usar/ })
    : painelDeMagias.locator('.magia').first().getByRole('button', { name: /^usar/ })
  await usar.click()
  await pagina.locator('.aviso-de-acao').waitFor({ timeout: 10_000 })
  const feedback = await pagina.locator('.aviso-de-acao').innerText()
  passo(`usar deu resposta na tela: ${feedback}`)

  await pagina.getByRole('button', { name: 'Histórico' }).click()
  await pagina.getByText(/conjurou|lançou o truque/).first().waitFor({ timeout: 10_000 })
  passo('e a linha entrou no histórico')

  // ------------------------------------------------ inventário: pegar e equipar
  // O escudo é o caso que prova a corrente inteira: a tela manda estado, o motor
  // recalcula, e a CA lá em cima muda sem que esta tela saiba o que um escudo faz.
  // O rótulo é exato: 'CA' casaria também com 'CAR' na lista de atributos.
  const numeroDaCA = async () =>
    Number(await pagina.locator('.numero')
      .filter({ has: pagina.locator('.rotulo', { hasText: /^CA$/ }) })
      .locator('.valor').first().innerText())

  await pagina.getByRole('button', { name: 'Ficha' }).click()
  const inventario = pagina.locator('.painel', { hasText: 'Inventário' }).first()
  await inventario.waitFor({ timeout: 10_000 })
  const caAntes = await numeroDaCA()

  await inventario.getByLabel('Adicionar item').fill('escudo')
  await inventario.locator('.opcao', { hasText: 'Escudo' }).first().click()
  const linhaDoEscudo = inventario.locator('.item', { hasText: 'Escudo' }).first()
  await linhaDoEscudo.waitFor({ timeout: 10_000 })
  passo('pegou o escudo: entrou no inventário')

  await linhaDoEscudo.getByRole('button', { name: 'equipar' }).click()
  for (let i = 0; i < 20 && (await numeroDaCA()) === caAntes; i++) {
    await pagina.waitForTimeout(250)
  }
  const caDepois = await numeroDaCA()
  if (caDepois <= caAntes) throw new Error(`a CA não subiu ao equipar: ${caAntes} → ${caDepois}`)
  passo(`equipou e a CA subiu: ${caAntes} → ${caDepois}`)

  // ------------------------------------------------------ perícias e salvaguardas
  await pagina.getByRole('button', { name: 'Detalhes' }).click()
  const pericias = pagina.locator('.painel', { hasText: 'Perícias' }).first()
  await pericias.locator('.linha-de-pericia').first().waitFor({ timeout: 10_000 })
  const quantasPericias = await pericias.locator('.linha-de-pericia').count()
  if (quantasPericias < 18) throw new Error(`só ${quantasPericias} perícias na ficha`)

  const arcanismo = pericias.locator('.linha-de-pericia', { hasText: 'Arcanismo' }).first()
  const valor = await arcanismo.locator('strong').innerText()
  await arcanismo.click()
  const conta = await pericias.locator('.proveniencia').first().innerText()
  passo(`Arcanismo ${valor} — e a conta aparece: ${conta}`)

  const salvas = pagina.locator('.painel', { hasText: 'Salvaguardas' }).first()
  if ((await salvas.locator('.numero').count()) !== 6) throw new Error('faltam salvaguardas')
  passo('as seis salvaguardas na tela')

  // ---------------------------------------------------------------- sessão
  await pagina.getByRole('button', { name: 'Ficha' }).click()
  await pagina.getByRole('button', { name: '← meus personagens' }).click()
  await pagina.getByText('Vesna').click()
  await pagina.getByRole('heading', { name: 'Vesna' }).waitFor({ timeout: 10_000 })
  await pagina.reload()
  await pagina.getByRole('heading', { name: 'Vesna' }).waitFor({ timeout: 10_000 }).catch(async () => {
    await pagina.getByText('Meus personagens').waitFor({ timeout: 5000 })
  })
  passo('recarregou a página e continuou logado')

  await pagina.getByRole('button', { name: 'sair' }).click()
  await pagina.getByRole('button', { name: 'Entrar' }).waitFor({ timeout: 5000 })
  passo('saiu e voltou para o login')

  await pagina.getByLabel(/E-mail/).fill(email)
  await pagina.getByLabel(/Senha/).fill(SENHA)
  await pagina.getByRole('button', { name: 'Entrar' }).click()
  await pagina.getByText('Vesna').waitFor({ timeout: 10_000 })
  passo('entrou de novo e a Vesna continua lá')

  await navegador.close()
  console.log(`\n${passos} de ${passos} passos passaram.`)
  encerrar()
  process.exit(0)
} catch (e) {
  console.error(`\nFALHOU no passo ${passos + 1}: ${e.message}`)
  encerrar()
  process.exit(1)
}
