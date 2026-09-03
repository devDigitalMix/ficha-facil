# -*- coding: utf-8 -*-
"""Bancada da releitura das 391 magias.

O `auditar_descricoes.py` compara fatos verificáveis por termo: se a paráfrase diz
"3d8" e o livro diz "4d8", ele pega. O que ele NÃO pega é o que precisa de leitura:
inversão de sucesso e falha, duração trocada, alvo errado, regra de 2014 escrita com
a segurança de quem lembra mal — que foi o defeito real, encontrado em oito magias.

Esta ferramenta não julga nada. Ela põe lado a lado, em lotes, o TEXTO DO LIVRO e a
PARÁFRASE, para alguém ler os dois. É a única forma de conferência que pega esse
defeito, e ela custa tempo — o que é o preço, não um problema a contornar.

    python3 revisar_magias.py            # quantos lotes, e o tamanho de cada
    python3 revisar_magias.py 3          # imprime o lote 3
    python3 revisar_magias.py 3 --so-corpo   # sem os campos estruturados

Os campos estruturados (alcance, duração, componentes) saem do parser e são fato da
tabela; entram no lote porque a paráfrase às vezes os contradiz.
"""
import json, os, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, 'geradores'))

TAMANHO = 35


def carregar():
    import parse_magias
    from descricoes_magias import DESCRICOES

    livro = {m['nome']: m for m in parse_magias.parse()}
    cat = json.load(open(os.path.join(RAIZ, 'dados', 'catalogos', 'magias.json'),
                        encoding='utf-8'))
    saida = []
    for i in cat['itens']:
        nome = i['nome']
        saida.append({
            'id': i['id'],
            'nome': nome,
            'nivel': i['nivel'],
            'escola': i['escola'],
            'pagina': i['fonte']['pagina_livro'],
            'duracao': (i.get('duracao') or {}).get('texto'),
            'alcance': (i.get('alcance') or {}).get('texto'),
            'tempo': (i.get('tempo_de_conjuracao') or {}).get('texto'),
            'concentracao': i.get('concentracao'),
            'ritual': i.get('ritual'),
            'parafrase': DESCRICOES.get(nome, i.get('descricao_curta')),
            'livro': (livro.get(nome) or {}).get('_corpo', '(SEM TEXTO DO LIVRO)'),
        })
    saida.sort(key=lambda m: (m['nivel'], m['nome']))
    return saida


def main():
    magias = carregar()
    lotes = [magias[i:i + TAMANHO] for i in range(0, len(magias), TAMANHO)]

    if len(sys.argv) < 2:
        print('%d magias em %d lotes de até %d' % (len(magias), len(lotes), TAMANHO))
        for n, l in enumerate(lotes, 1):
            print('  lote %2d: %3d magias — círculo %s a %s, de "%s" a "%s"'
                  % (n, len(l), l[0]['nivel'], l[-1]['nivel'], l[0]['nome'], l[-1]['nome']))
        return 0

    n = int(sys.argv[1])
    so_corpo = '--so-corpo' in sys.argv
    for m in lotes[n - 1]:
        print('=' * 78)
        print('%s  [círculo %s · %s · p. %s]' % (m['nome'], m['nivel'], m['escola'], m['pagina']))
        if not so_corpo:
            print('  tempo: %s | alcance: %s | duração: %s%s%s'
                  % (m['tempo'], m['alcance'], m['duracao'],
                     ' | CONCENTRAÇÃO' if m['concentracao'] else '',
                     ' | RITUAL' if m['ritual'] else ''))
        print('--- LIVRO')
        print(m['livro'])
        print('--- PARÁFRASE')
        print(m['parafrase'])
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
