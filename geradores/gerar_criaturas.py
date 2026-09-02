# -*- coding: utf-8 -*-
"""Apêndice B — 51 blocos de estatísticas de criaturas (p. 346-359).

O catálogo `criaturas` existia vazio desde a fase 0, com `preenchida: false`, e a
Forma Selvagem do Druida já apontava para ele por FILTRO — exatamente para que o
seletor passasse a funcionar quando o apêndice fosse extraído, sem reeditar o
Druida. É o que acontece aqui.

Três decisões deste lote:

1. **Parser, não digitação.** 51 blocos × ~15 campos é onde erro de digitação se
   esconde. Os números saem de `parse_criaturas.py`; as frases são paráfrase à mão
   em `descricoes_criaturas.py`, e o gerador **falha** se faltar alguma — o mesmo
   guarda-corpo das magias.

2. **Ataque puro não tem paráfrase.** Quando a ação é só jogada + alcance + dano, a
   descrição é DERIVADA do próprio dado estruturado e marcada `descricao_derivada`,
   como já se faz com equipamento. Escrever à mão o que a máquina deduz é convite a
   divergência.

3. **Efeito onde é efeito.** Traços que são regra mecânica de verdade viram efeito
   executável (Táticas de Grupo é `vantagem` com condição; Animal de Carga é
   `modificador` em `capacidade_de_carga`). O resto fica `efeito_narrativo`, marcado
   — não escondido.
"""
import json, os, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos
from parse_criaturas import parse
from descricoes_criaturas import buscar

SAIDA = os.path.join(caminhos.CATALOGOS, 'criaturas.json')
TIPOS_DE_EFEITO = os.path.join(caminhos.CATALOGOS, 'tipos_de_efeito.json')

# Assumir a ficha de outra criatura não é 'forma_selvagem' (que é o recurso do
# Druida) nem 'efeito_narrativo': é carregar um bloco de estatísticas do catálogo.
# A Forma Selvagem passa a usar isto agora que há blocos para carregar.
TIPO_NOVO = collections.OrderedDict([
    ("id", "assumir_bloco_de_estatisticas"),
    ("nome", "Assumir o bloco de estatísticas de uma criatura"),
    ("descricao_curta",
     "Troca as estatísticas do personagem pelas de um bloco do catálogo indicado. "
     "Quais estatísticas são mantidas é regra de quem concede — a Forma Selvagem "
     "declara isso em `regras_enquanto_multimorfado`."),
])


def fonte(pagina):
    return {"capitulo": "ap_b", "pagina_livro": pagina, "pagina_pdf": pagina + 4}


def modificador(valor):
    """A conta é a mesma de qualquer ficha (valores_derivados/modificador_de_atributo)."""
    return (valor - 10) // 2


def resolver_atributos(c, divergencias):
    """O livro imprime VALOR, MOD e SG por atributo. Em quatro casos o MOD impresso
    não corresponde ao valor, e há DOIS fenômenos diferentes:

    · Alce (Car 6: "–4 –2") e Camelo (Des 8: "–4 –1") — o MOD diverge mas o SG bate
      com a conta. Cheira a ruído da extração de coluna do PDF, e o próprio bloco
      se corrige.
    · Cabra (Int 2: "–5 –5") e Cavalo Marinho Gigante (For 16: "+2 +2") — MOD e SG
      concordam entre si e discordam do valor. Aí é o livro sendo inconsistente
      consigo mesmo.

    Nos dois casos a saída é a mesma: o VALOR do atributo é dado primário e o
    modificador é DERIVADO dele pela regra universal (valores_derivados/
    modificador_de_atributo). O modificador é recalculado, o impresso é preservado
    e a divergência fica registrada com a página.

    A proficiência em salvaguarda sai da distância entre o SG impresso e o
    modificador CORRETO: 0 é não proficiente, o Bônus de Proficiência é proficiente.
    Qualquer outro valor não é adivinhado — vira divergência declarada.
    """
    mods, salv, prof = {}, {}, []
    bp = c['nivel_de_desafio']['bonus_de_proficiencia']
    for a, valor in c['atributos'].items():
        certo = modificador(valor)
        mod_impresso = c['modificadores_impressos'][a]
        sg_impresso = c['salvaguardas_impressas'][a]
        mods[a] = certo
        if mod_impresso != certo:
            divergencias.append({
                "criatura": c['id'], "atributo": a, "valor": valor,
                "campo": "modificador",
                "impresso": mod_impresso, "calculado": certo,
                "sg_impresso": sg_impresso,
                "pagina_livro": c['pagina_livro'],
                "tipo": ("sg_confirma_a_conta" if sg_impresso == certo
                         else "livro_inconsistente_consigo"),
                "nota": ("O modificador impresso não corresponde ao valor do atributo. "
                         "Vale a conta; o impresso fica em `modificadores_impressos`.")})
        delta = sg_impresso - certo
        if delta == bp:
            prof.append(a)
            salv[a] = certo + bp
        elif delta == 0:
            salv[a] = certo
        else:
            salv[a] = sg_impresso
            divergencias.append({
                "criatura": c['id'], "atributo": a, "valor": valor,
                "campo": "salvaguarda",
                "impresso": sg_impresso, "calculado": certo,
                "pagina_livro": c['pagina_livro'],
                "tipo": "sg_nao_e_mod_nem_mod_mais_bp",
                "nota": ("A salvaguarda impressa não é nem o modificador nem o "
                         "modificador mais o Bônus de Proficiência. Mantida como "
                         "impressa, sem inventar proficiência.")})
    return mods, salv, sorted(prof)


