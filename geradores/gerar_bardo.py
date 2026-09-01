# -*- coding: utf-8 -*-
"""Bardo (cap. 3, p. 59-67).

O ponto do esquema aqui é Segredos Mágicos: acesso a listas alheias EM ESCALA.
Não é uma escolha nova nem chaves soltas — é o filtro da escolha já existente
que se alarga. Por isso `expandir_opcoes_de_escolha` ganha uma segunda forma:
além de `chaves`, aceita `filtro`. O validador resolve as duas.
"""
import json, collections

F = {"capitulo": 3}


def fonte(p):
    return {"capitulo": 3, "pagina_livro": p, "pagina_pdf": p + 4}


def rev(status="ok", notas=""):
    return {"status": status, "notas": notas}


CARACS = []


def car(cid, nome, nivel, pag, desc, efeitos, **extra):
    d = collections.OrderedDict([
        ("id", cid), ("nome", nome), ("classe", "bardo"), ("nivel", nivel),
        ("fonte", fonte(pag)), ("revisao", rev()),
        ("descricao_curta", desc), ("efeitos", efeitos)])
    d.update(extra)
    CARACS.append(d)
    return d


def sub(cid, nome, nivel, pag, desc, efeitos, subclasse, **extra):
    d = car(cid, nome, nivel, pag, desc, efeitos, **extra)
    d['subclasse'] = subclasse
    return d


# ------------------------------------------------------------ classe, nível 1
car("inspiracao_de_bardo", "Inspiração de Bardo", 1, 61,
    "Ação Bônus para dar um dado de Inspiração a uma criatura a até 18 m que veja ou ouça "
    "você. Dentro de 1 hora, depois de falhar num Teste de D20, ela soma o dado e pode "
    "virar a falha em sucesso. Usos iguais ao modificador de Carisma, recuperados no "
    "Descanso Longo.",
    [{"tipo": "recurso_com_recarga", "id": "inspiracao_de_bardo",
      "nome": "Inspiração de Bardo",
      "formula_maximo": [{"op": "max", "args": ["mod:CAR", "1"]}],
      "recarga": [{"gatilho": "descanso_longo", "quantidade": "todos"}],
      "consumo": "por_uso"},
     {"tipo": "conceder_acao", "id": "acao_conceder_inspiracao", "custo": "acao_bonus",
      "recurso_id": "inspiracao_de_bardo", "alcance_m": 18,
      "efeitos": [
          {"id": "conceder_inspiracao", "tipo": "escolha",
           "rotulo": "Como o dado de Inspiração pode ser gasto", "quantidade": 1,
           "momento": "ao_gastar_o_dado", "reescolhivel": True,
           "de": {"catalogo": "usos_da_inspiracao_de_bardo", "chaves": ["padrao"]},
           "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                         "chave": "{{escolhido}}"},
           "duracao": "1 hora",
           "limite": {"por_criatura": 1,
                      "nota": "Uma criatura só carrega um dado por vez."}}]}])

car("conjuracao_bardo", "Conjuração", 1, 61,
    "Conjura pela lista de Bardo, com Carisma. Prepara da lista inteira, sem livro, "
    "trocando uma magia por nível ganho.",
    [{"tipo": "desbloquear_magias", "modo": "disponivel_para_preparar",
      "lista_id": "bardo"},
     {"id": "bardo_truques", "tipo": "escolha", "rotulo": "Escolha os truques de Bardo",
      "quantidade": ["coluna:truques"], "reescolhivel": True,
      "reescolha_em": "subir_de_nivel", "quantidade_de_trocas": 1,
      "recomendadas": ["luzes_dancantes", "zombaria_perversa"],
      "de": {"catalogo": "magias", "filtro": {"lista": "bardo", "nivel": 0}},
      "efeito_por_item_escolhido": {"tipo": "desbloquear_magias",
                                    "magia": "{{escolhido}}", "modo": "conhecida"}},
     {"id": "bardo_preparadas", "tipo": "escolha",
      "rotulo": "Escolha as magias preparadas de Bardo",
      "quantidade": ["coluna:magias_preparadas"], "reescolhivel": True,
      "reescolha_em": "subir_de_nivel", "quantidade_de_trocas": 1,
      "de": {"catalogo": "magias",
             "filtro": {"lista": "bardo", "nivel_minimo": 1,
                        "circulo_com_espaco_disponivel": True}},
      "efeito_por_item_escolhido": {"tipo": "preparar_magias",
                                    "magia": "{{escolhido}}",
                                    "fonte_das_magias": "lista_de_classe",
                                    "lista_id": "bardo"}},
     ],
    cd_para_evitar_sua_magia=["8", "mod:CAR", "prof"],
    foco_de_conjuracao=["instrumento_musical"])

