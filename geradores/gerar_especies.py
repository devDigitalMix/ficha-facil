# -*- coding: utf-8 -*-
"""Espécies (cap. 4, p. 186-197). As 10 do livro.

Espécie não tem a regularidade do antecedente: cada uma é um punhado de traços
próprios. Então o formato é `tracos[]`, cada traço com id, nome, página e os
efeitos dele — e não uma lista solta de efeitos no topo, que perderia o nome do
traço que a ficha precisa mostrar.

Quatro espécies têm LINHAGEM: um sub-conjunto escolhido na criação que muda o que
você ganha nos níveis 1, 3 e 5 (Elfo e Tiferino), ou só no nível 1 (Gnomo), ou uma
opção de uso repetível (Golias). Cada uma vira catálogo de opção próprio, como já
se fez com Metamagia e Manobras — nunca texto solto dentro do traço.

Três traços dependem de nível de PERSONAGEM, não de classe: Revelação Celestial
(3), Voo Dracônico (5) e Forma Grande (5). Ficam com `nivel_de_personagem`, que é
campo novo: até aqui todo nível no dataset era de classe.
"""
import json, collections

CAT = 'dados/catalogos'


def fonte(p):
    return {"capitulo": 4, "pagina_livro": p, "pagina_pdf": p + 4}


def rev(status="ok", notas=""):
    return {"status": status, "notas": notas}


def traco(tid, nome, pag, desc, efeitos, **extra):
    d = collections.OrderedDict([
        ("id", tid), ("nome", nome), ("fonte", fonte(pag)),
        ("descricao_curta", desc), ("efeitos", efeitos)])
    d.update(extra)
    return d


def visao_no_escuro(m):
    return {"tipo": "conceder_sentido", "sentido": "visao_no_escuro", "alcance_m": m}


def resistencia(*tipos):
    return [{"tipo": "alterar_dano", "tipo_dano": t, "operacao": "resistencia"} for t in tipos]


def truque(magia, atributo=None, nota=None):
    e = {"tipo": "desbloquear_magias", "modo": "conhecida", "magia": magia, "circulo": 0}
    if atributo:
        e["atributo_conjuracao"] = atributo
    if nota:
        e["nota"] = nota
    return e


def recurso_pb(rid, nome, recarga=("descanso_longo",)):
    return {"tipo": "recurso_com_recarga", "id": rid, "nome": nome,
            "formula_maximo": ["prof"], "recarga": list(recarga), "consumo": "por_uso"}


def uma_vez_por_descanso_longo(rid, nome):
    return {"tipo": "recurso_com_recarga", "id": rid, "nome": nome,
            "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"}


def opcao(oid, nome, pag, desc, efeitos, **extra):
    d = collections.OrderedDict([
        ("id", oid), ("nome", nome), ("fonte", fonte(pag)),
        ("descricao_curta", desc), ("efeitos", efeitos)])
    d.update(extra)
    return d


def catalogo(cid, nome, pag, itens, nota=None, **extra):
    d = collections.OrderedDict([
        ("catalogo", cid), ("nome", nome), ("fonte", fonte(pag)),
        ("total", len(itens)), ("itens", itens)])
    if nota:
        d["nota"] = nota
    d.update(extra)
    return d


# =========================================================== catálogos de opção

HERANCA_DRACONICA = [
    ("azul", "Azul", "eletrico"), ("branco", "Branco", "gelido"),
    ("bronze", "Bronze", "eletrico"), ("cobre", "Cobre", "acido"),
    ("latao", "Latão", "igneo"), ("negro", "Negro", "acido"),
    ("ouro", "Ouro", "igneo"), ("prata", "Prata", "gelido"),
    ("verde", "Verde", "venenoso"), ("vermelho", "Vermelho", "igneo"),
]

CAT_HERANCA = catalogo(
    "heranca_draconica", "Herança Dracônica", 188,
    [opcao(f"dragao_{i}", f"Dragão {nome}", 188,
           f"Progenitor dracônico {nome}: o dano do Ataque de Sopro e a Resistência a Dano "
           f"passam a ser do tipo {dano}.",
           [{"tipo": "alterar_dano", "tipo_dano": dano, "operacao": "resistencia"},
            {"tipo": "escolher_tipo_de_dano", "opcoes": [dano],
             "escopo": "ataque_de_sopro", "define": "tipo_de_dano_do_sopro"}],
           tipo_de_dano=dano)
     for i, nome, dano in HERANCA_DRACONICA],
    nota="Dez dragões, cinco tipos de dano. A escolha define o sopro E a resistência.",
    preenchida=True)

