# -*- coding: utf-8 -*-
"""Guardião (cap. 3, p. 117-125).

Duas coisas novas aqui.

A primeira é o Companheiro Primal do Senhor das Feras. Ele traz TRÊS BLOCOS DE
ESTATÍSTICAS impressos no próprio capítulo 3 — Fera da Terra, do Céu e do Mar —
com PV, CA e Golpe da Fera escritos em função do NÍVEL e do MODIFICADOR do
Guardião. Isso não é o Apêndice B: a decisão de adiar criaturas continua de pé, e
`criaturas.json` continua vazio. Estes três moram em catálogo próprio,
`feras_companheiras`, porque são parte da subclasse, não bestiário.

A segunda é o Combatente Druídico: uma opção que substitui o talento de Estilo de
Luta. O Paladino tem a irmã dela (Combatente Abençoado), então o catálogo
`opcoes_de_estilo_de_luta_de_classe` nasce compartilhado, e a característica de
cada classe libera a sua chave com `expandir_opcoes_de_escolha` — o mesmo
mecanismo do Golpe Brutal Fortalecido.
"""
import json, collections

CAT = 'dados/catalogos'


def fonte(p):
    return {"capitulo": 3, "pagina_livro": p, "pagina_pdf": p + 4}


def rev(status="ok", notas=""):
    return {"status": status, "notas": notas}


CARACS = []


def car(cid, nome, nivel, pag, desc, efeitos, **extra):
    d = collections.OrderedDict([
        ("id", cid), ("nome", nome), ("classe", "guardiao"), ("nivel", nivel),
        ("fonte", fonte(pag)), ("revisao", rev()),
        ("descricao_curta", desc), ("efeitos", efeitos)])
    d.update(extra)
    CARACS.append(d)
    return d


def sub(cid, nome, nivel, pag, desc, efeitos, subclasse, **extra):
    d = car(cid, nome, nivel, pag, desc, efeitos, **extra)
    d['subclasse'] = subclasse
    return d


CD = ["8", "mod:SAB", "prof"]

# ============================================================ classe, nível 1

car("conjuracao_guardiao", "Conjuração", 1, 117,
    "Conjura pela lista de Guardião, com Sabedoria. Prepara da lista inteira conforme a coluna "
    "Magias Preparadas, trocando uma a cada Descanso Longo. Usa Foco Druídico.",
    [{"tipo": "conceder_slot", "tabela_progressao_id": "guardiao",
      "colunas": ["espacos_1", "espacos_2", "espacos_3", "espacos_4", "espacos_5"],
      "recarga": "descanso_longo"},
     {"tipo": "preparar_magias", "formula_quantidade": ["coluna:magias_preparadas"],
      "atributo_conjuracao": "SAB", "fonte_das_magias": "lista_de_classe",
      "lista_id": "guardiao",
      "restricao": "de um círculo para o qual você possui espaços de magia",
      "magias_sempre_preparadas_nao_contam": True},
     {"tipo": "desbloquear_magias", "lista_id": "guardiao",
      "modo": "disponivel_para_preparar", "atributo_conjuracao": "SAB"},
     {"id": "guardiao_preparadas", "tipo": "escolha",
      "rotulo": "Prepare magias de Guardião", "quantidade": "coluna:magias_preparadas",
      "momento": "nivel_1", "reescolhivel": True, "reescolha_em": "descanso_longo",
      "reescolha_quantidade": 1,
      "de": {"catalogo": "magias",
             "filtro": {"nivel_minimo": 1, "lista": "guardiao",
                        "circulo_com_espaco_disponivel": True}},
      "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "lista_id": "guardiao",
                                    "modo": "preparada", "magia": "{{escolhido}}"}}],
    foco_de_conjuracao=["ramo_de_visco"],
    cd_para_evitar_sua_magia=CD,
    nota_do_livro="Sem truques: o Guardião não tem coluna de truques. Os dois truques de "
                  "Druida do Combatente Druídico são a única porta para truques na classe.")

car("inimigo_favorito", "Inimigo Favorito", 1, 117,
    "Marca do Predador sempre preparada, e conjurável sem gastar espaço um número de vezes igual "
    "à coluna Inimigo Favorito. Todos os usos voltam no Descanso Longo.",
    [{"tipo": "desbloquear_magias", "lista_id": "guardiao", "modo": "sempre_preparada",
      "magias": ["marca_do_predador"]},
     {"tipo": "recurso_com_recarga", "id": "inimigo_favorito",
      "nome": "Inimigo Favorito", "formula_maximo": ["coluna:inimigo_favorito"],
      "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "conjurar_sem_espaco", "magia": "marca_do_predador",
      "consome_recurso": "inimigo_favorito"}])

car("maestria_em_arma_guardiao", "Maestria em Arma", 1, 118,
    "Usa as propriedades de maestria de dois tipos de arma à escolha entre aquelas com que tem "
    "proficiência. Troca as escolhas a cada Descanso Longo.",
    [{"id": "guardiao_maestrias", "tipo": "escolha",
      "rotulo": "Escolha os tipos de arma com maestria", "quantidade": 2,
      "momento": "nivel_1", "reescolhivel": True, "reescolha_em": "descanso_longo",
      "de": {"catalogo": "itens",
             "filtro": {"categoria": "arma", "grupo": ["simples", "marcial"]}},
      "efeito_por_item_escolhido": {"tipo": "conceder_maestria_de_arma",
                                    "arma": "{{escolhido}}"}}],
    nota_do_livro="O livro não dá coluna de progressão aqui: são dois tipos de arma, fixos, "
                  "do nível 1 ao 20. Diferente do Guerreiro, que sobe pela coluna.")

# ============================================================ classe, nível 2

car("estilo_de_luta_guardiao", "Estilo de Luta", 2, 118,
    "Adquire um talento de Estilo de Luta à escolha; em vez dele, pode pegar Combatente Druídico, "
    "que dá dois truques de Druida conjurados com Sabedoria.",
    [{"id": "guardiao_estilo_de_luta", "tipo": "escolha",
      "rotulo": "Escolha um talento de Estilo de Luta", "quantidade": 1,
      "momento": "nivel_2",
      "de": {"catalogo": "talentos", "filtro": {"categoria": "estilo_de_luta"}},
      "efeito_por_item_escolhido": {"tipo": "conceder_talento",
                                    "talento_id": "{{escolhido}}"}},
     {"tipo": "expandir_opcoes_de_escolha", "escolha_id": "guardiao_estilo_de_luta",
      "catalogo": "opcoes_de_estilo_de_luta_de_classe", "chaves": ["combatente_druidico"],
      "nota": "A opção da classe entra na mesma escolha do talento, não numa escolha à parte: "
              "o livro diz 'em vez de escolher um desses talentos'."}])

