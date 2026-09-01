# -*- coding: utf-8 -*-
import json, os
BASE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(BASE, 'dados')
def f(p): return {"capitulo": "ap_c", "pagina_livro": p, "pagina_pdf": p + 4}
def V(alvo, tipo, **kw): return dict({"tipo": "vantagem", "alvo": alvo, "modo": tipo}, **kw)

C = []
C.append({"id":"amedrontado","nome":"Amedrontado","fonte":f(361),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Você tem Desvantagem enquanto a fonte do medo estiver na sua linha de visão e não pode se aproximar dela voluntariamente.",
 "efeitos":[
  V("teste_de_atributo","desvantagem",condicao={"todas":["fonte_do_medo_na_linha_de_visao"]}),
  V("jogada_de_ataque","desvantagem",condicao={"todas":["fonte_do_medo_na_linha_de_visao"]}),
  {"tipo":"impedir","alvo":"aproximar_voluntariamente_de","referencia":"fonte_do_medo"}]})

C.append({"id":"atordoado","nome":"Atordoado","fonte":f(363),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Você fica Incapacitado, falha automaticamente em salvaguardas de FOR e DES, e ataques contra você têm Vantagem.",
 "efeitos":[
  {"tipo":"conceder_condicao","condicao_id":"incapacitado"},
  {"tipo":"falha_automatica","alvo":"salvaguarda:FOR"},
  {"tipo":"falha_automatica","alvo":"salvaguarda:DES"},
  V("jogada_de_ataque_contra_voce","vantagem")]})

C.append({"id":"caido","nome":"Caído","fonte":f(364),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Só pode rastejar ou gastar metade do Deslocamento para se levantar; Desvantagem nos seus ataques; ataques contra você têm Vantagem se a até 1,5 m, senão Desvantagem.",
 "efeitos":[
  {"tipo":"restringir_movimento","opcoes":["rastejar","levantar"],
   "custo_para_levantar":{"op":"div_arred_baixo","args":["deslocamento","2"]},
   "condicao":{"nao":"deslocamento_zero"}},
  V("jogada_de_ataque","desvantagem"),
  V("jogada_de_ataque_contra_voce","vantagem",condicao={"todas":["atacante_a_ate_1_5m"]}),
  V("jogada_de_ataque_contra_voce","desvantagem",condicao={"nao":"atacante_a_ate_1_5m"})]})

C.append({"id":"cego","nome":"Cego","fonte":f(364),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Você não enxerga, falha automaticamente em testes que dependam da visão; ataques contra você têm Vantagem e os seus, Desvantagem.",
 "efeitos":[
  {"tipo":"falha_automatica","alvo":"teste_de_atributo","condicao":{"todas":["depende_de:visao"]}},
  V("jogada_de_ataque_contra_voce","vantagem"),
  V("jogada_de_ataque","desvantagem")]})

C.append({"id":"contido","nome":"Contido","fonte":f(365),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Deslocamento 0; ataques contra você têm Vantagem e os seus, Desvantagem; Desvantagem em salvaguardas de DES.",
 "efeitos":[
  {"tipo":"travar_deslocamento","valor":0,"impede_aumento":True},
  V("jogada_de_ataque_contra_voce","vantagem"),
  V("jogada_de_ataque","desvantagem"),
  V("salvaguarda:DES","desvantagem")]})

C.append({"id":"enfeiticado","nome":"Enfeitiçado","fonte":f(368),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Não pode atacar nem ter como alvo quem o enfeitiçou; o enfeitiçador tem Vantagem em interações sociais com você.",
 "efeitos":[
  {"tipo":"impedir","alvo":"atacar_ou_alvejar","referencia":"enfeiticador"},
  {"tipo":"vantagem","alvo":"interacao_social_contra_voce","modo":"vantagem","beneficiario":"enfeiticador"}]})

C.append({"id":"envenenado","nome":"Envenenado","fonte":f(368),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Desvantagem em jogadas de ataque e testes de atributo.",
 "efeitos":[V("jogada_de_ataque","desvantagem"), V("teste_de_atributo","desvantagem")]})

C.append({"id":"exaustao","nome":"Exaustão","fonte":f(368),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Condição acumulativa em 6 níveis; reduz Testes de D20 e Deslocamento conforme o nível. No nível 6 você morre.",
 "acumulativa":True,"nivel_maximo":6,"efeito_no_nivel_maximo":"morte",
 "efeitos":[
  {"tipo":"modificador","alvo":"teste_d20","valor":{"op":"mult","args":["-2","nivel_exaustao"]},"empilha":"soma"},
  {"tipo":"modificador","alvo":"deslocamento","valor":{"op":"mult","args":["-1.5","nivel_exaustao"]},"unidade":"m","empilha":"soma"},
  {"tipo":"remocao","gatilho":"descanso_longo","quantidade":1}]})

C.append({"id":"imobilizado","nome":"Imobilizado","fonte":f(369),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Deslocamento 0; Desvantagem em ataques contra qualquer alvo que não seja o imobilizador; pode ser arrastado pelo imobilizador.",
 "efeitos":[
  {"tipo":"travar_deslocamento","valor":0,"impede_aumento":True},
  V("jogada_de_ataque","desvantagem",condicao={"nao":"alvo_e:imobilizador"}),
  {"tipo":"efeito_narrativo","chave":"movel","texto":"O imobilizador pode arrastá-lo ou carregá-lo; cada metro custa 1 metro adicional, salvo se você for Minúsculo ou dois ou mais tamanhos menor."}],
 "encerramento":[
  {"gatilho":"teste_para_escapar","teste":{"opcoes":["FOR:atletismo","DES:acrobacia"],"cd":"cd_do_imobilizador"},"custo":"acao"},
  {"gatilho":"imobilizador_incapacitado"},
  {"gatilho":"distancia_maior_que_alcance_da_imobilizacao"}]})

