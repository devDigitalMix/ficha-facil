# -*- coding: utf-8 -*-
"""Fase 2d — Classe Bruxo (cap. 3, p. 69-79), invocações místicas e 4 patronos."""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
CD = ["8", "mod:CAR", "prof"]   # CD para evitar sua magia

# ------------------------------------------- tipos de efeito e alvos novos
NOVOS = [
 ("reserva_de_dados","id formula_quantidade dado recarga gasto_maximo_por_uso","Reserva de dados gastáveis (Luz Medicinal do Celestial)."),
 ("magias_de_patrono","tabela","Magias sempre preparadas por nível, concedidas pela subclasse, que não contam para o limite."),
 ("alterar_tipo_de_dano_da_magia","opcoes escopo","Troca o tipo de dano de uma magia conjurada."),
 ("dispensar_componentes","componentes escopo","Conjura sem componentes Verbais e/ou Somáticos."),
]
te = rd('catalogos/tipos_de_efeito.json'); ex = {i['id'] for i in te['itens']}
for i, campos, nota in NOVOS:
    if i not in ex:
        te['itens'].append({"id": i, "nome": i.replace('_',' ').capitalize(),
                            "origem": "NOVO_FASE2D", "campos": campos.split(), "nota": nota})
te['total'] = len(te['itens']); wr('catalogos/tipos_de_efeito.json', te)

# ------------------------------------------------- invocações místicas (28)
def inv(id_, nome, pag, desc, efeitos, prereq=None, repetivel=False, **kw):
    d = {"id": id_, "nome": nome, "fonte": f(pag), "descricao_curta": desc, "efeitos": efeitos,
         "pre_requisitos": prereq or [], "repetivel": repetivel}
    d.update(kw); return d
def nivel(n): return {"tipo": "nivel_de_classe", "classe": "bruxo", "minimo": n}
def invoc(i): return {"tipo": "invocacao", "chave": i}
def truque_dano(comataque=False):
    return {"tipo": "magia_conhecida", "filtro": dict({"lista": "bruxo", "nivel": 0, "causa_dano": True},
            **({"exige_jogada_de_ataque": True} if comataque else {}))}
def conjurar_sem_espaco(magia, **kw):
    return dict({"tipo": "conjurar_sem_espaco", "magia": magia}, **kw)

