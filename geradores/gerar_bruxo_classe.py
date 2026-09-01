# -*- coding: utf-8 -*-
"""Classe Bruxo, características e os 4 patronos."""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
CD = ["8", "mod:CAR", "prof"]

TAB = {  # nivel: (invocacoes, truques, preparadas, espacos, circulo)
 1:(1,2,2,1,1), 2:(3,2,3,2,1), 3:(3,2,4,2,2), 4:(3,3,5,2,2), 5:(5,3,6,2,3),
 6:(5,3,7,2,3), 7:(6,3,8,2,4), 8:(6,3,9,2,4), 9:(7,3,10,2,5), 10:(7,4,10,2,5),
 11:(7,4,11,3,5), 12:(8,4,11,3,5), 13:(8,4,12,3,5), 14:(8,4,12,3,5), 15:(9,4,13,3,5),
 16:(9,4,13,3,5), 17:(9,4,14,4,5), 18:(10,4,14,4,5), 19:(10,4,15,4,5), 20:(10,4,15,4,5)}
BP = {n: (2 if n<5 else 3 if n<9 else 4 if n<13 else 5 if n<17 else 6) for n in range(1,21)}
CAR = {1:["invocacoes_misticas","magia_de_pacto"], 2:["astucia_magica"], 3:["subclasse_de_bruxo"],
 4:["aumento_no_valor_de_atributo"], 5:[], 6:["caracteristica_de_subclasse"], 7:[],
 8:["aumento_no_valor_de_atributo"], 9:["contatar_patrono"], 10:["caracteristica_de_subclasse"],
 11:["arcana_mistica"], 12:["aumento_no_valor_de_atributo"], 13:["arcana_mistica"],
 14:["caracteristica_de_subclasse"], 15:["arcana_mistica"], 16:["aumento_no_valor_de_atributo"],
 17:["arcana_mistica"], 18:[], 19:["dadiva_epica"], 20:["mestre_mistico"]}

classe = {
 "id":"bruxo","nome":"Bruxo","fonte":f(69),"revisao":OK,
 "descricao_curta":"Firmou um pacto com uma entidade poderosa em troca de magia: conjura com poucos espaços de alto círculo que voltam a cada descanso e acumula Invocações Místicas.",
 "dado_de_vida":8,"atributo_primario":["CAR"],"salvaguardas_primarias":["SAB","CAR"],
 "nivel_subclasse":3,
 "conjuracao":{"tipo":"pacto","atributo":"CAR","ritual":False,"foco":["foco_arcano"],
   "preparacao":"lista_de_classe","lista_id":"bruxo","fonte":f(70),
   "nota":"Magia de Pacto: poucos espaços, todos do MESMO círculo (coluna Círculo de Magia), recuperados em Descanso Curto OU Longo."},
 "subclasses":["patrono_arquifada","patrono_celestial","patrono_grande_antigo","patrono_infero"],
 "proficiencias_iniciais":[
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"SAB","nivel_dominio":"proficiente"},
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"CAR","nivel_dominio":"proficiente"},
   {"id":"bruxo_pericias_iniciais","tipo":"escolha","rotulo":"Escolha 2 perícias","quantidade":2,
    "momento":"criacao",
    "de":{"catalogo":"pericias","chaves":["arcanismo","enganacao","historia","intimidacao",
                                          "investigacao","natureza","religiao"]},
    "efeito_por_item_escolhido":{"tipo":"conceder_proficiencia","categoria":"pericia",
                                 "chave":"{{escolhido}}","nivel_dominio":"proficiente"}},
   {"tipo":"conceder_proficiencia","categoria":"arma","chave":"categoria:simples","nivel_dominio":"proficiente"}],
 "treinamento_com_armadura":["leve"],
 "equipamento_inicial":{"opcoes":[
   {"id":"A","itens":[{"item":"armadura_de_couro"},{"item":"foice"},{"item":"adaga","quantidade":2},
                      {"item":"foco_arcano_orbe"},{"item":"livro_conhecimento_oculto"},
                      {"item":"kit_de_erudito"}],"moedas":{"po":15}},
   {"id":"B","moedas":{"po":100}}],
   "revisao":{"status":"duvida","notas":"Ids de item dependem do catálogo do cap. 6."}},
 "progressao":[{"nivel":n,"bonus_de_proficiencia":BP[n],"caracteristicas":CAR[n],
   "colunas":{"invocacoes":TAB[n][0],"truques":TAB[n][1],"magias_preparadas":TAB[n][2],
              "espacos_de_pacto":TAB[n][3],"circulo_dos_espacos":TAB[n][4]}} for n in range(1,21)],
 "colunas_da_tabela":{"invocacoes":{"nome":"Invocações","tipo":"inteiro"},
   "truques":{"nome":"Truques","tipo":"inteiro"},
   "magias_preparadas":{"nome":"Magias Preparadas","tipo":"inteiro"},
   "espacos_de_pacto":{"nome":"Espaço de Magia","tipo":"inteiro"},
   "circulo_dos_espacos":{"nome":"Círculo de Magia","tipo":"inteiro"}},
 "multiclasse":{"adquire":["dado_de_vida","treinamento_armadura:leve"],
   "nota":"Espaços de Magia de Pacto seguem regra própria no cap. 2.","fonte":f(69)}}
