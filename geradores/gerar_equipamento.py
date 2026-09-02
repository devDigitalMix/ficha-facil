# -*- coding: utf-8 -*-
"""Grava o capítulo 6 nos catálogos.

- `itens` deixa de ser parcial: 38 armas com dano/propriedades/maestria/peso/custo,
  13 armaduras, munição, equipamento de aventura, focos, montarias, arreios e
  veículos.
- `ferramentas` ganha atributo, peso, custo, o teste de Usar Objeto com a CD e a
  lista de Fabricação, com os itens resolvidos em ids sempre que possível.

O que a Fabricação cita e ainda não tem id vira `nao_resolvidos`, com nota — em
vez de sumir ou virar uma chave inventada.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos
import json, sys, re, collections

sys.path.insert(0, '.')
import parse_equipamento as P                                   # noqa: E402

TXT = caminhos.exigir('cap6.txt', 'gerar_equipamento.py')

# nome no singular da tabela de Armas -> id na tabela de Munição
MUNICAO = {'flecha': 'flechas', 'virote': 'virotes', 'agulha': 'agulhas'}
# 'Bala' serve para duas munições diferentes; a arma decide qual
MUNICAO_POR_ARMA = {
    ('funda', 'bala'): 'balas_funda',
    ('mosquete', 'bala'): 'balas_arma_de_fogo',
    ('pistola', 'bala'): 'balas_arma_de_fogo',
}
FONTE = {"capitulo": 6}

# páginas das tabelas (pagina_livro)
PAGINAS = {"arma": 215, "armadura": 219, "municao": 227,
           "equipamento_de_aventura": 222, "foco_de_conjuracao": 225,
           "montaria": 229, "arreio_ou_veiculo_de_tracao": 229, "veiculo": 230,
           "ferramenta": 220}


def fonte(cat):
    p = PAGINAS[cat]
    return {"capitulo": 6, "pagina_livro": p, "pagina_pdf": p + 4}


def main():
    t = open(TXT, encoding='utf-8').read()

    itens = []
    for a in P.ler_armas(t):
        a['propriedades'] = P.decompor_propriedades(a.pop('propriedades_texto'))
        # a tabela de Armas nomeia a munição no singular ('Flecha') e a tabela de
        # Munição no plural ('Flechas'); 'Bala' ainda é ambíguo entre as duas
        # linhas de bala. Resolvo pelo id real da munição.
        for prop in a['propriedades']:
            if prop.get('propriedade') == 'municao' and 'municao' in prop:
                prop['municao'] = MUNICAO_POR_ARMA.get(
                    (P.ident(a['nome']), prop['municao']),
                    MUNICAO.get(prop['municao'], prop['municao']))
        itens.append(a)
    itens += P.ler_armaduras(t)
    RECIPIENTES = {'estojo': 'estojo_virote_de_besta'}
    for m in P.ler_municao(t):
        m['armazenada_em'] = RECIPIENTES.get(m['armazenada_em'], m['armazenada_em'])
        itens.append(m)
    itens += P.ler_equipamento(t)
    itens += P.ler_focos(t)
    itens += P.ler_montarias(t)
    itens += P.ler_arreios(t)
    itens += P.ler_veiculos(t)

    vistos = {}
    finais = []
    for it in itens:
        it['id'] = P.ident(it['nome'])
        if it['id'] in vistos:
            # mesmo nome em duas tabelas (o Cajado é arma e foco arcano):
            # o item fica um só, com as duas categorias
            outro = vistos[it['id']]
            cats = outro.setdefault('tambem_e', [])
            if it['categoria'] not in cats:
                cats.append(it['categoria'])
            for k, v in it.items():
                if k not in outro and k not in ('id', 'nome', 'categoria'):
                    outro[k] = v
            continue
        it['fonte'] = fonte(it['categoria'])
        vistos[it['id']] = it
        finais.append(it)

    # O livro imprime 'Aeronau' na tabela de veículos; parece 'Aeronave' truncado,
    # mas não invento nome: fica como está, marcado para você decidir.
    for it in finais:
        if it['id'] == 'aeronau':
            it['revisao'] = {"status": "duvida",
                             "notas": "O livro imprime 'Aeronau' (p. 230). Parece "
                                      "'Aeronave' truncado, mas mantive como está impresso."}

    ordem = ['id', 'nome', 'categoria']
    def ordenar(d):
        return collections.OrderedDict(
            [(k, d[k]) for k in ordem if k in d] +
            [(k, v) for k, v in d.items() if k not in ordem])
    finais = [ordenar(d) for d in sorted(finais, key=lambda x: (x['categoria'], x['id']))]

    cat = collections.OrderedDict([
        ("catalogo", "itens"),
        ("nome", "Itens de Equipamento"),
        ("fonte", {"capitulo": 6, "pagina_livro": 213, "pagina_pdf": 217}),
        ("nota", "Capítulo 6 completo: armas, armaduras, munição, equipamento de "
                 "aventura, focos de conjuração, montarias, arreios e veículos. "
                 "Itens mágicos ficam no Livro do Mestre e estão fora do escopo."),
        ("total", len(finais)),
        ("itens", finais),
    ])
    with open('dados/catalogos/itens.json', 'w', encoding='utf-8') as f:
        json.dump(cat, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------- ferramentas
    ids_de_item = {i['id'] for i in finais}
    fer_cat = json.load(open('dados/catalogos/ferramentas.json', encoding='utf-8'),
                        object_pairs_hook=collections.OrderedDict)
    por_id = {i['id']: i for i in fer_cat['itens']}
    lidas = 0
    for f in P.ler_ferramentas(t):
        alvo = por_id.get(P.ident(f['nome']))
        if alvo is None:
            continue
        lidas += 1
        alvo['atributo'] = f['atributo']
        alvo['peso_kg'] = f['peso_kg']
        alvo['custo'] = f['custo']
        for k in ('custo_varia', 'peso_varia'):
            if f.get(k):
                alvo[k] = True
        if 'usar_objeto' in f:
            alvo['usar_objeto'] = f['usar_objeto']
        if 'fabricacao_texto' in f:
            resolvidos, soltos = resolver_fabricacao(f['fabricacao_texto'], ids_de_item)
            alvo['fabricacao'] = {"texto": f['fabricacao_texto'], "itens": resolvidos}
            if soltos:
                alvo['fabricacao']['nao_resolvidos'] = soltos
        alvo['fonte'] = fonte('ferramenta')
    fer_cat['total'] = len(fer_cat['itens'])
    fer_cat['parcial'] = False
    fer_cat['nota'] = ("As 25 ferramentas do capítulo 6 (p. 220-222), com atributo, "
                       "peso, custo, o teste de Usar Objeto e a lista de Fabricação.")
    with open('dados/catalogos/ferramentas.json', 'w', encoding='utf-8') as f:
        json.dump(fer_cat, f, ensure_ascii=False, indent=2)

    print(f"itens: {len(finais)}")
    for c, n in collections.Counter(i['categoria'] for i in finais).most_common():
        print(f"   {c:32s} {n}")
    print(f"ferramentas detalhadas: {lidas}")
    n_res = sum(len(i.get('fabricacao', {}).get('itens', [])) for i in fer_cat['itens'])
    n_sol = sum(len(i.get('fabricacao', {}).get('nao_resolvidos', [])) for i in fer_cat['itens'])
    print(f"fabricação: {n_res} itens resolvidos, {n_sol} não resolvidos")


# nomes que a lista de Fabricação usa e que não são um item único
GENERICOS = {
    'qualquer arma corpo a corpo', 'armas a distancia', 'armadura media',
    'armadura pesada', 'armadura leve', 'foco arcano', 'foco druidico',
    'instrumentos musicais', 'itens de vidro', 'roupas', 'joias',
    'simbolo sagrado',      # amuleto, emblema ou relicário — é uma categoria
    'pergaminho magico',    # há dois: Truque e 1º Círculo
}
# grafias que a lista de Fabricação usa diferentes da tabela de itens
SINONIMOS = {
    'armadura de couro': 'couro',
    'armadura de couro batido': 'couro_batido',
    'estojo de mapa ou pergaminho': 'estojo_mapa_ou_pergaminho',
    'estojo de virotes de besta': 'estojo_virote_de_besta',
    'panela de ferro': 'pote_ferro',
    'arpeu e gancho': 'arpeu',
    'balas de arma de fogo': 'balas_arma_de_fogo',
    'balas de funda': 'balas_funda',
    'dardos': 'dardo',
    'flechas': 'flechas',
    'virotes': 'virotes',
    'armadura acolchoada': 'acolchoada',
    'roupas de viagem': 'roupas_viagem',
    'fantasia': 'roupas_fantasia',
    'cadeado ou fechadura': 'cadeado',
}


def resolver_fabricacao(texto, ids):
    """Quebra a lista de Fabricação em ids, guardando o que não resolve."""
    partes, atual, prof = [], '', 0
    for c in texto:
        if c == '(':
            prof += 1
        elif c == ')':
            prof -= 1
        if c == ',' and prof == 0:
            partes.append(atual); atual = ''
        else:
            atual += c
    partes.append(atual)
    resolvidos, soltos = [], []
    for p in partes:
        p = re.sub(r'\(.*?\)', '', p).strip(' .')
        if not p:
            continue
        n = P.norm(p)
        if n in GENERICOS:
            soltos.append({"texto": p, "motivo": "descrição genérica, não é um item único"})
            continue
        alvo = SINONIMOS.get(n, P.ident(p))
        if alvo in ids:
            resolvidos.append(alvo)
        elif P.ident(p).rstrip('s') in ids:
            resolvidos.append(P.ident(p).rstrip('s'))
        else:
            soltos.append({"texto": p, "motivo": "sem item correspondente na tabela"})
    return resolvidos, soltos


if __name__ == '__main__':
    main()
