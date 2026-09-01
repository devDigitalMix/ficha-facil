# -*- coding: utf-8 -*-
"""Catálogo `valores_derivados`: as contas da ficha, como dado.

Até agora o dataset dizia quais BÔNUS existem (uma característica dá +2 aqui, um
item dá vantagem ali), mas nunca dizia a CONTA de base — o que é uma jogada de
ataque, de onde sai a CA, qual atributo cada tipo de ataque usa. Isso obrigaria o
backend a chumbar as regras em código, que é justamente o que o projeto evita.

Cada derivado traz:
  `formula`  — em árvore, no mesmo formato usado no resto do dataset;
  `parcelas` — cada termo com rótulo e condição, para o backend devolver o log de
               proveniência pronto ("+3 Destreza, +3 proficiência") sem remontar
               a explicação a partir do resultado;
  `fonte`    — capítulo e página.

Fontes: cap. 1 (Testes de D20 p. 21-22, Jogadas de Ataque p. 27, Jogadas de Dano
p. 29), cap. 7 (p. 236-237), Ap. C (Classe de Armadura, Capacidade de Carga).
"""
import json, collections

SAIDA = 'dados/catalogos/valores_derivados.json'


def fonte(cap, pag):
    return {"capitulo": cap, "pagina_livro": pag, "pagina_pdf": pag + 4}