car("especialista_bardo", "Especialista", 2, 61,
    "Especialização em duas perícias em que já é proficiente, e mais duas no nível 9.",
    [{"id": "bardo_especializacao", "tipo": "escolha",
      "rotulo": "Escolha perícias para Especialização", "quantidade": 2,
      "quantidade_por_nivel": {"2": 2, "9": 4},
      "recomendadas": ["atuacao", "persuasao"],
      "de": {"catalogo": "pericias", "todo_o_catalogo": True,
             "filtro_adicional": {"ja_proficiente": True}},
      "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                    "categoria": "pericia", "chave": "{{escolhido}}",
                                    "nivel_dominio": "especializacao"}}],
    niveis=[2, 9], repetivel=True, tipo_de_repeticao="melhoria",
    nome_na_tabela="Especialização")

car("pau_pra_toda_obra", "Pau pra Toda Obra", 2, 61,
    "Soma metade do Bônus de Proficiência (arredondado para baixo) em testes de atributo "
    "com perícia em que não é proficiente e que ainda não usem o bônus.",
    [{"tipo": "modificador", "alvo": "teste_de_atributo",
      "valor": [{"op": "div_arred_baixo", "args": ["prof", "2"]}],
      "empilha": "soma",
      "condicao": {"todas": ["nao_proficiente_na_pericia",
                             {"nao": "ja_soma_bonus_de_proficiencia"}]}}])

car("subclasse_de_bardo", "Subclasse de Bardo", 3, 61,
    "Escolhe um Colégio de Bardo. Ele concede características nos níveis 3, 6 e 14, "
    "somadas às da classe nesses mesmos níveis.",
    [{"id": "bardo_subclasse", "tipo": "escolha", "rotulo": "Escolha um Colégio de Bardo",
      "quantidade": 1,
      "de": {"catalogo": "subclasses", "filtro": {"classe": "bardo"}},
      "efeito_por_item_escolhido": {"tipo": "conceder_subclasse",
                                    "chave": "{{escolhido}}"}}])

car("fonte_de_inspiracao", "Fonte de Inspiração", 5, 61,
    "A Inspiração de Bardo passa a recuperar todos os usos também no Descanso Curto.",
    [{"tipo": "melhorar_caracteristica", "alvo": "inspiracao_de_bardo",
      "efeitos": [{"tipo": "recurso_com_recarga", "id": "inspiracao_de_bardo",
                   "modo": "acrescenta_recarga",
                   "recarga": [{"gatilho": "descanso_curto", "quantidade": "todos"}]}]}])

car("contra_encantamento", "Contra-Encantamento", 7, 61,
    "Reação: quando você ou alguém a até 9 m falha numa salvaguarda contra Amedrontado "
    "ou Enfeitiçado, repete a salvaguarda com Vantagem.",
    [{"tipo": "rolar_novamente", "alvo": "salvaguarda", "custo": "reacao",
      "com_vantagem": True,
      "beneficiario": "voce_ou_criatura_a_ate_9m",
      "condicao": {"todas": ["falhou_na_salvaguarda",
                             {"alguma": ["efeito_aplica:amedrontado",
                                         "efeito_aplica:enfeiticado"]}]}}])

car("segredos_magicos", "Segredos Mágicos", 10, 62,
    "As magias preparadas de Bardo passam a poder vir também das listas de Clérigo, "
    "Druida e Mago, e contam como magias de Bardo. Vale para cada nova magia preparada e "
    "para cada troca.",
    [{"tipo": "expandir_opcoes_de_escolha", "escolha_id": "bardo_preparadas",
      "catalogo": "magias",
      "filtro": {"lista": ["bardo", "clerigo", "druida", "mago"], "nivel_minimo": 1,
                 "circulo_com_espaco_disponivel": True},
      "modo": "substitui_filtro",
      "nota": "Alarga o filtro da escolha de preparadas em vez de criar outra escolha. "
              "As magias escolhidas contam como magias de Bardo."}])

