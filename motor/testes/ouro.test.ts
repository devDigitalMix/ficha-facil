// Personagens de ouro: fichas montadas à mão, conferidas contra o livro, que o
// motor tem de acertar. Escritas ANTES do motor, de propósito — a mesma ideia dos
// testes negativos do dataset: o alvo existe antes do código.
//
// Desde o passo 3 o caminho é inteiro: sai da CONSTRUÇÃO (o que o jogador
// escolheu), coleta os efeitos do dataset, monta o contexto e calcula a ficha.
// Nada aqui é escrito à mão além da construção e do que se espera.
//
// O que cada golden prova está no campo `por_que_existe` do próprio JSON.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { coletar, type Construcao } from '../src/colecao.ts'
import { montarContexto, type Estado } from '../src/contexto.ts'
import { montarFicha, testeDePericia } from '../src/ficha.ts'
import { opcoesDe } from '../src/escolha.ts'
import { catalogo, vocabularioDeRuntime } from '../src/dataset.ts'

const AQUI = dirname(fileURLToPath(import.meta.url))
const OURO = join(AQUI, '..', 'ouro')

const VOCAB = vocabularioDeRuntime()
const PERICIAS = new Map(
  catalogo<{ id: string; atributo: string }>('pericias').itens.map((p) => [p.id, p.atributo]),
)

type Golden = {
  id: string
  nome: string
  construcao: Construcao
  estado?: Estado
  estado_sem_furia?: Estado
  esperado: Record<string, any>
}

export function fichaDe(g: Golden, estado: Estado = {}) {
  const col = coletar(g.construcao)
  const equipado = g.construcao.equipamento_equipado ?? []
  const { contexto, nao_consumidos } = montarContexto(
    col,
    g.construcao.atributos_base,
    estado,
    VOCAB,
    equipado,
  )
  return { col, contexto, nao_consumidos, ficha: montarFicha(contexto, VOCAB, equipado) }
}

const goldens: Golden[] = readdirSync(OURO)
  .filter((f) => f.endsWith('.json'))
  .map((f) => JSON.parse(readFileSync(join(OURO, f), 'utf-8')) as Golden)

test('há personagens de ouro para conferir', () => {
  assert.ok(goldens.length >= 2, 'o motor precisa de mais de uma ficha de referência')
})

