# -*- coding: utf-8 -*-
"""Quatro magias estavam com o nome diferente do livro.

Achado na releitura das 391 magias (fase 19). A bancada põe lado a lado o texto do
capítulo 7 e a paráfrase — e quatro magias apareceram **sem texto do livro**. Não
era falta de texto: era o nome não casar.

| no catálogo | no capítulo 7 |
|---|---|
| Benção | **Bênção** (p. 248) |
| Pele-casca | **Pele-Casca** (p. 316) |
| Invocar Morto-vivo | **Invocar Morto-Vivo** (p. 296) |
| Proteção contra Energia | **Proteção Contra Energia** (p. 320) |

De onde veio: `parse_magias.ler_nomes` resolve o nome colado por quebra de coluna
usando a lista de nomes CONHECIDOS, que vem das listas de magia das classes. Quando
a lista da classe imprime com outra caixa ou sem o circunflexo, é a grafia da lista
que ganha — e a entrada do capítulo 7, que é onde a magia é definida, perde.

O efeito prático era pior do que uma letra: essas quatro magias nunca tiveram o
corpo do livro extraído, então nunca passaram por conferência nenhuma. As
paráfrases delas, por sorte, estavam certas — `descricoes_magias.py` já usava a
grafia do livro, e o casamento por id salvou o conteúdo.

O id não muda: ele é normalizado (`bencao`, `pele_casca`) e já estava certo.
"""
import json, collections, sys

MAGIAS = 'dados/catalogos/magias.json'

# id -> (nome errado que estava, nome como o capítulo 7 imprime, página)
CORRECOES = {
    'bencao': ('Benção', 'Bênção', 248),
    'pele_casca': ('Pele-casca', 'Pele-Casca', 316),
    'invocar_morto_vivo': ('Invocar Morto-vivo', 'Invocar Morto-Vivo', 296),
    'protecao_contra_energia': ('Proteção contra Energia', 'Proteção Contra Energia', 320),
}


def main():
    d = json.load(open(MAGIAS, encoding='utf-8'),
                  object_pairs_hook=collections.OrderedDict)
    trocados, ja_certos, faltando = 0, 0, []

    por_id = {i['id']: i for i in d['itens']}
    for iid, (errado, certo, pagina) in CORRECOES.items():
        item = por_id.get(iid)
        if item is None:
            faltando.append(iid)
            continue
        if item['nome'] == certo:
            ja_certos += 1
            continue
        if item['nome'] != errado:
            print("ERRO: '%s' está como '%s'; esperava '%s' ou '%s'"
                  % (iid, item['nome'], errado, certo))
            return 1
        item['nome'] = certo
        item['nota_do_nome'] = (
            "A grafia é a da entrada do capítulo 7, p. %d, que é onde a magia é "
            "definida. A lista de magias da classe imprime diferente, e era ela que "
            "estava ganhando." % pagina
        )
        trocados += 1

    json.dump(d, open(MAGIAS, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    if faltando:
        print('ERRO: id de magia inexistente: %s' % faltando)
        return 1
    print('nomes de magia: %d corrigidos (%d já estavam)' % (trocados, ja_certos))
    return 0


if __name__ == '__main__':
    sys.exit(main())