# Traços cuja mecânica cabe num efeito de verdade. O resto é narrativo e fica
# marcado como tal — a regra do projeto é não fingir que texto é motor.
EFEITOS_DE_TRACO = {
    'agil': [{"tipo": "impedir",
              "alvo": "ataque_de_oportunidade_provocado_por_voce"}],
    'sobrevoo': [{"tipo": "impedir",
                  "alvo": "ataque_de_oportunidade_provocado_por_voce",
                  "condicao": {"todas": ["voando"]}}],
    'resistencia_a_magia': [{"tipo": "vantagem", "alvo": "salvaguarda",
                             "modo": "vantagem",
                             "condicao": {"todas": ["origem:magia"]}}],
    'taticas_de_grupo': [{"tipo": "vantagem", "alvo": "jogada_de_ataque",
                          "modo": "vantagem",
                          "condicao": {"todas": [
                              "aliado_a_ate_1_5m_do_alvo",
                              {"nao": "aliado_com_condicao:incapacitado"}]}}],
    'furia_sangrenta': [{"tipo": "vantagem", "alvo": "jogada_de_ataque",
                         "modo": "vantagem",
                         "condicao": {"todas": ["estado:sangrando"]}}],
    'animal_de_carga': [{"tipo": "modificador", "alvo": "capacidade_de_carga",
                         "valor": ["um_tamanho_acima"], "empilha": "substitui"}],
    'saltador': [{"tipo": "substituir_atributo", "de": "FOR", "para": "DES",
                  "escopo": ["distancia_de_salto"]}],
    'respirar_na_agua': [{"tipo": "efeito_narrativo", "chave": "so_respira_na_agua",
                          "texto": "Só respira debaixo d'água."}],
    'anfibio': [{"tipo": "efeito_narrativo", "chave": "respira_ar_e_agua",
                 "texto": "Respira ar e água."}],
}


def descricao_de_ataque(e):
    """A frase sai do dado: '+5 para acertar, alcance 1,5 m, 1d6 + 3 Contundente'."""
    partes = [f"{'+' if e['bonus_de_ataque'] >= 0 else ''}{e['bonus_de_ataque']} "
              f"para acertar"]
    alc = f"{e['alcance_m']:g} m".replace('.', ',')
    if e.get('alcance_maximo_m'):
        alc = f"{e['alcance_m']:g}/{e['alcance_maximo_m']:g} m".replace('.', ',')
    partes.append(("alcance " if e['tipo_de_ataque'] == 'corpo_a_corpo'
                   else "distância ") + alc)
    for d in (e.get('dano') or []):
        formula = d['formula_dado'] or str(d['media'])
        partes.append(f"{formula} {d['tipo_dano']}")
    tipo = ("Ataque corpo a corpo" if e['tipo_de_ataque'] == 'corpo_a_corpo'
            else "Ataque à distância")
    return f"{tipo}: " + ", ".join(partes) + "."


def montar_entrada(criatura, entrada, secao, faltando):
    d = collections.OrderedDict([("id", entrada['id']), ("nome", entrada['nome'])])
    for campo in ('tipo_de_ataque', 'bonus_de_ataque', 'alcance_m',
                  'alcance_maximo_m', 'dano'):
        if campo in entrada:
            d[campo] = entrada[campo]

    frase = buscar(criatura['id'], entrada['id'])
    if frase:
        if 'tipo_de_ataque' in d:
            # ataque COM regra extra: a descrição derivada carrega os números e a
            # paráfrase carrega a regra que sobra
            d["descricao_curta"] = descricao_de_ataque(d) + " " + frase
        else:
            d["descricao_curta"] = frase
    elif 'tipo_de_ataque' in d:
        d["descricao_curta"] = descricao_de_ataque(d)
        d["descricao_derivada"] = True
    else:
        faltando.append((criatura['id'], secao, entrada['id']))
        return None

    efeitos = EFEITOS_DE_TRACO.get(entrada['id'])
    if efeitos:
        d["efeitos"] = json.loads(json.dumps(efeitos))
    elif 'tipo_de_ataque' not in d:
        d["efeitos"] = [{"tipo": "efeito_narrativo", "chave": entrada['id'],
                         "texto": d["descricao_curta"]}]
    return d


