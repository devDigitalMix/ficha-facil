# -*- coding: utf-8 -*-
"""Fase 2g — Ladino (cap. 3, p. 137-145)."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D,p),encoding='utf-8'))
def wr(p,o): json.dump(o,open(os.path.join(D,p),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
CD=["8","mod:DES","prof"]
PERICIAS=["acrobacia","atletismo","enganacao","furtividade","intimidacao","intuicao",
          "investigacao","percepcao","persuasao","prestidigitacao"]

wr('catalogos/efeitos_de_golpe_astuto.json', {"catalogo":"efeitos_de_golpe_astuto",
 "nome":"Efeitos de Golpe Astuto","fonte":f(141),"total":7,
 "nota":"O custo em dados é subtraído do dano do Ataque Furtivo antes de jogar. CD: 8 + mod. de Destreza + BP.",
 "itens":[
  {"id":"envenenar","nome":"Envenenar","custo_em_dados":1,"nivel_minimo":5,
   "descricao_curta":"Salvaguarda de Constituição ou Envenenado por 1 minuto, repetindo no fim de cada turno. Exige Kit de Veneno."},
  {"id":"retirada","nome":"Retirada","custo_em_dados":1,"nivel_minimo":5,
   "descricao_curta":"Move metade do Deslocamento sem provocar Ataques de Oportunidade."},
  {"id":"tropeco","nome":"Tropeço","custo_em_dados":1,"nivel_minimo":5,
   "descricao_curta":"Alvo Grande ou menor faz salvaguarda de Destreza ou fica Caído."},
  {"id":"aturdir","nome":"Aturdir","custo_em_dados":2,"nivel_minimo":14,
   "descricao_curta":"Salvaguarda de Constituição ou, no próximo turno, o alvo só pode se mover, agir OU usar uma Ação Bônus."},
  {"id":"obscurecer","nome":"Obscurecer","custo_em_dados":3,"nivel_minimo":14,
   "descricao_curta":"Salvaguarda de Destreza ou o alvo fica Cego até o fim do próximo turno dele."},
  {"id":"nocaute","nome":"Nocaute","custo_em_dados":6,"nivel_minimo":14,
   "descricao_curta":"Salvaguarda de Constituição ou Inconsciente por 1 minuto ou até sofrer dano, repetindo no fim de cada turno."},
  {"id":"ataque_escondido","nome":"Ataque Escondido","custo_em_dados":1,"nivel_minimo":9,
   "origem":"subclasse:ladrao","descricao_curta":"Estando Invisível pela ação Esconder, o ataque não encerra a condição se você terminar o turno atrás de Cobertura de Três Quartos ou Total."}]})

def faixa(mp):
    o={}
    for (a,b),v in mp.items():
        for n in range(a,b+1): o[n]=v
    return o
BP=faixa({(1,4):2,(5,8):3,(9,12):4,(13,16):5,(17,20):6})
FURT={n:f"{(n+1)//2}d6" for n in range(1,21)}
CAR={1:["ataque_furtivo","especialista","giria_do_ladrao","maestria_em_arma_ladino"],
 2:["acao_ardilosa"], 3:["mira_firme","subclasse_de_ladino"], 4:["aumento_no_valor_de_atributo"],
 5:["esquiva_sobrenatural","golpe_astuto"], 6:["especialista"], 7:["evasao_ladino","talento_confiavel"],
 8:["aumento_no_valor_de_atributo"], 9:["caracteristica_de_subclasse"], 10:["aumento_no_valor_de_atributo"],
 11:["golpe_astuto_aprimorado"], 12:["aumento_no_valor_de_atributo"], 13:["caracteristica_de_subclasse"],
 14:["golpes_sujos"], 15:["mente_escorregadia"], 16:["aumento_no_valor_de_atributo"],
 17:["caracteristica_de_subclasse"], 18:["elusivo"], 19:["dadiva_epica"], 20:["golpe_de_sorte"]}

classe={"id":"ladino","nome":"Ladino","fonte":f(137),"revisao":OK,
 "descricao_curta":"Especialista em astúcia, furtividade e precisão: Ataque Furtivo, Especialização em perícias e Ação Ardilosa.",
 "dado_de_vida":8,"atributo_primario":["DES"],"salvaguardas_primarias":["DES","INT"],
 "nivel_subclasse":3,"conjuracao":None,"conjuracao_por_subclasse":True,
 "subclasses":["adaga_espiritual","assassino","ladrao","trapaceiro_arcano"],
 "proficiencias_iniciais":[
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"DES","nivel_dominio":"proficiente"},
   {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"INT","nivel_dominio":"proficiente"},
   {"id":"ladino_pericias_iniciais","tipo":"escolha","rotulo":"Escolha 4 perícias","quantidade":4,
    "momento":"criacao","de":{"catalogo":"pericias","chaves":PERICIAS},
    "efeito_por_item_escolhido":{"tipo":"conceder_proficiencia","categoria":"pericia","chave":"{{escolhido}}","nivel_dominio":"proficiente"}},
   {"tipo":"conceder_proficiencia","categoria":"arma","chave":"categoria:simples","nivel_dominio":"proficiente"},
   {"tipo":"conceder_proficiencia","categoria":"arma","chave":"categoria:marcial+propriedade:acuidade_ou_leve","nivel_dominio":"proficiente",
    "nota":"Só armas Marciais com a propriedade Acuidade ou Leve."},
   {"tipo":"conceder_proficiencia","categoria":"ferramenta","chave":"ferramentas_de_ladrao","nivel_dominio":"proficiente"}],
 "treinamento_com_armadura":["leve"],
 "equipamento_inicial":{"opcoes":[
   {"id":"A","itens":[{"item":"armadura_de_couro"},{"item":"adaga","quantidade":2},{"item":"espada_curta"},
                      {"item":"arco_curto"},{"item":"flecha","quantidade":20},{"item":"aljava"},
                      {"item":"ferramentas_de_ladrao"},{"item":"kit_de_assaltante"}],"moedas":{"po":8}},
   {"id":"B","moedas":{"po":100}}],
   "revisao":{"status":"duvida","notas":"Ids de item dependem do catálogo do cap. 6."}},
 "progressao":[{"nivel":n,"bonus_de_proficiencia":BP[n],"caracteristicas":CAR[n],
   "colunas":{"ataque_furtivo":FURT[n]}} for n in range(1,21)],
 "colunas_da_tabela":{"ataque_furtivo":{"nome":"Ataque Furtivo","tipo":"dado"}},
 "multiclasse":{"adquire":["dado_de_vida"],"fonte":f(137),"nota":"Registrado para a fase de multiclasse."}}
cl=rd('classes.json'); cl['itens']=[c for c in cl['itens'] if c['id']!='ladino']+[classe]
cl['total']=len(cl['itens']); wr('classes.json', cl)

C=rd('caracteristicas.json'); C['itens']=[c for c in C['itens'] if c.get('classe')!='ladino']
N=[]
def car(i,nome,nv,pag,desc,ef,**kw):
    d={"id":i,"nome":nome,"classe":"ladino","nivel":nv,"fonte":f(pag),
       "revisao":kw.pop("revisao",OK),"descricao_curta":desc,"efeitos":ef}
    d.update(kw); N.append(d)

car("ataque_furtivo","Ataque Furtivo",1,137,
 "Uma vez por turno, ao acertar com arma de Acuidade ou à Distância tendo Vantagem, causa dano extra conforme a coluna Ataque Furtivo. Dispensa a Vantagem se um aliado não Incapacitado estiver a até 1,5 m do alvo e você não tiver Desvantagem.",
 [{"tipo":"dado_de_impacto","coluna":"ataque_furtivo","tipo_dano":"mesmo_da_arma",
   "frequencia":"uma_vez_por_turno",
   "condicao":{"todas":["arma:acuidade_ou_a_distancia"],
               "alguma":["vantagem_na_jogada","aliado_nao_incapacitado_a_ate_1_5m_do_alvo_e_sem_desvantagem"]}}])

car("especialista","Especialista",1,137,
 "Especialização em duas perícias em que já é proficiente. Mais duas no nível 6.",
 [{"id":"ladino_especializacao","tipo":"escolha","rotulo":"Escolha perícias para Especialização",
   "quantidade":2,"momento":"nivel_1","quantidade_por_nivel":{"1":2,"6":4},
   "recomendadas":["furtividade","prestidigitacao"],
   "de":{"catalogo":"pericias","chaves":PERICIAS,"filtro_adicional":{"ja_proficiente":True}},
   "efeito_por_item_escolhido":{"tipo":"conceder_proficiencia","categoria":"pericia",
                                "chave":"{{escolhido}}","nivel_dominio":"especialista"}}],
 niveis=[1,6], repetivel=True, tipo_de_repeticao="nova_escolha")

car("giria_do_ladrao","Gíria do Ladrão",1,137,
 "Conhece a Gíria dos Ladrões e mais um idioma à escolha.",
 [{"tipo":"conceder_proficiencia","categoria":"idioma","chave":"giria_dos_ladroes","nivel_dominio":"proficiente"},
  {"id":"ladino_idioma","tipo":"escolha","rotulo":"Escolha mais um idioma","quantidade":1,
   "momento":"nivel_1","de":{"catalogo":"idiomas","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"conceder_proficiencia","categoria":"idioma",
                                "chave":"{{escolhido}}","nivel_dominio":"proficiente"}}])

car("maestria_em_arma_ladino","Maestria em Arma",1,137,
 "Usa as propriedades de maestria de dois tipos de armas com que tenha proficiência. Troca a cada Descanso Longo.",
 [{"id":"ladino_maestrias","tipo":"escolha","rotulo":"Escolha dois tipos de arma","quantidade":2,
   "momento":"nivel_1","reescolhivel":True,"reescolha_em":"descanso_longo",
   "de":{"catalogo":"itens","filtro":{"categoria":"arma","com_proficiencia":True}},
   "efeito_por_item_escolhido":{"tipo":"efeito_narrativo","chave":"maestria_liberada","arma":"{{escolhido}}"}}])

car("acao_ardilosa","Ação Ardilosa",2,137,
 "Ação Bônus para executar Correr, Desengajar ou Esconder.",
 [{"tipo":"conceder_acao","id":"acao_ardilosa","custo":"acao_bonus",
   "acoes":["correr","desengajar","esconder"]}])

car("mira_firme","Mira Firme",3,139,
 "Ação Bônus para dar a si Vantagem na próxima jogada de ataque do turno. Só se não tiver se movido, e depois o Deslocamento vira 0 até o fim do turno.",
 [{"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem","custo":"acao_bonus",
   "pre_requisitos":[{"tipo":"estado","chave":"nao_se_moveu_neste_turno"}],
   "duracao":"proxima_jogada_de_ataque_do_turno"},
  {"tipo":"modificador","alvo":"deslocamento","valor":["0"],"empilha":"substitui",
   "duracao":"ate_o_fim_do_turno_atual"}])

car("subclasse_de_ladino","Subclasse de Ladino",3,139,
 "Escolhe uma subclasse; as características chegam nos níveis 3, 9, 13 e 17.",
 [{"id":"ladino_escolha_de_subclasse","tipo":"escolha","rotulo":"Escolha uma subclasse","quantidade":1,
   "momento":"nivel_3","de":{"catalogo":"subclasses","filtro":{"classe":"ladino"}},
   "efeito_por_item_escolhido":{"tipo":"conceder_subclasse","chave":"{{escolhido}}"}}])

car("golpe_astuto","Golpe Astuto",5,139,
 "Ao causar dano com Ataque Furtivo, aplica um efeito de Golpe Astuto pagando o custo em dados, subtraído do dano antes de jogar. CD: 8 + mod. de Destreza + BP.",
 [{"id":"ladino_golpe_astuto","tipo":"escolha","rotulo":"Escolha o efeito de Golpe Astuto",
   "quantidade":1,"momento":"ao_causar_dano_de_ataque_furtivo","reescolhivel":True,
   "de":{"catalogo":"efeitos_de_golpe_astuto","todo_o_catalogo":True,"respeitar_nivel_minimo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}],
 cd_dos_efeitos=CD,
 nota="O custo em dados sai do dano do Ataque Furtivo: remova o dado antes de jogar.")

car("esquiva_sobrenatural","Esquiva Sobrenatural",5,139,
 "Reação para reduzir à metade o dano de um ataque de atacante à vista.",
 [{"tipo":"reducao_de_dano","custo":"reacao",
   "formula":{"op":"div_arred_baixo","args":["dano","2"]},"tipos_de_dano":["todos"],
   "requisitos":["atacante_a_vista"]}])

car("evasao_ladino","Evasão",7,139,
 "Contra efeito com salvaguarda de Destreza por metade do dano: nenhum dano no sucesso, metade na falha. Não funciona Incapacitado.",
 [{"tipo":"alterar_resultado_de_salvaguarda","alvo":"salvaguarda:DES",
   "aplica_a":"efeito_com_metade_do_dano","em_sucesso":"nenhum_dano","em_falha":"metade_do_dano",
   "condicao":{"nao":"condicao:incapacitado"}}])

car("talento_confiavel","Talento Confiável",7,141,
 "Em teste de atributo com proficiência em perícia ou ferramenta, trata 9 ou menos no d20 como 10.",
 [{"tipo":"tratar_resultado_minimo","alvo":["teste_de_atributo"],"minimo":10,
   "condicao":{"todas":["com_proficiencia_em_pericia_ou_ferramenta"]}}])

car("golpe_astuto_aprimorado","Golpe Astuto Aprimorado",11,141,
 "Aplica até dois efeitos de Golpe Astuto por Ataque Furtivo, pagando o custo de cada um.",
 [{"tipo":"melhorar_caracteristica","alvo":"golpe_astuto",
   "efeitos":[{"tipo":"efeito_narrativo","chave":"dois_efeitos",
               "texto":"Até dois efeitos de Golpe Astuto por uso, pagando o custo em dados de cada um."}]}])

car("golpes_sujos","Golpes Sujos",14,141,
 "Aturdir, Nocaute e Obscurecer entram nas opções de Golpe Astuto.",
 [{"tipo":"melhorar_caracteristica","alvo":"golpe_astuto",
   "efeitos":[{"tipo":"efeito_narrativo","chave":"novas_opcoes_de_golpe_astuto",
               "texto":"Aturdir (2d6), Obscurecer (3d6) e Nocaute (6d6) passam a estar disponíveis."}]}])

car("mente_escorregadia","Mente Escorregadia",15,141,
 "Proficiência em salvaguardas de Sabedoria e Carisma.",
 [{"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"SAB","nivel_dominio":"proficiente"},
  {"tipo":"conceder_proficiencia","categoria":"salvaguarda","chave":"CAR","nivel_dominio":"proficiente"}])

car("elusivo","Elusivo",18,141,
 "Nenhuma jogada de ataque pode ter Vantagem contra você, salvo se estiver Incapacitado.",
 [{"tipo":"impedir","alvo":"vantagem_em_ataque_contra_voce","condicao":{"nao":"condicao:incapacitado"}}])

car("golpe_de_sorte","Golpe de Sorte",20,141,
 "Ao falhar num Teste de D20, transforma o resultado em 20. Recarrega em Descanso Curto ou Longo.",
 [{"tipo":"recurso_com_recarga","id":"golpe_de_sorte","formula_maximo":["1"],
   "recarga":["descanso_curto","descanso_longo"],"consumo":"por_uso"},
  {"tipo":"tratar_resultado_minimo","alvo":["teste_d20"],"minimo":20,"gatilho":"falha",
   "consome_recurso":"golpe_de_sorte"}])

# --------------------------------------------------------- Adaga Espiritual
S="adaga_espiritual"
DEP={3:("d6",4),5:("d8",6),9:("d8",8),11:("d10",8),13:("d10",10),17:("d12",12)}
car("laminas_psiquicas","Lâminas Psíquicas",3,139,
 "Na ação Atacar ou num Ataque de Oportunidade, manifesta uma Lâmina Psíquica: arma Simples Corpo a Corpo, 1d6 Psíquico + modificador do ataque, Acuidade e Arremesso (18/36), maestria Afligir sem contar para o limite. Depois de atacar com ela, pode atacar com uma segunda como Ação Bônus, com dado 1d4.",
 [{"tipo":"conceder_ataque","quantidade":["1"],"arma_virtual":{
    "nome":"Lâmina Psíquica","categoria":"arma","grupo":"simples","alcance":"corpo_a_corpo",
    "dano":"1d6","tipo_dano":"psiquico","somar":["mod_do_ataque"],
    "propriedades":["acuidade","arremesso"],"alcance_arremesso_m":[18,36],
    "maestria":"afligir","maestria_nao_conta_para_o_limite":True}},
  {"tipo":"conceder_ataque","quantidade":["1"],"custo":"acao_bonus",
   "arma_virtual":{"nome":"Lâmina Psíquica (segunda)","dano":"1d4","tipo_dano":"psiquico"},
   "requisitos":["outra_mao_livre"]}], subclasse=S)
car("poder_psionico_ladino","Poder Psiônico",3,140,
 "Dados de Energia Psiônica pela tabela, recuperando um em Descanso Curto e todos no Longo. Aptidão Reforçada Psiquicamente (soma um dado a teste falho, gastando só se virar sucesso) e Sussurros Psíquicos (telepatia com até BP criaturas por horas iguais ao dado).",
 [{"tipo":"recurso_com_recarga","id":"dados_de_energia_psionica_ladino","nome":"Dados de Energia Psiônica",
   "formula_maximo":["tabela:dados_de_energia_ladino.quantidade"],
   "dado":"tabela:dados_de_energia_ladino.tipo",
   "recarga":[{"gatilho":"descanso_curto","quantidade":1},{"gatilho":"descanso_longo","quantidade":"todos"}],
   "consumo":"por_uso"},
  {"tipo":"modificador","alvo":"teste_de_atributo","valor":["dado:dados_de_energia_psionica_ladino"],
   "empilha":"soma","gatilho":"falha","momento":"apos_a_jogada",
   "condicao":{"todas":["com_proficiencia_em_pericia_ou_ferramenta"]},
   "consome_recurso":"dados_de_energia_psionica_ladino",
   "nota":"O dado só é gasto se o teste virar sucesso."},
  {"tipo":"efeito_narrativo","chave":"sussurros_psiquicos","custo":"acao","acao_id":"usar_magia",
   "texto":"Telepatia com até (Bônus de Proficiência) criaturas à vista, por horas iguais ao resultado do dado, alcance 1,5 km. O primeiro uso após Descanso Longo não gasta o dado."}],
 subclasse=S,
 tabela_de_dados={"id":"dados_de_energia_ladino","fonte":f(140),
   "linhas":[{"nivel":n,"tipo":t,"quantidade":q} for n,(t,q) in sorted(DEP.items())]})
car("laminas_da_alma","Lâminas da Alma",9,140,
 "Golpes Teleguiados (soma um dado à jogada de ataque errada da Lâmina; gasta só se acertar) e Teleporte Psíquico (Ação Bônus: arremessa a lâmina e se teleporta até 3 m por ponto do dado).",
 [{"tipo":"modificador","alvo":"jogada_de_ataque","valor":["dado:dados_de_energia_psionica_ladino"],
   "empilha":"soma","gatilho":"erro","momento":"apos_a_jogada",
   "condicao":{"todas":["ataque_com_lamina_psiquica"]},
   "consome_recurso":"dados_de_energia_psionica_ladino","nota":"Gasta o dado só se o ataque passar a acertar."},
  {"tipo":"teleporte","custo":"acao_bonus",
   "alcance_formula":{"op":"mult","args":["3","dado:dados_de_energia_psionica_ladino"]},
   "unidade":"m","consome_recurso":"dados_de_energia_psionica_ladino",
   "requisitos":["destino_desocupado","destino_a_vista"]}], subclasse=S)
car("veu_psiquico","Véu Psíquico",13,140,
 "Ação Usar Magia para ficar Invisível por 1 hora ou até encerrar; acaba se causar dano ou forçar salvaguarda. Recarrega gastando um Dado de Energia Psiônica ou em Descanso Longo.",
 [{"tipo":"recurso_com_recarga","id":"veu_psiquico","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso",
   "recuperacao_alternativa":{"consome_recurso":"dados_de_energia_psionica_ladino","custo":"livre"}},
  {"tipo":"conceder_condicao","condicao_id":"invisivel","custo":"acao","acao_id":"usar_magia",
   "duracao":"1 hora","consome_recurso":"veu_psiquico",
   "encerra_se":[{"gatilho":"causar_dano"},{"gatilho":"forcar_salvaguarda"},{"gatilho":"encerrar"}]}],
 subclasse=S)
car("rasgar_mente","Rasgar Mente",17,140,
 "Ao causar dano de Ataque Furtivo com a Lâmina Psíquica, o alvo faz salvaguarda de Sabedoria ou fica Atordoado por 1 minuto, repetindo no fim de cada turno. Recarrega gastando três Dados de Energia Psiônica ou em Descanso Longo.",
 [{"tipo":"recurso_com_recarga","id":"rasgar_mente","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso",
   "recuperacao_alternativa":{"consome_recurso":"dados_de_energia_psionica_ladino","quantidade":3,"custo":"livre"}},
  {"tipo":"conceder_condicao","condicao_id":"atordoado","beneficiario":"alvo",
   "gatilho":"dano_de_ataque_furtivo_com_lamina_psiquica",
   "salvaguarda":{"atributo":"SAB","cd":CD},"duracao":"1 minuto",
   "repete_salvaguarda":"fim_de_cada_turno_do_alvo","consome_recurso":"rasgar_mente"}], subclasse=S)

# ---------------------------------------------------------------- Assassino
S="assassino"
car("assassinar","Assassinar",3,142,
 "Vantagem nas jogadas de Iniciativa. Na primeira rodada, Vantagem em ataques contra quem ainda não agiu; e se o Ataque Furtivo acertar nessa rodada, o alvo sofre dano extra do tipo da arma igual ao seu nível de Ladino.",
 [{"tipo":"vantagem","alvo":"iniciativa","modo":"vantagem"},
  {"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem",
   "condicao":{"todas":["primeira_rodada","alvo_ainda_nao_agiu"]}},
  {"tipo":"dano","formula_dado":"nivel_classe:ladino","tipo_dano":"mesmo_da_arma","modo":"dano_adicional",
   "condicao":{"todas":["primeira_rodada","acerto_com_ataque_furtivo"]}}], subclasse=S)
car("ferramentas_de_assassino","Ferramentas de Assassino",3,142,
 "Ganha um Kit de Disfarce e um Kit de Veneno, com proficiência em ambos.",
 [{"tipo":"conceder_proficiencia","categoria":"ferramenta","chave":"kit_de_disfarce","nivel_dominio":"proficiente"},
  {"tipo":"conceder_proficiencia","categoria":"ferramenta","chave":"kit_de_veneno","nivel_dominio":"proficiente"},
  {"tipo":"efeito_narrativo","chave":"itens_concedidos","texto":"Você recebe um Kit de Disfarce e um Kit de Veneno."}],
 subclasse=S)
car("especialista_em_infiltracao","Especialista em Infiltração",9,142,
 "Mimetismo Magistral (imita fala e caligrafia após 1 hora de estudo) e Mira Móvel (Mira Firme não zera seu Deslocamento).",
 [{"tipo":"efeito_narrativo","chave":"mimetismo_magistral",
   "texto":"Imita perfeitamente a fala, a caligrafia ou ambos de alguém, após 1 hora estudando."},
  {"tipo":"melhorar_caracteristica","alvo":"mira_firme",
   "efeitos":[{"tipo":"efeito_narrativo","chave":"mira_movel",
               "texto":"Mira Firme deixa de reduzir seu Deslocamento a 0."}]}], subclasse=S)
car("armas_venenosas","Armas Venenosas",13,142,
 "Com a opção Envenenar do Golpe Astuto, o alvo sofre também 2d6 de dano Venenoso a cada falha na salvaguarda, ignorando Resistência a Venenoso.",
 [{"tipo":"dano","formula_dado":"2d6","tipo_dano":"venenoso","modo":"dano_adicional",
   "ignora":["resistencia"],"condicao":{"todas":["usou:envenenar","alvo_falhou_na_salvaguarda"]}}], subclasse=S)
car("golpe_mortal","Golpe Mortal",17,142,
 "Ao acertar com Ataque Furtivo na primeira rodada, o alvo faz salvaguarda de Constituição ou o dano do ataque é dobrado.",
 [{"tipo":"dano","modo":"dobrar_dano_do_ataque",
   "condicao":{"todas":["primeira_rodada","acerto_com_ataque_furtivo"]},
   "salvaguarda":{"atributo":"CON","cd":CD}}], subclasse=S)

# ------------------------------------------------------------------ Ladrão
S="ladrao"
car("andarilho_de_telhados","Andarilho de Telhados",3,142,
 "Deslocamento de Escalada igual ao seu Deslocamento, e distância de salto calculada por Destreza em vez de Força.",
 [{"tipo":"conceder_velocidade","tipo_deslocamento":"escalada","formula":["deslocamento"]},
  {"tipo":"substituir_atributo","de":"FOR","para":"DES","escopo":["distancia_de_salto"]}], subclasse=S)
car("mao_leve","Mão Leve",3,143,
 "Ação Bônus para um teste de Destreza (Prestidigitação) — abrir fechadura, desarmar armadilha com Ferramentas de Ladrão ou furtar um bolso — ou para executar Usar Objeto/Usar Magia com item mágico.",
 [{"tipo":"conceder_acao","id":"mao_leve","custo":"acao_bonus",
   "opcoes":[{"id":"prestidigitacao","teste":{"atributo":"DES","pericia":"prestidigitacao"}},
             {"id":"usar_objeto","acoes":["usar_objeto","usar_magia"],
              "nota":"para utilizar item mágico que exija essa ação"}]}], subclasse=S)
car("furtividade_suprema","Furtividade Suprema",9,143,
 "Ganha a opção de Golpe Astuto Ataque Escondido (1d6).",
 [{"tipo":"melhorar_caracteristica","alvo":"golpe_astuto",
   "efeitos":[{"tipo":"efeito_narrativo","chave":"ataque_escondido",
               "texto":"Ataque Escondido (1d6) entra nas opções de Golpe Astuto."}]}], subclasse=S)
car("usar_dispositivo_magico","Usar Dispositivo Mágico",13,143,
 "Sintoniza até quatro itens mágicos; ao gastar cargas, 1d6 — num 6 não gasta; e usa qualquer Pergaminho Mágico com Inteligência (truque e 1º círculo direto; acima disso, teste de Inteligência (Arcanismo) CD 10 + círculo, e o pergaminho se desintegra na falha).",
 [{"tipo":"efeito_narrativo","chave":"sintonizacao_extra","texto":"Pode sintonizar até quatro itens mágicos."},
  {"tipo":"efeito_narrativo","chave":"cargas_economizadas","texto":"Ao gastar cargas de item mágico, jogue 1d6: num 6 a carga não é gasta."},
  {"tipo":"efeito_narrativo","chave":"pergaminhos",
   "texto":"Usa qualquer Pergaminho Mágico com Inteligência como atributo de conjuração. Truque ou 1º círculo saem direto; acima disso exige teste de Inteligência (Arcanismo) CD 10 + círculo, e o pergaminho se desintegra em caso de falha.",
   "teste":{"atributo":"INT","pericia":"arcanismo"}}], subclasse=S)
car("reflexos_de_ladrao","Reflexos de Ladrão",17,143,
 "Na primeira rodada de combate você tem dois turnos: um na sua Iniciativa e outro na Iniciativa menos 10.",
 [{"tipo":"efeito_narrativo","chave":"turno_extra_na_primeira_rodada",
   "texto":"Dois turnos na primeira rodada: o normal e outro na sua Iniciativa menos 10."}], subclasse=S)

# -------------------------------------------------------- Trapaceiro Arcano
S="trapaceiro_arcano"
PREP={3:3,4:4,5:4,6:4,7:5,8:6,9:6,10:7,11:8,12:8,13:9,14:10,15:10,16:11,17:11,18:11,19:12,20:13}
SL={3:[2,0,0,0],4:[3,0,0,0],5:[3,0,0,0],6:[3,0,0,0],7:[4,2,0,0],8:[4,2,0,0],9:[4,2,0,0],
 10:[4,3,0,0],11:[4,3,0,0],12:[4,3,0,0],13:[4,3,2,0],14:[4,3,2,0],15:[4,3,2,0],16:[4,3,3,0],
 17:[4,3,3,0],18:[4,3,3,0],19:[4,3,3,1],20:[4,3,3,1]}
car("conjuracao_trapaceiro_arcano","Conjuração",3,143,
 "Conjura magias da lista do Mago com Inteligência. Três truques (Mãos Mágicas obrigatória + dois à escolha; mais um no nível 10), espaços e magias preparadas pela tabela Conjuração do Trapaceiro Arcano.",
 [{"tipo":"conceder_slot","tabela_progressao_id":"trapaceiro_arcano","recarga":"descanso_longo"},
  {"tipo":"preparar_magias","formula_quantidade":["coluna_conjuracao:magias_preparadas"],
   "atributo_conjuracao":"INT","fonte_das_magias":"lista_de_classe","lista_id":"mago",
   "restricao":"de um círculo para o qual você possui espaços de magia"},
  {"tipo":"desbloquear_magias","lista_id":"mago","modo":"disponivel_para_preparar",
   "atributo_conjuracao":"INT","circulo_minimo":1},
  {"tipo":"desbloquear_magias","lista_id":"mago","modo":"conhecida","magias":["maos_magicas"],
   "obrigatoria":True,"nao_substituivel":True},
  {"id":"trapaceiro_truques","tipo":"escolha","rotulo":"Escolha truques da lista do Mago",
   "quantidade":2,"momento":"nivel_3","quantidade_por_nivel":{"3":2,"10":3},
   "reescolhivel":True,"reescolha_em":"cada_nivel_de_ladino",
   "recomendados":["ilusao_menor","talho_mental"],
   "de":{"catalogo":"magias","filtro":{"nivel":0,"lista":"mago"}},
   "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"mago","modo":"conhecida","magia":"{{escolhido}}"}},
  {"id":"trapaceiro_preparadas","tipo":"escolha","rotulo":"Prepare magias de 1º círculo ou superior",
   "quantidade":"coluna_conjuracao:magias_preparadas","momento":"nivel_3",
   "reescolhivel":True,"reescolha_em":"cada_nivel_de_ladino","reescolha_quantidade":1,
   "recomendados":["disfarcar_se","enfeiticar_pessoa","nevoa_obscurecente"],
   "de":{"catalogo":"magias","filtro":{"nivel_minimo":1,"lista":"mago","circulo_com_espaco_disponivel":True}},
   "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"mago","modo":"preparada","magia":"{{escolhido}}"}}],
 subclasse=S, foco_de_conjuracao=["foco_arcano"],
 tabela_de_conjuracao={"id":"trapaceiro_arcano","fonte":f(144),
   "colunas":["magias_preparadas","espacos_1","espacos_2","espacos_3","espacos_4"],
   "linhas":[{"nivel":n,"magias_preparadas":PREP[n],"espacos_1":SL[n][0],"espacos_2":SL[n][1],
              "espacos_3":SL[n][2],"espacos_4":SL[n][3]} for n in range(3,21)]})
car("maos_magicas_ligeiras","Mãos Mágicas Ligeiras",3,145,
 "Conjura Mãos Mágicas como Ação Bônus, pode deixar a mão Invisível, controlá-la como Ação Bônus e usá-la para testes de Destreza (Prestidigitação).",
 [{"tipo":"efeito_narrativo","chave":"maos_magicas_ligeiras","custo":"acao_bonus",
   "texto":"Mãos Mágicas como Ação Bônus, mão espectral Invisível, controlada por Ação Bônus e capaz de testes de Destreza (Prestidigitação).",
   "teste":{"atributo":"DES","pericia":"prestidigitacao"}}], subclasse=S)
car("emboscada_magica","Emboscada Mágica",9,145,
 "Estando Invisível ao conjurar uma magia numa criatura, ela tem Desvantagem nas salvaguardas contra essa magia no mesmo turno.",
 [{"tipo":"vantagem","alvo":"salvaguarda","modo":"desvantagem","beneficiario":"alvo",
   "condicao":{"todas":["voce_invisivel_ao_conjurar"]},"duracao":"mesmo_turno"}], subclasse=S)
car("trapaceiro_versatil","Trapaceiro Versátil",13,145,
 "Ao usar Golpe Astuto numa criatura, pode aplicar a mesma opção em outra criatura a até 1,5 m da mão espectral.",
 [{"tipo":"melhorar_caracteristica","alvo":"golpe_astuto",
   "efeitos":[{"tipo":"efeito_narrativo","chave":"golpe_astuto_em_segundo_alvo",
               "texto":"Aplica a mesma opção de Golpe Astuto em outra criatura a até 1,5 m das Mãos Mágicas."}]}],
 subclasse=S)
car("ladrao_de_magias","Ladrão de Magias",17,145,
 "Reação quando alguém conjura magia que te atinge: salvaguarda de Inteligência contra sua CD ou você nega o efeito e rouba a magia por 8 horas (se for de 1º círculo ou de um círculo que você conjura, mesmo não sendo de Mago); a criatura não pode conjurá-la nesse período. Recarrega em Descanso Longo.",
 [{"tipo":"recurso_com_recarga","id":"ladrao_de_magias","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"efeito_narrativo","chave":"roubar_magia","custo":"reacao",
   "salvaguarda":{"atributo":"INT","cd":["8","mod:INT","prof"]},
   "consome_recurso":"ladrao_de_magias",
   "texto":"Nega o efeito da magia contra você e a rouba por 8 horas, ficando com ela preparada; a criatura não pode conjurá-la nesse período. Vale para magia de 1º círculo ou de círculo que você possa conjurar, mesmo fora da lista do Mago."}],
 subclasse=S)

C['itens']=C['itens']+N; C['total']=len(C['itens']); wr('caracteristicas.json', C)
S_=rd('subclasses.json'); S_['itens']=[s for s in S_['itens'] if s.get('classe')!='ladino']
NOVAS=[("adaga_espiritual","Adaga Espiritual",139,"Lâminas psiônicas manifestadas e Dados de Energia Psiônica.",
        ["laminas_psiquicas","poder_psionico_ladino","laminas_da_alma","veu_psiquico","rasgar_mente"]),
       ("assassino","Assassino",142,"Furtividade, veneno e disfarce para eliminar com eficiência mortal.",
        ["assassinar","ferramentas_de_assassino","especialista_em_infiltracao","armas_venenosas","golpe_mortal"]),
       ("ladrao","Ladrão",142,"Caçador de tesouros clássico: escalada, mãos rápidas e uso de itens mágicos.",
        ["andarilho_de_telhados","mao_leve","furtividade_suprema","usar_dispositivo_magico","reflexos_de_ladrao"]),
       ("trapaceiro_arcano","Trapaceiro Arcano",143,"Furtividade turbinada por magia arcana da lista do Mago.",
        ["conjuracao_trapaceiro_arcano","maos_magicas_ligeiras","emboscada_magica","trapaceiro_versatil","ladrao_de_magias"])]
S_['itens']=S_['itens']+[{"id":i,"nome":n,"classe":"ladino","fonte":f(p),"revisao":OK,
  "descricao_curta":d,"niveis_de_caracteristica":[3,9,13,17],"caracteristicas":c} for i,n,p,d,c in NOVAS]
S_['total']=len(S_['itens']); wr('subclasses.json', S_)
print("ladino:", len(N), "características |", len(NOVAS), "subclasses | classes:", cl['total'])
