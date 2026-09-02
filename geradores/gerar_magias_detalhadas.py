# -*- coding: utf-8 -*-
"""Grava no catálogo os detalhes do capítulo 7 para o primeiro terço das magias.

Faz três coisas:
1. Acrescenta as magias do cap. 7 que ainda não estavam no catálogo (elas vinham
   só das quatro listas de classe já parseadas, então faltavam as de Bardo,
   Feiticeiro, Guardião e Paladino).
2. Corrige o que a checagem cruzada acusou: escola divergente entre a lista de
   classe e a entrada da magia — vale a entrada — e o nome de Jallarzi.
3. Detalha as 130 primeiras em ordem alfabética: campos do topo, mecânica
   reconhecida e a descrição em paráfrase escrita à mão.

Magia detalhada leva `detalhada: true`; o validador cobra os campos obrigatórios
só dessas, para o resto do capítulo poder entrar em lotes.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos
import json, sys, unicodedata, collections, re

sys.path.insert(0, '.')
from parse_magias import parse, norm                       # noqa: E402
from descricoes_magias import DESCRICOES                    # noqa: E402

CATALOGO = 'dados/catalogos/magias.json'
QUANTAS = 391   # capítulo 7 inteiro
ALIAS_ESCOLA = {'conjuracao': 'invocacao'}   # o livro alterna os dois nomes

# escola que a lista de classe imprime diferente da entrada da própria magia.
# Regra do projeto (fixada no caso "Remeter"): vale a entrada do capítulo 7.
DIVERGENCIAS_DE_ESCOLA = {
    'consagrar':          "A lista do Clérigo (p. 84) diz Evocação; a entrada (p. 264) diz Abjuração.",
    'esfera_flamejante':  "As listas de Druida (p. 95) e Mago (p. 150) dizem Evocação; a entrada (p. 279) diz Invocação.",
}


def ident(nome):
    s = norm(nome)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip('_')
    return s


def circulo_para_fonte(e):
    return {"capitulo": 7, "pagina_livro": None, "pagina_pdf": None}


def main():
    cat = json.load(open(CATALOGO, encoding='utf-8'),
                    object_pairs_hook=collections.OrderedDict)
    por_nome = {}
    for m in cat['itens']:
        por_nome[norm(m['nome'])] = m
        for a in m.get('nomes_alternativos', []):
            por_nome[norm(a)] = m

    # As duas grafias do livro para a mesma magia tinham virado DUAS entradas:
    # a lista do Bruxo (p. 74) escreve 'Jallarzi' e a do Mago (p. 152) 'Jallazar'.
    # A entrada do capítulo 7 (p. 342) diz Jallarzi, então essa é a canônica; a
    # outra é fundida nela, somando as listas.
    jall = [m for m in cat['itens'] if m['id'].startswith('tempestade_radiante')]
    if len(jall) > 1:
        principal = next(m for m in jall if m['id'].endswith('jallarzi'))
        for outra in jall:
            if outra is principal:
                continue
            principal['listas'] = sorted(set(principal.get('listas') or []) |
                                         set(outra.get('listas') or []))
            principal.setdefault('nomes_alternativos', []).append(outra['nome'])
            cat['itens'].remove(outra)
        principal['nota_de_divergencia'] = (
            "A lista do Mago (p. 152) grafa 'Jallazar'; a entrada (p. 342) e a lista do "
            "Bruxo (p. 74) grafam 'Jallarzi'. Vale a entrada. As duas grafias tinham "
            "criado duas magias no catálogo; foram fundidas.")
        por_nome = {}
        for m in cat['itens']:
            por_nome[norm(m['nome'])] = m
            for a in m.get('nomes_alternativos', []):
                por_nome[norm(a)] = m

    ms = parse()
    ms.sort(key=lambda e: norm(e['nome']))

    novas, detalhadas, escolas_corrigidas = [], 0, []
    for pos, e in enumerate(ms):
        k = norm(e['nome'])
        alvo = por_nome.get(k)
        if alvo is None:
            alvo = collections.OrderedDict([
                ("id", ident(e['nome'])), ("nome", e['nome']),
                ("nivel", e['circulo']),
                ("escola", ALIAS_ESCOLA.get(norm(e['escola']), norm(e['escola']))),
                ("concentracao", e['duracao']['concentracao']),
                ("ritual", e['tempo_de_conjuracao']['ritual']),
                ("componente_material_especifico",
                 bool(e['componentes'].get('material_descricao'))),
                ("listas", [norm(x) for x in e['listas']]),
                ("fonte", {"capitulo": 7, "pagina_livro": e['pagina_livro'],
                           "pagina_pdf": e['pagina_livro'] + 4}),
            ])
            cat['itens'].append(alvo)
            por_nome[k] = alvo
            novas.append(e['nome'])

        # a fonte passa a apontar para a ENTRADA da magia, não para a tabela da
        # lista de classe de onde o nome tinha saído
        alvo['fonte'] = {"capitulo": 7, "pagina_livro": e['pagina_livro'],
                         "pagina_pdf": e['pagina_livro'] + 4}

        # o círculo também sai da ENTRADA, não da tabela da lista de classe. Sem isto,
        # magia que entrou no catálogo como stub com 'nivel': None (gerar_bruxo_magias.py
        # grava None quando a raspagem do cabeçalho falha) ficava sem círculo para sempre:
        # o setdefault dos geradores de lista não substitui chave que já existe com None.
        # Numa reconstrução do zero isso derrubava Raio Guia e Dominar Fera.
        if alvo.get('nivel') != e['circulo']:
            alvo['nivel'] = e['circulo']

        # escola: a entrada do capítulo 7 é a autoridade
        esc = ALIAS_ESCOLA.get(norm(e['escola']), norm(e['escola']))
        if alvo.get('escola') != esc:
            nota = DIVERGENCIAS_DE_ESCOLA.get(alvo['id'])
            escolas_corrigidas.append((alvo['nome'], alvo.get('escola'), esc))
            alvo['escola'] = esc
            if nota:
                alvo['nota_de_divergencia'] = nota

        # listas: a entrada traz TODAS as classes; as parseadas eram só quatro
        listas = sorted({norm(x) for x in e['listas']} | set(alvo.get('listas') or []))
        alvo['listas'] = listas

        if pos >= QUANTAS:
            continue

        desc = DESCRICOES.get(e['nome'])
        if not desc:
            raise SystemExit(f"falta descrição escrita à mão: {e['nome']}")

        alvo['concentracao'] = e['duracao']['concentracao']
        alvo['ritual'] = e['tempo_de_conjuracao']['ritual']
        alvo['componente_material_especifico'] = bool(
            e['componentes'].get('material_descricao'))
        alvo['descricao_curta'] = desc
        alvo['tempo_de_conjuracao'] = e['tempo_de_conjuracao']
        alvo['alcance'] = e['alcance']
        comp = dict(e['componentes'])
        if comp.get('material'):
            # Regra do cap. 7 (p. 237): material sem custo declarado e que não é
            # consumido pode ser trocado por Bolsa de Componentes ou Foco de
            # Conjuração. Fica no dado para o app não precisar deduzir.
            subs = (not comp.get('material_consumido')
                    and 'material_custo_po' not in comp)
            comp['substituivel_por_foco_ou_bolsa'] = subs
            comp['regra'] = (
                "Sem custo declarado e sem consumo: vale Bolsa de Componentes ou Foco "
                "de Conjuração (p. 237)." if subs else
                "Material com custo ou consumido: precisa ser fornecido de verdade "
                "(p. 237).")
        alvo['componentes'] = comp
        alvo['duracao'] = e['duracao']
        for campo in ('dano', 'dano_adicional_citado', 'salvaguarda', 'area',
                      'ataque', 'cura', 'condicoes_citadas', 'aprimoramento'):
            if campo in e:
                alvo[campo] = e[campo]
        alvo['detalhada'] = True
        detalhadas += 1

    cat['total'] = len(cat['itens'])
    cat['detalhadas'] = detalhadas
    cat['parcial'] = detalhadas < cat['total']
    cat['nota'] = (
        f"{detalhadas} das {cat['total']} magias estão detalhadas com os campos do "
        "capítulo 7 (marcadas com 'detalhada': true). As demais têm só nome, círculo, "
        "escola e listas.")
    with open(CATALOGO, 'w', encoding='utf-8') as f:
        json.dump(cat, f, ensure_ascii=False, indent=2)

    print(f"magias no catálogo: {cat['total']} (eram {cat['total'] - len(novas)})")
    print(f"novas do cap. 7: {len(novas)}")
    print(f"detalhadas: {detalhadas}")
    print("escolas corrigidas pela entrada da magia:")
    for n, de, para in escolas_corrigidas:
        print(f"   {n}: {de} -> {para}")


if __name__ == '__main__':
    main()
