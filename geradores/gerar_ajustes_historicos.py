# -*- coding: utf-8 -*-
"""Correções que foram aplicadas à mão e nunca viraram gerador.

Durante as fases 2 a 9, várias decisões já registradas nos `revisao-fase*.md` foram
gravadas editando o JSON direto, sem passar por gerador. Elas não apareciam em lugar
nenhum como código, então a reconstrução do dataset não as reproduzia — e a regra
central do projeto ("o gerador é a fonte") estava valendo só no papel.

A auditoria de 2026-09-02 achou o buraco comparando `dados/` com uma reconstrução
limpa. Este script fecha: os dados corrigidos vivem em `ajustes_historicos.json`,
ao lado, e são aplicados por cima da saída dos geradores.

O que há aqui, por origem:

- **`tipos_de_efeito`**: 28 tipos sem o campo `nome` e 5 tipos nunca declarados
  (`expandir_opcoes_de_escolha`, `alterar_alvos_da_magia`, `substituir_ataque_por_magia`,
  `alterar_quantidade_de_escolha`, `declara_campo_no_item`). Os cinco eram USADOS por
  características desde a fase 7, sem estar no catálogo.
- **`alvos`** e **`alvos_de_impedimento`**: 5 alvos idem.
- **`magias`**: quatro entradas espúrias do parser (`de_jallarzi`, `de_tasha`, `e_o_mal`,
  `o_mal`) — nomes que quebraram de linha e viraram magia. Mais 24 entradas com
  `aprimoramento`, `nota` e `nomes_alternativos` revisados à mão (fases 6 e 8).
- **`caracteristicas`/`classes`/`subclasses`**: o desdobramento do Golpe Brutal Fortalecido
  em `_13` e `_17`, o Prodígio Maior, e correções pontuais de nome e efeito.
- **`itens`**, **`ferramentas`**, **`manobras`**, **`talentos`**, **`efeitos_de_golpe_astuto`**:
  correções de valor pontuais.
- **`listas_de_magia`**: os totais por classe, que a fase 6 reconciliou contra o capítulo 7.
  Estes NÃO são aplicados às cegas: são recalculados a partir de `magias.json` e conferidos
  contra o valor gravado. Se divergirem, o script falha em vez de gravar número errado.

Cada linha aqui é dívida paga, não decisão nova. Quando um destes voltar a ser tocado, o
certo é migrar a correção para o gerador de origem e tirá-la daqui. Ver BACKLOG B1.
"""
import collections, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos

AQUI = os.path.dirname(os.path.abspath(__file__))
PATCHES = os.path.join(AQUI, 'ajustes_historicos.json')


def carregar(rel):
    return json.load(open(os.path.join(caminhos.DADOS, rel), encoding='utf-8'),
                     object_pairs_hook=collections.OrderedDict)


def gravar(rel, d):
    json.dump(d, open(os.path.join(caminhos.DADOS, rel), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def conferir_listas_de_magia(substituicoes):
    """As contagens saem do próprio catálogo de magias — aqui só se confere."""
    magias = carregar('catalogos/magias.json')['itens']
    por_lista = collections.Counter(l for m in magias for l in m.get('listas', []))
    por_circulo = collections.defaultdict(collections.Counter)
    for m in magias:
        for l in m.get('listas', []):
            por_circulo[l][str(m['nivel'])] += 1
    for lid, item in substituicoes.items():
        esperado = por_lista.get(lid, 0)
        if item.get('total_de_magias') != esperado:
            raise SystemExit(
                f"[ajustes históricos] lista '{lid}': o patch diz {item.get('total_de_magias')} "
                f"magias, mas o catálogo tem {esperado}. Recalcule antes de gravar.")
        if 'por_circulo' in item and item['por_circulo'] != dict(por_circulo[lid]):
            raise SystemExit(
                f"[ajustes históricos] lista '{lid}': 'por_circulo' não bate com o catálogo.")
    return len(substituicoes)


def main():
    patches = json.load(open(PATCHES, encoding='utf-8'),
                        object_pairs_hook=collections.OrderedDict)
    resumo = []
    for rel, patch in patches.items():
        d = carregar(rel)
        remover = set(patch.get('remover', []))
        substituir = patch.get('substituir', {})
        itens = []
        for i in d['itens']:
            if i['id'] in remover:
                continue
            itens.append(substituir.get(i['id'], i))
        itens += patch.get('acrescentar', [])
        # A ordem dos itens é parte da saída: sem fixá-la, cada reconstrução produz um
        # arquivo equivalente mas com as linhas em lugar diferente, e o `git diff` de um
        # lote vira ruído. A ordem gravada é a do dataset revisado.
        ordem = patch.get('ordem')
        if ordem:
            posicao = {i: n for n, i in enumerate(ordem)}
            itens.sort(key=lambda i: posicao.get(i['id'], len(posicao)))
        d['itens'] = itens
        if 'total' in d:
            d['total'] = len(itens)
        # Campos de cabeçalho que também eram mantidos à mão: a nota de contagem do
        # catálogo de magias, a fonte de `tipos_de_efeito`, a lista de operações de
        # `valores_derivados`.
        for chave, valor in (patch.get('cabecalho') or {}).items():
            d[chave] = valor
        gravar(rel, d)
        resumo.append(f"{os.path.basename(rel)}: "
                      f"+{len(patch.get('acrescentar', []))} "
                      f"-{len(remover)} ~{len(substituir)}")
    # A conferência das listas vem DEPOIS de o catálogo de magias já estar corrigido:
    # é ele que define a contagem, e o patch dele remove as quatro entradas espúrias
    # do parser. Conferir antes daria o número errado — e deu, na primeira execução.
    if 'catalogos/listas_de_magia.json' in patches:
        conferir_listas_de_magia(patches['catalogos/listas_de_magia.json'].get('substituir', {}))
    print("ajustes históricos aplicados — " + " | ".join(resumo))


if __name__ == '__main__':
    main()
