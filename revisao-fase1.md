# Fase 1 — Ap. C: Glossário de Regras — lote para revisão

Fonte: PHB 2024 PT-BR, Apêndice C (p. 360–377 do livro) + tabela *Perícias* e tabela *Ações* do
capítulo 1 (p. 14–15). Validador: **0 erros, 0 avisos**. JSON Schema: todos os arquivos passam.

> Convenção de página: `pagina_livro` é o número impresso no rodapé; `pagina_pdf` é o número no
> leitor (sempre `pagina_livro + 4`). Ambos gravados em toda entidade.

## O que saiu

**Catálogos canônicos — 20 arquivos**

| catálogo | itens | página |
|---|---|---|
| pericias | **18** | 14 (cap. 1) |
| atributos | 6 | 377 |
| condicoes | **15** | 361–375 |
| tipos_de_dano | **13** | 376 |
| tipos_de_criatura | **14** | 376 |
| tamanhos | 6 | 375 |
| areas_de_efeito | 6 | 361 |
| atitudes | 3 | 363 |
| riscos | 5 | 362–374 |
| graus_de_cobertura | 3 | 364 |
| tipos_de_deslocamento | 5 | 366 |
| sentidos | 5 | 377 |
| tipos_de_descanso | 2 | 365–366 |
| custos_de_acao | 4 | 360 |
| categorias_de_arma | 2 | 361 |
| categorias_de_armadura | 4 | 377 |
| alvos / alvos_de_impedimento / tipos_de_efeito | 10 / 8 / 28 | catálogos de engine |

**Coleções**

- `condicoes.json` — 15 condições, cada uma com seus efeitos componíveis.
- `acoes.json` — 12 ações, com teste, perícias aplicáveis, efeitos e gatilhos de encerramento.

## Confere rápido (contagens que valem checar no livro)

- **18 perícias** · **15 condições** · **13 tipos de dano** · **14 tipos de criatura** · **12 ações**.
- Se alguma dessas contagens não bater com o livro, o erro é meu e o resto do lote fica suspeito.

## Precisa da sua decisão

### 1. Doze tipos de efeito novos (extensão do esquema → v1.1)

O esquema v1 não tinha como expressar o que as condições fazem. Adicionei:

`conceder_condicao` · `alterar_condicao` · `travar_deslocamento` · `restringir_movimento` ·
`falha_automatica` · `impedir` · `acerto_critico_automatico` · `remocao` · `conceder_ataque` ·
`efeito_narrativo`

Todos estão em `dados/catalogos/tipos_de_efeito.json` com os campos que aceitam, marcados
`"origem": "NOVO"`. Vale destacar dois:

- **`efeito_narrativo`** — para o que não tem mecânica (Inconsciente "Alheio", Petrificado "peso ×10
  e para de envelhecer"). O motor ignora, o app exibe. Serve para não perder regra por não caber no
  modelo. Se você preferir que isso simplesmente não entre no dataset, eu tiro.
- **`impedir`** — bloqueia ação, Ação Bônus, Reação, fala, Concentração e aproximação. É o que faz
  Incapacitado funcionar sem código especial.

### 2. Uma dúvida real (marcada `revisao.status = "duvida"`)

**Ação Ajudar.** A tabela do capítulo 1 (p. 15) resume Ajudar como *"ajudar no teste de atributo ou
na jogada de ataque de outra criatura **ou prestar primeiros socorros**"*. A entrada do glossário
(p. 360) descreve só as duas primeiras opções. Os primeiros socorros aparecem em outro lugar — na
regra de nocaute (p. 371): *"alguém use uma ação para prestar primeiros socorros, exigindo um teste
bem-sucedido de Sabedoria CD 10 (Medicina)"*. **Primeiros socorros é uma terceira opção da ação
Ajudar, ou uma ação genérica à parte?** Deixei fora até você decidir.

### 3. Perícias vieram do capítulo 1, não do Apêndice C

O glossário define *o que é* uma perícia, mas não lista as 18 — a tabela está no capítulo 1, p. 14.
Como nenhuma classe pode ser validada sem esse catálogo, extraí a tabela junto. É a única coisa
neste lote fora do Apêndice C. Se você preferir manter as fases estanques, eu movo para a Fase 2.

## Onde 2024 difere do que a memória de 2014 puxaria

Tudo abaixo saiu **do PDF**. A comparação com 2014 é apontamento meu para você conferir — não tratei
nada de 2014 como fonte.

- **Exaustão** é uma escala única e acumulativa: −2 em *todos* os Testes de D20 por nível e −1,5 m de
  Deslocamento por nível; morte no nível 6; Descanso Longo remove 1 nível. Não há tabela de efeitos
  diferentes por nível.
- **Esconder-se** é um teste de Destreza (Furtividade) **CD 15** fixo e, em caso de sucesso, concede
  a condição **Invisível** — o seu total no teste vira a CD para te encontrarem.
- **Invisível** é uma condição com regras próprias (Vantagem na Iniciativa, Vantagem/Desvantagem em
  ataques), e todos os benefícios de ataque caem contra quem consegue te ver de alguma forma.
- **Imobilizado** vem do Ataque Desarmado com CD fixa (8 + mod. de Força + BP), não de teste oposto;
  escapar é uma ação com Força (Atletismo) ou Destreza (Acrobacia).
- **Ataque Desarmado** tem três opções à escolha: Dano, Empurrar ou Imobilizar.
- **Influenciar**, **Analisar**, **Procurar** e **Usar Magia** são ações nomeadas do glossário.
- **Cobertura** tem três graus com bônus fixos: Parcial +2, Três Quartos +5, Total (não pode ser alvo).

## Arquivos

```
dados/catalogos/*.json    20 catálogos
dados/condicoes.json      15 condições
dados/acoes.json          12 ações
schema/*.schema.json      fonte, efeito, catalogo, condicoes, acoes
validar.py                validador (0 erros)
gerar*.py                 scripts que produziram os JSONs, para auditoria
```

Rode `python3 validar.py` na pasta para reproduzir a checagem.

## Próximo passo sugerido

Antes do capítulo 3 (Classes) faltam quatro catálogos fechados que as classes referenciam:
**idiomas** (cap. 2), **ferramentas** (cap. 6), **propriedades e maestrias de arma** (cap. 6) e
**escolas de magia** (cap. 7). São tabelas curtas. Sugiro um lote rápido só com elas — aí a Fase 2
começa com todas as chaves já existindo, e o validador consegue de fato garantir que nenhuma classe
aponte para nada inventado.
