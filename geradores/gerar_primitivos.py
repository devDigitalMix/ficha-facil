# -*- coding: utf-8 -*-
"""Os quatro primitivos que eu tinha deixado como dúvida — resolvidos no dado.

Eu havia dito que faltavam primitivos no esquema. Revendo: três dos quatro são
DECLARAÇÃO, não motor. O backend precisa aplicar a regra, mas quem diz quantas
mãos uma arma ocupa, quanta munição um ataque gasta e quantos disparos cabem numa
ação é o dado. Deixar isso para o backend seria devolver a regra para o código.

1. MÃOS OCUPADAS — cada item que se empunha declara quantas mãos usa, e a
   propriedade Versátil declara as duas formas de segurar.
2. CONSUMO DE MUNIÇÃO — a arma com Munição declara o que gasta e quanto, e a
   recuperação depois do combate.
3. TETO POR AÇÃO — Recarga declara o limite de disparos por ação.
4. CÁLCULOS DE CA CONCORRENTES — todo efeito `ca_base` ganha um id e a marca de
   que concorre; o backend junta os candidatos e o jogador escolhe um.
"""
import json, collections

ITENS = 'dados/catalogos/itens.json'
PROPS = 'dados/catalogos/propriedades_de_arma.json'
CARACS = 'dados/caracteristicas.json'


def carregar(p):
    return json.load(open(p, encoding='utf-8'),
                     object_pairs_hook=collections.OrderedDict)


def gravar(p, d):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def main():
    itens = carregar(ITENS)
    props = carregar(PROPS)

    # ------------------------------------------------- 1 e 2: armas e itens
    n_maos = n_mun = 0
    for i in itens['itens']:
        p_ids = {p['propriedade'] for p in (i.get('propriedades') or [])}
        if i['categoria'] == 'arma':
            versatil = next((p for p in (i.get('propriedades') or [])
                             if p['propriedade'] == 'versatil'), None)
            if 'duas_maos' in p_ids:
                i['maos_ocupadas'] = 2
            elif versatil:
                i['maos_ocupadas'] = 1
                i['maos_alternativas'] = {
                    "2": {"dado_de_dano": versatil.get('dado_versatil'),
                          "nota": "Empunhada com as duas mãos, usa o dado Versátil."}}
            else:
                i['maos_ocupadas'] = 1
            n_maos += 1
            mun = next((p for p in (i.get('propriedades') or [])
                        if p['propriedade'] == 'municao'), None)
            if mun:
                i['consumo'] = {
                    "item": mun.get('municao'),
                    "por_ataque": 1,
                    "recuperacao_apos_o_combate": {
                        "fracao": "metade", "arredondamento": "baixo",
                        "tempo": "1 minuto"},
                }
                n_mun += 1
            if 'recarga' in p_ids:
                i['limite_por_acao'] = {
                    "disparos": 1,
                    "vale_para": ["acao", "acao_bonus", "reacao"],
                    "nota": "Vale mesmo com Ataque Extra (p. 217).",
                }
        elif i['categoria'] == 'armadura' and i['grupo'] == 'escudo':
            i['maos_ocupadas'] = 1
            n_maos += 1
        elif i['categoria'] == 'foco_de_conjuracao':
            i.setdefault('maos_ocupadas', 1)
            i['deve_ser_segurado'] = True
            n_maos += 1

    # as propriedades deixam de ser 'substituir_regra' e passam a apontar o campo
    NOVOS_EFEITOS = {
        "duas_maos": [
            {"tipo": "declara_campo_no_item", "campo": "maos_ocupadas",
             "valor": 2,
             "nota": "Cada arma com esta propriedade declara maos_ocupadas: 2."}],
        "versatil": [
            {"tipo": "dado_de_dano", "modo": "substitui_dado_da_arma",
             "formula_dado": "dado_versatil_da_arma",
             "condicao": {"todas": ["empunhando_com_as_duas_maos"]},
             "nota": "A arma declara maos_ocupadas: 1 e maos_alternativas['2'] com o "
                     "dado maior."}],
        "municao": [
            {"tipo": "declara_campo_no_item", "campo": "consumo",
             "consumo_por_ataque": 1,
             "recuperacao_apos_o_combate": {"fracao": "metade",
                                            "arredondamento": "baixo",
                                            "tempo": "1 minuto"},
             "nota": "Cada arma com esta propriedade declara o campo `consumo`, com o "
                     "id da munição que gasta."}],
        "recarga": [
            {"tipo": "declara_campo_no_item", "campo": "limite_por_acao",
             "disparos": 1,
             "vale_para": ["acao", "acao_bonus", "reacao"],
             "nota": "Cada arma com esta propriedade declara o campo `limite_por_acao`."}],
    }
    for p in props['itens']:
        if p['id'] in NOVOS_EFEITOS:
            p['efeitos'] = NOVOS_EFEITOS[p['id']]
            p['revisao'] = {"status": "ok", "notas": ""}

    # ---------------------------------------- 4: cálculos de CA concorrentes
    caracs = carregar(CARACS)
    n_ca = 0

    def marcar(efs, dono):
        nonlocal n_ca
        for e in efs:
            if isinstance(e, dict):
                if e.get('tipo') == 'ca_base':
                    e.setdefault('id', f"ca_{dono}")
                    e['concorre_como'] = 'calculo_de_ca_base'
                    e['nota'] = ("Concorre com os demais cálculos de CA base; o jogador "
                                 "escolhe um, não se somam (Ap. C, 'Classe de Armadura').")
                    n_ca += 1
                for ch in ('efeitos', 'efeito_por_item_escolhido'):
                    v = e.get(ch)
                    if isinstance(v, list):
                        marcar(v, dono)
                    elif isinstance(v, dict):
                        marcar([v], dono)

    for it in caracs['itens']:
        marcar(it.get('efeitos') or [], it['id'])

    # a armadura também é um cálculo de base concorrente
    for i in itens['itens']:
        if i['categoria'] == 'armadura' and i['grupo'] != 'escudo':
            i['ca']['concorre_como'] = 'calculo_de_ca_base'
            i['ca']['id'] = f"ca_{i['id']}"
            n_ca += 1

    gravar(ITENS, itens)
    gravar(PROPS, props)
    gravar(CARACS, caracs)
    print(f"itens com maos_ocupadas: {n_maos}")
    print(f"armas com consumo de munição: {n_mun}")
    print(f"armas com limite por ação: "
          f"{sum(1 for i in itens['itens'] if 'limite_por_acao' in i)}")
    print(f"cálculos de CA base marcados como concorrentes: {n_ca}")


if __name__ == '__main__':
    main()
