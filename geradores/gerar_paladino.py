# -*- coding: utf-8 -*-
"""Paladino (cap. 3, p. 167-175). Fecha as 12 classes do livro.

Três coisas merecem nota.

A primeira é que Canalizar Divindade NÃO é a mesma característica do Clérigo. O
recurso é próprio (2 usos, 3 no nível 11), a CD sai da Conjuração do Paladino e a
opção base é Sentido Divino. As opções do Paladino entram no catálogo já existente
`efeitos_de_canalizar_divindade` marcadas com `classe`, e cada característica que
abre uma opção nova a libera com `expandir_opcoes_de_escolha` — inclusive as das
subclasses, que é exatamente o caso que o catálogo previa quando nasceu 'parcial'.

A segunda é Mãos Consagradas: uma RESERVA DE PONTOS DE VIDA (cinco vezes o nível),
gasta em cura ou em 5 pontos por condição removida. Não é dado de cura nem recurso
com usos — é um pote numérico. Entra como tipo novo, `reserva_de_cura`.

A terceira é a Aura de Proteção: uma Emanação de 3 metros (9 no nível 18) que
outras características só ENGROSSAM. Todas elas apontam para ela com
`melhorar_caracteristica`, e não recriam a aura — assim o app soma os efeitos numa
aura só, que é como a mesa joga.
"""
import json, collections

CAT = 'dados/catalogos'


def fonte(p):
    return {"capitulo": 3, "pagina_livro": p, "pagina_pdf": p + 4}


def rev(status="ok", notas=""):
    return {"status": status, "notas": notas}


CARACS = []


def car(cid, nome, nivel, pag, desc, efeitos, **extra):
    d = collections.OrderedDict([
        ("id", cid), ("nome", nome), ("classe", "paladino"), ("nivel", nivel),
        ("fonte", fonte(pag)), ("revisao", rev()),
        ("descricao_curta", desc), ("efeitos", efeitos)])
    d.update(extra)
    CARACS.append(d)
    return d


def sub(cid, nome, nivel, pag, desc, efeitos, subclasse, **extra):
    d = car(cid, nome, nivel, pag, desc, efeitos, **extra)
    d['subclasse'] = subclasse
    return d


def tabela_magias(nome, pag, linhas):
    return {"nome": nome, "fonte": fonte(pag),
            "linhas": [{"nivel": n, "magias": m} for n, m in linhas]}


CD = ["8", "mod:CAR", "prof"]

# ============================================================ classe, nível 1

car("conjuracao_paladino", "Conjuração", 1, 167,
    "Conjura pela lista de Paladino, com Carisma. Prepara da lista inteira conforme a coluna "
    "Magias Preparadas, trocando uma a cada Descanso Longo. Usa Símbolo Sagrado.",
    [{"tipo": "conceder_slot", "tabela_progressao_id": "paladino",
      "colunas": ["espacos_1", "espacos_2", "espacos_3", "espacos_4", "espacos_5"],
      "recarga": "descanso_longo"},
     {"tipo": "preparar_magias", "formula_quantidade": ["coluna:magias_preparadas"],
      "atributo_conjuracao": "CAR", "fonte_das_magias": "lista_de_classe",
      "lista_id": "paladino",
      "restricao": "de um círculo para o qual você possui espaços de magia",
      "magias_sempre_preparadas_nao_contam": True},
     {"tipo": "desbloquear_magias", "lista_id": "paladino",
      "modo": "disponivel_para_preparar", "atributo_conjuracao": "CAR"},
     {"id": "paladino_preparadas", "tipo": "escolha",
      "rotulo": "Prepare magias de Paladino", "quantidade": "coluna:magias_preparadas",
      "momento": "nivel_1", "reescolhivel": True, "reescolha_em": "descanso_longo",
      "reescolha_quantidade": 1,
      "de": {"catalogo": "magias",
             "filtro": {"nivel_minimo": 1, "lista": "paladino",
                        "circulo_com_espaco_disponivel": True}},
      "efeito_por_item_escolhido": {"tipo": "desbloquear_magias", "lista_id": "paladino",
                                    "modo": "preparada", "magia": "{{escolhido}}"}}],
    foco_de_conjuracao=["amuleto", "emblema", "relicario"],
    cd_para_evitar_sua_magia=CD,
    nota_do_livro="Sem truques, como o Guardião. Os dois truques de Clérigo do Combatente "
                  "Abençoado são a única porta para truques na classe.")

car("maestria_em_arma_paladino", "Maestria em Arma", 1, 168,
    "Usa as propriedades de maestria de dois tipos de arma à escolha entre aquelas com que tem "
    "proficiência. Troca as escolhas a cada Descanso Longo.",
    [{"id": "paladino_maestrias", "tipo": "escolha",
      "rotulo": "Escolha os tipos de arma com maestria", "quantidade": 2,
      "momento": "nivel_1", "reescolhivel": True, "reescolha_em": "descanso_longo",
      "de": {"catalogo": "itens",
             "filtro": {"categoria": "arma", "grupo": ["simples", "marcial"]}},
      "efeito_por_item_escolhido": {"tipo": "conceder_maestria_de_arma",
                                    "arma": "{{escolhido}}"}}])

car("maos_consagradas", "Mãos Consagradas", 1, 168,
    "Reserva de cura igual a cinco vezes o seu nível de Paladino, que volta no Descanso Longo. "
    "Ação Bônus para tocar uma criatura e gastar quanto quiser da reserva em Pontos de Vida; ou "
    "gastar 5 pontos para remover a condição Envenenado, sem curar.",
    [{"tipo": "reserva_de_cura", "id": "maos_consagradas", "nome": "Mãos Consagradas",
      "formula_maximo": {"op": "mult", "args": ["5", "nivel_classe:paladino"]},
      "unidade": "pontos_de_vida", "recarga": ["descanso_longo"]},
     {"tipo": "cura", "consome_reserva": "maos_consagradas", "quantidade": "a_escolha_do_jogador",
      "custo": "acao_bonus", "alcance": "toque", "beneficiario": "criatura_tocada_ou_voce"},
     {"tipo": "remover_condicao", "condicoes": ["envenenado"], "quantidade": 1,
      "consome_reserva": "maos_consagradas", "custo_na_reserva": 5,
      "nao_restaura_pv": True, "custo": "acao_bonus"}])

# ============================================================ classe, nível 2

car("destruicao_do_paladino", "Destruição do Paladino", 2, 168,
    "Destruição Divina sempre preparada, e conjurável uma vez por Descanso Longo sem gastar "
    "espaço de magia.",
    [{"tipo": "desbloquear_magias", "lista_id": "paladino", "modo": "sempre_preparada",
      "magias": ["destruicao_divina"]},
     {"tipo": "recurso_com_recarga", "id": "destruicao_do_paladino",
      "nome": "Destruição do Paladino", "formula_maximo": ["1"],
      "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "conjurar_sem_espaco", "magia": "destruicao_divina",
      "consome_recurso": "destruicao_do_paladino"}])

