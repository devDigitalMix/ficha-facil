# -*- coding: utf-8 -*-
"""Lê os blocos de estatísticas do Apêndice B (p. 346-359).

O bloco é regular, então vale parser em vez de digitação: 51 criaturas × ~15 campos
é onde erro de digitação se esconde. O que o parser NÃO faz é escrever a prosa dos
traços e ações — isso é paráfrase à mão, em `descricoes_criaturas.py`, pela mesma
regra que vale para as magias: o texto do livro não é copiado.

Uso: python3 geradores/parse_criaturas.py          # resumo
     python3 geradores/parse_criaturas.py --json 2  # os dois primeiros, cru
"""
import json, re, sys, unicodedata

import caminhos

TXT = caminhos.exigir('apb.txt', 'parse_criaturas.py')
PAGINAS = caminhos.exigir('apb_paginas.json', 'parse_criaturas.py')

TIPOS = ('Aberração|Celestial|Constructo|Dragão|Elemental|Feérico|Fera|Gigante|'
         'Gosma|Humanoide|Ínfero|Monstruosidade|Morto-Vivo|Morto-vivo|Planta')
TAMANHOS = ('Minúsculo|Minúscula|Pequeno|Pequena|Médio|Média|Grande|Enorme|'
            'Colossal')

ID_TIPO = {'aberracao': 'aberracao', 'celestial': 'celestial',
           'constructo': 'constructo', 'dragao': 'dragao', 'elemental': 'elemental',
           'feerico': 'feerico', 'fera': 'fera', 'gigante': 'gigante',
           'gosma': 'gosma', 'humanoide': 'humanoide', 'infero': 'infero',
           'monstruosidade': 'monstruosidade', 'morto_vivo': 'morto_vivo',
           'planta': 'planta'}
ID_TAMANHO = {'minusculo': 'minusculo', 'minuscula': 'minusculo',
              'pequeno': 'pequeno', 'pequena': 'pequeno',
              'medio': 'medio', 'media': 'medio', 'grande': 'grande',
              'enorme': 'enorme', 'colossal': 'colossal'}
ID_DESLOCAMENTO = {'deslocamento': 'caminhada', 'escalada': 'escalada',
                   'natacao': 'natacao', 'voo': 'voo', 'escavacao': 'escavacao'}
ID_ATRIBUTO = {'for': 'FOR', 'des': 'DES', 'con': 'CON',
               'int': 'INT', 'sab': 'SAB', 'car': 'CAR'}
ID_DANO = {'acido': 'acido', 'contundente': 'contundente', 'cortante': 'cortante',
           'eletrico': 'eletrico', 'energetico': 'energetico', 'gelido': 'gelido',
           'igneo': 'igneo', 'necrotico': 'necrotico', 'perfurante': 'perfurante',
           'psiquico': 'psiquico', 'radiante': 'radiante',
           'trovejante': 'trovejante', 'venenoso': 'venenoso'}
ID_CONDICAO = {'amedrontado', 'atordoado', 'caido', 'cego', 'contido',
               'enfeiticado', 'envenenado', 'exaustao', 'imobilizado',
               'incapacitado', 'inconsciente', 'invisivel', 'paralisado',
               'petrificado', 'surdo'}
ID_SENTIDO = {'visao_no_escuro': 'visao_no_escuro',
              'visao_as_cegas': 'visao_as_cegas',
              'visao_verdadeira': 'visao_verdadeira',
              'percepcao_passiva': 'percepcao_passiva',
              'telepatia': 'telepatia', 'sismiconsciencia': 'sismiconsciencia'}


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')


def num(s):
    """'1,5' e '12' viram float; o livro usa vírgula decimal."""
    return float(s.replace(',', '.'))


def desdobrar(s):
    """Junta a hifenização de quebra de linha e normaliza espaços."""
    return re.sub(r'\s+', ' ', re.sub(r'-\s*\n\s*', '', s)).strip()


CABECALHO = re.compile(
    r'(?m)^(?P<nome>[^\n]{2,40})\n'
    r'(?P<tipo>' + TIPOS + r')\s+(?P<tamanho>' + TAMANHOS + r')'
    r'(?:\s*\((?P<subtipo>[^)]+)\))?,\s*(?P<alinhamento>[^\n]+)\n'
    r'(?=CA\s)')

