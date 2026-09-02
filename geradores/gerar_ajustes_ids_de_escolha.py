# -*- coding: utf-8 -*-
"""Toda escolha precisa de id.

Achado ao começar o motor de escolha (fase 16). Das 230 escolhas do dataset, **53
não tinham id** — todas em `talentos.json`, todas o mesmo "Escolha o atributo a
aumentar" das Dádivas Épicas.

Sem id, uma escolha não pode ser resolvida (a construção guarda a resposta POR id),
não pode entrar no checklist de subir de nível, e duas escolhas iguais em talentos
diferentes viram a mesma coisa. É o mesmo defeito das portas de efeito, na porta ao
lado: identidade que o motor precisava e o dado não dava.

Cada talento tem exatamente uma dessas, então o id sai do próprio talento:
`<id do talento>_atributo`.
"""
import json, collections, sys

TALENTOS = 'dados/catalogos/talentos.json'
SUFIXO = '_atributo'


def carregar(p):
    return json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)


def por_id(o, dono, postos):
    if isinstance(o, list):
        for x in o:
            por_id(x, dono, postos)
        return
    if not isinstance(o, dict):
        return
    if o.get('tipo') == 'escolha' and 'id' not in o:
        novo = collections.OrderedDict()
        for k, v in o.items():
            novo[k] = v
            if k == 'tipo':
                novo['id'] = dono + SUFIXO
        o.clear()
        o.update(novo)
        postos.append(dono + SUFIXO)
    for v in list(o.values()):
        por_id(v, dono, postos)


def main():
    d = carregar(TALENTOS)
    postos = []
    for t in d['itens']:
        antes = len(postos)
        por_id(t, t['id'], postos)
        if len(postos) - antes > 1:
            print("ERRO: '%s' tem mais de uma escolha sem id; o sufixo único não serve"
                  % t['id'])
            return 1
    json.dump(d, open(TALENTOS, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    if len(set(postos)) != len(postos):
        print('ERRO: id de escolha repetido: %s'
              % [k for k, n in collections.Counter(postos).items() if n > 1])
        return 1
    print('ids de escolha: %d postos' % len(postos))
    return 0


if __name__ == '__main__':
    sys.exit(main())
