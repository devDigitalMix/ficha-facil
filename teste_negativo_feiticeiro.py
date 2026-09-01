# -*- coding: utf-8 -*-
"""Teste negativo do lote Bardo + Feiticeiro.

Planta um defeito de cada vez numa cópia dos dados e confere que o validador
acusa. Um validador que passa em tudo não prova nada; o que prova é ele
reprovar o que está errado.
"""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.abspath(__file__))


def carregar(base, rel):
    return json.load(open(os.path.join(base, rel), encoding='utf-8'))


def gravar(base, rel, d):
    json.dump(d, open(os.path.join(base, rel), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def item(d, iid):
    return next(i for i in d['itens'] if i['id'] == iid)


# ---------------------------------------------------------------- os defeitos
def buraco_na_tabela(b):
    d = carregar(b, 'catalogos/surtos_de_magia_selvagem.json')
    d['itens'] = [i for i in d['itens'] if i['id'] != 'escudo_espectral']
    d['total'] = len(d['itens'])
    gravar(b, 'catalogos/surtos_de_magia_selvagem.json', d)


def faixas_sobrepostas(b):
    d = carregar(b, 'catalogos/surtos_de_magia_selvagem.json')
    item(d, 'escudo_espectral')['faixa_1d100']['min'] = 48
    gravar(b, 'catalogos/surtos_de_magia_selvagem.json', d)


def tabela_nao_fecha(b):
    d = carregar(b, 'catalogos/surtos_de_magia_selvagem.json')
    item(d, 'beneficio_aleatorio_1d6')['faixa_1d100']['max'] = 99
    gravar(b, 'catalogos/surtos_de_magia_selvagem.json', d)


def metamagia_sem_custo(b):
    d = carregar(b, 'catalogos/opcoes_de_metamagia.json')
    del item(d, 'magia_sutil')['custo_em_pontos_de_feiticaria']
    gravar(b, 'catalogos/opcoes_de_metamagia.json', d)


def metamagia_custo_zero(b):
    d = carregar(b, 'catalogos/opcoes_de_metamagia.json')
    item(d, 'magia_distante')['custo_em_pontos_de_feiticaria'] = 0
    gravar(b, 'catalogos/opcoes_de_metamagia.json', d)


def movimento_sem_direcao(b):
    d = carregar(b, 'caracteristicas.json')
    for e in item(d, 'implosao_de_distorcao')['efeitos']:
        for sub in e.get('efeitos', []):
            if sub.get('tipo') == 'movimento_forcado':
                sub['direcao'] = 'arrastar'
    gravar(b, 'caracteristicas.json', d)


def movimento_sem_distancia(b):
    d = carregar(b, 'caracteristicas.json')
    for e in item(d, 'ira_do_mar')['efeitos']:
        for sub in e.get('efeitos', []):
            if sub.get('tipo') == 'movimento_forcado':
                del sub['distancia_m']
    gravar(b, 'caracteristicas.json', d)


def tabela_inexistente(b):
    d = carregar(b, 'caracteristicas.json')
    item(d, 'surto_de_magia_selvagem')['efeitos'][0]['catalogo'] = 'pericias'
    gravar(b, 'caracteristicas.json', d)


def niveis_de_subclasse_divergentes(b):
    d = carregar(b, 'subclasses.json')
    item(d, 'feiticaria_draconica')['niveis_de_caracteristica'] = [3, 6, 14]
    gravar(b, 'subclasses.json', d)


def caracteristica_fora_do_nivel(b):
    d = carregar(b, 'caracteristicas.json')
    item(d, 'asas_de_dragao')['nivel'] = 15
    gravar(b, 'caracteristicas.json', d)


def tipo_de_efeito_inventado(b):
    d = carregar(b, 'caracteristicas.json')
    item(d, 'apoteose_arcana')['efeitos'][0]['efeitos'][0]['tipo'] = 'zerar_custo'
    gravar(b, 'caracteristicas.json', d)


def alvo_de_impedimento_inventado(b):
    d = carregar(b, 'caracteristicas.json')
    for e in item(d, 'restaurar_equilibrio')['efeitos']:
        if e['tipo'] == 'impedir':
            e['alvo'] = 'anular_a_sorte'
    gravar(b, 'caracteristicas.json', d)


def magia_de_subclasse_inexistente(b):
    d = carregar(b, 'caracteristicas.json')
    linhas = item(d, 'magias_mecanicas')['efeitos'][0]['tabela']['linhas']
    linhas[0]['magias'][0] = 'alarme_de_engrenagem'
    gravar(b, 'caracteristicas.json', d)


def escolha_com_catalogo_inexistente(b):
    d = carregar(b, 'caracteristicas.json')
    item(d, 'metamagia')['efeitos'][0]['de']['catalogo'] = 'opcoes_de_meta_magia'
    gravar(b, 'caracteristicas.json', d)


def filtro_do_surto_vazio(b):
    d = carregar(b, 'catalogos/surtos_de_magia_selvagem.json')
    for i in d['itens']:
        i['escolhivel_no_surto_controlado'] = False
    gravar(b, 'catalogos/surtos_de_magia_selvagem.json', d)


def catalogo_de_opcao_sem_efeitos(b):
    d = carregar(b, 'catalogos/alteracoes_da_revelacao_em_carne.json')
    item(d, 'voo_reluzente')['efeitos'] = []
    gravar(b, 'catalogos/alteracoes_da_revelacao_em_carne.json', d)


def total_errado(b):
    d = carregar(b, 'catalogos/opcoes_de_metamagia.json')
    d['total'] = 9
    gravar(b, 'catalogos/opcoes_de_metamagia.json', d)


def escolha_referencia_fantasma(b):
    d = carregar(b, 'caracteristicas.json')
    item(d, 'feiticaria_encarnada')['efeitos'][1]['efeitos'][0]['escolha_id'] = \
        'feiticeiro_metamagias'
    gravar(b, 'caracteristicas.json', d)


DEFEITOS = [
    ("linha da tabela apagada (buraco de 49 a 52)", buraco_na_tabela),
    ("duas linhas cobrindo o mesmo resultado", faixas_sobrepostas),
    ("tabela que não chega a 100", tabela_nao_fecha),
    ("opção de Metamagia sem custo declarado", metamagia_sem_custo),
    ("opção de Metamagia com custo zero", metamagia_custo_zero),
    ("movimento forçado com direção inventada", movimento_sem_direcao),
    ("movimento forçado sem distância nem destino", movimento_sem_distancia),
    ("rolar_na_tabela apontando para catálogo que não é tabela", tabela_inexistente),
    ("subclasse com níveis diferentes dos da classe", niveis_de_subclasse_divergentes),
    ("característica de subclasse num nível fora dos declarados",
     caracteristica_fora_do_nivel),
    ("tipo de efeito inventado", tipo_de_efeito_inventado),
    ("alvo de impedimento inventado", alvo_de_impedimento_inventado),
    ("magia de subclasse que não existe no catálogo", magia_de_subclasse_inexistente),
    ("escolha apontando para catálogo inexistente", escolha_com_catalogo_inexistente),
    ("filtro do Surto Controlado que não devolve nenhuma linha", filtro_do_surto_vazio),
    ("item de catálogo de opção sem efeitos", catalogo_de_opcao_sem_efeitos),
    ("total do catálogo fora da contagem real", total_errado),
    ("expandir/alterar escolha apontando para id inexistente",
     escolha_referencia_fantasma),
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
        marca = 'PEGOU ' if ok else 'PASSOU'
        print(f"{marca} {nome}")
        if not ok:
            print("        (o validador não acusou — isto é um furo)")
        shutil.rmtree(tmp)
    print(f"\n{pegos} de {len(DEFEITOS)} defeitos plantados foram pegos")
    return 0 if pegos == len(DEFEITOS) else 1


if __name__ == '__main__':
    sys.exit(main())