car("estilo_de_luta_paladino", "Estilo de Luta", 2, 168,
    "Adquire um talento de Estilo de Luta à escolha; em vez dele, pode pegar Combatente "
    "Abençoado, que dá dois truques de Clérigo conjurados com Carisma.",
    [{"id": "paladino_estilo_de_luta", "tipo": "escolha",
      "rotulo": "Escolha um talento de Estilo de Luta", "quantidade": 1,
      "momento": "nivel_2",
      "de": {"catalogo": "talentos", "filtro": {"categoria": "estilo_de_luta"}},
      "efeito_por_item_escolhido": {"tipo": "conceder_talento",
                                    "talento_id": "{{escolhido}}"}},
     {"tipo": "expandir_opcoes_de_escolha", "escolha_id": "paladino_estilo_de_luta",
      "catalogo": "opcoes_de_estilo_de_luta_de_classe", "chaves": ["combatente_abencoado"],
      "nota": "Mesma construção do Combatente Druídico do Guardião: a opção da classe entra na "
              "escolha do talento, não numa escolha à parte."}])

# ============================================================ classe, nível 3+

car("canalizar_divindade_paladino", "Canalizar Divindade", 3, 168,
    "Recurso próprio do Paladino: dois usos, três a partir do nível 11, com um recuperado no "
    "Descanso Curto e todos no Longo. Começa com Sentido Divino; outras características de "
    "classe e as subclasses acrescentam opções. A CD é a mesma da sua Conjuração.",
    [{"tipo": "recurso_com_recarga", "id": "canalizar_divindade_paladino",
      "nome": "Canalizar Divindade", "formula_maximo": ["coluna:canalizar_divindade"],
      "recarga": [{"gatilho": "descanso_curto", "quantidade": 1},
                  {"gatilho": "descanso_longo", "quantidade": "todos"}],
      "consumo": "por_uso"},
     {"tipo": "canalizar_divindade", "recurso_id": "canalizar_divindade_paladino",
      "opcoes": {"catalogo": "efeitos_de_canalizar_divindade",
                 "base": ["sentido_divino"],
                 "expansivel_por_subclasse": True,
                 "filtro": {"classe": "paladino"}},
      "cd": CD},
     {"id": "canalizar_divindade_paladino_opcao", "tipo": "escolha",
      "rotulo": "Escolha o efeito de Canalizar Divindade", "quantidade": 1,
      "momento": "cada_uso", "reescolhivel": True, "reescolha_em": "cada_uso",
      "de": {"catalogo": "efeitos_de_canalizar_divindade",
             "filtro": {"classe": "paladino"}},
      "efeito_por_item_escolhido": {"tipo": "aplicar_efeito_nomeado",
                                    "catalogo": "efeitos_de_canalizar_divindade",
                                    "chave": "{{escolhido}}"},
      "nota": "É esta escolha que as características de classe e de subclasse expandem: "
              "Repudiar Inimigos, Arma Sagrada, Voto de Inimizade e as demais entram aqui."}],
    revisao=rev("ok", "Recurso separado do Canalizar Divindade do Clérigo: id próprio, coluna "
                      "própria e opções próprias. Só o nome é compartilhado."))

car("montaria_fiel", "Montaria Fiel", 5, 169,
    "Convocar Montaria sempre preparada, e conjurável uma vez por Descanso Longo sem gastar "
    "espaço de magia.",
    [{"tipo": "desbloquear_magias", "lista_id": "paladino", "modo": "sempre_preparada",
      "magias": ["convocar_montaria"]},
     {"tipo": "recurso_com_recarga", "id": "montaria_fiel", "nome": "Montaria Fiel",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "conjurar_sem_espaco", "magia": "convocar_montaria",
      "consome_recurso": "montaria_fiel"}])

car("aura_de_protecao", "Aura de Proteção", 6, 169,
    "Emanação de 3 metros: você e seus aliados dentro dela ganham bônus em salvaguardas igual ao "
    "seu modificador de Carisma (mínimo +1). Inativa enquanto você estiver Incapacitado, e uma "
    "criatura só se beneficia de uma Aura de Proteção por vez.",
    [{"tipo": "emanacao", "id": "aura_de_protecao", "tamanho_m": 3, "origem": "voce",
      "ativacao": "passiva",
      "inativa_se": [{"condicao_id": "incapacitado"}],
      "beneficiarios": "voce_e_aliados_na_emanacao",
      "empilha": "unico",
      "nota_de_empilhamento": "Com outro Paladino presente, a criatura escolhe de qual aura se "
                              "beneficia enquanto está nela.",
      "efeitos": [{"tipo": "modificador", "alvo": "salvaguarda",
                   "valor": {"op": "max", "args": ["1", "mod:CAR"]},
                   "empilha": "soma"}]}])

car("repudiar_inimigos", "Repudiar Inimigos", 9, 169,
    "Ação Usar Magia e um uso de Canalizar Divindade: criaturas à vista a até 18 m, em número "
    "igual ao modificador de Carisma, fazem salvaguarda de Sabedoria ou ficam Amedrontadas por "
    "1 minuto ou até sofrerem dano — e, enquanto isso, só podem mover-se, agir ou usar uma Ação "
    "Bônus no turno, nunca as três.",
    [{"tipo": "expandir_opcoes_de_escolha", "escolha_id": "canalizar_divindade_paladino_opcao",
      "catalogo": "efeitos_de_canalizar_divindade", "chaves": ["repudiar_inimigos"]}])

car("aura_de_coragem", "Aura de Coragem", 10, 169,
    "Você e seus aliados têm Imunidade à condição Amedrontado dentro da Aura de Proteção — e um "
    "aliado que entre Amedrontado não sofre a condição enquanto estiver nela.",
    [{"tipo": "melhorar_caracteristica", "alvo": "aura_de_protecao",
      "efeitos": [{"tipo": "alterar_condicao", "condicao_id": "amedrontado",
                   "operacao": "imunidade", "beneficiarios": "voce_e_aliados_na_emanacao",
                   "nota": "Suspende a condição já existente enquanto o aliado estiver na aura."}]}])

car("golpes_radiantes", "Golpes Radiantes", 11, 169,
    "Ao atingir com uma arma Corpo a Corpo ou Ataque Desarmado, o alvo sofre 1d8 de dano "
    "Radiante adicional.",
    [{"tipo": "dado_de_impacto", "formula_dado": "1d8", "tipo_dano": "radiante",
      "condicao": {"alguma": ["acerto_com_arma_corpo_a_corpo", "acerto_com_ataque_desarmado"]}}])

