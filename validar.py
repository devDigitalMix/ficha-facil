# -*- coding: utf-8 -*-
"""Validador do dataset Ficha Fácil.

Regras (esquema v1, §4.3). Sai com código 1 se qualquer regra falhar.
Uso: python3 validar.py [pasta_dados]
"""
import json, os, sys, re

BASE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
erros, avisos = [], []


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
for nome in sorted(os.listdir(BASE)):
    if nome.endswith('.json'):
        d = carregar(os.path.join(BASE, nome))
        colecoes[d['colecao']] = d

CHAVES = {cid: {i['id'] for i in c['itens']} for cid, c in catalogos.items()}
for cid, c in colecoes.items():
    CHAVES[cid] = {i['id'] for i in c['itens']}

TIPOS_EFEITO = CHAVES['tipos_de_efeito']
ATRIBUTOS = CHAVES['atributos']
PERICIAS = CHAVES['pericias']
ALVOS = CHAVES['alvos']
ALVOS_IMP = CHAVES['alvos_de_impedimento']
DANOS = CHAVES['tipos_de_dano'] | {'todos'}
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
                  'categoria', 'grupo', 'classe'}
    if not any(k in conhecidas for k in filtro):
        return (1, 'nao_avaliavel')
    lista_alvo = filtro.get('lista')
    if isinstance(lista_alvo, str) and lista_alvo.startswith('$'):
        return (1, 'variavel')
    if lista_alvo and lista_alvo in LISTAS_DECLARADAS and lista_alvo not in LISTAS_PREENCHIDAS:
        return (0, 'lista_nao_preenchida')
    n = 0
    for it in itens:
        ok = True
        for k, v in filtro.items():
            if k not in conhecidas or (isinstance(v, str) and v.startswith('$')):
                continue
            if k == 'nivel' and it.get('nivel') != v: ok = False
            elif k == 'nivel_minimo' and (it.get('nivel') is None or it['nivel'] < v): ok = False
            elif k == 'nivel_maximo' and (it.get('nivel') is None or it['nivel'] > v): ok = False
            elif k == 'lista' and v not in (it.get('listas') or []): ok = False
            elif k == 'escola' and it.get('escola') != v: ok = False
            elif k == 'categoria' and it.get('categoria') != v: ok = False
            elif k == 'classe' and it.get('classe') != v: ok = False
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
    if t in ('modificador', 'vantagem') and isinstance(e.get('alvo'), str):
        checar_alvo(ctx, e['alvo'])
    if t == 'impedir' and e.get('alvo') not in ALVOS_IMP:
        erros.append(f"[alvo de impedimento inexistente] {ctx}: '{e.get('alvo')}'")
    if t == 'falha_automatica' and 'alvo' in e:
        checar_alvo(ctx, e['alvo'])
    if t == 'alterar_dano':
        # ou o tipo é literal, ou é derivado de uma escolha — e aí todo valor do mapa vale
        if 'tipo_dano_derivado' in e:
            mapa = (e['tipo_dano_derivado'] or {}).get('mapa') or {}
            if not mapa:
                erros.append(f"[tipo_dano_derivado sem mapa] {ctx}")
            for chave, dano in mapa.items():
                if dano not in DANOS:
                    erros.append(f"[tipo de dano inexistente] {ctx}: mapa['{chave}'] = '{dano}'")
        elif e.get('tipo_dano') not in DANOS:
            erros.append(f"[tipo de dano inexistente] {ctx}: '{e.get('tipo_dano')}'")
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
                if isinstance(q, int) and q > len(de['chaves']):
                    erros.append(f"[quantidade > opções] {ctx}: {e.get('quantidade')} de {len(de['chaves'])}")
            elif 'filtro' not in de and not de.get('todo_o_catalogo'):
                erros.append(f"[escolha sem chaves, filtro ou todo_o_catalogo] {ctx}")
            elif (de.get('todo_o_catalogo') and isinstance(e.get('quantidade'), int)
                  and e['quantidade'] > len(CHAVES[cat])):
                erros.append(f"[quantidade > opções] {ctx}: {e.get('quantidade')} de {len(CHAVES[cat])} em '{cat}'")
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


def varrer(ctx, obj):
    if isinstance(obj, dict):
        if 'tipo' in obj and isinstance(obj.get('tipo'), str) and obj['tipo'] in TIPOS_EFEITO:
            checar_efeito(ctx, obj)
        for k, v in obj.items():
            if k == 'efeito_por_item_escolhido':
                continue  # já validado pelo bloco 'escolha' da mãe
            varrer(f"{ctx}/{k}", v)
    elif isinstance(obj, list):
        for n, v in enumerate(obj):
            varrer(f"{ctx}[{n}]", v)


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
    for s_ in cl.get('salvaguardas_primarias', []) + cl.get('atributo_primario', []):
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
