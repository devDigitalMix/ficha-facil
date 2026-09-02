# Ficha Fácil

Base de dados do *Livro do Jogador* de D&D 2024 (PT-BR) em JSON estruturado, e o plano do app que
vai usá-la. Uso interno de uma mesa; não é produto.

O jogo continua no dado, na interpretação e na mesa. O app existe para quatro coisas: pesquisar
uma regra sem abrir o livro, guardar o histórico do personagem, consultar rápido a própria ficha e
**subir de nível sem esquecer nada**.

## Estado

O vocabulário de runtime — predicado, gatilho, duração, custo — é **lista fechada** desde a
fase 13, em `dados/vocabulario_de_runtime.json`: token que ninguém declarou é erro de build.
É o que impede o mesmo efeito de existir escrito de dois jeitos.

A extração está **completa**: capítulos 3 a 7 e o Apêndice B, com 12 classes, 48 subclasses, 16
antecedentes, 10 espécies, 391 magias, 170 itens, 75 talentos e 51 blocos de estatísticas de
criatura. Fora do escopo por decisão: multiclasse e o Apêndice A.

O motor está em `motor/` — TypeScript, biblioteca pura, zero dependências. Uma chamada,
`montar(construcao, estado)`, devolve a ficha com proveniência, o checklist de escolhas em
aberto **com as opções**, e as queixas do que foi escolhido errado. Fecha contra três
personagens de ouro: um Monge 1, um Bárbaro 5 e uma Clériga 5 — com armadura, escudo, armas e
magia. Falta o backend. Ver `PLANO-MOTOR.md` (como) e `PLANO-APP.md` (o quê).

## Por onde começar a ler

| arquivo | o que é |
|---|---|
| `esquema-v1.md` | **o contrato.** Como o dado é modelado e por quê. Comece aqui. |
| `PLANO-APP.md` | o que o app vai ser, em fases |
| `PLANO-MOTOR.md` | como o motor de efeitos e o backend vão funcionar — ler antes de escrever código |
| `motor/README.md` | o motor em si: como rodar, o que já existe, os personagens de ouro |
| `PENDENCIAS.md` | registro vivo: o que ficou de fora, o que depende de decisão, divergências do livro |
| `BACKLOG.md` | dívida técnica, escrita para quem for consertar |
| `revisoes/` | um arquivo por fase: o que entrou, o que foi decidido, o que ficou aberto |

## A ideia central

**Tudo é efeito componível.** Nenhuma entidade conhece as outras: o Monge carrega o efeito que
troca a fórmula de CA, o Druida carrega o que desbloqueia a lista de magias dele. O motor só sabe
aplicar efeitos — nunca nomes de classe.

Disso saem as outras regras: fórmulas são árvore e não string a parsear; toda entidade traz a
página de onde veio; incerteza é explícita (`revisao.status`); e **chave inexistente é erro de
build**, não bug silencioso.

## Como mexer

```bash
pip install -U "jsonschema>=4" --break-system-packages   # a do sistema é 3.2.0 e não serve

python3 testes/rodar_todos.py           # a conferência inteira, na ordem que faz sentido
python3 testes/rodar_todos.py --rapido  # sem a reconstrução, que é a demorada
```

São 14 passos: forma, semântica, derivação, auditoria das descrições, os oito testes negativos, o
motor e a reconstrução. Cada um também roda sozinho:

```bash
python3 validar.py                    # semântica: referências, filtros, coerência entre entidades
python3 checar_schema.py              # forma: campos obrigatórios, tipos, padrões de id
python3 testes/teste_negativo_*.py    # planta defeitos e cobra que o validador os pegue
python3 inventariar_vocabulario.py    # o vocabulário de runtime: o que existe e onde
cd motor && npm run teste             # o motor: fórmula, personagens de ouro, negativo
```

Os dois primeiros precisam sair limpos. Os testes negativos são o que dá sentido ao "0 erros": sem
eles, um validador que não checa nada também passaria.

**O gerador é a fonte; o JSON de `dados/` é saída.** Nunca edite o JSON à mão — mexa no gerador
correspondente em `geradores/`, ou escreva um `gerar_ajustes_<coisa>.py` para uma correção pontual.

```bash
python3 geradores/extrair_texto.py           # texto do PDF que os parsers consomem
python3 reconstruir.py /tmp/rb --comparar    # refaz tudo do zero e compara com dados/
```

A reconstrução nunca escreve em `dados/`: ela copia os geradores para um diretório separado e
trabalha lá. `--comparar` deve dizer **0 diferenças de conteúdo** — se disser outra coisa, alguém
editou o JSON à mão e a correção não está em gerador nenhum.

A ordem de execução importa e está declarada em `reconstruir.py`: um lote antigo rodado fora de
hora desfaz correção posterior. Por isso não se roda gerador antigo isolado contra `dados/`.

## Convenções

- Ids em pt-br, sem acento, minúsculo, `snake_case`. Únicos **dentro do catálogo**, não
  globalmente (ver `esquema-v1.md` §4.0).
- A página do PDF é a do livro **+ 4**.
- `intermediarios/` é texto extraído do PDF: derivado, regenerável, fora do git.
- A raiz guarda só ferramenta e documento de entrada. O resto mora em pasta:
  `geradores/` (a fonte do dado), `dados/` (a saída), `schema/`, `testes/`, `revisoes/`, `motor/`.

## O PDF

O Livro do Jogador precisa estar na raiz do repositório, em `.pdf`. Ele não é versionado.
