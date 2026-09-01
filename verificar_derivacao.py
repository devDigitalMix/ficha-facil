# -*- coding: utf-8 -*-
"""Prova de que o backend consegue montar a conta a partir do dado, sem regra em código.

Não é o motor do app: é um teste. Ele monta o bônus de ataque de um personagem
com uma arma percorrendo APENAS os catálogos — nenhuma regra de D&D escrita aqui
dentro. Se este script conseguir, o backend consegue.

Uso: python3 verificar_derivacao.py
"""
import json, sys

D = 'dados/'


def carregar(p):
    with open(D + p, encoding='utf-8') as f:
        return json.load(f)


ITENS = {i['id']: i for i in carregar('catalogos/itens.json')['itens']}
CLASSES = {c['id']: c for c in carregar('classes.json')['itens']}
DERIV = {d['id']: d for d in carregar('catalogos/valores_derivados.json')['itens']}
PROPS = {p['id']: p for p in carregar('catalogos/propriedades_de_arma.json')['itens']}


def modificador(valor):
    """Lê a fórmula do catálogo em vez de escrever (valor-10)//2 aqui."""
    f = DERIV['modificador_de_atributo']['formula'][0]
    assert f['op'] == 'div_arred_baixo'
    interno = f['args'][0]
    assert interno['op'] == 'soma'
    return (valor + int(interno['args'][1])) // int(f['args'][1])


def bonus_de_proficiencia(nivel):
    return DERIV['bonus_de_proficiencia']['tabela_por_nivel'][str(nivel)]


def atributo_da_arma(arma, escolha_de_acuidade=None):
    """Qual atributo o ataque usa. Sai da regra do catálogo, não de um if."""
    regra = DERIV['atributo_de_ataque_da_arma']
    props = {p['propriedade'] for p in (arma.get('propriedades') or [])}
    for exc in regra['excecoes']:
        alvo = exc['quando'].split(':')[-1]
        if exc['quando'].startswith('arma_tem_propriedade:') and alvo in props:
            if exc['efeito'] == 'escolha_entre':
                return escolha_de_acuidade or exc['opcoes'][0], f"Acuidade ({'/'.join(exc['opcoes'])})"
    return regra['por_alcance_da_arma'][arma['alcance']], f"arma {arma['alcance'].replace('_',' ')}"


def proficiente_com(classe_id, arma):
    """Resolve o filtro de proficiência da classe contra a arma."""
    for e in (CLASSES[classe_id].get('proficiencias_iniciais') or []):
        if e.get('tipo') != 'conceder_proficiencia' or e.get('categoria') != 'arma':
            continue
        f = e['de']['filtro']
        if f.get('categoria') != arma.get('categoria'):
            continue
        g = f.get('grupo')
        if isinstance(g, list):
            if arma.get('grupo') not in g:
                continue
        elif g != arma.get('grupo'):
            continue
        if 'alguma_propriedade' in f:
            tem = {p['propriedade'] for p in (arma.get('propriedades') or [])}
            if not set(f['alguma_propriedade']) & tem:
                continue
        return True, f
    return False, None


def bonus_de_ataque(classe_id, nivel, atributos, arma_id, escolha_de_acuidade=None):
    arma = ITENS[arma_id]
    d = DERIV['jogada_de_ataque_com_arma']
    atrib, motivo = atributo_da_arma(arma, escolha_de_acuidade)
    prof, filtro = proficiente_com(classe_id, arma)
    log, total = [], 0
    for parc in d['parcelas']:
        if parc['chave'] == 'dado':
            log.append(('d20', None))
        elif parc['chave'] == 'mod:atributo_de_ataque_da_arma':
            v = modificador(atributos[atrib])
            total += v
            log.append((f"{parc['rotulo']}: {atrib} {atributos[atrib]} ({motivo})", v))
        elif parc['chave'] == 'prof':
            if prof:
                v = bonus_de_proficiencia(nivel)
                total += v
                log.append((f"{parc['rotulo']} (nível {nivel})", v))
            else:
                log.append((f"{parc['rotulo']}: não proficiente", 0))
    return total, log, arma


def mostrar(titulo, classe, nivel, atributos, arma_id, acuidade=None):
    total, log, arma = bonus_de_ataque(classe, nivel, atributos, arma_id, acuidade)
    print(f"\n{titulo}")
    print(f"  {arma['nome']} — {arma['grupo']} {arma['alcance'].replace('_',' ')}, "
          f"dano {arma['dano']['formula_dado']} {arma['dano']['tipo_dano']}")
    for rotulo, v in log:
        print(f"     {rotulo}" + (f"  {v:+d}" if v is not None else ""))
    print(f"  => jogada de ataque: 1d20 {total:+d}")
    dano = DERIV['dano_de_arma']
    atrib, _ = atributo_da_arma(arma, acuidade)
    m = modificador(atributos[atrib])
    print(f"  => dano: {arma['dano']['formula_dado']} {m:+d} {arma['dano']['tipo_dano']}")


if __name__ == '__main__':
    LADINO = {"FOR": 10, "DES": 16, "CON": 14, "INT": 12, "SAB": 12, "CAR": 10}
    mostrar("Ladino nível 5, Destreza 16, com Arco Curto:", 'ladino', 5, LADINO, 'arco_curto')
    mostrar("Mesmo Ladino com Rapieira (Marcial + Acuidade):", 'ladino', 5, LADINO,
            'rapieira', acuidade='DES')
    mostrar("Mesmo Ladino com Machado Grande (Marcial, sem Acuidade nem Leve):",
            'ladino', 5, LADINO, 'machado_grande')
    GUERREIRO = {"FOR": 18, "DES": 12, "CON": 16, "INT": 10, "SAB": 12, "CAR": 8}
    mostrar("Guerreiro nível 11, Força 18, com Machado Grande:", 'guerreiro', 11,
            GUERREIRO, 'machado_grande')
