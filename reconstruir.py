# -*- coding: utf-8 -*-
"""Reconstrói o dataset do zero, em ordem, num diretório de trabalho separado.

Existe por causa de uma regra do projeto: o gerador é a fonte, e o JSON de `dados/`
é saída. Enquanto ninguém consegue refazer a saída a partir da fonte, essa regra é
só intenção — e correção feita à mão fica invisível.

Uso:
    python3 reconstruir.py [destino]        # reconstrói (padrão: um tempdir)
    python3 reconstruir.py --comparar       # reconstrói e compara com dados/

NUNCA escreve em `dados/`: copia `geradores/`, `schema/` e o PDF para o destino e
roda tudo lá. A comparação é o ponto — diferença entre o reconstruído e o que está
versionado significa correção manual que nenhum gerador registra.
"""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.abspath(__file__))

# A ordem importa: lote antigo rodado depois de um ajuste desfaz o ajuste. Foi o que
# `gerar_guerreiro_catalogos.py` fez na fase 9, quando rodou fora de ordem e desfez o
# capítulo 5. Esta lista é a ordem declarada; mexer nela sem pensar quebra o dataset.
# Cada passo é (script, rótulo) ou (script, rótulo, [argumentos]).
ORDEM = [
    # fase 0 — texto extraído do PDF, de que os parsers dependem
    ('extrair_texto.py', 'fase 0: texto do cap. 6 e do cap. 7'),
    # fase 1 — Apêndice C (glossário), perícias, primitivos
    ('gerar.py', 'fase 1: glossário, perícias, catálogos de vocabulário'),
    ('gerar_condicoes.py', 'fase 1: condições'),
    ('gerar_acoes.py', 'fase 1: ações'),
    ('gerar_efeitos.py', 'fase 1: catálogo de tipos de efeito'),
    # fase 2 — classes do capítulo 3
    ('gerar_monge.py', 'fase 2: Monge'),
    ('gerar_monge_extras.py', 'fase 2: Monge, extras'),
    ('gerar_guerreiro.py', 'fase 2: Guerreiro'),
    ('gerar_guerreiro_catalogos.py', 'fase 2: catálogos do Guerreiro'),
    ('gerar_guerreiro_manobras.py', 'fase 2: manobras'),
    ('gerar_correcoes_guerreiro.py', 'fase 2: correções do Guerreiro'),
    ('parse_lista_mago.py', 'fase 2: lista de magias do Mago'),
    ('gerar_mago.py', 'fase 2: Mago'),
    ('gerar_bruxo.py', 'fase 2: Bruxo'),
    ('gerar_bruxo_classe.py', 'fase 2: Bruxo, classe'),
    ('parse_lista_magias.py', 'fase 2: lista do Bruxo', ['bruxo', '76', '78', '73']),
    ('gerar_bruxo_magias.py', 'fase 2: Bruxo, magias'),
    ('parse_lista_magias.py', 'fase 2: lista do Druida', ['druida', '97', '99', '94']),
    ('gerar_druida.py', 'fase 2: Druida'),
    ('gerar_druida_caracteristicas.py', 'fase 2: Druida, características'),
    ('parse_lista_magias.py', 'fase 2: lista do Clérigo', ['clerigo', '86', '88', '83']),
    ('gerar_clerigo.py', 'fase 2: Clérigo'),
    ('gerar_clerigo_caracteristicas.py', 'fase 2: Clérigo, características'),
    ('gerar_barbaro.py', 'fase 2: Bárbaro'),
    ('gerar_barbaro_car.py', 'fase 2: Bárbaro, características'),
    ('gerar_ladino.py', 'fase 2: Ladino'),
    ('gerar_lote2.py', 'fase 2: lote 2'),
    ('gerar_ajustes_fase2.py', 'fase 2: ajustes'),
    ('gerar_ajustes_marcador.py', 'fase 2: marcador de subclasse'),
    ('gerar_genericas.py', 'fase 2: características genéricas'),
    ('gerar_ajustes_preparacao.py', 'fase 2: preparação de magias'),
    ('gerar_livro_de_magias.py', 'fase 2: o livro de magias do Mago como escolha'),
    # fase 3a — magias do capítulo 7
    ('parse_magias.py', 'fase 3a: parse das magias'),
    ('gerar_magias_detalhadas.py', 'fase 3a: magias detalhadas'),
    ('descricoes_magias.py', 'fase 3a: descrições'),
    # fase 4 — equipamento do capítulo 6
    ('parse_equipamento.py', 'fase 4: parse do equipamento'),
    ('gerar_equipamento.py', 'fase 4: itens e ferramentas'),
    ('gerar_ajustes_equipamento.py', 'fase 4: ajustes de equipamento'),
    ('gerar_propriedades_e_proficiencias.py', 'fase 4: propriedades e proficiências'),
    ('gerar_primitivos.py', 'fase 4b: primitivos (dependem do catálogo de itens)'),
    # fase 5 — valores derivados
    ('gerar_derivados.py', 'fase 5: valores derivados'),
    # fase 7 — Bardo, Feiticeiro e a varredura das opções
    ('gerar_bardo.py', 'fase 7: Bardo'),
    ('gerar_feiticeiro.py', 'fase 7: Feiticeiro'),
    ('gerar_efeitos_de_opcao.py', 'fase 7: efeitos de opção'),
    ('gerar_beneficios_do_terceiro_olho.py', 'fase 7: benefícios do Terceiro Olho'),
    ('gerar_varredura_opcoes.py', 'fase 7: varredura das opções'),
    ('gerar_ajustes_movimento_forcado.py', 'fase 7: movimento forçado'),
    # O Apêndice B precisa existir ANTES do ajuste da Forma Selvagem: é ele que liga
    # o seletor de formas contra o catálogo de criaturas.
    ('gerar_criaturas.py', 'fase 12: Apêndice B, blocos de estatísticas'),
    ('gerar_ajuste_forma_selvagem.py', 'fase 7: Forma Selvagem'),
    # fase 8 — pontos de vida
    ('gerar_pontos_de_vida.py', 'fase 8: pontos de vida'),
    # fase 9 — talentos do capítulo 5
    ('gerar_talentos.py', 'fase 9: talentos'),
    ('gerar_iniciado_em_magia.py', 'fase 9: Iniciado em Magia'),
    # fase 10 — Guardião e Paladino
    ('gerar_guardiao.py', 'fase 10: Guardião'),
    ('gerar_paladino.py', 'fase 10: Paladino'),
    # fase 11 — capítulo 4
    ('gerar_antecedentes.py', 'fase 11: antecedentes'),
    ('gerar_especies.py', 'fase 11: espécies'),
    # auditorias
    ('gerar_ajustes_historicos.py', 'auditoria 2026-09-02: correções que eram feitas à mão'),
    ('gerar_ajustes_maestria.py', 'auditoria 2026-09-02: marcas obsoletas de maestria'),
    ('gerar_ajustes_auditoria.py', 'auditoria 2026-09-02: fontes herdadas, primitivos, reservados'),
    ('gerar_descricoes_de_equipamento.py', 'auditoria 2026-09-02: descrições de itens e ferramentas'),
    # fase 15 — achados ao escrever o motor
    ('gerar_ajustes_aumento_de_antecedente.py',
     'fase 15: aumento de atributo do antecedente (p. 177), achado pelo motor'),
    ('gerar_ajustes_efeitos_aninhados.py',
     'fase 15: o que um efeito aninhado significa — condição ou estrutura'),
    ('gerar_ajustes_ids_de_escolha.py',
     'fase 16: id para as 53 escolhas que não tinham'),
    ('gerar_ajustes_variantes_de_antecedente.py',
     'fase 16: quatro escolhas que ofereciam a categoria em vez das variantes'),
    ('gerar_ajustes_escolha_de_um.py',
     'fase 16: nove talentos que pediam escolha entre uma opção só'),
    ('gerar_ajustes_nomes_de_magia.py',
     'fase 19: quatro magias com o nome diferente da entrada do capítulo 7'),
    ('gerar_ajustes_efeito_nomeado.py',
     'fase 23: 15 efeitos nomeados que não diziam de que catálogo vinham'),
    ('gerar_ajustes_filtros_de_proficiencia.py',
     'fase 23: três chaves de filtro inventadas, em nove escolhas'),
    ('gerar_ajustes_idiomas.py',
     'fase 23: escolher idioma não oferece o que já se fala'),
    ('gerar_ajustes_espacos_de_magia.py',
     'fase 23: espaços do Bardo e do Feiticeiro numa coluna por círculo'),
    ('gerar_escala_dos_truques.py',
     'fase 23: o dado do truque por nível, declarado em vez de em prosa'),
    ('gerar_idiomas_iniciais.py',
     'fase 24: Comum e mais dois idiomas, que todo personagem tem (p. 37)'),
    ('gerar_niveis_de_dominio.py',
     'fase 24: quanto vale proficiência e Especialização, declarado'),
    # fase 13 — vocabulário de runtime. A normalização reescreve o dado inteiro,
    # então é a ÚLTIMA de todas: qualquer gerador de conteúdo rodado depois dela
    # reintroduz o token antigo, e o validador acusa. A declaração vem em seguida,
    # e é ela que fecha a lista para quem vier.
    ('gerar_normalizacao_vocabulario.py', 'fase 13: fusão do vocabulário de runtime'),
    ('gerar_vocabulario_de_runtime.py', 'fase 13: vocabulário de runtime declarado'),
]


