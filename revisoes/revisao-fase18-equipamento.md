# Fase 18 — equipamento equipado, e a ficha de combate fecha

Feita em 2026-09-02. A última peça que faltava para a ficha estar completa, e o fim
de três buracos que não apareciam porque nada os olhava.

`testes/rodar_todos.py`: **16 de 16 passos limpos.** Motor em 70 de 70, dataset em
`validar.py` 0 erros e 0 avisos, `checar_schema.py` 76/76, dez testes negativos e
`reconstruir.py --comparar` em 66/66 sem diferença.

---

## Os três buracos

Até esta fase o motor sabia tudo sobre o personagem e nada sobre o que ele estava
vestindo. Isso deixava três coisas em aberto — e as três eram do tipo que passa
despercebido, porque o número que sai **parece** certo:

1. **CA com armadura nunca era calculada.** Nenhum dos três goldens usava armadura;
   a Clériga estava sem, com o buraco escrito no arquivo em `nota_do_equipamento`.
2. **O `soma_se segurando:escudo` da fórmula de CA nunca ficava verdadeiro.** Estava
   lá desde a fase 5, escrito certo, e nunca tinha sido exercido uma vez.
3. **O bônus de ataque das armas estava escrito à mão nos goldens e nenhum teste
   lia.** "+7, 1d12+4" para o machado do Torvar era um número que eu tinha calculado
   de cabeça e ninguém conferia.

Os três fecharam. E os números que eu tinha escrito à mão estavam certos — o que só
vale alguma coisa agora que o motor os produz sozinho e um teste compara.

## Como ficou

O equipamento vira **predicado**, como todo o resto:

| equipado | predicado que o motor liga |
|---|---|
| qualquer armadura | `armadura:qualquer` e `armadura:<grupo>` |
| escudo | `segurando:escudo` |
| nenhuma arma | `sem_arma_na_mao` |

É assim que a Defesa sem Armadura do Monge sabe que não vale — a condição já estava
no dado desde a fase 2 (`{nao: 'armadura:qualquer'}`); faltava alguém dizer que havia
armadura. O motor continua sem saber quem é o Monge.

**A armadura CONCORRE, não substitui.** Ela entra pela mesma porta que a Defesa sem
Armadura do Monge e a do Bárbaro, e o maior ganha (Ap. C, p. 363). O Escudo é outra
coisa: soma por fora, porque não é cálculo de base.

**A Clériga vestiu.** Cota de Malha Parcial, Escudo e Maça: CA **16** = 13 (armadura)
+ 1 (Destreza, com teto 2) + 2 (Escudo). O cálculo padrão daria 11. E a Maça prova
que a proficiência sai do **filtro** da classe — "armas Simples" — e não de uma lista
de armas dentro do motor.

**O Ataque Desarmado entra sempre**, e é onde o Monge aparece: Artes Marciais troca
Força por Destreza (`substituir_atributo`) e troca o dano de 1 pelo dado da coluna
Artes Marciais (`dado_de_dano`). As duas trocas são efeito no dado. Kaida ataca com
**+5** e causa **1d6+3**; o Torvar, que não tem nada disso, ataca desarmado com +7 e
causa 1 + 4 de Força, como manda a p. 361.

## A lint pegou um id de conteúdo meu

Escrevi `i.grupo === 'escudo'` para reconhecer um escudo. `escudo` é o id de um item —
a lint da fase 14 acusou na hora, e ela estava certa: era exatamente a regra que ela
existe para proteger.

O conserto foi reconhecer o escudo **pela forma, não pelo nome**: escudo dá um `bonus`
de CA, armadura dá uma `base`. Isso vale para qualquer escudo futuro, inclusive um que
não se chame escudo.

No mesmo passo a lint precisou ficar mais precisa. Ela barrava também
`'segurando:escudo'`, que é **predicado do vocabulário de runtime** — a única lista
que o motor tem direito de conhecer, porque é o que ele implementa. Barrar isso seria
proibir o motor de nomear o que ele executa. A lint passou a aceitar os tokens
declarados em `vocabulario_de_runtime.json`, e só eles.

## O teste de mutação, quarta fase seguida

Seis defeitos plantados. Quatro reprovaram na hora; **dois passaram**, e os dois pela
mesma razão: os goldens não tinham como mordê-los.

| defeito plantado | passou porque |
|---|---|
| ignorar o teto de Destreza da armadura Média | a Clériga tem Destreza 13 (+1), e o teto é 2 — o corte nunca acontecia |
| dar proficiência com qualquer arma | os três personagens são proficientes com o que carregam |

Um golden é uma pessoa, e uma pessoa não cobre tudo. O conserto foi um arquivo de
testes focados — `equipamento.test.ts` — com os casos que exigem outra pessoa:
Destreza 18 em armadura Média (CA 17, e não 19), e a Clériga empunhando um Machado
Grande, que é Marcial (ataque **+1**: só a Força, sem os 3 de proficiência, e a ficha
diz `proficiente: false` em vez de somar calada).

Com eles, os seis defeitos reprovam. Também entrou o par que impede o conserto de
virar outro defeito: armadura **sem** teto soma a Destreza inteira — senão "respeitar
o teto" poderia virar "ignorar a Destreza sempre".

## As três decisões que estavam paradas

Fechadas pelo João nesta fase, e registradas no `BACKLOG.md` §B6:

1. **"Aeronau" (p. 230) fica como está.** É o que o livro imprime, e o dado reproduz
   o livro — inclusive quando parece deslize de edição. Corrigir por conta própria
   seria inventar.
2. **"Ler qualquer idioma" continua regra declarada**, e segue sendo o último
   `substituir_regra` do dataset. O critério de promover a primitivo é o mesmo dos
   `efeito_narrativo` — a mesma coisa aparecer em três lugares — e esta aparece em um.
3. **A releitura das 391 magias fica para depois.** Não bloqueia o motor: o argumento
   está no `PLANO-MOTOR.md` §10 — o motor lê o campo estruturado, não a paráfrase.
   As três ressalvas de lá continuam valendo.

## O que vem

Passo 5 do plano: o **backend**, com os endpoints da §7. O motor entrega tudo o que
eles precisam por uma porta só — `montar(construcao, estado)` devolve ficha com
proveniência, checklist com opções, problemas e ataques.

Continuam de antes: os `efeito_narrativo`, as 391 paráfrases de magia e as 112 de
criatura, e a regra de mesa do §B6.6 (Maestria em Arma no nível 20 do Guardião e do
Paladino), que espera a camada de overrides.