car("toque_restaurador", "Toque Restaurador", 14, 169,
    "Ao usar Mãos Consagradas, pode gastar 5 pontos da reserva por condição para remover "
    "Amedrontado, Atordoado, Cego, Enfeitiçado, Paralisado ou Surdo. Esses pontos não curam.",
    [{"tipo": "melhorar_caracteristica", "alvo": "maos_consagradas",
      "efeitos": [{"tipo": "remover_condicao",
                   "condicoes": ["amedrontado", "atordoado", "cego", "enfeiticado",
                                 "paralisado", "surdo"],
                   "quantidade": "a_escolha_do_jogador",
                   "consome_reserva": "maos_consagradas", "custo_na_reserva": 5,
                   "custo_por": "condicao_removida", "nao_restaura_pv": True}]}])

car("aura_expandida", "Aura Expandida", 18, 169,
    "Sua Aura de Proteção passa a ser uma Emanação de 9 metros.",
    [{"tipo": "melhorar_caracteristica", "alvo": "aura_de_protecao",
      "efeitos": [{"tipo": "modificador", "alvo": "tamanho_da_emanacao", "valor": 9,
                   "empilha": "substitui", "escopo": {"emanacao": "aura_de_protecao"}}]}])


def opcao_cd(cid, nome, pag, desc, efeitos, subclasse=None):
    """Opção de Canalizar Divindade do Paladino, no catálogo compartilhado."""
    d = collections.OrderedDict([
        ("id", cid), ("nome", nome), ("classe", "paladino"), ("fonte", fonte(pag)),
        ("descricao_curta", desc), ("efeitos", efeitos)])
    if subclasse:
        d["subclasse"] = subclasse
        d["apenas_se_concedido"] = True
    OPCOES_CD.append(d)
    return d


OPCOES_CD = []

opcao_cd("sentido_divino", "Sentido Divino", 169,
         "Ação Bônus: por 10 minutos ou até ficar Incapacitado, você sabe a localização e o tipo "
         "de qualquer Celestial, Ínfero ou Morto-Vivo a até 18 m, e detecta lugares e objetos "
         "consagrados ou profanados no mesmo raio.",
         [{"tipo": "efeito_narrativo", "chave": "detectar_tipos_de_criatura",
           "texto": "Revela localização e tipo de Celestiais, Ínferos e Mortos-Vivos a até 18 m, "
                    "e lugares ou objetos consagrados ou profanados como na magia Consagrar.",
           "custo": "acao_bonus", "alcance_m": 18, "duracao": "10 minutos",
           "tipos_de_criatura": ["celestial", "infero", "morto_vivo"],
           "encerra_se": [{"condicao_id": "incapacitado"}]}])

opcao_cd("repudiar_inimigos", "Repudiar Inimigos", 169,
         "Ação Usar Magia: criaturas à vista a até 18 m, em número igual ao modificador de "
         "Carisma, fazem salvaguarda de Sabedoria ou ficam Amedrontadas por 1 minuto ou até "
         "sofrerem dano; Amedrontadas assim, só fazem uma coisa por turno.",
         [{"tipo": "conceder_condicao", "condicao_id": "amedrontado",
           "custo": "acao", "acao_id": "usar_magia", "alcance_m": 18,
           "alvo": "criaturas_a_vista",
           "quantidade_de_alvos": {"op": "max", "args": ["1", "mod:CAR"]},
           "salvaguarda": {"atributo": "SAB", "cd": CD},
           "duracao": "1 minuto",
           "encerra_se": [{"gatilho": "alvo_sofre_dano"}]},
          {"tipo": "impedir", "alvo": ["acao", "acao_bonus"],
           "modo": "apenas_uma_das_tres",
           "nota": "Amedrontado por esta característica, o alvo escolhe UMA por turno: mover-se, "
                   "executar uma ação ou executar uma Ação Bônus.",
           "condicao": {"todas": ["amedrontado_por:repudiar_inimigos"]}}])

# ============================================== subclasse: Juramento da Devoção

sub("magias_do_juramento_da_devocao", "Magias do Juramento da Devoção", 3, 171,
    "Magias sempre preparadas pela tabela Magias do Juramento da Devoção, sem contar para o limite.",
    [{"tipo": "magias_de_patrono",
      "tabela": tabela_magias("Magias do Juramento da Devoção", 171, [
          (3, ["escudo_da_fe", "protecao_contra_o_bem_e_o_mal"]),
          (5, ["auxilio", "zona_da_verdade"]),
          (9, ["dissipar_magia", "sinal_de_esperanca"]),
          (13, ["defensor_da_fe", "movimentacao_livre"]),
          (17, ["coluna_de_chamas", "comunhao"])]),
      "modo": "sempre_preparada", "lista_id": "paladino",
      "acesso_concedido_pela_subclasse": True, "nao_conta_para_o_limite": True}],
    "juramento_da_devocao")

sub("arma_sagrada", "Arma Sagrada", 3, 172,
    "Opção de Canalizar Divindade na ação Atacar: por 10 minutos, a arma Corpo a Corpo empunhada "
    "soma o modificador de Carisma às jogadas de ataque (mínimo +1), pode causar dano Radiante "
    "no lugar do tipo normal e emite Luz Plena em 6 m e Meia-luz por mais 6 m.",
    [{"tipo": "expandir_opcoes_de_escolha", "escolha_id": "canalizar_divindade_paladino_opcao",
      "catalogo": "efeitos_de_canalizar_divindade", "chaves": ["arma_sagrada"]}],
    "juramento_da_devocao")

opcao_cd("arma_sagrada", "Arma Sagrada", 172,
         "Na ação Atacar, imbui uma arma Corpo a Corpo empunhada por 10 minutos ou até usar de "
         "novo: +modificador de Carisma nas jogadas de ataque (mínimo +1), dano Radiante à "
         "escolha e Luz Plena em 6 m mais Meia-luz por 6 m. Encerra se largar a arma.",
         [{"tipo": "modificador", "alvo": "jogada_de_ataque",
           "valor": {"op": "max", "args": ["1", "mod:CAR"]}, "empilha": "soma",
           "escopo": "arma_imbuida"},
          {"tipo": "escolher_tipo_de_dano", "opcoes": ["mesmo_da_arma", "radiante"],
           "escopo": "arma_imbuida"},
          {"tipo": "efeito_narrativo", "chave": "emite_luz",
           "texto": "Luz Plena em raio de 6 m e Meia-luz por mais 6 m.",
           "luz_plena_m": 6, "meia_luz_m": 6}],
         subclasse="juramento_da_devocao")

sub("aura_de_devocao", "Aura de Devoção", 7, 172,
    "Você e seus aliados têm Imunidade à condição Enfeitiçado dentro da Aura de Proteção.",
    [{"tipo": "melhorar_caracteristica", "alvo": "aura_de_protecao",
      "efeitos": [{"tipo": "alterar_condicao", "condicao_id": "enfeiticado",
                   "operacao": "imunidade", "beneficiarios": "voce_e_aliados_na_emanacao"}]}],
    "juramento_da_devocao")