car("inspiracao_superior", "Inspiração Superior", 18, 62,
    "Ao jogar Iniciativa, recupera usos de Inspiração de Bardo até ter dois, se tiver menos.",
    [{"tipo": "restaurar_recurso", "recurso_id": "inspiracao_de_bardo",
      "gatilho": "jogar_iniciativa", "ate_o_total_de": 2,
      "condicao": {"todas": ["usos_atuais_menores_que:2"]}}])

car("palavras_de_criacao", "Palavras de Criação", 20, 62,
    "Sempre com Palavra de Poder: Matar e Palavra de Poder: Salvar preparadas, e ao "
    "conjurar qualquer uma delas pode escolher uma segunda criatura a até 3 m do "
    "primeiro alvo.",
    [{"tipo": "preparar_magias", "magias": ["palavra_de_poder_matar",
                                            "palavra_de_poder_salvar"],
      "modo": "sempre_preparada", "nao_conta_para_o_limite": True,
      "fonte_das_magias": "lista_de_classe", "lista_id": "bardo"},
     {"tipo": "alterar_alvos_da_magia",
      "magias": ["palavra_de_poder_matar", "palavra_de_poder_salvar"],
      "alvos_adicionais": 1,
      "distancia_do_primeiro_alvo_m": 3}])

# --------------------------------------------------- Colégio da Bravura (p. 64)
sub("inspiracao_em_combate", "Inspiração em Combate", 3, 64,
    "Quem tem seu dado de Inspiração pode gastá-lo de dois jeitos novos: somar à CA "
    "contra um ataque que a acertou (Reação), ou somar ao dano de um ataque que ela "
    "acertou.",
    [{"tipo": "expandir_opcoes_de_escolha", "escolha_id": "conceder_inspiracao",
      "catalogo": "usos_da_inspiracao_de_bardo",
      "chaves": ["defensivo", "ofensivo"]}],
    "colegio_da_bravura")

sub("treinamento_marcial", "Treinamento Marcial", 3, 64,
    "Proficiência com armas Marciais e armaduras Médias, treinamento com Escudos, e pode "
    "usar uma arma Simples ou Marcial como Foco de Conjuração para magias de Bardo.",
    [{"tipo": "conceder_proficiencia", "categoria": "arma",
      "de": {"catalogo": "itens", "filtro": {"categoria": "arma", "grupo": "marcial"}},
      "nivel_dominio": "proficiente"},
     {"tipo": "conceder_proficiencia", "categoria": "armadura", "chave": "media",
      "nivel_dominio": "treinado"},
     {"tipo": "conceder_proficiencia", "categoria": "armadura", "chave": "escudo",
      "nivel_dominio": "treinado"},
     ],
    "colegio_da_bravura",
    foco_de_conjuracao=["arma_simples_ou_marcial"],
    nota_do_foco="Só para magias da lista de Bardo (p. 64).")

sub("ataque_extra_bardo", "Ataque Extra", 6, 65,
    "Dois ataques na ação Atacar, e pode trocar um deles por um truque de conjuração de "
    "uma ação.",
    [{"tipo": "conceder_ataque", "quantidade": ["1"], "modo": "ataque_extra",
      "condicao": {"todas": ["executou:atacar"]}},
     {"tipo": "substituir_ataque_por_magia", "quantidade_de_ataques": 1,
      "de": {"catalogo": "magias",
             "filtro": {"lista": "bardo", "nivel": 0,
                        "tempo_de_conjuracao": "acao"}}}],
    "colegio_da_bravura")

sub("magia_de_batalha", "Magia de Batalha", 14, 65,
    "Depois de conjurar uma magia de uma ação, pode atacar com uma arma como Ação Bônus.",
    [{"tipo": "conceder_ataque", "quantidade": ["1"], "custo": "acao_bonus",
      "condicao": {"todas": ["conjurou_magia_de_tempo:acao"]}}],
    "colegio_da_bravura")

# ------------------------------------------------------ Colégio da Dança (p. 65)
sub("ginga_fascinante", "Ginga Fascinante", 3, 65,
    "Sem armadura e sem Escudo: Vantagem em testes de Atuação que envolvam dançar; usa "
    "Destreza no ataque desarmado; e o dano desarmado pode ser o dado de Inspiração + "
    "Destreza, como dano Contundente.",
    [{"tipo": "vantagem", "alvo": "teste_de_atributo:atuacao", "modo": "vantagem",
      "condicao": {"todas": ["flag:sem_armadura", "flag:sem_escudo", "envolve_dancar"]}},
     {"tipo": "substituir_atributo", "alvo_do_calculo": ["jogada_de_ataque_desarmado"],
      "usa": "DES",
      "condicao": {"todas": ["flag:sem_armadura", "flag:sem_escudo"]}},
     {"tipo": "dado_de_dano", "modo": "substitui_dano_desarmado",
      "formula_dado": "coluna:dados_de_inspiracao", "formula_bonus": ["mod:DES"],
      "tipo_dano": "contundente",
      "condicao": {"todas": ["flag:sem_armadura", "flag:sem_escudo"]}}],
    "colegio_da_danca")

