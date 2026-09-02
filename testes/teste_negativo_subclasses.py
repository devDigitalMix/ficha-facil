# -*- coding: utf-8 -*-
"""Teste negativo do nível das características de subclasse (fase 17).

`niveis_de_caracteristica` é o RESUMO de em que níveis a subclasse dá algo. Não é
o mapa de qual característica chega quando: em 42 das 48 subclasses há mais
características do que níveis. O nível de verdade está na PRÓPRIA característica.

O primeiro coletor do motor casava as duas listas por posição. Funcionou para a
Trilha da Árvore do Mundo, que tem quatro de cada, e teria calculado errado em
quase todas as outras — o Domínio da Vida, com cinco características em três
níveis, foi quem denunciou.

Estes defeitos plantados cobram que o validador trave a invariante de que o motor
passou a depender.
"""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = 'subclasses.json'
CAR = 'caracteristicas.json'


def carregar(b, rel):
    return json.load(open(os.path.join(b, rel), encoding='utf-8'))


def gravar(b, rel, d):
    json.dump(d, open(os.path.join(b, rel), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def item(d, iid):
    return next(i for i in d['itens'] if i['id'] == iid)


# ------------------------------------------------------------------ defeitos

def caracteristica_sem_nivel(b):
    """Sem nível, o motor não sabe quando a característica chega."""
    d = carregar(b, CAR)
    item(d, 'discipulo_da_vida').pop('nivel', None)
    gravar(b, CAR, d)


def resumo_de_niveis_desatualizado(b):
    """O resumo diz uma coisa e as características dizem outra."""
    d = carregar(b, SUB)
    item(d, 'dominio_da_vida')['niveis_de_caracteristica'] = [3, 6, 10, 17]
    gravar(b, SUB, d)


def caracteristica_de_outra_subclasse(b):
    d = carregar(b, SUB)
    item(d, 'dominio_da_vida')['caracteristicas'].append('vitalidade_da_arvore')
    gravar(b, SUB, d)


def caracteristica_inexistente(b):
    d = carregar(b, SUB)
    item(d, 'dominio_da_vida')['caracteristicas'].append('cura_absoluta_definitiva')
    gravar(b, SUB, d)


def nivel_da_caracteristica_mudado_sem_o_resumo(b):
    """O caso realista: alguém corrige o nível de uma característica e esquece o
    resumo da subclasse. Antes desta checagem, o resumo mentia calado."""
    d = carregar(b, CAR)
    item(d, 'preservar_a_vida')['nivel'] = 5
    gravar(b, CAR, d)


DEFEITOS = [
    ("característica de subclasse sem nível", caracteristica_sem_nivel),
    ("resumo de níveis que não bate com as características", resumo_de_niveis_desatualizado),
    ("característica que pertence a outra subclasse", caracteristica_de_outra_subclasse),
    ("característica que não existe", caracteristica_inexistente),
    ("nível corrigido na característica e esquecido no resumo",
     nivel_da_caracteristica_mudado_sem_o_resumo),
]


def mais_caracteristicas_que_niveis_e_normal(b):
    """Controle: ter mais características do que níveis NÃO é defeito — é o caso de
    42 das 48 subclasses. Uma checagem que cobrasse `len(niveis) == len(cars)` seria
    o erro do primeiro coletor, promovido a regra. Este caso TEM de passar."""
    d = carregar(b, SUB)
    n = len(item(d, 'dominio_da_vida')['caracteristicas'])
    assert n > len(item(d, 'dominio_da_vida')['niveis_de_caracteristica'])


DEVEM_PASSAR = [
    ("mais características do que níveis não é defeito", mais_caracteristicas_que_niveis_e_normal),
]


def rodar(plantar, base):
    plantar(base)
    return subprocess.run([sys.executable, os.path.join(RAIZ, 'validar.py'), base],
                          capture_output=True, text=True).returncode


def main():
    pegos = 0
    for nome, plantar in DEFEITOS:
        tmp = tempfile.mkdtemp()
        base = os.path.join(tmp, 'dados')
        shutil.copytree(os.path.join(RAIZ, 'dados'), base)
        ok = rodar(plantar, base) != 0
        pegos += ok
        print(f"{'PEGOU ' if ok else 'PASSOU'} {nome}")
        if not ok:
            print("        (o validador não acusou — isto é um furo)")
        shutil.rmtree(tmp)

    folgas = 0
    for nome, plantar in DEVEM_PASSAR:
        tmp = tempfile.mkdtemp()
        base = os.path.join(tmp, 'dados')
        shutil.copytree(os.path.join(RAIZ, 'dados'), base)
        ok = rodar(plantar, base) == 0
        folgas += ok
        print(f"{'OK    ' if ok else 'FALHOU'} {nome} (tem de passar)")
        shutil.rmtree(tmp)

    print(f"\n{pegos} de {len(DEFEITOS)} defeitos plantados foram pegos; "
          f"{folgas} de {len(DEVEM_PASSAR)} casos de folga passaram")
    return 0 if (pegos == len(DEFEITOS) and folgas == len(DEVEM_PASSAR)) else 1


if __name__ == '__main__':
    sys.exit(main())
