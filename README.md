# Ficha Fácil

Base de dados do *Livro do Jogador* de D&D 2024 (PT-BR) em JSON estruturado, e o plano do app que
vai usá-la. Uso interno de uma mesa; não é produto.

O jogo continua no dado, na interpretação e na mesa. O app existe para quatro coisas: pesquisar
uma regra sem abrir o livro, guardar o histórico do personagem, consultar rápido a própria ficha e
**subir de nível sem esquecer nada**.

## Estado

A extração está **completa**: capítulos 3 a 7 do livro, com 12 classes, 48 subclasses, 16
antecedentes, 10 espécies, 391 magias, 170 itens e 75 talentos. Fora do escopo por decisão:
criaturas (Apêndice B), multiclasse e o Apêndice A.

O próximo passo não é mais o PDF — é o motor de efeitos. Ver `PLANO-APP.md`.

## Por onde começar a ler

| arquivo | o que é |
|---|---|
| `esquema-v1.md` | **o contrato.** Como o dado é modelado e por quê. Comece aqui. |
| `PLANO-APP.md` | o que o app vai ser, em fases |
| `PENDENCIAS.md` | registro vivo: o que ficou de fora, o que depende de decisão, divergências do livro |
| `BACKLOG.md` | dívida técnica, escrita para quem for consertar |
| `revisao-fase*.md` | um por lote de extração: o que entrou, o que foi decidido, o que ficou aberto |

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

python3 validar.py            # semântica: referências, filtros, coerência entre entidades
python3 checar_schema.py      # forma: campos obrigatórios, tipos, padrões de id
python3 teste_negativo_*.py   # planta defeitos e cobra que o validador os pegue
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

## O PDF

O Livro do Jogador precisa estar na raiz do repositório, em `.pdf`. Ele não é versionado.
