# -*- coding: utf-8 -*-
"""Capítulo 5 — Talentos (p. 199-211). 75 talentos, as quatro categorias.

Fecha as quatro pendências (`pendente: true`) que as classes já apontavam:
Aumento no Valor de Atributo, Dádiva Épica, Dádiva da Proeza em Combate e
Dádiva do Ataque Irresistível.

Duas coisas que este capítulo obrigou a arrumar no esquema:

1. **O aumento de atributo dentro do talento.** Quase todo talento Geral traz um
   "Aumente seu valor de X ou Y em 1, até no máximo 20". Isso é uma ESCOLHA
   entre atributos, não um número fixo — modelada como `escolha` sobre o
   catálogo de atributos, com o teto declarado (20 nos Gerais, 30 nas Dádivas
   Épicas). Nada de texto.

2. **"Trate qualquer 1 num dado de dano como 2".** O Combate com Armas Grandes
   já tinha essa regra e estava como `efeito_narrativo` — texto que o backend
   teria de ler. O Adepto Elemental pede a mesma coisa. Virou
   `tratar_dado_de_dano_minimo`, e o talento antigo foi migrado.
"""
import json, collections

CAT = 'dados/catalogos'
P = {}  # id -> pagina_livro, preenchido abaixo


def fonte(pag):
    return {"capitulo": 5, "pagina_livro": pag, "pagina_pdf": pag + 4}


TALENTOS = []


def t(tid, nome, categoria, pag, desc, efeitos, pre=None, repetivel=False, **extra):
    d = collections.OrderedDict([
        ("id", tid), ("nome", nome), ("categoria", categoria),
        ("pre_requisitos", pre or []), ("repetivel", repetivel),
        ("descricao_curta", desc), ("efeitos", efeitos), ("fonte", fonte(pag))])
    d.update(extra)
    TALENTOS.append(d)
    return d


# pré-requisitos padrão
NV4 = [{"tipo": "nivel_de_personagem", "minimo": 4}]
NV19 = [{"tipo": "nivel_de_personagem", "minimo": 19}]


def nv4_e(*outros):
    return NV4 + list(outros)


def atributo_min(atributos, valor=13):
    return {"tipo": "valor_de_atributo", "atributos": list(atributos), "minimo": valor}


CONJURACAO = {"tipo": "caracteristica",
              "alguma": ["conjuracao", "magia_de_pacto"],
              "nota": "Característica Conjuração ou Magia de Pacto."}


def asi(atributos, teto=20, quantidade=1, rotulo=None):
    """O 'Aumento no Valor de Atributo' embutido em quase todo talento Geral.

    É escolha entre atributos, com teto declarado — não um bônus fixo.
    `atributos=None` significa qualquer um."""
    de = ({"catalogo": "atributos", "todo_o_catalogo": True} if atributos is None
          else {"catalogo": "atributos", "chaves": list(atributos)})
    return {"tipo": "escolha",
            "rotulo": rotulo or "Escolha o atributo a aumentar",
            "quantidade": quantidade, "momento": "ao_adquirir_o_talento",
            "de": de,
            "efeito_por_item_escolhido": {
                "tipo": "aumento_atributo", "atributo": "{{escolhido}}",
                "valor": 1, "limite": teto}}


# ============================================================ Talentos de Origem

t("alerta", "Alerta", "origem", 200,
  "Soma o Bônus de Proficiência na Iniciativa e, logo depois de jogá-la, pode trocar sua "
  "Iniciativa com a de um aliado voluntário — nenhum dos dois pode estar Incapacitado.",
  [{"tipo": "modificador", "alvo": "iniciativa", "valor": ["prof"], "empilha": "soma"},
   {"tipo": "trocar_iniciativa", "com": "aliado_voluntario_no_combate",
    "momento": "imediatamente_apos_jogar_iniciativa",
    "condicao": {"todas": [{"nao": "condicao:incapacitado"},
                           {"nao": "aliado_com_condicao:incapacitado"}]}}])

FABRICACAO_RAPIDA = [
    ("ferramentas_de_carpinteiro", ["escada", "tocha"]),
    ("ferramentas_de_coureiro", ["algibeira", "estojo"]),
    ("ferramentas_de_entalhador", ["cajado", "clava", "clava_grande"]),
    ("ferramentas_de_ferreiro", ["arpeu", "balde", "esferas_de_metal", "estrepes",
                                 "panela_de_ferro"]),
    ("ferramentas_de_funileiro", ["pederneira", "pa", "sino"]),
    ("ferramentas_de_oleiro", ["jarro", "lampada"]),
    ("ferramentas_de_pedreiro", ["roldana_e_polias"]),
    ("ferramentas_de_tecelao", ["cesta", "corda", "rede", "tenda"]),
]

t("artifista", "Artifista", "origem", 200,
  "Proficiência com três Ferramentas de Artesão à escolha na tabela Fabricação Rápida, "
  "20% de desconto em item não mágico, e no Descanso Longo fabrica uma peça da tabela — "
  "que se desfaz no Descanso Longo seguinte.",
  [{"id": "artifista_ferramentas", "tipo": "escolha",
    "rotulo": "Escolha 3 Ferramentas de Artesão", "quantidade": 3,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "ferramentas",
           "chaves": [f for f, _ in FABRICACAO_RAPIDA]},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                  "categoria": "ferramenta", "chave": "{{escolhido}}",
                                  "nivel_dominio": "proficiente"}},
   {"tipo": "desconto_em_compra", "percentual": 20,
    "escopo": {"apenas_itens_nao_magicos": True}},
   {"tipo": "fabricar_item", "gatilho": "descanso_longo", "quantidade": 1,
    "requer_proficiencia_na_ferramenta": True,
    "duracao": "ate_o_proximo_descanso_longo",
    "tabela": {"nome": "Fabricação Rápida", "fonte": fonte(201),
               "linhas": [{"ferramenta": f, "itens": itens}
                          for f, itens in FABRICACAO_RAPIDA]}}])

t("atacante_selvagem", "Atacante Selvagem", "origem", 201,
  "Uma vez por turno, ao atingir com uma arma, joga os dados de dano da arma duas vezes e "
  "usa a jogada que quiser.",
  [{"tipo": "rolar_novamente", "alvo": "dado_de_dano_da_arma",
    "frequencia": "uma_vez_por_turno", "gatilho": "acerto_com_arma",
    "usa_novo_resultado": False, "escolhe_entre_os_resultados": True}])

t("curandeiro", "Curandeiro", "origem", 201,
  "Com Kit de Curandeiro, gasta um uso como ação Usar Objeto para uma criatura a até "
  "1,5 m gastar um Dado de Vida: ela recupera a jogada mais seu Bônus de Proficiência. E "
  "todo dado de cura seu que sair 1 é rejogado.",
  [{"tipo": "cura", "custo": "acao", "acao_id": "usar_objeto",
    "formula": ["dado_de_vida_do_alvo", "prof"],
    "beneficiario": "criatura_a_ate_1_5m", "alcance_m": 1.5,
    "requisitos": ["item:kit_de_curandeiro"], "consome": {"item": "kit_de_curandeiro",
                                                          "usos": 1},
    "gasta_dado_de_vida_do_alvo": 1},
   {"tipo": "rolar_novamente", "alvo": "dado_de_cura", "gatilho": "resultado_1",
    "usa_novo_resultado": True,
    "escopo": {"origem": ["magia", "talento:curandeiro"]}}])

t("habilidoso", "Habilidoso", "origem", 201,
  "Proficiência em três perícias ou ferramentas à sua escolha.",
  [{"id": "habilidoso_escolha", "tipo": "escolha",
    "rotulo": "Escolha 3 perícias ou ferramentas", "quantidade": 3,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "pericias", "todo_o_catalogo": True,
           "tambem_de": [{"catalogo": "ferramentas", "todo_o_catalogo": True}]},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                  "categoria": "pericia_ou_ferramenta",
                                  "chave": "{{escolhido}}",
                                  "nivel_dominio": "proficiente"}}],
  repetivel=True)

t("musico", "Músico", "origem", 201,
  "Proficiência com três Instrumentos Musicais e, num Descanso Curto ou Longo, toca para "
  "dar Inspiração Heroica a tantos aliados quanto seu Bônus de Proficiência.",
  [{"id": "musico_instrumentos", "tipo": "escolha",
    "rotulo": "Escolha 3 Instrumentos Musicais", "quantidade": 3,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "ferramentas", "chaves": ["instrumento_musical"],
           "de_variantes": True,
           "nota": "As dez variantes estão declaradas na entrada de Instrumento Musical "
                   "(cap. 6, p. 221)."},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                  "categoria": "ferramenta",
                                  "chave": "instrumento_musical",
                                  "variante": "{{escolhido}}",
                                  "nivel_dominio": "proficiente"}},
   {"tipo": "conceder_inspiracao_heroica",
    "beneficiario": "aliados_que_ouvem", "quantidade_de_alvos": ["prof"],
    "gatilho": ["descanso_curto", "descanso_longo"],
    "requisitos": ["proficiente_no_instrumento_tocado"]}])

t("sortudo", "Sortudo", "origem", 201,
  "Pontos de Sorte iguais ao Bônus de Proficiência, recuperados no Descanso Longo. Gasta "
  "1 para ter Vantagem num Teste de D20 seu, ou para impor Desvantagem num ataque contra "
  "você.",
  [{"tipo": "recurso_com_recarga", "id": "pontos_de_sorte", "nome": "Pontos de Sorte",
    "formula_maximo": ["prof"], "recarga": ["descanso_longo"], "consumo": "por_ponto"},
   {"tipo": "vantagem", "alvo": "teste_d20", "modo": "vantagem",
    "custo_em_recurso": {"recurso_id": "pontos_de_sorte", "quantidade": 1},
    "momento": "ao_jogar_o_d20"},
   {"tipo": "vantagem", "alvo": "jogada_de_ataque_contra_voce", "modo": "desvantagem",
    "custo_em_recurso": {"recurso_id": "pontos_de_sorte", "quantidade": 1},
    "momento": "ao_atacante_jogar_o_d20"}])