def preparar(destino):
    os.makedirs(destino, exist_ok=True)
    shutil.copytree(os.path.join(RAIZ, 'geradores'), os.path.join(destino, 'geradores'),
                    dirs_exist_ok=True)
    shutil.copytree(os.path.join(RAIZ, 'schema'), os.path.join(destino, 'schema'),
                    dirs_exist_ok=True)
    for extra in ('validar.py', 'checar_schema.py'):
        shutil.copy(os.path.join(RAIZ, extra), destino)
    for nome in os.listdir(RAIZ):
        if nome.lower().endswith('.pdf'):
            shutil.copy(os.path.join(RAIZ, nome), destino)
    os.makedirs(os.path.join(destino, 'dados', 'catalogos'), exist_ok=True)


def reconstruir(destino):
    preparar(destino)
    resultados = []
    for passo in ORDEM:
        script, rotulo = passo[0], passo[1]
        argumentos = passo[2] if len(passo) > 2 else []
        caminho = os.path.join(destino, 'geradores', script)
        if not os.path.exists(caminho):
            resultados.append((script, 'AUSENTE', rotulo, ''))
            continue
        r = subprocess.run([sys.executable, caminho] + argumentos, cwd=destino,
                           capture_output=True, text=True, timeout=300)
        estado = 'ok' if r.returncode == 0 else 'FALHOU'
        erro = (r.stderr.strip().splitlines() or [''])[-1][:160]
        resultados.append((script, estado, rotulo, erro))
    return resultados


