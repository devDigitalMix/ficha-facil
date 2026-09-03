# Plano da Fase A — o mínimo jogável

Escrito em 2026-09-03, a partir do escopo que o João descreveu. O `PLANO-APP.md` diz **o que**
o produto é; este arquivo diz **o que fazer nos próximos dias**, em que ordem, e o que cada parte
depende. O `PENDENCIAS.md` cuida do dataset e o `PLANO-MOTOR.md`, do motor e dos endpoints.

## O escopo, como o João descreveu

1. **Múltiplos personagens por usuário**, salvos no banco, com status ativo · reserva · morto ·
   aposentado.
2. **Compêndio** pesquisável por nome e por filtros, sobre todo o dataset.
3. **Administração da ficha em sessão**: inventário, vida, magias, modificadores e CA, alteráveis
   conforme o jogador age.
4. **Custo de conjuração**: ao selecionar a magia, o app gasta o que tem de ser gasto — e sabe
   quando o foco cobre o componente material, quando o material é obrigatório, e quando uma
   característica de classe deixa conjurar **sem custo nenhum** (o exemplo do João: as Invocações
   Místicas do Bruxo).
5. **Histórico por personagem** de vida, magia e recursos.

## As três decisões tomadas em 2026-09-03

| decisão | escolha | consequência |
|---|---|---|
| Onde mora o compêndio | **Continua em `dados/`**, com busca no backend | Mongo fica só para contas e personagens. `reconstruir.py --comparar` continua provando que o gerador é a fonte — não existe segunda cópia do dataset para divergir. |
| Contas | **E-mail e senha, próprio** | Coleção `usuarios` com hash de senha e sessão por token. Nada de OAuth por ora. |
| Histórico | **Só o essencial**: vida, magia e recursos | Inventário e equipamento mudam sem virar evento. |

**Uma correção que veio junto da terceira decisão.** O João citou, como exemplo de histórico, mostrar
que a CA "vem 2 da armadura, 2 do escudo e 2 de destreza além do 10 padrão". Isso **não é
histórico** — é **proveniência**, e o motor já a produz viva, a cada montagem da ficha. Hoje, para a
Clériga de ouro:

```json
"classe_de_armadura": { "valor": 16, "parcelas": [
  { "rotulo": "13", "valor": 13 },
  { "rotulo": "DES", "valor": 1 },
  { "rotulo": "2", "valor": 2 },
  { "rotulo": "cálculo de base usado", "valor": "ca_cota_de_malha_parcial" },
  { "rotulo": "bonus_do_escudo", "valor": 2 } ] }
```

O número está certo e a decomposição está lá. **O que falta é o rótulo ser apresentável**: "13" e
"2" não dizem de onde vieram, e `bonus_do_escudo` é id, não frase. Está na lista de tarefas abaixo
como trabalho do motor, não do histórico. A diferença importa: proveniência é do **agora** e se
recalcula; histórico é do **passado** e se grava.

---

## O que já está pronto

Inventário honesto, com o que sustenta cada linha.

| item do escopo | estado | onde |
|---|---|---|
| Status do personagem | **pronto** | `backend/src/personagem.ts` já declara `ativo · reserva · morto · aposentado`. |
| Guardar personagem | **pronto, menos o banco** | `Armazem` é interface, com `ArmazemEmArquivos` e `ArmazemNaMemoria`. Trocar por Mongo é implementar a interface. |
| Estado de sessão | **pronto** | `EstadoDeJogo` já tem PV atuais, temporários, `espacos_gastos`, `recursos_gastos`, condições e concentração. |
| Espaços por círculo | **pronto** | `ficha.conjuracao.espacos`, lido de `progressao[].colunas.espacos_N`. |
| CA, ataques, equipamento | **pronto** | Fase 18. A armadura concorre, o escudo soma, o Ataque Desarmado entra sempre. |
| Compêndio servido | **pronto** | `backend/src/compendio.ts`, com ETag pela versão do dataset. |
| **Componentes de magia** | **pronto, e bom** | Das 391 magias: 214 com componente Material, das quais **148 substituíveis por foco ou bolsa** e **66 com custo em PO**. Cada uma declara `material_descricao`, `material_consumido`, `substituivel_por_foco_ou_bolsa`, `material_custo_po` e `material_custo_minimo`. |
| Focos de conjuração | **pronto** | 10 itens de categoria `foco_de_conjuracao`, mais `bolsa_de_componentes`. |
| Ritual | **pronto** | 31 magias com `ritual: true`. |

**O item 4 do escopo — o custo do componente material — está inteiramente sustentado pelo dado.**
O app consegue decidir sozinho, hoje, se a conjuração sai de graça pelo foco, se exige o material, e
quanto custa.

---

## O achado: `conjurar_sem_espaco` faz três trabalhos diferentes

Esta é a única parte do escopo que **exige mexer no dataset**, e o motivo é interessante.

