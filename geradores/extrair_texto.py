# -*- coding: utf-8 -*-
"""Extrai do PDF os textos que os parsers consomem, em `intermediarios/`.

Este passo existia como comando solto rodado à mão em cada sessão, gravando em
/tmp. Quando o /tmp sumiu, seis geradores pararam de rodar e o dataset deixou de
ser reproduzível. Agora é um script do projeto, determinístico e versionado.

A saída NÃO entra no git: é derivada do PDF e regenerável a qualquer momento.

Uso: python3 geradores/extrair_texto.py
"""
import json, os, sys, warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caminhos

warnings.filterwarnings('ignore')

# Faixas em página do LIVRO. A página do PDF é a do livro + 4; o índice do pypdf é
# 0-based, então índice = página do livro + 3.
FAIXAS = {
    'cap6': (213, 233),   # Equipamento
    'cap7': (239, 343),   # Magias
}


def indice(pagina_do_livro):
    return pagina_do_livro + 3


def extrair(nome, primeira, ultima):
    """Escreve <nome>.txt e <nome>_paginas.json (offsets de caractere por página)."""
    import pypdf
    leitor = pypdf.PdfReader(caminhos.pdf())
    partes, offsets, pos = [], [], 0
    for pagina in range(primeira, ultima + 1):
        texto = leitor.pages[indice(pagina)].extract_text() or ''
        offsets.append([pos, pagina])
        partes.append(texto)
        pos += len(texto) + 1  # +1 do "\n" que junta as páginas
    inteiro = "\n".join(partes)
    with open(caminhos.intermediario(f'{nome}.txt'), 'w', encoding='utf-8') as f:
        f.write(inteiro)
    with open(caminhos.intermediario(f'{nome}_paginas.json'), 'w', encoding='utf-8') as f:
        json.dump(offsets, f, ensure_ascii=False)
    return len(inteiro), len(offsets)


def main():
    for nome, (a, b) in FAIXAS.items():
        n, p = extrair(nome, a, b)
        print(f"{nome}: páginas {a}-{b} do livro | {p} páginas | {n} caracteres")
    print(f"em: {caminhos.INTERMEDIARIOS}")


if __name__ == '__main__':
    main()
