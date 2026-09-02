# -*- coding: utf-8 -*-
"""Benefícios do Terceiro Olho (Adivinhador do Mago, cap. 3, p. 155).

Este catálogo era o único arquivo de `dados/` sem gerador nenhum: foi escrito à
mão numa fase antiga e a reconstrução não o produzia, o que fazia
`gerar_varredura_opcoes.py` falhar. Escrito aqui a partir do conteúdo já revisado,
para fechar o buraco.

A Compreensão Superior é o último `substituir_regra` do dataset. Continua como
dúvida de propósito: "ler qualquer idioma" não tem primitivo, e criar um só para
ela seria vocabulário de um uso só. Ver BACKLOG B6.4.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos

FONTE = {"capitulo": 3, "pagina_livro": 155, "pagina_pdf": 159}

ITENS = [
    {
        "id": "compreensao_superior",
        "nome": "Compreensão Superior",
        "descricao_curta": "Você pode ler qualquer idioma.",
        "efeitos": [{
            "tipo": "substituir_regra",
            "chave": "ler_qualquer_idioma",
            "duracao": "ate_o_proximo_descanso",
            "revisao": "duvida",
            "nota": "Ler qualquer idioma não tem primitivo próprio no esquema; fica como regra "
                    "declarada até existir um efeito de compreensão de idiomas.",
        }],
        "revisao": {
            "status": "duvida",
            "notas": "Ler qualquer idioma não tem primitivo próprio no esquema; fica como "
                     "substituir_regra até existir um efeito de compreensão de idiomas "
                     "(provável no cap. 5, com os talentos).",
        },
    },
    {
        "id": "ver_o_invisivel",
        "nome": "Ver o Invisível",
        "descricao_curta": "Conjura Ver o Invisível sem gastar espaço de magia.",
        "efeitos": [{"tipo": "conjurar_sem_espaco", "magia": "ver_o_invisivel"}],
    },
    {
        "id": "visao_no_escuro",
        "nome": "Visão no Escuro",
        "descricao_curta": "Visão no Escuro com alcance de 36 metros.",
        "efeitos": [{
            "tipo": "conceder_sentido", "sentido": "visao_no_escuro", "alcance_m": 36,
            "empilha": "substitui_se_maior", "duracao": "ate_o_proximo_descanso",
        }],
    },
]


def main():
    d = {"catalogo": "beneficios_do_terceiro_olho", "nome": "Benefícios do Terceiro Olho",
         "fonte": FONTE, "total": len(ITENS), "itens": ITENS}
    caminho = os.path.join(caminhos.CATALOGOS, 'beneficios_do_terceiro_olho.json')
    os.makedirs(caminhos.CATALOGOS, exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"beneficios_do_terceiro_olho: {len(ITENS)} itens")


if __name__ == '__main__':
    main()
