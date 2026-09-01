# -*- coding: utf-8 -*-
"""Duas coisas que estavam implícitas e viram dado.

1. As 10 propriedades de arma (p. 214-217) ganham `efeitos` executáveis. Eram só
   `descricao_curta` — o mesmo defeito que a varredura tirou dos catálogos de
   opção, e que aqui impedia o backend de saber que Acuidade deixa escolher o
   atributo ou que Pesada dá Desvantagem abaixo de 13.

2. A proficiência com armas das classes deixa de ser uma string codificada
   ('categoria:marcial+propriedade:acuidade_ou_leve') e vira filtro estruturado,
   que o validador resolve contra o catálogo de itens e conta.
"""
import json, collections, re

PROPS = 'dados/catalogos/propriedades_de_arma.json'
CLASSES = 'dados/classes.json'


def f(pag):
    return {"capitulo": 6, "pagina_livro": pag, "pagina_pdf": pag + 4}


EFEITOS = {
    "acuidade": [
        {"tipo": "substituir_atributo",
         "alvo_do_calculo": ["jogada_de_ataque_com_arma", "dano_de_arma"],
         "escolha_entre": ["FOR", "DES"],
         "mesmo_nas_duas_jogadas": True,
         "momento": "ao_equipar"},
    ],
    "alcance": [
        {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "desvantagem",
         "condicao": {"todas": ["alvo_alem_do_alcance_normal"]}},
        {"tipo": "impedir", "alvo": "atacar_ou_alvejar",
         "condicao": {"todas": ["alvo_alem_do_alcance_maximo"]}},
    ],
    "arremesso": [
        {"tipo": "conceder_ataque", "quantidade": ["1"], "tipo_ataque": "a_distancia",
         "modo": "arremessar_a_arma",
         "saca_como_parte_do_ataque": True,
         "atributo": "mantem_o_da_arma",
         "nota": "Arma corpo a corpo arremessada usa o mesmo atributo do ataque corpo "
                 "a corpo dela; com Acuidade, vale a escolha feita."},
    ],
    "duas_maos": [
        {"tipo": "substituir_regra", "chave": "exige_duas_maos_para_atacar",
         "revisao": "duvida",
         "nota": "Restrição de empunhadura: precisa de um primitivo de mãos ocupadas, "
                 "que ainda não existe no esquema."},
    ],
    "extensao": [
        {"tipo": "modificador", "alvo": "alcance_do_ataque_desarmado", "valor": ["1.5"],
         "unidade": "metros", "empilha": "soma",
         "aplica_a": ["ataque_com_a_arma", "ataque_de_oportunidade_com_a_arma"],
         "nota": "Some 1,5 m ao alcance com esta arma, inclusive para Ataques de "
                 "Oportunidade."},
    ],
    "leve": [
        {"tipo": "conceder_ataque", "quantidade": ["1"], "custo": "acao_bonus",
         "condicao": {"todas": ["executou:atacar_no_turno", "empunhando:arma_leve"]},
         "exige_outra_arma_leve": True,
         "sem_modificador_no_dano": True,
         "excecao": "modificador negativo continua sendo somado",
         "momento": "mais_tarde_no_mesmo_turno"},
    ],
    "municao": [
        {"tipo": "substituir_regra", "chave": "consome_municao_por_ataque",
         "revisao": "duvida",
         "consumo_por_ataque": 1,
         "recuperacao_apos_o_combate": {"fracao": "metade", "arredondamento": "baixo",
                                        "tempo": "1 minuto"},
         "nota": "Consumo de recurso por ataque; o esquema ainda não tem primitivo de "
                 "inventário consumível."},
    ],
    "pesada": [
        {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "desvantagem",
         "condicao": {"alguma": ["arma_corpo_a_corpo_e_forca_menor_que:13",
                                 "arma_a_distancia_e_destreza_menor_que:13"]}},
    ],
    "recarga": [
        {"tipo": "substituir_regra", "chave": "um_disparo_por_acao",
         "revisao": "duvida",
         "nota": "Limita a um disparo por ação, Ação Bônus ou Reação, mesmo com "
                 "Ataque Extra. Precisa de um primitivo de teto por ação."},
    ],
    "versatil": [
        {"tipo": "dado_de_dano", "modo": "substitui_dado_da_arma",
         "formula_dado": "dado_versatil_da_arma",
         "condicao": {"todas": ["empunhando_com_as_duas_maos"]}},
    ],
}

# a string que estava no dado -> filtro estruturado equivalente
FILTROS = {
    "categoria:simples": {
        "catalogo": "itens", "filtro": {"categoria": "arma", "grupo": "simples"}},
    "categoria:marcial": {
        "catalogo": "itens", "filtro": {"categoria": "arma", "grupo": "marcial"}},
    "categoria:simples+categoria:marcial": {
        "catalogo": "itens", "filtro": {"categoria": "arma", "grupo": ["simples", "marcial"]}},
    "categoria:marcial+propriedade:leve": {
        "catalogo": "itens",
        "filtro": {"categoria": "arma", "grupo": "marcial",
                   "alguma_propriedade": ["leve"]}},
    "categoria:marcial+propriedade:acuidade_ou_leve": {
        "catalogo": "itens",
        "filtro": {"categoria": "arma", "grupo": "marcial",
                   "alguma_propriedade": ["acuidade", "leve"]}},
}


def main():
    d = json.load(open(PROPS, encoding='utf-8'),
                  object_pairs_hook=collections.OrderedDict)
    for i in d['itens']:
        if i['id'] in EFEITOS:
            i['efeitos'] = EFEITOS[i['id']]
            if any(e.get('revisao') == 'duvida' for e in EFEITOS[i['id']]):
                i['revisao'] = {"status": "duvida",
                                "notas": "Regra de empunhadura ou de consumo: falta "
                                         "primitivo no esquema, então está declarada "
                                         "como substituir_regra."}
    d['nota'] = ("As 10 propriedades da coluna Propriedades da tabela Armas (p. 214-217), "
                 "com efeitos executáveis. Acuidade é a que o backend precisa para saber "
                 "qual atributo usar.")
    with open(PROPS, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)

    cl = json.load(open(CLASSES, encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    trocados, nao_mapeados = 0, []
    for c in cl['itens']:
        for e in (c.get('proficiencias_iniciais') or []):
            if e.get('tipo') != 'conceder_proficiencia' or e.get('categoria') != 'arma':
                continue
            chave = e.get('chave')
            if chave in FILTROS:
                e['de'] = FILTROS[chave]
                e['chave_antiga'] = chave
                del e['chave']
                trocados += 1
            elif 'de' not in e:
                nao_mapeados.append((c['id'], chave))
    with open(CLASSES, 'w', encoding='utf-8') as fh:
        json.dump(cl, fh, ensure_ascii=False, indent=2)

    print(f"propriedades com efeitos: {sum(1 for i in d['itens'] if i.get('efeitos'))}/{d['total']}")
    print(f"filtros de proficiência estruturados: {trocados}")
    print(f"não mapeados: {nao_mapeados if nao_mapeados else 'nenhum'}")


if __name__ == '__main__':
    main()
