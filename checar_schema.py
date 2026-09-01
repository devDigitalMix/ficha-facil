# -*- coding: utf-8 -*-
"""Roda os JSON Schemas de schema/ contra os arquivos de dados/.

Existia como passo solto a cada lote; virou script para não depender de eu
lembrar de rodar. O validador semântico é `validar.py`; este aqui só cobra a
FORMA (campos obrigatórios, tipos, padrões de id).
"""
import glob, json, os, sys

try:
    from jsonschema import Draft202012Validator, RefResolver
except ImportError:
    print("jsonschema não instalado: pip install jsonschema --break-system-packages")
    sys.exit(2)

SCHEMAS = {}
for p in glob.glob('schema/*.schema.json'):
    s = json.load(open(p, encoding='utf-8'))
    SCHEMAS[s['$id']] = s

BASE = 'https://ficha-facil.local/'
ALVOS = [
    ('dados/catalogos/*.json', BASE + 'catalogo.schema.json'),
    ('dados/caracteristicas.json', BASE + 'caracteristicas.schema.json'),
    ('dados/classes.json', BASE + 'classes.schema.json'),
    ('dados/subclasses.json', BASE + 'subclasses.schema.json'),
    ('dados/condicoes.json', BASE + 'condicoes.schema.json'),
    ('dados/acoes.json', BASE + 'acoes.schema.json'),
]


def main():
    falhas = arquivos = 0
    for padrao, sid in ALVOS:
        for caminho in sorted(glob.glob(padrao)):
            arquivos += 1
            doc = json.load(open(caminho, encoding='utf-8'))
            v = Draft202012Validator(
                SCHEMAS[sid], resolver=RefResolver(sid, SCHEMAS[sid], store=SCHEMAS))
            for e in sorted(v.iter_errors(doc), key=lambda x: list(x.path)):
                falhas += 1
                print(f"FALHA {os.path.basename(caminho)} "
                      f"{'/'.join(str(x) for x in e.path)}: {e.message}")
    print(f"\n{arquivos} arquivos · "
          + ("todos passam" if not falhas else f"{falhas} falhas de forma"))
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
