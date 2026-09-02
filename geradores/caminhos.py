# -*- coding: utf-8 -*-
"""Caminhos do projeto, num lugar só.

Existe porque os geradores das primeiras fases apontavam para arquivos de scratch
da sessão em que foram escritos (`/tmp/claude-0/cap7.txt`, `/mnt/user-data/...`).
Isso quebrava a regra central do projeto: se o gerador não roda, ele deixa de ser
fonte e vira documentação. Aqui tudo é resolvido a partir da raiz do repositório.
"""
import glob, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, 'dados')
CATALOGOS = os.path.join(DADOS, 'catalogos')
# Texto extraído do PDF. Regenerável por `geradores/extrair_texto.py`, e por isso
# fora do controle de versão: é derivado, não fonte.
INTERMEDIARIOS = os.path.join(RAIZ, 'intermediarios')


def pdf():
    """O PDF do Livro do Jogador, achado por glob na raiz — nunca por caminho fixo."""
    achados = sorted(glob.glob(os.path.join(RAIZ, '*.pdf')))
    if not achados:
        raise FileNotFoundError(
            f"nenhum PDF na raiz do repositório ({RAIZ}). O Livro do Jogador precisa estar lá.")
    return achados[0]


def intermediario(nome):
    os.makedirs(INTERMEDIARIOS, exist_ok=True)
    return os.path.join(INTERMEDIARIOS, nome)


def exigir(nome, quem):
    """Caminho de um intermediário que PRECISA existir — falha cedo e dizendo como resolver."""
    p = intermediario(nome)
    if not os.path.exists(p):
        raise FileNotFoundError(
            f"{quem} precisa de '{nome}', que não existe.\n"
            f"    Rode antes: python3 geradores/extrair_texto.py")
    return p
