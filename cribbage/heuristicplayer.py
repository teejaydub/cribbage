#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
heuristicplayer.py
(c) Timothy Weber, June 2022

This player uses basic heuristics, like a normal person could memorize.
The class also provides some mechanics that other Player classes can use to simplify evaluation.
'''

from __future__ import absolute_import, print_function
import random
import numpy as np
from cards import make_deck, hand_tostring, split_card, card_worth
from player import CribbagePlayer
# try:
#     from _cribbage_score import score_hand, score_play
# except ImportError:
from cribbage_score import score_hand, score_play

KEEP_COMBINATIONS = [(0, 1, 2, 3),
                     (0, 1, 2, 4),
                     (0, 1, 2, 5),
                     (0, 1, 3, 4),
                     (0, 1, 3, 5),
                     (0, 1, 4, 5),
                     (0, 2, 3, 4),
                     (0, 2, 3, 5),
                     (0, 2, 4, 5),
                     (0, 3, 4, 5),
                     (1, 2, 3, 4),
                     (1, 2, 3, 5),
                     (1, 2, 4, 5),
                     (1, 3, 4, 5),
                     (2, 3, 4, 5)]


def pick_best(d: dict):
    '''
    Return a key from d with the largest value.
    If there are multiple keys with the same value, pick at random.
    '''
    max_value = max(d.values())
    best_choices = [k for (k, v) in d.items() if v == max_value]
    return random.choice(best_choices)


class HeuristicCribbagePlayer(CribbagePlayer):
    '''
    Cribbage player with moderately experienced heuristics.
    '''

    # def __init__(self):
    #     '''Constructor.'''
    #     super().__init__()

    def discard(self,
                is_dealer,
                hand,
                player_score,
                opponent_score):
        '''
        Asks the player to select two cards from `hand` for discarding to
        the crib.

        Return is a list of two indices into the hand array.

        Arguments:
        - `is_dealer`: a flag to indicate whether the given player is
          currently the dealer or not
        - `hand`: an array of 6 card values
        - `player_score`: the score of the current player
        - `opponent_score`: the score of the current player's opponent
        '''
        # Loop through all possibilities for what to keep
        deck = sorted(set(make_deck()) - set(hand))
        npdeck = np.array(deck)
        nphand = np.array(hand)
        results = {}
        for keep_idxs in KEEP_COMBINATIONS:
            keep = list(nphand[list(keep_idxs)])
            discard_values = set(hand) - set(keep)

            # Find the heuristic score for this discard.
            results[tuple(discard_values)] = self.score_discard(keep, discard_values, is_dealer, npdeck)

        # Pick any arbitrary discard set with the best score.
        best_discard = pick_best(results)

        # Return the indices of the cards to discard.
        # convert back into indices into hand
        return [idx for idx, card in enumerate(hand) if card in best_discard]

    def play_card(self,
                  is_dealer,
                  hand,
                  played_cards,
                  is_go,
                  linear_play,
                  player_score,
                  opponent_score,
                  legal_moves):
        '''
        Asks the player to select one card from `hand` to play during a
        cribbage round.

        Return an index into the hand array.

        Arguments:
        - `is_dealer`: a flag to indicate whether the given player is
          currently the dealer or not
        - `hand`: an array of 1 to 4 card values
        - `played_cards`: a set of card values, containing all cards
          seen so far in this round (including the starter card)
        - `is_go`: a flag to indicate if the play is currently in go or not
        - `linear_play`: the array of card values that have been
          played in this round by both players, zippered into a single
          list
        - `player_score`: the score of the current player
        - `opponent_score`: the score of the current player's opponent
        - `legal_moves`: a list of indices into `hand` indicating
          which cards from the hand may be played legally at this
          point in the game
        '''
        # Enumerate the choices with the best heuristic score.
        choices = [hand[x] for x in legal_moves]
        results = {}
        for choice in choices:
            results[choice] = self.score_play(linear_play, choice)

        # Pick the best choice.
        return hand.index(pick_best(results))

    # The heuristic logic:

    def score_discard(self, keep, discard, is_dealer, deck):
        ''' Return this player's idea of the heuristic score for this discard. '''
        # Find the score without a starter.
        score = score_hand(keep, None)

        # Find the value of the discard pair, from simple rules.
        dvalues = sorted([split_card(c)[0] + 1 for c in discard])  # start with ace=1
        score += self.score_discard_values(dvalues, is_dealer)

        return score

    def score_discard_values(self, dvalues, is_dealer):
        ''' Return the heuristic value of discarding the given pair of card values (1-relative). '''
        if is_dealer:
            return self.score_discard_to_own(dvalues)
        else:
            return self.score_discard_to_other(dvalues)

    def score_discard_to_own(self, dvalues):
        # From http://www.cribbageforum.com/YourCrib.htm

        if np.array_equal(dvalues, (5, 5)):
            return 4

        elif np.array_equal(dvalues, (2, 3)):
            return 2
        elif np.array_equal(dvalues, (4, 5)):
            return 2
        elif np.array_equal(dvalues, (5, 6)):
            return 2
        elif dvalues[0] == 5 and dvalues[1] >= 10:
            return 2
        elif np.array_equal(dvalues, (7, 8)):
            return 2

        elif np.array_equal(dvalues, (1, 4)):
            return 1
        elif dvalues[0] == dvalues[1] and dvalues[0] <= 8:
            return 1
        elif dvalues[0] == 5 or dvalues[1] == 5:
            return 1

        else:
            return 0

    def score_discard_to_other(self, dvalues):
        # Simplified version of http://www.cribbageforum.com/OppCrib.htm
        # Returns a heuristic score of the negative of the expected crib score.

        # Prefer large spans that don't include low cards.
        # Spans can run from 1 to 12, and generally produce total points from 4.3 to 6+.
        # So pretend it's 4 points, then scaling up to 6 points for adjacent
        span = dvalues[1] - dvalues[0]
        score = 4 + (13 - span) / 6

        # 5s or sums of 5 or 15 are powerful.
        total = sum(np.clip(dvalues, 1, 10))
        if 5 in dvalues or total == 5 or total == 15:
            score += 1

        # As a separate step, a pair is a given - but we've already seen some of its effect as a close span.
        if span == 0:
            score += 1

        return -score


    def score_play(self, linear_play, choice):
        # The play heuristic equals its immediate score.
        return score_play(linear_play + [choice])
