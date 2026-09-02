# -*- coding: utf-8 -*-
"""Descrição curta para os 170 itens e as 25 ferramentas do capítulo 6.

O `PLANO-APP.md` promete um Compêndio navegável, mas 169 dos 170 itens e todas as
25 ferramentas estavam sem uma linha sequer de texto: só dados mecânicos, nada para
mostrar na tela. O validador não cobrava porque `catalogo.schema.json` só exige
`id` e `nome`.

Estas descrições são **derivadas do próprio dado**, não paráfrase do livro: dano,
propriedades, maestria, CA, peso, custo e — nas ferramentas — atributo, teste de
Usar Objeto e o que dá para fabricar. Por isso cada uma leva `descricao_derivada:
true`. Isso importa: quando alguém quiser trocar por uma paráfrase de verdade, sabe
o que é texto autoral e o que é composição automática.

Se o dado mudar, esta descrição muda junto — é a vantagem de derivar em vez de
escrever à mão 195 vezes.
"""
import collections, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos

MOEDAS = {'pc': 'PC', 'pp': 'PP', 'pe': 'PE', 'po': 'PO', 'pl': 'PL'}
GRUPO_ARMA = {'simples': 'Arma Simples', 'marcial': 'Arma Marcial'}
GRUPO_ARMADURA = {'leve': 'Armadura Leve', 'media': 'Armadura Média',
                  'pesada': 'Armadura Pesada', 'escudo': 'Escudo'}
ALCANCE = {'corpo_a_corpo': 'Corpo a Corpo', 'a_distancia': 'à Distância'}


def numero(v):
    """1.0 -> '1'; 0.5 -> '0,5'. Vírgula decimal, como no livro."""
    if v is None:
        return None
    return (f"{v:.2f}".rstrip('0').rstrip('.') or '0').replace('.', ',')


def preco(custo):
    if not custo:
        return None
    return f"{numero(custo['valor'])} {MOEDAS.get(custo['moeda'], custo['moeda'].upper())}"


def peso(kg):
    if kg in (None, 0):
        return None
    return f"{numero(kg)} kg"


def juntar(partes, sep='; '):
    """Junta com ponto e vírgula: os pedaços são cláusulas, não frases — começam em
    minúscula e um ponto entre elas ficaria errado."""
    return sep.join(p for p in partes if p)


def descrever_arma(i, maestrias):
    cabeca = juntar([GRUPO_ARMA.get(i.get('grupo'), 'Arma'),
                     ALCANCE.get(i.get('alcance'))], ' ')
    d = i.get('dano') or {}
    dano = None
    if d.get('formula_dado'):
        dano = f"dano {d['formula_dado']} {(d.get('tipo_dano') or '').capitalize()}".strip()
    props = [p.get('texto') for p in (i.get('propriedades') or []) if p.get('texto')]
    prop = f"propriedades: {', '.join(props)}" if props else None
    mst = i.get('maestria')
    mestria = f"maestria {maestrias.get(mst, mst)}" if mst else None
    return juntar([juntar([cabeca, dano], ', '), prop, mestria])


def descrever_armadura(i):
    cabeca = GRUPO_ARMADURA.get(i.get('grupo'), 'Armadura')
    ca = i.get('ca') or {}
    if i.get('grupo') == 'escudo':
        # o escudo declara 'bonus', não 'base': ele soma à CA em vez de defini-la
        pedaco = f"CA +{ca['bonus']}" if ca.get('bonus') is not None else None
    elif ca.get('base') is not None:
        pedaco = f"CA {ca['base']}"
        if ca.get('soma_modificador_destreza'):
            teto = ca.get('teto_do_modificador')
            pedaco += (f" + modificador de Destreza (máx. +{teto})" if teto
                       else " + modificador de Destreza")
    else:
        pedaco = None
    extras = []
    if i.get('forca_minima'):
        extras.append(f"exige Força {i['forca_minima']}")
    if i.get('desvantagem_em_furtividade'):
        extras.append("Desvantagem em Furtividade")
    if i.get('minutos_para_vestir'):
        extras.append(f"{i['minutos_para_vestir']} min para vestir")
    return juntar([juntar([cabeca, pedaco], ', '), '; '.join(extras) or None])


