# -*- coding: utf-8 -*-
"""Parser das descrições de magia do capítulo 7 (p. 239-343).

Extrai o que é FATO da entrada: círculo, escola, listas, tempo de conjuração,
alcance, componentes, duração, e os padrões mecânicos que dá para reconhecer com
segurança (dado de dano + tipo, salvaguarda, área, aprimoramento de truque e uso
de espaço superior).

NÃO copia o texto do livro. A `descricao_curta` de cada magia é escrita à mão,
em paráfrase curta, como manda a regra do projeto. O parser só devolve o texto
bruto para eu ler e resumir.

Uso:
    python3 parse_magias.py            # relatório do que o parser enxerga
    python3 parse_magias.py --json X   # despeja as N primeiras em JSON
"""
import re, json, sys, unicodedata

TXT = '/tmp/claude-0/cap7.txt'
PAGINAS = '/tmp/claude-0/cap7_paginas.json'
CATALOGO = 'dados/catalogos/magias.json'

# o livro usa 'º' quase sempre e '°' em Animar Mortos (p. 244) — aceitamos os dois
CABECALHO = re.compile(
    r'^(?:(Truque) de|([1-9])\s*[º°]\s*Círculo,)\s*'
    r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)\s*\(([^)]*)\)\s*$', re.M)

# 'Componente:' no singular aparece em Tempestade Radiante de Jallarzi (p. 342)
CAMPOS = {
    'tempo_de_conjuracao': re.compile(r'^Tempo de Conjuração:\s*(.+)$', re.M),
    'alcance':             re.compile(r'^Alcance:\s*(.+)$', re.M),
    'componentes':         re.compile(r'^Componentes?:\s*(.+)$', re.M),
    'duracao':             re.compile(r'^Duração:\s*(.+)$', re.M),
}

APRIMORAMENTO = re.compile(
    r'(Aprimoramento de Truque|Usando um Espaço de Magia de Círculo Superior)\.?\s*(.*?)$',
    re.S)


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', s).strip()


# créditos de arte impressos no meio da coluna: nomes em CAIXA ALTA e legendas
RE_CREDITO = re.compile(r'\b(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}\s+){1,3}[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}\b')

# valores possíveis do campo Duração — o que vier depois é corpo colado
UNID = r'(?:rodadas?|minutos?|horas?|dias?|anos?)'
RE_DURACAO_VALOR = re.compile(
    r'^(Concentração,\s*até\s+\d+\s+' + UNID +
    r'|Instantânea|Especial|Até ser dissipada(?:\s+ou desencadeada)?'
    r'|\d+\s+' + UNID + r'(?:\s+ou\s+até\s+ser\s+dissipada)?)')


def limpar_creditos(s):
    """Remove nomes de artista em caixa alta impressos dentro do texto."""
    return re.sub(r'\s{2,}', ' ', RE_CREDITO.sub(' ', s)).strip()


def desdobrar(s):
    """Junta palavras quebradas por hífen de fim de linha e normaliza espaços."""
    s = re.sub(r'(\w)\s*-\s*\n\s*(\w)', r'\1\2', s)
    s = re.sub(r'\s*\n\s*', ' ', s)
    return re.sub(r'\s{2,}', ' ', s).strip()


# ------------------------------------------------------------------ cabeçalho
def ler_nomes(txt, conhecidos):
    """Nome de cada magia: a linha anterior ao cabeçalho. Quando a quebra de
    coluna cola o nome no fim do parágrafo anterior, o nome conhecido mais longo
    que termina a linha vence; para magia nova, cai na cauda em Title Case."""
    PALAVRA = r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ'’/-]*"
    LIGA = r"(?:de|do|da|dos|das|e|em|no|na|o|a|à|aos|ou|para|sobre|com|contra|via|às)"
    CAUDA = re.compile(rf"(?:{PALAVRA})(?:[:\s]+(?:{PALAVRA}|{LIGA}))*$")
    saida = []
    for m in CABECALHO.finditer(txt):
        fim = txt.rfind('\n', 0, m.start())
        ini = txt.rfind('\n', 0, fim)
        linha = txt[ini + 1:fim].strip()
        ln = norm(linha)
        c = CAUDA.search(linha)
        cauda = c.group(0).strip() if c else linha
        if cauda == linha:
            # a linha inteira é o nome — inclusive quando é uma magia nova cujo
            # nome TERMINA com o nome de outra ('Flecha Relâmpago' × 'Relâmpago').
            nome = linha
        else:
            # nome colado no fim do parágrafo anterior por quebra de coluna:
            # vale o nome conhecido mais longo que fecha a linha.
            cands = [k for k in conhecidos if ln.endswith(k)]
            nome = conhecidos[max(cands, key=len)] if cands else cauda
        saida.append((nome, m))
    return saida


