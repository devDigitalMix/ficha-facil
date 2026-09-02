# Ficha Fácil — Esquema de Dados v1 (aprovado, com decisões aplicadas)

Fonte: `DnD 5.5 - Livro do Jogador 2024 [PT] - Herois Anonimos.pdf` (393 páginas, edição 2024, PT-BR).

## Decisões travadas (Fase 0)

| # | Decisão | Escolha |
|---|---|---|
| 1 | Idioma de chaves e ids | **pt-br**, sem acento, minúsculo, snake_case |
| 2 | Fórmulas | **árvore** (arrays/objetos), nunca string a parsear |
| 3 | `escolha` | **efeito de primeira classe** (Jeito B), com catálogos fechados — ver §4 |
| 4 | Multiclasse | **fase posterior**; esquema não bloqueia, mas não extraio regra de multiclasse agora |
| 5 | Escopo | **jogador e classes**. Ap. A (Multiverso) e Ap. B (Criaturas) fora |
| 6 | Ordem | **Ap. C (Glossário de Regras) primeiro**, depois Cap. 3 (Classes) |

---

## 1. Princípios

1. **Tudo é efeito componível.** Nenhuma entidade conhece as outras. O Monge carrega o efeito que
   troca a fórmula de CA; o Druida carrega o efeito que desbloqueia sua lista de magias. O motor só
   sabe aplicar efeitos — nunca nomes de classe.
2. **Dado > prosa.** Cada regra vira `efeito` + `condicao` + `empilhamento`. Sabor vira uma linha
   parafraseada em `descricao_curta`.
3. **Rastreabilidade.** Toda entidade tem `fonte: { capitulo, pagina }`.
4. **Incerteza explícita.** `revisao: { status: "ok" | "duvida" | "conflito_2014", notas }`.
5. **Sobrescrevível.** `overrides` da mesa aplicados por último, sem tocar no dado original.
6. **Chave inexistente é erro de build.** Ver §4.

---

## 2. Vocabulário de referência

- Atributos: `FOR DES CON INT SAB CAR`.
- Caminhos usados em fórmulas e condições:
  `mod:DES` · `attr:FOR` · `prof` · `nivel` · `nivel_classe:monge` ·
  `recurso:surto_de_acao.atual` · `flag:sem_armadura` · `flag:sem_escudo`
- Fórmula = array de termos somados `["10","mod:DES","mod:SAB"]`, ou objeto
  `{ "op": "max" | "min" | "mult" | "div_arred_baixo", "args": [...] }` quando não for soma.

---

## 3. Catálogo de tipos de efeito

| tipo | payload | uso típico |
|---|---|---|
| `modificador` | `alvo`, `valor`, `empilha` | +2 em Percepção, +1 CA |
| `ca_base` | `formula`, `permite_escudo` | Defesa sem Armadura (Monge, Bárbaro) |
| `travar_atributo` | `atributo`, `valor_minimo` | itens que fixam FOR 19 |
| `conceder_proficiencia` | `categoria`, `chave`, `nivel_dominio` (`proficiente`/`especialista`) | classes, antecedentes |
| `conceder_talento` | `talento_id` | Antecedente 2024, Melhoria de Atributo |
| `aumento_atributo` | `distribuicao`, `limite` | Antecedente 2024 |
| `conceder_slot` | `tabela_progressao_id` ou `{nivel_magia, quantidade}` | conjuradores |
| `desbloquear_magias` | `lista_id`, `modo` (`sempre_preparada`/`disponivel_para_preparar`/`conhecida`) | listas por classe e subclasse |
| `preparar_magias` | `formula_quantidade`, `atributo_conjuracao` | preparação 2024 |
| `recurso_com_recarga` | `id`, `formula_maximo`, `recarga`, `consumo` | Fúria, Ki, Inspiração |
| `conceder_acao` | `id`, `custo` (`acao`/`bonus`/`reacao`/`livre`), `efeitos[]` | Surto de Ação |
| `dado_de_impacto` | `formula_dado`, `escalonamento_por_nivel` | Furtivo, Golpe Certeiro |
| `alterar_dano` | `tipo_dano`, `operacao` (`resistencia`/`imunidade`/`vulnerabilidade`/`bonus`) | traços de espécie |
| `conceder_sentido` | `sentido`, `alcance` | Visão no Escuro |
| `conceder_velocidade` | `tipo`, `formula` | espécies, Movimento sem Armadura |
| `vantagem` | `alvo`, `tipo` (`vantagem`/`desvantagem`) | Sortudo, Ancestral Feérico |
| `escolha` | ver §4 | "escolha 2 perícias entre…" |
| `substituir_regra` | `regra_id`, `novo_valor` | último recurso; sempre `revisao.status = "duvida"` |

