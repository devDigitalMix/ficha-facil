# -*- coding: utf-8 -*-
"""Parser genérico das listas de magia por classe do capítulo 3.

Uso: python3 parse_lista_magias.py <lista_id> <idx_inicial> <idx_final> <pagina_livro>
Generalizado a partir do parser da lista do Mago. Imprime o que não casou.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos
import pypdf, warnings, re, json, unicodedata, sys, os
from collections import Counter
warnings.filterwarnings('ignore')
PDF = caminhos.pdf()

ESCOLAS = {"Abjuração":"abjuracao","Adivinhação":"adivinhacao","Encantamento":"encantamento",
 "Evocação":"evocacao","Ilusão":"ilusao","Invocação":"invocacao","Necromancia":"necromancia",
 "Transmutação":"transmutacao",
 # O livro usa "Conjuração" em algumas entradas onde usa "Invocação" em outras (ex.: Fome de
 # Hadar, na lista do Bruxo). Mesma escola (Conjuration); normalizo e registro a ocorrência.
 "Conjuração":"invocacao"}
ALIAS_ESCOLA = {"Conjuração": "Invocação"}
ESC_RE = "|".join(ESCOLAS)

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode()
    return re.sub(r'[^a-z0-9]+','_', s.lower()).strip('_')

def _entrada_direta(nome, escola, esp, circ, lista_id, pagina_livro):
    nome = re.sub(r'\s+', ' ', nome).strip()
    return {"id": slug(nome), "nome": nome, "nivel": circ, "escola": ESCOLAS[escola],
            **({"_escola_no_livro": escola} if escola in ALIAS_ESCOLA else {}),
            "concentracao": 'C' in esp, "ritual": 'R' in esp,
            "componente_material_especifico": 'M' in esp, "listas": [lista_id],
            "fonte": {"capitulo": 3, "pagina_livro": pagina_livro, "pagina_pdf": pagina_livro + 4}}


def parse(lista_id, ini, fim, pagina_livro, marcador_inicial=None, marcador_final=None):
    r = pypdf.PdfReader(PDF)
    texto = "\n".join((r.pages[i].extract_text() or '') for i in range(ini, fim + 1))
    if marcador_inicial:
        k = texto.find(marcador_inicial)
        if k >= 0: texto = texto[k:]
    if marcador_final:
        k = texto.find(marcador_final)
        if k >= 0: texto = texto[:k]
    # créditos de arte grudados no fim da linha (ex.: '—WAYNE ENGLAND')
    texto = re.sub(r'(—|C|R|M)([A-ZÁÉÍÓÚÃÕÇ]{4,}(?: [A-ZÁÉÍÓÚÃÕÇ]{2,})*)\s*$', r'\1',
                   texto, flags=re.M)
    texto = re.sub(r'\n(?=\w+(?:%s))' % ESC_RE, ' ', texto)
    texto = re.sub(r'\n(?=(?:de|da|do|dos|das|e) [\wÀ-ÿ]+(?:%s))' % ESC_RE, ' ', texto)
    texto = texto.replace('­', '')

    CAB = re.compile(r'Truques \(Magias de \w+ de (?:Círculo )?0(?: Círculo)?\)|'
                     r'Magias de \w+ de (\d)º Círculo')
    LINHA = re.compile(r'^(.+?)\s*(%s)\s*(C, R|R, M|C, M|C|R|M|—|-)\s*$' % ESC_RE)
    # Em algumas páginas duas ou três colunas caem na MESMA linha extraída. Este scanner
    # encontra cada par (escola, marcador) e toma como nome o texto desde o fim do anterior.
    PAR = re.compile(r'\s*(%s)\s+(C, R|R, M|C, M|C|R|M|—|-)(?=\s|$)' % ESC_RE)

    def varrer_linha(linha, circ):
        achados, fim = [], 0
        for mm in PAR.finditer(linha):
            nome = linha[fim:mm.start()].strip()
            nome = re.sub(r'^(Magia\s+Escola\s+Especial)\s*', '', nome).strip()
            fim = mm.end()
            if nome:
                achados.append((nome, mm.group(1), mm.group(2)))
        return achados, linha[fim:].strip()
    IGNORAR = re.compile(r'^(Magia\s+Escola\s+Especial|CAPÍTULO 3.*|\d+|Esta seção apresenta.*|'
                         r'.*nizadas por círculo.*|com suas respectivas.*|.*indica que a magia.*|'
                         r'e M que necessita.*|Lista de Magias.*|[A-ZÍÉÁÔÃ ]{4,}|.*específico\.?|'
                         r'Ritual e M que.*|Subclasses de.*|Uma subclasse de.*|.*conforme especificado.*|'
                         r'.*Esta seção apre.*|Patrono.*|.*senta as subclasses.*)$')
    circ, saida, nao = None, [], []
    pendente = None   # linha que sozinha não casou: pode ser o começo de um nome quebrado
    for linha in texto.split('\n'):
        linha = linha.strip()
        if not linha: continue
        if pendente:
            # tenta casar 'pendente + linha' antes de tratar a linha isolada
            juncao = f"{pendente} {linha}"
            if PAR.search(juncao):
                linha, pendente = juncao, None
            else:
                nao.append((circ, pendente)); pendente = None
        cab = CAB.search(linha)
        if cab:
            # O cabeçalho pode vir COLADO NO FIM de uma linha de magia, por causa da coluna.
            # Nesse caso a magia ainda pertence ao círculo ANTERIOR — processá-la antes de virar.
            antes = linha[:cab.start()].strip()
            depois = linha[cab.end():].strip()
            novo_circ = 0 if 'Truques' in cab.group(0) else int(cab.group(1))
            if antes:
                ach, _r = varrer_linha(re.sub(r'Magia\s+Escola\s+Especial\s*$', '', antes).strip(), circ)
                if ach and circ is not None:
                    for nome, esc, esp in ach:
                        saida.append(_entrada_direta(nome, esc, esp, circ, lista_id, pagina_livro))
                elif not IGNORAR.match(antes):
                    nao.append((circ, antes))
            circ = novo_circ
            linha = depois
            if not linha: continue
        linha = re.sub(r'Magia\s+Escola\s+Especial\s*$', '', linha).strip()
        achados, resto = varrer_linha(linha, circ)
        if achados and circ is not None:
            for nome, esc, esp in achados:
                saida.append(_entrada_direta(nome, esc, esp, circ, lista_id, pagina_livro))
            if resto and not IGNORAR.match(resto):
                pendente = resto
        elif not IGNORAR.match(linha):
            pendente = linha        # segura para tentar juntar com a próxima
    if pendente: nao.append((circ, pendente))
    return saida, nao

if __name__ == '__main__':
    lista_id, ini, fim, pag = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    mi = sys.argv[5] if len(sys.argv) > 5 else None
    mf = sys.argv[6] if len(sys.argv) > 6 else None
    saida, nao = parse(lista_id, ini, fim, pag, mi, mf)
    alias = [x['nome'] for x in saida if x.get('_escola_no_livro')]
    if alias: print("escolas com nome alternativo no livro:", alias)
    c = Counter(x['nivel'] for x in saida)
    print(f"lista '{lista_id}':")
    for k in sorted(c): print(f"  círculo {k}: {c[k]}")
    print("TOTAL:", len(saida))
    ids = [x['id'] for x in saida]
    dup = [i for i in set(ids) if ids.count(i) > 1]
    print("ids duplicados:", dup or "nenhum")
    print("\nnão reconhecidas (revisar):")
    for n, l in nao:
        if l.strip(): print("  ", n, "|", l[:90])
    json.dump(saida, open(caminhos.intermediario(f'lista_{lista_id}.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