# ------------------------------------------------------------- campos do topo
def ler_tempo(t):
    d = {"texto": t}
    tl = norm(t)
    d["ritual"] = 'ritual' in tl
    if tl.startswith('acao bonus'):
        d["tipo"] = "acao_bonus"
    elif tl.startswith('reacao'):
        d["tipo"] = "reacao"
        g = re.search(r'que você realiza (.+)$', t, re.I) or re.search(r',\s*(?:a )?qual(?:quer)?\s*(.+)$', t, re.I)
        if g:
            d["gatilho"] = g.group(1).strip(' .')
    elif tl.startswith('acao'):
        d["tipo"] = "acao"
    else:
        d["tipo"] = "tempo"
        n = re.match(r'(\d+)\s*(minuto|hora)', tl)
        if n:
            d["minutos"] = int(n.group(1)) * (60 if n.group(2) == 'hora' else 1)
    return d


def ler_alcance(t):
    d = {"texto": t}
    tl = norm(t)
    if tl.startswith('pessoal'):
        d["tipo"] = "pessoal"
    elif tl.startswith('toque'):
        d["tipo"] = "toque"
    elif 'ilimitad' in tl:
        d["tipo"] = "ilimitado"
    elif 'vista' in tl or 'visao' in tl:
        d["tipo"] = "a_vista"
    elif tl.startswith('especial'):
        # 'Alcance: Especial' — o alcance está no corpo da magia (Sonho, p. 331)
        d["tipo"] = "especial"
    else:
        d["tipo"] = "distancia"
    n = re.search(r'([\d.,]+)\s*(metros?|quil[oô]metros?|km|m)\b', t, re.I)
    if n:
        v = float(n.group(1).replace('.', '').replace(',', '.')) if ',' in n.group(1) \
            else float(n.group(1))
        u = norm(n.group(2))
        d["metros"] = v * 1000 if (u.startswith('quil') or u == 'km') else v
    # 'Pessoal (Esfera de 4,5 metros de raio)' e afins
    a = re.search(r'\(([^)]*(?:Esfera|Cubo|Cone|Cilindro|Linha|Emanação)[^)]*)\)', t)
    if a:
        d["area_no_alcance"] = a.group(1)
    return d


def ler_componentes(t):
    d = {"texto": t, "verbal": False, "somatico": False, "material": False}
    cabeca = t.split('(')[0]
    d["verbal"] = bool(re.search(r'\bV\b', cabeca))
    d["somatico"] = bool(re.search(r'\bS\b', cabeca))
    d["material"] = bool(re.search(r'\bM\b', cabeca))
    m = re.search(r'M\s*\((.*)\)\s*$', t, re.S)
    if m:
        mat = desdobrar(m.group(1))
        d["material_descricao"] = mat
        # 'no valor de 1.000 ou mais PO' — o número não encosta no 'PO'
        c = re.search(r'([\d.]+)\s*(ou mais\s*)?PO\b', mat)
        if c:
            d["material_custo_po"] = int(c.group(1).replace('.', ''))
            d["material_custo_minimo"] = bool(c.group(2))
        d["material_consumido"] = bool(re.search(r'consum', norm(mat)))
    return d


def ler_duracao(t):
    d = {"texto": t}
    tl = norm(t)
    d["concentracao"] = tl.startswith('concentracao')
    if 'instantanea' in tl:
        d["tipo"] = "instantanea"
    elif 'dissipada' in tl or 'ate ser dissipada' in tl:
        d["tipo"] = "ate_dissipada"
    elif 'especial' in tl:
        d["tipo"] = "especial"
    else:
        d["tipo"] = "tempo"
    n = re.search(r'(\d+)\s*(rodada|minuto|hora|dia)', tl)
    if n:
        f = {"rodada": 1 / 10, "minuto": 1, "hora": 60, "dia": 1440}[n.group(2)]
        d["minutos"] = round(int(n.group(1)) * f, 2)
    return d


# ----------------------------------------------------- padrões dentro do corpo
DANOS = {'ácido': 'acido', 'contundente': 'contundente', 'cortante': 'cortante',
         'elétrico': 'eletrico', 'energético': 'energetico', 'gélido': 'gelido',
         'ígneo': 'igneo', 'necrótico': 'necrotico', 'perfurante': 'perfurante',
         'psíquico': 'psiquico', 'radiante': 'radiante', 'trovejante': 'trovejante',
         'venenoso': 'venenoso'}
