# -*- coding: utf-8 -*-
"""Características do Clérigo e os 4 domínios."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
CD = ["8", "mod:SAB", "prof"]
C = rd('caracteristicas.json'); C['itens'] = [c for c in C['itens'] if c.get('classe') != 'clerigo']
novos = []
def car(id_, nome, nv, pag, desc, ef, **kw):
    d = {"id": id_, "nome": nome, "classe": "clerigo", "nivel": nv, "fonte": f(pag),
         "revisao": kw.pop("revisao", OK), "descricao_curta": desc, "efeitos": ef}
    d.update(kw); novos.append(d)
def tabela_dominio(nome, linhas, pag):
    return {"tipo":"magias_de_patrono","tabela":{"nome":nome,"fonte":f(pag),
            "linhas":[{"nivel":n,"magias":ms} for n,ms in linhas]},
            "modo":"sempre_preparada","nao_conta_para_o_limite":True}

car("conjuracao_clerigo","Conjuração",1,81,
 "Conjura magias de Clérigo com Sabedoria, preparando direto da lista da classe conforme a coluna Magias Preparadas. Usa Símbolo Sagrado como Foco de Conjuração.",
 [{"tipo":"conceder_slot","tabela_progressao_id":"clerigo",
   "colunas":[f"espacos_{i}" for i in range(1,10)],"recarga":"descanso_longo"},
  {"tipo":"preparar_magias","formula_quantidade":["coluna:magias_preparadas"],
   "atributo_conjuracao":"SAB","fonte_das_magias":"lista_de_classe","lista_id":"clerigo",
   "restricao":"de um círculo para o qual você possui espaços de magia",
   "magias_sempre_preparadas_nao_contam":True},
  {"tipo":"desbloquear_magias","lista_id":"clerigo","modo":"disponivel_para_preparar",
   "atributo_conjuracao":"SAB"},
  {"id":"clerigo_truques","tipo":"escolha","rotulo":"Escolha truques de Clérigo",
   "quantidade":"coluna:truques","momento":"nivel_1","reescolhivel":True,
   "reescolha_em":"cada_nivel_de_clerigo","reescolha_quantidade":1,
   "de":{"catalogo":"magias","filtro":{"nivel":0,"lista":"clerigo"}},
   "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"clerigo","modo":"conhecida",
                                "magia":"{{escolhido}}"}},
  {"id":"clerigo_preparadas","tipo":"escolha","rotulo":"Prepare magias de Clérigo",
   "quantidade":"coluna:magias_preparadas","momento":"nivel_1","reescolhivel":True,
   "reescolha_em":"descanso_longo",
   "de":{"catalogo":"magias","filtro":{"nivel_minimo":1,"lista":"clerigo",
                                       "circulo_com_espaco_disponivel":True}},
   "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"clerigo","modo":"preparada",
                                "magia":"{{escolhido}}"}}],
 foco_de_conjuracao=["simbolo_sagrado"], cd_para_evitar_sua_magia=CD)

car("ordem_divina","Ordem Divina",1,82,
 "Escolhe um papel sagrado: Protetor (armas Marciais e Armadura Pesada) ou Taumaturgo (um truque a mais e bônus igual ao modificador de Sabedoria em Arcanismo/Religião).",
 [{"id":"clerigo_ordem_divina","tipo":"escolha","rotulo":"Escolha sua Ordem Divina","quantidade":1,
   "momento":"nivel_1","de":{"catalogo":"ordens_divinas","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}],
 efeitos_nomeados={
  "protetor":{"efeitos":[
    {"tipo":"conceder_proficiencia","categoria":"arma","chave":"categoria:marcial","nivel_dominio":"proficiente"},
    {"tipo":"conceder_proficiencia","categoria":"armadura","chave":"pesada","nivel_dominio":"proficiente"}]},
  "taumaturgo":{"efeitos":[
    {"tipo":"modificador","alvo":"teste_de_atributo","valor":{"op":"max","args":["1","mod:SAB"]},
     "empilha":"soma","condicao":{"alguma":["teste:INT.arcanismo","teste:INT.religiao"]}},
    {"id":"taumaturgo_truque_extra","tipo":"escolha","rotulo":"Escolha um truque de Clérigo adicional",
     "quantidade":1,"momento":"nivel_1",
     "de":{"catalogo":"magias","filtro":{"nivel":0,"lista":"clerigo"}},
     "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","lista_id":"clerigo","modo":"conhecida",
                                  "magia":"{{escolhido}}","nao_conta_para_o_limite":True}}]}})

car("canalizar_divindade","Canalizar Divindade",2,82,
 "Recurso da classe conforme a coluna Canalizar Divindade, recuperando um uso em Descanso Curto e todos no Longo. Começa com Centelha Divina e Expulsar Mortos-Vivos; subclasses acrescentam opções. A CD dos efeitos é a mesma da sua Conjuração.",
 [{"tipo":"recurso_com_recarga","id":"canalizar_divindade","nome":"Canalizar Divindade",
   "formula_maximo":["coluna:canalizar_divindade"],
   "recarga":[{"gatilho":"descanso_curto","quantidade":1},
              {"gatilho":"descanso_longo","quantidade":"todos"}],"consumo":"por_uso"},
  {"tipo":"canalizar_divindade","recurso_id":"canalizar_divindade",
   "opcoes":{"catalogo":"efeitos_de_canalizar_divindade","base":["centelha_divina","expulsar_mortos_vivos"],
             "expansivel_por_subclasse":True},
   "cd":CD}],
 efeitos_nomeados={
  "centelha_divina":{"custo":"acao","acao_id":"usar_magia","alcance_m":9,
   "formula":["1d8","mod:SAB"],"escalonamento_por_nivel":{"7":"2d8","13":"3d8","18":"4d8"},
   "efeitos":[{"tipo":"cura","formula":["1d8","mod:SAB"],"alternativa":True},
              {"tipo":"dano","formula_dado":"1d8","somar":["mod:SAB"],
               "escolher_tipo_de_dano":["necrotico","radiante"],
               "salvaguarda":{"atributo":"CON","cd":CD,"sucesso":"metade"}}]},
  "expulsar_mortos_vivos":{"custo":"acao","acao_id":"usar_magia","alcance_m":9,
   "efeitos":[{"tipo":"conceder_condicao","condicao_id":"amedrontado","beneficiario":"mortos_vivos_a_escolha",
               "salvaguarda":{"atributo":"SAB","cd":CD},"duracao":"1 minuto"},
              {"tipo":"conceder_condicao","condicao_id":"incapacitado","beneficiario":"mortos_vivos_a_escolha",
               "duracao":"1 minuto"}],
   "encerra_se":[{"gatilho":"a_criatura_sofre_dano"},{"condicao_id":"incapacitado"},{"gatilho":"morte"}]}})

car("subclasse_de_clerigo","Subclasse de Clérigo",3,83,
 "Escolhe um domínio; as características chegam nos níveis 3, 6 e 17.",
 [{"id":"clerigo_escolha_de_subclasse","tipo":"escolha","rotulo":"Escolha um domínio","quantidade":1,
   "momento":"nivel_3","de":{"catalogo":"subclasses","filtro":{"classe":"clerigo"}},
   "efeito_por_item_escolhido":{"tipo":"conceder_subclasse","chave":"{{escolhido}}"}}])

car("fulminar_mortos_vivos","Fulminar Mortos-Vivos",5,83,
 "Ao usar Expulsar Mortos-Vivos, joga tantos d8 quanto seu modificador de Sabedoria (mínimo 1d8): cada Morto-Vivo que falhar sofre esse dano Radiante, sem encerrar o efeito.",
 [{"tipo":"melhorar_caracteristica","alvo":"canalizar_divindade",
   "efeitos":[{"tipo":"dano","formula_dado":{"op":"mult","args":[{"op":"max","args":["1","mod:SAB"]},"1d8"]},
               "tipo_dano":"radiante","condicao":{"todas":["falhou_em:expulsar_mortos_vivos"]},
               "nao_encerra_o_efeito":True}]}])

car("golpes_abencoados","Golpes Abençoados",7,83,
 "Escolhe Conjuração Poderosa (modificador de Sabedoria no dano dos truques de Clérigo) ou Golpe Divino (1d8 extra de dano Necrótico ou Radiante, uma vez por turno, ao acertar com arma).",
 [{"id":"clerigo_golpes_abencoados","tipo":"escolha","rotulo":"Escolha os Golpes Abençoados",
   "quantidade":1,"momento":"nivel_7",
   "de":{"catalogo":"opcoes_de_golpes_abencoados","todo_o_catalogo":True},
   "efeito_por_item_escolhido":{"tipo":"aplicar_efeito_nomeado","chave":"{{escolhido}}"}}],
 efeitos_nomeados={
  "conjuracao_poderosa":{"efeitos":[{"tipo":"modificador","alvo":"jogada_de_dano","valor":["mod:SAB"],
    "empilha":"soma","condicao":{"todas":["magia_nivel:0","lista:clerigo"]}}]},
  "golpe_divino":{"efeitos":[{"tipo":"dano","formula_dado":"1d8","modo":"dano_adicional",
    "frequencia":"uma_vez_por_turno","escolher_tipo_de_dano":["necrotico","radiante"],
    "gatilho":"acerto_com_arma"}]}},
 nota="Se você já tiver uma dessas opções por subclasse de um livro antigo de D&D, vale só a escolhida aqui.")

car("intervencao_divina","Intervenção Divina",10,83,
 "Ação Usar Magia para conjurar, sem gastar espaço nem componentes Materiais, qualquer magia de Clérigo de 5º círculo ou inferior que não exija Reação. Recarrega em Descanso Longo.",
 [{"tipo":"recurso_com_recarga","id":"intervencao_divina","formula_maximo":["1"],
   "recarga":["descanso_longo"],"consumo":"por_uso"},
  {"id":"clerigo_intervencao","tipo":"escolha","rotulo":"Escolha a magia da Intervenção Divina",
   "quantidade":1,"momento":"ao_usar","custo":"acao","acao_id":"usar_magia",
   "de":{"catalogo":"magias","filtro":{"lista":"clerigo","nivel_maximo":5}},
   "restricao":"a magia não pode ter tempo de conjuração de Reação",
   "efeito_por_item_escolhido":{"tipo":"conjurar_sem_espaco","magia":"{{escolhido}}",
     "sem_componentes_materiais":True,"consome_recurso":"intervencao_divina"}}])

car("golpes_abencoados_aprimorados","Golpes Abençoados Aprimorados",14,84,
 "A opção escolhida melhora: Conjuração Poderosa passa a dar PV temporários iguais ao dobro do modificador de Sabedoria ao causar dano com truque; Golpe Divino sobe para 2d8.",
 [{"tipo":"melhorar_caracteristica","alvo":"golpes_abencoados",
   "efeitos":[{"tipo":"efeito_narrativo","chave":"golpes_aprimorados",
     "texto":"Conjuração Poderosa: ao causar dano com truque de Clérigo, você ou criatura a até 18 m ganha PV temporários iguais ao dobro do modificador de Sabedoria. Golpe Divino: dano adicional vira 2d8."}]}])

car("intervencao_divina_maior","Intervenção Divina Maior",20,84,
 "A Intervenção Divina passa a poder escolher Desejo; usando assim, só volta depois de 2d4 Descansos Longos.",
 [{"tipo":"melhorar_caracteristica","alvo":"intervencao_divina",
   "efeitos":[{"tipo":"conjurar_sem_espaco","magia":"desejo",
     "recarga":["2d4_descansos_longos"],
     "nota":"Escolher Desejo troca a recarga normal por 2d4 Descansos Longos."}]}])

# ------------------------------------------------------------- Domínio da Guerra
SUB="dominio_da_guerra"
car("magias_de_dominio_da_guerra","Magias de Domínio da Guerra",3,85,
 "Magias sempre preparadas pela tabela Magias de Domínio da Guerra, sem contar para o limite.",
 [tabela_dominio("Magias de Domínio da Guerra",
   [(3,["arma_espiritual","arma_magica","escudo_da_fe","raio_guia"]),
    (5,["guardioes_espirituais","manto_do_cruzado"]),
    (7,["escudo_ardente","movimentacao_livre"]),
    (9,["golpe_de_arco","paralisar_monstro"])], 85)], subclasse=SUB)
car("ataque_direcionado","Ataque Direcionado",3,85,
 "Quando você ou criatura a até 9 m erra um ataque, gasta um uso de Canalizar Divindade para dar +10 à jogada. Para outra criatura, você usa sua Reação.",
 [{"tipo":"modificador","alvo":"jogada_de_ataque","valor":["10"],"empilha":"soma",
   "gatilho":"erro","momento":"apos_a_jogada","consome_recurso":"canalizar_divindade",
   "beneficiario":"voce_ou_criatura_a_ate_9m","custo_para_outro":"reacao"}], subclasse=SUB)
car("sacerdote_da_guerra","Sacerdote da Guerra",3,86,
 "Ação Bônus para atacar com arma ou Ataque Desarmado. Usos iguais ao modificador de Sabedoria (mínimo 1), recarregados em Descanso Curto ou Longo.",
 [{"tipo":"recurso_com_recarga","id":"sacerdote_da_guerra",
   "formula_maximo":{"op":"max","args":["1","mod:SAB"]},
   "recarga":["descanso_curto","descanso_longo"],"consumo":"por_uso"},
  {"tipo":"conceder_acao","id":"ataque_do_sacerdote","custo":"acao_bonus",
   "consome_recurso":"sacerdote_da_guerra",
   "efeitos":[{"tipo":"conceder_ataque","quantidade":["1"]}]}], subclasse=SUB)
car("bencao_do_deus_da_guerra","Bênção do Deus da Guerra",6,86,
 "Gasta um uso de Canalizar Divindade para conjurar Arma Espiritual ou Escudo da Fé sem espaço de magia e sem Concentração; dura 1 minuto e encerra se reconjurar, ficar Incapacitado ou morrer.",
 [{"tipo":"conjurar_sem_espaco","magias":["arma_espiritual","escudo_da_fe"],
   "consome_recurso":"canalizar_divindade","dispensa_concentracao":True,"duracao":"1 minuto",
   "encerra_se":[{"gatilho":"reconjurar"},{"condicao_id":"incapacitado"},{"gatilho":"morte"}]}],
 subclasse=SUB)
car("avatar_da_guerra","Avatar da Guerra",17,86,
 "Resistência a dano Contundente, Cortante e Perfurante.",
 [{"tipo":"alterar_dano","tipo_dano":"contundente","operacao":"resistencia"},
  {"tipo":"alterar_dano","tipo_dano":"cortante","operacao":"resistencia"},
  {"tipo":"alterar_dano","tipo_dano":"perfurante","operacao":"resistencia"}], subclasse=SUB)

# ---------------------------------------------------------------- Domínio da Luz
SUB="dominio_da_luz"
car("brilho_do_amanhecer","Brilho do Amanhecer",3,86,
 "Ação Usar Magia gastando um uso de Canalizar Divindade: Emanação de 9 m que dissipa Escuridão mágica; criaturas à escolha fazem salvaguarda de Constituição, sofrendo 2d10 + nível de Clérigo de dano Radiante (metade no sucesso).",
 [{"tipo":"dano","custo":"acao","acao_id":"usar_magia","consome_recurso":"canalizar_divindade",
   "formula_dado":"2d10","somar":["nivel_classe:clerigo"],"tipo_dano":"radiante",
   "area":{"forma":"emanacao","tamanho_m":9},
   "salvaguarda":{"atributo":"CON","cd":CD,"sucesso":"metade"}},
  {"tipo":"efeito_narrativo","chave":"dissipa_escuridao_magica",
   "texto":"Qualquer Escuridão mágica na área é dissipada."}], subclasse=SUB)
car("labareda_protetora","Labareda Protetora",3,86,
 "Reação para impor Desvantagem numa jogada de ataque de criatura à vista a até 9 m. Usos iguais ao modificador de Sabedoria (mínimo 1), recarregados em Descanso Longo.",
 [{"tipo":"recurso_com_recarga","id":"labareda_protetora",
   "formula_maximo":{"op":"max","args":["1","mod:SAB"]},"recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"desvantagem","custo":"reacao",
   "beneficiario":"criatura_a_vista_a_ate_9m","consome_recurso":"labareda_protetora"}], subclasse=SUB)
car("magias_de_dominio_da_luz","Magias de Domínio da Luz",3,87,
 "Magias sempre preparadas pela tabela Magias de Domínio da Luz.",
 [tabela_dominio("Magias de Domínio da Luz",
   [(3,["fogo_das_fadas","maos_ardentes","raio_ardente","ver_o_invisivel"]),
    (5,["bola_de_fogo","luz_do_dia"]),(7,["muralha_de_fogo","olho_arcano"]),
    (9,["coluna_de_chamas","videncia"])], 87)], subclasse=SUB,
 revisao={"status":"duvida","notas":"A tabela grafa 'Mãos Ardentes'; a lista do Mago (p. 150) e o cap. 7 usam 'Mãos Flamejantes'. Mantive o id maos_ardentes apontando para a entrada própria até conferir se são a mesma magia com nome inconsistente no livro."})
car("labareda_protetora_aprimorada","Labareda Protetora Aprimorada",6,87,
 "Labareda Protetora passa a recarregar em Descanso Curto ou Longo, e concede ao alvo do ataque 2d6 + modificador de Sabedoria de PV temporários.",
 [{"tipo":"melhorar_caracteristica","alvo":"labareda_protetora",
   "efeitos":[{"tipo":"recurso_com_recarga","id":"labareda_protetora",
               "recarga":["descanso_curto","descanso_longo"],"modo":"substitui_recarga"},
              {"tipo":"pontos_de_vida_temporarios","formula":["2d6","mod:SAB"],
               "beneficiario":"alvo_do_ataque"}]}], subclasse=SUB)
car("coroa_de_luz","Coroa de Luz",17,87,
 "Ação Usar Magia: aura de luz solar por 1 minuto, com Luz Plena em 18 m e Meia-luz por mais 9 m. Inimigos na Luz Plena têm Desvantagem em salvaguardas contra seu Brilho do Amanhecer e contra magias suas de dano Ígneo ou Radiante. Usos iguais ao modificador de Sabedoria.",
 [{"tipo":"recurso_com_recarga","id":"coroa_de_luz",
   "formula_maximo":{"op":"max","args":["1","mod:SAB"]},"recarga":["descanso_longo"],"consumo":"por_uso"},
  {"tipo":"vantagem","alvo":"salvaguarda","modo":"desvantagem","beneficiario":"inimigos_na_luz_plena",
   "custo":"acao","acao_id":"usar_magia","duracao":"1 minuto","consome_recurso":"coroa_de_luz",
   "condicao":{"alguma":["contra:brilho_do_amanhecer","magia_com_dano:igneo","magia_com_dano:radiante"]}},
  {"tipo":"efeito_narrativo","chave":"aura_de_luz","texto":"Luz Plena em raio de 18 m e Meia-luz por mais 9 m."}],
 subclasse=SUB)

# ------------------------------------------------------------ Domínio da Trapaça
SUB="dominio_da_trapaca"
car("magias_de_dominio_da_trapaca","Magias de Domínio da Trapaça",3,88,
 "Magias sempre preparadas pela tabela Magias de Domínio da Trapaça.",
 [tabela_dominio("Magias de Domínio da Trapaça",
   [(3,["disfarcar_se","enfeiticar_pessoa","invisibilidade","passo_sem_rastro"]),
    (5,["indetectavel","padrao_hipnotico"]),(7,["confusao","porta_dimensional"]),
    (9,["dominar_pessoa","modificar_memoria"])], 88)], subclasse=SUB)
car("bencao_do_trapaceiro","Bênção do Trapaceiro",3,88,
 "Ação Usar Magia para dar a si ou a criatura voluntária a até 9 m Vantagem em testes de Destreza (Furtividade), até o Descanso Longo ou até usar de novo.",
 [{"tipo":"vantagem","alvo":"teste_de_atributo:furtividade","modo":"vantagem",
   "custo":"acao","acao_id":"usar_magia","beneficiario":"voce_ou_criatura_voluntaria_a_ate_9m",
   "duracao":"ate_o_descanso_longo_ou_novo_uso"}], subclasse=SUB)
car("invocar_duplicidade","Invocar Duplicidade",3,88,
 "Ação Bônus gastando Canalizar Divindade para criar uma ilusão perfeita de si a até 9 m, por 1 minuto: conjura como se estivesse no espaço dela, tem Vantagem contra quem estiver a até 1,5 m de ambos, e move a ilusão até 9 m com Ação Bônus.",
 [{"tipo":"conceder_acao","id":"invocar_duplicidade","custo":"acao_bonus",
   "consome_recurso":"canalizar_divindade","duracao":"1 minuto",
   "encerra_se":[{"condicao_id":"incapacitado"},{"gatilho":"encerrar"}],
   "efeitos":[{"tipo":"efeito_narrativo","chave":"conjurar_do_espaco_da_ilusao",
               "texto":"Conjura magias como se estivesse no espaço da ilusão, usando os próprios sentidos."},
              {"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem",
               "condicao":{"todas":["voce_e_a_ilusao_a_ate_1_5m_do_alvo","alvo_ve_a_ilusao"]}},
              {"tipo":"efeito_narrativo","chave":"mover_ilusao","custo":"acao_bonus",
               "texto":"Move a ilusão até 9 m para espaço desocupado a até 36 m de você."}]}],
 subclasse=SUB)
car("transposicao_do_trapaceiro","Transposição do Trapaceiro",6,88,
 "Ao criar ou mover a ilusão do Invocar Duplicidade, pode se teleportar trocando de lugar com ela.",
 [{"tipo":"melhorar_caracteristica","alvo":"invocar_duplicidade",
   "efeitos":[{"tipo":"teleporte","destino":"espaco_da_ilusao","modo":"troca_de_lugar",
               "gatilho":"criar_ou_mover_a_ilusao"}]}], subclasse=SUB)
car("duplicidade_aprimorada","Duplicidade Aprimorada",17,88,
 "A ilusão passa a dar Vantagem também aos seus aliados contra quem estiver a até 1,5 m dela, e ao terminar cura você ou criatura a até 1,5 m dela em PV iguais ao seu nível de Clérigo.",
 [{"tipo":"melhorar_caracteristica","alvo":"invocar_duplicidade",
   "efeitos":[{"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem",
               "beneficiario":"voce_e_aliados","condicao":{"todas":["alvo_a_ate_1_5m_da_ilusao"]}},
              {"tipo":"cura","formula":["nivel_classe:clerigo"],
               "beneficiario":"voce_ou_criatura_a_ate_1_5m_da_ilusao",
               "gatilho":"a_ilusao_termina"}]}], subclasse=SUB)

# --------------------------------------------------------------- Domínio da Vida
SUB="dominio_da_vida"
car("magias_de_dominio_da_vida","Magias de Domínio da Vida",3,89,
 "Magias sempre preparadas pela tabela Magias de Domínio da Vida.",
 [tabela_dominio("Magias de Domínio da Vida",
   [(3,["auxilio","bencao","curar_ferimentos","restauracao_menor"]),
    (5,["palavra_curativa_em_massa","revivificar"]),
    (7,["aura_de_vida","protecao_contra_a_morte"]),
    (9,["curar_ferimentos_em_massa","restauracao_maior"])], 89)], subclasse=SUB)
car("discipulo_da_vida","Discípulo da Vida",3,89,
 "Suas magias de cura restauram PV adicionais iguais a 2 mais o círculo do espaço gasto.",
 [{"tipo":"cura","modo":"cura_adicional",
   "formula":[{"op":"soma","args":["2","circulo_do_espaco_gasto"]}],
   "gatilho":"conjurar_magia_que_restaura_pv"}], subclasse=SUB)
car("preservar_a_vida","Preservar a Vida",3,89,
 "Ação Usar Magia gastando Canalizar Divindade: distribui cinco vezes seu nível de Clérigo em PV entre criaturas Sangrando a até 9 m (você incluído), sem passar da metade dos PV máximos de cada uma.",
 [{"tipo":"cura","custo":"acao","acao_id":"usar_magia","consome_recurso":"canalizar_divindade",
   "formula":[{"op":"mult","args":["5","nivel_classe:clerigo"]}],
   "modo":"distribuir_entre_alvos","alcance_m":9,
   "condicao_do_alvo":{"todas":["estado:sangrando"]},
   "limite_por_alvo":"metade dos Pontos de Vida máximos"}], subclasse=SUB)
car("curandeiro_abencoado","Curandeiro Abençoado",6,89,
 "Ao conjurar com espaço uma magia que cure outra criatura, você também recupera PV iguais a 2 mais o círculo do espaço.",
 [{"tipo":"cura","formula":[{"op":"soma","args":["2","circulo_do_espaco_gasto"]}],
   "beneficiario":"voce","gatilho":"conjurar_magia_de_cura_em_outra_criatura"}], subclasse=SUB)
car("cura_suprema","Cura Suprema",17,89,
 "Ao restaurar PV com magia ou Canalizar Divindade, não joga os dados: usa o resultado máximo de cada um.",
 [{"tipo":"efeito_narrativo","chave":"cura_maximizada",
   "texto":"Toda cura sua por magia ou Canalizar Divindade usa o resultado máximo de cada dado."}],
 subclasse=SUB)

C['itens'] = C['itens'] + novos; C['total'] = len(C['itens']); wr('caracteristicas.json', C)
S = rd('subclasses.json'); S['itens'] = [s for s in S['itens'] if s.get('classe') != 'clerigo']
NOVAS = [
 ("dominio_da_guerra","Domínio da Guerra",85,"Inspira bravura e derrota inimigos: ataque extra, bônus de acerto e resistência física.",
  ["magias_de_dominio_da_guerra","ataque_direcionado","sacerdote_da_guerra","bencao_do_deus_da_guerra","avatar_da_guerra"]),
 ("dominio_da_luz","Domínio da Luz",86,"Traz luz para banir a escuridão: explosões radiantes e labaredas que atrapalham o inimigo.",
  ["brilho_do_amanhecer","labareda_protetora","magias_de_dominio_da_luz","labareda_protetora_aprimorada","coroa_de_luz"]),
 ("dominio_da_trapaca","Domínio da Trapaça",88,"Enganação, ilusão e furtividade, com uma cópia ilusória de si mesmo.",
  ["magias_de_dominio_da_trapaca","bencao_do_trapaceiro","invocar_duplicidade","transposicao_do_trapaceiro","duplicidade_aprimorada"]),
 ("dominio_da_vida","Domínio da Vida",89,"Mestre da cura: energia positiva que sustenta e restaura.",
  ["magias_de_dominio_da_vida","discipulo_da_vida","preservar_a_vida","curandeiro_abencoado","cura_suprema"])]
S['itens'] = S['itens'] + [{"id":i,"nome":n,"classe":"clerigo","fonte":f(p),"revisao":OK,
  "descricao_curta":d,"niveis_de_caracteristica":[3,6,17],"caracteristicas":c}
  for i,n,p,d,c in NOVAS]
S['total']=len(S['itens']); wr('subclasses.json', S)
print("caracteristicas:", C['total'], "| subclasses:", S['total'])
