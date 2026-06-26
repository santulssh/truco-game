### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    Lucas Henrique dos Santos
# RA #01 (quem entregou o código):      220449
# Nome #02:                             [NOME COMPLETO #02]
# RA #02:                               [RA #02]


from basic_players import Player
from judge import card_value, manilha_rank

global_score = [0, 0]

# NOTE:
# Arquivo com configuração antiga porque o arquivo mais recente possui algumas funções quebradas que ainda não implementei adequadamente. Vou resumir o que está no outro arquivo com esse aqui.
#
# Basicamente estamos criando um algoritmo para tentar calcualar a probabilidade de ganhar através das cartas nas mãos dos jogadoes. Vamos implementar um sistema baseado em Monte Carlo para fazer isso utilizando o estado das cartas dos jogadores (nossa dupla) com as cartas a serem lançadas pela outra dupla.
#
# Calculo deve considerar a força das nossas cartas e as cartas jogadas pelos outros jogadores. Vamos avaliar também se possuimos manilhas e quais as chances de ganharmos através das nossas cartas.
#
# Por enquanto, esse sistema apenas considera um score da dupla que estava fazendo, isso aqui já é suficiente para derrotar os bots nesse projeto, mas devemos implementar esse sistema.
#
# Leia os arquivos no docs/ para saber mais.


def hand_score(cards: list[tuple] | tuple, top_card: tuple):
    count = sum([1 for card in cards if card[0] == manilha_rank(top_card[0])])
    hand_score = sum(card_value(card, top_card) for card in cards)
    return count, hand_score


def calculate_id(pos: int):
    return 0 if pos == 1 or pos == 2 else 1


def calculate_team_score():
    return sum(global_score)


class Player1(Player):
    hand_score = (0, 0)

    # Se estiver dúvida sobre como começar olhe os players prontos em basic_players.py e o ReadMe
    def __init__(self, ra, name):
        super().__init__(ra, name)

    # Função para retornar o que você vai jogar em determinada mão
    def play(self, top_card, play_hist, score_hist):
        """Retorna uma tupla (decisão, carta):
        decisão: 0 = encoberta, 1 = normal, 2 = pedir truco
        carta: a carta a ser jogada (ou None)
        Parâmetros:
        - `top_card` / `vira`: a carta virada na mesa
        - `play_hist`: histórico de jogadas (lista de mãos, cada mão é lista de jogadas)
        - `score_hist`: histórico de placares correspondendo a cada mão
        """

        global global_score
        # print("hist", play_hist)
        # print("score_hist", score_hist)
        best_card = self._cards[0]
        best_value = card_value(best_card, top_card)
        worst_card = self._cards[0]
        worst_value = card_value(worst_card, top_card)

        id = calculate_id(self.position)

        for card in self._cards:
            val = card_value(card, top_card)
            if val > best_value:
                best_card, best_value = card, val
            if val < worst_value:
                worst_card, worst_value = card, val

        self.hand_score = hand_score(self.cards, top_card)
        global_score[id] = self.hand_score[1]

        print("id", self.name)
        print("best_card", best_card)
        print("cards:", self.cards)
        print("manilha:", manilha_rank(top_card[0]))
        print("score", self.hand_score[1])
        print("global_score", global_score)
        print("team_score", calculate_team_score())

        resp = 1, None
        if self.cards and calculate_team_score() >= 1_000:
            resp = 2, best_card
        elif self.cards and calculate_team_score() <= 1_000:
            resp = 1, worst_card
        elif self.cards:
            resp = 1, self.cards[0]

        return resp

    # Função para retornar o que você vai dar de resposta a trucos
    def respond(self, top_card, play_hist, score_hist):
        """Responde a pedidos de truco:
        retorna 0 (correr), 1 (aceitar) ou 2 (aumentar)
        """
        global global_score
        resp = 0
        if calculate_team_score() >= 1_000:
            resp = 2
        if 800 <= calculate_team_score() <= 1_000:
            resp = 1

        return resp


## A ideia È implementar duas classes. Vamos dizer que vamos inserir dois jogadores com nosso respectivos nomes ou algum nome de personagem.
# Depois Passamos o nome de nossa Dupla


# Função que define o nome da dupla:
def pair_name():
    return "Nossa Dupla"  # Defina aqui o nome da sua dupla


# Função que cria a dupla:
def create_pair():
    return (
        Player1("1", "L"),
        Player1("2", "H"),
    )  # Defina aqui a dupla de jogadores. Deve ser uma tupla com dois jogadores.