CAT_LINHAGEM_ELFICA = catalogo(
    "linhagens_elficas", "Linhagem Élfica", 190, [
        opcao("alto_elfo", "Alto Elfo", 190,
              "Nível 1: truque Prestidigitação Arcana, trocável por outro truque de Mago a cada "
              "Descanso Longo. Nível 3: Detectar Magia. Nível 5: Passo Nebuloso.",
              [truque("prestidigitacao_arcana",
                      nota="Trocável por outro truque da lista de Mago a cada Descanso Longo."),
               {"id": "alto_elfo_troca_de_truque", "tipo": "escolha",
                "rotulo": "Troque o truque de Alto Elfo", "quantidade": 1,
                "reescolhivel": True, "reescolha_em": "descanso_longo",
                "de": {"catalogo": "magias", "filtro": {"nivel": 0, "lista": "mago"}},
                "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "modo": "conhecida",
                                              "magia": "{{escolhido}}", "circulo": 0}}],
              magias_por_nivel={"3": ["detectar_magia"], "5": ["passo_nebuloso"]}),
        opcao("drow", "Drow", 190,
              "Nível 1: alcance da Visão no Escuro sobe para 36 m, e você conhece Luzes "
              "Dançantes. Nível 3: Fogo das Fadas. Nível 5: Escuridão.",
              [{"tipo": "conceder_sentido", "sentido": "visao_no_escuro", "alcance_m": 36,
                "empilha": "maior_valor",
                "nota": "O livro diz 'aumenta para 36 metros', não 'soma 36'."},
               truque("luzes_dancantes")],
              magias_por_nivel={"3": ["fogo_das_fadas"], "5": ["escuridao"]}),
        opcao("elfo_silvestre", "Elfo Silvestre", 190,
              "Nível 1: Deslocamento sobe para 10,5 m, e você conhece Arte Druídica. "
              "Nível 3: Passos Largos. Nível 5: Passo Sem Rastro.",
              [{"tipo": "conceder_velocidade", "tipo_deslocamento": "caminhada",
                "formula": ["10.5"], "unidade": "metros", "empilha": "maior_valor",
                "nota": "O livro diz 'aumenta para 10,5 metros'."},
               truque("arte_druidica")],
              magias_por_nivel={"3": ["passos_largos"], "5": ["passo_sem_rastro"]}),
    ],
    nota="As magias de nível 3 e 5 ficam sempre preparadas, podem ser conjuradas uma vez por "
         "Descanso Longo sem espaço, ou com qualquer espaço apropriado. O atributo de "
         "conjuração (INT, SAB ou CAR) é escolhido junto com a linhagem.",
    preenchida=True)

CAT_LINHAGEM_GNOMICA = catalogo(
    "linhagens_gnomicas", "Linhagem Gnômica", 191, [
        opcao("gnomo_das_rochas", "Gnomo das Rochas", 191,
              "Truques Reparar e Prestidigitação Arcana. Além disso, 10 minutos conjurando "
              "Prestidigitação Arcana fabricam um dispositivo mecânico Minúsculo (CA 5, 1 PV) "
              "com um efeito da magia à escolha, ativado por Ação Bônus ao toque. Até três "
              "dispositivos ao mesmo tempo; cada um dura 8 horas ou até ser desmontado.",
              [truque("reparar",
                      nota="O traço imprime 'Consertar'; a entrada do cap. 7 é 'Reparar'."),
               truque("prestidigitacao_arcana"),
               {"tipo": "fabricar_item", "id": "dispositivo_mecanico",
                "tempo": "10 minutos", "conjurando": "prestidigitacao_arcana",
                "tamanho": "minusculo", "classe_de_armadura": 5, "pontos_de_vida": 1,
                "maximo_simultaneo": 3, "duracao": "8 horas",
                "desmontagem": {"custo": "acao", "acao_id": "usar_objeto"},
                "ativacao": {"custo": "acao_bonus", "requer": "toque"},
                "nota": "O efeito do dispositivo é um efeito de Prestidigitação Arcana escolhido "
                        "na fabricação; se o efeito tiver opções, uma delas é fixada ali."}]),
        opcao("gnomo_do_bosque", "Gnomo do Bosque", 191,
              "Truque Ilusão Menor, e Falar com Animais sempre preparada — conjurável sem "
              "espaço um número de vezes igual ao Bônus de Proficiência, ou com qualquer espaço "
              "que você tenha.",
              [truque("ilusao_menor"),
               {"tipo": "desbloquear_magias", "modo": "sempre_preparada",
                "magias": ["falar_com_animais"]},
               recurso_pb("gnomo_do_bosque_falar_com_animais", "Falar com Animais (Gnomo do Bosque)"),
               {"tipo": "conjurar_sem_espaco", "magia": "falar_com_animais",
                "consome_recurso": "gnomo_do_bosque_falar_com_animais",
                "tambem_com_espaco": True}]),
    ],
    nota="A linhagem determina se o atributo de conjuração é INT, SAB ou CAR — escolhido junto.",
    preenchida=True)

CAT_ANCESTRALIDADE_GIGANTE = catalogo(
    "ancestralidades_gigantes", "Ancestralidade Gigante", 192, [
        opcao("arrepio_do_gelo", "Arrepio do Gelo (Gigante do Gelo)", 192,
              "Ao atingir e causar dano com uma jogada de ataque, também causa 1d6 de dano "
              "Gélido e reduz o Deslocamento do alvo em 3 m até o início do seu próximo turno.",
              [{"tipo": "dano", "formula_dado": "1d6", "tipo_dano": "gelido",
                "gatilho": "acertar_e_causar_dano_com_jogada_de_ataque"},
               {"tipo": "modificador", "alvo": "deslocamento", "valor": ["-3"],
                "unidade": "metros", "empilha": "soma", "beneficiario": "alvo",
                "duracao": "ate_o_inicio_do_seu_proximo_turno"}]),
        opcao("queimadura_de_fogo", "Queimadura de Fogo (Gigante de Fogo)", 192,
              "Ao atingir e causar dano com uma jogada de ataque, também causa 1d10 de dano Ígneo.",
              [{"tipo": "dano", "formula_dado": "1d10", "tipo_dano": "igneo",
                "gatilho": "acertar_e_causar_dano_com_jogada_de_ataque"}]),
        opcao("resistencia_da_pedra", "Resistência da Pedra (Gigante da Pedra)", 192,
              "Ao sofrer dano, Reação para jogar 1d12, somar o modificador de Constituição e "
              "reduzir o dano nesse total.",
              [{"tipo": "reducao_de_dano", "formula": ["1d12", "mod:CON"],
                "custo": "reacao", "gatilho": "sofrer_dano"}]),
        opcao("salto_da_nuvem", "Salto da Nuvem (Gigante das Nuvens)", 192,
              "Ação Bônus para se teleportar até 9 m para um espaço desocupado à vista.",
              [{"tipo": "teleporte", "distancia_m": 9, "custo": "acao_bonus",
                "destino": "espaco_desocupado_a_vista"}]),
        opcao("tombo_da_colina", "Tombo da Colina (Gigante da Colina)", 192,
              "Ao atingir e causar dano a uma criatura Grande ou menor com uma jogada de "
              "ataque, pode impor a ela a condição Caído.",
              [{"tipo": "conceder_condicao", "condicao_id": "caido", "alvo": "criatura_atingida",
                "restricao_de_tamanho": "grande_ou_menor",
                "gatilho": "acertar_e_causar_dano_com_jogada_de_ataque"}]),
        opcao("trovao_da_tempestade", "Trovão da Tempestade (Gigante da Tempestade)", 192,
              "Ao sofrer dano de uma criatura a até 18 m, Reação para causar 1d8 de dano "
              "Trovejante nela.",
              [{"tipo": "dano", "formula_dado": "1d8", "tipo_dano": "trovejante",
                "custo": "reacao", "alcance_m": 18, "alvo": "a_criatura_que_causou_o_dano",
                "gatilho": "sofrer_dano_de_criatura_a_ate_18m"}]),
    ],
    nota="Escolhe-se UMA na criação. Os usos são iguais ao Bônus de Proficiência e voltam no "
         "Descanso Longo — o recurso vive no traço Ancestralidade Gigante, não aqui.",
    preenchida=True)