C.append({"id":"incapacitado","nome":"Incapacitado","fonte":f(369),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Não pode executar ação, Ação Bônus ou Reação; perde Concentração; não pode falar; Desvantagem na Iniciativa se estiver Incapacitado ao jogá-la.",
 "efeitos":[
  {"tipo":"impedir","alvo":"acao"},{"tipo":"impedir","alvo":"acao_bonus"},{"tipo":"impedir","alvo":"reacao"},
  {"tipo":"impedir","alvo":"concentracao"},{"tipo":"impedir","alvo":"falar"},
  V("iniciativa","desvantagem")]})

C.append({"id":"inconsciente","nome":"Inconsciente","fonte":f(369),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Você fica Caído e Incapacitado, solta o que segura, Deslocamento 0, falha em salvaguardas de FOR e DES, e ataques a até 1,5 m são Acertos Críticos.",
 "efeitos":[
  {"tipo":"conceder_condicao","condicao_id":"caido","persiste_apos_encerrar":True},
  {"tipo":"conceder_condicao","condicao_id":"incapacitado"},
  {"tipo":"travar_deslocamento","valor":0,"impede_aumento":True},
  V("jogada_de_ataque_contra_voce","vantagem"),
  {"tipo":"falha_automatica","alvo":"salvaguarda:FOR"},
  {"tipo":"falha_automatica","alvo":"salvaguarda:DES"},
  {"tipo":"acerto_critico_automatico","condicao":{"todas":["atacante_a_ate_1_5m"]}},
  {"tipo":"efeito_narrativo","chave":"alheio","texto":"Você não está ciente do que está ao seu redor e solta qualquer coisa que estiver segurando."}]})

C.append({"id":"invisivel","nome":"Invisível","fonte":f(370),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Vantagem na Iniciativa; oculto para efeitos que exigem ver o alvo; ataques contra você têm Desvantagem e os seus, Vantagem — nada disso vale contra quem consegue vê-lo.",
 "efeitos":[
  V("iniciativa","vantagem"),
  {"tipo":"efeito_narrativo","chave":"oculto","texto":"Não é afetado por efeitos que exijam ver o alvo, a menos que o criador do efeito possa vê-lo. O equipamento vestido ou carregado também fica oculto."},
  V("jogada_de_ataque_contra_voce","desvantagem",condicao={"nao":"atacante_pode_ve_lo"}),
  V("jogada_de_ataque","vantagem",condicao={"nao":"alvo_pode_ve_lo"})]})

C.append({"id":"paralisado","nome":"Paralisado","fonte":f(372),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Você fica Incapacitado, Deslocamento 0, falha em salvaguardas de FOR e DES, ataques contra você têm Vantagem e são críticos a até 1,5 m.",
 "efeitos":[
  {"tipo":"conceder_condicao","condicao_id":"incapacitado"},
  {"tipo":"travar_deslocamento","valor":0,"impede_aumento":True},
  {"tipo":"falha_automatica","alvo":"salvaguarda:FOR"},
  {"tipo":"falha_automatica","alvo":"salvaguarda:DES"},
  V("jogada_de_ataque_contra_voce","vantagem"),
  {"tipo":"acerto_critico_automatico","condicao":{"todas":["atacante_a_ate_1_5m"]}}]})

C.append({"id":"petrificado","nome":"Petrificado","fonte":f(372),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Transformado em substância sólida: Incapacitado, Deslocamento 0, Resistência a todo dano, Imunidade à condição Envenenado, peso ×10 e para de envelhecer.",
 "efeitos":[
  {"tipo":"conceder_condicao","condicao_id":"incapacitado"},
  {"tipo":"travar_deslocamento","valor":0,"impede_aumento":True},
  V("jogada_de_ataque_contra_voce","vantagem"),
  {"tipo":"falha_automatica","alvo":"salvaguarda:FOR"},
  {"tipo":"falha_automatica","alvo":"salvaguarda:DES"},
  {"tipo":"alterar_dano","tipo_dano":"todos","operacao":"resistencia"},
  {"tipo":"alterar_condicao","condicao_id":"envenenado","operacao":"imunidade"},
  {"tipo":"efeito_narrativo","chave":"transformado","texto":"Você e seus objetos não mágicos viram substância sólida inanimada; seu peso aumenta dez vezes e você para de envelhecer."}]})

C.append({"id":"surdo","nome":"Surdo","fonte":f(375),"revisao":{"status":"ok","notas":""},
 "descricao_curta":"Você não ouve e falha automaticamente em testes de atributo que dependam da audição.",
 "efeitos":[{"tipo":"falha_automatica","alvo":"teste_de_atributo","condicao":{"todas":["depende_de:audicao"]}}]})

json.dump({"colecao":"condicoes","total":len(C),"itens":C},
          open(os.path.join(D,'condicoes.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('condicoes:', len(C))
