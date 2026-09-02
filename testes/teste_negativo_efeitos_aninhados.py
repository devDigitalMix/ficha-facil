# -*- coding: utf-8 -*-
"""Teste negativo da declaração de efeitos aninhados (fase 15).

Um efeito pode trazer outros dentro, e o que isso significa não pode ser
adivinhado pelo formato: a Fúria CONDICIONA o que traz (só vale ligada), e
`melhorar_caracteristica` só REDIRECIONA (o alvo diz onde aplicar, não quando).

O motor adivinhava, e adivinhava errado — os 56 `melhorar_caracteristica` viravam
condição sem nome e ficavam desligados por padrão. A regra passou a ser declarada
em `catalogos/tipos_de_efeito.json`. Estes defeitos plantados cobram que o
validador não deixe a declaração faltar nem colidir.
"""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIPOS = 'catalogos/tipos_de_efeito.json'
CAR = 'caracteristicas.json'


def carregar(b, rel):
    return json.load(open(os.path.join(b, rel), encoding='utf-8'))


def gravar(b, rel, d):
    json.dump(d, open(os.path.join(b, rel), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def item(d, iid):
    return next(i for i in d['itens'] if i['id'] == iid)


def efeito_com(d, iid, tipo):
    for e in item(d, iid)['efeitos']:
        if e.get('tipo') == tipo:
            return e
    raise AssertionError('sem efeito %s em %s' % (tipo, iid))


# ------------------------------------------------------------------ defeitos

def declaracao_apagada(b):
    """O defeito original: ninguém diz o que o aninhamento significa."""
    d = carregar(b, TIPOS)
    item(d, 'furia').pop('efeitos_aninhados', None)
    gravar(b, TIPOS, d)


def declaracao_com_valor_inventado(b):
    d = carregar(b, TIPOS)
    item(d, 'furia')['efeitos_aninhados'] = 'as_vezes'
    gravar(b, TIPOS, d)


def condicionante_sem_id(b):
    """Sem id não há nome para a condição — foi assim que 56 caíram no mesmo balde."""
    d = carregar(b, CAR)
    efeito_com(d, 'furia', 'furia').pop('id', None)
    gravar(b, CAR, d)


def duas_condicoes_com_o_mesmo_id(b):
    d = carregar(b, CAR)
    efeito_com(d, 'forma_selvagem', 'forma_selvagem')['id'] = 'furia'
    gravar(b, CAR, d)


def tipo_novo_que_aninha_sem_declarar(b):
    """O décimo tipo, criado por quem não passou pelo catálogo."""
    d = carregar(b, TIPOS)
    d['itens'].append({'id': 'aura_improvisada', 'nome': 'Aura improvisada',
                       'origem': 'teste', 'campos': ['efeitos']})
    d['total'] = len(d['itens'])
    gravar(b, TIPOS, d)
    c = carregar(b, CAR)
    item(c, 'furia')['efeitos'].append({
        'tipo': 'aura_improvisada',
        'efeitos': [{'tipo': 'efeito_narrativo', 'chave': 'x', 'texto': 'qualquer coisa'}],
    })
    gravar(b, CAR, c)


DEFEITOS = [
    ("tipo que aninha e não declara o que isso significa", declaracao_apagada),
    ("efeitos_aninhados com valor inventado", declaracao_com_valor_inventado),
    ("efeito condicionante sem id para nomear a condição", condicionante_sem_id),
    ("duas condições diferentes com o mesmo id", duas_condicoes_com_o_mesmo_id),
    ("tipo novo que aninha sem passar pelo catálogo", tipo_novo_que_aninha_sem_declarar),
]


def estrutural_nao_precisa_de_id(b):
    """Controle: `melhorar_caracteristica` não condiciona nada, então não precisa
    de id — e cobrar id dela seria voltar ao defeito por outro caminho.
    Este caso TEM de passar."""
    d = carregar(b, CAR)
    for i in d['itens']:
        for e in (i.get('efeitos') or []):
            if e.get('tipo') == 'melhorar_caracteristica':
                e.pop('id', None)
    gravar(b, CAR, d)


DEVEM_PASSAR = [
    ("efeito estrutural sem id não é defeito", estrutural_nao_precisa_de_id),
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
