# -*- coding: utf-8 -*-
"""Forma Selvagem: o seletor de formas LIGA, agora que o Apêndice B existe.

Este script nasceu na fase 2 com a decisão oposta — criaturas estavam fora de
escopo, o app só avisava quantas formas e qual ND, e o jogador escolhia a Fera
fora do app. A escolha já apontava para o catálogo `criaturas` por FILTRO, com
`pendente: true`, justamente para ligar sem reeditar o Druida quando o apêndice
chegasse. Chegou (`gerar_criaturas.py`), então:

- sai o `pendente` do filtro: ele resolve contra as 43 Feras do apêndice e o
  validador volta a cobrar que não devolva conjunto vazio;
- as recomendações deixam de ser nome de exibição e viram id de verdade;
- o efeito por item escolhido deixa de ser `efeito_narrativo` e passa a apontar o
  bloco de estatísticas que o app vai carregar;
- o aviso ao subir de nível FICA. O ND máximo e o teto de voo continuam sendo o
  que o jogador precisa saber, e o Mestre continua podendo liberar Fera de fora
  do apêndice — o texto agora diz isso em vez de dizer que a escolha é fora do app.
"""
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
          "quantidade": "tabela:formas_de_feras.formas_conhecidas",
          "momento": "nivel_2", "reescolhivel": True, "reescolha_em": "descanso_longo",
          "reescolha_quantidade": 1,
          "recomendadas": ["aranha", "cavalo_de_montaria", "lobo", "rato"],
          "de": {"catalogo": "criaturas",
                 "filtro": {"tipo_de_criatura": "fera",
                            "nd_maximo": "tabela:formas_de_feras.nd_maximo",
                            "sem_deslocamento_de_voo": "tabela:formas_de_feras.deslocamento_de_voo == false"}},
          "aviso_ao_subir_de_nivel": {
            "quando": "o nível de Druida atinge 2, 4 ou 8",
            "texto": ("Você conhece {formas_conhecidas} formas Animais, de Nível de Desafio até "
                      "{nd_maximo}{voo}. O app oferece as Feras do Apêndice B; o Mestre pode "
                      "liberar outras, do Livro dos Monstros."),
            "variaveis": {"voo": {"true": ", podendo ter Deslocamento de Voo",
                                  "false": ", sem Deslocamento de Voo"}}},
          "efeito_por_item_escolhido": {"tipo": "assumir_bloco_de_estatisticas",
                                        "criatura": "{{escolhido}}",
                                        "catalogo": "criaturas",
                                        "modo": "forma_selvagem"}}
c['revisao'] = {"status": "ok",
  "notas": ("O Apêndice B foi extraído em 2026-09-02 e o seletor de formas ligou: a escolha "
            "resolve contra as 43 Feras do catálogo `criaturas`, filtradas por ND máximo e por "
            "Deslocamento de Voo conforme a tabela Formas de Feras. O aviso ao subir de nível "
            "continua, porque o Mestre pode liberar Fera de fora do apêndice.")}
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('forma selvagem: seletor ligado contra o catálogo de criaturas')
