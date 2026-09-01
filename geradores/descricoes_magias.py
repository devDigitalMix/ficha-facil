# -*- coding: utf-8 -*-
"""Descrições curtas das magias, escritas à mão em paráfrase.

Regra do projeto: o texto do livro NÃO é copiado. Cada entrada aqui é um resumo
mecânico próprio — o que a magia faz, com os números que o jogador precisa —
escrito a partir da leitura da entrada do capítulo 7. Os campos estruturados
(alcance, duração, componentes, dano, salvaguarda, área) vêm do parser e são
fatos da tabela, não prosa.

Chave: o nome da magia como aparece no livro.
"""

DESCRICOES = {
 # ---------------------------------------------------------------- A
 "Acalmar Emoções":
  "Humanoides numa Esfera de 6 m fazem salvaguarda de Carisma. Para cada um que falhar, "
  "escolha: fica imune a Amedrontado e Enfeitiçado (suprimindo os que já tiver), ou fica "
  "Indiferente com criaturas à sua escolha de quem era Hostil — indiferença que acaba se ele "
  "ou os aliados dele sofrerem dano.",
 "Acudir os Moribundos":
  "Estabiliza uma criatura com 0 Pontos de Vida que ainda não morreu. Não cura.",
 "Alarme":
  "Marca uma porta, janela ou área de até um Cubo de 6 m. Por 8 horas, avisa quando alguém "
  "toca ou entra, exceto criaturas que você designou na conjuração. Escolha alarme mental "
  "(sentido a até 1,5 km, acorda você) ou sonoro (sineta por 10 s, ouvida a 18 m).",
 "Aliado Extraplanar":
  "Pede a uma entidade cósmica que você conhece pelo nome que envie um Celestial, Elemental "
  "ou Ínfero. A criatura chega sem obrigação de obedecer: você negocia o serviço, e o preço "
  "cresce com o risco e a duração. O Mestre interpreta a entidade.",
 "Aljava Veloz":
  "Ao conjurar e depois como Ação Bônus, faz dois ataques com arma de Dardos ou Flechas. "
  "A magia cria a munição, que causa dano de munição não mágica e se desfaz após o ataque.",
 "Alterar-se":
  "Muda sua forma; troca de opção com uma ação Usar Magia enquanto durar. Adaptação Aquática: "
  "respira sob a água e ganha Deslocamento de Natação igual ao seu. Armas Naturais: Ataque "
  "Desarmado passa a 1d6 do tipo da arma criada, com bônus de acerto se for mágico. "
  "Mudar de Aparência: altera traços à vontade, sem mudar de tamanho nem de tipo.",
 "Amigos":
  "Uma criatura à vista faz salvaguarda de Sabedoria ou fica Enfeitiçada. Passa automaticamente "
  "se não for Humanoide, se estiver lutando com você ou se você já a alvejou nas últimas 24 h. "
  "Acaba se ela sofrer dano ou se você atacar — e aí ela sabe que foi enfeitiçada por você.",
 "Amizade Animal":
  "Uma Fera à vista faz salvaguarda de Sabedoria ou fica Enfeitiçada por 24 horas. Acaba se "
  "você ou um aliado causar dano a ela.",
 "Âncora Planar":
  "Vincula um Celestial, Elemental, Feérico ou Ínfero ao seu serviço por 24 horas. A criatura "
  "precisa ficar no alcance durante toda a conjuração (o normal é prendê-la antes com Círculo "
  "Mágico invertido) e falhar numa salvaguarda de Carisma. Obedece ao pé da letra e procura "
  "brechas; se foi invocada por outra magia, a duração daquela se estende junto.",
 "Animar Mortos":
  "Anima uma pilha de ossos (Esqueleto) ou um cadáver Humanoide Médio ou Pequeno (Zumbi). "
  "Comanda com Ação Bônus a até 18 m; sem ordem, só se defende. O controle dura 24 horas e "
  "precisa ser renovado reconjurando a magia no mesmo morto-vivo.",
 "Animar Objetos":
  "Anima objetos não mágicos soltos, até o seu modificador de conjuração (Grande conta 2, "
  "Enorme conta 3). Viram Constructos com o bloco Objeto Animado sob seu controle. Comanda "
  "todos com Ação Bônus.",
 "Antipatia/Simpatia":
  "Escolha um alvo Enorme ou menor e um tipo de criatura. Por 10 dias, criaturas desse tipo a "
  "até 36 m fazem salvaguarda de Sabedoria. Antipatia: ficam Amedrontadas e fogem do alvo. "
  "Simpatia: sentem compulsão de se aproximar e ficar. Repetem a salvaguarda a cada minuto; "
  "quem escapa fica imune por 1 minuto.",
 "Aprimorar Atributo":
  "Toque: o alvo ganha Vantagem em testes de um atributo à sua escolha por até 1 hora.",
 "Aprisionamento":
  "Uma criatura à vista faz salvaguarda de Sabedoria ou é aprisionada até a magia ser dissipada "
  "— sem respirar, comer ou envelhecer, invisível à Adivinhação e sem teleportar. Escolha a "
  "forma: acorrentada, enterrada em esfera minúscula, presa em labirinto, adormecida ou "
  "encolhida numa gema. Cada forma tem uma condição própria de libertação, definida na "
  "conjuração. Quem passa fica imune por 24 horas.",
 "Arca Secreta de Leomund":
  "Manda um baú (até 340 litros de material não vivo) para o Plano Etéreo. Traz de volta ou "
  "reenvia tocando a réplica em miniatura. Passados 60 dias, 5% cumulativos por dia de a magia "
  "acabar; perder a réplica também custa o baú.",
 "Arma Elemental":
  "Torna mágica uma arma tocada: +1 em ataque e 1d4 extra de Ácido, Elétrico, Gélido, Ígneo ou "
  "Trovejante à sua escolha, por até 1 hora.",
 "Arma Mágica":
  "Torna mágica uma arma tocada, com +1 em ataque e dano por 1 hora.",
 "Arma Espiritual":
  "Cria uma arma espectral no alcance e ataca de imediato: ataque mágico corpo a corpo por "
  "1d8 + modificador de conjuração de dano Energético. Depois, Ação Bônus para mover 6 m e "
  "atacar de novo.",
 "Armadura Arcana":
  "Toque numa criatura voluntária sem armadura: CA base passa a 13 + Destreza por 8 horas. "
  "Acaba se ela vestir armadura.",
 "Armadura de Agathys":
  "5 Pontos de Vida Temporários; quem acertar você corpo a corpo sofre 5 de dano Gélido. "
  "Acaba quando os temporários zeram.",
 "Arrombar":
  "Destranca ou desobstrui um objeto à vista — porta, baú, cadeado, grilhões. Só uma fechadura "
  "por conjuração. Suprime Tranca Arcana por 10 minutos. O estrondo é ouvido a 90 m.",
 "Arte Druídica":
  "Um efeito menor da natureza: acender ou apagar chama pequena, criar efeito sensorial "
  "inofensivo num Cubo de 1,5 m, fazer uma flor desabrochar ou uma semente germinar, ou prever "
  "o clima local das próximas 24 horas.",
 "Assassino Fantasmagórico":
  "Cria o medo mais profundo de uma criatura à vista. Salvaguarda de Sabedoria: falhou, sofre "
  "4d10 Psíquico e fica com Desvantagem em testes e ataques; passou, metade do dano e a magia "
  "acaba. Repete a salvaguarda no fim de cada turno dela, sofrendo o dano de novo a cada falha.",
 "Augúrio":
  "Pergunta sobre um curso de ação dos próximos 30 minutos e recebe um presságio: Prosperidade "
  "(bom), Infortúnio (mau), os dois, ou Nada. Não considera circunstâncias que possam mudar o "
  "resultado. Repetir antes de um Descanso Longo acumula 25% de chance de não haver resposta.",
 "Aumentar/Reduzir":
  "Muda o tamanho de uma criatura ou objeto à vista em uma categoria (alvo involuntário faz "
  "salvaguarda de Constituição). Aumentar: Vantagem em Força e salvaguardas de Força, +1d4 no "
  "dano de arma. Reduzir: Desvantagem nas mesmas e −1d4 no dano.",
 "Aura de Pureza":
  "Emanação de 9 m a partir de você: você e seus aliados têm Resistência a dano Venenoso e "
  "Vantagem nas salvaguardas contra Amedrontado, Atordoado, Cego, Enfeitiçado, Envenenado, "
  "Paralisado e Surdo.",
 "Aura de Vida":
  "Emanação de 9 m: você e seus aliados têm Resistência a dano Necrótico e não têm os Pontos de "
  "Vida máximos reduzidos. Aliado com 0 Pontos de Vida que comece o turno na aura recupera 1.",
 "Aura de Vitalidade":
  "Emanação de 9 m: ao criar e no início de cada turno seu, restaura 2d6 Pontos de Vida numa "
  "criatura dentro dela.",
 "Aura Mágica de Nystul":
  "Por 24 horas, disfarça a aura mágica de um alvo. Em objeto (Falsa Aura), muda como ele "
  "aparece à Detectar Magia — mágico virando comum e vice-versa. Em criatura (Máscara), faz "
  "parecer de outro tipo. Conjurada no mesmo alvo 30 dias seguidos, dura até ser dissipada.",
 "Aura Sagrada":
  "Emanação de 9 m: criaturas à sua escolha têm Vantagem em todas as salvaguardas, e quem "
  "ataca elas tem Desvantagem. Ínfero ou Morto-Vivo que acertar um protegido corpo a corpo faz "
  "salvaguarda de Constituição ou fica Cego até o fim do próximo turno dele.",
 "Auxílio":
  "Até três criaturas ganham +5 nos Pontos de Vida máximos e atuais por 8 horas.",
 "Badalar Fúnebre":
  "Uma criatura à vista faz salvaguarda de Sabedoria ou sofre 1d8 de dano Necrótico — 1d12 se "
  "já tiver perdido Pontos de Vida.",
 "Banimento":
  "Uma criatura à vista faz salvaguarda de Carisma ou vai para um semiplano inofensivo, "
  "Incapacitada, até a magia acabar. Se for Aberração, Celestial, Elemental, Feérico ou Ínfero "
  "e a magia durar o minuto inteiro, ela não volta: fica num plano do próprio tipo.",
}

