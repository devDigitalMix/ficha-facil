# -*- coding: utf-8 -*-
"""Fase 2b — Classe Guerreiro (cap. 3, p. 127-135) e suas 4 subclasses."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

PERICIAS_GUERREIRO = ["acrobacia","atletismo","historia","intimidacao","intuicao",
                      "lidar_com_animais","percepcao","persuasao","sobrevivencia"]

# ------------------------------------------------------------------ tabela
def faixa(m):
    out = {}
    for (a, b), v in m.items():
        for n in range(a, b + 1): out[n] = v
    return out
BP = faixa({(1,4):2,(5,8):3,(9,12):4,(13,16):5,(17,20):6})
FOLEGO = faixa({(1,3):2,(4,9):3,(10,20):4})
MAESTRIA = faixa({(1,3):3,(4,9):4,(10,15):5,(16,20):6})
CAR = {1:["estilo_de_luta","maestria_em_arma","recuperar_folego"],
 2:["mente_tatica","surto_de_acao"], 3:["subclasse_de_guerreiro"],
 4:["aumento_no_valor_de_atributo"], 5:["ajuste_tatico","ataque_extra"],
 6:["aumento_no_valor_de_atributo"], 7:["caracteristica_de_subclasse"],
 8:["aumento_no_valor_de_atributo"], 9:["indomavel","mestre_tatico"],
 10:["caracteristica_de_subclasse"], 11:["dois_ataques_extras"],
 12:["aumento_no_valor_de_atributo"], 13:["ataques_estudados","indomavel"],
 14:["aumento_no_valor_de_atributo"], 15:["caracteristica_de_subclasse"],
 16:["aumento_no_valor_de_atributo"], 17:["indomavel","surto_de_acao"],
 18:["caracteristica_de_subclasse"], 19:["dadiva_epica"], 20:["tres_ataques_extras"]}

classe = {
 "id": "guerreiro", "nome": "Guerreiro", "fonte": f(127), "revisao": OK,
 "descricao_curta": "Combatente de competência incomparável com armas e armaduras, que domina vários estilos de combate e sempre tem a ferramenta certa para a situação.",
 "dado_de_vida": 10,
 "atributo_primario": ["FOR", "DES"],
 "atributo_primario_modo": "um_ou_outro",
 "salvaguardas_primarias": ["FOR", "CON"],
 "nivel_subclasse": 3,
 "conjuracao": None,
 "conjuracao_por_subclasse": True,
 "subclasses": ["campeao", "cavaleiro_mistico", "combatente_psiquico", "mestre_da_batalha"],
 "proficiencias_iniciais": [
   {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "FOR", "nivel_dominio": "proficiente"},
   {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "CON", "nivel_dominio": "proficiente"},
   {"id": "guerreiro_pericias_iniciais", "tipo": "escolha", "rotulo": "Escolha 2 perícias",
    "quantidade": 2, "momento": "criacao",
    "de": {"catalogo": "pericias", "chaves": PERICIAS_GUERREIRO},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                  "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}},
   {"tipo": "conceder_proficiencia", "categoria": "arma", "chave": "categoria:simples", "nivel_dominio": "proficiente"},
   {"tipo": "conceder_proficiencia", "categoria": "arma", "chave": "categoria:marcial", "nivel_dominio": "proficiente"}],
 "treinamento_com_armadura": ["leve", "media", "pesada", "escudo"],
 "equipamento_inicial": {"opcoes": [
   {"id": "A", "itens": [{"item": "cota_de_malha"}, {"item": "espada_grande"}, {"item": "mangual"},
                         {"item": "azagaia", "quantidade": 8},
                         {"item": "kit_de_explorador_de_masmorras"}], "moedas": {"po": 4}},
   {"id": "B", "itens": [{"item": "armadura_de_couro_batido"}, {"item": "cimitarra"},
                         {"item": "espada_curta"}, {"item": "arco_longo"},
                         {"item": "flecha", "quantidade": 20}, {"item": "aljava"},
                         {"item": "kit_de_explorador_de_masmorras"}], "moedas": {"po": 11}},
   {"id": "C", "moedas": {"po": 155}}],
   "revisao": {"status": "duvida", "notas": "Ids de item dependem do catálogo do cap. 6, ainda não extraído. Referência pendente."}},
 "progressao": [{"nivel": n, "bonus_de_proficiencia": BP[n], "caracteristicas": CAR[n],
                 "colunas": {"recuperar_folego": FOLEGO[n], "maestria_em_arma": MAESTRIA[n]}}
                for n in range(1, 21)],
 "colunas_da_tabela": {"recuperar_folego": {"nome": "Recuperar Fôlego", "tipo": "inteiro"},
                       "maestria_em_arma": {"nome": "Maestria em Armas", "tipo": "inteiro"}},
 "multiclasse": {"adquire": ["dado_de_vida", "proficiencia:arma:categoria:marcial",
                             "treinamento_armadura:leve", "treinamento_armadura:media",
                             "treinamento_armadura:escudo"],
                 "fonte": f(127),
                 "nota": "Registrado para a fase de multiclasse; não aplicado agora."}}

cl = rd('classes.json')
cl['itens'] = [c for c in cl['itens'] if c['id'] != 'guerreiro'] + [classe]
cl['total'] = len(cl['itens'])
wr('classes.json', cl)

# ------------------------------------------------------------ características
C = rd('caracteristicas.json')
C['itens'] = [c for c in C['itens'] if c.get('classe') != 'guerreiro']
novos = []
def car(id_, nome, nivel, pag, desc, efeitos, **kw):
    d = {"id": id_, "nome": nome, "classe": "guerreiro", "nivel": nivel, "fonte": f(pag),
         "revisao": kw.pop("revisao", OK), "descricao_curta": desc, "efeitos": efeitos}
    d.update(kw); novos.append(d)

car("estilo_de_luta", "Estilo de Luta", 1, 127,
 "Você tem um talento de Estilo de Luta à sua escolha. Sempre que sobe de nível de Guerreiro pode trocá-lo por outro talento de Estilo de Luta.",
 [{"id": "guerreiro_estilo_de_luta", "tipo": "escolha", "rotulo": "Escolha um talento de Estilo de Luta",
   "quantidade": 1, "momento": "nivel_1", "reescolhivel": True,
   "reescolha_em": "cada_nivel_de_guerreiro",
   "de": {"catalogo": "talentos", "filtro": {"categoria": "estilo_de_luta"}},
   "efeito_por_item_escolhido": {"tipo": "conceder_talento", "talento_id": "{{escolhido}}"}}])

car("maestria_em_arma", "Maestria em Arma", 1, 127,
 "Você pode usar as propriedades de maestria de um número de tipos de armas Simples ou Marciais à sua escolha, conforme a coluna Maestria em Armas. A cada Descanso Longo pode trocar uma dessas escolhas.",
 [{"id": "guerreiro_maestrias", "tipo": "escolha", "rotulo": "Escolha os tipos de arma com maestria",
   "quantidade": "coluna:maestria_em_arma", "momento": "nivel_1",
   "reescolhivel": True, "reescolha_em": "descanso_longo", "reescolha_quantidade": 1,
   "de": {"catalogo": "itens", "filtro": {"categoria": "arma", "grupo": ["simples", "marcial"]}},
   "efeito_por_item_escolhido": {"tipo": "efeito_narrativo", "chave": "maestria_liberada",
     "texto": "Libera a propriedade de maestria da arma escolhida.", "arma": "{{escolhido}}"}}],
 revisao={"status": "ok", "notas": "Era dúvida enquanto o catálogo de itens não existia. O capítulo 6 entrou na fase 4 e o filtro resolveu sozinho, como o esquema previa — 38 armas Simples e Marciais. Resolvido na auditoria de 2026-09-02."})

car("recuperar_folego", "Recuperar Fôlego", 1, 127,
 "Ação Bônus para recuperar Pontos de Vida iguais a 1d10 mais seu nível de Guerreiro. Usos conforme a coluna Recuperar Fôlego: recupera um uso em Descanso Curto e todos em Descanso Longo.",
 [{"tipo": "recurso_com_recarga", "id": "recuperar_folego", "nome": "Recuperar Fôlego",
   "formula_maximo": ["coluna:recuperar_folego"],
   "recarga": [{"gatilho": "descanso_curto", "quantidade": 1},
               {"gatilho": "descanso_longo", "quantidade": "todos"}], "consumo": "por_uso"},
  {"tipo": "cura", "custo": "acao_bonus", "formula": ["1d10", "nivel_classe:guerreiro"],
   "consome_recurso": "recuperar_folego"}])

car("mente_tatica", "Mente Tática", 2, 127,
 "Ao falhar num teste de atributo, gaste um uso de Recuperar Fôlego para jogar 1d10 e somar ao teste. Se ainda assim falhar, o uso não é gasto.",
 [{"tipo": "modificador", "alvo": "teste_de_atributo", "valor": ["1d10"], "empilha": "soma",
   "gatilho": "falha", "momento": "apos_a_jogada", "consome_recurso": "recuperar_folego",
   "devolve_recurso_se": "o teste continuar falhando"}])

car("surto_de_acao", "Surto de Ação", 2, 128,
 "No seu turno, executa uma ação adicional — exceto Usar Magia. Recarrega em Descanso Curto ou Longo. A partir do nível 17, dois usos por descanso, mas só um por turno.",
 [{"tipo": "recurso_com_recarga", "id": "surto_de_acao", "formula_maximo": ["1"],
   "recarga": ["descanso_curto", "descanso_longo"], "consumo": "por_uso"},
  {"tipo": "acao_adicional", "excecoes": ["usar_magia"], "consome_recurso": "surto_de_acao",
   "frequencia": "uma_vez_por_turno"}],
 niveis=[2, 17], repetivel=True, tipo_de_repeticao="melhoria",
 melhorias_por_nivel={"17": {"formula_maximo": ["2"],
   "nota": "Dois usos por descanso, ainda limitado a um por turno."}})

car("subclasse_de_guerreiro", "Subclasse de Guerreiro", 3, 128,
 "Escolhe uma subclasse de Guerreiro; suas características chegam nos níveis 3, 7, 10, 15 e 18.",
 [{"id": "guerreiro_escolha_de_subclasse", "tipo": "escolha", "rotulo": "Escolha uma subclasse de Guerreiro",
   "quantidade": 1, "momento": "nivel_3",
   "de": {"catalogo": "subclasses", "filtro": {"classe": "guerreiro"}},
   "efeito_por_item_escolhido": {"tipo": "conceder_subclasse", "chave": "{{escolhido}}"}}])

car("ajuste_tatico", "Ajuste Tático", 5, 128,
 "Sempre que usa Recuperar Fôlego como Ação Bônus, pode mover até metade do seu Deslocamento sem provocar Ataques de Oportunidade.",
 [{"tipo": "efeito_narrativo", "chave": "movimento_livre_apos_folego", "gatilho": "usar:recuperar_folego",
   "texto": "Move até metade do Deslocamento sem provocar Ataques de Oportunidade."}])

car("ataque_extra", "Ataque Extra", 5, 128,
 "Ataca duas vezes, em vez de uma, sempre que executa a ação Atacar no seu turno.",
 [{"tipo": "conceder_ataque", "quantidade": ["2"], "modo": "define_total_da_acao_atacar"}])

car("indomavel", "Indomável", 9, 128,
 "Ao falhar numa salvaguarda, joga de novo somando um bônus igual ao seu nível de Guerreiro, e usa o novo resultado. Um uso por Descanso Longo; dois a partir do nível 13 e três a partir do 17.",
 [{"tipo": "recurso_com_recarga", "id": "indomavel", "formula_maximo": ["1"],
   "recarga": ["descanso_longo"], "consumo": "por_uso"},
  {"tipo": "rolar_novamente", "alvo": "salvaguarda", "gatilho": "falha",
   "bonus": ["nivel_classe:guerreiro"], "usa_novo_resultado": True, "consome_recurso": "indomavel"}],
 niveis=[9, 13, 17], repetivel=True, tipo_de_repeticao="melhoria",
 melhorias_por_nivel={"13": {"formula_maximo": ["2"]}, "17": {"formula_maximo": ["3"]}})

car("mestre_tatico", "Mestre Tático", 9, 128,
 "Ao atacar com arma cuja maestria você pode usar, substitui essa propriedade por Empurrar, Drenar ou Lentidão para aquele ataque.",
 [{"tipo": "substituir_maestria", "escopo": "arma_com_maestria_liberada",
   "opcoes": ["empurrar", "drenar", "lentidao"]}])

car("dois_ataques_extras", "Dois Ataques Extras", 11, 128,
 "Ataca três vezes, em vez de uma, sempre que executa a ação Atacar no seu turno.",
 [{"tipo": "conceder_ataque", "quantidade": ["3"], "modo": "define_total_da_acao_atacar"}])

car("ataques_estudados", "Ataques Estudados", 13, 128,
 "Ao errar uma jogada de ataque contra uma criatura, você tem Vantagem na próxima jogada de ataque contra ela antes do fim do seu próximo turno.",
 [{"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "vantagem", "gatilho": "erro",
   "condicao": {"todas": ["mesmo_alvo"]}, "duracao": "ate_o_fim_do_seu_proximo_turno"}])

car("tres_ataques_extras", "Três Ataques Extras", 20, 129,
 "Ataca quatro vezes, em vez de uma, sempre que executa a ação Atacar no seu turno.",
 [{"tipo": "conceder_ataque", "quantidade": ["4"], "modo": "define_total_da_acao_atacar"}])

# ---------------------------------------------------------------- Campeão
SUB = "campeao"
car("atleta_extraordinario", "Atleta Extraordinário", 3, 129,
 "Vantagem em jogadas de Iniciativa e em testes de Força (Atletismo). Imediatamente após um Acerto Crítico, move até metade do Deslocamento sem provocar Ataques de Oportunidade.",
 [{"tipo": "vantagem", "alvo": "iniciativa", "modo": "vantagem"},
  {"tipo": "vantagem", "alvo": "teste_de_atributo:atletismo", "modo": "vantagem"},
  {"tipo": "efeito_narrativo", "chave": "movimento_apos_critico", "gatilho": "acerto_critico",
   "texto": "Move até metade do Deslocamento sem provocar Ataques de Oportunidade."}], subclasse=SUB)

car("critico_aprimorado", "Crítico Aprimorado", 3, 129,
 "Suas jogadas de ataque com armas e Ataques Desarmados obtêm Acerto Crítico com 19 ou 20 no d20.",
 [{"tipo": "alterar_faixa_de_critico", "alvo": ["ataque_com_arma", "ataque_desarmado"], "faixa": [19, 20]}],
 subclasse=SUB)

car("estilo_de_luta_adicional", "Estilo de Luta Adicional", 7, 129,
 "Adquire outro talento de Estilo de Luta à sua escolha.",
 [{"id": "campeao_estilo_de_luta_2", "tipo": "escolha", "rotulo": "Escolha outro talento de Estilo de Luta",
   "quantidade": 1, "momento": "nivel_7",
   "de": {"catalogo": "talentos", "filtro": {"categoria": "estilo_de_luta"}},
   "efeito_por_item_escolhido": {"tipo": "conceder_talento", "talento_id": "{{escolhido}}"}}], subclasse=SUB)

car("combatente_heroico", "Combatente Heroico", 10, 129,
 "Durante o combate, concede a si mesmo Inspiração Heroica sempre que começar seu turno sem ela.",
 [{"tipo": "efeito_narrativo", "chave": "inspiracao_heroica_automatica", "momento": "inicio_do_seu_turno",
   "texto": "Em combate, ganha Inspiração Heroica sempre que iniciar o turno sem ela."}], subclasse=SUB)

car("critico_superior", "Crítico Superior", 15, 129,
 "Suas jogadas de ataque com armas e Ataques Desarmados obtêm Acerto Crítico com 18 a 20 no d20.",
 [{"tipo": "alterar_faixa_de_critico", "alvo": ["ataque_com_arma", "ataque_desarmado"], "faixa": [18, 20]}],
 subclasse=SUB)

car("sobrevivente", "Sobrevivente", 18, 129,
 "Vantagem em Salvaguardas Contra Morte, e um 18-20 nelas conta como 20. No início de cada turno seu, recupera PV iguais a 5 mais o modificador de Constituição, se estiver Sangrando e tiver ao menos 1 PV.",
 [{"tipo": "vantagem", "alvo": "salvaguarda_contra_morte", "modo": "vantagem"},
  {"tipo": "alterar_resultado_de_salvaguarda", "alvo": "salvaguarda_contra_morte",
   "aplica_a": "resultado_18_a_20", "em_sucesso": "conta_como_20"},
  {"tipo": "cura", "formula": ["5", "mod:CON"], "momento": "inicio_do_seu_turno",
   "condicao": {"todas": ["estado:sangrando", "pv_atual >= 1"]}}], subclasse=SUB)

# -------------------------------------------------------- Cavaleiro Místico
SUB = "cavaleiro_mistico"
PREP = {3:3,4:4,5:4,6:4,7:5,8:6,9:6,10:7,11:8,12:8,13:9,14:10,15:10,16:11,17:11,18:11,19:12,20:13}
SLOTS = {3:[2,0,0,0],4:[3,0,0,0],5:[3,0,0,0],6:[3,0,0,0],7:[4,2,0,0],8:[4,2,0,0],9:[4,2,0,0],
 10:[4,3,0,0],11:[4,3,0,0],12:[4,3,0,0],13:[4,3,2,0],14:[4,3,2,0],15:[4,3,2,0],16:[4,3,3,0],
 17:[4,3,3,0],18:[4,3,3,0],19:[4,3,3,1],20:[4,3,3,1]}
car("conjuracao_cavaleiro_mistico", "Conjuração", 3, 130,
 "Conjura magias da lista do Mago com Inteligência: dois truques (mais um no nível 10), espaços de magia e magias preparadas conforme a tabela Conjuração de Cavaleiro Místico. Recupera os espaços em Descanso Longo. Pode usar Foco Arcano.",
 [{"tipo": "conceder_slot", "tabela_progressao_id": "cavaleiro_mistico", "recarga": "descanso_longo"},
  {"tipo": "preparar_magias", "formula_quantidade": ["coluna_conjuracao:magias_preparadas"],
   "atributo_conjuracao": "INT",
   "restricao": "as magias escolhidas devem ser de um círculo para o qual você tem espaços"},
  {"tipo": "desbloquear_magias", "lista_id": "mago", "modo": "disponivel_para_preparar",
   "atributo_conjuracao": "INT", "circulo_minimo": 1},
  {"id": "cavaleiro_mistico_truques", "tipo": "escolha", "rotulo": "Escolha truques da lista do Mago",
   "quantidade": 2, "momento": "nivel_3", "reescolhivel": True, "reescolha_em": "cada_nivel_de_guerreiro",
   "quantidade_por_nivel": {"3": 2, "10": 3},
   "recomendados": ["raio_de_gelo", "toque_chocante"],
   "de": {"catalogo": "magias", "filtro": {"nivel": 0, "lista": "mago"}},
   "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "lista_id": "mago",
                                 "modo": "conhecida", "magia": "{{escolhido}}"}},
  {"id": "cavaleiro_mistico_preparadas", "tipo": "escolha",
   "rotulo": "Prepare magias de 1º círculo ou superior da lista do Mago",
   "quantidade": "coluna_conjuracao:magias_preparadas", "momento": "nivel_3",
   "reescolhivel": True, "reescolha_em": "cada_nivel_de_guerreiro", "reescolha_quantidade": 1,
   "recomendados": ["escudo_arcano", "maos_flamejantes", "salto"],
   "de": {"catalogo": "magias", "filtro": {"nivel_minimo": 1, "lista": "mago",
                                           "circulo_com_espaco_disponivel": True}},
   "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "lista_id": "mago",
                                 "modo": "sempre_preparada", "magia": "{{escolhido}}"}}],
 subclasse=SUB,
 foco_de_conjuracao=["foco_arcano"],
 tabela_de_conjuracao={"id": "cavaleiro_mistico", "fonte": f(130),
   "colunas": ["magias_preparadas", "espacos_1", "espacos_2", "espacos_3", "espacos_4"],
   "linhas": [{"nivel": n, "magias_preparadas": PREP[n],
               "espacos_1": SLOTS[n][0], "espacos_2": SLOTS[n][1],
               "espacos_3": SLOTS[n][2], "espacos_4": SLOTS[n][3]} for n in range(3, 21)]})

car("vinculo_com_arma", "Vínculo com Arma", 3, 131,
 "Ritual de 1 hora (cabe num Descanso Curto) que vincula uma arma a você: ela não pode ser desarmada de você, salvo se estiver Incapacitado, e pode ser invocada à sua mão como Ação Bônus, de qualquer lugar do mesmo plano. Até dois vínculos, invocando um por vez.",
 [{"tipo": "conceder_acao", "id": "invocar_arma_vinculada", "custo": "acao_bonus",
   "efeitos": [{"tipo": "teleporte", "alvo": "arma_vinculada", "destino": "sua_mao",
                "requisitos": ["mesmo_plano_de_existencia"]}]},
  {"tipo": "efeito_narrativo", "chave": "nao_pode_ser_desarmado",
   "texto": "A arma vinculada não pode ser desarmada de você, a menos que você tenha a condição Incapacitado."}],
 subclasse=SUB, limite_de_vinculos=2,
 ritual={"duracao": "1 hora", "pode_ocorrer_em": "descanso_curto",
         "falha_se": ["outro Guerreiro já vinculado à arma",
                      "arma é item mágico sintonizado com outra pessoa"]})

car("magia_de_guerra", "Magia de Guerra", 7, 131,
 "Na ação Atacar, substitui um dos ataques pela conjuração de um truque de Mago com tempo de conjuração de uma ação.",
 [{"tipo": "efeito_narrativo", "chave": "trocar_ataque_por_truque",
   "texto": "Troca um ataque da ação Atacar pela conjuração de um truque de Mago de tempo 'ação'."}],
 subclasse=SUB)

car("golpe_mistico", "Golpe Místico", 10, 131,
 "Ao atingir uma criatura com ataque usando arma, ela tem Desvantagem na próxima salvaguarda contra magia que você conjurar, antes do fim do seu próximo turno.",
 [{"tipo": "vantagem", "alvo": "salvaguarda", "modo": "desvantagem", "beneficiario": "alvo",
   "gatilho": "acerto_com_arma", "aplica_a": "proxima_salvaguarda_contra_magia_sua",
   "duracao": "ate_o_fim_do_seu_proximo_turno"}], subclasse=SUB)

car("investida_mistica", "Investida Mística", 15, 132,
 "Ao usar Surto de Ação, teleporta-se até 9 metros para um espaço desocupado à sua vista, antes ou depois da ação adicional.",
 [{"tipo": "teleporte", "alcance_m": 9, "gatilho": "usar:surto_de_acao",
   "requisitos": ["destino_desocupado", "destino_a_vista"],
   "momento": "antes_ou_depois_da_acao_adicional"}], subclasse=SUB)

car("magia_de_guerra_aprimorada", "Magia de Guerra Aprimorada", 18, 132,
 "Na ação Atacar, substitui dois ataques pela conjuração de uma magia de Mago de 1º ou 2º círculo com tempo de conjuração de uma ação.",
 [{"tipo": "melhorar_caracteristica", "alvo": "magia_de_guerra",
   "efeitos": [{"tipo": "efeito_narrativo", "chave": "trocar_dois_ataques_por_magia",
                "texto": "Troca dois ataques da ação Atacar pela conjuração de uma magia de Mago de 1º ou 2º círculo de tempo 'ação'."}]}],
 subclasse=SUB)

# ------------------------------------------------------ Combatente Psíquico
SUB = "combatente_psiquico"
DEP = {3:("d6",4),5:("d8",6),9:("d8",8),11:("d10",8),13:("d10",10),17:("d12",12)}
car("poder_psionico", "Poder Psiônico", 3, 132,
 "Você tem Dados de Energia Psiônica (tipo e quantidade pela tabela), que recarregam um em Descanso Curto e todos em Descanso Longo. Desbloqueia Golpe Psiônico, Movimento Telecinético e Vínculo Protetivo.",
 [{"tipo": "recurso_com_recarga", "id": "dados_de_energia_psionica", "nome": "Dados de Energia Psiônica",
   "formula_maximo": ["tabela:dados_de_energia.quantidade"], "dado": "tabela:dados_de_energia.tipo",
   "recarga": [{"gatilho": "descanso_curto", "quantidade": 1},
               {"gatilho": "descanso_longo", "quantidade": "todos"}], "consumo": "por_uso"},
  {"tipo": "dano", "id": "golpe_psionico", "frequencia": "uma_vez_por_turno",
   "gatilho": "acerto_com_arma_a_ate_9m", "formula_dado": "dado:dados_de_energia_psionica",
   "somar": ["mod:INT"], "tipo_dano": "energetico", "modo": "dano_adicional",
   "consome_recurso": "dados_de_energia_psionica"},
  {"tipo": "conceder_acao", "id": "movimento_telecinetico", "custo": "acao", "acao_id": "usar_magia",
   "descricao_curta": "Transporta um objeto solto Grande ou menor, ou uma criatura voluntária que não seja você, a até 9 m, movendo-a até 9 m para espaço desocupado à sua vista.",
   "recarga": ["descanso_curto", "descanso_longo"],
   "recuperacao_alternativa": {"consome_recurso": "dados_de_energia_psionica", "custo": "livre"}},
  {"tipo": "reducao_de_dano", "id": "vinculo_protetivo", "custo": "reacao",
   "formula": ["dado:dados_de_energia_psionica", "mod:INT"], "minimo": 1,
   "beneficiario": "voce_ou_criatura_a_ate_9m", "tipos_de_dano": ["todos"],
   "consome_recurso": "dados_de_energia_psionica"}],
 subclasse=SUB,
 tabela_de_dados={"id": "dados_de_energia", "fonte": f(132),
   "linhas": [{"nivel": n, "tipo": t, "quantidade": q} for n, (t, q) in sorted(DEP.items())]})

car("adepto_telecinetico", "Adepto Telecinético", 7, 133,
 "Estocada Telecinética: ao causar dano com Golpe Psiônico, o alvo faz salvaguarda de Força (CD 8 + mod. de Inteligência + BP) ou fica Caído, ou é transportado até 3 m horizontalmente. Salto com Impulsão Psíquica: Ação Bônus para ganhar Deslocamento de Voo igual ao dobro do seu até o fim do turno.",
 [{"tipo": "conceder_condicao", "condicao_id": "caido", "beneficiario": "alvo",
   "gatilho": "dano_de:golpe_psionico",
   "salvaguarda": {"atributo": "FOR", "cd": ["8", "mod:INT", "prof"]},
   "alternativa": "transportar o alvo até 3 metros horizontalmente"},
  {"tipo": "conceder_velocidade", "tipo_deslocamento": "voo",
   "formula": [{"op": "mult", "args": ["2", "deslocamento"]}], "custo": "acao_bonus",
   "duracao": "ate_o_fim_do_turno_atual", "recarga": ["descanso_curto", "descanso_longo"],
   "recuperacao_alternativa": {"consome_recurso": "dados_de_energia_psionica", "custo": "livre"}}],
 subclasse=SUB)

car("resguardo_mental", "Resguardo Mental", 10, 133,
 "Resistência a dano Psíquico. Ao iniciar o turno Amedrontado ou Enfeitiçado, gasta um Dado de Energia Psiônica para encerrar todos os efeitos que impõem essas condições a você.",
 [{"tipo": "alterar_dano", "tipo_dano": "psiquico", "operacao": "resistencia"},
  {"tipo": "remover_condicao", "condicoes": ["amedrontado", "enfeiticado"], "quantidade": "todas",
   "momento": "inicio_do_seu_turno", "consome_recurso": "dados_de_energia_psionica",
   "nota": "Encerra também os efeitos que estavam impondo essas condições."}],
 subclasse=SUB)

car("baluarte_de_energia", "Baluarte de Energia", 15, 133,
 "Ação Bônus para dar Cobertura Parcial, por 1 minuto ou até você ficar Incapacitado, a até um número de criaturas igual ao seu modificador de Inteligência (mínimo 1) a até 9 m, você incluído.",
 [{"tipo": "conceder_cobertura", "grau": "parcial", "custo": "acao_bonus", "alcance_m": 9,
   "alvos": {"quantidade": {"op": "max", "args": ["1", "mod:INT"]}, "inclui_voce": True},
   "duracao": "1 minuto", "encerra_se": [{"condicao_id": "incapacitado"}],
   "recarga": ["descanso_longo"],
   "recuperacao_alternativa": {"consome_recurso": "dados_de_energia_psionica", "custo": "livre"}}],
 subclasse=SUB)

car("mestre_telecinetico", "Mestre Telecinético", 18, 133,
 "Tem sempre Telecinese preparada, conjurável sem espaço de magia nem componentes, com Inteligência. Enquanto mantém a Concentração nela, pode atacar com arma como Ação Bônus a cada turno. Recarrega em Descanso Longo.",
 [{"tipo": "desbloquear_magias", "lista_id": "mestre_telecinetico", "modo": "sempre_preparada",
   "magias": ["telecinese"], "atributo_conjuracao": "INT",
   "sem_espaco_de_magia": True, "sem_componentes": True, "recarga": ["descanso_longo"],
   "recuperacao_alternativa": {"consome_recurso": "dados_de_energia_psionica", "custo": "livre"}},
  {"tipo": "conceder_acao", "id": "ataque_bonus_na_telecinese", "custo": "acao_bonus",
   "condicao": {"todas": ["concentrando_em:telecinese"]},
   "efeitos": [{"tipo": "conceder_ataque", "quantidade": ["1"]}]}],
 subclasse=SUB)

# --------------------------------------------------------- Mestre da Batalha
SUB = "mestre_da_batalha"
car("estudioso_da_guerra", "Estudioso da Guerra", 3, 133,
 "Proficiência com um tipo de Ferramentas de Artesão à sua escolha e com uma perícia da lista do Guerreiro.",
 [{"id": "mestre_batalha_ferramenta", "tipo": "escolha", "rotulo": "Escolha Ferramentas de Artesão",
   "quantidade": 1, "momento": "nivel_3",
   "de": {"catalogo": "ferramentas", "filtro": {"grupo": "artesao"}},
   "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "ferramenta",
                                 "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}},
  {"id": "mestre_batalha_pericia", "tipo": "escolha", "rotulo": "Escolha uma perícia de Guerreiro",
   "quantidade": 1, "momento": "nivel_3",
   "de": {"catalogo": "pericias", "chaves": PERICIAS_GUERREIRO},
   "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                 "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}}],
 subclasse=SUB)

car("superioridade_em_combate", "Superioridade em Combate", 3, 133,
 "Aprende três manobras (mais duas nos níveis 7, 10 e 15, podendo trocar uma a cada vez) e tem quatro Dados de Superioridade d8, recarregados em Descanso Curto ou Longo. Ganha um dado a mais nos níveis 7 e 15. CD das manobras: 8 + mod. de Força ou Destreza + BP. Só uma manobra por ataque.",
 [{"tipo": "recurso_com_recarga", "id": "superioridade", "nome": "Dados de Superioridade",
   "formula_maximo": ["4"], "dado": "d8", "recarga": ["descanso_curto", "descanso_longo"],
   "consumo": "por_uso"},
  {"id": "mestre_batalha_manobras", "tipo": "escolha", "rotulo": "Escolha manobras",
   "quantidade": 3, "momento": "nivel_3", "reescolhivel": True,
   "reescolha_em": "cada_nivel_que_concede_manobras", "reescolha_quantidade": 1,
   "quantidade_por_nivel": {"3": 3, "7": 5, "10": 7, "15": 9},
   "de": {"catalogo": "manobras"},
   "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado", "chave": "{{escolhido}}"}}],
 subclasse=SUB,
 cd_das_manobras=["8", "mod:FOR_ou_DES", "prof"],
 limite="uma manobra por ataque",
 melhorias_por_nivel={"7": {"formula_maximo": ["5"]}, "15": {"formula_maximo": ["6"]}})

car("conheca_seu_inimigo", "Conheça Seu Inimigo", 7, 133,
 "Ação Bônus para saber se uma criatura à vista a até 9 m tem Imunidades, Resistências ou Vulnerabilidades — e quais são. Recarrega em Descanso Longo, ou gastando um Dado de Superioridade.",
 [{"tipo": "recurso_com_recarga", "id": "conheca_seu_inimigo", "formula_maximo": ["1"],
   "recarga": ["descanso_longo"], "consumo": "por_uso",
   "recuperacao_alternativa": {"consome_recurso": "superioridade", "custo": "livre"}},
  {"tipo": "efeito_narrativo", "chave": "revelar_defesas", "custo": "acao_bonus",
   "texto": "Revela Imunidades, Resistências e Vulnerabilidades de uma criatura à vista a até 9 metros."}],
 subclasse=SUB)

car("superioridade_em_combate_aprimorada", "Superioridade em Combate Aprimorada", 10, 134,
 "Seu Dado de Superioridade passa a ser um d10.",
 [{"tipo": "melhorar_caracteristica", "alvo": "superioridade_em_combate",
   "efeitos": [{"tipo": "recurso_com_recarga", "id": "superioridade", "dado": "d10",
                "modo": "substitui_dado"}]}], subclasse=SUB)

car("implacavel", "Implacável", 15, 134,
 "Uma vez por turno, ao usar uma manobra, joga 1d8 e usa o resultado em vez de gastar um Dado de Superioridade.",
 [{"tipo": "efeito_narrativo", "chave": "manobra_sem_gastar_dado", "frequencia": "uma_vez_por_turno",
   "texto": "Joga 1d8 e usa o resultado no lugar de gastar um Dado de Superioridade."}], subclasse=SUB)

car("superioridade_em_combate_suprema", "Superioridade em Combate Suprema", 18, 134,
 "Seu Dado de Superioridade passa a ser um d12.",
 [{"tipo": "melhorar_caracteristica", "alvo": "superioridade_em_combate",
   "efeitos": [{"tipo": "recurso_com_recarga", "id": "superioridade", "dado": "d12",
                "modo": "substitui_dado"}]}], subclasse=SUB)

C['itens'] = C['itens'] + novos
C['total'] = len(C['itens'])
wr('caracteristicas.json', C)

# ------------------------------------------------------------------ subclasses
S = rd('subclasses.json')
S['itens'] = [s for s in S['itens'] if s.get('classe') != 'guerreiro']
NOVAS = [
 ("campeao", "Campeão", 129, "Foca no desenvolvimento marcial e na excelência física: críticos mais frequentes, atletismo e resiliência.",
  ["atleta_extraordinario","critico_aprimorado","estilo_de_luta_adicional","combatente_heroico",
   "critico_superior","sobrevivente"]),
 ("cavaleiro_mistico", "Cavaleiro Místico", 130, "Une habilidade marcial ao estudo da magia arcana, com conjuração parcial da lista do Mago.",
  ["conjuracao_cavaleiro_mistico","vinculo_com_arma","magia_de_guerra","golpe_mistico",
   "investida_mistica","magia_de_guerra_aprimorada"]),
 ("combatente_psiquico", "Combatente Psíquico", 132, "Desperta poder psiônico para infundir ataques, mover objetos com a mente e erguer barreiras de força.",
  ["poder_psionico","adepto_telecinetico","resguardo_mental","baluarte_de_energia","mestre_telecinetico"]),
 ("mestre_da_batalha", "Mestre da Batalha", 133, "Estudante da arte do combate: aprende manobras alimentadas por Dados de Superioridade.",
  ["estudioso_da_guerra","superioridade_em_combate","conheca_seu_inimigo",
   "superioridade_em_combate_aprimorada","implacavel","superioridade_em_combate_suprema"])]
S['itens'] = S['itens'] + [{"id": i, "nome": n, "classe": "guerreiro", "fonte": f(p), "revisao": OK,
  "descricao_curta": d, "niveis_de_caracteristica": [3, 7, 10, 15, 18], "caracteristicas": c}
  for i, n, p, d, c in NOVAS]
S['total'] = len(S['itens'])
wr('subclasses.json', S)
print("classes:", cl['total'], "| caracteristicas:", C['total'], "| subclasses:", S['total'])
