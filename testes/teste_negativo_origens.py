# -*- coding: utf-8 -*-
"""Teste negativo do capítulo 4 (antecedentes e espécies).

As duas famílias novas do validador fazem promessas fortes — antecedente tem
forma fixa, espécie tem traços com nome e página. Estes defeitos plantados são o
que garante que essas promessas não são só comentário.
"""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # os testes moram em testes/; a raiz do projeto é um nível acima


def carregar(b, rel):
    return json.load(open(os.path.join(b, rel), encoding='utf-8'))


def gravar(b, rel, d):
    json.dump(d, open(os.path.join(b, rel), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def item(d, iid):
    return next(i for i in d['itens'] if i['id'] == iid)


A = 'catalogos/antecedentes.json'
E = 'catalogos/especies.json'
LE = 'catalogos/linhagens_elficas.json'
HD = 'catalogos/heranca_draconica.json'


# ------------------------------------------------------------- antecedentes

def antecedente_com_duas_pericias_apenas_uma(b):
    d = carregar(b, A)
    item(d, 'acolito')['pericias'] = ['religiao']
    gravar(b, A, d)


def antecedente_com_pericia_inventada(b):
    d = carregar(b, A)
    item(d, 'soldado')['pericias'] = ['atletismo', 'esgrima']
    gravar(b, A, d)


def antecedente_com_quatro_atributos(b):
    d = carregar(b, A)
    item(d, 'nobre')['atributos'] = ['FOR', 'INT', 'CAR', 'DES']
    gravar(b, A, d)


def antecedente_com_atributo_inventado(b):
    d = carregar(b, A)
    item(d, 'guia')['atributos'] = ['DES', 'CON', 'AGI']
    gravar(b, A, d)


def antecedente_com_talento_que_nao_e_de_origem(b):
    """Atacante Selvagem é de Origem; Atleta é Geral. Trocar tem de doer."""
    d = carregar(b, A)
    item(d, 'soldado')['talento_de_origem'] = 'atleta'
    gravar(b, A, d)


def antecedente_com_talento_inexistente(b):
    d = carregar(b, A)
    item(d, 'artesao')['talento_de_origem'] = 'artesao_habilidoso'
    gravar(b, A, d)


def antecedente_com_item_inexistente(b):
    d = carregar(b, A)
    item(d, 'eremita')['equipamento']['opcoes'][0]['itens'][0]['item'] = 'bordao'
    gravar(b, A, d)


def antecedente_sem_a_alternativa_de_50_po(b):
    d = carregar(b, A)
    for o in item(d, 'mercador')['equipamento']['opcoes']:
        if o['id'] == 'B':
            o['moedas'] = {'po': 75}
    gravar(b, A, d)


def antecedente_sem_a_opcao_b(b):
    d = carregar(b, A)
    eq = item(d, 'charlatao')['equipamento']
    eq['opcoes'] = [o for o in eq['opcoes'] if o['id'] != 'B']
    gravar(b, A, d)


# ------------------------------------------------------------------ espécies

def especie_com_tamanho_inventado(b):
    d = carregar(b, E)
    item(d, 'anao')['tamanho'] = {'fixo': 'baixinho'}
    gravar(b, E, d)


def especie_sem_tamanho(b):
    d = carregar(b, E)
    item(d, 'orc')['tamanho'] = {}
    gravar(b, E, d)


def especie_com_tamanho_de_escolha_invalido(b):
    d = carregar(b, E)
    item(d, 'aasimar')['tamanho'] = {'escolha': ['medio', 'gigantesco'], 'momento': 'criacao'}
    gravar(b, E, d)


def especie_com_tipo_de_criatura_inventado(b):
    d = carregar(b, E)
    item(d, 'gnomo')['tipo_de_criatura'] = 'feerico_pequeno'
    gravar(b, E, d)


def especie_com_deslocamento_inventado(b):
    d = carregar(b, E)
    item(d, 'golias')['deslocamento'] = {'tipo': 'passada', 'metros': 10.5}
    gravar(b, E, d)


def especie_sem_deslocamento_em_metros(b):
    d = carregar(b, E)
    item(d, 'elfo')['deslocamento'] = {'tipo': 'caminhada', 'metros': '9 metros'}
    gravar(b, E, d)


def especie_sem_tracos(b):
    d = carregar(b, E)
    item(d, 'pequenino')['tracos'] = []
    gravar(b, E, d)


def traco_sem_efeitos(b):
    d = carregar(b, E)
    item(d, 'humano')['tracos'][0]['efeitos'] = []
    gravar(b, E, d)


def traco_sem_fonte(b):
    d = carregar(b, E)
    del item(d, 'tiferino')['tracos'][0]['fonte']
    gravar(b, E, d)


def traco_sem_descricao(b):
    d = carregar(b, E)
    item(d, 'draconato')['tracos'][0]['descricao_curta'] = ''
    gravar(b, E, d)


def tracos_com_id_repetido(b):
    d = carregar(b, E)
    tr = item(d, 'anao')['tracos']
    tr[1]['id'] = tr[0]['id']
    gravar(b, E, d)


def traco_com_nivel_de_personagem_fora_da_faixa(b):
    d = carregar(b, E)
    for tr in item(d, 'golias')['tracos']:
        if tr['id'] == 'forma_grande':
            tr['nivel_de_personagem'] = 21
    gravar(b, E, d)


def especie_com_sentido_inventado(b):
    d = carregar(b, E)
    for tr in item(d, 'anao')['tracos']:
        if tr['id'] == 'conhecimento_de_pedras':
            for e in tr['efeitos']:
                if e['tipo'] == 'conceder_sentido':
                    e['sentido'] = 'radar'
    gravar(b, E, d)


def linhagem_com_magia_inexistente(b):
    d = carregar(b, LE)
    item(d, 'alto_elfo')['magias_por_nivel'] = {'3': ['detectar_magias'], '5': ['passo_nebuloso']}
    gravar(b, LE, d)


def linhagem_com_truque_inexistente(b):
    d = carregar(b, LE)
    for e in item(d, 'drow')['efeitos']:
        if e['tipo'] == 'desbloquear_magias':
            e['magia'] = 'luzes_dancarinas'
    gravar(b, LE, d)


def heranca_draconica_com_tipo_de_dano_inventado(b):
    d = carregar(b, HD)
    for e in item(d, 'dragao_verde')['efeitos']:
        if e['tipo'] == 'alterar_dano':
            e['tipo_dano'] = 'toxico'
    gravar(b, HD, d)


def mapa_de_dano_derivado_com_tipo_inventado(b):
    d = carregar(b, E)
    for tr in item(d, 'draconato')['tracos']:
        if tr['id'] == 'resistencia_a_dano_draconato':
            tr['efeitos'][0]['tipo_dano_derivado']['mapa']['dragao_ouro'] = 'chamas'
    gravar(b, E, d)


DEFEITOS = [
    ("antecedente com uma perícia em vez de duas", antecedente_com_duas_pericias_apenas_uma),
    ("antecedente com perícia inventada", antecedente_com_pericia_inventada),
    ("antecedente com quatro atributos", antecedente_com_quatro_atributos),
    ("antecedente com atributo inventado", antecedente_com_atributo_inventado),
    ("antecedente com talento que não é da categoria Origem",
     antecedente_com_talento_que_nao_e_de_origem),
    ("antecedente com talento inexistente", antecedente_com_talento_inexistente),
    ("antecedente com item inexistente no pacote", antecedente_com_item_inexistente),
    ("antecedente cuja opção B não são 50 PO", antecedente_sem_a_alternativa_de_50_po),
    ("antecedente sem a opção B", antecedente_sem_a_opcao_b),
    ("espécie com tamanho inventado", especie_com_tamanho_inventado),
    ("espécie sem tamanho", especie_sem_tamanho),
    ("espécie com escolha de tamanho inválida", especie_com_tamanho_de_escolha_invalido),
    ("espécie com tipo de criatura inventado", especie_com_tipo_de_criatura_inventado),
    ("espécie com tipo de deslocamento inventado", especie_com_deslocamento_inventado),
    ("espécie com deslocamento em texto em vez de número",
     especie_sem_deslocamento_em_metros),
    ("espécie sem traços", especie_sem_tracos),
    ("traço sem efeitos", traco_sem_efeitos),
    ("traço sem fonte", traco_sem_fonte),
    ("traço sem descrição", traco_sem_descricao),
    ("traços com id repetido na mesma espécie", tracos_com_id_repetido),
    ("traço com nível de personagem fora da faixa",
     traco_com_nivel_de_personagem_fora_da_faixa),
    ("traço concedendo sentido inventado", especie_com_sentido_inventado),
    ("linhagem concedendo magia inexistente", linhagem_com_magia_inexistente),
    ("linhagem concedendo truque inexistente", linhagem_com_truque_inexistente),
    ("herança dracônica com tipo de dano inventado",
     heranca_draconica_com_tipo_de_dano_inventado),
    ("mapa de dano derivado com tipo inventado", mapa_de_dano_derivado_com_tipo_inventado),
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