DESCRICOES.update({
 # ---------------------------------------------------------------- B - C
 "Banquete de Heróis":
  "Um banquete para até doze criaturas, consumido em 1 hora. Quem come ganha por 24 horas: "
  "Resistência a dano Venenoso, Imunidade a Amedrontado e Envenenado, +2d10 nos Pontos de Vida "
  "máximos e a mesma quantidade de Pontos de Vida recuperados.",
 "Barreira de Lâminas":
  "Muro de lâminas de energia: reta de até 30 m × 6 m de altura, ou círculo de 18 m de diâmetro. "
  "Dá Cobertura de Três Quartos e é Terreno Difícil. Salvaguarda de Destreza para quem estiver, "
  "entrar ou terminar o turno nela: 6d10 de dano Energético, metade se passar. Uma vez por turno.",
 "Bênção":
  "Até três criaturas somam 1d4 às jogadas de ataque e às salvaguardas pela duração.",
 "Boca Encantada":
  "Grava numa mensagem de até 25 palavras num objeto, com uma circunstância de disparo visual "
  "ou auditiva a até 9 m. Disparada, uma boca aparece no objeto e recita com a sua voz. Escolha "
  "se acaba depois de falar ou se repete a cada disparo.",
 "Bola de Fogo":
  "Explosão numa Esfera de 6 m de raio: salvaguarda de Destreza, 8d6 de dano Ígneo, metade se "
  "passar. Objetos inflamáveis soltos na área pegam fogo.",
 "Bola de Fogo Adiável":
  "Um grânulo fica suspenso no ponto escolhido acumulando dano: começa em 12d6 e ganha 1d6 no "
  "fim de cada turno seu. Quando a magia acaba, explode numa Esfera de 6 m (salvaguarda de "
  "Destreza, metade se passar). Quem tocar o grânulo faz salvaguarda de Destreza: falhando, "
  "detona ali; passando, pode arremessá-lo até 12 m.",
 "Bolha Ácida":
  "Explode numa Esfera de 1,5 m de raio: salvaguarda de Destreza ou 1d6 de dano Ácido.",
 "Bom Fruto":
  "Dez frutos que duram 24 horas. Comer um (Ação Bônus) restaura 1 Ponto de Vida e alimenta uma "
  "criatura por um dia.",
 "Bordão Místico":
  "Um Cajado ou Clava que você segura usa seu atributo de conjuração no ataque e no dano, com "
  "dado de dano d8, e pode causar dano Energético em vez do tipo normal. Acaba se você largar a "
  "arma ou reconjurar.",
 "Braços de Hadar":
  "Tentáculos numa Emanação de 3 m em volta de você: salvaguarda de Força, 2d6 de dano Necrótico "
  "e sem Reações até o início do próximo turno do alvo; metade do dano se passar.",
 "Caldeirão Borbulhante de Tasha":
  "Um caldeirão fixo por 10 minutos com o líquido de uma poção Comum ou Incomum à sua escolha. "
  "Ação Bônus para retirar uma; rende tantas quanto seu modificador de conjuração (mínimo 1) e "
  "some quando a última sai. Poções não bebidas somem se você reconjurar.",
 "Caminhar no Vento":
  "Você e até dez criaturas viram nuvens por 8 horas: Deslocamento de Voo 90 m com pairar, "
  "Imunidade a Caído e Resistência a Contundente, Cortante e Perfurante. Só pode Correr ou "
  "começar a reverter — reverter leva 1 minuto, Atordoado.",
 "Caminhar Sobre as Águas":
  "Até dez criaturas andam sobre qualquer superfície líquida — água, lama, lava, neve — como "
  "chão sólido, por 1 hora. Entrar ou sair do líquido custa Ação Bônus.",
 "Campo Antimagia":
  "Emanação de 3 m onde nenhuma magia funciona: não se conjura, itens mágicos não operam, áreas "
  "de efeito não entram, invocações somem enquanto estiverem dentro e magias ativas ficam "
  "suprimidas. Não dissipa nada — apenas desliga enquanto vale.",
 "Cão Fiel de Mordenkainen":
  "Um cão de guarda invisível para os outros, intangível e invulnerável, por 8 horas. Late quando "
  "alguém Pequeno ou maior chega a 9 m sem a senha, tem Visão Verdadeira de 9 m e morde no início "
  "de cada turno seu. Acaba se vocês se separarem por mais de 90 m.",
 "Cárcere de Energia":
  "Prisão de energia em forma de jaula (até 6 m de lado, com grades) ou caixa sólida (até 3 m, "
  "opaca e impermeável a magia). Quem está dentro fica preso; sair exige Teleporte ou viagem "
  "planar, e mesmo assim com salvaguarda de Carisma.",
 "Cativar":
  "Criaturas à sua escolha à vista fazem salvaguarda de Sabedoria — quem estiver lutando com "
  "vocês passa automaticamente. Quem falha leva −10 em testes de Percepção e na Percepção "
  "Passiva enquanto durar.",
 "Cegueira/Surdez":
  "Uma criatura à vista faz salvaguarda de Constituição ou fica Cega ou Surda (você escolhe) por "
  "1 minuto, repetindo a salvaguarda no fim de cada turno dela.",
 "Celeridade":
  "Uma criatura voluntária dobra o Deslocamento, ganha +2 de CA, Vantagem em salvaguardas de "
  "Destreza e uma ação extra por turno, usável só para Atacar (um ataque), Correr, Desengajar, "
  "Esconder ou Usar Objeto. Ao acabar, fica Incapacitada e com Deslocamento 0 até o fim do "
  "próximo turno dela.",
 "Chama Contínua":
  "Chama permanente num objeto tocado: Luz Plena em 6 m e Meia-luz por mais 6 m, sem calor e sem "
  "combustível. Pode ser coberta, não apagada.",
 "Chama Sagrada":
  "Uma criatura à vista faz salvaguarda de Destreza ou sofre 1d8 de dano Radiante. Cobertura "
  "Parcial e de Três Quartos não ajudam nessa salvaguarda.",
 "Chicote de Espinhos":
  "Ataque mágico corpo a corpo a até 9 m: 1d6 de dano Perfurante e, se o alvo for Grande ou "
  "menor, puxa ele 3 m em sua direção.",
 "Chuva de Meteoros":
  "Quatro esferas de fogo caem em pontos distintos, cada uma numa Esfera de 12 m de raio: "
  "salvaguarda de Destreza, 20d6 de dano Ígneo mais 20d6 de dano Contundente, metade se passar. "
  "Quem estiver em mais de uma esfera é atingido só uma vez.",
 "Círculo da Morte":
  "Esfera de 18 m de raio: salvaguarda de Constituição, 8d8 de dano Necrótico, metade se passar.",
 "Círculo de Poder":
  "Emanação de 9 m: você e seus aliados têm Vantagem em salvaguardas contra magia, e quando a "
  "salvaguarda bem-sucedida daria metade do dano, não sofrem dano nenhum.",
 "Círculo de Teleporte":
  "Abre por uma rodada um portal para um círculo de teleporte permanente cuja sequência de "
  "símbolos você conhece, no mesmo plano. Quem entrar sai a 1,5 m do círculo de destino.",
 "Círculo Mágico":
  "Cilindro de 3 m de raio e 6 m de altura por 1 hora, contra os tipos que você escolher entre "
  "Celestial, Elemental, Feérico, Ínfero e Morto-Vivo. Esses tipos não entram, não enfeitiçam, "
  "amedrontam nem possuem quem está dentro. Pode ser invertida, prendendo em vez de proteger.",
 "Clarividência":
  "Um sensor invisível e inatacável num lugar familiar ou obviamente descrito, a até 1,5 km. "
  "Escolha ver ou ouvir pelo sensor; Ação Bônus para alternar.",
 "Clone":
  "Cria uma duplicata inerte de uma criatura tocada, pronta em 120 dias, com a idade que você "
  "escolher. Se o original morrer depois disso, a alma passa para o clone, com os Pontos de Vida "
  "máximos dele e sem os efeitos que matavam o corpo antigo.",
 "Coluna de Chamas":
  "Cilindro de 3 m de raio e 12 m de altura: salvaguarda de Destreza, 5d6 de dano Ígneo mais 5d6 "
  "de dano Radiante, metade se passar.",
 "Comando":
  "Uma palavra de ordem a uma criatura à vista: salvaguarda de Sabedoria ou ela obedece no "
  "próximo turno dela. Opções: Abaixar (fica Caída), Aproximar, Fugir, Largar (solta o que "
  "segura) ou Parar (não se move nem age).",
 "Compreender Idiomas":
  "Por 1 hora, entende o sentido literal de qualquer idioma falado, e de qualquer escrita que "
  "toque — cerca de 1 minuto por página. Não quebra códigos nem mensagens secretas.",
 "Compulsão":
  "Criaturas à sua escolha à vista fazem salvaguarda de Sabedoria ou ficam Enfeitiçadas. Ação "
  "Bônus para apontar uma direção horizontal: cada alvo gasta o movimento indo por ali pelo "
  "caminho mais seguro, e depois repete a salvaguarda.",
})

DESCRICOES.update({
 # ---------------------------------------------------------------- C
 "Comunhão":
  "Até três perguntas de sim ou não a uma divindade. A resposta é correta, mas pode vir "
  "'indeterminado' se estiver além do que a entidade sabe.",
 "Comunhão com a Natureza":
  "Aprende três fatos à sua escolha sobre a região — até 5 km ao ar livre, 90 m no subterrâneo "
  "natural. Não funciona onde a natureza foi substituída por construção.",
 "Cone de Frio":
  "Cone de 18 m: salvaguarda de Constituição, 8d8 de dano Gélido, metade se passar. Quem morre "
  "vira estátua congelada até descongelar.",
 "Confusão":
  "Esfera de 3 m de raio: salvaguarda de Sabedoria ou o alvo fica sem Ações Bônus e sem Reações "
  "e joga 1d10 no início de cada turno para saber o que faz — de vagar sem agir a atacar quem "
  "estiver por perto. Repete a salvaguarda no fim de cada turno dele.",
 "Consagrar":
  "Santifica uma área de até 18 m de raio até ser dissipada. Vigília Consagrada barra um tipo de "
  "criatura à sua escolha; o segundo efeito, escolhido na conjuração, pode ser desde luz ou "
  "escuridão constantes até proteção contra dano de um tipo. Não pode sobrepor outra Consagrar.",
 "Contágio":
  "Toque: salvaguarda de Constituição ou 11d8 de dano Necrótico e a condição Envenenado, com "
  "Desvantagem nas salvaguardas de um atributo à sua escolha. Repete no fim de cada turno até "
  "três sucessos (acaba) ou três falhas (dura os 7 dias inteiros).",
 "Contato Extraplanar":
  "Faz uma salvaguarda de Inteligência CD 15. Passando, faz até cinco perguntas a uma entidade "
  "extraplanar, respondidas em uma palavra. Falhando, sofre 6d6 de dano Psíquico e fica com "
  "Desvantagem em testes de Inteligência até terminar um Descanso Longo.",
 "Contingência":
  "Prepara uma magia de 5º círculo ou inferior, com tempo de conjuração de uma ação e que possa "
  "ter você como alvo, para disparar sozinha num gatilho que você descreve. Gasta os dois "
  "espaços na hora e dura 10 dias; só uma Contingência ativa por vez.",
 "Contramagia":
  "Interrompe quem está conjurando: salvaguarda de Constituição do conjurador ou a magia se "
  "perde e a ação usada é desperdiçada. O espaço de magia dele não é gasto.",
 "Controlar Água":
  "Controla a água num Cubo de até 30 m: dividir criando uma trincheira, mudar o fluxo, criar uma "
  "onda que derruba, ou um redemoinho que prende e fere. Troca de efeito com uma ação Usar Magia.",
 "Controlar o Clima":
  "Ao ar livre, controla precipitação, temperatura e vento num raio de 8 km. Cada mudança sobe ou "
  "desce um estágio de cada vez e leva 1d4 × 10 minutos para valer. Acaba se você entrar em "
  "ambiente fechado.",
 "Convocar Celestial":
  "Invoca um Espírito Celestial (Defensor ou Vingador) por até 1 hora, com o bloco de "
  "estatísticas próprio. É seu aliado, age no seu turno e obedece a comandos verbais; sem ordem, "
  "só Esquiva e se move para evitar perigo.",
 "Convocar Elemental":
  "Invoca um Espírito Elemental de Água, Ar, Fogo ou Terra por até 1 hora, com o bloco de "
  "estatísticas próprio. Aliado, age no seu turno, obedece a comandos verbais.",
 "Convocar Familiar":
  "Um familiar em forma de Fera de ND 0 à sua escolha, mas de tipo Celestial, Feérico ou Ínfero. "
  "Age por conta própria, obedece a você, não ataca, e você pode ver e ouvir por ele. Some ao "
  "chegar a 0 Pontos de Vida e volta com uma reconjuração. Pode conjurar magias de toque por ele.",
 "Convocar Feérico":
  "Invoca um Espírito Feérico Alegre, Enfurecido ou Malandro por até 1 hora, com o bloco de "
  "estatísticas próprio. Aliado, age no seu turno, obedece a comandos verbais.",
 "Convocar Montaria":
  "Uma montaria sobrenatural Celestial, Feérica ou Ínfera, com o bloco de estatísticas próprio, "
  "que escala com o círculo usado. Some a 0 Pontos de Vida; conjurar de novo substitui a "
  "montaria anterior.",
 "Convocar Relâmpagos":
  "Nuvem em Cilindro de 18 m de raio e 3 m de altura. Ao conjurar e depois com uma ação Usar "
  "Magia, cai um raio num ponto sob ela: quem estiver a 1,5 m faz salvaguarda de Destreza, 3d10 "
  "de dano Elétrico, metade se passar. Ao ar livre e sob tempestade, o dano sobe.",
 "Corda Extradimensional":
  "Uma corda tocada sobe sozinha e abre no alto um portal invisível para um espaço "
  "extradimensional que abriga até oito criaturas. Quem está dentro não é alcançado de fora; ao "
  "acabar, todos caem.",
 "Cordão de Flechas":
  "Finca até quatro flechas ou dardos no seu espaço. Por 8 horas, quem passar ou terminar o turno "
  "a 9 m delas é atingido por uma: salvaguarda de Destreza ou 2d4 de dano Perfurante. A munição "
  "usada é destruída.",
 "Coroa da Loucura":
  "Um Humanoide à vista faz salvaguarda de Sabedoria ou fica Enfeitiçado. A cada turno dele, "
  "antes de se mover, ele precisa atacar corpo a corpo alguém que você escolher mentalmente. "
  "Se você não escolher, ele age normalmente.",
 "Corrente de Relâmpagos":
  "Um raio no alvo e mais três que saltam para alvos a até 9 m dele. Cada um faz salvaguarda de "
  "Destreza: 10d8 de dano Elétrico, metade se passar. Cada alvo é atingido por um só raio.",
 "Crescer Espinhos":
  "Esfera de 6 m de raio vira Terreno Difícil camuflado por 10 minutos. Quem se mover na área "
  "sofre 2d4 de dano Perfurante a cada 1,5 m percorrido.",
 "Crescimento de Plantas":
  "Conjurada como ação: Crescimento Excessivo faz as plantas numa Esfera de 30 m de raio "
  "cobrarem 4 m de deslocamento por metro andado. Conjurada em 8 horas: Fertilização enriquece a "
  "terra num raio de 800 m, dobrando a colheita por um ano.",
 "Criação":
  "Cria um objeto de matéria vegetal ou mineral de até um Cubo de 1,5 m, com forma e material que "
  "você já viu. A duração depende do material — do mais efêmero ao mais durável — e o objeto "
  "some quando ela acaba.",
 "Criar Chamas":
  "Uma chama fria na mão por 10 minutos: Luz Plena em 6 m e Meia-luz por mais 6 m. Pode ser "
  "arremessada com uma ação Usar Magia — ataque mágico à distância a 18 m por 1d8 de dano Ígneo.",
 "Criar Comida e Água":
  "20 kg de comida simples e 120 litros de água potável. A comida estraga em 24 horas.",
 "Criar Mortos-Vivos":
  "Só à noite. Até três cadáveres Humanoides Médios ou Pequenos viram Carniçais sob seu comando "
  "(Ação Bônus, a até 36 m). O controle dura 24 horas e precisa ser renovado.",
 "Criar ou Destruir Água":
  "Cria até 40 litros de água limpa (num recipiente ou como chuva num Cubo de 9 m, apagando "
  "chamas expostas) ou destrói o mesmo volume, ou dispersa uma névoa no mesmo Cubo.",
 "Criar Passagem":
  "Abre por 1 hora uma passagem de até 1,5 m × 2,5 m × 6 m de profundidade em madeira, gesso ou "
  "pedra, sem comprometer a estrutura. Quem estiver dentro quando fechar é ejetado em segurança.",
 "Cúpula Antivida":
  "Emanação de 3 m que barra a passagem de tudo que não seja Constructo ou Morto-Vivo. Magias e "
  "ataques à distância atravessam. Acaba se você forçar a barreira contra alguém afetado.",
 "Cura Completa":
  "Restaura 70 Pontos de Vida numa criatura à vista e remove Cego, Envenenado e Surdo.",
 "Cura Completa em Massa":
  "Distribui até 700 Pontos de Vida entre quantas criaturas à vista você quiser, removendo Cego, "
  "Envenenado e Surdo de cada uma.",
 "Curar Ferimentos":
  "Toque: restaura 2d8 + seu modificador de conjuração em Pontos de Vida.",
})