sub("destruicao_protetora", "Destruição Protetora", 15, 172,
    "Ao conjurar Destruição Divina, você e seus aliados na Aura de Proteção ganham Cobertura "
    "Parcial até o início do seu próximo turno.",
    [{"tipo": "melhorar_caracteristica", "alvo": "aura_de_protecao",
      "efeitos": [{"tipo": "conceder_cobertura", "grau": "parcial",
                   "alvos": {"voce_e_aliados_na_emanacao": True},
                   "gatilho": "conjurar:destruicao_divina",
                   "duracao": "ate_o_inicio_do_seu_proximo_turno"}]}],
    "juramento_da_devocao")

sub("resplendor_sagrado", "Resplendor Sagrado", 20, 172,
    "Ação Bônus, uma vez por Descanso Longo (ou gastando um espaço de 5º círculo): por 10 minutos "
    "a Aura de Proteção causa dano Radiante igual ao modificador de Carisma mais o Bônus de "
    "Proficiência a inimigos que comecem o turno nela, enche-se de Luz Plena que é luz solar, e "
    "você tem Vantagem em salvaguardas forçadas por Ínferos e Mortos-Vivos.",
    [{"tipo": "recurso_com_recarga", "id": "resplendor_sagrado", "nome": "Resplendor Sagrado",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso",
      "recuperacao_alternativa": {"consome": "espaco_de_magia", "circulo": 5, "custo": "livre"}},
     {"tipo": "melhorar_caracteristica", "alvo": "aura_de_protecao",
      "custo": "acao_bonus", "duracao": "10 minutos", "consome_recurso": "resplendor_sagrado",
      "efeitos": [{"tipo": "dano", "formula": ["mod:CAR", "prof"], "tipo_dano": "radiante",
                   "alvo": "inimigo_na_emanacao",
                   "gatilho": "inicio_do_turno_do_inimigo_na_emanacao"},
                  {"tipo": "efeito_narrativo", "chave": "emite_luz",
                   "texto": "A aura é preenchida com Luz Plena que conta como luz solar.",
                   "luz_solar": True},
                  {"tipo": "vantagem", "alvo": "salvaguarda", "modo": "vantagem",
                   "condicao": {"todas": ["forcada_por:infero_ou_morto_vivo"]}}]}],
    "juramento_da_devocao")


# ============================================== subclasse: Juramento da Glória

sub("atleta_inigualavel", "Atleta Inigualável", 3, 173,
    "Opção de Canalizar Divindade, Ação Bônus: por 1 hora, Vantagem em testes de Força "
    "(Atletismo) e Destreza (Acrobacia), e +3 m na distância dos Saltos Longo e em Altura.",
    [{"tipo": "expandir_opcoes_de_escolha", "escolha_id": "canalizar_divindade_paladino_opcao",
      "catalogo": "efeitos_de_canalizar_divindade", "chaves": ["atleta_inigualavel"]}],
    "juramento_da_gloria")

opcao_cd("atleta_inigualavel", "Atleta Inigualável", 173,
         "Ação Bônus: por 1 hora, Vantagem em testes de Força (Atletismo) e Destreza "
         "(Acrobacia), e a distância dos seus Saltos Longo e em Altura aumenta em 3 m — a "
         "distância adicional custa movimento padrão.",
         [{"tipo": "vantagem", "alvo": "teste_de_atributo", "modo": "vantagem",
           "pericias": ["atletismo", "acrobacia"], "custo": "acao_bonus",
           "duracao": "1 hora"},
          {"tipo": "efeito_narrativo", "chave": "aumentar_salto",
           "texto": "Saltos Longo e em Altura aumentam em 3 m; a distância adicional custa "
                    "movimento padrão.",
           "distancia_adicional_m": 3, "duracao": "1 hora"}],
         subclasse="juramento_da_gloria")

sub("destruicao_inspiradora", "Destruição Inspiradora", 3, 173,
    "Opção de Canalizar Divindade logo após conjurar Destruição Divina: 2d8 mais o seu nível de "
    "Paladino em Pontos de Vida Temporários, divididos como quiser entre criaturas à escolha a "
    "até 9 m, você incluído.",
    [{"tipo": "expandir_opcoes_de_escolha", "escolha_id": "canalizar_divindade_paladino_opcao",
      "catalogo": "efeitos_de_canalizar_divindade", "chaves": ["destruicao_inspiradora"]}],
    "juramento_da_gloria")

opcao_cd("destruicao_inspiradora", "Destruição Inspiradora", 173,
         "Imediatamente após conjurar Destruição Divina: 2d8 mais o seu nível de Paladino em "
         "Pontos de Vida Temporários, divididos como preferir entre criaturas à sua escolha a "
         "até 9 m, incluindo você.",
         [{"tipo": "pontos_de_vida_temporarios",
           "formula": {"op": "soma", "args": ["2d8", "nivel_classe:paladino"]},
           "distribuivel": True, "alcance_m": 9, "inclui_voce": True,
           "gatilho": "imediatamente_apos_conjurar:destruicao_divina"}],
         subclasse="juramento_da_gloria")

sub("magias_do_juramento_da_gloria", "Magias do Juramento da Glória", 3, 173,
    "Magias sempre preparadas pela tabela Magias do Juramento da Glória, sem contar para o limite.",
    [{"tipo": "magias_de_patrono",
      "tabela": tabela_magias("Magias do Juramento da Glória", 173, [
          (3, ["heroismo", "raio_guia"]),
          (5, ["aprimorar_atributo", "arma_magica"]),
          (9, ["celeridade", "protecao_contra_energia"]),
          (13, ["compulsao", "movimentacao_livre"]),
          (17, ["lendas_e_historias", "presenca_regia_de_yolande"])]),
      "modo": "sempre_preparada", "lista_id": "paladino",
      "acesso_concedido_pela_subclasse": True, "nao_conta_para_o_limite": True}],
    "juramento_da_gloria")

sub("aura_de_vivacidade", "Aura de Vivacidade", 7, 173,
    "Seu Deslocamento aumenta em 3 m. E o aliado que entra na Aura de Proteção pela primeira vez "
    "no turno, ou começa o turno nela, ganha +3 m de Deslocamento até o fim do próximo turno dele.",
    [{"tipo": "modificador", "alvo": "deslocamento", "valor": ["3"], "unidade": "metros",
      "empilha": "soma"},
     {"tipo": "melhorar_caracteristica", "alvo": "aura_de_protecao",
      "efeitos": [{"tipo": "modificador", "alvo": "deslocamento", "valor": ["3"],
                   "unidade": "metros", "empilha": "soma", "beneficiario": "aliado",
                   "gatilho": "entrar_na_emanacao_pela_primeira_vez_no_turno_ou_comecar_o_turno_nela",
                   "duracao": "ate_o_fim_do_proximo_turno_do_aliado"}]}],
    "juramento_da_gloria")

