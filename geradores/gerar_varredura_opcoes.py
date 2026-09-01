# -*- coding: utf-8 -*-
"""Varredura: dá efeitos estruturados às opções de catálogo que ainda eram só texto.

Complementa `gerar_efeitos_de_opcao.py`, que cobriu os cinco catálogos do lote
Bárbaro + Ladino. Aqui entram os das classes anteriores:

  monge   — efeitos_da_mao_espalmada (3)
  bruxo   — efeitos_dos_passos_feericos (4)
  mago    — beneficios_do_terceiro_olho (3)
  clerigo — ordens_divinas (2), efeitos_de_canalizar_divindade (2),
            opcoes_de_golpes_abencoados (2)
  druida  — ordens_primais (2), constelacoes (3), opcoes_de_furia_elemental (2),
            terrenos_druidicos (4)

Os `terrenos_druidicos` tinham um buraco maior que a falta de efeitos: as quatro
tabelas de Magias de Círculo Druídico (p. 98) nunca haviam sido extraídas, e a
característica que escolhe o terreno aplicava um efeito nomeado que não existia.
"""
import json, collections

CD_MAGIA = "cd_para_evitar_sua_magia"  # CD de conjuração da própria classe


def carregar(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=collections.OrderedDict)


def aplicar(caminho, mapa, descricoes=None, duvidas=()):
    d = carregar(caminho)
    for i in d['itens']:
        if i['id'] in mapa:
            i['efeitos'] = mapa[i['id']]
        if i['id'] in duvidas:
            i['revisao'] = {"status": "duvida", "notas": duvidas[i['id']]}
        if descricoes and i['id'] in descricoes:
            i['descricao_curta'] = descricoes[i['id']]
    sem = [i['id'] for i in d['itens'] if not i.get('efeitos')]
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    return sem


# ------------------------------------ Monge: Técnica da Mão Espalmada (p. 162)
MAO_ESPALMADA = {
    "derrubar": [
        {"tipo": "conceder_condicao", "condicao_id": "caido", "beneficiario": "alvo",
         "salvaguarda": {"atributo": "DES", "cd": ["8", "mod:SAB", "prof"]}}
    ],
    "desorientar": [
        {"tipo": "impedir", "alvo": "reacao", "beneficiario": "alvo",
         "restrito_a": "ataque_de_oportunidade",
         "duracao": "ate_o_inicio_do_proximo_turno_do_alvo"}
    ],
    "empurrar": [
        {"tipo": "restringir_movimento", "modo": "empurrar", "beneficiario": "alvo",
         "distancia_m": 4.5, "direcao": "para_longe_de_voce",
         "salvaguarda": {"atributo": "FOR", "cd": ["8", "mod:SAB", "prof"]}}
    ],
}

# ------------------------------- Bruxo: Passos Feéricos (p. 75) e Fuga em Névoa
PASSOS_FEERICOS = {
    "passo_provocante": [
        {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "desvantagem",
         "beneficiario": "criaturas_a_ate_1_5m_do_espaco_de_saida",
         "excecao_de_alvo": ["voce"],
         "salvaguarda": {"atributo": "SAB", "cd": [CD_MAGIA]},
         "duracao": "ate_inicio_do_seu_proximo_turno"}
    ],
    "passo_revigorante": [
        {"tipo": "pontos_de_vida_temporarios", "formula": ["1d10"],
         "beneficiario": "voce_ou_criatura_a_vista_a_ate_3m",
         "momento": "imediatamente_apos_o_teleporte"}
    ],
    "passo_desvanecedor": [
        {"tipo": "conceder_condicao", "condicao_id": "invisivel", "beneficiario": "voce",
         "duracao": "ate_inicio_do_seu_proximo_turno",
         "encerra_se": [{"gatilho": "jogada_de_ataque"}, {"gatilho": "causar_dano"},
                        {"gatilho": "conjurar_magia"}]}
    ],
    "passo_terrivel": [
        {"tipo": "dano", "formula_dado": "2d10", "tipo_dano": "psiquico",
         "alvo": "criaturas_a_ate_1_5m_do_espaco_escolhido",
         "escolha_de_espaco": ["saida", "chegada"],
         "salvaguarda": {"atributo": "SAB", "cd": [CD_MAGIA], "em_sucesso": "nenhum_dano"}}
    ],
}

