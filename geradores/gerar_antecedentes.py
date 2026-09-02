# -*- coding: utf-8 -*-
"""Antecedentes (cap. 4, p. 177-185). Os 16 do livro.

Antecedente de 2024 é uma máquina regular: três atributos, um talento de Origem,
duas perícias, uma ferramenta e um pacote de equipamento contra 50 PO. Por ser
regular, ele é escrito como TABELA e montado por função — nada de 16 blocos
copiados à mão, que é onde erro de digitação se esconde.

O aumento de atributo é a parte que o app precisa acertar: o livro dá três
atributos e duas formas de distribuir — +2 num e +1 noutro, ou +1 nos três — com
teto de 20. Isso vira uma `escolha` entre dois modos, e os modos já existem em
`modos_de_aumento_de_atributo`, criado no capítulo 5.

Três antecedentes fixam a lista do Iniciado em Magia (Acólito → Clérigo, Guia →
Druida, Sábio → Mago). O talento é o mesmo, repetível, com uma escolha de lista
dentro; o antecedente não duplica o talento, ele **pré-resolve a escolha**.
"""
import json, collections

CAT = 'dados/catalogos'


def fonte(p):
    return {"capitulo": 4, "pagina_livro": p, "pagina_pdf": p + 4}


def rev(status="ok", notas=""):
    return {"status": status, "notas": notas}


def talento(tid, **extra):
    e = {"tipo": "conceder_talento", "talento_id": tid}
    e.update(extra)
    return e


def iniciado(lista):
    """Iniciado em Magia com a lista já escolhida pelo antecedente."""
    return talento("iniciado_em_magia",
                   escolhas_predefinidas={"iniciado_em_magia_lista": lista},
                   nota="O antecedente fixa a lista; o atributo de conjuração e os truques "
                        "continuam sendo escolha do jogador.")


def pericia(chave):
    return {"tipo": "conceder_proficiencia", "categoria": "pericia", "chave": chave,
            "nivel_dominio": "proficiente"}


def ferramenta(chave):
    return {"tipo": "conceder_proficiencia", "categoria": "ferramenta", "chave": chave,
            "nivel_dominio": "proficiente"}


def escolher_ferramenta(aid, rotulo, filtro):
    return {"id": f"{aid}_ferramenta", "tipo": "escolha", "rotulo": rotulo, "quantidade": 1,
            "momento": "criacao",
            "de": {"catalogo": "ferramentas", "filtro": filtro},
            "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia",
                                          "categoria": "ferramenta", "chave": "{{escolhido}}",
                                          "nivel_dominio": "proficiente"},
            "define_variavel": "ferramenta_do_antecedente"}


def aumento(aid, atributos):
    """Os dois modos do livro: +2/+1 ou +1/+1/+1, teto 20."""
    return {"id": f"{aid}_aumento", "tipo": "escolha",
            "rotulo": "Escolha como distribuir o aumento de atributo", "quantidade": 1,
            "momento": "criacao",
            "de": {"catalogo": "modos_de_aumento_de_atributo", "todo_o_catalogo": True},
            "atributos_disponiveis": atributos,
            "efeito_por_item_escolhido": {"tipo": "aumento_atributo",
                                          "modo": "{{escolhido}}",
                                          "atributos": atributos,
                                          "limite": 20}}


def item(iid, quantidade=None, nota=None):
    d = {"item": iid}
    if quantidade:
        d["quantidade"] = quantidade
    if nota:
        d["nota"] = nota
    return d


def mesma_ferramenta(nota):
    """O pacote repete a ferramenta que o antecedente já escolheu."""
    return {"referencia": "ferramenta_do_antecedente", "nota": nota}


SIMBOLO_SAGRADO = {
    "id": "acolito_simbolo_sagrado", "tipo": "escolha",
    "rotulo": "Escolha a forma do seu Símbolo Sagrado", "quantidade": 1,
    "de": {"catalogo": "itens", "chaves": ["amuleto", "emblema", "relicario"]},
    "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "item",
                                  "chave": "{{escolhido}}"},
    "nota": "No capítulo 6 (p. 225) 'Símbolo Sagrado' é uma categoria com três formas, não um "
            "item — mesma resolução do Clérigo e do Paladino."}

ARTESAO = {"grupo": "artesao"}