cl = rd('classes.json'); cl['itens']=[c for c in cl['itens'] if c['id']!='bruxo']+[classe]
cl['total']=len(cl['itens']); wr('classes.json', cl)

C = rd('caracteristicas.json'); C['itens']=[c for c in C['itens'] if c.get('classe')!='bruxo']
novos=[]
def car(id_,nome,nv,pag,desc,ef,**kw):
    d={"id":id_,"nome":nome,"classe":"bruxo","nivel":nv,"fonte":f(pag),
       "revisao":kw.pop("revisao",OK),"descricao_curta":desc,"efeitos":ef}
    d.update(kw); novos.append(d)

car("invocacoes_misticas","Invocações Místicas",1,69,
 "Aprende Invocações Místicas conforme a coluna Invocações. Só pode escolher as que atende aos pré-requisitos, não repete a mesma (salvo se marcada repetível) e, a cada nível de Bruxo, pode trocar uma que não seja pré-requisito de outra que tenha.",
 [{"id":"bruxo_invocacoes","tipo":"escolha","rotulo":"Escolha suas Invocações Místicas",
   "quantidade":"coluna:invocacoes","momento":"nivel_1","reescolhivel":True,
   "reescolha_em":"cada_nivel_de_bruxo","reescolha_quantidade":1,
   "restricao_de_reescolha":"não pode trocar uma invocação que seja pré-requisito de outra que você tem",
   "de":{"catalogo":"invocacoes_misticas","todo_o_catalogo":True,"respeitar_pre_requisitos":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}])

car("magia_de_pacto","Magia de Pacto",1,69,
 "Conjura com Carisma. Espaços de Magia de Pacto: poucos e TODOS do mesmo círculo (colunas Espaço de Magia e Círculo de Magia), recuperados em Descanso Curto ou Longo. Truques e magias preparadas da lista do Bruxo conforme a tabela.",
 [{"tipo":"conceder_slot","modo":"pacto","tabela_progressao_id":"bruxo",
   "coluna_quantidade":"espacos_de_pacto","coluna_circulo":"circulo_dos_espacos",
   "todos_do_mesmo_circulo":True,"recarga":["descanso_curto","descanso_longo"],
   "nota":"Conjurar uma magia de círculo inferior com um espaço de Pacto a eleva ao círculo do espaço."},
  {"tipo":"preparar_magias","formula_quantidade":["coluna:magias_preparadas"],
   "atributo_conjuracao":"CAR","fonte_das_magias":"lista_de_classe","lista_id":"bruxo",
   "restricao":"de círculo não superior ao mostrado na coluna Círculo de Magia",
   "magias_sempre_preparadas_nao_contam":True},
  {"tipo":"desbloquear_magias","lista_id":"bruxo","modo":"disponivel_para_preparar",
   "atributo_conjuracao":"CAR"},
  {"id":"bruxo_truques","tipo":"escolha","rotulo":"Escolha truques de Bruxo",
   "quantidade":"coluna:truques","momento":"nivel_1","reescolhivel":True,
   "reescolha_em":"cada_nivel_de_bruxo","reescolha_quantidade":1,
   "recomendados":["prestidigitacao_arcana","raio_mistico"],
   "de":{"catalogo":"magias","filtro":{"nivel":0,"lista":"bruxo"}},
   "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"bruxo","modo":"conhecida",
                                "magia":"{{escolhido}}"}},
  {"id":"bruxo_preparadas","tipo":"escolha","rotulo":"Prepare magias de Bruxo",
   "quantidade":"coluna:magias_preparadas","momento":"nivel_1","reescolhivel":True,
   "reescolha_em":"cada_nivel_de_bruxo","reescolha_quantidade":1,
   "recomendados":["danacao","enfeiticar_pessoa"],
   "de":{"catalogo":"magias","filtro":{"nivel_minimo":1,"lista":"bruxo",
                                       "circulo_maximo":"coluna:circulo_dos_espacos"}},
   "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"bruxo","modo":"preparada",
                                "magia":"{{escolhido}}"}}],
 cd_para_evitar_sua_magia=CD)

