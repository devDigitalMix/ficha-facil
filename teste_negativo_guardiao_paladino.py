# -*- coding: utf-8 -*-
"""Teste negativo do lote Guardião + Paladino.

Cobre principalmente as regras NOVAS do validador — a família de catálogo de
bloco de estatísticas e o alvo de impedimento em lista — mais as promessas que
as duas classes passaram a fazer: níveis de subclasse, opções de Canalizar
Divindade e as escolhas expandidas por característica.
"""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.abspath(__file__))


def carregar(b, rel):
    return json.load(open(os.path.join(b, rel), encoding='utf-8'))


def gravar(b, rel, d):
    json.dump(d, open(os.path.join(b, rel), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def item(d, iid):
    return next(i for i in d['itens'] if i['id'] == iid)


FERAS = 'catalogos/feras_companheiras.json'
CARACS = 'caracteristicas.json'
CLASSES = 'classes.json'
SUBS = 'subclasses.json'
CD = 'catalogos/efeitos_de_canalizar_divindade.json'


# ------------------------------------------- bloco de estatísticas incompleto

def fera_sem_pontos_de_vida(b):
    d = carregar(b, FERAS)
    del item(d, 'fera_do_ceu')['pontos_de_vida']
    gravar(b, FERAS, d)


def fera_sem_acoes(b):
    d = carregar(b, FERAS)
    item(d, 'fera_da_terra')['acoes'] = []
    gravar(b, FERAS, d)


def fera_com_tamanho_inventado(b):
    d = carregar(b, FERAS)
    item(d, 'fera_do_mar')['tamanho'] = 'medio_grande'
    gravar(b, FERAS, d)


def fera_com_tipo_de_criatura_inventado(b):
    d = carregar(b, FERAS)
    item(d, 'fera_do_ceu')['tipo_de_criatura'] = 'bicho'
    gravar(b, FERAS, d)


def fera_com_deslocamento_inventado(b):
    d = carregar(b, FERAS)
    item(d, 'fera_do_ceu')['deslocamentos'][1]['tipo'] = 'planeio'
    gravar(b, FERAS, d)


def fera_com_sentido_inventado(b):
    d = carregar(b, FERAS)
    item(d, 'fera_do_mar')['sentidos'][0]['sentido'] = 'ecolocalizacao'
    gravar(b, FERAS, d)


def fera_com_atributo_inventado(b):
    d = carregar(b, FERAS)
    item(d, 'fera_da_terra')['atributos']['AGI'] = 14
    gravar(b, FERAS, d)


# --------------------------------------------------- alvo de impedimento em lista

def impedimento_em_lista_com_chave_inventada(b):
    """O bug que este lote corrigiu: alvo em LISTA estourava o validador em vez
    de ser conferido item a item — e uma chave inventada passava batida."""
    d = carregar(b, CARACS)
    for e in item(d, 'repudiar_inimigos')['efeitos']:
        if e.get('tipo') == 'expandir_opcoes_de_escolha':
            e['chaves'] = ['repudiar_inimigos']
    c = carregar(b, CD)
    for e in item(c, 'repudiar_inimigos')['efeitos']:
        if e['tipo'] == 'impedir':
            e['alvo'] = ['acao', 'sesta']
    gravar(b, CD, c)
    gravar(b, CARACS, d)


# ------------------------------------------------------ promessas das classes

def subclasse_sem_caracteristica_no_nivel_marcado(b):
    """Paladino marca característica de subclasse no nível 20: tirar a do
    Juramento da Glória tem de virar erro."""
    d = carregar(b, SUBS)
    s = item(d, 'juramento_da_gloria')
    s['caracteristicas'] = [c for c in s['caracteristicas'] if c != 'lenda_viva']
    gravar(b, SUBS, d)
    c = carregar(b, CARACS)
    c['itens'] = [i for i in c['itens'] if i['id'] != 'lenda_viva']
    c['total'] = len(c['itens'])
    gravar(b, CARACS, c)


def caracteristica_de_guardiao_na_progressao_do_paladino(b):
    d = carregar(b, CLASSES)
    for l in item(d, 'paladino')['progressao']:
        if l['nivel'] == 6:
            l['caracteristicas'].append('errante')
    gravar(b, CLASSES, d)


def nivel_divergente_da_progressao(b):
    d = carregar(b, CARACS)
    item(d, 'golpes_radiantes')['nivel'] = 12
    gravar(b, CARACS, d)


def coluna_nao_declarada(b):
    d = carregar(b, CLASSES)
    item(d, 'guardiao')['progressao'][0]['colunas']['pontos_de_feiticaria'] = 2
    gravar(b, CLASSES, d)


def expandir_opcoes_apontando_para_escolha_inexistente(b):
    d = carregar(b, CARACS)
    for e in item(d, 'voto_de_inimizade')['efeitos']:
        if e['tipo'] == 'expandir_opcoes_de_escolha':
            e['escolha_id'] = 'canalizar_divindade_do_clerigo'
    gravar(b, CARACS, d)


def opcao_de_canalizar_divindade_inexistente(b):
    d = carregar(b, CARACS)
    for e in item(d, 'arma_sagrada')['efeitos']:
        if e['tipo'] == 'expandir_opcoes_de_escolha':
            e['chaves'] = ['espada_sagrada']
    gravar(b, CARACS, d)


def opcao_de_canalizar_divindade_sem_efeitos(b):
    d = carregar(b, CD)
    item(d, 'sentido_divino')['efeitos'] = []
    gravar(b, CD, d)


def equipamento_inicial_com_item_inexistente(b):
    d = carregar(b, CLASSES)
    item(d, 'guardiao')['equipamento_inicial']['opcoes'][0]['itens'][0]['item'] = \
        'armadura_de_couro_batido'
    gravar(b, CLASSES, d)


def magia_de_juramento_inexistente(b):
    """A armadilha do lote: 'Marca do Caçador', o nome impresso na tabela do
    Juramento da Vingança, não existe no capítulo 7."""
    d = carregar(b, CARACS)
    for e in item(d, 'magias_do_juramento_da_vinganca')['efeitos']:
        if e['tipo'] == 'magias_de_patrono':
            e['tabela']['linhas'][0]['magias'] = ['marca_do_cacador', 'perdicao']
    gravar(b, CARACS, d)


def truque_de_classe_sem_truques(b):
    """Combatente Druídico filtra truques de Druida. Trocar por uma lista sem
    truques deixa o filtro vazio."""
    d = carregar(b, 'catalogos/opcoes_de_estilo_de_luta_de_classe.json')
    for e in item(d, 'combatente_druidico')['efeitos']:
        e['de']['filtro']['lista'] = 'paladino'
    gravar(b, 'catalogos/opcoes_de_estilo_de_luta_de_classe.json', d)


DEFEITOS = [
    ("fera companheira sem pontos de vida", fera_sem_pontos_de_vida),
    ("fera companheira sem ações", fera_sem_acoes),
    ("fera companheira com tamanho inventado", fera_com_tamanho_inventado),
    ("fera companheira com tipo de criatura inventado",
     fera_com_tipo_de_criatura_inventado),
    ("fera companheira com deslocamento inventado", fera_com_deslocamento_inventado),
    ("fera companheira com sentido inventado", fera_com_sentido_inventado),
    ("fera companheira com atributo inventado", fera_com_atributo_inventado),
    ("impedimento em lista com chave inventada",
     impedimento_em_lista_com_chave_inventada),
    ("subclasse sem característica no nível marcado pela classe",
     subclasse_sem_caracteristica_no_nivel_marcado),
    ("característica de Guardião na progressão do Paladino",
     caracteristica_de_guardiao_na_progressao_do_paladino),
    ("nível da característica divergindo da progressão", nivel_divergente_da_progressao),
    ("coluna usada na progressão sem estar declarada", coluna_nao_declarada),
    ("expandir_opcoes_de_escolha apontando para escolha inexistente",
     expandir_opcoes_apontando_para_escolha_inexistente),
    ("opção de Canalizar Divindade inexistente",
     opcao_de_canalizar_divindade_inexistente),
    ("opção de Canalizar Divindade sem efeitos",
     opcao_de_canalizar_divindade_sem_efeitos),
    ("equipamento inicial com item inexistente",
     equipamento_inicial_com_item_inexistente),
    ("magia de juramento que não existe no capítulo 7",
     magia_de_juramento_inexistente),
    ("filtro de truques de classe que não devolve nenhum truque",
     truque_de_classe_sem_truques),
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
