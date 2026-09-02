# -*- coding: utf-8 -*-
"""Fase 13 — funde o vocabulário de runtime que estava escrito de dois jeitos.

O `PLANO-MOTOR.md` §5 registrou o defeito: os tipos de efeito são catálogo
validado, mas o que aparece DENTRO deles — predicado de condição, gatilho,
duração — nunca foi declarado. Em doze fases isso acumulou sinônimo acidental:
o mesmo evento escrito `entrar_em_furia` num lugar e `ao_entrar_em_furia` noutro.

No motor, cada par desses vira ou dois `case` fazendo a mesma coisa, ou um efeito
que nunca dispara. Não é dívida cosmética.

Este gerador roda DEPOIS de todos os geradores de conteúdo e reescreve o dado
inteiro por tabelas explícitas. Ele é a única fonte da fusão: quem quiser saber
por que `criacao` sumiu lê aqui, e não um diff.

Regra de ouro: **falha se uma origem declarada for encontrada só em parte**. Tabela
que casa com metade do dado é tabela mentindo, e vale erro de build.

O caso de NENHUMA origem aparecer é diferente e legítimo: quer dizer que este
gerador já rodou sobre este `dados/` e não há o que fundir. Ele então não faz nada
e sai limpo — senão seria impossível rodá-lo duas vezes, e o `reconstruir.py`
precisa poder.

Quatro operações:
  1. FUSÃO de token — dois nomes para a mesma coisa viram um.
  2. `momento` some. Era usado como sinônimo de `gatilho` em 257 de 264 vezes.
     O que sobra — a fase dentro da resolução — vira o campo novo `fase`.
  3. DURAÇÃO de tempo vira objeto {quantidade: <fórmula>, unidade: ...}.
     Prosa como "minutos iguais ao nível de Bruxo" o motor não executa.
  4. COMPARAÇÃO vira objeto {comparar, op, com}, com os dois lados em fórmula.
     Havia oito sintaxes diferentes, incluindo espaços dentro do id.
"""
import json, os, sys, collections

DADOS = 'dados'

# ---------------------------------------------------------------- 1. durações

DURACOES = {
    # até o fim do turno atual — eram OITO grafias
    'ate_o_fim_do_turno': 'ate_o_fim_do_turno_atual',
    'ate_o_fim_deste_turno': 'ate_o_fim_do_turno_atual',
    'este_turno': 'ate_o_fim_do_turno_atual',
    'neste_turno': 'ate_o_fim_do_turno_atual',
    'mesmo_turno': 'ate_o_fim_do_turno_atual',
    'resto_do_turno': 'ate_o_fim_do_turno_atual',
    'resto_do_turno_atual': 'ate_o_fim_do_turno_atual',
    # o artigo que faltava
    'ate_inicio_do_seu_proximo_turno': 'ate_o_inicio_do_seu_proximo_turno',
    'ate_inicio_do_proximo_turno_do_alvo': 'ate_o_inicio_do_proximo_turno_do_beneficiario',
    'ate_o_inicio_do_proximo_turno_do_alvo': 'ate_o_inicio_do_proximo_turno_do_beneficiario',
    # o referente sai do campo `beneficiario`, não do nome da duração: 'dela',
    # 'dele', 'do_alvo' e 'do_aliado' eram quatro nomes para o mesmo turno.
    'ate_o_fim_do_proximo_turno_dela': 'ate_o_fim_do_proximo_turno_do_beneficiario',
    'ate_o_fim_do_proximo_turno_dele': 'ate_o_fim_do_proximo_turno_do_beneficiario',
    'ate_o_fim_do_proximo_turno_do_alvo': 'ate_o_fim_do_proximo_turno_do_beneficiario',
    'ate_o_fim_do_proximo_turno_do_aliado': 'ate_o_fim_do_proximo_turno_do_beneficiario',
    'proximo_turno_do_alvo': 'ate_o_fim_do_proximo_turno_do_beneficiario',
    'proxima_salvaguarda_do_alvo': 'ate_a_proxima_salvaguarda_do_beneficiario',
    'proxima_jogada_de_ataque_do_turno': 'ate_a_proxima_jogada_de_ataque_do_turno',
    # descansos
    'ate_o_descanso_longo': 'ate_o_proximo_descanso_longo',
    'ate_o_descanso_longo_ou_novo_uso': 'ate_o_proximo_descanso_longo_ou_novo_uso',
    # p. 155: "dura até você iniciar um Descanso Curto ou Longo". O nome antigo
    # dizia só 'descanso' e deixava a pergunta em aberto.
    'ate_o_proximo_descanso': 'ate_iniciar_descanso_curto_ou_longo',
}

