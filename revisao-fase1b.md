# Fase 1b — catálogos que as Classes referenciam + correção da ação Ajudar

Validador: **0 erros, 0 avisos**. JSON Schema: todos os arquivos passam.
Página: `pagina_livro` é o número impresso; `pagina_pdf` = `pagina_livro + 4`.

## Correção aplicada

**Ação Ajudar** — confirmado por você: primeiros socorros é a **terceira opção da própria ação**,
não uma ação separada. Adicionei `ajudar_primeiros_socorros` com o teste de **Sabedoria CD 10
(Medicina)** e o efeito (a criatura fica Estável). O teste e a CD vieram da p. 371 — a entrada de
Ajudar no glossário não os traz, então o dado aponta para as duas páginas. `revisao.status` passou
de `duvida` para `ok`, com a nota registrando que foi decisão sua.

## Catálogos novos — 4 arquivos

| catálogo | itens | fonte |
|---|---|---|
| **idiomas** | **19** (10 comuns + 9 raros) | cap. 2, p. 37 |
| **propriedades_de_arma** | **10** | cap. 6, p. 213–214 |
| **maestrias_de_arma** | **8** | cap. 6, p. 214 |
| **escolas_de_magia** | **8** | cap. 7, p. 236 |
| **ferramentas** | **25** (17 de artesão + 8 outras) | cap. 6, p. 220–221 |

Contagens para você bater no livro: **19 idiomas** · **10 propriedades** · **8 maestrias** ·
**8 escolas** · **17 ferramentas de artesão + 8 outras**.

### Detalhes que valem nota

- **Idiomas** — cada um traz `raridade` (`comum`/`raro`) e `origem`. Personagem começa com Comum +
  2 da tabela de comuns; raros só por característica que os conceda. Primordial guarda os quatro
  dialetos (Aquan, Auran, Ignan, Terran) num campo próprio, com a regra de intercompreensão.
- **Maestrias** vieram **com efeitos modelados**, não só nome e texto — Derrubar já carrega a
  salvaguarda de Constituição com CD `8 + mod. do ataque + BP` e a condição `caido`; Drenar e
  Lentidão carregam `beneficiario` e `duracao`. Quatro delas (Ágil, Empurrar, Garantido, Trespassar)
  têm partes que só um motor de combate resolve, e essas ficaram em `efeito_narrativo` com o texto
  parafraseado.
- **Ferramentas** — id, grupo, atributo do teste, custo e peso. Instrumento Musical (10 variantes) e
  Kit de Jogos (4) guardam as variantes em `variantes`, já que custo e peso variam. **Não extraí as
  listas de "Fabricação"** de cada ferramenta: elas apontam para itens do capítulo 6 que ainda não
  existem no dataset, e um catálogo apontando para chaves inexistentes é exatamente o que
  combinamos evitar. Entram junto com o capítulo 6.
- **Propriedades de arma** incluem `alcance`, que é propriedade de verdade no livro (define a leitura
  dos dois números) e não só uma coluna da tabela.

## Validador reforçado

Ele agora também varre os **catálogos**, não só as coleções — antes, um efeito escrito dentro de um
catálogo (como os das maestrias) passava sem checagem. E valida perícias/atributos em qualquer bloco
`teste` ou `salvaguarda`, em qualquer profundidade.

Rodei um teste negativo para confirmar que ele morde: plantei uma condição fantasma, um atributo
inválido e um `total` desatualizado num cópia do dataset — pegou os três, mais o efeito cascata.
Depois apaguei a cópia.

## Estado do dataset

```
23 catálogos · 2 coleções (15 condições, 12 ações)
```

Todas as chaves que uma Classe precisa referenciar já existem: perícias, salvaguardas, idiomas,
ferramentas, categorias e propriedades de arma, maestrias, categorias de armadura, escolas de magia,
tipos de dano, condições e ações.

## Próximo passo

Fase 2 — capítulo 3, **uma classe por lote**. Sugiro começar pelo **Monge**: ele exercita a parte
mais afiada do esquema logo de cara (fórmula de CA que substitui a padrão, recurso com recarga,
progressão com colunas próprias, ataque desarmado). Se o modelo aguentar o Monge, aguenta o resto.

Só me diga se prefere outra classe primeiro.