RE_CA = re.compile(r'CA\s+(\d+)')
RE_INIC = re.compile(r'Iniciativa\s*([+\-–−]\s*\d+)\s*\((\d+)\)')
RE_PV = re.compile(r'PV\s+(\d+)\s*\(([^)]*)\)')
RE_DESLOC = re.compile(r'(?m)^Deslocamento\s+([^\n]+)')
RE_ATRIB = re.compile(
    r'(?m)^(For|Int)\s+(\d+)\s*([+\-–−]?\s*\d+)\s*([+\-–−]?\s*\d+)\s+'
    r'(Des|Sab)\s+(\d+)\s*([+\-–−]?\s*\d+)\s*([+\-–−]?\s*\d+)\s+'
    r'(Con|Car)\s+(\d+)\s*([+\-–−]?\s*\d+)\s*([+\-–−]?\s*\d+)')
# O valor de um campo pode continuar na linha seguinte — o Zumbi tem
# "Idiomas Compreende os idiomas que conhecia em vida, mas não fala". Pegar só a
# primeira linha cortava a frase no meio. Cada campo vai até o PRÓXIMO rótulo.
ROTULOS = (r'Perícias|Resistências|Imunidades|Vulnerabilidades|Sentidos|Idiomas|'
           r'Equipamento|ND|Traços|Ações Bônus|Ações|Reações')


def _campo(rotulo):
    return re.compile(r'(?m)^' + rotulo + r'\s+(.+?)(?=\n(?:' + ROTULOS + r')\b|\Z)',
                      re.S)


RE_LINHA = {
    'pericias': _campo('Perícias'),
    'resistencias': _campo('Resistências'),
    'imunidades': _campo('Imunidades'),
    'vulnerabilidades': _campo('Vulnerabilidades'),
    'sentidos': _campo('Sentidos'),
    'idiomas': _campo('Idiomas'),
    'engrenagem': _campo('Equipamento'),
}
RE_ND = re.compile(r'(?m)^ND\s+(\S+)\s*\(XP\s*([\d.]+)\s*;\s*BP\s*([+\-–−]\s*\d+)\)')

SECOES = ('Traços', 'Ações', 'Ações Bônus', 'Reações')
RE_SECAO = re.compile(r'(?m)^(' + '|'.join(SECOES) + r')\s*$')
# "Nome da coisa. Texto..." — o nome vem antes do primeiro ponto final
RE_ENTRADA = re.compile(r'(?m)^([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^.\n]{1,48})\.\s+')

RE_ATAQUE = re.compile(
    r'Jogada de Ataque (Corpo a Corpo|à Distância):\s*([+\-–−]\s*\d+)\s*para acertar,\s*'
    r'(?:alcance|distância)\s*([\d,]+)(?:/([\d,]+))?\s*m')
RE_DANO = re.compile(
    r'Dano:\s*(\d+)\s*\((\d+d\d+(?:\s*[+\-]\s*\d+)?)\)\s*(\w+)'
    r'|Dano:\s*(\d+)\s+(\w+)')


def sinal(s):
    return int(s.replace('–', '-').replace('−', '-').replace(' ', ''))


def ler_deslocamentos(txt):
    saida = []
    for parte in txt.split(','):
        parte = parte.strip()
        m = re.match(r'([\d,]+)\s*m', parte)
        if m:                       # o primeiro vem sem rótulo: é caminhada
            saida.append({"tipo": "caminhada", "metros": num(m.group(1))})
            continue
        m = re.match(r'([A-Za-zÁ-ú]+)\s+([\d,]+)\s*m', parte)
        if m:
            t = ID_DESLOCAMENTO.get(norm(m.group(1)))
            if t:
                saida.append({"tipo": t, "metros": num(m.group(2))})
    return saida


def ler_sentidos(txt):
    saida = []
    for parte in txt.split(','):
        parte = parte.strip()
        m = re.match(r'(.+?)\s+([\d,]+)\s*m$', parte)
        if m:
            s = ID_SENTIDO.get(norm(m.group(1)))
            if s:
                saida.append({"sentido": s, "alcance_m": num(m.group(2))})
            continue
        m = re.match(r'Percepção Passiva\s+(\d+)', parte)
        if m:
            saida.append({"sentido": "percepcao_passiva", "valor": int(m.group(1))})
    return saida


def ler_pericias(txt):
    saida = []
    for m in re.finditer(r'([A-Za-zÁ-ú ]+?)\s*([+\-–−]\s*\d+)', txt):
        saida.append({"pericia": norm(m.group(1)), "bonus": sinal(m.group(2))})
    return saida