# duração de tempo: deixa de ser prosa e vira objeto executável
TEMPOS = {
    '1 minuto': {'quantidade': ['1'], 'unidade': 'minuto'},
    '10 minutos': {'quantidade': ['10'], 'unidade': 'minuto'},
    '1 hora': {'quantidade': ['1'], 'unidade': 'hora'},
    '8 horas': {'quantidade': ['8'], 'unidade': 'hora'},
    '24 horas': {'quantidade': ['24'], 'unidade': 'hora'},
    'minutos iguais ao nível de Bruxo': {
        'quantidade': ['nivel_classe:bruxo'], 'unidade': 'minuto'},
    'nivel de Feiticeiro em minutos': {
        'quantidade': ['nivel_classe:feiticeiro'], 'unidade': 'minuto'},
}

# ---------------------------------------------------------------- 2. gatilhos

GATILHOS = {
    # "quando esta coisa entra na ficha" — eram três nomes, um deles ('criacao')
    # dizendo respeito só a classe e outro ('ao_adquirir_o_talento') citando o
    # tipo de conteúdo, coisa que o motor não pode conhecer.
    'ao_adquirir_o_talento': 'ao_adquirir',
    'criacao': 'ao_adquirir',
    # Fúria
    'entrar_em_furia': 'ao_entrar_em_furia',
    'ao_ativar_a_furia': 'ao_entrar_em_furia',
    # conjuração
    'conjurar_magia': 'ao_conjurar',
    'conjurar_magia_de_feiticeiro_com_espaco':
        'apos_conjurar_magia_de_feiticeiro_com_espaco',
    # erro de digitação: dispersar/dispensar, os dois para "encerrar a forma"
    'dispersar': 'dispensar',
    # d20 natural
    'resultado_1': 'resultado_natural_1',
    # jogada de ataque como evento
    'voce_realiza_jogada_de_ataque': 'realizar_jogada_de_ataque',
    'jogada_de_ataque': 'realizar_jogada_de_ataque',
    # acerto
    'ao_acertar_ataque_com_arma': 'acerto_com_arma',
    'ao_acertar_ataque_com_arma_ou_da_forma_animal':
        'acerto_com_arma_ou_ataque_da_forma_animal',
    'ao_acertar_ataque_corpo_a_corpo': 'acerto_corpo_a_corpo',
    'apos_acertar': 'acerto',
    'a_cada_acerto': 'acerto',
    'no_acerto': 'acerto',
    # ser atingido
    'ser_atingido_por_ataque': 'ser_atingido_por_jogada_de_ataque',
    # fim de turno
    'fim_de_cada_turno_seu': 'fim_do_seu_turno',
    # zerar PV
    'chegar_a_0_pv': 'reduzido_a_0_pontos_de_vida',
    'reduzido_a_zero_pv': 'reduzido_a_0_pontos_de_vida',
    # falhar num teste de d20: o campo `alvo` já diz se é salvaguarda ou teste
    'apos_falhar': 'falha',
    'falhar_em_salvaguarda': 'falha',
    # sofrer dano: o referente está em `beneficiario`/`alvo`, não no nome
    'a_criatura_sofre_dano': 'alvo_sofre_dano',
    'alvo_sofre_qualquer_dano': 'alvo_sofre_dano',
    # p. 262, Repreensão Diabólica: "Reação, que você realiza ao receber dano de
    # uma criatura a até 18 metros". O parser cortou a frase no meio e sobrou um
    # gatilho com espaço no meio do id.
    'ao receber': 'sofrer_dano_de_criatura_a_ate_18m',
    # ação executada: havia a família `executar_acao*` e um `acao_atacar` solto
    'acao_atacar': 'executar_acao:atacar',
    # conjurar Destruição Divina: o 'imediatamente_apos' não distinguia nada
    'imediatamente_apos_conjurar:destruicao_divina': 'conjurar:destruicao_divina',
    # acerto é, por definição, de jogada de ataque
    'acerto_com_jogada_de_ataque': 'acerto',
}

