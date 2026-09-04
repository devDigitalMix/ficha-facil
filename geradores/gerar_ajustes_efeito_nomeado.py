# -*- coding: utf-8 -*-
"""`aplicar_efeito_nomeado` que vem de um catálogo passa a DIZER de qual.

Defeitos relatados pelo João em 2026-09-04, montando um Bruxo e um Bardo:

    efeito nomeado 'pacto_da_lamina' não existe em 'invocacoes_misticas'
    efeito nomeado 'padrao' não existe em 'inspiracao_de_bardo'

Eram dois sintomas de uma coisa só, e a varredura achou **15 lugares**, não dois.

O padrão que quebra é sempre o mesmo: a escolha oferece itens de um catálogo
(`de: {catalogo: 'invocacoes_misticas'}`), e o `efeito_por_item_escolhido` é um
`aplicar_efeito_nomeado` com `chave: {{escolhido}}` — mas **sem dizer o catálogo**.
Sem essa palavra, o coletor procura a chave em `dono.efeitos_nomeados`, que nesses
casos nem existe, e o motor derruba a montagem inteira.

É o mesmo defeito da fase 21 visto pelo outro lado: lá o efeito declarava `catalogo`
e o motor ignorava; aqui o motor lê, e o dado é que não declara. As duas metades
juntas cobriam quase todas as classes — Guerreiro (manobras), Bruxo (invocações),
Bárbaro (golpe brutal, fúria/aspecto/poder dos selvagens), Ladino (golpe astuto),
Bardo (inspiração), Feiticeiro (metamagia, surtos), Druida (passos feéricos),
Vigilante (revelação em carne) e dois talentos.

A regra que este gerador aplica é mecânica e conferível: **se a escolha tira as
opções de um catálogo e o efeito aplicado é `aplicar_efeito_nomeado` sem `catalogo`,
o catálogo é o da escolha.** Nada é adivinhado — quando o dono tem `efeitos_nomeados`
com aquela chave, não se toca em nada.

Fecha com guarda: o `validar.py` passou a exigir que todo `aplicar_efeito_nomeado`
resolva, pelo dono ou pelo catálogo. Isso não podia ficar para o teste de tela achar.
"""
import json, os

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')


def carregar():
    docs = {}
    for f in sorted(os.listdir(D)):
        if f.endswith('.json'):
            docs[os.path.join(D, f)] = json.load(open(os.path.join(D, f), encoding='utf-8'))
    cat = os.path.join(D, 'catalogos')
    for f in sorted(os.listdir(cat)):
        if f.endswith('.json'):
            docs[os.path.join(cat, f)] = json.load(open(os.path.join(cat, f), encoding='utf-8'))
    return docs


docs = carregar()
por_catalogo = {
    os.path.basename(c)[:-5]: {i['id']: i for i in d.get('itens', [])}
    for c, d in docs.items()
}

consertados = []


def anda(no, dono, ctx, catalogo_da_escolha=None):
    """Percorre a árvore de efeitos carregando o catálogo que a escolha mais próxima
    declarou — que é a única informação que falta ao efeito aplicado."""
    if isinstance(no, list):
        for x in no:
            anda(x, dono, ctx, catalogo_da_escolha)
        return
    if not isinstance(no, dict):
        return

    if no.get('tipo') == 'aplicar_efeito_nomeado' and 'catalogo' not in no:
        chave = no.get('chave')
        nomeados = (dono.get('efeitos_nomeados') or {})
        # O dono resolve? Então está certo como está — são 16 dos 31 usos.
        resolve_no_dono = chave in nomeados if chave != '{{escolhido}}' else bool(nomeados)
        if not resolve_no_dono and catalogo_da_escolha:
            no['catalogo'] = catalogo_da_escolha
            consertados.append(f"{ctx}: '{chave}' → catálogo '{catalogo_da_escolha}'")

    proximo = catalogo_da_escolha
    if no.get('tipo') == 'escolha':
        proximo = (no.get('de') or {}).get('catalogo') or catalogo_da_escolha
    for v in no.values():
        anda(v, dono, ctx, proximo)


for caminho, doc in docs.items():
    nome = os.path.basename(caminho)[:-5]
    for item in doc.get('itens', []):
        # Um item de catálogo que aponta para um IRMÃO — a Dádiva do Caos manda
        # aplicar o efeito cosmético da própria tabela de surtos. O catálogo aqui é
        # o do próprio item.
        anda(item.get('efeitos'), item, f'{nome}/{item["id"]}', nome)

for caminho, doc in docs.items():
    json.dump(doc, open(caminho, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print(f'ok — {len(consertados)} efeitos nomeados passaram a dizer o catálogo:')
for c in consertados:
    print('   ', c)