O conceito existe: **43 ocorrências** de `conjurar_sem_espaco`, sendo **12 em
`invocacoes_misticas.json`** — exatamente o caso que o João levantou (Máscara das Muitas Faces →
Disfarçar-se à vontade; Uno com as Sombras → Invisibilidade; Passo Ascendente → Levitação). O dado
**sabe**. O que ele não faz é dizer isso de um jeito que um programa execute.

Lendo as 43 uma a uma, o mesmo tipo cobre três mecânicas que não são a mesma coisa:

1. **Conjurar de graça.** Nenhum custo; o limite é a frequência. É o caso das Invocações Místicas.
2. **Conjurar pagando outra moeda.** Bênção do Deus da Guerra gasta **Canalizar Divindade**;
   Feitiçaria Psiônica gasta **Pontos de Feitiçaria** iguais ao círculo; Companheiro Selvagem aceita
   **espaço de magia OU um uso de Forma Selvagem**. Não é de graça — é outra moeda.
3. **Devolver o espaço depois de gastá-lo.** Dádiva da Recordação de Magia gasta o espaço
   normalmente e joga 1d4; se der igual ao círculo, o espaço volta. Isso já é um tipo separado
   (`nao_gastar_espaco_de_magia`), e **deve continuar separado** — é reembolso, não custo.

Sobre isso, a escrita está irregular de um jeito que impede execução:

| defeito | tamanho |
|---|---|
| `frequencia` ausente | **18 de 43** — o app não sabe se é à vontade ou uma vez por descanso |
| Quatro grafias para três conceitos | `a_vontade` (14) e `sem_limite` (1) são o mesmo; `uma_vez_por_descanso` (1), `uma_vez_por_descanso_longo` (7) e `..._para_cada_magia` (2) |
| `magia` (35) × `magias` (5) | mesma coisa, dois nomes |
| `recarga` ausente | **35 de 43**, inclusive onde a frequência diz "uma vez por descanso" |
| Custo dito de quatro maneiras | `consome_recurso` (11), `custo` (5), `custo_em_recurso` (1), `custo_alternativo` (1) |
| "Sem componente material" de duas maneiras | `sem_componentes_materiais` (2), `sem_componentes` (1) |

É o **mesmo defeito da fase 13** — a mesma regra escrita de formas diferentes em lugares diferentes
—, e o conserto é o mesmo: uma forma declarada, fechada, e o validador cobrando.

**A ressalva que a fase 13 ensinou: não fundir por nome.** `conjurar_sem_espaco` e
`nao_gastar_espaco_de_magia` *parecem* a mesma regra e não são. A normalização junta as grafias do
mesmo conceito e **mantém separado** o que é mecânica diferente — com o custo declarado
explicitamente, onde "nada" é uma das moedas, e não a ausência de campo.

### Forma proposta

```jsonc
{
  "tipo": "conjurar_sem_espaco",
  "magias": ["disfarcar_se"],          // sempre lista, mesmo com uma
  "custo": { "moeda": "nada" },        // nada · recurso · espaco_de_magia · pontos
  "frequencia": "a_vontade",           // lista fechada, sempre presente
  "recarga": [],                       // vazio quando a frequência não pede
  "dispensa_componentes": []           // [] · ["M"] · ["V","S","M"]
}
```

Com `custo.moeda` valendo também `{ "moeda": "recurso", "recurso_id": "canalizar_divindade" }`, e
`custo_alternativo` virando uma **lista de custos aceitos** em vez de um campo à parte. Nenhuma
regra nova: é a mesma informação, dita de um jeito só.

---

## Modelo de dados no Mongo Atlas

Três coleções. O compêndio **não entra** — fica em `dados/`.

### `usuarios`

```jsonc
{ "_id": ObjectId, "email": "joao@…",   // índice único, guardado em minúsculas
  "senha_hash": "scrypt$N$r$p$sal$hash", // nunca a senha
  "criado_em": ISODate, "ultimo_login": ISODate }
```

Índice único em `email`. O hash é **scrypt do `node:crypto`** — está na biblioteca padrão, o que
mantém a promessa de zero dependências do motor e do backend.

### `personagens`

O documento é o `Personagem` que o backend já tem, mais dois campos:

```jsonc
{ "_id": ObjectId,
  "usuario_id": ObjectId,               // NOVO — dono
  "nome": "Kaida", "status": "ativo",
  "construcao": { … }, "estado": { … }, // nunca a ficha: ela se recalcula
  "versao_do_dataset": "…",
  "imagem": { "chave": "personagens/<id>/<uuid>.webp",  // NOVO — só a chave do S3
              "atualizada_em": ISODate },
  "criado_em": ISODate, "ultimo_acesso": ISODate }
```

Índice `{ usuario_id: 1, ultimo_acesso: -1 }` — é exatamente a consulta de "Meus personagens".

**A decisão que não muda:** o documento guarda **construção e estado, nunca a ficha**. É o que faz o
dataset valer a pena — corrigir uma regra em `dados/` corrige todos os personagens de uma vez.
Guardar a ficha seria criar uma segunda verdade, que envelhece em silêncio. Foi por isso que as 89
paráfrases corrigidas ontem não exigiram migração nenhuma.

