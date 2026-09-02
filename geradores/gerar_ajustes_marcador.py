# -*- coding: utf-8 -*-
"""Separa as duas semânticas que estavam no mesmo campo `niveis_repetidos`."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
p = os.path.join(D, 'caracteristicas.json')
d = json.load(open(p, encoding='utf-8'))
por_id = {i['id']: i for i in d['itens']}

# A) característica de verdade que se repete: cada ocorrência é uma NOVA escolha
c = por_id['aumento_no_valor_de_atributo']
c['tipo_de_entrada'] = 'caracteristica'
c['niveis'] = c.pop('niveis_repetidos')
c['repetivel'] = True
c['nota_de_repeticao'] = ("A cada nível listado você adquire a característica de novo e faz uma "
                          "escolha nova de talento. As ocorrências se somam.")

# B) marcador de tabela: não é característica, é um ponteiro para a subclasse
c = por_id['caracteristica_de_subclasse']
c['tipo_de_entrada'] = 'marcador'
c['niveis'] = c.pop('niveis_repetidos')
c.pop('nivel', None)
c['nivel'] = 6
c['resolve_por'] = {"colecao": "subclasses", "campo": "caracteristicas",
                    "criterio": "caracteristica da subclasse escolhida cujo nivel == nivel atual"}
c['descricao_curta'] = ("Marcador da tabela, não uma característica em si: nestes níveis a linha da "
    "tabela também traz a característica correspondente da subclasse escolhida. As características de "
    "classe do mesmo nível continuam valendo — no nível 6, por exemplo, o Monge ganha Golpes "
    "Potencializados E a característica de nível 6 da sua subclasse.")
c['revisao'] = {"status": "ok",
  "notas": ("Marcador de tabela. O motor não deve aplicá-lo como efeito: ele só sinaliza que, naquele "
            "nível, a subclasse escolhida contribui com a característica dela. Não substitui nem "
            "compete com as características de classe do mesmo nível.")}
c['efeitos'] = []

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok')