sub("defesa_gloriosa", "Defesa Gloriosa", 15, 173,
    "Quando você ou criatura à vista a até 3 m é atingida por um ataque, Reação para dar bônus de "
    "CA igual ao modificador de Carisma (mínimo +1) contra ele — e, se o ataque errar, você pode "
    "atacar o atacante na mesma Reação. Usos iguais ao modificador de Carisma.",
    [{"tipo": "recurso_com_recarga", "id": "defesa_gloriosa", "nome": "Defesa Gloriosa",
      "formula_maximo": {"op": "max", "args": ["1", "mod:CAR"]},
      "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "modificador", "alvo": "ca_total",
      "valor": {"op": "max", "args": ["1", "mod:CAR"]}, "empilha": "soma",
      "custo": "reacao", "consome_recurso": "defesa_gloriosa",
      "beneficiario": "voce_ou_criatura_a_vista_a_ate_3m",
      "gatilho": "ser_atingido_por_jogada_de_ataque",
      "escopo": "apenas_contra_esse_ataque"},
     {"tipo": "conceder_ataque", "quantidade": ["1"], "alvo_do_ataque": "o_atacante",
      "junto_com": "a mesma Reação, se o ataque passar a errar e o atacante estiver no alcance "
                   "da sua arma"}],
    "juramento_da_gloria")

sub("lenda_viva", "Lenda Viva", 20, 173,
    "Ação Bônus, uma vez por Descanso Longo (ou gastando um espaço de 5º círculo): por 10 minutos, "
    "Vantagem em todos os testes de Carisma; uma vez por turno pode transformar um erro de ataque "
    "com arma em acerto; e pode rolar de novo uma salvaguarda falha, valendo o novo resultado.",
    [{"tipo": "recurso_com_recarga", "id": "lenda_viva", "nome": "Lenda Viva",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso",
      "recuperacao_alternativa": {"consome": "espaco_de_magia", "circulo": 5, "custo": "livre"}},
     {"tipo": "vantagem", "alvo": "teste_de_atributo", "modo": "vantagem", "atributo": "CAR",
      "custo": "acao_bonus", "duracao": "10 minutos", "consome_recurso": "lenda_viva"},
     {"tipo": "transformar_erro_em_acerto", "frequencia": "uma_vez_por_turno",
      "escopo": "jogada_de_ataque_com_arma", "duracao": "10 minutos"},
     {"tipo": "rolar_novamente", "alvo": "salvaguarda", "custo": "reacao",
      "gatilho": "falhar_em_salvaguarda", "usa_o_novo_resultado": True,
      "duracao": "10 minutos"}],
    "juramento_da_gloria")

# ============================================ subclasse: Juramento da Vingança

sub("magias_do_juramento_da_vinganca", "Magias do Juramento da Vingança", 3, 174,
    "Magias sempre preparadas pela tabela Magias do Juramento da Vingança, sem contar para o limite.",
    [{"tipo": "magias_de_patrono",
      "tabela": tabela_magias("Magias do Juramento da Vingança", 174, [
          (3, ["marca_do_predador", "perdicao"]),
          (5, ["paralisar_pessoa", "passo_nebuloso"]),
          (9, ["celeridade", "protecao_contra_energia"]),
          (13, ["banimento", "porta_dimensional"]),
          (17, ["paralisar_monstro", "videncia"])]),
      "modo": "sempre_preparada", "lista_id": "paladino",
      "acesso_concedido_pela_subclasse": True, "nao_conta_para_o_limite": True}],
    "juramento_da_vinganca",
    revisao=rev("ok", "A tabela do livro imprime 'Marca do Caçador' no nível 3. Essa magia não "
                      "existe no cap. 7: a entrada é Marca do Predador (p. 303), nome 2024 da "
                      "Hunter's Mark. Resolvido pelo id real."))

sub("voto_de_inimizade", "Voto de Inimizade", 3, 174,
    "Opção de Canalizar Divindade na ação Atacar: Vantagem em jogadas de ataque contra uma "
    "criatura à vista a até 9 m por 1 minuto. Se ela cair a 0 Pontos de Vida antes do fim, o voto "
    "passa para outra criatura a até 9 m.",
    [{"tipo": "expandir_opcoes_de_escolha", "escolha_id": "canalizar_divindade_paladino_opcao",
      "catalogo": "efeitos_de_canalizar_divindade", "chaves": ["voto_de_inimizade"]}],
    "juramento_da_vinganca")

opcao_cd("voto_de_inimizade", "Voto de Inimizade", 174,
         "Na ação Atacar: Vantagem em jogadas de ataque contra uma criatura à vista a até 9 m por "
         "1 minuto ou até usar de novo. Reduzida a 0 Pontos de Vida antes disso, o voto se "
         "transfere para outra criatura a até 9 m, sem gastar ação.",
         [{"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "vantagem",
           "alcance_m": 9, "duracao": "1 minuto",
           "gatilho": "acao_atacar",
           "encerra_se": [{"gatilho": "usar_a_caracteristica_de_novo"}],
           "transferivel": {"gatilho": "alvo_a_0_pontos_de_vida", "alcance_m": 9,
                            "custo": "livre"}}],
         subclasse="juramento_da_vinganca")

sub("vingador_implacavel", "Vingador Implacável", 7, 174,
    "Ao atingir com um Ataque de Oportunidade, reduz o Deslocamento do alvo a 0 até o fim do turno "
    "e pode mover metade do seu Deslocamento na mesma Reação, sem provocar Ataques de Oportunidade.",
    [{"tipo": "travar_deslocamento", "alvo": "criatura_atingida", "valor": 0,
      "gatilho": "acertar_ataque_de_oportunidade", "duracao": "ate_o_fim_do_turno_atual"},
     {"tipo": "efeito_narrativo", "chave": "movimento_na_reacao",
      "texto": "Move até metade do seu Deslocamento como parte da mesma Reação, sem provocar "
               "Ataques de Oportunidade.",
      "fracao_do_deslocamento": 0.5, "provoca_ataque_de_oportunidade": False}],
    "juramento_da_vinganca")

sub("alma_vingativa", "Alma Vingativa", 15, 174,
    "Logo depois de a criatura sob seu Voto de Inimizade acertar ou errar uma jogada de ataque, "
    "Reação para atacá-la corpo a corpo, se ela estiver ao seu alcance.",
    [{"tipo": "conceder_ataque", "quantidade": ["1"], "tipo_ataque": "corpo_a_corpo",
      "custo": "reacao",
      "gatilho": "criatura_sob:voto_de_inimizade_realiza_jogada_de_ataque",
      "condicao": {"todas": ["alvo_ao_alcance_da_sua_arma"]}}],
    "juramento_da_vinganca")

