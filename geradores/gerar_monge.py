# -*- coding: utf-8 -*-
"""Fase 2 — Classe Monge (cap. 3, p. 159-165) e suas 4 subclasses."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def w(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

MD = "dado_de_artes_marciais"          # coluna da tabela
CD_FOCO = ["8", "mod:SAB", "prof"]     # CD das características que gastam Ponto de Foco

# =========================================================== CLASSE
DADO_ARTES = {1:"1d6",2:"1d6",3:"1d6",4:"1d6",5:"1d8",6:"1d8",7:"1d8",8:"1d8",9:"1d8",10:"1d8",
 11:"1d10",12:"1d10",13:"1d10",14:"1d10",15:"1d10",16:"1d10",17:"1d12",18:"1d12",19:"1d12",20:"1d12"}
FOCO = {1:None,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,10:10,11:11,12:12,13:13,14:14,15:15,16:16,17:17,18:18,19:19,20:20}
MOV = {1:None,2:3,3:3,4:3,5:3,6:4.5,7:4.5,8:4.5,9:4.5,10:6,11:6,12:6,13:6,14:7.5,15:7.5,16:7.5,17:7.5,18:9,19:9,20:9}
CARACS_POR_NIVEL = {
 1:["artes_marciais","defesa_sem_armadura"],
 2:["foco_do_monge","movimento_sem_armadura","metabolismo_incomum"],
 3:["defletir_ataques","subclasse_de_monge"],
 4:["aumento_no_valor_de_atributo","queda_lenta"],
 5:["ataque_extra","golpe_atordoante"],
 6:["golpes_potencializados","caracteristica_de_subclasse"],
 7:["evasao"], 8:["aumento_no_valor_de_atributo"], 9:["movimento_acrobatico"],
 10:["restauro_pessoal","foco_aprimorado"], 11:["caracteristica_de_subclasse"],
 12:["aumento_no_valor_de_atributo"], 13:["defletir_energia"], 14:["sobrevivente_disciplinado"],
 15:["foco_perfeito"], 16:["aumento_no_valor_de_atributo"], 17:["caracteristica_de_subclasse"],
 18:["defesa_superior"], 19:["dadiva_epica"], 20:["corpo_e_mente"]}
BP = {1:2,2:2,3:2,4:2,5:3,6:3,7:3,8:3,9:4,10:4,11:4,12:4,13:5,14:5,15:5,16:5,17:6,18:6,19:6,20:6}

progressao = []
for n in range(1, 21):
    linha = {"nivel": n, "bonus_de_proficiencia": BP[n], "caracteristicas": CARACS_POR_NIVEL[n],
             "colunas": {MD: DADO_ARTES[n]}}
    if FOCO[n] is not None: linha["colunas"]["pontos_de_foco"] = FOCO[n]
    if MOV[n] is not None: linha["colunas"]["movimento_sem_armadura_m"] = MOV[n]
    progressao.append(linha)

classe = {
 "id": "monge", "nome": "Monge", "fonte": f(159), "revisao": OK,
 "descricao_curta": "Guerreiro que canaliza um poder interior por treinamento marcial e disciplina mental, lutando desarmado ou com armas leves e sem armadura.",
 "dado_de_vida": 8,
 "atributo_primario": ["DES", "SAB"],
 "salvaguardas_primarias": ["FOR", "DES"],
 "nivel_subclasse": 3,
 "conjuracao": None,
 "subclasses": ["combatente_da_mao_espalmada", "combatente_da_misericordia",
                "combatente_das_sombras", "combatente_dos_elementos"],
 "proficiencias_iniciais": [
   {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "FOR", "nivel_dominio": "proficiente"},
   {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "DES", "nivel_dominio": "proficiente"},
   {"id": "monge_pericias_iniciais", "tipo": "escolha", "rotulo": "Escolha 2 perícias",
    "quantidade": 2, "momento": "criacao",
    "de": {"catalogo": "pericias",
           "chaves": ["acrobacia", "atletismo", "furtividade", "historia", "intuicao", "religiao"]},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                  "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}},
   {"tipo": "conceder_proficiencia", "categoria": "arma", "chave": "categoria:simples", "nivel_dominio": "proficiente"},
   {"tipo": "conceder_proficiencia", "categoria": "arma",
    "chave": "categoria:marcial+propriedade:leve", "nivel_dominio": "proficiente",
    "nota": "Só armas Marciais que tenham a propriedade Leve."},
   {"id": "monge_ferramenta_inicial", "tipo": "escolha", "rotulo": "Escolha uma ferramenta",
    "quantidade": 1, "momento": "criacao",
    "de": {"catalogo": "ferramentas", "filtro": {"alguma": [{"grupo": "artesao"}, {"id": "instrumento_musical"}]}},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "ferramenta",
                                  "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}}],
 "treinamento_com_armadura": [],
 "equipamento_inicial": {"opcoes": [
   {"id": "A", "itens": [{"item": "lanca", "quantidade": 1}, {"item": "adaga", "quantidade": 5},
                         {"referencia": "ferramenta_escolhida_em:monge_ferramenta_inicial", "quantidade": 1},
                         {"item": "kit_de_aventureiro", "quantidade": 1}],
    "moedas": {"po": 11}},
   {"id": "B", "moedas": {"po": 50}}],
   "revisao": {"status": "duvida", "notas": "Os ids de item (lanca, adaga, kit_de_aventureiro) apontam para o catálogo de itens do cap. 6, que ainda não foi extraído. Ficam como referência pendente até a fase do equipamento."}},
 "progressao": progressao,
 "colunas_da_tabela": {
   MD: {"nome": "Artes Marciais", "tipo": "dado"},
   "pontos_de_foco": {"nome": "Pontos de Foco", "tipo": "inteiro"},
   "movimento_sem_armadura_m": {"nome": "Movimento sem Armadura", "tipo": "metros"}}}

w('classes.json', {"colecao": "classes", "total": 1, "itens": [classe]})

# =============================================== CARACTERÍSTICAS DE CLASSE
C = []
def car(id_, nome, nivel, pag, desc, efeitos, **kw):
    d = {"id": id_, "nome": nome, "classe": "monge", "nivel": nivel, "fonte": f(pag),
         "revisao": kw.pop("revisao", OK), "descricao_curta": desc, "efeitos": efeitos}
    d.update(kw); C.append(d)

SEM_ARMADURA = {"todas": ["flag:sem_armadura", "flag:sem_escudo"]}
ARMAS_MONGE = {"todas": ["flag:sem_armadura", "flag:sem_escudo",
                         {"alguma": ["desarmado", "empunhando_apenas:armas_de_monge"]}]}

car("artes_marciais", "Artes Marciais", 1, 159,
 "Desarmado ou com armas de Monge, sem armadura e sem Escudo: Ataque Desarmado como Ação Bônus, dado de dano próprio e uso de Destreza no lugar de Força.",
 [{"tipo": "conceder_acao", "id": "ataque_desarmado_bonus", "custo": "acao_bonus",
   "condicao": ARMAS_MONGE, "efeitos": [{"tipo": "conceder_ataque", "quantidade": ["1"], "tipo_ataque": "desarmado"}]},
  {"tipo": "dado_de_dano", "coluna": MD, "escopo": ["ataque_desarmado", "armas_de_monge"],
   "modo": "substitui_se_maior_a_criterio_do_jogador", "condicao": ARMAS_MONGE},
  {"tipo": "substituir_atributo", "de": "FOR", "para": "DES",
   "escopo": ["jogada_de_ataque", "jogada_de_dano", "cd_de_empurrar_ou_imobilizar"],
   "aplica_a": ["ataque_desarmado", "armas_de_monge"], "condicao": ARMAS_MONGE}],
 definicao_armas_de_monge={"inclui": ["categoria:simples+alcance:corpo_a_corpo",
                                      "categoria:marcial+alcance:corpo_a_corpo+propriedade:leve"]})

car("defesa_sem_armadura", "Defesa sem Armadura", 1, 159,
 "Sem armadura e sem Escudo, sua CA base é 10 + modificador de Destreza + modificador de Sabedoria.",
 [{"tipo": "ca_base", "formula": ["10", "mod:DES", "mod:SAB"], "permite_escudo": False,
   "condicao": SEM_ARMADURA, "empilha": "substitui"}])

car("foco_do_monge", "Foco do Monge", 2, 160,
 "Reserva de Pontos de Foco (igual ao nível de Monge, a partir do 2º) recuperada em Descanso Curto ou Longo. Desbloqueia Defesa Paciente, Passo do Vento e Torrente de Golpes. CD das características que usam Foco: 8 + mod. de Sabedoria + BP.",
 [{"tipo": "recurso_com_recarga", "id": "pontos_de_foco", "nome": "Pontos de Foco",
   "formula_maximo": ["coluna:pontos_de_foco"], "recarga": ["descanso_curto", "descanso_longo"],
   "consumo": "por_uso"},
  {"tipo": "conceder_acao", "id": "defesa_paciente", "custo": "acao_bonus",
   "descricao_curta": "Ação Desengajar como Ação Bônus; ou 1 Ponto de Foco para Desengajar e Esquivar como Ação Bônus.",
   "opcoes": [{"custo_em_foco": 0, "acoes": ["desengajar"]},
              {"custo_em_foco": 1, "acoes": ["desengajar", "esquivar"]}]},
  {"tipo": "conceder_acao", "id": "passo_do_vento", "custo": "acao_bonus",
   "descricao_curta": "Ação Correr como Ação Bônus; ou 1 Ponto de Foco para Desengajar e Correr como Ação Bônus, com distância de salto dobrada no turno.",
   "opcoes": [{"custo_em_foco": 0, "acoes": ["correr"]},
              {"custo_em_foco": 1, "acoes": ["desengajar", "correr"], "distancia_de_salto": "dobrada"}]},
  {"tipo": "conceder_acao", "id": "torrente_de_golpes", "custo": "acao_bonus",
   "descricao_curta": "Gaste 1 Ponto de Foco para realizar dois Ataques Desarmados como Ação Bônus.",
   "opcoes": [{"custo_em_foco": 1,
               "efeitos": [{"tipo": "conceder_ataque", "quantidade": ["2"], "tipo_ataque": "desarmado"}]}]}],
 cd_das_caracteristicas_de_foco=CD_FOCO)

car("movimento_sem_armadura", "Movimento sem Armadura", 2, 160,
 "Sem armadura e sem Escudo, seu Deslocamento aumenta conforme a coluna Movimento sem Armadura da tabela.",
 [{"tipo": "modificador", "alvo": "deslocamento", "valor": ["coluna:movimento_sem_armadura_m"],
   "unidade": "m", "empilha": "soma", "condicao": SEM_ARMADURA}])

car("metabolismo_incomum", "Metabolismo Incomum", 2, 160,
 "Ao jogar Iniciativa, pode restaurar todos os Pontos de Foco gastos e recuperar PV iguais ao nível de Monge mais uma jogada do dado de Artes Marciais. Recarrega em Descanso Longo.",
 [{"tipo": "recurso_com_recarga", "id": "metabolismo_incomum_usos", "formula_maximo": ["1"],
   "recarga": ["descanso_longo"], "consumo": "por_uso"},
  {"tipo": "restaurar_recurso", "recurso_id": "pontos_de_foco", "quantidade": "total",
   "gatilho": "jogar_iniciativa"},
  {"tipo": "cura", "formula": ["nivel_classe:monge", f"dado:{MD}"], "gatilho": "jogar_iniciativa"}])

car("defletir_ataques", "Defletir Ataques", 3, 160,
 "Reação ao ser atingido por ataque que cause dano Contundente, Cortante ou Perfurante: reduz o dano em 1d10 + mod. de Destreza + nível de Monge. Se zerar o dano, pode gastar 1 Ponto de Foco para redirecionar parte da força a uma criatura próxima.",
 [{"tipo": "reducao_de_dano", "custo": "reacao",
   "formula": ["1d10", "mod:DES", "nivel_classe:monge"],
   "tipos_de_dano": ["contundente", "cortante", "perfurante"]},
  {"tipo": "dano", "custo_em_foco": 1, "condicao": {"todas": ["dano_reduzido_a_zero"]},
   "formula_dado": {"op": "mult", "args": ["2", f"dado:{MD}"]}, "somar": ["mod:DES"],
   "tipo_dano": "mesmo_do_ataque_defletido",
   "alcance_m": {"corpo_a_corpo": 1.5, "a_distancia": 18},
   "salvaguarda": {"atributo": "DES", "cd": CD_FOCO, "sucesso": "nenhum_dano"}}])

car("subclasse_de_monge", "Subclasse de Monge", 3, 161,
 "Escolha uma subclasse de Monge; suas características chegam nos níveis 3, 6, 11 e 17.",
 [{"id": "monge_escolha_de_subclasse", "tipo": "escolha", "rotulo": "Escolha uma subclasse de Monge",
   "quantidade": 1, "momento": "nivel_3",
   "de": {"catalogo": "subclasses", "filtro": {"classe": "monge"}},
   "efeito_por_item_escolhido": {"tipo": "conceder_subclasse", "chave": "{{escolhido}}"}}])

car("aumento_no_valor_de_atributo", "Aumento no Valor de Atributo", 4, 161,
 "Adquire o talento Aumento no Valor de Atributo ou outro talento cujos pré-requisitos você atenda. Repete nos níveis 8, 12 e 16.",
 [{"id": "monge_asi", "tipo": "escolha", "rotulo": "Escolha um talento", "quantidade": 1,
   "momento": "nivel_da_caracteristica",
   "de": {"catalogo": "talentos", "filtro": {"categoria": "geral", "pre_requisitos_atendidos": True}},
   "efeito_por_item_escolhido": {"tipo": "conceder_talento", "talento_id": "{{escolhido}}"}}],
 niveis_repetidos=[4, 8, 12, 16], repetivel=True)

car("queda_lenta", "Queda Lenta", 4, 161,
 "Reação ao cair para reduzir o dano da queda em cinco vezes o seu nível de Monge.",
 [{"tipo": "reducao_de_dano", "custo": "reacao", "gatilho": "queda",
   "formula": [{"op": "mult", "args": ["5", "nivel_classe:monge"]}],
   "tipos_de_dano": ["contundente"], "origem_do_dano": "queda"}])

car("ataque_extra", "Ataque Extra", 5, 161,
 "Ataca duas vezes, em vez de uma, sempre que executa a ação Atacar no seu turno.",
 [{"tipo": "conceder_ataque", "quantidade": ["2"], "modo": "define_total_da_acao_atacar"}])

car("golpe_atordoante", "Golpe Atordoante", 5, 161,
 "Uma vez por turno, ao acertar com arma de Monge ou Ataque Desarmado, gaste 1 Ponto de Foco: salvaguarda de Constituição ou o alvo fica Atordoado até o início do seu próximo turno. Em caso de sucesso, Deslocamento do alvo pela metade e Vantagem no próximo ataque contra ele.",
 [{"tipo": "conceder_condicao", "condicao_id": "atordoado", "custo_em_foco": 1,
   "frequencia": "uma_vez_por_turno", "duracao": "ate_inicio_do_seu_proximo_turno",
   "salvaguarda": {"atributo": "CON", "cd": CD_FOCO},
   "em_sucesso": [{"tipo": "modificador", "alvo": "deslocamento",
                   "valor": {"op": "div_arred_baixo", "args": ["deslocamento", "2"]},
                   "beneficiario": "alvo", "empilha": "substitui",
                   "duracao": "ate_inicio_do_seu_proximo_turno"},
                  {"tipo": "vantagem", "alvo": "jogada_de_ataque_contra_voce", "modo": "vantagem",
                   "beneficiario": "proximo_atacante_do_alvo",
                   "duracao": "ate_inicio_do_seu_proximo_turno"}]}])

car("golpes_potencializados", "Golpes Potencializados", 6, 161,
 "Ao causar dano com o Ataque Desarmado, escolhe entre dano Energético ou o tipo normal.",
 [{"tipo": "escolher_tipo_de_dano", "aplica_a": ["ataque_desarmado"],
   "opcoes": ["energetico", "tipo_normal"]}],
 revisao={"status": "duvida", "notas": "A tabela Características do Monge (p. 160) chama esta característica de 'Ataques Potencializados'; o título da própria característica (p. 161) diz 'Golpes Potencializados'. Adotei o nome do corpo do texto. Confirmar qual usar no app."})

car("evasao", "Evasão", 7, 161,
 "Contra efeito que permita salvaguarda de Destreza por metade do dano: nenhum dano em caso de sucesso, metade em caso de falha. Não funciona se você estiver Incapacitado.",
 [{"tipo": "alterar_resultado_de_salvaguarda", "alvo": "salvaguarda:DES",
   "aplica_a": "efeito_com_metade_do_dano",
   "em_sucesso": "nenhum_dano", "em_falha": "metade_do_dano",
   "condicao": {"nao": "condicao:incapacitado"}}])

car("movimento_acrobatico", "Movimento Acrobático", 9, 161,
 "Sem armadura e sem Escudo, pode se mover por superfícies verticais e sobre líquidos no seu turno sem cair durante o movimento.",
 [{"tipo": "efeito_narrativo", "chave": "movimento_acrobatico", "condicao": SEM_ARMADURA,
   "texto": "Move-se por superfícies verticais e sobre líquidos durante o turno sem cair."}])

car("restauro_pessoal", "Restauro Pessoal", 10, 161,
 "No final de cada um dos seus turnos, remove de si Amedrontado, Enfeitiçado ou Envenenado (uma delas). Além disso, não sofre níveis de Exaustão por não comer nem beber.",
 [{"tipo": "remover_condicao", "condicoes": ["amedrontado", "enfeiticado", "envenenado"],
   "quantidade": 1, "momento": "fim_do_seu_turno"},
  {"tipo": "imunidade_a_risco", "riscos": ["desidratacao", "desnutricao"],
   "nota": "Não adquire níveis de Exaustão por não se alimentar nem se hidratar."}],
 revisao={"status": "duvida", "notas": "A tabela (p. 160) chama esta característica de 'Autocura'; o título da característica (p. 161) diz 'Restauro Pessoal'. Adotei o nome do corpo do texto. Confirmar qual usar no app."})

car("foco_aprimorado", "Foco Aprimorado", 10, 161,
 "Melhora Defesa Paciente (PV temporários), Passo do Vento (leva uma criatura junto) e Torrente de Golpes (três Ataques Desarmados).",
 [{"tipo": "melhorar_caracteristica", "alvo": "defesa_paciente",
   "efeitos": [{"tipo": "pontos_de_vida_temporarios",
                "formula": [{"op": "mult", "args": ["2", f"dado:{MD}"]}],
                "condicao": {"todas": ["gastou_ponto_de_foco"]}}]},
  {"tipo": "melhorar_caracteristica", "alvo": "passo_do_vento",
   "efeitos": [{"tipo": "efeito_narrativo", "chave": "leva_aliado",
                "texto": "Leva junto uma criatura voluntária Grande ou menor a até 1,5 m até o fim do turno; o movimento dela não provoca Ataques de Oportunidade."}]},
  {"tipo": "melhorar_caracteristica", "alvo": "torrente_de_golpes",
   "efeitos": [{"tipo": "conceder_ataque", "quantidade": ["3"], "tipo_ataque": "desarmado",
                "modo": "substitui_quantidade"}]}])

car("defletir_energia", "Defletir Energia", 13, 161,
 "Defletir Ataques passa a funcionar contra ataques de qualquer tipo de dano.",
 [{"tipo": "melhorar_caracteristica", "alvo": "defletir_ataques",
   "efeitos": [{"tipo": "reducao_de_dano", "tipos_de_dano": ["todos"], "modo": "substitui_lista"}]}])

car("sobrevivente_disciplinado", "Sobrevivente Disciplinado", 14, 161,
 "Proficiência em todas as salvaguardas. Ao falhar em uma salvaguarda, pode gastar 1 Ponto de Foco para jogar novamente e usar o novo resultado.",
 [{"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "todas", "nivel_dominio": "proficiente"},
  {"tipo": "rolar_novamente", "alvo": "salvaguarda", "custo_em_foco": 1,
   "gatilho": "falha", "usa_novo_resultado": True}])

car("foco_perfeito", "Foco Perfeito", 15, 161,
 "Ao jogar Iniciativa sem usar Metabolismo Incomum, recupera Pontos de Foco até ter 4, se tiver 3 ou menos.",
 [{"tipo": "restaurar_recurso", "recurso_id": "pontos_de_foco", "ate": 4,
   "condicao": {"todas": ["recurso:pontos_de_foco.atual<=3", {"nao": "usou:metabolismo_incomum"}]},
   "gatilho": "jogar_iniciativa"}])

car("defesa_superior", "Defesa Superior", 18, 161,
 "No início do seu turno, gaste 3 Pontos de Foco para ter Resistência a todos os tipos de dano exceto Energético, por 1 minuto ou até ficar Incapacitado.",
 [{"tipo": "alterar_dano", "tipo_dano": "todos", "operacao": "resistencia",
   "excecoes": ["energetico"], "custo_em_foco": 3, "duracao": "1 minuto",
   "encerra_se": [{"condicao_id": "incapacitado"}], "momento": "inicio_do_seu_turno"}])

car("dadiva_epica", "Dádiva Épica", 19, 161,
 "Adquire o talento Dádiva Épica ou outro talento para o qual se qualifique. Dádiva do Ataque Irresistível é a recomendação do livro.",
 [{"id": "monge_dadiva_epica", "tipo": "escolha", "rotulo": "Escolha um talento de Dádiva Épica",
   "quantidade": 1, "momento": "nivel_19",
   "de": {"catalogo": "talentos", "filtro": {"categoria": "epico", "pre_requisitos_atendidos": True}},
   "recomendado": "dadiva_do_ataque_irresistivel",
   "efeito_por_item_escolhido": {"tipo": "conceder_talento", "talento_id": "{{escolhido}}"}}])

car("corpo_e_mente", "Corpo e Mente", 20, 161,
 "Seus valores de Destreza e Sabedoria aumentam em 4, até o máximo de 25.",
 [{"tipo": "aumento_atributo", "distribuicao": {"DES": 4, "SAB": 4}, "limite": 25}])

# ------------------------------------------------ características de subclasse
SUB = "combatente_da_mao_espalmada"
car("tecnica_da_mao_espalmada", "Técnica da Mão Espalmada", 3, 162,
 "Ao atingir com um ataque da Torrente de Golpes, impõe ao alvo um efeito à escolha: Derrubar, Desorientar ou Empurrar.",
 [{"id": "mao_espalmada_efeito", "tipo": "escolha", "rotulo": "Escolha o efeito da técnica",
   "quantidade": 1, "momento": "no_acerto", "gatilho": "acerto_com_torrente_de_golpes",
   "de": {"catalogo": "efeitos_da_mao_espalmada",
          "chaves": ["derrubar", "desorientar", "empurrar"]},
   "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado", "chave": "{{escolhido}}"}}],
 subclasse=SUB,
 efeitos_nomeados={
  "derrubar": {"salvaguarda": {"atributo": "DES", "cd": CD_FOCO},
               "em_falha": [{"tipo": "conceder_condicao", "condicao_id": "caido"}]},
  "desorientar": {"efeitos": [{"tipo": "impedir", "alvo": "ataque_de_oportunidade_provocado_por_voce",
                               "beneficiario": "alvo", "duracao": "ate_inicio_do_proximo_turno_do_alvo"}]},
  "empurrar": {"salvaguarda": {"atributo": "FOR", "cd": CD_FOCO},
               "em_falha": [{"tipo": "efeito_narrativo", "chave": "empurrao",
                             "texto": "Empurra o alvo até 4,5 metros para longe de você."}]}})

car("integridade_corporal", "Integridade Corporal", 6, 162,
 "Ação Bônus para recuperar PV iguais a uma jogada do dado de Artes Marciais mais o modificador de Sabedoria (mínimo 1). Usos iguais ao modificador de Sabedoria (mínimo 1), recarregados em Descanso Longo.",
 [{"tipo": "recurso_com_recarga", "id": "integridade_corporal_usos",
   "formula_maximo": [{"op": "max", "args": ["1", "mod:SAB"]}], "recarga": ["descanso_longo"], "consumo": "por_uso"},
  {"tipo": "cura", "custo": "acao_bonus", "formula": [f"dado:{MD}", "mod:SAB"], "minimo": 1}],
 subclasse=SUB)

car("passo_veloz", "Passo Veloz", 11, 162,
 "Ao executar uma Ação Bônus que não seja Passo do Vento, pode usar Passo do Vento imediatamente depois dela.",
 [{"tipo": "efeito_narrativo", "chave": "passo_veloz",
   "texto": "Permite encaixar Passo do Vento logo após qualquer outra Ação Bônus no mesmo turno."}],
 subclasse=SUB)

car("palma_vibrante", "Palma Vibrante", 17, 162,
 "Ao acertar um Ataque Desarmado, gaste 4 Pontos de Foco para implantar vibrações que duram dias iguais ao seu nível de Monge. Ao encerrá-las, o alvo faz salvaguarda de Constituição e sofre 10d12 de dano Energético (metade em caso de sucesso). Só uma criatura por vez.",
 [{"tipo": "dano", "custo_em_foco": 4, "gatilho": "acerto_com_ataque_desarmado",
   "formula_dado": "10d12", "tipo_dano": "energetico",
   "salvaguarda": {"atributo": "CON", "cd": CD_FOCO, "sucesso": "metade"},
   "atraso": {"duracao_em_dias": ["nivel_classe:monge"],
              "encerramento": ["acao", "abrir_mao_de_um_ataque_da_acao_atacar"],
              "requer": "mesmo_plano_de_existencia"},
   "limite": "uma_criatura_por_vez"}],
 subclasse=SUB)

SUB = "combatente_da_misericordia"
car("implementos_de_misericordia", "Implementos de Misericórdia", 3, 162,
 "Proficiência nas perícias Intuição e Medicina e com o Kit de Herbalismo.",
 [{"tipo": "conceder_proficiencia", "categoria": "pericia", "chave": "intuicao", "nivel_dominio": "proficiente"},
  {"tipo": "conceder_proficiencia", "categoria": "pericia", "chave": "medicina", "nivel_dominio": "proficiente"},
  {"tipo": "conceder_proficiencia", "categoria": "ferramenta", "chave": "kit_de_herbalismo", "nivel_dominio": "proficiente"}],
 subclasse=SUB)

car("mao_de_cura", "Mão de Cura", 3, 163,
 "Ação Usar Magia e 1 Ponto de Foco para tocar uma criatura e curar uma jogada do dado de Artes Marciais mais o modificador de Sabedoria. Na Torrente de Golpes, pode trocar um Ataque Desarmado por este uso sem gastar o Ponto de Foco da cura.",
 [{"tipo": "cura", "custo": "acao", "acao_id": "usar_magia", "custo_em_foco": 1, "alcance": "toque",
   "formula": [f"dado:{MD}", "mod:SAB"]},
  {"tipo": "efeito_narrativo", "chave": "troca_na_torrente",
   "texto": "Na Torrente de Golpes, substitui um Ataque Desarmado por Mão de Cura sem gastar Ponto de Foco para a cura."}],
 subclasse=SUB)

car("mao_de_dolo", "Mão de Dolo", 3, 163,
 "Uma vez por turno, ao acertar e causar dano com um Ataque Desarmado, gaste 1 Ponto de Foco para causar dano Necrótico adicional igual a uma jogada do dado de Artes Marciais mais o modificador de Sabedoria.",
 [{"tipo": "dano", "custo_em_foco": 1, "frequencia": "uma_vez_por_turno",
   "gatilho": "acerto_com_ataque_desarmado", "formula_dado": f"dado:{MD}", "somar": ["mod:SAB"],
   "tipo_dano": "necrotico", "modo": "dano_adicional"}],
 subclasse=SUB)

car("toque_de_medico", "Toque de Médico", 6, 163,
 "Mão de Cura passa a encerrar uma condição na criatura curada (Atordoado, Cego, Envenenado, Paralisado ou Surdo); Mão de Dolo passa a impor Envenenado até o fim do seu próximo turno.",
 [{"tipo": "melhorar_caracteristica", "alvo": "mao_de_cura",
   "efeitos": [{"tipo": "remover_condicao", "quantidade": 1, "beneficiario": "alvo_curado",
                "condicoes": ["atordoado", "cego", "envenenado", "paralisado", "surdo"]}]},
  {"tipo": "melhorar_caracteristica", "alvo": "mao_de_dolo",
   "efeitos": [{"tipo": "conceder_condicao", "condicao_id": "envenenado", "beneficiario": "alvo",
                "duracao": "ate_o_fim_do_seu_proximo_turno"}]}],
 subclasse=SUB)

car("torrente_de_cura_e_dolo", "Torrente de Cura e Dolo", 11, 163,
 "Na Torrente de Golpes, pode trocar cada Ataque Desarmado por Mão de Cura sem gastar Foco, e usar Mão de Dolo num ataque da Torrente sem gastar Foco (ainda uma vez por turno). Usos iguais ao modificador de Sabedoria (mínimo 1), recarregados em Descanso Longo.",
 [{"tipo": "recurso_com_recarga", "id": "torrente_de_cura_e_dolo_usos",
   "formula_maximo": [{"op": "max", "args": ["1", "mod:SAB"]}], "recarga": ["descanso_longo"], "consumo": "por_uso"},
  {"tipo": "melhorar_caracteristica", "alvo": "mao_de_cura",
   "efeitos": [{"tipo": "efeito_narrativo", "chave": "cura_em_todos_os_ataques",
                "texto": "Cada Ataque Desarmado da Torrente pode virar Mão de Cura sem custo em Foco."}]},
  {"tipo": "melhorar_caracteristica", "alvo": "mao_de_dolo",
   "efeitos": [{"tipo": "efeito_narrativo", "chave": "dolo_sem_foco",
                "texto": "Mão de Dolo em um ataque da Torrente sem gastar Ponto de Foco; ainda uma vez por turno."}]}],
 subclasse=SUB)

car("mao_da_misericordia_final", "Mão da Misericórdia Final", 17, 163,
 "Ação Usar Magia e 5 Pontos de Foco para tocar o cadáver de quem morreu nas últimas 24 horas: a criatura volta à vida com 4d10 + modificador de Sabedoria PV, sem Atordoado, Cego, Envenenado, Paralisado e Surdo. Recarrega em Descanso Longo.",
 [{"tipo": "recurso_com_recarga", "id": "misericordia_final_usos", "formula_maximo": ["1"],
   "recarga": ["descanso_longo"], "consumo": "por_uso"},
  {"tipo": "cura", "custo": "acao", "acao_id": "usar_magia", "custo_em_foco": 5, "alcance": "toque",
   "formula": ["4d10", "mod:SAB"], "modo": "ressurreicao",
   "requisito": "cadáver de criatura morta há no máximo 24 horas"},
  {"tipo": "remover_condicao", "beneficiario": "alvo_curado",
   "condicoes": ["atordoado", "cego", "envenenado", "paralisado", "surdo"], "quantidade": "todas"}],
 subclasse=SUB)

SUB = "combatente_das_sombras"
car("artes_das_sombras", "Artes das Sombras", 3, 163,
 "Gaste 1 Ponto de Foco para conjurar Escuridão sem componentes, enxergando dentro dela e podendo movê-la até 18 m no início de cada turno. Conhece Ilusão Menor (Sabedoria como atributo de conjuração). Ganha Visão no Escuro de 18 m, ou +18 m se já tiver.",
 [{"tipo": "desbloquear_magias", "lista_id": "combatente_das_sombras_3", "modo": "conhecida",
   "magias": ["ilusao_menor"], "atributo_conjuracao": "SAB"},
  {"tipo": "desbloquear_magias", "lista_id": "combatente_das_sombras_escuridao", "modo": "conhecida",
   "magias": ["escuridao"], "atributo_conjuracao": "SAB", "custo_em_foco": 1,
   "sem_componentes": True,
   "nota": "Você enxerga na área da magia conjurada assim e pode mover a área até 18 m no início de cada turno seu."},
  {"tipo": "conceder_sentido", "sentido": "visao_no_escuro", "alcance_m": 18,
   "empilha": "soma", "nota": "Se já tiver Visão no Escuro, o alcance aumenta em 18 m."}],
 subclasse=SUB)

car("passo_da_sombra", "Passo da Sombra", 6, 164,
 "Inteiramente em Meia-luz ou Escuridão, Ação Bônus para se teleportar até 18 m a um espaço desocupado à vista também em Meia-luz ou Escuridão, ganhando Vantagem no próximo ataque corpo a corpo até o fim do turno.",
 [{"tipo": "teleporte", "custo": "acao_bonus", "alcance_m": 18,
   "requisitos": ["voce_em:meia_luz_ou_escuridao", "destino_em:meia_luz_ou_escuridao",
                  "destino_desocupado", "destino_a_vista"]},
  {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "vantagem",
   "aplica_a": "proximo_ataque_corpo_a_corpo", "duracao": "ate_o_fim_do_turno_atual"}],
 subclasse=SUB)

car("passo_da_sombra_aprimorado", "Passo da Sombra Aprimorado", 11, 164,
 "Gaste 1 Ponto de Foco no Passo da Sombra para dispensar a exigência de Meia-luz ou Escuridão, e realize um Ataque Desarmado logo após o teleporte, como parte da mesma Ação Bônus.",
 [{"tipo": "melhorar_caracteristica", "alvo": "passo_da_sombra", "custo_em_foco": 1,
   "efeitos": [{"tipo": "efeito_narrativo", "chave": "sem_requisito_de_luz",
                "texto": "Dispensa a exigência de iniciar ou encerrar o turno em Meia-luz ou Escuridão."},
               {"tipo": "conceder_ataque", "quantidade": ["1"], "tipo_ataque": "desarmado",
                "momento": "imediatamente_apos_o_teleporte"}]}],
 subclasse=SUB,
 revisao={"status": "duvida", "notas": "O texto de Passo da Sombra (nível 6) exige estar 'inteiramente em Meia-luz ou Escuridão'; já a melhoria de nível 11 fala em remover o requisito de 'iniciar ou encerrar seu turno' em Meia-luz ou Escuridão. As duas redações não batem. Copiei ambas literalmente; confirmar qual leitura vale na mesa."})

car("manto_da_sombra", "Manto da Sombra", 17, 164,
 "Ação Usar Magia, inteiramente em Meia-luz ou Escuridão, gastando 3 Pontos de Foco: por 1 minuto (ou até ficar Incapacitado ou encerrar o turno em Luz Plena) você fica Invisível, atravessa espaços ocupados como Terreno Difícil e usa Torrente de Golpes sem gastar Foco.",
 [{"tipo": "conceder_condicao", "condicao_id": "invisivel", "custo": "acao", "acao_id": "usar_magia",
   "custo_em_foco": 3, "duracao": "1 minuto",
   "requisitos": ["voce_em:meia_luz_ou_escuridao"],
   "encerra_se": [{"condicao_id": "incapacitado"}, {"gatilho": "encerrar_turno_em_luz_plena"}]},
  {"tipo": "efeito_narrativo", "chave": "parcialmente_incorporeo",
   "texto": "Move-se por espaços ocupados como se fossem Terreno Difícil; encerrando o turno num espaço desses, é deslocado para o último espaço desocupado."},
  {"tipo": "melhorar_caracteristica", "alvo": "torrente_de_golpes",
   "efeitos": [{"tipo": "efeito_narrativo", "chave": "torrente_sem_foco",
                "texto": "Torrente de Golpes sem gastar Pontos de Foco enquanto o manto durar."}]}],
 subclasse=SUB)

SUB = "combatente_dos_elementos"
car("manipular_elementos", "Manipular Elementos", 3, 164,
 "Conhece a magia Elementalismo, com Sabedoria como atributo de conjuração.",
 [{"tipo": "desbloquear_magias", "lista_id": "combatente_dos_elementos_3", "modo": "conhecida",
   "magias": ["elementalismo"], "atributo_conjuracao": "SAB"}],
 subclasse=SUB)

ELEM = ["acido", "eletrico", "gelido", "igneo", "trovejante"]
car("sintonia_elemental", "Sintonia Elemental", 3, 164,
 "No início do seu turno, gaste 1 Ponto de Foco para se imbuir de energia elemental por 10 minutos ou até ficar Incapacitado: escolhe o tipo de dano do Ataque Desarmado entre cinco elementais (com salvaguarda de Força para deslocar o alvo 3 m) e ganha +3 m de alcance no Ataque Desarmado.",
 [{"tipo": "recurso_com_recarga", "id": "sintonia_elemental_ativa", "formula_maximo": ["1"],
   "recarga": ["por_ativacao"], "custo_em_foco": 1, "duracao": "10 minutos",
   "momento": "inicio_do_seu_turno", "encerra_se": [{"condicao_id": "incapacitado"}]},
  {"tipo": "escolher_tipo_de_dano", "aplica_a": ["ataque_desarmado"], "opcoes": ELEM,
   "condicao": {"todas": ["ativo:sintonia_elemental"]}},
  {"tipo": "efeito_narrativo", "chave": "deslocar_alvo",
   "condicao": {"todas": ["ativo:sintonia_elemental", "causou_dano_elemental"]},
   "texto": "O alvo faz salvaguarda de Força; falhando, você pode movê-lo até 3 m na sua direção ou para longe.",
   "salvaguarda": {"atributo": "FOR", "cd": CD_FOCO}},
  {"tipo": "modificador", "alvo": "alcance_do_ataque_desarmado", "valor": ["3"], "unidade": "m",
   "empilha": "soma", "condicao": {"todas": ["ativo:sintonia_elemental"]}}],
 subclasse=SUB)

car("explosao_elemental", "Explosão Elemental", 6, 164,
 "Ação Usar Magia e 2 Pontos de Foco: Esfera de 6 m de raio centrada em um ponto a até 36 m. Escolha um tipo de dano elemental; cada criatura na área faz salvaguarda de Destreza, sofrendo três jogadas do dado de Artes Marciais (metade em caso de sucesso).",
 [{"tipo": "dano", "custo": "acao", "acao_id": "usar_magia", "custo_em_foco": 2,
   "formula_dado": {"op": "mult", "args": ["3", f"dado:{MD}"]},
   "escolher_tipo_de_dano": ELEM,
   "area": {"forma": "esfera", "raio_m": 6, "alcance_m": 36},
   "salvaguarda": {"atributo": "DES", "cd": CD_FOCO, "sucesso": "metade"}}],
 subclasse=SUB)

car("passo_dos_elementos", "Passo dos Elementos", 11, 164,
 "Com a Sintonia Elemental ativa, você também tem Deslocamento de Natação e de Voo iguais ao seu Deslocamento.",
 [{"tipo": "conceder_velocidade", "tipo_deslocamento": "natacao", "formula": ["deslocamento"],
   "condicao": {"todas": ["ativo:sintonia_elemental"]}},
  {"tipo": "conceder_velocidade", "tipo_deslocamento": "voo", "formula": ["deslocamento"],
   "condicao": {"todas": ["ativo:sintonia_elemental"]}}],
 subclasse=SUB)

car("apice_elemental", "Ápice Elemental", 17, 164,
 "Com a Sintonia Elemental ativa: dano extra de uma jogada do dado de Artes Marciais uma vez por turno no Ataque Desarmado; Passo do Vento passa a dar +6 m e a ferir quem você passa perto; e Resistência a um tipo elemental à sua escolha, trocável a cada turno.",
 [{"tipo": "dano", "frequencia": "uma_vez_por_turno", "gatilho": "acerto_com_ataque_desarmado",
   "formula_dado": f"dado:{MD}", "tipo_dano": "mesmo_do_ataque", "modo": "dano_adicional",
   "condicao": {"todas": ["ativo:sintonia_elemental"]}},
  {"tipo": "melhorar_caracteristica", "alvo": "passo_do_vento",
   "condicao": {"todas": ["ativo:sintonia_elemental"]},
   "efeitos": [{"tipo": "modificador", "alvo": "deslocamento", "valor": ["6"], "unidade": "m",
                "empilha": "soma", "duracao": "ate_o_fim_do_turno"},
               {"tipo": "dano", "formula_dado": f"dado:{MD}", "escolher_tipo_de_dano": ELEM,
                "gatilho": "entrar_em_espaco_a_ate_1_5m_da_criatura",
                "frequencia": "uma_vez_por_turno_por_criatura"}]},
  {"id": "apice_elemental_resistencia", "tipo": "escolha",
   "rotulo": "Escolha um tipo de dano para Resistência", "quantidade": 1,
   "momento": "inicio_do_seu_turno", "reescolhivel": True,
   "de": {"catalogo": "tipos_de_dano", "chaves": ELEM},
   "efeito_por_item_escolhido": {"tipo": "alterar_dano", "tipo_dano": "{{escolhido}}",
                                 "operacao": "resistencia"},
   "condicao": {"todas": ["ativo:sintonia_elemental"]}}],
 subclasse=SUB)

w('caracteristicas.json', {"colecao": "caracteristicas", "total": len(C), "itens": C})

# =========================================================== SUBCLASSES
S = [
 ("combatente_da_mao_espalmada", "Combatente da Mão Espalmada", 162,
  "Mestres do combate desarmado: empurram, derrubam e manipulam a própria energia para se proteger.",
  ["tecnica_da_mao_espalmada", "integridade_corporal", "passo_veloz", "palma_vibrante"]),
 ("combatente_da_misericordia", "Combatente da Misericórdia", 162,
  "Controlam a força vital alheia: curam com uma mão e eliminam com a outra.",
  ["implementos_de_misericordia", "mao_de_cura", "mao_de_dolo", "toque_de_medico",
   "torrente_de_cura_e_dolo", "mao_da_misericordia_final"]),
 ("combatente_das_sombras", "Combatente das Sombras", 163,
  "Praticam furtividade e subterfúgio aproveitando o poder do Sombral.",
  ["artes_das_sombras", "passo_da_sombra", "passo_da_sombra_aprimorado", "manto_da_sombra"]),
 ("combatente_dos_elementos", "Combatente dos Elementos", 164,
  "Dominam momentaneamente a energia do Caos Elemental para golpes e explosões.",
  ["manipular_elementos", "sintonia_elemental", "explosao_elemental", "passo_dos_elementos",
   "apice_elemental"])]
w('subclasses.json', {"colecao": "subclasses", "total": len(S),
  "itens": [{"id": i, "nome": n, "classe": "monge", "fonte": f(p), "revisao": OK,
             "descricao_curta": d, "niveis_de_caracteristica": [3, 6, 11, 17],
             "caracteristicas": c} for i, n, p, d, c in S]})

# ============================== catálogo parcial de magias (só as referenciadas)
w('catalogos/magias.json', {"catalogo": "magias", "nome": "Magias", "parcial": True,
  "fonte": {"capitulo": 7, "pagina_livro": 236, "pagina_pdf": 240},
  "nota": "PARCIAL: contém apenas as magias já referenciadas por outras entidades, para manter a integridade das chaves. O capítulo 7 completo ainda não foi extraído.",
  "total": 3,
  "itens": [
    {"id": "elementalismo", "nome": "Elementalismo", "nivel": 0, "fonte": {"capitulo": 7, "pagina_livro": 275, "pagina_pdf": 279}},
    {"id": "escuridao", "nome": "Escuridão", "nivel": 2, "fonte": {"capitulo": 7, "pagina_livro": 278, "pagina_pdf": 282}},
    {"id": "ilusao_menor", "nome": "Ilusão Menor", "nivel": 0, "fonte": {"capitulo": 7, "pagina_livro": 288, "pagina_pdf": 292}}]})

print("classe: 1 | caracteristicas:", len(C), "| subclasses:", len(S))
