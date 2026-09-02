# -*- coding: utf-8 -*-
"""Paráfrases dos traços, ações, ações bônus e reações do Apêndice B.

Mesma regra das magias: **o texto do livro não é copiado**. O parser lê os números
(CA, PV, atributos, dano, alcance) — que são fato de tabela e vão literais — e aqui
ficam as frases, escritas à mão.

A chave é (id_da_criatura, id_da_entrada). Quando duas criaturas têm o mesmo traço
com o mesmo texto, a chave curta (só o id da entrada) serve para as duas — o gerador
procura a específica primeiro. Ataque puro (só jogada, alcance e dano) NÃO entra
aqui: a descrição sai do próprio dado estruturado, marcada `descricao_derivada`.
"""

# ----------------------------------------------------- traços e ações repetidos
COMUNS = {
    'andar_na_teia':
        "Ignora restrições de movimento causadas por teias e sente onde está "
        "qualquer criatura em contato com a mesma teia.",
    'escalada_de_aranha':
        "Escala superfícies difíceis, inclusive tetos, sem teste de atributo.",
    'anfibio':
        "Respira ar e água.",
    'respirar_na_agua':
        "Só respira debaixo d'água.",
    'resistencia_a_magia':
        "Vantagem em salvaguardas contra magias e outros efeitos mágicos.",
    'taticas_de_grupo':
        "Vantagem numa jogada de ataque contra uma criatura se um aliado seu, não "
        "Incapacitado, estiver a até 1,5 m dela.",
    'invisibilidade':
        "Conjura Invisibilidade em si, sem componentes, usando Carisma como atributo "
        "de conjuração.",
    'sobrevoo':
        "Voar para fora do alcance de um inimigo não provoca Ataque de Oportunidade.",
    'rondar':
        "Move-se até metade do próprio Deslocamento sem provocar Ataques de "
        "Oportunidade e, no fim do movimento, pode executar a ação Esconder.",
    'alterar_forma':
        "Ação para assumir uma de três formas pequenas, ou voltar à verdadeira. Só o "
        "Deslocamento muda; o equipamento não se transforma. Morrendo, volta à forma "
        "verdadeira.",
}

# ------------------------------------------------------ específicas por criatura
DESCRICOES = {
    ('rato', 'agil'):
        "Sair do alcance de um inimigo não provoca Ataque de Oportunidade.",
    ('esfinge_maravilhosa', 'ampliar_engenhosidade_2_dia'):
        "Reação, quando ela ou alguém a até 9 m faz um teste de atributo ou "
        "salvaguarda: soma 2 ao resultado.",
    ('mula', 'animal_de_carga'):
        "Conta como um tamanho maior para calcular a capacidade de carga.",
    ('quasit', 'assustar_1_dia'):
        "Salvaguarda de Sabedoria CD 10 para uma criatura a até 6 m: falhando, fica "
        "Amedrontada, repetindo a salvaguarda no fim de cada turno dela e passando "
        "automaticamente depois de 1 minuto.",
    ('polvo', 'compressao'):
        "Passa por espaços de até 2,5 cm sem gastar movimento a mais.",
    ('cobra_constritora', 'constricao'):
        "Salvaguarda de Força CD 12 para uma criatura Média ou menor a até 1,5 m: "
        "falhando, sofre 3d4 de dano Contundente e fica Imobilizada (CD 12 para "
        "escapar).",
    ('pseudodragao', 'ferroada'):
        "Salvaguarda de Constituição CD 12 para uma criatura a até 1,5 m: falhando, "
        "sofre 2d4 de dano Venenoso e fica Envenenada por 1 hora; falhando por 5 ou "
        "mais, fica também Inconsciente até sofrer dano ou ser sacudida.",
    ('zumbi', 'fortitude_de_morto_vivo'):
        "Reduzido a 0 Pontos de Vida, faz salvaguarda de Constituição CD 5 + dano "
        "sofrido e fica com 1 Ponto de Vida se passar. Não vale contra dano Radiante "
        "nem contra Acerto Crítico.",
    ('javali', 'furia_sangrenta'):
        "Vantagem nas jogadas de ataque enquanto estiver Sangrando.",
    ('corvo', 'mimica'):
        "Imita sons simples que ouviu; quem ouve percebe a imitação com um teste de "
        "Sabedoria (Intuição) CD 10.",
    ('polvo', 'nuvem_de_tinta_1_dia'):
        "Reação, quando alguém termina o turno a até 1,5 m debaixo d'água: solta "
        "tinta num Cubo de 1,5 m centrado em si, que fica Totalmente Obscurecido por "
        "1 minuto, e nada o máximo do seu Deslocamento de Natação.",
    ('elefante', 'pisao'):
        "Salvaguarda de Destreza CD 16 para uma criatura Caída a até 1,5 m: 2d10 + 6 "
        "de dano Contundente, metade se passar.",
    ('crocodilo', 'prender_a_respiracao'):
        "Prende a respiração por 1 hora.",
    ('cavalo_marinho_gigante', 'propulsao'):
        "Debaixo d'água, move-se até metade do Deslocamento de Natação sem provocar "
        "Ataques de Oportunidade.",
    ('leao', 'rugido'):
        "Salvaguarda de Sabedoria CD 11 para uma criatura a até 4,5 m: falhando, fica "
        "Amedrontada até o início do próximo turno do leão.",
    ('gato', 'saltador'):
        "A distância de salto sai da Destreza, não da Força.",
    ('leao', 'salto_com_impulso'):
        "Movendo-se pelo menos 3 m, faz um Salto em Distância de até 7,5 m.",
    ('ra', 'salto_parado'):
        "Salta até 3 m em distância e 1,5 m em altura, com ou sem corrida.",
    ('aranha_gigante', 'teia_recarga_5_6'):
        "Salvaguarda de Destreza CD 13 para uma criatura à vista a até 18 m: "
        "falhando, fica Contida até a teia ser destruída (CA 10, 5 PV, Vulnerável a "
        "Ígneo, Imune a Psíquico e Venenoso).",
    ('sprite', 'ver_o_coracao'):
        "Salvaguarda de Carisma CD 10 para uma criatura a até 1,5 m — Celestiais, "
        "Ínferos e Mortos-Vivos falham automaticamente: falhando, o sprite conhece as "
        "emoções e o alinhamento dela.",
    ('diabrete', 'visao_diabolica'):
        "Escuridão Mágica não atrapalha a Visão no Escuro do diabrete.",
}

