# Pygames
Intruções de como usar o módulo pygame para ensinar uma máquina a jogar. Sprites e imagens usadas estão na pasta "Recursos".

# Basic_pygame.py
Conceitos básicos de como usar o módulo pygame.

# Flappy_Game.py
O joguinho do flappy bird clássico pronto pra jogar.

# Flappy_Evolve.py
Evolui uma rede neural pra jogar utilizando o algoritmo genético neat-0.92 (NeuroEvolution of Augmenting Topologies), que é bastante fácil de implementar. Usa o arquivo "flappy_neat_config.txt" pra definir os parâmetros da evolução.

O espaço de cenários diferentes e o espaço de ações dos pássaros são bem pequenos, então o neat consegue convergir rápido numa solução satisfatória.

# Dino_Game.py
O joguinho do dinossauro do chrome clássico pronto pra jogar.

# Dino_Evolve.py
Como evoluir uma rede neural utilizando o algoritmo genético neat-0.92 (NeuroEvolution of Augmenting Topologies), que é bastante fácil de implementar. Usa o arquivo "dino_evolve_neat_config.txt" pra definir os parâmetros da evolução e o "visualize.py" pra desenhar a estrutura da rede vencedora.

A complexidade é maior do que o jogo do flappy bird, então demora mais até uma solução boa ser encontrada.

# Dino_Learn.py
Como Ensinar uma rede neural a jogar através de Double Deep-Q Reinforcement-Learning. O funcionamento desse algoritmo depende majoritariamente da Função de Recompensa (escrita no jogo em si), que vai definir exatamente os tipos de comportamentos que são desejáveis ou não. A arquitetura da rede e o loop de treino estão no arquivo "dino_lear_reinf_structure.py". 

Aprendizado de reforço depende de um único agente quebrando a cabeça de novo e de novo até ele entender o que fazer, o que é bem diferente de um algoritmo genético onde deixamos mil jogadores se matarem para  deixando os melhores vivos e repetir o processo nos seus decendentes até sair algum muito bom. Então se prepare porque o treino vai demorar bastaaante.

DQ-RL é, no geral, mais difícil de entender do que outros métodos de machine learning, então necessita de um bom tempo encarando o código pra fazer sentido de como tudo se encaixa.

# Pong_game.py
O clássico jogo de pong (para 2 jogadores) recriado usando pygame e a engine de física pymunk.
 