DESCRICOES.update({
 # ---------------------------------------------------------------- C - D
 "Curar Ferimentos em Massa":
  "Até seis criaturas numa Esfera de 9 m de raio recuperam 5d8 + seu modificador de conjuração "
  "em Pontos de Vida cada.",
 "Danação":
  "Amaldiçoa uma criatura à vista: seus acertos nela causam 1d6 de dano Necrótico extra, e ela "
  "tem Desvantagem nos testes de um atributo à sua escolha. Se ela cair a 0 Pontos de Vida, "
  "Ação Bônus para transferir a maldição a outra criatura.",
 "Dança Irresistível de Otto":
  "Salvaguarda de Sabedoria. Passando, o alvo dança até o fim do próximo turno dele. Falhando, "
  "fica Enfeitiçado, gasta todo o movimento dançando no lugar, tem Desvantagem em salvaguardas "
  "de Destreza e em ataques, e quem ataca ele tem Vantagem. Repete a salvaguarda no fim de cada "
  "turno dele.",
 "De Carne para Pedra":
  "Salvaguarda de Constituição ou o alvo fica Contido enquanto vira pedra; Constructos passam "
  "automaticamente. Repete no fim de cada turno: três sucessos encerram a magia, três falhas "
  "petrificam de vez. Passando de primeira, só perde o Deslocamento até o início do seu turno.",
 "Dedo da Morte":
  "Salvaguarda de Constituição: 7d8 + 30 de dano Necrótico, metade se passar. Humanoide morto "
  "por ela levanta como Zumbi sob suas ordens no início do seu próximo turno.",
 "Defensor da Fé":
  "Um defensor espectral Grande, intocável, paira por 8 horas. Inimigo que entrar ou começar o "
  "turno a 3 m dele faz salvaguarda de Destreza: 20 de dano Radiante, metade se passar. Ação "
  "Bônus para movê-lo até 9 m.",
 "Desejo":
  "Duplica qualquer magia de 8º círculo ou inferior, sem precisar atender requisitos nem pagar "
  "componentes caros. Ou produz um dos efeitos listados — trocar um talento, restaurar Pontos de "
  "Vida de até vinte criaturas, conceder Resistência, dar Imunidade a uma magia, desfazer um "
  "resultado recente. Usar além da duplicação custa caro: 1d10 de dano Energético por círculo da "
  "magia imitada, Exaustão, −4 em Força por dias, e 33% de nunca mais poder conjurá-la.",
 "Desintegrar":
  "Raio verde numa criatura, objeto não mágico ou criação de energia. Salvaguarda de Destreza ou "
  "10d6 + 40 de dano Energético; quem cair a 0 vira pó, e só volta por Desejo ou Ressurreição "
  "Verdadeira.",
 "Despedaçar":
  "Esfera de 3 m de raio: salvaguarda de Constituição, 3d8 de dano Trovejante, metade se passar. "
  "Constructo tem Desvantagem. Objetos soltos também sofrem o dano.",
 "Despertar":
  "Dá Inteligência 10 e fala a uma Fera ou Planta de Inteligência 3 ou menos, ou a uma planta "
  "comum (que vira criatura do tipo Planta e passa a se mover). O alvo fica Enfeitiçado por 30 "
  "dias e depois guarda a atitude conforme você o tratou.",
 "Despistar":
  "Você fica Invisível e uma cópia ilusória sua aparece no seu lugar. A invisibilidade acaba se "
  "você atacar, causar dano ou conjurar; a cópia dura a magia inteira. Ação Usar Magia para movê-la "
  "até o dobro do seu Deslocamento e fazê-la falar e gesticular; você vê e ouve pelos olhos dela.",
 "Destruição Atordoante":
  "Golpe: +4d6 de dano Psíquico e salvaguarda de Sabedoria ou o alvo fica Atordoado até o fim do "
  "seu próximo turno.",
 "Destruição Banidora":
  "Golpe: +5d10 de dano Energético. Se o ataque deixar o alvo com 50 Pontos de Vida ou menos, "
  "salvaguarda de Carisma ou ele vai Incapacitado para um semiplano até a magia acabar.",
 "Destruição Cauterizante":
  "Golpe: +1d6 de dano Ígneo, e o alvo continua queimando — 1d6 no início de cada turno dele, com "
  "salvaguarda de Constituição para apagar.",
 "Destruição Cegante":
  "Golpe: +3d8 de dano Radiante e o alvo fica Cego, repetindo salvaguarda de Constituição no fim "
  "de cada turno dele.",
 "Destruição Colérica":
  "Golpe: +1d6 de dano Necrótico e salvaguarda de Sabedoria ou o alvo fica Amedrontado, repetindo "
  "a salvaguarda no fim de cada turno dele.",
 "Destruição Divina":
  "Golpe: +2d8 de dano Radiante, +1d8 a mais se o alvo for Ínfero ou Morto-Vivo.",
 "Destruição Estrondosa":
  "Golpe: +2d6 de dano Trovejante, com estrondo ouvido a 90 m. Salvaguarda de Força ou o alvo é "
  "empurrado 3 m e fica Caído.",
 "Destruição Radiante":
  "Golpe: +2d6 de dano Radiante. O alvo passa a emitir Luz Plena em 1,5 m, sofre ataques com "
  "Vantagem e não se beneficia da condição Invisível.",
 "Detectar Magia":
  "Sente efeitos mágicos a até 9 m. Com uma ação Usar Magia, vê a aura e descobre a escola de "
  "cada um. Bloqueada por 30 cm de pedra, terra ou madeira, 2,5 cm de metal ou uma folha de chumbo.",
 "Detectar o Bem e o Mal":
  "Sente onde estão Aberrações, Celestiais, Elementais, Feéricos, Ínferos e Mortos-Vivos a até 9 m, "
  "e se há Consagrar ativa. Mesmos bloqueios de Detectar Magia.",
 "Detectar Pensamentos":
  "Sentir Pensamentos localiza quem pensa a até 9 m e o que está pensando. Sondar Mente escolhe "
  "uma criatura à vista a 9 m: salvaguarda de Inteligência ou você lê a superfície da mente dela; "
  "insistir permite vasculhar mais fundo, mas ela percebe.",
 "Detectar Veneno e Doença":
  "Sente venenos, criaturas venenosas ou peçonhentas e contágios mágicos a até 9 m, e de que tipo "
  "cada um é. Mesmos bloqueios de Detectar Magia.",
 "Disco Flutuante de Tenser":
  "Um disco de energia de 1 m de diâmetro flutuando a 1 m do chão, carregando até 225 kg por "
  "1 hora. Segue você a até 6 m; some se ficar a mais de 30 m ou se você exceder o peso.",
 "Disfarçar-se":
  "Muda sua aparência e a de tudo que veste por 1 hora — até 30 cm mais alto ou mais baixo, com a "
  "mesma disposição de membros. É ilusão: não resiste a inspeção física.",
 "Dissipar Magia":
  "Encerra magias de 3º círculo ou inferior no alvo. Para as de 4º ou superior, teste de atributo "
  "de conjuração contra CD 10 + o círculo da magia. Usando espaço superior, encerra "
  "automaticamente tudo de círculo igual ou menor ao espaço gasto.",
 "Dissipar o Bem e o Mal":
  "Celestiais, Elementais, Feéricos, Ínferos e Mortos-Vivos atacam você com Desvantagem. Pode ser "
  "gasta antes do fim para Exorcizar (manda um deles de volta ao plano de origem, salvaguarda de "
  "Carisma) ou para Repelir (empurra um a 9 m).",
 "Dominar Fera":
  "Uma Fera à vista faz salvaguarda de Sabedoria ou fica Enfeitiçada, com vínculo telepático: "
  "você comanda e ela obedece; gastando a ação, controla o turno dela por inteiro. Tem Vantagem "
  "na salvaguarda se estiver lutando com vocês, e repete a cada dano sofrido.",
 "Dominar Monstro":
  "Como Dominar Fera, mas qualquer criatura, e por até 1 hora.",
 "Dominar Pessoa":
  "Como Dominar Fera, mas contra Humanoides.",
 "Duelo Compelido":
  "Salvaguarda de Sabedoria ou o alvo ataca com Desvantagem qualquer um que não seja você e não "
  "pode se afastar mais de 9 m de você. Acaba se você atacar outra criatura, conjurar magia num "
  "outro inimigo, um aliado seu ferir o alvo, ou você terminar o turno a mais de 9 m dele.",
})

