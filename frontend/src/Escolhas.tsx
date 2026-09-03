// O checklist: o que ainda falta escolher.
//
// **Nenhuma tela conhece classe, espécie ou talento.** O backend manda
// `{ escolha_id, rotulo, quantidade, opcoes, catalogo }` e a tela desenha "escolha N
// destes". Se aparecer aqui um `if (classe === 'clerigo')`, está no lugar errado.
//
// Duas coisas mudaram depois do primeiro uso de verdade (relato do João, 2026-09-03):
//
// 1. **Era um monte de botões com um nome cada.** "Escolha 6 magias" entre 31 pílulas
//    sem alcance, dano ou descrição é escolher no escuro. Agora cada opção é uma
//    linha com nome, as etiquetas que o item tiver (círculo, escola, alcance, dano,
//    duração) e a descrição curta. Nada disso é conhecimento de conteúdo: a tela
//    desenha os CAMPOS que vierem, e um catálogo novo com `descricao_curta` já
//    aparece descrito sem tocar neste arquivo.
//
// 2. **O talento era escolhido antes de se saber o que ele faz.** Iniciado em Magia
//    só revelava que pede lista, atributo e três magias depois de gravado. Agora,
//    marcada a opção, a tela pede uma PRÉVIA ao backend e mostra as escolhas que ela
//    abriria ali mesmo, aninhadas — e o Confirmar grava tudo de uma vez.
//
// **A exceção, e ela é um débito, não um desenho.** O aumento de atributo do
// antecedente não é "escolha N de uma lista": escolhido o modo (`+2 e +1` ou `+1 nos
// três`), ainda falta dizer *quais* atributos sobem. O checklist não declara isso —
// descobrir exige duas consultas ao compêndio. Está feito por DADO, não por id
// chumbado, mas o conserto certo é o motor declarar a forma que espera.

import { useEffect, useState } from 'react'
import {
  api, ATRIBUTOS, lerCatalogo,
  type Atributo, type ItemDoChecklist, type ItemDoCompendio,
} from './api.ts'

type Modo = { id: string; nome: string; aumentos: number[] }
type Antecedente = { id: string; atributos: Atributo[] }

/** O valor que o backend espera para uma escolha. */
export type Valor = string | string[] | { escolhido: string; distribuicao: Record<string, number> }

export function Escolhas({
  itens, antecedente, personagemId, aoResponder,
}: {
  itens: ItemDoChecklist[]
  antecedente: string
  personagemId: string
  aoResponder: (escolhas: Record<string, Valor>) => Promise<void>
}) {
  const [modos, setModos] = useState<Modo[]>([])
  const [atributosDoAntecedente, setAtributos] = useState<Atributo[]>([])

  useEffect(() => {
    void api.get<{ itens: Modo[] }>('/compendio/modos_de_aumento_do_antecedente')
      .then((r) => setModos(r.itens)).catch(() => setModos([]))
  }, [])

  useEffect(() => {
    void api.get<Antecedente>(`/compendio/antecedentes/${antecedente}`)
      .then((a) => setAtributos(a.atributos ?? [])).catch(() => setAtributos([]))
  }, [antecedente])

  if (!itens.length) {
    return <p className="vazio">Nada pendente. Este personagem está completo.</p>
  }

  const idsDosModos = new Set(modos.map((m) => m.id))
  const ehDistribuicao = (i: ItemDoChecklist) =>
    i.opcoes.length > 0 && i.opcoes.every((o) => idsDosModos.has(o.id))

  return (
    <>
      {itens.map((item) =>
        ehDistribuicao(item) ? (
          <Distribuicao
            key={item.escolha_id} item={item} modos={modos}
            permitidos={atributosDoAntecedente} aoResponder={aoResponder}
          />
        ) : (
          <EscolherDaLista
            key={item.escolha_id} item={item} personagemId={personagemId}
            jaNaTela={new Set(itens.map((x) => x.escolha_id))} aoResponder={aoResponder}
          />
        ),
      )}
    </>
  )
}

// ------------------------------------------------------- descrever uma opção

/**
 * As etiquetas de um item, montadas dos campos que ele tiver.
 *
 * Ordem fixa e nenhuma obrigatória: uma magia sai "1º círculo · Evocação · Ação ·
 * 36 metros · 1d4+1 energético"; um talento sai "origem"; uma perícia sai sem
 * etiqueta nenhuma e não fica pior por isso.
 */