def comparar(destino):
    """Compara arquivo a arquivo o reconstruído com o versionado."""
    import filecmp
    base_a = os.path.join(RAIZ, 'dados')
    base_b = os.path.join(destino, 'dados')
    rel = lambda raiz: {os.path.relpath(os.path.join(dp, f), raiz)
                        for dp, _, fs in os.walk(raiz) for f in fs if f.endswith('.json')}
    a, b = rel(base_a), rel(base_b)
    so_versionado = sorted(a - b)
    so_reconstruido = sorted(b - a)
    diferentes = []
    for f in sorted(a & b):
        pa, pb = os.path.join(base_a, f), os.path.join(base_b, f)
        if filecmp.cmp(pa, pb, shallow=False):
            continue
        try:
            da = json.load(open(pa, encoding='utf-8'))
            db = json.load(open(pb, encoding='utf-8'))
        except Exception:
            diferentes.append((f, 'CONTEÚDO'))
            continue
        if da == db:
            # mesmos dados, mesma ordem: só espaço em branco ou ordem de chave
            diferentes.append((f, 'só formatação'))
            continue
        # mesmos itens em ordem diferente é equivalente, não divergência
        ia = {i['id']: i for i in da.get('itens', [])}
        ib = {i['id']: i for i in db.get('itens', [])}
        cabeca_a = {k: v for k, v in da.items() if k != 'itens'}
        cabeca_b = {k: v for k, v in db.items() if k != 'itens'}
        if ia == ib and cabeca_a == cabeca_b:
            diferentes.append((f, 'ordem/chaves'))
        else:
            diferentes.append((f, 'CONTEÚDO'))
    return so_versionado, so_reconstruido, diferentes


def main():
    quer_comparar = '--comparar' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    destino = args[0] if args else tempfile.mkdtemp(prefix='ficha-facil-rebuild-')
    print(f"reconstruindo em: {destino}\n")
    resultados = reconstruir(destino)
    ok = sum(1 for _, e, _, _ in resultados if e == 'ok')
    for script, estado, rotulo, erro in resultados:
        if estado != 'ok':
            print(f"  {estado:8} {script:42} {rotulo}")
            if erro:
                print(f"           └─ {erro}")
    print(f"\n{ok} de {len(resultados)} geradores rodaram sem erro")

    if quer_comparar:
        so_v, so_r, dif = comparar(destino)
        print(f"\n--- comparação com dados/")
        print(f"só no versionado ({len(so_v)}): {so_v}")
        print(f"só no reconstruído ({len(so_r)}): {so_r}")
        conteudo = [f for f, t in dif if t == 'CONTEÚDO']
        print(f"idênticos a menos de formatação: "
              f"{len([f for f, t in dif if t == 'só formatação'])}")
        equiv = [f for f, t in dif if t == 'ordem/chaves']
        print(f"equivalentes, com itens em ordem diferente ({len(equiv)}): {equiv}")
        print(f"DIFERENTES EM CONTEÚDO ({len(conteudo)}):")
        for f in conteudo:
            print(f"   {f}")
        # Diferença de conteúdo é FALHA, e não relatório. A conferência da raiz olha
        # só o código de saída: com --comparar devolvendo 0 mesmo com três arquivos
        # divergentes, ela dizia "19 de 19 passos limpos" enquanto o dado versionado
        # já não era o que os geradores produzem. Um gerador novo que ninguém
        # registrou passava despercebido exatamente assim.
        if conteudo:
            return 1
    return 0 if ok == len(resultados) else 1


if __name__ == '__main__':
    sys.exit(main())
