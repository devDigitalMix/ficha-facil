# -*- coding: utf-8 -*-
"""Declara o que um efeito aninhado dentro de outro significa.

Achado ao explicar o coletor da fase 15. Vários efeitos trazem outros efeitos
dentro (`efeitos: [...]`), e o motor precisava saber se o aninhamento é uma
CONDIÇÃO ou só ESTRUTURA. Ele estava adivinhando pelo formato — todo aninhamento
virava condição — e adivinhou errado.

O tamanho do erro: dos 81 efeitos que aninham, **56 são `melhorar_caracteristica`**,
que não é condição nenhuma. O `alvo` dela diz a QUAL característica os efeitos se
aplicam; é redirecionamento. Tratada como condição, e sem `id` para dar nome à
condição, as 56 caíam todas no mesmo balde e — pior — ficavam desligadas por padrão.
Melhoria de característica sumia calada.

    Fúria           é condição: liga, dura, encerra. O que está dentro só vale ligada.
    Melhorar        é estrutura: o alvo diz onde aplicar, não quando.

A regra passa a ser DECLARADA, em `catalogos/tipos_de_efeito.json`, e não inferida:

    "efeitos_aninhados": "condicionados"   ou   "estruturais"

E todo efeito que condiciona precisa de `id`, porque é ele que nomeia a condição.
Cinco não tinham; ganham o id da entidade que os carrega, que é único e é como as
pessoas já os chamam.
"""
import json, collections, os, sys

TIPOS = 'dados/catalogos/tipos_de_efeito.json'

# Os nove tipos que aninham efeitos, classificados à mão. Quem criar o décimo tem de
# passar por aqui — o validador cobra.
CLASSIFICACAO = {
    # ---- condicionados: coisas que se ligam, duram e encerram
    'furia': ('condicionados',
              'Enquanto a Fúria está ativa. Tem custo, duração e encerra_se.'),
    'forma_selvagem': ('condicionados',
                       'Enquanto multimorfado.'),
    'emanacao': ('condicionados',
                 'Enquanto a emanação existe.'),
    'alterar_tamanho': ('condicionados',
                        'Enquanto o tamanho alterado dura.'),
    'aplicar_veneno': ('condicionados',
                       'Enquanto o veneno aplicado dura.'),
    'redirecionar_dano': ('condicionados',
                          'Só quando a Reação é usada.'),
    'reserva_de_dados': ('condicionados',
                         'Só quando um dado da reserva é gasto.'),
    'conceder_acao': ('condicionados',
                      'Os efeitos são o que a ação FAZ; valem ao executá-la, '
                      'não passivamente.'),
    # ---- estruturais: o pai não liga nem desliga nada
    'melhorar_caracteristica': ('estruturais',
                                'O campo `alvo` diz a qual característica os efeitos '
                                'se aplicam. É redirecionamento, não condição: quem '
                                'tem a melhoria tem os efeitos.'),
}

# efeito condicionante sem id -> o id da entidade que o carrega
IDS_QUE_FALTAVAM = {
    'furia': 'furia',
    'forma_selvagem': 'forma_selvagem',
    'alterar_tamanho': 'forma_grande',
    'redirecionar_dano': 'dadiva_da_resistencia_a_energia',
    'aplicar_veneno': 'envenenador',
}

ARQUIVOS = []


def carregar(p):
    return json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)


def gravar(p, d):
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def por_ids(o, postos):
    """Dá id ao efeito condicionante que não tem, com o nome que o dado já usa."""
    if isinstance(o, list):
        for x in o:
            por_ids(x, postos)
        return
    if not isinstance(o, dict):
        return
    t = o.get('tipo')
    if t in IDS_QUE_FALTAVAM and isinstance(o.get('efeitos'), list) and 'id' not in o:
        # o id entra logo depois do tipo, para ficar legível
        novo = collections.OrderedDict()
        for k, v in o.items():
            novo[k] = v
            if k == 'tipo':
                novo['id'] = IDS_QUE_FALTAVAM[t]
        o.clear()
        o.update(novo)
        postos[t] += 1
    for v in list(o.values()):
        por_ids(v, postos)


def main():
    # 1. a declaração no catálogo de tipos de efeito
    d = carregar(TIPOS)
    conhecidos = {i['id'] for i in d['itens']}
    faltando = set(CLASSIFICACAO) - conhecidos
    if faltando:
        print('ERRO: tipo classificado que não existe no catálogo: %s' % sorted(faltando))
        return 1
    declarados = 0
    for i in d['itens']:
        if i['id'] not in CLASSIFICACAO:
            continue
        modo, porque = CLASSIFICACAO[i['id']]
        i['efeitos_aninhados'] = modo
        i['nota_dos_aninhados'] = porque
        declarados += 1
    d['nota_dos_aninhados'] = (
        "Um efeito pode trazer outros dentro. `efeitos_aninhados` diz o que isso "
        "significa: 'condicionados' = só valem enquanto o pai estiver ativo (e o pai "
        "precisa de `id`, que nomeia a condição); 'estruturais' = valem sempre, o pai "
        "só diz onde aplicá-los. Sem esta declaração o motor teria de adivinhar pelo "
        "formato — e adivinhava errado nos 56 `melhorar_caracteristica`."
    )
    gravar(TIPOS, d)

    # 2. os ids que faltavam nos condicionantes
    postos = collections.Counter()
    for raiz, _, fs in os.walk('dados'):
        for f in sorted(fs):
            if not f.endswith('.json'):
                continue
            p = os.path.join(raiz, f)
            doc = carregar(p)
            antes = json.dumps(doc, ensure_ascii=False)
            por_ids(doc, postos)
            if json.dumps(doc, ensure_ascii=False) != antes:
                gravar(p, doc)

    ja_tinham = len(IDS_QUE_FALTAVAM) - sum(postos.values())
    print('efeitos aninhados: %d tipos declarados, %d ids postos (%d já tinham)'
          % (declarados, sum(postos.values()), ja_tinham))
    return 0


if __name__ == '__main__':
    sys.exit(main())