DESCRICOES.update({
 # ---------------------------------------------------------------- E - G
 "Elementalismo":
  "Um efeito elemental menor: névoa que umedece um Cubo de 1,5 m ou 1 xícara de água; brisa "
  "forte o bastante para mover objetos leves; uma chama que cabe na mão; ou moldar terra e "
  "areia num Cubo de 1,5 m.",
 "Emaranhar":
  "Plantas cobrem um quadrado de 6 m e o tornam Terreno Difícil. Quem estiver lá na conjuração "
  "faz salvaguarda de Força ou fica Contido; o Contido pode gastar a ação para repetir um teste "
  "de Força e se soltar.",
 "Encarnação Fantasmagórica":
  "Esfera de 9 m de raio: salvaguarda de Sabedoria, 10d10 de dano Psíquico e a condição "
  "Amedrontado (metade do dano se passar). O Amedrontado repete no fim de cada turno dele, "
  "sofrendo 5d10 de dano Psíquico a cada falha.",
 "Encontrar Armadilhas":
  "Sente a presença de qualquer armadilha à vista no alcance — mecânica ou mágica —, mas só "
  "que existe uma, não onde nem de que tipo. Perigo natural não conta.",
 "Encontrar o Caminho":
  "Sente a rota física mais direta para um lugar que você conhece, no mesmo plano. Não vale "
  "para destino móvel nem inespecífico. Enquanto durar, você sabe a distância e a direção e "
  "não pode se perder por meios não mágicos.",
 "Enfeitiçar Monstro":
  "Uma criatura à vista faz salvaguarda de Sabedoria (com Vantagem se estiver lutando com "
  "vocês) ou fica Enfeitiçada e Amigável por 1 hora, ou até você ou um aliado feri-la. Ao "
  "acabar, ela sabe que foi enfeitiçada.",
 "Enfeitiçar Pessoa":
  "Como Enfeitiçar Monstro, mas contra Humanoides.",
 "Escalada de Aranha":
  "Toque: o alvo anda por paredes e tetos com as mãos livres e ganha Deslocamento de Escalada "
  "igual ao dele.",
 "Escrita Ilusória":
  "Um texto que só você e quem você escolher leem normalmente; para os outros vira um alfabeto "
  "indecifrável. Visão Verdadeira lê o texto de verdade.",
 "Escudo Arcano":
  "Reação: +5 de CA até o início do seu próximo turno, valendo já contra o ataque que disparou "
  "a magia, e imunidade a Mísseis Mágicos.",
 "Escudo Ardente":
  "Chamas ao redor do corpo por 10 minutos, com Luz Plena em 3 m. Escolha quente (Resistência a "
  "Gélido) ou frio (Resistência a Ígneo). Quem acertar você corpo a corpo a 1,5 m sofre 2d8 do "
  "tipo oposto ao escudo.",
 "Escudo da Fé":
  "+2 de CA numa criatura à sua escolha por até 10 minutos.",
 "Escuridão":
  "Esfera de 4,5 m de raio de escuridão mágica, ou uma Emanação de 4,5 m a partir de um objeto "
  "(que pode ser coberto para desligar). Visão no escuro não atravessa e luz não mágica não "
  "ilumina.",
 "Esfera Congelante de Otiluke":
  "Esfera de 18 m de raio: salvaguarda de Constituição, 10d6 de dano Gélido, metade se passar. "
  "Sobre água, congela 15 cm de superfície numa área de 9 m por 1 minuto.",
 "Esfera Flamejante":
  "Uma esfera de fogo de 1,5 m no chão por até 1 minuto. Quem terminar o turno a 1,5 m dela "
  "faz salvaguarda de Destreza: 2d6 de dano Ígneo, metade se passar. Ação Bônus para rolá-la "
  "até 9 m; passar por cima de uma criatura força a salvaguarda.",
 "Esfera Resiliente de Otiluke":
  "Envolve um alvo Grande ou menor numa esfera impenetrável (salvaguarda de Destreza se for "
  "involuntário). Nada entra nem sai, e quem está dentro respira. A esfera é imune a dano e "
  "pode ser empurrada com metade do Deslocamento.",
 "Esfera Vitriólica":
  "Esfera de 6 m de raio: salvaguarda de Destreza, 10d4 de dano Ácido mais 5d4 no fim do "
  "próximo turno do alvo; passando, só metade do dano inicial.",
 "Espada de Mordenkainen":
  "Uma espada espectral que ataca ao aparecer e depois a cada Ação Bônus: ataque mágico corpo a "
  "corpo por 4d12 + seu modificador de conjuração de dano Energético. Ação Bônus também move a "
  "espada até 9 m.",
 "Espinho Mental":
  "Salvaguarda de Sabedoria: 3d8 de dano Psíquico, metade se passar. Falhando, você sabe onde o "
  "alvo está enquanto a magia durar, e ele tem Desvantagem em testes de atributo.",
 "Esquentar Metal":
  "Um objeto de metal fabricado à vista fica em brasa: 2d8 de dano Ígneo em quem o toca ou "
  "veste, e Ação Bônus para repetir. Quem sofre o dano faz salvaguarda de Constituição ou "
  "solta o objeto, se puder, e tem Desvantagem em ataques e testes até seu próximo turno.",
 "Estática Sináptica":
  "Esfera de 6 m de raio: salvaguarda de Inteligência, 8d6 de dano Psíquico, metade se passar. "
  "Quem falha fica 1 minuto subtraindo 1d6 dos ataques, testes de atributo e salvaguardas de "
  "Constituição para manter Concentração.",
 "Explosão Elemental":
  "Ataque mágico à distância: 1d8 de dano de um tipo à sua escolha entre Ácido, Elétrico, "
  "Gélido, Ígneo, Psíquico, Trovejante e Venenoso. Cada 8 no dado permite rolar outro d8 e "
  "somar, até um teto que cresce com o nível.",
 "Explosão Solar":
  "Esfera de 18 m de raio: salvaguarda de Constituição, 12d6 de dano Radiante e a condição Cego "
  "por 1 minuto (metade do dano e sem cegueira se passar). O Cego repete no fim de cada turno "
  "dele. Também dissipa Escuridão mágica na área.",
 "Fabricar":
  "Transforma matéria-prima à vista em um produto do mesmo material — um objeto Grande ou "
  "menor, ou vários Médios. Precisa de proficiência com a ferramenta se o item for algo de "
  "artesão; não cria itens mágicos nem obras que exijam grande perícia.",
 "Faca de Gelo":
  "Ataque mágico à distância por 1d10 de dano Perfurante; acertando ou errando, o fragmento "
  "explode: o alvo e quem estiver a 1,5 m fazem salvaguarda de Destreza ou sofrem 2d6 de dano "
  "Gélido.",
 "Fagulha Estelar":
  "Ataque mágico à distância: 1d8 de dano Radiante, e até o fim do seu próximo turno o alvo "
  "emite Meia-luz em 3 m e não se beneficia da condição Invisível.",
 "Falar com Animais":
  "Por 10 minutos, entende e conversa com Feras, e pode usar a ação Influenciar com elas. Elas "
  "sabem pouco além de sobrevivência e do que passou por perto.",
 "Falar com Mortos":
  "Um cadáver com boca responde até cinco perguntas, com o que sabia em vida — nem mais. Não "
  "funciona se a criatura já era Morto-Vivo, nem no mesmo cadáver duas vezes em 10 dias.",
 "Falar com Plantas":
  "Emanação imóvel de 9 m: as plantas conversam com você e contam o que passou nas últimas 24 "
  "horas, obedecem a ordens simples, e você pode desfazer ou criar Terreno Difícil vegetal.",
 "Favor Divino":
  "Seus ataques com arma causam 1d4 de dano Radiante adicional por 1 minuto.",
 "Flecha Ácida de Melf":
  "Ataque mágico à distância: 4d4 de dano Ácido mais 2d4 no fim do próximo turno do alvo; "
  "errando, metade do dano inicial.",
 "Flecha Relâmpago":
  "O ataque vira um relâmpago: o alvo sofre 4d8 de dano Elétrico no acerto (metade no erro) em "
  "vez do dano normal, e quem estiver a 3 m dele faz salvaguarda de Destreza ou sofre 2d8.",
 "Fogo das Fadas":
  "Cubo de 6 m: objetos ficam delineados por luz, e criaturas também se falharem numa "
  "salvaguarda de Destreza. Os afetados emitem Meia-luz em 3 m, não se beneficiam de "
  "Invisível, e sofrem ataques com Vantagem.",
 "Fome de Hadar":
  "Esfera de Escuridão de 6 m de raio, Terreno Difícil, onde nenhuma luz entra. Quem começa o "
  "turno lá sofre 2d6 de dano Gélido; quem termina faz salvaguarda de Destreza ou sofre 2d6 de "
  "dano Necrótico.",
 "Fonte do Luar":
  "Luz fria em volta de você por 10 minutos: Resistência a dano Radiante e +2d6 de dano "
  "Radiante nos seus ataques corpo a corpo. Reação, depois de sofrer dano de alguém à vista a "
  "18 m: salvaguarda de Constituição do agressor ou 2d6 Radiante e Desvantagem no próximo "
  "ataque dele.",
 "Força Espectral":
  "Salvaguarda de Inteligência ou o alvo passa a perceber uma ilusão de até um cubo de 3 m — "
  "com som e temperatura — que só ele vê. Ele pode gastar a ação para estudá-la e repetir a "
  "salvaguarda; a ilusão pode causar dano psíquico se for algo perigoso.",
 "Forma Etérea":
  "Você entra na Fronteira Etérea por até 8 horas: atravessa matéria, vê o plano de origem em "
  "cinza a até 9 m, e nada do plano normal o afeta. Terminar dentro de um sólido o joga para "
  "fora com dano.",
 "Forma Gasosa":
  "Toque: o alvo vira névoa por até 1 hora — Deslocamento de Voo 3 m com pairar, Resistência a "
  "Contundente, Cortante e Perfurante, passa por frestas. Não pode atacar, conjurar nem usar "
  "objetos.",
 "Formas Animais":
  "Qualquer número de criaturas voluntárias vira Fera Grande ou menor de ND até 4, por 24 "
  "horas. As estatísticas são as da Fera, guardando personalidade, INT, SAB e CAR. Ação Usar "
  "Magia para transformar de novo.",
 "Gargalhada Nefasta de Tasha":
  "Salvaguarda de Sabedoria ou o alvo fica Caído e Incapacitado, rindo sem parar e sem poder "
  "levantar sozinho. Repete a salvaguarda no fim de cada turno e a cada dano sofrido, com "
  "Vantagem se a Inteligência dele for 4 ou menos.",
})