def ler_dano_e_condicao(txt):
    """A linha 'Imunidades' mistura tipo de dano e condição, separados por ';'."""
    danos, condicoes, nao_reconhecidos = [], [], []
    for bloco in txt.split(';'):
        for parte in bloco.split(','):
            k = norm(parte)
            if k in ID_DANO:
                danos.append(ID_DANO[k])
            elif k in ID_CONDICAO:
                condicoes.append(k)
            elif k:
                nao_reconhecidos.append(parte.strip())
    return danos, condicoes, nao_reconhecidos


RE_CREDITO = re.compile(r'(?m)^[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ \'\-.]{6,}$')
RE_ORNAMENTO = re.compile(r'Estatísticas de Criaturas(?:Estatísticas de Criaturas)*')


def limpar(texto):
    """Tira o crédito do artista, o ornamento de título e o rabo de página.

    O bloco termina onde começa o NOME da próxima criatura, e entre uma coisa e
    outra o PDF larga crédito de artista e número de página. Como toda entrada de
    verdade acaba em ponto final, o corte no último ponto resolve os três de uma vez.
    """
    texto = RE_CREDITO.sub(' ', texto)
    texto = RE_ORNAMENTO.sub(' ', texto)
    texto = desdobrar(texto)
    corte = texto.rfind('.')
    return texto[:corte + 1] if corte > 0 else texto


def ler_entradas(bloco):
    """Quebra uma seção em entradas 'Nome. texto'.

    O nome só vale se a frase anterior TERMINOU. Sem isso, o Zumbi ganhava um traço
    fantasma chamado "Ponto de Vida", recortado do meio da frase "o zumbi tem 1
    Ponto de Vida em vez disso".
    """
    marcas = []
    for m in RE_ENTRADA.finditer(bloco):
        antes = bloco[:m.start()].rstrip()
        if antes and not antes.endswith(('.', '!', '?', ':')):
            continue
        marcas.append(m)
    saida = []
    for n, m in enumerate(marcas):
        fim = marcas[n + 1].start() if n + 1 < len(marcas) else len(bloco)
        nome = desdobrar(m.group(1))
        saida.append({"nome": nome, "id": norm(nome),
                      "_texto": limpar(bloco[m.end():fim])})
    return saida


def ler_ataque(texto):
    m = RE_ATAQUE.search(texto)
    if not m:
        return None
    d = {"tipo_de_ataque": ("corpo_a_corpo" if 'Corpo' in m.group(1) else "a_distancia"),
         "bonus_de_ataque": sinal(m.group(2)),
         "alcance_m": num(m.group(3))}
    if m.group(4):
        d["alcance_maximo_m"] = num(m.group(4))
    danos = []
    for md in RE_DANO.finditer(texto):
        if md.group(1):
            danos.append({"media": int(md.group(1)),
                          "formula_dado": re.sub(r'\s+', ' ', md.group(2)),
                          "tipo_dano": ID_DANO.get(norm(md.group(3)), norm(md.group(3)))})
        else:
            danos.append({"media": int(md.group(4)), "formula_dado": None,
                          "tipo_dano": ID_DANO.get(norm(md.group(5)), norm(md.group(5)))})
    if danos:
        d["dano"] = danos
    return d