t("valentao_de_taverna", "Valentão de Taverna", "origem", 202,
  "Ataque Desarmado pode causar 1d4 + modificador de Força de dano Contundente, com "
  "rejogada de qualquer 1; proficiência com armas improvisadas; e uma vez por turno, ao "
  "atingir com Ataque Desarmado na ação Atacar, empurra o alvo 1,5 m.",
  [{"tipo": "dado_de_dano", "escopo": ["ataque_desarmado"], "formula_dado": "1d4",
    "somar": ["mod:FOR"], "tipo_dano": "contundente",
    "modo": "substitui_a_criterio_do_jogador"},
   {"tipo": "rolar_novamente", "alvo": "dado_de_dano_do_ataque_desarmado",
    "gatilho": "resultado_1", "usa_novo_resultado": True},
   {"tipo": "conceder_proficiencia", "categoria": "arma",
    "chave": "arma_improvisada", "nivel_dominio": "proficiente"},
   {"tipo": "movimento_forcado", "direcao": "empurrar", "distancia_m": 1.5,
    "origem": "voce", "alvo": "alvo_do_ataque_desarmado",
    "frequencia": "uma_vez_por_turno",
    "condicao": {"todas": ["acerto_com_ataque_desarmado", "na_acao_atacar", "seu_turno"]}}])

t("vigoroso", "Vigoroso", "origem", 202,
  "Pontos de Vida máximos aumentam no dobro do seu nível de personagem ao pegar o "
  "talento, e mais 2 a cada nível ganho depois disso.",
  [{"tipo": "modificador", "alvo": "pontos_de_vida_maximos",
    "valor": [{"op": "mult", "args": ["2", "nivel_do_personagem"]}],
    "empilha": "soma",
    "nota": "O livro diz 'o dobro do nível ao adquirir, +2 por nível depois'. Como os "
            "dois passos dão 2 por nível, o total é sempre 2 × nível do personagem. "
            "Guardado como a conta fechada, com a origem anotada."}])

# ============================================================= Talentos Gerais