# ------------------------------------------------------------------ 4. custos

# `custo` guardava duas coisas: o que a característica CUSTA (uma ação, a Reação,
# seu movimento) e QUANDO ela se usa. As manobras do Guerreiro carregavam a
# segunda no campo da primeira. Janela de uso é gatilho.
CUSTO_VIRA_GATILHO = {
    'no_acerto': 'acerto',
    'no_erro': 'erro',
    'no_teste': 'teste_de_atributo',
}

CUSTOS = {
    'nenhum': 'livre',
}

# o que sobra de `momento` depois da fusão: a fase DENTRO da resolução do gatilho
FASES = {'antes_da_jogada', 'apos_a_jogada', 'antes_ou_depois_da_acao_adicional'}

# ------------------------------------------------------------- 3. predicados

PREDICADOS = {
    # armadura: havia a família `armadura:<categoria>` e um `usando:` solto
    'usando:armadura_pesada': 'armadura:pesada',
    # proficiência: cinco grafias para "sou proficiente naquilo que está em jogo"
    'proficiente_na_pericia_ou_ferramenta': 'proficiente_em:pericia_ou_ferramenta_do_teste',
    'com_proficiencia_em_pericia_ou_ferramenta': 'proficiente_em:pericia_ou_ferramenta_do_teste',
    'proficiente_na_salvaguarda': 'proficiente_em:salvaguarda_do_teste',
    'ja_proficiente_em_salvaguarda:SAB': 'proficiente_em:salvaguarda:SAB',
    'proficiente_com_a_arma': 'proficiente_em:arma_do_ataque',
    'proficiente_em:percepcao': 'proficiente_em:pericia:percepcao',
    # salvaguarda e concentração
    'alvo_falhou_na_salvaguarda': 'falhou_na_salvaguarda',
    'para_manter_concentracao': 'manter_concentracao',
    # tamanho do alvo: forma paramétrica, que o motor resolve com o catálogo
    'alvo_grande_ou_menor': 'alvo_de_tamanho_ate:grande',
    'alvo_enorme_ou_menor': 'alvo_de_tamanho_ate:enorme',
    # amedrontado por uma fonte: o sujeito é sempre a criatura afetada
    'amedrontado_por:repudiar_inimigos': 'alvo_amedrontado_por:repudiar_inimigos',
    # ação Atacar
    'executou:atacar': 'na_acao_atacar',
    'executou:atacar_no_turno': 'executou:atacar_neste_turno',
    'executou_a_acao_atacar_com_essa_arma': 'executou:atacar_com_essa_arma',
    # escudo: `usando_escudo` e `flag:sem_escudo` eram o mesmo fato e seu oposto
    'usando_escudo': 'segurando:escudo',
    # feitiçaria inata é um efeito ativo, como Fúria e Sintonia Elemental
    'flag:feiticaria_inata_ativa': 'ativo:feiticaria_inata',
    # distância: 1,5 m se escreve `1_5m` em todo o resto do dado
    'alvo_inimigo_a_ate:1.5m_de_voce': 'alvo_inimigo_a_ate:1_5m',
    'inimigo_a_vista_terminou_turno_a_ate:1.5m': 'inimigo_a_vista_terminou_turno_a_ate:1_5m',
    # já existia a forma paramétrica `alcance_minimo_m:<n>`
    'alcance >= 3m': 'alcance_minimo_m:3',
    # 'desarmado' colidia de nome com a AÇÃO Ataque Desarmado, e dizia a mesma
    # coisa que 'sem_arma_na_mao'
    'desarmado': 'sem_arma_na_mao',
    # o mesmo alvo do ataque que disparou — acertando ou errando, é o mesmo alvo
    'mesmo_alvo_atingido': 'mesmo_alvo',
}

# predicado que era a NEGAÇÃO de outro escrito por extenso
NEGACOES = {
    'flag:sem_escudo': 'segurando:escudo',
    'flag:sem_armadura': 'armadura:qualquer',
    'nao_proficiente_na_pericia': 'proficiente_em:pericia_do_teste',
}

