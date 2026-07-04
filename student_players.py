### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    Lucas Henrique dos Santos
# RA #01 (quem entregou o código):      220449
# Nome #02:                             João Rodolfo Berger Andrade
# RA #02:                               306480

import random
from typing import NewType, cast

from basic_players import Player
from judge import RANK_ORDER, SUIT_ORDER, card_value, generate_deck, manilha_rank

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


class ProbabilisticStrategist(Player):
    current_hand_score: int = 0
    count_manilhas_in_hand: int = 0
    truco_requested = False

    def __init__(self, ra: str, name: str):
        super().__init__(ra, name)

    def get_rounds_won(self, play_hist, top_card):
        # Calcula quantas rodadas foram ganhas tanto por nós quanto pelo oponente

        my_rounds = 0
        opp_rounds = 0

        # Se não houve histórico, então está 0 a 0
        if not play_hist:
            return 0, 0

        # Pega todas as jogadas de cartas (descosidera trucos)
        plays = [play for play in play_hist[-1] if play[1] is not None]

        num_complete_rounds = len(plays) // 4

        for i in range(num_complete_rounds):
            # Recupera as cartas jogadas do round i
            round_plays = plays[i*4:(i+1)*4]

            # Descobre qual carta ganhou
            winner = max(round_plays, key=lambda p: card_value(p[1], top_card))
            winner_player = winner[0]

            # Descobre qual dupla gahou
            if winner_player % 2 == self.position % 2:
                my_rounds += 1
            else:
                opp_rounds += 1

        return my_rounds, opp_rounds

    def permutations(self, cards):
        # Gera todas as possíveis ordens que podemos jogar nossas cartas para podermos simulá-las

        orders = []

        if len(cards) == 1:
            orders.append([cards[0]])

        elif len(cards) == 2:
            orders.append([cards[0], cards[1]])
            orders.append([cards[1], cards[0]])

        elif len(cards) == 3:
            # Gera as 6 permutações
            for i in range(3):
                for j in range(3):
                    if j == i:
                        continue
                    for k in range(3):
                        if k == i or k == j:
                            continue
                        orders.append([cards[i], cards[j], cards[k]])

        return orders

    def _get_cards_not_played(self, top_card: Card, play_hist: GameHist):
        played = []

    def _get_probability_of_winning(self, play_hist, top_card, cards):
        # Calcula a probabilidade de vencer a mão considerando todas as ordens das cartas

        # Cartas que podem estar com os outros jogadores
        not_played = get_cards_not_played(play_hist, top_card, cards)

        current_round = self.get_current_round(play_hist)

        # Quantas cartas já foram jogadas na rodada
        number_cards_in_round = 0
        if play_hist:
            number_cards_in_round = len(self._get_played_cards(play_hist[-1])) % 4

        simulations_number = 200

        wins = 0
        best_order = None
        best_order_wins = -1

        # Testa todas as ordens possíveis das cartas
        orders = self.permutations(cards)

        for card_order in orders:
            order_wins = 0

            # Executa um certo número de simulações aleatórias
            for i in range(simulations_number):
                result = self.simulate(
                    play_hist,
                    top_card,
                    not_played,
                    current_round,
                    number_cards_in_round,
                    card_order,
                )

                wins += result
                order_wins += result

            # Guarda a melhor ordem
            if order_wins > best_order_wins:
                best_order_wins = order_wins
                best_order = card_order.copy()

        probability = best_order_wins / simulations_number

        return probability, best_order
    
    def _get_probability_of_winning_after_response(self, play_hist, top_card, cards):
        # Mesmo conceito da anterior, mas usada quando estamos respondendo ao truco
        # Precisamos dela porque não é razoável aceitar diante de jogadas aleatórias
        # Usamos a estratégia Greedy para decidir

        not_played = get_cards_not_played(play_hist, top_card, cards)

        current_round = self.get_current_round(play_hist)

        number_cards_in_round = 0
        if play_hist:
            number_cards_in_round = len(self._get_played_cards(play_hist[-1])) % 4

        simulations_number = 200

        best_order = None
        best_order_wins = -1

        orders = self.permutations(cards)

        for card_order in orders:
            order_wins = 0

            for i in range(simulations_number):

                order_wins += self.simulate_response(play_hist, top_card, not_played, current_round, number_cards_in_round, card_order)

            if order_wins > best_order_wins:
                best_order_wins = order_wins
                best_order = card_order.copy()

        probability = best_order_wins / simulations_number

        return probability, best_order
    
    def simulate(self, play_hist, top_card, not_played_original, current_round, number_cards_played_in_round, card_order):
        # Faz uma simulação da partida

        not_played = not_played_original.copy()

        # Placar da mão
        my_rounds, opp_rounds = self.get_rounds_won(play_hist, top_card)

        # Número de cartas desconhecidas que ainda precisam ser distribuídas
        cards_to_simulate = ((4 - number_cards_played_in_round - 1) + (3 - current_round) * 3)

        simulated_cards = random.sample(not_played, cards_to_simulate)

        # Mão simulada de cada jogador
        players_cards = [[], [], [], []]

        # A primeira carta da ordem será jogada imediatamente
        # Ela não fica na nossa mão
        players_cards[self.position] = card_order[1:].copy()

        current_player = (self.position + 1) % 4

        # Distribui cartas aleatórias aos outros jogadores
        for card in simulated_cards:
            while current_player == self.position:
                current_player = (current_player + 1) % 4

            players_cards[current_player].append(card)

            current_player = (current_player + 1) % 4

        hands = [hand.copy() for hand in players_cards]

        # Os adversários jogam em ordem aleatória
        for player in range(4):
            if player != self.position:
                random.shuffle(hands[player])

        my_rounds_sim = my_rounds
        opp_rounds_sim = opp_rounds

        first_round = True

        # Enquanto ninguém ganha
        while my_rounds_sim < 2 and opp_rounds_sim < 2:
            played_cards = []

            if first_round and play_hist:
                last_round = play_hist[-1]
                start = (current_round - 1) * 4

                # Recupera as cartas já jogadas nesta rodada
                for play in last_round[start:]:
                    if play[1] is not None:
                        played_cards.append((play[0], play[1]))

                played_cards.append((self.position, card_order[0]))

                current_player = (self.position + 1) % 4

                first_round = False

            else:
                current_player = self.position

            # Completa a simulação
            while len(played_cards) < 4:
                player = current_player

                card = hands[player].pop(0)

                played_cards.append((player, card))

                current_player = (current_player + 1) % 4

            winner = max(played_cards, key=lambda x: card_value(x[1], top_card))[0]

            if winner % 2 == self.position % 2:
                my_rounds_sim += 1
            else:
                opp_rounds_sim += 1

            # O vencedor inicia a próxima rodada
            current_player = winner

        # Retorna vitória ou derrota
        return 1 if my_rounds_sim >= 2 else 0
    
    def simulate_response(self, play_hist, top_card, not_played_original, current_round, number_cards_played_in_round, card_order):
        # Simulação usada quando decidimos aceitar ou aumentar o truco
        
        not_played = not_played_original.copy()

        my_rounds, opp_rounds = self.get_rounds_won(play_hist, top_card)

        # Aqui NÃO removemos uma carta da nossa mão como na outra função
        cards_to_simulate = ((4 - number_cards_played_in_round) + (3 - current_round) * 3)

        simulated_cards = random.sample(not_played, cards_to_simulate)

        players_cards = [[], [], [], []]

        # Já sabemos nossa mão
        players_cards[self.position] = card_order.copy()

        current_player = (self.position + 1) % 4

        # Distribui cartas aleatórias
        for card in simulated_cards:
            while current_player == self.position:
                current_player = (current_player + 1) % 4

            players_cards[current_player].append(card)
            current_player = (current_player + 1) % 4

        hands = [hand.copy() for hand in players_cards]

        # Greedy para os outros jogadores
        for player in range(4):
            if player != self.position:
                hands[player].sort(key=lambda c: card_value(c, top_card), reverse=True)

        my_rounds_sim = my_rounds
        opp_rounds_sim = opp_rounds

        first_round = True

        while my_rounds_sim < 2 and opp_rounds_sim < 2:
            played_cards = []

            if first_round and play_hist:
                last_round = play_hist[-1]
                start = (current_round - 1) * 4

                # Recupera as cartas já jogadas
                for play in last_round[start:]:
                    if play[1] is not None:
                        played_cards.append((play[0], play[1]))

                # Quem joga depois da última carta conhecida
                if played_cards:
                    current_player = (played_cards[-1][0] + 1) % 4
                else:
                    current_player = self.position

                first_round = False

            # Completa a rodada
            while len(played_cards) < 4:
                player = current_player

                if hands[player]:
                    card = hands[player].pop(0)
                    played_cards.append((player, card))

                current_player = (current_player + 1) % 4

            # Vencedor da rodada
            winner = max(played_cards, key=lambda x: card_value(x[1], top_card))[0]

            if winner % 2 == self.position % 2:
                my_rounds_sim += 1
            else:
                opp_rounds_sim += 1

            # Vencedor começa a próxima rodada
            current_player = winner
        
        # Retorna vitória ou derrota
        return 1 if my_rounds_sim >= 2 else 0

    def _get_played_cards(self, current_play_list: list[PlayerDecision]):
        # NOTE:
        # Função ainda não sendo usada
        # Retornar todas as cartas jogadas na rodada atual
        return [
            current_play[1]
            for current_play in current_play_list
            if current_play[1] is not None
        ]

    def _sort_hand_by_score(self, top_card: Card) -> list[Card]:
        # Retorna as cartas em mãos ordenadas a partir do valor das cartas
        return sorted(
            self.cards.copy(), key=lambda card: card_value(card, top_card), reverse=True
        )

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

        if self.current_hand_score >= 1_000 and self.count_manilhas_in_hand > 0:
            return max(self.cards, key=lambda c: card_value(c, top_card))

        if self.current_hand_score >= 1_000:
            return max(self.cards, key=lambda c: card_value(c, top_card))

        if (
            self.current_hand_score >= 300
            and self.count_manilhas_in_hand > 0
            and team_score > 0
        ):
            return max(self.cards, key=lambda c: card_value(c, top_card))

        if self.current_hand_score >= 300 and team_score > 0:
            return max(self.cards, key=lambda c: card_value(c, top_card))

        if self.current_hand_score >= 300 and self.count_manilhas_in_hand > 0:
            return max(self.cards, key=lambda c: card_value(c, top_card))

        return min(self.cards, key=lambda c: card_value(c, top_card))

    """def play(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
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

        if (
            self.current_hand_score >= 300
            and self.count_manilhas_in_hand > 0
            and team_score > 0
        ):
            return (
                [2, selected_card] if not self.truco_requested else [1, selected_card]
            )

        if self.current_hand_score >= 300 and self.count_manilhas_in_hand > 0:
            return (
                [2, selected_card] if not self.truco_requested else [1, selected_card]
            )

        return [1, selected_card]"""

    def play(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
        # Calcula a melhor ordem de cartas
        probability, best_order = self._get_probability_of_winning(top_card, play_hist)

        # print(best_order[0], probability)

        return [1, best_order[0]]

    """def respond(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
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
            self.current_hand_score >= 300
            and self.count_manilhas_in_hand > 0
            and team_score > 0
        ):
            return 2 if is_raise_allowed else 1

        if self.current_hand_score >= 300 and self.count_manilhas_in_hand > 0:
            return 2 if is_raise_allowed else 1

        if self.current_hand_score >= 800 and team_score > 0:
            return 1

        return 0"""

    def respond(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
        # Intuitivo
        probability, _ = self._get_probability_of_winning_after_response(play_hist, top_card, self.cards)

        # print(probability)

        current_play_list = self._get_current_play_list(play_hist)
        player_decision = current_play_list[-1] if current_play_list else []
        status = player_decision[-1] if player_decision else None

        is_raise_allowed = (self._is_raise_allowed(status) if type(status) is int or status is None else False)

        if probability >= 0.85:
            return 2 if is_raise_allowed else 1

        if probability >= 0.60:
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
