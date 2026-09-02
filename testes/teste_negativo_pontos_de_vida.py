# -*- coding: utf-8 -*-
"""Teste negativo do lote de Pontos de Vida.

Mesma ideia dos outros: planta um defeito por vez numa cópia dos dados e confere
que o validador reprova. O defeito nº 1 é justamente o que passou despercebido
até agora — um alvo apontando para um valor derivado que não existe.
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


def derivado_sumido(b):
    d = carregar(b, 'catalogos/valores_derivados.json')
    d['itens'] = [i for i in d['itens'] if i['id'] != 'pontos_de_vida_maximos']
    d['total'] = len(d['itens'])
    gravar(b, 'catalogos/valores_derivados.json', d)


def derivado_com_nome_errado(b):
    d = carregar(b, 'catalogos/alvos.json')
    item(d, 'ca_total')['derivado_id'] = 'classe_de_armadura_total'
    gravar(b, 'catalogos/alvos.json', d)


def operacao_inventada(b):
    d = carregar(b, 'catalogos/valores_derivados.json')
    item(d, 'pontos_de_vida_maximos')['formula'][0]['op'] = 'somatorio'
    gravar(b, 'catalogos/valores_derivados.json', d)


def derivado_sem_parcela_rotulada(b):
    d = carregar(b, 'catalogos/valores_derivados.json')
    del item(d, 'pontos_de_vida_maximos')['parcelas'][0]['rotulo']
    gravar(b, 'catalogos/valores_derivados.json', d)


def parcela_sem_condicao(b):
    d = carregar(b, 'catalogos/valores_derivados.json')
    p = item(d, 'pontos_de_vida_maximos')['parcelas'][2]
    p.pop('condicao', None)
    p.pop('sempre', None)
    gravar(b, 'catalogos/valores_derivados.json', d)


def pv_temporarios_sem_quantidade(b):
    d = carregar(b, 'caracteristicas.json')
    for e in item(d, 'vitalidade_da_arvore')['efeitos']:
        if e.get('tipo') == 'pontos_de_vida_temporarios':
            e.pop('formula', None)
    gravar(b, 'caracteristicas.json', d)


def forma_selvagem_sem_pv_temporarios(b):
    d = carregar(b, 'caracteristicas.json')
    for e in item(d, 'forma_selvagem')['efeitos']:
        if e.get('tipo') == 'forma_selvagem':
            for sub in e.get('efeitos', []):
                if sub.get('tipo') == 'pontos_de_vida_temporarios':
                    sub.pop('formula', None)
    gravar(b, 'caracteristicas.json', d)


def magia_com_temporarios_vazio(b):
    d = carregar(b, 'catalogos/magias.json')
    item(d, 'vitalidade_vazia')['pontos_de_vida']['temporarios'].pop('formula')
    gravar(b, 'catalogos/magias.json', d)


def magia_mexe_no_maximo_sem_dizer_como(b):
    d = carregar(b, 'catalogos/magias.json')
    item(d, 'auxilio')['pontos_de_vida']['maximos'] = {"beneficiario": "ate_3_criaturas"}
    gravar(b, 'catalogos/magias.json', d)


def derivado_sem_formula(b):
    d = carregar(b, 'catalogos/valores_derivados.json')
    del item(d, 'pontos_de_vida_temporarios')['formula']
    gravar(b, 'catalogos/valores_derivados.json', d)


def alvo_de_modificador_inexistente(b):
    d = carregar(b, 'caracteristicas.json')
    for e in item(d, 'resiliencia_draconica')['efeitos']:
        if e.get('tipo') == 'modificador':
            e['alvo'] = 'pontos_de_vida_totais'
    gravar(b, 'caracteristicas.json', d)


DEFEITOS = [
    ("valor derivado apagado, com um alvo ainda apontando para ele", derivado_sumido),
    ("alvo apontando para um derivado com nome errado", derivado_com_nome_errado),
    ("operação de fórmula fora do vocabulário declarado", operacao_inventada),
    ("parcela do log de proveniência sem rótulo", derivado_sem_parcela_rotulada),
    ("parcela que não é 'sempre' e não diz quando entra", parcela_sem_condicao),
    ("efeito de PV temporários sem quantidade", pv_temporarios_sem_quantidade),
    ("Forma Selvagem sem a quantidade de PV temporários",
     forma_selvagem_sem_pv_temporarios),
    ("magia concedendo PV temporários sem dizer quantos", magia_com_temporarios_vazio),
    ("magia mexendo no PV máximo sem dizer se aumenta ou reduz",
     magia_mexe_no_maximo_sem_dizer_como),
    ("valor derivado sem fórmula", derivado_sem_formula),
    ("modificador apontando para um alvo que não existe",
     alvo_de_modificador_inexistente),
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
