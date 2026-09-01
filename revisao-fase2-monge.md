# Fase 2 — Monge (cap. 3, p. 159–165)

Validador: **0 erros, 0 avisos**. JSON Schema: todos os arquivos passam (3 schemas novos).

## O que saiu

| coleção | itens |
|---|---|
| `classes.json` | 1 classe (Monge), progressão completa de 1 a 20 |
| `caracteristicas.json` | **42** — 23 de classe, 19 de subclasse |
| `subclasses.json` | **4** — Mão Espalmada, Misericórdia, Sombras, Elementos |

**Contagens para conferir no livro:** 20 linhas de progressão · 4 subclasses · características de
subclasse nos níveis **3, 6, 11 e 17** · dado de vida **d8** · salvaguardas **Força e Destreza** ·
atributo primário **Destreza e Sabedoria**.

### A tabela virou dado

As três colunas viraram valores por nível, e as características leem delas em vez de repetir números:

- `dado_de_artes_marciais`: 1d6 (níveis 1–4) → 1d8 (5–10) → 1d10 (11–16) → 1d12 (17–20)
- `pontos_de_foco`: igual ao nível de Monge, a partir do 2
- `movimento_sem_armadura_m`: +3 (2–5) → +4,5 (6–9) → +6 (10–13) → +7,5 (14–17) → +9 (18–20)

Assim, Defletir Ataques não guarda "1d10 + DES + nível": guarda a fórmula em árvore. E o dano da
Torrente de Golpes puxa `dado:dado_de_artes_marciais`, que resolve pela linha do nível atual.

### O que o Monge provou sobre o esquema

- **CA substituta** funcionou como planejado: `ca_base` com `empilha: "substitui"` e condição
  `sem_armadura + sem_escudo`. Nenhum `if classe == monge` em lugar nenhum.
- **Pontos de Foco** são um `recurso_com_recarga` com `formula_maximo` lendo a coluna da tabela e
  recarga em Descanso Curto **ou** Longo.
- **Escolhas** apareceram cinco vezes (2 perícias, ferramenta, subclasse, talento de nível 4/8/12/16,
  talento épico de 19) e todas passaram pelo validador contra catálogos reais.
- **`melhorar_caracteristica`** resolveu o padrão mais chato do Monge: Foco Aprimorado (nível 10) não
  duplica Defesa Paciente / Passo do Vento / Torrente de Golpes — ele aponta para elas e altera. O
  mesmo vale para Defletir Energia (13) sobre Defletir Ataques, e para Toque de Médico (6) sobre Mão
  de Cura e Mão de Dolo.

## Precisa da sua decisão

### 1. Dezesseis tipos de efeito novos (esquema v1.2)

`dado_de_dano` · `substituir_atributo` · `restaurar_recurso` · `cura` · `reducao_de_dano` · `dano` ·
`escolher_tipo_de_dano` · `alterar_resultado_de_salvaguarda` · `remover_condicao` ·
`imunidade_a_risco` · `melhorar_caracteristica` · `pontos_de_vida_temporarios` · `rolar_novamente` ·
`teleporte` · `conceder_subclasse` · `aplicar_efeito_nomeado`

Todos registrados em `tipos_de_efeito.json` com `"origem": "NOVO_FASE2"` e a lista de campos. A
maioria vai se pagar nas outras classes (`dano`, `cura`, `reducao_de_dano`, `melhorar_caracteristica`
são universais). Se algum te parecer específico demais, me diga e eu reescrevo como
`efeito_narrativo`.

### 2. Três divergências do próprio livro (marcadas `duvida` no dado)

- **Nível 6:** a tabela (p. 160) chama de **"Ataques Potencializados"**; o título da característica
  (p. 161) diz **"Golpes Potencializados"**. Adotei o do corpo do texto.
- **Nível 10:** a tabela diz **"Autocura"**; o título diz **"Restauro Pessoal"**. Adotei o do corpo.
- **Passo da Sombra (6) vs. Passo da Sombra Aprimorado (11):** o nível 6 exige estar *"inteiramente
  em Meia-luz ou Escuridão"*; o nível 11 diz remover o requisito de *"iniciar ou encerrar seu turno"*
  em Meia-luz ou Escuridão. As duas redações não descrevem a mesma exigência. Copiei ambas
  literalmente sem tentar harmonizar.

Nos três casos o dado guarda as duas páginas. Você decide qual leitura vale na sua mesa.

### 3. Referências pendentes, declaradas como parciais

Para não deixar chave apontando para o vazio, criei dois catálogos **parciais**, cada um marcado
`"parcial": true` com nota explicando:

- `magias.json` — só Elementalismo, Escuridão e Ilusão Menor (as três que as subclasses citam).
- `talentos.json` — só Aumento no Valor de Atributo, Dádiva Épica e Dádiva do Ataque Irresistível.

E o **equipamento inicial do Monge** ficou com `revisao: duvida`: os ids `lanca`, `adaga` e
`kit_de_aventureiro` apontam para o catálogo de itens do capítulo 6, que ainda não existe. Está
registrado como referência pendente, não como erro silencioso.

## Validador: cinco checagens novas

Agora ele também verifica que:

1. a progressão cobre exatamente os níveis 1 a 20;
2. toda característica citada na progressão existe como entidade;
3. toda coluna usada numa linha foi declarada em `colunas_da_tabela`;
4. o nível declarado na característica bate com o nível em que a classe a concede;
5. `melhorar_caracteristica` aponta para uma característica (ou sub-característica) que existe — e
   nenhuma característica de subclasse fica órfã, sem estar listada na sua subclasse.

Também ensinei o validador a tratar o placeholder `{{escolhido}}`: dentro de
`efeito_por_item_escolhido` ele é obrigatório (o efeito precisa consumir o item escolhido) e a chave
real é validada contra o catálogo da escolha, não contra o efeito.

Teste negativo: plantei uma característica fantasma na progressão, uma subclasse inexistente, uma
coluna não declarada e um `melhorar_caracteristica` apontando para o nada. Pegou os quatro.

## Próximo passo

Sugiro o **Guerreiro** — é o oposto do Monge (armadura pesada, maestrias de arma, Estilo de Luta como
escolha, três subclasses com conjuração parcial no Cavaleiro Arcano) e vai testar a parte do esquema
que o Monge não encostou: `conceder_slot`, `desbloquear_magias` de verdade e treinamento com
armadura. Se preferir outra, é só dizer.