# ------------------------------- Mago (Adivinhador): Terceiro Olho (p. 155)
TERCEIRO_OLHO = {
    "compreensao_superior": [
        {"tipo": "substituir_regra", "chave": "ler_qualquer_idioma",
         "duracao": "ate_o_proximo_descanso",
         "revisao": "duvida",
         "nota": "Ler qualquer idioma não tem primitivo próprio no esquema; fica como regra "
                 "declarada até existir um efeito de compreensão de idiomas."}
    ],
    "ver_o_invisivel": [
        {"tipo": "conjurar_sem_espaco", "magia": "ver_o_invisivel"}
    ],
    "visao_no_escuro": [
        {"tipo": "conceder_sentido", "sentido": "visao_no_escuro", "alcance_m": 36,
         "empilha": "substitui_se_maior", "duracao": "ate_o_proximo_descanso"}
    ],
}

DUVIDA_TERCEIRO_OLHO = {
    "compreensao_superior": "Ler qualquer idioma não tem primitivo próprio no esquema; "
                            "fica como substituir_regra até existir um efeito de compreensão "
                            "de idiomas (provável no cap. 5, com os talentos).",
}

# ---------------------------------------------- Clérigo: Ordem Divina (p. 82)
ORDENS_DIVINAS = {
    "protetor": [
        {"tipo": "conceder_proficiencia", "categoria": "arma", "chave": "marciais",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "armadura", "chave": "pesada",
         "nivel_dominio": "treinado"}
    ],
    "taumaturgo": [
        {"id": "clerigo_truque_taumaturgo", "tipo": "escolha",
         "rotulo": "Truque adicional de Clérigo", "quantidade": 1,
         "de": {"catalogo": "magias", "filtro": {"lista": "clerigo", "nivel": 0}},
         "efeito_por_item_escolhido": {"tipo": "desbloquear_magias",
                                       "magia": "{{escolhido}}", "modo": "conhecida"}},
        {"tipo": "modificador", "alvo": "teste_de_atributo:arcanismo",
         "valor": [{"op": "max", "args": ["mod:SAB", "1"]}], "empilha": "soma"},
        {"tipo": "modificador", "alvo": "teste_de_atributo:religiao",
         "valor": [{"op": "max", "args": ["mod:SAB", "1"]}], "empilha": "soma"}
    ],
}

# ------------------------------------ Clérigo: Canalizar Divindade (p. 82-83)
CANALIZAR = {
    "centelha_divina": [
        {"tipo": "cura", "formula": ["1d8", "mod:SAB"],
         "alvo": "criatura_a_vista_a_ate_9m", "custo": "acao_usar_magia",
         "escala_por_nivel": {"7": "2d8", "13": "3d8", "18": "4d8"},
         "alternativa": "dano"},
        {"tipo": "dano", "formula_dado": "1d8", "formula_bonus": ["mod:SAB"],
         "alvo": "criatura_a_vista_a_ate_9m",
         "escolher_tipo_dano": ["necrotico", "radiante"],
         "salvaguarda": {"atributo": "CON", "cd": [CD_MAGIA],
                         "em_sucesso": "metade_do_dano"},
         "escala_por_nivel": {"7": "2d8", "13": "3d8", "18": "4d8"}}
    ],
    "expulsar_mortos_vivos": [
        {"tipo": "conceder_condicao", "condicao_id": "amedrontado",
         "alvo": "mortos_vivos_a_escolha_a_ate_9m", "custo": "acao_usar_magia",
         "salvaguarda": {"atributo": "SAB", "cd": [CD_MAGIA]}, "duracao": "1 minuto",
         "encerra_se": [{"gatilho": "alvo_sofre_dano"},
                        {"condicao_id": "incapacitado", "de": "voce"},
                        {"gatilho": "voce_morre"}],
         "efeito_adicional": "o alvo tenta se afastar o máximo possível de você nos turnos dele"},
        {"tipo": "conceder_condicao", "condicao_id": "incapacitado",
         "alvo": "mortos_vivos_a_escolha_a_ate_9m",
         "salvaguarda": {"atributo": "SAB", "cd": [CD_MAGIA]}, "duracao": "1 minuto",
         "encerra_se": [{"gatilho": "alvo_sofre_dano"},
                        {"condicao_id": "incapacitado", "de": "voce"},
                        {"gatilho": "voce_morre"}]}
    ],
}

