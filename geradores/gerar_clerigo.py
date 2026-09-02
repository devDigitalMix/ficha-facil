# -*- coding: utf-8 -*-
"""Fase 2f — Classe Clérigo (cap. 3, p. 81-89), Canalizar Divindade e os 4 domínios."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
CD = ["8", "mod:SAB", "prof"]

# ------------------------------------------------------ efeitos e catálogos
NOVOS = [("canalizar_divindade","recurso_id opcoes","Recurso da classe que alimenta efeitos escolhidos (Canalizar Divindade).")]
te = rd('catalogos/tipos_de_efeito.json'); ex = {i['id'] for i in te['itens']}
for i, campos, nota in NOVOS:
    if i not in ex:
        te['itens'].append({"id":i,"nome":i.replace('_',' ').capitalize(),"origem":"NOVO_FASE2F",
                            "campos":campos.split(),"nota":nota})
te['total']=len(te['itens']); wr('catalogos/tipos_de_efeito.json', te)

wr('catalogos/ordens_divinas.json', {"catalogo":"ordens_divinas","nome":"Ordem Divina",
 "fonte":f(82),"total":2,"itens":[
  {"id":"protetor","nome":"Protetor","descricao_curta":"Proficiência com armas Marciais e treinamento com Armadura Pesada."},
  {"id":"taumaturgo","nome":"Taumaturgo","descricao_curta":"Um truque adicional da lista de Clérigo e bônus igual ao modificador de Sabedoria (mínimo +1) em testes de Inteligência (Arcanismo ou Religião)."}]})
wr('catalogos/efeitos_de_canalizar_divindade.json', {"catalogo":"efeitos_de_canalizar_divindade",
 "nome":"Efeitos de Canalizar Divindade","fonte":f(82),"total":2,"parcial":True,
 "nota":"Efeitos básicos da classe. Subclasses acrescentam os seus (ver características de domínio).",
 "itens":[
  {"id":"centelha_divina","nome":"Centelha Divina","fonte":f(82),
   "descricao_curta":"Ação Usar Magia: 1d8 + modificador de Sabedoria a uma criatura a até 9 m — cura, ou dano Necrótico/Radiante com salvaguarda de Constituição por metade. Sobe para 2d8 no nível 7, 3d8 no 13 e 4d8 no 18."},
  {"id":"expulsar_mortos_vivos","nome":"Expulsar Mortos-Vivos","fonte":f(82),
   "descricao_curta":"Ação Usar Magia: cada Morto-Vivo à escolha a até 9 m faz salvaguarda de Sabedoria ou fica Amedrontado e Incapacitado por 1 minuto, fugindo de você. Encerra se sofrer dano, se você ficar Incapacitado ou morrer."}]})
wr('catalogos/opcoes_de_golpes_abencoados.json', {"catalogo":"opcoes_de_golpes_abencoados",
 "nome":"Opções de Golpes Abençoados","fonte":f(83),"total":2,"itens":[
  {"id":"conjuracao_poderosa","nome":"Conjuração Poderosa","descricao_curta":"Soma o modificador de Sabedoria ao dano de qualquer truque de Clérigo."},
  {"id":"golpe_divino","nome":"Golpe Divino","descricao_curta":"Uma vez por turno, ao acertar com arma, causa 1d8 extra de dano Necrótico ou Radiante (2d8 no nível 14)."}]})

# ------------------------------------------------------------ lista (117)
m = rd('catalogos/magias.json'); por = {i['id']: i for i in m['itens']}
for x in json.load(open(caminhos.exigir('lista_clerigo.json', 'gerar_clerigo.py'), encoding='utf-8')):
    x.pop('_escola_no_livro', None)
    if x['id'] in por:
        a = por[x['id']]; a.setdefault('listas', [])
        if 'clerigo' not in a['listas']: a['listas'].append('clerigo')
        for k in ('escola','concentracao','ritual','componente_material_especifico','nivel'):
            a.setdefault(k, x[k])
        a.pop('parcial', None)
    else:
        por[x['id']] = x
m['itens'] = sorted(por.values(), key=lambda x: (x.get('nivel') if x.get('nivel') is not None else 99, x['id']))
m['total'] = len(m['itens'])
m['listas_completas'] = sorted(set(m.get('listas_completas', []) + ['clerigo']))
wr('catalogos/magias.json', m)
lm = rd('catalogos/listas_de_magia.json')
for l in lm['itens']:
    if l['id'] == 'clerigo':
        l['preenchida'] = True; l['total_de_magias'] = 117; l['fonte'] = f(83)
wr('catalogos/listas_de_magia.json', lm)

# ------------------------------------------------------------------ classe
def faixa(mp):
    o = {}
    for (a,b),v in mp.items():
        for n in range(a,b+1): o[n]=v
    return o
BP = faixa({(1,4):2,(5,8):3,(9,12):4,(13,16):5,(17,20):6})
CANAL = {1:0,2:2,3:2,4:2,5:2,6:3,7:3,8:3,9:3,10:3,11:3,12:3,13:3,14:3,15:3,16:3,17:3,18:4,19:4,20:4}
TRU = faixa({(1,3):3,(4,9):4,(10,20):5})
PREP = {1:4,2:5,3:6,4:7,5:9,6:10,7:11,8:12,9:14,10:15,11:16,12:16,13:17,14:17,15:18,16:18,17:19,18:20,19:21,20:22}
SLOTS = {1:[2],2:[3],3:[4,2],4:[4,3],5:[4,3,2],6:[4,3,3],7:[4,3,3,1],8:[4,3,3,2],9:[4,3,3,3,1],
 10:[4,3,3,3,2],11:[4,3,3,3,2,1],12:[4,3,3,3,2,1],13:[4,3,3,3,2,1,1],14:[4,3,3,3,2,1,1],
 15:[4,3,3,3,2,1,1,1],16:[4,3,3,3,2,1,1,1],17:[4,3,3,3,2,1,1,1,1],18:[4,3,3,3,3,1,1,1,1],
 19:[4,3,3,3,3,2,1,1,1],20:[4,3,3,3,3,2,2,1,1]}
CAR = {1:["conjuracao_clerigo","ordem_divina"], 2:["canalizar_divindade"], 3:["subclasse_de_clerigo"],
 4:["aumento_no_valor_de_atributo"], 5:["fulminar_mortos_vivos"], 6:["caracteristica_de_subclasse"],
 7:["golpes_abencoados"], 8:["aumento_no_valor_de_atributo"], 9:[], 10:["intervencao_divina"],
 11:[], 12:["aumento_no_valor_de_atributo"], 13:[], 14:["golpes_abencoados_aprimorados"],
 15:[], 16:["aumento_no_valor_de_atributo"], 17:["caracteristica_de_subclasse"], 18:[],
 19:["dadiva_epica"], 20:["intervencao_divina_maior"]}
def slots(n):
    s = SLOTS[n]; return {f"espacos_{i+1}": (s[i] if i < len(s) else 0) for i in range(9)}

classe = {
 "id":"clerigo","nome":"Clérigo","fonte":f(81),"revisao":OK,
 "descricao_curta":"Canaliza o poder de uma divindade para curar, proteger e fulminar: conjurador pleno com Canalizar Divindade.",
 "dado_de_vida":8,"atributo_primario":["SAB"],"salvaguardas_primarias":["SAB","CAR"],
 "nivel_subclasse":3,
 "conjuracao":{"tipo":"pleno","atributo":"SAB","ritual":False,"foco":["simbolo_sagrado"],
   "preparacao":"lista_de_classe","lista_id":"clerigo","fonte":f(81)},
 "subclasses":["dominio_da_guerra","dominio_da_luz","dominio_da_trapaca","dominio_da_vida"],
 "proficiencias_iniciais":[
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"SAB","nivel_dominio":"proficiente"},
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"CAR","nivel_dominio":"proficiente"},
   {"id":"clerigo_pericias_iniciais","tipo":"escolha","rotulo":"Escolha 2 perícias","quantidade":2,
    "momento":"criacao",
    "de":{"catalogo":"pericias","chaves":["historia","intuicao","medicina","persuasao","religiao"]},
    "efeito_por_item_escolhido":{"tipo":"conceder_proficiencia","categoria":"pericia",
                                 "chave":"{{escolhido}}","nivel_dominio":"proficiente"}},
   {"tipo":"conceder_proficiencia","categoria":"arma","chave":"categoria:simples","nivel_dominio":"proficiente"}],
 "treinamento_com_armadura":["leve","media","escudo"],
 "equipamento_inicial":{"opcoes":[
   {"id":"A","itens":[{"item":"cota_de_malha_parcial"},{"item":"escudo"},{"item":"maca"},
                      {"item":"simbolo_sagrado"},{"item":"kit_de_sacerdote"}],"moedas":{"po":7}},
   {"id":"B","moedas":{"po":110}}],
   "revisao":{"status":"duvida","notas":"Ids de item dependem do catálogo do cap. 6."}},
 "progressao":[{"nivel":n,"bonus_de_proficiencia":BP[n],"caracteristicas":CAR[n],
   "colunas":dict({"canalizar_divindade":CANAL[n],"truques":TRU[n],"magias_preparadas":PREP[n]}, **slots(n))}
   for n in range(1,21)],
 "colunas_da_tabela":dict({"canalizar_divindade":{"nome":"Canalizar Divindade","tipo":"inteiro"},
   "truques":{"nome":"Truques","tipo":"inteiro"},
   "magias_preparadas":{"nome":"Magias Preparadas","tipo":"inteiro"}},
   **{f"espacos_{i}":{"nome":f"Espaços de {i}º Círculo","tipo":"inteiro"} for i in range(1,10)}),
 "multiclasse":{"adquire":["dado_de_vida"],"fonte":f(81),
   "nota":"Espaços por multiclasse seguem a regra do cap. 2."}}
cl = rd('classes.json'); cl['itens']=[c for c in cl['itens'] if c['id']!='clerigo']+[classe]
cl['total']=len(cl['itens']); wr('classes.json', cl)
print('classe ok | magias:', m['total'])
