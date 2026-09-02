# -*- coding: utf-8 -*-
"""Fase 2e — Classe Druida (cap. 3, p. 91-101), Forma Selvagem e os 4 círculos."""
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

# --------------------------------------------- tipos de efeito e catálogos novos
NOVOS = [
 ("forma_selvagem","recurso_id tabela_de_formas regras_enquanto_multimorfado","Multimorfia em forma Animal (Forma Selvagem do Druida)."),
 ("converter_recurso","de para taxa gatilho","Troca usos de um recurso por outro (Forma Selvagem ↔ espaço de magia)."),
 ("emanacao","tamanho_m duracao efeitos encerra_se","Área que acompanha o personagem (Ira do Mar)."),
 ("tratar_resultado_minimo","alvo minimo","Trata um resultado abaixo de X no d20 como X (constelação do Dragão)."),
]
te = rd('catalogos/tipos_de_efeito.json'); ex = {i['id'] for i in te['itens']}
for i, campos, nota in NOVOS:
    if i not in ex:
        te['itens'].append({"id": i, "nome": i.replace('_',' ').capitalize(),
                            "origem": "NOVO_FASE2E", "campos": campos.split(), "nota": nota})
te['total'] = len(te['itens']); wr('catalogos/tipos_de_efeito.json', te)

# catálogo de criaturas: existe como chave, vazio até o Ap. B (fora do escopo atual)
wr('catalogos/criaturas.json', {"catalogo":"criaturas","nome":"Blocos de Estatísticas de Criaturas",
 "fonte":{"capitulo":"ap_b","pagina_livro":346,"pagina_pdf":350},
 "parcial": True, "preenchida": False, "total": 0, "itens": [],
 "nota":("VAZIO POR DECISÃO DE ESCOPO: o Apêndice B ficou de fora (decisão 5 da Fase 0). A Forma "
         "Selvagem do Druida escolhe entre blocos de Fera com ND máximo, então a escolha aponta para "
         "este catálogo por FILTRO. Enquanto ele estiver vazio o validador emite AVISO, não erro, e o "
         "seletor do app fica vazio — o mesmo dado passa a funcionar se o Ap. B for extraído depois.")})

# constelações e opções da Fúria Elemental
wr('catalogos/constelacoes.json', {"catalogo":"constelacoes","nome":"Constelações da Forma Estrelada",
 "fonte":f(98),"total":3,"itens":[
  {"id":"arqueiro","nome":"Arqueiro","descricao_curta":"Ação Bônus para um ataque mágico à distância a até 18 m, causando 1d8 + modificador de Sabedoria de dano Radiante."},
  {"id":"dragao","nome":"Dragão","descricao_curta":"Trata 9 ou menos no d20 como 10 em testes de Inteligência, de Sabedoria e em salvaguardas de Constituição para manter Concentração."},
  {"id":"taca","nome":"Taça","descricao_curta":"Ao conjurar magia com espaço que cure alguém, você ou criatura a até 9 m recupera 1d8 + modificador de Sabedoria."}]})
wr('catalogos/opcoes_de_furia_elemental.json', {"catalogo":"opcoes_de_furia_elemental",
 "nome":"Opções de Fúria Elemental","fonte":f(94),"total":2,"itens":[
  {"id":"ataque_primal","nome":"Ataque Primal","descricao_curta":"Uma vez por turno, ao acertar com arma ou ataque da forma Animal, causa 1d8 extra de dano Elétrico, Gélido, Ígneo ou Trovejante (2d8 no nível 15)."},
  {"id":"conjuracao_poderosa","nome":"Conjuração Poderosa","descricao_curta":"Soma o modificador de Sabedoria ao dano de qualquer truque de Druida (no nível 15, truques de alcance 3 m ou mais passam a 90 m)."}]})
