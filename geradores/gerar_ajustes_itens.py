# -*- coding: utf-8 -*-
"""O nome que o jogador lê, e o que dá para vestir ou segurar.

Três achados do João em 2026-09-04, no inventário:

**1. "a armadura de couro só aparece como Couro".** O livro imprime as armaduras de
dois jeitos: a TABELA (p. 219) usa a forma curta — "Acolchoada", "Couro", "Couro
Batido" —, e a ilustração da mesma seção (p. 218) usa o nome inteiro: "Armadura
Acolchoada", "Armadura de Couro", "Armadura de Couro Batido", "Armadura de Placas",
"Armadura de Placas parcial". Os dois são o livro; o que serve numa ficha é o
inteiro, porque "Couro" sozinho não diz o que é. A forma curta fica em `nome_curto`,
que é a que a tabela imprime.

A regra é mecânica, e por isso não vira lista de gosto: **usa-se o nome da ilustração
só quando ele ACRESCENTA o prefixo "Armadura"**. "Gibão de Peles", "Cota de Malha" e
"Couraça Peitoral" não mudam, e nomes de outras categorias não são tocados.

**2. "não deixa eu equipar o cajado de madeira, mas eu uso ele como druida".** Duas
coisas faltavam. A tela decidia o que é equipável por categoria (arma ou armadura), e
o foco de conjuração ficava de fora — mas foco é justamente algo que se segura. E o
livro diz mais do que isso, na tabela de Focos Druídicos (p. 225):

    Cajado de madeira (também um Bastão)   2 kg   5 PO

O "(também um Bastão)" quer dizer que aquele foco **é também a arma Cajado** — e é o
que faz o Bordão Místico funcionar com ele. O mesmo vale para o Foco Arcano "Cajado
(também um Bastão)", que no dataset é a própria arma. Então o dado passa a declarar:

    cajado_de_madeira  → tambem_e: "cajado"   (é também aquela arma)
    cajado             → tambem_foco: "arcano" (a arma também é Foco Arcano)

Nada é copiado: `tambem_e` é uma REFERÊNCIA, e os números continuam vindo de um lugar
só. Quem resolve isso é o motor, ao equipar.

**3. `equipavel`** passa a ser dado, e não decisão da tela: arma, armadura e foco de
conjuração se vestem ou se seguram; o resto se carrega. Uma categoria nova no livro
entra aqui, e não em três telas.
"""
import json, os

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
p = os.path.join(D, 'catalogos', 'itens.json')
doc = json.load(open(p, encoding='utf-8'))

# p. 218: o nome inteiro, como a ilustração da seção o imprime.
NOME_INTEIRO = {
    'acolchoada': 'Armadura Acolchoada',
    'couro': 'Armadura de Couro',
    'couro_batido': 'Armadura de Couro Batido',
    'placas': 'Armadura de Placas',
    'placas_parcial': 'Armadura de Placas Parcial',
}

EQUIPAVEIS = {'arma', 'armadura', 'foco_de_conjuracao'}

renomeados, equipaveis = [], 0

for item in doc['itens']:
    if item['id'] in NOME_INTEIRO:
        inteiro = NOME_INTEIRO[item['id']]
        # Só quando ACRESCENTA o prefixo: nunca para encurtar nem para trocar palavra.
        assert inteiro.endswith(item['nome']), (item['id'], item['nome'], inteiro)
        item.setdefault('nome_curto', item['nome'])
        item['nome'] = inteiro
        item['nota_do_nome'] = ('A tabela de armaduras (p. 219) imprime a forma curta; '
                                'a ilustração da mesma seção (p. 218) imprime o nome inteiro.')
        renomeados.append(f"{item['id']}: {item['nome_curto']} → {inteiro}")

    if item.get('categoria') in EQUIPAVEIS and not item.get('equipavel'):
        item['equipavel'] = True
        equipaveis += 1

por_id = {i['id']: i for i in doc['itens']}

# "(também um Bastão)": o foco druídico É a arma Cajado — é isso que faz o Bordão
# Místico valer com ele.
por_id['cajado_de_madeira']['tambem_e'] = 'cajado'
por_id['cajado_de_madeira']['nota_do_nome'] = (
    'A tabela de Focos Druídicos (p. 225) o imprime como "Cajado de madeira (também um '
    'Bastão)": é foco e é a arma Cajado ao mesmo tempo.')
# …e a arma Cajado é também o Foco Arcano de mesmo nome (p. 225).
por_id['cajado']['tambem_foco'] = 'arcano'

json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'ok — {len(renomeados)} armaduras com o nome inteiro, {equipaveis} itens equipáveis, '
      f'e o cajado ligado ao seu par:')
for r in renomeados:
    print('   ', r)
