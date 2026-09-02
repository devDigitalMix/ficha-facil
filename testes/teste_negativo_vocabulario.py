# -*- coding: utf-8 -*-
"""Teste negativo do vocabulário de runtime (fase 13).

O ponto desta fase é que sinônimo acidental deixe de entrar calado. Um validador
que diz "0 erros" sem nunca ter reprovado nada não prova coisa alguma — então
aqui se planta, de propósito, cada forma do defeito que a fase existiu para
matar, e se cobra que o validador acuse.

O defeito característico é o primeiro: alguém escreve `ao_entrar_em_furia` como
`entrar_em_furia`, o dado continua parecendo certo, e no motor o efeito nunca
dispara.
"""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # os testes moram em testes/; a raiz do projeto é um nível acima
CAR = 'caracteristicas.json'
VOC = 'vocabulario_de_runtime.json'


def carregar(b, rel):
    return json.load(open(os.path.join(b, rel), encoding='utf-8'))


def gravar(b, rel, d):
    json.dump(d, open(os.path.join(b, rel), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def item(d, iid):
    return next(i for i in d['itens'] if i['id'] == iid)


def primeiro_efeito_com(d, iid, campo):
    for e in item(d, iid)['efeitos']:
        if campo in e:
            return e
    raise AssertionError('sem %s em %s' % (campo, iid))


# ------------------------------------------------------------------ defeitos

def gatilho_sinonimo(b):
    """O defeito que deu origem à fase: o mesmo evento com outro nome."""
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'vitalidade_da_arvore', 'gatilho')['gatilho'] = 'entrar_em_furia'
    gravar(b, CAR, d)


def gatilho_inventado(b):
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'vitalidade_da_arvore', 'gatilho')['gatilho'] = 'ao_espirrar'
    gravar(b, CAR, d)


def campo_momento_ressuscitado(b):
    """`momento` foi revogado: quem o reintroduzir está criando o sinônimo de novo."""
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'vitalidade_da_arvore', 'gatilho')['momento'] = 'ao_entrar_em_furia'
    gravar(b, CAR, d)


def predicado_inventado(b):
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'ramos_da_arvore', 'condicao')['condicao'] = {
        'todas': ['em_forma_de_estrela']}   # o certo é 'em_forma_estrelada'
    gravar(b, CAR, d)


def predicado_com_argumento_inexistente(b):
    """Família validada contra outro catálogo: `condicao:<id de condicoes>`."""
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'ramos_da_arvore', 'condicao')['condicao'] = {
        'todas': ['condicao:sonolento']}
    gravar(b, CAR, d)


def operador_logico_inventado(b):
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'ramos_da_arvore', 'condicao')['condicao'] = {
        'quaisquer': ['em_forma_estrelada']}
    gravar(b, CAR, d)


def comparacao_com_operador_inventado(b):
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'ramos_da_arvore', 'condicao')['condicao'] = {
        'todas': [{'comparar': ['pv_atual'], 'op': 'maior_ou_igual', 'com': ['1']}]}
    gravar(b, CAR, d)


def duracao_sinonima(b):
    """As oito grafias de 'até o fim do turno atual' viraram uma."""
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'passo_lunar', 'duracao')['duracao'] = 'resto_do_turno'
    gravar(b, CAR, d)


def duracao_em_prosa(b):
    """Duração de tempo é objeto; texto solto o motor não executa."""
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'passo_lunar', 'duracao')['duracao'] = '1 minuto'
    gravar(b, CAR, d)


def unidade_de_duracao_inventada(b):
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'passo_lunar', 'duracao')['duracao'] = {
        'quantidade': ['1'], 'unidade': 'rodada'}
    gravar(b, CAR, d)


def custo_inventado(b):
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'passo_lunar', 'custo')['custo'] = 'meia_acao'
    gravar(b, CAR, d)


def empilhamento_inventado(b):
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'ramos_da_arvore', 'empilha')['empilha'] = 'acumula'
    gravar(b, CAR, d)


def fase_inventada(b):
    d = carregar(b, CAR)
    primeiro_efeito_com(d, 'vitalidade_da_arvore', 'gatilho')['fase'] = 'durante_a_jogada'
    gravar(b, CAR, d)


def vocabulario_ausente(b):
    """Sem a lista declarada, nada disto acima é checado — e isso é o erro."""
    os.remove(os.path.join(b, VOC))


def token_declarado_mas_nao_usado_nao_e_erro(b):
    """Controle: declarar um predicado a mais é folga, não defeito.

    A lista fechada existe para barrar o que o dado usa sem declarar, não para
    obrigar o dado a usar tudo o que a lista tem. Este caso TEM de passar — se
    ele falhar, o validador está apertado demais e vai atrapalhar quem escrever
    a próxima característica.
    """
    d = carregar(b, VOC)
    d['predicados'].append('predicado_que_ninguem_usa_ainda')
    gravar(b, VOC, d)


DEFEITOS = [
    ("gatilho escrito com o sinônimo antigo", gatilho_sinonimo),
    ("gatilho que ninguém declarou", gatilho_inventado),
    ("campo 'momento' reintroduzido", campo_momento_ressuscitado),
    ("predicado que ninguém declarou", predicado_inventado),
    ("predicado de família com argumento inexistente",
     predicado_com_argumento_inexistente),
    ("operador lógico inventado na condição", operador_logico_inventado),
    ("comparação com operador inventado", comparacao_com_operador_inventado),
    ("duração escrita com o sinônimo antigo", duracao_sinonima),
    ("duração de tempo escrita como prosa", duracao_em_prosa),
    ("unidade de duração inventada", unidade_de_duracao_inventada),
    ("custo que ninguém declarou", custo_inventado),
    ("modo de empilhamento inventado", empilhamento_inventado),
    ("fase que ninguém declarou", fase_inventada),
    ("vocabulário de runtime apagado", vocabulario_ausente),
]

DEVEM_PASSAR = [
    ("token declarado e ainda não usado", token_declarado_mas_nao_usado_nao_e_erro),
]


def rodar(plantar, base):
    plantar(base)
    return subprocess.run([sys.executable, os.path.join(RAIZ, 'validar.py'), base],
                          capture_output=True, text=True).returncode


def main():
    pegos = 0
    for nome, plantar in DEFEITOS:
        tmp = tempfile.mkdtemp()
        base = os.path.join(tmp, 'dados')
        shutil.copytree(os.path.join(RAIZ, 'dados'), base)
        ok = rodar(plantar, base) != 0
        pegos += ok
        print(f"{'PEGOU ' if ok else 'PASSOU'} {nome}")
        if not ok:
            print("        (o validador não acusou — isto é um furo)")
        shutil.rmtree(tmp)

    folgas = 0
    for nome, plantar in DEVEM_PASSAR:
        tmp = tempfile.mkdtemp()
        base = os.path.join(tmp, 'dados')
        shutil.copytree(os.path.join(RAIZ, 'dados'), base)
        ok = rodar(plantar, base) == 0
        folgas += ok
        print(f"{'OK    ' if ok else 'FALHOU'} {nome} (tem de passar)")
        shutil.rmtree(tmp)

    print(f"\n{pegos} de {len(DEFEITOS)} defeitos plantados foram pegos; "
          f"{folgas} de {len(DEVEM_PASSAR)} casos de folga passaram")
    return 0 if (pegos == len(DEFEITOS) and folgas == len(DEVEM_PASSAR)) else 1


if __name__ == '__main__':
    sys.exit(main())
