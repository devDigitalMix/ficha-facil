# -*- coding: utf-8 -*-
"""Conserta o aumento de atributo dos antecedentes.

Achado ao escrever o coletor de efeitos do motor (fase 15). Os 16 antecedentes
apontavam a escolha de aumento de atributo para o catálogo
`modos_de_aumento_de_atributo` — que é o do TALENTO Aumento no Valor de Atributo,
com modos "um atributo em +2" e "dois atributos em +1".

Só que a regra do antecedente é outra. Página 177:

    "Um antecedente apresenta três dos valores de atributo do seu personagem.
     Aumente um em 2 e outro em 1, ou aumente todos os três em 1."

As duas regras se parecem e não são a mesma: "todos os três em 1" **não existe**
no catálogo do talento, e "dois atributos em +1" não é o que o antecedente
oferece. Com o catálogo errado, um personagem legítimo (+1 em Destreza,
Constituição e Sabedoria pelo Guia) não tinha como ser montado, e um ilegítimo
tinha.

Ninguém pegou antes porque nada consumia a escolha: o dado passava no validador,
que confere se o catálogo existe — e ele existe. Foi preciso alguém tentar MONTAR
um personagem para a diferença aparecer. É o argumento do `PLANO-MOTOR.md` §8 na
prática: tipo de efeito nenhum jamais tinha sido executado.

Cria `modos_de_aumento_do_antecedente` e repõe a referência nos 16.
"""
import json, collections, os, sys

ANTECEDENTES = 'dados/catalogos/antecedentes.json'
MODOS_DO_TALENTO = 'dados/catalogos/modos_de_aumento_de_atributo.json'
DESTINO = 'dados/catalogos/modos_de_aumento_do_antecedente.json'

FONTE = {"capitulo": 4, "pagina_livro": 177, "pagina_pdf": 181}

MODOS = [
    collections.OrderedDict([
        ("id", "um_em_2_e_outro_em_1"),
        ("nome", "Um em +2 e outro em +1"),
        ("descricao_curta", "Aumenta um dos três valores de atributo em 2 e outro "
                            "em 1. Nenhum passa de 20."),
        ("aumentos", [2, 1]),
        ("fonte", FONTE),
    ]),
    collections.OrderedDict([
        ("id", "todos_os_tres_em_1"),
        ("nome", "Todos os três em +1"),
        ("descricao_curta", "Aumenta cada um dos três valores de atributo em 1. "
                            "Nenhum passa de 20."),
        ("aumentos", [1, 1, 1]),
        ("fonte", FONTE),
    ]),
]

ERRADO = 'modos_de_aumento_de_atributo'
CERTO = 'modos_de_aumento_do_antecedente'


def main():
    doc = collections.OrderedDict([
        ("catalogo", CERTO),
        ("nome", "Modos do Aumento de Atributo do Antecedente"),
        ("fonte", FONTE),
        ("nota", "A regra do antecedente (p. 177) não é a do talento Aumento no "
                 "Valor de Atributo (p. 203): aqui são TRÊS atributos, e a segunda "
                 "opção aumenta os três em 1. O catálogo do talento não tem esse modo."),
        ("total", len(MODOS)),
        ("itens", MODOS),
    ])
    json.dump(doc, open(DESTINO, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    d = json.load(open(ANTECEDENTES, encoding='utf-8'),
                  object_pairs_hook=collections.OrderedDict)
    trocados = 0
    ja_certos = 0
    for a in d['itens']:
        for e in a.get('efeitos', []):
            if e.get('tipo') != 'escolha':
                continue
            de = e.get('de') or {}
            if de.get('catalogo') == CERTO:
                ja_certos += 1        # já rodou antes; rodar de novo não pode falhar
                continue
            if de.get('catalogo') != ERRADO:
                continue
            de['catalogo'] = CERTO
            e['nota'] = ("A regra do antecedente é 'um em 2 e outro em 1, ou os três "
                         "em 1' (p. 177) — não a do talento Aumento no Valor de "
                         "Atributo.")
            trocados += 1
    json.dump(d, open(ANTECEDENTES, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    # O catálogo do talento carregava um `efeito_narrativo` de fachada em cada modo,
    # cujo texto dizia "os efeitos reais estão em efeitos_nomeados do talento". Era
    # placeholder para satisfazer a regra de que opção tem efeitos — e o item nunca
    # foi opção: é vocabulário, o nome de uma forma de distribuir. Os dois catálogos
    # de modo passam a ser VOCABULÁRIO no validador, e o disfarce sai.
    t = json.load(open(MODOS_DO_TALENTO, encoding='utf-8'),
                  object_pairs_hook=collections.OrderedDict)
    limpos = 0
    for i in t['itens']:
        if i.pop('efeitos', None) is not None:
            limpos += 1
    t['nota'] = ("As duas formas de gastar o talento Aumento no Valor de Atributo "
                 "(p. 203). Os efeitos moram em `efeitos_nomeados` do talento; estes "
                 "itens são o vocabulário da escolha. NÃO servem para o antecedente, "
                 "cuja regra é outra (ver modos_de_aumento_do_antecedente).")
    json.dump(t, open(MODOS_DO_TALENTO, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    if trocados + ja_certos != len(d['itens']):
        print('ERRO: %d antecedentes, mas %d escolhas de aumento encontradas'
              % (len(d['itens']), trocados + ja_certos))
        return 1
    print('aumento de antecedente: catálogo próprio criado; %d antecedentes repontados '
          '(%d já estavam), %d efeitos de fachada removidos do catálogo do talento'
          % (trocados, ja_certos, limpos))
    return 0


if __name__ == '__main__':
    sys.exit(main())
