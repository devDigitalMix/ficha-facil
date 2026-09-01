# -*- coding: utf-8 -*-
"""Pontos de Vida máximos e temporários viram dado (cap. 1 p. 28-29, cap. 2 p. 39 e 42, Ap. C).

O buraco: a Resiliência Dracônica do Feiticeiro aponta um modificador para
`pontos_de_vida_maximos` — e esse valor derivado NÃO EXISTIA. Havia
`pontos_de_vida_no_nivel_1` e `pontos_de_vida_por_nivel`, os dois sem parcelas, e
nada que somasse as duas coisas e recebesse bônus de fora. Sem isso o backend não
teria onde encaixar o +N do Dragão, o aumento retroativo quando a Constituição
sobe, o +5 de Auxílio ou a redução de Moléstia.

Agora existem dois derivados:

1. `pontos_de_vida_maximos` — a conta inteira, com as parcelas rotuladas para o
   log de proveniência, mais as regras que o livro dá em volta dela: o mínimo de
   1 por nível, o recálculo retroativo quando o modificador de Constituição sobe
   (p. 42) e a morte quando o máximo chega a 0 (p. 28).

2. `pontos_de_vida_temporarios` — que NÃO é um valor somado à ficha. É um
   amortecedor com quatro regras próprias (p. 28-29): some primeiro, não acumula
   (o jogador escolhe qual fonte fica), não é cura e não devolve consciência, e
   acaba no Descanso Longo. Guardar isso como dado impede o backend de tratar
   PV temporário como PV.

Além disso o script conserta duas coisas que o buraco escondia:
  · a Forma Selvagem guardava os PV temporários num campo solto dentro de
    `regras_enquanto_multimorfado` em vez de um efeito de verdade;
  · 16 magias mexem em PV máximos ou temporários e nenhuma declarava isso em
    campo estruturado — só na paráfrase.
"""
import json, collections

CAT = 'dados/catalogos'
DERIVADOS = f'{CAT}/valores_derivados.json'
ALVOS = f'{CAT}/alvos.json'
MAGIAS = f'{CAT}/magias.json'
CARACS = 'dados/caracteristicas.json'


def carregar(p):
    return json.load(open(p, encoding='utf-8'),
                     object_pairs_hook=collections.OrderedDict)


def gravar(p, d):
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def fonte(cap, pag):
    return {"capitulo": cap, "pagina_livro": pag, "pagina_pdf": pag + 4}


# ------------------------------------------------------------------ derivados
# A tabela de PV fixos por nível (p. 42). O livro imprime os números; guardo os
# números, não a conta que eu deduziria deles.
PV_FIXOS = [
    {"dado_de_vida": 12, "classes": ["barbaro"], "pv_por_nivel": 7},
    {"dado_de_vida": 10, "classes": ["guardiao", "guerreiro", "paladino"],
     "pv_por_nivel": 6},
    {"dado_de_vida": 8, "classes": ["bardo", "bruxo", "clerigo", "druida", "ladino",
                                    "monge"], "pv_por_nivel": 5},
    {"dado_de_vida": 6, "classes": ["feiticeiro", "mago"], "pv_por_nivel": 4},
]

