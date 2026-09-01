# Ficha Fácil — Esquema de Dados v0 (proposta para aprovação)

Fonte: `DnD 5.5 - Livro do Jogador 2024 [PT] - Herois Anonimos.pdf` (393 páginas, edição 2024).
Estrutura confirmada no sumário do PDF: Cap. 1 Jogando o Jogo · Cap. 2 Criação de Personagens ·
Cap. 3 Classes · Cap. 4 Origens (Espécies/Antecedentes) · Cap. 5 Talentos · Cap. 6 Equipamento ·
Cap. 7 Magias · Ap. A Multiverso · Ap. B Criaturas · Ap. C Glossário de Regras.

> Nada foi extraído ainda. Este documento define **como** os dados serão modelados.

---

## 1. Princípios

1. **Tudo é efeito componível.** Nenhuma entidade "sabe" das outras. O Monge carrega o efeito que
   troca a fórmula de CA; o Druida carrega o efeito que desbloqueia a lista de magias de druida.
   O motor só sabe aplicar efeitos, nunca nomes de classe.
2. **Dado > prosa.** Cada regra vira `efeito` + `condicao` + `empilhamento`. Texto de sabor é
   parafraseado em uma linha (`descricao_curta`), nunca copiado em bloco.
3. **Rastreabilidade.** Toda entidade tem `fonte: { livro, capitulo, pagina }` para eu conferir.
4. **Incerteza é explícita.** Campo `revisao: { status, notas }` — nada entra como certo por palpite.
5. **Sobrescrevível.** Toda entidade aceita `override` da mesa sem editar o dado original.

---

## 2. Identificadores e vocabulário

- `id`: slug estável, minúsculo, sem acento — `monge`, `defesa_sem_armadura`, `bola_de_fogo`.
- Atributos: `FOR DES CON INT SAB CAR`.
- Referências dentro de fórmulas e condições usam **caminhos**:
  - `mod:DES` — modificador de atributo
  - `attr:FOR` — valor bruto
  - `prof` — bônus de proficiência
  - `nivel` / `nivel_classe:monge`
  - `recurso:surto_de_acao.atual`
  - `flag:sem_armadura`, `flag:sem_escudo`

Fórmulas são **arrays de termos somados** (`["10","mod:DES","mod:SAB"]`) ou objetos
`{ "op": "max|min|mult", "args": [...] }` quando precisa de mais que soma. Sem expressão em string
para o app parsear — o dado já vem em árvore.

---

## 3. Catálogo de tipos de efeito (o "instruction set" do motor)

| tipo | payload | uso típico |
|---|---|---|
| `modificador` | `alvo`, `valor`, `empilha` | +2 em testes de Percepção, +1 CA |
| `ca_base` | `formula`, `permite_escudo` | Defesa sem Armadura (Monge, Bárbaro) |
| `travar_atributo` | `atributo`, `valor_minimo` | itens que fixam FOR 19 |
| `conceder_proficiencia` | `categoria` (pericia/arma/armadura/ferramenta/salvaguarda/idioma), `chaves`, `nivel_dominio` (`proficiente`/`especialista`) | quase toda classe e antecedente |
| `conceder_talento` | `talento_id` \| `escolha` | Antecedente 2024, ASI de classe |
| `aumento_atributo` | `distribuicao` (`{FOR:2, CON:1}` ou escolha guiada), `limite` | Antecedente 2024, Melhoria de Atributo |
| `conceder_slot` | `tabela_progressao_id` ou `{nivel_magia, quantidade}` | conjuradores plenos/parciais/pactos |
| `desbloquear_magias` | `lista_id`, `modo` (`sempre_preparada`/`disponivel_para_preparar`/`conhecida`) | listas por classe, magias de subclasse |
| `preparar_magias` | `formula_quantidade`, `atributo_conjuracao` | preparação 2024 |
| `recurso_com_recarga` | `id`, `formula_maximo`, `recarga` (`descanso_curto`/`longo`/`por_turno`), `consumo` | Fúria, Inspiração Bárdica, Ki |
| `conceder_acao` | `id`, `custo` (`acao`/`bonus`/`reacao`/`livre`), `efeitos[]` | Surto de Ação, Ataque Desarmado |
| `dado_de_impacto` | `formula_dado`, `escalonamento_por_nivel` | Golpe Certeiro, Furtivo |
| `alterar_dano` | `tipo`, `operacao` (`resistencia`/`imunidade`/`vulnerabilidade`/`bonus`) | traços de espécie |
| `conceder_sentido` | `sentido`, `alcance` | Visão no Escuro |
| `conceder_velocidade` | `tipo` (`caminhada`/`voo`/`natacao`/`escalada`), `formula` | espécies, Movimento sem Armadura |
| `vantagem` | `alvo`, `tipo` (`vantagem`/`desvantagem`) | Sortudo, Ancestral Feérico |
| `substituir_regra` | `regra_id`, `novo_valor` | exceções raras (última escolha, sempre marcada para revisão) |
| `escolha` | `de` (lista/filtro), `quantidade`, `momento` | "escolha 2 perícias entre..." |

