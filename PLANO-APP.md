# Plano do aplicativo — Ficha Fácil

Registrado em 2026-09-01, a partir da descrição do João. Vale **depois** de a base de dados estar
pronta. Este arquivo é a referência do produto; o `PENDENCIAS.md` cuida do dataset.

## Princípio que orienta tudo

O jogo continua **no dado, na interpretação e na mesa**. O app é facilitador, não substituto. Ele
existe para quatro coisas: pesquisar uma regra sem abrir o livro, guardar o histórico do personagem,
consultar rápido algo da própria ficha ou de uma magia, e **subir de nível sem esquecer nada**.

Toda decisão de escopo daqui pra frente passa por esse filtro: se a funcionalidade tenta jogar o jogo
no lugar das pessoas, ela está fora.

## Fase A — PWA do jogador (celular primeiro)

**Criar personagem.** Guiado pelos dados que já temos: espécie, antecedente, classe, escolhas por
nível. Cada escolha do jogador já existe como `escolha` no dataset, com o filtro do que ele pode
pegar — o app renderiza o seletor a partir do dado, sem código por classe.

**Meus personagens.** Lista com status: **ativo, reserva, morto, aposentado**. Ordenação por
**último acesso** (o mais recente no topo).

**Ficha.** Consulta rápida de atributos, CA, PV, proficiências, características, recursos, magias.
Valores derivados calculados na hora pela pilha de efeitos, com o log de proveniência ("CA 17 = 10 +
3 DES + 4 SAB") disponível para quem quiser conferir.

**Compêndio.** As regras que estamos extraindo, navegáveis por categoria, para consultar no meio da
sessão. O glossário (Ap. C) já está pronto para isso — condições e ações têm descrição curta e
página. Magias e itens ficam completos quando os capítulos 7 e 6 entrarem.

**Subir de nível.** É o ponto onde os dados mais se pagam: a progressão diz exatamente o que chega
naquele nível, quais escolhas abrem e quais melhorias incidem sobre características já existentes. O
padrão `aviso_ao_subir_de_nivel` — criado para a Forma Selvagem, quando decidimos adiar as criaturas
— generaliza aqui: vira o **checklist de subida de nível**, e nada passa despercebido.

**Histórico de ações do personagem.** O jogador vê o que fez. Como ações, condições e efeitos têm id
no dataset, o log pode ser estruturado (evento tipado) em vez de texto solto.

## Fase B — Party e tempo real

Criar **partys**. O mestre enxerga as fichas dos jogadores ao vivo: jogador marca dano, atualiza para
o mestre; mestre marca algo na ficha do jogador, atualiza para o jogador.

Isso é sincronização, não dataset. O que ajuda é o esquema já separar **estado** (PV atual,
temporários, slots gastos, recursos, condições) de **derivado** (que é recalculado): o que precisa
trafegar é pequeno e bem delimitado.

## Fase C — Versão do mestre (desktop)

Reaproveita boa parte da base, mais as regras do mestre.

- **Gerar ficha de inimigo.** Escolher um arquétipo (bandido, por exemplo) e uma dificuldade, e sair
  uma ficha pronta.
- **Iniciativa.** Acompanhar a ordem do combate.
- **Histórico completo** de ações de personagens e NPCs, compartilhado com o que os jogadores veem.

### Consequência para o dataset, que vale registrar agora

A versão do mestre **reabre a decisão sobre criaturas**. Adiar o Apêndice B foi certo para o app do
jogador — a Forma Selvagem se vira com o aviso de ND. Mas gerar inimigo aleatório por arquétipo e
dificuldade precisa de blocos de estatísticas de verdade, e provavelmente de material do Livro do
Mestre, que ainda não temos.

Quando a Fase C entrar na fila, esta é a primeira coisa a decidir. Está anotado também no
`PENDENCIAS.md`, seção 1.

## Ordem sugerida

1. Terminar a base: seis classes restantes, capítulo 6 (equipamento), capítulo 7 (magias),
   capítulos 4 e 5 (origens e talentos).
2. Fase A.
3. Fase B.
4. Fase C — decidindo antes o que fazer com criaturas.

O capítulo 6 pode ser antecipado se a Fase A começar antes: ele destrava as armas na ficha e fecha as
cinco dúvidas de equipamento inicial que estão abertas hoje.
