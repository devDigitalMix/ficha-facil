# -*- coding: utf-8 -*-
"""Deixa explícita a FONTE de onde cada conjurador prepara magias.

Pergunta do usuário em 2026-09-01: 'preparar magias já está restrito às magias que o
personagem conhece?' Estava, mas só implicitamente e de forma desigual — o Mago
declarava `fonte_das_magias`, o Cavaleiro Místico não, e o Mago não tinha uma
`escolha` explícita para as magias preparadas (só para os truques)."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
p = os.path.join(D, 'caracteristicas.json')
d = json.load(open(p, encoding='utf-8'))
por = {i['id']: i for i in d['itens']}

# --- Cavaleiro Místico: prepara da LISTA da classe, não de um livro
c = por['conjuracao_cavaleiro_mistico']
for e in c['efeitos']:
    if e.get('tipo') == 'preparar_magias':
        e['fonte_das_magias'] = 'lista_de_classe'
        e['lista_id'] = 'mago'
        e['nota'] = ("O Cavaleiro Místico não tem livro de magias: o conjunto preparado É o que ele "
                     "conhece, escolhido da lista do Mago e trocável em uma magia por nível de Guerreiro.")

# --- Mago: faltava a escolha explícita das magias preparadas (só havia a dos truques)
c = por['conjuracao_mago']
if not any(e.get('id') == 'mago_preparadas' for e in c['efeitos']):
    c['efeitos'].append({
      "id": "mago_preparadas", "tipo": "escolha",
      "rotulo": "Prepare magias do seu livro de magias",
      "quantidade": "coluna:magias_preparadas", "momento": "descanso_longo",
      "reescolhivel": True, "reescolha_em": "descanso_longo",
      "de": {"catalogo": "magias",
             "filtro": {"lista": "mago", "no_livro": True, "nivel_minimo": 1,
                        "circulo_com_espaco_disponivel": True}},
      "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "lista_id": "mago",
                                    "modo": "preparada", "magia": "{{escolhido}}"}})

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok')
