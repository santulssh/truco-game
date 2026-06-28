### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    Lucas Henrique dos Santos
# RA #01 (quem entregou o código):      220449
# Nome #02:                             João Rodolfo Berger Andrade
# RA #02:                               306480

from typing import NewType

from basic_players import Player
from judge import RANK_ORDER, SUIT_ORDER, card_value, manilha_rank

import random

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

def get_cards_played(last_play_hist):
    # Retornar todas as cartas jogadas na rodada atual
    return [state[1] for state in last_play_hist if state[1] is not None]

def get_cards_not_played(play_hist, top_card, cards):
    played = []

    if play_hist:
        played = get_cards_played(play_hist[-1]).copy()

    played.append(top_card)
    played.extend(cards)

    all_cards = [(rank, suit) for suit in SUIT_ORDER for rank in RANK_ORDER]

    return [card for card in all_cards if card not in played]

def get_current_round(play_hist):
    #calcula o número do round atual
    if not play_hist:
        return 1

    cards_played = get_cards_played(play_hist[-1])
    return len(cards_played) // 4 + 1

def get_hand_score(cards: list[Card], top_card: Card):
    # Calcula o valor da mão com base nas cartas
    return sum(card_value(card, top_card) for card in cards)


def is_manilha(card: Card, top_card: Card):
    # Verifica se uma carta é uma manilha com base no rank da vira
    return card[0] == manilha_rank(top_card[0])


def count_manilhas_hand(cards: list[Card], top_card: Card):
    # Calcula a quantidade de manilhas em mãos
    return sum(1 for card in cards if is_manilha(card, top_card))
  

class ProbabilisticStrategist(Player):
    current_hand_score: int = 0
    count_manilhas_in_hand: int = 0
    truco_requested = False

    def __init__(self, ra: str, name: str, image_path="img/none.jpg"):
        super().__init__(ra, name, image_path)
        
    def get_rounds_won(self, play_hist, top_card):
        #calcula quantas rodadas foram ganhas tanto por nós quanto pelo oponente

        my_rounds = 0
        opp_rounds = 0

        if not play_hist:
            return 0, 0

        plays = [play for play in play_hist[-1] if play[1] is not None]

        num_complete_rounds = len(plays) // 4

        for i in range(num_complete_rounds):
            round_plays = plays[i*4:(i+1)*4]

            winner = max(round_plays, key=lambda p: card_value(p[1], top_card))

            winner_player = winner[0]

            if winner_player % 2 == self.position % 2:
                my_rounds += 1
            else:
                opp_rounds += 1

        return my_rounds, opp_rounds
    
    def permutations(self, cards):
        orders = []

        if len(cards) == 1:
            orders.append([cards[0]])

        elif len(cards) == 2:
            orders.append([cards[0], cards[1]])
            orders.append([cards[1], cards[0]])

        elif len(cards) == 3:
            for i in range(3):
                for j in range(3):
                    if j == i:
                        continue
                    for k in range(3):
                        if k == i or k == j:
                            continue
                        orders.append([cards[i], cards[j], cards[k]])

        return orders


    def _get_probability_of_winning(self, play_hist, top_card, cards):
        # calcula a probabilidade de vencer a rodada
        not_played = get_cards_not_played(play_hist, top_card, cards)

        current_round = get_current_round(play_hist)

        number_cards_in_round = 0
        if play_hist:
            number_cards_in_round = len(get_cards_played(play_hist[-1])) % 4

        simulations_number = 2000

        wins = 0
        best_order = None
        best_order_wins = -1

        orders = self.permutations(cards)

        for card_order in orders:

            order_wins = 0

            for i in range(simulations_number):
                result = self.simulate(play_hist, top_card, not_played, current_round, number_cards_in_round, card_order)

                wins += result
                order_wins += result

            if order_wins > best_order_wins:
                best_order_wins = order_wins
                best_order = card_order.copy()

        probability = wins / (2 * simulations_number * len(orders))

        return probability, best_order
    
    def simulate(self, play_hist, top_card, not_played_original, current_round, number_cards_played_in_round, card_order):
        #deu tudo errado vou refazer
        not_played = not_played_original.copy()

        my_rounds, opp_rounds = self.get_rounds_won(play_hist, top_card)

        #Número de cartas que precisamos gerar
        cards_to_simulate = (4-number_cards_played_in_round-1) + (3-current_round)*3

        simulated_cards = random.sample(not_played, min(cards_to_simulate, len(not_played)))

        return 1 if win else 0

    def _get_current_played_status(self, play_hist: CardHist):
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

        if self.current_hand_score >= 1_000 and self.count_manilhas_in_hand > 0:
            return max(self.cards, key=lambda c: card_value(c, top_card))

        if self.current_hand_score >= 1_000:
            return max(self.cards, key=lambda c: card_value(c, top_card))

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

        return min(self.cards, key=lambda c: card_value(c, top_card))

    def play(self, top_card: Card, play_hist: CardHist, score_hist: GameScore):

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

        # FIX: A jogada inválida acontece quando o jogador tenta pedir truco quando ja foi pedido.
        # # Armazenamos as jogadas conhecidas na partida e o último tipo de jogada feita
        # current_status = self._get_current_played_status(play_hist)
        # last_status: list = current_status[-1] if current_status else []
        # play_type = last_status[-1] if last_status else None

        # print(play_type)
        # # Válidamos se é possível pedir truco se nenhum truco foi feito
        # if type(play_type) is int and not self.truco_requested:
        #     self.truco_requested = True

        # print(play_type)
        # print(self.truco_requested)

        #print(f"CARTAS JOGADAS: {get_cards_played(play_hist[-1]) if play_hist else []}")
        #print(f"CURRENT ROUND: {get_current_round(play_hist)}")
        #print(f"VITÓRIAS / DERROTAS: {self.get_rounds_won(play_hist, top_card)}")


        # Escolhe jogar normal ou pedir truco com base pontuação das cartas em mãos e no placar do time
        if self.current_hand_score >= 1_000:
            return (
                [2, selected_card] if not self.truco_requested else [1, selected_card]
            )

        if self.current_hand_score >= 800 and team_score > 0:
            return [2, selected_card]

        return [1, selected_card]

    def respond(self, top_card: Card, play_hist: CardHist, score_hist: GameScore):
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


def pair_name():
    # Defina o nome da dupla
    return "ProbabilisticStrategist"


def create_pair():
    # Defina a dupla de jogadores a partir da classe criada
    return (
        ProbabilisticStrategist(
            "000000", "Strategist1", "img/custom/Headphone_Cat.jpg"
        ),
        ProbabilisticStrategist("100000", "Strategist2", "img/none.jpg"),
    )
