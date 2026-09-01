# -*- coding: utf-8 -*-
"""Lista do Bruxo (91) + as magias de patrono que ainda faltavam no catálogo."""
import pypdf, warnings, re, json, os, unicodedata
warnings.filterwarnings('ignore')
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
PDF = '/mnt/user-data/uploads/ficha-facil/DnD 5.5 - Livro do Jogador 2024 [PT] - Herois Anonimos.pdf'
def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode()
    return re.sub(r'[^a-z0-9]+','_', s.lower()).strip('_')

m = json.load(open(os.path.join(D,'catalogos/magias.json'), encoding='utf-8'))
por = {i['id']: i for i in m['itens']}

# 1) lista do Bruxo
for x in json.load(open('/tmp/lista_bruxo.json', encoding='utf-8')):
    x.pop('_escola_no_livro', None)
    if x['id'] in por:
        alvo = por[x['id']]
        alvo.setdefault('listas', [])
        if 'bruxo' not in alvo['listas']: alvo['listas'].append('bruxo')
        for k in ('escola','concentracao','ritual','componente_material_especifico','nivel'):
            alvo.setdefault(k, x[k])
    else:
        por[x['id']] = x
# Fome de Hadar: o livro escreve a escola como "Conjuração" aqui e "Invocação" no resto
if 'fome_de_hadar' in por:
    por['fome_de_hadar']['nota'] = ("O livro grafa a escola como 'Conjuração' nesta entrada e como "
                                    "'Invocação' no resto do material. Normalizado para 'invocacao'.")

# 2) magias concedidas pelos patronos que ainda não estavam no catálogo
PATRONO = [
 "Acalmar Emoções","Fogo das Fadas","Força Espectral","Passo Nebuloso","Sono",
 "Crescimento de Plantas","Piscar","Dominar Fera","Invisibilidade Maior","Dominar Pessoa","Similaridade",
 "Auxílio","Chama Sagrada","Curar Ferimentos","Luz","Raio Guia","Restauração Menor",
 "Luz do Dia","Revivificar","Defensor da Fé","Muralha de Fogo","Convocar Celestial","Restauração Maior",
 "Detectar Pensamentos","Gargalhada Nefasta de Tasha","Sussurros Dissonantes","Clarividência",
 "Fome de Hadar","Confusão","Invocar Aberração","Modificar Memória","Telecinese",
 "Comando","Mãos Flamejantes","Raio Ardente","Sugestão","Bola de Fogo","Nuvem Fétida",
 "Escudo Ardente","Missão","Praga de Insetos","Contato Extraplanar","Danação","Armadura Arcana",
 "Convocar Familiar","Disfarçar-se","Alterar-se","Levitação","Respirar na Água","Invisibilidade",
 "Vitalidade Vazia","Olho Arcano","Imagem Silenciosa","Salto","Falar com Mortos",
]
faltando = [n for n in PATRONO if slug(n) not in por]
if faltando:
    r = pypdf.PdfReader(PDF)
    paginas = {}
    for i in range(242, 347):
        t = r.pages[i].extract_text() or ''
        for n in faltando:
            # o nome pode vir colado no fim do parágrafo anterior (sem \n antes); por isso
            # aceito também 'NomeDaMagia\n<círculo>' logo antes da linha do círculo.
            if n not in paginas and (re.search(r'\n' + re.escape(n) + r'\n', t)
                                     or re.search(re.escape(n) + r'\n(?:\d)º Círculo|'
                                                  + re.escape(n) + r'\nTruque', t)):
                paginas[n] = i - 3
    CIRC = re.compile(r'(\d)º Círculo|Truque')
    for n in faltando:
        pg = paginas.get(n)
        entrada = {"id": slug(n), "nome": n, "fonte": {"capitulo": 7, "pagina_livro": pg,
                   "pagina_pdf": (pg + 4) if pg else None} if pg else None,
                   "parcial": True,
                   "nota": "Referenciada por característica de classe/subclasse; detalhes vêm com o cap. 7."}
        if pg:
            t = r.pages[pg + 3].extract_text() or ''
            j = t.find('\n' + n + '\n')
            cab = t[j:j + 200]
            mc = re.search(r'(\d)º Círculo', cab)
            entrada['nivel'] = int(mc.group(1)) if mc else (0 if 'Truque' in cab else None)
            listas = re.search(r'\(([^)]+)\)', cab)
            if listas:
                entrada['listas'] = [slug(x.strip()) for x in listas.group(1).split(',')]
        por[n and slug(n)] = entrada
m['itens'] = sorted(por.values(), key=lambda x: (x.get('nivel') if x.get('nivel') is not None else 99, x['id']))
m['total'] = len(m['itens'])
m['listas_completas'] = sorted(set(m.get('listas_completas', []) + ['mago', 'bruxo']))
m['nota'] = ("Listas COMPLETAS: Mago (242, p. 150-153) e Bruxo (91, p. 73-75). Outras entradas são "
             "parciais, presentes porque alguma característica as referencia; o texto completo de "
             "cada magia vem na fase do capítulo 7.")
json.dump(m, open(os.path.join(D,'catalogos/magias.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=2)

lm = json.load(open(os.path.join(D,'catalogos/listas_de_magia.json'), encoding='utf-8'))
for l in lm['itens']:
    if l['id'] == 'bruxo':
        l['preenchida'] = True
        l['total_de_magias'] = 91
        l['fonte'] = {"capitulo": 3, "pagina_livro": 73, "pagina_pdf": 77}
json.dump(lm, open(os.path.join(D,'catalogos/listas_de_magia.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('magias no catálogo:', m['total'], '| novas de patrono:', len(faltando))
