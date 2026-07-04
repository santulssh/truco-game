### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    Lucas Henrique dos Santos
# RA #01 (quem entregou o código):      220449
# Nome #02:                             João Rodolfo Berger Andrade
# RA #02:                               306480

import random
from collections import deque
from itertools import permutations
from typing import NewType, cast

from basic_players import Player
from judge import card_value, generate_deck, manilha_rank

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


def _get_remaining_deck(known_cards: list[Card]) -> list[Card]:
    # Retornar todas as cartas não jogadas na rodada atual.
    default_deck = cast(list[Card], generate_deck())
    return list(filter(lambda card: card not in known_cards, default_deck))


def _check_truco_requested(current_play_hist: list[PlayerDecision]):
    # Verifica se um pedido de truco foi registrado na partida. Caso não tenha sido feito o jogador
    # pode pedir truco, caso contrário não.
    for player_decision in current_play_hist:
        if type(player_decision[-1]) is int:
            return True
    return False


class ProbabilisticStrategist(Player):
    def __init__(self, ra: str, name: str):
        super().__init__(ra, name)

    def _get_rounds_won(self, top_card: Card, current_play_hist: list[PlayerDecision]):
        # Calcula a quantidade de rodadas ganhas pelo time e pelos oponentes
        team_rounds_wins, opp_rounds_wins = 0, 0

        # Recuperamos as decisões dos jogadores na rodada deconsiderando truco
        players_decision = list(
            filter(lambda play: type(play[-1]) is not int, current_play_hist)
        )

        completed_rounds = len(players_decision) // 4

        for i in range(completed_rounds):
            # Selecionamos as decisões dos jogadores de cada dupla
            players_decision = players_decision[i * 4 : (i + 1) * 4]

            if not players_decision:
                break

            # Pegamos o jogador com o maior lance na rodada em valor de carta
            player_decision = max(
                players_decision, key=lambda play: card_value(play[1], top_card)
            )
            winner_player = player_decision

            # Validamos a posição do jogador ganhador com o atual jogador jogando.
            # Se o vencer for um dos jogadores da dupla, aumentamos o placar de rodadas vencidas
            # Caso contrário aumentamos o do oponente
            if winner_player[0] % 2 == self.position % 2:
                team_rounds_wins += 1
            else:
                opp_rounds_wins += 1

        return team_rounds_wins, opp_rounds_wins

    def _get_current_round(self, cards_played: list[Card]):
        # Retorna o número da rodada atual
        return len(cards_played) // 4 + 1 if cards_played else 1

    def _get_cards_played(self, current_play_list: list[PlayerDecision]) -> list[Card]:
        # Retornar todas as cartas jogadas na rodada atual
        return [play[1] for play in current_play_list if play[1] is not None]

    def _calculate_hand_score(
        self, top_card: Card, custom_cards: list[Card] | None = None
    ) -> int:
        # Retorna a pontuação total das cartas
        cards = self.cards.copy() if custom_cards is None else custom_cards
        return sum([card_value(card, top_card) for card in cards])

    def _sort_hand_by_score(
        self, top_card: Card, custom_cards: list[Card] | None = None
    ) -> list[Card]:
        # Retorna as cartas em mãos ordenadas a partir do valor das cartas
        cards = self.cards.copy() if custom_cards is None else custom_cards
        return sorted(cards, key=lambda card: card_value(card, top_card), reverse=True)

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

    def _get_current_order_permutation(self) -> list[list[Card]]:
        return [list(order) for order in permutations(self.cards)]

    def _simulate_monte_carlo(
        self,
        top_card: Card,
        current_round: int,
        number_of_cards_in_round: int,
        card_order: list[Card],
        remaining_cards: list[Card],
        team_rounds_wins: int,
        opp_rounds_wins: int,
    ):

        # Quantidade de cartas desconhecidas na atual partida a serem distribuídas
        cards_per_player = 4 - current_round
        k_card_simulate = (4 - number_of_cards_in_round - 1) + (3 - current_round) * 3
        pick_random_order = random.sample(remaining_cards, k_card_simulate)

        # Distribuição dinâmica das cartas restantes aos outros jogadores através das quantidade de
        # Digamos que cada um dos outros jogadores precisa de 'X' cartas dependendo do estado do jogo
        players_cards: dict[int, deque[Card]] = {}

        index = 0
        for position in range(4):
            if position == self.position:
                players_cards[position] = deque(card_order.copy())
                continue

            players_cards[position] = deque(
                pick_random_order[index : index + cards_per_player]
            )
            index += cards_per_player

        team_rounds_sim, opp_rounds_sim = team_rounds_wins, opp_rounds_wins

        while team_rounds_sim <= 2 and opp_rounds_sim <= 2:
            team_score = 0
            opp_score = 0
            for pos in players_cards.keys():
                pos_next = (pos + 1) % 4

                if pos == 3 or not players_cards[pos] or not players_cards[pos_next]:
                    break

                player1, player2 = (
                    (
                        pos,
                        card_value(players_cards[pos].popleft(), top_card),
                    ),
                    (
                        pos_next,
                        card_value(players_cards[pos_next][0], top_card),
                    ),
                )

                if player1[1] > player2[1]:
                    # Condição de Vitória
                    if player1[0] % 2 == self.position % 2:
                        team_score += 1
                    else:
                        opp_score += 1
                elif player1[1] < player2[1]:
                    # Condição de Derrota
                    if player1[0] % 2 == self.position % 2:
                        opp_score += 1
                    else:
                        team_score += 1
                else:
                    opp_score += 1
                    team_score += 1

            if team_score > opp_score:
                team_rounds_sim += 1
            else:
                opp_rounds_sim += 1

        return 1 if team_rounds_sim >= 2 else 0

    def play(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
        # Estado da partida atual considerando as decisões dos jogadores
        current_play_hist = self._get_current_play_list(play_hist)
        team_rounds_wins, opp_rounds_wins = self._get_rounds_won(
            top_card, current_play_hist
        )

        # Buscamos todas as cartas jogadas na partida atual e então salvamos todas as cartas
        # conhecidas pelo jogador e as demais cartas ainda não jogadas
        cards_played = self._get_cards_played(current_play_hist)
        known_cards: list[Card] = [top_card] + self.cards + cards_played
        remaining_cards = _get_remaining_deck(known_cards)

        # Número atual da rodada para o placar atual de rodadas ganhadas tanto para o time quanto
        # para os oponentes, além da atual quantidade de cartas na mesa
        current_round = self._get_current_round(cards_played)
        number_of_cards_in_round = len(cards_played) % 4

        simulations = 200
        best_order_wins = -1
        best_order: list[Card] = []

        # Receber todas as possibilidades de organizar as cartas da mão atual.
        all_valid_arrange = self._get_current_order_permutation()

        for card_order in all_valid_arrange:
            current_win = sum(
                self._simulate_monte_carlo(
                    top_card,
                    current_round,
                    number_of_cards_in_round,
                    card_order,
                    remaining_cards,
                    team_rounds_wins,
                    opp_rounds_wins,
                )
                for _ in range(simulations)
            )

            # Guarda a melhor ordem
            if current_win > best_order_wins:
                best_order_wins = current_win
                best_order = card_order.copy()

        probability = best_order_wins / simulations

        # Válidamos se é possível pedir truco se nenhum truco foi feito
        if probability >= 0.9 and not _check_truco_requested(current_play_hist):
            return [2, best_order[0]]
        return [1, best_order[0]]

    def respond(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
        # Estado da partida atual considerando as decisões dos jogadores
        current_play_hist = self._get_current_play_list(play_hist)
        player_decision = current_play_hist[-1] if current_play_hist else []
        status = player_decision[-1] if player_decision else None
        team_rounds_wins, opp_rounds_wins = self._get_rounds_won(
            top_card, current_play_hist
        )

        # Buscamos todas as cartas jogadas na partida atual e então salvamos todas as cartas
        # conhecidas pelo jogador e as demais cartas ainda não jogadas
        cards_played = self._get_cards_played(current_play_hist)
        known_cards: list[Card] = [top_card] + self.cards + cards_played
        remaining_cards = _get_remaining_deck(known_cards)

        # Número atual da rodada para o placar atual de rodadas ganhadas tanto para o time quanto
        # para os oponentes, além da atual quantidade de cartas na mesa
        current_round = self._get_current_round(cards_played)
        number_of_cards_in_round = len(cards_played) % 4

        simulations = 200
        best_order_wins = -1

        # Receber todas as possibilidades de organizar as cartas da mão atual.
        all_valid_arrange = self._get_current_order_permutation()

        for card_order in all_valid_arrange:
            current_win = sum(
                self._simulate_monte_carlo(
                    top_card,
                    current_round,
                    number_of_cards_in_round,
                    card_order,
                    remaining_cards,
                    team_rounds_wins,
                    opp_rounds_wins,
                )
                for _ in range(simulations)
            )

            # Guarda a melhor ordem
            if current_win > best_order_wins:
                best_order_wins = current_win

        probability = best_order_wins / simulations

        is_raise_allowed = (
            self._is_raise_allowed(status)
            if type(status) is int or status is None
            else False
        )

        if probability >= 0.9:
            return 2 if is_raise_allowed else 1

        if probability >= 0.7:
            return 1

        return 0


def pair_name():
    # Defina o nome da dupla
    return "ProbabilisticStrategist"


def create_pair():
    # Defina a dupla de jogadores a partir da classe criada
    return (
        ProbabilisticStrategist("220449", "Lucas H."),
        ProbabilisticStrategist("306480", "João R. Berger"),
    )
