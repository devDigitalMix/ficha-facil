# -*- coding: utf-8 -*-
"""Parser das tabelas do capítulo 6 (Equipamento, p. 213-233).

Lê as tabelas de armas, armaduras, munição, equipamento de aventura, focos de
conjuração, montarias e veículos, e as descrições de ferramentas. Devolve dados
estruturados; nada de texto do livro copiado em bloco.

As tabelas do PDF quebram linha no meio de uma célula e às vezes colam a coluna
seguinte no fim da anterior ('Recarga' + 'Lentidão' virando 'RecargaLentidão').
Cada leitor abaixo trata isso explicitamente.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos
import re, json, unicodedata

TXT = caminhos.exigir('cap6.txt', 'parse_equipamento.py')

MAESTRIAS = ['Afligir', 'Ágil', 'Derrubar', 'Drenar', 'Empurrar', 'Garantido',
             'Lentidão', 'Trespassar']
TIPOS_DANO = {'contundente': 'contundente', 'cortante': 'cortante',
              'perfurante': 'perfurante'}
MOEDAS = {'pc': 1, 'pp': 10, 'pe': 50, 'po': 100, 'pl': 1000}   # em peças de cobre


def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', s).strip()


def ident(nome):
    return re.sub(r'[^a-z0-9]+', '_', norm(nome)).strip('_')


def ler_custo(txt):
    """'1.500 PO' -> {'valor': 1500, 'moeda': 'po', 'em_pc': 150000}."""
    m = re.search(r'([\d.,]+)\s*(PC|PP|PE|PO|PL)\b', txt, re.I)
    if not m:
        return None
    v = float(m.group(1).replace('.', '').replace(',', '.'))
    moeda = m.group(2).lower()
    return {"valor": int(v) if v == int(v) else v, "moeda": moeda,
            "em_pc": int(v * MOEDAS[moeda])}


def ler_peso(txt):
    """'0,5 kg' -> 0.5 ; '150 g' -> 0.15 ; '—' -> None."""
    m = re.search(r'([\d.,]+)\s*(kg|g)\b', txt)
    if not m:
        return None
    v = float(m.group(1).replace('.', '').replace(',', '.'))
    return round(v / 1000, 3) if m.group(2) == 'g' else v


def linhas_da_tabela(txt, inicio, fim):
    """Junta as linhas de uma tabela, colando as continuações de célula."""
    i = txt.find(inicio)
    j = txt.find(fim, i + len(inicio)) if fim else len(txt)
    bruto = txt[i + len(inicio):j]
    # a tabela vira de coluna e o cabeçalho reaparece colado no fim de uma linha:
    # 'Kit de Curandeiro 1,5 kg 5 POItem Peso Custo' — senão essa linha se perde
    bruto = re.sub(r'(?<=[a-zA-Z0-9])' + re.escape(inicio.split('\n')[-1]), '\n', bruto)
    saida = []
    for linha in bruto.split('\n'):
        linha = linha.rstrip()
        if not linha.strip():
            continue
        # linha de continuação: começa em minúscula ou o anterior terminou em vírgula
        if saida and (re.match(r'^[a-zà-ÿ(]', linha.strip()) or
                      saida[-1].rstrip().endswith(',')):
            saida[-1] = saida[-1].rstrip() + ' ' + linha.strip()
        else:
            saida.append(linha)
    return [l.strip() for l in saida if l.strip()]


# ------------------------------------------------------------------- armas
def ler_armas(txt):
    GRUPOS = {
        'Armas Simples Corpo a Corpo': ('simples', 'corpo_a_corpo'),
        'Armas Simples à Distância':   ('simples', 'a_distancia'),
        'Armas Marciais Corpo a Corpo': ('marcial', 'corpo_a_corpo'),
        'Armas Marciais à Distância':  ('marcial', 'a_distancia'),
    }
    linhas = linhas_da_tabela(txt, 'Nome Dano Propriedades Maestria Peso Custo', '\nArmas\n')
    grupo = alcance = None
    armas = []
    for linha in linhas:
        if linha in GRUPOS:
            grupo, alcance = GRUPOS[linha]
            continue
        if grupo is None:
            continue
        # nome + dano vêm primeiro: 'Adaga 1d4 Perfurante ...'
        m = re.match(r'^(.+?)\s+(\d+d\d+|1)\s+(Contundente|Cortante|Perfurante),?\s+(.*)$', linha)
        if not m:
            continue
        nome, dado, tipo, resto = m.group(1), m.group(2), m.group(3), m.group(4)
        # a maestria é uma das oito palavras conhecidas, e vem colada na coluna
        # anterior quando a célula de propriedades quebrou linha ('RecargaLentidão')
        maestria = None
        for cand in MAESTRIAS:
            k = resto.find(cand)
            if k >= 0 and (k + len(cand) >= len(resto) or not resto[k + len(cand)].isalpha()):
                maestria = cand
                propriedades = resto[:k].strip(' ,')
                cauda = resto[k + len(cand):]
                break
        else:
            propriedades, cauda = resto, ''
        armas.append({
            "nome": nome.strip(),
            "categoria": "arma",
            "grupo": grupo,
            "alcance": alcance,
            "dano": {"formula_dado": dado if 'd' in dado else None,
                     "valor_fixo": None if 'd' in dado else int(dado),
                     "tipo_dano": TIPOS_DANO[norm(tipo)]},
            "propriedades_texto": propriedades,
            "maestria": ident(maestria) if maestria else None,
            "peso_kg": ler_peso(cauda),
            "custo": ler_custo(cauda),
        })
    return armas


PROPRIEDADES = {
    'acuidade': 'acuidade', 'duas maos': 'duas_maos', 'extensao': 'extensao',
    'leve': 'leve', 'pesada': 'pesada', 'recarga': 'recarga',
    'arremesso': 'arremesso', 'municao': 'municao', 'versatil': 'versatil',
}


def decompor_propriedades(texto):
    """'Arremesso (Alcance 6/18), Leve' -> lista estruturada."""
    if not texto or texto.strip() in ('—', '-'):
        return []
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
    saida = []
    for p in partes:
        p = p.strip()
        if not p:
            continue
        base = norm(re.sub(r'\(.*', '', p))
        base = re.sub(r'\s*\(a menos que montado\)', '', base).strip()
        chave = PROPRIEDADES.get(base)
        item = {"propriedade": chave or base, "texto": p}
        if chave is None:
            item["revisao"] = "duvida"
        a = re.search(r'Alcance\s+([\d,.]+)/([\d,.]+)', p)
        if a:
            item["alcance_normal_m"] = float(a.group(1).replace(',', '.'))
            item["alcance_longo_m"] = float(a.group(2).replace(',', '.'))
        v = re.search(r'\((\d+d\d+)\)', p)
        if v and chave == 'versatil':
            item["dado_versatil"] = v.group(1)
        mun = re.search(r';\s*([A-ZÁÉÍÓÚ][\w]*)', p)
        if mun and chave == 'municao':
            item["municao"] = ident(mun.group(1))
        if 'menos que montado' in norm(p):
            item["condicional"] = "duas_maos_exceto_montado"
        saida.append(item)
    return saida


# --------------------------------------------------------------- armaduras
def ler_armaduras(txt):
    CATS = {
        'Armadura Leve (1 Minuto para Vestir ou Despir)': ('leve', 1, 1),
        'Armadura Média (5 Minutos para Vestir e 1 Minuto para Despir)': ('media', 5, 1),
        'Armadura Pesada (10 Minutos para Vestir e 5 Minutos para Despir)': ('pesada', 10, 5),
        'Escudo (Ação Usar Objeto para Equipar ou Desequipar)': ('escudo', None, None),
    }
    linhas = linhas_da_tabela(
        txt, 'Armadura Classe de Armadura (CA) Força Furtividade Peso Custo',
        'Variante: Tamanhos de Equipamento')
    cat = vestir = despir = None
    saida = []
    for linha in linhas:
        if linha in CATS:
            cat, vestir, despir = CATS[linha]
            continue
        if cat is None:
            continue
        m = re.match(r'^(.+?)\s+(\d+)(\s*\+\s*[Mm]odificador de Des(?:\s*\(máx\.\s*(\d+)\))?)?\s+'
                     r'(—|For\s+\d+)\s+(—|Desvantagem)\s+(.*)$', linha)
        if not m:
            continue
        nome, base, soma, teto, forca, furt, cauda = m.groups()
        ca = {"base": int(base), "soma_modificador_destreza": bool(soma)}
        if teto:
            ca["teto_do_modificador"] = int(teto)
        f = re.match(r'For\s+(\d+)', forca)
        item = {
            "nome": nome.strip(), "categoria": "armadura", "grupo": cat,
            "ca": ca,
            "forca_minima": int(f.group(1)) if f else None,
            "desvantagem_em_furtividade": furt == 'Desvantagem',
            "peso_kg": ler_peso(cauda), "custo": ler_custo(cauda),
        }
        if vestir:
            item["minutos_para_vestir"] = vestir
            item["minutos_para_despir"] = despir
        if cat == 'escudo':
            item["ca"] = {"bonus": int(base)}
        saida.append(item)
    return saida


# ----------------------------------------------- tabelas simples (item/peso/custo)
def ler_tabela_simples(txt, cabecalho, fim, categoria, extra=None):
    linhas = linhas_da_tabela(txt, cabecalho, fim)
    saida = []
    for linha in linhas:
        c = ler_custo(linha)
        if not c:
            continue
        nome = re.split(r'\s+[\d.,]+\s*(?:kg|g)\b|\s+[\d.,]+\s*(?:PC|PP|PE|PO|PL)\b',
                        linha)[0].strip()
        nome = re.sub(r'\s*\(.*?\)\s*$', '', nome).strip()
        nome = re.sub(r'\s*—\s*$', '', nome).strip()   # coluna Peso vazia colada no nome
        if not nome or len(nome) > 60:
            continue
        it = {"nome": nome, "categoria": categoria,
              "peso_kg": ler_peso(linha), "custo": c}
        if extra:
            it.update(extra)
        saida.append(it)
    return saida


if __name__ == '__main__':
    t = open(TXT, encoding='utf-8').read()
    armas = ler_armas(t)
    armaduras = ler_armaduras(t)
    print(f"armas: {len(armas)}")
    for a in armas[:3] + armas[-2:]:
        print('  ', a['nome'], a['dano'], a['maestria'], a['peso_kg'], a['custo'],
              '|', a['propriedades_texto'])
    print(f"armaduras: {len(armaduras)}")
    for a in armaduras:
        print('  ', a['nome'], a['grupo'], a['ca'], a['forca_minima'],
              a['desvantagem_em_furtividade'], a['peso_kg'], a['custo'])


# ---------------------------------------------------- demais tabelas do capítulo
def ler_municao(txt):
    linhas = linhas_da_tabela(txt, 'Tipo Quant. Armz. Peso Custo', 'Óleo (1 PP)')
    saida = []
    for l in linhas:
        m = re.match(r'^(.+?)\s+(\d+)\s+(\w+)\s+([\d.,]+\s*(?:kg|g))\s+(.*)$', l)
        if not m:
            continue
        saida.append({"nome": m.group(1).strip(), "categoria": "municao",
                      "quantidade_por_compra": int(m.group(2)),
                      "armazenada_em": ident(m.group(3)),
                      "peso_kg": ler_peso(m.group(4)), "custo": ler_custo(m.group(5))})
    return saida


def ler_montarias(txt):
    linhas = linhas_da_tabela(txt, 'Item Capc. de Carga Custo',
                              'Arreios, Apetrechos e Veículos de Tração')
    saida = []
    for l in linhas:
        m = re.match(r'^(.+?)\s+([\d.,]+)\s*kg\s+(.*)$', l)
        if not m:
            continue
        saida.append({"nome": m.group(1).strip(), "categoria": "montaria",
                      "capacidade_de_carga_kg": float(m.group(2).replace(',', '.')),
                      "custo": ler_custo(m.group(3))})
    return saida


def ler_veiculos(txt):
    cab = ('Embarcação Deslocamento Tripulação Passageiros Carga (Ton) CA PV '
           'Limiar de Dano Custo')
    linhas = linhas_da_tabela(txt, cab, 'KATERINA LADON')
    saida = []
    for l in linhas:
        m = re.match(r'^(.+?)\s+([\d.,]+)\s*km/h\s+(\d+)\s+(\d+|—)\s+([\d.,]+|—)\s+'
                     r'(\d+)\s+(\d+)\s+(\d+|—)\s+(.*)$', l)
        if not m:
            continue
        def num(v):
            return None if v == '—' else float(v.replace(',', '.'))
        saida.append({"nome": m.group(1).strip(), "categoria": "veiculo",
                      "deslocamento_kmh": num(m.group(2)),
                      "tripulacao": int(m.group(3)), "passageiros": num(m.group(4)),
                      "carga_toneladas": num(m.group(5)),
                      "ca": int(m.group(6)), "pontos_de_vida": int(m.group(7)),
                      "limiar_de_dano": num(m.group(8)),
                      "custo": ler_custo(m.group(9))})
    return saida


def ler_focos(txt):
    """Focos Arcanos, Druídicos e Símbolos Sagrados."""
    blocos = [('Foco Peso Custo', 'Foco Druídico (Varia)', 'arcano'),
              ('Focos Druídicos\nFoco Peso Custo', 'Fogo Alquímico', 'druidico'),
              ('Símbolo Peso Custo', 'Sino (1 PO)', 'sagrado')]
    saida = []
    for cab, fim, tipo in blocos:
        for l in linhas_da_tabela(txt, cab, fim):
            c = ler_custo(l)
            if not c:
                continue
            nome = re.split(r'\s+(?:[\d.,]+\s*(?:kg|g)|—)\s', l)[0].strip()
            nome = re.sub(r'\s*\(.*?\)\s*$', '', nome).strip()
            if not nome or nome.startswith('Foco') or nome.startswith('Símbolo'):
                continue
            saida.append({"nome": nome, "categoria": "foco_de_conjuracao",
                          "tipo_de_foco": tipo, "peso_kg": ler_peso(l), "custo": c})
    return saida


def ler_equipamento(txt):
    return ler_tabela_simples(txt, 'Item Peso Custo', 'Ácido (25 PO)',
                              'equipamento_de_aventura')


SUBITENS_DE_SELA = {'Exótica', 'Militar', 'Viagem'}


def ler_arreios(txt):
    itens = ler_tabela_simples(txt, 'Arreios, Apetrechos e Veículos de Tração\nItem Peso Custo',
                               'WAYNE ENGLAND', 'arreio_ou_veiculo_de_tracao')
    for i in itens:
        # a tabela imprime 'Sela' como subtítulo e as três variantes abaixo
        if i['nome'] in SUBITENS_DE_SELA:
            i['nome'] = f"Sela {i['nome']}"
    return [i for i in itens if i['nome'] != 'Sela']


# ------------------------------------------------------------ ferramentas
ATRIBUTOS_CURTOS = {'forca': 'FOR', 'destreza': 'DES', 'constituicao': 'CON',
                    'inteligencia': 'INT', 'sabedoria': 'SAB', 'carisma': 'CAR'}

# cabeçalho de ferramenta: 'Nome (custo)' seguido da linha 'Atributo: X Peso: Y'
RE_CAB_FERRAMENTA = re.compile(
    r'^([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^\n(]{3,55}?)\s*\(([^)]*)\)\s*\n'
    r'Atributo:\s*(\w+)\s+Peso:\s*([\d.,]+\s*kg|Varia|—)\s*$', re.M)


def ler_ferramentas(txt):
    """Corta o bloco nos cabeçalhos e lê os campos de cada entrada.

    Uma regex única para a entrada inteira falhava sempre que 'Usar Objeto' ou
    'Fabricação' quebravam de um jeito diferente; separar as duas etapas resolve.
    """
    i = txt.find('Ferramentas de Artesão')
    j = txt.find('Equipamento de Aventura')
    bloco = txt[i:j]
    # créditos de artista em CAIXA ALTA vazam para dentro da lista de Fabricação
    # ('Kit de Escalada WAYNE ENGLAND')
    bloco = re.sub(r'\b(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}\s+){1,3}[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}\b', ' ', bloco)
    # o cabeçalho da ferramenta seguinte vem colado no fim da linha anterior
    # ('…, VirotesFerramentas de Ferreiro (20 PO)'). Sem separar, ela some.
    bloco = re.sub(
        r'(?<=[a-zà-ÿ0-9\)])((?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*)(?:\s+(?:de|do|da|dos|das|[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*))*'
        r'\s*\([^)\n]*\)\s*\nAtributo:)', r'\n\1', bloco)
    cabs = list(RE_CAB_FERRAMENTA.finditer(bloco))
    saida = []
    for n, m in enumerate(cabs):
        nome, custo_txt, atrib, peso = m.groups()
        nome = nome.strip()
        if norm(nome).startswith(('ferramentas de artesao', 'outras ferramentas')):
            continue
        corpo = bloco[m.end():cabs[n + 1].start() if n + 1 < len(cabs) else len(bloco)]
        item = {
            "nome": nome,
            "atributo": ATRIBUTOS_CURTOS.get(norm(atrib), atrib),
            "peso_kg": ler_peso(peso),
            "custo": ler_custo(custo_txt),
        }
        if norm(custo_txt) == 'varia':
            item["custo_varia"] = True
        if norm(peso) == 'varia':
            item["peso_varia"] = True
        u = re.search(r'Usar Objeto:\s*(.*?)(?=\n(?:Fabricação|Variantes|[A-ZÁÉÍÓÚ][^\n]*\n?Atributo:)|\Z)',
                      corpo, re.S)
        if u:
            usar = desdobrar_ferramenta(u.group(1))
            c = re.search(r'CD\s*(\d+)', usar)
            item["usar_objeto"] = {"acao": re.sub(r'\s*\(CD\s*\d+\)\s*$', '', usar).strip()}
            if c:
                item["usar_objeto"]["cd"] = int(c.group(1))
        f = re.search(r'Fabricação:\s*(.*?)'
                      r'(?=\n(?:Variantes|Outras Ferramentas|[A-ZÁÉÍÓÚ][^\n]*\n?Atributo:)'
                      r'|Outras Ferramentas|\Z)', corpo, re.S)
        if f:
            item["fabricacao_texto"] = desdobrar_ferramenta(f.group(1))
        saida.append(item)
    return saida


def desdobrar_ferramenta(s):
    s = re.sub(r'(\w)\s*-\s*\n\s*(\w)', r'\1\2', s)
    s = re.sub(r'\s*\n\s*', ' ', s)
    return re.sub(r'\s{2,}', ' ', s).strip()