### `eventos` — o histórico

Append-only. Nunca se edita um evento; corrigir é gravar outro.

```jsonc
{ "_id": ObjectId, "personagem_id": ObjectId, "em": ISODate,
  "tipo": "magia_conjurada",
  "magia_id": "bola_de_fogo", "circulo": 3,
  "custo": { "moeda": "espaco_de_magia", "circulo": 3 } }
```

Tipos, no escopo escolhido (só o essencial):

| tipo | campos |
|---|---|
| `dano_sofrido` / `vida_recuperada` | `quantidade`, `pv_antes`, `pv_depois` |
| `temporarios_ganhos` | `quantidade`, `fonte` |
| `magia_conjurada` | `magia_id`, `circulo`, `custo` |
| `espacos_recuperados` | `por_circulo`, `origem` (descanso, característica) |
| `recurso_gasto` / `recurso_recuperado` | `recurso_id`, `quantidade` |
| `descanso` | `tipo: curto \| longo` |

Índice `{ personagem_id: 1, em: -1 }`, com paginação por cursor.

**Por que evento e não texto.** Ações, condições, recursos e magias todos têm id no dataset. Um
evento tipado permite filtrar ("só magia"), somar ("quanto dano nesta sessão") e, no futuro,
mostrar ao mestre — coisas que uma linha de texto não permite. É o que o `PLANO-APP.md` já
antecipava.

## Imagens no S3

O backend **não** faz proxy do arquivo. Fluxo:

1. Cliente pede `POST /personagens/{id}/imagem` e recebe uma **URL assinada de PUT**, válida por
   poucos minutos, com `Content-Type` e tamanho máximo fixados na assinatura.
2. Cliente envia direto ao S3.
3. Cliente confirma; o backend grava só a **chave** no documento.
4. Para exibir, o backend devolve uma **URL assinada de GET** de vida curta — o bucket fica privado.

Chave: `personagens/<id>/<uuid>.webp`. O `uuid` a cada troca evita cache velho sem precisar
invalidar nada. Trocar de imagem não apaga a anterior na hora; uma limpeza posterior varre as
chaves órfãs.

---

## O que fazer, em ordem

Cada passo termina em conferência: `python3 testes/rodar_todos.py` inteiro, verde.

**1. Dataset — normalizar `conjurar_sem_espaco`.** Um gerador de ajuste, como os das fases 15 e 16,
mais as checagens no `validar.py` (lista fechada de moeda e de frequência; frequência obrigatória;
recarga coerente com a frequência) e um teste negativo que planta cada defeito. É o passo que
destrava o item 4 do escopo, e é o único que mexe em `dados/`.

**2. Motor — `podeConjurar(personagem, magia)`.** Responde, sem conhecer nenhum id de conteúdo:
quais formas de conjurar aquela magia estão disponíveis agora, o que cada uma custa, e o que o
componente material exige (coberto pelo foco, exige material, custa X PO, é consumido). É a peça
que o app consulta ao tocar na magia.

**3. Motor — rótulos de proveniência apresentáveis.** As `parcelas` existem e estão certas; falta
cada uma dizer de onde vem em português, para a tela mostrar "10 base + 2 armadura + 2 escudo + 2
Destreza" sem o frontend adivinhar.

**4. Backend — `ArmazemMongo`.** Implementa a interface que já existe. Os testes de personagem
rodam contra `ArmazemNaMemoria`; um teste de integração roda contra o Atlas.

**5. Backend — contas.** `usuarios`, registro, login, token de sessão, e `usuario_id` em todo
personagem. Fecha o §B14.1 do `BACKLOG.md`.

**6. Backend — busca do compêndio.** Índice em memória construído na subida: nome normalizado sem
acento, coleção, e os campos filtráveis de cada família (círculo, escola, classe, para magia;
categoria, grupo, propriedade, para item). Hoje são **1.737 itens em 76 coleções** — cabe folgado na
memória, e a busca não precisa sair do processo.

**7. Backend — eventos.** Gravar no mesmo caminho que já altera o estado, para não existir mudança
de estado sem evento. Endpoint de leitura paginado.

**8. Backend — imagens.** URLs assinadas, como acima.

**9. Frontend — Fase A.** Criar personagem, Meus personagens, ficha em sessão, compêndio, histórico.

**Enquanto o cluster não existe**, os passos 1, 2, 3 e 6 andam inteiros — nenhum deles toca banco.

## O que não entra agora

- **Escrita concorrente** (`BACKLOG.md` §B14.2). Uma pessoa, um cliente: não morde. Morde na Fase B,
  e a solução (revisão no documento + `If-Match`) pertence ao desenho da sincronização.
- **CORS** (§B14.3) — depende de onde o app for servido.
- **Criaturas** e a versão do mestre — Fase C, com a decisão do Apêndice B antes.
- **As 112 paráfrases de criatura**, que não passaram pela releitura das magias e correm o mesmo
  risco. Não bloqueiam a Fase A.
