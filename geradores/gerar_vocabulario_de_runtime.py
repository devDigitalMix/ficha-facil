# -*- coding: utf-8 -*-
"""Fase 13 — declara o vocabulário de runtime.

Os 103 tipos de efeito sempre foram catálogo validado. O que aparece DENTRO
deles — o predicado de uma condição, o gatilho que dispara, a duração, o custo —
nunca foi. Cresceu solto por doze fases, e foi assim que o mesmo evento acabou
escrito de dois jeitos (ver `gerar_normalizacao_vocabulario.py`).

Este arquivo é a lista fechada. Não é derivada do dado: é DECLARADA aqui, à mão.
A diferença é o ponto — catálogo que se deriva da saída aceita qualquer coisa que
a saída contenha, e não pega sinônimo nenhum. Este falha o build quando o dado
usa um token que ninguém declarou, e obriga quem inventar um termo novo a passar
por aqui e olhar se ele já não existe com outro nome.

Para o motor, é a lista do que ele precisa saber implementar: 152 predicados +
12 famílias, 127 gatilhos, 3 fases, 13 durações simbólicas e a forma de tempo,
9 custos, 5 modos de empilhamento. Antes desta fase essa lista não existia, e
descobri-la era tentativa e erro.

Não vai em `catalogos/`: o id de catálogo é `[a-z0-9_]+`, e estes tokens têm
argumento depois de dois-pontos (`condicao:incapacitado`). São vocabulário do
motor, não termo do livro.
"""
import json, os, sys, collections

DESTINO = 'dados/vocabulario_de_runtime.json'

