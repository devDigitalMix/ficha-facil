# -*- coding: utf-8 -*-
"""Teste negativo das regras que a auditoria de 2026-09-02 acrescentou.

A mais importante é a chave de filtro desconhecida: antes dela, `resolver_filtro`
ignorava em silêncio toda chave que não sabia avaliar, e um erro de digitação num
filtro nunca era acusado.
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


C = 'caracteristicas.json'


def filtro_com_chave_digitada_errado(b):
    d = carregar(b, C)
    for e in item(d, 'maestria_em_arma')['efeitos']:
        if e.get('tipo') == 'escolha':
            e['de']['filtro']['categoira'] = 'arma'
    gravar(b, C, d)


def filtro_com_chave_inventada(b):
    d = carregar(b, C)
    for e in item(d, 'estilo_de_luta')['efeitos']:
        if e.get('tipo') == 'escolha':
            e['de']['filtro']['nivel_de_lua'] = 3
    gravar(b, C, d)


def emitir_luz_com_alvo_de_jogada_invalido(b):
    """`emitir_luz` nasceu na auditoria; um efeito novo tem de continuar sujeito às
    checagens gerais de efeito."""
    d = carregar(b, C)
    for e in item(d, 'resplendor_sagrado')['efeitos']:
        if e.get('tipo') == 'melhorar_caracteristica':
            e['efeitos'].append({"tipo": "emitir_luz_falso", "luz_plena_m": 6})
    gravar(b, C, d)


def maestria_apontando_para_arma_inexistente(b):
    d = carregar(b, C)
    for e in item(d, 'maestria_em_arma')['efeitos']:
        if e.get('tipo') == 'escolha':
            e['efeito_por_item_escolhido'] = {"tipo": "conceder_maestria_de_arma",
                                              "arma": "espada_de_luz"}
    gravar(b, C, d)


DEFEITOS = [
    ("filtro com chave digitada errado ('categoira')", filtro_com_chave_digitada_errado),
    ("filtro com chave inventada", filtro_com_chave_inventada),
    ("efeito com tipo inexistente dentro de melhoria", emitir_luz_com_alvo_de_jogada_invalido),
    ("efeito_por_item_escolhido sem o marcador do item escolhido",
     maestria_apontando_para_arma_inexistente),
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