car("astucia_magica","Astúcia Mágica",2,70,
 "Rito de 1 minuto que recupera espaços de Magia de Pacto gastos em número igual à metade do máximo (arredondado para cima). Recarrega em Descanso Longo.",
 [{"tipo":"recurso_com_recarga","id":"astucia_magica","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"recuperar_espacos_de_magia","gatilho":"rito_de_1_minuto",
   "formula_espacos":{"op":"div_arred_cima","args":["coluna:espacos_de_pacto","2"]},
   "consome_recurso":"astucia_magica"}])

car("subclasse_de_bruxo","Subclasse de Bruxo",3,71,
 "Escolhe um patrono; as características chegam nos níveis 3, 6, 10 e 14.",
 [{"id":"bruxo_escolha_de_subclasse","tipo":"escolha","rotulo":"Escolha um patrono","quantidade":1,
   "momento":"nivel_3","de":{"catalogo":"subclasses","filtro":{"classe":"bruxo"}},
   "efeito_por_item_escolhido":{"tipo":"conceder_subclasse","chave":"{{escolhido}}"}}])

car("contatar_patrono","Contatar Patrono",9,71,
 "Tem sempre Contato Extraplanar preparada e a conjura sem gastar espaço para falar com o patrono, passando automaticamente na salvaguarda da magia. Recarrega em Descanso Longo.",
 [{"tipo":"desbloquear_magias","lista_id":"bruxo","modo":"sempre_preparada",
   "magias":["contato_extraplanar"]},
  {"tipo":"conjurar_sem_espaco","magia":"contato_extraplanar","frequencia":"uma_vez_por_descanso_longo",
   "recarga":["descanso_longo"],"efeito_extra":"sucesso automático na salvaguarda da magia"}])

car("arcana_mistica","Arcana Mística",11,71,
 "Escolhe uma magia de Bruxo de 6º círculo conjurável uma vez sem gastar espaço; ganha outra de 7º no nível 13, de 8º no 15 e de 9º no 17. Todos os usos voltam em Descanso Longo, e a cada nível pode trocar uma delas por outra do mesmo círculo.",
 [{"id":"arcana_mistica_escolha","tipo":"escolha","rotulo":"Escolha a magia de arcanum",
   "quantidade":1,"momento":"nivel_da_caracteristica","reescolhivel":True,
   "reescolha_em":"cada_nivel_de_bruxo",
   "circulo_por_nivel":{"11":6,"13":7,"15":8,"17":9},
   "de":{"catalogo":"magias","filtro":{"lista":"bruxo","nivel":"$circulo_do_nivel"}},
   "efeito_por_item_escolhido":{"tipo":"conjurar_sem_espaco","magia":"{{escolhido}}",
     "frequencia":"uma_vez_por_descanso_longo","recarga":["descanso_longo"]}}],
 niveis=[11,13,15,17], repetivel=True, tipo_de_repeticao="nova_escolha",
 nota_de_repeticao="Cada nível concede um arcanum de círculo diferente: 6º no 11, 7º no 13, 8º no 15, 9º no 17.")