# `requisitos` é vocabulário próprio, quase todo em objeto tipado. O que sobra de
# string solta compartilha família com os predicados e seguia duas convenções:
# arma se EMPUNHA, objeto se SEGURA.
REQUISITOS = {
    'equipado:escudo': 'segurando:escudo',
    'segurando:arma_com_acuidade': 'empunhando:arma_com_acuidade',
}

# comparação: era prosa dentro do id, em oito sintaxes
COMPARACOES = {
    'espaco_usado_circulo >= 2':
        {'comparar': ['circulo_do_espaco_usado'], 'op': 'gte', 'com': ['2']},
    'pv_atual >= 1':
        {'comparar': ['pv_atual'], 'op': 'gte', 'com': ['1']},
    'recurso:pontos_de_foco.atual<=3':
        {'comparar': ['recurso:pontos_de_foco.atual'], 'op': 'lte', 'com': ['3']},
    'recurso:forma_selvagem.atual == 0':
        {'comparar': ['recurso:forma_selvagem.atual'], 'op': 'eq', 'com': ['0']},
    'recurso:feiticaria_inata_usos.atual == 0':
        {'comparar': ['recurso:feiticaria_inata_usos.atual'], 'op': 'eq', 'com': ['0']},
    'recurso:mares_do_caos_usos.atual == 0':
        {'comparar': ['recurso:mares_do_caos_usos.atual'], 'op': 'eq', 'com': ['0']},
    'valor_de_atributo:DES>=16':
        {'comparar': ['valor_de_atributo:DES'], 'op': 'gte', 'com': ['16']},
    'usos_atuais_menores_que:2':
        {'comparar': ['usos_atuais'], 'op': 'lt', 'com': ['2']},
    'nivel_maior_que_1':
        {'comparar': ['nivel_do_personagem'], 'op': 'gt', 'com': ['1']},
    'soma_menor_que_1':
        {'comparar': ['soma_do_calculo'], 'op': 'lt', 'com': ['1']},
    'arma_corpo_a_corpo_e_forca_menor_que:13':
        {'todas': ['arma:corpo_a_corpo',
                   {'comparar': ['valor_de_atributo:FOR'], 'op': 'lt', 'com': ['13']}]},
    'arma_a_distancia_e_destreza_menor_que:13':
        {'todas': ['arma:a_distancia',
                   {'comparar': ['valor_de_atributo:DES'], 'op': 'lt', 'com': ['13']}]},
}

# a condição de Sangrando já era árvore de fórmula, com um operador de comparação
# que só ela usava. Vira a mesma forma das outras.
COMPARACAO_EM_ARVORE = {
    'menor_ou_igual': 'lte',
}

# ------------------------------------------------------------------ execução

usos = collections.Counter()


def normaliza_condicao(o):
    """Reescreve uma árvore de condição."""
    if isinstance(o, str):
        if o in COMPARACOES:
            usos['pred:' + o] += 1
            return json.loads(json.dumps(COMPARACOES[o]))
        if o in NEGACOES:
            usos['pred:' + o] += 1
            return {'nao': NEGACOES[o]}
        if o in PREDICADOS:
            usos['pred:' + o] += 1
            return PREDICADOS[o]
        return o
    if isinstance(o, list):
        return [normaliza_condicao(x) for x in o]
    if isinstance(o, dict):
        # {"op": "menor_ou_igual", "args": [a, b]} -> {comparar, op, com}
        if o.get('op') in COMPARACAO_EM_ARVORE and len(o.get('args', [])) == 2:
            usos['pred:op:' + o['op']] += 1
            return {'comparar': [o['args'][0]], 'op': COMPARACAO_EM_ARVORE[o['op']],
                    'com': [o['args'][1]]}
        return {k: normaliza_condicao(v) for k, v in o.items()}
    return o