sub("gingado_coordenado", "Gingado Coordenado", 6, 66,
    "Ao jogar Iniciativa, gasta um uso de Inspiração (se não estiver Incapacitado): você "
    "e cada aliado a até 9 m que veja ou ouça você somam o dado à Iniciativa.",
    [{"tipo": "modificador", "alvo": "iniciativa",
      "valor": ["coluna:dados_de_inspiracao"], "empilha": "soma",
      "recurso_id": "inspiracao_de_bardo",
      "beneficiario": "voce_e_aliados_a_ate_9m_que_vejam_ou_ouçam",
      "condicao": {"nao": "condicao:incapacitado"}}],
    "colegio_da_danca")

sub("movimento_inspirador", "Movimento Inspirador", 6, 66,
    "Reação, quando um inimigo à vista termina o turno a 1,5 m de você: gasta um uso de "
    "Inspiração para mover metade do seu Deslocamento, e um aliado a até 9 m também move "
    "metade do dele com a Reação dele. Nenhum dos dois provoca Ataques de Oportunidade.",
    [{"tipo": "conceder_velocidade", "tipo_deslocamento": "caminhada",
      "modo": "movimento_imediato", "custo": "reacao",
      "recurso_id": "inspiracao_de_bardo",
      "formula": [{"op": "div_arred_baixo", "args": ["deslocamento", "2"]}],
      "sem_provocar_ataques_de_oportunidade": True,
      "condicao": {"todas": ["inimigo_a_vista_terminou_turno_a_ate:1.5m"]}},
     {"tipo": "conceder_velocidade", "tipo_deslocamento": "caminhada",
      "modo": "movimento_imediato", "custo": "reacao_do_aliado",
      "beneficiario": "aliado_a_escolha_a_ate_9m",
      "formula": [{"op": "div_arred_baixo", "args": ["deslocamento_do_aliado", "2"]}],
      "sem_provocar_ataques_de_oportunidade": True}],
    "colegio_da_danca")

sub("evasao_liderada", "Evasão Liderada", 14, 66,
    "Numa salvaguarda de Destreza por metade do dano, você não sofre nada se passar e "
    "metade se falhar, e pode estender isso a criaturas a até 1,5 m que também façam a "
    "salvaguarda. Não funciona se você estiver Incapacitado.",
    [{"tipo": "alterar_resultado_de_salvaguarda", "alvo": "salvaguarda:DES",
      "em_sucesso": "nenhum_dano", "em_falha": "metade_do_dano",
      "condicao": {"nao": "condicao:incapacitado"}},
     {"tipo": "alterar_resultado_de_salvaguarda", "alvo": "salvaguarda:DES",
      "beneficiario": "criaturas_a_escolha_a_ate_1_5m",
      "em_sucesso": "nenhum_dano", "em_falha": "metade_do_dano",
      "condicao": {"todas": ["criatura_tambem_faz_a_salvaguarda",
                             {"nao": "condicao:incapacitado"}]}}],
    "colegio_da_danca")

# ------------------------------------------- Colégio do Conhecimento (p. 66)
sub("palavras_de_interrupcao", "Palavras de Interrupção", 3, 66,
    "Reação, quando uma criatura à vista a até 18 m faz uma jogada de dano ou passa num "
    "teste ou ataque: gasta um uso de Inspiração e subtrai o dado do resultado dela.",
    [{"tipo": "modificador", "alvo": "teste_d20_de_criatura_a_vista",
      "valor": [{"op": "mult", "args": ["coluna:dados_de_inspiracao", "-1"]}],
      "custo": "reacao", "recurso_id": "inspiracao_de_bardo",
      "empilha": "soma", "alcance_m": 18,
      "tambem_vale_para": ["jogada_de_dano"]}],
    "colegio_do_conhecimento")