DESCRICOES.update({
 # ---------------------------------------------------------------- G - L
 "Glifo de Proteção":
  "Um glifo escondido numa superfície ou objeto que dispara num gatilho definido por você. "
  "Escolha: Runa Explosiva (Esfera de 6 m, salvaguarda de Destreza, 5d8 de um tipo de dano à "
  "sua escolha) ou Glifo de Magia (guarda uma magia de círculo até o desta, conjurada no "
  "disparo). Dura até ser dissipada ou acionada.",
 "Globo de Invulnerabilidade":
  "Emanação de 3 m: magia de 5º círculo ou inferior conjurada de fora não afeta nada dentro. "
  "Espaço superior sobe o círculo bloqueado.",
 "Golpe Certeiro":
  "Um ataque com a arma da conjuração usando o atributo de conjuração no ataque e no dano, e "
  "podendo trocar o tipo de dano por Radiante.",
 "Golpe Constritor":
  "Ao acertar, vinhas prendem o alvo: salvaguarda de Força (Vantagem se for Grande ou maior) ou "
  "fica Contido, sofrendo 1d6 de dano Perfurante no início de cada turno dele e repetindo a "
  "salvaguarda.",
 "Golpe de Arço":
  "Ataque mágico corpo a corpo contra até cinco criaturas à vista: 6d10 de dano Energético em "
  "cada acerto. Depois você se teleporta para junto de um dos alvos.",
 "Graxa":
  "Quadrado de 3 m vira Terreno Difícil escorregadio por 1 minuto. Quem está lá ao aparecer, "
  "entra ou termina o turno faz salvaguarda de Destreza ou fica Caído.",
 "Guardiões Espirituais":
  "Emanação de 4,5 m em volta de você por até 10 minutos. Inimigos na área têm o Deslocamento "
  "reduzido à metade e, ao entrar ou começar o turno nela, fazem salvaguarda de Sabedoria: 3d8 "
  "de dano Radiante (ou Necrótico, se você for mau), metade se passar.",
 "Heroísmo":
  "Toque: imunidade a Amedrontado e Pontos de Vida Temporários iguais ao seu modificador de "
  "conjuração no início de cada turno do alvo.",
 "Identificar":
  "Descobre as propriedades de um item mágico, se exige Sintonização, quantas cargas tem e "
  "quais magias o afetam. Numa criatura, revela as magias ativas nela. Não detecta itens "
  "amaldiçoados.",
 "Ilusão Menor":
  "Um som ou a imagem de um objeto (até um Cubo de 1,5 m), por 1 minuto. A imagem é só visual e "
  "não faz som; o som pode ser qualquer volume. Um teste de Investigação contra sua CD revela a "
  "ilusão.",
 "Ilusão Programada":
  "Uma ilusão de até um Cubo de 9 m, com som, que fica invisível até um gatilho que você define "
  "e então roda por até 5 minutos. Dura até ser dissipada.",
 "Imagem Maior":
  "Ilusão de até um Cubo de 6 m com som, cheiro e temperatura, que você pode mover e alterar "
  "com uma ação Usar Magia. Não causa dano. Investigação revela.",
 "Imagem Silenciosa":
  "Ilusão puramente visual de até um Cubo de 4,5 m, movida com uma ação Usar Magia. Sem som, "
  "cheiro ou temperatura. Investigação revela.",
 "Indetectável":
  "Por 8 horas, o alvo tocado — criatura, lugar ou objeto de até 3 m — fica fora do alcance de "
  "magias de Adivinhação e de sensores mágicos.",
 "Infligir Ferimentos":
  "Toque: salvaguarda de Constituição, 2d10 de dano Necrótico, metade se passar.",
 "Inseto Gigante":
  "Invoca uma aranha, centopeia ou vespa gigante com o bloco Inseto Gigante, por até 10 "
  "minutos. Aliada, age no seu turno, obedece a comandos verbais.",
 "Inverter a Gravidade":
  "Cilindro de 15 m de raio e 30 m de altura com gravidade invertida: tudo que não está fixo "
  "sobe até o topo e cai lá. Salvaguarda de Destreza para se agarrar a algo fixo.",
 "Invisibilidade":
  "Toque: o alvo fica Invisível por até 1 hora, ou até atacar, causar dano ou conjurar.",
 "Invisibilidade Maior":
  "Toque: o alvo fica Invisível por até 1 minuto, e continua mesmo atacando ou conjurando.",
 "Invocação Instantânea de Drawmij":
  "Marca um objeto de até 3 kg e o nome dele numa safira. Depois, uma ação Usar Magia traz o "
  "objeto à sua mão de qualquer lugar do mesmo plano, se ninguém estiver segurando.",
 "Invocar Aberração":
  "Invoca um Espírito Aberrante — Devorador de Mentes, Pseudo-observador ou Slaad — com o bloco "
  "próprio, por até 1 hora. Aliado, age no seu turno, obedece a comandos verbais.",
 "Invocar Animais":
  "Um bando de animais espectrais por até 10 minutos: Vantagem em salvaguardas de Força a 1,5 m "
  "dele e, ao invocar e como Ação Bônus, os animais atacam uma criatura a até 1,5 m — "
  "salvaguarda de Destreza ou 3d10 de dano Perfurante.",
 "Invocar Barragem":
  "Cone de 18 m de armas espectrais: salvaguarda de Destreza, 5d8 de dano Energético, metade se "
  "passar.",
 "Invocar Celestial":
  "Cilindro de 3 m de raio e 12 m de altura. Para cada criatura à vista dentro, escolha Luz "
  "Curativa (recupera 4d12 + seu modificador de conjuração) ou Luz Flamejante (salvaguarda de "
  "Destreza, 6d12 de dano Radiante, metade se passar).",
 "Invocar Constructo":
  "Invoca um Espírito do Constructo de Argila, Metal ou Pedra, com o bloco próprio, por até 1 "
  "hora. Aliado, age no seu turno, obedece a comandos verbais.",
 "Invocar Dragão":
  "Invoca um Espírito Dracônico com o bloco próprio, por até 1 hora. Aliado, age no seu turno, "
  "obedece a comandos verbais.",
 "Invocar Elementais Menores":
  "Emanação de 4,5 m em volta de você por até 10 minutos: seus ataques causam +2d8 de dano "
  "Ácido, Elétrico, Gélido ou Ígneo (à escolha no ataque) contra quem estiver na área, que "
  "também é Terreno Difícil para seus inimigos.",
 "Invocar Elemental":
  "Um espírito elemental Grande e intangível de água (Gélido), ar (Elétrico), fogo (Ígneo) ou "
  "terra (Trovejante). Quem entra no espaço dele ou começa o turno lá faz salvaguarda de "
  "Destreza ou sofre dano do tipo escolhido.",
 "Invocar Feérico":
  "Um espírito feérico Médio que ataca ao aparecer e a cada Ação Bônus: ataque mágico corpo a "
  "corpo por 3d12 + seu modificador de conjuração de dano Psíquico. Move-se com você.",
 "Invocar Fera":
  "Invoca um Espírito Bestial de Água, Ar ou Terra, com o bloco próprio, por até 1 hora. "
  "Aliado, age no seu turno, obedece a comandos verbais.",
 "Invocar Ínfero":
  "Invoca um Espírito Ínfero — Demônio, Diabo ou Yugoloth — com o bloco próprio, por até 1 "
  "hora. Aliado, age no seu turno, obedece a comandos verbais.",
 "Invocar Morto-Vivo":
  "Invoca um Espírito Morto-vivo Esquelético, Fantasmagórico ou Pútrido, com o bloco próprio, "
  "por até 1 hora. Aliado, age no seu turno, obedece a comandos verbais.",
 "Invocar Saraivada":
  "Cilindro de 12 m de raio e 6 m de altura de armas espectrais caindo: salvaguarda de "
  "Destreza, 8d8 de dano Energético, metade se passar.",
 "Invocar Seres da Floresta":
  "Emanação de 3 m em volta de você por até 10 minutos. Quando ela alcança uma criatura à vista "
  "ou alguém entra ou termina o turno nela, salvaguarda de Sabedoria: 5d8 de dano Energético, "
  "metade se passar.",
 "Labirinto":
  "Bane uma criatura à vista para um semiplano labiríntico por até 10 minutos. Ela escapa "
  "gastando a ação Analisar num teste de Investigação CD 20; ao sair, volta ao espaço que "
  "deixou.",
 "Lâmina Flamejante":
  "Uma cimitarra de fogo na mão livre por até 10 minutos, com Luz Plena em 3 m. Ação Usar "
  "Magia para atacar: ataque mágico corpo a corpo por 3d6 de dano Ígneo. Reevoca com Ação "
  "Bônus se soltar.",
 "Lendas e Histórias":
  "Um resumo do que se sabe sobre uma pessoa, lugar ou objeto famoso — incluindo segredos. "
  "Quanto mais você já sabe, mais preciso o resultado.",
 "Lentidão":
  "Até seis criaturas num Cubo de 12 m fazem salvaguarda de Sabedoria: quem falha tem "
  "Deslocamento pela metade, −2 em CA e salvaguardas de Destreza, não pode usar Reação e só "
  "faz uma coisa por turno (ação ou Ação Bônus). Repete a salvaguarda no fim de cada turno.",
 "Leque Cromático":
  "Cone de 4,5 m: salvaguarda de Constituição ou o alvo fica Cego até o fim do seu próximo "
  "turno.",
 "Levitação":
  "Uma criatura ou objeto de até 200 kg sobe 6 m e fica suspenso por até 10 minutos "
  "(salvaguarda de Constituição se for involuntário). O alvo só se move puxando algo fixo; "
  "você o sobe ou desce 6 m com uma ação Usar Magia.",
})

DESCRICOES.update({
 # ---------------------------------------------------------------- L - M
 "Ligação Telepática de Rary":
  "Até oito criaturas voluntárias que falem algum idioma conversam por telepatia a qualquer "
  "distância no mesmo plano, por 1 hora.",
 "Limpar a Mente":
  "Por 24 horas, o alvo tocado fica imune a dano Psíquico e à condição Enfeitiçado, e invisível "
  "a qualquer Adivinhação — nem Desejo o encontra, lê ou observa à distância.",
 "Línguas":
  "Por 1 hora, o alvo entende qualquer idioma falado ou sinalizado que ouça ou veja, e quem "
  "conhece ao menos um idioma o entende de volta.",
 "Localizar Animais ou Plantas":
  "Descobre a direção e a distância até a Fera, Planta ou planta comum mais próxima do tipo que "
  "você nomear, num raio de 8 km.",
 "Localizar Criatura":
  "Descobre a direção e a posição de uma criatura que você conhece bem, ou da mais próxima de "
  "um tipo, num raio de 300 m. Água corrente de 3 m ou mais bloqueia.",
 "Localizar Objeto":
  "Descobre a direção e a posição de um objeto que você conhece bem (ou do tipo mais próximo) "
  "num raio de 300 m. Chumbo bloqueia.",
 "Loquacidade":
  "Por 1 hora, você pode trocar o resultado de qualquer teste de Carisma por 15, e magia de "
  "detecção de mentira sempre indica que você fala a verdade.",
 "Lufada de Vento":
  "Linha de 18 m por 3 m de vento forte: salvaguarda de Força ou empurrado 4,5 m. Dispersa gás "
  "e névoa, apaga chamas expostas e você pode redirecioná-la com uma Ação Bônus.",
 "Luz":
  "Um objeto tocado emite Luz Plena em 6 m e Meia-luz por mais 6 m, na cor que você quiser, por "
  "1 hora. Cobrir bloqueia.",
 "Luz do Dia":
  "Esfera de 18 m de raio de luz do sol, ou uma Emanação de 18 m a partir de um objeto. "
  "Dissipa Escuridão mágica de círculo 3 ou inferior na área.",
 "Luzes Dançantes":
  "Até quatro luzes do tamanho de tochas, ou uma forma humanoide Média, com Meia-luz em 3 m. "
  "Ação Bônus para movê-las até 18 m.",
 "Malogro":
  "Salvaguarda de Constituição: 8d8 de dano Necrótico, metade se passar. Criatura do tipo "
  "Planta falha automaticamente. Também mata e apodrece vegetação não mágica na área.",
 "Mansão Magnífica de Mordenkainen":
  "Uma porta para uma moradia extradimensional de até cinquenta cubos de 3 m, com criados "
  "invisíveis e um banquete para cem pessoas, por 24 horas. Só quem você designou entra.",
 "Manto do Cruzado":
  "Emanação de 9 m: você e seus aliados causam +1d4 de dano Radiante ao acertar com arma ou "
  "Ataque Desarmado.",
 "Mão de Bigby":
  "Uma mão Grande de energia com CA 20 e Pontos de Vida iguais ao seu máximo. Ação Usar Magia "
  "para: Punho Cerrado (5d8 Energético), Mão Impelidora (empurra), Mão Interposta (Cobertura "
  "Total e freia o avanço) ou Mão Agarradora (agarra e esmaga por 2d6 + modificador).",
 "Mãos Flamejantes":
  "Cone de 4,5 m: salvaguarda de Destreza, 3d6 de dano Ígneo, metade se passar. Objetos "
  "inflamáveis soltos pegam fogo.",
 "Mãos Mágicas":
  "Uma mão espectral a até 9 m por 1 minuto: manipula objetos, abre o que não está trancado, "
  "carrega até 5 kg. Não ataca nem ativa item mágico.",
 "Marca do Predador":
  "Marca uma criatura à vista: +1d6 de dano Energético sempre que você a acerta, e Vantagem em "
  "testes de Percepção ou Sobrevivência para encontrá-la. Se ela cair a 0 Pontos de Vida, "
  "Ação Bônus para marcar outra.",
 "Mau Olhado":
  "Seus olhos viram um vazio. A cada turno, ação Usar Magia para atingir uma criatura à vista a "
  "18 m: salvaguarda de Sabedoria ou o efeito escolhido — Doente (Desvantagem em ataques e "
  "testes), Medo (Amedrontado) ou Sono (Inconsciente até sofrer dano).",
 "Medo":
  "Cone de 9 m: salvaguarda de Sabedoria ou o alvo larga o que segura e fica Amedrontado, "
  "usando Correr para fugir de você. Repete a salvaguarda ao terminar o turno sem você à vista.",
 "Mensageiro Animal":
  "Uma Fera Minúscula leva uma mensagem de até 25 palavras a um lugar que você já visitou e a "
  "um destinatário que você descreva, viajando até 80 km por 24 horas.",
 "Mensagem":
  "Sussurra a uma criatura a até 36 m; só ela ouve e pode responder do mesmo jeito. Atravessa "
  "sólidos se você souber que o alvo está do outro lado, mas não silêncio mágico, 30 cm de "
  "pedra ou uma fina camada de chumbo.",
 "Mesclar-se às Rochas":
  "Você se funde a uma rocha grande o bastante por 8 horas, invisível e indetectável por "
  "sentidos não mágicos. Sente o que passa a até 3 m e sai gastando 1,5 m de deslocamento.",
 "Metamorfose":
  "Você vira outra criatura de ND até o seu nível, que já tenha visto e que não seja Constructo "
  "nem Morto-vivo, por até 1 hora. Assume as estatísticas dela, guardando personalidade, INT, "
  "SAB, CAR e as próprias características de classe.",
 "Miragem Arcana":
  "Faz até 2,5 km² de terreno parecer, soar, cheirar e ser sentido como outro tipo de terreno, "
  "por 10 dias. Não muda o que é sólido de verdade: quem investiga com toque percebe.",
 "Missão":
  "Ordena um serviço a uma criatura à vista que entenda você: salvaguarda de Sabedoria ou fica "
  "Enfeitiçada por 30 dias e obedece. Desobedecer custa 5d10 de dano Psíquico, uma vez por dia. "
  "Ordem claramente suicida cancela a magia.",
 "Mísseis Mágicos":
  "Três dardos que acertam automaticamente criaturas à vista, 1d4 + 1 de dano Energético cada. "
  "Pode dividir entre alvos ou concentrar num só.",
 "Modificar Memória":
  "Salvaguarda de Sabedoria (com Vantagem se você estiver lutando com o alvo) ou ele fica "
  "Enfeitiçado e Incapacitado. Você reescreve uma memória das últimas 24 horas — apagando, "
  "alterando ou inventando. A memória modificada dura como memória comum.",
 "Moldar Rochas":
  "Molda um objeto de pedra Médio ou menor, ou uma seção de até 1,5 m, na forma que quiser — "
  "arma tosca, estátua, passagem numa parede de até 1,5 m de espessura, porta com fechadura.",
 "Moléstia":
  "Salvaguarda de Constituição: 14d6 de dano Necrótico e os Pontos de Vida máximos caem no "
  "mesmo valor; metade do dano se passar. A magia não reduz os Pontos de Vida máximos do "
  "alvo abaixo de 1.",
 "Montaria Fantasmagórica":
  "Uma montaria quase real com sela e rédeas, Deslocamento 30 m, por 1 hora. Viaja 20 km por "
  "hora a passo e 40 km a galope. Some se sofrer dano.",
 "Mover Terra":
  "Remodela terra, areia ou argila numa área de até 12 m de lado por até 2 horas — elevação, "
  "trincheira, muro, pilar. Não afeta pedra nem construção, e as mudanças levam 10 minutos.",
 "Movimentação Livre":
  "Por 1 hora, o alvo ignora Terreno Difícil, não pode ter o Deslocamento reduzido por magia "
  "nem ficar Contido ou Paralisado, ganha Deslocamento de Natação e escapa de agarrões e "
  "prisões gastando 1,5 m de movimento.",
 "Muralha de Energia":
  "Muralha invisível de energia por até 10 minutos: cúpula ou globo de até 3 m de raio, ou dez "
  "painéis de 3 m. Nada atravessa, nem física nem magicamente. Só Desintegrar a destrói.",
 "Muralha de Espinhos":
  "Muralha de espinhos de até 18 m × 3 m, ou um círculo de 6 m de diâmetro. Quem aparece dentro "
  "faz salvaguarda de Destreza (7d8 Perfurante); atravessá-la é Terreno Difícil e custa "
  "salvaguarda de Destreza por 7d8 Cortante.",
 "Muralha de Fogo":
  "Muralha de fogo de até 18 m × 6 m, ou um círculo de 6 m de diâmetro. Um lado escolhido por "
  "você causa 5d8 de dano Ígneo a quem chegar a 3 m ou terminar o turno lá; atravessar custa "
  "salvaguarda de Destreza por 5d8.",
 "Muralha de Gelo":
  "Muralha de gelo em cúpula, globo de 3 m de raio ou dez painéis de 3 m, por 10 minutos. Cada "
  "painel tem CA 12 e 30 Pontos de Vida; quebrar deixa gelo cortante. Quem aparece dentro faz "
  "salvaguarda de Destreza por 10d6 Gélido.",
 "Muralha de Pedra":
  "Muralha de pedra maciça em dez painéis de 3 m, por 10 minutos. Pode ser feita permanente "
  "mantendo Concentração a magia inteira. Quem é envolvido por ela pode fazer salvaguarda de "
  "Destreza para sair.",
 "Muralha de Vento":
  "Muralha de vento de até 15 m × 4,5 m por 1 minuto. Quem entra ou começa o turno nela faz "
  "salvaguarda de Força ou sofre 4d8 de dano Contundente, metade se passar. Barra gás, névoa "
  "e projéteis leves.",
 "Muralha Prismática":
  "Sete camadas de cor, cada uma com um efeito e uma forma de ser desfeita: Vermelha (12d6 "
  "Ígneo), Laranja (12d6 Ácido), Amarela (12d6 Elétrico), Verde (12d6 Venenoso), Azul (12d6 "
  "Gélido), Anil (Contido, virando Petrificado) e Violeta (Cego, e teleporta para outro "
  "plano). Cada camada pede salvaguarda de Destreza, com metade do dano em caso de sucesso. "
  "Atravessar exige vencer camada por camada.",
})

