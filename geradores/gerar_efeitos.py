# -*- coding: utf-8 -*-
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')

TIPOS = [
 # (id, origem, campos, nota)
 ("modificador","v1",["alvo","valor","empilha"],"Soma/subtrai um valor de um alvo de rolagem."),
 ("vantagem","v1",["alvo","modo","condicao","duracao","beneficiario"],"modo: vantagem | desvantagem."),
 ("alterar_dano","v1",["tipo_dano","operacao"],"operacao: resistencia | imunidade | vulnerabilidade | bonus. tipo_dano aceita 'todos'."),
 ("conceder_condicao","NOVO","condicao_id persiste_apos_encerrar".split(),"Impõe outra condição (Paralisado concede Incapacitado)."),
 ("alterar_condicao","NOVO",["condicao_id","operacao"],"operacao: imunidade. Ex.: Petrificado dá Imunidade a Envenenado."),
 ("travar_deslocamento","NOVO",["valor","impede_aumento"],"Deslocamento fixado (0) e impedido de aumentar."),
 ("restringir_movimento","NOVO",["opcoes","custo_para_levantar","condicao"],"Caído: só rastejar ou levantar."),
 ("falha_automatica","NOVO",["alvo","condicao"],"Falha automática em salvaguarda ou teste."),
 ("impedir","NOVO",["alvo","referencia","duracao"],"Bloqueia ação, reação, fala, concentração, aproximação etc."),
 ("acerto_critico_automatico","NOVO",["condicao"],"Ataques que acertam viram crítico sob a condição."),
 ("remocao","NOVO",["gatilho","quantidade"],"Remove níveis/instâncias da própria condição (Exaustão em Descanso Longo)."),
 ("efeito_narrativo","NOVO",["chave","texto"],"Sem efeito mecânico; o app só exibe. Mantido para não perder regra."),
 ("conceder_ataque","NOVO",["quantidade"],"Ação Atacar."),
 ("conceder_acao","v1",["id","custo","duracao","efeitos"],"Concede uma ação/reação nova."),
 ("ca_base","v1",["formula","permite_escudo"],"Não usado nesta fase."),
 ("travar_atributo","v1",["atributo","valor_minimo"],"Não usado nesta fase."),
 ("conceder_proficiencia","v1",["categoria","chave","nivel_dominio"],"Não usado nesta fase."),
 ("conceder_talento","v1",["talento_id"],"Não usado nesta fase."),
 ("aumento_atributo","v1",["distribuicao","limite"],"Não usado nesta fase."),
 ("conceder_slot","v1",["tabela_progressao_id"],"Não usado nesta fase."),
 ("desbloquear_magias","v1",["lista_id","modo"],"Não usado nesta fase."),
 ("preparar_magias","v1",["formula_quantidade","atributo_conjuracao"],"Não usado nesta fase."),
 ("recurso_com_recarga","v1",["id","formula_maximo","recarga","consumo"],"Não usado nesta fase."),
 ("dado_de_impacto","v1",["formula_dado","escalonamento_por_nivel"],"Não usado nesta fase."),
 ("conceder_sentido","v1",["sentido","alcance"],"Não usado nesta fase."),
 ("conceder_velocidade","v1",["tipo","formula"],"Não usado nesta fase."),
 ("escolha","v1",["rotulo","quantidade","de","momento","efeito_por_item_escolhido"],"Não usado nesta fase."),
 ("substituir_regra","v1",["regra_id","novo_valor"],"Último recurso; exige revisao.status='duvida'."),
]
json.dump({"catalogo":"tipos_de_efeito","nome":"Tipos de Efeito","total":len(TIPOS),
 "itens":[{"id":i,"origem":o,"campos":c,"nota":n} for i,o,c,n in TIPOS]},
 open(os.path.join(D,'catalogos/tipos_de_efeito.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2)

IMPED = [("acao","Executar uma ação"),("acao_bonus","Executar uma Ação Bônus"),
 ("reacao","Executar uma Reação"),("concentracao","Manter Concentração"),("falar","Falar"),
 ("atacar_ou_alvejar","Atacar ou ter como alvo uma criatura específica"),
 ("aproximar_voluntariamente_de","Aproximar-se voluntariamente de algo"),
 ("ataque_de_oportunidade_provocado_por_voce","Provocar Ataques de Oportunidade ao se mover")]
json.dump({"catalogo":"alvos_de_impedimento","nome":"Alvos de Impedimento","total":len(IMPED),
 "itens":[{"id":i,"nome":n} for i,n in IMPED],
 "fonte":{"capitulo":"ap_c","pagina_livro":360,"pagina_pdf":364}},
 open(os.path.join(D,'catalogos/alvos_de_impedimento.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('ok')