t("adepto_elemental", "Adepto Elemental", "geral", 202,
  "Escolhe um tipo de dano entre Ácido, Elétrico, Gélido, Ígneo ou Trovejante: suas "
  "magias ignoram Resistência a ele, e qualquer 1 num dado de dano desse tipo vira 2.",
  [asi(["INT", "SAB", "CAR"]),
   {"id": "adepto_elemental_tipo", "tipo": "escolha",
    "rotulo": "Escolha o tipo de dano do Domínio Elemental", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "tipos_de_dano",
           "chaves": ["acido", "eletrico", "gelido", "igneo", "trovejante"]},
    "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                  "chave": "{{escolhido}}"}}],
  pre=nv4_e(CONJURACAO), repetivel=True,
  nota_repeticao="Cada repetição escolhe um tipo de dano diferente.",
  efeitos_nomeados={
      d: {"efeitos": [
          {"tipo": "ignorar_resistencia", "tipo_dano": d,
           "escopo": {"origem": "magia"}},
          {"tipo": "tratar_dado_de_dano_minimo", "resultado_ate": 1, "vira": 2,
           "escopo": {"origem": "magia", "tipo_de_dano": d}}]}
      for d in ("acido", "eletrico", "gelido", "igneo", "trovejante")})

t("agressor", "Agressor", "geral", 202,
  "Na ação Correr, o Deslocamento aumenta 3 m. E movendo-se 3 m em linha reta até o alvo "
  "antes de acertá-lo corpo a corpo na ação Atacar, escolhe +1d8 no dano ou empurrar o "
  "alvo 3 m — uma vez por turno.",
  [asi(["FOR", "DES"]),
   {"tipo": "modificador", "alvo": "deslocamento", "valor": ["3"], "empilha": "soma",
    "condicao": {"todas": ["acao:correr"]}, "duracao": "esta_acao"},
   {"id": "agressor_investida", "tipo": "escolha",
    "rotulo": "Escolha o efeito do Ataque em Investida", "quantidade": 1,
    "momento": "no_acerto", "reescolhivel": True, "reescolha_em": "cada_uso",
    "frequencia": "uma_vez_por_turno",
    "condicao": {"todas": ["moveu_3m_em_linha_reta_ate_o_alvo", "na_acao_atacar",
                           "acerto_corpo_a_corpo"]},
    "de": {"catalogo": "efeitos_do_ataque_em_investida", "todo_o_catalogo": True},
    "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                  "chave": "{{escolhido}}"}}],
  pre=nv4_e(atributo_min(["FOR", "DES"])))

t("analitico", "Analítico", "geral", 202,
  "Proficiência (ou Especialização, se já proficiente) em Intuição, Investigação ou "
  "Percepção à escolha, e a ação Procurar passa a caber numa Ação Bônus.",
  [asi(["INT", "SAB"]),
   {"id": "analitico_pericia", "tipo": "escolha",
    "rotulo": "Escolha a perícia do Observador Atento", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "pericias", "chaves": ["intuicao", "investigacao", "percepcao"]},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                  "categoria": "pericia", "chave": "{{escolhido}}",
                                  "nivel_dominio": "proficiente_ou_especializacao",
                                  "nota": "Se ainda não é proficiente, vira proficiente; "
                                          "se já é, vira Especialização."}},
   {"tipo": "alterar_custo_de_acao", "acao_id": "procurar", "novo_custo": "acao_bonus"}],
  pre=nv4_e(atributo_min(["INT", "SAB"])))

t("atirador_arcano", "Atirador Arcano", "geral", 202,
  "Ataques com magia ignoram Cobertura Parcial e de Três Quartos, estar a 1,5 m de um "
  "inimigo não dá Desvantagem neles, e magia de ataque com alcance de pelo menos 3 m pode "
  "ter o alcance aumentado em 18 m.",
  [asi(["INT", "SAB", "CAR"]),
   {"tipo": "ignorar_cobertura", "graus": ["parcial", "tres_quartos"],
    "escopo": {"jogada": "jogada_de_ataque_magico"}},
   {"tipo": "impedir", "alvo": "desvantagem_por_inimigo_adjacente",
    "escopo": {"jogada": "jogada_de_ataque_magico"}},
   {"tipo": "alterar_alcance_da_magia", "operacao": "somar", "metros": 18,
    "escopo": {"alcance_minimo_m": 3, "exige_jogada_de_ataque": True}}],
  pre=nv4_e(CONJURACAO))

t("atleta", "Atleta", "geral", 202,
  "Deslocamento de Escalada igual ao seu Deslocamento; levanta-se de Caído com 1,5 m de "
  "movimento; e faz Salto em Distância ou em Altura com corrida de apenas 1,5 m.",
  [asi(["FOR", "DES"]),
   {"tipo": "conceder_velocidade", "tipo_deslocamento": "escalada",
    "formula": ["deslocamento"]},
   {"tipo": "efeito_narrativo", "chave": "levantar_barato",
    "texto": "Levantar-se da condição Caído custa apenas 1,5 metro de movimento."},
   {"tipo": "efeito_narrativo", "chave": "salto_com_corrida_curta",
    "texto": "Salto em Distância ou em Altura correndo exige apenas 1,5 metro de "
             "movimento antes."}],
  pre=nv4_e(atributo_min(["FOR", "DES"])))

t("ator", "Ator", "geral", 203,
  "Disfarçado de alguém real ou fictício, tem Vantagem em testes de Carisma (Atuação ou "
  "Enganação) para convencer que é essa pessoa; e imita sons e vozes, com CD 8 + "
  "modificador de Carisma + Bônus de Proficiência para o ouvinte perceber.",
  [asi(["CAR"]),
   {"tipo": "vantagem", "alvo": "teste_de_atributo:atuacao", "modo": "vantagem",
    "condicao": {"todas": ["disfarcado_como_pessoa_especifica"]}},
   {"tipo": "vantagem", "alvo": "teste_de_atributo:enganacao", "modo": "vantagem",
    "condicao": {"todas": ["disfarcado_como_pessoa_especifica"]}},
   {"tipo": "efeito_narrativo", "chave": "mimetismo",
    "texto": "Imita sons de outras criaturas, inclusive a fala. Quem ouve precisa passar "
             "num teste de Sabedoria (Intuição) para perceber que é falso.",
    "cd": ["8", "mod:CAR", "prof"]}],
  pre=nv4_e(atributo_min(["CAR"])))

t("aumento_no_valor_de_atributo", "Aumento no Valor de Atributo", "geral", 203,
  "Aumenta um valor de atributo em 2, ou dois valores em 1 cada. Nenhum passa de 20.",
  [{"id": "avatributo_modo", "tipo": "escolha",
    "rotulo": "Como distribuir o aumento", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "modos_de_aumento_de_atributo", "todo_o_catalogo": True},
    "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                  "chave": "{{escolhido}}"}}],
  pre=NV4, repetivel=True,
  efeitos_nomeados={
      "um_atributo_em_2": {"efeitos": [
          {"tipo": "escolha", "id": "avatributo_um", "quantidade": 1,
           "rotulo": "Escolha o atributo a aumentar em 2",
           "de": {"catalogo": "atributos", "todo_o_catalogo": True},
           "efeito_por_item_escolhido": {"tipo": "aumento_atributo",
                                         "atributo": "{{escolhido}}", "valor": 2,
                                         "limite": 20}}]},
      "dois_atributos_em_1": {"efeitos": [
          {"tipo": "escolha", "id": "avatributo_dois", "quantidade": 2,
           "rotulo": "Escolha 2 atributos para aumentar em 1 cada",
           "de": {"catalogo": "atributos", "todo_o_catalogo": True},
           "efeito_por_item_escolhido": {"tipo": "aumento_atributo",
                                         "atributo": "{{escolhido}}", "valor": 1,
                                         "limite": 20}}]}})

t("chef", "Chef", "geral", 203,
  "Proficiência com Utensílios de Cozinheiro. No Descanso Curto cozinha para 4 + Bônus de "
  "Proficiência criaturas: quem gastar Dado de Vida recupera 1d8 a mais. E faz "
  "guloseimas — tantas quanto o Bônus de Proficiência, válidas 8 horas — que dão PV "
  "temporários iguais ao Bônus de Proficiência com uma Ação Bônus.",
  [asi(["CON", "SAB"]),
   {"tipo": "conceder_proficiencia", "categoria": "ferramenta",
    "chave": "utensilios_de_cozinheiro", "nivel_dominio": "proficiente"},
   {"tipo": "cura", "formula": ["1d8"], "modo": "adicional_ao_dado_de_vida",
    "gatilho": "descanso_curto", "beneficiario": "criaturas_que_comem",
    "quantidade_de_alvos": [{"op": "soma", "args": ["4", "prof"]}],
    "requisitos": ["ferramenta:utensilios_de_cozinheiro", "ingredientes"]},
   {"tipo": "fabricar_item", "item": "guloseima_revigorante",
    "quantidade": ["prof"], "gatilho": ["descanso_longo", "1 hora de trabalho"],
    "duracao": "8 horas",
    "requisitos": ["ferramenta:utensilios_de_cozinheiro", "ingredientes"],
    "efeitos_ao_consumir": [
        {"tipo": "pontos_de_vida_temporarios", "formula": ["prof"],
         "custo": "acao_bonus", "beneficiario": "quem_come"}]}],
  pre=NV4)

t("combatente_montado", "Combatente Montado", "geral", 203,
  "Montado: Vantagem contra criatura desmontada a até 1,5 m da montaria e menor que ela; "
  "a montaria passa a não sofrer dano quando passa numa salvaguarda de Destreza por "
  "metade do dano, e metade se falhar; e pode redirecionar para si um ataque que a acerte.",
  [asi(["FOR", "DES", "SAB"]),
   {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "vantagem",
    "condicao": {"todas": ["montado", "alvo_desmontado",
                           "alvo_a_ate_1_5m_da_montaria",
                           "alvo_menor_que_a_montaria"]}},
   {"tipo": "alterar_resultado_de_salvaguarda", "alvo": "salvaguarda:DES",
    "beneficiario": "sua_montaria", "aplica_a": "efeito_com_metade_do_dano",
    "em_sucesso": "nenhum_dano", "em_falha": "metade_do_dano",
    "condicao": {"todas": ["montado", {"nao": "condicao:incapacitado"},
                           {"nao": "montaria_com_condicao:incapacitado"}]}},
   {"tipo": "redirecionar_ataque", "de": "sua_montaria", "para": "voce",
    "custo": "livre",
    "condicao": {"todas": ["montado", {"nao": "condicao:incapacitado"}]}}],
  pre=NV4)

t("conjurador_belico", "Conjurador Bélico", "geral", 203,
  "Vantagem nas salvaguardas de Constituição para manter Concentração; troca o Ataque de "
  "Oportunidade por uma magia de uma ação que só tenha aquela criatura como alvo; e faz "
  "componentes Somáticos com armas ou Escudo nas mãos.",
  [asi(["INT", "SAB", "CAR"]),
   {"tipo": "vantagem", "alvo": "salvaguarda", "modo": "vantagem",
    "aplica_a": "manter_concentracao"},
   {"tipo": "substituir_ataque_por_magia", "escopo": "ataque_de_oportunidade",
    "custo": "reacao",
    "restricoes": ["magia_com_tempo_de_conjuracao_de_uma_acao",
                   "magia_com_alvo_unico_na_criatura_que_provocou"]},
   {"tipo": "efeito_narrativo", "chave": "somaticos_com_maos_ocupadas",
    "texto": "Executa componentes Somáticos mesmo com armas ou Escudo em uma ou nas duas "
             "mãos."}],
  pre=nv4_e(CONJURACAO))

t("conjurador_ritualista", "Conjurador Ritualista", "geral", 203,
  "Tem sempre preparadas tantas magias de 1º círculo com marcador Ritual quanto seu Bônus "
  "de Proficiência, conjuráveis com qualquer espaço; ganha mais uma a cada aumento do "
  "Bônus. E uma vez por Descanso Longo conjura um Ritual preparado no tempo normal, sem "
  "espaço de magia.",
  [asi(["INT", "SAB", "CAR"]),
   {"id": "ritualista_magias", "tipo": "escolha",
    "rotulo": "Escolha magias de 1º círculo com o marcador Ritual",
    "quantidade": ["prof"], "reescolhivel": False,
    "quantidade_cresce_com": "bonus_de_proficiencia",
    "de": {"catalogo": "magias", "filtro": {"nivel": 1, "ritual": True}},
    "efeito_por_item_escolhido": {"tipo": "preparar_magias", "magia": "{{escolhido}}",
                                  "fonte_das_magias": "conhecidas",
                                  "modo": "sempre_preparada",
                                  "nao_conta_para_o_limite": True}},
   {"tipo": "recurso_com_recarga", "id": "ritual_rapido", "formula_maximo": ["1"],
    "recarga": ["descanso_longo"], "consumo": "por_uso"},
   {"tipo": "conjurar_como_ritual", "modo": "tempo_normal_sem_espaco",
    "consome_recurso": "ritual_rapido",
    "escopo": {"apenas_rituais_preparados": True}}],
  pre=nv4_e(atributo_min(["INT", "SAB", "CAR"])))

t("duelista_defensivo", "Duelista Defensivo", "geral", 204,
  "Segurando arma de Acuidade, ao ser acertado corpo a corpo pode gastar a Reação e somar "
  "o Bônus de Proficiência à CA — inclusive contra o ataque que disparou — até o início do "
  "seu próximo turno.",
  [asi(["DES"]),
   {"tipo": "modificador", "alvo": "ca_total", "valor": ["prof"], "empilha": "soma",
    "custo": "reacao", "aplica_a": "ataques_corpo_a_corpo",
    "duracao": "ate_inicio_do_seu_proximo_turno",
    "requisitos": ["segurando:arma_com_acuidade"],
    "momento": "ao_ser_atingido_corpo_a_corpo"}],
  pre=nv4_e(atributo_min(["DES"])))

t("envenenador", "Envenenador", "geral", 204,
  "Ignora Resistência a dano Venenoso. Proficiência com Kit de Veneno; com 1 hora e 50 PO "
  "faz tantas doses quanto o Bônus de Proficiência. Ação Bônus para aplicar numa arma ou "
  "munição: dura 1 minuto ou até causar dano, e quem sofrer faz salvaguarda de "
  "Constituição ou leva 2d8 de dano Venenoso e fica Envenenado até o fim do próximo turno.",
  [asi(["DES", "INT"]),
   {"tipo": "ignorar_resistencia", "tipo_dano": "venenoso"},
   {"tipo": "conceder_proficiencia", "categoria": "ferramenta", "chave": "kit_de_veneno",
    "nivel_dominio": "proficiente"},
   {"tipo": "fabricar_item", "item": "dose_de_veneno", "quantidade": ["prof"],
    "tempo": "1 hora", "custo_em_po": 50,
    "requisitos": ["ferramenta:kit_de_veneno"]},
   {"tipo": "aplicar_veneno", "custo": "acao_bonus", "consome": {"item": "dose_de_veneno"},
    "alvo_da_aplicacao": ["arma", "municao"],
    "duracao": "1 minuto", "encerra_se": [{"gatilho": "causar_dano_com_o_item"}],
    "efeitos": [
        {"tipo": "dano", "formula_dado": "2d8", "tipo_dano": "venenoso",
         "salvaguarda": {"atributo": "CON",
                         "cd": ["8", "mod:atributo_aumentado_pelo_talento", "prof"],
                         "sucesso": "nenhum_dano"}},
        {"tipo": "conceder_condicao", "condicao_id": "envenenado",
         "beneficiario": "alvo", "duracao": "ate_o_fim_do_proximo_turno_dele",
         "condicao": {"todas": ["falhou_na_salvaguarda"]}}]}],
  pre=NV4)

t("esmagador", "Esmagador", "geral", 204,
  "Uma vez por turno, ao acertar com dano Contundente pode mover o alvo 1,5 m se ele não "
  "for maior que você; e num Acerto Crítico com dano Contundente, ataques contra o alvo "
  "têm Vantagem até o início do seu próximo turno.",
  [asi(["FOR", "CON"]),
   {"tipo": "movimento_forcado", "direcao": "empurrar", "distancia_m": 1.5,
    "origem": "voce", "alvo": "alvo_atingido", "frequencia": "uma_vez_por_turno",
    "destino": "espaco_desocupado",
    "condicao": {"todas": ["acerto_com_dano_contundente",
                           {"nao": "alvo_maior_que_voce"}]}},
   {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "vantagem",
    "beneficiario": "qualquer_atacante_do_alvo",
    "duracao": "ate_inicio_do_seu_proximo_turno",
    "condicao": {"todas": ["acerto_critico_com_dano_contundente"]}}],
  pre=NV4)

t("especialista_ambidestro", "Especialista Ambidestro", "geral", 204,
  "Atacando com arma Leve na ação Atacar, ganha um ataque de Ação Bônus com outra arma "
  "Corpo a Corpo sem Duas Mãos, sem somar o modificador ao dano (salvo se negativo). E "
  "saca ou guarda duas armas sem Duas Mãos onde normalmente sacaria uma.",
  [asi(["FOR", "DES"]),
   {"tipo": "conceder_ataque", "quantidade": ["1"], "custo": "acao_bonus",
    "frequencia": "uma_vez_por_turno",
    "arma_permitida": {"categoria": "arma", "corpo_a_corpo": True,
                       "sem_propriedade": ["duas_maos"]},
    "sem_modificador_de_atributo_no_dano": True,
    "excecao": "modificador negativo continua se aplicando",
    "condicao": {"todas": ["na_acao_atacar", "atacou_com_arma_leve", "seu_turno"]}},
   {"tipo": "efeito_narrativo", "chave": "saque_rapido",
    "texto": "Desembainha ou embainha duas armas sem a propriedade Duas Mãos onde "
             "normalmente faria isso com apenas uma."}],
  pre=nv4_e(atributo_min(["FOR", "DES"])))

t("especialista_em_armaduras_leves", "Especialista em Armaduras Leves", "geral", 204,
  "Treinamento com Armadura Leve e Escudos.",
  [asi(["FOR", "DES"]),
   {"tipo": "conceder_proficiencia", "categoria": "armadura", "chave": "leve",
    "nivel_dominio": "treinado"},
   {"tipo": "conceder_proficiencia", "categoria": "armadura", "chave": "escudo",
    "nivel_dominio": "treinado"}],
  pre=NV4)

t("especialista_em_armaduras_medias", "Especialista em Armaduras Médias", "geral", 204,
  "Treinamento com Armadura Média.",
  [asi(["FOR", "DES"]),
   {"tipo": "conceder_proficiencia", "categoria": "armadura", "chave": "media",
    "nivel_dominio": "treinado"}],
  pre=nv4_e({"tipo": "treinamento_com_armadura", "chave": "leve"}))

t("especialista_em_armaduras_pesadas", "Especialista em Armaduras Pesadas", "geral", 205,
  "Treinamento com Armadura Pesada.",
  [asi(["CON", "FOR"]),
   {"tipo": "conceder_proficiencia", "categoria": "armadura", "chave": "pesada",
    "nivel_dominio": "treinado"}],
  pre=nv4_e({"tipo": "treinamento_com_armadura", "chave": "media"}))

t("especialista_em_besta", "Especialista em Besta", "geral", 205,
  "Ignora a propriedade Recarga das bestas e recarrega sem mão livre; estar a 1,5 m de um "
  "inimigo não dá Desvantagem no ataque com besta; e no ataque adicional da propriedade "
  "Leve com besta Leve, soma o modificador ao dano se ainda não somava.",
  [asi(["DES"]),
   {"tipo": "ignorar_propriedade_de_arma", "propriedade": "recarga",
    "itens": ["besta_de_mao", "besta_leve", "besta_pesada"],
    "tambem": "recarrega sem precisar de mão livre"},
   {"tipo": "impedir", "alvo": "desvantagem_por_inimigo_adjacente",
    "escopo": {"arma": ["besta_de_mao", "besta_leve", "besta_pesada"]}},
   {"tipo": "modificador", "alvo": "jogada_de_dano",
    "valor": ["mod:atributo_de_ataque_da_arma"], "empilha": "soma",
    "condicao": {"todas": ["ataque_adicional_da_propriedade_leve", "arma_e_besta_leve",
                           {"nao": "ja_soma_modificador_no_dano"}]}}],
  pre=nv4_e(atributo_min(["DES"])))

t("especialista_em_pericia", "Especialista em Perícia", "geral", 205,
  "Proficiência numa perícia à escolha e Especialização em outra em que já seja "
  "proficiente sem Especialização.",
  [asi(None),
   {"id": "esp_pericia_proficiencia", "tipo": "escolha",
    "rotulo": "Escolha uma perícia para ganhar proficiência", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "pericias", "todo_o_catalogo": True},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                  "categoria": "pericia", "chave": "{{escolhido}}",
                                  "nivel_dominio": "proficiente"}},
   {"id": "esp_pericia_especializacao", "tipo": "escolha",
    "rotulo": "Escolha uma perícia para Especialização", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "pericias", "todo_o_catalogo": True,
           "filtro_adicional": {"ja_proficiente": True, "sem_especializacao": True}},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                  "categoria": "pericia", "chave": "{{escolhido}}",
                                  "nivel_dominio": "especializacao"}}],
  pre=NV4)

