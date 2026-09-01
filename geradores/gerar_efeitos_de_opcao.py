# -*- coding: utf-8 -*-
"""Dá efeitos estruturados às opções de catálogo do lote Bárbaro + Ladino.

Antes deste script, `efeitos_de_golpe_astuto`, `efeitos_de_golpe_brutal` e as três
`opcoes_de_*_dos_selvagens` traziam só `descricao_curta` — texto. `manobras` e
`invocacoes_misticas`, dos lotes anteriores, já traziam `efeitos` executáveis.
Aqui as 20 opções passam a ter a mesma forma das manobras.

CD do Golpe Astuto: 8 + mod. de Destreza + Bônus de Proficiência (p. 141).
"""
import json, collections

CD_LADINO = ["8", "mod:DES", "prof"]


def carregar(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=collections.OrderedDict)


def gravar(p, d):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def aplicar(caminho, mapa):
    d = carregar(caminho)
    for i in d['itens']:
        if i['id'] in mapa:
            i['efeitos'] = mapa[i['id']]
    faltando = [i['id'] for i in d['itens'] if not i.get('efeitos')]
    gravar(caminho, d)
    return faltando


# ------------------------------------------------- Golpe Astuto (Ladino, p. 141)
GOLPE_ASTUTO = {
    "envenenar": [
        {"tipo": "conceder_condicao", "condicao_id": "envenenado", "beneficiario": "alvo",
         "salvaguarda": {"atributo": "CON", "cd": CD_LADINO},
         "duracao": "1 minuto",
         "repete_salvaguarda": {"quando": "fim_do_turno_do_alvo", "encerra_em_sucesso": True},
         "pre_requisitos": [{"tipo": "item", "chave": "kit_de_veneno",
                             "revisao": "duvida", "nota": "id depende do cap. 6"}]}
    ],
    "retirada": [
        {"tipo": "conceder_velocidade", "tipo_deslocamento": "caminhada",
         "modo": "movimento_imediato",
         "formula": [{"op": "div_arred_baixo", "args": ["deslocamento", "2"]}],
         "sem_provocar_ataques_de_oportunidade": True,
         "momento": "imediatamente_apos_o_ataque"}
    ],
    "tropeco": [
        {"tipo": "conceder_condicao", "condicao_id": "caido", "beneficiario": "alvo",
         "salvaguarda": {"atributo": "DES", "cd": CD_LADINO},
         "condicao": {"todas": ["alvo_de_tamanho_ate:grande"]}}
    ],
    "aturdir": [
        {"tipo": "restringir_movimento", "beneficiario": "alvo",
         "salvaguarda": {"atributo": "CON", "cd": CD_LADINO},
         "duracao": "proximo_turno_do_alvo",
         "limite": {"escolher": 1, "entre": ["mover", "acao", "acao_bonus"]},
         "nota": "No próximo turno o alvo faz apenas UMA das três coisas."}
    ],
    "obscurecer": [
        {"tipo": "conceder_condicao", "condicao_id": "cego", "beneficiario": "alvo",
         "salvaguarda": {"atributo": "DES", "cd": CD_LADINO},
         "duracao": "ate_o_fim_do_proximo_turno_do_alvo"}
    ],
    "nocaute": [
        {"tipo": "conceder_condicao", "condicao_id": "inconsciente", "beneficiario": "alvo",
         "salvaguarda": {"atributo": "CON", "cd": CD_LADINO},
         "duracao": "1 minuto",
         "encerra_se": [{"gatilho": "alvo_sofre_qualquer_dano"}],
         "repete_salvaguarda": {"quando": "fim_do_turno_do_alvo", "encerra_em_sucesso": True}}
    ],
    "ataque_escondido": [
        {"tipo": "alterar_condicao", "condicao_id": "invisivel",
         "operacao": "impedir_encerramento",
         "gatilho_impedido": "atacar",
         "condicao": {"todas": ["condicao_obtida_por:esconder",
                                {"alguma": ["termina_o_turno_atras_de:cobertura_tres_quartos",
                                            "termina_o_turno_atras_de:cobertura_total"]}]},
         "nota": "O ataque normalmente encerra a Invisibilidade da ação Esconder; aqui não encerra."}
    ],
}

