# -*- coding: utf-8 -*-
"""Nove talentos pediam para escolher entre uma opção só.

Achado pela regra nova "escolha tem de ter o que escolher" (fase 16), que nasceu
por causa dos Kits de Jogos e pegou estes de brinde.

Ator, Duelista Defensivo, Especialista em Besta, Mente Aguçada, Mestre Atirador,
Mestre em Armas Grandes, Mestre em Escudos, Resistente e Sorrateiro **não deixam
escolher atributo**: o livro fixa qual sobe (Ator é Carisma, Resistente é
Constituição). O dado modelava isso como uma escolha de uma opção — o que faz o app
perguntar "escolha o atributo: Carisma" e o checklist de subir de nível ganhar uma
linha que não é decisão de ninguém.

Vira o que sempre foi: um `aumento_atributo` direto.
"""
import json, collections, sys

TALENTOS = 'dados/catalogos/talentos.json'


def main():
    d = json.load(open(TALENTOS, encoding='utf-8'),
                  object_pairs_hook=collections.OrderedDict)
    trocados = []
    for t in d['itens']:
        novos = []
        for e in t.get('efeitos', []):
            if not isinstance(e, dict):
                novos.append(e)
                continue
            de = e.get('de') if isinstance(e.get('de'), dict) else {}
            chaves = de.get('chaves') or []
            modelo = (e.get('efeito_por_item_escolhido')
                      if isinstance(e.get('efeito_por_item_escolhido'), dict) else {})
            eh_falsa = (e.get('tipo') == 'escolha' and e.get('quantidade') == 1
                        and len(chaves) == 1
                        and modelo.get('tipo') == 'aumento_atributo'
                        and modelo.get('atributo') == '{{escolhido}}')
            if not eh_falsa:
                novos.append(e)
                continue
            atributo = chaves[0]
            novos.append(collections.OrderedDict([
                ('tipo', 'aumento_atributo'),
                ('atributo', atributo),
                ('valor', modelo.get('valor', 1)),
                ('limite', modelo.get('limite', 20)),
                ('gatilho', e.get('gatilho', 'ao_adquirir')),
                ('nota', 'O livro fixa o atributo; não é escolha do jogador.'),
            ]))
            trocados.append((t['id'], atributo))
        t['efeitos'] = novos

    json.dump(d, open(TALENTOS, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    for tid, a in trocados:
        print('  %-28s +1 %s' % (tid, a))
    print('escolha de uma opção só: %d viraram aumento direto' % len(trocados))
    return 0


if __name__ == '__main__':
    sys.exit(main())
