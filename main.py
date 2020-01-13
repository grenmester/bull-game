import click
import numpy as np
import random

NUM_PILES = 4
PLAYER_HAND_SIZE = 10
MAX_CARD_SIZE = 100


class Game(object):
    def __init__(self, num_players):
        self.num_players = num_players
        game_deck = set(range(1, MAX_CARD_SIZE))
        self.players = []
        for _ in range(num_players):
            # Deal cards to players
            player_hand = random.sample(game_deck, PLAYER_HAND_SIZE)
            game_deck.difference_update(player_hand)
            self.players.append(Player(player_hand))
        # Initialize game board
        self.board = Board(random.sample(game_deck, NUM_PILES))


class Board(object):
    def __init__(self, starting_cards):
        self.board = np.zeros((NUM_PILES, PLAYER_HAND_SIZE), dtype=int)
        self.board[:, 0] = starting_cards


class Player(object):
    def __init__(self, hand):
        self.hand = sorted(hand)
        self.points = 0


@click.command()
def main():
    num_players = click.prompt('Number of players', type=int)
    game = Game(num_players)