CAT_REVELACAO_CELESTIAL = catalogo(
    "revelacoes_celestiais", "Revelação Celestial", 186, [
        opcao("asas_celestiais", "Asas Celestiais", 186,
              "Asas espectrais: Deslocamento de Voo igual ao seu Deslocamento enquanto durar.",
              [{"tipo": "conceder_velocidade", "tipo_deslocamento": "voo",
                "formula": ["deslocamento"]}],
              tipo_de_dano_adicional="radiante"),
        opcao("manto_necrotico", "Manto Necrótico", 186,
              "Olhos viram poças de escuridão e asas que não voam brotam: criaturas que não "
              "sejam aliadas a até 3 m fazem salvaguarda de Carisma ou ficam Amedrontadas até o "
              "fim do seu próximo turno.",
              [{"tipo": "conceder_condicao", "condicao_id": "amedrontado",
                "alvo": "criatura_nao_aliada_a_ate_3m",
                "salvaguarda": {"atributo": "CAR", "cd": ["8", "mod:CAR", "prof"]},
                "duracao": "ate_o_fim_do_seu_proximo_turno"}],
              tipo_de_dano_adicional="necrotico"),
        opcao("transfiguracao_radiante", "Transfiguração Radiante", 186,
              "Luz abrasadora nos olhos e na boca: Luz Plena em 3 m e Meia-luz por mais 3 m, e "
              "no fim de cada turno seu cada criatura a até 3 m sofre dano Radiante igual ao "
              "seu Bônus de Proficiência.",
              [{"tipo": "efeito_narrativo", "chave": "emite_luz",
                "texto": "Luz Plena em raio de 3 m e Meia-luz por mais 3 m.",
                "luz_plena_m": 3, "meia_luz_m": 3},
               {"tipo": "dano", "formula": ["prof"], "tipo_dano": "radiante",
                "alvo": "criatura_a_ate_3m", "gatilho": "fim_de_cada_turno_seu"}],
              tipo_de_dano_adicional="radiante"),
    ],
    nota="Escolhida a cada transformação, não na criação. O dano adicional por turno é igual ao "
         "Bônus de Proficiência, e o tipo vem da opção escolhida.",
    preenchida=True)

CAT_LEGADO_INFERO = catalogo(
    "legados_inferos", "Legado Ínfero", 197, [
        opcao("abissal", "Abissal", 197,
              "Nível 1: Resistência a dano Venenoso e o truque Rajada de Veneno. "
              "Nível 3: Raio Nauseante. Nível 5: Paralisar Pessoa.",
              resistencia("venenoso") + [truque("rajada_de_veneno")],
              magias_por_nivel={"3": ["raio_nauseante"], "5": ["paralisar_pessoa"]}),
        opcao("ctonico", "Ctônico", 197,
              "Nível 1: Resistência a dano Necrótico e o truque Toque Necrótico. "
              "Nível 3: Vitalidade Vazia. Nível 5: Raio do Enfraquecimento.",
              resistencia("necrotico") + [truque("toque_necrotico")],
              magias_por_nivel={"3": ["vitalidade_vazia"], "5": ["raio_do_enfraquecimento"]}),
        opcao("infernal", "Infernal", 197,
              "Nível 1: Resistência a dano Ígneo e o truque Raio de Fogo. "
              "Nível 3: Repreensão Diabólica. Nível 5: Escuridão.",
              resistencia("igneo") + [truque("raio_de_fogo")],
              magias_por_nivel={"3": ["repreensao_diabolica"], "5": ["escuridao"]}),
    ],
    nota="As magias de nível 3 e 5 ficam sempre preparadas, conjuráveis uma vez por Descanso "
         "Longo sem espaço, ou com qualquer espaço do círculo correspondente. O atributo (INT, "
         "SAB ou CAR) é escolhido junto com o legado e vale também para Presença Sobrenatural.",
    preenchida=True)


# ==================================================================== espécies

def especie(eid, nome, pag, tamanho, deslocamento_m, tracos, desc, **extra):
    d = collections.OrderedDict([
        ("id", eid), ("nome", nome), ("fonte", fonte(pag)), ("revisao", rev()),
        ("descricao_curta", desc),
        ("tipo_de_criatura", "humanoide"),
        ("tamanho", tamanho),
        ("deslocamento", {"tipo": "caminhada", "metros": deslocamento_m}),
        ("tracos", tracos)])
    d.update(extra)
    return d


TAMANHO_MEDIO = {"fixo": "medio"}


