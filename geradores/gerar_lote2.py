# -*- coding: utf-8 -*-
"""Lote 2: catálogos fechados que as Classes referenciam (idiomas, ferramentas,
propriedades e maestrias de arma, escolas de magia). Corrige também a ação Ajudar."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def f(cap, livro): return {"capitulo": cap, "pagina_livro": livro, "pagina_pdf": livro + 4}
def w(p, o):
    json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ------------------------------------------------------------ idiomas (cap. 2, p. 37)
COMUNS = [("comum","Comum","Sigil"),("linguagem_de_sinais_comum","Linguagem de Sinais Comum","Sigil"),
 ("draconico","Dracônico","Dragões"),("anao","Anão","Anões"),("elfico","Élfico","Elfos"),
 ("gigante","Gigante","Gigantes"),("gnomico","Gnômico","Gnomos"),("goblin","Goblin","Goblinoides"),
 ("pequenino","Pequenino","Pequeninos"),("orc","Orc","Orcs")]
RAROS = [("abissal","Abissal","Demônios do Abismo"),("celestial","Celestial","Celestiais"),
 ("dialeto_obscuro","Dialeto Obscuro","Aberrações"),("druidico","Druídico","Círculos druídicos"),
 ("giria_dos_ladroes","Gíria dos Ladrões","Várias guildas criminosas"),
 ("infernal","Infernal","Diabos dos Nove Infernos"),("primordial","Primordial","Elementais"),
 ("silvestre","Silvestre","A Faéria"),("subcomum","Subcomum","A Umbraeterna")]
itens = ([{"id":i,"nome":n,"raridade":"comum","origem":o} for i,n,o in COMUNS] +
         [{"id":i,"nome":n,"raridade":"raro","origem":o} for i,n,o in RAROS])
for it in itens:
    if it["id"] == "primordial":
        it["dialetos"] = ["Aquan","Auran","Ignan","Terran"]
        it["nota"] = "Quem conhece um dialeto se comunica com quem conhece outro."
w('catalogos/idiomas.json', {"catalogo":"idiomas","nome":"Idiomas","fonte":f(2,37),
  "total":len(itens),"itens":itens,
  "nota":"Todo personagem sabe Comum + 2 idiomas da tabela Idiomas Comuns. Idiomas raros só por característica que os conceda."})

# ------------------------------------------- propriedades de arma (cap. 6, p. 213-214)
PROPS = [
 ("acuidade","Acuidade","Use o modificador de Força ou Destreza (o mesmo nas duas jogadas) para ataque e dano.",213),
 ("alcance","Alcance","Dois números em metros: alcance normal e máximo. Além do normal, Desvantagem; além do máximo, não pode atacar.",213),
 ("arremesso","Arremesso","Pode ser arremessada para um ataque à distância, sacando-a como parte do ataque. Arma corpo a corpo usa o mesmo modificador do ataque corpo a corpo.",213),
 ("duas_maos","Duas Mãos","Exige as duas mãos para atacar.",214),
 ("extensao","Extensão","Soma 1,5 m ao seu alcance com ela, inclusive para Ataques de Oportunidade.",214),
 ("leve","Leve","Ao executar a ação Atacar com uma arma Leve, pode atacar de novo como Ação Bônus com outra arma Leve, sem somar o modificador de atributo ao dano (salvo se negativo).",214),
 ("municao","Munição","Só ataca à distância com munição disponível; cada ataque gasta uma peça. Recupera metade (arred. baixo) em 1 minuto após a luta.",214),
 ("pesada","Pesada","Desvantagem nas jogadas de ataque se For < 13 (corpo a corpo) ou Des < 13 (à distância).",214),
 ("recarga","Recarga","Dispara só uma peça de munição por ação, Ação Bônus ou Reação, independentemente do número de ataques.",214),
 ("versatil","Versátil","Usável com uma ou duas mãos; o dano entre parênteses vale para o uso com as duas mãos.",214)]
w('catalogos/propriedades_de_arma.json', {"catalogo":"propriedades_de_arma","nome":"Propriedades de Arma",
  "fonte":f(6,213),"total":len(PROPS),
  "itens":[{"id":i,"nome":n,"descricao_curta":d,"fonte":f(6,p)} for i,n,d,p in PROPS]})

# -------------------------------------------- maestrias de arma (cap. 6, p. 214)
MAESTRIAS = [
 ("afligir","Afligir","Se acertar e causar dano, você tem Vantagem na próxima jogada de ataque contra essa criatura antes do fim do seu próximo turno.",
  [{"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"vantagem","condicao":{"todas":["mesmo_alvo_atingido"]},"duracao":"ate_o_fim_do_seu_proximo_turno"}]),
 ("agil","Ágil","O ataque adicional da propriedade Leve pode ser feito como parte da ação Atacar, em vez de Ação Bônus. Uma vez por turno.",
  [{"tipo":"efeito_narrativo","chave":"ataque_leve_na_acao_atacar","texto":"O ataque extra de arma Leve passa a caber na ação Atacar; uma vez por turno."}]),
 ("derrubar","Derrubar","Se acertar, o alvo faz salvaguarda de Constituição (CD 8 + modificador usado no ataque + BP) ou fica Caído.",
  [{"tipo":"conceder_condicao","condicao_id":"caido","em":"falha_na_salvaguarda",
    "salvaguarda":{"atributo":"CON","cd":["8","mod_do_ataque","prof"]}}]),
 ("drenar","Drenar","Se acertar, o alvo tem Desvantagem na próxima jogada de ataque dele antes do início do seu próximo turno.",
  [{"tipo":"vantagem","alvo":"jogada_de_ataque","modo":"desvantagem","beneficiario":"alvo_atingido","duracao":"ate_inicio_do_seu_proximo_turno"}]),
 ("empurrar","Empurrar","Se acertar, você pode empurrar o alvo até 3 metros para longe, se ele for Grande ou menor.",
  [{"tipo":"efeito_narrativo","chave":"empurrao","texto":"Empurra o alvo até 3 m; só contra criaturas Grandes ou menores."}]),
 ("garantido","Garantido","Se errar, causa dano igual ao modificador de atributo usado no ataque, do mesmo tipo da arma.",
  [{"tipo":"efeito_narrativo","chave":"dano_no_erro","texto":"No erro, causa dano igual ao modificador de atributo do ataque, do tipo da arma."}]),
 ("lentidao","Lentidão","Se acertar e causar dano, pode reduzir o Deslocamento do alvo em 3 metros até o início do seu próximo turno (não acumula além de 3 m).",
  [{"tipo":"modificador","alvo":"deslocamento","valor":["-3"],"unidade":"m","empilha":"maior_valor",
    "beneficiario":"alvo_atingido","duracao":"ate_inicio_do_seu_proximo_turno"}]),
 ("trespassar","Trespassar","Se acertar um ataque corpo a corpo, pode atacar uma segunda criatura a até 1,5 m da primeira e dentro do seu alcance, sem somar o modificador ao dano. Uma vez por turno.",
  [{"tipo":"conceder_ataque","quantidade":["1"],"condicao":{"todas":["segundo_alvo_a_ate_1_5m_do_primeiro"]},"frequencia":"uma_vez_por_turno"}])]
w('catalogos/maestrias_de_arma.json', {"catalogo":"maestrias_de_arma","nome":"Propriedades de Maestria",
  "fonte":f(6,214),"total":len(MAESTRIAS),
  "nota":"Só utilizável por quem tenha uma característica (ex.: Maestria em Armas) que desbloqueie a propriedade.",
  "itens":[{"id":i,"nome":n,"descricao_curta":d,"efeitos":e,"fonte":f(6,214)} for i,n,d,e in MAESTRIAS]})

# ------------------------------------------------ escolas de magia (cap. 7, p. 236)
ESCOLAS = [("abjuracao","Abjuração","Previne ou neutraliza efeitos nocivos"),
 ("adivinhacao","Adivinhação","Revela informações"),("encantamento","Encantamento","Influencia mentes"),
 ("evocacao","Evocação","Canaliza energia para criar efeitos frequentemente destrutivos"),
 ("ilusao","Ilusão","Engana os sentidos ou a mente"),("invocacao","Invocação","Transporta criaturas ou objetos"),
 ("necromancia","Necromancia","Manipula a vida e a morte"),
 ("transmutacao","Transmutação","Transforma criaturas ou objetos")]
w('catalogos/escolas_de_magia.json', {"catalogo":"escolas_de_magia","nome":"Escolas de Magia",
  "fonte":f(7,236),"total":len(ESCOLAS),"nota":"As escolas não têm regras próprias; outras regras podem referenciá-las.",
  "itens":[{"id":i,"nome":n,"descricao_curta":d} for i,n,d in ESCOLAS]})

# ------------------------------------------------------ ferramentas (cap. 6, p. 220-221)
ART = [
 ("ferramentas_de_carpinteiro","Ferramentas de Carpinteiro","FOR",8,3.0),
 ("ferramentas_de_cartografo","Ferramentas de Cartógrafo","SAB",15,3.0),
 ("ferramentas_de_coureiro","Ferramentas de Coureiro","DES",5,2.5),
 ("ferramentas_de_entalhador","Ferramentas de Entalhador","DES",1,2.5),
 ("ferramentas_de_ferreiro","Ferramentas de Ferreiro","FOR",20,4.0),
 ("ferramentas_de_funileiro","Ferramentas de Funileiro","DES",50,5.0),
 ("ferramentas_de_joalheiro","Ferramentas de Joalheiro","INT",25,1.0),
 ("ferramentas_de_oleiro","Ferramentas de Oleiro","INT",10,1.5),
 ("ferramentas_de_pedreiro","Ferramentas de Pedreiro","FOR",10,4.0),
 ("ferramentas_de_sapateiro","Ferramentas de Sapateiro","DES",5,2.5),
 ("ferramentas_de_tecelao","Ferramentas de Tecelão","DES",1,2.5),
 ("ferramentas_de_vidreiro","Ferramentas de Vidreiro","INT",30,2.5),
 ("suprimentos_de_alquimista","Suprimentos de Alquimista","INT",50,4.0),
 ("suprimentos_de_caligrafo","Suprimentos de Calígrafo","DES",10,2.5),
 ("suprimentos_de_cervejeiro","Suprimentos de Cervejeiro","INT",20,4.5),
 ("suprimentos_de_pintor","Suprimentos de Pintor","SAB",10,2.5),
 ("utensilios_de_cozinheiro","Utensílios de Cozinheiro","SAB",1,4.0)]
OUTRAS = [
 ("ferramentas_de_ladrao","Ferramentas de Ladrão","DES",25,0.5,None),
 ("ferramentas_de_navegador","Ferramentas de Navegador","SAB",25,1.0,None),
 # As variantes vêm da linha "Variantes:" da própria entrada (p. 221), com custo e
 # peso impressos. Antes eram só o nome, e por isso o Bardo e o Músico não tinham o que
 # escolher — a dúvida "o livro não enumera os instrumentos" era falsa: ele enumera aqui.
 ("instrumento_musical","Instrumento Musical","CAR",None,None,
  [("alaude","Alaúde",35,"po",1.0), ("flauta","Flauta",2,"po",0.5),
   ("flauta_de_pan","Flauta de Pan",12,"po",1.0), ("gaita_de_foles","Gaita de Foles",30,"po",3.0),
   ("lira","Lira",30,"po",1.0), ("obo","Oboé",2,"po",0.5),
   ("tambor","Tambor",6,"po",1.5), ("trombeta","Trombeta",3,"po",1.0),
   ("violino","Violino",30,"po",0.5), ("xilofone","Xilofone",25,"po",5.0)]),
 ("kit_de_disfarce","Kit de Disfarce","CAR",25,1.5,None),
 ("kit_de_falsificacao","Kit de Falsificação","DES",15,2.5,None),
 ("kit_de_herbalismo","Kit de Herbalismo","INT",5,1.5,None),
 # O livro imprime o custo das variantes do Kit de Jogos, mas não o peso (p. 221).
 ("kit_de_jogos","Kit de Jogos","SAB",None,None,
  [("dados","Dados",1,"pp",None), ("xadrez_do_dragao","Xadrez-do-Dragão",1,"po",None),
   ("baralho","Baralho",5,"pp",None),
   ("conjunto_do_jogo_dos_tres_dragoes","Conjunto do Jogo dos Três Dragões",1,"po",None)]),
 ("kit_de_veneno","Kit de Veneno","INT",50,1.0,None)]
itens = [{"id":i,"nome":n,"grupo":"artesao","atributo":a,"custo_po":c,"peso_kg":p,
          "proficiencia_separada":True,"fonte":f(6,220)} for i,n,a,c,p in ART]
for i,n,a,c,p,v in OUTRAS:
    d = {"id":i,"nome":n,"grupo":"outras","atributo":a,"custo_po":c,"peso_kg":p,"fonte":f(6,221)}
    if v:
        FATOR = {"po": 100, "pp": 10, "pc": 1}
        d["variantes"] = [
            {"id": vid, "nome": vnome,
             "custo": {"valor": val, "moeda": moeda, "em_pc": val * FATOR[moeda]},
             "peso_kg": peso}
            for vid, vnome, val, moeda, peso in v]
        d["nota"] = "Custo e peso variam conforme a variante."
    itens.append(d)
w('catalogos/ferramentas.json', {"catalogo":"ferramentas","nome":"Ferramentas","fonte":f(6,220),
  "total":len(itens),"itens":itens,
  "nota":"Cada Ferramenta de Artesão exige proficiência separada. Proficiência soma o BP ao teste; proficiência na perícia usada no mesmo teste dá Vantagem. Listas de 'Fabricação' de cada ferramenta não foram extraídas nesta fase (dependem do catálogo de itens do cap. 6)."})

# ------------------------------------------------------- correção: ação Ajudar
p = os.path.join(D, 'acoes.json')
d = json.load(open(p, encoding='utf-8'))
for a in d['itens']:
    if a['id'] == 'ajudar':
        a['descricao_curta'] = ("Concede Vantagem no próximo teste de atributo de um aliado (com perícia/ferramenta "
            "em que você é proficiente), ou na próxima jogada de ataque de um aliado contra um inimigo a até 1,5 m, "
            "ou presta primeiros socorros a uma criatura Inconsciente com 0 PV.")
        a['opcoes'].append({"id":"ajudar_primeiros_socorros",
          "descricao_curta":"Estabiliza uma criatura Inconsciente com 0 Pontos de Vida.",
          "teste":{"atributo":"SAB","pericia":"medicina","cd":10},
          "fonte":f("ap_c",371),
          "efeitos":[{"tipo":"efeito_narrativo","chave":"primeiros_socorros",
                      "texto":"Em caso de sucesso, a criatura fica Estável (0 PV, sem Salvaguardas Contra Morte)."}]})
        a['revisao'] = {"status":"ok","notas":"Confirmado pelo usuário em 2026-08-31: primeiros socorros é a terceira opção da ação Ajudar, não uma ação separada. Regra e CD extraídos de p. 371 (nocaute)."}
json.dump(d, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('lote 2 gerado; Ajudar corrigida')
