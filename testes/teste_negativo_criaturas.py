# -*- coding: utf-8 -*-
"""Teste negativo do Apêndice B.

A checagem que mais importa aqui é a de coerência interna do bloco: o modificador
tem de bater com o valor do atributo e a Iniciativa passiva com o bônus. Foi ela
que encontrou quatro divergências do próprio livro durante a extração.
"""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # os testes moram em testes/; a raiz do projeto é um nível acima
C = 'catalogos/criaturas.json'


def carregar(b, rel):
    return json.load(open(os.path.join(b, rel), encoding='utf-8'))


def gravar(b, rel, d):
    json.dump(d, open(os.path.join(b, rel), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def item(d, iid):
    return next(i for i in d['itens'] if i['id'] == iid)


def modificador_nao_bate_com_o_atributo(b):
    d = carregar(b, C)
    item(d, 'lobo')['modificadores']['FOR'] = 4      # FOR 14 dá +2
    gravar(b, C, d)


def iniciativa_passiva_incoerente(b):
    d = carregar(b, C)
    item(d, 'urso_pardo')['iniciativa']['passiva'] = 15
    gravar(b, C, d)


def pericia_inventada(b):
    d = carregar(b, C)
    item(d, 'lobo')['pericias'][0]['pericia'] = 'rastreamento'
    gravar(b, C, d)


def tipo_de_dano_inventado_na_imunidade(b):
    d = carregar(b, C)
    item(d, 'zumbi')['imunidades_a_dano'] = ['venenoso', 'sonoro']
    gravar(b, C, d)


def condicao_inventada_na_imunidade(b):
    d = carregar(b, C)
    item(d, 'zumbi')['imunidades_a_condicao'] = ['envenenado', 'sonolento']
    gravar(b, C, d)


def ataque_sem_dano(b):
    d = carregar(b, C)
    del item(d, 'lobo')['acoes'][0]['dano']
    gravar(b, C, d)


def ataque_com_tipo_de_dano_inventado(b):
    d = carregar(b, C)
    item(d, 'urso_pardo')['acoes'][1]['dano'][0]['tipo_dano'] = 'espiritual'
    gravar(b, C, d)


def entrada_sem_descricao(b):
    d = carregar(b, C)
    del item(d, 'aranha')['tracos'][0]['descricao_curta']
    gravar(b, C, d)


def tamanho_inventado(b):
    d = carregar(b, C)
    item(d, 'gato')['tamanho'] = 'diminuto'
    gravar(b, C, d)


def tipo_de_criatura_inventado(b):
    d = carregar(b, C)
    item(d, 'esqueleto')['tipo_de_criatura'] = 'espectro'
    gravar(b, C, d)


def deslocamento_inventado(b):
    d = carregar(b, C)
    item(d, 'coruja')['deslocamentos'][1]['tipo'] = 'planeio'
    gravar(b, C, d)


def sentido_inventado(b):
    d = carregar(b, C)
    item(d, 'morcego')['sentidos'][0]['sentido'] = 'ecolocalizacao'
    gravar(b, C, d)


def nivel_de_desafio_incompleto(b):
    d = carregar(b, C)
    del item(d, 'leao')['nivel_de_desafio']['xp']
    gravar(b, C, d)


def bloco_sem_acoes(b):
    d = carregar(b, C)
    del item(d, 'rato')['acoes']
    gravar(b, C, d)


def forma_selvagem_aponta_para_criatura_inexistente(b):
    d = carregar(b, 'caracteristicas.json')
    for e in item(d, 'forma_selvagem')['efeitos']:
        if e.get('id') == 'druida_formas_conhecidas':
            e['efeito_por_item_escolhido']['criatura'] = 'grifo'
    gravar(b, 'caracteristicas.json', d)


def forma_selvagem_aponta_para_catalogo_que_nao_e_bloco(b):
    d = carregar(b, 'caracteristicas.json')
    for e in item(d, 'forma_selvagem')['efeitos']:
        if e.get('id') == 'druida_formas_conhecidas':
            e['efeito_por_item_escolhido']['catalogo'] = 'pericias'
    gravar(b, 'caracteristicas.json', d)


def filtro_de_forma_selvagem_vazio(b):
    """Com o Apêndice B extraído, o filtro tem de devolver Fera. Se não devolver,
    é erro — antes era AVISO, porque o catálogo estava declarado vazio."""
    d = carregar(b, C)
    for i in d['itens']:
        i['tipo_de_criatura'] = 'monstruosidade'
    gravar(b, C, d)


DEFEITOS = [
    ("modificador que não bate com o valor do atributo",
     modificador_nao_bate_com_o_atributo),
    ("Iniciativa passiva que não é 10 + bônus", iniciativa_passiva_incoerente),
    ("perícia inventada no bloco", pericia_inventada),
    ("tipo de dano inventado numa imunidade", tipo_de_dano_inventado_na_imunidade),
    ("condição inventada numa imunidade", condicao_inventada_na_imunidade),
    ("ação de ataque sem dano", ataque_sem_dano),
    ("ataque com tipo de dano inventado", ataque_com_tipo_de_dano_inventado),
    ("traço sem descrição", entrada_sem_descricao),
    ("tamanho inventado", tamanho_inventado),
    ("tipo de criatura inventado", tipo_de_criatura_inventado),
    ("tipo de deslocamento inventado", deslocamento_inventado),
    ("sentido inventado", sentido_inventado),
    ("nível de desafio sem XP", nivel_de_desafio_incompleto),
    ("bloco de estatísticas sem nenhuma ação", bloco_sem_acoes),
    ("Forma Selvagem apontando para criatura que não existe",
     forma_selvagem_aponta_para_criatura_inexistente),
    ("Forma Selvagem apontando para catálogo que não é de blocos",
     forma_selvagem_aponta_para_catalogo_que_nao_e_bloco),
    ("filtro da Forma Selvagem sem nenhuma Fera para devolver",
     filtro_de_forma_selvagem_vazio),
]


def main():
    pegos = 0
    for nome, plantar in DEFEITOS:
        tmp = tempfile.mkdtemp()
        base = os.path.join(tmp, 'dados')
        shutil.copytree(os.path.join(RAIZ, 'dados'), base)
        plantar(base)
        r = subprocess.run([sys.executable, os.path.join(RAIZ, 'validar.py'), base],
                           capture_output=True, text=True)
        ok = r.returncode != 0
        pegos += ok
        print(f"{'PEGOU ' if ok else 'PASSOU'} {nome}")
        if not ok:
            print("        (o validador não acusou — isto é um furo)")
        shutil.rmtree(tmp)
    print(f"\n{pegos} de {len(DEFEITOS)} defeitos plantados foram pegos")
    return 0 if pegos == len(DEFEITOS) else 1


if __name__ == '__main__':
    sys.exit(main())
