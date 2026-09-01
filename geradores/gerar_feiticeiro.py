# -*- coding: utf-8 -*-
"""Feiticeiro (cap. 3, p. 103-114).

O ponto do esquema aqui é a Metamagia: pela primeira vez uma característica
MODIFICA UMA MAGIA NO ATO DE CONJURAR — tempo de conjuração, alcance, duração,
círculo efetivo, componentes, tipo de dano. Isso não cabia em nenhum tipo de
efeito existente, então entram cinco tipos novos e um catálogo de opção
(`opcoes_de_metamagia`), com o custo em Pontos de Feitiçaria declarado por opção.

O segundo ponto é o Surto de Magia Selvagem: uma tabela de 1d100 que no nível 18
deixa de ser aleatória e vira ESCOLHA. Por isso ela é um catálogo de opção com
efeitos por linha — e não um bloco de texto —, com a faixa do d100 declarada e a
marca de qual linha o Surto Controlado não pode escolher.
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
        ("id", cid), ("nome", nome), ("classe", "feiticeiro"), ("nivel", nivel),
        ("fonte", fonte(pag)), ("revisao", rev()),
        ("descricao_curta", desc), ("efeitos", efeitos)])
    d.update(extra)
    CARACS.append(d)
    return d


def sub(cid, nome, nivel, pag, desc, efeitos, subclasse, **extra):
    d = car(cid, nome, nivel, pag, desc, efeitos, **extra)
    d['subclasse'] = subclasse
    return d


def tabela(nome, pag, linhas):
    return {"nome": nome, "fonte": fonte(pag),
            "linhas": [{"nivel": n, "magias": m} for n, m in linhas]}


CD = ["8", "mod:CAR", "prof"]
PF = "pontos_de_feiticaria"

# ============================================================ classe, nível 1

car("conjuracao_feiticeiro", "Conjuração", 1, 103,
    "Conjura pela lista de Feiticeiro, com Carisma. Prepara da lista inteira, sem livro, "
    "trocando uma magia por nível ganho. Usa Foco Arcano.",
    [{"tipo": "desbloquear_magias", "modo": "disponivel_para_preparar",
      "lista_id": "feiticeiro"},
     {"id": "feiticeiro_truques", "tipo": "escolha",
      "rotulo": "Escolha os truques de Feiticeiro",
      "quantidade": ["coluna:truques"], "reescolhivel": True,
      "reescolha_em": "subir_de_nivel", "quantidade_de_trocas": 1,
      "recomendadas": ["explosao_elemental", "luz", "prestidigitacao_arcana",
                       "toque_chocante"],
      "de": {"catalogo": "magias", "filtro": {"lista": "feiticeiro", "nivel": 0}},
      "efeito_por_item_escolhido": {"tipo": "desbloquear_magias",
                                    "magia": "{{escolhido}}", "modo": "conhecida"}},
     {"id": "feiticeiro_preparadas", "tipo": "escolha",
      "rotulo": "Escolha as magias preparadas de Feiticeiro",
      "quantidade": ["coluna:magias_preparadas"], "reescolhivel": True,
      "reescolha_em": "subir_de_nivel", "quantidade_de_trocas": 1,
      "recomendadas": ["detectar_magia", "maos_flamejantes"],
      "de": {"catalogo": "magias",
             "filtro": {"lista": "feiticeiro", "nivel_minimo": 1,
                        "circulo_com_espaco_disponivel": True}},
      "efeito_por_item_escolhido": {"tipo": "preparar_magias",
                                    "magia": "{{escolhido}}",
                                    "fonte_das_magias": "lista_de_classe",
                                    "lista_id": "feiticeiro"}}],
    cd_para_evitar_sua_magia=CD,
    foco_de_conjuracao=["foco_arcano"])

car("feiticaria_inata", "Feitiçaria Inata", 1, 104,
    "Ação Bônus para liberar a magia latente por 1 minuto: a CD para evitar suas magias "
    "de Feiticeiro sobe 1 e você tem Vantagem nas jogadas de ataque das magias de "
    "Feiticeiro que conjurar. Dois usos, recuperados no Descanso Longo.",
    [{"tipo": "recurso_com_recarga", "id": "feiticaria_inata_usos",
      "nome": "Feitiçaria Inata", "formula_maximo": ["2"],
      "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "conceder_acao", "id": "ativar_feiticaria_inata", "custo": "acao_bonus",
      "recurso_id": "feiticaria_inata_usos", "duracao": "1 minuto",
      "concede_flag": "feiticaria_inata_ativa",
      "efeitos": [
          {"tipo": "modificador", "alvo": "cd_para_evitar_sua_magia", "valor": ["1"],
           "empilha": "soma", "escopo": {"lista": "feiticeiro"}},
          {"tipo": "vantagem", "alvo": "jogada_de_ataque_magico", "modo": "vantagem",
           "escopo": {"lista": "feiticeiro"}}]}])

# ============================================================ classe, nível 2

CUSTO_DE_ESPACO = [(1, 2, 2), (2, 3, 3), (3, 5, 5), (4, 6, 7), (5, 7, 9)]

car("fonte_de_magia", "Fonte de Magia", 2, 104,
    "Você tem Pontos de Feitiçaria conforme a tabela, recuperados no Descanso Longo. "
    "Pode gastar um espaço de magia para receber pontos iguais ao círculo dele, e como "
    "Ação Bônus transformar pontos em um espaço de até 5º círculo — espaço criado assim "
    "some no Descanso Longo.",
    [{"tipo": "recurso_com_recarga", "id": PF, "nome": "Pontos de Feitiçaria",
      "formula_maximo": ["coluna:pontos_de_feiticaria"],
      "recarga": ["descanso_longo"], "consumo": "por_ponto"},
     {"tipo": "converter_recurso", "id": "espaco_para_pontos",
      "de": "espaco_de_magia", "para": PF,
      "taxa": "pontos_iguais_ao_circulo_do_espaco", "custo": "livre",
      "nota": "Nenhuma ação é necessária (p. 105)."},
     {"tipo": "converter_recurso", "id": "pontos_para_espaco",
      "de": PF, "para": "espaco_de_magia", "custo": "acao_bonus",
      "circulo_maximo": 5,
      "tabela_de_custo": [
          {"circulo": c, "custo_em_pontos": p, "nivel_minimo_de_feiticeiro": n}
          for c, p, n in CUSTO_DE_ESPACO],
      "espaco_criado": {"expira_em": "descanso_longo"},
      "fonte": fonte(105)}])

car("metamagia", "Metamagia", 2, 105,
    "Escolhe duas opções de Metamagia, mais duas no nível 10 e mais duas no nível 17, "
    "trocando uma por nível ganho. Cada opção consome Pontos de Feitiçaria e só se pode "
    "usar uma opção por magia, salvo quando a própria opção disser o contrário.",
    [{"id": "feiticeiro_metamagia", "tipo": "escolha",
      "rotulo": "Escolha opções de Metamagia", "quantidade": 2,
      "quantidade_por_nivel": {"2": 2, "10": 4, "17": 6},
      "reescolhivel": True, "reescolha_em": "subir_de_nivel", "quantidade_de_trocas": 1,
      "de": {"catalogo": "opcoes_de_metamagia", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                    "chave": "{{escolhido}}"},
      "limite": {"opcoes_por_magia": 1,
                 "nota": "Uma opção por conjuração, salvo quando a opção disser o "
                         "contrário (Buscadora e Potencializada dizem)."}}],
    niveis=[2, 10, 17], repetivel=True, tipo_de_repeticao="melhoria",
    nome_na_tabela="Metamagia")

car("subclasse_de_feiticeiro", "Subclasse de Feiticeiro", 3, 105,
    "Escolhe uma origem de feitiçaria. Ela concede características nos níveis 3, 6, 14 "
    "e 18 de Feiticeiro.",
    [{"id": "feiticeiro_subclasse", "tipo": "escolha",
      "rotulo": "Escolha uma origem de Feiticeiro", "quantidade": 1,
      "de": {"catalogo": "subclasses", "filtro": {"classe": "feiticeiro"}},
      "efeito_por_item_escolhido": {"tipo": "conceder_subclasse",
                                    "subclasse": "{{escolhido}}"}}])

car("restauracao_feiticeira", "Restauração Feiticeira", 5, 105,
    "Ao completar um Descanso Curto, recupera Pontos de Feitiçaria gastos até metade do "
    "seu nível de Feiticeiro (arredondado para baixo). Só de novo depois de um "
    "Descanso Longo.",
    [{"tipo": "recurso_com_recarga", "id": "restauracao_feiticeira_usos",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "restaurar_recurso", "recurso_id": PF,
      "quantidade": [{"op": "div_arred_baixo",
                      "args": ["nivel_classe:feiticeiro", "2"]}],
      "gatilho": "descanso_curto", "consome_recurso": "restauracao_feiticeira_usos"}])

car("feiticaria_encarnada", "Feitiçaria Encarnada", 7, 105,
    "Sem usos de Feitiçaria Inata, ainda pode ativá-la gastando 2 Pontos de Feitiçaria na "
    "Ação Bônus. E enquanto a Feitiçaria Inata estiver ativa, pode usar até duas opções "
    "de Metamagia em cada magia conjurada.",
    [{"tipo": "melhorar_caracteristica", "alvo": "feiticaria_inata",
      "efeitos": [
          {"tipo": "converter_recurso", "id": "inata_por_pontos",
           "de": PF, "para": "feiticaria_inata_usos", "taxa": "2:1",
           "custo": "acao_bonus",
           "condicao": {"todas": ["recurso:feiticaria_inata_usos.atual == 0"]}}]},
     {"tipo": "melhorar_caracteristica", "alvo": "metamagia",
      "efeitos": [
          {"tipo": "alterar_quantidade_de_escolha", "escolha_id": "feiticeiro_metamagia",
           "campo": "limite.opcoes_por_magia", "novo_valor": 2,
           "condicao": {"todas": ["flag:feiticaria_inata_ativa"]}}]}])

car("apoteose_arcana", "Apoteose Arcana", 20, 105,
    "Enquanto a Feitiçaria Inata estiver ativa, uma opção de Metamagia por turno não "
    "custa Pontos de Feitiçaria.",
    [{"tipo": "melhorar_caracteristica", "alvo": "metamagia",
      "efeitos": [
          {"tipo": "modificador", "alvo": "custo_de_metamagia", "valor": ["0"],
           "empilha": "substitui", "frequencia": "uma_vez_por_turno",
           "condicao": {"todas": ["flag:feiticaria_inata_ativa"]}}]}])

# ================================================== subclasse: Feitiçaria Aberrante

sub("fala_telepatica", "Fala Telepática", 3, 109,
    "Ação Bônus para abrir um canal telepático com uma criatura à vista a até 9 m. O "
    "canal alcança 1,5 km por ponto do modificador de Carisma (mínimo 1,5 km) e dura "
    "tantos minutos quanto seu nível de Feiticeiro; abrir outro canal encerra o anterior.",
    [{"tipo": "conceder_acao", "id": "abrir_fala_telepatica", "custo": "acao_bonus",
      "alcance_m": 9, "alvo_requerido": "criatura_a_vista",
      "duracao": "nivel de Feiticeiro em minutos",
      "duracao_em_minutos": ["nivel_classe:feiticeiro"],
      "encerra_se": [{"gatilho": "conectar_com_outra_criatura"}],
      "efeitos": [
          {"tipo": "efeito_narrativo", "chave": "canal_telepatico",
           "texto": "Você e a criatura se comunicam telepaticamente enquanto estiverem a "
                    "até 1,5 km por ponto do seu modificador de Carisma (mínimo 1,5 km); "
                    "cada um precisa usar mentalmente um idioma que o outro conheça.",
           "alcance_km": [{"op": "max",
                           "args": ["1.5", {"op": "mult", "args": ["1.5", "mod:CAR"]}]}]}]}],
    "feiticaria_aberrante")

sub("magias_psionicas", "Magias Psiônicas", 3, 109,
    "Magias sempre preparadas pela tabela Magias Psiônicas, sem contar para o limite.",
    [{"tipo": "magias_de_patrono",
      "tabela": tabela("Magias Psiônicas", 109, [
          (3, ["acalmar_emocoes", "bracos_de_hadar", "detectar_pensamentos",
               "sussurros_dissonantes", "talho_mental"]),
          (5, ["fome_de_hadar", "remeter"]),
          (7, ["invocar_aberracao", "tentaculos_negros_de_evard"]),
          (9, ["ligacao_telepatica_de_rary", "telecinese"])]),
      "modo": "sempre_preparada", "nao_conta_para_o_limite": True}],
    "feiticaria_aberrante")

sub("defesas_psiquicas", "Defesas Psíquicas", 6, 110,
    "Resistência a dano Psíquico e Vantagem em salvaguardas para evitar ou encerrar as "
    "condições Amedrontado e Enfeitiçado.",
    [{"tipo": "alterar_dano", "tipo_dano": "psiquico", "operacao": "resistencia"},
     {"tipo": "vantagem", "alvo": "salvaguarda", "modo": "vantagem",
      "aplica_a": "evitar_ou_encerrar_condicao",
      "condicao": {"alguma": ["condicao:amedrontado", "condicao:enfeiticado"]}}],
    "feiticaria_aberrante")

sub("feiticaria_psionica", "Feitiçaria Psiônica", 6, 110,
    "Magias de 1º círculo ou superior da característica Magias Psiônicas podem ser "
    "conjuradas gastando Pontos de Feitiçaria iguais ao círculo, em vez de um espaço. "
    "Conjurada assim, a magia dispensa componentes Verbais, Somáticos e Materiais — "
    "salvo material consumido ou com custo detalhado.",
    [{"tipo": "conjurar_sem_espaco", "escopo": {"caracteristica": "magias_psionicas",
                                                "nivel_minimo": 1},
      "custo_em_recurso": {"recurso_id": PF, "quantidade": "igual_ao_circulo"},
      "frequencia": "sem_limite"},
     {"tipo": "dispensar_componentes", "componentes": ["V", "S", "M"],
      "escopo": {"caracteristica": "magias_psionicas", "nivel_minimo": 1},
      "excecoes": ["material_consumido", "material_com_custo"],
      "condicao": {"todas": ["conjurada_com_pontos_de_feiticaria"]}}],
    "feiticaria_aberrante")

sub("revelacao_em_carne", "Revelação em Carne", 14, 110,
    "Ação Bônus gastando 1 ou mais Pontos de Feitiçaria para alterar o corpo por 10 "
    "minutos: cada ponto compra um dos quatro benefícios à sua escolha.",
    [{"id": "revelacao_em_carne_escolha", "tipo": "escolha",
      "rotulo": "Escolha os benefícios da Revelação em Carne",
      "quantidade": "um_por_ponto_gasto", "custo_por_item": {"recurso_id": PF,
                                                             "quantidade": 1},
      "custo": "acao_bonus", "duracao": "10 minutos",
      "momento": "ao_ativar", "reescolhivel": True, "reescolha_em": "cada_ativacao",
      "de": {"catalogo": "alteracoes_da_revelacao_em_carne", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                    "chave": "{{escolhido}}"}}],
    "feiticaria_aberrante")

sub("implosao_de_distorcao", "Implosão de Distorção", 18, 110,
    "Ação Usar Magia: teleporta-se para um espaço desocupado à vista a até 36 m. Cada "
    "criatura a até 9 m do espaço abandonado faz salvaguarda de Força contra a CD para "
    "evitar sua magia; se falhar, sofre 3d10 de dano Energético e é puxada para o espaço "
    "desocupado mais próximo daquele que você deixou. Uma vez por Descanso Longo, ou "
    "gastando 5 Pontos de Feitiçaria.",
    [{"tipo": "recurso_com_recarga", "id": "implosao_de_distorcao_usos",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "conceder_acao", "id": "usar_implosao_de_distorcao", "custo": "acao",
      "acao_id": "usar_magia", "recurso_id": "implosao_de_distorcao_usos",
      "custo_alternativo": {"recurso_id": PF, "quantidade": 5, "custo": "livre"},
      "efeitos": [
          {"tipo": "teleporte", "alcance_m": 36,
           "requisitos": ["destino_desocupado", "destino_a_vista"]},
          {"tipo": "dano", "formula_dado": "3d10", "tipo_dano": "energetico",
           "area": {"forma": "esfera", "raio_m": 9, "origem": "espaco_abandonado"},
           "salvaguarda": {"atributo": "FOR", "cd": CD, "sucesso": "metade_do_dano"}},
          {"tipo": "movimento_forcado", "direcao": "puxar",
           "destino": "espaco_desocupado_mais_proximo_do_espaco_abandonado",
           "condicao": {"todas": ["falhou_na_salvaguarda"]}}]}],
    "feiticaria_aberrante")

# ================================================== subclasse: Feitiçaria Dracônica

sub("magias_draconicas", "Magias Dracônicas", 3, 110,
    "Magias sempre preparadas pela tabela Magias Dracônicas, sem contar para o limite.",
    [{"tipo": "magias_de_patrono",
      "tabela": tabela("Magias Dracônicas", 110, [
          (3, ["alterar_se", "comando", "orbe_cromatico", "sopro_de_dragao"]),
          (5, ["medo", "voo"]),
          (7, ["enfeiticar_monstro", "olho_arcano"]),
          (9, ["invocar_dragao", "lendas_e_historias"])]),
      "modo": "sempre_preparada", "nao_conta_para_o_limite": True}],
    "feiticaria_draconica")

sub("resiliencia_draconica", "Resiliência Dracônica", 3, 110,
    "Pontos de Vida máximos aumentam em 3 e mais 1 a cada nível de Feiticeiro seguinte. "
    "Sem armadura, sua CA base é 10 + modificador de Destreza + modificador de Carisma.",
    [{"tipo": "modificador", "alvo": "pontos_de_vida_maximos",
      "valor": ["nivel_classe:feiticeiro"],
      "empilha": "soma",
      "nota": "O livro diz '+3 ao adquirir, +1 a cada nível de Feiticeiro seguinte' "
              "(p. 110). Como a característica chega no nível 3, isso é exatamente o "
              "nível de Feiticeiro: 3 no nível 3, 4 no nível 4, e assim por diante. "
              "Guardado como a conta fechada, não como duas parcelas."},
     {"tipo": "ca_base", "id": "ca_resiliencia_draconica",
      "formula": ["10", "mod:DES", "mod:CAR"],
      "concorre_como": "calculo_de_ca_base",
      "condicao": {"todas": ["flag:sem_armadura"]},
      "permite_escudo": True,
      "nota": "Concorre com os demais cálculos de CA base; o jogador escolhe um, não se "
              "somam (Ap. C, 'Classe de Armadura')."}],
    "feiticaria_draconica")

sub("afinidade_elemental", "Afinidade Elemental", 6, 110,
    "Escolhe um tipo de dano dracônico (Ácido, Elétrico, Gélido, Ígneo ou Venenoso): "
    "ganha Resistência a ele e soma o modificador de Carisma a uma jogada de dano das "
    "magias que causam esse tipo.",
    [{"id": "afinidade_elemental_tipo", "tipo": "escolha",
      "rotulo": "Escolha o tipo de dano da sua ancestralidade dracônica", "quantidade": 1,
      "de": {"catalogo": "tipos_de_dano",
             "chaves": ["acido", "eletrico", "gelido", "igneo", "venenoso"]},
      "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                    "chave": "{{escolhido}}"}}],
    "feiticaria_draconica",
    efeitos_nomeados={
        d: {"efeitos": [
            {"tipo": "alterar_dano", "tipo_dano": d, "operacao": "resistencia"},
            {"tipo": "modificador", "alvo": "jogada_de_dano", "valor": ["mod:CAR"],
             "empilha": "soma", "frequencia": "uma_jogada_por_magia",
             "escopo": {"origem": "magia", "tipo_de_dano": d}}]}
        for d in ("acido", "eletrico", "gelido", "igneo", "venenoso")})

sub("asas_de_dragao", "Asas de Dragão", 14, 110,
    "Ação Bônus: asas dracônicas por 1 hora, ou até você encerrá-las, dando Deslocamento "
    "de Voo de 18 m. Uma vez por Descanso Longo, ou gastando 3 Pontos de Feitiçaria para "
    "restaurar o uso.",
    [{"tipo": "recurso_com_recarga", "id": "asas_de_dragao_usos",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "converter_recurso", "id": "asas_por_pontos", "de": PF,
      "para": "asas_de_dragao_usos", "taxa": "3:1", "custo": "livre"},
     {"tipo": "conceder_acao", "id": "abrir_asas_de_dragao", "custo": "acao_bonus",
      "recurso_id": "asas_de_dragao_usos", "duracao": "1 hora",
      "encerra_se": [{"gatilho": "encerrar_voluntariamente", "custo": "livre"}],
      "efeitos": [{"tipo": "conceder_velocidade", "tipo_deslocamento": "voo",
                   "formula": ["18"]}]}],
    "feiticaria_draconica")

sub("companheiro_draconico", "Companheiro Dracônico", 18, 110,
    "Conjura Invocar Dragão sem componente Material e, uma vez por Descanso Longo, sem "
    "gastar espaço de magia. Ao começar a conjurar, pode dispensar a Concentração — e "
    "então a duração daquela conjuração vira 1 minuto.",
    [{"tipo": "dispensar_componentes", "componentes": ["M"],
      "escopo": {"magias": ["invocar_dragao"]}},
     {"tipo": "conjurar_sem_espaco", "magia": "invocar_dragao",
      "frequencia": "uma_vez_por_descanso_longo"},
     {"tipo": "dispensar_concentracao", "magias": ["invocar_dragao"],
      "opcional": True, "momento": "ao_comecar_a_conjurar",
      "duracao_substituta": "1 minuto"}],
    "feiticaria_draconica")

# ================================================== subclasse: Feitiçaria Mecânica

sub("magias_mecanicas", "Magias Mecânicas", 3, 111,
    "Magias sempre preparadas pela tabela Magias Mecânicas, sem contar para o limite. "
    "Escolhe também, na tabela Manifestações da Ordem, como a conexão com a ordem "
    "aparece quando você conjura.",
    [{"tipo": "magias_de_patrono",
      "tabela": tabela("Magias Mecânicas", 111, [
          (3, ["alarme", "auxilio", "protecao_contra_o_bem_e_o_mal",
               "restauracao_menor"]),
          (5, ["dissipar_magia", "protecao_contra_energia"]),
          (7, ["invocar_constructo", "movimentacao_livre"]),
          (9, ["muralha_de_energia", "restauracao_maior"])]),
      "modo": "sempre_preparada", "nao_conta_para_o_limite": True},
     {"id": "manifestacao_da_ordem", "tipo": "escolha",
      "rotulo": "Escolha (ou role 1d6) a sua Manifestação da Ordem", "quantidade": 1,
      "aleatorio_permitido": {"dado": "1d6"}, "apenas_narrativo": True,
      "de": {"catalogo": "manifestacoes_da_ordem", "todo_o_catalogo": True},
      "efeito_por_item_escolhido": {"tipo": "efeito_narrativo",
                                    "chave": "{{escolhido}}"}}],
    "feiticaria_mecanica")

sub("restaurar_equilibrio", "Restaurar Equilíbrio", 3, 111,
    "Reação, quando uma criatura à vista a até 18 m está prestes a jogar um d20 com "
    "Vantagem ou Desvantagem: o teste deixa de ser afetado por Vantagem e Desvantagem. "
    "Usos iguais ao modificador de Carisma (mínimo 1), recuperados no Descanso Longo.",
    [{"tipo": "recurso_com_recarga", "id": "restaurar_equilibrio_usos",
      "nome": "Restaurar Equilíbrio",
      "formula_maximo": [{"op": "max", "args": ["mod:CAR", "1"]}],
      "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "impedir", "alvo": "vantagem_ou_desvantagem_em_teste_d20",
      "beneficiario": "criatura_a_vista", "alcance_m": 18, "custo": "reacao",
      "recurso_id": "restaurar_equilibrio_usos",
      "momento": "antes_da_jogada"}],
    "feiticaria_mecanica")

sub("bastiao_da_lei", "Bastião da Lei", 6, 111,
    "Ação Usar Magia gastando de 1 a 5 Pontos de Feitiçaria: cria uma proteção em você ou "
    "numa criatura à vista a até 9 m, com um d8 por ponto gasto. Quando a criatura "
    "protegida sofre dano, pode gastar dados da reserva e reduzir o dano pelo resultado. "
    "Dura até o Descanso Longo ou até você usar de novo.",
    [{"tipo": "reserva_de_dados", "id": "bastiao_da_lei", "dado": "d8",
      "formula_quantidade": ["pontos_de_feiticaria_gastos"],
      "custo": "acao", "acao_id": "usar_magia",
      "custo_em_recurso": {"recurso_id": PF, "minimo": 1, "maximo": 5},
      "alvo": "voce_ou_criatura_a_vista", "alcance_m": 9,
      "recarga": ["descanso_longo"],
      "encerra_se": [{"gatilho": "usar_a_caracteristica_de_novo"}],
      "gasto": {"gatilho": "criatura_protegida_sofre_dano",
                "quantidade": "a_escolha_da_criatura"},
      "efeitos": [{"tipo": "reducao_de_dano",
                   "formula": ["resultado_dos_dados_gastos"]}]}],
    "feiticaria_mecanica")

sub("transe_da_ordem", "Transe da Ordem", 14, 111,
    "Ação Bônus para entrar em transe por 1 minuto: jogadas de ataque contra você não se "
    "beneficiam de Vantagem, e em qualquer Teste de D20 você trata um resultado 9 ou "
    "menor no d20 como 10. Uma vez por Descanso Longo, ou gastando 5 Pontos de Feitiçaria "
    "para restaurar o uso.",
    [{"tipo": "recurso_com_recarga", "id": "transe_da_ordem_usos",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "converter_recurso", "id": "transe_por_pontos", "de": PF,
      "para": "transe_da_ordem_usos", "taxa": "5:1", "custo": "livre"},
     {"tipo": "conceder_acao", "id": "entrar_em_transe_da_ordem", "custo": "acao_bonus",
      "recurso_id": "transe_da_ordem_usos", "duracao": "1 minuto",
      "efeitos": [
          {"tipo": "impedir", "alvo": "vantagem_em_ataque_contra_voce"},
          {"tipo": "tratar_resultado_minimo", "alvo": "teste_d20", "minimo": 10}]}],
    "feiticaria_mecanica")

sub("cavalgada_mecanica", "Cavalgada Mecânica", 18, 112,
    "Ação Usar Magia: espíritos da ordem num Cubo de 9 m originado em você. Eles curam "
    "até 100 Pontos de Vida divididos como você quiser entre criaturas à sua escolha no "
    "Cubo, encerram magias de 6º círculo ou inferior em criaturas e objetos à sua escolha "
    "no Cubo, e reparam instantaneamente os objetos danificados no Cubo. Uma vez por "
    "Descanso Longo, ou gastando 7 Pontos de Feitiçaria para restaurar o uso.",
    [{"tipo": "recurso_com_recarga", "id": "cavalgada_mecanica_usos",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "converter_recurso", "id": "cavalgada_por_pontos", "de": PF,
      "para": "cavalgada_mecanica_usos", "taxa": "7:1", "custo": "livre"},
     {"tipo": "conceder_acao", "id": "usar_cavalgada_mecanica", "custo": "acao",
      "acao_id": "usar_magia", "recurso_id": "cavalgada_mecanica_usos",
      "area": {"forma": "cubo", "lado_m": 9, "origem": "voce"},
      "efeitos": [
          {"tipo": "cura", "formula": ["100"], "modo": "dividido_a_sua_escolha",
           "alvo": "criaturas_a_sua_escolha_na_area"},
          {"tipo": "dissipar_magias", "circulo_maximo": 6,
           "alvo": "criaturas_e_objetos_a_sua_escolha_na_area"},
          {"tipo": "efeito_narrativo", "chave": "reparar_objetos",
           "texto": "Todos os objetos danificados inteiramente dentro do Cubo são "
                    "reparados instantaneamente."}]}],
    "feiticaria_mecanica")

# ================================================== subclasse: Feitiçaria Selvagem

sub("mares_do_caos", "Marés do Caos", 3, 113,
    "Antes de jogar, garante Vantagem num Teste de D20 à sua escolha. Depois de usar, só "
    "recupera conjurando uma magia de Feiticeiro com um espaço — o que dispara "
    "automaticamente um Surto de Magia Selvagem — ou completando um Descanso Longo.",
    [{"tipo": "recurso_com_recarga", "id": "mares_do_caos_usos",
      "nome": "Marés do Caos", "formula_maximo": ["1"],
      "recarga": ["descanso_longo",
                  {"gatilho": "conjurar_magia_de_feiticeiro_com_espaco",
                   "quantidade": "todos",
                   "condicao": {"todas": ["recurso:mares_do_caos_usos.atual == 0"]},
                   "efeito_colateral": {"tipo": "efeito_narrativo",
                                        "chave": "surto_automatico",
                                        "texto": "Essa conjuração dispara "
                                                 "automaticamente um Surto de Magia "
                                                 "Selvagem, sem a jogada de 1d20."}}],
      "consumo": "por_uso"},
     {"tipo": "vantagem", "alvo": "teste_d20", "modo": "vantagem",
      "momento": "antes_da_jogada", "recurso_id": "mares_do_caos_usos"}],
    "feiticaria_selvagem")

sub("surto_de_magia_selvagem", "Surto de Magia Selvagem", 3, 113,
    "Uma vez por turno, logo depois de conjurar uma magia de Feiticeiro com um espaço, "
    "pode jogar 1d20: em 20, joga na tabela Surto de Magia Selvagem. Se o efeito for uma "
    "magia, ela é selvagem demais para sua Metamagia.",
    [{"tipo": "rolar_na_tabela", "id": "surto_de_magia_selvagem",
      "catalogo": "surtos_de_magia_selvagem", "dado_da_tabela": "1d100",
      "gatilho": {"evento": "conjurar_magia_de_feiticeiro_com_espaco",
                  "teste": {"dado": "1d20", "dispara_em": [20]}},
      "frequencia": "uma_vez_por_turno",
      "restricoes": ["magia_resultante_nao_aceita_metamagia"]}],
    "feiticaria_selvagem")

sub("distorcer_a_sorte", "Distorcer a Sorte", 6, 113,
    "Reação, logo depois de outra criatura à sua vista jogar o d20 de um Teste de D20: "
    "gasta 1 Ponto de Feitiçaria, joga 1d4 e aplica o resultado como bônus ou penalidade, "
    "à sua escolha, naquele teste.",
    [{"tipo": "modificador", "alvo": "teste_d20_de_criatura_a_vista",
      "valor": ["1d4"], "empilha": "soma", "sinal": "a_sua_escolha",
      "custo": "reacao", "momento": "apos_a_jogada",
      "custo_em_recurso": {"recurso_id": PF, "quantidade": 1}}],
    "feiticaria_selvagem")

sub("caos_controlado", "Caos Controlado", 14, 113,
    "Ao jogar na tabela Surto de Magia Selvagem, joga duas vezes e usa qualquer um dos "
    "dois resultados.",
    [{"tipo": "melhorar_caracteristica", "alvo": "surto_de_magia_selvagem",
      "efeitos": [{"tipo": "rolar_novamente", "alvo": "rolagem_na_tabela",
                   "usa_novo_resultado": False,
                   "escolhe_entre_os_resultados": True}]}],
    "feiticaria_selvagem")

sub("surto_controlado", "Surto Controlado", 18, 114,
    "Logo depois de conjurar uma magia de Feiticeiro com um espaço, pode escolher um "
    "efeito da tabela Surto de Magia Selvagem em vez de jogar — qualquer um, exceto a "
    "linha final; se o efeito escolhido envolver uma jogada, você a realiza. Uma vez por "
    "Descanso Longo.",
    [{"tipo": "recurso_com_recarga", "id": "surto_controlado_usos",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"id": "surto_controlado_escolha", "tipo": "escolha",
      "rotulo": "Escolha o efeito do Surto de Magia Selvagem", "quantidade": 1,
      "momento": "apos_conjurar_magia_de_feiticeiro_com_espaco",
      "reescolhivel": True, "reescolha_em": "cada_uso",
      "recurso_id": "surto_controlado_usos",
      "de": {"catalogo": "surtos_de_magia_selvagem",
             "filtro": {"escolhivel_no_surto_controlado": True}},
      "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                    "chave": "{{escolhido}}"}}],
    "feiticaria_selvagem")

# =========================================================== progressão da classe

PROF = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6]
PONTOS = [0] + list(range(2, 21))
PREPARADAS = [2, 4, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16, 17, 17, 18, 18, 19, 20, 21, 22]
ESPACOS = [
    [2], [3], [4, 2], [4, 3], [4, 3, 2], [4, 3, 3], [4, 3, 3, 1], [4, 3, 3, 2],
    [4, 3, 3, 3, 1], [4, 3, 3, 3, 2], [4, 3, 3, 3, 2, 1], [4, 3, 3, 3, 2, 1],
    [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 2, 1, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1, 1],
    [4, 3, 3, 3, 3, 1, 1, 1, 1], [4, 3, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 3, 2, 2, 1, 1]]
TRUQUES = {1: 4, 4: 5, 10: 6}
POR_NIVEL = {
    1: ["conjuracao_feiticeiro", "feiticaria_inata"],
    2: ["fonte_de_magia", "metamagia"],
    3: ["subclasse_de_feiticeiro"],
    4: ["aumento_no_valor_de_atributo"],
    5: ["restauracao_feiticeira"],
    6: ["caracteristica_de_subclasse"],
    7: ["feiticaria_encarnada"],
    8: ["aumento_no_valor_de_atributo"],
    10: ["metamagia"],
    12: ["aumento_no_valor_de_atributo"],
    14: ["caracteristica_de_subclasse"],
    16: ["aumento_no_valor_de_atributo"],
    17: ["metamagia"],
    18: ["caracteristica_de_subclasse"],
    19: ["dadiva_epica"],
    20: ["apoteose_arcana"],
}


def truques(n):
    v = 4
    for lim, q in sorted(TRUQUES.items()):
        if n >= lim:
            v = q
    return v


def progressao():
    saida = []
    for n in range(1, 21):
        saida.append(collections.OrderedDict([
            ("nivel", n), ("bonus_de_proficiencia", PROF[n - 1]),
            ("caracteristicas", POR_NIVEL.get(n, [])),
            ("colunas", collections.OrderedDict([
                ("pontos_de_feiticaria", PONTOS[n - 1]),
                ("truques", truques(n)),
                ("magias_preparadas", PREPARADAS[n - 1]),
                ("espacos_de_magia", ESPACOS[n - 1])]))]))
    return saida


CLASSE = collections.OrderedDict([
    ("id", "feiticeiro"), ("nome", "Feiticeiro"), ("fonte", fonte(103)), ("revisao", rev()),
    ("descricao_curta", "Conjurador de magia inata e Carisma. Gasta Pontos de Feitiçaria "
                        "para dobrar as próprias magias com Metamagia e para trocar "
                        "pontos por espaços — e espaços por pontos."),
    ("dado_de_vida", 6), ("atributo_primario", ["CAR"]),
    ("salvaguardas_primarias", ["CON", "CAR"]),
    ("nivel_subclasse", 3),
    ("niveis_de_caracteristica_de_subclasse", [3, 6, 14, 18]),
    ("conjuracao", {"atributo": "CAR", "modo": "lista_de_classe",
                    "lista_id": "feiticeiro", "preparadas_por_nivel": True}),
    ("subclasses", ["feiticaria_aberrante", "feiticaria_draconica",
                    "feiticaria_mecanica", "feiticaria_selvagem"]),
    ("proficiencias_iniciais", [
        {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "CON",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "CAR",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "arma",
         "de": {"catalogo": "itens",
                "filtro": {"categoria": "arma", "grupo": "simples"}},
         "nivel_dominio": "proficiente"},
        {"id": "feiticeiro_pericias_iniciais", "tipo": "escolha",
         "rotulo": "Escolha 2 perícias", "quantidade": 2,
         "de": {"catalogo": "pericias",
                "chaves": ["arcanismo", "enganacao", "intimidacao", "intuicao",
                           "persuasao", "religiao"]},
         "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                       "categoria": "pericia",
                                       "chave": "{{escolhido}}",
                                       "nivel_dominio": "proficiente"}},
    ]),
    ("treinamento_com_armadura", []),
    ("equipamento_inicial", {
        "opcoes": [
            {"id": "A", "itens": [
                {"item": "lanca"}, {"item": "adaga", "quantidade": 2},
                {"item": "cristal", "nota": "Foco Arcano (cristal)."},
                {"item": "kit_de_explorador_de_masmorras"}],
             "moedas": {"po": 28}},
            {"id": "B", "moedas": {"po": 50}}],
        "revisao": rev()}),
    ("progressao", progressao()),
    ("colunas_da_tabela", collections.OrderedDict([
        ("pontos_de_feiticaria", {"nome": "Pontos de Feitiçaria", "tipo": "inteiro"}),
        ("truques", {"nome": "Truques", "tipo": "inteiro"}),
        ("magias_preparadas", {"nome": "Magias Preparadas", "tipo": "inteiro"}),
        ("espacos_de_magia", {"nome": "Espaços de Magia por Círculo", "tipo": "lista"})])),
    ("multiclasse", {"proficiencias": [], "fonte": fonte(103),
                     "nota": "O bloco de multiclasse do Feiticeiro (p. 103) só manda "
                             "pegar o Dado de Ponto de Vida e as características de "
                             "nível 1; não concede proficiências novas."}),
])

SUBCLASSES = [
    ("feiticaria_aberrante", "Feitiçaria Aberrante", 109,
     "Poder psiônico de origem alienígena: telepatia, magias da mente pagas com Pontos de "
     "Feitiçaria e um corpo que se altera."),
    ("feiticaria_draconica", "Feitiçaria Dracônica", 110,
     "Herança de dragão: mais Pontos de Vida, escamas no lugar de armadura, afinidade com "
     "um elemento e asas."),
    ("feiticaria_mecanica", "Feitiçaria Mecânica", 111,
     "A ordem de Mecanos: anula Vantagem e Desvantagem alheias, protege com dados de "
     "redução de dano e enfim cura, dissipa e repara de uma vez."),
    ("feiticaria_selvagem", "Feitiçaria Selvagem", 113,
     "Caos bruto: Vantagem sob demanda ao preço de um surto, uma tabela de 1d100 e, no "
     "fim, o poder de escolher o surto."),
]

# =========================================================== catálogos novos

METAMAGIA = [
    ("magia_acelerada", "Magia Acelerada", 2,
     "Magia com tempo de conjuração de uma ação passa a custar uma Ação Bônus nesta "
     "conjuração. Não vale se já conjurou magia de 1º círculo ou superior neste turno, "
     "nem permite conjurar outra depois no mesmo turno.",
     [{"tipo": "alterar_tempo_de_conjuracao", "de": "acao", "para": "acao_bonus",
       "escopo": {"tempo_de_conjuracao": "acao"},
       "restricoes": ["nenhuma_magia_de_circulo_1_ou_superior_antes_no_turno",
                      "nenhuma_magia_de_circulo_1_ou_superior_depois_no_turno"]}]),
    ("magia_agravada", "Magia Agravada", 2,
     "Um alvo da magia tem Desvantagem nas salvaguardas contra ela.",
     [{"tipo": "vantagem", "alvo": "salvaguarda", "modo": "desvantagem",
       "beneficiario": "um_alvo_da_magia", "escopo": {"forca_salvaguarda": True},
       "duracao": "contra_esta_magia"}]),
    ("magia_buscadora", "Magia Buscadora", 1,
     "Ao errar uma jogada de ataque com magia, joga o d20 de novo e usa o novo resultado. "
     "Pode ser usada mesmo já tendo usado outra opção de Metamagia nesta conjuração.",
     [{"tipo": "rolar_novamente", "alvo": "jogada_de_ataque_magico", "gatilho": "erro",
       "usa_novo_resultado": True}],
     {"empilha_com_outra_metamagia": True}),
    ("magia_cautelosa", "Magia Cautelosa", 1,
     "Escolhe até seu modificador de Carisma criaturas (mínimo 1) entre as que a magia "
     "obriga a fazer salvaguarda: elas passam automaticamente e não sofrem dano nem "
     "quando o sucesso normalmente daria metade.",
     [{"tipo": "alterar_resultado_de_salvaguarda", "alvo": "salvaguarda",
       "beneficiario": "criaturas_escolhidas",
       "quantidade_de_alvos": [{"op": "max", "args": ["mod:CAR", "1"]}],
       "aplica_a": "salvaguarda_contra_esta_magia",
       "resultado": "sucesso_automatico", "em_sucesso": "nenhum_dano",
       "escopo": {"forca_salvaguarda": True}}]),
    ("magia_distante", "Magia Distante", 1,
     "Dobra o alcance de uma magia com alcance de pelo menos 1,5 m; ou, se o alcance for "
     "Toque, ele vira 9 metros.",
     [{"tipo": "alterar_alcance_da_magia", "operacao": "dobrar",
       "escopo": {"alcance_minimo_m": 1.5}},
      {"tipo": "alterar_alcance_da_magia", "operacao": "substituir",
       "novo_alcance_m": 9, "escopo": {"tipo_de_alcance": "toque"}}]),
    ("magia_duplicada", "Magia Duplicada", 1,
     "Aumenta em 1 o círculo efetivo de uma magia que, com espaço superior, atinge uma "
     "criatura adicional.",
     [{"tipo": "alterar_circulo_efetivo", "delta": 1,
       "escopo": {"aprimoramento_atinge_criatura_adicional": True}}]),
    ("magia_persistente", "Magia Persistente", 1,
     "Dobra a duração de uma magia de 1 minuto ou mais, até o máximo de 24 horas. Se ela "
     "exigir Concentração, você tem Vantagem nas salvaguardas para mantê-la.",
     [{"tipo": "alterar_duracao_da_magia", "operacao": "dobrar", "maximo": "24 horas",
       "escopo": {"duracao_minima_minutos": 1}},
      {"tipo": "vantagem", "alvo": "salvaguarda", "modo": "vantagem",
       "aplica_a": "manter_concentracao_desta_magia",
       "condicao": {"todas": ["magia_exige_concentracao"]}}]),
    ("magia_potencializada", "Magia Potencializada", 1,
     "Joga novamente até seu modificador de Carisma dados de dano da magia (mínimo 1) e "
     "usa os novos resultados. Pode ser usada mesmo já tendo usado outra Metamagia.",
     [{"tipo": "rolar_novamente", "alvo": "dado_de_dano_da_magia",
       "quantidade_de_dados": [{"op": "max", "args": ["mod:CAR", "1"]}],
       "usa_novo_resultado": True}],
     {"empilha_com_outra_metamagia": True}),
    ("magia_sutil", "Magia Sutil", 1,
     "Conjura sem componentes Verbais, Somáticos ou Materiais — exceto material consumido "
     "pela magia ou com custo detalhado nela.",
     [{"tipo": "dispensar_componentes", "componentes": ["V", "S", "M"],
       "excecoes": ["material_consumido", "material_com_custo"]}]),
    ("magia_transmutada", "Magia Transmutada", 1,
     "Troca o tipo de dano da magia por outro da lista: Ácido, Elétrico, Gélido, Ígneo, "
     "Trovejante ou Venenoso.",
     [{"tipo": "alterar_tipo_de_dano_da_magia",
       "opcoes": ["acido", "eletrico", "gelido", "igneo", "trovejante", "venenoso"],
       "escopo": {"tipo_de_dano_atual": ["acido", "eletrico", "gelido", "igneo",
                                         "trovejante", "venenoso"]}}]),
]

REVELACAO = [
    ("adaptacao_aquatica", "Adaptação Aquática",
     "Deslocamento de Natação igual ao dobro do seu Deslocamento e respiração "
     "subaquática; guelras crescem no pescoço ou atrás das orelhas.",
     [{"tipo": "conceder_velocidade", "tipo_deslocamento": "natacao",
       "formula": [{"op": "mult", "args": ["2", "deslocamento"]}]},
      {"tipo": "efeito_narrativo", "chave": "respirar_agua",
       "texto": "Você pode respirar debaixo d'água."}]),
    ("movimento_vermiforme", "Movimento Vermiforme",
     "O corpo e o equipamento ficam viscosos: passa por espaços de até 2,5 cm e gasta "
     "1,5 m de movimento para escapar de restrições não mágicas ou da condição Imobilizado.",
     [{"tipo": "restringir_movimento", "modo": "libera",
       "permite": "passar_por_espaco_estreito", "largura_minima_cm": 2.5},
      {"tipo": "remover_condicao", "condicao_id": "imobilizado",
       "custo_em_movimento_m": 1.5,
       "tambem_remove": ["restricoes_nao_magicas"]}]),
    ("ver_o_invisivel", "Ver o Invisível",
     "Enxerga criaturas com a condição Invisível a até 18 m que não estejam atrás de "
     "Cobertura Total.",
     [{"tipo": "conceder_sentido", "sentido": "ver_invisivel", "alcance_m": 18,
       "excecoes": ["atras_de_cobertura_total"]}]),
    ("voo_reluzente", "Voo Reluzente",
     "Deslocamento de Voo igual ao seu Deslocamento, e pode pairar.",
     [{"tipo": "conceder_velocidade", "tipo_deslocamento": "voo",
       "formula": ["deslocamento"], "pode_pairar": True}]),
]

MANIFESTACOES = [
    (1, "engrenagens_espectrais", "Engrenagens espectrais pairam atrás de você."),
    (2, "ponteiros_nos_olhos", "Os ponteiros de um relógio giram em seus olhos."),
    (3, "reflexo_acobreado", "Sua pele brilha com um reflexo acobreado."),
    (4, "equacoes_flutuantes",
     "Equações flutuantes e objetos geométricos se sobrepõem ao seu corpo."),
    (5, "foco_de_relojoaria",
     "Seu Foco de Conjuração assume temporariamente a forma de um mecanismo de relógio "
     "Minúsculo."),
    (6, "tique_taque",
     "O tique-taque das engrenagens ou o toque de um relógio podem ser ouvidos por você "
     "e por quem é afetado por sua magia."),
]

# --------------------------------------------------------- tabela do Surto (1d100)
SURTOS = [
    ((1, 4), "rolar_de_novo_a_cada_turno", "Surtos em cadeia",
     "Pelo próximo minuto, joga nesta tabela no início de cada um dos seus turnos, "
     "ignorando este resultado nas jogadas seguintes.",
     [{"tipo": "rolar_na_tabela", "catalogo": "surtos_de_magia_selvagem",
       "dado_da_tabela": "1d100", "momento": "inicio_do_seu_turno",
       "duracao": "1 minuto", "ignora_faixas": [[1, 4]]}]),
    ((5, 8), "criatura_amigavel", "Criatura amigável",
     "Uma criatura Amigável aparece num espaço desocupado aleatório a até 18 m, sob "
     "controle do Mestre, e some depois de 1 minuto (1d4: Modron Duodrone, Flunf, Modron "
     "Monodrone ou Unicórnio).",
     [{"tipo": "efeito_narrativo", "chave": "invocar_criatura_amigavel",
       "texto": "Criatura Amigável aleatória (1d4) aparece a até 18 m, controlada pelo "
                "Mestre, e desaparece depois de 1 minuto. Bloco de estatísticas no Livro "
                "dos Monstros.",
       "alcance_m": 18, "duracao": "1 minuto",
       "tabela_1d4": ["Modron Duodrone", "Flunf", "Modron Monodrone", "Unicórnio"]}]),
    ((9, 12), "cura_no_inicio_do_turno", "Cura contínua",
     "Pelo próximo minuto, recupera 5 Pontos de Vida no início de cada um dos seus turnos.",
     [{"tipo": "cura", "formula": ["5"], "momento": "inicio_do_seu_turno",
       "duracao": "1 minuto"}]),
    ((13, 16), "desvantagem_na_proxima_magia", "Salvaguardas fracas",
     "As criaturas têm Desvantagem nas salvaguardas contra a próxima magia com "
     "salvaguarda que você conjurar no minuto seguinte.",
     [{"tipo": "vantagem", "alvo": "salvaguarda", "modo": "desvantagem",
       "beneficiario": "alvos_da_proxima_magia_com_salvaguarda", "duracao": "1 minuto"}]),
    ((17, 20), "efeito_cosmetico_1d8", "Marca do caos",
     "Você fica sujeito a um efeito de 1d8 por 1 minuto (música etérea, tamanho maior, "
     "barba de plumas, fala aos gritos, borboletas ilusórias, um olho na testa com "
     "Vantagem em Sabedoria (Percepção), bolhas rosas ao falar, ou pele azul por 24 h).",
     [{"tipo": "efeito_narrativo", "chave": "efeito_do_caos_1d8",
       "texto": "Role 1d8 na lista de efeitos da linha 17–20 (p. 114). Só o resultado 6 "
                "tem efeito mecânico: Vantagem em testes de Sabedoria (Percepção).",
       "duracao": "1 minuto",
       "efeitos_possiveis": [
           {"d8": 6, "efeitos": [{"tipo": "vantagem",
                                  "alvo": "teste_de_atributo:percepcao",
                                  "modo": "vantagem", "duracao": "1 minuto"}]}]}]),
    ((21, 24), "acao_vira_acao_bonus", "Conjuração acelerada",
     "Pelo próximo minuto, todas as suas magias com tempo de conjuração de uma ação "
     "passam a custar uma Ação Bônus.",
     [{"tipo": "alterar_tempo_de_conjuracao", "de": "acao", "para": "acao_bonus",
       "escopo": {"todas_as_suas_magias": True, "tempo_de_conjuracao": "acao"},
       "duracao": "1 minuto"}]),
    ((25, 28), "plano_astral", "Desvio astral",
     "Você é transportado para o Plano Astral até o fim do seu próximo turno e depois "
     "volta ao espaço que ocupava, ou ao desocupado mais próximo.",
     [{"tipo": "efeito_narrativo", "chave": "desvio_astral",
       "texto": "Transportado para o Plano Astral até o fim do seu próximo turno; retorna "
                "ao espaço anterior ou ao desocupado mais próximo.",
       "duracao": "ate_o_fim_do_seu_proximo_turno"}]),
    ((29, 32), "dano_maximo_na_proxima_magia", "Dano máximo",
     "Na próxima magia de dano que conjurar no minuto seguinte, não joga os dados: usa o "
     "número mais alto possível em cada dado de dano.",
     [{"tipo": "dano_maximizado", "escopo": {"proxima_magia_com_dano": True},
       "duracao": "1 minuto"}]),
    ((33, 36), "resistencia_a_tudo", "Resistência total",
     "Resistência a todos os tipos de dano pelo próximo minuto.",
     [{"tipo": "alterar_dano", "tipo_dano": "todos", "operacao": "resistencia",
       "duracao": "1 minuto"}]),
    ((37, 40), "vaso_de_plantas", "Vaso de plantas",
     "Você vira um vaso de plantas até o início do seu próximo turno: fica Incapacitado e "
     "com Vulnerabilidade a todo dano. A 0 Pontos de Vida o vaso quebra e você volta ao "
     "normal.",
     [{"tipo": "conceder_condicao", "condicao_id": "incapacitado", "beneficiario": "voce",
       "duracao": "ate_o_inicio_do_seu_proximo_turno"},
      {"tipo": "alterar_dano", "tipo_dano": "todos", "operacao": "vulnerabilidade",
       "duracao": "ate_o_inicio_do_seu_proximo_turno"},
      {"tipo": "efeito_narrativo", "chave": "vaso_quebra",
       "texto": "Se chegar a 0 Pontos de Vida enquanto é planta, o vaso quebra e você "
                "reverte à forma original."}]),
    ((41, 44), "teleporte_por_turno", "Salto curto",
     "Pelo próximo minuto, pode se teleportar até 6 m como Ação Bônus em cada um dos seus "
     "turnos.",
     [{"tipo": "teleporte", "custo": "acao_bonus", "alcance_m": 6,
       "frequencia": "uma_vez_por_turno", "duracao": "1 minuto"}]),
    ((45, 48), "invisibilidade_do_grupo", "Sumiço",
     "Você e até três criaturas à sua escolha a até 9 m ficam Invisíveis por 1 minuto; a "
     "invisibilidade acaba para quem atacar, causar dano ou conjurar magia.",
     [{"tipo": "conceder_condicao", "condicao_id": "invisivel",
       "beneficiario": "voce_e_ate_3_criaturas_a_sua_escolha", "alcance_m": 9,
       "duracao": "1 minuto",
       "encerra_se": [{"gatilho": "realizar_jogada_de_ataque"}, {"gatilho": "causar_dano"},
                      {"gatilho": "conjurar_magia"}]}]),
    ((49, 52), "escudo_espectral", "Escudo espectral",
     "Um escudo espectral paira perto de você pelo próximo minuto: +2 na CA e imunidade a "
     "Mísseis Mágicos.",
     [{"tipo": "modificador", "alvo": "ca_total", "valor": ["2"], "empilha": "soma",
       "duracao": "1 minuto"},
      {"tipo": "imunidade_a_risco", "risco": "magia:misseis_magicos",
       "duracao": "1 minuto"}]),
    ((53, 56), "acao_adicional", "Impulso",
     "Você pode executar uma ação adicional neste turno.",
     [{"tipo": "acao_adicional", "frequencia": "uma_vez", "duracao": "este_turno"}]),
    ((57, 60), "magia_aleatoria", "Magia aleatória",
     "Você conjura uma magia aleatória (1d10), sem exigir Concentração — ela dura o tempo "
     "todo.",
     [{"tipo": "efeito_narrativo", "chave": "conjurar_magia_aleatoria",
       "texto": "Role 1d10 e conjure a magia correspondente; se ela exigiria "
                "Concentração, não exige neste caso e dura a duração inteira.",
       "tabela_1d10": [
           {"d10": 1, "magia": "confusao"}, {"d10": 2, "magia": "bola_de_fogo"},
           {"d10": 3, "magia": "nevoa_obscurecente"},
           {"d10": 4, "magia": "voo", "alvo": "criatura aleatória a até 18 m"},
           {"d10": 5, "magia": "graxa"},
           {"d10": 6, "magia": "levitacao", "alvo": "você"},
           {"d10": 7, "magia": "misseis_magicos", "circulo": 5},
           {"d10": 8, "magia": "reflexos"},
           {"d10": 9, "magia": "polimorfia", "alvo": "você",
            "nota": "Falhando na salvaguarda, vira uma Cabra (apêndice B)."},
           {"d10": 10, "magia": "ver_o_invisivel"}]}]),
    ((61, 64), "toque_incendiario", "Toque incendiário",
     "Pelo próximo minuto, todo objeto inflamável e não mágico que você tocar e que não "
     "esteja sendo usado ou carregado por outra criatura pega fogo, sofre 1d4 de dano "
     "Ígneo e fica em combustão.",
     [{"tipo": "dano", "formula_dado": "1d4", "tipo_dano": "igneo",
       "alvo": "objeto_inflamavel_tocado", "duracao": "1 minuto"}]),
    ((65, 68), "reencarnar_ao_morrer", "Retorno",
     "Se você morrer na próxima hora, revive imediatamente como se estivesse sob a magia "
     "Reencarnar.",
     [{"tipo": "efeito_narrativo", "chave": "reencarnar_automatico",
       "texto": "Morrendo na próxima hora, você revive imediatamente como pela magia "
                "Reencarnar.",
       "magia_de_referencia": "reencarnar", "duracao": "1 hora"}]),
    ((69, 72), "medo_subito", "Medo súbito",
     "Você fica Amedrontado até o fim do seu próximo turno; o Mestre determina a fonte do "
     "medo.",
     [{"tipo": "conceder_condicao", "condicao_id": "amedrontado", "beneficiario": "voce",
       "duracao": "ate_o_fim_do_seu_proximo_turno"}]),
    ((73, 76), "teleporte_18m", "Deslize",
     "Você se teleporta até 18 m para um espaço desocupado à sua vista.",
     [{"tipo": "teleporte", "alcance_m": 18,
       "requisitos": ["destino_desocupado", "destino_a_vista"]}]),
    ((77, 80), "veneno_aleatorio", "Veneno errante",
     "Uma criatura aleatória a até 18 m fica Envenenada por 1d4 horas.",
     [{"tipo": "conceder_condicao", "condicao_id": "envenenado",
       "beneficiario": "criatura_aleatoria", "alcance_m": 18,
       "duracao": {"formula_horas": ["1d4"]}}]),
    ((81, 84), "luz_plena_ofuscante", "Farol",
     "Você irradia Luz Plena num raio de 9 m pelo próximo minuto; quem terminar o turno a "
     "até 1,5 m de você fica Cego até o fim do próprio próximo turno.",
     [{"tipo": "efeito_narrativo", "chave": "luz_plena_9m",
       "texto": "Você irradia Luz Plena num raio de 9 metros.", "duracao": "1 minuto"},
      {"tipo": "conceder_condicao", "condicao_id": "cego",
       "beneficiario": "criatura_que_termina_o_turno_perto", "alcance_m": 1.5,
       "duracao": "ate_o_fim_do_proximo_turno_dela", "duracao_do_efeito": "1 minuto"}]),
    ((85, 88), "dreno_necrotico", "Dreno",
     "Até três criaturas à sua escolha, à vista e a até 9 m, sofrem 1d10 de dano "
     "Necrótico; você recupera Pontos de Vida iguais à soma do dano causado.",
     [{"tipo": "dano", "formula_dado": "1d10", "tipo_dano": "necrotico",
       "alvo": "ate_3_criaturas_a_sua_escolha", "alcance_m": 9},
      {"tipo": "cura", "formula": ["dano_necrotico_causado"], "beneficiario": "voce"}]),
    ((89, 92), "descarga_eletrica", "Descarga",
     "Até três criaturas à sua escolha, à vista e a até 9 m, sofrem 4d10 de dano Elétrico.",
     [{"tipo": "dano", "formula_dado": "4d10", "tipo_dano": "eletrico",
       "alvo": "ate_3_criaturas_a_sua_escolha", "alcance_m": 9}]),
    ((93, 96), "vulnerabilidade_perfurante", "Casca fina",
     "Você e todas as criaturas a até 9 m ficam com Vulnerabilidade a dano Perfurante "
     "pelo próximo minuto.",
     [{"tipo": "alterar_dano", "tipo_dano": "perfurante", "operacao": "vulnerabilidade",
       "beneficiario": "voce_e_todas_as_criaturas_ate_9m", "alcance_m": 9,
       "duracao": "1 minuto"}]),
    ((97, 100), "beneficio_aleatorio_1d6", "Dádiva do caos",
     "Role 1d6: 1) você recupera 2d10 Pontos de Vida; 2) um aliado à sua escolha a até "
     "90 m recupera 2d10; 3) você recupera seu espaço de magia gasto de menor círculo; "
     "4) um aliado a até 90 m recupera o dele; 5) você restaura todos os Pontos de "
     "Feitiçaria gastos; 6) todos os efeitos da linha 17–20 o afetam ao mesmo tempo.",
     [{"tipo": "efeito_narrativo", "chave": "dadiva_do_caos_1d6",
       "texto": "Role 1d6 na lista da linha 97–00 (p. 114) e aplique o resultado.",
       "efeitos_possiveis": [
           {"d6": 1, "efeitos": [{"tipo": "cura", "formula": ["2d10"],
                                  "beneficiario": "voce"}]},
           {"d6": 2, "efeitos": [{"tipo": "cura", "formula": ["2d10"],
                                  "beneficiario": "aliado_a_sua_escolha",
                                  "alcance_m": 90}]},
           {"d6": 3, "efeitos": [{"tipo": "recuperar_espacos_de_magia",
                                  "quantidade": 1, "circulo": "menor_gasto",
                                  "beneficiario": "voce"}]},
           {"d6": 4, "efeitos": [{"tipo": "recuperar_espacos_de_magia",
                                  "quantidade": 1, "circulo": "menor_gasto",
                                  "beneficiario": "aliado_a_sua_escolha",
                                  "alcance_m": 90}]},
           {"d6": 5, "efeitos": [{"tipo": "restaurar_recurso", "recurso_id": PF,
                                  "quantidade": "total"}]},
           {"d6": 6, "efeitos": [{"tipo": "aplicar_efeito_nomeado",
                                  "chave": "efeito_cosmetico_1d8",
                                  "modo": "todos_simultaneamente"}]}]}],
     False),
]


def catalogo(cid, nome, pag, nota, itens, **extra):
    d = collections.OrderedDict([
        ("catalogo", cid), ("nome", nome), ("fonte", fonte(pag)), ("nota", nota),
        ("total", len(itens)), ("itens", itens)])
    d.update(extra)
    return d


def montar_metamagia():
    itens = []
    for entrada in METAMAGIA:
        cid, nome, custo, desc, efeitos = entrada[:5]
        extra = entrada[5] if len(entrada) > 5 else {}
        it = collections.OrderedDict([
            ("id", cid), ("nome", nome),
            ("custo_em_pontos_de_feiticaria", custo),
            ("descricao_curta", desc),
            ("momento", "ao_conjurar"),
            ("efeitos", efeitos)])
        it.update(extra)
        itens.append(it)
    return catalogo("opcoes_de_metamagia", "Opções de Metamagia", 105,
                    "Toda opção é aplicada NO ATO DE CONJURAR e consome Pontos de "
                    "Feitiçaria. Só uma por magia, salvo as que declaram "
                    "empilha_com_outra_metamagia (Buscadora e Potencializada) — e salvo "
                    "Feitiçaria Encarnada, que sobe o teto para duas.",
                    itens, recurso="pontos_de_feiticaria")


def montar_revelacao():
    itens = [collections.OrderedDict([
        ("id", cid), ("nome", nome), ("custo_em_pontos_de_feiticaria", 1),
        ("descricao_curta", desc), ("duracao", "10 minutos"), ("efeitos", efeitos)])
        for cid, nome, desc, efeitos in REVELACAO]
    return catalogo("alteracoes_da_revelacao_em_carne",
                    "Alterações da Revelação em Carne", 110,
                    "Cada Ponto de Feitiçaria gasto compra uma destas alterações; podem "
                    "ser combinadas na mesma ativação.", itens,
                    recurso="pontos_de_feiticaria")


def montar_manifestacoes():
    itens = [collections.OrderedDict([
        ("id", cid), ("nome", texto.split('.')[0]), ("resultado_1d6", n),
        ("descricao_curta", texto)]) for n, cid, texto in MANIFESTACOES]
    return catalogo("manifestacoes_da_ordem", "Manifestações da Ordem", 111,
                    "Tabela puramente descritiva (1d6): diz como a conexão com a ordem "
                    "aparece quando o Feiticeiro Mecânico conjura. Não tem efeito "
                    "mecânico — por isso é catálogo de vocabulário.", itens)


def montar_surtos():
    itens = []
    for entrada in SURTOS:
        faixa, cid, nome, desc, efeitos = entrada[:5]
        escolhivel = entrada[5] if len(entrada) > 5 else True
        itens.append(collections.OrderedDict([
            ("id", cid), ("nome", nome),
            ("faixa_1d100", {"min": faixa[0], "max": faixa[1]}),
            ("descricao_curta", desc),
            ("escolhivel_no_surto_controlado", escolhivel),
            ("efeitos", efeitos)]))
    return catalogo("surtos_de_magia_selvagem", "Surto de Magia Selvagem", 114,
                    "Tabela de 1d100 do Feiticeiro Selvagem. É catálogo de OPÇÃO, não de "
                    "vocabulário, porque no nível 18 (Surto Controlado) o jogador ESCOLHE "
                    "a linha em vez de rolar — menos a última, marcada com "
                    "escolhivel_no_surto_controlado: false. As linhas que dependem de "
                    "decisão do Mestre ou de subtabelas aleatórias trazem o efeito "
                    "mecânico quando existe e efeito_narrativo quando o livro deixa a "
                    "resolução para a mesa.",
                    itens, dado_da_tabela="1d100",
                    cobertura_da_faixa={"min": 1, "max": 100})


# ------------------------------------------------------------------ alvos e tipos

ALVOS_NOVOS = [
    ("cd_para_evitar_sua_magia", "CD para evitar suas magias",
     "O valor que as criaturas precisam alcançar na salvaguarda contra suas magias. "
     "Alvo de modificador, por exemplo, na Feitiçaria Inata do Feiticeiro."),
    ("jogada_de_ataque_magico", "Jogada de ataque mágico",
     "A jogada de ataque de uma magia, distinta da jogada de ataque com arma."),
    ("pontos_de_vida_maximos", "Pontos de Vida máximos",
     "O teto de Pontos de Vida da ficha. Alvo de modificador, por exemplo, na "
     "Resiliência Dracônica."),
    ("custo_de_metamagia", "Custo em Pontos de Feitiçaria de uma opção de Metamagia",
     "Alvo de modificador da Apoteose Arcana (p. 105), que zera o custo de uma opção "
     "por turno."),
    ("rolagem_na_tabela", "Rolagem numa tabela aleatória",
     "A jogada que escolhe a linha de uma tabela (o 1d100 do Surto de Magia Selvagem, "
     "p. 113). Alvo do Caos Controlado, que joga duas vezes."),
    ("dado_de_dano_da_magia", "Dado de dano de uma magia",
     "Os dados de dano de uma magia já conjurada, distintos dos dados de dano de arma. "
     "Alvo da Magia Potencializada (p. 106)."),
]

IMPEDIMENTOS_NOVOS = [
    ("vantagem_ou_desvantagem_em_teste_d20",
     "Beneficiar-se de Vantagem ou Desvantagem num Teste de D20",
     "Usado pelo Restaurar Equilíbrio do Feiticeiro Mecânico (nível 3, p. 111): a "
     "Reação faz o teste deixar de ser afetado por Vantagem e por Desvantagem."),
]

TIPOS_NOVOS = [
    ("alterar_tempo_de_conjuracao", "Alterar o tempo de conjuração de uma magia",
     "Muda o tempo de conjuração de uma magia no ato de conjurar (Magia Acelerada, "
     "p. 105). Traz 'de', 'para', o escopo e as restrições do turno."),
    ("alterar_alcance_da_magia", "Alterar o alcance de uma magia",
     "Dobra ou substitui o alcance de uma magia no ato de conjurar (Magia Distante, "
     "p. 106)."),
    ("alterar_duracao_da_magia", "Alterar a duração de uma magia",
     "Multiplica a duração de uma magia até um teto no ato de conjurar (Magia "
     "Persistente, p. 106)."),
    ("alterar_circulo_efetivo", "Alterar o círculo efetivo de uma magia",
     "Soma ao círculo que a magia conta como para efeito de aprimoramento, sem gastar um "
     "espaço maior (Magia Duplicada, p. 106)."),
    ("dispensar_concentracao", "Dispensar a Concentração de uma magia",
     "Retira a exigência de Concentração de uma magia, opcionalmente trocando a duração "
     "(Companheiro Dracônico, p. 110)."),
    ("dissipar_magias", "Encerrar magias em alvos escolhidos",
     "Encerra magias até um círculo máximo em alvos escolhidos, sem teste (Cavalgada "
     "Mecânica, p. 112)."),
    ("rolar_na_tabela", "Rolar numa tabela aleatória de catálogo",
     "Rola numa tabela aleatória de um catálogo e aplica os efeitos da linha sorteada "
     "(Surto de Magia Selvagem, p. 113)."),
    ("movimento_forcado", "Empurrar ou puxar uma criatura",
     "Empurra ou puxa uma criatura uma distância dada, sem que ela gaste movimento. "
     "Antes isto era escrito como efeito_narrativo em cada característica."),
]

SENTIDOS_NOVOS = [
    ("ver_invisivel", "Ver o Invisível",
     "Enxerga criaturas com a condição Invisível dentro do alcance indicado."),
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
    for cat in (montar_metamagia(), montar_revelacao(), montar_manifestacoes(),
                montar_surtos()):
        with open(f"{CAT}/{cat['catalogo']}.json", 'w', encoding='utf-8') as f:
            json.dump(cat, f, ensure_ascii=False, indent=2)

    n_alvos = juntar(f'{CAT}/alvos.json', ALVOS_NOVOS,
                     ['id', 'nome', 'descricao_curta'])
    n_tipos = juntar(f'{CAT}/tipos_de_efeito.json', TIPOS_NOVOS,
                     ['id', 'nome', 'descricao_curta'])
    n_sent = juntar(f'{CAT}/sentidos.json', SENTIDOS_NOVOS,
                    ['id', 'nome', 'descricao_curta'])
    n_imp = juntar(f'{CAT}/alvos_de_impedimento.json', IMPEDIMENTOS_NOVOS,
                   ['id', 'nome', 'nota'])

    cl = json.load(open('dados/classes.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    cl['itens'] = [c for c in cl['itens'] if c['id'] != 'feiticeiro'] + [CLASSE]
    cl['total'] = len(cl['itens'])
    json.dump(cl, open('dados/classes.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    sc = json.load(open('dados/subclasses.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    sc['itens'] = [s for s in sc['itens'] if s.get('classe') != 'feiticeiro']
    for sid, nome, pag, desc in SUBCLASSES:
        sc['itens'].append(collections.OrderedDict([
            ("id", sid), ("nome", nome), ("classe", "feiticeiro"),
            ("fonte", fonte(pag)), ("revisao", rev()),
            ("descricao_curta", desc),
            ("niveis_de_caracteristica", [3, 6, 14, 18]),
            ("caracteristicas", [c['id'] for c in CARACS
                                 if c.get('subclasse') == sid])]))
    sc['total'] = len(sc['itens'])
    json.dump(sc, open('dados/subclasses.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    ca = json.load(open('dados/caracteristicas.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    ca['itens'] = [c for c in ca['itens'] if c.get('classe') != 'feiticeiro'] + CARACS
    ca['total'] = len(ca['itens'])
    json.dump(ca, open('dados/caracteristicas.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    print(f"feiticeiro: {len(CARACS)} características | {len(SUBCLASSES)} subclasses")
    print(f"catálogos novos: opcoes_de_metamagia ({len(METAMAGIA)}), "
          f"alteracoes_da_revelacao_em_carne ({len(REVELACAO)}), "
          f"manifestacoes_da_ordem ({len(MANIFESTACOES)}), "
          f"surtos_de_magia_selvagem ({len(SURTOS)})")
    print(f"alvos novos: {n_alvos} | tipos de efeito novos: {n_tipos} | "
          f"sentidos novos: {n_sent} | alvos de impedimento novos: {n_imp}")
    print(f"classes: {cl['total']} | subclasses: {sc['total']} | "
          f"características: {ca['total']}")


if __name__ == '__main__':
    main()