# O livro escreve as duas formas: "14d6 de dano Necrótico" e "5d10 pontos de dano
# Energético". Sem aceitar o "de dano" seco, Moléstia (p. 311) ficava sem dano nenhum.
RE_DANO = re.compile(r'(\d+d\d+)((?:\s*\+\s*\d+)?)\s+(?:(?:pontos? )?de\s+)?dano\s+(' +
                     '|'.join(DANOS) + r')', re.I)
RE_CURA = re.compile(r'(?:(\d+d\d+)[^.;]{0,40}?Pontos? de Vida'
                     r'|Pontos? de Vida[^.;]{0,40}?(\d+d\d+))', re.I)
RE_SALV = re.compile(r'salvaguarda de (Força|Destreza|Constituição|Inteligência|'
                     r'Sabedoria|Carisma)', re.I)
ATRIB = {'forca': 'FOR', 'destreza': 'DES', 'constituicao': 'CON',
         'inteligencia': 'INT', 'sabedoria': 'SAB', 'carisma': 'CAR'}
RE_AREA = re.compile(r'(Esfera|Cubo|Cone|Cilindro|Linha|Emanação)\s+de\s+'
                     r'([\d,.]+)\s*metros?(?:\s+de\s+(raio|lados?|comprimento|altura))?', re.I)
RE_ATAQUE = re.compile(r'ataque m[áa]gico\s+(corpo a corpo|[àa] dist[âa]ncia)', re.I)
RE_COND = re.compile(r'condiç(?:ão|ões)\s+((?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)'
                     r'(?:(?:,|\s+e|\s+ou)\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)*)')
CONDICOES = {'amedrontado', 'atordoado', 'caido', 'cego', 'contido', 'enfeiticado',
             'envenenado', 'exaustao', 'imobilizado', 'incapacitado', 'inconsciente',
             'invisivel', 'paralisado', 'petrificado', 'surdo'}


def ler_mecanica(corpo):
    """Só o que dá para afirmar sem interpretar. O que for ambíguo fica de fora."""
    d = {}
    mapa = {norm(k): v for k, v in DANOS.items()}
    danos = []
    for f, b, t in RE_DANO.findall(corpo):
        item = {"formula_dado": f, "tipo_dano": mapa[norm(t)]}
        if b.strip():
            item["bonus_fixo"] = int(b.replace('+', '').strip())
        danos.append(item)
    if danos:
        d["dano"] = danos[0]
        if len(danos) > 1:
            d["dano_adicional_citado"] = danos[1:]
    s = RE_SALV.search(corpo)
    if s:
        d["salvaguarda"] = {"atributo": ATRIB[norm(s.group(1))]}
        if re.search(r'metade do dano', corpo, re.I):
            d["salvaguarda"]["em_sucesso"] = "metade_do_dano"
    a = RE_AREA.search(corpo)
    if a:
        d["area"] = {"forma": norm(a.group(1)).replace('emanacao', 'emanacao'),
                     "metros": float(a.group(2).replace(',', '.')),
                     "medida": {"lado": "lados"}.get((a.group(3) or "").lower(),
                                (a.group(3) or "").lower()) or None}
    at = RE_ATAQUE.search(corpo)
    if at:
        d["ataque"] = "corpo_a_corpo" if 'corpo' in norm(at.group(1)) else "a_distancia"
    c = RE_CURA.search(corpo)
    if c and not danos and re.search(r'recupera|restaur|cura', corpo, re.I):
        d["cura"] = {"formula_dado": c.group(1) or c.group(2)}
    brutas = set()
    for g in RE_COND.findall(corpo):
        for parte in re.split(r',|\se\s|\sou\s', g):
            brutas.add(norm(parte))
    conds = sorted(brutas & CONDICOES)
    if conds:
        d["condicoes_citadas"] = conds
    return d


# --------------------------------------------------------------------- montar
def pagina_de(offsets, pos):
    """Página do livro em que o caractere `pos` do capítulo caiu."""
    pagina = offsets[0][1]
    for ini, pag in offsets:
        if ini <= pos:
            pagina = pag
        else:
            break
    return pagina


