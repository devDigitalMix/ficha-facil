# -*- coding: utf-8 -*-
"""Empurrão e puxão deixam de ser texto.

Ao modelar a Implosão de Distorção (Feiticeiro Aberrante, nível 18) eu precisei
de um puxão como efeito de verdade, e criei `movimento_forcado`. Aí ficou óbvio
que os empurrões que já existiam no dado estavam escritos como `efeito_narrativo`
— texto que o backend teria de ler para entender. Este script migra os que já
existiam para o tipo novo, para não ficar uma regra em dois formatos.

Migrados:
  · Técnica da Mão Espalmada, opção "empurrar" (Monge, p. 162)
  · Ira do Mar (Druida do Círculo do Mar, p. 101)
"""
import json, collections

ALVOS = [
    ('dados/caracteristicas.json', 'empurrao_do_mar', {
        "tipo": "movimento_forcado", "direcao": "empurrar", "distancia_m": 4.5,
        "origem": "voce", "alvo": "criatura_que_falhou_na_salvaguarda",
        "restricao_de_tamanho": "grande_ou_menor",
        "nota": "Antes era efeito_narrativo; virou efeito com o tipo movimento_forcado."}),
]

CATALOGO_MAO = ('dados/catalogos/efeitos_da_mao_espalmada.json', None)


def carregar(p):
    return json.load(open(p, encoding='utf-8'),
                     object_pairs_hook=collections.OrderedDict)


def gravar(p, d):
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def substituir(obj, chave, novo, contador):
    """Troca todo efeito_narrativo com a chave dada pelo efeito estruturado."""
    if isinstance(obj, list):
        for n, v in enumerate(obj):
            if (isinstance(v, dict) and v.get('tipo') == 'efeito_narrativo'
                    and v.get('chave') == chave):
                obj[n] = collections.OrderedDict(novo)
                contador[0] += 1
            else:
                substituir(v, chave, novo, contador)
    elif isinstance(obj, dict):
        for v in obj.values():
            substituir(v, chave, novo, contador)


def main():
    total = 0
    for caminho, chave, novo in ALVOS:
        d = carregar(caminho)
        c = [0]
        substituir(d['itens'], chave, novo, c)
        if c[0]:
            gravar(caminho, d)
        print(f"{caminho} · {chave}: {c[0]} substituição(ões)")
        total += c[0]

    # o empurrão da Mão Espalmada mora em efeitos_nomeados dentro da característica
    d = carregar('dados/caracteristicas.json')
    n = 0
    for it in d['itens']:
        nomeados = it.get('efeitos_nomeados') or {}
        alvo = nomeados.get('empurrar')
        if not alvo:
            continue
        for bloco in ('em_falha', 'efeitos'):
            for i, e in enumerate(alvo.get(bloco) or []):
                if (isinstance(e, dict) and e.get('tipo') == 'efeito_narrativo'
                        and e.get('chave') == 'empurrao'):
                    alvo[bloco][i] = collections.OrderedDict([
                        ("tipo", "movimento_forcado"), ("direcao", "empurrar"),
                        ("distancia_m", 4.5), ("origem", "voce"), ("alvo", "alvo"),
                        ("nota", "Antes era efeito_narrativo; virou efeito com o tipo "
                                 "movimento_forcado.")])
                    n += 1
    if n:
        gravar('dados/caracteristicas.json', d)
    print(f"caracteristicas.json · empurrao (Mão Espalmada): {n} substituição(ões)")
    print(f"total migrado: {total + n}")


if __name__ == '__main__':
    main()