PREDICADOS = [
    'a_fera_moveu_ao_menos_6m_ate_o_alvo', 'abriu_mao_da_vantagem',
    'acao:correr', 'acao:esconder', 'acerto', 'acerto_com_arma',
    'acerto_com_arma_corpo_a_corpo', 'acerto_com_arma_pesada',
    'acerto_com_ataque_de_oportunidade', 'acerto_com_ataque_desarmado',
    'acerto_com_ataque_furtivo', 'acerto_com_dano_contundente',
    'acerto_com_dano_cortante', 'acerto_com_dano_perfurante',
    'acerto_corpo_a_corpo', 'acerto_critico_com_arma_corpo_a_corpo',
    'acerto_critico_com_dano_contundente',
    'acerto_critico_com_dano_cortante',
    'acerto_critico_com_dano_perfurante', 'alcance_minimo_m:3',
    'aliado_a_ate_1_5m_do_alvo',
    'aliado_nao_incapacitado_a_ate_1_5m_do_alvo_e_sem_desvantagem',
    'alvo_a_ate_1_5m', 'alvo_a_ate_1_5m_da_ilusao',
    'alvo_a_ate_1_5m_da_montaria', 'alvo_ainda_nao_agiu',
    'alvo_alem_do_alcance_maximo', 'alvo_alem_do_alcance_normal',
    'alvo_amedrontado_por:anjo_vingador',
    'alvo_amedrontado_por:repudiar_inimigos', 'alvo_ao_alcance_da_sua_arma',
    'alvo_com_pv_abaixo_do_maximo', 'alvo_desmontado',
    'alvo_do_ataque_e_voce', 'alvo_e:imobilizador',
    'alvo_e_a_criatura_ligada', 'alvo_e_infero',
    'alvo_imobilizado_por_voce', 'alvo_inimigo_a_ate:1_5m',
    'alvo_maior_que_voce', 'alvo_marcado_por:marca_do_predador',
    'alvo_menor_que_a_montaria', 'alvo_pode_ve_lo', 'alvo_sob_danacao',
    'alvo_ve_a_ilusao', 'arma:a_distancia', 'arma:acuidade_ou_a_distancia',
    'arma:corpo_a_corpo', 'arma:propriedade:arremesso', 'arma_de_pacto',
    'arma_e_besta_leve', 'arma_magica', 'armadura:leve', 'armadura:media',
    'armadura:pesada', 'armadura:qualquer', 'atacante_a_ate_1_5m',
    'atacante_pode_ve_lo', 'atacou_com_arma_leve', 'ataque:a_distancia',
    'ataque_adicional_da_propriedade_leve', 'ataque_com_forca',
    'ataque_com_lamina_psiquica', 'ativo:feiticaria_inata', 'ativo:furia',
    'ativo:furia_dos_deuses', 'ativo:ira_do_mar',
    'ativo:sintonia_elemental', 'atributo_escolhido_na_danacao',
    'calculo_soma_destreza', 'causou_dano_elemental',
    'concentrando_em:telecinese', 'condicao_obtida_por:esconder',
    'conjurada_com_pontos_de_feiticaria',
    'conjurou_magia_de_escola:encantamento_ou_ilusao',
    'conjurou_magia_de_tempo:acao', 'contra:brilho_do_amanhecer',
    'criatura_tambem_faz_a_salvaguarda', 'dano_reduzido_a_zero',
    'depende_de:audicao', 'depende_de:visao', 'deslocamento_zero',
    'desvantagem_na_jogada', 'disfarcado_como_pessoa_especifica',
    'duas_maos_exceto_montado', 'efeito_ativo_que_aumenta_o_maximo',
    'efeito_ativo_que_reduz_o_maximo', 'em:meia_luz_ou_escuridao',
    'em_combate', 'em_forma_estrelada', 'em_forma_selvagem',
    'empunhando:arma_leve', 'empunhando_apenas:armas_de_monge',
    'empunhando_com_as_duas_maos', 'envolve_dancar', 'estado:sangrando',
    'executou:atacar_com_essa_arma', 'executou:atacar_neste_turno',
    'falhou_em:expulsar_mortos_vivos', 'falhou_na_salvaguarda',
    'fonte_do_medo_na_linha_de_visao', 'forcada_por:infero_ou_morto_vivo',
    'gastou_espaco_de_magia', 'gastou_ponto_de_foco',
    'inimigo_a_vista_terminou_turno_a_ate:1_5m',
    'inteiramente_na_escuridao', 'ja_soma_bonus_de_proficiencia',
    'ja_soma_modificador_no_dano', 'jogada_original_atinge_a_segunda',
    'magia:truque_de_clerigo', 'magia:truque_de_druida',
    'magia_com_alvo:voce_mesmo', 'magia_com_marcador:ritual',
    'magia_exige_concentracao', 'magia_nivel:0', 'magia_no_livro',
    'manter_concentracao', 'mesmo_alvo', 'montado',
    'moveu_1_5m_em_linha_reta_antes_do_ataque',
    'moveu_3m_em_linha_reta_ate_o_alvo', 'na_acao_atacar',
    'nenhuma_outra_arma', 'origem:magia', 'primeira_rodada',
    'proficiente_em:arma_do_ataque', 'proficiente_em:pericia:percepcao',
    'proficiente_em:pericia_do_teste',
    'proficiente_em:pericia_ou_ferramenta_do_teste',
    'proficiente_em:salvaguarda:SAB', 'proficiente_em:salvaguarda_do_teste',
    'reduziu_criatura_a_zero_pv_com_arma_corpo_a_corpo',
    'resultado_20_no_d20_de_ataque',
    'salvaguarda_de_concentracao_ou_teste_int_sab',
    'segunda_criatura_a_ate_1_5m_do_alvo',
    'segundo_alvo_a_ate_1_5m_do_primeiro', 'segurando:escudo',
    'segurando:mapa_estelar', 'sem_arma_na_mao', 'seu_turno',
    'tem_caracteristica_que_aumenta_o_maximo',
    'termina_o_turno_atras_de:cobertura_total',
    'termina_o_turno_atras_de:cobertura_tres_quartos', 'uma_mao',
    'usou:ataque_imprudente', 'usou:envenenar', 'usou:metabolismo_incomum',
    'vantagem_na_jogada', 'voando', 'voce_e_a_ilusao_a_ate_1_5m_do_alvo',
    'voce_invisivel_ao_conjurar', 'voce_pode_ver_o_atacante',
]

FAMILIAS_DE_PREDICADO = {
    'aliado_com_condicao':   'condicoes',
    'alvo_de_tamanho_ate':   'tamanhos',
    'condicao':              'condicoes',
    'contra_condicao':       'condicoes',
    'dano':                  'tipos_de_dano',
    'efeito_aplica':         'condicoes',
    'lista':                 'listas_de_magia',
    'magia_com_dano':        'tipos_de_dano',
    'magia_da_escola':       'escolas_de_magia',
    'montaria_com_condicao': 'condicoes',
    'para_encerrar_condicao': 'condicoes',
    'teste':                 None,
}

