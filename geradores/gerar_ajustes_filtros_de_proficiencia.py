# -*- coding: utf-8 -*-
"""Três chaves de filtro inventadas, em nove escolhas, que casavam com nada.

O João, montando um Ladino em 2026-09-04: "a escolha de perícias de especialização
não mostra nada nem a do tipo de arma".

A da Especialização dizia `filtro_adicional: {ja_proficiente: true}`. Só que
`ja_proficiente` não é campo de `pericias` nem filtro que o motor prometa resolver:
o motor caía no ramo genérico (`item['ja_proficiente'] === true`), que é falso para
toda perícia — e a escolha ficava com **zero opções, em silêncio**.

Não era só o Ladino. A varredura achou **nove escolhas e três chaves**:

  ja_proficiente               → com_proficiencia          (Acadêmico do Mago,
                                 Especialista do Ladino e do Bardo, Mestre das Armas,
                                 e os dois talentos de Especialização em perícia)
  sem_especializacao           → ainda_nao_especialista    (os dois talentos)
  sem_proficiencia_em_salvaguarda → o próprio nome, agora resolvido pelo motor
                                 (Resiliente: "escolha um atributo em que você NÃO
                                 tenha proficiência em salvaguardas", p. 203)

As duas primeiras já existiam com outro nome no vocabulário do motor; a terceira
passou a existir. Nenhuma regra do livro muda aqui — o que muda é o dado deixar de
pedir uma coisa que ninguém sabia responder.

Fecha com guarda: o `validar.py` só conferia as chaves de `filtro`, e não as de
`filtro_adicional`. Era exatamente a fresta por onde as nove passaram.
"""
import json, os

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')

RENOMES = {
    'ja_proficiente': 'com_proficiencia',
    'sem_especializacao': 'ainda_nao_especialista',
}

trocados = []


def anda(no, ctx):
    if isinstance(no, list):
        for x in no:
            anda(x, ctx)
        return
    if not isinstance(no, dict):
        return
    for onde in ('filtro', 'filtro_adicional'):
        f = no.get(onde)
        if not isinstance(f, dict):
            continue
        for velho, novo in RENOMES.items():
            if velho in f:
                f[novo] = f.pop(velho)
                trocados.append(f"{ctx}: {onde}.{velho} → {novo}")
    for v in no.values():
        anda(v, ctx)


for caminho in [os.path.join(D, 'caracteristicas.json'),
                os.path.join(D, 'catalogos', 'talentos.json'),
                os.path.join(D, 'subclasses.json'),
                os.path.join(D, 'catalogos', 'especies.json'),
                os.path.join(D, 'catalogos', 'antecedentes.json')]:
    doc = json.load(open(caminho, encoding='utf-8'))
    for item in doc.get('itens', []):
        anda(item.get('efeitos'), f"{os.path.basename(caminho)[:-5]}/{item['id']}")
    json.dump(doc, open(caminho, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print(f'ok — {len(trocados)} filtros renomeados para o vocabulário que o motor resolve:')
for t in trocados:
    print('   ', t)