`empilha`: `soma` · `maior_valor` · `unico` · `substitui`.
`ativacao`: `passiva` · `ativa` · `reativa` · `escolha_do_jogador`.
`condicao` é árvore booleana: `{"todas":[…]}` · `{"alguma":[…]}` · `{"nao":…}`.

---

## 4. `escolha` e os catálogos canônicos

Sua condição: **os itens disponíveis têm que estar certinhos.** Isso vira regra estrutural, não
boa intenção. Três mecanismos:

### 4.0 Ids são escopados por catálogo

Um id é único **dentro do seu catálogo**, não no dataset inteiro. Duas entidades diferentes podem
ter o mesmo id em catálogos diferentes, e isso é comum: `protetor` é uma Ordem Divina e também uma
Ordem Primal; `anao`, `orc` e `pequenino` são espécies e também idiomas; `escudo` é categoria de
armadura e item.

O caso que mais confunde é o das opções de Canalizar Divindade do Paladino. `arma_sagrada`,
`atleta_inigualavel`, `destruicao_inspiradora`, `voto_de_inimizade`, `a_ira_da_natureza` e
`repudiar_inimigos` existem ao mesmo tempo em duas coleções, com papéis distintos:

- em `caracteristicas`, é o que a classe ou a subclasse **concede** ao subir de nível;
- em `efeitos_de_canalizar_divindade`, é o **efeito** que o jogador escolhe ao gastar um uso.

São entidades diferentes com o mesmo nome no livro, e por isso o mesmo id. Toda referência a
opção de catálogo carrega o catálogo junto (`aplicar_efeito_nomeado` tem `catalogo` e `chave`;
`expandir_opcoes_de_escolha` também), então a resolução nunca é por id global. **Nenhum código do
motor deve indexar entidades por id sem o catálogo.**

### 4.1 Catálogos fechados

Enumerações extraídas do PDF **antes** de qualquer coisa que as referencie. Cada uma vira um
arquivo próprio com a lista completa e a página de origem:

`pericias` · `atributos` · `condicoes` · `tipos_de_dano` · `escolas_de_magia` · `idiomas` ·
`categorias_de_arma` · `propriedades_de_arma` · `maestrias_de_arma` · `categorias_de_armadura` ·
`ferramentas` · `tipos_de_criatura` · `tamanhos` · `sentidos` · `custos_de_acao` · `tipos_de_descanso`

Quase todos saem do **Apêndice C (Glossário de Regras)** — que é exatamente por isso que ele é a
Fase 1. Cada catálogo é entregue com contagem explícita ("18 perícias, p. XXX") pra você bater o olho.

### 4.2 Forma da `escolha`

```json
{
  "id": "monge_pericias_iniciais",
  "tipo": "escolha",
  "rotulo": "Escolha 2 perícias",
  "quantidade": 2,
  "de": {
    "catalogo": "pericias",
    "chaves": ["acrobacia","atletismo","historia","intuicao","religiao","furtividade"]
  },
  "momento": "criacao",
  "permite_repetir": false,
  "efeito_por_item_escolhido": {
    "tipo": "conceder_proficiencia",
    "categoria": "pericia",
    "chave": "{{escolhido}}",
    "nivel_dominio": "proficiente"
  },
  "fonte": { "capitulo": 3, "pagina": 0 }
}
```

`de` tem duas formas, nunca as duas ao mesmo tempo:

- **Lista explícita** — `catalogo` + `chaves[]`. Usada quando o livro enumera as opções.
- **Filtro** — `catalogo` + `filtro`, ex. `{"catalogo":"magias","filtro":{"nivel":0,"lista":"druida"}}`.
  Usada quando o livro diz "qualquer truque de druida". O filtro é resolvido em tempo de execução
  contra o catálogo, então nunca desatualiza.

Escolhas aninhadas funcionam sem tratamento especial: o Antecedente concede um talento, e o talento
carrega a própria `escolha` dentro dele. O motor só re-entra na pilha.

