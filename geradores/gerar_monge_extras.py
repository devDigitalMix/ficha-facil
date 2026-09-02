# -*- coding: utf-8 -*-
"""Registra no catálogo de engine os tipos de efeito e alvos que a Fase 2 introduziu,
e cria os catálogos parciais que as escolhas do Monge referenciam."""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
def rd(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
def wr(p, o): json.dump(o, open(os.path.join(D, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

NOVOS = [
 ("dado_de_dano","coluna escopo modo condicao","Dado de dano alternativo vindo de uma coluna da tabela de classe (Artes Marciais)."),
 ("substituir_atributo","de para escopo aplica_a condicao","Troca o atributo usado em ataque/dano/CD (Ataques com Destreza)."),
 ("restaurar_recurso","recurso_id quantidade ate gatilho condicao","Devolve pontos a um recurso com recarga."),
 ("cura","formula minimo custo custo_em_foco alcance modo","Recupera Pontos de Vida."),
 ("reducao_de_dano","formula tipos_de_dano custo gatilho origem_do_dano modo","Reduz dano recebido (Defletir Ataques, Queda Lenta)."),
 ("dano","formula_dado somar tipo_dano salvaguarda area modo frequencia gatilho","Causa dano, com ou sem salvaguarda e área."),
 ("escolher_tipo_de_dano","aplica_a opcoes condicao","O jogador escolhe o tipo de dano na hora."),
 ("alterar_resultado_de_salvaguarda","alvo aplica_a em_sucesso em_falha condicao","Evasão e similares."),
 ("remover_condicao","condicoes quantidade momento beneficiario","Remove condições de si ou do alvo."),
 ("imunidade_a_risco","riscos","Não sofre um Risco do glossário (fome, sede)."),
 ("melhorar_caracteristica","alvo efeitos custo_em_foco condicao","Altera outra característica já concedida, em vez de duplicá-la."),
 ("pontos_de_vida_temporarios","formula condicao","Concede PV temporários."),
 ("rolar_novamente","alvo custo_em_foco gatilho usa_novo_resultado","Permite rejogar um dado."),
 ("teleporte","alcance_m custo requisitos","Teleporte de curta distância."),
 ("conceder_subclasse","chave","Aplica a subclasse escolhida."),
 ("aplicar_efeito_nomeado","chave","Aplica um efeito definido em 'efeitos_nomeados' da própria característica."),
]
t = rd('catalogos/tipos_de_efeito.json')
existentes = {i['id'] for i in t['itens']}
for i, campos, nota in NOVOS:
    if i not in existentes:
        t['itens'].append({"id": i, "nome": i.replace('_', ' ').capitalize(),
                           "origem": "NOVO_FASE2", "campos": campos.split(), "nota": nota})
t['total'] = len(t['itens'])
wr('catalogos/tipos_de_efeito.json', t)

a = rd('catalogos/alvos.json')
for i, n in [("alcance_do_ataque_desarmado", "Alcance do Ataque Desarmado")]:
    if i not in {x['id'] for x in a['itens']}:
        a['itens'].append({"id": i, "nome": n})
a['total'] = len(a['itens'])
wr('catalogos/alvos.json', a)

# catálogo parcial de talentos (só os referenciados pelo Monge)
wr('catalogos/talentos.json', {"catalogo": "talentos", "nome": "Talentos", "parcial": True,
 "fonte": {"capitulo": 5, "pagina_livro": 198, "pagina_pdf": 202},
 "nota": "PARCIAL: apenas os talentos já referenciados. O capítulo 5 completo ainda não foi extraído.",
 "total": 3, "itens": [
  {"id": "aumento_no_valor_de_atributo", "nome": "Aumento no Valor de Atributo", "categoria": "geral",
   "fonte": {"capitulo": 5, "pagina_livro": 199, "pagina_pdf": 203}},
  {"id": "dadiva_epica", "nome": "Dádiva Épica", "categoria": "epico",
   "fonte": {"capitulo": 5, "pagina_livro": 210, "pagina_pdf": 214}},
  {"id": "dadiva_do_ataque_irresistivel", "nome": "Dádiva do Ataque Irresistível", "categoria": "epico",
   "fonte": {"capitulo": 5, "pagina_livro": 210, "pagina_pdf": 214}}]})

# catálogo dos três efeitos da Técnica da Mão Espalmada
wr('catalogos/efeitos_da_mao_espalmada.json', {"catalogo": "efeitos_da_mao_espalmada",
 "nome": "Efeitos da Técnica da Mão Espalmada",
 "fonte": {"capitulo": 3, "pagina_livro": 162, "pagina_pdf": 166}, "total": 3,
 "itens": [
  {"id": "derrubar", "nome": "Derrubar", "descricao_curta": "Salvaguarda de Destreza ou o alvo fica Caído."},
  {"id": "desorientar", "nome": "Desorientar", "descricao_curta": "O alvo não pode realizar Ataques de Oportunidade até o início do próximo turno dele."},
  {"id": "empurrar", "nome": "Empurrar", "descricao_curta": "Salvaguarda de Força ou o alvo é empurrado até 4,5 metros."}]})

# marcador de subclasse na progressão vira entidade real
c = rd('caracteristicas.json')
if not any(i['id'] == 'caracteristica_de_subclasse' for i in c['itens']):
    c['itens'].append({"id": "caracteristica_de_subclasse", "nome": "Característica de Subclasse",
      "classe": "monge", "nivel": 6, "niveis_repetidos": [6, 11, 17],
      "fonte": {"capitulo": 3, "pagina_livro": 161, "pagina_pdf": 165},
      "revisao": {"status": "ok", "notas": "Marcador: a característica concreta vem da subclasse escolhida."},
      "descricao_curta": "Nestes níveis você adquire a característica correspondente da sua subclasse.",
      "efeitos": [{"tipo": "efeito_narrativo", "chave": "caracteristica_de_subclasse",
                   "texto": "Concede a característica do nível correspondente da subclasse escolhida."}]})
    c['total'] = len(c['itens'])
    wr('caracteristicas.json', c)
print('extras ok')