wr('catalogos/terrenos_druidicos.json', {"catalogo":"terrenos_druidicos","nome":"Terrenos do Círculo da Terra",
 "fonte":f(98),"total":4,"itens":[
  {"id":"arido","nome":"Árido","resistencia":"igneo"},{"id":"polar","nome":"Polar","resistencia":"gelido"},
  {"id":"temperado","nome":"Temperado","resistencia":"eletrico"},
  {"id":"tropical","nome":"Tropical","resistencia":"venenoso"}]})
wr('catalogos/ordens_primais.json', {"catalogo":"ordens_primais","nome":"Ordem Primal",
 "fonte":f(92),"total":2,"itens":[
  {"id":"protetor","nome":"Protetor","descricao_curta":"Proficiência com armas Marciais e treinamento com armadura Média."},
  {"id":"xama","nome":"Xamã","descricao_curta":"Um truque adicional da lista de Druida e bônus igual ao modificador de Sabedoria (mínimo +1) em testes de Inteligência (Arcanismo ou Natureza)."}]})

# ----------------------------------------------------- lista de magias (135)
m = rd('catalogos/magias.json'); por = {i['id']: i for i in m['itens']}
for x in json.load(open(caminhos.exigir('lista_druida.json', 'gerar_druida.py'), encoding='utf-8')):
    x.pop('_escola_no_livro', None)
    if x['id'] in por:
        alvo = por[x['id']]; alvo.setdefault('listas', [])
        if 'druida' not in alvo['listas']: alvo['listas'].append('druida')
        for k in ('escola','concentracao','ritual','componente_material_especifico','nivel'):
            alvo.setdefault(k, x[k])
        alvo.pop('parcial', None)
    else:
        por[x['id']] = x
m['itens'] = sorted(por.values(), key=lambda x: (x.get('nivel') if x.get('nivel') is not None else 99, x['id']))
m['total'] = len(m['itens'])
m['listas_completas'] = sorted(set(m.get('listas_completas', []) + ['druida']))
wr('catalogos/magias.json', m)
lm = rd('catalogos/listas_de_magia.json')
for l in lm['itens']:
    if l['id'] == 'druida':
        l['preenchida'] = True; l['total_de_magias'] = 135; l['fonte'] = f(94)
wr('catalogos/listas_de_magia.json', lm)

# ------------------------------------------------------------------ a classe
def faixa(mp):
    o = {}
    for (a,b),v in mp.items():
        for n in range(a,b+1): o[n]=v
    return o
BP = faixa({(1,4):2,(5,8):3,(9,12):4,(13,16):5,(17,20):6})
FS = {1:0,2:2,3:2,4:2,5:2,6:3,7:3,8:3,9:3,10:3,11:3,12:3,13:3,14:3,15:3,16:3,17:4,18:4,19:4,20:4}
TRU = faixa({(1,3):2,(4,9):3,(10,20):4})
PREP = {1:4,2:5,3:6,4:7,5:9,6:10,7:11,8:12,9:14,10:15,11:16,12:16,13:17,14:17,15:18,16:18,17:19,18:20,19:21,20:22}
SLOTS = {1:[2],2:[3],3:[4,2],4:[4,3],5:[4,3,2],6:[4,3,3],7:[4,3,3,1],8:[4,3,3,2],9:[4,3,3,3,1],
 10:[4,3,3,3,2],11:[4,3,3,3,2,1],12:[4,3,3,3,2,1],13:[4,3,3,3,2,1,1],14:[4,3,3,3,2,1,1],
 15:[4,3,3,3,2,1,1,1],16:[4,3,3,3,2,1,1,1],17:[4,3,3,3,2,1,1,1,1],18:[4,3,3,3,3,1,1,1,1],
 19:[4,3,3,3,3,2,1,1,1],20:[4,3,3,3,3,2,2,1,1]}