# ------------------- ataques que trazem regra além da jogada, do alcance e do dano
ATAQUES_COM_REGRA = {
    ('alce', 'cabecada_ariete'):
        "Movendo-se 6 m em linha reta até o alvo antes do ataque, causa 1d6 de dano "
        "Contundente a mais e derruba alvo Enorme ou menor.",
    ('cabra_gigante', 'cabecada_ariete'):
        "Movendo-se 6 m em linha reta até o alvo antes do ataque, causa 2d4 de dano "
        "Contundente a mais e derruba alvo Enorme ou menor.",
    ('cavalo_de_guerra', 'cascos'):
        "Movendo-se 6 m em linha reta até o alvo antes do ataque, causa 2d4 de dano "
        "Contundente a mais e derruba alvo Enorme ou menor.",
    ('javali', 'investida'):
        "Movendo-se 6 m em linha reta até o alvo antes do ataque, causa 1d6 de dano "
        "Perfurante a mais e derruba alvo Grande ou menor.",
    ('elefante', 'investida'):
        "Movendo-se 6 m em linha reta até o alvo antes do ataque, também derruba o "
        "alvo.",
    ('tigre', 'bote'):
        "Com Vantagem na jogada de ataque, causa 1d6 de dano Cortante a mais e "
        "derruba alvo Enorme ou menor.",
    ('crocodilo', 'mordida'):
        "Alvo Médio ou menor fica Imobilizado (CD 12 para escapar) e, enquanto "
        "estiver assim, também Contido.",
    ('lobo', 'mordida'):
        "Alvo Médio ou menor fica Caído.",
    ('caranguejo_gigante', 'garra'):
        "Alvo Médio ou menor fica Imobilizado (CD 11 para escapar). São duas garras, "
        "cada uma podendo agarrar um alvo.",
}

# ------------------------------------------------------------- Ataques Múltiplos
MULTIATAQUE = {
    'pantera': "Um ataque de Bote e um uso de Rondar.",
    'tigre': "Um ataque de Bote e um uso de Rondar.",
    'elefante': "Dois ataques de Investida.",
    'gorila': "Dois ataques de Punho.",
    'leao': "Dois ataques de Dilacerar; um deles pode virar um Rugido.",
    'pseudodragao': "Dois ataques de Mordida.",
    'urso_negro': "Dois ataques de Dilacerar.",
    'urso_pardo': "Um ataque de Mordida e um de Garras.",
}


def buscar(id_criatura, id_entrada):
    """A específica vence a comum; sem nenhuma das duas, devolve None."""
    if (id_criatura, id_entrada) in DESCRICOES:
        return DESCRICOES[(id_criatura, id_entrada)]
    if (id_criatura, id_entrada) in ATAQUES_COM_REGRA:
        return ATAQUES_COM_REGRA[(id_criatura, id_entrada)]
    if id_entrada == 'ataques_multiplos' and id_criatura in MULTIATAQUE:
        return MULTIATAQUE[id_criatura]
    return COMUNS.get(id_entrada)
