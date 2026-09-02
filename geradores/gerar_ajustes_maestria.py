# -*- coding: utf-8 -*-
"""Ajuste da auditoria de 2026-09-02: marcas de pendência que o capítulo 6 já resolveu.

As três Maestrias em Arma (Guerreiro, Bárbaro, Ladino) foram escritas na fase 2,
quando o catálogo de itens ainda não existia. Cada uma levou uma marca dizendo
isso — `revisao: duvida` no Guerreiro, `pendente: true` no bloco `de` do Bárbaro e
do Ladino. O capítulo 6 entrou na fase 4 e os filtros passaram a resolver sozinhos,
como o esquema previa; as marcas ficaram para trás.

Isso não é cosmético. `pendente: true` no bloco `de` **desliga a checagem de filtro
vazio** (regra 5 do esquema): enquanto ela estiver lá, um filtro que pare de
devolver itens vira silêncio em vez de erro. Conferido antes de remover: sem as
marcas, o validador continua limpo.

Os geradores de origem também foram corrigidos, para que uma reconstrução do zero
já nasça certa.
"""
import json, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(RAIZ, 'dados', 'caracteristicas.json')
d = json.load(open(p, encoding='utf-8'))
por_id = {i['id']: i for i in d['itens']}

mudou = []

# --- Guerreiro: a dúvida era "o catálogo de itens só existe a partir do cap. 6"
c = por_id['maestria_em_arma']
if c['revisao']['status'] == 'duvida':
    c['revisao'] = {
        "status": "ok",
        "notas": "Era dúvida enquanto o catálogo de itens não existia. O capítulo 6 entrou na "
                 "fase 4 e o filtro resolveu sozinho, como o esquema previa — 38 armas Simples e "
                 "Marciais. Resolvido na auditoria de 2026-09-02."}
    mudou.append('maestria_em_arma: revisao duvida -> ok')

# --- Bárbaro e Ladino: 'pendente' no bloco 'de' desligava a regra 5
for cid in ('maestria_em_arma_barbaro', 'maestria_em_arma_ladino'):
    for e in por_id[cid].get('efeitos', []):
        if e.get('tipo') == 'escolha' and e.get('de', {}).pop('pendente', None):
            e['de']['nota_da_auditoria'] = (
                "A marca 'pendente' saiu em 2026-09-02: existia porque o catálogo de itens ainda "
                "não tinha chegado, e estava desligando a checagem de filtro vazio.")
            mudou.append(f'{cid}: pendente removido do bloco de escolha')

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('\n'.join(mudou) if mudou else 'nada a ajustar')