# ------------------------------------ Clérigo: Golpes Abençoados (p. 83)
GOLPES_ABENCOADOS = {
    "conjuracao_poderosa": [
        {"tipo": "modificador", "alvo": "jogada_de_dano", "valor": ["mod:SAB"],
         "empilha": "soma", "condicao": {"todas": ["magia:truque_de_clerigo"]}}
    ],
    "golpe_divino": [
        {"tipo": "dano", "formula_dado": "1d8", "modo": "dano_adicional",
         "escolher_tipo_dano": ["necrotico", "radiante"],
         "frequencia": "uma_vez_por_turno",
         "momento": "ao_acertar_ataque_com_arma",
         "escala_por_nivel": {"14": "2d8"}}
    ],
}

# ------------------------------------------- Druida: Ordem Primal (p. 92)
ORDENS_PRIMAIS = {
    "protetor": [
        {"tipo": "conceder_proficiencia", "categoria": "arma", "chave": "marciais",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "armadura", "chave": "media",
         "nivel_dominio": "treinado"}
    ],
    "xama": [
        {"id": "druida_truque_xama", "tipo": "escolha",
         "rotulo": "Truque adicional de Druida", "quantidade": 1,
         "de": {"catalogo": "magias", "filtro": {"lista": "druida", "nivel": 0}},
         "efeito_por_item_escolhido": {"tipo": "desbloquear_magias",
                                       "magia": "{{escolhido}}", "modo": "conhecida"}},
        {"tipo": "modificador", "alvo": "teste_de_atributo:arcanismo",
         "valor": [{"op": "max", "args": ["mod:SAB", "1"]}], "empilha": "soma"},
        {"tipo": "modificador", "alvo": "teste_de_atributo:natureza",
         "valor": [{"op": "max", "args": ["mod:SAB", "1"]}], "empilha": "soma"}
    ],
}

# -------------------------------- Druida: Fúria Elemental (p. 94), com o nível 15
FURIA_ELEMENTAL = {
    "ataque_primal": [
        {"tipo": "dano", "formula_dado": "1d8", "modo": "dano_adicional",
         "escolher_tipo_dano": ["eletrico", "gelido", "igneo", "trovejante"],
         "momento_da_escolha": "ao_acertar",
         "frequencia": "uma_vez_por_turno",
         "momento": "ao_acertar_ataque_com_arma_ou_da_forma_animal",
         "escala_por_nivel": {"15": "2d8"}}
    ],
    "conjuracao_poderosa": [
        {"tipo": "modificador", "alvo": "jogada_de_dano", "valor": ["mod:SAB"],
         "empilha": "soma", "condicao": {"todas": ["magia:truque_de_druida"]}},
        {"tipo": "modificador", "alvo": "alcance_de_magia", "valor": ["90"],
         "unidade": "metros", "empilha": "substitui", "nivel_minimo": 15,
         "condicao": {"todas": ["magia:truque_de_druida", "alcance_minimo_m:3"]}}
    ],
}