car("mestre_mistico","Mestre Místico",20,71,
 "Astúcia Mágica passa a restaurar TODOS os espaços de Magia de Pacto gastos.",
 [{"tipo":"melhorar_caracteristica","alvo":"astucia_magica",
   "efeitos":[{"tipo":"recuperar_espacos_de_magia","formula_espacos":["coluna:espacos_de_pacto"],
               "modo":"substitui_formula"}]}])

# ------------------------------------------------------------------ patronos
def tabela_patrono(nome, linhas, pag):
    return {"tipo":"magias_de_patrono","tabela":{"nome":nome,"fonte":f(pag),
            "linhas":[{"nivel":n,"magias":ms} for n,ms in linhas]},
            "modo":"sempre_preparada","nao_conta_para_o_limite":True}

SUB="patrono_arquifada"
car("magias_de_pacto_da_arquifada","Magias de Pacto da Arquifada",3,75,
 "Magias sempre preparadas conforme a tabela Magias da Arquifada, sem contar para o limite de preparadas.",
 [tabela_patrono("Magias da Arquifada", [
   (3,["acalmar_emocoes","fogo_das_fadas","forca_espectral","passo_nebuloso","sono"]),
   (5,["crescimento_de_plantas","piscar"]), (7,["dominar_fera","invisibilidade_maior"]),
   (9,["dominar_pessoa","similaridade"])], 75)], subclasse=SUB)
