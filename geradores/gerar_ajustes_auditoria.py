# -*- coding: utf-8 -*-
"""Dívidas fechadas pela auditoria de 2026-09-02 (BACKLOG B3, B5 e B7).

**B5 — fonte nos catálogos de opção.** O princípio 3 do esquema diz que toda entidade
tem `fonte`. Vinte e um catálogos de OPÇÃO tinham a página só no cabeçalho, e os itens
sem nenhuma. Cada item passa a declarar a fonte do próprio catálogo, marcada com
`fonte_herdada: true` — para ficar claro que é a página do bloco, não uma página
conferida item a item. Catálogo de vocabulário (atributos, tamanhos, tipos de dano)
continua sem, de propósito: ali o item é um termo, não uma regra com endereço.

**B7 — dois efeitos narrativos que já eram primitivos disfarçados.**

- `emite_luz` aparecia três vezes (Arma Sagrada, Resplendor Sagrado, Transfiguração
  Radiante), sempre com os mesmos campos estruturados. Virou o tipo `emitir_luz`. Foi a
  mesma promoção que os empurrões tiveram na fase 7 e a Concentração na 10: quando o
  terceiro caso aparece com a mesma forma, é primitivo.
- `maestria_liberada` era pior: o tipo `conceder_maestria_de_arma` **já existia** e era
  usado pelo Guardião e pelo Paladino, enquanto Guerreiro, Bárbaro e Ladino ainda diziam
  a mesma coisa como narrativa. Duas maneiras de dizer o mesmo é o que o esquema existe
  para evitar. Migrados.

**B3 — vocabulário sem uso.** `travar_atributo` (tipo) e `teste_de_atributo_de_outro`
(alvo) estão declarados e nunca foram usados. Não são removidos: vieram do esquema v1 e
descrevem coisa real que ainda não entrou no escopo. Passam a declarar
`reservado_para`, para que "declarado e sem uso" seja estado explícito, e não esquecimento.
"""
import collections, glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos

# Catálogos de vocabulário: item é termo, não regra com endereço no livro.
VOCABULARIO = {
    'alvos', 'alvos_de_impedimento', 'areas_de_efeito', 'atitudes', 'atributos',
    'categorias_de_arma', 'categorias_de_armadura', 'criaturas', 'custos_de_acao',
    'escolas_de_magia', 'estados', 'ferramentas', 'graus_de_cobertura', 'idiomas',
    'itens', 'listas_de_iniciado_em_magia', 'listas_de_magia', 'magias', 'pericias',
    'riscos', 'sentidos', 'tamanhos', 'tipos_de_criatura', 'tipos_de_dano',
    'tipos_de_descanso', 'tipos_de_deslocamento', 'tipos_de_efeito', 'valores_derivados',
    'modos_de_aumento_de_atributo', 'feras_companheiras', 'especies', 'antecedentes',
}

RESERVADOS = {
    'tipos_de_efeito': {
        'travar_atributo': "Itens mágicos que fixam um atributo num valor mínimo (esquema v1 §3). "
                           "Itens mágicos estão fora do escopo atual.",
    },
    'alvos': {
        'teste_de_atributo_de_outro': "Efeitos que alteram o teste de OUTRA criatura, e não o seu. "
                                      "Nenhuma entidade do escopo atual precisa disso.",
    },
}


def carregar(caminho):
    return json.load(open(caminho, encoding='utf-8'),
                     object_pairs_hook=collections.OrderedDict)


def gravar(caminho, d):
    json.dump(d, open(caminho, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def herdar_fontes():
    n_cat = n_itens = 0
    for caminho in sorted(glob.glob(os.path.join(caminhos.CATALOGOS, '*.json'))):
        d = carregar(caminho)
        cid = d.get('catalogo')
        if cid in VOCABULARIO or not d.get('fonte'):
            continue
        tocou = 0
        for i in d['itens']:
            if not i.get('fonte'):
                i['fonte'] = json.loads(json.dumps(d['fonte']))
                i['fonte_herdada'] = True
                tocou += 1
        if tocou:
            gravar(caminho, d)
            n_cat += 1
            n_itens += tocou
    return n_cat, n_itens


def migrar_efeitos():
    """emite_luz -> emitir_luz; maestria_liberada -> conceder_maestria_de_arma."""
    contagem = collections.Counter()

    def visitar(o):
        if isinstance(o, dict):
            if o.get('tipo') == 'efeito_narrativo' and o.get('chave') == 'emite_luz':
                o['tipo'] = 'emitir_luz'
                o.pop('chave', None)
                o.pop('texto', None)
                contagem['emitir_luz'] += 1
            elif (o.get('tipo') == 'efeito_narrativo'
                  and o.get('chave') == 'maestria_liberada'):
                arma = o.pop('arma', None)
                for k in list(o):
                    if k not in ('condicao', 'nota'):
                        o.pop(k)
                o['tipo'] = 'conceder_maestria_de_arma'
                if arma is not None:
                    o['arma'] = arma
                contagem['conceder_maestria_de_arma'] += 1
            for v in o.values():
                visitar(v)
        elif isinstance(o, list):
            for v in o:
                visitar(v)

    for caminho in (sorted(glob.glob(os.path.join(caminhos.DADOS, '*.json')))
                    + sorted(glob.glob(os.path.join(caminhos.CATALOGOS, '*.json')))):
        d = carregar(caminho)
        antes = json.dumps(d, ensure_ascii=False)
        for i in d.get('itens', []):
            visitar(i)
        if json.dumps(d, ensure_ascii=False) != antes:
            gravar(caminho, d)
    return contagem


def declarar_tipo_emitir_luz():
    caminho = os.path.join(caminhos.CATALOGOS, 'tipos_de_efeito.json')
    d = carregar(caminho)
    if any(i['id'] == 'emitir_luz' for i in d['itens']):
        return False
    d['itens'].append(collections.OrderedDict([
        ("id", "emitir_luz"), ("nome", "Emitir luz"),
        ("descricao_curta",
         "A fonte passa a emitir Luz Plena num raio, e opcionalmente Meia-luz por mais um "
         "trecho; `luz_solar` marca a luz que conta como luz solar. Arma Sagrada, Resplendor "
         "Sagrado e Transfiguração Radiante."),
    ]))
    d['total'] = len(d['itens'])
    gravar(caminho, d)
    return True


def marcar_reservados():
    n = 0
    for cid, itens in RESERVADOS.items():
        caminho = os.path.join(caminhos.CATALOGOS, f'{cid}.json')
        d = carregar(caminho)
        for i in d['itens']:
            if i['id'] in itens and not i.get('reservado_para'):
                i['reservado_para'] = itens[i['id']]
                n += 1
        gravar(caminho, d)
    return n


def main():
    n_cat, n_itens = herdar_fontes()
    novo = declarar_tipo_emitir_luz()
    migrados = migrar_efeitos()
    n_res = marcar_reservados()
    print(f"B5 fonte herdada: {n_itens} itens em {n_cat} catálogos de opção")
    print(f"B7 efeitos migrados: {dict(migrados)}"
          + (" | tipo 'emitir_luz' declarado" if novo else ""))
    print(f"B3 vocabulário marcado como reservado: {n_res}")


if __name__ == '__main__':
    main()