DESCRICOES.update({
 # ---------------------------------------------------------------- N - P
 "Nevasca":
  "Cilindro de 6 m de raio e 12 m de altura de granizo: área Totalmente Obscurecida, chão "
  "Terreno Difícil, chamas expostas apagadas. Quem entra pela primeira vez no turno ou começa "
  "o turno lá faz salvaguarda de Destreza ou fica Caído e perde a Concentração. A magia não "
  "causa dano.",
 "Névoa Mortal":
  "Esfera de 6 m de raio de névoa venenosa que desce e Obscurece Totalmente. Quem começa o "
  "turno lá faz salvaguarda de Constituição: 5d8 de dano Venenoso, metade se passar. Vento "
  "forte dispersa.",
 "Névoa Obscurecente":
  "Esfera de névoa de 6 m de raio, Totalmente Obscurecida, por até 1 hora. Vento forte dispersa.",
 "Nuvem de Adagas":
  "Cubo de 1,5 m de adagas girando: 4d4 de dano Cortante a quem estiver dentro, entrar ou "
  "terminar o turno lá, uma vez por turno. Ação Bônus para mover o cubo até 9 m.",
 "Nuvem Fétida":
  "Esfera de 6 m de raio de gás nauseante, Totalmente Obscurecida. Quem começa o turno lá faz "
  "salvaguarda de Constituição ou fica Envenenado até o fim do turno atual — e, Envenenado "
  "assim, não pode executar ação nem Ação Bônus. Vento forte dispersa.",
 "Nuvem Incendiária":
  "Esfera de 6 m de raio de brasas, Totalmente Obscurecida. Salvaguarda de Destreza ao aparecer "
  "e para quem entrar ou terminar o turno: 10d8 de dano Ígneo, metade se passar. A nuvem se "
  "move 3 m para longe de você no fim de cada turno seu.",
 "Olho Arcano":
  "Um olho invisível e invulnerável que você vê por ele em todas as direções, com Visão no "
  "Escuro de 9 m. Ação Bônus para movê-lo até 9 m; barreira sólida o bloqueia, mas uma fresta "
  "de 2,5 cm passa.",
 "Onda Destrutiva":
  "Emanação de 9 m: salvaguarda de Constituição, 5d6 de dano Trovejante mais 5d6 Necrótico ou "
  "Radiante (à sua escolha) e a condição Caído; metade do dano e sem Caído se passar.",
 "Onda Trovejante":
  "Cubo de 4,5 m a partir de você: salvaguarda de Constituição, 2d8 de dano Trovejante e "
  "empurrado 3 m; metade do dano e sem empurrão se passar. O estrondo é ouvido a 90 m.",
 "Oração de Cura":
  "Até cinco criaturas que fiquem no alcance durante toda a conjuração (10 minutos) ganham os "
  "benefícios de um Descanso Curto e 2d8 Pontos de Vida. Uma criatura só é afetada de novo "
  "depois de um Descanso Longo.",
 "Orbe Cromático":
  "Ataque mágico à distância: 3d8 de dano de um tipo à sua escolha entre Ácido, Elétrico, "
  "Gélido, Ígneo, Trovejante e Venenoso. Se dois ou mais dados saírem iguais, o orbe salta para "
  "outra criatura a até 9 m.",
 "Orientação":
  "Toque: por até 1 minuto, o alvo soma 1d4 aos testes de uma perícia à sua escolha.",
 "Padrão Hipnótico":
  "Cubo de 9 m: quem vê o padrão faz salvaguarda de Sabedoria ou fica Enfeitiçado e "
  "Incapacitado, com Deslocamento 0. Acaba se o alvo sofrer dano ou alguém gastar a ação para "
  "sacudi-lo.",
 "Palavra Curativa":
  "Ação Bônus, a 18 m: o alvo recupera 2d4 + seu modificador de conjuração em Pontos de Vida.",
 "Palavra Curativa em Massa":
  "Ação Bônus: até seis criaturas à vista recuperam 2d4 + seu modificador de conjuração cada.",
 "Palavra de Poder: Atordoar":
  "Alvo com 150 Pontos de Vida ou menos fica Atordoado; acima disso, só perde o Deslocamento "
  "até o início do seu próximo turno. O Atordoado repete salvaguarda de Constituição no fim de "
  "cada turno dele.",
 "Palavra de Poder: Fortificar":
  "120 Pontos de Vida Temporários divididos como você quiser entre até seis criaturas à vista.",
 "Palavra de Poder: Matar":
  "Alvo com 100 Pontos de Vida ou menos morre; acima disso, sofre 12d12 de dano Psíquico.",
 "Palavra de Poder: Salvar":
  "O alvo recupera todos os Pontos de Vida e perde as condições Amedrontado, Atordoado, "
  "Enfeitiçado, Envenenado e Paralisado; se estiver Caído, pode se levantar com a Reação.",
 "Palavra de Radiância":
  "Emanação de 1,5 m: criaturas à sua escolha fazem salvaguarda de Constituição ou sofrem 1d6 "
  "de dano Radiante.",
 "Palavra de Regresso":
  "Teleporta você e até cinco criaturas a 1,5 m para um santuário que você preparou antes com "
  "esta magia. Sem santuário preparado, a magia não faz nada.",
 "Palavra Sagrada":
  "Criaturas à sua escolha a 9 m fazem salvaguarda de Carisma. Quem falha com 50 Pontos de Vida "
  "ou menos sofre um efeito conforme o total — de Surdo a morto, quanto menos vida, pior. Quem "
  "falha, independentemente da vida, também fica Cego por 1 minuto.",
 "Paralisar Monstro":
  "Uma criatura à vista faz salvaguarda de Sabedoria ou fica Paralisada por até 1 minuto, "
  "repetindo no fim de cada turno dela.",
 "Paralisar Pessoa":
  "Como Paralisar Monstro, mas contra Humanoides.",
 "Parar o Tempo":
  "Você joga 1d4 + 1 turnos seguidos enquanto o tempo para para todos os outros. Acaba se você "
  "afetar outra criatura ou um objeto carregado por ela, ou se sair a mais de 300 m de onde "
  "conjurou.",
 "Passo Arbóreo":
  "Você entra numa árvore viva e sai de outra do mesmo tipo a até 150 m, gastando 1,5 m de "
  "movimento para entrar. Sabe onde estão as outras árvores válidas; ficar mais de 1 rodada "
  "dentro exige salvaguarda de Destreza ou dano e expulsão.",
 "Passo Nebuloso":
  "Ação Bônus: você se teleporta até 9 m para um espaço desocupado à vista.",
 "Passo Sem Rastro":
  "Emanação de 9 m: você e quem você escolher ganham +10 em Furtividade e não deixam rastros, "
  "por até 1 hora.",
 "Passos Largos":
  "Toque: +3 m de Deslocamento por 1 hora.",
 "Pele-Casca":
  "Toque: a CA do alvo passa a 17 por 1 hora, se já não for maior.",
 "Pele-Rocha":
  "Toque: Resistência a dano Contundente, Cortante e Perfurante por até 1 hora.",
 "Pequeno Refúgio de Leomund":
  "Uma cúpula de Emanação de 3 m por 8 horas: só quem estava dentro na conjuração entra e sai. "
  "Clima e temperatura confortáveis, luz fraca à sua escolha, e nada atravessa a barreira.",
 "Perdição":
  "Até três criaturas fazem salvaguarda de Carisma; quem falha subtrai 1d4 dos ataques e "
  "salvaguardas enquanto a magia durar.",
 "Piscar":
  "No fim de cada turno seu, 1d6: em 4 a 6 você some para o Plano Etéreo e volta no início do "
  "seu próximo turno, a até 3 m de onde saiu. Enquanto etéreo, nada do plano normal o alcança.",
 "Polimorfia":
  "Salvaguarda de Sabedoria ou o alvo vira uma Fera de ND até o dele, por até 1 hora. Assume as "
  "estatísticas da Fera, mas mantém alinhamento, personalidade, tipo de criatura, Pontos de "
  "Vida e Dados de Vida, e recebe Pontos de Vida Temporários iguais aos PV da forma. Não fala "
  "nem conjura, e a magia acaba quando esses temporários zeram.",
 "Polimorfia Total":
  "Transforma uma criatura noutra criatura ou objeto, ou um objeto em criatura. Criatura "
  "involuntária faz salvaguarda de Sabedoria. Mantida a Concentração pela duração inteira, a "
  "transformação vira permanente.",
 "Porta Dimensional":
  "Você se teleporta para um lugar a até 150 m que veja, visualize ou descreva por distância e "
  "direção, levando uma criatura voluntária a 1,5 m. Chegar em espaço ocupado causa 4d6 de dano "
  "Energético nos dois e cancela o teleporte.",
 "Portais Arcanos":
  "Dois portais ligados no chão, um perto de você e outro a até 150 m, por 10 minutos. Quem "
  "entra num sai do outro.",
 "Portal":
  "Um portal de 1,5 a 6 m para um ponto exato de outro plano, por até 1 minuto. Falando o nome "
  "de uma criatura de outro plano, o portal se abre junto dela e pode trazê-la.",
 "Praga de Insetos":
  "Esfera de 6 m de raio de gafanhotos: Parcialmente Obscurecida e Terreno Difícil. Salvaguarda "
  "de Constituição ao aparecer e para quem entrar ou começar o turno: 4d10 de dano Perfurante, "
  "metade se passar.",
 "Presença Régia de Yolande":
  "Emanação de 3 m por até 1 minuto. Quando ela alcança uma criatura à vista, ou alguém entra "
  "ou termina o turno nela, salvaguarda de Sabedoria: 4d6 de dano Psíquico e a condição Caído, "
  "e você pode empurrá-lo até 3 m; metade do dano em caso de sucesso. Cada criatura faz essa "
  "salvaguarda só uma vez por turno.",
 "Presságio":
  "Uma pergunta sobre um objetivo, evento ou atividade dos próximos 7 dias recebe resposta "
  "verdadeira do Mestre — uma frase curta ou uma rima enigmática.",
 "Prestidigitação Arcana":
  "Um truque menor: acender ou apagar chama pequena, limpar ou sujar um objeto, esquentar ou "
  "esfriar até 500 g por 1 hora, um sinal ou marca que dura 1 hora, uma bugiganga que some no "
  "próximo turno. Até três efeitos não instantâneos ativos ao mesmo tempo.",
 "Proibição":
  "Por 1 dia, uma área de até 3.700 m² e 9 m de altura fica fechada a teleporte e viagem "
  "planar. Você pode escolher um tipo de criatura que atravessa livremente, e nomear uma senha. "
  "Criaturas dos tipos que você escolher sofrem 5d10 de dano ao entrar.",
 "Projeção Astral":
  "Você e até oito criaturas projetam corpos astrais no Plano Astral, deixando os corpos "
  "Inconscientes e em animação suspensa. O cordão de prata liga os dois; cortá-lo mata. Dura "
  "até ser dissipada.",
})

