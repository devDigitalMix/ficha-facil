# -*- coding: utf-8 -*-
"""O truque que cresce com o nível passa a dizer quanto, em vez de contar em prosa.

O João, em 2026-09-04: "eu quero que tenha o nome, o número e tipo de dados que lanço
para acertar, o mesmo para cura ou dano […] tudo o que eu preciso para jogar, já
calculado os bônus e tudo".

Para quase tudo o dado já respondia: `ataque`, `salvaguarda`, `dano`, `alcance` e
`area` são campos. **Só o crescimento do truque estava em prosa** — "O dano aumenta
em 1d8 quando você atinge os níveis 5 (2d8), 11 (3d8) e 17 (4d8)" —, e prosa não se
soma. Ou a tela passava a interpretar texto (regra de D&D na tela, que é o que este
projeto não faz), ou o dado passava a declarar.

Este gerador lê o texto que veio do livro e escreve `escala_por_nivel`, com os dados
que o próprio texto imprime entre parênteses. Não deduz progressão nenhuma: se o
texto não traz os três valores no formato do livro, o campo simplesmente não é
escrito — e o motor continua mostrando o dado-base, que é a verdade que ele tem.

Um truque não casa, e por um bom motivo: o Raio Místico não aumenta o dado, aumenta
o **número de feixes** ("dois feixes no nível 5, três no 11 e quatro no 17"). Isso não
é a mesma coisa e não vira `escala_por_nivel`; fica anotado como está.
"""
import json, os, re

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
p = os.path.join(D, 'catalogos', 'magias.json')
doc = json.load(open(p, encoding='utf-8'))

# "níveis 5 (2d8), 11 (3d8) e 17 (4d8)" — os três valores que o livro imprime.
PADRAO = re.compile(
    r'níveis?\s*5\s*\(([^)]+)\)[^0-9]*11\s*\(([^)]+)\)[^0-9]*17\s*\(([^)]+)\)'
)
DADO = re.compile(r'^\d+d\d+$')

escritos, sem_padrao = [], []

for magia in doc['itens']:
    apr = magia.get('aprimoramento') or {}
    if magia.get('nivel') != 0 or apr.get('tipo') != 'truque':
        continue
    achado = PADRAO.search(apr.get('texto', ''))
    if not achado:
        sem_padrao.append(magia['id'])
        continue
    valores = [v.strip() for v in achado.groups()]
    if not all(DADO.match(v) for v in valores):
        sem_padrao.append(magia['id'])
        continue
    apr['escala_por_nivel'] = {'5': valores[0], '11': valores[1], '17': valores[2]}
    escritos.append(magia['id'])

json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'ok — {len(escritos)} truques com a escala declarada; '
      f'{len(sem_padrao)} continuam só em prosa: {", ".join(sem_padrao) or "-"}')