t("exterminador_de_conjuradores", "Exterminador de Conjuradores", "geral", 205,
  "Quem você fere e está concentrado tem Desvantagem na salvaguarda de Concentração. E "
  "uma vez por descanso, uma salvaguarda falha de Inteligência, Sabedoria ou Carisma vira "
  "sucesso à sua escolha.",
  [asi(["FOR", "DES"]),
   {"tipo": "vantagem", "alvo": "salvaguarda", "modo": "desvantagem",
    "beneficiario": "criatura_que_voce_feriu", "aplica_a": "manter_concentracao"},
   {"tipo": "recurso_com_recarga", "id": "resguardo_mental", "formula_maximo": ["1"],
    "recarga": ["descanso_curto", "descanso_longo"], "consumo": "por_uso"},
   {"tipo": "alterar_resultado_de_salvaguarda",
    "alvo": ["salvaguarda:INT", "salvaguarda:SAB", "salvaguarda:CAR"],
    "aplica_a": "falha", "resultado": "sucesso_a_sua_escolha",
    "consome_recurso": "resguardo_mental"}],
  pre=NV4)

t("imobilizador", "Imobilizador", "geral", 205,
  "Ao acertar com Ataque Desarmado na ação Atacar, usa Dano e Imobilizar juntos, uma vez "
  "por turno. Vantagem nos ataques contra quem você Imobilizou, e mover quem está "
  "Imobilizado do seu tamanho ou menor não custa movimento extra.",
  [asi(["FOR", "DES"]),
   {"tipo": "efeito_narrativo", "chave": "socar_e_imobilizar",
    "texto": "Ao acertar com Ataque Desarmado na ação Atacar, usa as opções Dano e "
             "Imobilizar no mesmo golpe, uma vez por turno."},
   {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "vantagem",
    "condicao": {"todas": ["alvo_imobilizado_por_voce"]}},
   {"tipo": "efeito_narrativo", "chave": "imobilizador_veloz",
    "texto": "Mover criatura Imobilizada por você do seu tamanho ou menor não gasta "
             "movimento adicional."}],
  pre=nv4_e(atributo_min(["FOR", "DES"])))

t("lider_inspirador", "Líder Inspirador", "geral", 205,
  "Num Descanso Curto ou Longo, uma atuação encorajadora dá a até seis aliados a até 9 m "
  "(você incluído) PV temporários iguais ao seu nível de personagem mais o modificador do "
  "atributo aumentado por este talento.",
  [asi(["SAB", "CAR"]),
   {"tipo": "pontos_de_vida_temporarios",
    "formula": ["nivel_do_personagem", "mod:atributo_aumentado_pelo_talento"],
    "beneficiario": "ate_6_aliados_a_ate_9m_incluindo_voce",
    "alcance_m": 9, "gatilho": ["descanso_curto", "descanso_longo"]}],
  pre=nv4_e(atributo_min(["SAB", "CAR"])))

t("mente_agucada", "Mente Aguçada", "geral", 205,
  "Proficiência (ou Especialização, se já proficiente) em Arcanismo, História, "
  "Investigação, Natureza ou Religião à escolha, e a ação Analisar passa a caber numa "
  "Ação Bônus.",
  [asi(["INT"]),
   {"id": "mente_agucada_pericia", "tipo": "escolha",
    "rotulo": "Escolha a perícia do Conhecimento Vasto", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "pericias",
           "chaves": ["arcanismo", "historia", "investigacao", "natureza", "religiao"]},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                  "categoria": "pericia", "chave": "{{escolhido}}",
                                  "nivel_dominio": "proficiente_ou_especializacao"}},
   {"tipo": "alterar_custo_de_acao", "acao_id": "analisar", "novo_custo": "acao_bonus"}],
  pre=nv4_e(atributo_min(["INT"])))

t("mestre_das_armas", "Mestre das Armas", "geral", 206,
  "Usa a propriedade de maestria de um tipo de arma Simples ou Marcial em que seja "
  "proficiente, trocando o tipo a cada Descanso Longo.",
  [asi(["FOR", "DES"]),
   {"id": "mestre_das_armas_arma", "tipo": "escolha",
    "rotulo": "Escolha a arma cuja maestria você usa", "quantidade": 1,
    "reescolhivel": True, "reescolha_em": "descanso_longo",
    "de": {"catalogo": "itens", "filtro": {"categoria": "arma"},
           "filtro_adicional": {"ja_proficiente": True}},
    "efeito_por_item_escolhido": {"tipo": "conceder_maestria_de_arma",
                                  "item": "{{escolhido}}"}}],
  pre=NV4)

t("mestre_em_armaduras_medias", "Mestre em Armaduras Médias", "geral", 206,
  "Com armadura Média, soma 3 em vez de 2 na CA se a Destreza for 16 ou mais.",
  [asi(["FOR", "DES"]),
   {"tipo": "alterar_teto_de_modificador_na_ca", "categoria_de_armadura": "media",
    "novo_teto": 3,
    "condicao": {"todas": ["armadura:media", "valor_de_atributo:DES>=16"]}}],
  pre=nv4_e({"tipo": "treinamento_com_armadura", "chave": "media"}))