for (const g of goldens) {
  test(`ouro: ${g.nome}`, () => {
    const estado = g.estado ?? g.estado_sem_furia ?? {}
    const { col, contexto, ficha } = fichaDe(g, estado)
    const e = g.esperado

    assert.deepEqual(ficha.modificadores, e.modificadores, 'modificadores de atributo')
    assert.equal(ficha.bonus_de_proficiencia, e.bonus_de_proficiencia, 'Bônus de Proficiência')

    assert.equal(
      ficha.classe_de_armadura.valor,
      e.classe_de_armadura.valor,
      `CA — esperado ${e.classe_de_armadura.proveniencia}`,
    )
    const usado = ficha.classe_de_armadura.parcelas.find(
      (p) => p.rotulo === 'cálculo de base usado',
    )
    assert.equal(
      usado?.valor,
      e.classe_de_armadura.calculo_de_base_usado,
      'o cálculo de CA base escolhido — os concorrentes não se somam',
    )

    assert.equal(
      ficha.pontos_de_vida_maximos.valor,
      e.pontos_de_vida_maximos.valor,
      `PV máximos — esperado ${e.pontos_de_vida_maximos.proveniencia}`,
    )

    assert.equal(ficha.iniciativa.valor, e.iniciativa.valor, 'Iniciativa')
    assert.deepEqual(
      ficha.iniciativa.dados,
      e.iniciativa.dados,
      'a Iniciativa sai com o d20 simbólico: o motor não joga dado',
    )

    assert.equal(ficha.percepcao_passiva.valor, e.percepcao_passiva.valor, 'Percepção Passiva')
    assert.deepEqual(ficha.salvaguardas, e.salvaguardas, 'salvaguardas')
    assert.equal(ficha.deslocamento_m, e.deslocamento_m, 'Deslocamento')

    for (const [pericia, esperado] of Object.entries(
      e.testes_de_pericia as Record<string, number>,
    )) {
      const atributo = PERICIAS.get(pericia)
      assert.ok(atributo, `perícia inexistente no catálogo: '${pericia}'`)
      assert.equal(testeDePericia(contexto, pericia, atributo), esperado, `teste de ${pericia}`)
    }

    // O checklist de subir de nível nasce aqui: escolha não resolvida é pendência,
    // não erro, e a lista tem de bater exatamente.
    assert.deepEqual(
      col.pendencias.map((p) => p.escolha_id).sort(),
      [...(e.escolhas_em_aberto as string[])].sort(),
      'escolhas em aberto',
    )

    // --- ataques: o Ataque Desarmado sempre, e as armas equipadas
    if (e.ataques) {
      for (const esperado of e.ataques as Record<string, any>[]) {
        const a = ficha.ataques.find((x) => x.arma === esperado.arma)
        assert.ok(a, `a ficha não trouxe o ataque '${esperado.arma}'`)
        assert.equal(a.jogada.valor, esperado.jogada, `${esperado.arma} — ${esperado.proveniencia}`)
        assert.equal(a.dano.valor, esperado.dano_valor, `${esperado.arma}: dano`)
        assert.deepEqual(a.dano.dados, esperado.dano_dados, `${esperado.arma}: dado de dano`)
        assert.equal(a.atributo, esperado.atributo, `${esperado.arma}: atributo`)
        assert.equal(a.proficiente, esperado.proficiente, `${esperado.arma}: proficiência`)
      }
    }

    // --- conjuração, para quem conjura
    if (e.conjuracao) {
      const c = ficha.conjuracao
      assert.ok(c, 'a ficha tem de trazer a parte de magia')
      assert.equal(c.atributo, e.conjuracao.atributo, 'atributo de conjuração')
      assert.equal(
        c.cd_para_evitar_sua_magia.valor,
        e.conjuracao.cd_para_evitar_sua_magia,
        `CD — esperado ${e.conjuracao.proveniencia_da_cd}`,
      )
      assert.equal(c.jogada_de_ataque_magico.valor, e.conjuracao.jogada_de_ataque_magico)
      assert.deepEqual(
        Object.fromEntries(Object.entries(c.espacos).map(([k, v]) => [String(k), v])),
        e.conjuracao.espacos,
        'espaços por círculo',
      )
      assert.equal(c.magias_preparadas, e.conjuracao.magias_preparadas)
      assert.equal(c.truques, e.conjuracao.truques)
    } else {
      assert.equal(ficha.conjuracao, undefined, 'quem não conjura não tem linha de magia')
    }

    // --- o que a escolha de preparar magias oferece
    //
    // A conta importa: sem o filtro "de um círculo para o qual você possui espaços"
    // a Clériga de nível 5 veria as 108 magias da lista, inclusive as de 9º círculo.
    // Asserção sobre a quantidade exata, e não sobre "menos que a lista toda":
    // é o número que muda quando o filtro para de funcionar.
    if (e.opcoes_para_preparar) {
      const escolha = col.escolhas.get('clerigo_preparadas')
      assert.ok(escolha, 'a Clériga prepara magias')
      const of = opcoesDe(escolha.efeito, contexto)
      assert.equal(
        of.opcoes.length,
        e.opcoes_para_preparar.quantidade,
        e.opcoes_para_preparar.nota,
      )
      assert.deepEqual(of.nao_avaliados, [], 'o filtro do círculo tem de ser avaliado')
    }

    // --- os atributos finais, depois de todos os aumentos
    if (e.atributos_finais) {
      assert.deepEqual(
        contexto.atributos,
        e.atributos_finais,
        `atributos — esperado ${e.proveniencia_dos_atributos}`,
      )
    }
  })
}

// A Fúria é o caso em que o MESMO personagem tem duas fichas. Sem isto, um motor
// que ignorasse o estado passaria em tudo.
test('ouro: o Bárbaro em Fúria não é o mesmo Bárbaro', () => {
  const g = goldens.find((x) => x.estado_sem_furia)
  assert.ok(g, 'nenhum golden declara estado com e sem Fúria')
  const emFuria = (g as any).estado_em_furia as Estado

  const parado = fichaDe(g, g.estado_sem_furia)
  const furioso = fichaDe(g, emFuria)

  // A asserção precisa ser sobre as PORTAS, não sobre a contagem. Contagem é fraca:
  // com o portão ignorado, o Bárbaro parado ainda ficava com menos efeitos que o
  // furioso — por causa das condições — e o defeito passava. Isto aqui é literal:
  // parado, nenhum efeito atrás de porta pode incidir.
  const atrasDePorta = (r: typeof parado) =>
    r.nao_consumidos.filter((c) => c.portas.length > 0).map((c) => c.portas.join('>'))

  assert.deepEqual(
    atrasDePorta(parado),
    [],
    'fora de Fúria, nenhum efeito de dentro da Fúria pode incidir',
  )
  assert.ok(
    atrasDePorta(furioso).some((p) => p.includes('furia')),
    'em Fúria, os efeitos de dentro dela têm de incidir',
  )
  assert.ok(
    furioso.nao_consumidos.length > parado.nao_consumidos.length,
    'em Fúria têm de incidir MAIS efeitos: resistências, vantagem e dano adicional',
  )
  // e o que não depende da Fúria não pode mudar
  assert.equal(furioso.ficha.classe_de_armadura.valor, parado.ficha.classe_de_armadura.valor)
  assert.equal(furioso.ficha.pontos_de_vida_maximos.valor, parado.ficha.pontos_de_vida_maximos.valor)
})