# id, nome, página, atributos, talento, perícias, ferramenta, pacote, PO, descrição
ANTECEDENTES = [
    ("acolito", "Acólito", 178, ["INT", "SAB", "CAR"], iniciado("clerigo"),
     ["intuicao", "religiao"], ferramenta("suprimentos_de_caligrafo"),
     [item("suprimentos_de_caligrafo"), item("livro", nota="Livro de orações."),
      SIMBOLO_SAGRADO, item("pergaminho", 10), item("tunica")], 8,
     "Serviu num templo, aprendendo religião sob a orientação de um sacerdote e canalizando "
     "um pouco do poder divino para o local de culto."),
    ("andarilho", "Andarilho", 178, ["DES", "SAB", "CAR"], talento("sortudo"),
     ["furtividade", "intuicao"], ferramenta("ferramentas_de_ladrao"),
     [item("adaga", 2), item("ferramentas_de_ladrao"),
      item("kit_de_jogos", nota="Qualquer um."), item("algibeira", 2),
      item("roupas_viagem"), item("saco_de_dormir")], 16,
     "Cresceu nas ruas, dormindo onde dava e fazendo bicos por comida — às vezes furtando, "
     "nunca perdendo o orgulho."),
    ("artesao", "Artesão", 179, ["FOR", "DES", "INT"], talento("artifista"),
     ["investigacao", "persuasao"],
     escolher_ferramenta("artesao", "Escolha um tipo de Ferramentas de Artesão", ARTESAO),
     [mesma_ferramenta("As mesmas Ferramentas de Artesão escolhidas acima."),
      item("algibeira", 2), item("roupas_viagem")], 32,
     "Foi aprendiz numa oficina desde criança: aprendeu a fabricar, a lidar com cliente "
     "exigente e a reparar em detalhe."),
    ("artista", "Artista", 179, ["FOR", "DES", "CAR"], talento("musico"),
     ["acrobacia", "atuacao"],
     escolher_ferramenta("artista", "Escolha um tipo de Instrumento Musical",
                         {"id": "instrumento_musical"}),
     [mesma_ferramenta("O mesmo Instrumento Musical escolhido acima."), item("espelho"),
      item("roupas_fantasia", 2), item("perfume"), item("roupas_viagem")], 11,
     "Passou a juventude em feiras e festivais, trocando bicos por aulas de corda bamba, "
     "alaúde e dicção."),
    ("charlatao", "Charlatão", 180, ["DES", "CON", "CAR"], talento("habilidoso"),
     ["enganacao", "prestidigitacao"], ferramenta("kit_de_falsificacao"),
     [item("kit_de_falsificacao"), item("roupas_fantasia"), item("roupas_finas")], 15,
     "Fez o circuito de tavernas aprendendo a vender mentira reconfortante — poção falsa, "
     "árvore genealógica forjada."),
    ("criminoso", "Criminoso", 180, ["DES", "CON", "INT"], talento("alerta"),
     ["furtividade", "prestidigitacao"], ferramenta("ferramentas_de_ladrao"),
     [item("adaga", 2), item("ferramentas_de_ladrao"), item("algibeira", 2),
      item("pe_de_cabra"), item("roupas_viagem")], 16,
     "Sobreviveu em becos, furtando e assaltando — em gangue pequena ou como lobo solitário "
     "contra a guilda dos ladrões."),
    ("eremita", "Eremita", 181, ["CON", "SAB", "CAR"], talento("curandeiro"),
     ["medicina", "religiao"], ferramenta("kit_de_herbalismo"),
     [item("cajado"), item("kit_de_herbalismo"), item("lampada"),
      item("livro", nota="Livro de filosofia."), item("oleo", 3), item("roupas_viagem"),
      item("saco_de_dormir")], 16,
     "Passou os primeiros anos isolado numa cabana ou mosteiro, com as criaturas da floresta "
     "por companhia e horas de sobra para ponderar."),
    ("escriba", "Escriba", 181, ["DES", "INT", "SAB"], talento("habilidoso"),
     ["investigacao", "percepcao"], ferramenta("suprimentos_de_caligrafo"),
     [item("suprimentos_de_caligrafo"), item("lampada"), item("oleo", 3),
      item("pergaminho", 12), item("roupas_finas")], 23,
     "Formou-se num scriptorium copiando tomos e documentos, com mão firme e atenção "
     "cuidadosa ao detalhe."),
    ("fazendeiro", "Fazendeiro", 182, ["FOR", "CON", "SAB"], talento("vigoroso"),
     ["lidar_com_animais", "natureza"], ferramenta("ferramentas_de_carpinteiro"),
     [item("foice"), item("ferramentas_de_carpinteiro"), item("kit_de_curandeiro"),
      item("balde", nota="Balde de ferro."), item("pa")], 30,
     "Cresceu perto da terra: anos de lavoura e criação renderam paciência, boa saúde e "
     "respeito pela ira da natureza."),
    ("guarda", "Guarda", 182, ["FOR", "INT", "SAB"], talento("alerta"),
     ["atletismo", "percepcao"],
     escolher_ferramenta("guarda", "Escolha um tipo de Kit de Jogos", {"id": "kit_de_jogos"}),
     [item("lanca"), item("besta_leve"), item("virotes", 20),
      mesma_ferramenta("O mesmo Kit de Jogos escolhido acima."), item("aljava"),
      item("grilhoes"), item("lanterna_coberta"), item("roupas_viagem")], 12,
     "Passou horas incontáveis no posto da torre, um olho na floresta atrás de saqueadores e "
     "o outro na muralha atrás de encrenqueiro."),
    ("guia", "Guia", 183, ["DES", "CON", "SAB"], iniciado("druida"),
     ["furtividade", "sobrevivencia"], ferramenta("ferramentas_de_cartografo"),
     [item("arco_curto"), item("flechas", 20), item("ferramentas_de_cartografo"),
      item("aljava"), item("roupas_viagem"), item("saco_de_dormir"), item("tenda")], 3,
     "Cresceu ao ar livre, longe de terra povoada, aprendendo a se defender enquanto "
     "explorava — e guiando sacerdotes da natureza que o instruíram."),
    ("marinheiro", "Marinheiro", 183, ["FOR", "DES", "SAB"], talento("valentao_de_taverna"),
     ["acrobacia", "percepcao"], ferramenta("ferramentas_de_navegador"),
     [item("adaga"), item("ferramentas_de_navegador"), item("corda"),
      item("roupas_viagem")], 20,
     "Viveu com o vento nas costas e o convés balançando: mais portos do que consegue "
     "lembrar, e tempestade que conta história."),
    ("mercador", "Mercador", 184, ["CON", "INT", "CAR"], talento("sortudo"),
     ["lidar_com_animais", "persuasao"], ferramenta("ferramentas_de_navegador"),
     [item("ferramentas_de_navegador"), item("algibeira", 2), item("roupas_viagem")], 22,
     "Foi aprendiz de comerciante ou mestre de caravana, viajando muito e vivendo de comprar "
     "matéria-prima e vender trabalho acabado."),
    ("nobre", "Nobre", 184, ["FOR", "INT", "CAR"], talento("habilidoso"),
     ["historia", "persuasao"],
     escolher_ferramenta("nobre", "Escolha um tipo de Kit de Jogos", {"id": "kit_de_jogos"}),
     [mesma_ferramenta("O mesmo Kit de Jogos escolhido acima."), item("perfume"),
      item("roupas_finas")], 29,
     "Criado num castelo entre riqueza e privilégio, com educação de primeira e muitas horas "
     "observando a família na corte."),
    ("sabio", "Sábio", 185, ["CON", "INT", "SAB"], iniciado("mago"),
     ["arcanismo", "historia"], ferramenta("suprimentos_de_caligrafo"),
     [item("cajado"), item("suprimentos_de_caligrafo"),
      item("livro", nota="Livro de história."), item("pergaminho", 8), item("tunica")], 8,
     "Viajou entre mansões e mosteiros trocando serviço por acesso à biblioteca, estudando "
     "até os rudimentos da magia."),
    ("soldado", "Soldado", 185, ["FOR", "DES", "CON"], talento("atacante_selvagem"),
     ["atletismo", "intimidacao"],
     escolher_ferramenta("soldado", "Escolha um tipo de Kit de Jogos", {"id": "kit_de_jogos"}),
     [item("lanca"), item("arco_curto"), item("flechas", 20), item("kit_de_curandeiro"),
      mesma_ferramenta("O mesmo Kit de Jogos escolhido acima."), item("aljava"),
      item("roupas_viagem")], 14,
     "Treinou para a guerra assim que virou adulto; a batalha está no sangue, e os exercícios "
     "básicos ainda saem por reflexo."),
]