t("mestre_em_armaduras_pesadas", "Mestre em Armaduras Pesadas", "geral", 206,
  "Com armadura Pesada, reduz em pontos iguais ao Bônus de Proficiência o dano "
  "Contundente, Cortante e Perfurante de cada ataque que o acerta.",
  [asi(["FOR", "CON"]),
   {"tipo": "reducao_de_dano", "formula": ["prof"],
    "tipos_de_dano": ["contundente", "cortante", "perfurante"],
    "gatilho": "ser_atingido_por_ataque",
    "condicao": {"todas": ["armadura:pesada"]}}],
  pre=nv4_e({"tipo": "treinamento_com_armadura", "chave": "pesada"}))

t("mestre_em_armas_de_haste", "Mestre em Armas de Haste", "geral", 206,
  "Com Cajado, Lança ou arma com Alcance e Pesada: depois da ação Atacar, Ação Bônus para "
  "um golpe com a outra ponta (d4 Contundente); e Reação para atacar quem entra no seu "
  "alcance.",
  [asi(["FOR", "DES"]),
   {"tipo": "conceder_ataque", "quantidade": ["1"], "custo": "acao_bonus",
    "tipo_ataque": "corpo_a_corpo", "formula_dado": "1d4", "tipo_dano": "contundente",
    "arma_permitida": {"chaves": ["cajado", "lanca"],
                       "ou_propriedades": ["alcance", "pesada"]},
    "condicao": {"todas": ["executou_a_acao_atacar_com_essa_arma"]}},
   {"tipo": "conceder_ataque", "quantidade": ["1"], "custo": "reacao",
    "tipo_ataque": "corpo_a_corpo",
    "arma_permitida": {"chaves": ["cajado", "lanca"],
                       "ou_propriedades": ["alcance", "pesada"]},
    "gatilho": "criatura_entra_no_seu_alcance"}],
  pre=nv4_e(atributo_min(["FOR", "DES"])))

t("mestre_em_armas_grandes", "Mestre em Armas Grandes", "geral", 206,
  "Ao acertar com arma Pesada na ação Atacar, causa dano adicional igual ao Bônus de "
  "Proficiência. E logo após um Acerto Crítico ou derrubar alguém a 0 PV com arma Corpo a "
  "Corpo, ataca de novo como Ação Bônus.",
  [asi(["FOR"]),
   {"tipo": "modificador", "alvo": "jogada_de_dano", "valor": ["prof"],
    "empilha": "soma",
    "condicao": {"todas": ["acerto_com_arma_pesada", "na_acao_atacar", "seu_turno"]}},
   {"tipo": "conceder_ataque", "quantidade": ["1"], "custo": "acao_bonus",
    "arma_permitida": {"mesma_arma_do_gatilho": True},
    "condicao": {"alguma": ["acerto_critico_com_arma_corpo_a_corpo",
                            "reduziu_criatura_a_zero_pv_com_arma_corpo_a_corpo"]}}],
  pre=nv4_e(atributo_min(["FOR"])))

t("mestre_em_escudos", "Mestre em Escudos", "geral", 206,
  "Ao acertar corpo a corpo na ação Atacar, golpeia com o Escudo: salvaguarda de Força ou "
  "o alvo é empurrado 1,5 m ou fica Caído, à sua escolha — uma vez por turno. E com "
  "Escudo em mãos, uma salvaguarda de Destreza bem-sucedida por metade do dano passa a "
  "não causar dano nenhum, com a Reação.",
  [asi(["FOR"]),
   {"id": "mestre_em_escudos_golpe", "tipo": "escolha",
    "rotulo": "Escolha o efeito do Golpe de Escudo", "quantidade": 1,
    "momento": "no_acerto", "frequencia": "uma_vez_por_turno",
    "requisitos": ["equipado:escudo"],
    "condicao": {"todas": ["acerto_corpo_a_corpo", "na_acao_atacar",
                           "alvo_a_ate_1_5m"]},
    "salvaguarda": {"atributo": "FOR", "cd": ["8", "mod:FOR", "prof"]},
    "de": {"catalogo": "efeitos_do_golpe_de_escudo", "todo_o_catalogo": True},
    "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                  "chave": "{{escolhido}}"}},
   {"tipo": "alterar_resultado_de_salvaguarda", "alvo": "salvaguarda:DES",
    "aplica_a": "efeito_com_metade_do_dano", "em_sucesso": "nenhum_dano",
    "custo": "reacao", "requisitos": ["segurando:escudo"]}],
  pre=nv4_e({"tipo": "treinamento_com_armadura", "chave": "escudo"}))

t("mestre_atirador", "Mestre-Atirador", "geral", 207,
  "Ataques à distância com armas ignoram Cobertura Parcial e de Três Quartos; estar a "
  "1,5 m de um inimigo não dá Desvantagem; e atacar no alcance máximo também não.",
  [asi(["DES"]),
   {"tipo": "ignorar_cobertura", "graus": ["parcial", "tres_quartos"],
    "escopo": {"jogada": "jogada_de_ataque", "arma_a_distancia": True}},
   {"tipo": "impedir", "alvo": "desvantagem_por_inimigo_adjacente",
    "escopo": {"arma_a_distancia": True}},
   {"tipo": "impedir", "alvo": "desvantagem_por_alcance_maximo",
    "escopo": {"arma_a_distancia": True}}],
  pre=nv4_e(atributo_min(["DES"])))

t("perfurador", "Perfurador", "geral", 207,
  "Uma vez por turno, ao acertar com dano Perfurante, rejoga um dos dados de dano e usa a "
  "nova jogada. Num Acerto Crítico com dano Perfurante, joga um dado de dano a mais.",
  [asi(["FOR", "DES"]),
   {"tipo": "rolar_novamente", "alvo": "dado_de_dano_da_arma",
    "quantidade_de_dados": ["1"], "usa_novo_resultado": True,
    "frequencia": "uma_vez_por_turno",
    "condicao": {"todas": ["acerto_com_dano_perfurante"]}},
   {"tipo": "alterar_dano", "tipo_dano": "perfurante", "operacao": "dado_adicional",
    "quantidade_de_dados": 1,
    "condicao": {"todas": ["acerto_critico_com_dano_perfurante"]}}],
  pre=NV4)

t("resiliente", "Resiliente", "geral", 207,
  "Escolhe um atributo em que não tem proficiência em salvaguarda: aumenta em 1 e ganha "
  "proficiência na salvaguarda dele.",
  [{"id": "resiliente_atributo", "tipo": "escolha",
    "rotulo": "Escolha o atributo", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "atributos", "todo_o_catalogo": True,
           "filtro_adicional": {"sem_proficiencia_em_salvaguarda": True}},
    "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                  "chave": "{{escolhido}}"}}],
  pre=NV4,
  efeitos_nomeados={
      a: {"efeitos": [
          {"tipo": "aumento_atributo", "atributo": a, "valor": 1, "limite": 20},
          {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": a,
           "nivel_dominio": "proficiente"}]}
      for a in ("FOR", "DES", "CON", "INT", "SAB", "CAR")})

t("resistente", "Resistente", "geral", 207,
  "Vantagem em Salvaguardas Contra Morte e, como Ação Bônus, gasta um Dado de Vida para "
  "recuperar Pontos de Vida iguais ao resultado.",
  [asi(["CON"]),
   {"tipo": "vantagem", "alvo": "salvaguarda_contra_morte", "modo": "vantagem"},
   {"tipo": "cura", "custo": "acao_bonus", "formula": ["dado_de_vida"],
    "gasta_dado_de_vida": 1}],
  pre=NV4)

t("sentinela", "Sentinela", "geral", 207,
  "Ataque de Oportunidade contra quem, a até 1,5 m, Desengaja ou ataca outro alvo que não "
  "você. E quem você acerta com Ataque de Oportunidade fica com Deslocamento 0 pelo resto "
  "do turno.",
  [asi(["FOR", "DES"]),
   {"tipo": "conceder_ataque", "quantidade": ["1"], "custo": "reacao",
    "tipo_ataque": "ataque_de_oportunidade",
    "gatilho": "criatura_a_ate_1_5m_desengaja_ou_ataca_outro_alvo"},
   {"tipo": "travar_deslocamento", "valor": 0, "alvo": "criatura_atingida",
    "duracao": "resto_do_turno_atual",
    "condicao": {"todas": ["acerto_com_ataque_de_oportunidade"]}}],
  pre=nv4_e(atributo_min(["FOR", "DES"])))

t("sorrateiro", "Sorrateiro", "geral", 207,
  "Visão às Cegas de 3 m; Vantagem em Destreza (Furtividade) na ação Esconder durante o "
  "combate; e errar um ataque estando escondido não revela sua posição.",
  [asi(["DES"]),
   {"tipo": "conceder_sentido", "sentido": "visao_as_cegas", "alcance_m": 3},
   {"tipo": "vantagem", "alvo": "teste_de_atributo:furtividade", "modo": "vantagem",
    "condicao": {"todas": ["acao:esconder", "em_combate"]}},
   {"tipo": "efeito_narrativo", "chave": "erro_nao_revela",
    "texto": "Errar uma jogada de ataque enquanto está escondido não revela sua "
             "localização."}],
  pre=nv4_e(atributo_min(["DES"])))

t("talhador", "Talhador", "geral", 208,
  "Uma vez por turno, ao acertar com dano Cortante, reduz o Deslocamento do alvo em 3 m "
  "até o início do seu próximo turno. Num Acerto Crítico com dano Cortante, o alvo ataca "
  "com Desvantagem até lá.",
  [asi(["FOR", "DES"]),
   {"tipo": "modificador", "alvo": "deslocamento", "valor": ["-3"], "empilha": "soma",
    "beneficiario": "alvo_atingido", "frequencia": "uma_vez_por_turno",
    "duracao": "ate_inicio_do_seu_proximo_turno",
    "condicao": {"todas": ["acerto_com_dano_cortante"]}},
   {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "desvantagem",
    "beneficiario": "alvo_atingido", "duracao": "ate_inicio_do_seu_proximo_turno",
    "condicao": {"todas": ["acerto_critico_com_dano_cortante"]}}],
  pre=NV4)

t("telecinetico", "Telecinético", "geral", 208,
  "Aprende Mãos Mágicas, conjurável sem componentes Verbais nem Somáticos, com a mão "
  "Invisível e +9 m de alcance. E, como Ação Bônus, empurra ou puxa 1,5 m uma criatura à "
  "vista a até 9 m que falhe numa salvaguarda de Força.",
  [asi(["INT", "SAB", "CAR"]),
   {"tipo": "desbloquear_magias", "magia": "maos_magicas", "modo": "conhecida",
    "atributo_de_conjuracao": "atributo_aumentado_pelo_talento"},
   {"tipo": "dispensar_componentes", "componentes": ["V", "S"],
    "escopo": {"magias": ["maos_magicas"]}},
   {"tipo": "alterar_alcance_da_magia", "operacao": "somar", "metros": 9,
    "escopo": {"magias": ["maos_magicas"]}},
   {"tipo": "movimento_forcado", "direcao": "a_sua_escolha", "distancia_m": 1.5,
    "custo": "acao_bonus", "alcance_m": 9, "alvo": "criatura_a_vista",
    "salvaguarda": {"atributo": "FOR",
                    "cd": ["8", "mod:atributo_aumentado_pelo_talento", "prof"]},
    "nota": "Move o alvo na sua direção ou para longe de você, à sua escolha."}],
  pre=NV4)

t("telepatico", "Telepático", "geral", 208,
  "Fala telepaticamente com qualquer criatura à vista a até 18 m, num idioma que você "
  "conhece (ela só entende se souber o idioma, e não pode responder). E tem Detectar "
  "Pensamentos sempre preparada, conjurável uma vez por Descanso Longo sem espaço nem "
  "componentes, ou com espaço do círculo apropriado.",
  [asi(["INT", "SAB", "CAR"]),
   {"tipo": "conceder_sentido", "sentido": "telepatia", "alcance_m": 18,
    "modo": "unidirecional",
    "nota": "Fala no idioma que você conhece; a criatura só entende se souber esse "
            "idioma e não pode responder telepaticamente."},
   {"tipo": "preparar_magias", "magia": "detectar_pensamentos",
    "fonte_das_magias": "conhecidas", "modo": "sempre_preparada",
    "nao_conta_para_o_limite": True,
    "atributo_de_conjuracao": "atributo_aumentado_pelo_talento"},
   {"tipo": "conjurar_sem_espaco", "magia": "detectar_pensamentos",
    "frequencia": "uma_vez_por_descanso_longo", "sem_componentes": True}],
  pre=NV4)

t("tocado_pelas_sombras", "Tocado Pelas Sombras", "geral", 208,
  "Escolhe uma magia de 1º círculo de Ilusão ou Necromancia: ela e Invisibilidade ficam "
  "sempre preparadas, cada uma conjurável uma vez por Descanso Longo sem espaço, ou com "
  "espaço do círculo apropriado.",
  [asi(["INT", "SAB", "CAR"]),
   {"id": "tocado_sombras_magia", "tipo": "escolha",
    "rotulo": "Escolha a magia de Ilusão ou Necromancia", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "magias",
           "filtro": {"nivel": 1, "escola": ["ilusao", "necromancia"]}},
    "efeito_por_item_escolhido": {"tipo": "preparar_magias", "magia": "{{escolhido}}",
                                  "fonte_das_magias": "conhecidas",
                                  "modo": "sempre_preparada",
                                  "nao_conta_para_o_limite": True}},
   {"tipo": "preparar_magias", "magia": "invisibilidade",
    "fonte_das_magias": "conhecidas", "modo": "sempre_preparada",
    "nao_conta_para_o_limite": True,
    "atributo_de_conjuracao": "atributo_aumentado_pelo_talento"},
   {"tipo": "conjurar_sem_espaco", "magias": ["invisibilidade", "$tocado_sombras_magia"],
    "frequencia": "uma_vez_por_descanso_longo_para_cada_magia"}],
  pre=NV4)

t("tocado_por_fadas", "Tocado Por Fadas", "geral", 208,
  "Escolhe uma magia de 1º círculo de Adivinhação ou Encantamento: ela e Passo Nebuloso "
  "ficam sempre preparadas, cada uma conjurável uma vez por Descanso Longo sem espaço, ou "
  "com espaço do círculo apropriado.",
  [asi(["INT", "SAB", "CAR"]),
   {"id": "tocado_fadas_magia", "tipo": "escolha",
    "rotulo": "Escolha a magia de Adivinhação ou Encantamento", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "magias",
           "filtro": {"nivel": 1, "escola": ["adivinhacao", "encantamento"]}},
    "efeito_por_item_escolhido": {"tipo": "preparar_magias", "magia": "{{escolhido}}",
                                  "fonte_das_magias": "conhecidas",
                                  "modo": "sempre_preparada",
                                  "nao_conta_para_o_limite": True}},
   {"tipo": "preparar_magias", "magia": "passo_nebuloso",
    "fonte_das_magias": "conhecidas", "modo": "sempre_preparada",
    "nao_conta_para_o_limite": True,
    "atributo_de_conjuracao": "atributo_aumentado_pelo_talento"},
   {"tipo": "conjurar_sem_espaco", "magias": ["passo_nebuloso", "$tocado_fadas_magia"],
    "frequencia": "uma_vez_por_descanso_longo_para_cada_magia"}],
  pre=NV4)

