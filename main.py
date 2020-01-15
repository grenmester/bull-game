import bisect
import click
import numpy as np
import random

DECK_SIZE = 104
MAX_NUM_PLAYERS = 10
NUM_PILES = 4
PILE_SIZE = 5
PLAYER_HAND_SIZE = 10


class Pile(object):
    def __init__(self, base_card):
        self.cards = np.zeros(PILE_SIZE, dtype=int)
        self.cards[0] = base_card
        self.size = 1
        self.high_card = base_card

    def __str__(self):
        return str(self.cards[:self.size])

    def add_card(self, card):
        if self.size >= PILE_SIZE or card < self.high_card:
            # Reset pile
            points = self.size
            self.__init__(card)
            return points
        else:
            # Add card to pile
            self.cards[self.size] = card
            self.size += 1
            self.high_card = card
            return 0


class Player(object):
    def __init__(self, hand):
        self.hand = sorted(hand)
        self.points = 0

    def __str__(self):
        return str(self.hand)

    def select_card(self):
        click.echo(self)
        selected_idx = click.prompt(
            'Player move', type=click.IntRange(0, len(self.hand)-1))
        selected_card = self.hand[selected_idx]
        self.hand.remove(selected_card)
        return selected_card

    def select_pile(self):
        return click.prompt('Select pile', type=click.IntRange(0, NUM_PILES-1))


class Game(object):
    def __init__(self, num_players):
        self.num_players = num_players
        game_deck = set(range(1, DECK_SIZE+1))
        self.players = []
        # Deal cards to players
        for _ in range(num_players):
            player_hand = random.sample(game_deck, PLAYER_HAND_SIZE)
            game_deck.difference_update(player_hand)
            self.players.append(Player(player_hand))
        # Initialize game board
        base_cards = sorted(random.sample(game_deck, NUM_PILES))
        self.board = [Pile(base_card) for base_card in base_cards]

    def __str__(self):
        return '\n'.join([str(pile) for pile in self.board])

    def play_turn(self, player):
        # Player chooses move
        selected_card = player.select_card()
        high_cards = [pile.high_card for pile in self.board]
        if selected_card > min(high_cards):
            # Regular move
            card_pile = bisect.bisect(high_cards, selected_card) - 1
        else:
            # A pile has to be replaced
            card_pile = player.select_pile()
        # Add card to pile and give points to player
        player.points += self.board[card_pile].add_card(selected_card)
        # Resort piles by highest value card
        self.board = sorted(self.board, key=lambda pile: pile.high_card)

    def play_game(self):
        for turn in range(PLAYER_HAND_SIZE):
            for player in self.players:
                click.echo(self)
                self.play_turn(player)
        # Compute scores
        all_points = [player.points for player in self.players]
        winners = np.argwhere(all_points == np.amin(all_points)).flatten()
        click.echo(f'The final scores are {all_points}.')
        if len(winners) == 1:
            winner = winners[0]
            click.echo(f'The winner is Player {winner}!')
        else:
            winners = ', '.join([f'Player {winner}' for winner in winners])
            click.echo(f'There is a tie between {winners}!')


@click.command()
def main():
    num_players = click.prompt(
        'Number of players', type=click.IntRange(2, MAX_NUM_PLAYERS))
    game = Game(num_players)
    game.play_game()