car("passos_feericos","Passos Feéricos",3,75,
 "Conjura Passo Nebuloso sem gastar espaço um número de vezes igual ao modificador de Carisma (mínimo 1), recarregando em Descanso Longo, e escolhe um efeito adicional ao conjurar.",
 [{"tipo":"recurso_com_recarga","id":"passos_feericos",
   "formula_maximo":{"op":"max","args":["1","mod:CAR"]},"recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"conjurar_sem_espaco","magia":"passo_nebuloso","consome_recurso":"passos_feericos"},
  {"id":"passos_feericos_efeito","tipo":"escolha","rotulo":"Escolha o efeito do Passo",
   "quantidade":1,"momento":"ao_conjurar",
   "de":{"catalogo":"efeitos_dos_passos_feericos","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}],
 subclasse=SUB)
car("fuga_em_nevoa","Fuga em Névoa",6,75,
 "Conjura Passo Nebuloso como Reação ao sofrer dano, e ganha os efeitos Passo Desvanecedor e Passo Terrível entre as opções de Passos Feéricos.",
 [{"tipo":"conjurar_sem_espaco","magia":"passo_nebuloso","custo":"reacao","gatilho":"sofrer_dano"},
  {"tipo":"melhorar_caracteristica","alvo":"passos_feericos",
   "efeitos":[{"tipo":"efeito_narrativo","chave":"novas_opcoes_de_passo",
               "texto":"Passo Desvanecedor e Passo Terrível entram nas opções."}]}], subclasse=SUB)
car("defesas_sedutoras","Defesas Sedutoras",10,76,
 "Imune à condição Enfeitiçado. Reação ao ser acertado: reduz o dano à metade e força salvaguarda de Sabedoria; falhando, o atacante sofre dano Psíquico igual ao que você sofreu. Recarrega em Descanso Longo ou gastando um espaço de Pacto.",
 [{"tipo":"alterar_condicao","condicao_id":"enfeiticado","operacao":"imunidade"},
  {"tipo":"recurso_com_recarga","id":"defesas_sedutoras","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso",
   "recuperacao_alternativa":{"gasta_espaco_de_magia":{"tipo":"pacto"},"custo":"livre"}},
  {"tipo":"reducao_de_dano","custo":"reacao","formula":{"op":"div_arred_baixo","args":["dano","2"]},
   "tipos_de_dano":["todos"],"consome_recurso":"defesas_sedutoras"},
  {"tipo":"dano","beneficiario":"atacante","tipo_dano":"psiquico","formula_dado":"dano_que_voce_sofreu",
   "salvaguarda":{"atributo":"SAB","cd":CD}}],
 subclasse=SUB)
car("magia_sedutora","Magia Sedutora",14,76,
 "Imediatamente após conjurar magia de Encantamento ou Ilusão com uma ação e um espaço, conjura Passo Nebuloso como parte da mesma ação e sem gastar espaço.",
 [{"tipo":"conjurar_sem_espaco","magia":"passo_nebuloso","momento":"apos_magia_de_encantamento_ou_ilusao",
   "custo":"nenhum","frequencia":"a_vontade"}], subclasse=SUB)

SUB="patrono_celestial"
car("luz_medicinal","Luz Medicinal",3,76,
 "Reserva de d6s igual a 1 mais seu nível de Bruxo. Ação Bônus para curar você ou criatura à vista a até 18 m, gastando até seu modificador de Carisma em dados por uso. Recarrega em Descanso Longo.",
 [{"tipo":"reserva_de_dados","id":"luz_medicinal","dado":"d6",
   "formula_quantidade":{"op":"soma","args":["1","nivel_classe:bruxo"]},
   "gasto_maximo_por_uso":{"op":"max","args":["1","mod:CAR"]},"recarga":["descanso_longo"]},
  {"tipo":"cura","custo":"acao_bonus","alcance_m":18,"formula":["dados_gastos:luz_medicinal"],
   "beneficiario":"voce_ou_criatura_a_vista"}], subclasse=SUB)
car("magias_de_pacto_do_celestial","Magias de Pacto do Celestial",3,76,
 "Magias sempre preparadas conforme a tabela Magias do Celestial, sem contar para o limite.",
 [tabela_patrono("Magias do Celestial", [
   (3,["auxilio","chama_sagrada","curar_ferimentos","luz","raio_guia","restauracao_menor"]),
   (5,["luz_do_dia","revivificar"]), (7,["defensor_da_fe","muralha_de_fogo"]),
   (9,["convocar_celestial","restauracao_maior"])], 76)], subclasse=SUB)
car("alma_radiante","Alma Radiante",6,76,
 "Resistência a dano Radiante. Uma vez por turno, ao conjurar magia que cause dano Ígneo ou Radiante, soma o modificador de Carisma ao dano contra um dos alvos.",
 [{"tipo":"alterar_dano","tipo_dano":"radiante","operacao":"resistencia"},
  {"tipo":"modificador","alvo":"jogada_de_dano","valor":["mod:CAR"],"empilha":"soma",
   "frequencia":"uma_vez_por_turno","condicao":{"alguma":["dano:igneo","dano:radiante"]},
   "limite":"um alvo da magia"}], subclasse=SUB)
car("resiliencia_celestial","Resiliência Celestial",10,77,
 "Ganha PV temporários iguais ao nível de Bruxo mais o modificador de Carisma ao usar Astúcia Mágica ou completar um descanso; até cinco criaturas à vista ganham metade do nível mais o modificador.",
 [{"tipo":"pontos_de_vida_temporarios","formula":["nivel_classe:bruxo","mod:CAR"],
   "gatilho":["usar:astucia_magica","descanso_curto","descanso_longo"]},
  {"tipo":"pontos_de_vida_temporarios","beneficiario":"ate_5_criaturas_a_vista",
   "formula":[{"op":"div_arred_baixo","args":["nivel_classe:bruxo","2"]},"mod:CAR"]}], subclasse=SUB)
car("vinganca_calcinante","Vingança Calcinante",14,77,
 "Quando você ou aliado a até 18 m for realizar Salvaguarda Contra Morte, a criatura recupera metade dos PV máximos e pode encerrar Caído; criaturas à escolha a até 9 m dela sofrem 2d8 + modificador de Carisma de dano Radiante e ficam Cegas até o fim do turno. Recarrega em Descanso Longo.",
 [{"tipo":"recurso_com_recarga","id":"vinganca_calcinante","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"cura","formula":[{"op":"div_arred_baixo","args":["pv_maximo","2"]}],
   "beneficiario":"voce_ou_aliado_a_ate_18m","gatilho":"antes_de_salvaguarda_contra_morte"},
  {"tipo":"remover_condicao","condicoes":["caido"],"quantidade":1,"beneficiario":"alvo_curado"},
  {"tipo":"dano","formula_dado":"2d8","somar":["mod:CAR"],"tipo_dano":"radiante",
   "alvo":"criaturas_a_escolha_a_ate_9m_do_alvo"},
  {"tipo":"conceder_condicao","condicao_id":"cego","beneficiario":"alvos_do_dano",
   "duracao":"ate_o_fim_do_turno_atual"}], subclasse=SUB)

SUB="patrono_grande_antigo"
car("magias_de_pacto_do_grande_antigo","Magias de Pacto do Grande Antigo",3,77,
 "Magias sempre preparadas conforme a tabela Magias do Grande Antigo, sem contar para o limite.",
 [tabela_patrono("Magias do Grande Antigo", [
   (3,["detectar_pensamentos","forca_espectral","gargalhada_nefasta_de_tasha","sussurros_dissonantes"]),
   (5,["clarividencia","fome_de_hadar"]), (7,["confusao","invocar_aberracao"]),
   (9,["modificar_memoria","telecinese"])], 77)], subclasse=SUB)
car("magias_psiquicas","Magias Psíquicas",3,78,
 "Pode mudar para Psíquico o tipo de dano de uma magia de Bruxo, e conjurar magias de Bruxo de Encantamento ou Ilusão sem componentes Verbais nem Somáticos.",
 [{"tipo":"alterar_tipo_de_dano_da_magia","opcoes":["psiquico"],"escopo":{"lista":"bruxo","causa_dano":True}},
  {"tipo":"dispensar_componentes","componentes":["V","S"],
   "escopo":{"lista":"bruxo","escola":["encantamento","ilusao"]}}], subclasse=SUB)
car("mente_desperta","Mente Desperta",3,78,
 "Ação Bônus para abrir conexão telepática com criatura à vista a até 9 m, alcançando 1,5 km vezes o modificador de Carisma, por minutos iguais ao seu nível de Bruxo.",
 [{"tipo":"efeito_narrativo","chave":"conexao_telepatica","custo":"acao_bonus",
   "alcance_de_uso_m":9,"alcance_da_conexao_km":{"op":"max","args":["1.5",{"op":"mult","args":["1.5","mod:CAR"]}]},
   "duracao":"minutos iguais ao nível de Bruxo",
   "texto":"Exige idioma comum usado mentalmente. Encerra antes se você conectar com outra criatura."}],
 subclasse=SUB)
car("combatente_clarividente","Combatente Clarividente",6,78,
 "Ao formar a ligação de Mente Desperta, força salvaguarda de Sabedoria: falhando, a criatura tem Desvantagem em ataques contra você e você tem Vantagem contra ela pela duração. Recarrega em descanso ou gastando espaço de Pacto.",
 [{"tipo":"recurso_com_recarga","id":"combatente_clarividente","formula_maximo":["1"],
   "recarga":["descanso_curto","descanso_longo"],"consumo":"por_uso",
   "recuperacao_alternativa":{"gasta_espaco_de_magia":{"tipo":"pacto"},"custo":"livre"}},
  {"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"desvantagem","beneficiario":"alvo",
   "salvaguarda":{"atributo":"SAB","cd":CD},"condicao":{"todas":["alvo_do_ataque_e_voce"]}},
  {"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem",
   "condicao":{"todas":["alvo_e_a_criatura_ligada"]}}], subclasse=SUB)
car("danacao_mistica","Danação Mística",10,78,
 "Tem sempre Danação preparada; ao conjurá-la escolhendo um atributo, o alvo também tem Desvantagem nas salvaguardas daquele atributo pela duração.",
 [{"tipo":"desbloquear_magias","lista_id":"bruxo","modo":"sempre_preparada","magias":["danacao"]},
  {"tipo":"vantagem","alvo":"salvaguarda","modo":"desvantagem","beneficiario":"alvo_da_danacao",
   "condicao":{"todas":["atributo_escolhido_na_danacao"]}}], subclasse=SUB)
car("escudo_mental","Escudo Mental",10,78,
 "Seus pensamentos não podem ser lidos sem permissão. Resistência a dano Psíquico, e quem causar dano Psíquico a você sofre a mesma quantidade.",
 [{"tipo":"alterar_dano","tipo_dano":"psiquico","operacao":"resistencia"},
  {"tipo":"dano","beneficiario":"quem_causou_dano_psiquico","tipo_dano":"psiquico",
   "formula_dado":"dano_que_voce_sofreu"},
  {"tipo":"efeito_narrativo","chave":"mente_ilegivel",
   "texto":"Seus pensamentos não podem ser lidos por telepatia ou outros meios sem sua permissão."}],
 subclasse=SUB)
car("criar_servo","Criar Servo",14,78,
 "Invocar Aberração pode dispensar Concentração, virando 1 minuto de duração, com a Aberração ganhando PV temporários iguais ao nível de Bruxo mais o modificador de Carisma; e ela causa dano Psíquico extra ao atingir alvo sob sua Danação.",
 [{"tipo":"efeito_narrativo","chave":"invocar_aberracao_sem_concentracao",
   "texto":"Invocar Aberração sem Concentração, duração 1 minuto; a Aberração ganha PV temporários iguais ao nível de Bruxo mais o modificador de Carisma."},
  {"tipo":"dano","tipo_dano":"psiquico","modo":"dano_adicional","frequencia":"uma_vez_por_turno",
   "condicao":{"todas":["alvo_sob_danacao"]},"formula_dado":"dano_bonus_da_danacao",
   "origem":"aberracao_invocada"}], subclasse=SUB)

SUB="patrono_infero"
car("bencao_do_tenebroso","Bênção do Tenebroso",3,79,
 "Ao reduzir um inimigo a 0 PV — ou quando alguém reduz um inimigo a até 3 m de você — ganha PV temporários iguais ao modificador de Carisma mais o nível de Bruxo (mínimo 1).",
 [{"tipo":"pontos_de_vida_temporarios","formula":["mod:CAR","nivel_classe:bruxo"],"minimo":1,
   "gatilho":["reduzir_inimigo_a_zero_pv","aliado_reduz_inimigo_a_ate_3m"]}], subclasse=SUB)
car("magias_de_pacto_do_infero","Magias de Pacto do Ínfero",3,79,
 "Magias sempre preparadas conforme a tabela Magias do Ínfero, sem contar para o limite.",
 [tabela_patrono("Magias do Ínfero", [
   (3,["comando","maos_flamejantes","raio_ardente","sugestao"]),
   (5,["bola_de_fogo","nuvem_fetida"]), (7,["escudo_ardente","muralha_de_fogo"]),
   (9,["missao","praga_de_insetos"])], 79)], subclasse=SUB)
car("a_sorte_do_proprio_tenebroso","A Sorte do Próprio Tenebroso",6,79,
 "Soma 1d10 a um teste de atributo ou salvaguarda depois de ver a jogada e antes dos efeitos. Usos iguais ao modificador de Carisma (mínimo 1), no máximo um por jogada, recarregados em Descanso Longo.",
 [{"tipo":"recurso_com_recarga","id":"sorte_do_tenebroso",
   "formula_maximo":{"op":"max","args":["1","mod:CAR"]},"recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"modificador","alvo":"teste_de_atributo","valor":["1d10"],"empilha":"soma",
   "momento":"apos_a_jogada","frequencia":"uma_vez_por_jogada","consome_recurso":"sorte_do_tenebroso"},
  {"tipo":"modificador","alvo":"salvaguarda","valor":["1d10"],"empilha":"soma",
   "momento":"apos_a_jogada","frequencia":"uma_vez_por_jogada","consome_recurso":"sorte_do_tenebroso"}],
 subclasse=SUB)
car("resistencia_infera","Resistência Ínfera",10,79,
 "A cada descanso escolhe um tipo de dano, exceto Energético, e tem Resistência a ele até escolher outro.",
 [{"id":"resistencia_infera_escolha","tipo":"escolha","rotulo":"Escolha um tipo de dano",
   "quantidade":1,"momento":"descanso_curto_ou_longo","reescolhivel":True,
   "de":{"catalogo":"tipos_de_dano","filtro":{"exceto":["energetico"]},
         "chaves":["acido","contundente","cortante","eletrico","gelido","igneo","necrotico",
                   "perfurante","psiquico","radiante","trovejante","venenoso"]},
   "efeito_por_item_escolhido":{"tipo":"alterar_dano","tipo_dano":"{{escolhido}}","operacao":"resistencia"}}],
 subclasse=SUB)
car("lancar_no_inferno","Lançar no Inferno",14,79,
 "Uma vez por turno, ao acertar uma criatura, ela faz salvaguarda de Carisma ou desaparece nos Planos Inferiores: sofre 8d10 de dano Psíquico se não for Ínfero e fica Incapacitada até o fim do seu próximo turno, quando volta. Recarrega em Descanso Longo ou gastando espaço de Pacto.",
 [{"tipo":"recurso_com_recarga","id":"lancar_no_inferno","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso",
   "recuperacao_alternativa":{"gasta_espaco_de_magia":{"tipo":"pacto"},"custo":"livre"}},
  {"tipo":"dano","frequencia":"uma_vez_por_turno","gatilho":"acerto_com_jogada_de_ataque",
   "formula_dado":"8d10","tipo_dano":"psiquico",
   "salvaguarda":{"atributo":"CAR","cd":CD},"condicao":{"nao":"alvo_e_infero"}},
  {"tipo":"conceder_condicao","condicao_id":"incapacitado","beneficiario":"alvo",
   "duracao":"ate_o_fim_do_seu_proximo_turno"}], subclasse=SUB)

C['itens'] = C['itens'] + novos; C['total'] = len(C['itens']); wr('caracteristicas.json', C)

wr('catalogos/efeitos_dos_passos_feericos.json', {"catalogo":"efeitos_dos_passos_feericos",
 "nome":"Efeitos dos Passos Feéricos","fonte":f(75),"total":4,"itens":[
  {"id":"passo_provocante","nome":"Passo Provocante","nivel_minimo":3,
   "descricao_curta":"Criaturas a até 1,5 m do espaço que você deixou fazem salvaguarda de Sabedoria ou têm Desvantagem em ataques contra outros que não você até o início do seu próximo turno."},
  {"id":"passo_revigorante","nome":"Passo Revigorante","nivel_minimo":3,
   "descricao_curta":"Você ou criatura à vista a até 3 m ganha 1d10 Pontos de Vida Temporários."},
  {"id":"passo_desvanecedor","nome":"Passo Desvanecedor","nivel_minimo":6,
   "descricao_curta":"Fica Invisível até o início do seu próximo turno ou até atacar, causar dano ou conjurar."},
  {"id":"passo_terrivel","nome":"Passo Terrível","nivel_minimo":6,
   "descricao_curta":"Criaturas a até 1,5 m do espaço de saída ou de chegada fazem salvaguarda de Sabedoria ou sofrem 2d10 de dano Psíquico."}]})

S = rd('subclasses.json'); S['itens']=[s for s in S['itens'] if s.get('classe')!='bruxo']
NOVAS=[("patrono_arquifada","Patrono Arquifada",75,"Pacto fundado no poder de Faéria: teleporte, encantamento e defesas sedutoras.",
        ["magias_de_pacto_da_arquifada","passos_feericos","fuga_em_nevoa","defesas_sedutoras","magia_sedutora"]),
       ("patrono_celestial","Patrono Celestial",76,"Pacto com os Planos Superiores: cura, luz radiante e resiliência.",
        ["luz_medicinal","magias_de_pacto_do_celestial","alma_radiante","resiliencia_celestial","vinganca_calcinante"]),
       ("patrono_grande_antigo","Patrono O Grande Antigo",77,"Conhecimento de entidades inefáveis: telepatia, dano psíquico e servos aberrantes.",
        ["magias_de_pacto_do_grande_antigo","magias_psiquicas","mente_desperta","combatente_clarividente",
         "danacao_mistica","escudo_mental","criar_servo"]),
       ("patrono_infero","Patrono Ínfero",78,"Pacto com os Planos Inferiores: vigor tenebroso, sorte alterada e fogo infernal.",
        ["bencao_do_tenebroso","magias_de_pacto_do_infero","a_sorte_do_proprio_tenebroso",
         "resistencia_infera","lancar_no_inferno"])]
S['itens']=S['itens']+[{"id":i,"nome":n,"classe":"bruxo","fonte":f(p),"revisao":OK,
  "descricao_curta":d,"niveis_de_caracteristica":[3,6,10,14],"caracteristicas":c}
  for i,n,p,d,c in NOVAS]
S['total']=len(S['itens']); wr('subclasses.json', S)
print("classes:", cl['total'], "| caracteristicas:", C['total'], "| subclasses:", S['total'])
