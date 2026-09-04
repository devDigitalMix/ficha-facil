# -*- coding: utf-8 -*-
"""Bardo e Feiticeiro: os espaços numa forma que ninguém lê, e sem quem prepara.

O João, em 2026-09-04: "apareceu para eu escolher todas as magias do bardo, logo ali
no nível um, ao invés de só aparecer as de primeiro círculo" — e, separado, "não
aparecem espaços de magia para o bruxo".

São o mesmo defeito com duas caras. **A tabela do Bardo e a do Feiticeiro guardavam
os espaços como LISTA numa coluna só** (`espacos_de_magia: [4, 3, 2]`), enquanto
Clérigo, Druida, Mago, Paladino e Guardião usam uma coluna por círculo
(`espacos_1`… `espacos_9`). Nada lê a forma de lista:

- a ficha monta os espaços lendo `espacos_<n>` — para Bardo e Feiticeiro o painel de
  espaços simplesmente não existia;
- o filtro `circulo_com_espaco_disponivel` pergunta a mesma coisa, não acha nada,
  declara-se `nao_avaliado` e **não recorta** — daí as 127 magias de Bardo e as 130
  de Feiticeiro oferecidas no nível 1, quando o certo são as de 1º círculo;
- e nenhum dos dois tinha sequer o efeito `conceder_slot` que as outras classes têm.

Duas formas para a mesma coisa é dado que mente para metade de quem o lê. Este
gerador normaliza as duas classes para a forma que o resto do dataset usa — os
NÚMEROS são os mesmos do livro, só mudam de arrumação — e acrescenta o
`conceder_slot` que faltava, com recarga em Descanso Longo (p. 100 e p. 122).

Puxando esse fio apareceu o resto: **nenhuma das duas classes tinha `preparar_magias`**,
que é o efeito que diz "o atributo de conjuração desta ficha é este". Sem ele a ficha
devolve `conjuracao: undefined` — sem CD, sem bônus de ataque mágico, sem painel de
espaços. Um Bardo de nível 1 não tinha bloco de magia nenhum, e a única coisa que
denunciava era não aparecer.

O livro diz o atributo com todas as letras: "Carisma é seu atributo de conjuração para
suas magias de Bardo" (p. 60) e "…para suas magias de Feiticeiro" (p. 104). Os dois
preparam da lista da classe, e não de livro.

O Bruxo **não** entra aqui, e de propósito: a tabela dele é mesmo diferente no livro
(Espaços de Pacto, todos do mesmo círculo, recarga no Descanso Curto), e quem tinha
de aprender a ler aquilo era o motor, não o dado.
"""
import json, os

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
COLUNAS = [f'espacos_{i}' for i in range(1, 10)]

classes = json.load(open(os.path.join(D, 'classes.json'), encoding='utf-8'))
caracs = json.load(open(os.path.join(D, 'caracteristicas.json'), encoding='utf-8'))
por_carac = {i['id']: i for i in caracs['itens']}

ORDINAIS = ['1º', '2º', '3º', '4º', '5º', '6º', '7º', '8º', '9º']
feitos = []

for classe in classes['itens']:
    colunas = classe.get('colunas_da_tabela') or {}
    if 'espacos_de_magia' not in colunas:
        continue

    # a coluna-lista some, e no lugar dela entram as nove do resto do dataset
    colunas.pop('espacos_de_magia')
    for i, c in enumerate(COLUNAS):
        colunas[c] = {'nome': f'Espaços de {ORDINAIS[i]} Círculo', 'tipo': 'inteiro'}

    for linha in classe['progressao']:
        lista = linha['colunas'].pop('espacos_de_magia', []) or []
        for i, c in enumerate(COLUNAS):
            linha['colunas'][c] = lista[i] if i < len(lista) else 0

    # os dois efeitos que estas duas classes nunca tiveram: o que concede os espaços
    # e o que declara quem prepara (e com qual atributo)
    conj = por_carac.get(f'conjuracao_{classe["id"]}')
    if conj and not any(e.get('tipo') == 'conceder_slot' for e in conj['efeitos']):
        conj['efeitos'].insert(0, {
            'tipo': 'conceder_slot',
            'tabela_progressao_id': classe['id'],
            'colunas': COLUNAS,
            'recarga': 'descanso_longo',
        })
    if conj and not any(e.get('tipo') == 'preparar_magias' for e in conj['efeitos']):
        conj['efeitos'].insert(1, {
            'tipo': 'preparar_magias',
            'formula_quantidade': ['coluna:magias_preparadas'],
            'atributo_conjuracao': classe['conjuracao']['atributo'],
            'fonte_das_magias': 'lista_de_classe',
            'lista_id': classe['id'],
            'restricao': 'de um círculo para o qual você tenha espaços de magia',
            'magias_sempre_preparadas_nao_contam': True,
        })
    feitos.append(classe['id'])

json.dump(classes, open(os.path.join(D, 'classes.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
json.dump(caracs, open(os.path.join(D, 'caracteristicas.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('ok — espaços de magia normalizados para uma coluna por círculo:', ', '.join(feitos))