CAR = {1:["conjuracao_druida","idioma_druidico","ordem_primal"],
 2:["companheiro_selvagem","forma_selvagem"], 3:["subclasse_de_druida"],
 4:["aumento_no_valor_de_atributo"], 5:["ressurgimento_selvagem"], 6:["caracteristica_de_subclasse"],
 7:["furia_elemental"], 8:["aumento_no_valor_de_atributo"], 9:[], 10:["caracteristica_de_subclasse"],
 11:[], 12:["aumento_no_valor_de_atributo"], 13:[], 14:["caracteristica_de_subclasse"],
 15:["furia_elemental_aprimorada"], 16:["aumento_no_valor_de_atributo"], 17:[],
 18:["magias_bestiais"], 19:["dadiva_epica"], 20:["arquidruida"]}
def slots(n):
    s = SLOTS[n]; return {f"espacos_{i+1}": (s[i] if i < len(s) else 0) for i in range(9)}

classe = {
 "id":"druida","nome":"Druida","fonte":f(91),"revisao":OK,
 "descricao_curta":"Conjurador das forças da natureza que cura, controla os elementos e se multimorfa em animais.",
 "dado_de_vida":8,"atributo_primario":["SAB"],"salvaguardas_primarias":["INT","SAB"],
 "nivel_subclasse":3,
 "conjuracao":{"tipo":"pleno","atributo":"SAB","ritual":False,"foco":["foco_druidico"],
   "preparacao":"lista_de_classe","lista_id":"druida","fonte":f(91)},
 "subclasses":["circulo_da_lua","circulo_da_terra","circulo_das_estrelas","circulo_do_mar"],
 "proficiencias_iniciais":[
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"INT","nivel_dominio":"proficiente"},
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"SAB","nivel_dominio":"proficiente"},
   {"id":"druida_pericias_iniciais","tipo":"escolha","rotulo":"Escolha 2 perícias","quantidade":2,
    "momento":"criacao",
    "de":{"catalogo":"pericias","chaves":["arcanismo","lidar_com_animais","intuicao","medicina",
                                          "natureza","percepcao","religiao","sobrevivencia"]},
    "efeito_por_item_escolhido":{"tipo":"conceder_proficiencia","categoria":"pericia",
                                 "chave":"{{escolhido}}","nivel_dominio":"proficiente"}},
   {"tipo":"conceder_proficiencia","categoria":"arma","chave":"categoria:simples","nivel_dominio":"proficiente"},
   {"tipo":"conceder_proficiencia","categoria":"ferramenta","chave":"kit_de_herbalismo","nivel_dominio":"proficiente"}],
 "treinamento_com_armadura":["leve","escudo"],
 "equipamento_inicial":{"opcoes":[
   {"id":"A","itens":[{"item":"armadura_de_couro"},{"item":"escudo"},{"item":"foice"},
                      {"item":"foco_druidico_cajado"},{"item":"kit_de_explorador"},
                      {"item":"kit_de_herbalismo"}],"moedas":{"po":9}},
   {"id":"B","moedas":{"po":50}}],
   "revisao":{"status":"duvida","notas":"Ids de item dependem do catálogo do cap. 6."}},
 "progressao":[{"nivel":n,"bonus_de_proficiencia":BP[n],"caracteristicas":CAR[n],
   "colunas":dict({"forma_selvagem":FS[n],"truques":TRU[n],"magias_preparadas":PREP[n]}, **slots(n))}
   for n in range(1,21)],
 "colunas_da_tabela":dict({"forma_selvagem":{"nome":"Forma Selvagem","tipo":"inteiro"},
   "truques":{"nome":"Truques","tipo":"inteiro"},
   "magias_preparadas":{"nome":"Magias Preparadas","tipo":"inteiro"}},
   **{f"espacos_{i}":{"nome":f"Espaços de {i}º Círculo","tipo":"inteiro"} for i in range(1,10)}),
 "multiclasse":{"adquire":["dado_de_vida"],"fonte":f(91),
   "nota":"Espaços por multiclasse seguem a regra do cap. 2."}}
cl = rd('classes.json'); cl['itens']=[c for c in cl['itens'] if c['id']!='druida']+[classe]
cl['total']=len(cl['itens']); wr('classes.json', cl)
print('classe ok')