def parse():
    txt = open(TXT, encoding='utf-8').read()
    offsets = json.load(open(PAGINAS, encoding='utf-8'))
    cat = json.load(open(CATALOGO, encoding='utf-8'))
    conhecidos = {}
    for m in cat['itens']:
        conhecidos[norm(m['nome'])] = m['nome']
        for a in m.get('nomes_alternativos', []):
            conhecidos[norm(a)] = m['nome']
    entradas = ler_nomes(txt, conhecidos)
    saida = []
    for n, (nome, m) in enumerate(entradas):
        ini = m.end()
        fim_bruto = entradas[n + 1][1].start() if n + 1 < len(entradas) else len(txt)
        # O nome da próxima magia mora na LINHA ANTERIOR ao próximo cabeçalho. Cortar
        # essa linha inteira funciona quando ela só tem o nome — mas quando a última
        # frase desta magia está COLADA no nome da próxima ("…abaixo de 1.Montaria
        # Fantasmagórica"), o corte engolia o fim do corpo. Era assim em 55 das 391
        # magias, e custou mecânica: Graxa perdia a condição Caído e Moléstia perdia
        # os 14d6. Agora o corte é EXATAMENTE onde o nome da próxima começa.
        if n + 1 < len(entradas):
            prox_nome = entradas[n + 1][0]
            fim_linha_nome = txt.rfind('\n', 0, fim_bruto)
            ini_linha_nome = txt.rfind('\n', 0, fim_linha_nome) + 1
            linha_nome = txt[ini_linha_nome:fim_linha_nome]
            pos = linha_nome.rfind(prox_nome)
            fim = (ini_linha_nome + pos) if pos > 0 else (ini_linha_nome - 1)
        else:
            fim = txt.rfind('\n', 0, txt.rfind('\n', 0, fim_bruto))
        bloco = txt[ini:fim]
        e = {"nome": nome,
             "pagina_livro": pagina_de(offsets, m.start()),
             "circulo": 0 if m.group(1) else int(m.group(2)),
             "escola": m.group(3),
             "listas": [x.strip() for x in desdobrar(m.group(4)).split(',') if x.strip()]}
        pos_corpo = ini
        for campo, rx in CAMPOS.items():
            g = rx.search(bloco)
            if g:
                valor, fimc = g.group(1), g.end()
                # o texto do componente Material atravessa a quebra de linha: só
                # termina quando o parêntese fecha. Sem isso, Bola de Fogo entrava
                # com 'M (uma bola de guano de morcego e'.
                while valor.count('(') > valor.count(')') and fimc < len(bloco):
                    q = bloco.find('\n', fimc + 1)
                    if q < 0:
                        q = len(bloco)
                    valor += ' ' + bloco[fimc:q]
                    fimc = q
                valor = desdobrar(valor)
                if campo == 'duracao':
                    dv = RE_DURACAO_VALOR.match(valor)
                    if dv and len(dv.group(0)) < len(valor):
                        # 'InstantâneaVocê recebe um presságio…' (Augúrio, p. 247)
                        fimc -= (len(valor) - len(dv.group(0)))
                        valor = dv.group(0)
                e[campo] = valor
                pos_corpo = max(pos_corpo, ini + fimc)
            else:
                e.setdefault('_faltando', []).append(campo)
        corpo = limpar_creditos(desdobrar(txt[pos_corpo:fim]))
        e["_corpo"] = corpo
        e["tempo_de_conjuracao"] = ler_tempo(e["tempo_de_conjuracao"]) if "tempo_de_conjuracao" in e else None
        e["alcance"] = ler_alcance(e["alcance"]) if "alcance" in e else None
        e["componentes"] = ler_componentes(e["componentes"]) if "componentes" in e else None
        e["duracao"] = ler_duracao(e["duracao"]) if "duracao" in e else None
        ap = APRIMORAMENTO.search(corpo)
        if ap:
            e["aprimoramento"] = {
                "tipo": "truque" if 'Truque' in ap.group(1) else "espaco_superior",
                "texto": desdobrar(ap.group(2))[:400]}
            corpo = corpo[:ap.start()]
        e.update(ler_mecanica(corpo))
        saida.append(e)
    return saida


if __name__ == '__main__':
    ms = parse()
    if '--json' in sys.argv:
        k = int(sys.argv[sys.argv.index('--json') + 1])
        print(json.dumps(ms[:k], ensure_ascii=False, indent=1))
    else:
        faltando = [(e['nome'], e['_faltando']) for e in ms if e.get('_faltando')]
        print(f"entradas: {len(ms)}")
        print(f"com dano reconhecido: {sum(1 for e in ms if 'dano' in e)}")
        print(f"com salvaguarda: {sum(1 for e in ms if 'salvaguarda' in e)}")
        print(f"com área: {sum(1 for e in ms if 'area' in e)}")
        print(f"com ataque: {sum(1 for e in ms if 'ataque' in e)}")
        print(f"com aprimoramento: {sum(1 for e in ms if 'aprimoramento' in e)}")
        print(f"campo do topo faltando: {len(faltando)}")
        for n, f in faltando[:20]:
            print('   ', n, f)