function etiquetas(i: ItemDoCompendio): string[] {
  const e: string[] = []
  if (typeof i.nivel === 'number') e.push(i.nivel === 0 ? 'truque' : `${i.nivel}º círculo`)
  if (i.escola) e.push(String(i.escola).replace(/_/g, ' '))
  if (i.categoria) e.push(String(i.categoria).replace(/_/g, ' '))
  if (typeof i.atributo === 'string') e.push(i.atributo)
  if (i.tempo_de_conjuracao?.texto) e.push(i.tempo_de_conjuracao.texto)
  if (i.alcance?.texto) e.push(i.alcance.texto)
  if (i.dano?.formula_dado) {
    const b = i.dano.bonus_fixo ? ` + ${i.dano.bonus_fixo}` : ''
    e.push(`${i.dano.formula_dado}${b} ${String(i.dano.tipo_dano ?? '').replace(/_/g, ' ')}`.trim())
  }
  if (i.duracao?.texto && i.duracao.texto !== 'Instantânea') e.push(i.duracao.texto)
  if (i.concentracao) e.push('concentração')
  if (i.ritual) e.push('ritual')
  if (i.componentes?.texto) e.push(i.componentes.texto)
  return e
}

function Opcao({
  id, nome, detalhe, marcado, recomendada, jaTem, desabilitado, aoClicar,
}: {
  id: string; nome: string; detalhe?: ItemDoCompendio; marcado: boolean
  recomendada: boolean; jaTem?: string; desabilitado: boolean; aoClicar: () => void
}) {
  const tags = detalhe ? etiquetas(detalhe) : []
  return (
    <button
      className="opcao" aria-pressed={marcado} disabled={desabilitado}
      onClick={aoClicar} data-id={id}
    >
      <div className="espalha">
        <strong>{nome}</strong>
        {/* AVISO, não bloqueio: pegar de novo continua permitido — às vezes é
            mesmo o que se quer —, mas gastar as duas escolhas de um talento em
            truques que a classe já dava é um erro que não dá para desfazer. */}
        {jaTem && <span className="marca ja-tem">você já tem</span>}
        {recomendada && !jaTem && <span className="marca reserva">recomendada</span>}
      </div>
      {jaTem && <div className="etiquetas">já vem de: {jaTem}</div>}
      {tags.length > 0 && <div className="etiquetas">{tags.join(' · ')}</div>}
      {detalhe?.descricao_curta && <p className="descricao">{detalhe.descricao_curta}</p>}
    </button>
  )
}

// -------------------------------------------------------- escolher N de uma lista

