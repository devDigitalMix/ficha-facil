# -*- coding: utf-8 -*-
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D,p),encoding='utf-8'))
def wr(p,o): json.dump(o,open(os.path.join(D,p),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
CD=["8","mod:FOR","prof"]
C=rd('caracteristicas.json'); C['itens']=[c for c in C['itens'] if c.get('classe')!='barbaro']
N=[]
def car(i,nome,nv,pag,desc,ef,**kw):
    d={"id":i,"nome":nome,"classe":"barbaro","nivel":nv,"fonte":f(pag),
       "revisao":kw.pop("revisao",OK),"descricao_curta":desc,"efeitos":ef}
    d.update(kw); N.append(d)
ATIVA={"todas":["ativo:furia"]}

car("furia","Fúria",1,51,
 "Ação Bônus para entrar em Fúria (não pode com armadura Pesada). Enquanto ativa: Resistência a Contundente, Cortante e Perfurante; bônus de dano em ataques com Força; Vantagem em testes e salvaguardas de Força; não pode conjurar nem manter Concentração. Dura até o fim do próximo turno, estendendo-se com ataque, salvaguarda forçada ou Ação Bônus, até 10 minutos.",
 [{"tipo":"recurso_com_recarga","id":"furia","nome":"Fúrias","formula_maximo":["coluna:furias"],
   "recarga":[{"gatilho":"descanso_curto","quantidade":1},{"gatilho":"descanso_longo","quantidade":"todos"}],
   "consumo":"por_uso"},
  {"tipo":"furia","recurso_id":"furia","custo":"acao_bonus",
   "pre_requisitos":[{"tipo":"estado","nao":"armadura:pesada"}],
   "duracao":"ate_o_fim_do_seu_proximo_turno","duracao_maxima":"10 minutos",
   "extensao":{"gatilhos":["jogada_de_ataque_contra_inimigo","forcar_salvaguarda_de_inimigo","acao_bonus"],
               "efeito":"estende até o fim do seu próximo turno"},
   "encerra_se":[{"gatilho":"vestir_armadura_pesada"},{"condicao_id":"incapacitado"}],
   "efeitos":[{"tipo":"alterar_dano","tipo_dano":"contundente","operacao":"resistencia"},
              {"tipo":"alterar_dano","tipo_dano":"cortante","operacao":"resistencia"},
              {"tipo":"alterar_dano","tipo_dano":"perfurante","operacao":"resistencia"},
              {"tipo":"modificador","alvo":"jogada_de_dano","valor":["coluna:dano_da_furia"],
               "empilha":"soma","condicao":{"todas":["ataque_com_forca"]}},
              {"tipo":"vantagem","alvo":"teste_de_atributo:FOR","modo":"vantagem"},
              {"tipo":"vantagem","alvo":"salvaguarda:FOR","modo":"vantagem"},
              {"tipo":"impedir","alvo":"concentracao"}]}])

car("defesa_sem_armadura_barbaro","Defesa sem Armadura",1,51,
 "Sem armadura, sua CA base é 10 + modificador de Destreza + modificador de Constituição. Pode usar Escudo e manter o benefício.",
 [{"tipo":"ca_base","formula":["10","mod:DES","mod:CON"],"permite_escudo":True,
   "condicao":{"todas":["flag:sem_armadura"]},"empilha":"substitui"}])

car("maestria_em_arma_barbaro","Maestria em Arma",1,51,
 "Usa as propriedades de maestria de tipos de armas Corpo a Corpo Simples ou Marciais à escolha, conforme a coluna Maestria em Armas. Troca uma escolha a cada Descanso Longo.",
 [{"id":"barbaro_maestrias","tipo":"escolha","rotulo":"Escolha os tipos de arma com maestria",
   "quantidade":"coluna:maestria_em_arma","momento":"nivel_1","reescolhivel":True,
   "reescolha_em":"descanso_longo","reescolha_quantidade":1,
   "de":{"catalogo":"itens","pendente":True,
         "filtro":{"categoria":"arma","grupo":["simples","marcial"],"alcance":"corpo_a_corpo"}},
   "efeito_por_item_escolhido":{"tipo":"efeito_narrativo","chave":"maestria_liberada","arma":"{{escolhido}}"}}])

car("ataque_imprudente","Ataque Imprudente",2,52,
 "Na primeira jogada de ataque do turno, pode atacar imprudentemente: Vantagem em ataques com Força até o início do próximo turno, mas ataques contra você também têm Vantagem.",
 [{"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem",
   "condicao":{"todas":["ataque_com_forca"]},"duracao":"ate_inicio_do_seu_proximo_turno"},
  {"tipo":"vantagem","alvo":"jogada_de_ataque_contra_voce","modo":"vantagem",
   "duracao":"ate_inicio_do_seu_proximo_turno"}])

car("sentido_de_perigo","Sentido de Perigo",2,52,
 "Vantagem em salvaguardas de Destreza, salvo se estiver Incapacitado.",
 [{"tipo":"vantagem","alvo":"salvaguarda:DES","modo":"vantagem","condicao":{"nao":"condicao:incapacitado"}}])

car("conhecimento_primordial","Conhecimento Primordial",3,52,
 "Mais uma perícia da lista do Bárbaro. Em Fúria, pode fazer testes de Acrobacia, Furtividade, Intimidação, Percepção ou Sobrevivência como testes de Força.",
 [{"id":"barbaro_pericia_extra","tipo":"escolha","rotulo":"Escolha mais uma perícia","quantidade":1,
   "momento":"nivel_3",
   "de":{"catalogo":"pericias","chaves":["atletismo","intimidacao","lidar_com_animais","natureza","percepcao","sobrevivencia"]},
   "efeito_por_item_escolhido":{"tipo":"conceder_proficiencia","categoria":"pericia","chave":"{{escolhido}}","nivel_dominio":"proficiente"}},
  {"tipo":"substituir_atributo","de":"atributo_normal","para":"FOR","escopo":["teste_de_atributo"],
   "aplica_a":["acrobacia","furtividade","intimidacao","percepcao","sobrevivencia"],"condicao":ATIVA}])

car("subclasse_de_barbaro","Subclasse de Bárbaro",3,52,
 "Escolhe uma trilha; as características chegam nos níveis 3, 6, 10 e 14.",
 [{"id":"barbaro_escolha_de_subclasse","tipo":"escolha","rotulo":"Escolha uma trilha","quantidade":1,
   "momento":"nivel_3","de":{"catalogo":"subclasses","filtro":{"classe":"barbaro"}},
   "efeito_por_item_escolhido":{"tipo":"conceder_subclasse","chave":"{{escolhido}}"}}])

car("movimento_rapido","Movimento Rápido",5,52,
 "Deslocamento aumenta em 3 metros enquanto não usar Armadura Pesada.",
 [{"tipo":"modificador","alvo":"deslocamento","valor":["3"],"unidade":"m","empilha":"soma",
   "condicao":{"nao":"armadura:pesada"}}])

car("bote_instintivo","Bote Instintivo",7,53,
 "Como parte da Ação Bônus para entrar em Fúria, move até metade do Deslocamento.",
 [{"tipo":"efeito_narrativo","chave":"movimento_ao_entrar_em_furia","gatilho":"entrar_em_furia",
   "texto":"Move até metade do Deslocamento como parte da mesma Ação Bônus."}])

car("instintos_primitivos","Instintos Primitivos",7,53,
 "Vantagem nas jogadas de Iniciativa.",
 [{"tipo":"vantagem","alvo":"iniciativa","modo":"vantagem"}])

car("golpe_brutal","Golpe Brutal",9,53,
 "Usando Ataque Imprudente, abre mão da Vantagem numa jogada de ataque com Força (que não tenha Desvantagem): acertando, causa 1d10 extra do tipo da arma e aplica um efeito de Golpe Brutal à escolha.",
 [{"tipo":"dano","formula_dado":"1d10","tipo_dano":"mesmo_do_ataque","modo":"dano_adicional",
   "condicao":{"todas":["usou:ataque_imprudente","abriu_mao_da_vantagem"],"nao":"desvantagem_na_jogada"}},
  {"id":"barbaro_golpe_brutal","tipo":"escolha","rotulo":"Escolha o efeito de Golpe Brutal",
   "quantidade":1,"momento":"no_acerto","reescolhivel":True,
   "de":{"catalogo":"efeitos_de_golpe_brutal","todo_o_catalogo":True,"respeitar_nivel_minimo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}])

car("furia_implacavel","Fúria Implacável",11,53,
 "Ao chegar a 0 PV em Fúria sem morrer na hora, salvaguarda de Constituição CD 10: passando, seus PV viram o dobro do seu nível de Bárbaro. A CD sobe 5 a cada uso e volta a 10 em qualquer descanso.",
 [{"tipo":"cura","formula":[{"op":"mult","args":["2","nivel_classe:barbaro"]}],"modo":"define_pv",
   "gatilho":"chegar_a_0_pv","condicao":ATIVA,
   "salvaguarda":{"atributo":"CON","cd":10,"cd_escalonavel":{"incremento":5,"reseta_em":["descanso_curto","descanso_longo"]}}}])

car("golpe_brutal_fortalecido","Golpe Brutal Fortalecido",13,53,
 "Nível 13: Golpe Atordoante e Golpe Destruidor entram nas opções. Nível 17: o dano extra vira 2d10 e você aplica dois efeitos por uso.",
 [{"tipo":"melhorar_caracteristica","alvo":"golpe_brutal",
   "efeitos":[{"tipo":"efeito_narrativo","chave":"novas_opcoes_de_golpe_brutal",
               "texto":"Golpe Atordoante e Golpe Destruidor passam a estar disponíveis."}]}],
 niveis=[13,17], repetivel=True, tipo_de_repeticao="melhoria",
 melhorias_por_nivel={"17":{"formula_dado":"2d10","efeitos_por_uso":2}},
 revisao={"status":"ok","notas":"A tabela (p. 52) chama o nível 13 de 'Golpe Brutal Aprimorado' e o 17 de 'Golpe Brutal Aprimorado'; os títulos no corpo do texto dizem 'Golpe Brutal Fortalecido' nos dois. Adotei o título do corpo, conforme a regra combinada."},
 nome_na_tabela="Golpe Brutal Aprimorado")

car("furia_persistente","Fúria Persistente",15,53,
 "Ao jogar Iniciativa, recupera todos os usos de Fúria (uma vez por Descanso Longo). A Fúria passa a durar 10 minutos sem precisar ser estendida, e só encerra se você ficar Inconsciente ou vestir armadura Pesada.",
 [{"tipo":"restaurar_recurso","recurso_id":"furia","quantidade":"total","gatilho":"jogar_iniciativa",
   "recarga":["descanso_longo"]},
  {"tipo":"melhorar_caracteristica","alvo":"furia",
   "efeitos":[{"tipo":"furia","duracao":"10 minutos","modo":"substitui_duracao",
               "encerra_se":[{"condicao_id":"inconsciente"},{"gatilho":"vestir_armadura_pesada"}],
               "dispensa_extensao":True}]}])

car("forca_indomavel","Força Indomável",18,53,
 "Se o total do seu teste ou salvaguarda de Força for menor que seu valor de Força, use o valor de Força no lugar.",
 [{"tipo":"tratar_resultado_minimo","alvo":["teste_de_atributo:FOR","salvaguarda:FOR"],"minimo":"attr:FOR"}])

car("campeao_primitivo","Campeão Primitivo",20,53,
 "Força e Constituição aumentam em 4, até o máximo de 25.",
 [{"tipo":"aumento_atributo","distribuicao":{"FOR":4,"CON":4},"limite":25}])

# ------------------------------------------------ Trilha da Árvore do Mundo
S="trilha_da_arvore_do_mundo"
car("vitalidade_da_arvore","Vitalidade da Árvore",3,54,
 "Ao entrar em Fúria, ganha PV temporários iguais ao nível de Bárbaro. E, no início de cada turno em Fúria, pode dar a outra criatura a até 3 m PV temporários iguais a tantos d6 quanto seu bônus de Dano da Fúria.",
 [{"tipo":"pontos_de_vida_temporarios","formula":["nivel_classe:barbaro"],"gatilho":"entrar_em_furia"},
  {"tipo":"pontos_de_vida_temporarios","beneficiario":"criatura_a_ate_3m",
   "formula":[{"op":"mult","args":["coluna:dano_da_furia","1d6"]}],
   "momento":"inicio_do_seu_turno","condicao":ATIVA,
   "nota":"Esses PV temporários desaparecem quando a Fúria termina."}], subclasse=S)
car("ramos_da_arvore","Ramos da Árvore",6,54,
 "Reação quando criatura à vista começa o turno a até 9 m em Fúria: salvaguarda de Força ou é teleportada para perto de você, e você pode zerar o Deslocamento dela até o fim do turno.",
 [{"tipo":"teleporte","custo":"reacao","beneficiario":"alvo","destino":"espaco_a_ate_1_5m_de_voce",
   "condicao":ATIVA,"salvaguarda":{"atributo":"FOR","cd":CD}},
  {"tipo":"modificador","alvo":"deslocamento","valor":["0"],"empilha":"substitui",
   "beneficiario":"alvo","duracao":"ate_o_fim_do_turno_atual"}], subclasse=S)
car("raizes_devastadoras","Raízes Devastadoras",10,54,
 "No seu turno, +3 m de alcance com arma corpo a corpo Pesada ou Versátil; ao acertar, pode ativar Derrubar ou Empurrar além da maestria que já estiver usando.",
 [{"tipo":"modificador","alvo":"alcance_do_ataque_desarmado","valor":["3"],"unidade":"m","empilha":"soma",
   "aplica_a":"arma_corpo_a_corpo_pesada_ou_versatil","condicao":{"todas":["seu_turno"]}},
  {"tipo":"substituir_maestria","escopo":"arma_corpo_a_corpo_pesada_ou_versatil",
   "opcoes":["derrubar","empurrar"],"modo":"adiciona_alem_da_atual"}], subclasse=S)
car("percorrer_a_arvore","Percorrer a Árvore",14,55,
 "Ao entrar em Fúria e com Ação Bônus durante ela, teleporta até 18 m. Uma vez por Fúria, o alcance vira 45 m e leva até seis criaturas voluntárias a até 3 m.",
 [{"tipo":"teleporte","alcance_m":18,"custo":"acao_bonus","condicao":ATIVA,
   "requisitos":["destino_desocupado","destino_a_vista"]},
  {"tipo":"teleporte","alcance_m":45,"frequencia":"uma_vez_por_furia","condicao":ATIVA,
   "leva_junto":{"quantidade":6,"alcance_m":3,"criaturas":"voluntarias"}}], subclasse=S)

# ---------------------------------------------------- Trilha do Berserker
S="trilha_do_berserker"
car("frenesi","Frenesi",3,55,
 "Usando Ataque Imprudente em Fúria, causa dano extra no primeiro alvo atingido no turno com ataque de Força: tantos d6 quanto seu bônus de Dano da Fúria, do tipo da arma.",
 [{"tipo":"dano","formula_dado":{"op":"mult","args":["coluna:dano_da_furia","1d6"]},
   "tipo_dano":"mesmo_do_ataque","modo":"dano_adicional","frequencia":"primeiro_alvo_do_turno",
   "condicao":{"todas":["ativo:furia","usou:ataque_imprudente","ataque_com_forca"]}}], subclasse=S)
car("furia_irracional","Fúria Irracional",6,55,
 "Imunidade às condições Amedrontado e Enfeitiçado em Fúria; se já estiver sob uma delas ao entrar em Fúria, ela encerra.",
 [{"tipo":"alterar_condicao","condicao_id":"amedrontado","operacao":"imunidade","condicao":ATIVA},
  {"tipo":"alterar_condicao","condicao_id":"enfeiticado","operacao":"imunidade","condicao":ATIVA},
  {"tipo":"remover_condicao","condicoes":["amedrontado","enfeiticado"],"quantidade":"todas",
   "gatilho":"entrar_em_furia"}], subclasse=S)
car("retaliacao","Retaliação",10,55,
 "Ao sofrer dano de criatura a até 1,5 m, Reação para atacá-la corpo a corpo com arma ou Ataque Desarmado.",
 [{"tipo":"conceder_ataque","quantidade":["1"],"custo":"reacao",
   "gatilho":"sofrer_dano_de_criatura_a_ate_1_5m"}], subclasse=S)
car("presenca_intimidante","Presença Intimidante",14,55,
 "Ação Bônus: criaturas à escolha numa Emanação de 9 m fazem salvaguarda de Sabedoria ou ficam Amedrontadas por 1 minuto, repetindo no fim de cada turno delas. Recarrega em Descanso Longo, ou gastando um uso de Fúria.",
 [{"tipo":"recurso_com_recarga","id":"presenca_intimidante","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso",
   "recuperacao_alternativa":{"consome_recurso":"furia","custo":"livre"}},
  {"tipo":"conceder_condicao","condicao_id":"amedrontado","custo":"acao_bonus",
   "beneficiario":"criaturas_a_escolha_na_emanacao","area":{"forma":"emanacao","tamanho_m":9},
   "salvaguarda":{"atributo":"SAB","cd":CD},"duracao":"1 minuto",
   "repete_salvaguarda":"fim_de_cada_turno_do_alvo","consome_recurso":"presenca_intimidante"}], subclasse=S)

# ---------------------------------------------- Trilha do Coração Selvagem
S="trilha_do_coracao_selvagem"
car("arauto_da_fauna","Arauto da Fauna",3,56,
 "Conjura Falar com Animais e Sentido Feral, mas só como Rituais, usando Sabedoria.",
 [{"tipo":"desbloquear_magias","modo":"conhecida","magias":["falar_com_animais","sentido_feral"],
   "atributo_conjuracao":"SAB","apenas_como_ritual":True}], subclasse=S)
car("furia_dos_selvagens","Fúria dos Selvagens",3,56,
 "A cada Fúria, escolhe Águia, Lobo ou Urso.",
 [{"id":"barbaro_furia_dos_selvagens","tipo":"escolha","rotulo":"Escolha o animal da Fúria",
   "quantidade":1,"momento":"ao_entrar_em_furia","reescolhivel":True,
   "de":{"catalogo":"opcoes_de_furia_dos_selvagens","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}], subclasse=S)
car("aspecto_dos_selvagens","Aspecto dos Selvagens",6,56,
 "Escolhe Coruja, Pantera ou Salmão; troca a cada Descanso Longo.",
 [{"id":"barbaro_aspecto","tipo":"escolha","rotulo":"Escolha o aspecto","quantidade":1,
   "momento":"nivel_6","reescolhivel":True,"reescolha_em":"descanso_longo",
   "de":{"catalogo":"opcoes_de_aspecto_dos_selvagens","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}], subclasse=S)
car("arauto_da_natureza","Arauto da Natureza",10,56,
 "Conjura Comunhão com a Natureza, só como Ritual, usando Sabedoria.",
 [{"tipo":"desbloquear_magias","modo":"conhecida","magias":["comunhao_com_a_natureza"],
   "atributo_conjuracao":"SAB","apenas_como_ritual":True}], subclasse=S)
car("poder_dos_selvagens","Poder dos Selvagens",14,56,
 "A cada Fúria, escolhe Carneiro, Falcão ou Leão.",
 [{"id":"barbaro_poder_dos_selvagens","tipo":"escolha","rotulo":"Escolha o poder da Fúria",
   "quantidade":1,"momento":"ao_entrar_em_furia","reescolhivel":True,
   "de":{"catalogo":"opcoes_de_poder_dos_selvagens","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}], subclasse=S)

# ------------------------------------------------------ Trilha do Fanático
S="trilha_do_fanatico"
car("campeao_dos_deuses","Campeão dos Deuses",3,57,
 "Reserva de d12s para se curar: começa com 4 e sobe para 5, 6 e 7 nos níveis 6, 12 e 17. Ação Bônus para gastar dados e recuperar PV. Recarrega em Descanso Longo.",
 [{"tipo":"reserva_de_dados","id":"campeao_dos_deuses","dado":"d12","formula_quantidade":["4"],
   "escalonamento_por_nivel":{"6":5,"12":6,"17":7},"recarga":["descanso_longo"]},
  {"tipo":"cura","custo":"acao_bonus","formula":["dados_gastos:campeao_dos_deuses"]}], subclasse=S)
car("furia_divina","Fúria Divina",3,57,
 "Em Fúria, a primeira criatura que você atinge a cada turno sofre 1d6 + metade do nível de Bárbaro (arredondado para baixo) de dano Necrótico ou Radiante, à sua escolha a cada vez.",
 [{"tipo":"dano","formula_dado":"1d6","somar":[{"op":"div_arred_baixo","args":["nivel_classe:barbaro","2"]}],
   "escolher_tipo_de_dano":["necrotico","radiante"],"modo":"dano_adicional",
   "frequencia":"primeiro_alvo_do_turno","condicao":ATIVA}], subclasse=S)
car("concentracao_fanatica","Concentração Fanática",6,57,
 "Uma vez por Fúria, ao falhar numa salvaguarda, joga de novo com bônus igual ao Dano da Fúria e usa o novo resultado.",
 [{"tipo":"rolar_novamente","alvo":"salvaguarda","gatilho":"falha","usa_novo_resultado":True,
   "bonus":["coluna:dano_da_furia"],"frequencia":"uma_vez_por_furia","condicao":ATIVA}], subclasse=S)
car("presenca_zelosa","Presença Zelosa",10,57,
 "Ação Bônus: até dez criaturas à escolha a até 18 m ganham Vantagem em ataques e salvaguardas até o início do seu próximo turno. Recarrega em Descanso Longo ou gastando um uso de Fúria.",
 [{"tipo":"recurso_com_recarga","id":"presenca_zelosa","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso",
   "recuperacao_alternativa":{"consome_recurso":"furia","custo":"livre"}},
  {"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem","custo":"acao_bonus",
   "beneficiario":"ate_10_criaturas_a_ate_18m","duracao":"ate_inicio_do_seu_proximo_turno",
   "consome_recurso":"presenca_zelosa"},
  {"tipo":"vantagem","alvo":"salvaguarda","modo":"vantagem",
   "beneficiario":"ate_10_criaturas_a_ate_18m","duracao":"ate_inicio_do_seu_proximo_turno"}], subclasse=S)
car("furia_dos_deuses","Fúria dos Deuses",14,57,
 "Ao entrar em Fúria, assume forma de combatente divino por 1 minuto ou até chegar a 0 PV: Resistência a Necrótico, Psíquico e Radiante; voo igual ao Deslocamento; e Reação gastando um uso de Fúria para pôr em pé uma criatura a até 9 m que chegou a 0 PV, com PV iguais ao seu nível. Recarrega em Descanso Longo.",
 [{"tipo":"recurso_com_recarga","id":"furia_dos_deuses","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"alterar_dano","tipo_dano":"necrotico","operacao":"resistencia","condicao":{"todas":["ativo:furia_dos_deuses"]}},
  {"tipo":"alterar_dano","tipo_dano":"psiquico","operacao":"resistencia","condicao":{"todas":["ativo:furia_dos_deuses"]}},
  {"tipo":"alterar_dano","tipo_dano":"radiante","operacao":"resistencia","condicao":{"todas":["ativo:furia_dos_deuses"]}},
  {"tipo":"conceder_velocidade","tipo_deslocamento":"voo","formula":["deslocamento"],
   "pode_pairar":True,"condicao":{"todas":["ativo:furia_dos_deuses"]}},
  {"tipo":"cura","custo":"reacao","consome_recurso":"furia","modo":"define_pv",
   "formula":["nivel_classe:barbaro"],"beneficiario":"criatura_a_ate_9m_que_chegou_a_0_pv"}], subclasse=S)

C['itens']=C['itens']+N; C['total']=len(C['itens']); wr('caracteristicas.json', C)
S_=rd('subclasses.json'); S_['itens']=[s for s in S_['itens'] if s.get('classe')!='barbaro']
NOVAS=[("trilha_da_arvore_do_mundo","Trilha da Árvore do Mundo",54,"Conecta a Fúria a Yggdrasil: vitalidade compartilhada, alcance ampliado e teleporte entre planos.",
        ["vitalidade_da_arvore","ramos_da_arvore","raizes_devastadoras","percorrer_a_arvore"]),
       ("trilha_do_berserker","Trilha do Berserker",55,"Frenesi violento: dano extra, imunidade a medo e retaliação.",
        ["frenesi","furia_irracional","retaliacao","presenca_intimidante"]),
       ("trilha_do_coracao_selvagem","Trilha do Coração Selvagem",56,"Comunhão com o mundo animal: rituais de fala com bichos e aspectos bestiais na Fúria.",
        ["arauto_da_fauna","furia_dos_selvagens","aspecto_dos_selvagens","arauto_da_natureza","poder_dos_selvagens"]),
       ("trilha_do_fanatico","Trilha do Fanático",57,"Fúria em êxtase divino: cura própria, dano sagrado e presença que inspira.",
        ["campeao_dos_deuses","furia_divina","concentracao_fanatica","presenca_zelosa","furia_dos_deuses"])]
S_['itens']=S_['itens']+[{"id":i,"nome":n,"classe":"barbaro","fonte":f(p),"revisao":OK,
  "descricao_curta":d,"niveis_de_caracteristica":[3,6,10,14],"caracteristicas":c} for i,n,p,d,c in NOVAS]
S_['total']=len(S_['itens']); wr('subclasses.json', S_)
print("bárbaro:", len(N), "características |", len(NOVAS), "subclasses")
