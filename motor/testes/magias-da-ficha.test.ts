// A lista de magias da ficha, e as marcas que ela põe nas escolhas.
//
// A queixa que originou este arquivo: "no Mago, as magias que peguei por
// antecedente/talento não aparecem entre as preparáveis — só as da lista da
// classe". Eram dois problemas com o mesmo sintoma:
//
//   1. o efeito `desbloquear_magias` caía em `nao_consumidos` e ninguém o lia, de
//      modo que a magia do talento não existia em NENHUM lugar da ficha;
//   2. a tela de escolha não tinha como avisar que uma opção já era conhecida por
//      outro caminho — e gastar as duas escolhas do Iniciado em Magia em truques
//      que a classe já dava é um erro que não dá para desfazer.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { montar } from '../src/motor.ts'
import { catalogo, lerJson } from '../src/dataset.ts'

const OURO = join(dirname(fileURLToPath(import.meta.url)), '..', 'ouro')

/** A Clériga de ouro tem Iniciado em Magia pelo antecedente: é o caso da queixa. */
function clerigaDeOuro() {
  return JSON.parse(readFileSync(join(OURO, 'clerigo-5.json'), 'utf8')).construcao
}

test('a magia vinda do talento aparece na ficha, e não só as da classe', () => {
  const magias = montar(clerigaDeOuro()).ficha!.magias
  const doTalento = magias.filter((m) => m.origem.includes('Iniciado em Magia'))
  assert.ok(
    doTalento.length >= 3,
    `esperava os dois truques e a magia de 1º círculo do talento; vieram ${doTalento.length}`,
  )
  assert.ok(
    magias.some((m) => m.origem.includes('Conjuração')),
    'as da classe continuam lá — o conserto não pode ter trocado uma fonte pela outra',
  )
})

test('cada magia diz de onde veio, com nome e não com id', () => {
  for (const m of montar(clerigaDeOuro()).ficha!.magias) {
    assert.ok(
      !/[a-z]_[a-z]/.test(m.origem),
      `origem com id cru em vez de nome: '${m.origem}' (magia ${m.id})`,
    )
    assert.ok(m.nome && m.nome !== m.id, `magia sem nome legível: '${m.id}'`)
    assert.equal(typeof m.circulo, 'number')
  }
})

test('a magia sempre preparada do talento não ocupa vaga de preparação', () => {
  const magias = montar(clerigaDeOuro()).ficha!.magias
  const sempre = magias.find((m) => m.modo === 'sempre_preparada')
  assert.ok(sempre, 'o Iniciado em Magia dá uma magia de 1º círculo sempre preparada')
  assert.equal(sempre!.nao_conta_para_o_limite, true)
  assert.equal(sempre!.pronta_para_conjurar, true)
})

test('truque e magia preparada estão prontos; nada mais é prometido', () => {
  for (const m of montar(clerigaDeOuro()).ficha!.magias) {
    if (['conhecida', 'preparada', 'sempre_preparada'].includes(m.modo)) {
      assert.equal(m.pronta_para_conjurar, true, `${m.nome} (${m.modo}) devia estar pronta`)
    } else {
      assert.equal(m.pronta_para_conjurar, false, `${m.nome} (${m.modo}) NÃO está pronta`)
    }
  }
})

test('a escolha avisa quando a opção já vem de outra porta', () => {
  const c = clerigaDeOuro()
  delete c.escolhas['iniciado_em_magia_truques'] // volta ao checklist
  const item = montar(c).checklist.find((i) => i.escolha_id === 'iniciado_em_magia_truques')
  assert.ok(item, 'a escolha esquecida tem de voltar para o checklist')
  const marcadas = item!.opcoes.filter((o) => o.ja_tem)
  assert.ok(marcadas.length > 0, 'a Clériga já tem truques da classe que estão nesta lista')
  for (const o of marcadas) {
    assert.ok(o.ja_tem!.includes('Clérigo'), `marca sem dizer de onde: '${o.ja_tem}'`)
  }
  assert.ok(
    item!.opcoes.length > marcadas.length,
    'marcar não é filtrar: a opção repetida continua escolhível',
  )
})

