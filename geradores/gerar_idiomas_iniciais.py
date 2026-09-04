# -*- coding: utf-8 -*-
"""Todo personagem sabe Comum e mais dois idiomas — e isso não é de espécie nenhuma.

O João, em 2026-09-04: "não deveria ser retirado a língua comum e da raça? acho que
isso todos têm por padrão, ou apenas a comum?"

O livro responde as duas coisas, e a segunda contraria o que a memória de 5e sugere:

  "O seu personagem sabe pelo menos três idiomas: Comum e mais dois idiomas que você
  pode escolher da tabela Idiomas Comuns." (p. 37, capítulo 2)

**É só o Comum que vem de graça, e ele não vem da espécie.** Em 2024 nenhuma espécie
concede idioma — o Anão não dá Anão, o Élfico não vem do Elfo. Idioma é passo da
criação do personagem (capítulo 2) e, depois, característica de classe (a Gíria do
Ladrão, o Idioma Druídico) ou de talento. Conferido no dataset: espécie nenhuma cita
idioma, e antecedente nenhum também.

Faltava, então, o começo: o personagem nascia sem falar nada, e a escolha "mais um
idioma" do Ladino oferecia o Comum como se ele não o soubesse.

Como isto entra sem inventar máquina nova: a característica ganha
`escopo: "todo_personagem"`, e o coletor passa a recolher tudo que tenha esse escopo
junto com espécie, antecedente e classe. É o mesmo desenho de `escopo: "generico"`
que já existia — a diferença é quem concede: ali é a classe, aqui é a criação.
"""
import json, os

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
p = os.path.join(D, 'caracteristicas.json')
doc = json.load(open(p, encoding='utf-8'))
por_id = {i['id']: i for i in doc['itens']}

FONTE = {"capitulo": 2, "pagina_livro": 37, "pagina_pdf": 41}

idiomas = {
    "id": "idiomas_iniciais",
    "nome": "Idiomas",
    "escopo": "todo_personagem",
    "tipo_de_entrada": "caracteristica",
    "fonte": FONTE,
    "revisao": {"status": "ok", "notas": "Capítulo 2, passo de criação do personagem."},
    "descricao_curta": ("Todo personagem conhece o Comum e mais dois idiomas à sua escolha, "
                        "tirados da tabela Idiomas Comuns. Classe, antecedente e talentos "
                        "podem conceder outros — inclusive raros."),
    "efeitos": [
        {"tipo": "conceder_proficiencia", "categoria": "idioma", "chave": "comum",
         "nivel_dominio": "proficiente",
         "nota": "Todo personagem jogador conhece o Comum, que se originou em Sigil (p. 37)."},
        {"id": "idiomas_iniciais_escolha", "tipo": "escolha",
         "rotulo": "Escolha dois idiomas",
         "quantidade": 2, "gatilho": "ao_adquirir",
         "de": {"catalogo": "idiomas",
                # A tabela é a de Idiomas COMUNS: os raros vêm por característica que
                # os conceda, e não pela criação (p. 37).
                "filtro": {"raridade": "comum"},
                "filtro_adicional": {"com_proficiencia": False}},
         "efeito_por_item_escolhido": {"tipo": "conceder_proficiencia", "categoria": "idioma",
                                       "chave": "{{escolhido}}", "nivel_dominio": "proficiente"}},
    ],
}

if 'idiomas_iniciais' in por_id:
    por_id['idiomas_iniciais'].update(idiomas)
else:
    doc['itens'].append(idiomas)
doc['itens'].sort(key=lambda i: i['id'])
doc['total'] = len(doc['itens'])

json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok — idiomas iniciais (Comum + dois da tabela Idiomas Comuns) para todo personagem')
