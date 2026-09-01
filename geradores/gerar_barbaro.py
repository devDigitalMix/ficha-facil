# -*- coding: utf-8 -*-
"""Fase 2g — Bárbaro (cap. 3, p. 51-57). Sem conjuração."""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
CD_FOR = ["8", "mod:FOR", "prof"]

NOVOS = [("furia","recurso_id efeitos duracao encerra_se extensao","Estado de Fúria do Bárbaro: recurso + pacote de efeitos enquanto ativo.")]
te = rd('catalogos/tipos_de_efeito.json'); ex={i['id'] for i in te['itens']}
for i,c_,n in NOVOS:
    if i not in ex: te['itens'].append({"id":i,"nome":i.capitalize(),"origem":"NOVO_FASE2G","campos":c_.split(),"nota":n})
te['total']=len(te['itens']); wr('catalogos/tipos_de_efeito.json', te)

wr('catalogos/efeitos_de_golpe_brutal.json', {"catalogo":"efeitos_de_golpe_brutal",
 "nome":"Efeitos de Golpe Brutal","fonte":f(53),"total":4,"itens":[
  {"id":"golpe_debilitador","nome":"Golpe Debilitador","nivel_minimo":9,
   "descricao_curta":"Deslocamento do alvo reduzido em 4,5 m até o início do seu próximo turno. Só um por alvo — o mais recente."},
  {"id":"golpe_poderoso","nome":"Golpe Poderoso","nivel_minimo":9,
   "descricao_curta":"Empurra o alvo 4,5 m para longe; você pode avançar metade do Deslocamento em direção a ele sem provocar Ataques de Oportunidade."},
  {"id":"golpe_atordoante","nome":"Golpe Atordoante","nivel_minimo":13,
   "descricao_curta":"O alvo tem Desvantagem na próxima salvaguarda e não pode fazer Ataques de Oportunidade até o início do seu próximo turno."},
  {"id":"golpe_destruidor","nome":"Golpe Destruidor","nivel_minimo":13,
   "descricao_curta":"O próximo ataque de outra criatura contra o alvo recebe +5, antes do início do seu próximo turno. Um bônus por jogada."}]})
wr('catalogos/opcoes_de_furia_dos_selvagens.json', {"catalogo":"opcoes_de_furia_dos_selvagens",
 "nome":"Fúria dos Selvagens","fonte":f(56),"total":3,"itens":[
  {"id":"aguia","nome":"Águia","descricao_curta":"Ao entrar em Fúria, executa Correr e Desengajar na mesma Ação Bônus; depois, uma Ação Bônus faz as duas."},
  {"id":"lobo","nome":"Lobo","descricao_curta":"Seus aliados têm Vantagem em ataques contra inimigos seus a até 1,5 m de você."},
  {"id":"urso","nome":"Urso","descricao_curta":"Resistência a todos os tipos de dano, exceto Energético, Necrótico, Psíquico e Radiante."}]})
wr('catalogos/opcoes_de_aspecto_dos_selvagens.json', {"catalogo":"opcoes_de_aspecto_dos_selvagens",
 "nome":"Aspecto dos Selvagens","fonte":f(56),"total":3,"itens":[
  {"id":"coruja","nome":"Coruja","descricao_curta":"Visão no Escuro de 18 m, ou +18 m se já tiver."},
  {"id":"pantera","nome":"Pantera","descricao_curta":"Deslocamento de Escalada igual ao seu Deslocamento."},
  {"id":"salmao","nome":"Salmão","descricao_curta":"Deslocamento de Natação igual ao seu Deslocamento."}]})
wr('catalogos/opcoes_de_poder_dos_selvagens.json', {"catalogo":"opcoes_de_poder_dos_selvagens",
 "nome":"Poder dos Selvagens","fonte":f(56),"total":3,"itens":[
  {"id":"carneiro","nome":"Carneiro","descricao_curta":"Impõe Caído a criatura Grande ou menor ao acertá-la corpo a corpo."},
  {"id":"falcao","nome":"Falcão","descricao_curta":"Deslocamento de Voo igual ao seu, se não estiver usando armadura."},
  {"id":"leao","nome":"Leão","descricao_curta":"Inimigos a até 1,5 m têm Desvantagem em ataques contra alvos que não sejam você ou outro Bárbaro com essa opção."}]})

def faixa(mp):
    o={}
    for (a,b),v in mp.items():
        for n in range(a,b+1): o[n]=v
    return o
