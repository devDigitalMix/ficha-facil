# BACKLOG — para o agente, não para o João

Arquivo de trabalho. Denso de propósito: cada item tem evidência, comando de reprodução e ação.
Ao resolver, apagar o item e registrar em `PENDENCIAS.md`.

**Estado em 2026-09-02, depois da rodada de conserto:**
`validar.py` 0/0 · `checar_schema.py` 75/75 · seis testes negativos (18+11+16+18+26+4) ·
`reconstruir.py --comparar` = **58/58 geradores, 0 diferenças de conteúdo**.

---

## FECHADO nesta rodada (não reabrir sem motivo)

- **B1 — reprodutibilidade.** Era o item crítico: 37 de 51 geradores rodavam e 22 arquivos saíam
  diferentes. Agora 58/58 e zero divergência. O que foi feito:
  - `geradores/caminhos.py` centraliza raiz, PDF (por glob) e `intermediarios/`;
  - `geradores/extrair_texto.py` regera `cap6.txt`, `cap7.txt` e os offsets de página, que antes
    eram arquivos de scratch em `/tmp/claude-0/`;
  - os 29 geradores que ancoravam em `<script>/dados` foram reancorados na raiz;
  - `gerar_beneficios_do_terceiro_olho.py` criado — era o único arquivo de `dados/` sem gerador;
  - `reconstruir.py` declara a ORDEM (que importa: lote antigo fora de hora desfaz ajuste
    posterior) e compara em três níveis: idêntico / equivalente em ordem / conteúdo diferente;
  - `gerar_ajustes_historicos.py` + `ajustes_historicos.json` capturam as correções que foram
    feitas à mão nas fases 2 a 9 e nunca viraram código. As contagens de `listas_de_magia` não
    são copiadas: são **recalculadas** de `magias.json` e conferidas — o script falha se
    divergirem, e falhou de verdade na primeira execução (117 x 118), o que provou a checagem.
- **B2 — descrições.** 169 itens e 25 ferramentas ganharam `descricao_curta` derivada do próprio
  dado (`gerar_descricoes_de_equipamento.py`), marcada com `descricao_derivada: true`.
- **B3 — vocabulário morto.** `travar_atributo` e `teste_de_atributo_de_outro` agora declaram
  `reservado_para`, em vez de parecerem esquecimento.
- **B4 — colisão de id.** Documentada como convenção no `esquema-v1.md` §4.0, com o aviso que
  importa: nenhum código do motor deve indexar entidade por id sem o catálogo.
- **B5 — fonte.** 97 itens em 21 catálogos de opção herdaram a fonte do catálogo, marcados com
  `fonte_herdada: true`. Vocabulário continua sem, de propósito.
- **B7 — dois primitivos promovidos.** `emite_luz` (3 usos) virou o tipo `emitir_luz`. E
  `maestria_liberada` foi migrado para `conceder_maestria_de_arma`, que **já existia** e era usado
  pelo Guardião e pelo Paladino — havia duas maneiras de dizer a mesma coisa.
- **B8 — higiene.** `.gitignore` criado (`intermediarios/`, `.VSCodeCounter/`, `__pycache__`);
  `.VSCodeCounter` e o zip de 515 KB saíram da árvore (o zip segue no histórico, commit afae88b —
  só continha `fase1/druida.txt` a mais, e 131 arquivos já desatualizados); `README.md` escrito;
  `esquema-v0.md` marcado como histórico no cabeçalho.
- **B9 — buraco do validador.** `resolver_filtro` ignorava em silêncio toda chave de filtro que não
  sabia avaliar. Agora existe `FILTROS_DE_RUNTIME` (lista explícita do que o motor resolve) e
  chave fora dela é **erro**. `teste_negativo_auditoria.py` planta `categoira` e cobra.

---

## B6 — Decisões que são do João, não minhas

Não resolver sozinho. Perguntar quando houver ocasião:

1. `itens/aeronau` — "Aeronau" (p. 230) parece "Aeronave"; a legenda da p. 212 usa a palavra no
   mesmo sentido. O app mostra como impresso?
2. `classes/druida` — o Druida (p. 92) pede "Kit de Explorador"; o cap. 6 só tem "Kit de Explorador
   de Masmorras" (p. 226). Tratado como o mesmo.
3. `classes/bardo` — o livro não enumera os instrumentos musicais; a lista teria de vir de fora.
4. `beneficios_do_terceiro_olho/compreensao_superior` — "ler qualquer idioma" é o **último**
   `substituir_regra` do dataset. Vira primitivo (`compreender_idioma_escrito`)?
5. Releitura das 391 magias contra a paráfrase, uma a uma. `auditar_descricoes.py` só pega fato
   verificável por termo; inversão de sucesso/falha e erro de duração passam.
