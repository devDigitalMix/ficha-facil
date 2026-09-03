# Frontend — PWA do jogador (Fase A)

React com Vite. Celular primeiro, como manda o `PLANO-APP.md`: a tela de uso é a que
está na mesa.

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, falando com o backend em 8787
npm run tipos      # tsc --noEmit — a única checagem de tipo do projeto
npm run fumaca     # o app inteiro num navegador de verdade
```

O backend precisa estar de pé (`cd backend && npm run servir`). Para apontar para
outra porta: `BACKEND=http://localhost:8899 npm run dev`.

## O build step, que é novo no projeto

Motor e backend rodam TypeScript direto, sem build. **React não roda assim** — JSX
precisa de transformação —, então este é o primeiro pedaço do projeto com etapa de
compilação, e com árvore de dependências de verdade. Foi decisão consciente ao pedir
React; vale registrar para não parecer descuido quando alguém comparar com o
`backend/package.json`, que tem uma dependência só.

## Sem CORS, de propósito

O Vite serve `/api` por **proxy** para o backend. Para o navegador, tudo vem da mesma
origem, e a questão de CORS simplesmente não existe em desenvolvimento — é por isso
que o `BACKLOG.md` §B14.3 continua aberto sem incomodar. Quando o app for hospedado, a
decisão de qual origem liberar pertence àquele momento; inventá-la agora seria decidir
cedo demais.

## A sessão

Fica no `localStorage` e vale **30 dias**, que é exatamente o que o backend assina
(`SESSAO_HORAS=720`). Guardar por mais tempo aqui só produziria um token que o servidor
recusa; por menos, jogaria fora sessão boa. O botão **sair** apaga na hora.

Quando qualquer chamada volta **401**, `api.ts` limpa a sessão e avisa o `App`, que
cai no login. Isso mora num lugar só — nenhuma tela precisa lembrar de tratar token
vencido, e ninguém vê tela em branco.

Motor e backend rodam TypeScript sem build e por isso não têm checagem de tipo nenhuma —
os tipos ali são documentação. Aqui o compilador já roda, então `npm run tipos` entra na
conferência da raiz: é barato onde é possível, e foi a falta disso que deixou três testes
passarem por engano na fase 19.

`localStorage` é legível por qualquer script desta origem. Para um app pessoal, com um
backend que serve só o dono, é troca aceitável; cookie `HttpOnly` seria mais seguro
contra XSS, mas exige o backend emitir e ler cookie, e CORS com credenciais. É a
primeira coisa a revisitar quando o app sair da máquina do João.

## A escolha mostra o que se está escolhendo

Cada opção é uma **linha** com nome, etiquetas e descrição — não uma pílula com um nome
só. Escolher seis magias entre trinta e uma sem ver alcance, dano ou duração é escolher
no escuro, e foi o primeiro uso de verdade que mostrou isso.

A tela não sabe o que é magia: ela recebe `catalogo` no item do checklist, busca aquele
catálogo no compêndio (uma vez por aba; o backend serve com ETag imutável) e desenha os
**campos que existirem**. Um catálogo novo com `descricao_curta` já aparece descrito sem
que ninguém toque neste arquivo; uma perícia, que só tem `atributo`, aparece com essa
etiqueta e nenhuma descrição, e não fica pior por isso.

## A prévia: escolher talento sabendo o que ele faz

Marcada uma opção, a tela chama `POST /personagens/:id/escolhas/previa` — que monta a
construção com a escolha proposta e devolve o checklist resultante **sem gravar nada** —
e mostra as sub-escolhas ali mesmo, aninhadas. Responder uma delas refaz a prévia, então
as que dependem de outra (os truques do Iniciado em Magia só existem depois da lista)
vão aparecendo. O **Confirmar** grava tudo de uma vez.

Antes disso, a única forma de descobrir o que um talento pedia era aceitá-lo. Isso cabe
no backend, e não numa regra escrita aqui, porque o motor é puro: montar de novo é
barato, e a resposta é a verdade em vez de um palpite do frontend.

## Nenhuma tela conhece regra de D&D

O checklist chega do backend como `{ escolha_id, rotulo, quantidade, opcoes }`, e a
tela desenha "escolha N destes". **Não há um `if (classe === 'clerigo')` em lugar
nenhum** — é o mesmo princípio do dataset, e se aparecer um, está no lugar errado.

O mesmo vale para os números: o `10 + 3 (DES) + 4 (SAB)` que aparece ao tocar na CA é
a `parcelas` que o motor devolve. A tela não recalcula nada; ela escreve o que recebeu.

### A exceção, e ela é um débito

O **aumento de atributo do antecedente** não é "escolha N de uma lista": escolhido o
modo (`+2 e +1` ou `+1 nos três`), ainda falta dizer *quais* atributos sobem — e o
checklist não declara isso. A tela descobre por dado, não por id chumbado: lê o
catálogo `modos_de_aumento_do_antecedente` (que traz `aumentos: [2, 1]`) e o
antecedente (que traz `atributos: ["INT","SAB","CAR"]`). Funciona, e um modo novo no
livro passaria a funcionar sozinho.

Mas o conserto certo não é aqui: **é o checklist declarar a forma que espera**. Hoje
o frontend precisa saber que aquele catálogo tem significado especial, o que é
exatamente o tipo de conhecimento que o projeto tira das pontas. Fica anotado.

## O que o teste de fumaça cobre

`npm run fumaca` sobe backend e frontend em portas próprias, com armazém em arquivo num
diretório temporário, e percorre num navegador de verdade o caminho que o jogador
percorre: criar conta, lista vazia, criar personagem, marcar dano, ver a linha no
histórico, responder uma escolha simples, distribuir o aumento do antecedente,
recarregar a página, sair e entrar de novo.

Não é teste de unidade e não tenta ser. É a pergunta que nenhum teste de componente
responde: **isto funciona ponta a ponta?** Sem navegador, ele **pula** em vez de fingir
que passou — a mesma regra dos testes que precisam de Mongo.

Ele entra no `testes/rodar_todos.py` da raiz, que é a conferência do projeto inteiro.

## O que ainda não tem

Nada disto bloqueia usar o app; são os próximos refinos.

- **Subir de nível.** O endpoint existe (`POST /personagens/:id/subir-nivel`, com a
  diferença do que chegou) e a tela ainda não.
- **Mudar o status** do personagem depois de criado, e apagar.
- **Conjurar por magia.** Hoje se gasta o espaço pelo círculo; o `motivo.magia_id`, que
  faz o histórico dizer "conjurou Bola de Fogo", ainda não tem tela — ele depende do
  `podeConjurar()` do passo 2 do `PLANO-FASE-A.md`.
- **Compêndio.** Depende da busca no backend (passo 6).
- **Recursos e condições**, que o estado já guarda.
- **PWA de verdade** — manifesto e service worker. Hoje é um site que funciona bem no
  celular, o que é diferente de instalável e offline.
- **Sem roteador.** Três telas, navegação em `useState`. Não há link compartilhável nem
  botão voltar do navegador; quando houver, um roteador se paga.