INV = [
 inv("armadura_de_sombras","Armadura de Sombras",71,"Conjura Armadura Arcana em si sem gastar espaço de magia.",
     [conjurar_sem_espaco("armadura_arcana", alvo="voce", frequencia="a_vontade")]),
 inv("explosao_agonizante","Explosão Agonizante",71,"Soma o modificador de Carisma às jogadas de dano de um truque de Bruxo à escolha.",
     [{"id":"explosao_agonizante_truque","tipo":"escolha","rotulo":"Escolha um truque de Bruxo que cause dano",
       "quantidade":1,"momento":"ao_adquirir",
       "de":{"catalogo":"magias","filtro":{"lista":"bruxo","nivel":0}},
       "efeito_por_item_escolhido":{"tipo":"modificador","alvo":"jogada_de_dano","valor":["mod:CAR"],
                                    "empilha":"soma","magia":"{{escolhido}}"}}],
     [nivel(2), truque_dano()], True),
 inv("explosao_repulsiva","Explosão Repulsiva",71,"Ao atingir criatura Grande ou menor com um truque de Bruxo que exija jogada de ataque, pode empurrá-la até 3 metros.",
     [{"tipo":"efeito_narrativo","chave":"empurrao_do_truque",
       "texto":"Empurra até 3 metros a criatura Grande ou menor atingida pelo truque escolhido."}],
     [nivel(2), truque_dano(True)], True),
 inv("investimento_do_mestre_da_corrente","Investimento do Mestre da Corrente",71,
     "O familiar de Convocar Familiar ganha voo ou natação 12 m, pode atacar com Ação Bônus sua, usa a CD para evitar sua magia, pode trocar dano físico por Necrótico ou Radiante, e você pode dar Resistência a ele com uma Reação.",
     [{"tipo":"efeito_narrativo","chave":"familiar_investido",
       "texto":"Familiar com Deslocamento de Voo ou Natação 12 m; Ação Bônus para mandá-lo Atacar; usa a CD para evitar sua magia; troca dano Contundente/Cortante/Perfurante por Necrótico ou Radiante; Reação para conceder Resistência a ele."}],
     [nivel(5), invoc("pacto_da_corrente")]),
 inv("lamento_das_sepulturas","Lamento das Sepulturas",71,"Conjura Falar com Mortos sem gastar espaço de magia.",
     [conjurar_sem_espaco("falar_com_mortos", frequencia="a_vontade")], [nivel(7)]),
 inv("lamina_devoradora","Lâmina Devoradora",71,"O Ataque Extra da Lâmina Sedenta passa a conceder dois ataques extras.",
     [{"tipo":"melhorar_caracteristica","alvo":"lamina_sedenta",
       "efeitos":[{"tipo":"conceder_ataque","quantidade":["3"],"modo":"define_total_da_acao_atacar",
                   "condicao":{"todas":["arma_de_pacto"]}}]}],
     [nivel(12), invoc("lamina_sedenta")]),
 inv("lamina_sedenta","Lâmina Sedenta",71,"Ganha Ataque Extra apenas com a arma de pacto: ataca duas vezes com ela na ação Atacar.",
     [{"tipo":"conceder_ataque","quantidade":["2"],"modo":"define_total_da_acao_atacar",
       "condicao":{"todas":["arma_de_pacto"]}}],
     [nivel(5), invoc("pacto_da_lamina")]),
 inv("lanca_mistica","Lança Mística",72,"O alcance de um truque de Bruxo à escolha (alcance 3 m ou mais) aumenta em 9 metros vezes seu nível de Bruxo.",
     [{"id":"lanca_mistica_truque","tipo":"escolha","rotulo":"Escolha um truque de Bruxo que cause dano",
       "quantidade":1,"momento":"ao_adquirir",
       "de":{"catalogo":"magias","filtro":{"lista":"bruxo","nivel":0}},
       "efeito_por_item_escolhido":{"tipo":"modificador","alvo":"alcance_de_magia",
         "valor":{"op":"mult","args":["9","nivel_classe:bruxo"]},"unidade":"m","empilha":"soma",
         "magia":"{{escolhido}}"}}],
     [nivel(2), truque_dano()], True),
 inv("licoes_dos_grandes_antigos","Lições dos Grandes Antigos",72,"Adquire um talento de Origem à escolha.",
     [{"id":"licoes_talento","tipo":"escolha","rotulo":"Escolha um talento de Origem","quantidade":1,
       "momento":"ao_adquirir","de":{"catalogo":"talentos","filtro":{"categoria":"origem"}},
       "efeito_por_item_escolhido":{"tipo":"conceder_talento","talento_id":"{{escolhido}}"}}],
     [nivel(2)], True),
 inv("mascara_das_muitas_faces","Máscara das Muitas Faces",72,"Conjura Disfarçar-se sem gastar espaço de magia.",
     [conjurar_sem_espaco("disfarcar_se", frequencia="a_vontade")], [nivel(2)]),
 inv("mente_mistica","Mente Mística",72,"Vantagem em salvaguardas de Constituição para manter Concentração.",
     [{"tipo":"vantagem","alvo":"salvaguarda:CON","modo":"vantagem",
       "condicao":{"todas":["manter_concentracao"]}}]),
 inv("mestre_das_infindaveis_formas","Mestre das Infindáveis Formas",72,"Conjura Alterar-se sem gastar espaço de magia.",
     [conjurar_sem_espaco("alterar_se", frequencia="a_vontade")], [nivel(5)]),
 inv("olhar_de_duas_mentes","Olhar de Duas Mentes",72,"Ação Bônus para tocar uma criatura voluntária e perceber pelos sentidos dela até o fim do seu próximo turno, prorrogável com nova Ação Bônus.",
     [{"tipo":"efeito_narrativo","chave":"percepcao_emprestada","custo":"acao_bonus",
       "texto":"Percebe pelos sentidos da criatura tocada, aproveitando sentidos especiais dela, e pode conjurar como se estivesse no espaço dela se estiverem a até 18 m."}],
     [nivel(5)]),
 inv("pacto_da_corrente","Pacto da Corrente",72,"Aprende Convocar Familiar e a conjura sem gastar espaço; o familiar pode ter formas especiais e atacar com a Reação dele quando você abre mão de um ataque.",
     [conjurar_sem_espaco("convocar_familiar", custo="acao", acao_id="usar_magia", frequencia="a_vontade"),
      {"tipo":"efeito_narrativo","chave":"formas_especiais_de_familiar",
       "texto":"Formas extras: Cobra Peçonhenta, Diabrete, Esfinge Maravilhosa, Esqueleto, Pseudodragão, Quasit, Slaad Girino, Sprite. Na ação Atacar, abre mão de um ataque para o familiar atacar com a Reação dele."}]),
 inv("pacto_da_lamina","Pacto da Lâmina",72,"Ação Bônus para conjurar ou vincular uma arma de pacto: proficiência com ela, uso como Foco de Conjuração, ataque e dano por Carisma, e dano Necrótico, Psíquico ou Radiante à escolha.",
     [{"tipo":"conceder_acao","id":"conjurar_arma_de_pacto","custo":"acao_bonus",
       "efeitos":[{"tipo":"conceder_proficiencia","categoria":"arma","chave":"arma_de_pacto",
                   "nivel_dominio":"proficiente"},
                  {"tipo":"substituir_atributo","de":"FOR_ou_DES","para":"CAR",
                   "escopo":["jogada_de_ataque","jogada_de_dano"],"aplica_a":["arma_de_pacto"]},
                  {"tipo":"escolher_tipo_de_dano","aplica_a":["arma_de_pacto"],
                   "opcoes":["necrotico","psiquico","radiante","tipo_normal"]}]}],
     encerramento=[{"gatilho":"usar_a_acao_bonus_de_novo"},
                   {"gatilho":"arma_a_mais_de_1_5m_por_1_minuto"},{"gatilho":"morte"}]),
 inv("pacto_do_tomo","Pacto do Tomo",72,"Conjura o Livro das Sombras ao fim de um descanso: três truques e duas magias de 1º círculo com marcador Ritual, de QUALQUER lista de classe, ficam preparadas como magias de Bruxo. O livro serve de Foco de Conjuração.",
     [{"id":"tomo_truques","tipo":"escolha","rotulo":"Escolha três truques de qualquer lista",
       "quantidade":3,"momento":"ao_conjurar_o_livro","reescolhivel":True,"reescolha_em":"descanso",
       "de":{"catalogo":"magias","filtro":{"nivel":0}},
       "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","modo":"conhecida","magia":"{{escolhido}}",
                                    "conta_como":"magia_de_bruxo"}},
      {"id":"tomo_rituais","tipo":"escolha","rotulo":"Escolha duas magias de 1º círculo com marcador Ritual",
       "quantidade":2,"momento":"ao_conjurar_o_livro","reescolhivel":True,"reescolha_em":"descanso",
       "de":{"catalogo":"magias","filtro":{"nivel":1,"ritual":True}},
       "efeito_por_item_escolhido":{"tipo":"desbloquear_magias","modo":"sempre_preparada",
                                    "magia":"{{escolhido}}","conta_como":"magia_de_bruxo"}}],
     nota="As magias escolhidas devem ser magias que você ainda não tem preparadas."),
 inv("passo_ascendente","Passo Ascendente",72,"Conjura Levitação em si sem gastar espaço de magia.",
     [conjurar_sem_espaco("levitacao", alvo="voce", frequencia="a_vontade")], [nivel(5)]),
 inv("presente_das_profundezas","Presente das Profundezas",72,"Respira debaixo d'água e tem Deslocamento de Natação igual ao seu Deslocamento; conjura Respirar na Água uma vez por Descanso Longo sem espaço.",
     [{"tipo":"conceder_velocidade","tipo_deslocamento":"natacao","formula":["deslocamento"]},
      {"tipo":"efeito_narrativo","chave":"respiracao_aquatica","texto":"Você pode respirar debaixo d'água."},
      conjurar_sem_espaco("respirar_na_agua", frequencia="uma_vez_por_descanso_longo",
                          recarga=["descanso_longo"])],
     [nivel(5)]),
 inv("presente_dos_protetores","Presente dos Protetores",73,"Uma página do Livro das Sombras guarda nomes (até seu modificador de Carisma): quem estiver nela e for reduzido a 0 PV sem morrer fica com 1 PV. Recarrega em Descanso Longo.",
     [{"tipo":"recurso_com_recarga","id":"presente_dos_protetores","formula_maximo":["1"],
       "recarga":["descanso_longo"],"consumo":"por_uso"},
      {"tipo":"efeito_narrativo","chave":"salvar_com_1_pv",
       "quantidade_de_nomes":{"op":"max","args":["1","mod:CAR"]},
       "texto":"Criatura cujo nome está na página fica com 1 Ponto de Vida ao ser reduzida a 0 sem morrer."}],
     [nivel(9), invoc("pacto_do_tomo")]),
 inv("punicao_mistica","Punição Mística",73,"Uma vez por turno, ao acertar com a arma de pacto, gasta um espaço de Magia de Pacto para causar 1d8 de dano Energético por círculo do espaço e impor Caído a alvo Enorme ou menor.",
     [{"tipo":"dano","frequencia":"uma_vez_por_turno","gatilho":"acerto_com_arma_de_pacto",
       "formula_dado":{"op":"mult","args":["circulo_do_espaco_gasto","1d8"]},"tipo_dano":"energetico",
       "modo":"dano_adicional","gasta_espaco_de_magia":True},
      {"tipo":"conceder_condicao","condicao_id":"caido","beneficiario":"alvo",
       "condicao":{"todas":["alvo_enorme_ou_menor"]}}],
     [nivel(5), invoc("pacto_da_lamina")]),
 inv("salto_sobrenatural","Salto Sobrenatural",73,"Conjura Salto em si sem gastar espaço de magia.",
     [conjurar_sem_espaco("salto", alvo="voce", frequencia="a_vontade")], [nivel(2)]),
 inv("sorvedouro_de_vida","Sorvedouro de Vida",73,"Uma vez por turno, ao acertar com a arma de pacto, causa 1d6 extra de dano Necrótico, Psíquico ou Radiante e pode gastar um Dado de Pontos de Vida para se curar.",
     [{"tipo":"dano","frequencia":"uma_vez_por_turno","gatilho":"acerto_com_arma_de_pacto",
       "formula_dado":"1d6","escolher_tipo_de_dano":["necrotico","psiquico","radiante"],
       "modo":"dano_adicional"},
      {"tipo":"cura","formula":["dado_de_vida","mod:CON"],"minimo":1,"gasta":"dado_de_vida"}],
     [nivel(9), invoc("pacto_da_lamina")]),
 inv("uno_com_as_sombras","Uno com as Sombras",73,"Em Meia-luz ou Escuridão, conjura Invisibilidade em si sem gastar espaço de magia.",
     [conjurar_sem_espaco("invisibilidade", alvo="voce", frequencia="a_vontade",
                          requisitos=["voce_em:meia_luz_ou_escuridao"])], [nivel(5)]),
 inv("vigor_infero","Vigor Ínfero",73,"Conjura Vitalidade Vazia em si sem gastar espaço de magia, e recebe automaticamente o resultado máximo do dado de Pontos de Vida Temporários.",
     [conjurar_sem_espaco("vitalidade_vazia", alvo="voce", frequencia="a_vontade",
                          modificacao="os Pontos de Vida Temporários usam o resultado máximo do dado")],
     [nivel(2)]),
 inv("visao_da_bruxa","Visão da Bruxa",73,"Visão Verdadeira com alcance de 9 metros.",
     [{"tipo":"conceder_sentido","sentido":"visao_verdadeira","alcance_m":9}], [nivel(15)]),
 inv("visao_diabolica","Visão Diabólica",73,"Enxerga normalmente em Meia-luz e Escuridão, mágicas ou não, a até 36 metros.",
     [{"tipo":"conceder_sentido","sentido":"visao_no_escuro","alcance_m":36,
       "inclui_escuridao_magica":True}], [nivel(2)]),
 inv("visoes_de_reinos_distantes","Visões de Reinos Distantes",73,"Conjura Olho Arcano sem gastar espaço de magia.",
     [conjurar_sem_espaco("olho_arcano", frequencia="a_vontade")], [nivel(9)]),
 inv("visoes_nebulosas","Visões Nebulosas",73,"Conjura Imagem Silenciosa sem gastar espaço de magia.",
     [conjurar_sem_espaco("imagem_silenciosa", frequencia="a_vontade")], [nivel(2)]),
]
wr('catalogos/invocacoes_misticas.json', {"catalogo":"invocacoes_misticas","nome":"Invocações Místicas",
 "fonte": f(71), "total": len(INV),
 "nota":"Pré-requisitos devem ser atendidos para escolher a invocação. Não se pode escolher a mesma duas vezes, salvo quando marcada repetível, e não se pode trocar uma invocação que seja pré-requisito de outra que você tenha.",
 "itens": INV})
print("invocações:", len(INV))