`empilha`: `soma` · `maior_valor` · `unico` (não acumula com mesma fonte) · `substitui`.

---

## 4. Entidades

### 4.1 Efeito (embutido em todas as demais)

```json
{
  "id": "monge_defesa_sem_armadura",
  "tipo": "ca_base",
  "formula": ["10", "mod:DES", "mod:SAB"],
  "condicao": { "todas": ["flag:sem_armadura", "flag:sem_escudo"] },
  "empilha": "substitui",
  "ativacao": "passiva",
  "fonte": { "capitulo": 3, "pagina": 0 }
}
```

`condicao` é uma árvore booleana: `{ "todas": [...] }`, `{ "alguma": [...] }`, `{ "nao": ... }`.
`ativacao`: `passiva` · `ativa` (gasta ação/recurso) · `reativa` · `escolha_do_jogador`.

### 4.2 Espécie (ex-"Raça")

```json
{
  "id": "elfo", "nome": "Elfo", "tipo_criatura": "Humanoide",
  "tamanho": ["Medio"], "velocidade": 9,
  "descricao_curta": "...",
  "tracos": [ { "id": "...", "nome": "...", "descricao_curta": "...", "efeitos": [ ... ] } ],
  "linhagens": [ { "id": "alto_elfo", "nome": "...", "efeitos": [...] } ],
  "fonte": {...}, "revisao": {...}
}
```
Nota 2024: espécie **não** concede aumento de atributo — isso migrou para o Antecedente.

### 4.3 Antecedente (Background 2024)

```json
{
  "id": "acolito", "nome": "Acólito",
  "aumento_atributo": { "atributos": ["INT","SAB","CAR"], "modo": "2_e_1_ou_1_1_1" },
  "talento_origem": "iniciado_em_magia",
  "efeitos": [ conceder_proficiencia (2 perícias fixas + 1 ferramenta), ... ],
  "equipamento_inicial": { "opcoes": [ { "itens": [...] }, { "moedas": 50 } ] }
}
```

### 4.4 Classe / Subclasse

```json
{
  "id": "monge", "nome": "Monge",
  "dado_de_vida": 8,
  "salvaguardas_primarias": ["FOR","DES"],
  "atributo_primario": ["DES","SAB"],
  "proficiencias_iniciais": [ efeitos conceder_proficiencia ],
  "equipamento_inicial": {...},
  "conjuracao": null | { "tipo": "pleno|meio|terco|pacto", "atributo": "SAB", "ritual": bool, "foco": "..." },
  "progressao": [
    { "nivel": 1, "caracteristicas": ["defesa_sem_armadura","artes_marciais"],
      "colunas": { "dado_de_artes_marciais": "1d6", "pontos_de_foco": 0 } }
  ],
  "nivel_subclasse": 3,
  "subclasses": ["guerreiro_da_mao_aberta", ...]
}
```

`CaracteristicaDeClasse` é entidade própria (reutilizável entre classe e subclasse):

```json
{ "id": "surto_de_acao", "nome": "Surto de Ação", "classe": "guerreiro",
  "nivel": 2, "descricao_curta": "...",
  "efeitos": [ {"tipo":"recurso_com_recarga", ...}, {"tipo":"conceder_acao", ...} ],
  "melhorias_por_nivel": { "17": { "formula_maximo": ["2"] } } }
```

### 4.5 Talento

```json
{ "id": "atacante_pesado", "nome": "...", "categoria": "origem|geral|estilo_de_luta|epico",
  "pre_requisitos": [ { "tipo": "atributo_minimo", "atributo": "FOR", "valor": 13 } ],
  "repetivel": false, "efeitos": [...] }
```

### 4.6 Magia

