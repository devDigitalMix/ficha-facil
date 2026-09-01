# -*- coding: utf-8 -*-
import json, os
BASE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(BASE, 'dados')
def f(p): return {"capitulo": "ap_c", "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}

A = [
{"id":"ajudar","nome":"Ajudar","custo":"acao","fonte":f(360),
 "revisao":{"status":"duvida","notas":"A tabela Ações do cap. 1 (p. 15) resume Ajudar como 'ajudar no teste/ataque de outra criatura OU prestar primeiros socorros', mas a entrada do glossário só descreve as duas primeiras opções. Os primeiros socorros aparecem na regra de Nocautear (teste de Sabedoria CD 10 com Medicina). Confirmar se primeiros socorros é uma terceira opção da ação Ajudar."},
 "descricao_curta":"Concede Vantagem no próximo teste de atributo de um aliado (com perícia/ferramenta em que você é proficiente) ou na próxima jogada de ataque de um aliado contra um inimigo a até 1,5 m de você.",
 "opcoes":[
  {"id":"ajudar_teste","efeitos":[{"tipo":"vantagem","alvo":"teste_de_atributo","modo":"vantagem","beneficiario":"aliado","requer":"proficiencia_sua_na_pericia_ou_ferramenta","duracao":"ate_inicio_do_seu_proximo_turno"}]},
  {"id":"ajudar_ataque","efeitos":[{"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem","beneficiario":"aliado","alcance_m":1.5,"duracao":"ate_inicio_do_seu_proximo_turno"}]}]},

{"id":"analisar","nome":"Analisar","custo":"acao","fonte":f(361),"revisao":OK,
 "descricao_curta":"Teste de Inteligência para recordar informação. Perícias aplicáveis: Arcanismo, História, Investigação, Natureza, Religião.",
 "teste":{"atributo":"INT","pericias":["arcanismo","historia","investigacao","natureza","religiao"]}},

{"id":"atacar","nome":"Atacar","custo":"acao","fonte":f(362),"revisao":OK,
 "descricao_curta":"Realiza um ataque com arma ou um Ataque Desarmado. Permite equipar/desequipar uma arma como parte da ação e mover-se entre ataques quando você tem Ataque Extra.",
 "efeitos":[{"tipo":"conceder_ataque","quantidade":{"op":"max","args":["1","ataques_por_acao"]}}]},

{"id":"correr","nome":"Correr","custo":"acao","fonte":f(365),"revisao":OK,
 "descricao_curta":"Ganha movimento adicional neste turno igual ao seu Deslocamento já modificado; pode usar um deslocamento especial no lugar.",
 "efeitos":[{"tipo":"modificador","alvo":"movimento_do_turno","valor":["deslocamento"],"empilha":"soma","permite_deslocamento_especial":True}]},

{"id":"desengajar","nome":"Desengajar","custo":"acao","fonte":f(366),"revisao":OK,
 "descricao_curta":"Seu movimento não provoca Ataques de Oportunidade pelo resto do turno.",
 "efeitos":[{"tipo":"impedir","alvo":"ataque_de_oportunidade_provocado_por_voce","duracao":"resto_do_turno"}]},

{"id":"esconder","nome":"Esconder","custo":"acao","fonte":f(368),"revisao":OK,
 "descricao_curta":"Teste de Destreza (Furtividade) CD 15, estando Totalmente Obscurecido ou atrás de Cobertura de Três Quartos/Total e fora da linha de visão dos inimigos. Em caso de sucesso você fica Invisível.",
 "teste":{"atributo":"DES","pericia":"furtividade","cd":15},
 "pre_requisitos":[{"tipo":"estado","alguma":["totalmente_obscurecido","cobertura:tres_quartos","cobertura:total"]},
                   {"tipo":"estado","chave":"fora_da_linha_de_visao_de_inimigos"}],
 "efeitos":[{"tipo":"conceder_condicao","condicao_id":"invisivel","em":"sucesso",
             "cd_para_ser_encontrado":"total_do_seu_teste"}],
 "encerramento":[{"gatilho":"som_mais_alto_que_sussurro"},{"gatilho":"inimigo_encontra_voce"},
                 {"gatilho":"voce_realiza_jogada_de_ataque"},{"gatilho":"conjura_magia_com_componente_verbal"}]},

{"id":"esquivar","nome":"Esquivar","custo":"acao","fonte":f(368),"revisao":OK,
 "descricao_curta":"Até o início do seu próximo turno, ataques contra você têm Desvantagem (se você puder ver o atacante) e suas salvaguardas de Destreza têm Vantagem.",
 "efeitos":[
  {"tipo":"vantagem","alvo":"jogada_de_ataque_contra_voce","modo":"desvantagem","condicao":{"todas":["voce_pode_ver_o_atacante"]},"duracao":"ate_inicio_do_seu_proximo_turno"},
  {"tipo":"vantagem","alvo":"salvaguarda:DES","modo":"vantagem","duracao":"ate_inicio_do_seu_proximo_turno"}],
 "perde_beneficio_se":[{"condicao_id":"incapacitado"},{"chave":"deslocamento_zero"}]},

{"id":"influenciar","nome":"Influenciar","custo":"acao","fonte":f(370),"revisao":OK,
 "descricao_curta":"Tenta fazer um monstro realizar algo. Só exige teste se ele estiver hesitante; CD 15 ou o valor de Inteligência do monstro, o que for maior.",
 "teste":{"cd":{"op":"max","args":["15","int_do_monstro"]},
  "opcoes":[{"atributo":"CAR","pericia":"atuacao","interacao":"entreter"},
            {"atributo":"CAR","pericia":"enganacao","interacao":"enganar"},
            {"atributo":"CAR","pericia":"intimidacao","interacao":"intimidar"},
            {"atributo":"CAR","pericia":"persuasao","interacao":"persuadir"},
            {"atributo":"SAB","pericia":"lidar_com_animais","interacao":"convencer Fera ou Monstruosidade"}]},
 "modificado_por_atitude":True,
 "em_falha":"esperar 24 horas (ou o período que o Mestre definir) antes de tentar da mesma maneira"},

{"id":"preparar","nome":"Preparar","custo":"acao","fonte":f(373),"revisao":OK,
 "descricao_curta":"Define um gatilho perceptível e a ação (ou movimento) de resposta, executada com sua Reação antes do início do seu próximo turno. Magia preparada é conjurada na hora, gasta os recursos e exige Concentração até liberar.",
 "efeitos":[{"tipo":"conceder_acao","id":"reacao_preparada","custo":"reacao","duracao":"ate_inicio_do_seu_proximo_turno"}],
 "regras_de_magia":{"tempo_de_conjuracao_exigido":"acao","exige_concentracao":True,
  "se_concentracao_interrompida":"a magia se dissipa sem efeito e os recursos já foram gastos"}},

{"id":"procurar","nome":"Procurar","custo":"acao","fonte":f(373),"revisao":OK,
 "descricao_curta":"Teste de Sabedoria para perceber algo não evidente. Perícias: Intuição, Medicina, Percepção, Sobrevivência.",
 "teste":{"atributo":"SAB","pericias":["intuicao","medicina","percepcao","sobrevivencia"]}},

{"id":"usar_magia","nome":"Usar Magia","custo":"acao","fonte":f(377),"revisao":OK,
 "descricao_curta":"Conjura uma magia com tempo de conjuração de uma ação, ou usa característica/item mágico que exija esta ação. Conjuração de 1 minuto ou mais exige repetir a ação a cada turno mantendo Concentração.",
 "regras_de_conjuracao_longa":{"repetir_por_turno":True,"exige_concentracao":True,
  "se_concentracao_interrompida":"a magia falha, mas o espaço de magia não é gasto"}},

{"id":"usar_objeto","nome":"Usar Objeto","custo":"acao","fonte":f(377),"revisao":OK,
 "descricao_curta":"Usa um objeto não mágico que exija uma ação. Interações simples com objetos acontecem de graça durante outra ação."},
]

json.dump({"colecao":"acoes","total":len(A),"itens":A},
          open(os.path.join(D,'acoes.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('acoes:', len(A))