test('escolha reescolhível não marca as próprias opções como repetidas', () => {
  // As magias que a Clériga preparou vieram de `clerigo_preparadas`. Se a marca não
  // excluísse a própria escolha, a lista voltaria inteira marcada no descanso
  // seguinte — o aviso viraria ruído e ninguém mais o leria.
  const c = clerigaDeOuro()
  delete c.escolhas['clerigo_preparadas']
  const item = montar(c).checklist.find((i) => i.escolha_id === 'clerigo_preparadas')
  assert.ok(item)
  const daPropriaEscolha = item!.opcoes.filter((o) => o.ja_tem?.includes('Conjuração'))
  assert.equal(daPropriaEscolha.length, 0)
})

test('o MESMO talento vindo de duas portas avisa uma sobre a outra', () => {
  // É onde o aviso mais vale: pegar Iniciado em Magia duas vezes e gastar as duas
  // escolhas no mesmo truque é o erro caro. A primeira versão comparava a escolha
  // com a trilha por `includes`, e `iniciado_em_magia_truques` casava com
  // `iniciado_em_magia_truques@humano_versatil` — logo o talento repetido achava
  // que a magia tinha vindo dele mesmo, e não avisava nada.
  const c = {
    especie: 'humano',
    antecedente: 'acolito',
    niveis: [{ classe: 'mago', nivel: 1 }],
    atributos_base: { FOR: 10, DES: 14, CON: 12, INT: 15, SAB: 13, CAR: 8 },
    escolhas: {
      humano_versatil: 'iniciado_em_magia',
      'iniciado_em_magia_truques@humano_versatil': ['luz', 'orientacao'],
    },
  } as unknown as Parameters<typeof montar>[0]

  const item = montar(c).checklist.find((i) => i.escolha_id === 'iniciado_em_magia_truques')
  assert.ok(item, 'o talento do antecedente ainda tem truques a escolher')
  const luz = item!.opcoes.find((o) => o.id === 'luz')
  assert.ok(luz?.ja_tem, 'Luz já veio pelo talento do Humano e o aviso tem de dizer isso')
  assert.match(luz!.ja_tem!, /Vers|Humano/)
})

// -------------------------------------- toda classe que conjura tem bloco de magia

/** As classes que o livro declara conjuradoras, tiradas do próprio dado. */
function classesQueConjuram(): { id: string; atributo: string }[] {
  return (lerJson<{ itens: { id: string; conjuracao?: { atributo: string } }[] }>('classes.json')
    .itens.filter((c) => c.conjuracao)
    .map((c) => ({ id: c.id, atributo: c.conjuracao!.atributo })))
}

test('toda classe conjuradora tem espaços e atributo na ficha, já no nível 1', () => {
  // O Bardo e o Feiticeiro guardavam os espaços como lista numa coluna só, e nenhum
  // dos dois tinha `preparar_magias`: a ficha devolvia `conjuracao: undefined` e o
  // jogador não via CD, ataque mágico nem espaço nenhum. O Bruxo tinha o problema
  // pelo outro lado — a tabela dele é por Pacto, e a ficha só sabia ler
  // `espacos_<n>`. Três classes, dois defeitos, uma pergunta só: quem conjura tem
  // com o que conjurar?
  for (const { id, atributo } of classesQueConjuram()) {
    const r = montar({
      especie: 'humano',
      antecedente: 'acolito',
      niveis: [{ classe: id, nivel: 1 }],
      atributos_base: { FOR: 10, DES: 14, CON: 12, INT: 13, SAB: 13, CAR: 15 },
    } as unknown as Parameters<typeof montar>[0])

    const c = r.ficha!.conjuracao
    assert.ok(c, `${id}: classe conjuradora sem bloco de conjuração na ficha`)
    assert.equal(c!.atributo, atributo, `${id}: atributo de conjuração diferente do livro`)
    assert.ok(
      Object.values(c!.espacos).some((n) => n > 0),
      `${id}: conjurador de nível 1 sem espaço de magia nenhum`,
    )
  }
})