# ------------------------------------------------ Golpe Brutal (Bárbaro, p. 53)
GOLPE_BRUTAL = {
    "golpe_debilitador": [
        {"tipo": "modificador", "alvo": "deslocamento", "beneficiario": "alvo",
         "valor": ["-4.5"], "unidade": "metros", "empilha": "substitui",
         "duracao": "ate_inicio_do_seu_proximo_turno",
         "limite": {"por_alvo": 1, "resolucao": "mais_recente_prevalece"}}
    ],
    "golpe_poderoso": [
        {"tipo": "restringir_movimento", "modo": "empurrar", "beneficiario": "alvo",
         "distancia_m": 4.5, "direcao": "para_longe_de_voce"},
        {"tipo": "conceder_velocidade", "tipo_deslocamento": "caminhada",
         "modo": "movimento_imediato",
         "formula": [{"op": "div_arred_baixo", "args": ["deslocamento", "2"]}],
         "direcao": "em_direcao_ao_alvo",
         "sem_provocar_ataques_de_oportunidade": True}
    ],
    "golpe_atordoante": [
        {"tipo": "vantagem", "alvo": "salvaguarda", "modo": "desvantagem",
         "beneficiario": "alvo", "duracao": "proxima_salvaguarda_do_alvo"},
        {"tipo": "impedir", "alvo": "reacao", "beneficiario": "alvo",
         "restrito_a": "ataque_de_oportunidade",
         "duracao": "ate_inicio_do_seu_proximo_turno"}
    ],
    "golpe_destruidor": [
        {"tipo": "modificador", "alvo": "jogada_de_ataque", "valor": ["5"],
         "beneficiario": "proxima_criatura_que_atacar_o_alvo",
         "duracao": "ate_inicio_do_seu_proximo_turno",
         "limite": {"por_jogada": 1, "nota": "Uma jogada só recebe um bônus de Golpe Destruidor por vez."}}
    ],
}

# ------------------------- Coração Selvagem: Fúria dos Selvagens (nível 3, p. 56)
FURIA_SELVAGENS = {
    "aguia": [
        {"tipo": "conceder_acao", "id": "correr_e_desengajar_ao_entrar_em_furia",
         "custo": "incluso_na_acao_bonus_da_furia",
         "acoes": ["correr", "desengajar"], "momento": "ao_ativar_a_furia"},
        {"tipo": "conceder_acao", "id": "correr_e_desengajar_em_furia",
         "custo": "acao_bonus", "acoes": ["correr", "desengajar"],
         "condicao": {"todas": ["ativo:furia"]}}
    ],
    "lobo": [
        {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "vantagem",
         "beneficiario": "aliados",
         "condicao": {"todas": ["ativo:furia", "alvo_inimigo_a_ate:1.5m_de_voce"]}}
    ],
    "urso": [
        {"tipo": "alterar_dano", "tipo_dano": "todos", "operacao": "resistencia",
         "excecoes": ["energetico", "necrotico", "psiquico", "radiante"],
         "condicao": {"todas": ["ativo:furia"]}}
    ],
}

# ---------------------- Coração Selvagem: Aspecto dos Selvagens (nível 6, p. 56)
ASPECTO_SELVAGENS = {
    "coruja": [
        {"tipo": "conceder_sentido", "sentido": "visao_no_escuro", "alcance_m": 18,
         "empilha": "soma",
         "nota": "Se já tiver Visão no Escuro, o alcance aumenta em 18 m."}
    ],
    "pantera": [
        {"tipo": "conceder_velocidade", "tipo_deslocamento": "escalada",
         "formula": ["deslocamento"]}
    ],
    "salmao": [
        {"tipo": "conceder_velocidade", "tipo_deslocamento": "natacao",
         "formula": ["deslocamento"]}
    ],
}

# ------------------------ Coração Selvagem: Poder dos Selvagens (nível 14, p. 56)
PODER_SELVAGENS = {
    "carneiro": [
        {"tipo": "conceder_condicao", "condicao_id": "caido", "beneficiario": "alvo",
         "momento": "ao_acertar_ataque_corpo_a_corpo",
         "condicao": {"todas": ["ativo:furia", "alvo_de_tamanho_ate:grande"]},
         "nota": "Sem salvaguarda: o livro impõe a condição direto (p. 56)."}
    ],
    "falcao": [
        {"tipo": "conceder_velocidade", "tipo_deslocamento": "voo",
         "formula": ["deslocamento"],
         "condicao": {"todas": ["ativo:furia", "flag:sem_armadura"]}}
    ],
    "leao": [
        {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "desvantagem",
         "beneficiario": "inimigos_a_ate_1_5m_de_voce",
         "excecao_de_alvo": ["voce", "outro_barbaro_com_leao_ativo"],
         "condicao": {"todas": ["ativo:furia"]}}
    ],
}

if __name__ == '__main__':
    lotes = [
        ('dados/catalogos/efeitos_de_golpe_astuto.json', GOLPE_ASTUTO),
        ('dados/catalogos/efeitos_de_golpe_brutal.json', GOLPE_BRUTAL),
        ('dados/catalogos/opcoes_de_furia_dos_selvagens.json', FURIA_SELVAGENS),
        ('dados/catalogos/opcoes_de_aspecto_dos_selvagens.json', ASPECTO_SELVAGENS),
        ('dados/catalogos/opcoes_de_poder_dos_selvagens.json', PODER_SELVAGENS),
    ]
    for caminho, mapa in lotes:
        faltando = aplicar(caminho, mapa)
        nome = caminho.split('/')[-1]
        print(f"{nome:40s} {len(mapa)} com efeitos"
              + (f" | SEM EFEITOS: {faltando}" if faltando else ""))