def montar(aid, nome, pag, atributos, tal, pericias, fer, pacote, po, desc):
    efeitos = [aumento(aid, atributos), tal] + [pericia(p) for p in pericias] + [fer]
    return collections.OrderedDict([
        ("id", aid), ("nome", nome), ("fonte", fonte(pag)), ("revisao", rev()),
        ("descricao_curta", desc),
        ("atributos", atributos),
        ("talento_de_origem", tal.get("talento_id")),
        ("pericias", pericias),
        ("efeitos", efeitos),
        ("equipamento", {
            "opcoes": [
                {"id": "A", "itens": pacote, "moedas": {"po": po}},
                {"id": "B", "itens": [], "moedas": {"po": 50}}],
            "fonte": fonte(pag)}),
    ])


ITENS = [montar(*a) for a in ANTECEDENTES]


def main():
    d = collections.OrderedDict([
        ("catalogo", "antecedentes"), ("nome", "Antecedentes de Personagem"),
        ("fonte", fonte(177)),
        ("nota", "Os 16 do capítulo 4. Todo antecedente tem a mesma forma: três atributos com "
                 "dois modos de aumento, um talento de Origem, duas perícias, uma ferramenta e "
                 "um pacote de equipamento contra 50 PO."),
        ("preenchida", True), ("total", len(ITENS)), ("itens", ITENS)])
    with open(f"{CAT}/antecedentes.json", 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"antecedentes: {len(ITENS)}")
    talentos = sorted({i['talento_de_origem'] for i in ITENS})
    print(f"talentos de Origem usados: {len(talentos)} — {', '.join(talentos)}")


if __name__ == '__main__':
    main()
