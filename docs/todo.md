# TODO:
- [x] [Fix]: O jogador tenta pedir truco ou aumentar a aposta sempre que o score da mão é suficiente.
      Devemos implementar uma verificação para sabermos se alguém pediu truco e se outro jogador
      aceitou ou se o jogador seguinte precisa aceitar ou aumentar.
- [x] [Feat]: Caso dois jogadores tenham em mãos manilhas, ambos vão jogar suas manilhas e ficaram
      com uma mão mais fraca. Precisamos verificar se nossa dupla já jogou uma manilha para então
      não jogarmos uma carta forte
- [x] [Feat]: Caso nossa dupla tenha jogado uma carta forte na mesa e continua a mais forte, então
      devemos jogar a mais fraca para mantermos a mão forte

- [ ] [Feat]: Levar empates em conta na simulação
- [ ] [Feat]: Pedir truco por meio de Monte Carlo