DESCRICOES.update({
 # ---------------------------------------------------------------- P - S
 "Projetar Imagem":
  "Uma cópia ilusória sua num lugar que você já viu, a até 800 km, por até 1 dia. Você vê e "
  "ouve por ela e a move com uma ação Usar Magia. Some se sofrer dano; investigar de perto "
  "revela.",
 "Proteção Contra a Morte":
  "Por 8 horas, a primeira vez que o alvo cairia a 0 Pontos de Vida ele fica com 1 e a magia "
  "acaba. Também barra efeitos de morte instantânea.",
 "Proteção Contra Energia":
  "Toque: Resistência a Ácido, Elétrico, Gélido, Ígneo ou Trovejante, à sua escolha, por até "
  "1 hora.",
 "Proteção Contra Lâminas":
  "Quem ataca você subtrai 1d4 da jogada de ataque, por até 1 minuto.",
 "Proteção Contra o Bem e o Mal":
  "Por até 10 minutos, Aberrações, Celestiais, Elementais, Feéricos, Ínferos e Mortos-Vivos "
  "atacam o alvo com Desvantagem e não conseguem possuí-lo, enfeitiçá-lo nem amedrontá-lo.",
 "Proteção Contra Veneno":
  "Toque: encerra a condição Envenenado e dá, por 1 hora, Vantagem nas salvaguardas contra ela "
  "e Resistência a dano Venenoso.",
 "Proteger Fortaleza":
  "Por 24 horas, uma área de até 225 m² e 6 m de altura fica protegida: nada de teleporte para "
  "dentro, e você escolhe efeitos como escuridão, terreno difícil ou dano contra os tipos de "
  "criatura que designar.",
 "Purificar Alimentos e Bebidas":
  "Tira veneno e podridão de comida e bebida não mágicas numa Esfera de 1,5 m de raio.",
 "Queda Suave":
  "Reação: até cinco criaturas em queda passam a cair 18 m por rodada e pousam sem dano.",
 "Raio Ardente":
  "Três raios de fogo, cada um com ataque mágico à distância por 2d6 de dano Ígneo. Podem ir "
  "num só alvo ou em vários.",
 "Raio de Bruxa":
  "Ataque mágico à distância por 2d12 de dano Elétrico e, nos turnos seguintes, Ação Bônus para "
  "repetir o dano automaticamente enquanto o alvo estiver à vista e no alcance.",
 "Raio de Fogo":
  "Ataque mágico à distância: 1d10 de dano Ígneo. Objeto inflamável solto pega fogo.",
 "Raio de Gelo":
  "Ataque mágico à distância: 1d8 de dano Gélido e −3 m de Deslocamento do alvo até o início do "
  "seu próximo turno.",
 "Raio do Enfraquecimento":
  "Salvaguarda de Constituição: falhando, o alvo tem Desvantagem em Testes de D20 e repete a "
  "salvaguarda no fim de cada turno dele; passando, só Desvantagem no próximo ataque dele.",
 "Raio Guia":
  "Ataque mágico à distância: 4d6 de dano Radiante, e o próximo ataque contra o alvo até o fim "
  "do seu próximo turno tem Vantagem.",
 "Raio Lunar":
  "Cilindro de 1,5 m de raio e 12 m de altura com Meia-luz. Quem aparece dentro ou começa o "
  "turno lá faz salvaguarda de Constituição: 2d10 de dano Radiante, metade se passar. Ação Usar "
  "Magia move o cilindro até 18 m.",
 "Raio Místico":
  "Ataque mágico à distância: 1d10 de dano Energético. Vira dois feixes no nível 5, três no 11 "
  "e quatro no 17, distribuíveis entre alvos.",
 "Raio Nauseante":
  "Ataque mágico à distância: 2d8 de dano Venenoso e a condição Envenenado até o fim do próximo "
  "turno do alvo.",
 "Raio Solar":
  "Linha de 18 m por 1,5 m: salvaguarda de Constituição, 6d8 de dano Radiante e Cego até o "
  "início do seu próximo turno; metade do dano se passar. Ação Usar Magia para repetir a linha "
  "em turnos seguintes.",
 "Rajada de Veneno":
  "Ataque mágico à distância: 1d12 de dano Venenoso.",
 "Rajada Prismática":
  "Cone de 18 m com oito raios. Cada alvo rola 1d8 para saber qual o atinge, e faz salvaguarda "
  "de Destreza: dano de um tipo por cor (Ígneo, Ácido, Elétrico, Venenoso, Gélido), Contido "
  "virando Petrificado, Cego com teleporte para outro plano, ou dois raios de uma vez.",
 "Receptáculo Arcano":
  "Sua alma passa para o receptáculo, deixando o corpo catatônico. De lá você pode possuir um "
  "Humanoide a até 30 m (salvaguarda de Carisma), usando o corpo dele com a sua mente. Dura até "
  "ser dissipada.",
 "Reencarnar":
  "Um Humanoide morto há no máximo 10 dias volta num corpo novo, de espécie sorteada em 1d10 ou "
  "escolhida pelo Mestre, com toda a memória e as características de classe.",
 "Reflexos":
  "Três cópias ilusórias suas por 1 minuto. Ataque contra você pode acertar uma cópia (CA 10 + "
  "seu modificador de Destreza), que some. Perde o efeito se você ficar Cego ou o atacante tiver "
  "Visão Verdadeira.",
 "Refugiar":
  "Esconde um objeto ou criatura voluntária: fica Invisível, fora de Adivinhação e, se for "
  "criatura, em animação suspensa e Inconsciente. Dura até ser dissipada ou até a condição de "
  "término que você definir.",
 "Regeneração":
  "Toque: 4d8 + 15 Pontos de Vida na hora, mais 1 no início de cada turno por 1 hora; membros "
  "decepados voltam a crescer em 2 minutos.",
 "Relâmpago":
  "Linha de 30 m por 1,5 m: salvaguarda de Destreza, 8d6 de dano Elétrico, metade se passar.",
 "Remeter":
  "Manda uma mensagem de até 25 palavras a alguém que você já encontrou, a qualquer distância, "
  "e recebe uma resposta imediata. Entre planos, 5% de chance de não chegar.",
 "Remover Maldição":
  "Toque: encerra todas as maldições numa criatura ou objeto. Item amaldiçoado continua "
  "amaldiçoado, mas a Sintonização é quebrada e ele pode ser largado.",
 "Reparar":
  "Conserta uma única ruptura ou rasgo de até 30 cm num objeto tocado, sem deixar marca. Não "
  "restaura magia.",
 "Repouso Tranquilo":
  "Um cadáver fica protegido da decomposição e não pode virar Morto-Vivo por 10 dias, e esses "
  "dias não contam para o prazo das magias de ressurreição.",
 "Repreensão Diabólica":
  "Reação contra quem lhe causou dano: salvaguarda de Destreza, 2d10 de dano Ígneo, metade se "
  "passar.",
 "Resistência":
  "Toque: por até 1 minuto, o alvo reduz em 1d4 o dano da primeira vez que sofrer o tipo de "
  "dano que você escolheu.",
 "Respirar na Água":
  "Até dez criaturas respiram debaixo d'água por 24 horas, sem perder o modo normal de "
  "respirar.",
 "Ressurreição":
  "Revive quem morreu há no máximo um século (não de velhice, não Morto-Vivo) com todos os "
  "Pontos de Vida, fechando feridas, neutralizando venenos e restaurando membros. O alvo fica "
  "com −4 em Testes de D20, que some 1 por Descanso Longo.",
 "Ressurreição Verdadeira":
  "Revive quem morreu há no máximo 200 anos por qualquer causa exceto velhice, com todos os "
  "Pontos de Vida, curando tudo e restaurando o corpo — ou criando um novo, se não houver.",
 "Restauração Maior":
  "Toque: remove um destes — 1 nível de Exaustão, a condição Enfeitiçado ou Petrificado, uma "
  "maldição, uma redução de atributo ou uma redução dos Pontos de Vida máximos.",
 "Restauração Menor":
  "Toque: remove uma condição entre Cego, Envenenado, Paralisado e Surdo.",
 "Retirada Acelerada":
  "Você Corre agora e pode Correr de novo como Ação Bônus a cada turno, por até 10 minutos.",
 "Reviver os Mortos":
  "Revive quem morreu há no máximo 10 dias, com 1 Ponto de Vida, neutralizando venenos e "
  "fechando ferimentos fatais. Não restaura membros.",
 "Revivificar":
  "Revive quem morreu no último minuto, com 1 Ponto de Vida. Não vale para morte por velhice e "
  "não restaura membros.",
 "Rogar Maldição":
  "Toque: salvaguarda de Sabedoria ou o alvo fica amaldiçoado por até 1 minuto, com um efeito à "
  "sua escolha — Desvantagem num atributo, Desvantagem em ataques contra você, gastar a ação a "
  "cada turno sem fazer nada, ou +1d8 de dano Necrótico dos seus ataques contra ele.",
 "Salto":
  "Toque: uma vez por turno, o alvo salta até 9 m gastando 3 m de movimento, por 1 minuto.",
 "Santuário":
  "Por 1 minuto, quem tentar atacar o protegido ou alvejá-lo com magia de dano faz salvaguarda "
  "de Sabedoria ou precisa trocar de alvo. Não protege de efeitos em área, e acaba se o "
  "protegido atacar ou lançar magia prejudicial.",
 "Santuário Particular de Mordenkainen":
  "Um Cubo de 1,5 a 30 m protegido por 24 horas, com as propriedades que você escolher: som não "
  "atravessa, não dá para ver de fora, luz não entra nem sai, sensores de Adivinhação barrados, "
  "e teleporte e viagem planar bloqueados.",
 "Saraivada de Espinhos":
  "Ao acertar com arma à distância, espinhos brotam: o alvo e quem estiver a 1,5 m fazem "
  "salvaguarda de Destreza por 1d10 de dano Perfurante, metade se passar.",
 "Semiplano":
  "Uma porta de sombras para uma sala vazia de 9 m em cada dimensão, por 1 hora. Reconjurar na "
  "mesma porta volta ao mesmo semiplano, e pode ligar dois semiplanos seus.",
 "Sentido Feral":
  "Toque numa Fera voluntária: por até 1 hora você percebe pelos sentidos dela além dos seus, "
  "aproveitando os sentidos especiais que ela tiver.",
 "Servo Invisível":
  "Uma força invisível Média com CA 10, 1 Ponto de Vida e Força 2, por 1 hora. Faz tarefas "
  "simples com uma Ação Bônus sua; não ataca.",
 "Sexto Sentido":
  "Toque: por 8 horas, o alvo tem Vantagem em todos os Testes de D20 e quem o ataca tem "
  "Desvantagem.",
})

