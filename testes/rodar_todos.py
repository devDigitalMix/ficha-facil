# -*- coding: utf-8 -*-
"""Roda a conferência inteira, na ordem em que ela faz sentido.

    python3 testes/rodar_todos.py            # tudo
    python3 testes/rodar_todos.py --rapido   # pula a reconstrução, que é a demorada

A ordem não é arbitrária: forma antes de semântica (um JSON malformado faz o
validador reclamar da coisa errada), semântica antes dos testes negativos (que
existem para provar que o validador confere), e a reconstrução por último, porque
ela é a única que responde "o gerador ainda é a fonte?".
"""
import os, subprocess, sys, glob

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))


def rodar(rotulo, cmd, cwd=RAIZ):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    ultima = (r.stdout.strip().splitlines() or [''])[-1][:100]
    print('%-6s %-46s %s' % ('ok' if r.returncode == 0 else 'FALHOU', rotulo, ultima))
    if r.returncode != 0 and r.stderr.strip():
        print('       ' + r.stderr.strip().splitlines()[-1][:140])
    return r.returncode == 0


def main():
    rapido = '--rapido' in sys.argv
    py = sys.executable
    passos = [
        ('forma (checar_schema.py)', [py, 'checar_schema.py']),
        ('semântica (validar.py)', [py, 'validar.py']),
        ('derivação (verificar_derivacao.py)', [py, 'verificar_derivacao.py']),
        ('descrições de magia (auditar_descricoes.py)', [py, 'auditar_descricoes.py']),
    ]
    for t in sorted(glob.glob(os.path.join(AQUI, 'teste_negativo_*.py'))):
        passos.append(('negativo: ' + os.path.basename(t)[15:-3], [py, t]))
    passos.append(('motor (node --test)',
                   ['npm', '--prefix', os.path.join(RAIZ, 'motor'), 'run', '--silent', 'teste']))
    passos.append(('backend (node --test)',
                   ['npm', '--prefix', os.path.join(RAIZ, 'backend'), 'run', '--silent', 'teste']))
    if not rapido:
        passos.append(('reconstrução (reconstruir.py --comparar)',
                       [py, 'reconstruir.py', '--comparar']))

    falhas = [r for r, ok in ((rot, rodar(rot, cmd)) for rot, cmd in passos) if not ok]
    print()
    if falhas:
        print('%d de %d passos falharam:' % (len(falhas), len(passos)))
        for f in falhas:
            print('  ' + f)
        return 1
    print('%d de %d passos limpos.' % (len(passos), len(passos)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