GATILHOS = [
    'a_fera_atinge_criatura_marcada_por:marca_do_predador',
    'a_ilusao_termina', 'acertar_ataque_de_oportunidade',
    'acertar_e_causar_dano_com_jogada_de_ataque', 'acerto',
    'acerto_com_arma', 'acerto_com_arma_a_ate_9m',
    'acerto_com_arma_de_pacto', 'acerto_com_arma_ou_ataque_da_forma_animal',
    'acerto_com_ataque_da_forma_selvagem', 'acerto_com_ataque_desarmado',
    'acerto_com_torrente_de_golpes', 'acerto_corpo_a_corpo',
    'acerto_critico', 'acerto_da_fera_que_causa_dano',
    'alvo_a_0_pontos_de_vida', 'alvo_sofre_dano',
    'antes_de_salvaguarda_contra_morte', 'ao_adquirir',
    'ao_assumir_a_forma', 'ao_atacante_jogar_o_d20', 'ao_ativar',
    'ao_ativar_e_nos_turnos_seguintes', 'ao_causar_dano_de_ataque_furtivo',
    'ao_comecar_a_conjurar', 'ao_conjurar', 'ao_conjurar_o_livro',
    'ao_entrar_em_furia', 'ao_equipar', 'ao_gastar_o_dado',
    'ao_jogar_o_d20', 'ao_ser_atingido_corpo_a_corpo', 'ao_usar',
    'apos_conjurar_magia_de_feiticeiro_com_espaco',
    'apos_magia_de_encantamento_ou_ilusao',
    'arma_a_mais_de_1_5m_por_1_minuto', 'cada_uso', 'causar_dano',
    'causar_dano_a_criatura_marcada_por:marca_do_predador',
    'causar_dano_com_ataque_ou_magia', 'causar_dano_com_o_item',
    'concentracao_quebrada', 'conectar_com_outra_criatura',
    'conjura_magia_com_componente_verbal', 'conjurar:destruicao_divina',
    'conjurar_magia_com_espaco_que_restaure_pontos_de_vida',
    'conjurar_magia_de_abjuracao_com_espaco',
    'conjurar_magia_de_adivinhacao', 'conjurar_magia_de_cura_com_espaco',
    'conjurar_magia_de_cura_em_outra_criatura',
    'conjurar_magia_que_restaura_pv', 'criar_ou_mover_a_ilusao',
    'criatura_a_ate_1_5m_desengaja_ou_ataca_outro_alvo',
    'criatura_entra_no_seu_alcance',
    'criatura_erra_ataque_corpo_a_corpo_contra_voce',
    'criatura_protegida_sofre_dano',
    'criatura_realiza_jogada_de_ataque_contra_voce',
    'criatura_sob:voto_de_inimizade_realiza_jogada_de_ataque',
    'dano_de:golpe_psionico', 'dano_de_ataque_furtivo_com_lamina_psiquica',
    'descanso_curto', 'descanso_curto_ou_longo', 'descanso_longo',
    'dispensar', 'distancia_maior_que_alcance_da_imobilizacao', 'encerrar',
    'encerrar_turno_em_luz_plena', 'encerrar_voluntariamente',
    'entrar_em_espaco_a_ate_1_5m_da_criatura',
    'entrar_na_emanacao_pela_primeira_vez_no_turno_ou_comecar_o_turno_nela',
    'erro', 'executar_acao', 'executar_acao:atacar', 'executar_acao_bonus',
    'executar_reacao', 'falha', 'fim_do_seu_turno', 'forcar_salvaguarda',
    'imediatamente_apos_jogar_iniciativa', 'imediatamente_apos_o_ataque',
    'imediatamente_apos_o_teleporte', 'imobilizador_incapacitado',
    'inicio_de_cada_turno_do_alvo',
    'inicio_do_seu_primeiro_turno_do_combate', 'inicio_do_seu_turno',
    'inicio_do_turno_do_inimigo_na_emanacao', 'inimigo_encontra_voce',
    'jogar_iniciativa', 'mais_tarde_no_mesmo_turno', 'manifestar_de_novo',
    'morte', 'nivel_1', 'nivel_18', 'nivel_2', 'nivel_20', 'nivel_3',
    'nivel_6', 'nivel_7', 'nivel_9', 'nivel_da_caracteristica',
    'novo_circulo_de_espacos_de_magia', 'queda',
    'realizar_jogada_de_ataque', 'reconjurar',
    'reduzido_a_0_pontos_de_vida', 'reduzido_a_0_pontos_de_vida_sem_morrer',
    'resultado_natural_1', 'retrair_as_asas', 'rito_de_1_minuto',
    'sair_como_acao_bonus', 'ser_atingido_por_jogada_de_ataque',
    'sofrer_dano', 'sofrer_dano_de_ataque_corpo_a_corpo',
    'sofrer_dano_de_criatura_a_ate_18m',
    'sofrer_dano_de_criatura_a_ate_1_5m',
    'sofrer_dano_de_um_dos_tipos_escolhidos', 'som_mais_alto_que_sussurro',
    'teste_de_atributo', 'teste_para_escapar', 'usar:recuperar_folego',
    'usar:surto_de_acao', 'usar_a_acao_bonus_de_novo',
    'usar_a_caracteristica_de_novo', 'usar_forma_selvagem_de_novo',
    'vestir_armadura_pesada', 'voce_morre',
    'voce_ou_criatura_a_vista_a_ate_36m_passa_em_salvaguarda_contra_amedrontado_ou_enfeiticado',
]