def main():
    criaturas = parse()
    faltando, divergencias = [], []
    itens = []
    for c in criaturas:
        item = collections.OrderedDict([
            ("id", c['id']), ("nome", c['nome']),
            ("fonte", fonte(c['pagina_livro'])),
            ("revisao", {"status": "ok", "notas": ""}),
            ("tipo_de_criatura", c['tipo_de_criatura']),
            ("tamanho", c['tamanho']),
            ("alinhamento", c['alinhamento']),
        ])
        if c.get('subtipo'):
            item["subtipo"] = c['subtipo']
        item["classe_de_armadura"] = {"valor": c['classe_de_armadura']}
        item["iniciativa"] = c['iniciativa']
        item["pontos_de_vida"] = c['pontos_de_vida']
        item["deslocamentos"] = c['deslocamentos']
        item["atributos"] = c['atributos']
        mods, salv, prof = resolver_atributos(c, divergencias)
        item["modificadores"] = mods
        item["salvaguardas"] = salv
        if prof:
            item["proficiente_em_salvaguarda"] = prof
        meus = [d_ for d_ in divergencias if d_['criatura'] == c['id']]
        for div in meus:
            if div['campo'] == 'modificador':
                item.setdefault("modificadores_impressos", {})[div['atributo']] = \
                    div['impresso']
        if meus:
            item["revisao"] = {"status": "ok",
                               "notas": " ".join(sorted({d_['nota'] for d_ in meus}))}
            item["divergencias_do_livro"] = [
                {k: v for k, v in d_.items() if k != 'criatura'} for d_ in meus]
        for campo in ('pericias', 'resistencias_a_dano', 'imunidades_a_dano',
                      'imunidades_a_condicao', 'vulnerabilidades_a_dano',
                      'vulnerabilidades_a_condicao', 'resistencias_a_condicao'):
            if c.get(campo):
                item[campo] = c[campo]
        item["sentidos"] = c.get('sentidos') or []
        item["idiomas_texto"] = c.get('idiomas_texto', '—')
        item["nivel_de_desafio"] = c['nivel_de_desafio']
        for chave, secao in (('tracos', 'tracos'), ('acoes', 'acoes'),
                             ('acoes_bonus', 'acoes_bonus'),
                             ('reacoes', 'reacoes')):
            entradas = []
            for e in (c.get(chave) or []):
                montada = montar_entrada(c, e, secao, faltando)
                if montada:
                    entradas.append(montada)
            if entradas:
                item[chave] = entradas
        itens.append(item)

    if faltando:
        raise SystemExit(
            "FALTA PARÁFRASE em descricoes_criaturas.py para:\n  "
            + "\n  ".join(f"{a} / {b} / {c_}" for a, b, c_ in faltando))

    te = json.load(open(TIPOS_DE_EFEITO, encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    if not any(t['id'] == TIPO_NOVO['id'] for t in te['itens']):
        te['itens'].append(TIPO_NOVO)
        te['total'] = len(te['itens'])
        with open(TIPOS_DE_EFEITO, 'w', encoding='utf-8') as f:
            json.dump(te, f, ensure_ascii=False, indent=2)

    itens.sort(key=lambda x: x['id'])
    catalogo = collections.OrderedDict([
        ("catalogo", "criaturas"),
        ("nome", "Blocos de Estatísticas de Criaturas"),
        ("fonte", fonte(346)),
        ("preenchida", True),
        ("nota", "Apêndice B completo: os 51 blocos que o livro imprime, para as "
                 "criaturas citadas nos capítulos de classe, equipamento e magia. "
                 "Não é bestiário — o Livro dos Monstros fica fora do escopo. Os "
                 "números saem do parser; as frases são paráfrase, e ataque puro tem "
                 "descrição derivada do próprio dado."),
        ("total", len(itens)),
        ("itens", itens),
    ])
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)

    feras = [i for i in itens if i['tipo_de_criatura'] == 'fera']
    print(f"criaturas: {len(itens)} (Feras: {len(feras)})")
    print(f"entradas de traço/ação: "
          f"{sum(len(i.get(k) or []) for i in itens for k in ('tracos','acoes','acoes_bonus','reacoes'))}")
    print(f"com descrição derivada: "
          f"{sum(1 for i in itens for k in ('tracos','acoes','acoes_bonus','reacoes') for e in (i.get(k) or []) if e.get('descricao_derivada'))}")
    nds = collections.Counter(i['nivel_de_desafio']['texto'] for i in itens)
    print("por ND:", dict(sorted(nds.items())))
    for d_ in divergencias:
        print(f"  DIVERGÊNCIA p.{d_['pagina_livro']}: {d_['criatura']} {d_['atributo']} "
              f"{d_['valor']} ({d_['campo']}) — livro {d_['impresso']:+d}, "
              f"conta {d_['calculado']:+d} [{d_['tipo']}]")


if __name__ == '__main__':
    main()