sub("proficiencias_bonus", "Proficiências Bônus", 3, 66,
    "Proficiência em três perícias à sua escolha.",
    [{"id": "bardo_pericias_bonus", "tipo": "escolha",
      "rotulo": "Escolha 3 perícias", "quantidade": 3,
      "de": {"catalogo": "pericias", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                    "categoria": "pericia", "chave": "{{escolhido}}",
                                    "nivel_dominio": "proficiente"}}],
    "colegio_do_conhecimento")

sub("descobertas_magicas", "Descobertas Mágicas", 6, 66,
    "Aprende duas magias das listas de Clérigo, Druida ou Mago — truque ou de círculo "
    "para o qual tenha espaço. Ficam sempre preparadas e podem ser trocadas a cada nível.",
    [{"id": "bardo_descobertas_magicas", "tipo": "escolha",
      "rotulo": "Escolha 2 magias de outra lista", "quantidade": 2,
      "reescolhivel": True, "reescolha_em": "subir_de_nivel",
      "quantidade_de_trocas": 1,
      "de": {"catalogo": "magias",
             "filtro": {"lista": ["clerigo", "druida", "mago"],
                        "circulo_com_espaco_disponivel": True}},
      "efeito_por_item_escolhido": {"tipo": "preparar_magias",
                                    "magia": "{{escolhido}}",
                                    "modo": "sempre_preparada",
                                    "nao_conta_para_o_limite": True,
                                    "fonte_das_magias": "conhecidas"}}],
    "colegio_do_conhecimento")

sub("pericia_inigualavel", "Perícia Inigualável", 14, 67,
    "Falhando num teste de atributo ou jogada de ataque, gasta um uso de Inspiração e "
    "soma o dado ao d20. Se ainda assim falhar, o uso não é gasto.",
    [{"tipo": "modificador", "alvo": "teste_d20",
      "valor": ["coluna:dados_de_inspiracao"], "empilha": "soma",
      "momento": "apos_falhar", "recurso_id": "inspiracao_de_bardo",
      "consumo_condicional": "so_gasta_se_virar_sucesso"}],
    "colegio_do_conhecimento")

# ----------------------------------------------------- Colégio do Glamour (p. 67)
sub("magia_fascinante", "Magia Fascinante", 3, 67,
    "Enfeitiçar Pessoa e Reflexos sempre preparadas. Depois de conjurar uma magia de "
    "Encantamento ou Ilusão com espaço, uma criatura à vista a 18 m faz salvaguarda de "
    "Sabedoria ou fica Amedrontada ou Enfeitiçada por 1 minuto. Uma vez por Descanso.",
    [{"tipo": "preparar_magias", "magias": ["enfeiticar_pessoa", "reflexos"],
      "modo": "sempre_preparada", "nao_conta_para_o_limite": True,
      "fonte_das_magias": "lista_de_classe", "lista_id": "bardo"},
     {"id": "glamour_condicao", "tipo": "escolha",
      "rotulo": "Amedrontado ou Enfeitiçado", "quantidade": 1,
      "momento": "ao_usar",
      "de": {"catalogo": "condicoes", "chaves": ["amedrontado", "enfeiticado"]},
      "efeito_por_item_escolhido": {"tipo": "conceder_condicao",
                                    "condicao_id": "{{escolhido}}",
                                    "beneficiario": "alvo"}},
     {"tipo": "conceder_condicao", "condicao_id": "amedrontado",
      "beneficiario": "alvo",
      "resolve_por": "glamour_condicao",
      "alvo": "criatura_a_vista_a_ate_18m",
      "salvaguarda": {"atributo": "SAB", "cd": ["cd_para_evitar_sua_magia"]},
      "duracao": "1 minuto",
      "repete_salvaguarda": {"quando": "fim_do_turno_do_alvo",
                             "encerra_em_sucesso": True},
      "condicao": {"todas": ["conjurou_magia_de_escola:encantamento_ou_ilusao",
                             "gastou_espaco_de_magia"]},
      "recarga": ["descanso_curto", "descanso_longo"]}],
    "colegio_do_glamour")