def escolha_de_tamanho(eid, alturas):
    return {"escolha": ["medio", "pequeno"], "momento": "criacao",
            "escolha_id": f"{eid}_tamanho", "alturas": alturas}


ESPECIES = [
    especie("aasimar", "Aasimar", 186,
            escolha_de_tamanho("aasimar", {"medio": "1,20-2,10 m", "pequeno": "0,60-1,20 m"}),
            9, [
                traco("resistencia_celestial", "Resistência Celestial", 186,
                      "Resistência a dano Necrótico e Radiante.",
                      resistencia("necrotico", "radiante")),
                traco("visao_no_escuro_aasimar", "Visão no Escuro", 186,
                      "Visão no Escuro com alcance de 18 metros.", [visao_no_escuro(18)]),
                traco("maos_curativas", "Mãos Curativas", 186,
                      "Ação Usar Magia para tocar uma criatura e curar o total de um número de "
                      "d4s igual ao seu Bônus de Proficiência. Uma vez por Descanso Longo.",
                      [uma_vez_por_descanso_longo("maos_curativas", "Mãos Curativas"),
                       {"tipo": "cura",
                        "formula_dado": {"op": "mult", "args": ["prof", "1d4"]},
                        "custo": "acao", "acao_id": "usar_magia", "alcance": "toque",
                        "consome_recurso": "maos_curativas"}]),
                traco("portador_da_luz", "Portador da Luz", 186,
                      "Você conhece o truque Luz, conjurado com Carisma.",
                      [truque("luz", "CAR")]),
                traco("revelacao_celestial", "Revelação Celestial", 186,
                      "No nível 3 de personagem, Ação Bônus para se transformar por 1 minuto, "
                      "uma vez por Descanso Longo, escolhendo a opção a cada vez. Enquanto durar, "
                      "uma vez por turno você causa dano adicional igual ao Bônus de "
                      "Proficiência, do tipo da opção escolhida.",
                      [uma_vez_por_descanso_longo("revelacao_celestial", "Revelação Celestial"),
                       {"id": "revelacao_celestial_opcao", "tipo": "escolha",
                        "rotulo": "Escolha a forma da Revelação Celestial", "quantidade": 1,
                        "momento": "cada_uso", "reescolhivel": True, "reescolha_em": "cada_uso",
                        "de": {"catalogo": "revelacoes_celestiais", "todo_o_catalogo": True},
                        "efeito_por_item_escolhido": {
                            "tipo": "aplicar_efeito_nomeado",
                            "catalogo": "revelacoes_celestiais", "chave": "{{escolhido}}"}},
                       {"tipo": "dano", "formula": ["prof"],
                        "tipo_dano_derivado": {
                            "variavel": "revelacao_celestial_escolhida",
                            "mapa": {"asas_celestiais": "radiante",
                                     "manto_necrotico": "necrotico",
                                     "transfiguracao_radiante": "radiante"}},
                        "frequencia": "uma_vez_por_turno",
                        "gatilho": "causar_dano_com_ataque_ou_magia"}],
                      nivel_de_personagem=3),
            ],
            "Mortal com uma centelha dos Planos Superiores: cura pelas mãos, carrega luz e "
            "revela a natureza celestial em três formas."),

    especie("anao", "Anão", 187, {"fixo": "medio", "altura": "1,20-1,50 m"}, 9, [
        traco("visao_no_escuro_anao", "Visão no Escuro", 187,
              "Visão no Escuro com alcance de 36 metros.", [visao_no_escuro(36)]),
        traco("resistencia_a_toxinas", "Resistência a Toxinas", 187,
              "Resistência a dano Venenoso, e Vantagem nas salvaguardas para evitar ou "
              "encerrar a condição Envenenado.",
              resistencia("venenoso") + [
                  {"tipo": "vantagem", "alvo": "salvaguarda", "modo": "vantagem",
                   "condicao": {"todas": ["contra_condicao:envenenado"]}}]),
        traco("tenacidade_ana", "Tenacidade Anã", 187,
              "Seus Pontos de Vida máximos aumentam em 1, e mais 1 a cada nível de personagem.",
              [{"tipo": "modificador", "alvo": "pontos_de_vida_maximos",
                "valor": ["nivel_do_personagem"], "empilha": "soma",
                "nota": "1 no nível 1 e mais 1 por nível: o total é igual ao nível de "
                        "personagem."}]),
        traco("conhecimento_de_pedras", "Conhecimento de Pedras", 187,
              "Ação Bônus para adquirir Sismiconsciência com alcance de 18 metros por 10 "
              "minutos, estando em contato com pedra natural ou trabalhada. Usos iguais ao "
              "Bônus de Proficiência.",
              [recurso_pb("conhecimento_de_pedras", "Conhecimento de Pedras"),
               {"tipo": "conceder_sentido", "sentido": "sismiconsciencia", "alcance_m": 18,
                "custo": "acao_bonus", "duracao": "10 minutos",
                "consome_recurso": "conhecimento_de_pedras",
                "requisito": "estar em, ou tocar, uma superfície de pedra natural ou trabalhada"}]),
    ],
        "Criado da terra por uma divindade da forja: enxerga longe no escuro, resiste a veneno, "
        "ganha vida a cada nível e sente a pedra ao redor."),

    especie("draconato", "Draconato", 188, {"fixo": "medio", "altura": "1,50-2,10 m"}, 9, [
        traco("heranca_draconica", "Herança Dracônica", 188,
              "Escolha o tipo de dragão do seu progenitor. A escolha define o tipo de dano do "
              "Ataque de Sopro e da Resistência a Dano, além da aparência.",
              [{"id": "draconato_heranca", "tipo": "escolha",
                "rotulo": "Escolha o tipo de dragão da sua herança", "quantidade": 1,
                "momento": "criacao",
                "de": {"catalogo": "heranca_draconica", "todo_o_catalogo": True},
                "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                              "catalogo": "heranca_draconica",
                                              "chave": "{{escolhido}}"},
                "define_variavel": "heranca_draconica"}]),
        traco("ataque_de_sopro", "Ataque de Sopro", 188,
              "Na ação Atacar, substitui um dos ataques por um Cone de 4,5 m ou uma Linha de "
              "9 m de largura (escolha a cada vez). Salvaguarda de Destreza; 1d10 do tipo da "
              "sua Herança Dracônica, metade em caso de sucesso. Sobe para 2d10 no nível 5, "
              "3d10 no 11 e 4d10 no 17. Usos iguais ao Bônus de Proficiência.",
              [recurso_pb("ataque_de_sopro", "Ataque de Sopro"),
               {"tipo": "substituir_ataque_por_magia", "modo": "sacrificar_ataque",
                "substitui_por": "ataque_de_sopro",
                "nota": "Reaproveita o primitivo de trocar um ataque da ação Atacar por outra "
                        "coisa; não é magia."},
               {"id": "ataque_de_sopro_area", "tipo": "escolha",
                "rotulo": "Escolha a forma do sopro", "quantidade": 1,
                "momento": "cada_uso", "reescolhivel": True, "reescolha_em": "cada_uso",
                "de": {"catalogo": "areas_de_efeito", "chaves": ["cone", "linha"]},
                "efeito_por_item_escolhido": {"tipo": "efeito_narrativo", "chave": "forma_do_sopro",
                                              "area": "{{escolhido}}"}},
               {"tipo": "dano", "formula_dado": "1d10",
                "tipo_dano_derivado": {
                    "variavel": "heranca_draconica",
                    "mapa": {f"dragao_{i}": d for i, _, d in HERANCA_DRACONICA}},
                "consome_recurso": "ataque_de_sopro",
                "area": {"opcoes": [{"forma": "cone", "tamanho_m": 4.5},
                                    {"forma": "linha", "comprimento_m": 9, "largura_m": 1.5}]},
                "salvaguarda": {"atributo": "DES", "cd": ["8", "mod:CON", "prof"],
                                "em_sucesso": "metade_do_dano"},
                "escalonamento_por_nivel_de_personagem": {"5": "2d10", "11": "3d10", "17": "4d10"}}]),
        traco("resistencia_a_dano_draconato", "Resistência a Dano", 188,
              "Resistência ao tipo de dano da sua Herança Dracônica.",
              [{"tipo": "alterar_dano", "operacao": "resistencia",
                "tipo_dano_derivado": {
                    "variavel": "heranca_draconica",
                    "mapa": {f"dragao_{i}": d for i, _, d in HERANCA_DRACONICA}}}]),
        traco("visao_no_escuro_draconato", "Visão no Escuro", 188,
              "Visão no Escuro com alcance de 18 metros.", [visao_no_escuro(18)]),
        traco("voo_draconico", "Voo Dracônico", 188,
              "No nível 5 de personagem, Ação Bônus para criar asas espectrais por 10 minutos, "
              "com Deslocamento de Voo igual ao seu Deslocamento. Encerra se você as retrair ou "
              "ficar Incapacitado. Uma vez por Descanso Longo.",
              [uma_vez_por_descanso_longo("voo_draconico", "Voo Dracônico"),
               {"tipo": "conceder_velocidade", "tipo_deslocamento": "voo",
                "formula": ["deslocamento"], "custo": "acao_bonus", "duracao": "10 minutos",
                "consome_recurso": "voo_draconico",
                "encerra_se": [{"gatilho": "retrair_as_asas"},
                               {"condicao_id": "incapacitado"}]}],
              nivel_de_personagem=5),
    ],
        "Descendente de dragão: sopro em cone ou linha, resistência ao mesmo tipo de dano e "
        "asas espectrais a partir do nível 5."),

    especie("elfo", "Elfo", 190, {"fixo": "medio", "altura": "1,50-1,80 m"}, 9, [
        traco("visao_no_escuro_elfo", "Visão no Escuro", 190,
              "Visão no Escuro com alcance de 18 metros.", [visao_no_escuro(18)]),
        traco("linhagem_elfica", "Linhagem Élfica", 190,
              "Escolha Alto Elfo, Drow ou Elfo Silvestre. Você ganha o benefício de nível 1 e, "
              "nos níveis 3 e 5, uma magia de círculo superior — sempre preparada, conjurável "
              "uma vez por Descanso Longo sem espaço, ou com qualquer espaço apropriado. O "
              "atributo de conjuração (INT, SAB ou CAR) é escolhido junto com a linhagem.",
              [{"id": "elfo_linhagem", "tipo": "escolha",
                "rotulo": "Escolha sua linhagem élfica", "quantidade": 1, "momento": "criacao",
                "de": {"catalogo": "linhagens_elficas", "todo_o_catalogo": True},
                "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                              "catalogo": "linhagens_elficas",
                                              "chave": "{{escolhido}}"},
                "define_variavel": "linhagem_elfica"},
               {"id": "elfo_atributo_de_conjuracao", "tipo": "escolha",
                "rotulo": "Escolha o atributo de conjuração da linhagem", "quantidade": 1,
                "momento": "criacao",
                "de": {"catalogo": "atributos", "chaves": ["INT", "SAB", "CAR"]},
                "efeito_por_item_escolhido": {"tipo": "efeito_narrativo",
                                              "chave": "atributo_da_linhagem",
                                              "atributo": "{{escolhido}}"},
                "define_variavel": "atributo_da_linhagem_elfica"}]),
        traco("ancestralidade_feerica", "Ancestralidade Feérica", 190,
              "Vantagem nas salvaguardas para evitar ou encerrar a condição Enfeitiçado.",
              [{"tipo": "vantagem", "alvo": "salvaguarda", "modo": "vantagem",
                "condicao": {"todas": ["contra_condicao:enfeiticado"]}}]),
        traco("sentidos_agucados", "Sentidos Aguçados", 190,
              "Proficiência em Intuição, Percepção ou Sobrevivência.",
              [{"id": "elfo_sentidos_agucados", "tipo": "escolha",
                "rotulo": "Escolha uma perícia", "quantidade": 1, "momento": "criacao",
                "de": {"catalogo": "pericias",
                       "chaves": ["intuicao", "percepcao", "sobrevivencia"]},
                "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                              "categoria": "pericia", "chave": "{{escolhido}}",
                                              "nivel_dominio": "proficiente"}}]),
        traco("transe", "Transe", 190,
              "Completa um Descanso Longo em 4 horas meditando, sem dormir e mantendo a "
              "consciência. Magia não pode forçá-lo a dormir.",
              [{"tipo": "alterar_descanso", "descanso": "descanso_longo", "duracao_horas": 4,
                "requer_sono": False, "mantem_consciencia": True},
               {"tipo": "efeito_narrativo", "chave": "imune_a_sono_magico",
                "texto": "Magia não pode forçá-lo a dormir.",
                "nota": "Não é imunidade à condição Inconsciente: é só à imposição mágica de "
                        "sono, que a base não modela como condição própria."}]),
    ],
        "Longevo e transformado pelo ambiente: linhagem que concede magia nos níveis 1, 3 e 5, "
        "vantagem contra Enfeitiçado e Descanso Longo em 4 horas."),
]