FASES = [
    'antes_da_jogada', 'antes_ou_depois_da_acao_adicional', 'apos_a_jogada',
]

DURACOES = [
    'ate_a_proxima_jogada_de_ataque_do_turno',
    'ate_a_proxima_salvaguarda_do_beneficiario',
    'ate_iniciar_descanso_curto_ou_longo',
    'ate_o_fim_do_proximo_turno_do_beneficiario',
    'ate_o_fim_do_seu_proximo_turno', 'ate_o_fim_do_turno_atual',
    'ate_o_inicio_do_proximo_turno_do_beneficiario',
    'ate_o_inicio_do_seu_proximo_turno', 'ate_o_proximo_descanso_longo',
    'ate_o_proximo_descanso_longo_ou_novo_uso', 'contra_esta_magia',
    'contra_o_ataque_que_disparou', 'esta_acao',
]

CUSTOS = [
    'acao', 'acao_bonus', 'acao_usar_magia',
    'incluso_na_acao_bonus_da_furia', 'livre', 'movimento', 'reacao',
    'reacao_do_aliado', 'substitui_ataque',
]

EMPILHAMENTOS = [
    'maior_valor', 'soma', 'substitui', 'substitui_se_maior', 'unico',
]

# unidades da duração de tempo, depois que ela deixou de ser prosa
UNIDADES_DE_DURACAO = ['minuto', 'hora', 'dia']

# a condição composta: um operador por objeto, aninhando
OPERADORES_LOGICOS = ['todas', 'alguma', 'nao']

# a comparação, depois que ela deixou de ser texto dentro do id
OPERADORES_DE_COMPARACAO = ['eq', 'ne', 'lt', 'lte', 'gt', 'gte']


def main():
    for nome, lista in (('predicados', PREDICADOS), ('gatilhos', GATILHOS),
                        ('fases', FASES), ('duracoes', DURACOES),
                        ('custos', CUSTOS), ('empilhamentos', EMPILHAMENTOS)):
        if len(set(lista)) != len(lista):
            vistos = collections.Counter(lista)
            print('ERRO: %s tem token repetido: %s'
                  % (nome, [k for k, v in vistos.items() if v > 1]))
            return 1

    doc = collections.OrderedDict([
        ('vocabulario_de_runtime', True),
        ('nota', 'Lista fechada do que o motor precisa saber interpretar. '
                 'Declarada a mão em geradores/gerar_vocabulario_de_runtime.py; '
                 'validar.py falha se o dado usar um token que nao esta aqui.'),
        ('operadores_logicos', OPERADORES_LOGICOS),
        ('operadores_de_comparacao', OPERADORES_DE_COMPARACAO),
        ('unidades_de_duracao', UNIDADES_DE_DURACAO),
        ('familias_de_predicado', collections.OrderedDict(
            sorted(FAMILIAS_DE_PREDICADO.items()))),
        ('predicados', sorted(PREDICADOS)),
        ('gatilhos', sorted(GATILHOS)),
        ('fases', sorted(FASES)),
        ('duracoes', sorted(DURACOES)),
        ('custos', sorted(CUSTOS)),
        ('empilhamentos', sorted(EMPILHAMENTOS)),
    ])
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    json.dump(doc, open(DESTINO, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    print('vocabulario de runtime: %d predicados (+%d familias), %d gatilhos, '
          '%d fases, %d duracoes, %d custos, %d empilhamentos'
          % (len(PREDICADOS), len(FAMILIAS_DE_PREDICADO), len(GATILHOS),
             len(FASES), len(DURACOES), len(CUSTOS), len(EMPILHAMENTOS)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
