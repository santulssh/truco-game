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
from judge import card_value, generate_deck

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

# Variáveis para a simulação
MAX_SIMULATIONS = 200  # Valor Padrão: 200
CONFIDENCE_THRESHOLD = 0.05  # Valor Padrão: 0.03 | Intervalo: (mais confiante) [0.01 - 0.1] (menos confiante)


def _get_remaining_deck(known_cards: list[Card]) -> list[Card]:
    """
    Retorna o restante das cartas do baralho de Truco ainda não jogadas a partir das cartas
    conhecidas no momento atual do jogo.
    """
    default_deck = cast(list[Card], generate_deck())
    return list(filter(lambda card: card not in known_cards, default_deck))


def _check_truco_requested(current_play_hist: list[PlayerDecision]):
    """
    Verifica se algum pedido de truco foi requisitado em algum momento da partida atual a partir do
    histórico atual de decisões dos jogadores. Caso tenha sido feito algum pedido retorna True, se
    não retorna False.
    """
    return any(
        isinstance(player_decision[-1], int) for player_decision in current_play_hist
    )


class ProbabilisticStrategist(Player):
    def __init__(self, ra: str, name: str):
        super().__init__(ra, name)

    def _get_partner_pos(self):
        """Retorna a posição do parceiro com base na posição do jogador atual"""
        return (self.position + 2) % 4

    def _get_current_round(self, cards_played: list[Card]):
        """
        Retorna a rodada atual a partir das cartas jogadas onde o máximo de cartas por rodada
        equivale a quatro.
        """
        # Retorna o número da rodada atual.
        return len(cards_played) // 4 + 1 if cards_played else 1

    def _get_rounds_won(self, top_card: Card, current_play_hist: list[PlayerDecision]):
        """
        Retorna a quantidade de rodadas ganhas pelo time e pelos oponentes a partir do histórico
        de decisões dos jogadores na partida atual.
        """
        team_rounds_wins, opp_rounds_wins = 0, 0
        # Filtramos as decisões dos jogadores na partida atual desconsiderando quando jogadores
        # pedem o truco ou aumentam, pois não são jogadas cartas.
        players_decision = list(
            filter(lambda play: type(play[-1]) is not int, current_play_hist)
        )

        completed_rounds = len(players_decision) // 4

        for i in range(completed_rounds):
            # Selecionamos as decisões dos jogadores de cada dupla.
            round_decisions = players_decision[i * 4 : (i + 1) * 4]

            if not round_decisions:
                break

            # Pegamos o jogador com o maior lance na rodada em valor de carta.
            winner_player = max(
                round_decisions, key=lambda play: card_value(play[1], top_card)
            )
            # Verificamos se a posição do jogador ganhador corresponde a algum jogador do time
            # para a distribuição das partidas ganhas.
            if winner_player[0] % 2 == self.position % 2:
                team_rounds_wins += 1
            else:
                opp_rounds_wins += 1

        return team_rounds_wins, opp_rounds_wins

    def _get_cards_played(self, current_play_hist: list[PlayerDecision]) -> list[Card]:
        """Retorna todas as cartas jogadas na partida atual."""
        return [play[1] for play in current_play_hist if play[1] is not None]

    def _get_current_play_list(self, play_hist: GameHist):
        """Retorna todas as decisões dos jogadores na partida atual."""
        return play_hist[-1] if len(play_hist) > 0 else []

    def _get_current_order_permutation(self) -> list[list[Card]]:
        """Retorna todas as possibilidades de ordem para a mão atual."""
        return [list(order) for order in permutations(self.cards)]

    def _simulate_monte_carlo(
        self,
        top_card: Card,
        number_of_cards_in_round: int,
        current_round: int,
        current_round_plays: dict[int, Card],
        card_order: list[Card],
        remaining_cards: list[Card],
        team_rounds_wins: int,
        opp_rounds_wins: int,
    ):

        # Quantidade de cartas desconhecidas na atual partida a serem distribuídas
        cards_per_player = 4 - current_round
        k_card_simulate = 3 * cards_per_player

        # Quem já jogou na rodada atual
        players_played_this_round = set(current_round_plays.keys())

        pick_random_order = random.sample(remaining_cards, k_card_simulate)

        index = 0
        players_cards: dict[int, deque[Card]] = {}
        for position in range(4):
            if position == self.position:
                players_cards[position] = deque(card_order.copy())
                continue

            players_cards[position] = deque(
                pick_random_order[index : index + cards_per_player]
            )
            index += cards_per_player

        team_rounds_sim, opp_rounds_sim = team_rounds_wins, opp_rounds_wins

        # Se estamos no meio da rodada atual, completá-la primeiro
        if number_of_cards_in_round > 0:
            # Remove cartas já jogadas na rodada atual das mãos
            for pos, card in current_round_plays.items():
                if pos in players_cards:
                    for i, c in enumerate(players_cards[pos]):
                        if c == card:
                            del players_cards[pos][i]
                            break

            # Jogadores que ainda não jogaram na rodada atual jogam agora
            round_plays = []
            for pos in sorted(players_cards.keys()):
                if pos in players_played_this_round:
                    continue
                if not players_cards[pos]:
                    break
                card = players_cards[pos].popleft()
                round_plays.append((pos, card_value(card, top_card)))

            if len(round_plays) + len(current_round_plays) == 4:
                # Inclui as jogadas já conhecidas para determinar o vencedor
                all_round_plays = round_plays + [
                    (pos, card_value(card, top_card))
                    for pos, card in current_round_plays.items()
                ]
                winner_pos = max(all_round_plays, key=lambda x: x[1])[0]
                if winner_pos % 2 == self.position % 2:
                    team_rounds_sim += 1
                else:
                    opp_rounds_sim += 1

        # Rodadas completas subsequentes
        while team_rounds_sim <= 2 and opp_rounds_sim <= 2:
            round_plays = []
            for pos in sorted(players_cards.keys()):
                if not players_cards[pos]:
                    break
                card = players_cards[pos].popleft()
                round_plays.append((pos, card_value(card, top_card)))

            if len(round_plays) < 4:
                break

            winner_pos = max(round_plays, key=lambda x: x[1])[0]
            if winner_pos % 2 == self.position % 2:
                team_rounds_sim += 1
            else:
                opp_rounds_sim += 1

        return 1 if team_rounds_sim >= 2 else 0

    def play(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
        # Estado da partida atual considerando as decisões dos jogadores.
        current_play_hist = self._get_current_play_list(play_hist)

        # O número atual da rodada e a quantidade de cartas conhecidas jogadas.
        cards_played = self._get_cards_played(current_play_hist)

        current_round = self._get_current_round(cards_played)
        number_of_cards_in_round = len(cards_played) % 4

        # Separa cartas da rodada atual das anteriores
        completed_rounds_cards = cards_played[
            : len(cards_played) - number_of_cards_in_round
        ]
        current_round_cards = (
            cards_played[-number_of_cards_in_round:]
            if number_of_cards_in_round > 0
            else []
        )

        current_round_plays: dict[int, Card] = {}
        if current_round_cards:
            # Precisamos saber quem jogou o quê na rodada atual. Filtramos as decisões da rodada
            # considerando as jogas normais
            normal_plays = [p for p in current_play_hist if type(p[-1]) is not int]
            round_starts = len(completed_rounds_cards)
            for play in normal_plays[round_starts:]:
                current_round_plays[play[0]] = play[1]

        # O placar de quantidade de rodadas vencidas na partida atual
        team_rounds_wins, opp_rounds_wins = self._get_rounds_won(
            top_card, current_play_hist
        )

        # Buscamos todas as cartas jogadas na partida atual e então salvamos todas as cartas
        # conhecidas pelo jogador e as demais cartas ainda não jogadas
        known_cards: list[Card] = [top_card] + self.cards + cards_played
        remaining_cards = _get_remaining_deck(known_cards)

        # A partir do estado da partida atual vamos simular possíveis partidas
        best_order_wins = -1
        best_order: list[Card] = []

        # Receber todas as possibilidades de organizar as cartas da mão atual.
        all_valid_arrange = self._get_current_order_permutation()

        # Se estivermos vecendo, priorizar a ordem que começa com a mais fraca para a próxima rodada.
        if team_rounds_wins == 1 and opp_rounds_wins == 0:
            all_valid_arrange.sort(key=lambda order: card_value(order[0], top_card))

        # Se estivermos perdend, priorizar a ordem que começa com a mais fraca para a próxima rodada.
        elif team_rounds_wins == 0 and opp_rounds_wins == 1:
            all_valid_arrange.sort(
                key=lambda order: card_value(order[0], top_card), reverse=True
            )

        for card_order in all_valid_arrange:
            current_win = 0

            for sim in range(MAX_SIMULATIONS):
                current_win += self._simulate_monte_carlo(
                    top_card,
                    number_of_cards_in_round,
                    current_round,
                    current_round_plays,
                    card_order,
                    remaining_cards,
                    team_rounds_wins,
                    opp_rounds_wins,
                )

                current_probability = current_win / (sim + 1)
                if (
                    best_order_wins > 0
                    and (current_probability + CONFIDENCE_THRESHOLD) * MAX_SIMULATIONS
                    < best_order_wins
                ):
                    break

            # Guarda a melhor ordem
            if current_win > best_order_wins:
                best_order_wins = current_win
                best_order = card_order.copy()

        probability = best_order_wins / MAX_SIMULATIONS
        # Válidamos se é possível pedir truco se nenhum truco foi feito
        if probability >= 0.9 and not _check_truco_requested(current_play_hist):
            return [2, best_order[0]]
        return [1, best_order[0]]

    def respond(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
        # Estado da partida atual considerando as decisões dos jogadores
        current_play_hist = self._get_current_play_list(play_hist)

        # O número atual da rodada e a quantidade de cartas conhecidas jogadas.
        cards_played = self._get_cards_played(current_play_hist)
        current_round = self._get_current_round(cards_played)
        number_of_cards_in_round = len(cards_played) % 4

        # Separa cartas da rodada atual das anteriores
        completed_rounds_cards = cards_played[
            : len(cards_played) - number_of_cards_in_round
        ]
        current_round_cards = (
            cards_played[-number_of_cards_in_round:]
            if number_of_cards_in_round > 0
            else []
        )

        current_round_plays: dict[int, Card] = {}
        if current_round_cards:
            # Precisamos saber quem jogou o quê na rodada atual. Filtramos as decisões da rodada
            # considerando as jogas normais
            normal_plays = [p for p in current_play_hist if type(p[-1]) is not int]
            round_starts = len(completed_rounds_cards)
            for play in normal_plays[round_starts:]:
                current_round_plays[play[0]] = play[1]

        # O placar de quantidade de rodadas vencidas na partida atual
        team_rounds_wins, opp_rounds_wins = self._get_rounds_won(
            top_card, current_play_hist
        )

        # Buscamos todas as cartas jogadas na partida atual e então salvamos todas as cartas
        # conhecidas pelo jogador e as demais cartas ainda não jogadas
        known_cards: list[Card] = [top_card] + self.cards + cards_played
        remaining_cards = _get_remaining_deck(known_cards)

        # A partir do estado da partida atual vamos simular possíveis partidas
        best_order_wins = -1

        # Receber todas as possibilidades de organizar as cartas da mão atual.
        all_valid_arrange = self._get_current_order_permutation()

        for card_order in all_valid_arrange:
            current_win = 0

            for sim in range(MAX_SIMULATIONS):
                current_win += self._simulate_monte_carlo(
                    top_card,
                    number_of_cards_in_round,
                    current_round,
                    current_round_plays,
                    card_order,
                    remaining_cards,
                    team_rounds_wins,
                    opp_rounds_wins,
                )

                current_probability = current_win / (sim + 1)
                if (
                    best_order_wins > 0
                    and (current_probability + CONFIDENCE_THRESHOLD) * MAX_SIMULATIONS
                    < best_order_wins
                ):
                    break

            # Guarda a melhor ordem
            if current_win > best_order_wins:
                best_order_wins = current_win

        probability = best_order_wins / MAX_SIMULATIONS

        # Verifica se é válido aumentar o valor do truco
        player_decision = current_play_hist[-1] if current_play_hist else []
        status = player_decision[-1] if player_decision else None
        is_raise_allowed = (
            True if status is None or (type(status) is int and status < 12) else False
        )

        if probability >= 0.95:
            return 2 if is_raise_allowed else 1

        if probability >= 0.85:
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
