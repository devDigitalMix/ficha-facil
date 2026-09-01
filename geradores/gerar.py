# -*- coding: utf-8 -*-
"""Gera os dados da Fase 1 (Ap. C - Glossario de Regras + tabela de Pericias do Cap. 1)."""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(BASE, 'dados')

def fonte(livro, pdf=None, cap='ap_c'):
    return {"capitulo": cap, "pagina_livro": livro, "pagina_pdf": (pdf or livro + 4)}

def cat(id_, nome, itens, fonte_, nota=None):
    d = {"catalogo": id_, "nome": nome, "fonte": fonte_, "total": len(itens), "itens": itens}
    if nota: d["nota"] = nota
    return d

def w(path, obj):
    with open(os.path.join(D, path), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

OK = {"status": "ok", "notas": ""}

# ---------------------------------------------------------------- atributos
w('catalogos/atributos.json', cat('atributos', 'Atributos', [
    {"id": "FOR", "nome": "Força"}, {"id": "DES", "nome": "Destreza"},
    {"id": "CON", "nome": "Constituição"}, {"id": "INT", "nome": "Inteligência"},
    {"id": "SAB", "nome": "Sabedoria"}, {"id": "CAR", "nome": "Carisma"},
], fonte(377, cap='ap_c')))

# ---------------------------------------------------------------- pericias (Cap. 1, p. 14)
PERICIAS = [
    ("acrobacia", "Acrobacia", "DES"), ("arcanismo", "Arcanismo", "INT"),
    ("atletismo", "Atletismo", "FOR"), ("atuacao", "Atuação", "CAR"),
    ("enganacao", "Enganação", "CAR"), ("furtividade", "Furtividade", "DES"),
    ("historia", "História", "INT"), ("intimidacao", "Intimidação", "CAR"),
    ("intuicao", "Intuição", "SAB"), ("investigacao", "Investigação", "INT"),
    ("lidar_com_animais", "Lidar com Animais", "SAB"), ("medicina", "Medicina", "SAB"),
    ("natureza", "Natureza", "INT"), ("percepcao", "Percepção", "SAB"),
    ("persuasao", "Persuasão", "CAR"), ("prestidigitacao", "Prestidigitação", "DES"),
    ("religiao", "Religião", "INT"), ("sobrevivencia", "Sobrevivência", "SAB"),
]
w('catalogos/pericias.json', cat('pericias', 'Perícias',
    [{"id": i, "nome": n, "atributo": a} for i, n, a in PERICIAS],
    fonte(14, pdf=18, cap=1),
    "Tabela 'Perícias' do capítulo 1. O Mestre pode pedir a perícia com outro atributo (regra 'Perícias com Atributos Diferentes')."))

# ---------------------------------------------------------------- tipos de dano
DANOS = [("acido","Ácido"),("contundente","Contundente"),("cortante","Cortante"),
    ("eletrico","Elétrico"),("energetico","Energético"),("gelido","Gélido"),
    ("igneo","Ígneo"),("necrotico","Necrótico"),("perfurante","Perfurante"),
    ("psiquico","Psíquico"),("radiante","Radiante"),("trovejante","Trovejante"),
    ("venenoso","Venenoso")]
w('catalogos/tipos_de_dano.json', cat('tipos_de_dano', 'Tipos de Dano',
    [{"id": i, "nome": n} for i, n in DANOS], fonte(376)))

# ---------------------------------------------------------------- tipos de criatura
CRIATURAS = [("aberracao","Aberração"),("celestial","Celestial"),("constructo","Constructo"),
    ("dragao","Dragão"),("elemental","Elemental"),("feerico","Feérico"),("fera","Fera"),
    ("gigante","Gigante"),("gosma","Gosma"),("humanoide","Humanoide"),("infero","Ínfero"),
    ("monstruosidade","Monstruosidade"),("morto_vivo","Morto-vivo"),("planta","Planta")]
w('catalogos/tipos_de_criatura.json', cat('tipos_de_criatura', 'Tipos de Criatura',
    [{"id": i, "nome": n} for i, n in CRIATURAS], fonte(376),
    "Os tipos não têm regras próprias; servem de alvo para outras regras."))

# ---------------------------------------------------------------- tamanhos
w('catalogos/tamanhos.json', cat('tamanhos', 'Tamanhos', [
    {"id":"minusculo","nome":"Minúsculo"},{"id":"pequeno","nome":"Pequeno"},
    {"id":"medio","nome":"Médio"},{"id":"grande","nome":"Grande"},
    {"id":"enorme","nome":"Enorme"},{"id":"colossal","nome":"Colossal"}], fonte(375)))

# ---------------------------------------------------------------- areas de efeito
w('catalogos/areas_de_efeito.json', cat('areas_de_efeito', 'Áreas de Efeito', [
    {"id":"cilindro","nome":"Cilindro"},{"id":"cone","nome":"Cone"},{"id":"cubo","nome":"Cubo"},
    {"id":"emanacao","nome":"Emanação"},{"id":"esfera","nome":"Esfera"},{"id":"linha","nome":"Linha"}],
    fonte(361)))

# ---------------------------------------------------------------- atitudes
w('catalogos/atitudes.json', cat('atitudes', 'Atitudes', [
    {"id":"amigavel","nome":"Amigável","descricao_curta":"Vê você de forma favorável; Vantagem em testes para influenciá-la."},
    {"id":"indiferente","nome":"Indiferente","descricao_curta":"Atitude padrão; não deseja ajudar nem atrapalhar."},
    {"id":"hostil","nome":"Hostil","descricao_curta":"Vê você de forma desfavorável; Desvantagem em testes para influenciá-la."}],
    fonte(363)))

# ---------------------------------------------------------------- riscos
w('catalogos/riscos.json', cat('riscos', 'Riscos', [
    {"id":"asfixia","nome":"Asfixia","fonte":fonte(362)},
    {"id":"combustao","nome":"Combustão","fonte":fonte(364)},
    {"id":"desidratacao","nome":"Desidratação","fonte":fonte(366)},
    {"id":"desnutricao","nome":"Desnutrição","fonte":fonte(367)},
    {"id":"queda","nome":"Queda","fonte":fonte(374)}], fonte(362),
    "Marcador [Risco] do glossário. Mecânica detalhada não modelada nesta fase."))

# ---------------------------------------------------------------- cobertura
w('catalogos/graus_de_cobertura.json', cat('graus_de_cobertura', 'Graus de Cobertura', [
    {"id":"parcial","nome":"Cobertura Parcial","bonus_ca":2,"bonus_salvaguarda_des":2},
    {"id":"tres_quartos","nome":"Cobertura de Três Quartos","bonus_ca":5,"bonus_salvaguarda_des":5},
    {"id":"total","nome":"Cobertura Total","bonus_ca":None,"bonus_salvaguarda_des":None,
     "descricao_curta":"Não pode ser alvo direto."}], fonte(364),
    "Só o grau mais protetor se aplica."))

# ---------------------------------------------------------------- deslocamentos / sentidos / descansos / custos
w('catalogos/tipos_de_deslocamento.json', cat('tipos_de_deslocamento', 'Tipos de Deslocamento', [
    {"id":"caminhada","nome":"Deslocamento"},{"id":"escalada","nome":"Deslocamento de Escalada"},
    {"id":"escavacao","nome":"Deslocamento de Escavação"},{"id":"natacao","nome":"Deslocamento de Natação"},
    {"id":"voo","nome":"Deslocamento de Voo"}], fonte(366)))

w('catalogos/sentidos.json', cat('sentidos', 'Sentidos', [
    {"id":"visao_as_cegas","nome":"Visão às Cegas","tem_alcance":True},
    {"id":"visao_no_escuro","nome":"Visão no Escuro","tem_alcance":True},
    {"id":"visao_verdadeira","nome":"Visão Verdadeira","tem_alcance":True},
    {"id":"telepatia","nome":"Telepatia","tem_alcance":True},
    {"id":"percepcao_passiva","nome":"Percepção Passiva","tem_alcance":False,
     "formula":["10","bonus_teste:SAB.percepcao"]}], fonte(377)))

w('catalogos/tipos_de_descanso.json', cat('tipos_de_descanso', 'Tipos de Descanso', [
    {"id":"descanso_curto","nome":"Descanso Curto","duracao":"1 hora","fonte":fonte(365),
     "interrompido_por":["jogar_iniciativa","conjurar_magia_nao_truque","receber_dano"]},
    {"id":"descanso_longo","nome":"Descanso Longo","duracao":"8 horas","fonte":fonte(366),
     "interrompido_por":["jogar_iniciativa","conjurar_magia_nao_truque","receber_dano","1h_de_esforco_fisico"],
     "intervalo_minimo_entre_descansos":"16 horas"}], fonte(365)))

w('catalogos/custos_de_acao.json', cat('custos_de_acao', 'Custos de Ação', [
    {"id":"acao","nome":"Ação"},{"id":"acao_bonus","nome":"Ação Bônus"},
    {"id":"reacao","nome":"Reação"},{"id":"livre","nome":"Sem custo"}], fonte(360)))

w('catalogos/categorias_de_arma.json', cat('categorias_de_arma', 'Categorias de Arma', [
    {"id":"simples","nome":"Simples"},{"id":"marcial","nome":"Marcial"}], fonte(361)))

w('catalogos/categorias_de_armadura.json', cat('categorias_de_armadura', 'Categorias de Armadura', [
    {"id":"leve","nome":"Leve"},{"id":"media","nome":"Média"},
    {"id":"pesada","nome":"Pesada"},{"id":"escudo","nome":"Escudo"}], fonte(377),
    "Sem Treinamento com Armadura: Desvantagem em Testes de D20 de FOR/DES e não pode conjurar magias; sem treinamento com Escudo, não recebe o bônus de CA."))

# ---------------------------------------------------------------- alvos (usado por modificador/vantagem)
w('catalogos/alvos.json', cat('alvos', 'Alvos de Efeito', [
    {"id":"teste_d20","nome":"Qualquer Teste de D20"},
    {"id":"jogada_de_ataque","nome":"Suas jogadas de ataque"},
    {"id":"jogada_de_ataque_contra_voce","nome":"Jogadas de ataque contra você"},
    {"id":"teste_de_atributo","nome":"Seus testes de atributo"},
    {"id":"salvaguarda","nome":"Suas salvaguardas"},
    {"id":"iniciativa","nome":"Sua jogada de Iniciativa"},
    {"id":"ca_total","nome":"Classe de Armadura"},
    {"id":"deslocamento","nome":"Deslocamento"},
    {"id":"interacao_social_contra_voce","nome":"Testes de interação social contra você"}],
    fonte(360), "Catálogo de engine: nomes de alvo aceitos em 'modificador' e 'vantagem'. Sufixos permitidos: ':FOR'..':CAR' e ':<pericia>'."))
