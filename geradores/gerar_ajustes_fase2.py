# -*- coding: utf-8 -*-
"""Ajustes decididos pelo usuário em 2026-08-31 sobre o lote do Monge."""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
p = os.path.join(D, 'caracteristicas.json')
d = json.load(open(p, encoding='utf-8'))
por_id = {i['id']: i for i in d['itens']}

# --- 1 e 2: nomes divergentes entre tabela e corpo do texto -----------------
for cid, nome_tabela, pag_tabela in [("golpes_potencializados", "Ataques Potencializados", 160),
                                     ("restauro_pessoal", "Autocura", 160)]:
    c = por_id[cid]
    c['nome_na_tabela'] = nome_tabela
    c['fonte_da_tabela'] = {"capitulo": 3, "pagina_livro": pag_tabela, "pagina_pdf": pag_tabela + 4}
    c['revisao'] = {"status": "ok",
        "notas": (f"O livro diverge de si mesmo: a tabela Características do Monge (p. {pag_tabela}) "
                  f"chama esta característica de '{nome_tabela}'. Decisão do usuário em 2026-08-31: "
                  f"vale o nome do corpo do texto ('{c['nome']}'); o nome da tabela fica guardado em "
                  "'nome_na_tabela' para busca.")}

# --- 3: Passo da Sombra Aprimorado -----------------------------------------
c = por_id['passo_da_sombra_aprimorado']
c['descricao_curta'] = ("Gaste 1 Ponto de Foco no Passo da Sombra para dispensar a exigência de luz: "
    "o teleporte pode partir de qualquer iluminação e chegar a qualquer iluminação. Você também "
    "realiza um Ataque Desarmado logo após o teleporte, na mesma Ação Bônus.")
c['efeitos'] = [
  {"tipo": "melhorar_caracteristica", "alvo": "passo_da_sombra", "custo_em_foco": 1,
   "efeitos": [
     {"tipo": "efeito_narrativo", "chave": "dispensa_requisito_de_luz",
      "texto": ("Remove os requisitos de iluminação do Passo da Sombra: origem e destino podem estar "
                "em qualquer nível de luz. Continuam valendo destino desocupado e à vista."),
      "remove_requisitos": ["voce_em:meia_luz_ou_escuridao", "destino_em:meia_luz_ou_escuridao"],
      "mantem_requisitos": ["destino_desocupado", "destino_a_vista"]},
     {"tipo": "conceder_ataque", "quantidade": ["1"], "tipo_ataque": "desarmado",
      "momento": "imediatamente_apos_o_teleporte"}]}]
c['revisao'] = {"status": "ok",
  "notas": ("Redação ambígua no livro: Passo da Sombra (p. 164) exige estar 'inteiramente em Meia-luz "
            "ou Escuridão' e chegar a espaço igualmente escuro, mas a melhoria de nível 11 fala em "
            "remover o requisito de 'iniciar ou encerrar seu turno' nessas condições. Ruling do usuário "
            "em 2026-08-31: gastando 1 Ponto de Foco, os dois requisitos de iluminação caem — pode "
            "teleportar de um lugar iluminado para a escuridão, da escuridão para um lugar iluminado, "
            "ou qualquer combinação. Interpretação de mesa, não literal do texto.")}

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("ajustes aplicados:", [i['id'] for i in d['itens'] if i['revisao']['status'] != 'ok'] or "nenhuma dúvida em aberto")