def descrever_generico(i):
    rotulos = {
        'municao': 'Munição',
        'foco_de_conjuracao': 'Foco de Conjuração',
        'equipamento_de_aventura': 'Equipamento de aventura',
        'montaria': 'Montaria',
        'veiculo': 'Veículo',
        'arreio_ou_veiculo_de_tracao': 'Arreio ou veículo de tração',
    }
    partes = [rotulos.get(i.get('categoria'), 'Item')]
    if i.get('quantidade_por_compra'):
        partes.append(f"vendida em lotes de {i['quantidade_por_compra']}")
    if i.get('armazenada_em'):
        partes.append(f"guardada em {i['armazenada_em'].replace('_', ' ')}")
    if i.get('capacidade_de_carga_kg'):
        partes.append(f"carrega até {numero(i['capacidade_de_carga_kg'])} kg")
    if i.get('velocidade_km_h'):
        partes.append(f"{numero(i['velocidade_km_h'])} km/h")
    return juntar([partes[0], ', '.join(partes[1:]) or None])


def descrever_item(i, maestrias):
    cat = i.get('categoria')
    if cat == 'arma':
        corpo = descrever_arma(i, maestrias)
    elif cat == 'armadura':
        corpo = descrever_armadura(i)
    else:
        corpo = descrever_generico(i)
    ficha = ' · '.join(x for x in (preco(i.get('custo')), peso(i.get('peso_kg'))) if x)
    return juntar([corpo, ficha]) + '.' 


ATRIBUTO_POR_EXTENSO = {'FOR': 'Força', 'DES': 'Destreza', 'CON': 'Constituição',
                        'INT': 'Inteligência', 'SAB': 'Sabedoria', 'CAR': 'Carisma'}


def descrever_ferramenta(f):
    cabeca = ("Ferramenta de Artesão" if f.get('grupo') == 'artesao' else "Ferramenta")
    attr = ATRIBUTO_POR_EXTENSO.get(f.get('atributo'))
    if attr:
        cabeca += f", usada com {attr}"
    uo = f.get('usar_objeto') or {}
    usar = None
    if uo.get('acao'):
        usar = f"Usar Objeto: {uo['acao'].rstrip('.')}"
        if uo.get('cd'):
            usar += f" (CD {uo['cd']})"
    fab = f.get('fabricacao') or {}
    n = len(fab.get('itens') or [])
    fabrica = f"fabrica {n} {'item' if n == 1 else 'itens'}" if n else None
    ficha = ' · '.join(x for x in (preco(f.get('custo')), peso(f.get('peso_kg'))) if x)
    return juntar([cabeca, usar, fabrica, ficha]) + '.' 


def main():
    maestrias = {m['id']: m['nome'] for m in json.load(
        open(os.path.join(caminhos.CATALOGOS, 'maestrias_de_arma.json'),
             encoding='utf-8'))['itens']}

    n_itens = n_fer = 0
    caminho = os.path.join(caminhos.CATALOGOS, 'itens.json')
    d = json.load(open(caminho, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    for i in d['itens']:
        if i.get('descricao_curta') and not i.get('descricao_derivada'):
            continue
        i['descricao_curta'] = descrever_item(i, maestrias)
        i['descricao_derivada'] = True
        n_itens += 1
    json.dump(d, open(caminho, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    caminho = os.path.join(caminhos.CATALOGOS, 'ferramentas.json')
    d = json.load(open(caminho, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    for f in d['itens']:
        if f.get('descricao_curta') and not f.get('descricao_derivada'):
            continue
        f['descricao_curta'] = descrever_ferramenta(f)
        f['descricao_derivada'] = True
        n_fer += 1
    json.dump(d, open(caminho, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    print(f"descrições derivadas: {n_itens} itens, {n_fer} ferramentas")


if __name__ == '__main__':
    main()