6. Regra da mesa pendente: +2 de Maestria em Arma no nível 20 do Guardião e do Paladino. Fora do
   dado até existir a camada de overrides (PENDENCIAS §8).

---

## B11 — Migrar os ajustes históricos para os geradores de origem

`ajustes_historicos.json` (87 KB) é dívida paga, não solução final. Ele aplica por cima o que
deveria estar no gerador que produziu a entidade. Enquanto existir, uma correção mora longe da
razão dela.

Ordem de ataque, do mais fácil ao mais caro:

1. **`magias.json` — 4 entradas espúrias** (`de_jallarzi`, `de_tasha`, `e_o_mal`, `o_mal`). São
   nomes que quebraram de linha e viraram magia. O certo é o parser não criá-las: consertar
   `parse_magias.py`/`parse_lista_magias.py` e tirar o `remover` do patch.
2. **`tipos_de_efeito` — campo `nome` em 28 tipos e 5 tipos não declarados.** Os cinco
   (`expandir_opcoes_de_escolha`, `alterar_alvos_da_magia`, `substituir_ataque_por_magia`,
   `alterar_quantidade_de_escolha`, `declara_campo_no_item`) eram **usados sem estar no catálogo**.
   Devem ser declarados pelo gerador que os introduziu (bardo, feiticeiro, primitivos).
3. **`alvos` e `alvos_de_impedimento` — 5 entradas** na mesma situação.
4. **`caracteristicas`/`classes`/`subclasses`** — o desdobramento do Golpe Brutal Fortalecido em
   `_13`/`_17`, o Prodígio Maior e correções pontuais. Cada uma está documentada num
   `revisao-fase*.md`; migrar para `gerar_barbaro*.py` e afins.
5. **`itens`, `ferramentas`, `manobras`, `talentos`, `efeitos_de_golpe_astuto`** — correções de
   valor pontuais.

Critério de pronto para cada passo: tirar o pedaço do patch, rodar
`python3 reconstruir.py /tmp/rb --comparar` e continuar em **0 diferenças de conteúdo**.

---

## B12 — Efeitos narrativos restantes

132 no dataset, todos marcados. A regra que vem funcionando: quando a mesma chave aparece 3+ vezes
com a mesma forma, vira primitivo. Depois da rodada de hoje, nenhuma chave passa de 2, exceto
`dadiva_de_faeria` (7), que é **estética por definição** e deve continuar narrativa.

Contagem atual: `dadiva_de_faeria` 7, `parcialmente_incorporeo` 2, `atributo_da_linhagem` 2,
`empurrao` 2, e uma cauda longa de 1. Reavaliar quando o próximo lote entrar.

Comando: agrupar por `.chave` todos os `efeito_narrativo` do dataset.

---

## B13 — Cobertura do validador: o que ainda não é conferido

- **`fonte_herdada`** marca item cuja página veio do cabeçalho do catálogo, não de conferência
  individual. Se algum dia a página do item importar (link do Compêndio para a página certa),
  esses 97 precisam ser conferidos um a um.
- **`descricao_derivada`** marca as 194 descrições compostas a partir do dado. Se o Compêndio
  quiser texto de verdade, é aqui que se troca — e o campo diz exatamente quais.
- O padrão que já se repetiu quatro vezes: **campo que não é efeito não é conferido por ninguém.**
  `efeito_por_item_escolhido` (fase 9), filtro booleano (fase 7), `alvo` em lista (fase 10),
  `magias_por_nivel` (fase 11). Ao criar campo novo que referencie id, escrever a checagem junto e
  plantar o defeito no teste negativo do mesmo lote.
- `pendente: true` dentro de um bloco `de` **desliga a regra 5** (filtro não pode resolver para
  vazio). Resta um uso legítimo: `forma_selvagem` apontando para `criaturas`, que é a pendência
  declarada. Se aparecer outro, conferir se ainda faz sentido.

---

## B10 — Nota de execução para o agente

- Rodar tudo a partir da **raiz do repositório**. A página do PDF é a do livro **+ 4**.
- `pip install -U "jsonschema>=4" --break-system-packages` — a do sistema é 3.2.0 e
  `checar_schema.py` falha em silêncio com ela.
- **Nunca** rodar um gerador antigo isolado contra `dados/`: a ordem importa. Usar `reconstruir.py`
  contra diretório temporário.
- Antes de qualquer lote novo: `python3 geradores/extrair_texto.py` (regenera `intermediarios/`,
  que não é versionado).
- Duas convenções de caminho ainda coexistem: os geradores novos usam caminho relativo ao CWD, os
  antigos resolvem a raiz por `__file__` via `caminhos.py`. Unificar no `caminhos.py` quando tocar
  em cada um.
