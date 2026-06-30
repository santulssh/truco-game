### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    Lucas Henrique dos Santos
# RA #01 (quem entregou o código):      220449
# Nome #02:                             João Rodolfo Berger Andrade
# RA #02:                               306480

import random
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

class ProbabilisticStrategist(Player):
    current_hand_score: int = 0
    count_manilhas_in_hand: int = 0
    truco_requested = False

    def __init__(self, ra: str, name: str, image_path="img/none.jpg"):
        super().__init__(ra, name, image_path)
        
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


    def _get_probability_of_winning(self, play_hist, top_card, cards):
        # Calcula a probabilidade de vencer a mão considerando todas as ordens das cartas

        # Cartas que podem estar com os outros jogadores
        not_played = get_cards_not_played(play_hist, top_card, cards)

        current_round = get_current_round(play_hist)    

        # Quantas cartas já foram jogadas na rodada
        number_cards_in_round = 0
        if play_hist:
            number_cards_in_round = len(get_cards_played(play_hist[-1])) % 4

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
                result = self.simulate(play_hist, top_card, not_played, current_round, number_cards_in_round, card_order)

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

        current_round = get_current_round(play_hist)

        number_cards_in_round = 0
        if play_hist:
            number_cards_in_round = (
                len(get_cards_played(play_hist[-1])) % 4
            )

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
                hands[player].sort(
                    key=lambda c: card_value(c, top_card),
                    reverse=True
                )

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

    def _is_raise_allowed(self, status: int | None):
        # Verifica se é válido aumentar o valor do truco
        if status is None or (type(status) is int and status < 12):
            return True
        return False
    
    def play(self, top_card: Card, play_hist: GameHist, score_hist: GameScore):
        # Calcula a melhor ordem de cartas
        probability, best_order = self._get_probability_of_winning(play_hist, top_card, self.cards)
        
        # print(best_order[0], probability)

        return [1,best_order[0]]

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
        ProbabilisticStrategist(
            "000000", "Strategist1", "img/custom/Headphone_Cat.jpg"
        ),
        ProbabilisticStrategist("100000", "Strategist2", "img/none.jpg"),
    )