sub("anjo_vingador", "Anjo Vingador", 20, 174,
    "Ação Bônus, uma vez por Descanso Longo (ou gastando um espaço de 5º círculo): por 10 minutos, "
    "inimigos que comecem o turno na sua Aura de Proteção fazem salvaguarda de Sabedoria ou ficam "
    "Amedrontados por 1 minuto, com Vantagem nos ataques contra eles; e você ganha asas "
    "espectrais com Deslocamento de Voo de 18 m, podendo pairar.",
    [{"tipo": "recurso_com_recarga", "id": "anjo_vingador", "nome": "Anjo Vingador",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso",
      "recuperacao_alternativa": {"consome": "espaco_de_magia", "circulo": 5, "custo": "livre"}},
     {"tipo": "melhorar_caracteristica", "alvo": "aura_de_protecao",
      "custo": "acao_bonus", "duracao": "10 minutos", "consome_recurso": "anjo_vingador",
      "efeitos": [{"tipo": "conceder_condicao", "condicao_id": "amedrontado",
                   "alvo": "inimigo_na_emanacao",
                   "gatilho": "inicio_do_turno_do_inimigo_na_emanacao",
                   "salvaguarda": {"atributo": "SAB", "cd": CD},
                   "duracao": "1 minuto",
                   "encerra_se": [{"gatilho": "alvo_sofre_dano"}]},
                  {"tipo": "vantagem", "alvo": "jogada_de_ataque", "modo": "vantagem",
                   "condicao": {"todas": ["alvo_amedrontado_por:anjo_vingador"]},
                   "beneficiario": "qualquer_atacante"}]},
     {"tipo": "conceder_velocidade", "tipo_deslocamento": "voo", "formula": ["18"],
      "unidade": "metros", "pode_pairar": True, "custo": "acao_bonus",
      "duracao": "10 minutos", "consome_recurso": "anjo_vingador"}],
    "juramento_da_vinganca")

# ============================================ subclasse: Juramento dos Anciões

sub("a_ira_da_natureza", "A Ira da Natureza", 3, 174,
    "Opção de Canalizar Divindade, ação Usar Magia: cada criatura à escolha à vista a até 4,5 m "
    "faz salvaguarda de Força ou fica Contida por 1 minuto, repetindo a salvaguarda no fim de "
    "cada turno dela.",
    [{"tipo": "expandir_opcoes_de_escolha", "escolha_id": "canalizar_divindade_paladino_opcao",
      "catalogo": "efeitos_de_canalizar_divindade", "chaves": ["a_ira_da_natureza"]}],
    "juramento_dos_anciaos")

opcao_cd("a_ira_da_natureza", "A Ira da Natureza", 174,
         "Ação Usar Magia: videiras espectrais. Cada criatura à sua escolha à vista a até 4,5 m "
         "faz salvaguarda de Força ou fica Contida por 1 minuto, repetindo a salvaguarda no fim "
         "de cada turno dela.",
         [{"tipo": "conceder_condicao", "condicao_id": "contido",
           "custo": "acao", "acao_id": "usar_magia", "alcance_m": 4.5,
           "alvo": "criaturas_a_escolha_a_vista",
           "salvaguarda": {"atributo": "FOR", "cd": CD,
                           "repete": "fim_de_cada_turno_do_alvo", "em_sucesso": "encerra"},
           "duracao": "1 minuto"}],
         subclasse="juramento_dos_anciaos")

sub("magias_do_juramento_dos_anciaos", "Magias do Juramento dos Anciões", 3, 175,
    "Magias sempre preparadas pela tabela Magias do Juramento dos Anciões, sem contar para o limite.",
    [{"tipo": "magias_de_patrono",
      "tabela": tabela_magias("Magias do Juramento dos Anciões", 175, [
          (3, ["falar_com_animais", "golpe_constritor"]),
          (5, ["passo_nebuloso", "raio_lunar"]),
          (9, ["crescimento_de_plantas", "protecao_contra_energia"]),
          (13, ["pele_rocha", "tempestade_glacial"]),
          (17, ["comunhao_com_a_natureza", "passo_arboreo"])]),
      "modo": "sempre_preparada", "lista_id": "paladino",
      "acesso_concedido_pela_subclasse": True, "nao_conta_para_o_limite": True}],
    "juramento_dos_anciaos")

sub("aura_de_resistencia", "Aura de Resistência", 7, 175,
    "Você e seus aliados têm Resistência a dano Necrótico, Psíquico e Radiante dentro da Aura de "
    "Proteção.",
    [{"tipo": "melhorar_caracteristica", "alvo": "aura_de_protecao",
      "efeitos": [{"tipo": "alterar_dano", "tipo_dano": t, "operacao": "resistencia",
                   "beneficiarios": "voce_e_aliados_na_emanacao"}
                  for t in ("necrotico", "psiquico", "radiante")]}],
    "juramento_dos_anciaos")

