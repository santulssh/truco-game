## Pesquisar e Avaliar sua implementação

Probabilidade de dedução para cartas: [link](https://www.reddit.com/r/probabilitytheory/comments/urs0ar/probability_of_a_brazilian_card_game)

- Calcular dinamicamente a probabilidade das cartas remanescentes com base nas cartas já conhecidas da própria dupla e as cartas jogadas até então. O modelo estatístico deduzirá a distribuição provável das cartas adversárias utilizando essas informações.

- Implementar um sistema de classificação para determinar o momento ideal de propor ou aceitar o aumento do truco. 

- O cálculo de probabilidade deve integrar o subconjunto de cartas do próprio jogador ativo e das cartas ocultas através da probabilidade condicional em tempo real. Para isso, vamos reavaliar a sempre partir do histórico de jogadas (`play_hist`).
 
- Para determinar instantaneamente a ordem de força da rodada a partir da carta de vira (`top_card`), será utilizada uma tabela de dispersão (*Hash Table*) para a chave combinada (número e naipe) diretamente para o tipo de manilha correspondente
