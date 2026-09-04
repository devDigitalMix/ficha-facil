# -*- coding: utf-8 -*-
"""Escolher "mais um idioma" não pode oferecer os que o personagem já fala.

O João, montando um Ladino em 2026-09-04: "ele fala para escolher uma língua, mas
acho que ele apenas dá a língua do dragão, não deveria ter a opção de escolher
qualquer uma".

O livro (p. 137, Gíria do Ladrão) diz: "Você conhece a Gíria dos Ladrões **e outro
idioma à sua escolha**, que você escolhe nas tabelas de idiomas no capítulo 2." Então
escolher está certo — o que estava errado era **o que a lista oferecia**: os 19
idiomas inteiros, incluindo a Gíria dos Ladrões que a própria característica acabou
de conceder, e o Comum, que todo personagem já fala (p. 37).

`com_proficiencia: false` é o filtro que o motor já sabe resolver, e agora resolve
também para idioma — antes `conceder_proficiencia` de categoria `idioma` caía em
`nao_consumidos` e ninguém sabia o que o personagem falava.

Vale igual para o Explorador Hábil do Guardião (p. 169), que tem a mesma forma.
"""
import json, os

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
p = os.path.join(D, 'caracteristicas.json')
doc = json.load(open(p, encoding='utf-8'))

ajustados = []


def anda(no, ctx):
    if isinstance(no, list):
        for x in no:
            anda(x, ctx)
        return
    if not isinstance(no, dict):
        return
    de = no.get('de')
    if no.get('tipo') == 'escolha' and isinstance(de, dict) and de.get('catalogo') == 'idiomas':
        filtro = de.setdefault('filtro_adicional', {})
        if 'com_proficiencia' not in filtro:
            filtro['com_proficiencia'] = False
            ajustados.append(f"{ctx}/{no.get('id')}")
    for v in no.values():
        anda(v, ctx)


for item in doc['itens']:
    anda(item.get('efeitos'), f"caracteristicas/{item['id']}")

json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok — escolhas de idioma que deixam de oferecer o que já se fala:', ', '.join(ajustados))