sub("sentinela_imortal", "Sentinela Imortal", 15, 175,
    "Reduzido a 0 Pontos de Vida sem morrer na hora, você fica com 1 Ponto de Vida e recupera "
    "três vezes o seu nível de Paladino. Uma vez por Descanso Longo. Além disso, não envelhece "
    "magicamente e sua aparência não envelhece.",
    [{"tipo": "recurso_com_recarga", "id": "sentinela_imortal", "nome": "Sentinela Imortal",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso"},
     {"tipo": "cura", "formula": {"op": "mult", "args": ["3", "nivel_classe:paladino"]},
      "beneficiario": "voce", "consome_recurso": "sentinela_imortal",
      "gatilho": "reduzido_a_0_pontos_de_vida_sem_morrer",
      "nota": "Você fica com 1 Ponto de Vida e então recupera a quantia curada."},
     {"tipo": "efeito_narrativo", "chave": "nao_envelhece",
      "texto": "Não pode ser envelhecido magicamente, e sua aparência não envelhece."}],
    "juramento_dos_anciaos")

sub("campeao_ancestral", "Campeão Ancestral", 20, 175,
    "Ação Bônus, uma vez por Descanso Longo (ou gastando um espaço de 5º círculo): por 1 minuto, "
    "inimigos na Aura de Proteção têm Desvantagem em salvaguardas contra suas magias e opções de "
    "Canalizar Divindade; magias de tempo de conjuração de uma ação podem ser conjuradas com Ação "
    "Bônus; e você recupera 10 Pontos de Vida no início de cada turno seu.",
    [{"tipo": "recurso_com_recarga", "id": "campeao_ancestral", "nome": "Campeão Ancestral",
      "formula_maximo": ["1"], "recarga": ["descanso_longo"], "consumo": "por_uso",
      "recuperacao_alternativa": {"consome": "espaco_de_magia", "circulo": 5, "custo": "livre"}},
     {"tipo": "melhorar_caracteristica", "alvo": "aura_de_protecao",
      "custo": "acao_bonus", "duracao": "1 minuto", "consome_recurso": "campeao_ancestral",
      "efeitos": [{"tipo": "vantagem", "alvo": "salvaguarda", "modo": "desvantagem",
                   "beneficiario": "inimigo_na_emanacao",
                   "escopo": "contra suas magias e opções de Canalizar Divindade"}]},
     {"tipo": "alterar_custo_de_acao", "acao_id": "usar_magia",
      "custo_original": "acao", "novo_custo": "acao_bonus",
      "escopo": "magia_com_tempo_de_conjuracao_de_uma_acao",
      "duracao": "1 minuto", "consome_recurso": "campeao_ancestral"},
     {"tipo": "cura", "formula": ["10"], "beneficiario": "voce",
      "gatilho": "inicio_do_seu_turno", "duracao": "1 minuto",
      "consome_recurso": "campeao_ancestral"}],
    "juramento_dos_anciaos")


# ==================================================================== a classe

SUBCLASSES = [
    ("juramento_da_devocao", "Juramento da Devoção", 171,
     "Justiça e ordem: arma imbuída de energia positiva, aura contra Enfeitiçado e destruição "
     "que também protege."),
    ("juramento_da_gloria", "Juramento da Glória", 172,
     "Heroísmo e feito: atletismo sobrenatural, PV temporários distribuídos e aura que acelera "
     "os aliados."),
    ("juramento_da_vinganca", "Juramento da Vingança", 174,
     "Punição: voto que dá Vantagem contra um alvo, perseguição implacável e asas espectrais no "
     "nível 20."),
    ("juramento_dos_anciaos", "Juramento dos Anciões", 174,
     "Vida e luz: videiras espectrais, aura de Resistência a dano Necrótico, Psíquico e Radiante, "
     "e imortalidade prática."),
]

COMBATENTE_ABENCOADO = collections.OrderedDict([
    ("id", "combatente_abencoado"), ("nome", "Combatente Abençoado"),
    ("classe", "paladino"), ("fonte", fonte(168)),
    ("descricao_curta", "Em vez de um talento de Estilo de Luta: dois truques de Clérigo à "
                        "escolha, contados como magias de Paladino, com Carisma. Troca um deles "
                        "a cada nível de Paladino."),
    ("efeitos", [{"id": "combatente_abencoado_truques", "tipo": "escolha",
                  "rotulo": "Escolha 2 truques de Clérigo", "quantidade": 2,
                  "reescolhivel": True, "reescolha_em": "cada_nivel_de_paladino",
                  "reescolha_quantidade": 1,
                  "de": {"catalogo": "magias", "filtro": {"nivel": 0, "lista": "clerigo"}},
                  "efeito_por_item_escolhido": {
                      "tipo": "desbloquear_magias", "lista_id": "paladino",
                      "modo": "conhecida", "magia": "{{escolhido}}",
                      "atributo_conjuracao": "CAR"}}]),
    ("recomendadas", ["chama_sagrada", "orientacao"]),
])

# tabela Características do Paladino, p. 168
PROGRESSAO = [
    (1, 2, ["conjuracao_paladino", "maestria_em_arma_paladino", "maos_consagradas"], 0, 2, [2, 0, 0, 0, 0]),
    (2, 2, ["destruicao_do_paladino", "estilo_de_luta_paladino"], 0, 3, [2, 0, 0, 0, 0]),
    (3, 2, ["canalizar_divindade_paladino", "caracteristica_de_subclasse"], 2, 4, [3, 0, 0, 0, 0]),
    (4, 2, ["aumento_no_valor_de_atributo"], 2, 5, [3, 0, 0, 0, 0]),
    (5, 3, ["ataque_extra", "montaria_fiel"], 2, 6, [4, 2, 0, 0, 0]),
    (6, 3, ["aura_de_protecao"], 2, 6, [4, 2, 0, 0, 0]),
    (7, 3, ["caracteristica_de_subclasse"], 2, 7, [4, 3, 0, 0, 0]),
    (8, 3, ["aumento_no_valor_de_atributo"], 2, 7, [4, 3, 0, 0, 0]),
    (9, 4, ["repudiar_inimigos"], 2, 9, [4, 3, 2, 0, 0]),
    (10, 4, ["aura_de_coragem"], 2, 9, [4, 3, 2, 0, 0]),
    (11, 4, ["golpes_radiantes"], 3, 10, [4, 3, 3, 0, 0]),
    (12, 4, ["aumento_no_valor_de_atributo"], 3, 10, [4, 3, 3, 0, 0]),
    (13, 5, [], 3, 11, [4, 3, 3, 1, 0]),
    (14, 5, ["toque_restaurador"], 3, 11, [4, 3, 3, 1, 0]),
    (15, 5, ["caracteristica_de_subclasse"], 3, 12, [4, 3, 3, 2, 0]),
    (16, 5, ["aumento_no_valor_de_atributo"], 3, 12, [4, 3, 3, 2, 0]),
    (17, 6, [], 3, 14, [4, 3, 3, 3, 1]),
    (18, 6, ["aura_expandida"], 3, 14, [4, 3, 3, 3, 1]),
    (19, 6, ["dadiva_epica"], 3, 15, [4, 3, 3, 3, 2]),
    (20, 6, ["caracteristica_de_subclasse"], 3, 15, [4, 3, 3, 3, 2]),
]

COLUNAS = collections.OrderedDict([
    ("canalizar_divindade", {"nome": "Canalizar Divindade", "tipo": "inteiro"}),
    ("magias_preparadas", {"nome": "Magias Preparadas", "tipo": "inteiro"}),
])
for n in range(1, 6):
    COLUNAS[f"espacos_{n}"] = {"nome": f"Espaços de {n}º Círculo", "tipo": "inteiro"}

CLASSE = collections.OrderedDict([
    ("id", "paladino"), ("nome", "Paladino"), ("fonte", fonte(167)), ("revisao", rev()),
    ("descricao_curta",
     "Meio-conjurador de armadura pesada, movido por juramento: Carisma na magia e nas auras, "
     "reserva de cura no toque, Destruição Divina de graça e Canalizar Divindade próprio."),
    ("dado_de_vida", 10),
    ("atributo_primario", ["FOR", "CAR"]),
    ("salvaguardas_primarias", ["SAB", "CAR"]),
    ("nivel_subclasse", 3),
    ("niveis_de_caracteristica_de_subclasse", [3, 7, 15, 20]),
    ("conjuracao", {"atributo": "CAR", "modo": "lista_de_classe", "lista_id": "paladino",
                    "preparadas_por_nivel": True, "meio_conjurador": True,
                    "circulo_maximo": 5, "truques": False}),
    ("subclasses", [s[0] for s in SUBCLASSES]),
    ("proficiencias_iniciais", [
        {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "SAB",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "salvaguarda", "chave": "CAR",
         "nivel_dominio": "proficiente"},
        {"tipo": "conceder_proficiencia", "categoria": "arma", "nivel_dominio": "proficiente",
         "de": {"catalogo": "itens", "filtro": {"categoria": "arma", "grupo": "simples"}}},
        {"tipo": "conceder_proficiencia", "categoria": "arma", "nivel_dominio": "proficiente",
         "de": {"catalogo": "itens", "filtro": {"categoria": "arma", "grupo": "marcial"}}},
        {"id": "paladino_pericias_iniciais", "tipo": "escolha", "rotulo": "Escolha 2 perícias",
         "quantidade": 2, "momento": "criacao",
         "de": {"catalogo": "pericias",
                "chaves": ["atletismo", "intimidacao", "intuicao", "medicina", "persuasao",
                           "religiao"]},
         "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "pericia",
                                       "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}},
    ]),
    ("treinamento_com_armadura", ["leve", "media", "pesada", "escudo"]),
    ("equipamento_inicial", {
        "opcoes": [
            {"id": "A",
             "itens": [{"item": "cota_de_malha"}, {"item": "escudo"}, {"item": "espada_longa"},
                       {"item": "azagaia", "quantidade": 6},
                       {"id": "paladino_simbolo_sagrado", "tipo": "escolha",
                        "rotulo": "Escolha a forma do seu Símbolo Sagrado", "quantidade": 1,
                        "de": {"catalogo": "itens",
                               "chaves": ["amuleto", "emblema", "relicario"]},
                        "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                                      "categoria": "item",
                                                      "chave": "{{escolhido}}"},
                        "nota": "No capítulo 6 (p. 225) 'Símbolo Sagrado' é uma categoria com "
                                "três formas, não um item — mesma resolução do Clérigo."},
                       {"item": "kit_de_sacerdote"}],
             "moedas": {"po": 9}},
            {"id": "B", "itens": [], "moedas": {"po": 150}},
        ],
        "revisao": rev()}),
    ("colunas_da_tabela", COLUNAS),
    ("multiclasse", {
        "adquire": ["dado_de_vida", "proficiencia:arma:categoria:marcial",
                    "treinamento_armadura:leve", "treinamento_armadura:media",
                    "treinamento_armadura:escudo"],
        "fonte": fonte(167),
        "nota": "Registrado para a fase de multiclasse; não aplicado agora."}),
    ("progressao", [
        collections.OrderedDict([
            ("nivel", n), ("bonus_de_proficiencia", bp), ("caracteristicas", cs),
            ("colunas", collections.OrderedDict(
                [("canalizar_divindade", cd), ("magias_preparadas", mp)]
                + [(f"espacos_{i+1}", v) for i, v in enumerate(sl)]))])
        for n, bp, cs, cd, mp, sl in PROGRESSAO]),
])

TIPOS_NOVOS = [
    ("reserva_de_cura", "Reserva de cura",
     "Pote de Pontos de Vida gasto livremente em cura ou, a um custo fixo por vez, em remover "
     "condições. Diferente de recurso com usos e de reserva de dados. Mãos Consagradas do Paladino."),
]

ALVOS_NOVOS = [
    ("tamanho_da_emanacao", "Tamanho da emanação",
     "O raio, em metros, de uma emanação já concedida. Aura Expandida troca 3 m por 9 m sem "
     "recriar a Aura de Proteção."),
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
    n_tipos = juntar(f'{CAT}/tipos_de_efeito.json', TIPOS_NOVOS,
                     ['id', 'nome', 'descricao_curta'])
    n_alvos = juntar(f'{CAT}/alvos.json', ALVOS_NOVOS, ['id', 'nome', 'descricao_curta'])

    # Combatente Abençoado entra no catálogo compartilhado criado pelo Guardião
    cf = f'{CAT}/opcoes_de_estilo_de_luta_de_classe.json'
    d = json.load(open(cf, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    d['itens'] = [i for i in d['itens'] if i['id'] != 'combatente_abencoado']
    d['itens'].append(COMBATENTE_ABENCOADO)
    d['total'] = len(d['itens'])
    d['parcial'] = False
    d['nota'] = ("Opções que o livro oferece NO LUGAR de um talento de Estilo de Luta. "
                 "As duas do livro estão aqui: Combatente Druídico (Guardião) e "
                 "Combatente Abençoado (Paladino).")
    json.dump(d, open(cf, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    # opções de Canalizar Divindade do Paladino no catálogo compartilhado
    cd_f = f'{CAT}/efeitos_de_canalizar_divindade.json'
    d = json.load(open(cd_f, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    d['itens'] = [i for i in d['itens'] if i.get('classe') != 'paladino']
    for i in d['itens']:
        i.setdefault('classe', 'clerigo')
    d['itens'] += OPCOES_CD
    d['total'] = len(d['itens'])
    d['nota'] = ("Efeitos básicos e de subclasse das duas classes que têm Canalizar Divindade. "
                 "O campo 'classe' separa: os recursos são independentes, só o nome é comum.")
    json.dump(d, open(cd_f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    cl = json.load(open('dados/classes.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    cl['itens'] = [c for c in cl['itens'] if c['id'] != 'paladino'] + [CLASSE]
    cl['total'] = len(cl['itens'])
    json.dump(cl, open('dados/classes.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    sc = json.load(open('dados/subclasses.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    sc['itens'] = [s for s in sc['itens'] if s.get('classe') != 'paladino']
    for sid, nome, pag, desc in SUBCLASSES:
        sc['itens'].append(collections.OrderedDict([
            ("id", sid), ("nome", nome), ("classe", "paladino"),
            ("fonte", fonte(pag)), ("revisao", rev()), ("descricao_curta", desc),
            ("niveis_de_caracteristica", [3, 7, 15, 20]),
            ("caracteristicas", [c['id'] for c in CARACS if c.get('subclasse') == sid])]))
    sc['total'] = len(sc['itens'])
    json.dump(sc, open('dados/subclasses.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    ca = json.load(open('dados/caracteristicas.json', encoding='utf-8'),
                   object_pairs_hook=collections.OrderedDict)
    ca['itens'] = [c for c in ca['itens'] if c.get('classe') != 'paladino'] + CARACS
    for c in ca['itens']:
        if c['id'] == 'ataque_extra':
            if not any(x.get('classe') == 'paladino' for x in c.get('concedida_por', [])):
                c.setdefault('concedida_por', []).append(
                    {"classe": "paladino", "nivel": 5, "pagina_livro": 169})
    ca['total'] = len(ca['itens'])
    json.dump(ca, open('dados/caracteristicas.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    print(f"paladino: {len(CARACS)} características | {len(SUBCLASSES)} subclasses")
    print(f"opções de Canalizar Divindade do Paladino: {len(OPCOES_CD)}")
    print(f"tipos de efeito novos: {n_tipos} | alvos novos: {n_alvos}")
    print(f"classes: {cl['total']} | subclasses: {sc['total']} | características: {ca['total']}")


if __name__ == '__main__':
    main()