BP=faixa({(1,4):2,(5,8):3,(9,12):4,(13,16):5,(17,20):6})
FURIAS={1:2,2:2,3:3,4:3,5:3,6:4,7:4,8:4,9:4,10:4,11:4,12:5,13:5,14:5,15:5,16:5,17:6,18:6,19:6,20:6}
DANO=faixa({(1,8):2,(9,15):3,(16,20):4})
MAEST=faixa({(1,3):2,(4,9):3,(10,20):4})
CAR={1:["defesa_sem_armadura_barbaro","furia","maestria_em_arma_barbaro"],
 2:["ataque_imprudente","sentido_de_perigo"], 3:["conhecimento_primordial","subclasse_de_barbaro"],
 4:["aumento_no_valor_de_atributo"], 5:["ataque_extra","movimento_rapido"],
 6:["caracteristica_de_subclasse"], 7:["bote_instintivo","instintos_primitivos"],
 8:["aumento_no_valor_de_atributo"], 9:["golpe_brutal"], 10:["caracteristica_de_subclasse"],
 11:["furia_implacavel"], 12:["aumento_no_valor_de_atributo"], 13:["golpe_brutal_fortalecido"],
 14:["caracteristica_de_subclasse"], 15:["furia_persistente"], 16:["aumento_no_valor_de_atributo"],
 17:["golpe_brutal_fortalecido"], 18:["forca_indomavel"], 19:["dadiva_epica"], 20:["campeao_primitivo"]}

classe={"id":"barbaro","nome":"Bárbaro","fonte":f(51),"revisao":OK,
 "descricao_curta":"Combatente movido por uma Fúria primitiva que lhe dá resistência, dano extra e vantagem com Força. Não conjura magias.",
 "dado_de_vida":12,"atributo_primario":["FOR"],"salvaguardas_primarias":["FOR","CON"],
 "nivel_subclasse":3,"conjuracao":None,
 "subclasses":["trilha_da_arvore_do_mundo","trilha_do_berserker","trilha_do_coracao_selvagem","trilha_do_fanatico"],
 "proficiencias_iniciais":[
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"FOR","nivel_dominio":"proficiente"},
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"CON","nivel_dominio":"proficiente"},
   {"id":"barbaro_pericias_iniciais","tipo":"escolha","rotulo":"Escolha 2 perícias","quantidade":2,
    "momento":"criacao",
    "de":{"catalogo":"pericias","chaves":["atletismo","intimidacao","lidar_com_animais","natureza","percepcao","sobrevivencia"]},
    "efeito_por_item_escolhido":{"tipo":"conceder_proficiencia","categoria":"pericia","chave":"{{escolhido}}","nivel_dominio":"proficiente"}},
   {"tipo":"conceder_proficiencia","categoria":"arma","chave":"categoria:simples","nivel_dominio":"proficiente"},
   {"tipo":"conceder_proficiencia","categoria":"arma","chave":"categoria:marcial","nivel_dominio":"proficiente"}],
 "treinamento_com_armadura":["leve","media","escudo"],
 "equipamento_inicial":{"opcoes":[
   {"id":"A","itens":[{"item":"machadinha","quantidade":4},{"item":"machado_grande"},{"item":"kit_de_aventureiro"}],"moedas":{"po":15}},
   {"id":"B","moedas":{"po":75}}],
   "revisao":{"status":"duvida","notas":"Ids de item dependem do catálogo do cap. 6."}},
 "progressao":[{"nivel":n,"bonus_de_proficiencia":BP[n],"caracteristicas":CAR[n],
   "colunas":{"furias":FURIAS[n],"dano_da_furia":DANO[n],"maestria_em_arma":MAEST[n]}} for n in range(1,21)],
 "colunas_da_tabela":{"furias":{"nome":"Fúrias","tipo":"inteiro"},
   "dano_da_furia":{"nome":"Dano da Fúria","tipo":"inteiro"},
   "maestria_em_arma":{"nome":"Maestria em Armas","tipo":"inteiro"}},
 "multiclasse":{"adquire":["dado_de_vida","proficiencia:arma:categoria:marcial","treinamento_armadura:escudo"],
   "fonte":f(51),"nota":"Registrado para a fase de multiclasse."}}
cl=rd('classes.json'); cl['itens']=[c for c in cl['itens'] if c['id']!='barbaro']+[classe]
cl['total']=len(cl['itens']); wr('classes.json', cl)
print('bárbaro: classe ok')
