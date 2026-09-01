# -*- coding: utf-8 -*-
"""Confere as paráfrases das magias contra o texto do livro.

Por que existe: as `descricao_curta` das 391 magias são escritas à mão por mim.
Escrever à mão é onde eu posso escorregar para o que "lembro" de D&D 5e 2014 em
vez do que a página 2024 diz — e escorreguei em oito magias. Este script não
julga estilo: ele pega TERMO POR TERMO os fatos verificáveis da paráfrase (dados
de dano, atributo da salvaguarda, condições, distâncias) e cobra que apareçam na
entrada da magia no PDF.

Falso positivo existe (o livro hifeniza, a entrada atravessa a página, a
paráfrase usa a palavra em sentido figurado). Por isso a saída é uma LISTA PARA
CONFERIR À MÃO, não um erro — o script aponta onde olhar.

Uso: python3 auditar_descricoes.py [--pdf CAMINHO]
"""
import json, re, sys, unicodedata, warnings

warnings.filterwarnings('ignore')

PDF = '/mnt/user-data/uploads/ficha-facil/DnD 5.5 - Livro do Jogador 2024 [PT] - Herois Anonimos.pdf'
if '--pdf' in sys.argv:
    PDF = sys.argv[sys.argv.index('--pdf') + 1]

CONDICOES = ['amedrontado', 'atordoado', 'caido', 'cego', 'contido', 'enfeiticado',
             'envenenado', 'imobilizado', 'incapacitado', 'inconsciente', 'invisivel',
             'paralisado', 'petrificado', 'surdo']
ATRIBUTOS = ['forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma']


def sem_acento(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def main():
    from pypdf import PdfReader
    r = PdfReader(PDF)
    mg = json.load(open('dados/catalogos/magias.json', encoding='utf-8'))
    cache = {}

    def pagina(p):
        """A entrada pode atravessar a página, e o livro hifeniza na quebra de linha
        ('Des - treza'). Junto três páginas e desfaço a hifenização antes de comparar."""
        if p not in cache:
            t = ''
            for i in (p + 3, p + 4, p + 5):
                if 0 <= i < len(r.pages):
                    t += r.pages[i].extract_text() + ' '
            t = re.sub(r'-\s*\n\s*', '', t)
            t = re.sub(r'\s*-\s+', '', t)
            cache[p] = sem_acento(re.sub(r'\s+', ' ', t))
        return cache[p]

    # o corpo que o parser isolou é mais preciso que a janela de páginas; uso os dois
    # e só reporto quando o termo falta NOS DOIS. Sozinha, a janela de páginas dava
    # dez falsos positivos por causa de entradas que atravessam a coluna.
    import parse_magias
    corpos = {}
    for e in parse_magias.parse():
        c = (e.get('_corpo') or '') + ' ' + ((e.get('aprimoramento') or {}).get('texto') or '')
        corpos[e['nome']] = sem_acento(re.sub(r'\s+', ' ', re.sub(r'\s*-\s+', '', c)))

    achados = []
    for i in mg['itens']:
        desc = i.get('descricao_curta') or ''
        if not desc:
            continue
        txt = pagina(i['fonte']['pagina_livro']) + ' ' + corpos.get(i['nome'], '')
        d = sem_acento(desc)
        faltas = []
        for dado in sorted(set(re.findall(r'\d+d\d+', d))):
            if dado not in txt:
                faltas.append(('dado', dado))
        for a in sorted(set(re.findall(r'salvaguarda de (' + '|'.join(ATRIBUTOS) + ')', d))):
            if f'salvaguarda de {a}' not in txt:
                faltas.append(('salvaguarda', a))
        for c in CONDICOES:
            if re.search(r'\b' + c + r'[ao]?s?\b', d) and c not in txt:
                faltas.append(('condicao', c))
        for m in sorted(set(re.findall(r'(\d+(?:[.,]\d+)?) m\b', d))):
            alvo = m.replace('.', ',')
            if f'{alvo} metro' not in txt:
                faltas.append(('distancia', m))
        if faltas:
            achados.append((i['id'], i['fonte']['pagina_livro'], faltas, desc))

    for mid, p, faltas, desc in achados:
        print(f"{mid} (p. {p})")
        for tipo, v in faltas:
            print(f"    {tipo}: '{v}' não aparece na entrada")
        print(f"    → {desc[:150]}")
    print(f"\n{len(achados)} magias para conferir à mão, de {len(mg['itens'])}.")
    print("Nem toda linha é defeito: confira cada uma contra a página antes de mexer.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