MAXIMOS = collections.OrderedDict([
    ("id", "pontos_de_vida_maximos"),
    ("nome", "Pontos de Vida Máximos"),
    ("descricao_curta",
     "O total quando você não está ferido: os Pontos de Vida do nível 1, mais os de cada "
     "nível seguinte, mais os bônus de características e magias, menos as reduções."),
    ("formula", [
        {"op": "soma", "args": ["pontos_de_vida_no_nivel_1",
                                "soma_dos_niveis_seguintes",
                                "bonus_de_caracteristicas",
                                "bonus_temporarios_de_maximo"]},
        {"op": "menos", "args": ["reducoes_de_maximo"]},
    ]),
    ("parcelas", [
        {"rotulo": "Pontos de Vida do nível 1", "chave": "pontos_de_vida_no_nivel_1",
         "sempre": True},
        {"rotulo": "Pontos de Vida dos níveis seguintes",
         "chave": "soma_dos_niveis_seguintes", "condicao": "nivel_maior_que_1"},
        {"rotulo": "bônus de características", "chave": "bonus_de_caracteristicas",
         "condicao": "tem_caracteristica_que_aumenta_o_maximo"},
        {"rotulo": "bônus temporário (magia ou efeito)",
         "chave": "bonus_temporarios_de_maximo",
         "condicao": "efeito_ativo_que_aumenta_o_maximo"},
        {"rotulo": "reduções do máximo", "chave": "reducoes_de_maximo",
         "condicao": "efeito_ativo_que_reduz_o_maximo"},
    ]),
    ("regras", [
        {"chave": "minimo_por_nivel", "texto": "Cada nível soma no mínimo 1 Ponto de Vida, "
                                               "mesmo com modificador de Constituição "
                                               "negativo.", "fonte": fonte(2, 42)},
        {"chave": "recalculo_retroativo_de_constituicao",
         "texto": "Quando o modificador de Constituição sobe 1, os Pontos de Vida máximos "
                  "sobem 1 POR NÍVEL já alcançado, não só no nível atual.",
         "formula_do_ajuste": [{"op": "mult", "args": ["delta_do_mod_CON",
                                                       "nivel_do_personagem"]}],
         "fonte": fonte(2, 42)},
        {"chave": "maximo_zero_e_morte",
         "texto": "A criatura morre se os Pontos de Vida máximos chegarem a 0.",
         "fonte": fonte(1, 28)},
        {"chave": "cura_nao_ultrapassa",
         "texto": "A cura nunca leva os Pontos de Vida atuais acima do máximo; o excedente "
                  "é perdido.", "fonte": fonte(1, 27)},
    ]),
    ("nota", "Os Pontos de Vida ATUAIS não são um derivado: são estado de jogo que o "
             "backend guarda. O que a base entrega é o teto e de que parcelas ele vem."),
    ("fonte", fonte(2, 39)),
])

TEMPORARIOS = collections.OrderedDict([
    ("id", "pontos_de_vida_temporarios"),
    ("nome", "Pontos de Vida Temporários"),
    ("descricao_curta",
     "Um amortecedor concedido por magias e características. Não é Ponto de Vida: some "
     "primeiro, não acumula, não é cura e acaba no Descanso Longo."),
    ("formula", ["valor_da_fonte_em_vigor"]),
    ("parcelas", [
        {"rotulo": "fonte em vigor", "chave": "valor_da_fonte_em_vigor", "sempre": True},
    ]),
    ("nao_acumula", True),
    ("regras", [
        {"chave": "perde_primeiro",
         "texto": "Ao sofrer dano, os temporários são perdidos primeiro; o resto sai dos "
                  "Pontos de Vida.", "fonte": fonte(1, 28)},
        {"chave": "nao_acumulam",
         "texto": "Não acumulam. Recebendo mais enquanto já tem, o JOGADOR escolhe se "
                  "mantém os que tem ou fica com os novos — não é automático nem é o "
                  "maior valor.", "fonte": fonte(1, 29)},
        {"chave": "nao_sao_pv_nem_cura",
         "texto": "Não somam aos Pontos de Vida, a cura não os restaura, e recebê-los não "
                  "é cura. Uma criatura com os Pontos de Vida cheios ainda pode recebê-los.",
         "fonte": fonte(1, 29)},
        {"chave": "nao_devolvem_consciencia",
         "texto": "Com 0 Pontos de Vida, receber temporários não faz recuperar a "
                  "consciência.", "fonte": fonte(1, 29)},
        {"chave": "duracao",
         "texto": "Duram até se esgotarem ou até o fim de um Descanso Longo.",
         "fonte": fonte(1, 29)},
    ]),
    ("nota", "Por isso é derivado próprio e não uma parcela de pontos_de_vida_maximos: "
             "somar as duas coisas seria o erro clássico."),
    ("fonte", fonte(1, 28)),
])

# parcelas para os dois derivados de PV que já existiam e estavam sem elas
PARCELAS_NIVEL_1 = [
    {"rotulo": "Dado de Vida da classe (valor máximo)", "chave": "dado_de_vida_da_classe",
     "sempre": True},
    {"rotulo": "Constituição", "chave": "mod:CON", "sempre": True},
]
PARCELAS_POR_NIVEL = [
    {"rotulo": "Dado de Vida rolado, ou o valor fixo da classe",
     "chave": "rolagem_ou_valor_fixo_do_dado_de_vida", "sempre": True},
    {"rotulo": "Constituição", "chave": "mod:CON", "sempre": True},
    {"rotulo": "piso de 1 por nível", "chave": "minimo_1",
     "condicao": "soma_menor_que_1"},
]