t("treinamento_com_armas_marciais", "Treinamento com Armas Marciais", "geral", 209,
  "Proficiência com armas Marciais.",
  [asi(["FOR", "DES"]),
   {"tipo": "conceder_proficiencia", "categoria": "arma",
    "de": {"catalogo": "itens", "filtro": {"categoria": "arma", "grupo": "marcial"}},
    "nivel_dominio": "proficiente"}],
  pre=NV4)

t("velocista", "Velocista", "geral", 209,
  "Deslocamento +3 m; na ação Correr, Terreno Difícil não custa movimento extra pelo "
  "resto do turno; e Ataques de Oportunidade contra você têm Desvantagem.",
  [asi(["DES", "CON"]),
   {"tipo": "modificador", "alvo": "deslocamento", "valor": ["3"], "empilha": "soma"},
   {"tipo": "efeito_narrativo", "chave": "correr_em_terreno_dificil",
    "texto": "Na ação Correr, Terreno Difícil não custa movimento adicional pelo resto do "
             "turno."},
   {"tipo": "vantagem", "alvo": "jogada_de_ataque_contra_voce", "modo": "desvantagem",
    "escopo": {"apenas_ataques_de_oportunidade": True}}],
  pre=nv4_e(atributo_min(["DES", "CON"])))

# ================================================== Talentos de Dádiva Épica

t("dadiva_da_fortitude", "Dádiva da Fortitude", "epico", 210,
  "Pontos de Vida máximos +40 e, ao recuperar Pontos de Vida, recupera ainda o "
  "modificador de Constituição — no máximo uma vez até o início do seu próximo turno.",
  [asi(None, teto=30),
   {"tipo": "modificador", "alvo": "pontos_de_vida_maximos", "valor": ["40"],
    "empilha": "soma"},
   {"tipo": "cura", "formula": ["mod:CON"], "modo": "adicional_a_qualquer_cura",
    "frequencia": "uma_vez_ate_o_inicio_do_seu_proximo_turno"}],
  pre=NV19)

t("dadiva_da_proeza_em_combate", "Dádiva da Proeza em Combate", "epico", 210,
  "Quando você erra uma jogada de ataque, ela acerta — no máximo uma vez até o início do "
  "seu próximo turno.",
  [asi(None, teto=30),
   {"tipo": "transformar_erro_em_acerto", "alvo": "jogada_de_ataque",
    "frequencia": "uma_vez_ate_o_inicio_do_seu_proximo_turno"}],
  pre=NV19)

t("dadiva_da_proficiencia_em_pericia", "Dádiva da Proficiência em Perícia", "epico", 210,
  "Proficiência em todas as perícias, mais Especialização numa em que ainda não a tenha.",
  [asi(None, teto=30),
   {"tipo": "conceder_proficiencia", "categoria": "pericia",
    "de": {"catalogo": "pericias", "todo_o_catalogo": True},
    "nivel_dominio": "proficiente"},
   {"id": "dadiva_pericia_especializacao", "tipo": "escolha",
    "rotulo": "Escolha uma perícia para Especialização", "quantidade": 1,
    "momento": "ao_adquirir_o_talento",
    "de": {"catalogo": "pericias", "todo_o_catalogo": True,
           "filtro_adicional": {"ja_proficiente": True, "sem_especializacao": True}},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                  "categoria": "pericia", "chave": "{{escolhido}}",
                                  "nivel_dominio": "especializacao"}}],
  pre=NV19)

t("dadiva_da_recordacao_de_magia", "Dádiva da Recordação de Magia", "epico", 210,
  "Ao conjurar com espaço de 1º a 4º círculo, joga 1d4: se o resultado for igual ao "
  "círculo do espaço, o espaço não é gasto.",
  [asi(["INT", "SAB", "CAR"], teto=30),
   {"tipo": "nao_gastar_espaco_de_magia", "circulos": [1, 2, 3, 4],
    "teste": {"dado": "1d4", "nao_gasta_se": "resultado_igual_ao_circulo_do_espaco"}}],
  pre=NV19 + [{"tipo": "caracteristica", "chave": "conjuracao"}])

