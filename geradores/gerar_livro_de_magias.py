# -*- coding: utf-8 -*-
"""O livro de magias do Mago vira uma ESCOLHA — e as magias preparadas saem dele.

Defeito relatado pelo João em 2026-09-03: "parece também que não estava aparecendo as
magias para preparar". Era verdade, e a causa não era a tela.

O `conjuracao_mago` declarava o livro (`livro_de_magias`, com `magias_iniciais`) como
um dado descritivo, mas **nunca abria a escolha das seis magias iniciais**. O livro
nascia vazio; e como `mago_preparadas` filtrava por `no_livro: true`, a lista de
preparadas era, corretamente, vazia. O jogador via "Prepare magias do seu livro de
magias" com zero opções e nada a fazer.

O que o livro diz (p. 147-148, cap. 3):

  Livro de Magias. "O livro contém as magias de 1º círculo ou superior que você
  conhece. Ele começa com seis magias de mago de 1º círculo à sua escolha. […] Ao
  atingir um nível de Mago após o primeiro, adicione duas magias de Mago à sua
  escolha ao seu livro de magias. Cada uma dessas magias deve ser de um círculo para
  o qual você tenha espaços de magia."

  Magias Preparadas. "escolha quatro magias do seu livro de magias. As magias
  escolhidas devem ser de um círculo para o qual você tenha espaços de magia."

Duas decisões, e o porquê de cada uma:

1. **Uma escolha só, cumulativa, e não uma por nível.** O total do livro no nível N é
   6 + 2×(N−1), e a restrição de círculo é a mesma nos dois casos ("um círculo para o
   qual você tenha espaços"). No nível 1 o Mago só tem espaços de 1º círculo, então
   `circulo_com_espaco_disponivel` já produz exatamente "seis magias de 1º círculo" —
   sem precisar de uma regra especial para o começo. A quantidade vem de uma coluna
   nova da tabela (`magias_no_livro`), e não de `quantidade_por_nivel`, porque coluna
   é lida pelo **nível de Mago** e `quantidade_por_nivel` pelo nível de personagem:
   num futuro multiclasse, só a primeira continua certa.

2. **`no_livro: true` vira `de: {fonte: "livro_de_magias"}`.** O filtro antigo
   comparava um campo `no_livro` do catálogo de magias, que nunca existiu — casava com
   nada. "Do seu livro" não é recorte do catálogo: é recorte do que o jogador
   escolheu. Quem alimenta declara `alimenta`, quem consome declara `fonte`, e nenhum
   dos dois cita o outro por id. Isso vale para as quatro escolhas que diziam "do
   livro": preparar magias, as duas de Maestria de Magias (nível 18) e Assinatura
   Mágica (nível 20).
"""
import json, os

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')


def rd(p):
    return json.load(open(os.path.join(D, p), encoding='utf-8'))


def wr(p, o):
    json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


# ------------------------------------------- a coluna: quantas magias o livro tem
classes = rd('classes.json')
mago = next(i for i in classes['itens'] if i['id'] == 'mago')

mago['colunas_da_tabela']['magias_no_livro'] = {
    "nome": "Magias no Livro", "tipo": "inteiro",
    "derivada": True,
    "nota": ("Não é coluna impressa no livro: é o total que o texto do Livro de Magias "
             "descreve (seis no nível 1, mais duas por nível de Mago). Fica na tabela "
             "para ser lida por nível de CLASSE, como as demais."),
}
for linha in mago['progressao']:
    linha['colunas']['magias_no_livro'] = 6 + 2 * (linha['nivel'] - 1)

wr('classes.json', classes)

# ------------------------------------- a escolha que enche o livro, e as que o leem
caracs = rd('caracteristicas.json')
por = {i['id']: i for i in caracs['itens']}

DO_LIVRO = {"catalogo": "magias", "fonte": "livro_de_magias"}

conj = por['conjuracao_mago']
conj['efeitos'] = [e for e in conj['efeitos'] if e.get('id') != 'mago_livro']

livro = next(e for e in conj['efeitos'] if e.get('tipo') == 'livro_de_magias')
recomendadas = livro['magias_iniciais']['recomendadas']

# Entra logo depois do efeito `livro_de_magias`, que é onde ela se explica.
conj['efeitos'].insert(conj['efeitos'].index(livro) + 1, {
    "id": "mago_livro", "tipo": "escolha",
    "rotulo": "Escreva magias no seu livro de magias",
    "quantidade": "coluna:magias_no_livro",
    "gatilho": "nivel_1",
    "recomendados": recomendadas,
    "alimenta": "livro_de_magias",
    "de": {"catalogo": "magias",
           "filtro": {"lista": "mago", "nivel_minimo": 1,
                      "circulo_com_espaco_disponivel": True}},
    "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "lista_id": "mago",
                                  "modo": "no_livro", "magia": "{{escolhido}}"},
    "nota": ("Seis no nível 1 e duas por nível depois: a coluna já traz o total, e o "
             "filtro de círculo já é o mesmo nos dois casos (p. 147)."),
})

# As quatro escolhas que tiravam "do livro" pelo filtro que não casava com nada.
trocadas = []
for c in caracs['itens']:
    for e in c.get('efeitos', []):
        de = e.get('de')
        if not isinstance(de, dict):
            continue
        filtro = de.get('filtro') or {}
        if not filtro.pop('no_livro', None):
            continue
        de['fonte'] = 'livro_de_magias'
        if not filtro:
            de.pop('filtro', None)
        trocadas.append(e['id'])

wr('caracteristicas.json', caracs)
print('ok — livro como escolha; leem do livro:', ', '.join(trocadas))
