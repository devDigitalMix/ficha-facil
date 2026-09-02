# -*- coding: utf-8 -*-
"""Características do Druida e os 4 círculos."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
CD = ["8", "mod:SAB", "prof"]

C = rd('caracteristicas.json'); C['itens'] = [c for c in C['itens'] if c.get('classe') != 'druida']
novos = []
def car(id_, nome, nv, pag, desc, ef, **kw):
    d = {"id": id_, "nome": nome, "classe": "druida", "nivel": nv, "fonte": f(pag),
         "revisao": kw.pop("revisao", OK), "descricao_curta": desc, "efeitos": ef}
    d.update(kw); novos.append(d)

car("conjuracao_druida","Conjuração",1,91,
 "Conjura magias de Druida com Sabedoria. Truques e magias preparadas conforme a tabela, escolhidas DIRETO da lista de Druida — sem livro e sem teto de círculo além dos espaços que você tem. Troca quantas quiser das preparadas a cada Descanso Longo.",
 [{"tipo":"conceder_slot","tabela_progressao_id":"druida",
   "colunas":[f"espacos_{i}" for i in range(1,10)],"recarga":"descanso_longo"},
  {"tipo":"preparar_magias","formula_quantidade":["coluna:magias_preparadas"],
   "atributo_conjuracao":"SAB","fonte_das_magias":"lista_de_classe","lista_id":"druida",
   "restricao":"de um círculo para o qual você possui espaços de magia",
   "magias_sempre_preparadas_nao_contam":True,
   "troca":{"gatilho":"descanso_longo","quantidade":"qualquer",
            "nota":"O Druida troca QUALQUER quantidade das preparadas a cada Descanso Longo (p. 92)."}},
  {"tipo":"desbloquear_magias","lista_id":"druida","modo":"disponivel_para_preparar",
   "atributo_conjuracao":"SAB"},
  {"id":"druida_truques","tipo":"escolha","rotulo":"Escolha truques de Druida",
   "quantidade":"coluna:truques","momento":"nivel_1","reescolhivel":True,
   "reescolha_em":"cada_nivel_de_druida","reescolha_quantidade":1,
   "recomendados":["arte_druidica","criar_chamas"],
   "de":{"catalogo":"magias","filtro":{"nivel":0,"lista":"druida"}},
   "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"druida","modo":"conhecida",
                                "magia":"{{escolhido}}"}},
  {"id":"druida_preparadas","tipo":"escolha","rotulo":"Prepare magias de Druida",
   "quantidade":"coluna:magias_preparadas","momento":"nivel_1","reescolhivel":True,
   "reescolha_em":"descanso_longo","reescolha_quantidade":"qualquer",
   "recomendados":["amizade_animal","curar_ferimentos","fogo_das_fadas","onda_trovejante"],
   "de":{"catalogo":"magias","filtro":{"nivel_minimo":1,"lista":"druida",
                                       "circulo_com_espaco_disponivel":True}},
   "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"druida","modo":"preparada",
                                "magia":"{{escolhido}}"}}],
 foco_de_conjuracao=["foco_druidico"], cd_para_evitar_sua_magia=CD)

car("idioma_druidico","Idioma Druídico",1,92,
 "Domina o Druídico, idioma secreto dos druidas, e tem sempre Falar com Animais preparada. Pode deixar mensagens ocultas em Druídico.",
 [{"tipo":"conceder_proficiencia","categoria":"idioma","chave":"druidico","nivel_dominio":"proficiente"},
  {"tipo":"desbloquear_magias","lista_id":"druida","modo":"sempre_preparada",
   "magias":["falar_com_animais"]},
  {"tipo":"efeito_narrativo","chave":"mensagens_ocultas",
   "texto":"Deixa mensagens ocultas em Druídico, legíveis só por quem conhece o idioma."}])

car("ordem_primal","Ordem Primal",1,92,
 "Escolhe uma função sagrada: Protetor (armas Marciais e armadura Média) ou Xamã (um truque a mais e bônus igual ao modificador de Sabedoria em Arcanismo/Natureza).",
 [{"id":"druida_ordem_primal","tipo":"escolha","rotulo":"Escolha sua Ordem Primal","quantidade":1,
   "momento":"nivel_1","de":{"catalogo":"ordens_primais","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}],
 efeitos_nomeados={
  "protetor":{"efeitos":[
    {"tipo":"conceder_proficiencia","categoria":"arma","chave":"categoria:marcial","nivel_dominio":"proficiente"},
    {"tipo":"conceder_proficiencia","categoria":"armadura","chave":"media","nivel_dominio":"proficiente"}]},
  "xama":{"efeitos":[
    {"tipo":"modificador","alvo":"teste_de_atributo","valor":{"op":"max","args":["1","mod:SAB"]},
     "empilha":"soma","condicao":{"alguma":["teste:INT.arcanismo","teste:INT.natureza"]}},
    {"id":"xama_truque_extra","tipo":"escolha","rotulo":"Escolha um truque de Druida adicional",
     "quantidade":1,"momento":"nivel_1",
     "de":{"catalogo":"magias","filtro":{"nivel":0,"lista":"druida"}},
     "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"druida","modo":"conhecida",
                                  "magia":"{{escolhido}}","nao_conta_para_o_limite":True}}]}})

car("companheiro_selvagem","Companheiro Selvagem",2,92,
 "Ação Usar Magia gastando um espaço de magia ou um uso de Forma Selvagem para conjurar Convocar Familiar sem componentes Materiais. O familiar é Feérico e some no Descanso Longo.",
 [{"tipo":"conjurar_sem_espaco","magia":"convocar_familiar","custo":"acao","acao_id":"usar_magia",
   "custo_alternativo":[{"gasta_espaco_de_magia":True},{"consome_recurso":"forma_selvagem"}],
   "sem_componentes_materiais":True,
   "modificacao":"o familiar é uma criatura Feérica e desaparece ao completar um Descanso Longo"}])

car("forma_selvagem","Forma Selvagem",2,92,
 "Ação Bônus para multimorfar numa forma Animal conhecida, por horas iguais à metade do seu nível de Druida. Usos conforme a coluna Forma Selvagem, recuperando um em Descanso Curto e todos no Longo. As formas conhecidas e o ND máximo crescem pela tabela Formas de Feras.",
 [{"tipo":"recurso_com_recarga","id":"forma_selvagem","nome":"Forma Selvagem",
   "formula_maximo":["coluna:forma_selvagem"],
   "recarga":[{"gatilho":"descanso_curto","quantidade":1},
              {"gatilho":"descanso_longo","quantidade":"todos"}],"consumo":"por_uso"},
  {"tipo":"forma_selvagem","recurso_id":"forma_selvagem","custo":"acao_bonus",
   "duracao":{"op":"div_arred_baixo","args":["nivel_classe:druida","2"]},"unidade_de_duracao":"horas",
   "encerra_se":[{"gatilho":"usar_forma_selvagem_de_novo"},{"condicao_id":"incapacitado"},
                 {"gatilho":"morte"},{"gatilho":"sair_como_acao_bonus"}],
   "tabela_de_formas":{"nome":"Formas de Feras","fonte":f(93),
     "linhas":[{"nivel":2,"formas_conhecidas":4,"nd_maximo":"1/4","deslocamento_de_voo":False},
               {"nivel":4,"formas_conhecidas":6,"nd_maximo":"1/2","deslocamento_de_voo":False},
               {"nivel":8,"formas_conhecidas":8,"nd_maximo":"1","deslocamento_de_voo":True}]},
   "regras_enquanto_multimorfado":{
     "mantem":["personalidade","memorias","fala","tipo_de_criatura","pontos_de_vida","dados_de_vida",
               "INT","SAB","CAR","caracteristicas_de_classe","idiomas","talentos",
               "proficiencias_de_pericia_e_salvaguarda"],
     "substitui":"as demais estatísticas pelo bloco da Fera; se a perícia ou salvaguarda do bloco for maior, use a do bloco",
     "pv_temporarios":["nivel_classe:druida"],
     "conjuracao":"não pode conjurar, mas a multimorfia não quebra Concentração nem interfere em magia já conjurada",
     "equipamento":"cai no espaço, funde-se à forma ou é usado por ela, à escolha; o que a forma não puder usar cai ou se funde e fica sem efeito"}},
  {"id":"druida_formas_conhecidas","tipo":"escolha","rotulo":"Escolha suas formas Animais",
   "quantidade":"tabela:formas_de_feras.formas_conhecidas","momento":"nivel_2",
   "reescolhivel":True,"reescolha_em":"descanso_longo","reescolha_quantidade":1,
   "recomendadas":["aranha","cavalo_de_montaria","lobo","rato"],
   "de":{"catalogo":"criaturas","filtro":{"tipo_de_criatura":"fera",
         "nd_maximo":"tabela:formas_de_feras.nd_maximo",
         "sem_deslocamento_de_voo":"tabela:formas_de_feras.deslocamento_de_voo == false"}},
   "efeito_por_item_escolhido":{"tipo":"efeito_narrativo","chave":"forma_conhecida",
                                "criatura":"{{escolhido}}"}}],
 revisao={"status":"duvida","notas":"A escolha das formas aponta para o catálogo 'criaturas', vazio por decisão de escopo (Apêndice B fora). O filtro está escrito e resolve sozinho se o Ap. B for extraído; enquanto isso o seletor fica vazio e o validador emite AVISO. Decidir se vale extrair as Feras de ND ≤ 1 do Ap. B só para alimentar a Forma Selvagem."})

car("subclasse_de_druida","Subclasse de Druida",3,94,
 "Escolhe um círculo druídico; as características chegam nos níveis 3, 6, 10 e 14.",
 [{"id":"druida_escolha_de_subclasse","tipo":"escolha","rotulo":"Escolha um círculo","quantidade":1,
   "momento":"nivel_3","de":{"catalogo":"subclasses","filtro":{"classe":"druida"}},
   "efeito_por_item_escolhido":{"tipo":"conceder_subclasse","chave":"{{escolhido}}"}}])

car("ressurgimento_selvagem","Ressurgimento Selvagem",5,94,
 "Uma vez por turno, sem usos de Forma Selvagem, recupera um gastando um espaço de magia. E pode gastar um uso de Forma Selvagem para recuperar um espaço de 1º círculo, uma vez por Descanso Longo.",
 [{"tipo":"converter_recurso","de":"espaco_de_magia","para":"forma_selvagem","taxa":"1:1",
   "frequencia":"uma_vez_por_turno","condicao":{"todas":["recurso:forma_selvagem.atual == 0"]}},
  {"tipo":"converter_recurso","de":"forma_selvagem","para":"espaco_de_magia","taxa":"1:1",
   "circulo_do_espaco":1,"frequencia":"uma_vez_por_descanso_longo","recarga":["descanso_longo"]}])

car("furia_elemental","Fúria Elemental",7,94,
 "Escolhe Ataque Primal (1d8 extra de dano elemental uma vez por turno) ou Conjuração Poderosa (modificador de Sabedoria no dano dos truques de Druida).",
 [{"id":"druida_furia_elemental","tipo":"escolha","rotulo":"Escolha a Fúria Elemental","quantidade":1,
   "momento":"nivel_7","de":{"catalogo":"opcoes_de_furia_elemental","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}],
 efeitos_nomeados={
  "ataque_primal":{"efeitos":[{"tipo":"dano","formula_dado":"1d8","modo":"dano_adicional",
    "frequencia":"uma_vez_por_turno","escolher_tipo_de_dano":["eletrico","gelido","igneo","trovejante"],
    "gatilho":"acerto_com_arma_ou_ataque_da_forma_animal"}]},
  "conjuracao_poderosa":{"efeitos":[{"tipo":"modificador","alvo":"jogada_de_dano","valor":["mod:SAB"],
    "empilha":"soma","condicao":{"todas":["magia_nivel:0","lista:druida"]}}]}})

car("furia_elemental_aprimorada","Fúria Elemental Aprimorada",15,94,
 "A opção escolhida melhora: Ataque Primal passa a 2d8; Conjuração Poderosa leva truques de alcance 3 m ou mais para 90 metros.",
 [{"tipo":"melhorar_caracteristica","alvo":"furia_elemental",
   "efeitos":[{"tipo":"efeito_narrativo","chave":"furia_aprimorada",
     "texto":"Ataque Primal: dano adicional vira 2d8. Conjuração Poderosa: truques de Druida com alcance de 3 m ou mais passam a ter alcance 90 m."}]}])

car("magias_bestiais","Magias Bestiais",18,94,
 "Pode conjurar magias em Forma Selvagem, exceto as que exigem componente Material com custo especificado ou que o consomem.",
 [{"tipo":"efeito_narrativo","chave":"conjurar_multimorfado",
   "texto":"Conjura normalmente na forma Animal, salvo magias com componente Material de custo especificado ou consumido."}])

car("arquidruida","Arquidruida",20,94,
 "Forma Selvagem Eterna (recupera um uso ao jogar Iniciativa sem usos), Natureza Xamânica (converte usos de Forma Selvagem em um espaço de magia, 2 círculos por uso, uma vez por Descanso Longo) e Longevidade.",
 [{"tipo":"restaurar_recurso","recurso_id":"forma_selvagem","quantidade":1,
   "gatilho":"jogar_iniciativa","condicao":{"todas":["recurso:forma_selvagem.atual == 0"]}},
  {"tipo":"converter_recurso","de":"forma_selvagem","para":"espaco_de_magia",
   "taxa":"1 uso = 2 círculos","modo":"soma_em_um_unico_espaco",
   "frequencia":"uma_vez_por_descanso_longo","recarga":["descanso_longo"]},
  {"tipo":"efeito_narrativo","chave":"longevidade",
   "texto":"Para cada dez anos que passam, seu corpo envelhece apenas um."}])

# ------------------------------------------------------------ Círculo da Lua
SUB="circulo_da_lua"
car("formas_animais_dos_circulos_druidicos","Formas Animais dos Círculos Druídicos",3,96,
 "Na Forma Selvagem: ND máximo igual ao nível de Druida dividido por 3 (arredondado para baixo), CA passa a 13 + modificador de Sabedoria se for maior que a da Fera, e PV temporários iguais a três vezes o nível de Druida.",
 [{"tipo":"melhorar_caracteristica","alvo":"forma_selvagem","efeitos":[
   {"tipo":"efeito_narrativo","chave":"nd_maximo_lunar",
    "formula":{"op":"div_arred_baixo","args":["nivel_classe:druida","3"]},
    "texto":"ND máximo da forma passa a ser o nível de Druida dividido por 3, arredondado para baixo."},
   {"tipo":"ca_base","formula":["13","mod:SAB"],"empilha":"maior_valor",
    "condicao":{"todas":["em_forma_selvagem"]}},
   {"tipo":"pontos_de_vida_temporarios",
    "formula":[{"op":"mult","args":["3","nivel_classe:druida"]}],"modo":"substitui"}]}], subclasse=SUB)
def magias_circulo(nome, linhas, pag, extra=None):
    e = {"tipo":"magias_de_patrono","tabela":{"nome":nome,"fonte":f(pag),
         "linhas":[{"nivel":n,"magias":ms} for n,ms in linhas]},
         "modo":"sempre_preparada","nao_conta_para_o_limite":True}
    if extra: e.update(extra)
    return e
car("magias_do_circulo_da_lua","Magias do Círculo da Lua",3,96,
 "Magias sempre preparadas pela tabela Magias do Círculo da Lua, conjuráveis inclusive em Forma Selvagem.",
 [magias_circulo("Magias do Círculo da Lua",
   [(3,["curar_ferimentos","fagulha_estelar","raio_lunar"]),(5,["invocar_animais"]),
    (7,["fonte_do_luar"]),(9,["curar_ferimentos_em_massa"])], 96,
   {"conjuravel_em_forma_selvagem":True})], subclasse=SUB)
car("formas_animais_dos_circulos_druidicos_aprimorada","Formas Animais dos Círculos Druídicos Aprimorada",6,96,
 "Em Forma Selvagem: cada ataque pode causar dano Radiante no lugar do normal (à escolha a cada acerto), e você soma o modificador de Sabedoria às salvaguardas de Constituição.",
 [{"tipo":"escolher_tipo_de_dano","aplica_a":["ataque_da_forma_animal"],
   "opcoes":["radiante","tipo_normal"],"momento":"a_cada_acerto"},
  {"tipo":"modificador","alvo":"salvaguarda:CON","valor":["mod:SAB"],"empilha":"soma",
   "condicao":{"todas":["em_forma_selvagem"]}}], subclasse=SUB)
car("passo_lunar","Passo Lunar",10,97,
 "Ação Bônus para teleportar até 9 m a espaço desocupado à vista, com Vantagem no próximo ataque neste turno. Usos iguais ao modificador de Sabedoria (mínimo 1), recarregados em Descanso Longo ou gastando espaço de 2º círculo ou superior.",
 [{"tipo":"recurso_com_recarga","id":"passo_lunar","formula_maximo":{"op":"max","args":["1","mod:SAB"]},
   "recarga":["descanso_longo"],"consumo":"por_uso",
   "recuperacao_alternativa":{"gasta_espaco_de_magia":{"circulo_minimo":2},"custo":"livre"}},
  {"tipo":"teleporte","custo":"acao_bonus","alcance_m":9,
   "requisitos":["destino_desocupado","destino_a_vista"],"consome_recurso":"passo_lunar"},
  {"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem","duracao":"ate_o_fim_do_turno_atual"}],
 subclasse=SUB)
car("forma_lunar","Forma Lunar",14,97,
 "Uma vez por turno, 2d10 de dano Radiante extra num alvo acertado pelo ataque da Forma Selvagem; e o Passo Lunar pode levar junto uma criatura voluntária a até 3 m.",
 [{"tipo":"dano","formula_dado":"2d10","tipo_dano":"radiante","modo":"dano_adicional",
   "frequencia":"uma_vez_por_turno","gatilho":"acerto_com_ataque_da_forma_selvagem"},
  {"tipo":"melhorar_caracteristica","alvo":"passo_lunar","efeitos":[
   {"tipo":"efeito_narrativo","chave":"luar_compartilhado",
    "texto":"Teleporta junto uma criatura voluntária a até 3 m, para espaço desocupado à vista a até 3 m do seu destino."}]}],
 subclasse=SUB)

# ---------------------------------------------------------- Círculo da Terra
SUB="circulo_da_terra"
car("auxilio_da_terra","Auxílio da Terra",3,97,
 "Ação Usar Magia gastando um uso de Forma Selvagem: Esfera de 3 m de raio a até 18 m; criaturas à escolha fazem salvaguarda de Constituição e sofrem 2d6 de dano Necrótico (metade no sucesso), e uma criatura à escolha na área recupera 2d6 PV. Sobe para 3d6 no nível 10 e 4d6 no 14.",
 [{"tipo":"dano","custo":"acao","acao_id":"usar_magia","consome_recurso":"forma_selvagem",
   "formula_dado":"2d6","tipo_dano":"necrotico",
   "area":{"forma":"esfera","raio_m":3,"alcance_m":18},
   "salvaguarda":{"atributo":"CON","cd":CD,"sucesso":"metade"},
   "escalonamento_por_nivel":{"10":"3d6","14":"4d6"}},
  {"tipo":"cura","formula":["2d6"],"beneficiario":"uma_criatura_a_escolha_na_area",
   "escalonamento_por_nivel":{"10":"3d6","14":"4d6"}}], subclasse=SUB)
TERRENOS = {
 "arido":[(3,["maos_flamejantes","raio_de_fogo","turvar"]),(5,["bola_de_fogo"]),(7,["malogro"]),(9,["muralha_de_pedra"])],
 "polar":[(3,["nevoa_obscurecente","paralisar_pessoa","raio_de_gelo"]),(5,["nevasca"]),(7,["tempestade_glacial"]),(9,["cone_de_frio"])],
 "temperado":[(3,["passo_nebuloso","sono","toque_chocante"]),(5,["relampago"]),(7,["movimentacao_livre"]),(9,["passo_arboreo"])],
 "tropical":[(3,["bolha_acida","raio_nauseante","teia"]),(5,["nuvem_fetida"]),(7,["polimorfia"]),(9,["praga_de_insetos"])]}
car("magias_do_circulo_da_terra","Magias do Círculo da Terra",3,97,
 "A cada Descanso Longo escolhe um terreno (árido, polar, temperado ou tropical) e tem preparadas as magias daquele terreno até o seu nível de Druida.",
 [{"id":"druida_terreno","tipo":"escolha","rotulo":"Escolha o tipo de terreno","quantidade":1,
   "momento":"descanso_longo","reescolhivel":True,"reescolha_em":"descanso_longo",
   "de":{"catalogo":"terrenos_druidicos","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}],
 subclasse=SUB,
 efeitos_nomeados={t: {"efeitos":[magias_circulo(f"Terreno {t.capitalize()}", linhas, 98)]}
                   for t, linhas in TERRENOS.items()})
car("recuperacao_natural","Recuperação Natural",6,98,
 "Conjura uma das magias de Círculo Druídico preparadas de 1º círculo ou superior sem gastar espaço, uma vez por Descanso Longo. E, em Descanso Curto, recupera espaços cuja soma de círculos não passe da metade do nível (arredondado para cima), nenhum de 6º ou superior.",
 [{"tipo":"recurso_com_recarga","id":"recuperacao_natural_magia","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"conjurar_sem_espaco","fonte":"magias_de_circulo_druidico_preparadas","circulo_minimo":1,
   "consome_recurso":"recuperacao_natural_magia"},
  {"tipo":"recurso_com_recarga","id":"recuperacao_natural_espacos","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"recuperar_espacos_de_magia","gatilho":"descanso_curto",
   "formula_circulos":{"op":"div_arred_cima","args":["nivel_classe:druida","2"]},
   "limite_de_circulo":5,"consome_recurso":"recuperacao_natural_espacos"}], subclasse=SUB)
car("protecao_natural","Proteção Natural",10,98,
 "Imune à condição Envenenado e com Resistência ao tipo de dano ligado ao terreno escolhido: Árido/Ígneo, Polar/Gélido, Temperado/Elétrico, Tropical/Venenoso.",
 [{"tipo":"alterar_condicao","condicao_id":"envenenado","operacao":"imunidade"},
  {"tipo":"alterar_dano","operacao":"resistencia",
   "tipo_dano_derivado":{"de":"druida_terreno",
     "mapa":{"arido":"igneo","polar":"gelido","temperado":"eletrico","tropical":"venenoso"}}}],
 subclasse=SUB)
car("santuario_natural","Santuário Natural",14,98,
 "Ação Usar Magia gastando um uso de Forma Selvagem: Cubo de 4,5 m no chão a até 36 m, por 1 minuto. Você e aliados têm Cobertura Parcial dentro, e os aliados ganham a Resistência atual da sua Proteção Natural. Ação Bônus para mover o Cubo até 18 m.",
 [{"tipo":"conceder_cobertura","grau":"parcial","custo":"acao","acao_id":"usar_magia",
   "consome_recurso":"forma_selvagem","area":{"forma":"cubo","lado_m":4.5,"alcance_m":36},
   "duracao":"1 minuto","alvos":{"voce_e_aliados_na_area":True},
   "encerra_se":[{"gatilho":"morte"},{"condicao_id":"incapacitado"}]},
  {"tipo":"alterar_dano","operacao":"resistencia","beneficiario":"aliados_na_area",
   "tipo_dano_derivado":{"de":"protecao_natural",
     "mapa":{"arido":"igneo","polar":"gelido","temperado":"eletrico","tropical":"venenoso"}}},
  {"tipo":"efeito_narrativo","chave":"mover_o_cubo","custo":"acao_bonus",
   "texto":"Move o Cubo até 18 metros para o chão a até 36 metros de você."}], subclasse=SUB)

# ------------------------------------------------------- Círculo das Estrelas
SUB="circulo_das_estrelas"
car("forma_estrelada","Forma Estrelada",3,98,
 "Ação Bônus gastando um uso de Forma Selvagem para assumir forma estrelada em vez de multimorfar: 10 minutos, Luz Plena em 3 m e Meia-luz por mais 3 m, com uma constelação à escolha (Arqueiro, Dragão ou Taça).",
 [{"tipo":"forma_selvagem","modo":"forma_alternativa","custo":"acao_bonus",
   "consome_recurso":"forma_selvagem","duracao":"10 minutos","mantem_estatisticas":True,
   "luz":{"plena_m":3,"meia_luz_adicional_m":3},
   "encerra_se":[{"gatilho":"dispensar"},{"condicao_id":"incapacitado"},
                 {"gatilho":"usar_a_caracteristica_de_novo"}]},
  {"id":"druida_constelacao","tipo":"escolha","rotulo":"Escolha a constelação","quantidade":1,
   "momento":"ao_assumir_a_forma","reescolhivel":True,
   "de":{"catalogo":"constelacoes","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}],
 subclasse=SUB,
 efeitos_nomeados={
  "arqueiro":{"efeitos":[{"tipo":"conceder_acao","id":"flecha_estelar","custo":"acao_bonus",
     "efeitos":[{"tipo":"dano","formula_dado":"1d8","somar":["mod:SAB"],"tipo_dano":"radiante",
                 "alcance_m":18,"exige_jogada_de_ataque":"magico_a_distancia"}]}]},
  "dragao":{"efeitos":[{"tipo":"tratar_resultado_minimo","alvo":["teste_de_atributo:INT",
     "teste_de_atributo:SAB","salvaguarda:CON"],"minimo":10,
     "condicao":{"todas":["salvaguarda_de_concentracao_ou_teste_int_sab"]}}]},
  "taca":{"efeitos":[{"tipo":"cura","formula":["1d8","mod:SAB"],
     "beneficiario":"voce_ou_criatura_a_ate_9m","gatilho":"conjurar_magia_de_cura_com_espaco"}]}})
car("mapa_estelar","Mapa Estelar",3,99,
 "Cria um mapa estelar Minúsculo que serve de Foco de Conjuração. Segurando-o, tem Orientação e Raio Guia preparadas e conjura Raio Guia sem gastar espaço, com usos iguais ao modificador de Sabedoria (mínimo 1), recarregados em Descanso Longo.",
 [{"tipo":"desbloquear_magias","lista_id":"druida","modo":"sempre_preparada",
   "magias":["orientacao","raio_guia"],"condicao":{"todas":["segurando:mapa_estelar"]}},
  {"tipo":"recurso_com_recarga","id":"mapa_estelar_raio_guia",
   "formula_maximo":{"op":"max","args":["1","mod:SAB"]},"recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"conjurar_sem_espaco","magia":"raio_guia","consome_recurso":"mapa_estelar_raio_guia"},
  {"tipo":"efeito_narrativo","chave":"foco_de_conjuracao","texto":"O mapa serve de Foco de Conjuração para suas magias de Druida. Se perdido, uma cerimônia de 1 hora (em descanso) cria outro e destrói o anterior."}],
 subclasse=SUB)
car("pressagio_cosmico","Presságio Cósmico",6,99,
 "A cada Descanso Longo joga um dado: par dá Prosperidade (Reação para somar 1d6 a um Teste de D20 de criatura à vista a até 9 m), ímpar dá Infortúnio (subtrair 1d6). Usos iguais ao modificador de Sabedoria (mínimo 1).",
 [{"tipo":"recurso_com_recarga","id":"pressagio_cosmico",
   "formula_maximo":{"op":"max","args":["1","mod:SAB"]},"recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"modificador","alvo":"teste_d20","valor":["1d6"],"empilha":"soma","custo":"reacao",
   "beneficiario":"criatura_a_vista_a_ate_9m","consome_recurso":"pressagio_cosmico",
   "sinal":"por_pressagio","nota":"Prosperidade (par) soma; Infortúnio (ímpar) subtrai. O presságio é sorteado no Descanso Longo."}],
 subclasse=SUB)
car("constelacoes_cintilantes","Constelações Cintilantes",10,99,
 "O 1d8 do Arqueiro e da Taça vira 2d8; o Dragão passa a dar Deslocamento de Voo de 6 m com capacidade de pairar; e você pode trocar de constelação no início de cada turno.",
 [{"tipo":"melhorar_caracteristica","alvo":"forma_estrelada","efeitos":[
   {"tipo":"efeito_narrativo","chave":"constelacoes_melhoradas",
    "texto":"Arqueiro e Taça passam a 2d8; Dragão concede Deslocamento de Voo 6 m com pairar; troca de constelação no início de cada turno."}]}],
 subclasse=SUB)
car("repleto_de_estrelas","Repleto de Estrelas",14,99,
 "Em Forma Estrelada, fica parcialmente incorpóreo e tem Resistência a dano Contundente, Cortante e Perfurante.",
 [{"tipo":"alterar_dano","tipo_dano":"contundente","operacao":"resistencia","condicao":{"todas":["em_forma_estrelada"]}},
  {"tipo":"alterar_dano","tipo_dano":"cortante","operacao":"resistencia","condicao":{"todas":["em_forma_estrelada"]}},
  {"tipo":"alterar_dano","tipo_dano":"perfurante","operacao":"resistencia","condicao":{"todas":["em_forma_estrelada"]}},
  {"tipo":"efeito_narrativo","chave":"parcialmente_incorporeo","texto":"Você se torna parcialmente incorpóreo."}],
 subclasse=SUB)

# ----------------------------------------------------------- Círculo do Mar
SUB="circulo_do_mar"
car("ira_do_mar","Ira do Mar",3,101,
 "Ação Bônus gastando um uso de Forma Selvagem para manifestar uma Emanação de 1,5 m por 10 minutos. Ao manifestar e como Ação Bônus depois, escolhe uma criatura na Emanação: salvaguarda de Constituição ou sofre dano Gélido de tantos d6 quanto seu modificador de Sabedoria (mínimo 1) e, se Grande ou menor, é empurrada até 4,5 m.",
 [{"tipo":"emanacao","id":"ira_do_mar","tamanho_m":1.5,"custo":"acao_bonus",
   "consome_recurso":"forma_selvagem","duracao":"10 minutos",
   "encerra_se":[{"gatilho":"dispersar"},{"gatilho":"manifestar_de_novo"},{"condicao_id":"incapacitado"}],
   "efeitos":[{"tipo":"dano","formula_dado":{"op":"mult","args":[{"op":"max","args":["1","mod:SAB"]},"1d6"]},
               "tipo_dano":"gelido","salvaguarda":{"atributo":"CON","cd":CD},
               "custo":"acao_bonus","alvo":"criatura_a_vista_na_emanacao"},
              {"tipo":"efeito_narrativo","chave":"empurrao_do_mar",
               "texto":"Alvo Grande ou menor que falhar é empurrado até 4,5 metros para longe de você."}]}],
 subclasse=SUB)
car("magias_do_circulo_do_mar","Magias do Círculo do Mar",3,101,
 "Magias sempre preparadas pela tabela Magias do Círculo do Mar.",
 [magias_circulo("Magias do Círculo do Mar",
   [(3,["despedacar","lufada_de_vento","nevoa_obscurecente","onda_trovejante","raio_de_gelo"]),
    (5,["relampago","respirar_na_agua"]),(7,["controlar_agua","tempestade_glacial"]),
    (9,["invocar_elemental","paralisar_monstro"])], 101)], subclasse=SUB)
car("afinidade_aquatica","Afinidade Aquática",6,101,
 "A Emanação da Ira do Mar cresce para 3 metros, e você ganha Deslocamento de Natação igual ao seu Deslocamento.",
 [{"tipo":"melhorar_caracteristica","alvo":"ira_do_mar",
   "efeitos":[{"tipo":"emanacao","id":"ira_do_mar","tamanho_m":3,"modo":"substitui_tamanho"}]},
  {"tipo":"conceder_velocidade","tipo_deslocamento":"natacao","formula":["deslocamento"]}], subclasse=SUB)
car("filho_da_tempestade","Filho da Tempestade",10,101,
 "Com a Ira do Mar ativa: Deslocamento de Voo igual ao seu Deslocamento e Resistência a dano Elétrico, Gélido e Trovejante.",
 [{"tipo":"conceder_velocidade","tipo_deslocamento":"voo","formula":["deslocamento"],
   "condicao":{"todas":["ativo:ira_do_mar"]}},
  {"tipo":"alterar_dano","tipo_dano":"eletrico","operacao":"resistencia","condicao":{"todas":["ativo:ira_do_mar"]}},
  {"tipo":"alterar_dano","tipo_dano":"gelido","operacao":"resistencia","condicao":{"todas":["ativo:ira_do_mar"]}},
  {"tipo":"alterar_dano","tipo_dano":"trovejante","operacao":"resistencia","condicao":{"todas":["ativo:ira_do_mar"]}}],
 subclasse=SUB)
car("manifestacao_oceanica","Manifestação Oceânica",14,101,
 "Pode manifestar a Emanação ao redor de uma criatura voluntária a até 18 m, que usa a sua CD e o seu modificador de Sabedoria; ou ao redor de vocês dois, gastando dois usos de Forma Selvagem.",
 [{"tipo":"melhorar_caracteristica","alvo":"ira_do_mar","efeitos":[
   {"tipo":"efeito_narrativo","chave":"emanacao_em_outro",
    "texto":"Manifesta a Emanação ao redor de criatura voluntária a até 18 m (usando sua CD e seu modificador de Sabedoria), ou ao redor de ambos gastando dois usos de Forma Selvagem."}]}],
 subclasse=SUB)

C['itens'] = C['itens'] + novos; C['total'] = len(C['itens']); wr('caracteristicas.json', C)

S = rd('subclasses.json'); S['itens'] = [s for s in S['itens'] if s.get('classe') != 'druida']
NOVAS = [
 ("circulo_da_lua","Círculo da Lua",96,"Canaliza a magia lunar na Forma Selvagem: formas mais fortes, dano radiante e teleporte de luar.",
  ["formas_animais_dos_circulos_druidicos","magias_do_circulo_da_lua",
   "formas_animais_dos_circulos_druidicos_aprimorada","passo_lunar","forma_lunar"]),
 ("circulo_da_terra","Círculo da Terra",97,"Místicos e sábios ligados ao terreno: magias que mudam com o bioma escolhido e recuperação natural.",
  ["auxilio_da_terra","magias_do_circulo_da_terra","recuperacao_natural","protecao_natural","santuario_natural"]),
 ("circulo_das_estrelas","Círculo das Estrelas",98,"Segue os padrões celestiais: forma estrelada com constelações e presságios.",
  ["forma_estrelada","mapa_estelar","pressagio_cosmico","constelacoes_cintilantes","repleto_de_estrelas"]),
 ("circulo_do_mar","Círculo do Mar",100,"Canaliza marés e tormentas numa Emanação de água que fere e empurra.",
  ["ira_do_mar","magias_do_circulo_do_mar","afinidade_aquatica","filho_da_tempestade","manifestacao_oceanica"])]
S['itens'] = S['itens'] + [{"id":i,"nome":n,"classe":"druida","fonte":f(p),"revisao":OK,
  "descricao_curta":d,"niveis_de_caracteristica":[3,6,10,14],"caracteristicas":c}
  for i,n,p,d,c in NOVAS]
S['total']=len(S['itens']); wr('subclasses.json', S)
print("caracteristicas:", C['total'], "| subclasses:", S['total'])