t("dadiva_da_recuperacao", "Dádiva da Recuperação", "epico", 210,
  "Ao ser reduzido a 0 Pontos de Vida, pode ficar com 1 e recuperar metade do seu máximo "
  "— uma vez por Descanso Longo. E tem uma reserva de dez d10 para gastar como Ação Bônus "
  "e curar o total rolado, restaurada no Descanso Longo.",
  [asi(None, teto=30),
   {"tipo": "recurso_com_recarga", "id": "ate_a_morte", "formula_maximo": ["1"],
    "recarga": ["descanso_longo"], "consumo": "por_uso"},
   {"tipo": "cura", "formula": [{"op": "div_arred_baixo",
                                 "args": ["pontos_de_vida_maximos", "2"]}],
    "gatilho": "reduzido_a_zero_pv", "consome_recurso": "ate_a_morte",
    "mantem_com_pv": 1},
   {"tipo": "reserva_de_dados", "id": "recuperar_vitalidade", "dado": "d10",
    "formula_quantidade": ["10"], "custo": "acao_bonus",
    "recarga": ["descanso_longo"],
    "efeitos": [{"tipo": "cura", "formula": ["resultado_dos_dados_gastos"]}]}],
  pre=NV19)

t("dadiva_da_resistencia_a_energia", "Dádiva da Resistência à Energia", "epico", 211,
  "Resistência a dois tipos de dano à escolha entre nove, trocáveis a cada Descanso "
  "Longo. E, ao sofrer dano de um deles, Reação para mandar dano do mesmo tipo a uma "
  "criatura à vista a até 18 m sem Cobertura Total: salvaguarda de Destreza ou 2d12 + "
  "modificador de Constituição.",
  [asi(None, teto=30),
   {"id": "dadiva_energia_tipos", "tipo": "escolha",
    "rotulo": "Escolha 2 tipos de dano para Resistência", "quantidade": 2,
    "reescolhivel": True, "reescolha_em": "descanso_longo",
    "de": {"catalogo": "tipos_de_dano",
           "chaves": ["acido", "eletrico", "gelido", "igneo", "necrotico", "psiquico",
                      "radiante", "trovejante", "venenoso"]},
    "efeito_por_item_escolhido": {"tipo": "alterar_dano", "tipo_dano": "{{escolhido}}",
                                  "operacao": "resistencia"}},
   {"tipo": "redirecionar_dano", "custo": "reacao", "alcance_m": 18,
    "alvo": "criatura_a_vista", "excecao_de_alvo": ["sob_cobertura_total"],
    "gatilho": "sofrer_dano_de_um_dos_tipos_escolhidos",
    "efeitos": [{"tipo": "dano", "formula_dado": "2d12", "somar": ["mod:CON"],
                 "tipo_dano": "mesmo_do_ataque",
                 "salvaguarda": {"atributo": "DES",
                                 "cd": ["8", "mod:CON", "prof"],
                                 "sucesso": "nenhum_dano"}}]}],
  pre=NV19)

t("dadiva_da_velocidade", "Dádiva da Velocidade", "epico", 211,
  "Ação Bônus para Desengajar, o que também encerra a condição Imobilizado em você. "
  "Deslocamento +9 m.",
  [asi(None, teto=30),
   {"tipo": "alterar_custo_de_acao", "acao_id": "desengajar",
    "novo_custo": "acao_bonus",
    "efeitos_adicionais": [{"tipo": "remover_condicao", "condicao_id": "imobilizado",
                            "beneficiario": "voce"}]},
   {"tipo": "modificador", "alvo": "deslocamento", "valor": ["9"], "empilha": "soma"}],
  pre=NV19)

t("dadiva_da_viagem_dimensional", "Dádiva da Viagem Dimensional", "epico", 211,
  "Logo depois da ação Atacar ou Usar Magia, teleporta-se até 9 m para um espaço "
  "desocupado à sua vista.",
  [asi(None, teto=30),
   {"tipo": "teleporte", "alcance_m": 9, "custo": "livre",
    "requisitos": ["destino_desocupado", "destino_a_vista"],
    "gatilho": ["acao:atacar", "acao:usar_magia"]}],
  pre=NV19)

t("dadiva_da_visao_verdadeira", "Dádiva da Visão Verdadeira", "epico", 211,
  "Visão Verdadeira com alcance de 18 metros.",
  [asi(None, teto=30),
   {"tipo": "conceder_sentido", "sentido": "visao_verdadeira", "alcance_m": 18}],
  pre=NV19)

t("dadiva_do_ataque_irresistivel", "Dádiva do Ataque Irresistível", "epico", 211,
  "Seu dano Contundente, Cortante e Perfurante sempre ignora Resistência. E num 20 no d20 "
  "de ataque, causa dano adicional igual ao VALOR do atributo aumentado por este talento, "
  "do mesmo tipo do ataque.",
  [asi(["FOR", "DES"], teto=30),
   {"tipo": "ignorar_resistencia",
    "tipos_de_dano": ["contundente", "cortante", "perfurante"]},
   {"tipo": "alterar_dano", "tipo_dano": "mesmo_do_ataque", "operacao": "dano_adicional",
    "valor": ["valor_do_atributo_aumentado_pelo_talento"],
    "condicao": {"todas": ["resultado_20_no_d20_de_ataque"]},
    "nota": "É o VALOR do atributo, não o modificador."}],
  pre=NV19)

t("dadiva_do_destino", "Dádiva do Destino", "epico", 211,
  "Quando você ou uma criatura a até 18 m passa ou falha num Teste de D20, joga 2d4 e "
  "aplica como bônus ou penalidade. Recarrega ao jogar Iniciativa ou num descanso.",
  [asi(None, teto=30),
   {"tipo": "recurso_com_recarga", "id": "aprimorar_destino", "formula_maximo": ["1"],
    "recarga": ["jogar_iniciativa", "descanso_curto", "descanso_longo"],
    "consumo": "por_uso"},
   {"tipo": "modificador", "alvo": "teste_d20_de_criatura_a_vista", "valor": ["2d4"],
    "empilha": "soma", "sinal": "a_sua_escolha", "alcance_m": 18,
    "beneficiario": "voce_ou_criatura_a_ate_18m", "momento": "apos_a_jogada",
    "consome_recurso": "aprimorar_destino"}],
  pre=NV19)

t("dadiva_do_espirito_da_noite", "Dádiva do Espírito da Noite", "epico", 211,
  "Em Meia-luz ou Escuridão: Ação Bônus para ficar Invisível — a condição acaba assim que "
  "você executa ação, Ação Bônus ou Reação — e Resistência a todo dano exceto Psíquico e "
  "Radiante.",
  [asi(None, teto=30),
   {"tipo": "conceder_condicao", "condicao_id": "invisivel", "beneficiario": "voce",
    "custo": "acao_bonus",
    "condicao": {"todas": ["em:meia_luz_ou_escuridao"]},
    "encerra_se": [{"gatilho": "executar_acao"}, {"gatilho": "executar_acao_bonus"},
                   {"gatilho": "executar_reacao"}]},
   {"tipo": "alterar_dano", "tipo_dano": "todos", "operacao": "resistencia",
    "excecoes": ["psiquico", "radiante"],
    "condicao": {"todas": ["em:meia_luz_ou_escuridao"]}}],
  pre=NV19)

# =========================================================== catálogos auxiliares

AUXILIARES = [
    ("modos_de_aumento_de_atributo", "Modos do Aumento no Valor de Atributo", 203,
     "As duas formas de gastar o talento Aumento no Valor de Atributo (p. 203).", [
         ("um_atributo_em_2", "Um atributo em +2",
          "Aumenta um valor de atributo à sua escolha em 2, até o máximo de 20."),
         ("dois_atributos_em_1", "Dois atributos em +1",
          "Aumenta dois valores de atributo à sua escolha em 1 cada, até o máximo de 20."),
     ]),
    ("efeitos_do_ataque_em_investida", "Efeitos do Ataque em Investida", 202,
     "As duas opções do Ataque em Investida do talento Agressor (p. 202).", [
         ("dano_extra", "+1d8 no dano",
          "Bônus de +1d8 na jogada de dano do ataque."),
         ("empurrar", "Empurrar até 3 metros",
          "Empurra o alvo até 3 metros, se ele não for de um tamanho maior que o seu."),
     ]),
    ("efeitos_do_golpe_de_escudo", "Efeitos do Golpe de Escudo", 207,
     "As duas opções do Golpe de Escudo do talento Mestre em Escudos (p. 207).", [
         ("empurrar", "Empurrar 1,5 metro",
          "Empurra o alvo 1,5 metro para longe de você."),
         ("derrubar", "Derrubar",
          "Impõe ao alvo a condição Caído."),
     ]),
]

EFEITOS_AUX = {
    ("efeitos_do_ataque_em_investida", "dano_extra"): [
        {"tipo": "modificador", "alvo": "jogada_de_dano", "valor": ["1d8"],
         "empilha": "soma"}],
    ("efeitos_do_ataque_em_investida", "empurrar"): [
        {"tipo": "movimento_forcado", "direcao": "empurrar", "distancia_m": 3,
         "origem": "voce", "alvo": "alvo_atingido",
         "condicao": {"todas": [{"nao": "alvo_maior_que_voce"}]}}],
    ("efeitos_do_golpe_de_escudo", "empurrar"): [
        {"tipo": "movimento_forcado", "direcao": "empurrar", "distancia_m": 1.5,
         "origem": "voce", "alvo": "alvo_atingido",
         "condicao": {"todas": ["falhou_na_salvaguarda"]}}],
    ("efeitos_do_golpe_de_escudo", "derrubar"): [
        {"tipo": "conceder_condicao", "condicao_id": "caido", "beneficiario": "alvo",
         "condicao": {"todas": ["falhou_na_salvaguarda"]}}],
    ("modos_de_aumento_de_atributo", "um_atributo_em_2"): [
        {"tipo": "efeito_narrativo", "chave": "modo_um_atributo",
         "texto": "Os efeitos reais estão em efeitos_nomeados do talento Aumento no Valor "
                  "de Atributo; este item é a opção da escolha."}],
    ("modos_de_aumento_de_atributo", "dois_atributos_em_1"): [
        {"tipo": "efeito_narrativo", "chave": "modo_dois_atributos",
         "texto": "Os efeitos reais estão em efeitos_nomeados do talento Aumento no Valor "
                  "de Atributo; este item é a opção da escolha."}],
}

