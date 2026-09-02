# -*- coding: utf-8 -*-
"""Catálogos que o Guerreiro referencia."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
def f(cap, livro): return {"capitulo": cap, "pagina_livro": livro, "pagina_pdf": livro + 4}

# ------------------------------------------------- estados derivados (Ap. C)
wr('catalogos/estados.json', {"catalogo": "estados", "nome": "Estados",
 "fonte": f("ap_c", 375), "total": 3,
 "nota": "Termos do glossário que descrevem um estado sem serem Condições (não têm marcador [Condição]). Lacuna da Fase 1: filtrei o glossário pelos marcadores e estes escaparam.",
 "itens": [
  {"id": "sangrando", "nome": "Sangrando", "fonte": f("ap_c", 375),
   "descricao_curta": "Uma criatura está Sangrando enquanto tiver metade ou menos dos seus Pontos de Vida restantes.",
   "condicao": {"op": "menor_ou_igual", "args": ["pv_atual", {"op": "div_arred_baixo", "args": ["pv_maximo", "2"]}]}},
  {"id": "estavel", "nome": "Estável", "fonte": f("ap_c", 365),
   "descricao_curta": "Criatura com 0 Pontos de Vida que não é obrigada a realizar Salvaguardas Contra Morte."},
  {"id": "surpresa", "nome": "Surpresa", "fonte": f("ap_c", 375),
   "descricao_curta": "Pego desprevenido no início do combate: Desvantagem na jogada de Iniciativa."}]})

# ------------------------- talentos de Estilo de Luta (categoria COMPLETA, cap. 5)
EL = [
 ("arquearia","Arquearia","+2 nas jogadas de ataque com armas à Distância.",209,
  [{"tipo":"modificador","alvo":"jogada_de_ataque","valor":["2"],"empilha":"soma",
    "condicao":{"todas":["arma:a_distancia"]}}]),
 ("combate_com_armas_de_arremesso","Combate com Armas de Arremesso","+2 no dano ao acertar ataque à distância com arma de Arremesso.",209,
  [{"tipo":"modificador","alvo":"jogada_de_dano","valor":["2"],"empilha":"soma",
    "condicao":{"todas":["arma:propriedade:arremesso","ataque:a_distancia"]}}]),
 ("combate_com_armas_grandes","Combate com Armas Grandes","Trata qualquer 1 ou 2 nos dados de dano como 3, com arma Corpo a Corpo empunhada com as duas mãos (Duas Mãos ou Versátil).",209,
  [{"tipo":"tratar_dado_de_dano_minimo","resultado_ate":2,"vira":3,
    "escopo":{"arma_corpo_a_corpo":True,"empunhada_com_as_duas_maos":True,
              "propriedade":["duas_maos","versatil"]}}]),
 ("combate_com_duas_armas","Combate com Duas Armas","No ataque adicional de arma Leve, soma o modificador de atributo ao dano, se já não estivesse somando.",209,
  [{"tipo":"modificador","alvo":"jogada_de_dano","valor":["mod:atributo_de_ataque_da_arma"],
    "empilha":"soma",
    "condicao":{"todas":["ataque_adicional_da_propriedade_leve",
                         {"nao":"ja_soma_modificador_no_dano"}]}}]),
 ("combate_desarmado","Combate Desarmado","Ataque Desarmado pode causar 1d6 + mod. de Força de dano Contundente (1d8 se você não segura arma nem Escudo). No início do seu turno, causa 1d4 Contundente a quem você tem Imobilizado.",209,
  [{"tipo":"dado_de_dano","escopo":["ataque_desarmado"],"formula_dado":"1d6","somar":["mod:FOR"],
    "tipo_dano":"contundente","modo":"substitui_a_criterio_do_jogador"},
   {"tipo":"dado_de_dano","escopo":["ataque_desarmado"],"formula_dado":"1d8","somar":["mod:FOR"],
    "tipo_dano":"contundente","condicao":{"todas":["sem_arma_na_mao","flag:sem_escudo"]},
    "modo":"substitui_a_criterio_do_jogador"},
   {"tipo":"dano","formula_dado":"1d4","tipo_dano":"contundente","momento":"inicio_do_seu_turno",
    "condicao":{"todas":["alvo_imobilizado_por_voce"]}}]),
 ("defensivo","Defensivo","+1 na Classe de Armadura enquanto usa armadura Leve, Média ou Pesada.",209,
  [{"tipo":"modificador","alvo":"ca_total","valor":["1"],"empilha":"soma",
    "condicao":{"alguma":["armadura:leve","armadura:media","armadura:pesada"]}}]),
 ("duelismo","Duelismo","+2 no dano com arma Corpo a Corpo empunhada em uma mão, sem nenhuma outra arma.",209,
  [{"tipo":"modificador","alvo":"jogada_de_dano","valor":["2"],"empilha":"soma",
    "condicao":{"todas":["arma:corpo_a_corpo","uma_mao","nenhuma_outra_arma"]}}]),
 ("intercepcao","Interceptação","Reação para reduzir em 1d10 + BP o dano de um ataque contra criatura a até 1,5 m de você. Exige segurar Escudo ou arma Simples/Marcial.",209,
  [{"tipo":"reducao_de_dano","custo":"reacao","formula":["1d10","prof"],
    "beneficiario":"criatura_a_ate_1_5m","tipos_de_dano":["todos"],
    "requisitos":["segurando:escudo_ou_arma"]}]),
 ("luta_as_cegas","Luta às Cegas","Visão às Cegas com alcance de 3 metros.",210,
  [{"tipo":"conceder_sentido","sentido":"visao_as_cegas","alcance_m":3}]),
 ("protetivo","Protetivo","Reação para interpor seu Escudo: Desvantagem no ataque que provocou a reação e em todos contra aquele alvo até o início do seu próximo turno, enquanto você estiver a até 1,5 m dele.",210,
  [{"tipo":"vantagem","alvo":"jogada_de_ataque_contra_voce","modo":"desvantagem",
    "custo":"reacao","beneficiario":"alvo_protegido","requisitos":["segurando:escudo"],
    "duracao":"ate_inicio_do_seu_proximo_turno"}])]

t = rd('catalogos/talentos.json')
por_id = {i['id']: i for i in t['itens']}
for i, n, d_, p, ef in EL:
    por_id[i] = {"id": i, "nome": n, "categoria": "estilo_de_luta",
                 "pre_requisitos": [{"tipo": "caracteristica", "chave": "estilo_de_luta"}],
                 "repetivel": False, "descricao_curta": d_, "efeitos": ef, "fonte": f(5, p)}
# O capítulo 5 (gerar_talentos.py) passou a ser o DONO do catálogo de talentos: ele
# traz os 75 e declara as quatro categorias completas. Este script mantém só os dez
# de Estilo de Luta, que o Guerreiro precisa desde o nível 1 — e não mexe mais no
# cabeçalho nem cria marcadores 'pendente', para não desfazer o capítulo 5 se for
# reexecutado fora de ordem.
t['itens'] = sorted(por_id.values(), key=lambda x: (x.get('categoria', ''), x['id']))
t['total'] = len(t['itens'])
wr('catalogos/talentos.json', t)

# ------------------------------------ magias parciais adicionais (referenciadas)
m = rd('catalogos/magias.json')
por_id = {i['id']: i for i in m['itens']}
for i, n, nivel, p in [("raio_de_gelo", "Raio de Gelo", 0, 323), ("toque_chocante", "Toque Chocante", 0, 339),
                       ("escudo_arcano", "Escudo Arcano", 1, 277), ("maos_flamejantes", "Mãos Flamejantes", 1, 303),
                       ("salto", "Salto", 1, 330), ("telecinese", "Telecinese", 5, 335)]:
    por_id.setdefault(i, {"id": i, "nome": n, "nivel": nivel, "fonte": f(7, p)})
m['itens'] = sorted(por_id.values(), key=lambda x: (x['nivel'], x['id']))
m['total'] = len(m['itens'])
wr('catalogos/magias.json', m)

# ------------------------------------------------- listas de magia (por classe)
wr('catalogos/listas_de_magia.json', {"catalogo": "listas_de_magia", "nome": "Listas de Magia de Classe",
 "fonte": f(7, 236), "total": 1, "parcial": True,
 "nota": "PARCIAL: só as listas já referenciadas. A lista do Mago em si será preenchida na fase do cap. 7; aqui existe como chave para o Cavaleiro Místico apontar.",
 "itens": [{"id": "mago", "nome": "Lista de magias do Mago", "classe_de_origem": "mago",
            "fonte": f(3, 147), "preenchida": False}]})

# ------------------------------------------------------ tipos de efeito novos
NOVOS = [
 ("alterar_faixa_de_critico","alvo faixa","Muda o intervalo do d20 que conta como Acerto Crítico."),
 ("acao_adicional","excecoes recarga","Concede uma ação a mais no turno (Surto de Ação)."),
 ("substituir_maestria","opcoes escopo","Troca a propriedade de maestria de uma arma no ataque."),
 ("conceder_cobertura","grau alvos alcance_m duracao","Concede um grau de Cobertura a criaturas escolhidas."),
]
te = rd('catalogos/tipos_de_efeito.json')
ex = {i['id'] for i in te['itens']}
for i, campos, nota in NOVOS:
    if i not in ex:
        te['itens'].append({"id": i, "nome": i.replace('_', ' ').capitalize(),
                            "origem": "NOVO_FASE2B", "campos": campos.split(), "nota": nota})
te['total'] = len(te['itens'])
wr('catalogos/tipos_de_efeito.json', te)

# novos alvos de rolagem/impedimento
a = rd('catalogos/alvos.json'); ids = {x['id'] for x in a['itens']}
for i, n in [("jogada_de_dano", "Suas jogadas de dano"),
             ("salvaguarda_contra_morte", "Salvaguardas Contra Morte"),
             ("teste_de_atributo_de_outro", "Teste de atributo de outra criatura")]:
    if i not in ids: a['itens'].append({"id": i, "nome": n})
a['total'] = len(a['itens']); wr('catalogos/alvos.json', a)
print('catálogos do Guerreiro ok')
