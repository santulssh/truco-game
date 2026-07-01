# TODO:

## Modelo
- [x] [Fix]: O jogador tenta pedir truco ou aumentar a aposta sempre que o score da mão é suficiente.
      Devemos implementar uma verificação para sabermos se alguém pediu truco e se outro jogador
      aceitou ou se o jogador seguinte precisa aceitar ou aumentar.
- [x] [Feature]: Caso dois jogadores tenham em mãos manilhas, ambos vão jogar suas manilhas e ficarão
      com uma mão mais fraca. Precisamos verificar se nossa dupla já jogou uma manilha para então
      não jogarmos uma carta forte.
- [x] [Feature]: Caso nossa dupla tenha jogado uma carta forte na mesa e continua a mais forte, então
      devemos jogar a mais fraca para mantermos a mão forte. Podemos considerar esconder a carta se 
      for possível.
- [x] [Feature]: Fazer pedidos de truco se a mão for boa pelo algoritmo de Monte Carlo
- [x] [Feature]: Caso tenha empate de manilhas, considerar se deve gastar a carta mais forte para
      vencer a partida ou não.
- [x] [Feature]: Caso um dos jogadoes jogue uma manilha e algum jogador da dupla possua uma manilha
      devemos verificar se é melhor empatar gastando uma manilha ou se é melhor perder aquela rodada e manter as cartas mais fortes para uma outra rodada.
- [x] [Feature]: Caso não seja possível ganhar a rodada com as cartas que possui, decidir jogar as cartas de menor valor.
- [x] [Feature]: Considerar empates na simulação. Definimos errôneamente quem começa a rodada nesse caso e quantos pontos precisamos fazer.



## Código
- [x] [Perf]: Existem diversas funções realizando processos de cálculo redundante que podem ser
      otimizadas. Avaliar as funções e reescrever sua lógica ou remover por completo caso seja
      desnecessário para o funcionamento do código.
- [ ] [Change]: Implementar a tipagem correta para evitar cenários imprevistos.
- [ ] [Perf]: O código precisa ser otimizado.