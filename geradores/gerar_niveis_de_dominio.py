# -*- coding: utf-8 -*-
"""O que "ser proficiente" e "ter Especialização" valem em número, declarado.

O João, em 2026-09-04: "poder ver o número que tenho em arcanismo".

Ao ir buscar esse número apareceu que **a Especialização não somava nada**. O dado
declara `nivel_dominio` no `conceder_proficiencia`, mas o motor guardava só a chave e
jogava o nível fora — então o Especialista do Ladino, o do Bardo e os dois talentos de
Especialização em Perícia existiam no JSON e não existiam na conta.

E os valores usados eram quatro para três coisas: `proficiente` (26), `especialista`
(4), `especializacao` (1, no Bardo) e `treinado` (2, no Treinamento Marcial). Duas
grafias para a mesma ideia é o tipo de coisa que faz uma regra valer em 26 lugares e
falhar em 3.

Este gerador faz duas coisas:

1. **Normaliza** `especializacao` → `especialista` e `treinado` → `proficiente`.
2. **Declara o catálogo `niveis_de_dominio`**, com o que cada um vale: proficiente
   soma o Bônus de Proficiência uma vez, Especialização soma duas — "seu Bônus de
   Proficiência é dobrado para qualquer teste de habilidade que use essa perícia"
   (p. 361, glossário). O multiplicador vira DADO: o motor lê, e a regra continua
   morando no dataset como todas as outras.
"""
import json, os

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')

TROCAS = {'especializacao': 'especialista', 'treinado': 'proficiente'}
trocados = []


def anda(no, ctx):
    if isinstance(no, list):
        for x in no:
            anda(x, ctx)
        return
    if not isinstance(no, dict):
        return
    n = no.get('nivel_dominio')
    if isinstance(n, str) and n in TROCAS:
        no['nivel_dominio'] = TROCAS[n]
        trocados.append(f'{ctx}: {n} → {TROCAS[n]}')
    for v in no.values():
        anda(v, ctx)


for arquivo in ('caracteristicas.json', 'classes.json', 'subclasses.json',
                os.path.join('catalogos', 'talentos.json'),
                os.path.join('catalogos', 'especies.json'),
                os.path.join('catalogos', 'antecedentes.json')):
    caminho = os.path.join(D, arquivo)
    doc = json.load(open(caminho, encoding='utf-8'))
    for item in doc.get('itens', []):
        anda(item, f'{os.path.basename(arquivo)[:-5]}/{item["id"]}')
    json.dump(doc, open(caminho, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

catalogo = {
    "catalogo": "niveis_de_dominio",
    "nome": "Níveis de Domínio",
    "fonte": {"capitulo": "ap_c", "pagina_livro": 361, "pagina_pdf": 365},
    "nota": ("Quanto o Bônus de Proficiência entra num teste, por nível de domínio. "
             "Está aqui, e não no motor, porque é regra do livro como qualquer outra."),
    "total": 2,
    "itens": [
        {"id": "proficiente", "nome": "Proficiente", "multiplicador_do_bonus": 1,
         "descricao_curta": "Soma o Bônus de Proficiência ao teste."},
        {"id": "especialista", "nome": "Especialização", "multiplicador_do_bonus": 2,
         "descricao_curta": ("Dobra o Bônus de Proficiência para os testes que usem "
                             "aquela perícia ou ferramenta (p. 361).")},
    ],
}
json.dump(catalogo, open(os.path.join(D, 'catalogos', 'niveis_de_dominio.json'), 'w',
                         encoding='utf-8'), ensure_ascii=False, indent=2)

print(f'ok — catálogo niveis_de_dominio declarado; {len(trocados)} grafias normalizadas:')
for t in trocados:
    print('   ', t)
