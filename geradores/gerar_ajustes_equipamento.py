# -*- coding: utf-8 -*-
"""Religa o que dependia do capítulo 6.

1. Nomes alternativos nos itens: a tabela de Armaduras imprime 'Couro', e as
   páginas de classe escrevem 'Armadura de Couro'. O item é um só.
2. Dois itens que as classes citam e a tabela do capítulo 6 não tem:
   - Livro de Magias, definido na página do Mago (p. 147);
   - Símbolo Sagrado, que no capítulo 6 é uma CATEGORIA com três formas
     (Amuleto, Emblema, Relicário) — vira escolha, não item.
3. `equipamento_inicial` das 8 classes deixa de ser dúvida: cada id passa a
   apontar para um item que existe, e o que o livro escreve como categoria
   ('Foco Arcano (Cajado)') fica explícito.
"""
import json, collections

ITENS = 'dados/catalogos/itens.json'
CLASSES = 'dados/classes.json'

# nome na tabela do cap. 6 -> como as páginas de classe escrevem
ALTERNATIVOS = {
    'couro': ["Armadura de Couro"],
    'couro_batido': ["Armadura de Couro Batido"],
    'acolchoada': ["Armadura Acolchoada"],
    'gibao_de_peles': ["Gibão de Pele"],
    'cota_de_malha_parcial': ["Malha Parcial"],
    'placas_parcial': ["Armadura de Placas Parcial"],
    'placas': ["Armadura de Placas"],
    'flechas': ["Flecha"],
    'virotes': ["Virote"],
    'kit_de_explorador_de_masmorras': ["Kit de Explorador"],
}

NOTA_EXPLORADOR = (
    "A página do Druida (p. 92) escreve 'Kit de Explorador'; o capítulo 6 só tem "
    "'Kit de Explorador de Masmorras' (p. 226). Tratei como o mesmo kit — "
    "confira se concorda."
)

NOVOS = [
    collections.OrderedDict([
        ("id", "livro_de_magias"), ("nome", "Livro de Magias"),
        ("categoria", "equipamento_de_aventura"),
        ("peso_kg", 1.5), ("custo", None), ("custo_varia", True),
        ("descricao_curta", "Objeto Minúsculo de 100 páginas onde o Mago registra as "
                            "magias que conhece."),
        ("nota", "Não está na tabela do capítulo 6: é definido na característica de "
                 "Conjuração do Mago (p. 147)."),
        ("fonte", {"capitulo": 3, "pagina_livro": 147, "pagina_pdf": 151}),
    ]),
]

# 'Símbolo Sagrado' é categoria: três formas na tabela (p. 225)
SIMBOLOS = ["amuleto", "emblema", "relicario"]
FOCOS_ARCANOS = ["cajado", "cetro", "cristal", "orbe", "varinha"]
FOCOS_DRUIDICOS = ["cajado_de_madeira", "ramo_de_visco", "varinha_de_teixo"]

# ajustes por classe: id antigo -> novo (ou bloco inteiro quando vira escolha)
RENOMEAR = {
    'armadura_de_couro': 'couro',
    'armadura_de_couro_batido': 'couro_batido',
    'flecha': 'flechas',
    'foco_arcano_cajado': 'cajado',
    'foco_arcano_orbe': 'orbe',
    'foco_druidico_cajado': 'cajado_de_madeira',
    'kit_de_explorador': 'kit_de_explorador_de_masmorras',
    'livro_conhecimento_oculto': 'livro',
}
COMO = {
    'cajado': 'foco_arcano', 'orbe': 'foco_arcano',
    'cajado_de_madeira': 'foco_druidico',
}
NOTAS_DE_ITEM = {
    'livro': "O livro do Bruxo é de conhecimento oculto (p. 70).",
    'kit_de_explorador_de_masmorras': NOTA_EXPLORADOR,
}


def main():
    cat = json.load(open(ITENS, encoding='utf-8'),
                    object_pairs_hook=collections.OrderedDict)
    por_id = {i['id']: i for i in cat['itens']}
    for iid, alts in ALTERNATIVOS.items():
        if iid in por_id:
            por_id[iid]['nomes_alternativos'] = alts
    for novo in NOVOS:
        if novo['id'] not in por_id:
            cat['itens'].append(novo)
            por_id[novo['id']] = novo
    cat['itens'].sort(key=lambda x: (x['categoria'], x['id']))
    cat['total'] = len(cat['itens'])
    with open(ITENS, 'w', encoding='utf-8') as f:
        json.dump(cat, f, ensure_ascii=False, indent=2)

    cl = json.load(open(CLASSES, encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    trocados = 0
    for c in cl['itens']:
        eq = c.get('equipamento_inicial')
        if not eq:
            continue
        for op in eq.get('opcoes', []):
            novos_itens = []
            for it in op.get('itens', []):
                if 'item' not in it:
                    novos_itens.append(it)
                    continue
                antigo = it['item']
                if antigo == 'simbolo_sagrado':
                    # o livro dá a categoria; a forma é escolha do jogador
                    novos_itens.append(collections.OrderedDict([
                        ("id", f"{c['id']}_simbolo_sagrado"),
                        ("tipo", "escolha"),
                        ("rotulo", "Escolha a forma do seu Símbolo Sagrado"),
                        ("quantidade", 1),
                        ("de", {"catalogo": "itens", "chaves": SIMBOLOS}),
                        ("efeito_por_item_escolhido",
                         {"tipo": "conceder_proficiencia", "categoria": "item",
                          "chave": "{{escolhido}}"}),
                        ("nota", "No capítulo 6 (p. 225) 'Símbolo Sagrado' é uma "
                                 "categoria com três formas, não um item."),
                    ]))
                    trocados += 1
                    continue
                if antigo in RENOMEAR:
                    it['item'] = RENOMEAR[antigo]
                    trocados += 1
                if it['item'] in COMO:
                    it['como'] = COMO[it['item']]
                if it['item'] in NOTAS_DE_ITEM:
                    it['nota'] = NOTAS_DE_ITEM[it['item']]
                novos_itens.append(it)
            op['itens'] = novos_itens
        eq['revisao'] = {"status": "ok", "notas": ""}
        if c['id'] == 'druida':
            eq['revisao'] = {"status": "duvida", "notas": NOTA_EXPLORADOR}
    with open(CLASSES, 'w', encoding='utf-8') as f:
        json.dump(cl, f, ensure_ascii=False, indent=2)

    ids = set(por_id)
    fer = {i['id'] for i in json.load(open('dados/catalogos/ferramentas.json',
                                           encoding='utf-8'))['itens']}
    faltam = []
    for c in cl['itens']:
        for op in (c.get('equipamento_inicial') or {}).get('opcoes', []):
            for it in op.get('itens', []):
                if 'item' in it and it['item'] not in ids | fer:
                    faltam.append((c['id'], it['item']))
    print(f"itens: {cat['total']} | referências trocadas: {trocados}")
    print(f"equipamento inicial que ainda não resolve: {faltam if faltam else 'nenhum'}")


if __name__ == '__main__':
    main()
