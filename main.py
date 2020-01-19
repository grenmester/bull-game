import abc
import bisect
import click
import numpy as np
import random

DECK_SIZE = 104
MAX_NUM_PLAYERS = 10
NUM_PILES = 4
PILE_SIZE = 5
PLAYER_HAND_SIZE = 10


class Card(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    @property
    def points(self):
        '''
        Return the point value of the card.
        '''
        if self.value % 55 == 0:
            return 7
        elif self.value % 11 == 0:
            return 5
        elif self.value % 10 == 0:
            return 3
        elif self.value % 5 == 0:
            return 2
        else:
            return 1


class Pile(object):
    def __init__(self, base_value):
        self.cards = [Card(base_value)]
        self.size = 1
        self.high_value = base_value

    def __str__(self):
        return ' '.join([str(card) for card in self.cards])

    def add_value(self, value):
        '''
        Add card to pile. Reset the pile if the pile is already at max size.
        Return points given to player for move.
        '''
        if self.size >= PILE_SIZE or value < self.high_value:
            # Reset pile
            points = sum([card.points for card in self.cards])
            self.__init__(value)
            return points
        else:
            # Add card to pile
            self.cards.append(Card(value))
            self.size += 1
            self.high_value = value
            return 0


class Player(abc.ABC):
    def __init__(self, uid, name, hand):
        self.name = f'(UID: {uid}) {name}'
        self.hand = [Card(card) for card in sorted(hand)]
        self.points = 0

    def __str__(self):
        return ' '.join([str(card) for card in self.hand])

    @abc.abstractmethod
    def select_value(self):
        '''
        Select a card value from the player hand.
        '''
        pass

    @abc.abstractmethod
    def select_pile(self):
        '''
        Select a pile to be replaced.
        '''
        pass


class HumanPlayer(Player):
    def __init__(self, uid, hand):
        name = click.prompt(f'Player {uid}\'s name', type=str)
        super().__init__(uid, name, hand)

    def select_value(self):
        '''
        Query a card value from the player hand.
        '''
        click.echo(self)
        selected_idx = click.prompt(
            f'{self.name}\'s move', type=click.IntRange(1, len(self.hand))) - 1
        selected_card = self.hand[selected_idx]
        self.hand.remove(selected_card)
        return selected_card.value

    def select_pile(self):
        '''
        Query a pile to be replaced.
        '''
        return click.prompt(
            'Select pile', type=click.IntRange(1, NUM_PILES)) - 1


class RandomPlayer(Player):
    def __init__(self, uid, hand):
        super().__init__(uid, 'CPU', hand)

    def select_value(self):
        '''
        Select a random card value from the player hand.
        '''
        selected_card = random.choice(self.hand)
        self.hand.remove(selected_card)
        return selected_card.value

    def select_pile(self):
        '''
        Select a random pile to be replaced.
        '''
        return random.choice(range(NUM_PILES))


class Game(object):
    def __init__(self, player_types):
        self.num_players = len(player_types)
        game_deck = set(range(1, DECK_SIZE+1))
        self.players = []
        # Iterate over list of player classes
        for idx, player_type in enumerate(player_types):
            # Deal cards to players
            player_hand = random.sample(game_deck, PLAYER_HAND_SIZE)
            game_deck.difference_update(player_hand)
            self.players.append(player_type(idx+1, player_hand))
        # Initialize game board
        base_values = sorted(random.sample(game_deck, NUM_PILES))
        self.board = [Pile(base_value) for base_value in base_values]

    def __str__(self):
        return '\n'.join([str(pile) for pile in self.board])

    def play_turn(self, player):
        '''
        Play one turn of one player.
        '''
        # Player chooses move
        selected_value = player.select_value()
        high_values = [pile.high_value for pile in self.board]
        if selected_value > min(high_values):
            # Regular move
            pile = bisect.bisect(high_values, selected_value) - 1
        else:
            # A pile has to be replaced
            pile = player.select_pile()
        # Add card to pile and give points to player
        player.points += self.board[pile].add_value(selected_value)
        # Resort piles by highest value card
        self.board = sorted(self.board, key=lambda pile: pile.high_value)

    def play_game(self):
        '''
        Play a game.
        '''
        for turn in range(PLAYER_HAND_SIZE):
            for player in self.players:
                click.echo('\n'.join(['-'*25, str(self), '-'*25]))
                self.play_turn(player)
        # Compute scores
        all_points = [player.points for player in self.players]
        winner_idxs = np.argwhere(all_points == np.amin(all_points)).flatten()
        winners = ', '.join([self.players[idx].name for idx in winner_idxs])
        click.echo(f'The final scores are {all_points}.')
        if len(winner_idxs) == 1:
            click.echo(f'The winner is {winners}!')
        else:
            click.echo(f'There is a tie between {winners}!')


@click.command()
def main():
    '''
    Query number of players, player types, and player names then play a game.
    '''
    num_players = click.prompt(
        'Number of players', type=click.IntRange(2, MAX_NUM_PLAYERS))
    player_types = []
    player_type_dict = {
        'human': HumanPlayer,
        'random': RandomPlayer,
    }
    # Query player types
    for idx in range(num_players):
        player_type = click.prompt(f'Player {idx+1} type', type=click.Choice(
            ['human', 'random'], case_sensitive=False))
        player_type = player_type_dict[player_type]
        player_types.append(player_type)
    # Play game
    game = Game(player_types)
    game.play_game()