def anda(o):
    if isinstance(o, list):
        return [anda(x) for x in o]
    if not isinstance(o, dict):
        return o

    novo = collections.OrderedDict()
    for k, v in o.items():
        # --- condição
        if k in ('condicao', 'condicional', 'condicao_do_alvo'):
            novo[k] = normaliza_condicao(v)
            continue

        # --- custo
        if k == 'custo' and isinstance(v, str):
            if v in CUSTO_VIRA_GATILHO:
                usos['cus:' + v] += 1
                novo['gatilho'] = CUSTO_VIRA_GATILHO[v]
            elif v in CUSTOS:
                usos['cus:' + v] += 1
                novo[k] = CUSTOS[v]
            else:
                novo[k] = v
            continue

        # --- requisitos
        if k in ('requisitos', 'pre_requisitos') and isinstance(v, list):
            saida = []
            for x in v:
                if isinstance(x, str) and x in REQUISITOS:
                    usos['req:' + x] += 1
                    saida.append(REQUISITOS[x])
                else:
                    saida.append(anda(x))
            novo[k] = saida
            continue

        # --- gatilho
        if k == 'gatilho' and isinstance(v, str):
            if v in GATILHOS:
                usos['gat:' + v] += 1
                v = GATILHOS[v]
            novo[k] = v
            continue

        # --- momento: o campo inteiro deixa de existir
        if k == 'momento' and isinstance(v, str):
            usos['momento'] += 1
            if v in FASES:
                novo['fase'] = v
            elif 'gatilho' in o:
                # gatilho e momento diziam a mesma coisa; o momento era redundante
                usos['momento:redundante'] += 1
            else:
                novo['gatilho'] = GATILHOS.get(v, v)
                if v in GATILHOS:
                    usos['gat:' + v] += 1
            continue

        # --- duração
        if k == 'duracao' and isinstance(v, str):
            if v in TEMPOS:
                usos['dur:' + v] += 1
                novo[k] = json.loads(json.dumps(TEMPOS[v]))
            elif v in DURACOES:
                usos['dur:' + v] += 1
                novo[k] = DURACOES[v]
            else:
                novo[k] = v
            continue
        if k == 'duracao_do_efeito' and isinstance(v, str) and v in TEMPOS:
            usos['dur:' + v] += 1
            novo[k] = json.loads(json.dumps(TEMPOS[v]))
            continue

        novo[k] = anda(v)
    return novo


def main():
    arquivos = []
    for d, _, fs in os.walk(DADOS):
        for f in sorted(fs):
            if f.endswith('.json'):
                arquivos.append(os.path.join(d, f))

    for p in arquivos:
        d = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
        json.dump(anda(d), open(p, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)

    # a tabela tem de casar com o dado: origem declarada que não apareceu é
    # tabela mentindo, e isso é erro de build.
    faltando = []
    for tabela, prefixo in ((DURACOES, 'dur:'), (TEMPOS, 'dur:'),
                            (GATILHOS, 'gat:'), (PREDICADOS, 'pred:'),
                            (NEGACOES, 'pred:'), (COMPARACOES, 'pred:'),
                            (REQUISITOS, 'req:'), (CUSTOS, 'cus:'),
                            (CUSTO_VIRA_GATILHO, 'cus:')):
        for origem in tabela:
            if not usos.get(prefixo + origem):
                faltando.append(prefixo + origem)
    if not usos.get('pred:op:menor_ou_igual'):
        faltando.append('pred:op:menor_ou_igual')

    total = sum(v for k, v in usos.items() if k != 'momento:redundante')
    print('fase 13: %d ocorrências normalizadas em %d arquivos' % (total, len(arquivos)))
    print('  duração .... %d' % sum(v for k, v in usos.items() if k.startswith('dur:')))
    print('  gatilho .... %d' % sum(v for k, v in usos.items() if k.startswith('gat:')))
    print('  predicado .. %d' % sum(v for k, v in usos.items() if k.startswith('pred:')))
    print('  custo ...... %d' % sum(v for k, v in usos.items() if k.startswith('cus:')))
    print('  requisito .. %d' % sum(v for k, v in usos.items() if k.startswith('req:')))
    print('  momento .... %d (%d eram redundantes com o gatilho ao lado)'
          % (usos['momento'], usos['momento:redundante']))

    if not total:
        print('  (nada a fundir: este dado já está normalizado)')
        return 0

    if faltando:
        print('\nERRO: a tabela casou só em parte — estas origens não apareceram:')
        for f in sorted(faltando):
            print('  ' + f)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