ESPECIES += [
    especie("gnomo", "Gnomo", 191, {"fixo": "pequeno", "altura": "0,90-1,20 m"}, 9, [
        traco("visao_no_escuro_gnomo", "Visão no Escuro", 191,
              "Visão no Escuro com alcance de 18 metros.", [visao_no_escuro(18)]),
        traco("astucia_de_gnomo", "Astúcia de Gnomo", 191,
              "Vantagem em salvaguardas de Inteligência, Sabedoria e Carisma.",
              [{"tipo": "vantagem", "alvo": f"salvaguarda:{a}", "modo": "vantagem"}
               for a in ("INT", "SAB", "CAR")]),
        traco("linhagem_gnomica", "Linhagem Gnômica", 191,
              "Escolha Gnomo das Rochas ou Gnomo do Bosque. A escolha também determina se o "
              "atributo de conjuração é Inteligência, Sabedoria ou Carisma.",
              [{"id": "gnomo_linhagem", "tipo": "escolha",
                "rotulo": "Escolha sua linhagem gnômica", "quantidade": 1, "momento": "criacao",
                "de": {"catalogo": "linhagens_gnomicas", "todo_o_catalogo": True},
                "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                              "catalogo": "linhagens_gnomicas",
                                              "chave": "{{escolhido}}"},
                "define_variavel": "linhagem_gnomica"},
               {"id": "gnomo_atributo_de_conjuracao", "tipo": "escolha",
                "rotulo": "Escolha o atributo de conjuração da linhagem", "quantidade": 1,
                "momento": "criacao",
                "de": {"catalogo": "atributos", "chaves": ["INT", "SAB", "CAR"]},
                "efeito_por_item_escolhido": {"tipo": "efeito_narrativo",
                                              "chave": "atributo_da_linhagem",
                                              "atributo": "{{escolhido}}"},
                "define_variavel": "atributo_da_linhagem_gnomica"}]),
    ],
        "Pequeno e mágico: enxerga no escuro, tem Vantagem nas três salvaguardas mentais e "
        "carrega a magia da rocha ou do bosque."),

    especie("golias", "Golias", 192, {"fixo": "medio", "altura": "2,10-2,40 m"}, 10.5, [
        traco("ancestralidade_gigante", "Ancestralidade Gigante", 192,
              "Escolha um benefício sobrenatural da sua linhagem de gigantes. Usos iguais ao "
              "Bônus de Proficiência, restaurados no Descanso Longo.",
              [recurso_pb("ancestralidade_gigante", "Ancestralidade Gigante"),
               {"id": "golias_ancestralidade", "tipo": "escolha",
                "rotulo": "Escolha o benefício da sua ancestralidade gigante", "quantidade": 1,
                "momento": "criacao",
                "de": {"catalogo": "ancestralidades_gigantes", "todo_o_catalogo": True},
                "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                              "catalogo": "ancestralidades_gigantes",
                                              "chave": "{{escolhido}}",
                                              "consome_recurso": "ancestralidade_gigante"},
                "define_variavel": "ancestralidade_gigante"}]),
        traco("forma_grande", "Forma Grande", 192,
              "No nível 5 de personagem, Ação Bônus para virar Grande por 10 minutos, se "
              "couber no espaço: Vantagem em testes de Força e +3 m de Deslocamento. Uma vez "
              "por Descanso Longo.",
              [uma_vez_por_descanso_longo("forma_grande", "Forma Grande"),
               {"tipo": "alterar_tamanho", "novo_tamanho": "grande", "custo": "acao_bonus",
                "duracao": "10 minutos", "consome_recurso": "forma_grande",
                "requisito": "estar em um espaço grande o suficiente",
                "efeitos": [{"tipo": "vantagem", "alvo": "teste_de_atributo", "atributo": "FOR",
                             "modo": "vantagem"},
                            {"tipo": "modificador", "alvo": "deslocamento", "valor": ["3"],
                             "unidade": "metros", "empilha": "soma"}]}],
              nivel_de_personagem=5),
        traco("porte_poderoso", "Porte Poderoso", 192,
              "Vantagem em qualquer teste de atributo para encerrar a condição Imobilizado, e "
              "conta como um tamanho maior para capacidade de carga.",
              [{"tipo": "vantagem", "alvo": "teste_de_atributo", "modo": "vantagem",
                "condicao": {"todas": ["para_encerrar_condicao:imobilizado"]}},
               {"tipo": "modificador", "alvo": "capacidade_de_carga",
                "modo": "conta_como_tamanho_maior", "valor": ["1"], "empilha": "soma"}]),
    ],
        "Descendente de gigantes: benefício ancestral com usos por descanso, Deslocamento de "
        "10,5 m e a possibilidade de crescer para Grande no nível 5."),

    especie("humano", "Humano", 193,
            escolha_de_tamanho("humano", {"medio": "1,20-2,10 m", "pequeno": "0,60-1,20 m"}),
            9, [
                traco("eficiente", "Eficiente", 193,
                      "Adquire Inspiração Heroica sempre que completa um Descanso Longo.",
                      [{"tipo": "conceder_inspiracao_heroica", "gatilho": "descanso_longo"}]),
                traco("habil", "Hábil", 193,
                      "Proficiência em uma perícia à sua escolha.",
                      [{"id": "humano_habil", "tipo": "escolha",
                        "rotulo": "Escolha uma perícia", "quantidade": 1, "momento": "criacao",
                        "de": {"catalogo": "pericias", "todo_o_catalogo": True},
                        "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                                      "categoria": "pericia",
                                                      "chave": "{{escolhido}}",
                                                      "nivel_dominio": "proficiente"}}]),
                traco("versatil", "Versátil", 193,
                      "Um talento de Origem à sua escolha. Habilidoso é recomendado.",
                      [{"id": "humano_versatil", "tipo": "escolha",
                        "rotulo": "Escolha um talento de Origem", "quantidade": 1,
                        "momento": "criacao",
                        "de": {"catalogo": "talentos", "filtro": {"categoria": "origem"}},
                        "efeito_por_item_escolhido": {"tipo": "conceder_talento",
                                                      "talento_id": "{{escolhido}}"}}],
                      recomendado="habilidoso"),
            ],
            "Ambicioso e versátil: Inspiração Heroica a cada Descanso Longo, uma perícia extra "
            "e um talento de Origem à escolha."),

    especie("orc", "Orc", 194, {"fixo": "medio", "altura": "1,80-2,10 m"}, 9, [
        traco("pico_de_adrenalina", "Pico de Adrenalina", 194,
              "Executa a ação Correr como Ação Bônus e ganha Pontos de Vida Temporários iguais "
              "ao Bônus de Proficiência. Usos iguais ao Bônus de Proficiência, restaurados em "
              "Descanso Curto ou Longo.",
              [recurso_pb("pico_de_adrenalina", "Pico de Adrenalina",
                          recarga=("descanso_curto", "descanso_longo")),
               {"tipo": "conceder_acao", "id": "pico_de_adrenalina", "custo": "acao_bonus",
                "acoes": ["correr"], "consome_recurso": "pico_de_adrenalina",
                "efeitos": [{"tipo": "pontos_de_vida_temporarios", "formula": ["prof"],
                             "beneficiario": "voce"}]}]),
        traco("visao_no_escuro_orc", "Visão no Escuro", 194,
              "Visão no Escuro com alcance de 36 metros.", [visao_no_escuro(36)]),
        traco("vigor_implacavel", "Vigor Implacável", 194,
              "Ao ser reduzido a 0 Pontos de Vida sem morrer na hora, você fica com 1 Ponto de "
              "Vida. Uma vez por Descanso Longo.",
              [uma_vez_por_descanso_longo("vigor_implacavel", "Vigor Implacável"),
               {"tipo": "substituir_resultado_de_d20", "alvo": "pontos_de_vida_maximos",
                "modo": "ficar_com_1_ponto_de_vida",
                "gatilho": "reduzido_a_0_pontos_de_vida_sem_morrer",
                "consome_recurso": "vigor_implacavel"}]),
    ],
        "Dons de Gruumsh: corrida como Ação Bônus com PV temporários, visão de 36 m e a "
        "teimosia de não cair na primeira vez."),

    especie("pequenino", "Pequenino", 195, {"fixo": "pequeno", "altura": "0,60-0,90 m"}, 9, [
        traco("corajoso", "Corajoso", 195,
              "Vantagem nas salvaguardas para evitar ou encerrar a condição Amedrontado.",
              [{"tipo": "vantagem", "alvo": "salvaguarda", "modo": "vantagem",
                "condicao": {"todas": ["contra_condicao:amedrontado"]}}]),
        traco("agilidade_pequenina", "Agilidade Pequenina", 195,
              "Move-se pelo espaço de qualquer criatura um tamanho maior que você, mas não "
              "pode parar nele.",
              [{"tipo": "efeito_narrativo", "chave": "mover_pelo_espaco_de_criatura_maior",
                "texto": "Move-se pelo espaço de criatura ao menos um tamanho maior; não pode "
                         "terminar o movimento nesse espaço.",
                "restricao_de_tamanho": "um_tamanho_maior_ou_mais",
                "pode_parar_no_espaco": False}]),
        traco("sorte_pequenina", "Sorte", 195,
              "Ao tirar 1 no d20 de um Teste de D20, joga o dado novamente e usa a nova jogada.",
              [{"tipo": "rolar_novamente", "alvo": "teste_d20", "gatilho": "resultado_natural_1",
                "usa_o_novo_resultado": True}]),
        traco("furtividade_natural", "Furtividade Natural", 195,
              "Executa a ação Esconder mesmo estando encoberto apenas por uma criatura ao menos "
              "um tamanho maior que você.",
              [{"tipo": "efeito_narrativo", "chave": "esconder_atras_de_criatura_maior",
                "texto": "Pode executar a ação Esconder encoberto apenas por criatura ao menos "
                         "um tamanho maior que você.",
                "acao_id": "esconder"}]),
    ],
        "Pequeno, corajoso e sortudo: rerrola o 1 natural, esconde-se atrás de gente grande e "
        "passa pelo espaço dela."),

    especie("tiferino", "Tiferino", 197,
            escolha_de_tamanho("tiferino", {"medio": "1,20-2,10 m", "pequeno": "0,90-1,20 m"}),
            9, [
                traco("visao_no_escuro_tiferino", "Visão no Escuro", 197,
                      "Visão no Escuro com alcance de 18 metros.", [visao_no_escuro(18)]),
                traco("legado_infero", "Legado Ínfero", 197,
                      "Escolha Abissal, Ctônico ou Infernal. Você ganha o benefício de nível 1 "
                      "e, nos níveis 3 e 5, magias de círculo superior — sempre preparadas, "
                      "conjuráveis uma vez por Descanso Longo sem espaço, ou com qualquer "
                      "espaço do círculo correspondente. O atributo de conjuração (INT, SAB ou "
                      "CAR) é escolhido junto com o legado.",
                      [{"id": "tiferino_legado", "tipo": "escolha",
                        "rotulo": "Escolha seu legado ínfero", "quantidade": 1,
                        "momento": "criacao",
                        "de": {"catalogo": "legados_inferos", "todo_o_catalogo": True},
                        "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                                      "catalogo": "legados_inferos",
                                                      "chave": "{{escolhido}}"},
                        "define_variavel": "legado_infero"},
                       {"id": "tiferino_atributo_de_conjuracao", "tipo": "escolha",
                        "rotulo": "Escolha o atributo de conjuração do legado", "quantidade": 1,
                        "momento": "criacao",
                        "de": {"catalogo": "atributos", "chaves": ["INT", "SAB", "CAR"]},
                        "efeito_por_item_escolhido": {"tipo": "efeito_narrativo",
                                                      "chave": "atributo_do_legado",
                                                      "atributo": "{{escolhido}}"},
                        "define_variavel": "atributo_do_legado_infero"}]),
                traco("presenca_sobrenatural", "Presença Sobrenatural", 197,
                      "Você conhece o truque Taumaturgia, conjurado com o mesmo atributo do "
                      "Legado Ínfero.",
                      [truque("taumaturgia",
                              nota="Usa o atributo escolhido no Legado Ínfero.")]),
            ],
            "Ligado por sangue aos Planos Inferiores: legado que concede resistência, truque e "
            "magias nos níveis 1, 3 e 5."),
]

