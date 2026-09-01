# -*- coding: utf-8 -*-
"""Torna genéricas as características que várias classes compartilham.

Antes, `aumento_no_valor_de_atributo`, `dadiva_epica` e o marcador
`caracteristica_de_subclasse` eram do Monge e carregavam os níveis do Monge.
O Guerreiro concede as mesmas em níveis diferentes — então os níveis passam a
viver só na progressão de cada classe, que é a fonte da verdade."""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
p = os.path.join(D, 'caracteristicas.json')
d = json.load(open(p, encoding='utf-8'))
por_id = {i['id']: i for i in d['itens']}

c = por_id['aumento_no_valor_de_atributo']
c.pop('classe', None); c.pop('niveis', None); c.pop('nivel', None); c.pop('niveis_repetidos', None)
c['escopo'] = 'generico'
c['tipo_de_entrada'] = 'caracteristica'
c['repetivel'] = True
c['tipo_de_repeticao'] = 'nova_escolha'
c['nota_de_repeticao'] = ("Os níveis em que é concedida vivem na progressão de cada classe. "
                          "Cada ocorrência é uma escolha nova de talento e as ocorrências se somam.")
c['fonte'] = {"capitulo": 3, "pagina_livro": 161, "pagina_pdf": 165}
c['efeitos'][0]['id'] = 'asi_escolha_de_talento'

c = por_id['dadiva_epica']
c.pop('classe', None); c.pop('nivel', None)
c['escopo'] = 'generico'
c['tipo_de_entrada'] = 'caracteristica'
c['efeitos'][0]['id'] = 'dadiva_epica_escolha_de_talento'
c['efeitos'][0].pop('recomendado', None)
c['recomendado_por_classe'] = {"monge": "dadiva_do_ataque_irresistivel",
                               "guerreiro": "dadiva_da_proeza_em_combate"}
c['descricao_curta'] = ("Adquire o talento Dádiva Épica ou outro talento épico para o qual se qualifique. "
                        "A recomendação do livro muda por classe (veja 'recomendado_por_classe').")

c = por_id['caracteristica_de_subclasse']
c.pop('classe', None); c.pop('niveis', None); c.pop('nivel', None)
c['escopo'] = 'generico'
c['descricao_curta'] = ("Marcador da tabela, não uma característica em si: nos níveis em que a "
    "progressão da classe o lista, a subclasse escolhida contribui com a característica dela daquele "
    "nível. As características de classe do mesmo nível continuam valendo — no nível 6 do Monge, por "
    "exemplo, você ganha Golpes Potencializados E a característica de nível 6 da sua subclasse. "
    "Os níveis vivem na progressão de cada classe.")

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('genéricas:', [i['id'] for i in d['itens'] if i.get('escopo') == 'generico'])
