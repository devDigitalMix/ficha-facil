# -*- coding: utf-8 -*-
"""Forma Selvagem: sem catálogo de criaturas por decisão de escopo (2026-09-01).

O app não oferece seletor de formas; ao subir de nível ele apenas AVISA quantas
formas o personagem conhece, o ND máximo e se já pode voar. A escolha em si fica
com o jogador, fora do app, até o Apêndice B ser extraído — se for."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
p = os.path.join(D, 'caracteristicas.json')
d = json.load(open(p, encoding='utf-8'))
por = {i['id']: i for i in d['itens']}

c = por['forma_selvagem']
for i, e in enumerate(c['efeitos']):
    if e.get('id') == 'druida_formas_conhecidas':
        c['efeitos'][i] = {
          "id": "druida_formas_conhecidas", "tipo": "escolha",
          "rotulo": "Formas Animais conhecidas",
          "resolucao": "manual",
          "quantidade": "tabela:formas_de_feras.formas_conhecidas",
          "momento": "nivel_2", "reescolhivel": True, "reescolha_em": "descanso_longo",
          "reescolha_quantidade": 1,
          "recomendadas": ["Aranha", "Cavalo de Montaria", "Lobo", "Rato"],
          "de": {"catalogo": "criaturas", "pendente": True,
                 "filtro": {"tipo_de_criatura": "fera",
                            "nd_maximo": "tabela:formas_de_feras.nd_maximo",
                            "sem_deslocamento_de_voo": "tabela:formas_de_feras.deslocamento_de_voo == false"}},
          "aviso_ao_subir_de_nivel": {
            "quando": "o nível de Druida atinge 2, 4 ou 8",
            "texto": ("Você conhece {formas_conhecidas} formas Animais, de Nível de Desafio até "
                      "{nd_maximo}{voo}. Escolha-as entre os blocos de estatísticas de Fera do "
                      "Apêndice B ou do Livro dos Monstros, com o aval do Mestre."),
            "variaveis": {"voo": {"true": ", podendo ter Deslocamento de Voo",
                                  "false": ", sem Deslocamento de Voo"}}},
          "efeito_por_item_escolhido": {"tipo": "efeito_narrativo", "chave": "forma_conhecida",
                                        "criatura": "{{escolhido}}"}}
c['revisao'] = {"status": "ok",
  "notas": ("Decisão do usuário em 2026-09-01: criaturas e blocos de estatísticas ficam FORA do "
            "escopo por enquanto. O app não oferece seletor de formas — ao subir de nível ele só "
            "informa quantas formas, o ND máximo e se já pode voar (campo "
            "`aviso_ao_subir_de_nivel`), e o jogador escolhe as Feras fora do app. O filtro está "
            "escrito e pronto: se o Apêndice B for extraído depois, o seletor passa a funcionar sem "
            "reeditar o Druida. Registrado em PENDENCIAS.md.")}
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok')