sub("manto_de_inspiracao", "Manto de Inspiração", 3, 67,
    "Ação Bônus, gastando uma Inspiração: criaturas a até 18 m em número igual ao seu "
    "modificador de Carisma ganham o dobro do dado em Pontos de Vida Temporários e podem "
    "usar a Reação para mover todo o Deslocamento sem provocar Ataques de Oportunidade.",
    [{"tipo": "pontos_de_vida_temporarios",
      "formula": [{"op": "mult", "args": ["coluna:dados_de_inspiracao", "2"]}],
      "custo": "acao_bonus", "recurso_id": "inspiracao_de_bardo",
      "beneficiario": "criaturas_a_escolha_a_ate_18m",
      "quantidade_de_alvos": [{"op": "max", "args": ["mod:CAR", "1"]}]},
     {"tipo": "conceder_velocidade", "tipo_deslocamento": "caminhada",
      "modo": "movimento_imediato", "custo": "reacao_do_aliado",
      "formula": ["deslocamento_do_aliado"],
      "sem_provocar_ataques_de_oportunidade": True,
      "beneficiario": "criaturas_afetadas"}],
    "colegio_do_glamour")

sub("manto_de_majestade", "Manto de Majestade", 6, 67,
    "Comando sempre preparada. Ação Bônus para conjurá-la sem espaço e assumir aparência "
    "sobrenatural por 1 minuto, durante a qual repete Comando como Ação Bônus sem gastar "
    "espaço. Quem está Enfeitiçado por você falha automaticamente. Uma vez por Descanso "
    "Longo, ou gastando um espaço de 3º círculo ou superior.",
    [{"tipo": "preparar_magias", "magias": ["comando"], "modo": "sempre_preparada",
      "nao_conta_para_o_limite": True,
      "fonte_das_magias": "lista_de_classe", "lista_id": "bardo"},
     {"tipo": "conjurar_sem_espaco", "magia": "comando", "custo": "acao_bonus",
      "duracao": "1 minuto",
      "encerra_se": [{"gatilho": "concentracao_quebrada"}],
      "repetivel_durante": {"custo": "acao_bonus", "sem_espaco": True},
      "falha_automatica_de": "criatura_enfeiticada_por_voce",
      "recarga": ["descanso_longo"],
      "recarga_alternativa": {"gastar_espaco_de_magia": {"circulo_minimo": 3}}}],
    "colegio_do_glamour")

sub("majestade_inquebravel", "Majestade Inquebrável", 14, 67,
    "Ação Bônus para uma presença majestosa por 1 minuto ou até ficar Incapacitado: quem "
    "acertar você pela primeira vez num turno faz salvaguarda de Carisma ou o ataque "
    "falha. Uma vez por Descanso.",
    [{"tipo": "impedir", "alvo": "atacar_ou_alvejar", "custo": "acao_bonus",
      "beneficiario": "atacante",
      "salvaguarda": {"atributo": "CAR", "cd": ["cd_para_evitar_sua_magia"]},
      "frequencia": "primeira_vez_por_turno_por_atacante",
      "duracao": "1 minuto",
      "encerra_se": [{"condicao_id": "incapacitado"}],
      "recarga": ["descanso_curto", "descanso_longo"]}],
    "colegio_do_glamour")

# ------------------------------------------------------------------ progressão
DADOS_INSP = {1: "1d6", 5: "1d8", 10: "1d10", 15: "1d12"}
TRUQUES = {1: 2, 4: 3, 10: 4}
PREPARADAS = [4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16, 17, 17, 18, 18, 19, 20, 21, 22]
ESPACOS = [
    [2], [3], [4, 2], [4, 3], [4, 3, 2], [4, 3, 3], [4, 3, 3, 1], [4, 3, 3, 2],
    [4, 3, 3, 3, 1], [4, 3, 3, 3, 2], [4, 3, 3, 3, 2, 1], [4, 3, 3, 3, 2, 1],
    [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 2, 1, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1, 1],
    [4, 3, 3, 3, 3, 1, 1, 1, 1], [4, 3, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 3, 2, 2, 1, 1]]
PROF = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6]
POR_NIVEL = {
    1: ["inspiracao_de_bardo", "conjuracao_bardo"],
    2: ["especialista_bardo", "pau_pra_toda_obra"],
    3: ["subclasse_de_bardo"],
    4: ["aumento_no_valor_de_atributo"],
    5: ["fonte_de_inspiracao"],
    6: ["caracteristica_de_subclasse"],
    7: ["contra_encantamento"],
    8: ["aumento_no_valor_de_atributo"],
    9: ["especialista_bardo"],
    10: ["segredos_magicos"],
    12: ["aumento_no_valor_de_atributo"],
    14: ["caracteristica_de_subclasse"],
    16: ["aumento_no_valor_de_atributo"],
    18: ["inspiracao_superior"],
    19: ["dadiva_epica"],
    20: ["palavras_de_criacao"],
}


