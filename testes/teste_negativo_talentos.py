# -*- coding: utf-8 -*-
"""Teste negativo do lote do capítulo 5 (Talentos)."""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # os testes moram em testes/; a raiz do projeto é um nível acima


def carregar(b, rel):
    return json.load(open(os.path.join(b, rel), encoding='utf-8'))


def gravar(b, rel, d):
    json.dump(d, open(os.path.join(b, rel), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def item(d, iid):
    return next(i for i in d['itens'] if i['id'] == iid)


T = 'catalogos/talentos.json'


def categoria_inventada(b):
    d = carregar(b, T)
    item(d, 'alerta')['categoria'] = 'antecedente'
    gravar(b, T, d)


def talento_geral_sem_nivel(b):
    d = carregar(b, T)
    item(d, 'atleta')['pre_requisitos'] = [
        {"tipo": "valor_de_atributo", "atributos": ["FOR", "DES"], "minimo": 13}]
    gravar(b, T, d)


def pre_requisito_sem_minimo(b):
    d = carregar(b, T)
    for pr in item(d, 'ator')['pre_requisitos']:
        pr.pop('minimo', None)
    gravar(b, T, d)


def pre_requisito_com_atributo_inventado(b):
    d = carregar(b, T)
    for pr in item(d, 'atleta')['pre_requisitos']:
        if pr['tipo'] == 'valor_de_atributo':
            pr['atributos'] = ['FOR', 'AGI']
    gravar(b, T, d)


def pre_requisitos_ausentes(b):
    d = carregar(b, T)
    del item(d, 'habilidoso')['pre_requisitos']
    gravar(b, T, d)


def aumento_de_atributo_sem_teto(b):
    d = carregar(b, T)
    for e in item(d, 'dadiva_da_fortitude')['efeitos']:
        if e.get('tipo') == 'escolha':
            e['efeito_por_item_escolhido'].pop('limite')
    gravar(b, T, d)


def acao_inexistente(b):
    d = carregar(b, T)
    for e in item(d, 'analitico')['efeitos']:
        if e.get('tipo') == 'alterar_custo_de_acao':
            e['acao_id'] = 'vasculhar'
    gravar(b, T, d)


def custo_de_acao_inexistente(b):
    d = carregar(b, T)
    for e in item(d, 'mente_agucada')['efeitos']:
        if e.get('tipo') == 'alterar_custo_de_acao':
            e['novo_custo'] = 'meia_acao'
    gravar(b, T, d)


def grau_de_cobertura_inventado(b):
    d = carregar(b, T)
    for e in item(d, 'mestre_atirador')['efeitos']:
        if e.get('tipo') == 'ignorar_cobertura':
            e['graus'] = ['parcial', 'metade']
    gravar(b, T, d)


def ignorar_resistencia_sem_tipo(b):
    d = carregar(b, T)
    for e in item(d, 'envenenador')['efeitos']:
        if e.get('tipo') == 'ignorar_resistencia':
            e.pop('tipo_dano')
    gravar(b, T, d)


def ignorar_resistencia_com_tipo_inventado(b):
    d = carregar(b, T)
    for e in item(d, 'dadiva_do_ataque_irresistivel')['efeitos']:
        if e.get('tipo') == 'ignorar_resistencia':
            e['tipos_de_dano'] = ['contundente', 'sonoro']
    gravar(b, T, d)


def impedimento_inventado(b):
    d = carregar(b, T)
    for e in item(d, 'atirador_arcano')['efeitos']:
        if e.get('tipo') == 'impedir':
            e['alvo'] = 'desvantagem_por_estar_perto'
    gravar(b, T, d)


def escolha_de_pericia_fora_do_catalogo(b):
    d = carregar(b, T)
    for e in item(d, 'analitico')['efeitos']:
        if e.get('tipo') == 'escolha' and e.get('id') == 'analitico_pericia':
            e['de']['chaves'] = ['intuicao', 'investigacao', 'observacao']
    gravar(b, T, d)


def filtro_de_magia_vazio(b):
    d = carregar(b, T)
    for e in item(d, 'tocado_por_fadas')['efeitos']:
        if e.get('tipo') == 'escolha':
            e['de']['filtro'] = {"nivel": 1, "escola": ["evocacao_sonora"]}
    gravar(b, T, d)


def talento_sem_efeitos(b):
    d = carregar(b, T)
    item(d, 'velocista')['efeitos'] = []
    gravar(b, T, d)


def dadiva_epica_aponta_para_categoria_vazia(b):
    d = carregar(b, 'caracteristicas.json')
    for e in item(d, 'dadiva_epica')['efeitos']:
        if e.get('tipo') == 'escolha':
            e['de']['filtro'] = {"categoria": "lendario"}
    gravar(b, 'caracteristicas.json', d)


DEFEITOS = [
    ("categoria de talento inventada", categoria_inventada),
    ("talento Geral sem pré-requisito de nível", talento_geral_sem_nivel),
    ("pré-requisito de atributo sem o valor mínimo", pre_requisito_sem_minimo),
    ("pré-requisito citando atributo que não existe", pre_requisito_com_atributo_inventado),
    ("talento sem o campo de pré-requisitos", pre_requisitos_ausentes),
    ("aumento de atributo sem o teto do livro", aumento_de_atributo_sem_teto),
    ("alterar_custo_de_acao apontando para ação inexistente", acao_inexistente),
    ("alterar_custo_de_acao com custo que não existe", custo_de_acao_inexistente),
    ("ignorar_cobertura com grau inventado", grau_de_cobertura_inventado),
    ("ignorar_resistencia sem dizer o tipo de dano", ignorar_resistencia_sem_tipo),
    ("ignorar_resistencia com tipo de dano inventado",
     ignorar_resistencia_com_tipo_inventado),
    ("impedimento inventado", impedimento_inventado),
    ("escolha de perícia com chave fora do catálogo",
     escolha_de_pericia_fora_do_catalogo),
    ("filtro de magia que não devolve nenhuma magia", filtro_de_magia_vazio),
    ("talento de catálogo sem efeitos", talento_sem_efeitos),
    ("Dádiva Épica apontando para uma categoria vazia",
     dadiva_epica_aponta_para_categoria_vazia),
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