# ---------------------------- Druida (Círculo das Estrelas): Constelações (p. 98)
CONSTELACOES = {
    "arqueiro": [
        {"tipo": "conceder_ataque", "quantidade": ["1"], "tipo_ataque": "magico_a_distancia",
         "custo": "acao_bonus", "alcance_m": 18,
         "dano": {"formula_dado": "1d8", "formula_bonus": ["mod:SAB"],
                  "tipo_dano": "radiante"},
         "momento": "ao_ativar_e_nos_turnos_seguintes"}
    ],
    "dragao": [
        {"tipo": "tratar_resultado_minimo", "alvo": "teste_de_atributo:INT",
         "minimo": 10},
        {"tipo": "tratar_resultado_minimo", "alvo": "teste_de_atributo:SAB",
         "minimo": 10},
        {"tipo": "tratar_resultado_minimo", "alvo": "salvaguarda:CON",
         "minimo": 10, "condicao": {"todas": ["para_manter_concentracao"]}}
    ],
    "taca": [
        {"tipo": "cura", "formula": ["1d8", "mod:SAB"],
         "beneficiario": "voce_ou_criatura_a_ate_9m",
         "gatilho": "conjurar_magia_com_espaco_que_restaure_pontos_de_vida"}
    ],
}

# ------------------- Druida (Círculo da Terra): Magias de Círculo Druídico (p. 98)
def tabela_terreno(nome, linhas):
    return [{"tipo": "magias_de_patrono",
             "tabela": {"nome": nome,
                        "fonte": {"capitulo": 3, "pagina_livro": 98, "pagina_pdf": 102},
                        "linhas": [{"nivel": n, "magias": m} for n, m in linhas]},
             "modo": "sempre_preparada",
             "nao_conta_para_o_limite": True}]


TERRENOS = {
    "arido": tabela_terreno("Terreno Árido", [
        (3, ["maos_flamejantes", "raio_de_fogo", "turvar"]),
        (5, ["bola_de_fogo"]), (7, ["malogro"]), (9, ["muralha_de_pedra"])]),
    "polar": tabela_terreno("Terreno Polar", [
        (3, ["nevoa_obscurecente", "paralisar_pessoa", "raio_de_gelo"]),
        (5, ["nevasca"]), (7, ["tempestade_glacial"]), (9, ["cone_de_frio"])]),
    "temperado": tabela_terreno("Terreno Temperado", [
        (3, ["passo_nebuloso", "sono", "toque_chocante"]),
        (5, ["relampago"]), (7, ["movimentacao_livre"]), (9, ["passo_arboreo"])]),
    "tropical": tabela_terreno("Terreno Tropical", [
        (3, ["bolha_acida", "raio_nauseante", "teia"]),
        (5, ["nuvem_fetida"]), (7, ["polimorfia"]), (9, ["praga_de_insetos"])]),
}

DESC_TERRENOS = {
    "arido": "Magias de Círculo Druídico de deserto e vulcão; Resistência a dano Ígneo pela Proteção Natural.",
    "polar": "Magias de Círculo Druídico de gelo e tundra; Resistência a dano Gélido pela Proteção Natural.",
    "temperado": "Magias de Círculo Druídico de floresta e campo; Resistência a dano Elétrico pela Proteção Natural.",
    "tropical": "Magias de Círculo Druídico de selva e pântano; Resistência a dano Venenoso pela Proteção Natural.",
}

if __name__ == '__main__':
    lotes = [
        ('efeitos_da_mao_espalmada', MAO_ESPALMADA, None),
        ('efeitos_dos_passos_feericos', PASSOS_FEERICOS, None),
        ('beneficios_do_terceiro_olho', TERCEIRO_OLHO, None, DUVIDA_TERCEIRO_OLHO),
        ('ordens_divinas', ORDENS_DIVINAS, None),
        ('efeitos_de_canalizar_divindade', CANALIZAR, None),
        ('opcoes_de_golpes_abencoados', GOLPES_ABENCOADOS, None),
        ('ordens_primais', ORDENS_PRIMAIS, None),
        ('opcoes_de_furia_elemental', FURIA_ELEMENTAL, None),
        ('constelacoes', CONSTELACOES, None),
        ('terrenos_druidicos', TERRENOS, DESC_TERRENOS),
    ]
    for lote in lotes:
        cat, mapa, desc = lote[0], lote[1], lote[2]
        duv = lote[3] if len(lote) > 3 else {}
        sem = aplicar(f'dados/catalogos/{cat}.json', mapa, desc, duv)
        print(f"{cat:34s} {len(mapa):2d} com efeitos"
              + (f" | SEM EFEITOS: {sem}" if sem else ""))