def dado_de_inspiracao(n):
    v = "1d6"
    for lim, d in sorted(DADOS_INSP.items()):
        if n >= lim:
            v = d
    return v


def truques(n):
    v = 2
    for lim, q in sorted(TRUQUES.items()):
        if n >= lim:
            v = q
    return v


def progressao():
    saida = []
    for n in range(1, 21):
        esp = ESPACOS[n - 1]
        saida.append(collections.OrderedDict([
            ("nivel", n), ("bonus_de_proficiencia", PROF[n - 1]),
            ("caracteristicas", POR_NIVEL.get(n, [])),
            ("colunas", collections.OrderedDict([
                ("dados_de_inspiracao", dado_de_inspiracao(n)),
                ("truques", truques(n)),
                ("magias_preparadas", PREPARADAS[n - 1]),
                ("espacos_de_magia", esp)]))]))
    return saida


CLASSE = collections.OrderedDict([
    ("id", "bardo"), ("nome", "Bardo"), ("fonte", fonte(59)), ("revisao", rev()),
    ("descricao_curta", "Conjura por música, dança e verso; inspira aliados com um dado "
                        "que vira falha em sucesso, e no nível 10 rouba magias das listas "
                        "de Clérigo, Druida e Mago."),
    ("dado_de_vida", 8), ("atributo_primario", ["CAR"]),
    ("salvaguardas_primarias", ["DES", "CAR"]),
    ("nivel_subclasse", 3),
    ("conjuracao", {"atributo": "CAR", "modo": "lista_de_classe",
                    "lista_id": "bardo", "preparadas_por_nivel": True}),
    ("subclasses", ["colegio_da_bravura", "colegio_da_danca",
                    "colegio_do_conhecimento", "colegio_do_glamour"]),
    ("proficiencias_iniciais", [
        {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "DES",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "CAR",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "arma",
         "de": {"catalogo": "itens",
                "filtro": {"categoria": "arma", "grupo": "simples"}},
         "nivel_dominio": "proficiente"},
        {"id": "bardo_pericias_iniciais", "tipo": "escolha",
         "rotulo": "Escolha 3 perícias quaisquer", "quantidade": 3,
         "de": {"catalogo": "pericias", "todo_o_catalogo": True},
         "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                       "categoria": "pericia",
                                       "chave": "{{escolhido}}",
                                       "nivel_dominio": "proficiente"}},
        {"id": "bardo_instrumentos", "tipo": "escolha",
         "rotulo": "Escolha 3 instrumentos musicais", "quantidade": 1,
         "quantidade_de_instrumentos": 3,
         "de": {"catalogo": "ferramentas", "chaves": ["instrumento_musical"],
                "nota": "O livro pede TRÊS instrumentos (p. 60); o capítulo 6 traz "
                        "'Instrumento Musical' como uma entrada genérica (p. 222), sem "
                        "listar os instrumentos um a um. A quantidade real está em "
                        "quantidade_de_instrumentos."},
         "revisao": {"status": "duvida",
                     "notas": "O livro não enumera os instrumentos; se você quiser a "
                              "lista (alaúde, tambor, flauta…), ela teria de vir de "
                              "outra fonte."},
         "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                       "categoria": "ferramenta",
                                       "chave": "{{escolhido}}",
                                       "nivel_dominio": "proficiente"}},
    ]),
    ("treinamento_com_armadura", ["leve"]),
    ("equipamento_inicial", {
        "opcoes": [
            {"id": "A", "itens": [
                {"item": "couro"}, {"item": "adaga", "quantidade": 2},
                {"item": "instrumento_musical"}, {"item": "kit_de_artista"}],
             "moedas": {"po": 19}},
            {"id": "B", "moedas": {"po": 90}}],
        "revisao": rev()}),
    ("progressao", progressao()),
    ("colunas_da_tabela", collections.OrderedDict([
        ("dados_de_inspiracao", {"nome": "Dados de Inspiração", "tipo": "dado"}),
        ("truques", {"nome": "Truques", "tipo": "inteiro"}),
        ("magias_preparadas", {"nome": "Magias Preparadas", "tipo": "inteiro"}),
        ("espacos_de_magia", {"nome": "Espaços de Magia por Círculo", "tipo": "lista"})])),
    ("multiclasse", {"proficiencias": ["armadura_leve", "uma_pericia", "um_instrumento"],
                     "fonte": fonte(59)}),
])

