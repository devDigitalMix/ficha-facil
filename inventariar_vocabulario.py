# -*- coding: utf-8 -*-
"""Levanta o vocabulário de runtime que aparece DENTRO dos efeitos.

Os 103 tipos de efeito são catálogo, validados, com teste negativo. O que aparece
dentro deles — predicado de condição, gatilho, duração, fase — cresceu por doze
fases sem nada conferindo, e foi assim que nasceram os sinônimos acidentais.

Esta ferramenta não julga: ela conta e mostra onde. É o que se roda antes de
declarar catálogo novo, e o que se roda de novo quando alguém desconfia.

Uso:
    python3 inventariar_vocabulario.py                 # o resumo
    python3 inventariar_vocabulario.py predicado       # a lista de um vocabulário
    python3 inventariar_vocabulario.py gatilho falha   # onde um token é usado
"""
import json, os, sys, collections

RAIZ = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(RAIZ, 'dados')

# os campos que carregam cada vocabulário
CAMPOS = {
    'predicado': ('condicao', 'condicional', 'condicao_do_alvo'),
    'gatilho': ('gatilho',),
    'fase': ('fase',),
    'duracao': ('duracao',),
    'custo': ('custo',),
    'empilha': ('empilha',),
    'momento': ('momento',),   # campo legado: deve ficar vazio depois da fase 13
}
OPERADORES_LOGICOS = ('todas', 'alguma', 'nao')


def _predicados(o, saida):
    """Achata uma árvore de condição nos predicados folha."""
    if isinstance(o, str):
        saida.append(o)
    elif isinstance(o, list):
        for x in o:
            _predicados(x, saida)
    elif isinstance(o, dict):
        if 'comparar' in o:
            saida.append('<comparação>')
            return
        for k, v in o.items():
            if k in OPERADORES_LOGICOS:
                _predicados(v, saida)
            else:
                saida.append('<forma inesperada: %s>' % k)


def varrer():
    """Devolve {vocabulário: {token: [(arquivo, id_dono, trecho), ...]}}."""
    achados = {k: collections.defaultdict(list) for k in CAMPOS}

    def anda(o, arq, dono):
        if isinstance(o, dict):
            dono = o.get('id', dono)
            trecho = json.dumps(o, ensure_ascii=False)[:240]
            for voc, chaves in CAMPOS.items():
                for c in chaves:
                    if c not in o:
                        continue
                    v = o[c]
                    if voc == 'predicado':
                        folhas = []
                        _predicados(v, folhas)
                        for f in folhas:
                            achados[voc][f].append((arq, dono, trecho))
                    elif isinstance(v, str):
                        achados[voc][v].append((arq, dono, trecho))
                    elif isinstance(v, dict):
                        achados[voc]['<objeto>'].append((arq, dono, trecho))
            for v in o.values():
                anda(v, arq, dono)
        elif isinstance(o, list):
            for x in o:
                anda(x, arq, dono)

    for d, _, fs in os.walk(DADOS):
        for f in sorted(fs):
            if f.endswith('.json'):
                p = os.path.join(d, f)
                anda(json.load(open(p, encoding='utf-8')), os.path.relpath(p, DADOS), None)
    return achados


def main():
    ach = varrer()
    args = sys.argv[1:]

    if not args:
        print('vocabulário de runtime — %s\n' % os.path.relpath(DADOS, RAIZ))
        print('%-12s %10s %12s' % ('vocabulário', 'distintos', 'ocorrências'))
        for voc in CAMPOS:
            d = ach[voc]
            print('%-12s %10d %12d' % (voc, len(d), sum(len(v) for v in d.values())))
        print('\nrode com o nome de um vocabulário para ver a lista.')
        return 0

    voc = args[0]
    if voc not in CAMPOS:
        print('vocabulário desconhecido: %s (conhecidos: %s)'
              % (voc, ', '.join(CAMPOS)))
        return 2

    if len(args) == 1:
        for token in sorted(ach[voc]):
            print('%4d  %s' % (len(ach[voc][token]), token))
        print('\n%d distintos' % len(ach[voc]))
        return 0

    token = args[1]
    for arq, dono, trecho in ach[voc].get(token, []):
        print('%-38s %s' % (arq, dono))
        print('      %s' % trecho)
    print('--- %d ocorrência(s)' % len(ach[voc].get(token, [])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