test('quem prepara da lista da classe só vê o círculo que cabe nos espaços', () => {
  // 127 magias de Bardo oferecidas no nível 1 foi a queixa. A causa era o filtro
  // `circulo_com_espaco_disponivel` não achar coluna nenhuma e, honestamente, se
  // declarar `nao_avaliado` — o que não recorta nada.
  for (const { id } of classesQueConjuram()) {
    const r = montar({
      especie: 'humano',
      antecedente: 'acolito',
      niveis: [{ classe: id, nivel: 1 }],
      atributos_base: { FOR: 10, DES: 14, CON: 12, INT: 13, SAB: 13, CAR: 15 },
    } as unknown as Parameters<typeof montar>[0])

    for (const item of r.checklist) {
      if (!item.escolha_id.endsWith('_preparadas')) continue
      assert.ok(
        !item.nao_avaliados.includes('circulo_com_espaco_disponivel'),
        `${id}: o filtro de círculo ficou sem avaliar — a lista sai inteira`,
      )
      const magias = catalogo<{ id: string; nivel: number }>('magias').itens
      for (const o of item.opcoes) {
        const nivel = magias.find((m) => m.id === o.id)!.nivel
        assert.ok(nivel <= 1, `${id}: ofereceu '${o.id}' de ${nivel}º círculo no nível 1`)
      }
    }
  }
})

// -------------------------------------------------- o que custa conjurar cada uma

test('truque não custa nada, e magia comum custa um espaço do círculo dela', () => {
  const c = clerigaDeOuro()
  const ficha = montar(c).ficha!
  for (const m of ficha.magias) {
    if (m.circulo === 0) {
      assert.equal(m.custo.tipo, 'nenhum', `${m.nome}: truque não gasta espaço`)
    } else if (m.custo.tipo === 'espaco') {
      assert.equal(m.custo.circulo_minimo, m.circulo)
    }
  }
})

test('a magia que o talento dá de graça custa o USO dela, não um espaço', () => {
  // A queixa do João: "tem algumas que posso usar uma vez por dia mas não gastam,
  // por exemplo uma magia que peguei de um talento". O talento declarava isso desde
  // sempre (`conjurar_sem_espaco`, p. 201) — mas a magia vinha de OUTRA escolha, e
  // o efeito chegava com `$escolhido_em:iniciado_em_magia_magia_1` no lugar do id.
  const r = montar({
    especie: 'humano',
    antecedente: 'acolito',
    niveis: [{ classe: 'clerigo', nivel: 1 }],
    atributos_base: { FOR: 10, DES: 14, CON: 12, INT: 12, SAB: 15, CAR: 13 },
    escolhas: {
      humano_versatil: 'iniciado_em_magia',
      'iniciado_em_magia_lista@humano_versatil': 'mago',
      'iniciado_em_magia_atributo@humano_versatil': 'INT',
      'iniciado_em_magia_truques@humano_versatil': ['luz', 'raio_de_gelo'],
      'iniciado_em_magia_magia_1@humano_versatil': 'misseis_magicos',
    },
  } as unknown as Parameters<typeof montar>[0])

  const misseis = r.ficha!.magias.find((m) => m.id === 'misseis_magicos')
  assert.ok(misseis, 'a magia do talento tem de estar na ficha')
  assert.equal(misseis!.custo.tipo, 'recurso', 'ela não gasta espaço de magia')
  if (misseis!.custo.tipo !== 'recurso') return
  assert.match(misseis!.custo.porque, /Iniciado em Magia/, 'a ficha diz por que é de graça')
  assert.equal(misseis!.custo.tambem_com_espaco, true, 'o livro deixa gastar espaço também')

  // …e o uso é contável: um recurso de 1, que volta no Descanso Longo.
  const recurso = r.ficha!.recursos.find((x) => x.id === misseis!.custo.recurso_id)
  assert.ok(recurso, 'sem recurso o app não teria o que mostrar nem o que gastar')
  assert.equal(recurso!.maximo, 1)
  assert.deepEqual(recurso!.recarga, [{ gatilho: 'descanso_longo', quantidade: 'todos' }])
})