# ------------------------------------------------------ ligação alvo → derivado
# Foi assim que o buraco apareceu: um alvo apontando para um derivado inexistente.
# Declarando a ligação, o validador cobra.
LIGACOES = {
    "teste_de_atributo": "teste_de_atributo",
    "salvaguarda": "salvaguarda",
    "iniciativa": "iniciativa",
    "ca_total": "classe_de_armadura",
    "jogada_de_ataque_magico": "jogada_de_ataque_magico",
    "cd_para_evitar_sua_magia": "cd_para_evitar_sua_magia",
    "pontos_de_vida_maximos": "pontos_de_vida_maximos",
}

ALVO_NOVO = collections.OrderedDict([
    ("id", "pontos_de_vida_temporarios"),
    ("nome", "Pontos de Vida Temporários"),
    ("descricao_curta", "O amortecedor de PV temporários. Alvo de efeitos que concedem ou "
                        "substituem a fonte em vigor."),
    ("derivado_id", "pontos_de_vida_temporarios"),
])

# --------------------------------------------------------- magias que mexem em PV
# Levantadas varrendo o corpo das 391 entradas do cap. 7 atrás de "Pontos de Vida
# Temporários" e "Pontos de Vida máximos" — 17 magias, uma delas (Convocar Celestial)
# só no bloco de estatísticas da criatura invocada, que está fora do escopo.
PV_DE_MAGIA = {
    "armadura_de_agathys": {
        "temporarios": {"formula": ["5"], "beneficiario": "voce",
                        "aprimoramento_por_circulo_acima": ["5"],
                        "encerra_a_magia_ao_zerar": True}},
    "vitalidade_vazia": {
        "temporarios": {"formula": ["2d4", "4"], "beneficiario": "voce",
                        "aprimoramento_por_circulo_acima": ["5"]}},
    "heroismo": {
        "temporarios": {"formula": ["mod:atributo_de_conjuracao"],
                        "beneficiario": "alvo",
                        "momento": "inicio_de_cada_turno_do_alvo"}},
    "palavra_de_poder_fortificar": {
        "temporarios": {"total": ["120"], "dividido_entre": "ate_6_criaturas_a_vista",
                        "beneficiario": "criaturas_a_sua_escolha"}},
    "polimorfia": {
        "temporarios": {"formula": ["pontos_de_vida_da_forma"], "beneficiario": "alvo",
                        "encerra_a_magia_ao_zerar": True}},
    "polimorfia_total": {
        "temporarios": {"formula": ["pontos_de_vida_da_forma"], "beneficiario": "alvo",
                        "encerra_a_magia_ao_zerar": True}},
    "metamorfose": {
        "temporarios": {"formula": ["pontos_de_vida_da_forma"], "beneficiario": "voce",
                        "encerra_a_magia_ao_zerar": True}},
    "formas_animais": {
        "temporarios": {"formula": ["pontos_de_vida_da_forma"], "beneficiario": "alvos",
                        "encerra_a_magia_no_alvo_ao_zerar": True}},
    "auxilio": {
        "maximos": {"aumento": ["5"], "tambem_aumenta_os_atuais": True,
                    "beneficiario": "ate_3_criaturas", "duracao": "8 horas",
                    "aprimoramento_por_circulo_acima": ["5"]}},
    "banquete_de_herois": {
        "maximos": {"aumento": ["2d10"], "tambem_aumenta_os_atuais": True,
                    "beneficiario": "ate_12_criaturas_que_participam",
                    "duracao": "24 horas"}},
    "molestia": {
        "maximos": {"reducao": ["igual_ao_dano_sofrido"], "piso": 1,
                    "beneficiario": "alvo",
                    "condicao": {"todas": ["falhou_na_salvaguarda"]}}},
    "aura_de_vida": {
        "maximos": {"impede_reducao": True,
                    "beneficiario": "voce_e_aliados_na_emanacao"}},
    "restauracao_maior": {
        "maximos": {"remove_reducao": True, "beneficiario": "alvo_tocado",
                    "nota": "É uma das opções da magia, escolhida na conjuração."}},
    "simulacro": {
        "maximos": {"da_criatura_criada": "metade_do_original",
                    "nota": "Vale para a duplicata, não para o conjurador."}},
    "mao_de_bigby": {
        "pontos_de_vida_do_efeito": {"formula": ["seus_pontos_de_vida_maximos"],
                                     "alvo": "a_mao", "ca": 20,
                                     "encerra_a_magia_ao_zerar": True}},
    "sinal_de_esperanca": {
        "cura_maximizada": {"beneficiario": "alvos",
                            "nota": "Qualquer cura recebida pelos alvos rende o número "
                                    "máximo possível — não mexe no teto de PV."}},
}