car("explorador_habil", "Explorador Hábil", 2, 118,
    "Especialização em uma perícia em que já é proficiente, e dois idiomas à escolha.",
    [{"id": "guardiao_especialista_nivel_2", "tipo": "escolha",
      "rotulo": "Escolha uma perícia para ganhar Especialização", "quantidade": 1,
      "momento": "nivel_2",
      "de": {"catalogo": "pericias",
             "filtro": {"proficiente": True, "ainda_nao_especialista": True}},
      "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                    "chave": "{{escolhido}}", "nivel_dominio": "especialista"}},
     {"id": "guardiao_idiomas", "tipo": "escolha", "rotulo": "Escolha 2 idiomas",
      "quantidade": 2, "momento": "nivel_2",
      "de": {"catalogo": "idiomas", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "idioma",
                                    "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}}])

# ============================================================ classe, níveis 6+

car("errante", "Errante", 6, 118,
    "Deslocamento +3 m sem Armadura Pesada, e Deslocamentos de Escalada e de Natação iguais ao "
    "seu Deslocamento.",
    [{"tipo": "modificador", "alvo": "deslocamento", "valor": ["3"], "unidade": "metros",
      "empilha": "soma", "condicao": {"nao": "usando:armadura_pesada"}},
     {"tipo": "conceder_velocidade", "tipo_deslocamento": "escalada",
      "formula": ["deslocamento"], "condicao": {"nao": "usando:armadura_pesada"}},
     {"tipo": "conceder_velocidade", "tipo_deslocamento": "natacao",
      "formula": ["deslocamento"], "condicao": {"nao": "usando:armadura_pesada"}}])

car("especialista_guardiao", "Especialista", 9, 119,
    "Especialização em duas perícias em que já é proficiente.",
    [{"id": "guardiao_especialista_nivel_9", "tipo": "escolha",
      "rotulo": "Escolha 2 perícias para ganhar Especialização", "quantidade": 2,
      "momento": "nivel_9",
      "de": {"catalogo": "pericias",
             "filtro": {"proficiente": True, "ainda_nao_especialista": True}},
      "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                    "chave": "{{escolhido}}", "nivel_dominio": "especialista"}}])

car("incansavel", "Incansável", 10, 119,
    "Ação Usar Magia para ganhar 1d8 + modificador de Sabedoria de Pontos de Vida Temporários, "
    "com usos iguais ao modificador de Sabedoria. E cada Descanso Curto reduz a Exaustão em 1.",
    [{"tipo": "recurso_com_recarga", "id": "incansavel", "nome": "Incansável",
      "formula_maximo": {"op": "max", "args": ["1", "mod:SAB"]},
      "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "pontos_de_vida_temporarios",
      "formula": {"op": "max", "args": ["1", {"op": "soma", "args": ["1d8", "mod:SAB"]}]},
      "custo": "acao", "acao_id": "usar_magia", "beneficiario": "voce",
      "consome_recurso": "incansavel"},
     {"tipo": "alterar_condicao", "condicao_id": "exaustao", "operacao": "reduzir_nivel",
      "quantidade": 1, "gatilho": "descanso_curto"}])

car("predador_implacavel", "Predador Implacável", 13, 119,
    "Sofrer dano não quebra sua Concentração na Marca do Predador.",
    [{"tipo": "imunidade_a_quebra_de_concentracao", "causa": "dano",
      "escopo": {"magia": "marca_do_predador"}}],
    revisao=rev("ok", "Era substituir_regra (remendo, e por isso dúvida) até 2026-09-01. Virou "
                      "primitivo próprio: o motor agora sabe dizer que uma fonte de quebra de "
                      "Concentração não se aplica, em vez de receber um remendo da regra do cap. 7."))

car("veu_da_natureza", "Véu da Natureza", 14, 119,
    "Ação Bônus para ficar Invisível até o fim do seu próximo turno, com usos iguais ao "
    "modificador de Sabedoria.",
    [{"tipo": "recurso_com_recarga", "id": "veu_da_natureza", "nome": "Véu da Natureza",
      "formula_maximo": {"op": "max", "args": ["1", "mod:SAB"]},
      "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "conceder_condicao", "condicao_id": "invisivel", "beneficiario": "voce",
      "custo": "acao_bonus", "duracao": "ate_o_fim_do_seu_proximo_turno",
      "consome_recurso": "veu_da_natureza"}])

car("cacador_preciso", "Caçador Preciso", 17, 119,
    "Vantagem em jogadas de ataque contra a criatura marcada pela sua Marca do Predador.",
    [{"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "vantagem",
      "condicao": {"todas": ["alvo_marcado_por:marca_do_predador"]}}])

car("sentidos_selvagens", "Sentidos Selvagens", 18, 119,
    "Visão às Cegas com alcance de 9 metros.",
    [{"tipo": "conceder_sentido", "sentido": "visao_as_cegas", "alcance_m": 9}])

car("matador_de_inimigos_favoritos", "Matador de Inimigos Favoritos", 20, 120,
    "O dado de dano da sua Marca do Predador passa a ser d10 em vez de d6.",
    [{"tipo": "modificador", "alvo": "dado_de_dano_da_magia", "modo": "substitui",
      "valor": ["d10"], "escopo": {"magia": "marca_do_predador"}, "empilha": "substitui"}])


def tabela_magias(nome, pag, linhas):
    return {"nome": nome, "fonte": fonte(pag),
            "linhas": [{"nivel": n, "magias": m} for n, m in linhas]}


# ==================================================== subclasse: Andarilho Feérico

sub("glamour_transcendental", "Glamour Transcendental", 3, 120,
    "Bônus igual ao modificador de Sabedoria (mínimo +1) em testes de Carisma, e proficiência em "
    "Atuação, Enganação ou Persuasão.",
    [{"tipo": "modificador", "alvo": "teste_de_atributo", "atributo": "CAR",
      "valor": {"op": "max", "args": ["1", "mod:SAB"]}, "empilha": "soma"},
     {"id": "andarilho_feerico_pericia", "tipo": "escolha",
      "rotulo": "Escolha uma perícia", "quantidade": 1, "momento": "nivel_3",
      "de": {"catalogo": "pericias", "chaves": ["atuacao", "enganacao", "persuasao"]},
      "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                    "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}}],
    "andarilho_feerico")

sub("golpes_terriveis", "Golpes Terríveis", 3, 120,
    "Uma vez por turno, ao atingir com uma arma, causa 1d4 de dano Psíquico adicional — 1d6 a "
    "partir do nível 11 de Guardião.",
    [{"tipo": "dado_de_impacto", "formula_dado": "1d4", "tipo_dano": "psiquico",
      "frequencia": "uma_vez_por_turno",
      "escalonamento_por_nivel": {"11": "1d6"},
      "condicao": {"todas": ["acerto_com_arma"]}}],
    "andarilho_feerico")

sub("magias_do_andarilho_feerico", "Magias do Andarilho Feérico", 3, 120,
    "Magias sempre preparadas pela tabela Magias do Andarilho Feérico, sem contar para o limite. "
    "Também recebe uma Dádiva de Faéria, escolhida ou sorteada em 1d6.",
    [{"tipo": "magias_de_patrono",
      "tabela": tabela_magias("Magias do Andarilho Feérico", 120, [
          (3, ["enfeiticar_pessoa"]), (5, ["passo_nebuloso"]), (9, ["convocar_feerico"]),
          (13, ["porta_dimensional"]), (17, ["despistar"])]),
      "modo": "sempre_preparada", "lista_id": "guardiao",
      "acesso_concedido_pela_subclasse": True,
      "nao_conta_para_o_limite": True},
     {"id": "dadiva_de_faeria", "tipo": "escolha", "rotulo": "Escolha ou sorteie sua Dádiva de Faéria",
      "quantidade": 1, "momento": "nivel_3", "aleatoria_permitida": True, "dado": "1d6",
      "de": {"catalogo": "dadivas_de_faeria", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "efeito_narrativo", "chave": "dadiva_de_faeria",
                                    "dadiva": "{{escolhido}}"}}],
    "andarilho_feerico")

sub("detalhe_sedutor", "Detalhe Sedutor", 7, 121,
    "Vantagem em salvaguardas contra Amedrontado e Enfeitiçado. Além disso, quando você ou uma "
    "criatura à vista a até 36 m passa numa dessas salvaguardas, Reação para forçar outra "
    "criatura a uma salvaguarda de Sabedoria ou ficar Amedrontada ou Enfeitiçada por 1 minuto.",
    [{"tipo": "vantagem", "alvo": "salvaguarda", "modo": "vantagem",
      "condicao": {"alguma": ["contra_condicao:amedrontado", "contra_condicao:enfeiticado"]}},
     {"tipo": "conceder_condicao", "escolher_condicao": ["amedrontado", "enfeiticado"],
      "condicao_id": "amedrontado",
      "custo": "reacao", "alcance_m": 36, "alvo": "criatura_a_vista_diferente",
      "gatilho": "voce_ou_criatura_a_vista_a_ate_36m_passa_em_salvaguarda_contra_amedrontado_ou_enfeiticado",
      "salvaguarda": {"atributo": "SAB", "cd": CD,
                      "repete": "fim_de_cada_turno_do_alvo", "em_sucesso": "encerra"},
      "duracao": "1 minuto"}],
    "andarilho_feerico")

sub("reforcos_feericos", "Reforços Feéricos", 11, 121,
    "Conjura Convocar Feérico sem componente Material; uma vez por Descanso Longo sem gastar "
    "espaço; e pode conjurá-la sem Concentração, com duração de 1 minuto.",
    [{"tipo": "dispensar_componentes", "componentes": ["material"],
      "escopo": {"magia": "convocar_feerico"}},
     {"tipo": "recurso_com_recarga", "id": "reforcos_feericos", "nome": "Reforços Feéricos",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "conjurar_sem_espaco", "magia": "convocar_feerico",
      "consome_recurso": "reforcos_feericos"},
     {"tipo": "dispensar_concentracao", "escopo": {"magia": "convocar_feerico"},
      "opcional": True, "momento": "ao_comecar_a_conjurar"},
     {"tipo": "alterar_duracao_da_magia", "escopo": {"magia": "convocar_feerico"},
      "nova_duracao": "1 minuto", "junto_com": "dispensar_concentracao"}],
    "andarilho_feerico")

sub("andarilho_nebuloso", "Andarilho Nebuloso", 15, 121,
    "Conjura Passo Nebuloso sem gastar espaço, com usos iguais ao modificador de Sabedoria. E "
    "cada conjuração pode levar junto uma criatura voluntária a até 1,5 m.",
    [{"tipo": "recurso_com_recarga", "id": "andarilho_nebuloso", "nome": "Andarilho Nebuloso",
      "formula_maximo": {"op": "max", "args": ["1", "mod:SAB"]},
      "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "conjurar_sem_espaco", "magia": "passo_nebuloso",
      "consome_recurso": "andarilho_nebuloso"},
     {"tipo": "alterar_alvos_da_magia", "escopo": {"magia": "passo_nebuloso"},
      "alvos_adicionais": 1, "restricao": "criatura voluntária a até 1,5 m de você",
      "destino": "espaço desocupado a até 1,5 m do seu destino"}],
    "andarilho_feerico")

# ============================================================= subclasse: Caçador

sub("conhecimento_do_cacador", "Conhecimento do Caçador", 3, 122,
    "Enquanto uma criatura está marcada pela sua Marca do Predador, você sabe se ela tem "
    "Imunidades, Resistências ou Vulnerabilidades — e quais são.",
    [{"tipo": "efeito_narrativo", "chave": "revelar_imunidades_resistencias_vulnerabilidades",
      "texto": "Revela Imunidades, Resistências e Vulnerabilidades do alvo marcado.",
      "condicao": {"todas": ["alvo_marcado_por:marca_do_predador"]}}],
    "cacador")

sub("presa_do_cacador", "Presa do Caçador", 3, 122,
    "Escolhe Assassino de Colossos ou Destruidor de Hordas, trocando a opção a cada Descanso "
    "Curto ou Longo.",
    [{"id": "cacador_presa", "tipo": "escolha",
      "rotulo": "Escolha uma opção de Presa do Caçador", "quantidade": 1, "momento": "nivel_3",
      "reescolhivel": True, "reescolha_em": ["descanso_curto", "descanso_longo"],
      "de": {"catalogo": "opcoes_de_presa_do_cacador", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                    "catalogo": "opcoes_de_presa_do_cacador",
                                    "chave": "{{escolhido}}"}}],
    "cacador")

sub("taticas_defensivas", "Táticas Defensivas", 7, 122,
    "Escolhe Defesa Contra Ataques Múltiplos ou Escapar de Hordas, trocando a opção a cada "
    "Descanso Curto ou Longo.",
    [{"id": "cacador_taticas", "tipo": "escolha",
      "rotulo": "Escolha uma opção de Táticas Defensivas", "quantidade": 1, "momento": "nivel_7",
      "reescolhivel": True, "reescolha_em": ["descanso_curto", "descanso_longo"],
      "de": {"catalogo": "opcoes_de_taticas_defensivas", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                    "catalogo": "opcoes_de_taticas_defensivas",
                                    "chave": "{{escolhido}}"}}],
    "cacador")

sub("presa_do_cacador_superior", "Presa do Caçador Superior", 11, 122,
    "Uma vez por turno, ao causar dano a uma criatura marcada pela Marca do Predador, repete o "
    "dano adicional dessa magia numa segunda criatura à vista a até 9 m da primeira.",
    [{"tipo": "dano", "formula_dado": "dado_de_dano_da_magia:marca_do_predador",
      "tipo_dano": "energetico", "frequencia": "uma_vez_por_turno",
      "alvo": "criatura_a_vista_a_ate_9m_da_primeira",
      "gatilho": "causar_dano_a_criatura_marcada_por:marca_do_predador"}],
    "cacador")

sub("defesa_do_cacador_superior", "Defesa do Caçador Superior", 15, 122,
    "Ao sofrer dano, Reação para ganhar Resistência a esse dano e a todo dano do mesmo tipo até "
    "o fim do turno atual.",
    [{"tipo": "alterar_dano", "tipo_dano": "mesmo_do_ataque", "operacao": "resistencia",
      "custo": "reacao", "gatilho": "sofrer_dano", "duracao": "ate_o_fim_do_turno_atual"}],
    "cacador")


# ==================================================== subclasse: Senhor das Feras

sub("companheiro_primal", "Companheiro Primal", 3, 122,
    "Invoca uma fera primal — Fera da Terra, do Céu ou do Mar — Amigável e obediente. Em combate "
    "ela só executa Esquivar, a menos que você gaste uma Ação Bônus para comandá-la ou sacrifique "
    "um ataque para mandá-la usar Golpe da Fera. Some se você morrer; volta com um espaço de "
    "magia até 1 hora depois, e pode ser trocada a cada Descanso Longo.",
    [{"id": "senhor_das_feras_companheira", "tipo": "escolha",
      "rotulo": "Escolha o bloco de estatísticas da sua fera", "quantidade": 1,
      "momento": "nivel_3", "reescolhivel": True, "reescolha_em": "descanso_longo",
      "de": {"catalogo": "feras_companheiras", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "conceder_companheiro",
                                    "catalogo": "feras_companheiras",
                                    "chave": "{{escolhido}}",
                                    "atitude": "amigavel",
                                    "some_se": ["voce_morre", "nova_fera_invocada"]}},
     {"tipo": "conceder_acao", "id": "comandar_fera_companheira", "custo": "acao_bonus",
      "descricao_curta": "Ordena à fera executar uma ação do bloco dela; sem o comando, a única "
                         "ação padrão dela é Esquivar. Incapacitado, ela age sozinha.",
      "efeitos": [{"tipo": "efeito_narrativo", "chave": "comando_da_fera",
                   "texto": "A fera executa a ação ordenada no turno dela."}]},
     {"tipo": "substituir_ataque_por_magia", "modo": "sacrificar_ataque",
      "substitui_por": "golpe_da_fera",
      "nota": "Não é magia: reaproveita o primitivo de trocar um ataque da ação Atacar por outra "
              "coisa. O livro chama de 'sacrificar um ataque para ordenar o Golpe da Fera'."},
     {"tipo": "efeito_narrativo", "chave": "restaurar_fera_companheira",
      "texto": "Ação Usar Magia e um espaço de magia para reviver a fera morta na última hora; "
               "ela volta com todos os Pontos de Vida após 1 minuto.",
      "custo": "acao", "acao_id": "usar_magia", "consome": "espaco_de_magia"}],
    "senhor_das_feras")

sub("treinamento_excepcional", "Treinamento Excepcional", 7, 124,
    "A Ação Bônus que comanda a fera também deixa ela usar Ajudar, Correr, Desengajar ou Esquivar "
    "com a Ação Bônus dela. E os acertos dela podem causar dano Energético em vez do tipo normal.",
    [{"tipo": "melhorar_caracteristica", "alvo": "comandar_fera_companheira",
      "efeitos": [{"tipo": "acao_adicional", "beneficiario": "fera_companheira",
                   "custo": "acao_bonus",
                   "acoes": ["ajudar", "correr", "desengajar", "esquivar"]}]},
     {"tipo": "escolher_tipo_de_dano", "beneficiario": "fera_companheira",
      "opcoes": ["energetico", "mesmo_da_arma"],
      "gatilho": "acerto_da_fera_que_causa_dano"}],
    "senhor_das_feras")

sub("furia_bestial", "Fúria Bestial", 11, 124,
    "Ordenado o Golpe da Fera, ela o usa duas vezes. E na primeira vez por turno em que acerta "
    "uma criatura sob Marca do Predador, causa o dano adicional dessa magia também.",
    [{"tipo": "conceder_ataque", "beneficiario": "fera_companheira", "quantidade": ["2"],
      "modo": "define_total_da_acao_atacar", "escopo": {"acao": "golpe_da_fera"}},
     {"tipo": "dano", "beneficiario": "fera_companheira",
      "formula_dado": "dado_de_dano_da_magia:marca_do_predador", "tipo_dano": "energetico",
      "frequencia": "uma_vez_por_turno",
      "gatilho": "a_fera_atinge_criatura_marcada_por:marca_do_predador"}],
    "senhor_das_feras")

sub("compartilhar_magias", "Compartilhar Magias", 15, 124,
    "Ao conjurar uma magia em si mesmo, pode afetar também a fera Companheira Primal, se ela "
    "estiver a até 9 m.",
    [{"tipo": "alterar_alvos_da_magia", "alvos_adicionais": 1,
      "restricao": "a sua fera Companheira Primal, a até 9 m de você",
      "condicao": {"todas": ["magia_com_alvo:voce_mesmo"]}}],
    "senhor_das_feras")

# ================================================= subclasse: Vigilante das Sombras

sub("emboscador_das_sombras", "Emboscador das Sombras", 3, 124,
    "Três benefícios: soma o modificador de Sabedoria na Iniciativa; Golpe Terrível com 2d6 de "
    "dano Psíquico adicional, uma vez por turno, com usos iguais ao modificador de Sabedoria; e "
    "+3 m de Deslocamento no seu primeiro turno de cada combate.",
    [{"tipo": "modificador", "alvo": "iniciativa", "valor": ["mod:SAB"], "empilha": "soma"},
     {"tipo": "recurso_com_recarga", "id": "golpe_terrivel", "nome": "Golpe Terrível",
      "formula_maximo": {"op": "max", "args": ["1", "mod:SAB"]},
      "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "dado_de_impacto", "id": "golpe_terrivel", "formula_dado": "2d6",
      "tipo_dano": "psiquico", "frequencia": "uma_vez_por_turno",
      "consome_recurso": "golpe_terrivel", "condicao": {"todas": ["acerto_com_arma"]}},
     {"tipo": "modificador", "alvo": "deslocamento", "valor": ["3"], "unidade": "metros",
      "empilha": "soma", "duracao": "ate_o_fim_deste_turno",
      "gatilho": "inicio_do_seu_primeiro_turno_do_combate"}],
    "vigilante_das_sombras")

sub("magias_do_vigilante_das_sombras", "Magias do Vigilante das Sombras", 3, 124,
    "Magias sempre preparadas pela tabela Magias do Vigilante das Sombras, sem contar para o limite.",
    [{"tipo": "magias_de_patrono",
      "tabela": tabela_magias("Magias do Vigilante das Sombras", 124, [
          (3, ["disfarcar_se"]), (5, ["corda_extradimensional"]), (9, ["medo"]),
          (13, ["invisibilidade_maior"]), (17, ["similaridade"])]),
      "modo": "sempre_preparada", "lista_id": "guardiao",
      "acesso_concedido_pela_subclasse": True,
      "nao_conta_para_o_limite": True}],
    "vigilante_das_sombras")

sub("visao_umbrosa", "Visão Umbrosa", 3, 125,
    "Visão no Escuro de 18 m — somando 18 m se já tiver. E, inteiramente na Escuridão, você fica "
    "Invisível para quem depende de Visão no Escuro para enxergar ali.",
    [{"tipo": "conceder_sentido", "sentido": "visao_no_escuro", "alcance_m": 18,
      "empilha": "soma"},
     {"tipo": "conceder_condicao", "condicao_id": "invisivel", "beneficiario": "voce",
      "escopo": "apenas_para_quem_depende_de_visao_no_escuro",
      "condicao": {"todas": ["inteiramente_na_escuridao"]}}],
    "vigilante_das_sombras")

sub("mente_de_ferro", "Mente de Ferro", 7, 125,
    "Proficiência em salvaguardas de Sabedoria — ou, se já tiver, de Carisma ou Inteligência.",
    [{"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "SAB",
      "nivel_dominio": "proficiente"},
     {"id": "mente_de_ferro_alternativa", "tipo": "escolha",
      "rotulo": "Já é proficiente em salvaguardas de Sabedoria: escolha Carisma ou Inteligência",
      "quantidade": 1, "momento": "nivel_7",
      "condicao": {"todas": ["ja_proficiente_em_salvaguarda:SAB"]},
      "de": {"catalogo": "atributos", "chaves": ["CAR", "INT"]},
      "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "salvaguarda",
                                    "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}}],
    "vigilante_das_sombras")

sub("torrente_do_vigilante", "Torrente do Vigilante", 11, 125,
    "O dano do Golpe Terrível vira 2d8, e cada uso pode acrescentar Golpe Repentino (outro ataque "
    "contra criatura a até 1,5 m do alvo) ou Medo em Massa (alvo e criaturas a até 3 m fazem "
    "salvaguarda de Sabedoria ou ficam Amedrontadas).",
    [{"tipo": "melhorar_caracteristica", "alvo": "emboscador_das_sombras",
      "efeitos": [{"tipo": "dado_de_impacto", "id": "golpe_terrivel", "formula_dado": "2d8",
                   "tipo_dano": "psiquico", "empilha": "substitui"}]},
     {"id": "torrente_do_vigilante_efeito", "tipo": "escolha",
      "rotulo": "Escolha o efeito adicional do Golpe Terrível", "quantidade": 1,
      "momento": "cada_uso", "reescolhivel": True, "reescolha_em": "cada_uso",
      "de": {"catalogo": "efeitos_da_torrente_do_vigilante", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                    "catalogo": "efeitos_da_torrente_do_vigilante",
                                    "chave": "{{escolhido}}"}}],
    "vigilante_das_sombras")

sub("esquiva_sombria", "Esquiva Sombria", 15, 125,
    "Reação para impor Desvantagem numa jogada de ataque contra você; acertando ou errando, você "
    "pode se teleportar até 9 m para um espaço desocupado à vista.",
    [{"tipo": "vantagem", "alvo": "jogada_de_ataque_contra_voce", "modo": "desvantagem",
      "custo": "reacao", "gatilho": "criatura_realiza_jogada_de_ataque_contra_voce"},
     {"tipo": "teleporte", "distancia_m": 9, "destino": "espaco_desocupado_a_vista",
      "junto_com": "a mesma Reação, tenha o ataque acertado ou errado"}],
    "vigilante_das_sombras")


# ================================================================== catálogos

def catalogo(cid, nome, pag, itens, nota=None, **extra):
    d = collections.OrderedDict([
        ("catalogo", cid), ("nome", nome), ("fonte", fonte(pag)),
        ("total", len(itens)), ("itens", itens)])
    if nota:
        d["nota"] = nota
    d.update(extra)
    return d


FERA_TRACO_VINCULO = {
    "id": "vinculo_primal", "nome": "Vínculo Primal",
    "descricao_curta": "Some seu Bônus de Proficiência a qualquer teste de atributo ou "
                       "salvaguarda que a fera realizar.",
    "efeitos": [{"tipo": "modificador", "alvo": "teste_de_atributo", "valor": ["prof"],
                 "empilha": "soma"},
                {"tipo": "modificador", "alvo": "salvaguarda", "valor": ["prof"],
                 "empilha": "soma"}]}


def fera(fid, nome, pag, tamanho, ca_bonus_pv, desloc, atributos, sentidos, tracos, golpe):
    """Bloco de estatísticas do Companheiro Primal (cap. 3, não Ap. B)."""
    return collections.OrderedDict([
        ("id", fid), ("nome", nome), ("fonte", fonte(pag)),
        ("tipo_de_criatura", "fera"), ("tamanho", tamanho), ("atitude", "neutra"),
        ("classe_de_armadura", {"formula": ["13", "mod:SAB"]}),
        ("iniciativa", ca_bonus_pv["iniciativa"]),
        ("pontos_de_vida", {
            "formula": {"op": "soma", "args": [str(ca_bonus_pv["pv_base"]),
                                               {"op": "mult", "args": ["5", "nivel_classe:guardiao"]}]},
            "dado_de_vida": ca_bonus_pv["dado_de_vida"],
            "quantidade_de_dados": ["nivel_classe:guardiao"]}),
        ("deslocamentos", desloc),
        ("atributos", atributos),
        ("sentidos", sentidos),
        ("idiomas_texto", "Compreende os idiomas que você fala"),
        ("nivel_de_desafio", {"texto": "Nenhum", "xp": 0,
                              "bonus_de_proficiencia": "prof_do_guardiao"}),
        ("tracos", tracos),
        ("acoes", [golpe])])


def golpe_da_fera(dado, bonus, tipos, extra=None):
    a = collections.OrderedDict([
        ("id", "golpe_da_fera"), ("nome", "Golpe da Fera"),
        ("tipo_de_ataque", "corpo_a_corpo"),
        ("bonus_de_ataque", ["jogada_de_ataque_magico_do_guardiao"]),
        ("alcance_m", 1.5),
        ("dano", {"formula_dado": dado, "somar": [str(bonus), "mod:SAB"],
                  "tipos_de_dano": tipos,
                  "escolha_do_tipo": "ao_invocar_a_fera" if len(tipos) > 1 else None}),
        # A descrição sai do próprio dado, como nas criaturas do Apêndice B. Faltava:
        # a checagem de bloco de estatísticas acusou quando o Ap. B chegou.
        ("descricao_curta",
         "Ataque corpo a corpo, alcance 1,5 m, usando o bônus de ataque mágico do "
         "Guardião: " + dado + " + " + str(bonus) + " + modificador de Sabedoria de "
         "dano " + (" ou ".join(tipos) if len(tipos) > 1 else tipos[0]) +
         ("; o tipo é escolhido ao invocar a fera." if len(tipos) > 1 else ".")),
        ("descricao_derivada", True)])
    if extra:
        a.update(extra)
    return a


ATRIB = lambda f, d, c, i, s, ca: {"FOR": f, "DES": d, "CON": c, "INT": i, "SAB": s, "CAR": ca}

FERAS = [
    fera("fera_do_ceu", "Fera do Céu", 123, "pequeno",
         {"iniciativa": 2, "pv_base": 4, "dado_de_vida": "d6"},
         [{"tipo": "caminhada", "metros": 3}, {"tipo": "voo", "metros": 18}],
         ATRIB(6, 16, 13, 8, 14, 11),
         [{"sentido": "visao_no_escuro", "alcance_m": 18},
          {"sentido": "percepcao_passiva", "valor": 12}],
         [{"id": "sobrevoo", "nome": "Sobrevoo",
           "descricao_curta": "Não provoca Ataques de Oportunidade ao voar para fora do alcance "
                              "de um inimigo.",
           "efeitos": [{"tipo": "impedir", "alvo": "ataque_de_oportunidade_provocado_por_voce",
                        "condicao": {"todas": ["voando"]}}]},
          FERA_TRACO_VINCULO],
         golpe_da_fera("1d4", 3, ["cortante"])),
    fera("fera_do_mar", "Fera do Mar", 124, "medio",
         {"iniciativa": 3, "pv_base": 5, "dado_de_vida": "d8"},
         [{"tipo": "caminhada", "metros": 1.5}, {"tipo": "natacao", "metros": 18}],
         ATRIB(14, 14, 15, 8, 14, 11),
         [{"sentido": "visao_no_escuro", "alcance_m": 18},
          {"sentido": "percepcao_passiva", "valor": 12}],
         [{"id": "anfibio", "nome": "Anfíbio",
           "descricao_curta": "Respira ar e água.",
           "efeitos": [{"tipo": "efeito_narrativo", "chave": "respira_ar_e_agua",
                        "texto": "A fera pode respirar ar e água."}]},
          FERA_TRACO_VINCULO],
         golpe_da_fera("1d6", 2, ["contundente", "perfurante"],
                       {"efeito_adicional": [
                           {"tipo": "conceder_condicao", "condicao_id": "imobilizado",
                            "cd_para_escapar": ["cd_para_evitar_sua_magia"]}]})),
    fera("fera_da_terra", "Fera da Terra", 124, "medio",
         {"iniciativa": 2, "pv_base": 5, "dado_de_vida": "d8"},
         [{"tipo": "caminhada", "metros": 12}, {"tipo": "escalada", "metros": 12}],
         ATRIB(14, 14, 15, 8, 14, 11),
         [{"sentido": "visao_no_escuro", "alcance_m": 18},
          {"sentido": "percepcao_passiva", "valor": 12}],
         [FERA_TRACO_VINCULO],
         golpe_da_fera("1d8", 2, ["contundente", "cortante", "perfurante"],
                       {"efeito_adicional": [
                           {"tipo": "dano", "formula_dado": "1d6", "tipo_dano": "mesmo_do_ataque",
                            "condicao": {"todas": ["a_fera_moveu_ao_menos_6m_ate_o_alvo"]}},
                           {"tipo": "conceder_condicao", "condicao_id": "caido",
                            "restricao_de_tamanho": "grande_ou_menor",
                            "condicao": {"todas": ["a_fera_moveu_ao_menos_6m_ate_o_alvo"]}}]})),
]

DADIVAS = [
    ("borboletas_ilusorias", "Borboletas ilusórias", 1,
     "Borboletas ilusórias flutuam ao seu redor durante um Descanso Curto ou Longo."),
    ("flores_no_cabelo", "Flores no cabelo", 2, "Flores desabrocham do seu cabelo a cada amanhecer."),
    ("fragrancia_natural", "Fragrância natural", 3,
     "Você cheira levemente a canela, lavanda, noz-moscada ou outra erva ou fragrância natural."),
    ("sombra_dancante", "Sombra dançante", 4,
     "Sua sombra dança enquanto ninguém está olhando diretamente para ela."),
    ("chifres_ou_galhadas", "Chifres ou galhadas", 5, "Chifres ou galhadas brotam da sua cabeça."),
    ("cores_mutaveis", "Cores mutáveis", 6, "Sua pele e cabelo mudam de cor a cada amanhecer."),
]

PRESA = [
    collections.OrderedDict([
        ("id", "assassino_de_colossos"), ("nome", "Assassino de Colossos"),
        ("fonte", fonte(122)),
        ("descricao_curta", "Ao atingir com arma uma criatura que não está com os Pontos de Vida "
                            "no máximo, causa 1d8 de dano adicional, uma vez por turno."),
        ("efeitos", [{"tipo": "dado_de_impacto", "formula_dado": "1d8",
                      "tipo_dano": "mesmo_da_arma", "frequencia": "uma_vez_por_turno",
                      "condicao": {"todas": ["acerto_com_arma",
                                             "alvo_com_pv_abaixo_do_maximo"]}}])]),
    collections.OrderedDict([
        ("id", "destruidor_de_hordas"), ("nome", "Destruidor de Hordas"),
        ("fonte", fonte(122)),
        ("descricao_curta", "Uma vez por turno, ao atacar com uma arma, faz outro ataque com a "
                            "mesma arma contra outra criatura a até 1,5 m do alvo original."),
        ("efeitos", [{"tipo": "conceder_ataque", "quantidade": ["1"],
                      "frequencia": "uma_vez_por_turno",
                      "restricao": "mesma arma, contra criatura diferente a até 1,5 m do alvo "
                                   "original, dentro do alcance da arma e ainda não atacada "
                                   "neste turno"}])]),
]

TATICAS = [
    collections.OrderedDict([
        ("id", "defesa_contra_ataques_multiplos"), ("nome", "Defesa Contra Ataques Múltiplos"),
        ("fonte", fonte(122)),
        ("descricao_curta", "Ao ser atingido por uma jogada de ataque, aquela criatura tem "
                            "Desvantagem em todas as outras jogadas de ataque contra você neste turno."),
        ("efeitos", [{"tipo": "vantagem", "alvo": "jogada_de_ataque_contra_voce",
                      "modo": "desvantagem", "gatilho": "ser_atingido_por_jogada_de_ataque",
                      "escopo": "demais_ataques_da_mesma_criatura_neste_turno"}])]),
    collections.OrderedDict([
        ("id", "escapar_de_hordas"), ("nome", "Escapar de Hordas"),
        ("fonte", fonte(122)),
        ("descricao_curta", "Ataques de Oportunidade contra você têm Desvantagem."),
        ("efeitos", [{"tipo": "vantagem", "alvo": "jogada_de_ataque_contra_voce",
                      "modo": "desvantagem",
                      "escopo": "ataques_de_oportunidade"}])]),
]

TORRENTE = [
    collections.OrderedDict([
        ("id", "golpe_repentino"), ("nome", "Golpe Repentino"), ("fonte", fonte(125)),
        ("descricao_curta", "Outro ataque com a mesma arma contra criatura diferente a até 1,5 m "
                            "do alvo original e dentro do alcance da arma."),
        ("efeitos", [{"tipo": "conceder_ataque", "quantidade": ["1"],
                      "restricao": "mesma arma, contra criatura diferente a até 1,5 m do alvo "
                                   "original e dentro do alcance da arma"}])]),
    collections.OrderedDict([
        ("id", "medo_em_massa"), ("nome", "Medo em Massa"), ("fonte", fonte(125)),
        ("descricao_curta", "O alvo e cada criatura a até 3 m dele fazem salvaguarda de Sabedoria "
                            "ou ficam Amedrontadas até o início do seu próximo turno."),
        ("efeitos", [{"tipo": "conceder_condicao", "condicao_id": "amedrontado",
                      "alvo": "o_alvo_e_criaturas_a_ate_3m_dele",
                      "salvaguarda": {"atributo": "SAB", "cd": CD},
                      "duracao": "ate_o_inicio_do_seu_proximo_turno"}])]),
]

ESTILO_DE_LUTA_DE_CLASSE = [
    collections.OrderedDict([
        ("id", "combatente_druidico"), ("nome", "Combatente Druídico"),
        ("classe", "guardiao"), ("fonte", fonte(118)),
        ("descricao_curta", "Em vez de um talento de Estilo de Luta: dois truques de Druida à "
                            "escolha, contados como magias de Guardião, com Sabedoria. Troca um "
                            "deles a cada nível de Guardião."),
        ("efeitos", [{"id": "combatente_druidico_truques", "tipo": "escolha",
                      "rotulo": "Escolha 2 truques de Druida", "quantidade": 2,
                      "reescolhivel": True, "reescolha_em": "cada_nivel_de_guardiao",
                      "reescolha_quantidade": 1,
                      "de": {"catalogo": "magias", "filtro": {"nivel": 0, "lista": "druida"}},
                      "efeito_por_item_escolhido": {
                          "tipo": "desbloquear_magias", "lista_id": "guardiao",
                          "modo": "conhecida", "magia": "{{escolhido}}",
                          "atributo_conjuracao": "SAB"}}]),
        ("recomendadas", ["fagulha_estelar", "orientacao"])]),
]


# ==================================================================== a classe

SUBCLASSES = [
    ("andarilho_feerico", "Andarilho Feérico", 120,
     "Mística feérica: bônus de Carisma, dano Psíquico nos golpes, magias de Faéria e "
     "teleporte que leva companheiro junto."),
    ("cacador", "Caçador", 122,
     "Especialista em presa: lê Imunidades e Resistências do alvo marcado e escolhe pares de "
     "opções ofensivas e defensivas, trocáveis a cada descanso."),
    ("senhor_das_feras", "Senhor das Feras", 122,
     "Vínculo com uma fera primal — Terra, Céu ou Mar — que age em combate sob seu comando."),
    ("vigilante_das_sombras", "Vigilante das Sombras", 124,
     "Magia do Sombral: emboscada com dano Psíquico, Visão no Escuro ampliada e invisibilidade "
     "na Escuridão."),
]

# tabela Características do Guardião, p. 118
PROGRESSAO = [
    (1, 2, ["conjuracao_guardiao", "inimigo_favorito", "maestria_em_arma_guardiao"], 2, 2, [2, 0, 0, 0, 0]),
    (2, 2, ["estilo_de_luta_guardiao", "explorador_habil"], 2, 3, [2, 0, 0, 0, 0]),
    (3, 2, ["caracteristica_de_subclasse"], 2, 4, [3, 0, 0, 0, 0]),
    (4, 2, ["aumento_no_valor_de_atributo"], 2, 5, [3, 0, 0, 0, 0]),
    (5, 3, ["ataque_extra"], 3, 6, [4, 2, 0, 0, 0]),
    (6, 3, ["errante"], 3, 6, [4, 2, 0, 0, 0]),
    (7, 3, ["caracteristica_de_subclasse"], 3, 7, [4, 3, 0, 0, 0]),
    (8, 3, ["aumento_no_valor_de_atributo"], 3, 7, [4, 3, 0, 0, 0]),
    (9, 4, ["especialista_guardiao"], 4, 9, [4, 3, 2, 0, 0]),
    (10, 4, ["incansavel"], 4, 9, [4, 3, 2, 0, 0]),
    (11, 4, ["caracteristica_de_subclasse"], 4, 10, [4, 3, 3, 0, 0]),
    (12, 4, ["aumento_no_valor_de_atributo"], 4, 10, [4, 3, 3, 0, 0]),
    (13, 5, ["predador_implacavel"], 5, 11, [4, 3, 3, 1, 0]),
    (14, 5, ["veu_da_natureza"], 5, 11, [4, 3, 3, 1, 0]),
    (15, 5, ["caracteristica_de_subclasse"], 5, 12, [4, 3, 3, 2, 0]),
    (16, 5, ["aumento_no_valor_de_atributo"], 5, 12, [4, 3, 3, 2, 0]),
    (17, 6, ["cacador_preciso"], 6, 14, [4, 3, 3, 3, 1]),
    (18, 6, ["sentidos_selvagens"], 6, 14, [4, 3, 3, 3, 1]),
    (19, 6, ["dadiva_epica"], 6, 15, [4, 3, 3, 3, 2]),
    (20, 6, ["matador_de_inimigos_favoritos"], 6, 15, [4, 3, 3, 3, 2]),
]

COLUNAS = collections.OrderedDict([
    ("inimigo_favorito", {"nome": "Inimigo Favorito", "tipo": "inteiro"}),
    ("magias_preparadas", {"nome": "Magias Preparadas", "tipo": "inteiro"}),
])
for n in range(1, 6):
    COLUNAS[f"espacos_{n}"] = {"nome": f"Espaços de {n}º Círculo", "tipo": "inteiro"}

CLASSE = collections.OrderedDict([
    ("id", "guardiao"), ("nome", "Guardião"), ("fonte", fonte(117)), ("revisao", rev()),
    ("descricao_curta",
     "Meio-conjurador dos ermos: Sabedoria, Marca do Predador de graça pelo Inimigo Favorito, "
     "Estilo de Luta e maestria em duas armas. Rastreia, se move e some pelo terreno."),
    ("dado_de_vida", 10),
    ("atributo_primario", ["DES", "SAB"]),
    ("salvaguardas_primarias", ["FOR", "DES"]),
    ("nivel_subclasse", 3),
    ("niveis_de_caracteristica_de_subclasse", [3, 7, 11, 15]),
    ("conjuracao", {"atributo": "SAB", "modo": "lista_de_classe", "lista_id": "guardiao",
                    "preparadas_por_nivel": True, "meio_conjurador": True,
                    "circulo_maximo": 5, "truques": False}),
    ("subclasses", [s[0] for s in SUBCLASSES]),
    ("proficiencias_iniciais", [
        {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "FOR",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "DES",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "arma", "nivel_dominio": "proficiente",
         "de": {"catalogo": "itens", "filtro": {"categoria": "arma", "grupo": "simples"}}},
        {"tipo": "conceder_proficiencia", "categoria": "arma", "nivel_dominio": "proficiente",
         "de": {"catalogo": "itens", "filtro": {"categoria": "arma", "grupo": "marcial"}}},
        {"id": "guardiao_pericias_iniciais", "tipo": "escolha", "rotulo": "Escolha 3 perícias",
         "quantidade": 3, "momento": "criacao",
         "de": {"catalogo": "pericias",
                "chaves": ["atletismo", "furtividade", "intuicao", "investigacao",
                           "lidar_com_animais", "natureza", "percepcao", "sobrevivencia"]},
         "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                       "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}},
    ]),
    ("treinamento_com_armadura", ["leve", "media", "escudo"]),
    ("equipamento_inicial", {
        "opcoes": [
            {"id": "A",
             "itens": [{"item": "couro_batido"}, {"item": "cimitarra"},
                       {"item": "espada_curta"}, {"item": "arco_longo"},
                       {"item": "flechas", "quantidade": 20}, {"item": "aljava"},
                       {"item": "ramo_de_visco", "nota": "Foco Druídico (ramo de visco)."},
                       {"item": "kit_de_aventureiro"}],
             "moedas": {"po": 7}},
            {"id": "B", "itens": [], "moedas": {"po": 150}},
        ],
        "revisao": rev()}),
    ("colunas_da_tabela", COLUNAS),
    ("multiclasse", {
        "adquire": ["dado_de_vida", "proficiencia:arma:categoria:marcial",
                    "proficiencia:pericia:uma_da_lista_do_guardiao",
                    "treinamento_armadura:leve", "treinamento_armadura:media",
                    "treinamento_armadura:escudo"],
        "fonte": fonte(117),
        "nota": "Registrado para a fase de multiclasse; não aplicado agora."}),
    ("progressao", [
        collections.OrderedDict([
            ("nivel", n), ("bonus_de_proficiencia", bp), ("caracteristicas", cs),
            ("colunas", collections.OrderedDict(
                [("inimigo_favorito", inim), ("magias_preparadas", mp)]
                + [(f"espacos_{i+1}", v) for i, v in enumerate(sl)]))])
        for n, bp, cs, inim, mp, sl in PROGRESSAO]),
])

TIPOS_NOVOS = [
    ("imunidade_a_quebra_de_concentracao", "Imunidade a quebra de Concentração",
     "Declara que uma causa de perda de Concentração não se aplica, opcionalmente restrita a uma "
     "magia. Sofrer dano não quebra a Marca do Predador do Predador Implacável (Guardião 13)."),
    ("conceder_companheiro", "Conceder companheiro",
     "Vincula ao personagem uma criatura de bloco próprio, cujos valores derivam do nível e dos "
     "modificadores dele. Usado pelo Companheiro Primal do Senhor das Feras."),
]


def juntar(caminho, novos, campos):
    d = json.load(open(caminho, encoding='utf-8'),
                  object_pairs_hook=collections.OrderedDict)
    existentes = {i['id'] for i in d['itens']}
    n = 0
    for valores in novos:
        item = collections.OrderedDict(zip(campos, valores))
        if item['id'] in existentes:
            continue
        d['itens'].append(item)
        n += 1
    d['total'] = len(d['itens'])
    json.dump(d, open(caminho, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return n


def main():
    cats = [
        catalogo("feras_companheiras", "Feras Companheiras (Companheiro Primal)", 122, FERAS,
                 nota="Blocos de estatísticas impressos no capítulo 3, dentro da subclasse "
                      "Senhor das Feras. NÃO é o Apêndice B: 'criaturas' continua adiado e "
                      "vazio. CA, PV e Golpe da Fera derivam do nível e do modificador de "
                      "Sabedoria do Guardião.", preenchida=True),
        catalogo("dadivas_de_faeria", "Dádivas de Faéria", 121,
                 [collections.OrderedDict([
                     ("id", i), ("nome", nome), ("resultado_1d6", face),
                     ("fonte", fonte(121)), ("descricao_curta", desc),
                     ("efeitos", [{"tipo": "efeito_narrativo", "chave": "dadiva_de_faeria",
                                   "texto": desc}])])
                  for i, nome, face, desc in DADIVAS],
                 nota="Puramente estética: nenhuma das seis tem efeito mecânico. Escolhida ou "
                      "sorteada em 1d6."),
        catalogo("opcoes_de_presa_do_cacador", "Opções de Presa do Caçador", 122, PRESA),
        catalogo("opcoes_de_taticas_defensivas", "Opções de Táticas Defensivas", 122, TATICAS),
        catalogo("efeitos_da_torrente_do_vigilante", "Efeitos da Torrente do Vigilante", 125,
                 TORRENTE),
        catalogo("opcoes_de_estilo_de_luta_de_classe",
                 "Opções de Estilo de Luta concedidas por classe", 118, ESTILO_DE_LUTA_DE_CLASSE,
                 nota="Opções que o livro oferece NO LUGAR de um talento de Estilo de Luta. "
                      "Guardião traz Combatente Druídico; Paladino, Combatente Abençoado.",
                 parcial=True),
    ]
    for c in cats:
        with open(f"{CAT}/{c['catalogo']}.json", 'w', encoding='utf-8') as f:
            json.dump(c, f, ensure_ascii=False, indent=2)

    n_tipos = juntar(f'{CAT}/tipos_de_efeito.json', TIPOS_NOVOS,
                     ['id', 'nome', 'descricao_curta'])

    cl = json.load(open('dados/classes.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    cl['itens'] = [c for c in cl['itens'] if c['id'] != 'guardiao'] + [CLASSE]
    cl['total'] = len(cl['itens'])
    json.dump(cl, open('dados/classes.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    sc = json.load(open('dados/subclasses.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    sc['itens'] = [s for s in sc['itens'] if s.get('classe') != 'guardiao']
    for sid, nome, pag, desc in SUBCLASSES:
        sc['itens'].append(collections.OrderedDict([
            ("id", sid), ("nome", nome), ("classe", "guardiao"),
            ("fonte", fonte(pag)), ("revisao", rev()), ("descricao_curta", desc),
            ("niveis_de_caracteristica", [3, 7, 11, 15]),
            ("caracteristicas", [c['id'] for c in CARACS if c.get('subclasse') == sid])]))
    sc['total'] = len(sc['itens'])
    json.dump(sc, open('dados/subclasses.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    ca = json.load(open('dados/caracteristicas.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    ca['itens'] = [c for c in ca['itens'] if c.get('classe') != 'guardiao'] + CARACS
    # Ataque Extra é genérica: o Guardião entra na lista de quem a concede
    for c in ca['itens']:
        if c['id'] == 'ataque_extra':
            if not any(x.get('classe') == 'guardiao' for x in c.get('concedida_por', [])):
                c.setdefault('concedida_por', []).append(
                    {"classe": "guardiao", "nivel": 5, "pagina_livro": 118})
    ca['total'] = len(ca['itens'])
    json.dump(ca, open('dados/caracteristicas.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    print(f"guardião: {len(CARACS)} características | {len(SUBCLASSES)} subclasses")
    print(f"catálogos novos: " + ", ".join(f"{c['catalogo']} ({c['total']})" for c in cats))
    print(f"tipos de efeito novos: {n_tipos}")
    print(f"classes: {cl['total']} | subclasses: {sc['total']} | características: {ca['total']}")


if __name__ == '__main__':
    main()