SUBCLASSES = [
    ("colegio_da_bravura", "Colégio da Bravura", 64,
     "Bardos guerreiros: treinamento marcial, ataque extra e uma Inspiração que serve "
     "para defender ou para ferir."),
    ("colegio_da_danca", "Colégio da Dança", 65,
     "Harmonia com o cosmos: luta desarmado com Destreza e o dado de Inspiração, e move "
     "a si e aos aliados fora do turno."),
    ("colegio_do_conhecimento", "Colégio do Conhecimento", 66,
     "Sagacidade e erudição: subtrai o dado de Inspiração dos outros, ganha perícias e "
     "magias de outras listas antes da hora."),
    ("colegio_do_glamour", "Colégio do Glamour", 67,
     "Magia feérica de encanto: amedronta ou enfeitiça com as próprias magias, dá vida "
     "temporária e movimento, e comanda com majestade."),
]

USOS_DA_INSPIRACAO = collections.OrderedDict([
    ("catalogo", "usos_da_inspiracao_de_bardo"),
    ("nome", "Usos da Inspiração de Bardo"),
    ("fonte", fonte(64)),
    ("nota", "A classe entra com o uso padrão; o Colégio da Bravura acrescenta os dois "
             "de combate. Catálogo expansível por subclasse."),
    ("expansivel_por_subclasse", True),
    ("total", 3),
    ("itens", [
        collections.OrderedDict([
            ("id", "padrao"), ("nome", "Virar uma falha em sucesso"),
            ("descricao_curta", "Depois de falhar num Teste de D20, soma o dado e pode "
                                "transformar a falha em sucesso."),
            ("efeitos", [{"tipo": "modificador", "alvo": "teste_d20",
                          "valor": ["coluna:dados_de_inspiracao"], "empilha": "soma",
                          "momento": "apos_falhar"}])]),
        collections.OrderedDict([
            ("id", "defensivo"), ("nome", "Defensivo"),
            ("descricao_curta", "Reação, ao ser atingida: soma o dado à própria CA contra "
                                "aquele ataque, podendo fazer errar."),
            ("efeitos", [{"tipo": "modificador", "alvo": "ca_total",
                          "valor": ["coluna:dados_de_inspiracao"], "empilha": "soma",
                          "custo": "reacao", "duracao": "contra_o_ataque_que_disparou"}])]),
        collections.OrderedDict([
            ("id", "ofensivo"), ("nome", "Ofensivo"),
            ("descricao_curta", "Depois de acertar um ataque: soma o dado ao dano."),
            ("efeitos", [{"tipo": "modificador", "alvo": "jogada_de_dano",
                          "valor": ["coluna:dados_de_inspiracao"], "empilha": "soma",
                          "momento": "apos_acertar"}])]),
    ]),
])


def main():
    # catálogo novo
    with open('dados/catalogos/usos_da_inspiracao_de_bardo.json', 'w',
              encoding='utf-8') as f:
        json.dump(USOS_DA_INSPIRACAO, f, ensure_ascii=False, indent=2)

    cl = json.load(open('dados/classes.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    cl['itens'] = [c for c in cl['itens'] if c['id'] != 'bardo'] + [CLASSE]
    cl['total'] = len(cl['itens'])
    json.dump(cl, open('dados/classes.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    sc = json.load(open('dados/subclasses.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    sc['itens'] = [s for s in sc['itens'] if s.get('classe') != 'bardo']
    for sid, nome, pag, desc in SUBCLASSES:
        sc['itens'].append(collections.OrderedDict([
            ("id", sid), ("nome", nome), ("classe", "bardo"),
            ("fonte", fonte(pag)), ("revisao", rev()),
            ("descricao_curta", desc),
            ("niveis_de_caracteristica", [3, 6, 14]),
            ("caracteristicas", [c['id'] for c in CARACS
                                 if c.get('subclasse') == sid])]))
    sc['total'] = len(sc['itens'])
    json.dump(sc, open('dados/subclasses.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    ca = json.load(open('dados/caracteristicas.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    ca['itens'] = [c for c in ca['itens'] if c.get('classe') != 'bardo'] + CARACS
    ca['total'] = len(ca['itens'])
    json.dump(ca, open('dados/caracteristicas.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    print(f"bardo: {len(CARACS)} características | {len(SUBCLASSES)} subclasses | "
          f"classes: {cl['total']} | subclasses: {sc['total']} | "
          f"características: {ca['total']}")


if __name__ == '__main__':
    main()