def main():
    # ---------------------------------------------------------------- derivados
    d = carregar(DERIVADOS)
    idx = {i['id']: i for i in d['itens']}
    idx['pontos_de_vida_no_nivel_1']['parcelas'] = PARCELAS_NIVEL_1
    idx['pontos_de_vida_no_nivel_1']['tabela_por_classe'] = PV_FIXOS
    p = idx['pontos_de_vida_por_nivel']
    p['parcelas'] = PARCELAS_POR_NIVEL
    p['tabela_por_classe'] = PV_FIXOS
    p['fonte'] = fonte(2, 42)
    p['nota'] = ("O livro imprime a tabela Pontos de Vida Fixos por Classe (p. 42); os "
                 "valores estão em tabela_por_classe, não deduzidos do Dado de Vida.")
    d['itens'] = [i for i in d['itens']
                  if i['id'] not in ('pontos_de_vida_maximos',
                                     'pontos_de_vida_temporarios')]
    d['itens'].append(MAXIMOS)
    d['itens'].append(TEMPORARIOS)
    d['total'] = len(d['itens'])
    gravar(DERIVADOS, d)

    # ------------------------------------------------------------------- alvos
    a = carregar(ALVOS)
    if not any(i['id'] == ALVO_NOVO['id'] for i in a['itens']):
        a['itens'].append(ALVO_NOVO)
    n_lig = 0
    for i in a['itens']:
        if i['id'] in LIGACOES:
            i['derivado_id'] = LIGACOES[i['id']]
            n_lig += 1
    a['total'] = len(a['itens'])
    gravar(ALVOS, a)

    # ------------------------------------------------- Forma Selvagem: campo → efeito
    c = carregar(CARACS)
    n_fs = 0
    for it in c['itens']:
        for e in it.get('efeitos') or []:
            if e.get('tipo') != 'forma_selvagem':
                continue
            regras = e.get('regras_enquanto_multimorfado') or {}
            pv = regras.pop('pv_temporarios', None)
            if pv is None:
                continue
            e.setdefault('efeitos', []).insert(0, collections.OrderedDict([
                ("tipo", "pontos_de_vida_temporarios"),
                ("formula", pv),
                ("beneficiario", "voce"),
                ("momento", "ao_assumir_a_forma"),
                ("nota", "Antes isto era um campo solto dentro de "
                         "regras_enquanto_multimorfado; virou efeito para o backend não "
                         "precisar conhecer o nome do campo. O Círculo da Lua substitui "
                         "esta fórmula por três vezes o nível de Druida.")]))
            n_fs += 1
    gravar(CARACS, c)

    # ------------------------------------------------------------------ magias
    m = carregar(MAGIAS)
    n_mg = 0
    for i in m['itens']:
        bloco = PV_DE_MAGIA.get(i['id'])
        if not bloco:
            continue
        i['pontos_de_vida'] = collections.OrderedDict(bloco)
        n_mg += 1
    gravar(MAGIAS, m)

    print(f"valores_derivados: {d['total']} itens "
          f"(+pontos_de_vida_maximos, +pontos_de_vida_temporarios)")
    print(f"alvos ligados a um derivado: {n_lig}")
    print(f"Forma Selvagem convertida para efeito: {n_fs}")
    print(f"magias com bloco 'pontos_de_vida': {n_mg}")


if __name__ == '__main__':
    main()
