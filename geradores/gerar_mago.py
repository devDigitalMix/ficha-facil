# -*- coding: utf-8 -*-
"""Fase 2c — Classe Mago (cap. 3, p. 147-157), suas 4 subclasses e a lista de magias."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos
import json, os, subprocess, sys
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def f(p, cap=3): return {"capitulo": cap, "pagina_livro": p, "pagina_pdf": p + 4}
OK = {"status": "ok", "notas": ""}
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ------------------------------------------------ tipos de efeito e alvos novos
NOVOS = [
 ("livro_de_magias","capacidade_paginas magias_iniciais ganho_por_nivel","O livro do Mago: magias de 1º círculo ou superior que ele conhece."),
 ("conjurar_como_ritual","condicao","Conjura como Ritual magias com o marcador Ritual, sem precisar prepará-las."),
 ("recuperar_espacos_de_magia","formula_circulos limite_de_circulo gatilho recarga","Devolve espaços gastos (Recuperação Arcana, Perito em Adivinhação)."),
 ("adicionar_magia_ao_livro","quantidade filtro gratuito momento","Acrescenta magias ao livro sem custo (Versado em <escola>)."),
 ("conjurar_sem_espaco","magias circulo frequencia","Conjura certas magias sem gastar espaço de magia."),
 ("trocar_magia_preparada","quantidade gatilho fonte","Substitui magia preparada (Memorizar Magia)."),
 ("barreira_de_dano","formula_pv_maximo recarga absorve","Reserva de PV que absorve dano antes do personagem (Proteção Arcana)."),
 ("substituir_resultado_de_d20","quantidade_de_jogadas recarga frequencia alvo","Troca um Teste de D20 por um resultado guardado (Prodígio)."),
 ("dano_maximizado","escopo custo_de_uso_repetido","Faz a magia causar dano máximo (Sobrecarga)."),
]
te = rd('catalogos/tipos_de_efeito.json'); ex = {i['id'] for i in te['itens']}
for i, campos, nota in NOVOS:
    if i not in ex:
        te['itens'].append({"id": i, "nome": i.replace('_',' ').capitalize(),
                            "origem": "NOVO_FASE2C", "campos": campos.split(), "nota": nota})
te['total'] = len(te['itens']); wr('catalogos/tipos_de_efeito.json', te)

a = rd('catalogos/alvos.json'); ids = {x['id'] for x in a['itens']}
for i, n in [("alcance_de_magia", "Alcance das suas magias"),
             ("teste_de_dissipar", "Teste de atributo para dissipar magia")]:
    if i not in ids: a['itens'].append({"id": i, "nome": n})
a['total'] = len(a['itens']); wr('catalogos/alvos.json', a)

# --------------------------------------------- lista de magias do Mago (242)
magias_mago = json.load(open(caminhos.exigir('lista_mago.json', 'gerar_mago.py'), encoding='utf-8'))
m = rd('catalogos/magias.json')
por_id = {i['id']: i for i in m['itens']}
for x in magias_mago:
    if x['id'] in por_id:
        por_id[x['id']].update({k: v for k, v in x.items() if k != 'fonte'})
        por_id[x['id']].setdefault('listas', []) 
        if 'mago' not in por_id[x['id']]['listas']: por_id[x['id']]['listas'].append('mago')
    else:
        por_id[x['id']] = x
m['itens'] = sorted(por_id.values(), key=lambda x: (x.get('nivel', 0), x['id']))
m['total'] = len(m['itens'])
m['nota'] = ("A lista do Mago (cap. 3, p. 150-153) está COMPLETA: 242 magias com círculo, escola e os "
             "marcadores C (Concentração), R (Ritual) e M (componente Material específico). O texto "
             "completo de cada magia — alcance, duração, efeitos — vem na fase do capítulo 7. "
             "Outras listas de classe ainda não foram extraídas.")
m['listas_completas'] = ["mago"]
wr('catalogos/magias.json', m)

lm = rd('catalogos/listas_de_magia.json')
for l in lm['itens']:
    if l['id'] == 'mago':
        l['preenchida'] = True
        l['total_de_magias'] = len(magias_mago)
        l['fonte'] = f(150)
        l['por_circulo'] = {str(n): sum(1 for x in magias_mago if x['nivel'] == n) for n in range(10)}
lm['parcial'] = True
lm['nota'] = "A lista do Mago está preenchida. As outras listas de classe entram com suas classes."
wr('catalogos/listas_de_magia.json', lm)

# ------------------------------------------------------------------ a classe
def faixa(mp):
    out = {}
    for (x, y), v in mp.items():
        for n in range(x, y + 1): out[n] = v
    return out
BP = faixa({(1,4):2,(5,8):3,(9,12):4,(13,16):5,(17,20):6})
TRUQUES = faixa({(1,3):3,(4,9):4,(10,20):5})
PREP = {1:4,2:5,3:6,4:7,5:9,6:10,7:11,8:12,9:14,10:15,11:16,12:16,13:17,14:18,15:19,16:21,17:22,18:23,19:24,20:25}
SLOTS = {1:[2],2:[3],3:[4,2],4:[4,3],5:[4,3,2],6:[4,3,3],7:[4,3,3,1],8:[4,3,3,2],
 9:[4,3,3,3,1],10:[4,3,3,3,2],11:[4,3,3,3,2,1],12:[4,3,3,3,2,1],13:[4,3,3,3,2,1,1],
 14:[4,3,3,3,2,1,1],15:[4,3,3,3,2,1,1,1],16:[4,3,3,3,2,1,1,1],17:[4,3,3,3,2,1,1,1,1],
 18:[4,3,3,3,3,1,1,1,1],19:[4,3,3,3,3,2,1,1,1],20:[4,3,3,3,3,2,2,1,1]}
CAR = {1:["adepto_de_ritual","conjuracao_mago","recuperacao_arcana"], 2:["academico"],
 3:["subclasse_de_mago"], 4:["aumento_no_valor_de_atributo"], 5:["memorizar_magia"],
 6:["caracteristica_de_subclasse"], 7:[], 8:["aumento_no_valor_de_atributo"], 9:[],
 10:["caracteristica_de_subclasse"], 11:[], 12:["aumento_no_valor_de_atributo"], 13:[],
 14:["caracteristica_de_subclasse"], 15:[], 16:["aumento_no_valor_de_atributo"], 17:[],
 18:["maestria_de_magias"], 19:["dadiva_epica"], 20:["assinatura_magica"]}

def linha_slots(n):
    s = SLOTS[n]; return {f"espacos_{i+1}": (s[i] if i < len(s) else 0) for i in range(9)}

classe = {
 "id": "mago", "nome": "Mago", "fonte": f(147), "revisao": OK,
 "descricao_curta": "Estudioso da magia arcana que aprende magias num livro próprio, prepara-as a cada dia e conjura de explosões e ilusões a portais entre mundos.",
 "dado_de_vida": 6,
 "atributo_primario": ["INT"],
 "salvaguardas_primarias": ["INT", "SAB"],
 "nivel_subclasse": 3,
 "conjuracao": {"tipo": "pleno", "atributo": "INT", "ritual": True,
                "foco": ["foco_arcano", "livro_de_magias"],
                "preparacao": "livro_de_magias", "fonte": f(147)},
 "subclasses": ["abjurador", "adivinhador", "evocador", "ilusionista"],
 "proficiencias_iniciais": [
   {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "INT", "nivel_dominio": "proficiente"},
   {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "SAB", "nivel_dominio": "proficiente"},
   {"id": "mago_pericias_iniciais", "tipo": "escolha", "rotulo": "Escolha 2 perícias",
    "quantidade": 2, "momento": "criacao",
    "de": {"catalogo": "pericias",
           "chaves": ["arcanismo","historia","intuicao","investigacao","medicina","natureza","religiao"]},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                  "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}},
   {"tipo": "conceder_proficiencia", "categoria": "arma", "chave": "categoria:simples", "nivel_dominio": "proficiente"}],
 "treinamento_com_armadura": [],
 "equipamento_inicial": {"opcoes": [
   {"id": "A", "itens": [{"item": "adaga", "quantidade": 2}, {"item": "foco_arcano_cajado"},
                         {"item": "kit_de_erudito"}, {"item": "livro_de_magias"}, {"item": "tunica"}],
    "moedas": {"po": 5}},
   {"id": "B", "moedas": {"po": 55}}],
   "revisao": {"status": "duvida", "notas": "Ids de item dependem do catálogo do cap. 6. Referência pendente."}},
 "progressao": [{"nivel": n, "bonus_de_proficiencia": BP[n], "caracteristicas": CAR[n],
                 "colunas": dict({"truques": TRUQUES[n], "magias_preparadas": PREP[n]}, **linha_slots(n))}
                for n in range(1, 21)],
 "colunas_da_tabela": dict({"truques": {"nome": "Truques", "tipo": "inteiro"},
   "magias_preparadas": {"nome": "Magias Preparadas", "tipo": "inteiro"}},
   **{f"espacos_{i}": {"nome": f"Espaços de {i}º Círculo", "tipo": "inteiro"} for i in range(1, 10)}),
 "multiclasse": {"adquire": ["dado_de_vida"],
                 "nota": "Espaços de magia por multiclasse seguem a regra do cap. 2. Registrado para a fase de multiclasse.",
                 "fonte": f(147)}}

cl = rd('classes.json')
cl['itens'] = [c for c in cl['itens'] if c['id'] != 'mago'] + [classe]
cl['total'] = len(cl['itens']); wr('classes.json', cl)

# ------------------------------------------------------------ características
C = rd('caracteristicas.json')
C['itens'] = [c for c in C['itens'] if c.get('classe') != 'mago']
novos = []
def car(id_, nome, nivel, pag, desc, efeitos, **kw):
    d = {"id": id_, "nome": nome, "classe": "mago", "nivel": nivel, "fonte": f(pag),
         "revisao": kw.pop("revisao", OK), "descricao_curta": desc, "efeitos": efeitos}
    d.update(kw); novos.append(d)

car("adepto_de_ritual", "Adepto de Ritual", 1, 147,
 "Conjura como Ritual qualquer magia com o marcador Ritual que esteja no seu livro de magias, sem precisar tê-la preparada — mas precisa ler o livro.",
 [{"tipo": "conjurar_como_ritual", "condicao": {"todas": ["magia_com_marcador:ritual", "magia_no_livro"]},
   "exige": "ler o livro de magias", "exige_preparada": False}])

car("conjuracao_mago", "Conjuração", 1, 147,
 "Conjura magias de Mago com Inteligência. Três truques (mais um nos níveis 4 e 10), um livro de magias que começa com seis magias de 1º círculo e ganha duas por nível, e espaços de magia de conjurador pleno, recuperados em Descanso Longo. Prepara magias do livro conforme a coluna Magias Preparadas.",
 [{"tipo": "conceder_slot", "tabela_progressao_id": "mago", "colunas": [f"espacos_{i}" for i in range(1, 10)],
   "recarga": "descanso_longo"},
  {"tipo": "livro_de_magias", "capacidade_paginas": 100, "peso_kg": 1.5, "tamanho": "minusculo",
   "magias_iniciais": {"quantidade": 6, "circulo": 1,
                       "recomendadas": ["armadura_arcana","detectar_magia","misseis_magicos",
                                        "onda_trovejante","queda_suave","sono"]},
   "ganho_por_nivel": {"quantidade": 2, "a_partir_do_nivel": 2,
                       "restricao": "de um círculo para o qual você tenha espaços de magia"},
   "legivel_por": "apenas você ou quem conjurar Identificar"},
  {"tipo": "preparar_magias", "formula_quantidade": ["coluna:magias_preparadas"],
   "atributo_conjuracao": "INT", "fonte_das_magias": "livro_de_magias",
   "restricao": "de um círculo para o qual você tenha espaços de magia"},
  {"tipo": "desbloquear_magias", "lista_id": "mago", "modo": "disponivel_para_preparar",
   "atributo_conjuracao": "INT"},
  {"id": "mago_truques", "tipo": "escolha", "rotulo": "Escolha truques de Mago",
   "quantidade": "coluna:truques", "momento": "nivel_1",
   "reescolhivel": True, "reescolha_em": "descanso_longo", "reescolha_quantidade": 1,
   "recomendados": ["luz", "maos_magicas", "raio_de_gelo"],
   "de": {"catalogo": "magias", "filtro": {"nivel": 0, "lista": "mago"}},
   "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "lista_id": "mago",
                                 "modo": "conhecida", "magia": "{{escolhido}}"}}],
 foco_de_conjuracao=["foco_arcano", "livro_de_magias"],
 expansao_do_livro={"copiar_magia_encontrada": {"tempo_por_circulo": "2 horas", "custo_por_circulo_po": 50},
                    "copiar_do_proprio_livro": {"tempo_por_circulo": "1 hora", "custo_por_circulo_po": 10},
                    "fonte": f(149)})

car("recuperacao_arcana", "Recuperação Arcana", 1, 148,
 "Ao terminar um Descanso Curto, recupera espaços de magia gastos cuja soma de círculos não passe da metade do seu nível de Mago (arredondado para cima), nenhum deles de 6º círculo ou superior. Recarrega em Descanso Longo.",
 [{"tipo": "recurso_com_recarga", "id": "recuperacao_arcana", "formula_maximo": ["1"],
   "recarga": ["descanso_longo"], "consumo": "por_uso"},
  {"tipo": "recuperar_espacos_de_magia", "gatilho": "descanso_curto",
   "formula_circulos": {"op": "div_arred_cima", "args": ["nivel_classe:mago", "2"]},
   "limite_de_circulo": 5, "consome_recurso": "recuperacao_arcana"}])

car("academico", "Acadêmico", 2, 148,
 "Escolhe uma perícia em que já tem proficiência entre Arcanismo, História, Investigação, Medicina, Natureza ou Religião, e ganha Especialização nela.",
 [{"id": "mago_academico", "tipo": "escolha", "rotulo": "Escolha a perícia para Especialização",
   "quantidade": 1, "momento": "nivel_2",
   "de": {"catalogo": "pericias",
          "chaves": ["arcanismo","historia","investigacao","medicina","natureza","religiao"],
          "filtro_adicional": {"ja_proficiente": True}},
   "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                 "chave": "{{escolhido}}", "nivel_dominio": "especialista"}}])

car("subclasse_de_mago", "Subclasse de Mago", 3, 149,
 "Escolhe uma subclasse de Mago; suas características chegam nos níveis 3, 6, 10 e 14.",
 [{"id": "mago_escolha_de_subclasse", "tipo": "escolha", "rotulo": "Escolha uma subclasse de Mago",
   "quantidade": 1, "momento": "nivel_3",
   "de": {"catalogo": "subclasses", "filtro": {"classe": "mago"}},
   "efeito_por_item_escolhido": {"tipo": "conceder_subclasse", "chave": "{{escolhido}}"}}])

car("memorizar_magia", "Memorizar Magia", 5, 149,
 "Ao terminar um Descanso Curto, estuda o livro e troca uma magia preparada de 1º círculo ou superior por outra do livro.",
 [{"tipo": "trocar_magia_preparada", "quantidade": 1, "gatilho": "descanso_curto",
   "fonte": "livro_de_magias", "circulo_minimo": 1}])

car("maestria_de_magias", "Maestria de Magias", 18, 149,
 "Escolhe uma magia de 1º e uma de 2º círculo do livro com tempo de conjuração de uma ação: ficam sempre preparadas e podem ser conjuradas no círculo mais baixo sem gastar espaço. Em Descanso Longo pode trocar uma delas por outra elegível do mesmo círculo.",
 [{"id": "mago_maestria_1", "tipo": "escolha", "rotulo": "Escolha uma magia de 1º círculo",
   "quantidade": 1, "momento": "nivel_18", "reescolhivel": True, "reescolha_em": "descanso_longo",
   "de": {"catalogo": "magias", "filtro": {"nivel": 1, "lista": "mago", "no_livro": True,
                                           "tempo_de_conjuracao": "acao"}},
   "efeito_por_item_escolhido": {"tipo": "conjurar_sem_espaco", "magia": "{{escolhido}}",
                                 "circulo": "mais_baixo", "frequencia": "a_vontade"}},
  {"id": "mago_maestria_2", "tipo": "escolha", "rotulo": "Escolha uma magia de 2º círculo",
   "quantidade": 1, "momento": "nivel_18", "reescolhivel": True, "reescolha_em": "descanso_longo",
   "de": {"catalogo": "magias", "filtro": {"nivel": 2, "lista": "mago", "no_livro": True,
                                           "tempo_de_conjuracao": "acao"}},
   "efeito_por_item_escolhido": {"tipo": "conjurar_sem_espaco", "magia": "{{escolhido}}",
                                 "circulo": "mais_baixo", "frequencia": "a_vontade"}}])

car("assinatura_magica", "Assinatura Mágica", 20, 149,
 "Escolhe duas magias de 3º círculo do livro: ficam sempre preparadas e cada uma pode ser conjurada uma vez no 3º círculo sem gastar espaço, recarregando em Descanso Curto ou Longo.",
 [{"id": "mago_assinaturas", "tipo": "escolha", "rotulo": "Escolha duas magias de 3º círculo",
   "quantidade": 2, "momento": "nivel_20",
   "de": {"catalogo": "magias", "filtro": {"nivel": 3, "lista": "mago", "no_livro": True}},
   "efeito_por_item_escolhido": {"tipo": "conjurar_sem_espaco", "magia": "{{escolhido}}",
                                 "circulo": 3, "frequencia": "uma_vez_por_descanso",
                                 "recarga": ["descanso_curto", "descanso_longo"]}}])

# ---------------------------------------------------- "Versado em <escola>" x4
VERSADO = [("abjuracao","Abjuração","abjurador",150),("adivinhacao","Adivinhação","adivinhador",155),
           ("evocacao","Evocação","evocador",156),("ilusao","Ilusão","ilusionista",157)]
for esc, nome_esc, sub, pag in VERSADO:
    car(f"versado_em_{esc}", f"Versado em {nome_esc}", 3, pag,
     f"Adiciona ao livro, de graça, duas magias de Mago da escola de {nome_esc} de 2º círculo ou inferior. Depois, a cada novo círculo de espaços de magia, adiciona de graça mais uma magia de {nome_esc} de um círculo para o qual tenha espaços.",
     [{"tipo": "adicionar_magia_ao_livro", "quantidade": 2, "gratuito": True, "momento": "nivel_3",
       "filtro": {"lista": "mago", "escola": esc, "nivel_maximo": 2}},
      {"tipo": "adicionar_magia_ao_livro", "quantidade": 1, "gratuito": True,
       "gatilho": "novo_circulo_de_espacos_de_magia",
       "filtro": {"lista": "mago", "escola": esc, "circulo_com_espaco_disponivel": True}}],
     subclasse=sub)

# ---------------------------------------------------------------- Abjurador
SUB = "abjurador"
car("protecao_arcana", "Proteção Arcana", 3, 154,
 "Ao conjurar uma magia de Abjuração com espaço de magia, cria uma proteção com PV máximos iguais ao dobro do seu nível de Mago mais o modificador de Inteligência, que absorve o dano no seu lugar até acabar. Conjurar Abjuração recupera o dobro do círculo em PV da proteção; uma Ação Bônus gastando espaço faz o mesmo. Dura até o Descanso Longo.",
 [{"tipo": "barreira_de_dano", "id": "protecao_arcana",
   "formula_pv_maximo": [{"op": "mult", "args": ["2", "nivel_classe:mago"]}, "mod:INT"],
   "gatilho_de_criacao": "conjurar_magia_de_abjuracao_com_espaco",
   "duracao": "ate_o_descanso_longo", "recarga": ["descanso_longo"],
   "absorve": "todo o dano recebido, aplicando Resistência e Vulnerabilidade antes",
   "ao_chegar_a_zero": "o dano restante passa para você; a proteção permanece sem absorver",
   "recuperacao": [{"gatilho": "conjurar_magia_de_abjuracao_com_espaco",
                    "formula": [{"op": "mult", "args": ["2", "nivel_do_espaco"]}]},
                   {"custo": "acao_bonus", "gasta_espaco": True,
                    "formula": [{"op": "mult", "args": ["2", "nivel_do_espaco"]}]}]}],
 subclasse=SUB)

car("protecao_projetada", "Proteção Projetada", 6, 155,
 "Reação para que a Proteção Arcana absorva o dano de uma criatura à vista a até 9 m. Se a proteção zerar, a criatura sofre o restante.",
 [{"tipo": "melhorar_caracteristica", "alvo": "protecao_arcana",
   "efeitos": [{"tipo": "barreira_de_dano", "id": "protecao_arcana", "custo": "reacao",
                "beneficiario": "criatura_a_ate_9m", "modo": "estende_alvo"}]}], subclasse=SUB)

car("rompe_magia", "Rompe-Magia", 10, 155,
 "Tem sempre Contramagia e Dissipar Magia preparadas. Conjura Dissipar Magia como Ação Bônus e soma o Bônus de Proficiência ao teste. Se a magia falhar em interromper outra magia, o espaço não é gasto.",
 [{"tipo": "desbloquear_magias", "lista_id": "mago", "modo": "sempre_preparada",
   "magias": ["contramagia", "dissipar_magia"]},
  {"tipo": "efeito_narrativo", "chave": "dissipar_como_acao_bonus",
   "texto": "Dissipar Magia pode ser conjurada como Ação Bônus."},
  {"tipo": "modificador", "alvo": "teste_de_dissipar", "valor": ["prof"], "empilha": "soma"},
  {"tipo": "efeito_narrativo", "chave": "espaco_devolvido_no_fracasso",
   "texto": "Se Contramagia ou Dissipar Magia não interromper uma magia, o espaço não é gasto."}],
 subclasse=SUB)

car("resistencia_a_magia", "Resistência à Magia", 14, 155,
 "Vantagem em salvaguardas contra magias e Resistência ao dano proveniente de magias.",
 [{"tipo": "vantagem", "alvo": "salvaguarda", "modo": "vantagem",
   "condicao": {"todas": ["origem:magia"]}},
  {"tipo": "alterar_dano", "tipo_dano": "todos", "operacao": "resistencia",
   "condicao": {"todas": ["origem:magia"]}}], subclasse=SUB)

# --------------------------------------------------------------- Adivinhador
SUB = "adivinhador"
car("prodigio", "Prodígio", 3, 155,
 "Ao terminar um Descanso Longo, joga dois d20 e guarda os resultados. Pode trocar por um deles qualquer Teste de D20 seu ou de criatura à vista, decidindo antes da jogada, uma vez por turno. Cada resultado guardado serve uma vez e some no próximo Descanso Longo.",
 [{"tipo": "substituir_resultado_de_d20", "quantidade_de_jogadas": 2, "recarga": ["descanso_longo"],
   "frequencia": "uma_vez_por_turno", "alvo": ["seu_teste_d20", "teste_d20_de_criatura_a_vista"],
   "momento": "antes_da_jogada", "perde_nao_usados_em": "descanso_longo"}],
 subclasse=SUB, niveis=[3, 14], repetivel=True, tipo_de_repeticao="melhoria",
 melhorias_por_nivel={"14": {"quantidade_de_jogadas": 3}})

car("perito_em_adivinhacao", "Perito em Adivinhação", 6, 155,
 "Ao conjurar uma magia de Adivinhação com espaço de 2º círculo ou superior, recupera um espaço gasto de círculo inferior ao usado, no máximo de 5º círculo.",
 [{"tipo": "recuperar_espacos_de_magia", "gatilho": "conjurar_magia_de_adivinhacao",
   "condicao": {"todas": ["espaco_usado_circulo >= 2"]},
   "formula_circulos": ["1"], "restricao": "círculo inferior ao espaço gasto",
   "limite_de_circulo": 5}], subclasse=SUB)

car("o_terceiro_olho", "O Terceiro Olho", 10, 155,
 "Ação Bônus para escolher um benefício que dura até você iniciar um descanso: ler qualquer idioma; conjurar Ver o Invisível sem gastar espaço; ou Visão no Escuro de 36 metros. Recarrega em Descanso Curto ou Longo.",
 [{"tipo": "recurso_com_recarga", "id": "terceiro_olho", "formula_maximo": ["1"],
   "recarga": ["descanso_curto", "descanso_longo"], "consumo": "por_uso"},
  {"id": "terceiro_olho_beneficio", "tipo": "escolha", "rotulo": "Escolha o benefício do Terceiro Olho",
   "quantidade": 1, "momento": "ao_usar", "custo": "acao_bonus",
   "de": {"catalogo": "beneficios_do_terceiro_olho", "todo_o_catalogo": True},
   "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado", "chave": "{{escolhido}}"}}],
 subclasse=SUB,
 efeitos_nomeados={
  "compreensao_superior": {"efeitos": [{"tipo": "efeito_narrativo", "chave": "ler_qualquer_idioma",
                                        "texto": "Você pode ler qualquer idioma."}]},
  "ver_o_invisivel": {"efeitos": [{"tipo": "conjurar_sem_espaco", "magias": ["ver_o_invisivel"]}]},
  "visao_no_escuro": {"efeitos": [{"tipo": "conceder_sentido", "sentido": "visao_no_escuro",
                                   "alcance_m": 36, "empilha": "maior_valor"}]}})

# ------------------------------------------------------------------ Evocador
SUB = "evocador"
car("truque_potente", "Truque Potente", 3, 156,
 "Seus truques que causam dano ainda afetam quem escapa: no erro do ataque ou no sucesso da salvaguarda, o alvo sofre metade do dano (se houver), mas nenhum efeito adicional.",
 [{"tipo": "alterar_resultado_de_salvaguarda", "aplica_a": "truque_de_dano",
   "em_sucesso": "metade_do_dano", "no_erro_do_ataque": "metade_do_dano",
   "sem_efeitos_adicionais": True}], subclasse=SUB)

car("esculpir_magias", "Esculpir Magias", 6, 156,
 "Ao conjurar magia de Evocação que afeta criaturas à sua vista, escolhe um número delas igual a 1 mais o círculo da magia: elas passam automaticamente na salvaguarda e não sofrem dano nenhum onde sofreriam metade.",
 [{"tipo": "efeito_narrativo", "chave": "zonas_seguras",
   "quantidade": {"op": "soma", "args": ["1", "circulo_da_magia"]},
   "texto": "As criaturas escolhidas têm sucesso automático na salvaguarda e não sofrem dano algum."}],
 subclasse=SUB)

car("evocacao_potencializada", "Evocação Potencializada", 10, 156,
 "Ao conjurar magia de Mago da escola de Evocação, soma o modificador de Inteligência a uma jogada de dano dela.",
 [{"tipo": "modificador", "alvo": "jogada_de_dano", "valor": ["mod:INT"], "empilha": "soma",
   "condicao": {"todas": ["magia_da_escola:evocacao", "lista:mago"]},
   "limite": "uma jogada de dano por magia"}], subclasse=SUB)

car("sobrecarga", "Sobrecarga", 14, 156,
 "Ao conjurar magia de Mago que cause dano com espaço de 1º a 5º círculo, pode causar dano máximo. A primeira vez sai de graça; repetir antes de um Descanso Longo custa 2d12 de dano Necrótico por círculo do espaço, ignorando Resistência e Imunidade, e esse custo sobe 1d12 por círculo a cada nova repetição.",
 [{"tipo": "dano_maximizado", "escopo": {"lista": "mago", "causa_dano": True,
                                         "circulo_do_espaco": [1, 5]},
   "custo_de_uso_repetido": {"formula_dado_por_circulo": "2d12", "tipo_dano": "necrotico",
                             "ignora": ["resistencia", "imunidade"],
                             "escalonamento": "+1d12 por círculo a cada novo uso antes do Descanso Longo",
                             "zera_em": "descanso_longo"}}], subclasse=SUB)

# --------------------------------------------------------------- Ilusionista
SUB = "ilusionista"
car("ilusoes_aprimoradas", "Ilusões Aprimoradas", 3, 157,
 "Conjura magias de Ilusão sem componentes Verbais, e as de alcance 3 metros ou mais ganham +18 metros. Conhece Ilusão Menor sem contar para o total de truques (ou outro truque de Mago, se já a conhecia), podendo criar som e imagem numa só conjuração e conjurá-la como Ação Bônus.",
 [{"tipo": "efeito_narrativo", "chave": "ilusao_sem_verbal",
   "texto": "Magias de Ilusão dispensam componentes Verbais."},
  {"tipo": "modificador", "alvo": "alcance_de_magia", "valor": ["18"], "unidade": "m", "empilha": "soma",
   "condicao": {"todas": ["magia_da_escola:ilusao", "alcance >= 3m"]}},
  {"tipo": "desbloquear_magias", "lista_id": "mago", "modo": "conhecida",
   "magias": ["ilusao_menor"], "nao_conta_para_o_limite": True,
   "alternativa_se_ja_conhecida": {"escolha_outro_truque_de": {"catalogo": "magias",
                                    "filtro": {"nivel": 0, "lista": "mago"}}}},
  {"tipo": "efeito_narrativo", "chave": "ilusao_menor_aprimorada",
   "texto": "Cria som e imagem numa única conjuração de Ilusão Menor, e pode conjurá-la como Ação Bônus."}],
 subclasse=SUB)

car("criaturas_espectrais", "Criaturas Espectrais", 6, 157,
 "Tem sempre Convocar Feérico e Invocar Fera preparadas e pode trocar a escola delas para Ilusão, deixando a criatura espectral. Pode conjurar a versão Ilusão sem espaço de magia, com metade dos PV da criatura; depois disso precisa de um Descanso Longo para repetir daquela forma.",
 [{"tipo": "desbloquear_magias", "lista_id": "mago", "modo": "sempre_preparada",
   "magias": ["convocar_feerico", "invocar_fera"]},
  {"tipo": "conjurar_sem_espaco", "magias": ["convocar_feerico", "invocar_fera"],
   "frequencia": "uma_vez_por_descanso_longo", "recarga": ["descanso_longo"],
   "efeito_colateral": "os Pontos de Vida da criatura invocada caem pela metade",
   "muda_escola_para": "ilusao"}],
 subclasse=SUB,
 revisao={"status": "duvida", "notas": "A característica cita 'Invocar Fera', que NÃO está na lista de magias do Mago (p. 150-153) — é magia de Druida/Guardião. Extraí como o livro escreve. Confirmar se é acesso concedido pela subclasse (o mais provável) ou erro de edição do livro."})

car("autoimagem_ilusoria", "Autoimagem Ilusória", 10, 157,
 "Ao ser atingido por uma jogada de ataque, Reação para criar uma duplicata ilusória: o ataque erra automaticamente e a ilusão se dissipa. Recarrega em Descanso Curto ou Longo, ou gastando um espaço de magia de 2º círculo ou superior.",
 [{"tipo": "recurso_com_recarga", "id": "autoimagem_ilusoria", "formula_maximo": ["1"],
   "recarga": ["descanso_curto", "descanso_longo"], "consumo": "por_uso",
   "recuperacao_alternativa": {"gasta_espaco_de_magia": {"circulo_minimo": 2}, "custo": "livre"}},
  {"tipo": "efeito_narrativo", "chave": "ataque_erra_automaticamente", "custo": "reacao",
   "gatilho": "ser_atingido_por_jogada_de_ataque",
   "texto": "O ataque erra automaticamente e a duplicata ilusória se dissipa."}],
 subclasse=SUB)

car("realidade_ilusoria", "Realidade Ilusória", 14, 157,
 "Ao conjurar magia de Ilusão com espaço de magia, pode tornar real, como Ação Bônus e enquanto a magia durar, um objeto inanimado e não mágico que faça parte da ilusão. Ele fica real por 1 minuto e não pode causar dano nem impor condições.",
 [{"tipo": "efeito_narrativo", "chave": "objeto_ilusorio_real", "custo": "acao_bonus",
   "duracao": "1 minuto",
   "texto": "Torna real um objeto inanimado e não mágico da ilusão; ele não causa dano nem impõe condições."}],
 subclasse=SUB)

C['itens'] = C['itens'] + novos
C['total'] = len(C['itens']); wr('caracteristicas.json', C)

# --------------------------------------------------- catálogo do Terceiro Olho
wr('catalogos/beneficios_do_terceiro_olho.json', {
 "catalogo": "beneficios_do_terceiro_olho", "nome": "Benefícios do Terceiro Olho",
 "fonte": f(155), "total": 3, "itens": [
  {"id": "compreensao_superior", "nome": "Compreensão Superior", "descricao_curta": "Você pode ler qualquer idioma."},
  {"id": "ver_o_invisivel", "nome": "Ver o Invisível", "descricao_curta": "Conjura Ver o Invisível sem gastar espaço de magia."},
  {"id": "visao_no_escuro", "nome": "Visão no Escuro", "descricao_curta": "Visão no Escuro com alcance de 36 metros."}]})

# ------------------------------------------------------------------ subclasses
S = rd('subclasses.json')
S['itens'] = [s for s in S['itens'] if s.get('classe') != 'mago']
NOVAS = [
 ("abjurador","Abjurador",154,"Concentra o estudo em bloqueio, banimento e proteção: ergue barreiras, dissipa magia hostil e defende o grupo.",
  ["protecao_arcana","versado_em_abjuracao","protecao_projetada","rompe_magia","resistencia_a_magia"]),
 ("adivinhador","Adivinhador",155,"Desvenda passado, presente e futuro com discernimento, visão remota e previsão.",
  ["prodigio","versado_em_adivinhacao","perito_em_adivinhacao","o_terceiro_olho"]),
 ("evocador","Evocador",156,"Concentra-se em efeitos elementais explosivos — fogo, frio, trovão, relâmpago e ácido.",
  ["truque_potente","versado_em_evocacao","esculpir_magias","evocacao_potencializada","sobrecarga"]),
 ("ilusionista","Ilusionista",157,"Tece magia sutil de enganação, deslumbrando os sentidos e fazendo o impossível parecer real.",
  ["ilusoes_aprimoradas","versado_em_ilusao","criaturas_espectrais","autoimagem_ilusoria","realidade_ilusoria"])]
S['itens'] = S['itens'] + [{"id": i, "nome": n, "classe": "mago", "fonte": f(p), "revisao": OK,
  "descricao_curta": d, "niveis_de_caracteristica": [3, 6, 10, 14], "caracteristicas": c}
  for i, n, p, d, c in NOVAS]
S['total'] = len(S['itens']); wr('subclasses.json', S)
print("classes:", cl['total'], "| caracteristicas:", C['total'], "| subclasses:", S['total'],
      "| magias:", m['total'])