def parse():
    txt = open(TXT, encoding='utf-8').read()
    offsets = json.load(open(PAGINAS, encoding='utf-8'))

    def pagina_de(pos):
        p = offsets[0][1]
        for ini, pag in offsets:
            if ini <= pos:
                p = pag
        return p

    marcas = list(CABECALHO.finditer(txt))
    saida = []
    for n, m in enumerate(marcas):
        fim = marcas[n + 1].start() if n + 1 < len(marcas) else len(txt)
        bloco = txt[m.end():fim]
        # o bloco termina onde começa o nome da próxima criatura; corta o rodapé
        bloco = re.sub(r'(?m)^APÊNDICE B[^\n]*\n?', '', bloco)

        e = {"nome": desdobrar(m.group('nome')),
             "id": norm(m.group('nome')),
             "tipo_de_criatura": ID_TIPO[norm(m.group('tipo'))],
             "tamanho": ID_TAMANHO[norm(m.group('tamanho'))],
             "alinhamento": desdobrar(m.group('alinhamento')),
             "pagina_livro": pagina_de(m.start()),
             "_faltando": []}
        if m.group('subtipo'):
            e["subtipo"] = desdobrar(m.group('subtipo'))

        mc = RE_CA.search(bloco)
        e["classe_de_armadura"] = int(mc.group(1)) if mc else e['_faltando'].append('ca')
        mi = RE_INIC.search(bloco)
        if mi:
            e["iniciativa"] = {"bonus": sinal(mi.group(1)), "passiva": int(mi.group(2))}
        else:
            e['_faltando'].append('iniciativa')
        mp = RE_PV.search(bloco)
        if mp:
            e["pontos_de_vida"] = {"media": int(mp.group(1)),
                                   "formula_dado": desdobrar(mp.group(2))}
        else:
            e['_faltando'].append('pv')
        md = RE_DESLOC.search(bloco)
        e["deslocamentos"] = ler_deslocamentos(md.group(1)) if md else []
        if not e["deslocamentos"]:
            e['_faltando'].append('deslocamentos')

        # A tabela de atributos vem em duas linhas de três colunas, cada uma com
        # VALOR, MOD e SG. Guardo os três: o MOD impresso é conferível contra o
        # valor, e o livro erra em duas criaturas (ver gerar_criaturas.py).
        atrib, mods, salv = {}, {}, {}
        for ma in RE_ATRIB.finditer(bloco):
            g = ma.groups()
            for k in (0, 4, 8):
                a = ID_ATRIBUTO[norm(g[k])]
                atrib[a] = int(g[k + 1])
                mods[a] = sinal(g[k + 2])
                salv[a] = sinal(g[k + 3])
        if len(atrib) == 6:
            e["atributos"] = atrib
            e["modificadores_impressos"] = mods
            e["salvaguardas_impressas"] = salv
        else:
            e['_faltando'].append('atributos')

        for campo, rx in RE_LINHA.items():
            mm = rx.search(bloco)
            if not mm:
                continue
            valor = desdobrar(mm.group(1))
            if campo == 'pericias':
                e["pericias"] = ler_pericias(valor)
            elif campo == 'sentidos':
                e["sentidos"] = ler_sentidos(valor)
            elif campo == 'idiomas':
                e["idiomas_texto"] = valor
            elif campo in ('resistencias', 'imunidades', 'vulnerabilidades'):
                danos, conds, resto = ler_dano_e_condicao(valor)
                if danos:
                    e[campo + '_a_dano'] = danos
                if conds:
                    e[campo + '_a_condicao'] = conds
                if resto:
                    e.setdefault('_nao_reconhecido', []).append((campo, resto))
            else:
                e[campo] = valor
        mn = RE_ND.search(bloco)
        if mn:
            e["nivel_de_desafio"] = {
                "texto": mn.group(1),
                "xp": int(mn.group(2).replace('.', '')),
                "bonus_de_proficiencia": sinal(mn.group(3))}
        else:
            e['_faltando'].append('nd')

        # seções: Traços, Ações, Ações Bônus, Reações
        cortes = list(RE_SECAO.finditer(bloco))
        for k, ms in enumerate(cortes):
            f = cortes[k + 1].start() if k + 1 < len(cortes) else len(bloco)
            entradas = ler_entradas(bloco[ms.end():f])
            chave = {'Traços': 'tracos', 'Ações': 'acoes',
                     'Ações Bônus': 'acoes_bonus', 'Reações': 'reacoes'}[ms.group(1)]
            for ent in entradas:
                atk = ler_ataque(ent['_texto'])
                if atk:
                    ent.update(atk)
            e[chave] = entradas
        if not e.get('acoes'):
            e['_faltando'].append('acoes')
        saida.append(e)
    return saida


if __name__ == '__main__':
    cs = parse()
    if '--json' in sys.argv:
        k = int(sys.argv[sys.argv.index('--json') + 1])
        print(json.dumps(cs[:k], ensure_ascii=False, indent=1))
    else:
        print(f"criaturas: {len(cs)}")
        print(f"com traços: {sum(1 for c in cs if c.get('tracos'))}")
        print(f"com ações: {sum(1 for c in cs if c.get('acoes'))}")
        print(f"com ações bônus: {sum(1 for c in cs if c.get('acoes_bonus'))}")
        print(f"com reações: {sum(1 for c in cs if c.get('reacoes'))}")
        print(f"entradas de traço/ação no total: "
              f"{sum(len(c.get(k) or []) for c in cs for k in ('tracos','acoes','acoes_bonus','reacoes'))}")
        ruins = [(c['nome'], c['_faltando']) for c in cs if c['_faltando']]
        print(f"blocos com campo faltando: {len(ruins)}")
        for n, f in ruins:
            print('   ', n, f)
        nr = [(c['nome'], c['_nao_reconhecido']) for c in cs if c.get('_nao_reconhecido')]
        for n, f in nr:
            print('   não reconhecido:', n, f)