# ------------------------------------------------------------- tipos e alvos novos
TIPOS_NOVOS = [
    ("tratar_dado_de_dano_minimo", "Tratar resultado baixo num dado de dano como maior",
     "Qualquer resultado até X num dado de dano vira Y. Combate com Armas Grandes "
     "(1 ou 2 viram 3) e Adepto Elemental (1 vira 2). Antes era efeito_narrativo."),
    ("ignorar_resistencia", "Ignorar Resistência a um tipo de dano",
     "O dano causado ignora Resistência ao tipo indicado (Adepto Elemental, Envenenador, "
     "Dádiva do Ataque Irresistível)."),
    ("ignorar_cobertura", "Ignorar graus de Cobertura",
     "A jogada de ataque indicada ignora os graus de Cobertura listados."),
    ("alterar_custo_de_acao", "Alterar o custo de uma ação",
     "Uma ação do catálogo passa a caber noutro custo (Procurar e Analisar como Ação "
     "Bônus; Desengajar como Ação Bônus na Dádiva da Velocidade)."),
    ("fabricar_item", "Fabricar item",
     "Produz itens com ferramenta, tempo e custo declarados (Artifista, Chef, "
     "Envenenador)."),
    ("desconto_em_compra", "Desconto na compra",
     "Reduz o preço de compra pelo percentual declarado (Artifista)."),
    ("conceder_inspiracao_heroica", "Conceder Inspiração Heroica",
     "Dá Inspiração Heroica a um número declarado de criaturas (Músico)."),
    ("trocar_iniciativa", "Trocar a Iniciativa com um aliado",
     "Troca o resultado de Iniciativa com um aliado voluntário (Alerta)."),
    ("transformar_erro_em_acerto", "Transformar um erro em acerto",
     "Uma jogada de ataque que erraria passa a acertar (Dádiva da Proeza em Combate)."),
    ("conceder_maestria_de_arma", "Conceder o uso da maestria de uma arma",
     "Libera a propriedade de maestria da arma indicada (Mestre das Armas)."),
    ("nao_gastar_espaco_de_magia", "Não gastar o espaço de magia",
     "Sob a condição declarada, o espaço usado não é consumido (Dádiva da Recordação de "
     "Magia)."),
    ("redirecionar_dano", "Redirecionar dano para outra criatura",
     "Manda para outro alvo dano do mesmo tipo recebido (Dádiva da Resistência à "
     "Energia)."),
    ("redirecionar_ataque", "Redirecionar um ataque para si",
     "Faz um ataque que atingiria outra criatura atingir você (Combatente Montado)."),
    ("aplicar_veneno", "Aplicar veneno numa arma ou munição",
     "Prepara o item envenenado, com duração e efeito ao causar dano (Envenenador)."),
    ("ignorar_propriedade_de_arma", "Ignorar uma propriedade de arma",
     "A propriedade indicada deixa de valer para os itens listados (Especialista em "
     "Besta ignora Recarga)."),
    ("alterar_teto_de_modificador_na_ca", "Alterar o teto do modificador somado na CA",
     "Muda quanto do modificador de Destreza a armadura deixa somar (Mestre em Armaduras "
     "Médias)."),
]

ALVOS_NOVOS = [
    ("dado_de_dano_da_arma", "Dado de dano de uma arma",
     "Os dados de dano de um ataque com arma, distintos dos de magia. Alvo de rejogada "
     "no Atacante Selvagem e no Perfurador."),
    ("dado_de_dano_do_ataque_desarmado", "Dado de dano do Ataque Desarmado",
     "O dado do Ataque Desarmado. Alvo da rejogada do Valentão de Taverna."),
    ("dado_de_cura", "Dado de cura",
     "Os dados jogados para determinar Pontos de Vida recuperados. Alvo da rejogada do "
     "Curandeiro."),
]

IMPEDIMENTOS_NOVOS = [
    ("desvantagem_por_inimigo_adjacente",
     "Ter Desvantagem por um inimigo estar a até 1,5 metro",
     "Usado por Atirador Arcano, Especialista em Besta e Mestre-Atirador (cap. 5): estar "
     "perto de um inimigo deixa de impor Desvantagem naquele tipo de ataque."),
    ("desvantagem_por_alcance_maximo",
     "Ter Desvantagem por atacar no alcance máximo",
     "Usado pelo Mestre-Atirador (p. 207): atacar no alcance máximo da arma à Distância "
     "deixa de impor Desvantagem."),
]


def carregar(p):
    return json.load(open(p, encoding='utf-8'),
                     object_pairs_hook=collections.OrderedDict)


def gravar(p, d):
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def juntar(caminho, novos, campos):
    d = carregar(caminho)
    existentes = {i['id'] for i in d['itens']}
    n = 0
    for valores in novos:
        item = collections.OrderedDict(zip(campos, valores))
        if item['id'] in existentes:
            continue
        d['itens'].append(item)
        n += 1
    d['total'] = len(d['itens'])
    gravar(caminho, d)
    return n


def main():
    # ---------------------------------------------------------- catálogos auxiliares
    for cid, nome, pag, nota, itens in AUXILIARES:
        d = collections.OrderedDict([
            ("catalogo", cid), ("nome", nome), ("fonte", fonte(pag)), ("nota", nota),
            ("total", len(itens)),
            ("itens", [collections.OrderedDict([
                ("id", iid), ("nome", inome), ("descricao_curta", idesc),
                ("efeitos", EFEITOS_AUX[(cid, iid)])])
                for iid, inome, idesc in itens])])
        gravar(f"{CAT}/{cid}.json", d)

    n_tipos = juntar(f'{CAT}/tipos_de_efeito.json', TIPOS_NOVOS,
                     ['id', 'nome', 'descricao_curta'])
    n_alvos = juntar(f'{CAT}/alvos.json', ALVOS_NOVOS,
                     ['id', 'nome', 'descricao_curta'])
    n_imp = juntar(f'{CAT}/alvos_de_impedimento.json', IMPEDIMENTOS_NOVOS,
                   ['id', 'nome', 'nota'])

    # ------------------------------------------------------------------ talentos
    d = carregar(f'{CAT}/talentos.json')
    antigos = {i['id']: i for i in d['itens']}
    novos = []
    for tal in TALENTOS:
        antigo = antigos.pop(tal['id'], None)
        if antigo and antigo.get('nota'):
            tal['nota_anterior'] = antigo['nota']
        novos.append(tal)
    # os de Estilo de Luta e Iniciado em Magia já estavam prontos: preserva
    preservados = [i for i in antigos.values() if not i.get('pendente')]
    # 'dadiva_epica' nunca foi um talento: era um MARCADOR que eu criei para as classes
    # poderem apontar antes do capítulo 5. Agora a categoria 'epico' existe de verdade,
    # com 12 talentos, e a característica de nível 19 escolhe dentro dela. O marcador sai.
    removidos = [i['id'] for i in antigos.values() if i.get('pendente')]
    ainda_pendentes = []
    d['itens'] = sorted(novos + preservados, key=lambda i: (i['categoria'], i['id']))
    d['total'] = len(d['itens'])
    d.pop('parcial', None)
    d['categorias_completas'] = ["origem", "geral", "estilo_de_luta", "epico"]
    d['nota'] = ("Capítulo 5 COMPLETO: 75 talentos nas quatro categorias. O talento "
                 "genérico 'dadiva_epica' virou a CATEGORIA 'epico' — quem antes "
                 "apontava para ele agora escolhe um talento dessa categoria.")
    gravar(f'{CAT}/talentos.json', d)

    # ---------------------- 'dadiva_epica' era um talento-marcador; vira categoria
    caracs = carregar('dados/caracteristicas.json')
    n_dadiva = 0
    for it in caracs['itens']:
        if it['id'] != 'dadiva_epica':
            continue
        it['descricao_curta'] = ("No nível 19 você adquire um talento da categoria Dádiva "
                                 "Épica, ou outro talento para o qual se qualifique.")
        it['efeitos'] = [{"id": "escolha_da_dadiva_epica", "tipo": "escolha",
                          "rotulo": "Escolha um talento de Dádiva Épica", "quantidade": 1,
                          "de": {"catalogo": "talentos",
                                 "filtro": {"categoria": "epico"}},
                          "efeito_por_item_escolhido": {"tipo": "conceder_talento",
                                                        "talento_id": "{{escolhido}}"}}]
        it['revisao'] = {"status": "ok", "notas": "Fechado com o capítulo 5."}
        n_dadiva += 1
    gravar('dados/caracteristicas.json', caracs)

    print(f"talentos: {d['total']} "
          f"(origem {sum(1 for i in d['itens'] if i['categoria']=='origem')}, "
          f"geral {sum(1 for i in d['itens'] if i['categoria']=='geral')}, "
          f"estilo_de_luta {sum(1 for i in d['itens'] if i['categoria']=='estilo_de_luta')}, "
          f"epico {sum(1 for i in d['itens'] if i['categoria']=='epico')})")
    print(f"marcadores removidos: {removidos} | ainda pendentes: "
          f"{[i['id'] for i in d['itens'] if i.get('pendente')]}")
    print(f"catálogos auxiliares novos: {len(AUXILIARES)}")
    print(f"tipos de efeito novos: {n_tipos} | alvos novos: {n_alvos} | "
          f"impedimentos novos: {n_imp}")
    print(f"característica 'Dádiva Épica' das classes fechada: {n_dadiva}")


if __name__ == '__main__':
    main()