DERIVADOS = [
    # ------------------------------------------------------------ atributos
    {
        "id": "modificador_de_atributo",
        "nome": "Modificador de Atributo",
        "descricao_curta": "Derivado do valor do atributo: (valor − 10) dividido por 2, "
                           "arredondado para baixo.",
        "formula": [{"op": "div_arred_baixo",
                     "args": [{"op": "soma", "args": ["valor_do_atributo", "-10"]}, "2"]}],
        "entradas": ["valor_do_atributo"],
        "fonte": fonte(1, 20),
    },
    {
        "id": "bonus_de_proficiencia",
        "nome": "Bônus de Proficiência",
        "descricao_curta": "Vem do nível do personagem; está na coluna Bônus de "
                           "Proficiência da tabela de cada classe.",
        "formula": ["coluna:bonus_de_proficiencia"],
        "entradas": ["nivel_do_personagem"],
        "tabela_por_nivel": {"1": 2, "2": 2, "3": 2, "4": 2, "5": 3, "6": 3, "7": 3,
                             "8": 3, "9": 4, "10": 4, "11": 4, "12": 4, "13": 5,
                             "14": 5, "15": 5, "16": 5, "17": 6, "18": 6, "19": 6,
                             "20": 6},
        "fonte": fonte(1, 22),
    },

    # ------------------------------------------------------- testes de d20
    {
        "id": "teste_de_atributo",
        "nome": "Teste de Atributo",
        "descricao_curta": "1d20 + modificador do atributo + bônus de proficiência se "
                           "for proficiente na perícia ou ferramenta usada.",
        "formula": ["1d20", "mod:atributo_relevante",
                    {"op": "soma_se", "condicao": "proficiente_na_pericia_ou_ferramenta",
                     "args": ["prof"]}],
        "parcelas": [
            {"rotulo": "d20", "chave": "dado", "sempre": True},
            {"rotulo": "modificador de atributo", "chave": "mod:atributo_relevante",
             "sempre": True},
            {"rotulo": "bônus de proficiência", "chave": "prof",
             "condicao": "proficiente_na_pericia_ou_ferramenta"},
            {"rotulo": "outros bônus e penalidades", "chave": "modificadores_ativos",
             "sempre": True},
        ],
        "fonte": fonte(1, 21),
    },
    {
        "id": "salvaguarda",
        "nome": "Salvaguarda",
        "descricao_curta": "1d20 + modificador do atributo da salvaguarda + bônus de "
                           "proficiência se a classe der proficiência nessa salvaguarda.",
        "formula": ["1d20", "mod:atributo_da_salvaguarda",
                    {"op": "soma_se", "condicao": "proficiente_na_salvaguarda",
                     "args": ["prof"]}],
        "parcelas": [
            {"rotulo": "d20", "chave": "dado", "sempre": True},
            {"rotulo": "modificador de atributo", "chave": "mod:atributo_da_salvaguarda",
             "sempre": True},
            {"rotulo": "bônus de proficiência", "chave": "prof",
             "condicao": "proficiente_na_salvaguarda"},
            {"rotulo": "outros bônus e penalidades", "chave": "modificadores_ativos",
             "sempre": True},
        ],
        "fonte": fonte(1, 22),
    },
    {
        "id": "jogada_de_ataque_com_arma",
        "nome": "Jogada de Ataque com Arma",
        "descricao_curta": "1d20 + modificador do atributo de ataque da arma + bônus de "
                           "proficiência se você for proficiente com ela.",
        "formula": ["1d20", "mod:atributo_de_ataque_da_arma",
                    {"op": "soma_se", "condicao": "proficiente_com_a_arma", "args": ["prof"]}],
        "parcelas": [
            {"rotulo": "d20", "chave": "dado", "sempre": True},
            {"rotulo": "modificador de atributo", "chave": "mod:atributo_de_ataque_da_arma",
             "sempre": True},
            {"rotulo": "bônus de proficiência", "chave": "prof",
             "condicao": "proficiente_com_a_arma"},
            {"rotulo": "bônus mágico da arma", "chave": "bonus_magico_da_arma",
             "condicao": "arma_magica"},
            {"rotulo": "outros bônus e penalidades", "chave": "modificadores_ativos",
             "sempre": True},
        ],
        "regra_do_atributo": "atributo_de_ataque_da_arma",
        "nota": "Arma improvisada NÃO soma o bônus de proficiência (Ap. C, 'Armas "
                "Improvisadas').",
        "fonte": fonte(1, 27),
    },
    {
        "id": "jogada_de_ataque_magico",
        "nome": "Jogada de Ataque Mágico",
        "descricao_curta": "1d20 + modificador do atributo de conjuração + bônus de "
                           "proficiência.",
        "formula": ["1d20", "mod:atributo_de_conjuracao", "prof"],
        "parcelas": [
            {"rotulo": "d20", "chave": "dado", "sempre": True},
            {"rotulo": "modificador de conjuração", "chave": "mod:atributo_de_conjuracao",
             "sempre": True},
            {"rotulo": "bônus de proficiência", "chave": "prof", "sempre": True},
        ],
        "fonte": fonte(7, 237),
    },
    {
        "id": "jogada_de_ataque_desarmado",
        "nome": "Jogada de Ataque Desarmado",
        "descricao_curta": "1d20 + modificador de Força + bônus de proficiência.",
        "formula": ["1d20", "mod:FOR", "prof"],
        "parcelas": [
            {"rotulo": "d20", "chave": "dado", "sempre": True},
            {"rotulo": "modificador de Força", "chave": "mod:FOR", "sempre": True},
            {"rotulo": "bônus de proficiência", "chave": "prof", "sempre": True},
        ],
        "fonte": fonte("ap_c", 361),
    },

    # ------------------------------------------------------------- dano
    {
        "id": "dano_de_arma",
        "nome": "Dano de Arma",
        "descricao_curta": "Dado de dano da arma + o MESMO modificador de atributo usado "
                           "na jogada de ataque.",
        "formula": ["dado_de_dano_da_arma", "mod:atributo_de_ataque_da_arma"],
        "parcelas": [
            {"rotulo": "dado da arma", "chave": "dado_de_dano_da_arma", "sempre": True},
            {"rotulo": "modificador de atributo", "chave": "mod:atributo_de_ataque_da_arma",
             "sempre": True},
            {"rotulo": "bônus mágico da arma", "chave": "bonus_magico_da_arma",
             "condicao": "arma_magica"},
        ],
        "nota": "Dano de valor fixo sem dado (a Zarabatana causa 1) NÃO soma o "
                "modificador de atributo (cap. 1, p. 29).",
        "fonte": fonte(1, 29),
    },
    {
        "id": "dano_desarmado",
        "nome": "Dano de Ataque Desarmado",
        "descricao_curta": "1 + modificador de Força, dano Contundente.",
        "formula": [{"op": "soma", "args": ["1", "mod:FOR"]}],
        "tipo_dano": "contundente",
        "fonte": fonte("ap_c", 361),
    },

    # ---------------------------------------------------------- defesas
    {
        "id": "classe_de_armadura",
        "nome": "Classe de Armadura",
        "descricao_curta": "Sem armadura, 10 + Destreza. Com armadura, a CA base da "
                           "armadura, somando Destreza até o teto dela. Escudo soma o "
                           "bônus dele. Só um cálculo de base por vez.",
        "formula": [{"op": "max_entre_calculos_de_base", "args": ["calculos_de_base_ativos"]},
                    {"op": "soma_se", "condicao": "usando_escudo", "args": ["bonus_do_escudo"]}],
        "calculo_padrao": {"id": "sem_armadura", "base": 10,
                           "soma_modificador": "DES", "teto_do_modificador": None},
        "parcelas": [
            {"rotulo": "base", "chave": "ca_base", "sempre": True},
            {"rotulo": "Destreza", "chave": "mod:DES", "condicao": "calculo_soma_destreza"},
            {"rotulo": "escudo", "chave": "bonus_do_escudo", "condicao": "usando_escudo"},
            {"rotulo": "outros bônus", "chave": "modificadores_ativos", "sempre": True},
        ],
        "nota": "Se mais de um cálculo de base estiver disponível (armadura, Defesa sem "
                "Armadura do Monge ou do Bárbaro), o jogador escolhe um — não se somam.",
        "fonte": fonte("ap_c", 363),
    },
    {
        "id": "cd_para_evitar_sua_magia",
        "nome": "CD para Evitar sua Magia",
        "descricao_curta": "8 + modificador do atributo de conjuração + bônus de "
                           "proficiência.",
        "formula": ["8", "mod:atributo_de_conjuracao", "prof"],
        "parcelas": [
            {"rotulo": "base", "chave": "8", "sempre": True},
            {"rotulo": "modificador de conjuração", "chave": "mod:atributo_de_conjuracao",
             "sempre": True},
            {"rotulo": "bônus de proficiência", "chave": "prof", "sempre": True},
        ],
        "fonte": fonte(7, 237),
    },
    {
        "id": "iniciativa",
        "nome": "Iniciativa",
        "descricao_curta": "1d20 + modificador de Destreza.",
        "formula": ["1d20", "mod:DES"],
        "parcelas": [
            {"rotulo": "d20", "chave": "dado", "sempre": True},
            {"rotulo": "Destreza", "chave": "mod:DES", "sempre": True},
            {"rotulo": "outros bônus", "chave": "modificadores_ativos", "sempre": True},
        ],
        "fonte": fonte(1, 24),
    },
    {
        "id": "percepcao_passiva",
        "nome": "Percepção Passiva",
        "descricao_curta": "10 + modificador de Sabedoria + bônus de proficiência se for "
                           "proficiente em Percepção.",
        "formula": ["10", "mod:SAB",
                    {"op": "soma_se", "condicao": "proficiente_em:percepcao", "args": ["prof"]}],
        "fonte": fonte(1, 22),
    },

    # ------------------------------------------------------------ corpo
    {
        "id": "pontos_de_vida_no_nivel_1",
        "nome": "Pontos de Vida no Nível 1",
        "descricao_curta": "Valor máximo do Dado de Vida da classe + modificador de "
                           "Constituição.",
        "formula": [{"op": "soma", "args": ["dado_de_vida_da_classe", "mod:CON"]}],
        "fonte": fonte(2, 39),
    },
    {
        "id": "pontos_de_vida_por_nivel",
        "nome": "Pontos de Vida ao Subir de Nível",
        "descricao_curta": "Rola o Dado de Vida (ou usa a média fixa da classe) e soma o "
                           "modificador de Constituição, no mínimo 1 por nível.",
        "formula": [{"op": "max", "args": [
            {"op": "soma", "args": ["rolagem_ou_media_do_dado_de_vida", "mod:CON"]}, "1"]}],
        "fonte": fonte(2, 39),
    },
    {
        "id": "capacidade_de_carga",
        "nome": "Capacidade de Carga",
        "descricao_curta": "Força × um fator que depende do tamanho da criatura, em "
                           "quilogramas.",
        "formula": [{"op": "mult", "args": ["valor_de_forca", "fator_por_tamanho"]}],
        "tabela_por_tamanho": {
            "minusculo": {"carregar_kg_por_forca": 3.5, "arrastar_kg_por_forca": 7},
            "pequeno":   {"carregar_kg_por_forca": 7,   "arrastar_kg_por_forca": 13.5},
            "medio":     {"carregar_kg_por_forca": 7,   "arrastar_kg_por_forca": 13.5},
            "grande":    {"carregar_kg_por_forca": 13.5, "arrastar_kg_por_forca": 27},
            "enorme":    {"carregar_kg_por_forca": 27,  "arrastar_kg_por_forca": 54.5},
            "colossal":  {"carregar_kg_por_forca": 54.5, "arrastar_kg_por_forca": 109},
        },
        "fonte": fonte("ap_c", 362),
    },
]

