### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    Lucas Henrique dos Santos
# RA #01 (quem entregou o código):      220449
# Nome #02:                             [NOME COMPLETO #02]
# RA #02:                               [RA #02]


from typing import NewType

from basic_players import Player
from judge import RANK_ORDER, SUIT_ORDER, card_value, manilha_rank

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
#
# TODO:
#  - [ ] Fix jogadas inválidas sendo registradas

Card = NewType("Card", tuple[str, str])  # Card[rank, suit]
# 0: Pontuação do adverśario; 1: Pontuação da dupla
RoundScore = NewType("RoundScore", list[int])
# round: [[RoundScore], int]
ScoreTeam = NewType("ScoreTeam", list[list[RoundScore]])
# hist: [pos, Card, PlayType]
# PlayType: "NORMAL" | "ACEITOU" | "CORREU" | 3, 6, 9, 12
CardHist = NewType("CardHist", list[list])

# @Deprecated
global_score = [0, 0]


# @DEPRECATED
def calculate_id(pos: int):
    return 0 if pos == 1 or pos == 2 else 1


# @DEPRECATED
def calculate_team_score():
    return sum(global_score)


# @DEPRECATED
def hand_score(cards: list[tuple] | tuple, top_card: tuple):
    count = sum([1 for card in cards if card[0] == manilha_rank(top_card[0])])
    hand_score = sum(card_value(card, top_card) for card in cards)
    return count, hand_score


def get_cards_played(hand_history: list):
    return [card for card in hand_history if card[1] is not None]


def get_hand_score(cards: list[Card], top_card: Card):
    return sum(card_value(card, top_card) for card in cards)


def is_manilha(card: Card, top_card: Card):
    return card[0] == manilha_rank(top_card[0])


def count_manilhas_hand(cards: list[Card], top_card: Card):
    return sum(1 for card in cards if is_manilha(card, top_card))


def select_card_to_play(
    cards: list[Card], top_card: Card, play_hist: CardHist, current_pos: int
):
    if len(cards) == 1:
        return cards[0]

    hist_cards_played = get_cards_played(play_hist[-1]) if play_hist else []
    completed_rounds = len(hist_cards_played) // 4

    if completed_rounds == 0:
        return min(cards, key=lambda c: card_value(c, top_card))

    # TODO:
    # Reimplementar lógica paras as jogadas completas

    return cards[0]


# Nova classe
# Ainda quebrado, não consegue vencer o ScoreStrategist ainda
class ProbabilisticStrategist(Player):
    def __init__(self, ra: str, name: str, image_path="img/none.jpg"):
        super().__init__(ra, name, image_path)

    def play(self, top_card: Card, play_hist: CardHist, score_hist: ScoreTeam):

        current_position = partner_pos = self.position % 4
        partner_position = partner_pos = (self.position + 2) % 4
        current_hand_score = get_hand_score(self.cards, top_card)
        current_hand: list[Card] = self.cards.copy()
        count_manilhas = count_manilhas_hand(self.cards, top_card)

        # print("play | position", current_position)
        # print("play | partner pos", partner_pos)
        # print("play | vira", top_card)
        # print("play | hand_score", current_hand_score)
        # print("play | current_hand", current_hand)
        # print("play | manilhas_hand", count_manilhas)

        # print("play", play_hist)

        # FIX: Avaliar a razão de uma jogada inválida ter sido feita
        selected_card = select_card_to_play(
            self.cards, top_card, play_hist, self.position
        )

        # Avaliar a pontuação necessária
        if current_hand_score >= 1_000:
            return [2, selected_card]

        return [1, selected_card]

    def respond(self, top_card, play_hist, score_hist):
        # Resposta quebrada, pois não possui o algoritmo de Monte Carlo para fazer o cálculo da probabilidade

        partner_pos = (self.position + 2) % 4

        current_hand_score = get_hand_score(self.cards, top_card)

        print("respond | hand_score", current_hand_score)

        if current_hand_score >= 1_000:
            return 2
        if 800 <= current_hand_score <= 1_000:
            return 1
        return 0


# Antigo
# Será mudado para a outra classe
class ScoreStrategist(Player):
    hand_score = (0, 0)

    # Se estiver dúvida sobre como começar olhe os players prontos em basic_players.py e o ReadMe
    def __init__(self, ra, name, image_path="img/none.jpg"):
        super().__init__(ra, name, image_path)

    # Função para retornar o que você vai jogar em determinada mão
    def play(self, top_card: Card, play_hist, score_hist):
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

        # print("id", self.name)
        # print("best_card", best_card)
        # print("cards:", self.cards)
        # print("manilha:", manilha_rank(top_card[0]))
        # print("score", self.hand_score[1])
        # print("global_score", global_score)
        # print("team_score", calculate_team_score())

        if self.cards and calculate_team_score() >= 1_000:
            return 2, best_card
        elif self.cards and calculate_team_score() <= 1_000:
            return 1, worst_card
        elif self.cards:
            return 1, self.cards[0]

        return 1, None

    # Função para retornar o que você vai dar de resposta a trucos
    def respond(self, top_card, play_hist, score_hist):
        """Responde a pedidos de truco:
        retorna 0 (correr), 1 (aceitar) ou 2 (aumentar)
        """
        resp = 0
        if calculate_team_score() >= 1_000:
            resp = 2
        if 800 <= calculate_team_score() <= 1_000:
            resp = 1

        return resp


def pair_name():
    # Defina o nome da dupla
    return "ProbabilisticStrategist"


def create_pair():
    # Defina a dupla de jogadores a partir da classe criada
    return (
        ProbabilisticStrategist("000000", "Player 1", "img/custom/Headphone_Cat.jpg"),
        ProbabilisticStrategist("100000", "Player 2"),
    )