### 4.3 Validador (roda antes de eu te entregar qualquer lote)

Um script `validar.py` que quebra o build se:

1. Alguma `chave` em `de.chaves` não existir no catálogo declarado.
2. Algum `catalogo` referenciado não existir.
3. `quantidade` for maior que o número de opções disponíveis.
4. Algum `efeito_por_item_escolhido` produzir um efeito de tipo desconhecido.
5. Alguma `filtro` retornar lista vazia contra o catálogo atual.
6. Algum `id` estiver duplicado dentro de uma coleção.
7. Alguma entidade estiver sem `fonte.pagina`.

Todo lote vem acompanhado da saída do validador. Se ele não passar, o lote não te chega.

---

## 5. Entidades

### 5.1 Espécie
`id`, `nome`, `tipo_criatura`, `tamanho[]`, `velocidade`, `descricao_curta`, `tracos[]`,
`linhagens[]`, `fonte`, `revisao`.
**2024:** espécie não concede aumento de atributo — isso migrou para o Antecedente.

### 5.2 Antecedente
`id`, `nome`, `aumento_atributo { atributos[], modo: "2_e_1" | "1_1_1" }`, `talento_origem`,
`efeitos[]` (proficiências), `equipamento_inicial { opcoes[] }`.

### 5.3 Classe
`id`, `nome`, `dado_de_vida`, `salvaguardas_primarias[]`, `atributo_primario[]`,
`proficiencias_iniciais[]`, `equipamento_inicial`,
`conjuracao: null | { tipo: "pleno"|"meio"|"terco"|"pacto", atributo, ritual, foco }`,
`progressao[] { nivel, caracteristicas[], colunas{} }`, `nivel_subclasse`, `subclasses[]`.

### 5.4 CaracterísticaDeClasse (entidade própria, reusada por classe e subclasse)
`id`, `nome`, `classe`, `subclasse?`, `nivel`, `descricao_curta`, `efeitos[]`,
`melhorias_por_nivel { "<nivel>": { …campos sobrescritos… } }`.

### 5.5 Talento
`id`, `nome`, `categoria` (`origem`/`geral`/`estilo_de_luta`/`epico`),
`pre_requisitos[]`, `repetivel`, `efeitos[]`.

### 5.6 Magia
`id`, `nome`, `nivel`, `escola`, `tempo_conjuracao`, `alcance`, `componentes {V,S,M,consumido,custo_po}`,
`duracao`, `ritual`, `concentracao`, `area`, `efeitos[]`, `escalonamento`, `listas[]` (índice
invertido **gerado**, não fonte da verdade — a verdade é o `desbloquear_magias` de cada classe).

### 5.7 Item
`id`, `nome`, `categoria`, `custo_po`, `peso_kg`,
`arma { tipo, grupo, dano, tipo_dano, propriedades[], versatil_dano, maestria }`,
`armadura { categoria, ca_base, mod_des_max, for_minima, furtividade_desvantagem }`, `efeitos[]`.

### 5.8 Personagem (estado)
`escolhas { especie, linhagem, antecedente, classes[], atributos_base, escolhas_resolvidas{} }`,
`estado { pv_atual, pv_temporarios, slots_gastos, recursos, magias_preparadas, inventario, condicoes }`,
`overrides[]`.

Nada derivado é armazenado. CA, PV máximo, bônus de ataque e perícias saem da resolução da pilha.

---

## 6. Contrato do motor

1. Coleta efeitos: espécie → antecedente → classes/subclasses (até o nível) → talentos → itens
   equipados → condições ativas → overrides.
2. Filtra por `condicao` contra o estado atual.
3. Agrupa por `alvo`, aplica `empilha`.
4. Devolve a ficha derivada **+ log de proveniência** por número: `CA 17 = 10 + 3 (DES) + 4 (SAB)`.

---

## 7. Entrega

Um JSON por coleção + um JSON Schema por coleção + `revisao.md` por lote (o que extraí, o que ficou
em dúvida, o que difere de 2014) + saída do `validar.py`.

Ordem de trabalho acordada:

1. **Fase 1 — Ap. C: Glossário de Regras** → catálogos canônicos + condições + ações.
2. **Fase 2 — Cap. 3: Classes**, uma classe por lote.
3. Depois: Espécies e Antecedentes (Cap. 4), Talentos (Cap. 5), Equipamento (Cap. 6), Magias (Cap. 7).
