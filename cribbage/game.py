#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
game.py
(c) Will Roberts  25 December, 2016

An object representing a game of cribbage between two CribbagePlayers.
'''

from __future__ import absolute_import, print_function
import random

from . round import Round
from . utils import accumulate_dict

class Game(object):
    '''
    An object representing a game of cribbage between two
    CribbagePlayers.
    '''

    def __init__(self, players):
        '''
        Constructor.

        Arguments:
        - `players`: a list of two CribbagePlayer objects
        '''
        self.players = players
        # scores start at zero
        self.scores = [0, 0]
        # The players cut for first deal, and the person who cuts the
        # lowest card deals.
        # Randomly pick one player to start.
        self.dealer_idx = random.randrange(2)
        self.target_score = 121
        # a flag to cache the game state
        self.over = False
        # indicates the index of the player that won
        self.winner = None
        # a game consists of a series of Round objects
        self.rounds = []
        # the last one in the series is called the current_round
        self.current_round = None
        # Track the types of points earned over the game, for each player.
        self.point_types = [{}, {}]

    def play_round(self, verbose=False):
        '''
        Executes a single round of cribbage.

            Play proceeds through a succession of "hands", each hand
            consisting of a "deal", "the play" and "the show." At any
            time during any of these stages, if a player reaches the
            target score (usually 121), play ends immediately with
            that player being the winner of the game. This can even
            happen during the deal, since the dealer can score if a
            Jack is cut as the starter.

        Returns True if the game is not over after the round; False if
        the game is over (or was already over before the round).

        Arguments:
        - `verbose`:
        '''
        if verbose:
            print('Starting new round')
        self.current_round = Round(self, self.players, self.dealer_idx)
        self.rounds.append(self.current_round)
        if self.current_round.deal(verbose=verbose):
            if self.current_round.play(verbose=verbose):
                if self.current_round.show(verbose=verbose):
                    # swap the dealer
                    self.dealer_idx = int(not self.dealer_idx)
                    return True
        # notify the players of the winner
        for player_idx, player in enumerate(self.players):
            player.game_over(player_idx == self.winner)
        return False

    def play(self, verbose=False):
        '''
        Plays through the whole game of cribbage until it is over.
        '''
        while self.play_round(verbose=verbose):
            if verbose:
                print('New round')

    def award_points(self, player_idx, num_points, point_type, verbose=False):
        '''
        Awards `num_points` to player `player_idx`.

        Returns True if neither player has yet reached `target_score`,
        or False if one or more players have already finished the
        game.

        Arguments:
        - `player_idx`:
        - `point_type`: A string used to classify the points in statistics.
        '''
        if self.over:
            return False
        # check that neither player is over target_score
        if any(score >= self.target_score for score in self.scores):
            self.over = True
            return False
        # add the points to the given player's score
        self.scores[player_idx] += num_points

        # Classify the points scored for statistical analysis later.
        self.accumulate_data(player_idx, point_type, 'pt', num_points)

        # check if that player is now over target_score
        if self.scores[player_idx] >= self.target_score:
            if verbose:
                print('Player {} wins with {} points'.format(
                    player_idx + 1, self.scores[player_idx]))
            self.over = True
            self.winner = player_idx
            return False
        return True

    def player_type(self, player_idx):
        if player_idx == self.current_round.dealer_idx:
            return 'dealer'
        else:
            return 'pone'

    def count_hand(self, player_idx):
        self.accumulate_data(player_idx, 'hand', 'ct', 1)

    def count_crib(self, player_idx):
        self.accumulate_data(player_idx, 'crib', 'ct', 1)

    def count_play(self):
        self.accumulate_data(0, 'play', 'ct', 1)
        self.accumulate_data(1, 'play', 'ct', 1)

    def accumulate_data(self, player_idx, topic, noun, value):
        accumulate_dict(self.point_types[player_idx],
            '_'.join([self.player_type(player_idx), topic, noun]),
            value)

    def accumulate_point_types(self, into):
        ''' Adds this game's point_types stats into the given array. '''
        for player in range(2):
            for t, p in self.point_types[player].items():
                accumulate_dict(into[player], t, p)


def compare_players(players, num_games=1000, point_types=None):
    '''
    Utility function to compare two player objects.

    This function plays the two players against each other for the
    specified number of games, and returns a two-item list indicating
    how many time each player won.

    Arguments:
    - `players`: a list of two CribbagePlayer objects
    - `num_games`: the number of games to play
    - `point_types`: a two-item list of dicts breaking down the points won by each player,
        which is accumulated into unless it is None.
    '''
    stats = [0, 0]
    for _idx in range(num_games):
        game = Game(players)
        game.play()
        stats[game.winner] += 1

        if point_types:
            game.accumulate_point_types(point_types)

        if _idx % 30 == 0:
            print('.', end='', flush=True)
    return stats
