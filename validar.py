# -*- coding: utf-8 -*-
"""Validador do dataset Ficha Fácil.

Regras (esquema v1, §4.3). Sai com código 1 se qualquer regra falhar.
Uso: python3 validar.py [pasta_dados]
"""
import json, os, sys, re

BASE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
erros, avisos = [], []
# ids de escolha declarados e referenciados, para casar depois
ESCOLHAS_DECLARADAS = {}
ESCOLHAS_REFERENCIADAS = set()
OPCOES_CONCEDIDAS = set()


def carregar(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


# ------------------------------------------------------------------ carregar
catalogos, colecoes = {}, {}
cat_dir = os.path.join(BASE, 'catalogos')
for nome in sorted(os.listdir(cat_dir)):
    if nome.endswith('.json'):
        d = carregar(os.path.join(cat_dir, nome))
        catalogos[d['catalogo']] = d
VOCAB = {}
for nome in sorted(os.listdir(BASE)):
    if nome.endswith('.json'):
        d = carregar(os.path.join(BASE, nome))
        # o vocabulário de runtime não é coleção de itens: é a lista fechada do
        # que o motor sabe interpretar (fase 13)
        if d.get('vocabulario_de_runtime'):
            VOCAB = d
            continue
        colecoes[d['colecao']] = d

CHAVES = {cid: {i['id'] for i in c['itens']} for cid, c in catalogos.items()}
for cid, c in colecoes.items():
    CHAVES[cid] = {i['id'] for i in c['itens']}

TIPOS_EFEITO = CHAVES['tipos_de_efeito']
ATRIBUTOS = CHAVES['atributos']
PERICIAS = CHAVES['pericias']
ALVOS = CHAVES['alvos']
ALVOS_IMP = CHAVES['alvos_de_impedimento']

# Tipos de efeito cujo campo 'alvo' aponta para uma jogada/valor da ficha
# (catalogos/alvos.json). Os demais usam 'alvo' noutro sentido: uma característica
# a melhorar (melhorar_caracteristica) ou uma descrição de quem sofre o efeito
# (dano, teleporte), e por isso não são conferidos aqui.
TIPOS_COM_ALVO_DE_JOGADA = {
    'modificador', 'vantagem', 'falha_automatica',
    'alterar_resultado_de_salvaguarda', 'rolar_novamente',
    'tratar_resultado_minimo', 'alterar_faixa_de_critico',
    'substituir_resultado_de_d20',
}
DANOS = CHAVES['tipos_de_dano'] | {'todos'}
# tipos de dano que não são literais: o valor sai da arma, do ataque ou de uma escolha
DANOS_DERIVADOS = {'mesmo_do_ataque', 'mesmo_da_arma', 'mesmo_do_ataque_defletido'}
DESLOCAMENTOS = CHAVES['tipos_de_deslocamento']
SENTIDOS = CHAVES['sentidos']
CONDICOES = CHAVES['condicoes']


# ------------------------------------------------------- 6. ids duplicados
def checar_ids(nome, itens):
    vistos = set()
    for i in itens:
        if i['id'] in vistos:
            erros.append(f"[id duplicado] {nome}: '{i['id']}'")
        vistos.add(i['id'])


for cid, c in list(catalogos.items()) + list(colecoes.items()):
    checar_ids(cid, c['itens'])
    # 2. total declarado bate com a contagem real
    if c.get('total') != len(c['itens']):
        erros.append(f"[total incorreto] {cid}: declarado {c.get('total')}, contados {len(c['itens'])}")


# --------------------------------------------------- 7. fonte.pagina_livro
def tem_fonte(obj):
    fo = obj.get('fonte')
    return isinstance(fo, dict) and isinstance(fo.get('pagina_livro'), int)


for cid, c in list(catalogos.items()) + list(colecoes.items()):
    if not tem_fonte(c) and not all(tem_fonte(i) for i in c['itens']):
        if cid not in ('tipos_de_efeito',):  # catálogo de engine, não sai do livro
            erros.append(f"[sem fonte] {cid}: nem a coleção nem todos os itens têm fonte.pagina_livro")
for cid, c in colecoes.items():
    for i in c['itens']:
        if not tem_fonte(i):
            erros.append(f"[sem fonte] {cid}/{i['id']}: falta fonte.pagina_livro")


# ------------------------------------------------------ alvos e referências
def checar_alvo(ctx, alvo):
    base, _, suf = alvo.partition(':')
    if base not in ALVOS:
        erros.append(f"[alvo inexistente] {ctx}: '{alvo}' (base '{base}' fora de catalogos/alvos.json)")
        return
    if suf and suf not in ATRIBUTOS and suf not in PERICIAS:
        erros.append(f"[sufixo de alvo inválido] {ctx}: '{alvo}' — '{suf}' não é atributo nem perícia")


PLACEHOLDER = '{{escolhido}}'
# de onde um conjurador pode preparar magias: nunca do vazio, nunca da lista inteira sem dizer
FONTES_DE_PREPARACAO = {'livro_de_magias', 'lista_de_classe', 'conhecidas'}


LISTAS_PREENCHIDAS = {i['id'] for i in catalogos.get('listas_de_magia', {}).get('itens', [])
                      if i.get('preenchida')}
LISTAS_DECLARADAS = CHAVES.get('listas_de_magia', set())


# Chaves de filtro que só o motor resolve, em tempo de execução: dependem do
# personagem, não do catálogo. Estão aqui para que o validador saiba a diferença
# entre "não sei avaliar isto" e "isto é erro de digitação". Antes da auditoria de
# 2026-09-02 as duas coisas eram a mesma: chave desconhecida era ignorada em
# silêncio, e um filtro escrito errado nunca era acusado.
FILTROS_DE_RUNTIME = {
    'circulo_com_espaco_disponivel',   # depende dos espaços que o personagem tem
    'proficiente',                     # depende das proficiências do personagem
    'ainda_nao_especialista',
    'com_proficiencia',
    'pre_requisitos_atendidos',        # depende dos atributos e do nível
    'nd_maximo',                       # Forma Selvagem: depende do nível de Druida
    'sem_deslocamento_de_voo',
    'exceto',                          # exclusão declarada na própria escolha
    'alguma',                          # árvore booleana dentro do filtro
    'id',                              # seleção direta por id
    'no_livro',                        # recorte editorial: só o que o livro lista ali
}


def chaves_de_filtro_desconhecidas(cat, filtro):
    """Chaves que nem o catálogo declara nem o motor promete resolver."""
    fonte_cat = catalogos.get(cat, colecoes.get(cat, {}))
    itens = fonte_cat.get('itens', [])
    campos = {k for it in itens for k in it}
    estruturais = {'nivel', 'nivel_minimo', 'nivel_maximo', 'lista', 'escola', 'categoria',
                   'grupo', 'classe', 'alguma_propriedade', 'circulo_maximo',
                   'tipo_de_criatura', 'alcance', 'ritual', 'tempo_de_conjuracao'}
    return sorted(k for k in filtro
                  if k not in campos and k not in estruturais and k not in FILTROS_DE_RUNTIME)


def resolver_filtro(cat, filtro):
    """Conta quantos itens do catálogo sobrevivem ao filtro.

    Devolve (quantidade, motivo). Chaves de filtro que o validador não sabe avaliar
    são ignoradas — melhor não contar do que acusar falso positivo. Referências a
    variáveis ($algo) também são ignoradas: só resolvem em tempo de execução.
    """
    fonte_cat = catalogos.get(cat, colecoes.get(cat, {}))
    itens = fonte_cat.get('itens', [])
    if not itens:
        # catálogo declarado mas ainda sem conteúdo: pendência conhecida, não defeito
        pendente = (fonte_cat['preenchida'] is False if 'preenchida' in fonte_cat
                    else bool(fonte_cat.get('parcial')))
        return (0, 'catalogo_pendente' if pendente else 'ok')
    conhecidas = {'nivel', 'nivel_minimo', 'nivel_maximo', 'lista', 'escola',
                  'categoria', 'grupo', 'classe', 'alguma_propriedade'}
    # Além dessas, qualquer campo simples que os próprios itens declarem pode ser
    # filtrado por igualdade. Sem isto, um filtro como
    # {'escolhivel_no_surto_controlado': True} era ignorado — e um filtro que não
    # devolve nada passava despercebido, que é justamente o defeito silencioso que
    # a regra 5 existe para pegar.
    diretas = {k for it in itens for k, v in it.items()
               if isinstance(v, (bool, int, float, str)) and k not in ('id', 'nome')}
    conhecidas = conhecidas | diretas
    if not any(k in conhecidas for k in filtro):
        return (1, 'nao_avaliavel')
    lista_alvo = filtro.get('lista')
    if isinstance(lista_alvo, str) and lista_alvo.startswith('$'):
        return (1, 'variavel')
    # 'lista' pode ser uma lista de listas (Segredos Mágicos do Bardo abre quatro)
    listas_alvo = ([lista_alvo] if isinstance(lista_alvo, str)
                   else list(lista_alvo or []))
    declaradas = [l for l in listas_alvo if l in LISTAS_DECLARADAS]
    if declaradas and not any(l in LISTAS_PREENCHIDAS for l in declaradas):
        return (0, 'lista_nao_preenchida')
    n = 0
    for it in itens:
        ok = True
        for k, v in filtro.items():
            if k not in conhecidas or (isinstance(v, str) and v.startswith('$')):
                continue
            if k in diretas and k not in (
                    'nivel', 'escola', 'categoria', 'classe', 'grupo'):
                if it.get(k) != v: ok = False
            elif k == 'nivel' and it.get('nivel') != v: ok = False
            elif k == 'nivel_minimo' and (it.get('nivel') is None or it['nivel'] < v): ok = False
            elif k == 'nivel_maximo' and (it.get('nivel') is None or it['nivel'] > v): ok = False
            elif k == 'lista':
                minhas = set(it.get('listas') or [])
                alvo_l = {v} if isinstance(v, str) else set(v)
                if not (minhas & alvo_l): ok = False
            elif k in ('escola', 'categoria', 'classe'):
                # o filtro pode trazer um valor ou uma lista de valores aceitos
                # (Tocado pelas Sombras: escola Ilusão OU Necromancia)
                atual = it.get(k)
                if isinstance(v, list):
                    if atual not in v: ok = False
                elif atual != v: ok = False
            elif k == 'alguma_propriedade':
                tem = {p.get('propriedade') for p in (it.get('propriedades') or [])}
                if not (set(v) & tem): ok = False
            elif k == 'grupo':
                g = it.get('grupo')
                if isinstance(v, list):
                    if g not in v: ok = False
                elif g != v: ok = False
            if not ok: break
        if ok: n += 1
    return (n, 'ok')


def checar_efeito(ctx, e, dentro_de_escolha=None):
    """dentro_de_escolha: o bloco 'de' da escolha-mãe, quando o efeito é
    'efeito_por_item_escolhido' — aí o placeholder {{escolhido}} é legítimo e a
    checagem da chave já foi feita contra o catálogo da escolha."""
    t = e.get('tipo')
    if t not in TIPOS_EFEITO:
        erros.append(f"[tipo de efeito desconhecido] {ctx}: '{t}'")
        return
    if dentro_de_escolha is not None:
        campos = [v for v in e.values() if isinstance(v, str)]
        if PLACEHOLDER not in campos:
            erros.append(f"[efeito_por_item_escolhido sem {PLACEHOLDER}] {ctx}: "
                         "o efeito precisa consumir o item escolhido")
        # o valor real vem do catálogo da escolha, já validado — não checar chaves aqui
        return
    if t == 'impedir':
        # o esquema do efeito sempre permitiu 'alvo' como LISTA; este ramo só olhava
        # string, e uma lista estourava o validador em vez de ser conferida item a item
        for a in (e['alvo'] if isinstance(e.get('alvo'), list) else [e.get('alvo')]):
            if a not in ALVOS_IMP:
                erros.append(f"[alvo de impedimento inexistente] {ctx}: '{a}'")
    elif t in TIPOS_COM_ALVO_DE_JOGADA and 'alvo' in e:
        # 'alvo' aqui é uma jogada/valor da ficha: sai de catalogos/alvos.json
        for a in (e['alvo'] if isinstance(e['alvo'], list) else [e['alvo']]):
            if isinstance(a, str):
                checar_alvo(ctx, a)
    if t == 'alterar_dano':
        # ou o tipo é literal, ou é derivado de uma escolha — e aí todo valor do mapa vale
        if 'tipo_dano_derivado' in e:
            mapa = (e['tipo_dano_derivado'] or {}).get('mapa') or {}
            if not mapa:
                erros.append(f"[tipo_dano_derivado sem mapa] {ctx}")
            for chave, dano in mapa.items():
                if dano not in DANOS:
                    erros.append(f"[tipo de dano inexistente] {ctx}: mapa['{chave}'] = '{dano}'")
        elif (e.get('tipo_dano') not in DANOS
              and e.get('tipo_dano') not in DANOS_DERIVADOS
              and e.get('tipo_dano') != PLACEHOLDER):
            # 'mesmo_do_ataque' e afins valem aqui como em qualquer outro efeito:
            # a Dádiva do Ataque Irresistível soma dano DO MESMO TIPO do ataque.
            erros.append(f"[tipo de dano inexistente] {ctx}: '{e.get('tipo_dano')}'")
        # 'todos, exceto X, Y' só vale se X e Y forem tipos de dano de verdade
        for d in e.get('excecoes', []):
            if d not in DANOS:
                erros.append(f"[tipo de dano inexistente] {ctx}: exceção '{d}'")
    # tipo de dano em QUALQUER efeito, não só em alterar_dano. Os valores derivados
    # ('mesmo_do_ataque', 'mesmo_da_arma'…) e o placeholder de escolha são legítimos.
    if t != 'alterar_dano' and isinstance(e.get('tipo_dano'), str):
        d = e['tipo_dano']
        if d not in DANOS and d not in DANOS_DERIVADOS and d != PLACEHOLDER:
            erros.append(f"[tipo de dano inexistente] {ctx}: '{d}'")
    for d in (e.get('escolher_tipo_dano') or []):
        if isinstance(d, str) and d not in DANOS:
            erros.append(f"[tipo de dano inexistente] {ctx}: escolha '{d}'")
    if t == 'conceder_velocidade' and e.get('tipo_deslocamento') not in DESLOCAMENTOS:
        erros.append(f"[tipo de deslocamento inexistente] {ctx}: '{e.get('tipo_deslocamento')}'")
    if t == 'conceder_sentido' and e.get('sentido') not in SENTIDOS:
        erros.append(f"[sentido inexistente] {ctx}: '{e.get('sentido')}'")
    if t in ('conceder_condicao', 'alterar_condicao') and e.get('condicao_id') not in CONDICOES:
        erros.append(f"[condição inexistente] {ctx}: '{e.get('condicao_id')}'")
    if t == 'preparar_magias':
        fonte = e.get('fonte_das_magias')
        if fonte not in FONTES_DE_PREPARACAO:
            erros.append(f"[fonte de preparação ausente ou inválida] {ctx}: '{fonte}' "
                         f"(esperado um de {sorted(FONTES_DE_PREPARACAO)})")
        if fonte == 'lista_de_classe' and not e.get('lista_id'):
            erros.append(f"[preparação da lista sem lista_id] {ctx}")
    if t == 'canalizar_divindade':
        op = e.get('opcoes') or {}
        cat = op.get('catalogo')
        if cat not in CHAVES:
            erros.append(f"[catálogo inexistente] {ctx}: '{cat}'")
        else:
            for k in op.get('base', []):
                if k not in CHAVES[cat]:
                    erros.append(f"[opção inexistente] {ctx}: '{k}' não está em '{cat}'")
    if t in ('expandir_opcoes_de_escolha', 'alterar_quantidade_de_escolha'):
        eid = e.get('escolha_id')
        if not eid:
            erros.append(f"[escolha_id ausente] {ctx}: '{t}' precisa dizer qual escolha altera")
        else:
            ESCOLHAS_REFERENCIADAS.add((ctx, eid))
    if t == 'expandir_opcoes_de_escolha':
        cat = e.get('catalogo')
        if cat not in CHAVES:
            erros.append(f"[catálogo inexistente] {ctx}: '{cat}'")
        else:
            for k in e.get('chaves', []):
                if k not in CHAVES[cat]:
                    erros.append(f"[opção inexistente] {ctx}: '{k}' não está em '{cat}'")
                else:
                    OPCOES_CONCEDIDAS.add((cat, k))
    if t == 'magias_de_patrono':
        for linha in ((e.get('tabela') or {}).get('linhas') or []):
            for mg in linha.get('magias', []):
                if mg not in CHAVES.get('magias', set()):
                    erros.append(f"[magia inexistente] {ctx}: nível {linha.get('nivel')} → '{mg}'")
    if t in ('desbloquear_magias', 'conjurar_sem_espaco', 'preparar_magias'):
        nomes = e.get('magias') or ([e['magia']] if isinstance(e.get('magia'), str) else [])
        for mg in nomes:
            if mg.startswith('$'):
                continue  # referência a uma escolha anterior; resolve em tempo de execução
            if mg != PLACEHOLDER and mg not in CHAVES.get('magias', set()):
                erros.append(f"[magia inexistente] {ctx}: '{mg}'")
        li = e.get('lista_id')
        # a lista só precisa existir quando ela É a fonte das magias; se o efeito nomeia
        # as magias, o lista_id é só um rótulo de agrupamento da própria característica
        if li and not nomes and li not in CHAVES.get('listas_de_magia', set()):
            erros.append(f"[lista de magia inexistente] {ctx}: '{li}'")
    if t == 'vantagem' and e.get('modo') not in ('vantagem', 'desvantagem'):
        erros.append(f"[modo inválido] {ctx}: '{e.get('modo')}'")
    if t == 'substituir_regra' and ctx_status.get(ctx.split('/')[0] + '/' + ctx.split('/')[1]) != 'duvida':
        avisos.append(f"[substituir_regra sem revisão] {ctx}")
    # 3./5. escolha: quantidade e filtro
    if t == 'escolha':
        if e.get('id'):
            ESCOLHAS_DECLARADAS[e['id']] = ctx
        de = e.get('de', {})
        cat = de.get('catalogo')
        if cat not in CHAVES:
            erros.append(f"[catálogo inexistente] {ctx}: '{cat}'")
        else:
            if 'chaves' in de:
                for k in de['chaves']:
                    if k not in CHAVES[cat]:
                        erros.append(f"[chave inexistente] {ctx}: '{k}' não está em '{cat}'")
                q = e.get('quantidade', 0)
                if de.get('de_variantes'):
                    # A escolha não é entre as CHAVES, e sim entre as VARIANTES do item
                    # apontado — os dez Instrumentos Musicais da p. 221, por exemplo.
                    # Sem isto, "escolha 3 instrumentos" com uma chave só parecia erro,
                    # e por isso vivia com um contorno em `quantidade_de_instrumentos`.
                    if len(de['chaves']) != 1:
                        erros.append(f"[de_variantes com mais de uma chave] {ctx}: "
                                     "aponte para um item só")
                    for k in de['chaves']:
                        alvo = next((i for i in (catalogos.get(cat) or {}).get('itens', [])
                                     if i['id'] == k), None)
                        vs = (alvo or {}).get('variantes') or []
                        if not vs:
                            erros.append(f"[item sem variantes] {ctx}: '{k}' não declara "
                                         "'variantes', mas a escolha diz de_variantes")
                        elif isinstance(q, int) and q > len(vs):
                            erros.append(f"[quantidade > opções] {ctx}: {q} de "
                                         f"{len(vs)} variantes de '{k}'")
                elif isinstance(q, int) and q > len(de['chaves']):
                    erros.append(f"[quantidade > opções] {ctx}: {e.get('quantidade')} de {len(de['chaves'])}")
            elif 'filtro' not in de and not de.get('todo_o_catalogo'):
                erros.append(f"[escolha sem chaves, filtro ou todo_o_catalogo] {ctx}")
            elif (de.get('todo_o_catalogo') and isinstance(e.get('quantidade'), int)
                  and e['quantidade'] > len(CHAVES[cat])):
                erros.append(f"[quantidade > opções] {ctx}: {e.get('quantidade')} de {len(CHAVES[cat])} em '{cat}'")
            if 'filtro' in de:
                for k in chaves_de_filtro_desconhecidas(cat, de['filtro']):
                    erros.append(
                        f"[chave de filtro desconhecida] {ctx}: '{k}' não é campo de "
                        f"'{cat}' nem filtro de runtime declarado. Se o motor resolve, "
                        f"declare em FILTROS_DE_RUNTIME; se não, é erro de digitação.")
            # regra 5 do esquema: filtro não pode resolver para conjunto vazio
            if 'filtro' in de and not de.get('pendente'):
                n, motivo = resolver_filtro(cat, de['filtro'])
                if n == 0:
                    (avisos if motivo in ('lista_nao_preenchida', 'catalogo_pendente')
                     else erros).append(
                        f"[filtro vazio] {ctx}: o filtro {de['filtro']} não devolve nenhum item de "
                        f"'{cat}'" + (" (ainda não preenchido — pendência conhecida, não erro)"
                                      if motivo in ('lista_nao_preenchida', 'catalogo_pendente')
                                      else ""))
        if 'efeito_por_item_escolhido' in e:
            checar_efeito(ctx + '/efeito_por_item_escolhido',
                          e['efeito_por_item_escolhido'], dentro_de_escolha=de)


ctx_status = {}
# todo efeito visto, com o caminho — para as checagens por tipo mais abaixo
EFEITOS_VISTOS = []


def varrer(ctx, obj, e_efeito=False):
    """e_efeito: obj está dentro de uma lista 'efeitos', logo TEM de ser um efeito
    com tipo conhecido. Sem isso, um tipo digitado errado passava despercebido —
    a checagem só rodava quando o tipo já era válido."""
    if isinstance(obj, dict):
        t = obj.get('tipo')
        if e_efeito and not (isinstance(t, str) and t in TIPOS_EFEITO):
            erros.append(f"[tipo de efeito desconhecido] {ctx}: '{t}'")
        elif isinstance(t, str) and t in TIPOS_EFEITO:
            checar_efeito(ctx, obj)
        if isinstance(t, str) and t in TIPOS_EFEITO:
            EFEITOS_VISTOS.append((ctx, obj))
        for k, v in obj.items():
            if k == 'efeito_por_item_escolhido':
                # A checagem de chaves fica com o bloco 'escolha' da mãe (o valor real
                # vem do catálogo). Mas o efeito EM SI precisa entrar em EFEITOS_VISTOS,
                # senão as checagens por tipo não o enxergam — foi assim que um
                # aumento_atributo sem teto passou no teste negativo.
                if isinstance(v, dict) and v.get('tipo') in TIPOS_EFEITO:
                    EFEITOS_VISTOS.append((f"{ctx}/{k}", v))
                continue
            varrer(f"{ctx}/{k}", v, e_efeito=(k == 'efeitos'))
    elif isinstance(obj, list):
        for n, v in enumerate(obj):
            varrer(f"{ctx}[{n}]", v, e_efeito=e_efeito)


for cid, c in list(colecoes.items()) + list(catalogos.items()):
    for i in c['itens']:
        ctx_status[f"{cid}/{i['id']}"] = i.get('revisao', {}).get('status')
        varrer(f"{cid}/{i['id']}", i)


def checar_teste(ctx, teste):
    """Valida perícias e atributos citados em qualquer bloco 'teste'."""
    if not isinstance(teste, dict):
        return
    for p in (teste.get('pericias') or []):
        if p not in PERICIAS:
            erros.append(f"[perícia inexistente] {ctx}: '{p}'")
    if teste.get('pericia') and teste['pericia'] not in PERICIAS:
        erros.append(f"[perícia inexistente] {ctx}: '{teste['pericia']}'")
    if teste.get('atributo') and teste['atributo'] not in ATRIBUTOS:
        erros.append(f"[atributo inexistente] {ctx}: '{teste['atributo']}'")
    for op in (teste.get('opcoes') or []):
        checar_teste(ctx + '/opcao', op)


def varrer_testes(ctx, obj):
    if isinstance(obj, dict):
        if 'teste' in obj:
            checar_teste(ctx, obj['teste'])
        if 'salvaguarda' in obj and isinstance(obj['salvaguarda'], dict):
            checar_teste(ctx + '/salvaguarda', obj['salvaguarda'])
        for k, v in obj.items():
            varrer_testes(f"{ctx}/{k}", v)
    elif isinstance(obj, list):
        for n, v in enumerate(obj):
            varrer_testes(f"{ctx}[{n}]", v)


for cid, c in list(colecoes.items()) + list(catalogos.items()):
    for i in c['itens']:
        varrer_testes(f"{cid}/{i['id']}", i)
    # idiomas citados em catálogos/coleções devem existir
    for i in c['itens']:
        for k in ('idioma', 'idiomas'):
            for v in ([i[k]] if isinstance(i.get(k), str) else (i.get(k) or [])):
                if v not in CHAVES.get('idiomas', set()):
                    erros.append(f"[idioma inexistente] {cid}/{i['id']}: '{v}'")

# perícias citadas em testes de ações
for i in colecoes.get('acoes', {}).get('itens', []):
    for p in (i.get('teste', {}).get('pericias') or []):
        if p not in PERICIAS:
            erros.append(f"[perícia inexistente] acoes/{i['id']}: '{p}'")
    for op in (i.get('teste', {}).get('opcoes') or []):
        if isinstance(op, dict):
            if op.get('pericia') and op['pericia'] not in PERICIAS:
                erros.append(f"[perícia inexistente] acoes/{i['id']}: '{op['pericia']}'")
            if op.get('atributo') and op['atributo'] not in ATRIBUTOS:
                erros.append(f"[atributo inexistente] acoes/{i['id']}: '{op['atributo']}'")
    if i.get('teste', {}).get('pericia') and i['teste']['pericia'] not in PERICIAS:
        erros.append(f"[perícia inexistente] acoes/{i['id']}: '{i['teste']['pericia']}'")
    if i.get('custo') not in CHAVES['custos_de_acao']:
        erros.append(f"[custo de ação inexistente] acoes/{i['id']}: '{i.get('custo')}'")
    for e in (i.get('encerramento') or []) + (i.get('perde_beneficio_se') or []):
        if e.get('condicao_id') and e['condicao_id'] not in CONDICOES:
            erros.append(f"[condição inexistente] acoes/{i['id']}: '{e['condicao_id']}'")

# ------------------------------------- classes, subclasses e características
CARACS = CHAVES.get('caracteristicas', set())
NIVEL_CARAC_TMP = {c_['id']: c_ for c_ in colecoes.get('caracteristicas', {}).get('itens', [])}
SUB_FEATURES = set()
for _ca in colecoes.get('caracteristicas', {}).get('itens', []):
    for _e in _ca.get('efeitos', []):
        if _e.get('tipo') == 'conceder_acao' and _e.get('id'):
            SUB_FEATURES.add(_e['id'])
CLASSES = CHAVES.get('classes', set())
SUBCLASSES = CHAVES.get('subclasses', set())

for cl in colecoes.get('classes', {}).get('itens', []):
    ctx = f"classes/{cl['id']}"
    # os dois campos são LISTA de atributos; string solta já causou erro de forma
    for campo in ('salvaguardas_primarias', 'atributo_primario'):
        v = cl.get(campo)
        if v is not None and not isinstance(v, list):
            erros.append(f"[campo deveria ser lista] {ctx}/{campo}: {v!r}")
            continue
        for s_ in (v or []):
            if s_ not in ATRIBUTOS:
                erros.append(f"[atributo inexistente] {ctx}: '{s_}'")
    for sc in cl.get('subclasses', []):
        if sc not in SUBCLASSES:
            erros.append(f"[subclasse inexistente] {ctx}: '{sc}'")
    niveis = [l['nivel'] for l in cl.get('progressao', [])]
    if niveis != list(range(1, 21)):
        erros.append(f"[progressão incompleta] {ctx}: níveis {niveis[:3]}... ({len(niveis)} linhas, esperado 1-20)")
    colunas_declaradas = set(cl.get('colunas_da_tabela', {}))
    for linha in cl.get('progressao', []):
        for c_ in linha.get('caracteristicas', []):
            if c_ not in CARACS:
                erros.append(f"[característica inexistente] {ctx}/nivel_{linha['nivel']}: '{c_}'")
        for col in linha.get('colunas', {}):
            if col not in colunas_declaradas:
                erros.append(f"[coluna não declarada] {ctx}/nivel_{linha['nivel']}: '{col}'")

# nível declarado na característica bate com o nível em que a classe a concede
NIVEL_NA_PROGRESSAO = {}
for cl in colecoes.get('classes', {}).get('itens', []):
    for linha in cl.get('progressao', []):
        for c_ in linha.get('caracteristicas', []):
            NIVEL_NA_PROGRESSAO.setdefault(c_, []).append(linha['nivel'])
for ca in colecoes.get('caracteristicas', {}).get('itens', []):
    if ca.get('subclasse') or ca.get('escopo') == 'generico':
        continue
    niveis = NIVEL_NA_PROGRESSAO.get(ca['id'])
    if niveis and ca.get('nivel') not in niveis:
        erros.append(f"[nível divergente] caracteristicas/{ca['id']}: declara nível "
                     f"{ca.get('nivel')}, mas a progressão a concede em {niveis}")

# toda característica de subclasse precisa estar listada na sua subclasse
LISTADAS = {c_ for sc in colecoes.get('subclasses', {}).get('itens', [])
            for c_ in sc.get('caracteristicas', [])}
for ca in colecoes.get('caracteristicas', {}).get('itens', []):
    if ca.get('subclasse') and ca['id'] not in LISTADAS:
        erros.append(f"[característica órfã] caracteristicas/{ca['id']}: tem subclasse "
                     f"'{ca['subclasse']}' mas não está listada nela")

for cl in colecoes.get('classes', {}).get('itens', []):
    for linha in cl.get('progressao', []):
        for c_ in linha.get('caracteristicas', []):
            ent = NIVEL_CARAC_TMP.get(c_)
            if ent and ent.get('escopo') != 'generico' and ent.get('classe') not in (None, cl['id']):
                erros.append(f"[característica de outra classe] classes/{cl['id']}/nivel_{linha['nivel']}: "
                             f"'{c_}' pertence a '{ent.get('classe')}'")

# níveis marcados como 'característica de subclasse' devem existir em todas as subclasses
NIVEL_CARAC = {c_['id']: c_ for c_ in colecoes.get('caracteristicas', {}).get('itens', [])}
for cl in colecoes.get('classes', {}).get('itens', []):
    marcados = [l['nivel'] for l in cl.get('progressao', [])
                if any(NIVEL_CARAC.get(c_, {}).get('tipo_de_entrada') == 'marcador'
                       for c_ in l.get('caracteristicas', []))]
    for sc in colecoes.get('subclasses', {}).get('itens', []):
        if sc.get('classe') != cl['id']:
            continue
        niveis_sc = {NIVEL_CARAC[c_]['nivel'] for c_ in sc.get('caracteristicas', []) if c_ in NIVEL_CARAC}
        for n in marcados:
            if n not in niveis_sc:
                erros.append(f"[subclasse sem característica no nível marcado] subclasses/{sc['id']}: "
                             f"a classe '{cl['id']}' concede característica de subclasse no nível {n}, "
                             f"mas esta subclasse não tem nenhuma nesse nível")

for sc in colecoes.get('subclasses', {}).get('itens', []):
    ctx = f"subclasses/{sc['id']}"
    if sc.get('classe') not in CLASSES:
        erros.append(f"[classe inexistente] {ctx}: '{sc.get('classe')}'")
    for c_ in sc.get('caracteristicas', []):
        if c_ not in CARACS:
            erros.append(f"[característica inexistente] {ctx}: '{c_}'")

for ca in colecoes.get('caracteristicas', {}).get('itens', []):
    ctx = f"caracteristicas/{ca['id']}"
    if ca.get('classe') and ca['classe'] not in CLASSES:
        erros.append(f"[classe inexistente] {ctx}: '{ca['classe']}'")
    if ca.get('subclasse') and ca['subclasse'] not in SUBCLASSES:
        erros.append(f"[subclasse inexistente] {ctx}: '{ca['subclasse']}'")
    for e_ in ca.get('efeitos', []):
        if e_.get('tipo') == 'melhorar_caracteristica':
            alvo = e_.get('alvo')
            if alvo not in CARACS and alvo not in SUB_FEATURES:
                erros.append(f"[alvo de melhoria inexistente] {ctx}: '{alvo}'")

# -------------------------------- invocações: pré-requisitos e círculo de pacto
INVOC = CHAVES.get('invocacoes_misticas', set())
for i in catalogos.get('invocacoes_misticas', {}).get('itens', []):
    for pr in i.get('pre_requisitos', []):
        if pr.get('tipo') == 'invocacao' and pr.get('chave') not in INVOC:
            erros.append(f"[invocação inexistente] invocacoes_misticas/{i['id']}: "
                         f"pré-requisito '{pr.get('chave')}'")
        if pr.get('tipo') == 'nivel_de_classe' and pr.get('classe') not in CHAVES.get('classes', set()):
            erros.append(f"[classe inexistente] invocacoes_misticas/{i['id']}: '{pr.get('classe')}'")

for cl in colecoes.get('classes', {}).get('itens', []):
    if (cl.get('conjuracao') or {}).get('tipo') != 'pacto':
        continue
    for linha in cl.get('progressao', []):
        c_ = linha.get('colunas', {}).get('circulo_dos_espacos')
        if c_ is not None and not (1 <= c_ <= 5):
            erros.append(f"[círculo de pacto fora da faixa] classes/{cl['id']}/nivel_{linha['nivel']}: "
                         f"{c_} (Magia de Pacto vai do 1º ao 5º círculo)")

# ------------------------------------------------------------------ itens
# O capítulo 6 fechou o catálogo de itens. Daqui em diante, referência a item
# que não existe é erro, e os campos numéricos precisam ser coerentes entre si.
MOEDAS_EM_PC = {'pc': 1, 'pp': 10, 'pe': 50, 'po': 100, 'pl': 1000}
CATEGORIAS_DE_ITEM = {
    'arma', 'armadura', 'municao', 'equipamento_de_aventura',
    'foco_de_conjuracao', 'montaria', 'arreio_ou_veiculo_de_tracao', 'veiculo',
}
GRUPOS_DE_ARMA = CHAVES.get('categorias_de_arma', set())
GRUPOS_DE_ARMADURA = CHAVES.get('categorias_de_armadura', set())
MAESTRIAS = CHAVES.get('maestrias_de_arma', set())
PROPRIEDADES_DE_ARMA = CHAVES.get('propriedades_de_arma', set())
ITENS = CHAVES.get('itens', set())
FERRAMENTAS = CHAVES.get('ferramentas', set())


def checar_custo(ctx, c):
    if c is None:
        return
    if c.get('moeda') not in MOEDAS_EM_PC:
        erros.append(f"[moeda inválida] {ctx}: {c.get('moeda')!r}")
        return
    esperado = c['valor'] * MOEDAS_EM_PC[c['moeda']]
    if abs(c.get('em_pc', -1) - esperado) > 0.001:
        erros.append(f"[custo incoerente] {ctx}: {c['valor']} {c['moeda'].upper()} "
                     f"são {esperado} PC, mas o campo diz {c.get('em_pc')}")


itens_cat = catalogos.get('itens')
if itens_cat:
    for i in itens_cat['itens']:
        ctx = f"itens/{i['id']}"
        if i.get('categoria') not in CATEGORIAS_DE_ITEM:
            erros.append(f"[categoria de item inválida] {ctx}: {i.get('categoria')!r}")
        checar_custo(ctx, i.get('custo'))
        if i.get('custo') is None and not i.get('custo_varia'):
            erros.append(f"[item sem custo] {ctx}: sem 'custo' e sem 'custo_varia'")
        p = i.get('peso_kg')
        if p is not None and (not isinstance(p, (int, float)) or p <= 0):
            erros.append(f"[peso inválido] {ctx}: {p!r}")
        if i['categoria'] == 'arma':
            if i.get('grupo') not in GRUPOS_DE_ARMA:
                erros.append(f"[grupo de arma inválido] {ctx}: {i.get('grupo')!r}")
            if i.get('alcance') not in ('corpo_a_corpo', 'a_distancia'):
                erros.append(f"[alcance de arma inválido] {ctx}: {i.get('alcance')!r}")
            if i.get('maestria') not in MAESTRIAS:
                erros.append(f"[maestria inexistente] {ctx}: {i.get('maestria')!r}")
            d = i.get('dano') or {}
            if d.get('tipo_dano') not in DANOS:
                erros.append(f"[tipo de dano inexistente] {ctx}: {d.get('tipo_dano')!r}")
            if not d.get('formula_dado') and d.get('valor_fixo') is None:
                erros.append(f"[arma sem dano] {ctx}")
            for prop in (i.get('propriedades') or []):
                if prop.get('propriedade') not in PROPRIEDADES_DE_ARMA:
                    erros.append(f"[propriedade de arma inexistente] {ctx}: "
                                 f"{prop.get('propriedade')!r}")
                if prop.get('propriedade') == 'municao' and 'municao' in prop:
                    if prop['municao'] not in ITENS:
                        erros.append(f"[munição inexistente] {ctx}: {prop['municao']!r}")
        if i['categoria'] == 'armadura':
            if i.get('grupo') not in GRUPOS_DE_ARMADURA:
                erros.append(f"[grupo de armadura inválido] {ctx}: {i.get('grupo')!r}")
            ca = i.get('ca') or {}
            if 'base' not in ca and 'bonus' not in ca:
                erros.append(f"[armadura sem CA] {ctx}")
        if i['categoria'] == 'municao' and i.get('armazenada_em') not in ITENS:
            erros.append(f"[recipiente de munição inexistente] {ctx}: "
                         f"{i.get('armazenada_em')!r}")

# ferramentas: atributo, custo e a lista de Fabricação
fer_cat = catalogos.get('ferramentas')
if fer_cat and not fer_cat.get('parcial'):
    for i in fer_cat['itens']:
        ctx = f"ferramentas/{i['id']}"
        if i.get('atributo') not in ATRIBUTOS:
            erros.append(f"[atributo inexistente] {ctx}: {i.get('atributo')!r}")
        checar_custo(ctx, i.get('custo'))
        for chave in ((i.get('fabricacao') or {}).get('itens') or []):
            if chave not in ITENS:
                erros.append(f"[item de fabricação inexistente] {ctx}: '{chave}'")

# Propriedade que DECLARA CAMPO: todo item que tem a propriedade precisa trazer o
# campo. Sem isso, 'declara_campo_no_item' seria só uma promessa no catálogo.
props_cat = catalogos.get('propriedades_de_arma')
if props_cat and itens_cat:
    exigidos = {}
    for p in props_cat['itens']:
        for e in (p.get('efeitos') or []):
            if e.get('tipo') == 'declara_campo_no_item':
                exigidos[p['id']] = e['campo']
    for i in itens_cat['itens']:
        tem = {x.get('propriedade') for x in (i.get('propriedades') or [])}
        for prop_id, campo in exigidos.items():
            if prop_id in tem and campo not in i:
                erros.append(f"[campo declarado ausente] itens/{i['id']}: tem a "
                             f"propriedade '{prop_id}', que exige o campo '{campo}'")
    # o consumo aponta para uma munição que existe
    for i in itens_cat['itens']:
        c = i.get('consumo')
        if c and c.get('item') not in ITENS:
            erros.append(f"[munição de consumo inexistente] itens/{i['id']}: "
                         f"{c.get('item')!r}")
    # toda arma e todo escudo dizem quantas mãos ocupam
    for i in itens_cat['itens']:
        if i['categoria'] == 'arma' or (i['categoria'] == 'armadura' and
                                        i.get('grupo') == 'escudo'):
            m = i.get('maos_ocupadas')
            if m not in (1, 2):
                erros.append(f"[mãos ocupadas inválidas] itens/{i['id']}: {m!r}")


# proficiência concedida por FILTRO: resolve contra o catálogo e cobra resultado.
# Antes isso era uma string ('categoria:marcial+propriedade:acuidade_ou_leve') que
# ninguém interpretava — filtro que não devolve nada é defeito silencioso.
for c in colecoes.get('classes', {}).get('itens', []):
    for e in (c.get('proficiencias_iniciais') or []):
        if e.get('tipo') != 'conceder_proficiencia' or 'de' not in e:
            continue
        ctx = f"classes/{c['id']}/proficiencias_iniciais"
        de = e['de']
        cat = de.get('catalogo')
        if cat not in CHAVES:
            erros.append(f"[catálogo inexistente] {ctx}: {cat!r}")
            continue
        q, motivo = resolver_filtro(cat, de.get('filtro') or {})
        if motivo == 'ok' and q == 0:
            erros.append(f"[filtro de proficiência vazio] {ctx}: {de.get('filtro')} "
                         f"não devolve nenhum item de '{cat}'")
        if 'chave' in e and 'de' in e:
            erros.append(f"[proficiência com chave e filtro] {ctx}: declare um ou outro")


# equipamento inicial das classes: todo id precisa existir
for c in colecoes.get('classes', {}).get('itens', []):
    eq = c.get('equipamento_inicial') or {}
    for op in eq.get('opcoes', []):
        for it in (op.get('itens') or []):
            if 'item' in it and it['item'] not in ITENS | FERRAMENTAS:
                erros.append(f"[item inexistente] classes/{c['id']}/equipamento_inicial: "
                             f"'{it['item']}'")


# ----------------------------------------------------------------- magias
# Uma magia 'detalhada' passou pelo capítulo 7 e precisa ter os campos da entrada.
# As demais ainda só têm nome/círculo/escola/listas, e isso é declarado, não defeito.
CAMPOS_DE_MAGIA = {
    'descricao_curta': str,
    'tempo_de_conjuracao': dict,
    'alcance': dict,
    'componentes': dict,
    'duracao': dict,
}
TIPOS_DE_CONJURACAO = {'acao', 'acao_bonus', 'reacao', 'tempo'}
TIPOS_DE_ALCANCE = {'pessoal', 'toque', 'distancia', 'ilimitado', 'a_vista',
                    'especial'}
TIPOS_DE_DURACAO = {'instantanea', 'tempo', 'ate_dissipada', 'especial'}
FORMAS_DE_AREA = {'esfera', 'cubo', 'cone', 'cilindro', 'linha', 'emanacao'}
ESCOLAS = CHAVES.get('escolas_de_magia', set())
LISTAS_DE_CLASSE = CHAVES.get('listas_de_magia', set())


def normalizar(s):
    import unicodedata
    s = unicodedata.normalize('NFD', str(s).lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


magias_cat = catalogos.get('magias')
if magias_cat:
    vistos_norm = {}
    n_detalhadas = 0
    for m in magias_cat['itens']:
        ctx = f"magias/{m['id']}"
        # nome duplicado depois de normalizar (acento, caixa e pontuação não contam)
        chave = normalizar(m['nome'])
        if chave in vistos_norm:
            erros.append(f"[nome de magia duplicado] {ctx}: '{m['nome']}' colide com "
                         f"'{vistos_norm[chave]}' depois de normalizar")
        vistos_norm[chave] = m['nome']

        if m.get('escola') and m['escola'] not in ESCOLAS:
            erros.append(f"[escola inexistente] {ctx}: '{m['escola']}'")
        if not isinstance(m.get('nivel'), int) or not 0 <= m['nivel'] <= 9:
            erros.append(f"[círculo inválido] {ctx}: {m.get('nivel')!r}")
        for lista in (m.get('listas') or []):
            if lista not in LISTAS_DE_CLASSE:
                erros.append(f"[lista de magia inexistente] {ctx}: '{lista}'")

        if not m.get('detalhada'):
            continue
        n_detalhadas += 1
        for campo, tipo in CAMPOS_DE_MAGIA.items():
            if not isinstance(m.get(campo), tipo):
                erros.append(f"[campo obrigatório ausente] {ctx}: falta '{campo}' "
                             "numa magia marcada como detalhada")
        tc = m.get('tempo_de_conjuracao') or {}
        if tc.get('tipo') not in TIPOS_DE_CONJURACAO:
            erros.append(f"[tempo de conjuração inválido] {ctx}: {tc.get('tipo')!r}")
        al = m.get('alcance') or {}
        if al.get('tipo') not in TIPOS_DE_ALCANCE:
            erros.append(f"[alcance inválido] {ctx}: {al.get('tipo')!r}")
        if al.get('tipo') == 'distancia' and not isinstance(al.get('metros'), (int, float)):
            erros.append(f"[alcance sem distância] {ctx}: tipo 'distancia' sem 'metros'")
        du = m.get('duracao') or {}
        if du.get('tipo') not in TIPOS_DE_DURACAO:
            erros.append(f"[duração inválida] {ctx}: {du.get('tipo')!r}")
        if du.get('concentracao') is not m.get('concentracao'):
            erros.append(f"[concentração inconsistente] {ctx}: o campo diz "
                         f"{m.get('concentracao')!r}, a duração diz {du.get('concentracao')!r}")
        if (m.get('tempo_de_conjuracao') or {}).get('ritual') is not m.get('ritual'):
            erros.append(f"[ritual inconsistente] {ctx}: o campo diz {m.get('ritual')!r}, "
                         f"o tempo de conjuração diz {tc.get('ritual')!r}")
        co = m.get('componentes') or {}
        if not any(co.get(k) for k in ('verbal', 'somatico', 'material')):
            erros.append(f"[sem componentes] {ctx}: nenhum de V, S ou M")
        if co.get('material') and 'material_descricao' not in co and \
                m.get('componente_material_especifico'):
            erros.append(f"[material sem descrição] {ctx}")
        for bloco in ([m['dano']] if 'dano' in m else []) + (m.get('dano_adicional_citado') or []):
            if bloco.get('tipo_dano') not in DANOS:
                erros.append(f"[tipo de dano inexistente] {ctx}: '{bloco.get('tipo_dano')}'")
            if not re.fullmatch(r'\d+d\d+', str(bloco.get('formula_dado', ''))):
                erros.append(f"[fórmula de dado inválida] {ctx}: {bloco.get('formula_dado')!r}")
        sv = m.get('salvaguarda')
        if sv and sv.get('atributo') not in ATRIBUTOS:
            erros.append(f"[atributo de salvaguarda inválido] {ctx}: {sv.get('atributo')!r}")
        ar = m.get('area')
        if ar and ar.get('forma') not in FORMAS_DE_AREA:
            erros.append(f"[forma de área inválida] {ctx}: {ar.get('forma')!r}")
        for c in (m.get('condicoes_citadas') or []):
            if c not in CONDICOES:
                erros.append(f"[condição inexistente] {ctx}: '{c}'")
    if magias_cat.get('detalhadas') != n_detalhadas:
        erros.append(f"[contagem de detalhadas incorreta] magias: declarado "
                     f"{magias_cat.get('detalhadas')}, contadas {n_detalhadas}")


# ------------------------------------------------ item de catálogo sem efeitos
# Catálogos de VOCABULÁRIO (perícias, idiomas, tipos de dano…) descrevem termos e
# não têm efeitos. Catálogos de OPÇÃO descrevem escolhas mecânicas: item sem
# 'efeitos' ali é ou defeito, ou pendência — e pendência precisa estar declarada.
CATALOGOS_DE_VOCABULARIO = {
    'alvos', 'alvos_de_impedimento', 'areas_de_efeito', 'atitudes', 'atributos',
    'categorias_de_arma', 'categorias_de_armadura', 'custos_de_acao',
    'escolas_de_magia', 'estados', 'ferramentas', 'graus_de_cobertura', 'idiomas',
    'itens', 'listas_de_iniciado_em_magia', 'listas_de_magia',
    'magias', 'manifestacoes_da_ordem', 'modos_de_aumento_de_atributo',
    'modos_de_aumento_do_antecedente',
    'pericias', 'riscos', 'sentidos', 'tamanhos',
    'tipos_de_criatura', 'tipos_de_dano', 'tipos_de_descanso',
    'tipos_de_deslocamento', 'tipos_de_efeito',
}
# Terceira família: catálogos de FÓRMULA, cujos itens são contas da ficha e não
# opções que o jogador escolhe. Ali o obrigatório é a fórmula, não os efeitos.
CATALOGOS_DE_FORMULA = {'valores_derivados'}
# Quarta família: BLOCOS DE ESTATÍSTICAS. A mecânica não mora em 'efeitos', e sim
# em atributos, pontos de vida, traços e ações — como no bloco impresso do livro.
# Cobrar 'efeitos' aqui empurraria a ficha da criatura para dentro de um campo que
# não foi feito para ela; o que se cobra é o bloco estar completo.
# `criaturas` era VOCABULÁRIO enquanto estava vazio. Com o Apêndice B extraído ele
# passa a ser o que sempre foi: bloco de estatísticas, e as checagens do bloco valem.
CATALOGOS_DE_BLOCO_DE_ESTATISTICAS = {'feras_companheiras', 'criaturas'}
# Quinta família: espécies. A mecânica mora em 'tracos', cada um com nome e página,
# porque a ficha mostra o TRAÇO, não uma lista solta de efeitos. O que se cobra é o
# cabeçalho da espécie (tipo, tamanho, deslocamento) e que todo traço tenha efeitos.
# Linhagens e legados concedem magia por NÍVEL DE PERSONAGEM, num campo próprio
# (`magias_por_nivel`) que não é um efeito — então o andador de efeitos nunca passava
# por ele, e um id de magia errado ali entrava calado. Este é o furo que o teste
# negativo do capítulo 4 encontrou.
MAGIAS = CHAVES.get('magias', set())


def checar_magias_por_nivel(ctx, obj):
    if isinstance(obj, dict):
        mpn = obj.get('magias_por_nivel')
        if isinstance(mpn, dict):
            for nivel, lista in mpn.items():
                try:
                    n_ = int(nivel)
                except (TypeError, ValueError):
                    erros.append(f"[nível não numérico] {ctx}/magias_por_nivel: '{nivel}'")
                    continue
                if not (1 <= n_ <= 20):
                    erros.append(f"[nível fora da faixa] {ctx}/magias_por_nivel: {n_}")
                for mg in (lista or []):
                    if mg not in MAGIAS:
                        erros.append(f"[magia inexistente] {ctx}/magias_por_nivel[{nivel}]: "
                                     f"'{mg}'")
        for k, v in obj.items():
            if k != 'magias_por_nivel':
                checar_magias_por_nivel(f"{ctx}/{k}", v)
    elif isinstance(obj, list):
        for n, v in enumerate(obj):
            checar_magias_por_nivel(f"{ctx}[{n}]", v)


for _cid, _c in list(catalogos.items()) + list(colecoes.items()):
    for _i in _c['itens']:
        checar_magias_por_nivel(f"{_cid}/{_i['id']}", _i)

CATALOGOS_DE_ESPECIE = {'especies'}
for cid in CATALOGOS_DE_ESPECIE:
    c = catalogos.get(cid)
    if not c:
        continue
    for i in c['itens']:
        ctx = f"{cid}/{i['id']}"
        if i.get('tipo_de_criatura') not in CHAVES.get('tipos_de_criatura', set()):
            erros.append(f"[tipo de criatura inexistente] {ctx}: '{i.get('tipo_de_criatura')}'")
        tam = i.get('tamanho') or {}
        opcoes_de_tamanho = ([tam['fixo']] if 'fixo' in tam else list(tam.get('escolha') or []))
        if not opcoes_de_tamanho:
            erros.append(f"[espécie sem tamanho] {ctx}: declare 'fixo' ou 'escolha'")
        for t_ in opcoes_de_tamanho:
            if t_ not in CHAVES.get('tamanhos', set()):
                erros.append(f"[tamanho inexistente] {ctx}: '{t_}'")
        desl = i.get('deslocamento') or {}
        if desl.get('tipo') not in DESLOCAMENTOS:
            erros.append(f"[tipo de deslocamento inexistente] {ctx}: '{desl.get('tipo')}'")
        if not isinstance(desl.get('metros'), (int, float)):
            erros.append(f"[espécie sem deslocamento em metros] {ctx}")
        if not i.get('tracos'):
            erros.append(f"[espécie sem traços] {ctx}")
        for tr in (i.get('tracos') or []):
            tctx = f"{ctx}/{tr.get('id')}"
            if not tr.get('id') or not tr.get('nome'):
                erros.append(f"[traço sem id ou nome] {ctx}")
            if not tr.get('descricao_curta'):
                erros.append(f"[traço sem descrição] {tctx}")
            if not tem_fonte(tr):
                erros.append(f"[traço sem fonte] {tctx}")
            if not tr.get('efeitos') and not tr.get('pendente'):
                erros.append(f"[traço sem efeitos] {tctx}: todo traço precisa de efeitos "
                             "executáveis, ou de 'pendente': true")
            n_ = tr.get('nivel_de_personagem')
            if n_ is not None and not (1 <= n_ <= 20):
                erros.append(f"[nível de personagem fora da faixa] {tctx}: {n_}")
        ids_ = [tr.get('id') for tr in (i.get('tracos') or [])]
        if len(ids_) != len(set(ids_)):
            erros.append(f"[traços com id repetido] {ctx}")

# Sexta família: antecedentes. Forma fixa do livro — três atributos, um talento de
# Origem, DUAS perícias, uma ferramenta e o pacote contra 50 PO. O erro que esta
# regra existe para pegar é o de digitação: uma perícia a menos, um item que não
# existe, o pacote sem a alternativa em dinheiro.
CATALOGOS_DE_ANTECEDENTE = {'antecedentes'}
TALENTOS_DE_ORIGEM = {i['id'] for i in catalogos.get('talentos', {}).get('itens', [])
                      if i.get('categoria') == 'origem'}
for cid in CATALOGOS_DE_ANTECEDENTE:
    c = catalogos.get(cid)
    if not c:
        continue
    for i in c['itens']:
        ctx = f"{cid}/{i['id']}"
        atrs = i.get('atributos') or []
        if len(atrs) != 3:
            erros.append(f"[antecedente sem três atributos] {ctx}: {len(atrs)}")
        for a_ in atrs:
            if a_ not in ATRIBUTOS:
                erros.append(f"[atributo inexistente] {ctx}: '{a_}'")
        tal = i.get('talento_de_origem')
        if tal not in TALENTOS_DE_ORIGEM:
            erros.append(f"[talento de Origem inexistente] {ctx}: '{tal}' não é um talento "
                         "da categoria 'origem'")
        pers = i.get('pericias') or []
        if len(pers) != 2:
            erros.append(f"[antecedente sem duas perícias] {ctx}: {len(pers)}")
        for p_ in pers:
            if p_ not in PERICIAS:
                erros.append(f"[perícia inexistente] {ctx}: '{p_}'")
        eq = i.get('equipamento') or {}
        ops = {o.get('id') for o in eq.get('opcoes', [])}
        if ops != {'A', 'B'}:
            erros.append(f"[antecedente sem as duas opções de equipamento] {ctx}: {sorted(ops)}")
        for o in eq.get('opcoes', []):
            for it_ in (o.get('itens') or []):
                if "item" in it_ and it_["item"] not in ITENS | FERRAMENTAS:
                    erros.append(f"[item inexistente] {ctx}/equipamento: '{it_['item']}'")
        if not any(o.get('id') == 'B' and (o.get('moedas') or {}).get('po') == 50
                   for o in eq.get('opcoes', [])):
            erros.append(f"[antecedente sem a alternativa de 50 PO] {ctx}")
for cid in CATALOGOS_DE_BLOCO_DE_ESTATISTICAS:
    c = catalogos.get(cid)
    if not c:
        continue
    for i in c['itens']:
        for campo in ('atributos', 'pontos_de_vida', 'classe_de_armadura',
                      'deslocamentos', 'acoes'):
            if not i.get(campo):
                erros.append(f"[bloco de estatísticas incompleto] {cid}/{i['id']}: "
                             f"falta '{campo}'")
        for a_ in (i.get('atributos') or {}):
            if a_ not in ATRIBUTOS:
                erros.append(f"[atributo inexistente] {cid}/{i['id']}: '{a_}'")
        if i.get('tamanho') and i['tamanho'] not in CHAVES.get('tamanhos', set()):
            erros.append(f"[tamanho inexistente] {cid}/{i['id']}: '{i['tamanho']}'")
        if (i.get('tipo_de_criatura')
                and i['tipo_de_criatura'] not in CHAVES.get('tipos_de_criatura', set())):
            erros.append(f"[tipo de criatura inexistente] {cid}/{i['id']}: "
                         f"'{i['tipo_de_criatura']}'")
        for d_ in (i.get('deslocamentos') or []):
            if d_.get('tipo') not in DESLOCAMENTOS:
                erros.append(f"[tipo de deslocamento inexistente] {cid}/{i['id']}: "
                             f"'{d_.get('tipo')}'")
        for s_ in (i.get('sentidos') or []):
            if s_.get('sentido') not in SENTIDOS:
                erros.append(f"[sentido inexistente] {cid}/{i['id']}: '{s_.get('sentido')}'")
for cid in CATALOGOS_DE_FORMULA:
    c = catalogos.get(cid)
    if not c:
        continue
    for i in c['itens']:
        tem = any(k in i for k in ('formula', 'tabela_por_nivel', 'tabela_por_tamanho',
                                   'por_alcance_da_arma'))
        if not tem:
            erros.append(f"[derivado sem fórmula] {cid}/{i['id']}: precisa de 'formula' "
                         "ou de uma tabela que a substitua")
        if not i.get('descricao_curta'):
            erros.append(f"[derivado sem descrição] {cid}/{i['id']}")
        for parc in (i.get('parcelas') or []):
            if 'rotulo' not in parc or 'chave' not in parc:
                erros.append(f"[parcela incompleta] {cid}/{i['id']}: toda parcela precisa "
                             "de 'rotulo' e 'chave' para o log de proveniência")
            if not parc.get('sempre') and 'condicao' not in parc:
                erros.append(f"[parcela sem condição] {cid}/{i['id']}/{parc.get('chave')}: "
                             "parcela que não é 'sempre' precisa dizer quando entra")

for cid, c in catalogos.items():
    if (cid in CATALOGOS_DE_VOCABULARIO or cid in CATALOGOS_DE_FORMULA
            or cid in CATALOGOS_DE_BLOCO_DE_ESTATISTICAS
            or cid in CATALOGOS_DE_ESPECIE):
        continue
    for i in c['itens']:
        if not i.get('efeitos') and not i.get('pendente'):
            erros.append(f"[opção de catálogo sem efeitos] {cid}/{i['id']}: "
                         "toda opção precisa de 'efeitos' executáveis, ou de "
                         "'pendente': true dizendo que ainda faltam")


# -------------------------------- escolhas alteradas à distância e opções gated
# Quem expande ou remaneja uma escolha precisa apontar para uma escolha que existe.
for ctx, eid in sorted(ESCOLHAS_REFERENCIADAS):
    if eid not in ESCOLHAS_DECLARADAS:
        erros.append(f"[escolha inexistente] {ctx}: nenhuma escolha declara id '{eid}'")

# Item de catálogo marcado 'apenas_se_concedido' não é alcançável por nível:
# alguma característica precisa concedê-lo explicitamente.
for cid, c in catalogos.items():
    for i in c['itens']:
        if i.get('apenas_se_concedido') and (cid, i['id']) not in OPCOES_CONCEDIDAS:
            erros.append(f"[opção órfã] {cid}/{i['id']}: marcada 'apenas_se_concedido', "
                         "mas nenhuma característica a concede")

# ------------------------------------- tabelas aleatórias: a faixa tem de fechar
# Uma tabela de dado só está inteira se as faixas cobrem o dado sem buraco e sem
# sobreposição. Faixa faltando é um resultado que o app não saberia resolver.
for cid, c in catalogos.items():
    if not c.get('dado_da_tabela'):
        continue
    campo = next((k for k in ('faixa_1d100', 'faixa_1d20', 'faixa_1d12', 'faixa_1d10',
                              'faixa_1d8', 'faixa_1d6')
                  if any(k in i for i in c['itens'])), None)
    if not campo:
        erros.append(f"[tabela sem faixas] {cid}: declara dado_da_tabela "
                     f"'{c['dado_da_tabela']}' mas nenhum item traz a faixa do dado")
        continue
    cob = c.get('cobertura_da_faixa') or {}
    inicio, fim = cob.get('min', 1), cob.get('max')
    if fim is None:
        erros.append(f"[tabela sem cobertura declarada] {cid}: precisa de "
                     "'cobertura_da_faixa' com min e max")
        continue
    faixas = []
    for i in c['itens']:
        f = i.get(campo)
        if not f or 'min' not in f or 'max' not in f:
            erros.append(f"[linha de tabela sem faixa] {cid}/{i['id']}: precisa de "
                         f"'{campo}' com min e max")
            continue
        if f['min'] > f['max']:
            erros.append(f"[faixa invertida] {cid}/{i['id']}: {f['min']}–{f['max']}")
        faixas.append((f['min'], f['max'], i['id']))
    faixas.sort()
    esperado = inicio
    for lo, hi, iid in faixas:
        if lo > esperado:
            erros.append(f"[buraco na tabela] {cid}: nada cobre {esperado}–{lo - 1} "
                         f"(antes de '{iid}')")
        elif lo < esperado:
            erros.append(f"[faixas sobrepostas] {cid}/{iid}: começa em {lo}, mas "
                         f"{esperado - 1} já estava coberto")
        esperado = max(esperado, hi + 1)
    if faixas and esperado != fim + 1:
        erros.append(f"[tabela incompleta] {cid}: cobertura termina em {esperado - 1}, "
                     f"deveria terminar em {fim}")

# ----------------------------------------- catálogo que custa recurso tem de dizer quanto
# opcoes_de_metamagia e afins declaram 'recurso' no cabeçalho: aí todo item precisa
# dizer o custo, ou o backend não saberia quanto debitar.
for cid, c in catalogos.items():
    rec = c.get('recurso')
    if not rec:
        continue
    campo = f"custo_em_{rec}"
    for i in c['itens']:
        v = i.get(campo)
        if not isinstance(v, int) or v < 1:
            erros.append(f"[opção sem custo] {cid}/{i['id']}: o catálogo declara "
                         f"recurso '{rec}', logo o item precisa de '{campo}' inteiro "
                         "e maior que zero")

# --------------------------------------------- movimento forçado precisa de direção
for ctx, e in EFEITOS_VISTOS:
    if e.get('tipo') != 'movimento_forcado':
        continue
    if e.get('direcao') not in ('empurrar', 'puxar', 'a_sua_escolha'):
        erros.append(f"[direção inválida] {ctx}: movimento_forcado precisa de direcao "
                     f"'empurrar', 'puxar' ou 'a_sua_escolha' (veio "
                     f"'{e.get('direcao')}')")
    if 'distancia_m' not in e and 'destino' not in e:
        erros.append(f"[movimento sem distância] {ctx}: movimento_forcado precisa de "
                     "'distancia_m' ou de um 'destino'")

# ------------------------------- rolar_na_tabela tem de apontar para uma tabela real
for ctx, e in EFEITOS_VISTOS:
    if e.get('tipo') != 'rolar_na_tabela':
        continue
    cat = e.get('catalogo')
    if cat not in catalogos:
        erros.append(f"[catálogo inexistente] {ctx}: '{cat}'")
    elif not catalogos[cat].get('dado_da_tabela'):
        erros.append(f"[catálogo não é tabela] {ctx}: '{cat}' não declara "
                     "'dado_da_tabela'")

# ------------------------- níveis de subclasse: classe e subclasse têm de concordar
for c in colecoes['classes']['itens']:
    niveis = c.get('niveis_de_caracteristica_de_subclasse')
    if not niveis:
        continue
    for s in colecoes['subclasses']['itens']:
        if s.get('classe') != c['id']:
            continue
        if s.get('niveis_de_caracteristica') != niveis:
            erros.append(f"[níveis de subclasse divergentes] subclasses/{s['id']}: "
                         f"{s.get('niveis_de_caracteristica')} ≠ {niveis} declarado em "
                         f"classes/{c['id']}")
        reais = sorted({f['nivel'] for f in colecoes['caracteristicas']['itens']
                        if f.get('subclasse') == s['id']})
        if reais and reais != sorted(niveis):
            erros.append(f"[características fora dos níveis] subclasses/{s['id']}: as "
                         f"características estão nos níveis {reais}, mas a subclasse "
                         f"declara {sorted(niveis)}")

# -------------------------------- alvo que promete um derivado tem de ter um derivado
# Foi assim que o buraco apareceu: a Resiliência Dracônica somava em
# 'pontos_de_vida_maximos' e NENHUM valor derivado montava esse número. O alvo
# declara 'derivado_id' e aqui a promessa é cobrada.
DERIVADOS_DECLARADOS = CHAVES.get('valores_derivados', set())
for i in catalogos.get('alvos', {}).get('itens', []):
    did = i.get('derivado_id')
    if did and did not in DERIVADOS_DECLARADOS:
        erros.append(f"[derivado inexistente] alvos/{i['id']}: aponta para "
                     f"'{did}', que não está em valores_derivados")

# ------------------------------- operação de fórmula tem de estar no vocabulário
# Antes cada gerador podia inventar um 'op'. Agora as operações são dado declarado.
OPS = {o['id'] for o in catalogos.get('valores_derivados', {}).get('operacoes', [])}


def checar_ops(ctx, obj):
    if isinstance(obj, dict):
        # a comparação de condição também usa a chave 'op', mas do vocabulário de
        # comparação (fase 13), não do catálogo de operações de fórmula
        if 'comparar' in obj:
            for k, v in obj.items():
                if k != 'op':
                    checar_ops(f"{ctx}/{k}", v)
            return
        op = obj.get('op')
        if isinstance(op, str) and OPS and op not in OPS:
            erros.append(f"[operação desconhecida] {ctx}: '{op}' não está em "
                         "valores_derivados.operacoes")
        for k, v in obj.items():
            checar_ops(f"{ctx}/{k}", v)
    elif isinstance(obj, list):
        for n, v in enumerate(obj):
            checar_ops(f"{ctx}[{n}]", v)


for cid, c in list(catalogos.items()) + list(colecoes.items()):
    for i in c['itens']:
        checar_ops(f"{cid}/{i['id']}", i)

# ------------------------------------------- PV temporários: sempre com quantidade
for ctx, e in EFEITOS_VISTOS:
    if e.get('tipo') != 'pontos_de_vida_temporarios':
        continue
    if not (e.get('formula') or e.get('total') or e.get('modo')):
        erros.append(f"[PV temporários sem quantidade] {ctx}: precisa de 'formula', "
                     "'total' ou 'modo'")

# ------------------------------------------- bloco de PV das magias
CHAVES_MAXIMOS = {'aumento', 'reducao', 'impede_reducao', 'remove_reducao',
                  'da_criatura_criada'}
for i in catalogos.get('magias', {}).get('itens', []):
    pv = i.get('pontos_de_vida')
    if not pv:
        continue
    ctx = f"magias/{i['id']}/pontos_de_vida"
    t = pv.get('temporarios')
    if t is not None and not (t.get('formula') or t.get('total')):
        erros.append(f"[PV temporários sem quantidade] {ctx}: 'temporarios' precisa de "
                     "'formula' ou 'total'")
    mx = pv.get('maximos')
    if mx is not None and not (set(mx) & CHAVES_MAXIMOS):
        erros.append(f"[efeito sobre o máximo sem operação] {ctx}: 'maximos' precisa de "
                     f"um de {sorted(CHAVES_MAXIMOS)}")

# ----------------------------------------------- talentos: categoria e pré-requisito
CATEGORIAS_DE_TALENTO = {'origem', 'geral', 'estilo_de_luta', 'epico'}
TIPOS_DE_PRE_REQUISITO = {'nivel_de_personagem', 'valor_de_atributo', 'caracteristica',
                          'treinamento_com_armadura', 'talento', 'classe'}
for i in catalogos.get('talentos', {}).get('itens', []):
    ctx = f"talentos/{i['id']}"
    if i.get('categoria') not in CATEGORIAS_DE_TALENTO:
        erros.append(f"[categoria de talento inválida] {ctx}: '{i.get('categoria')}' "
                     f"(esperado um de {sorted(CATEGORIAS_DE_TALENTO)})")
    if 'pre_requisitos' not in i:
        erros.append(f"[talento sem pré-requisitos declarados] {ctx}: use uma lista "
                     "vazia quando não houver — silêncio não é o mesmo que 'nenhum'")
    for pr in (i.get('pre_requisitos') or []):
        t_pr = pr.get('tipo')
        if t_pr not in TIPOS_DE_PRE_REQUISITO:
            erros.append(f"[pré-requisito desconhecido] {ctx}: '{t_pr}'")
        elif t_pr == 'valor_de_atributo':
            for a in (pr.get('atributos') or []):
                if a not in ATRIBUTOS:
                    erros.append(f"[atributo inexistente] {ctx}: pré-requisito '{a}'")
            if not isinstance(pr.get('minimo'), int):
                erros.append(f"[pré-requisito sem mínimo] {ctx}: 'valor_de_atributo' "
                             "precisa de 'minimo' inteiro")
        elif t_pr == 'nivel_de_personagem' and not isinstance(pr.get('minimo'), int):
            erros.append(f"[pré-requisito sem nível] {ctx}: 'nivel_de_personagem' "
                         "precisa de 'minimo' inteiro")
        elif t_pr == 'talento' and pr.get('chave') not in CHAVES.get('talentos', set()):
            erros.append(f"[talento inexistente] {ctx}: pré-requisito "
                         f"'{pr.get('chave')}'")
    # Talento das categorias Geral e Épica exige nível: o livro nunca dá um sem isso.
    if i.get('categoria') in ('geral', 'epico'):
        if not any(pr.get('tipo') == 'nivel_de_personagem'
                   for pr in (i.get('pre_requisitos') or [])):
            erros.append(f"[talento sem nível mínimo] {ctx}: talento {i['categoria']} "
                         "precisa declarar o pré-requisito de nível (4 nos Gerais, "
                         "19 nas Dádivas Épicas)")

# ---------------------------------- aumento de atributo dentro de talento tem teto
for ctx, e in EFEITOS_VISTOS:
    if e.get('tipo') != 'aumento_atributo':
        continue
    if 'limite' not in e:
        erros.append(f"[aumento de atributo sem teto] {ctx}: o livro sempre dá um teto "
                     "(20 nos talentos Gerais, 30 nas Dádivas Épicas)")
    at = e.get('atributo')
    if isinstance(at, str) and at != PLACEHOLDER and at not in ATRIBUTOS:
        erros.append(f"[atributo inexistente] {ctx}: '{at}'")

# ---------------------------------------- alterar_custo_de_acao aponta ação real
for ctx, e in EFEITOS_VISTOS:
    if e.get('tipo') != 'alterar_custo_de_acao':
        continue
    if e.get('acao_id') not in CHAVES.get('acoes', set()):
        erros.append(f"[ação inexistente] {ctx}: '{e.get('acao_id')}'")
    if e.get('novo_custo') not in CHAVES.get('custos_de_acao', set()):
        erros.append(f"[custo de ação inexistente] {ctx}: '{e.get('novo_custo')}'")

# ------------------------------------- ignorar_cobertura só usa graus declarados
for ctx, e in EFEITOS_VISTOS:
    if e.get('tipo') != 'ignorar_cobertura':
        continue
    for g in (e.get('graus') or []):
        if g not in CHAVES.get('graus_de_cobertura', set()):
            erros.append(f"[grau de cobertura inexistente] {ctx}: '{g}'")

# --------------------------------- ignorar_resistencia nomeia tipos de dano reais
for ctx, e in EFEITOS_VISTOS:
    if e.get('tipo') != 'ignorar_resistencia':
        continue
    tipos = e.get('tipos_de_dano') or ([e['tipo_dano']] if e.get('tipo_dano') else [])
    if not tipos:
        erros.append(f"[ignorar_resistencia sem tipo] {ctx}")
    for d in tipos:
        if d not in DANOS and d != PLACEHOLDER:
            erros.append(f"[tipo de dano inexistente] {ctx}: '{d}'")

# ------------------------------- pré-requisito de item/ferramenta tem de resolver
# O Golpe Astuto "Envenenar" exigia o Kit de Veneno e ficou anos com `revisao: duvida`
# e a nota "id depende do cap. 6" — o capítulo entrou e ninguém voltou para conferir.
# Agora a chave é cobrada, então dúvida assim não sobrevive calada.
CAT_DE_PRE_REQUISITO = {'item': 'itens', 'ferramenta': 'ferramentas'}
for cid, c in list(catalogos.items()) + list(colecoes.items()):
    for i in c['itens']:
        def checar_pre(obj, ctx):
            if isinstance(obj, dict):
                for pr in (obj.get('pre_requisitos') or []):
                    if not isinstance(pr, dict):
                        continue
                    destino = CAT_DE_PRE_REQUISITO.get(pr.get('tipo'))
                    if destino and pr.get('chave') not in CHAVES.get(destino, set()):
                        erros.append(f"[pré-requisito inexistente] {ctx}: "
                                     f"'{pr.get('chave')}' não está em '{destino}'")
                for k, v in obj.items():
                    checar_pre(v, f"{ctx}/{k}")
            elif isinstance(obj, list):
                for n, v in enumerate(obj):
                    checar_pre(v, f"{ctx}[{n}]")
        checar_pre(i, f"{cid}/{i['id']}")

# ----------------------------------------- variante declarada tem de existir no item
for ctx, e in EFEITOS_VISTOS:
    var = e.get('variante')
    if not isinstance(var, str) or var == PLACEHOLDER:
        continue
    chave = e.get('chave')
    alvo = next((i for i in catalogos.get('ferramentas', {}).get('itens', [])
                 if i['id'] == chave), None)
    if alvo is None:
        continue
    ids = {v['id'] if isinstance(v, dict) else v for v in (alvo.get('variantes') or [])}
    if var not in ids:
        erros.append(f"[variante inexistente] {ctx}: '{var}' não é variante de "
                     f"'{chave}'")

# ------------------------------------------- bloco de estatísticas: coerência interna
# O próprio bloco traz números que se conferem entre si: a Iniciativa passiva é
# 10 + o bônus, e o modificador é derivado do valor do atributo. Foi essa segunda
# conta que pegou quatro divergências do Apêndice B na extração.
PERICIAS_VALIDAS = CHAVES.get('pericias', set())
for cid in CATALOGOS_DE_BLOCO_DE_ESTATISTICAS:
    c = catalogos.get(cid)
    if not c:
        continue
    for i in c['itens']:
        ctx = f"{cid}/{i['id']}"
        ini = i.get('iniciativa')
        if isinstance(ini, dict) and 'bonus' in ini and 'passiva' in ini:
            if ini['passiva'] != 10 + ini['bonus']:
                erros.append(f"[iniciativa incoerente] {ctx}: passiva {ini['passiva']} "
                             f"não é 10 + bônus {ini['bonus']:+d}")
        for a_, valor in (i.get('atributos') or {}).items():
            esperado = (valor - 10) // 2
            if a_ in (i.get('modificadores') or {}) and i['modificadores'][a_] != esperado:
                erros.append(f"[modificador incoerente] {ctx}/{a_}: valor {valor} dá "
                             f"{esperado:+d}, mas o dado diz "
                             f"{i['modificadores'][a_]:+d}")
        for p_ in (i.get('pericias') or []):
            # feras_companheiras lista perícia como string; criaturas, como
            # {pericia, bonus}. As duas formas valem — o que se cobra é a chave.
            chave_p = p_.get('pericia') if isinstance(p_, dict) else p_
            if chave_p not in PERICIAS_VALIDAS:
                erros.append(f"[perícia inexistente] {ctx}: '{chave_p}'")
        for campo in ('resistencias_a_dano', 'imunidades_a_dano',
                      'vulnerabilidades_a_dano'):
            for d_ in (i.get(campo) or []):
                if d_ not in DANOS:
                    erros.append(f"[tipo de dano inexistente] {ctx}/{campo}: '{d_}'")
        for campo in ('resistencias_a_condicao', 'imunidades_a_condicao',
                      'vulnerabilidades_a_condicao'):
            for d_ in (i.get(campo) or []):
                if d_ not in CONDICOES:
                    erros.append(f"[condição inexistente] {ctx}/{campo}: '{d_}'")
        nd = i.get('nivel_de_desafio')
        if nd is not None:
            for campo in ('texto', 'xp', 'bonus_de_proficiencia'):
                if campo not in nd:
                    erros.append(f"[nível de desafio incompleto] {ctx}: falta '{campo}'")
        for secao in ('tracos', 'acoes', 'acoes_bonus', 'reacoes'):
            for e_ in (i.get(secao) or []):
                sub = f"{ctx}/{secao}/{e_.get('id')}"
                if not e_.get('descricao_curta'):
                    erros.append(f"[entrada sem descrição] {sub}")
                if 'tipo_de_ataque' in e_:
                    if 'bonus_de_ataque' not in e_:
                        erros.append(f"[ataque sem bônus] {sub}")
                    if not e_.get('dano'):
                        erros.append(f"[ataque sem dano] {sub}")
                    # 'dano' é lista de parcelas em criaturas e objeto único em
                    # feras_companheiras; as duas formas passam pela mesma checagem
                    dano = e_.get('dano')
                    for d_ in (dano if isinstance(dano, list) else [dano]):
                        if not isinstance(d_, dict):
                            continue
                        tipos = (d_.get('tipos_de_dano')
                                 or ([d_['tipo_dano']] if d_.get('tipo_dano') else []))
                        for td in tipos:
                            if td not in DANOS and td not in DANOS_DERIVADOS:
                                erros.append(f"[tipo de dano inexistente] {sub}: '{td}'")

# ---------------------------- assumir bloco de estatísticas aponta para bloco real
for ctx, e in EFEITOS_VISTOS:
    if e.get('tipo') != 'assumir_bloco_de_estatisticas':
        continue
    cat = e.get('catalogo')
    if cat not in CATALOGOS_DE_BLOCO_DE_ESTATISTICAS:
        erros.append(f"[catálogo não é de blocos de estatísticas] {ctx}: '{cat}'")
    elif (isinstance(e.get('criatura'), str) and e['criatura'] != PLACEHOLDER
          and e['criatura'] not in CHAVES.get(cat, set())):
        erros.append(f"[criatura inexistente] {ctx}: '{e['criatura']}'")


# --------------------------------- vocabulário de runtime: lista fechada (fase 13)
# Os tipos de efeito sempre foram catálogo validado; o que aparece DENTRO deles
# não era. Sem esta checagem, `entrar_em_furia` e `ao_entrar_em_furia` convivem
# calados, e no motor um dos dois nunca dispara.
if not VOCAB:
    erros.append("[vocabulário de runtime ausente] falta dados/vocabulario_de_runtime.json")
else:
    V_PRED = set(VOCAB['predicados'])
    V_FAM = VOCAB['familias_de_predicado']
    V_GAT = set(VOCAB['gatilhos'])
    V_FASE = set(VOCAB['fases'])
    V_DUR = set(VOCAB['duracoes'])
    V_CUSTO = set(VOCAB['custos'])
    V_EMP = set(VOCAB['empilhamentos'])
    V_UNI = set(VOCAB['unidades_de_duracao'])
    V_LOG = set(VOCAB['operadores_logicos'])
    V_CMP = set(VOCAB['operadores_de_comparacao'])

    def checar_predicado(ctx, o):
        if isinstance(o, str):
            if o in V_PRED:
                return
            prefixo, _, arg = o.partition(':')
            if prefixo in V_FAM:
                cat = V_FAM[prefixo]
                if cat and arg not in CHAVES.get(cat, set()):
                    erros.append(f"[argumento de predicado inexistente] {ctx}: "
                                 f"'{o}' (esperado id de {cat})")
                return
            erros.append(f"[predicado não declarado] {ctx}: '{o}'")
        elif isinstance(o, list):
            for x in o:
                checar_predicado(ctx, x)
        elif isinstance(o, dict):
            if 'comparar' in o:
                if o.get('op') not in V_CMP:
                    erros.append(f"[operador de comparação desconhecido] {ctx}: "
                                 f"'{o.get('op')}'")
                if 'com' not in o:
                    erros.append(f"[comparação sem lado direito] {ctx}")
                return
            for k, v in o.items():
                if k not in V_LOG:
                    erros.append(f"[operador lógico desconhecido] {ctx}: '{k}'")
                    continue
                checar_predicado(ctx, v)

    def checar_vocabulario(ctx, obj):
        if isinstance(obj, list):
            for x in obj:
                checar_vocabulario(ctx, x)
            return
        if not isinstance(obj, dict):
            return
        ctx = obj.get('id') and f"{ctx}/{obj['id']}" or ctx
        for campo in ('condicao', 'condicional', 'condicao_do_alvo'):
            if campo in obj:
                checar_predicado(ctx, obj[campo])
        if 'momento' in obj:
            erros.append(f"[campo 'momento' revogado] {ctx}: use 'gatilho' ou 'fase'")
        g = obj.get('gatilho')
        if isinstance(g, str) and g not in V_GAT:
            erros.append(f"[gatilho não declarado] {ctx}: '{g}'")
        f_ = obj.get('fase')
        if isinstance(f_, str) and f_ not in V_FASE:
            erros.append(f"[fase não declarada] {ctx}: '{f_}'")
        for campo in ('duracao', 'duracao_do_efeito'):
            d_ = obj.get(campo)
            if isinstance(d_, str) and d_ not in V_DUR:
                erros.append(f"[duração não declarada] {ctx}: '{d_}'")
            elif isinstance(d_, dict) and 'quantidade' in d_:
                if d_.get('unidade') not in V_UNI:
                    erros.append(f"[unidade de duração desconhecida] {ctx}: "
                                 f"'{d_.get('unidade')}'")
        c_ = obj.get('custo')
        if isinstance(c_, str) and c_ not in V_CUSTO:
            erros.append(f"[custo não declarado] {ctx}: '{c_}'")
        e_ = obj.get('empilha')
        if isinstance(e_, str) and e_ not in V_EMP:
            erros.append(f"[modo de empilhamento não declarado] {ctx}: '{e_}'")
        for v in obj.values():
            checar_vocabulario(ctx, v)

    for _cid, _c in list(catalogos.items()) + list(colecoes.items()):
        checar_vocabulario(_cid, _c)


# ------------------------- efeito aninhado: condição ou estrutura (fase 15)
# Um efeito pode trazer outros dentro. O que isso significa não pode ser adivinhado
# pelo formato — foi assim que os 56 `melhorar_caracteristica` viraram condição e
# ficaram desligados por padrão. O tipo declara; aqui se cobra a declaração.
ANINHADOS = {i['id']: i.get('efeitos_aninhados')
             for i in catalogos.get('tipos_de_efeito', {}).get('itens', [])}
PORTAS_VISTAS = {}


def checar_aninhados(ctx, obj):
    if isinstance(obj, list):
        for n, x in enumerate(obj):
            checar_aninhados(f"{ctx}[{n}]", x)
        return
    if not isinstance(obj, dict):
        return
    tipo = obj.get('tipo')
    if tipo == 'escolha' and not obj.get('id'):
        # sem id a escolha não pode ser resolvida (a construção guarda a resposta
        # POR id) nem entrar no checklist de subir de nível
        erros.append(f"[escolha sem id] {ctx}: '{obj.get('rotulo')}'")
    if tipo and isinstance(obj.get('efeitos'), list):
        modo = ANINHADOS.get(tipo)
        if modo is None:
            erros.append(f"[aninhamento não declarado] {ctx}: o tipo '{tipo}' traz "
                         "efeitos dentro e não diz em tipos_de_efeito.json se eles são "
                         "'condicionados' ou 'estruturais'")
        elif modo not in ('condicionados', 'estruturais'):
            erros.append(f"[aninhamento com valor inválido] {ctx}: '{tipo}' declara "
                         f"efeitos_aninhados='{modo}'")
        elif modo == 'condicionados':
            # o id é o nome da condição; sem ele o motor não tem como ligá-la nem
            # distinguir uma da outra
            eid = obj.get('id')
            if not eid:
                erros.append(f"[efeito condicionante sem id] {ctx}: '{tipo}' condiciona "
                             "o que traz dentro, então precisa de 'id' para nomear a "
                             "condição")
            elif eid in PORTAS_VISTAS and PORTAS_VISTAS[eid] != ctx:
                erros.append(f"[duas condições com o mesmo id] '{eid}': "
                             f"{PORTAS_VISTAS[eid]} e {ctx} — abrir uma abriria a outra")
            elif eid:
                PORTAS_VISTAS[eid] = ctx
    for k, v in obj.items():
        checar_aninhados(f"{ctx}/{k}", v)


for cid, c in list(catalogos.items()) + list(colecoes.items()):
    for i in c['itens']:
        checar_aninhados(f"{cid}/{i['id']}", i)


# --------------------------- escolha tem de ter o que escolher (fase 16)
# Regra que teria pego sozinha os quatro antecedentes que ofereciam "Escolha um tipo
# de Kit de Jogos" com UMA opção: a categoria, em vez das quatro variantes dela.
# O validador já cobrava "o filtro devolve algo"; devolvia — devolvia a categoria.
def contar_opcoes(e):
    """Quantas opções a escolha oferece, ou None quando o validador não sabe."""
    de = e.get('de') or {}
    cat = de.get('catalogo')
    if not cat:
        return None
    fonte = catalogos.get(cat, colecoes.get(cat, {}))
    itens = fonte.get('itens', [])
    if not itens:
        return None                     # catálogo pendente: já tem checagem própria
    if de.get('de_variantes'):
        alvo = (de.get('filtro') or {}).get('id')
        escolhidos = [i for i in itens if i['id'] == alvo] if alvo else itens
        return sum(len(i.get('variantes') or []) for i in escolhidos) or None
    if isinstance(de.get('chaves'), list):
        return len(de['chaves'])
    if de.get('todo_o_catalogo'):
        return len(itens)
    if de.get('filtro'):
        n, motivo = resolver_filtro(cat, de['filtro'])
        return n if motivo == 'ok' else None
    return None


def checar_tem_o_que_escolher(ctx, obj):
    if isinstance(obj, list):
        for n, x in enumerate(obj):
            checar_tem_o_que_escolher(f"{ctx}[{n}]", x)
        return
    if not isinstance(obj, dict):
        return
    if obj.get('tipo') == 'escolha':
        q = obj.get('quantidade')
        n = contar_opcoes(obj)
        if isinstance(q, int) and n is not None:
            if n < q:
                erros.append(f"[escolha impossível] {ctx}/{obj.get('id')}: pede {q} e "
                             f"oferece {n}")
            elif n == q and not obj.get('reescolhivel'):
                # reescolhível com uma opção hoje pode ter mais adiante — a
                # Inspiração de Bardo ganha usos novos por melhoria de característica
                avisos.append(f"[escolha sem escolha] {ctx}/{obj.get('id')}: pede {q} e "
                              f"oferece exatamente {n} — confira se não é uma "
                              f"categoria no lugar das variantes dela")
    for v in obj.values():
        checar_tem_o_que_escolher(ctx, v)


for cid, c in list(catalogos.items()) + list(colecoes.items()):
    for i in c['itens']:
        checar_tem_o_que_escolher(f"{cid}/{i['id']}", i)


# ------------------- subclasse: o nível de cada característica é dela (fase 17)
# `niveis_de_caracteristica` é o RESUMO de em que níveis a subclasse dá algo — não o
# mapa de qual característica chega quando. Em 42 das 48 subclasses há mais
# características que níveis, e o motor que casasse os dois por posição erraria (o
# primeiro coletor errou). O nível de verdade está na própria característica; esta
# checagem tranca a invariante de que o resumo não mente.
CARS_POR_ID = {i['id']: i for i in colecoes.get('caracteristicas', {}).get('itens', [])}

for s_ in colecoes.get('subclasses', {}).get('itens', []):
    ctx = f"subclasses/{s_['id']}"
    niveis_reais = set()
    for idc in (s_.get('caracteristicas') or []):
        car = CARS_POR_ID.get(idc)
        if car is None:
            erros.append(f"[característica inexistente] {ctx}: '{idc}'")
            continue
        if not isinstance(car.get('nivel'), int):
            erros.append(f"[característica de subclasse sem nível] {ctx}/{idc}: sem ela o "
                         "motor não sabe quando a característica chega")
            continue
        niveis_reais.add(car['nivel'])
        if car.get('subclasse') and car['subclasse'] != s_['id']:
            erros.append(f"[característica de outra subclasse] {ctx}/{idc}: declara "
                         f"subclasse '{car['subclasse']}'")
    declarados = set(s_.get('niveis_de_caracteristica') or [])
    if niveis_reais and declarados != niveis_reais:
        erros.append(f"[resumo de níveis não bate] {ctx}: declara "
                     f"{sorted(declarados)} e as características dizem {sorted(niveis_reais)}")

# ------------------------------------------------------------------ saída
erros = list(dict.fromkeys(erros))
avisos = list(dict.fromkeys(avisos))
print(f"catálogos: {len(catalogos)}  coleções: {len(colecoes)}")
for cid in sorted(CHAVES):
    print(f"  {cid:28s} {len(CHAVES[cid]):3d} itens")
print()
for a in avisos:
    print("AVISO ", a)
for e in erros:
    print("ERRO  ", e)
print()
print("RESULTADO:", "FALHOU" if erros else "OK", f"({len(erros)} erros, {len(avisos)} avisos)")
sys.exit(1 if erros else 0)