DESCRICOES.update({
 # ---------------------------------------------------------------- S - Z
 "Silêncio":
  "Esfera de 6 m de raio sem som nenhum: quem está totalmente dentro fica Surdo e imune a dano "
  "Trovejante, e magia com componente Verbal não pode ser conjurada ali.",
 "Símbolo":
  "Um glifo escondido que dispara num gatilho definido por você e afeta uma Esfera de 18 m. "
  "Escolha o efeito: Adormecer, Amedrontar, Atordoar, Dor, Enlouquecer, Morte ou Discórdia. "
  "Dura até ser dissipado ou acionado.",
 "Similaridade":
  "Dá aparência ilusória a quantas criaturas você quiser por 8 horas — alvo involuntário faz "
  "salvaguarda de Carisma. Muda corpo e equipamento, mas não o que se sente ao tocar.",
 "Simulacro":
  "Uma duplicata de neve de uma Fera ou Humanoide, com metade dos Pontos de Vida do original e "
  "sem poder ganhar níveis nem recuperar espaços de magia. Obedece a você e vira neve ao chegar "
  "a 0 Pontos de Vida. Só um simulacro por vez.",
 "Simular Morte":
  "Toque: o alvo parece morto por 1 hora, mesmo para magia — Cego, Incapacitado, Deslocamento "
  "0, com Resistência a tudo menos Psíquico e imunidade a Envenenado e a doenças, cujo avanço "
  "fica suspenso.",
 "Sinal de Esperança":
  "Quantas criaturas você quiser ganham, por até 1 minuto, Vantagem em salvaguardas de "
  "Sabedoria e contra Morte, e recebem o máximo possível de qualquer cura.",
 "Sonho":
  "Você ou um mensageiro que você toca entra em transe e aparece no sonho de uma criatura que "
  "você conhece, no mesmo plano, com a forma e a mensagem que quiser. Feita aparição de "
  "pesadelo, o alvo não descansa e sofre 3d6 de dano Psíquico se falhar numa salvaguarda de "
  "Sabedoria.",
 "Sono":
  "Esfera de 1,5 m de raio: salvaguarda de Sabedoria ou o alvo fica Incapacitado e repete no "
  "fim do próximo turno dele; falhando de novo, fica Inconsciente pela duração ou até sofrer "
  "dano.",
 "Sopro de Dragão":
  "Toque: por até 1 minuto, o alvo pode gastar uma ação Usar Magia para exalar um Cone de 4,5 m "
  "— salvaguarda de Destreza, 3d6 de dano Ácido, Elétrico, Gélido, Ígneo ou Venenoso à sua "
  "escolha, metade se passar.",
 "Sugestão":
  "Uma sugestão de até 25 palavras, que pareça razoável, a uma criatura que ouça e entenda "
  "você: salvaguarda de Sabedoria ou ela fica Enfeitiçada e segue a sugestão por até 8 horas. "
  "Acaba se você ou um aliado ferir o alvo.",
 "Sugestão em Massa":
  "Como Sugestão, mas para até doze criaturas e por 24 horas.",
 "Suplício":
  "Salvaguarda de Inteligência: 10d12 de dano Psíquico e o alvo fica sem conjurar magias nem "
  "usar a ação Usar Magia. Repete a salvaguarda a cada 30 dias.",
 "Sussurros Dissonantes":
  "Salvaguarda de Sabedoria: 3d6 de dano Psíquico e o alvo usa a Reação para fugir de você o "
  "mais longe possível; metade do dano e sem fuga se passar.",
 "Talho Mental":
  "Salvaguarda de Inteligência ou 1d6 de dano Psíquico e −1d4 na próxima salvaguarda do alvo "
  "até o fim do seu próximo turno.",
 "Taumaturgia":
  "Uma maravilha menor: fazer chamas piscarem ou mudarem de cor, abrir ou fechar porta ou "
  "janela sem tocar, mudar sua voz para triplicar o volume por 1 minuto, um tremor no chão, um "
  "som vindo de onde você quiser, ou um sinal ou marca inofensiva. Até três efeitos de 1 minuto "
  "ao mesmo tempo.",
 "Teia":
  "Cubo de 6 m de teias: Terreno Difícil e Parcialmente Obscurecido. Quem entra ou começa o "
  "turno lá faz salvaguarda de Destreza ou fica Contido, escapando com um teste de Força. "
  "Fogo queima as teias, causando 2d4 de dano Ígneo a quem estiver nelas.",
 "Telecinese":
  "Move e manipula com o pensamento por até 10 minutos: uma criatura Enorme ou menor "
  "(salvaguarda de Força) até 9 m em qualquer direção, ou um objeto solto de até 500 kg, "
  "podendo manipulá-lo à distância.",
 "Telepatia":
  "Elo telepático com uma criatura voluntária conhecida, em qualquer lugar do mesmo plano, por "
  "24 horas. Palavras, imagens, sons e sensações passam nos dois sentidos.",
 "Teleporte":
  "Teleporta você e até oito criaturas voluntárias, ou um objeto Grande ou menor, para um "
  "destino no mesmo plano. A precisão depende de quanto você conhece o lugar: um erro pode "
  "levar a alvo aproximado, área semelhante ou desastre.",
 "Tempestade da Vingança":
  "Nuvem de 90 m de raio por até 1 minuto, que a cada rodada muda de efeito: trovão e surdez, "
  "chuva ácida, relâmpagos, granizo, e por fim vento gelado que vira Terreno Difícil e "
  "atrapalha à distância.",
 "Tempestade de Fogo":
  "Até dez cubos de 3 m contíguos, dispostos como você quiser: salvaguarda de Destreza, 7d10 de "
  "dano Ígneo, metade se passar. Você pode poupar a vegetação da área.",
 "Tempestade Glacial":
  "Cilindro de 6 m de raio e 12 m de altura: salvaguarda de Destreza, 2d10 de dano Contundente "
  "mais 4d6 de dano Gélido, metade se passar. A área vira Terreno Difícil por 1 rodada.",
 "Tempestade Radiante de Jallarzi":
  "Cilindro de 3 m de raio e 12 m de altura: quem está dentro fica Cego e Surdo e não conjura "
  "com componente Verbal. Ao aparecer e a cada Ação Bônus sua, salvaguarda de Destreza por 2d10 "
  "de dano Radiante mais 2d10 Trovejante, metade se passar.",
 "Tentáculos Negros de Evard":
  "Quadrado de 6 m de tentáculos: Terreno Difícil. Salvaguarda de Força ao aparecer e para quem "
  "entrar ou começar o turno lá: 3d6 de dano Contundente e a condição Contido, com teste de "
  "Força ou Acrobacia para escapar.",
 "Terremoto":
  "Círculo de 30 m de raio de chão tremendo por até 1 minuto: Terreno Difícil, salvaguarda de "
  "Destreza a cada turno para não ficar Caído, fissuras que engolem quem falha numa segunda "
  "salvaguarda, e estruturas que desabam sobre quem estiver perto.",
 "Terreno Alucinatório":
  "Um cubo de 45 m de terreno natural parece, soa e cheira como outro tipo de terreno, por 24 "
  "horas. Toque revela a ilusão; objetos e criaturas não são disfarçados.",
 "Toque Chocante":
  "Ataque mágico corpo a corpo: 1d8 de dano Elétrico e o alvo não faz Ataques de Oportunidade "
  "até o início do próximo turno dele.",
 "Toque Necrótico":
  "Ataque mágico corpo a corpo: 1d10 de dano Necrótico e o alvo não recupera Pontos de Vida até "
  "o fim do seu próximo turno.",
 "Toque Vampírico":
  "Ataque mágico corpo a corpo: 3d6 de dano Necrótico e você recupera metade do dano em Pontos "
  "de Vida. Repetível a cada turno com uma ação, por até 1 minuto.",
 "Tranca Arcana":
  "Tranca uma porta, janela ou recipiente até ser dissipada. Só você, quem você designar e quem "
  "souber a senha abrem; Arrombar suprime por 10 minutos, e a CD para forçar sobe 10.",
 "Transição Planar":
  "Você e até oito criaturas de mãos dadas viajam para outro plano, num destino descrito em "
  "termos gerais. Também pode ser usada para banir uma criatura tocada de volta ao plano de "
  "origem, com salvaguarda de Carisma.",
 "Transporte via Plantas":
  "Liga por 1 minuto uma planta Grande ou maior a outra planta que você já viu ou tocou, em "
  "qualquer distância do mesmo plano. Quem entra numa sai da outra em 1 rodada.",
 "Trovão":
  "Emanação de 1,5 m: salvaguarda de Constituição ou 1d6 de dano Trovejante. O estrondo é "
  "ouvido a 30 m.",
 "Tsunami":
  "Muralha de água de até 90 m × 90 m × 15 m que avança e desaba: 6d10 de dano Contundente ao "
  "aparecer (salvaguarda de Força), diminuindo 1d10 a cada rodada, por até 6 rodadas.",
 "Turvar":
  "Por até 1 minuto, quem ataca você tem Desvantagem — salvo quem tiver Visão às Cegas ou Visão "
  "Verdadeira.",
 "Ver o Invisível":
  "Por 1 hora, você vê criaturas e objetos Invisíveis e enxerga o Plano Etéreo, que aparece "
  "translúcido.",
 "Vidência":
  "Vê e ouve uma criatura no mesmo plano por até 10 minutos. A salvaguarda de Sabedoria dela é "
  "modificada por quanto você a conhece e por que conexão física você tem com ela.",
 "Vigor Arcano":
  "Gasta um ou dois Dados de Vida não usados e recupera o total rolado mais seu modificador de "
  "conjuração em Pontos de Vida.",
 "Vínculo de Proteção":
  "Toque: enquanto o alvo estiver a 18 m de você, ele ganha +1 de CA e em salvaguardas e "
  "Resistência a todo dano — mas você sofre o mesmo dano que ele sofrer.",
 "Vinha Agarradora":
  "Uma vinha por até 1 minuto: ataque mágico corpo a corpo contra alguém a 9 m dela por 4d8 de "
  "dano Contundente, puxando o alvo até 9 m para junto dela. Ação Bônus para repetir.",
 "Visão da Verdade":
  "Toque: Visão Verdadeira com alcance de 36 m por 1 hora.",
 "Visão no Escuro":
  "Toque: Visão no Escuro com alcance de 45 m por 8 horas.",
 "Vitalidade Vazia":
  "2d4 + 4 Pontos de Vida Temporários.",
 "Voo":
  "Toque: Deslocamento de Voo de 18 m com pairar, por até 10 minutos. Ao acabar, o alvo cai se "
  "estiver no ar.",
 "Zombaria Perversa":
  "Salvaguarda de Sabedoria ou 1d6 de dano Psíquico e Desvantagem na próxima jogada de ataque "
  "do alvo até o fim do seu próximo turno. O alvo precisa ouvir você.",
 "Zona da Verdade":
  "Esfera de 4,5 m de raio por 10 minutos: quem entra ou começa o turno lá faz salvaguarda de "
  "Carisma ou não consegue mentir de propósito — mas pode omitir e ser evasivo. Você sabe quem "
  "passou na salvaguarda.",
})