ALVOS_NOVOS = [
    ("capacidade_de_carga", "Capacidade de carga",
     "O quanto o personagem consegue carregar. Já existe como valor derivado; passa a ser alvo "
     "para que um efeito possa alterá-la — Porte Poderoso (Golias) conta um tamanho maior.",
     "capacidade_de_carga"),
]

SENTIDOS_NOVOS = [
    ("sismiconsciencia", "Sismiconsciência",
     "Percebe e localiza criaturas e objetos em movimento pelas vibrações, dentro do alcance, "
     "desde que ambos estejam em contato com a mesma superfície. Conhecimento de Pedras (Anão)."),
]

TIPOS_NOVOS = [
    ("alterar_tamanho", "Alterar tamanho",
     "Muda o tamanho da criatura por uma duração, com efeitos próprios enquanto durar. "
     "Forma Grande (Golias)."),
    ("alterar_descanso", "Alterar descanso",
     "Muda a duração ou os requisitos de um tipo de descanso. Transe (Elfo) completa um "
     "Descanso Longo em 4 horas, sem dormir."),
]


def juntar(caminho, novos, campos):
    d = json.load(open(caminho, encoding='utf-8'),
                  object_pairs_hook=collections.OrderedDict)
    existentes = {i['id'] for i in d['itens']}
    n = 0
    for valores in novos:
        item = collections.OrderedDict(zip(campos, valores))
        if item['id'] in existentes:
            continue
        d['itens'].append(item)
        n += 1
    d['total'] = len(d['itens'])
    json.dump(d, open(caminho, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return n


def main():
    cats = [CAT_HERANCA, CAT_LINHAGEM_ELFICA, CAT_LINHAGEM_GNOMICA,
            CAT_ANCESTRALIDADE_GIGANTE, CAT_REVELACAO_CELESTIAL, CAT_LEGADO_INFERO]
    for c in cats:
        with open(f"{CAT}/{c['catalogo']}.json", 'w', encoding='utf-8') as f:
            json.dump(c, f, ensure_ascii=False, indent=2)

    n_alvos = juntar(f'{CAT}/alvos.json', ALVOS_NOVOS,
                     ['id', 'nome', 'descricao_curta', 'derivado_id'])
    n_sent = juntar(f'{CAT}/sentidos.json', SENTIDOS_NOVOS, ['id', 'nome', 'descricao_curta'])
    n_tipos = juntar(f'{CAT}/tipos_de_efeito.json', TIPOS_NOVOS,
                     ['id', 'nome', 'descricao_curta'])

    d = collections.OrderedDict([
        ("catalogo", "especies"), ("nome", "Espécies de Personagem"), ("fonte", fonte(186)),
        ("nota", "As 10 do capítulo 4. Cada espécie tem tipo de criatura, tamanho, deslocamento "
                 "e traços próprios. Quatro têm linhagem, em catálogo de opção separado."),
        ("preenchida", True), ("total", len(ESPECIES)), ("itens", ESPECIES)])
    with open(f"{CAT}/especies.json", 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    print(f"espécies: {len(ESPECIES)} | traços: {sum(len(e['tracos']) for e in ESPECIES)}")
    print("catálogos de linhagem: " + ", ".join(f"{c['catalogo']} ({c['total']})" for c in cats))
    print(f"sentidos novos: {n_sent} | tipos de efeito novos: {n_tipos} | "
          f"alvos novos: {n_alvos}")


if __name__ == '__main__':
    main()