# Qual atributo cada tipo de ataque usa (cap. 1, tabela Atributos de Jogada de Ataque).
# É a regra que faltava para o backend saber que o Arco Curto usa Destreza.
REGRA_DO_ATRIBUTO = {
    "id": "atributo_de_ataque_da_arma",
    "nome": "Atributo de Jogada de Ataque",
    "descricao_curta": "Corpo a corpo com arma ou Ataque Desarmado usa Força; ataque à "
                       "distância com arma usa Destreza; ataque mágico usa o atributo de "
                       "conjuração. A propriedade Acuidade deixa escolher entre Força e "
                       "Destreza, e o mesmo atributo vale para o ataque e para o dano.",
    "por_alcance_da_arma": {"corpo_a_corpo": "FOR", "a_distancia": "DES"},
    "excecoes": [
        {"quando": "arma_tem_propriedade:acuidade",
         "efeito": "escolha_entre", "opcoes": ["FOR", "DES"],
         "nota": "O mesmo atributo vale para a jogada de ataque e para o dano."},
        {"quando": "arma_tem_propriedade:arremesso", "efeito": "mantem_o_atributo_da_arma",
         "nota": "Arma corpo a corpo arremessada continua usando Força, salvo Acuidade."},
        {"quando": "ataque_magico", "efeito": "usa", "atributo": "atributo_de_conjuracao"},
        {"quando": "arma_improvisada", "efeito": "sem_bonus_de_proficiencia"},
    ],
    "fonte": fonte(1, 27),
}


def main():
    itens = list(DERIVADOS) + [REGRA_DO_ATRIBUTO]
    cat = collections.OrderedDict([
        ("catalogo", "valores_derivados"),
        ("nome", "Valores Derivados da Ficha"),
        ("fonte", {"capitulo": 1, "pagina_livro": 20, "pagina_pdf": 24}),
        ("nota", "As contas de base da ficha, para o backend calcular a partir do dado em "
                 "vez de chumbar regra em código. Cada derivado traz a fórmula em árvore e "
                 "as parcelas rotuladas, para o log de proveniência sair pronto."),
        ("total", len(itens)),
        ("itens", itens),
    ])
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(cat, f, ensure_ascii=False, indent=2)
    print(f"valores_derivados: {len(itens)} itens")
    for i in itens:
        print('  ', i['id'])


if __name__ == '__main__':
    main()
