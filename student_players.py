### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    Lucas Henrique dos Santos
# RA #01 (quem entregou o código):      220449
# Nome #02:                             [NOME COMPLETO #02]
# RA #02:                               [RA #02]

from typing import NewType

from basic_players import Player
from judge import RANK_ORDER, SUIT_ORDER, card_value, manilha_rank

# Descreve o tipo de carta
# 0: Rank da carta; 1: Suit da carta
Card = NewType("Card", tuple[str, str])
# Descreve a pontuação da rodada atual
# 0: Pontuação do adverśario; 1: Pontuação da dupla
RoundScore = NewType("RoundScore", list[int])
# Registra as últimas pontuações de cada jogo
# round: [[RoundScore], int]
GameScore = NewType("GameScore", list[list[RoundScore]])
# Registra o tipo de jogada
# hist: [pos, Card, status]
# status: "NORMAL" | "ACEITOU" | "CORREU" | int(3, 6, 9, 12)
PlayerDecision = NewType("PlayerDecision", list)
# Descreve o estado atual de todas as jogadas registradas no jogo
GameHist = NewType("GameHist", list[list[PlayerDecision]])


class ProbabilisticStrategist(Player):
    current_hand_score: int = 0
    count_manilhas_in_hand: int = 0
    truco_requested = False

    def __init__(self, ra: str, name: str, image_path="img/none.jpg"):
        super().__init__(ra, name, image_path)

    def _get_played_cards(self, current_play_list: list[PlayerDecision]):
        # NOTE:
        # Função ainda não sendo usada
        # Retornar todas as cartas jogadas na rodada atual
        return [
            current_play[1]
            for current_play in current_play_list
            if current_play[1] is not None
        ]

    def _calculate_hand_score(self, top_card: Card):
        # Calcula o valor da mão com base nas cartas
        return sum(card_value(card, top_card) for card in self.cards)

    def _is_manilha(self, card: Card, top_card: Card):
        # Verifica se uma carta é uma manilha com base no rank da vira
        return card[0] == manilha_rank(top_card[0])

    def _count_manilhas_hand(self, top_card: Card):
        # Calcula a quantidade de manilhas em mãos
        return sum(1 for card in self.cards if self._is_manilha(card, top_card))

    def _get_current_play_list(self, play_hist: GameHist):
        # Retorna jogas da partida atual
        return play_hist[-1] if len(play_hist) > 0 else []

    def _is_raise_allowed(self, status: int | None):
        # Verifica se é válido aumentar o valor do truco
        if status is None or (type(status) is int and status < 12):
            return True
        return False

    def _get_current_team_score(self, score_hist: GameScore) -> int:
        # Retorna a atual pontuação do time na partida
        # TODO: Avaliar se a posição do score permanece sempre a mesma
        current_score = score_hist[-1][0] if score_hist else []
        return current_score[1] if len(current_score) > 0 else 0

    def _select_card_to_play(
        self, top_card: Card, play_hist: GameHist, team_score: int
    ) -> Card:
        # Caso reste apenas uma carta em mãos, escolhemos a última carta que sobrou
        if len(self.cards) == 1:
            return self.cards[0]

        # Armazenamos as cartas jogadas por todos os jogadores
        # NOTE: Ainda não utilizado para a decisão
        # hist_cards_played = get_cards_played(play_hist[-1]) if play_hist else []

        # Avaliamos a estratégia de jogada a partir do score da mão do jogador e do placar do time.
        # Em seguida, selecionar a carta a ser jogada com base no maior ou menor valor da carta
        if (
            self.current_hand_score >= 800
            and self.count_manilhas_in_hand > 0
            and team_score > 0
        ):
            return max(self.cards, key=lambda c: card_value(c, top_card))

        if self.current_hand_score >= 800 and team_score > 0:
            return max(self.cards, key=lambda c: card_value(c, top_card))

        if self.current_hand_score >= 800 and self.count_manilhas_in_hand > 0:
            return max(self.cards, key=lambda c: card_value(c, top_card))

        if self.current_hand_score < 800 and team_score > 0:
            return min(self.cards, key=lambda c: card_value(c, top_card))

        return min(self.cards, key=lambda c: card_value(c, top_card))

    def play(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
        # NOTE:
        # Ainda não utilizadas, porém podem ser úteis
        # current_position = partner_pos = self.position % 4
        # partner_position = partner_pos = (self.position + 2) % 4

        # Calcula a atual pontuação da mão e quantidades de manilhas
        self.current_hand_score = self._calculate_hand_score(top_card)
        self.count_manilhas_in_hand = self._count_manilhas_hand(top_card)

        # Consideramos a pontuação da partida e armazenamos o estado atual do nosso time
        team_score = self._get_current_team_score(score_hist)

        # Selecionamos a carta a partir do estado do jogo
        selected_card = self._select_card_to_play(top_card, play_hist, team_score)

        # NOTE:
        # Debug apenas
        # print("play | position", current_position)
        # print("play | partner pos", partner_pos)
        # print("play | vira", top_card)
        # print("play | hand_score", current_hand_score)
        # print("play | current_hand", current_hand)
        # print("play | manilhas_hand", count_manilhas)
        # print("play", play_hist)
        # print("score", current_score)
        # print("team", team_score)

        # Armazenamos as jogadas conhecidas na partida e o último tipo de jogada feita
        current_play_list = self._get_current_play_list(play_hist)

        # Válidamos se é possível pedir truco se nenhum truco foi feito
        if not self.truco_requested:
            for player_decision in current_play_list:
                status = player_decision[-1]
                if type(status) is int:
                    self.truco_requested = True
                    break

        # Escolhe jogar normal ou pedir truco com base pontuação das cartas em mãos e no placar do time
        if self.current_hand_score >= 1_000:
            return (
                [2, selected_card] if not self.truco_requested else [1, selected_card]
            )

        if self.current_hand_score >= 800 and team_score > 0:
            return (
                [2, selected_card] if not self.truco_requested else [1, selected_card]
            )

        return [1, selected_card]

    def respond(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
        # NOTE:
        # Ainda não utilizado, pode ser útil
        # partner_pos = (self.position + 2) % 4

        # Calcula a atual pontuação da mão e quantidades de manilhas
        self.current_hand_score = self._calculate_hand_score(top_card)
        self.count_manilhas_in_hand = self._count_manilhas_hand(top_card)

        # Consideramos a pontuação da partida e armazenamos o estado atual do nosso time
        team_score = self._get_current_team_score(score_hist)

        # Armazenamos o estado atual da partida
        current_play_list = self._get_current_play_list(play_hist)
        player_decisision: list = current_play_list[-1] if current_play_list else []
        status = player_decisision[-1] if player_decisision else None

        # Verificamos se o jogador pode pedir aumento
        is_raise_allowed = (
            self._is_raise_allowed(status)
            if type(status) is int or status is None
            else False
        )

        # Jogador toma decisão a partir do estado atual do jogo
        # Escolhendo [0] correr, [1] aceitar truco e [2] aumentar truco
        if self.current_hand_score >= 1_000:
            return 2 if is_raise_allowed else 1

        if (
            self.current_hand_score >= 800
            and self.count_manilhas_in_hand > 0
            and team_score > 0
        ):
            return 2 if is_raise_allowed else 1

        if self.current_hand_score >= 800 and self.count_manilhas_in_hand > 0:
            return 2 if is_raise_allowed else 1

        if self.current_hand_score >= 800 and team_score > 0:
            return 1

        return 0


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


# NOTE:
# Classe de jogador com lógica apenas levando em consideração o score da mão.
# Remover no futuro, mas por enquanto serve para compararmos em relação a nova classe.
# @DEPRECATED
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
        ProbabilisticStrategist(
            "000000", "ProbabilisticPlayer1", "img/custom/Headphone_Cat.jpg"
        ),
        ProbabilisticStrategist("100000", "ProbabilisticPlayer2"),
    )