```json
{ "id": "bola_de_fogo", "nome": "Bola de Fogo", "nivel": 3, "escola": "Evocação",
  "tempo_conjuracao": { "custo": "acao", "quantidade": 1 },
  "alcance": { "tipo": "distancia", "valor": 45, "unidade": "m" },
  "componentes": { "V": true, "S": true, "M": "uma bolinha de guano..." , "consumido": false, "custo_po": 0 },
  "duracao": { "tipo": "instantanea|concentracao|tempo", "valor": null },
  "ritual": false, "concentracao": false,
  "area": { "forma": "esfera", "raio": 6 },
  "efeitos": [ { "tipo": "dano", "formula_dado": "8d6", "tipo_dano": "fogo",
                 "salvaguarda": { "atributo": "DES", "sucesso": "metade" } } ],
  "escalonamento": { "por_slot_acima": { "formula_dado": "+1d6" } },
  "listas": ["mago","feiticeiro"] }
```
As listas de classe **não** ficam aqui como verdade: cada classe carrega `desbloquear_magias`.
O campo `listas` existe só como índice invertido gerado, para busca rápida.

### 4.7 Item / Equipamento

```json
{ "id": "espada_longa", "nome": "Espada Longa", "categoria": "arma",
  "custo_po": 15, "peso_kg": 1.5,
  "arma": { "tipo": "corpo_a_corpo", "grupo": "marcial",
            "dano": "1d8", "tipo_dano": "cortante",
            "propriedades": ["versatil"], "versatil_dano": "1d10",
            "maestria": "empurrar" },
  "armadura": null, "efeitos": [] }
```
`maestria` é regra nova de 2024 — modelada como efeito nomeado, não como texto.

### 4.8 Personagem (estado do jogador)

```json
{
  "id": "...", "nome": "...",
  "escolhas": { "especie": "elfo", "linhagem": "alto_elfo", "antecedente": "acolito",
                "classes": [ { "id": "monge", "nivel": 5, "subclasse": "..." } ],
                "atributos_base": {...}, "escolhas_resolvidas": { "<id_escolha>": [...] } },
  "estado": { "pv_atual": 0, "pv_temporarios": 0, "slots_gastos": {}, "recursos": {},
              "magias_preparadas": [], "inventario": [], "condicoes": [] },
  "overrides": [ { "alvo": "ca_total", "valor": 18, "motivo": "regra da mesa" } ]
}
```
Tudo que é derivado (CA, PV máximo, bônus de ataque, perícias) **não é armazenado**: é calculado
resolvendo a pilha de efeitos, com `overrides` aplicados por último.

---

## 5. Como o motor resolve (contrato)

1. Coleta efeitos de: espécie → antecedente → classes/subclasses (até o nível) → talentos → itens
   equipados → condições ativas → overrides.
2. Filtra por `condicao` contra o estado atual.
3. Agrupa por `alvo` e aplica `empilha`.
4. Retorna a ficha derivada + um *log* de proveniência por número ("CA 17 = 10 + 3 DES + 4 SAB").

O log de proveniência é o que me deixa auditar o dado sem abrir o PDF.

---

## 6. Formato de entrega

- Um arquivo JSON por coleção: `especies.json`, `classes.json`, `caracteristicas.json`,
  `antecedentes.json`, `talentos.json`, `magias.json`, `itens.json`, `glossario.json`.
- Um `schema/*.schema.json` (JSON Schema) por coleção, para validar antes de eu revisar.
- Cada lote vem com um `revisao.md` curto: o que extraí, o que ficou incerto, o que mudou de 2014
  para 2024 e eu preciso confirmar.

---

## 7. Decisões que preciso que você aprove

1. **Idioma das chaves e dos ids**: proposta acima usa português (`ca_base`, `mod:DES`,
   `especie`). Alternativa: chaves em inglês, valores em português. Qual prefere?
2. **Fórmulas como árvore** (arrays/objetos) em vez de string tipo `"10 + DES + SAB"` — confirma?
3. **`escolha` como efeito de primeira classe** (o app renderiza o seletor a partir do dado) — ok?
4. **Multiclasse**: incluir desde já no esquema (regras de slot combinado) ou marcar como fase
   posterior?
5. **Ap. B (criaturas)** e **Ap. A (multiverso)**: fora do escopo por enquanto? Presumo que sim.
6. **Ap. C (Glossário de Regras)**: sugiro extrair *primeiro*, antes das classes — é onde 2024
   define condições, ações e termos que todo o resto referencia. Concorda com essa ordem?
