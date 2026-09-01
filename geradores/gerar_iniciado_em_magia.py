# -*- coding: utf-8 -*-
"""Exemplo trabalhado: o talento Iniciado em Magia (cap. 5, p. 201).

Serve para responder à pergunta do usuário: talentos que dão magias de OUTRA classe
já cabem no modelo? Cabem — é uma escolha aninhada (primeiro a lista, depois as
magias daquela lista). Este é o único talento do cap. 5 extraído por ora.
"""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
def f(cap, livro): return {"capitulo": cap, "pagina_livro": livro, "pagina_pdf": livro + 4}

# as três listas que o talento oferece precisam existir como chave
lm = rd('catalogos/listas_de_magia.json')
ids = {i['id'] for i in lm['itens']}
for i, n, classe, pag in [("clerigo", "Lista de magias do Clérigo", "clerigo", 81),
                          ("druida", "Lista de magias do Druida", "druida", 91),
                          ("bardo", "Lista de magias do Bardo", "bardo", 59),
                          ("feiticeiro", "Lista de magias do Feiticeiro", "feiticeiro", 103),
                          ("bruxo", "Lista de magias do Bruxo", "bruxo", 69),
                          ("guardiao", "Lista de magias do Guardião", "guardiao", 117),
                          ("paladino", "Lista de magias do Paladino", "paladino", 167)]:
    if i not in ids:
        lm['itens'].append({"id": i, "nome": n, "classe_de_origem": classe,
                            "fonte": f(3, pag), "preenchida": False})
lm['total'] = len(lm['itens'])
lm['nota'] = ("Só a lista do Mago está preenchida. As outras existem como chave para que efeitos e "
              "filtros possam referenciá-las desde já; cada uma é preenchida quando sua classe for extraída.")
wr('catalogos/listas_de_magia.json', lm)

# catálogo das listas que Iniciado em Magia oferece
wr('catalogos/listas_de_iniciado_em_magia.json', {
 "catalogo": "listas_de_iniciado_em_magia", "nome": "Listas oferecidas por Iniciado em Magia",
 "fonte": f(5, 201), "total": 3,
 "itens": [{"id": "clerigo", "nome": "Lista de magias do Clérigo"},
           {"id": "druida", "nome": "Lista de magias do Druida"},
           {"id": "mago", "nome": "Lista de magias do Mago"}]})

t = rd('catalogos/talentos.json')
por = {i['id']: i for i in t['itens']}
por['iniciado_em_magia'] = {
 "id": "iniciado_em_magia", "nome": "Iniciado em Magia", "categoria": "origem",
 "fonte": f(5, 201), "repetivel": True,
 "restricao_de_repeticao": "a cada vez você deve escolher uma lista de magias diferente",
 "descricao_curta": ("Dois truques e uma magia de 1º círculo de uma lista à escolha (Clérigo, Druida "
   "ou Mago). A magia de 1º círculo fica sempre preparada e pode ser conjurada uma vez por Descanso "
   "Longo sem espaço de magia, ou com qualquer espaço que você tenha."),
 "efeitos": [
  # 1) escolha-mãe: qual lista. As outras escolhas dependem desta.
  {"id": "iniciado_em_magia_lista", "tipo": "escolha", "rotulo": "Escolha a lista de magias",
   "quantidade": 1, "momento": "ao_adquirir_o_talento",
   "de": {"catalogo": "listas_de_iniciado_em_magia", "todo_o_catalogo": True},
   "efeito_por_item_escolhido": {"tipo": "efeito_narrativo", "chave": "lista_escolhida",
                                 "lista": "{{escolhido}}"},
   "define_variavel": "lista_do_talento"},
  # 2) escolha do atributo de conjuração
  {"id": "iniciado_em_magia_atributo", "tipo": "escolha",
   "rotulo": "Escolha o atributo de conjuração deste talento",
   "quantidade": 1, "momento": "ao_adquirir_o_talento",
   "de": {"catalogo": "atributos", "chaves": ["INT", "SAB", "CAR"]},
   "efeito_por_item_escolhido": {"tipo": "efeito_narrativo", "chave": "atributo_do_talento",
                                 "atributo": "{{escolhido}}"},
   "define_variavel": "atributo_do_talento"},
  # 3) dois truques DA LISTA ESCOLHIDA — filtro resolve na variável definida acima
  {"id": "iniciado_em_magia_truques", "tipo": "escolha", "rotulo": "Escolha dois truques",
   "quantidade": 2, "momento": "ao_adquirir_o_talento",
   "reescolhivel": True, "reescolha_em": "cada_novo_nivel", "reescolha_quantidade": 1,
   "depende_de": "iniciado_em_magia_lista",
   "de": {"catalogo": "magias", "filtro": {"nivel": 0, "lista": "$lista_do_talento"}},
   "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "modo": "conhecida",
                                 "magia": "{{escolhido}}",
                                 "atributo_conjuracao": "$atributo_do_talento"}},
  # 4) uma magia de 1º círculo da mesma lista, sempre preparada
  {"id": "iniciado_em_magia_magia_1", "tipo": "escolha", "rotulo": "Escolha uma magia de 1º círculo",
   "quantidade": 1, "momento": "ao_adquirir_o_talento",
   "reescolhivel": True, "reescolha_em": "cada_novo_nivel",
   "depende_de": "iniciado_em_magia_lista",
   "de": {"catalogo": "magias", "filtro": {"nivel": 1, "lista": "$lista_do_talento"}},
   "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "modo": "sempre_preparada",
                                 "magia": "{{escolhido}}",
                                 "atributo_conjuracao": "$atributo_do_talento",
                                 "nao_conta_para_o_limite_de_preparadas": True}},
  # 5) a conjuração gratuita por Descanso Longo
  {"tipo": "conjurar_sem_espaco", "magia": "$escolhido_em:iniciado_em_magia_magia_1",
   "frequencia": "uma_vez_por_descanso_longo", "recarga": ["descanso_longo"],
   "tambem_conjuravel_com": "qualquer espaço de magia que você tenha"}],
 "revisao": {"status": "ok",
   "notas": ("Extraído como exemplo trabalhado para validar o modelo de acesso a magias de outra "
             "classe. O restante do capítulo 5 ainda não foi extraído.")}}
t['itens'] = sorted(por.values(), key=lambda x: (x.get('categoria',''), x['id']))
t['total'] = len(t['itens'])
wr('catalogos/talentos.json', t)
print('ok — listas:', lm['total'], '| talentos:', t['total'])
