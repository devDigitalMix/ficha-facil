# -*- coding: utf-8 -*-
"""Extrai a Lista de Magias do Mago (cap. 3, p. 150-153) direto do PDF.

Parser em vez de transcrição manual: menos chance de eu errar um nome ou uma escola.
Tudo que não casar é impresso para revisão em vez de ser descartado em silêncio.
"""
import pypdf, warnings, re, json, unicodedata, os
warnings.filterwarnings('ignore')
PDF = '/mnt/user-data/uploads/ficha-facil/DnD 5.5 - Livro do Jogador 2024 [PT] - Herois Anonimos.pdf'
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')

ESCOLAS = {"Abjuração":"abjuracao","Adivinhação":"adivinhacao","Encantamento":"encantamento",
 "Evocação":"evocacao","Ilusão":"ilusao","Invocação":"invocacao","Necromancia":"necromancia",
 "Transmutação":"transmutacao"}
ESC_RE = "|".join(ESCOLAS)

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode()
    return re.sub(r'[^a-z0-9]+','_', s.lower()).strip('_')

r = pypdf.PdfReader(PDF)
bruto = []
for i in range(153, 157):
    bruto.append((i, r.pages[i].extract_text() or ''))

texto = "\n".join(t for _, t in bruto)
# junta quebras onde o nome da magia continuou na linha seguinte colado na escola
texto = re.sub(r'\n(?=\w+(?:%s))' % ESC_RE, ' ', texto)
# nomes que quebram ANTES de uma preposição ('Tempestade Radiante\nde JallazarEvocação C')
texto = re.sub(r'\n(?=(?:de|da|do|dos|das) \w+(?:%s))' % ESC_RE, ' ', texto)
texto = texto.replace('­', '')

circulo_atual, saida, nao_casou = None, [], []
CAB = re.compile(r'Truques \(Magias de Mago de Círculo 0\)|Magias de Mago de (\d)º Círculo')
LINHA = re.compile(r'^(.+?)\s*(%s)\s*(C, R|R, M|C, M|C|R|M|—|-)\s*$' % ESC_RE)
IGNORAR = re.compile(r'^(Magia\s+Escola\s+Especial|CAPÍTULO 3.*|\d+|Esta seção apresenta.*|'
                     r'nizadas por círculo.*|com suas respectivas.*|indica que a magia.*|'
                     r'e M que necessita.*|Lista de Magias do Mago|[A-Z ]{4,}|O arcano Leomund.*|'
                     r'para preparar suas magias\.?.*)$')

for linha in texto.split('\n'):
    linha = linha.strip()
    if not linha:
        continue
    cab = CAB.search(linha)
    if cab:
        circulo_atual = 0 if 'Círculo 0' in linha else int(cab.group(1))
        linha = CAB.sub('', linha).strip()
        if not linha:
            continue
    # uma linha pode trazer o cabeçalho da próxima coluna grudado
    linha = re.sub(r'Magia\s+Escola\s+Especial\s*$', '', linha).strip()
    m = LINHA.match(linha)
    if m and circulo_atual is not None:
        nome = re.sub(r'\s+', ' ', m.group(1)).strip()
        nome = re.sub(r'^(Magia\s+Escola\s+Especial)\s*', '', nome).strip()
        esp = m.group(3)
        saida.append({"id": slug(nome), "nome": nome, "nivel": circulo_atual,
                      "escola": ESCOLAS[m.group(2)],
                      "concentracao": 'C' in esp, "ritual": 'R' in esp,
                      "componente_material_especifico": 'M' in esp,
                      "listas": ["mago"],
                      "fonte": {"capitulo": 3, "pagina_livro": 150, "pagina_pdf": 154}})
    elif not IGNORAR.match(linha):
        nao_casou.append((circulo_atual, linha))

print("magias por círculo:")
from collections import Counter
c = Counter(x['nivel'] for x in saida)
for k in sorted(c): print(f"  círculo {k}: {c[k]}")
print("TOTAL:", len(saida))
print("\nlinhas não reconhecidas (revisar):")
for n, l in nao_casou: print("  ", n, "|", l[:90])
json.dump(saida, open('/tmp/lista_mago.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