function EscolherDaLista({
  item, personagemId, jaNaTela, aoResponder, aoMudar,
}: {
  item: ItemDoChecklist
  personagemId: string
  /** Ids que já estão desenhados na página: a prévia não pode repeti-los aqui dentro. */
  jaNaTela: Set<string>
  /** Só a escolha de cima grava. */
  aoResponder?: (e: Record<string, Valor>) => Promise<void>
  /** Só a escolha aninhada reporta para cima, a cada mudança. */
  aoMudar?: (id: string, valor?: Valor) => void
}) {
  const aninhado = !aoResponder
  const [marcados, setMarcados] = useState<string[]>([])
  const [detalhes, setDetalhes] = useState<Map<string, ItemDoCompendio>>()
  const [ocupado, setOcupado] = useState(false)
  // O que esta escolha abriria, se confirmada — vem da prévia, que não grava nada.
  const [abrem, setAbrem] = useState<ItemDoChecklist[]>([])
  const [respostasFilhas, setRespostasFilhas] = useState<Record<string, Valor>>({})
  const completo = marcados.length === item.quantidade

  useEffect(() => {
    if (!item.catalogo) return
    let vivo = true
    void lerCatalogo(item.catalogo)
      .then((m) => { if (vivo) setDetalhes(m) })
      .catch(() => { if (vivo) setDetalhes(new Map()) })
    return () => { vivo = false }
  }, [item.catalogo])

  // Trocar a opção marcada joga fora as respostas das filhas: elas pertenciam ao
  // talento anterior. Fica separado da prévia de propósito — a prévia roda de novo
  // a cada resposta de filha, e limpar ali seria apagar o que o jogador acabou de
  // responder, em laço.
  useEffect(() => { setRespostasFilhas({}) }, [marcados.join('|')])

  // Marcado o suficiente, pergunta ao backend o que isso abriria. É a prévia que
  // torna possível escolher o talento SABENDO o que ele pede — antes, a única forma
  // de descobrir era gravar e ver.
  //
  // As respostas das filhas entram no pedido porque escolha depende de escolha: os
  // truques do Iniciado em Magia só existem depois da lista. Sem isto o jogador via
  // "depende de iniciado_em_magia_lista" e não tinha como sair do lugar.
  useEffect(() => {
    if (!completo || aninhado) { setAbrem([]); return }
    let vivo = true
    void api
      .post<{ checklist: ItemDoChecklist[] }>(`/personagens/${personagemId}/escolhas/previa`, {
        escolhas: { [item.escolha_id]: valorDe(item, marcados), ...respostasFilhas },
      })
      .then((r) => {
        if (!vivo) return
        // A prévia devolve o checklist INTEIRO; o que interessa aqui é só o que
        // apareceu por causa desta escolha — e o que as filhas já responderam sai
        // sozinho, porque escolha respondida não é pendência.
        setAbrem(r.checklist.filter((c) => !jaNaTela.has(c.escolha_id)))
      })
      .catch(() => { if (vivo) setAbrem([]) })
    return () => { vivo = false }
    // `marcados` e as respostas entram por valor: mudar qualquer um muda a prévia.
  }, [completo, marcados.join('|'), JSON.stringify(respostasFilhas), item.escolha_id,
      personagemId, aninhado])

  // A aninhada não grava: ela avisa a de cima a cada mudança, e a de cima grava tudo
  // de uma vez. Assim o jogador vê talento e sub-escolhas como uma decisão só.
  useEffect(() => {
    if (aninhado) aoMudar?.(item.escolha_id, completo ? valorDe(item, marcados) : undefined)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [marcados.join('|'), completo])

  function alternar(id: string) {
    setMarcados((atual) => {
      if (atual.includes(id)) return atual.filter((x) => x !== id)
      // Escolher de uma só: trocar em vez de bloquear. Obrigar a desmarcar antes é
      // um toque a mais para nada.
      if (item.quantidade === 1) return [id]
      if (atual.length >= item.quantidade) return atual
      return [...atual, id]
    })
  }

  async function confirmar() {
    setOcupado(true)
    try {
      // As filhas vão junto, numa gravação só: o motor confere o conjunto, e o
      // jogador não vê meia escolha aplicada se algo for recusado.
      await aoResponder?.({ [item.escolha_id]: valorDe(item, marcados), ...respostasFilhas })
    } finally {
      setOcupado(false)
    }
  }

  if (item.bloqueada_por) {
    return (
      <div className="painel">
        <h2 style={{ margin: 0 }}>{item.rotulo}</h2>
        <p className="fraco">
          Depende de <strong>{item.bloqueada_por.replace(/_/g, ' ')}</strong>: responda
          aquela escolha primeiro e esta abre com as opções certas.
        </p>
      </div>
    )
  }

  const recomendados = new Set(item.recomendados ?? [])
  const faltamFilhas = abrem.filter((f) => !respostasFilhas[f.escolha_id])

  return (
    <div className={aninhado ? 'aninhado' : 'painel'}>
      <div className="espalha">
        <h2 style={{ margin: 0 }}>{item.rotulo}</h2>
        <span className="fraco">{marcados.length}/{item.quantidade}</span>
      </div>
      {item.origem && !aninhado && (
        <p className="fraco" style={{ margin: '4px 0 10px' }}>de {item.origem}</p>
      )}

      <div className="opcoes">
        {item.opcoes.map((o) => (
          <Opcao
            key={o.id} id={o.id} nome={o.nome} detalhe={detalhes?.get(o.id)}
            marcado={marcados.includes(o.id)} recomendada={recomendados.has(o.id)}
            jaTem={o.ja_tem}
            desabilitado={
              !marcados.includes(o.id) && marcados.length >= item.quantidade && item.quantidade > 1
            }
            aoClicar={() => alternar(o.id)}
          />
        ))}
      </div>

      {/* O que a escolha marcada abre, ali mesmo, antes de gravar. */}
      {abrem.length > 0 && (
        <div className="abre">
          <p className="fraco" style={{ margin: '12px 0 6px' }}>
            Isto também pede:
          </p>
          {abrem.map((f) => (
            <EscolherDaLista
              key={f.escolha_id} item={f} personagemId={personagemId} jaNaTela={jaNaTela}
              aoMudar={(id, valor) =>
                setRespostasFilhas((r) => {
                  const { [id]: _fora, ...resto } = r
                  return valor === undefined ? resto : { ...resto, [id]: valor }
                })}
            />
          ))}
        </div>
      )}

      {!aninhado && (
        <button
          className="principal" style={{ marginTop: 12 }}
          disabled={!completo || ocupado || faltamFilhas.length > 0} onClick={confirmar}
        >
          {ocupado
            ? 'gravando…'
            : faltamFilhas.length
              ? `faltam ${faltamFilhas.length} escolha(s) acima`
              : 'Confirmar'}
        </button>
      )}
    </div>
  )
}

/** Uma escolha de um item manda a string; de várias, a lista. */
function valorDe(item: ItemDoChecklist, marcados: string[]): Valor {
  return item.quantidade === 1 ? marcados[0] : marcados
}

// ------------------------------------------- escolher o modo e distribuir os pontos

function Distribuicao({
  item, modos, permitidos, aoResponder,
}: {
  item: ItemDoChecklist; modos: Modo[]; permitidos: Atributo[]
  aoResponder: (e: Record<string, Valor>) => Promise<void>
}) {
  const [modoId, setModoId] = useState('')
  const [porAtributo, setPorAtributo] = useState<Record<string, string>>({})
  const [ocupado, setOcupado] = useState(false)

  const modo = modos.find((m) => m.id === modoId)
  const lista = permitidos.length ? permitidos : [...ATRIBUTOS]

  // Os incrementos vêm do catálogo (`aumentos: [2, 1]`), não de conta feita aqui:
  // um modo novo no livro passa a funcionar sem tocar nesta tela.
  const aumentos = modo?.aumentos ?? []
  const usados = aumentos.map((quanto, i) => porAtributo[`${i}`] ?? '')
  const completo = !!modo &&
    usados.every((a) => a && lista.includes(a as Atributo)) &&
    new Set(usados).size === usados.length

  async function confirmar() {
    if (!modo) return
    const distribuicao: Record<string, number> = {}
    aumentos.forEach((quanto, i) => { distribuicao[usados[i]] = quanto })
    setOcupado(true)
    try {
      await aoResponder({ [item.escolha_id]: { escolhido: modo.id, distribuicao } })
    } finally {
      setOcupado(false)
    }
  }

  return (
    <div className="painel">
      <h2>{item.rotulo}</h2>
      {item.origem && <p className="fraco" style={{ margin: '4px 0 10px' }}>de {item.origem}</p>}
      <div className="pilulas">
        {item.opcoes.map((o) => (
          <button
            key={o.id} className="pilula" aria-pressed={modoId === o.id}
            onClick={() => { setModoId(o.id); setPorAtributo({}) }}
          >
            {o.nome}
          </button>
        ))}
      </div>

      {modo && (
        <div style={{ marginTop: 12 }}>
          {aumentos.map((quanto, i) => (
            <label key={i}>
              <span>+{quanto} em</span>
              <select
                value={porAtributo[`${i}`] ?? ''}
                onChange={(e) => setPorAtributo({ ...porAtributo, [`${i}`]: e.target.value })}
              >
                <option value="">escolha…</option>
                {lista.map((a) => (
                  <option
                    key={a} value={a}
                    // O mesmo atributo não pode receber dois aumentos do mesmo modo.
                    disabled={usados.includes(a) && porAtributo[`${i}`] !== a}
                  >
                    {a}
                  </option>
                ))}
              </select>
            </label>
          ))}
        </div>
      )}

      <button className="principal" disabled={!completo || ocupado} onClick={confirmar}>
        {ocupado ? 'gravando…' : 'Confirmar'}
      </button>
    </div>
  )
}
