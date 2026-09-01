# -*- coding: utf-8 -*-
"""Corrige os quatro erros que o validador apontou no lote do Guerreiro."""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
def f(cap, livro): return {"capitulo": cap, "pagina_livro": livro, "pagina_pdf": livro + 4}

# --- 1) Ataque Extra é a MESMA característica em Monge e Guerreiro -> genérica
C = rd('caracteristicas.json')
itens = [c for c in C['itens'] if c['id'] != 'ataque_extra']
itens.append({"id": "ataque_extra", "nome": "Ataque Extra", "escopo": "generico",
  "tipo_de_entrada": "caracteristica",
  "fonte": f(3, 128), "revisao": {"status": "ok",
   "notas": "Texto idêntico no Monge (p. 161) e no Guerreiro (p. 128). Modelada como genérica: cada classe a concede no nível da própria progressão. Importa para multiclasse, onde Ataque Extra não acumula."},
  "descricao_curta": "Ataca duas vezes, em vez de uma, sempre que executa a ação Atacar no seu turno.",
  "concedida_por": [{"classe": "monge", "nivel": 5, "pagina_livro": 161},
                    {"classe": "guerreiro", "nivel": 5, "pagina_livro": 128}],
  "efeitos": [{"tipo": "conceder_ataque", "quantidade": ["2"], "modo": "define_total_da_acao_atacar"}]})
C['itens'] = itens; C['total'] = len(itens)

# --- 3) escolha sobre o catálogo inteiro precisa dizer isso explicitamente
for c in C['itens']:
    if c['id'] == 'superioridade_em_combate':
        for e in c['efeitos']:
            if e.get('tipo') == 'escolha' and e['de'].get('catalogo') == 'manobras':
                e['de']['todo_o_catalogo'] = True
wr('caracteristicas.json', C)

# --- 2) catálogo de armas (a tabela Armas, p. 215) para Maestria em Arma validar
SIMPLES_CC = ["Adaga","Azagaia","Cajado","Clava","Clava Grande","Foice","Lança","Maça","Machadinha","Martelo Leve"]
SIMPLES_AD = ["Arco Curto","Besta Leve","Dardo","Funda"]
MARCIAL_CC = ["Alabarda","Chicote","Cimitarra","Espada Curta","Espada Grande","Espada Longa","Glaive",
              "Lança de Montaria","Lança Longa","Maça Estrela","Machado de Batalha","Machado Grande",
              "Malho","Mangual","Martelo de Guerra","Picareta de Guerra","Rapieira","Tridente"]
MARCIAL_AD = ["Arco Longo","Besta de Mão","Besta Pesada","Mosquete","Pistola","Zarabatana"]
import unicodedata, re
def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')
itens = []
for nomes, grupo, alcance in [(SIMPLES_CC,"simples","corpo_a_corpo"), (SIMPLES_AD,"simples","a_distancia"),
                              (MARCIAL_CC,"marcial","corpo_a_corpo"), (MARCIAL_AD,"marcial","a_distancia")]:
    for n in nomes:
        itens.append({"id": slug(n), "nome": n, "categoria": "arma", "grupo": grupo,
                      "alcance": alcance, "fonte": f(6, 215)})
wr('catalogos/itens.json', {"catalogo": "itens", "nome": "Itens", "parcial": True,
 "fonte": f(6, 215), "total": len(itens),
 "nota": ("PARCIAL: por ora só as armas da tabela Armas (p. 215), com nome, grupo e alcance — o que a "
          "escolha de Maestria em Arma do Guerreiro precisa referenciar. Dano, propriedades, maestria, "
          "peso e custo entram na fase do capítulo 6, junto com armaduras e equipamento de aventura."),
 "itens": itens})
print('armas no catálogo parcial:', len(itens))
