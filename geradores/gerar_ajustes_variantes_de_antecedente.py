# -*- coding: utf-8 -*-
"""Quatro antecedentes ofereciam uma escolha de uma opção só.

Achado ao ligar o motor de escolha (fase 16), que imprime quantas opções cada
escolha oferece — e três diziam "Escolha um tipo de Kit de Jogos: 1 opção".

O Kit de Jogos e o Instrumento Musical são CATEGORIAS: o item do catálogo tem
`variantes` (Dados, Xadrez-do-Dragão, Baralho…), e é entre as variantes que se
escolhe. As escolhas dos quatro antecedentes filtravam pelo id da categoria e não
pediam `de_variantes`, então ofereciam a categoria — uma opção, sem escolha
nenhuma.

O padrão certo já existia no dado desde a fase 7: `bardo_instrumentos` e
`musico_instrumentos` pedem `de_variantes`. Estes quatro ficaram para trás.

Ninguém pegou antes porque o validador confere se o filtro devolve ALGO, e devolvia:
devolvia a categoria. Foi preciso alguém tentar oferecer a escolha a um jogador.
"""
import json, collections, sys

ANTECEDENTES = 'dados/catalogos/antecedentes.json'
FERRAMENTAS = 'dados/catalogos/ferramentas.json'

NOTA = ("A escolha é entre as VARIANTES da categoria (Dados, Xadrez-do-Dragão…), "
        "não entre categorias: é o mesmo padrão de `bardo_instrumentos`.")


def main():
    ferr = {i['id']: i for i in json.load(open(FERRAMENTAS, encoding='utf-8'))['itens']}
    d = json.load(open(ANTECEDENTES, encoding='utf-8'),
                  object_pairs_hook=collections.OrderedDict)

    corrigidos, ja_certos = [], 0
    for a in d['itens']:
        for e in a.get('efeitos', []):
            if e.get('tipo') != 'escolha':
                continue
            de = e.get('de') or {}
            alvo = (de.get('filtro') or {}).get('id')
            if not isinstance(alvo, str):
                continue
            categoria = ferr.get(alvo)
            if not categoria or not categoria.get('variantes'):
                continue
            if de.get('de_variantes'):
                ja_certos += 1
                continue
            de['de_variantes'] = True
            e['nota'] = NOTA
            corrigidos.append((e.get('id'), alvo, len(categoria['variantes'])))

    json.dump(d, open(ANTECEDENTES, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    if not corrigidos and not ja_certos:
        print('ERRO: nenhuma escolha de variante encontrada nos antecedentes')
        return 1
    for eid, alvo, n in corrigidos:
        print('  %-24s %-20s %d variantes' % (eid, alvo, n))
    print('variantes de antecedente: %d corrigidas (%d já estavam)'
          % (len(corrigidos), ja_certos))
    return 0


if __name__ == '__main__':
    sys.exit(main())
