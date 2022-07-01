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

from cards import make_deck, hand_tostring, hand_to_faces, hand_to_values, split_card, card_worth, cards_worth, card_face
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
    if not d:
        return None
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
            results[choice] = self.score_play(linear_play, choice, hand, played_cards)

        # Pick the best choice.
        return hand.index(pick_best(results))

    # The heuristic logic:

    def score_discard(self, keep, discard, is_dealer, deck):
        ''' Return this player's idea of the heuristic score for this discard. '''
        # Find the score without a starter.
        score = score_hand(keep, None)

        # Find the value of the discard pair, from simple rules.
        dfs = hand_to_faces(discard, 1)
        score += self.score_discard_indices(dfs, is_dealer)

        # Add one point per card under 5, for pegging potential.
        lows = len([c for c in keep if card_worth(c) < 5])
        score += lows

        return score

    def score_discard_indices(self, dfs, is_dealer):
        ''' Return the heuristic value of discarding the given pair of card indices (1-relative).
            Arguments:
            - `dfs`: The two face values to discard, 1-relative.
            - `is_dealer`: True if the discard is to the player's own crib.
        '''
        if is_dealer:
            return self.score_discard_to_own(dfs)
        else:
            return self.score_discard_to_other(dfs)

    def score_discard_to_own(self, dfs):
        # From http://www.cribbageforum.com/YourCrib.htm

        if np.array_equal(dfs, (5, 5)):
            return 4

        elif np.array_equal(dfs, (2, 3)):
            return 2
        elif np.array_equal(dfs, (4, 5)):
            return 2
        elif np.array_equal(dfs, (5, 6)):
            return 2
        elif dfs[0] == 5 and dfs[1] >= 10:
            return 2
        elif np.array_equal(dfs, (7, 8)):
            return 2

        elif np.array_equal(dfs, (1, 4)):
            return 1
        elif dfs[0] == dfs[1] and dfs[0] <= 8:
            return 1
        elif 5 in dfs:
            return 1

        else:
            return 0

    def score_discard_to_other(self, dfs):
        # Simplified version of http://www.cribbageforum.com/OppCrib.htm
        # Returns a heuristic score of the negative of the expected crib score.

        # Prefer large spans that don't include low cards.
        # Spans can run from 1 to 12, and generally produce total points from 4.3 to 6+.
        # So pretend it's 4 points, then scaling up to 6 points for adjacent
        span = dfs[1] - dfs[0]
        score = 4 + (13 - span) / 6

        # Edge cards are less risky, because they can only be extended in one direction.
        if 1 in dfs or 13 in dfs:
            score -= 1

        # 5s or sums of 5 or 15 are powerful.
        total = sum(np.clip(dfs, 1, 10))
        if 5 in dfs or total == 5 or total == 15:
            score += 1

        # As a separate step, a pair is a given - but we've already seen some of its effect as a close span.
        if span == 0:
            score += 1

        return -score


    def score_play(self, linear_play, choice, hand, played_cards):
        # Start with the immediate score.
        new_layout = linear_play + [choice]
        new_hand = set(hand) - set([choice])
        score = score_play(new_layout)

        # Subtract if the resulting total is > 4 and less than 15, because your opponent might make it.
        # But that's OK if you can make a pair with the card that will make 15.
        total = cards_worth(new_layout)
        new_values = hand_to_values(new_hand)
        if total > 4 and total < 15:
            to15 = 15 - total
            if to15 not in new_values:
                score -= 1

        # Leading with your highest card < 5 is a good idea.
        # It saves any lower cards for making 31 later.
        face_value = card_face(choice)
        if len(linear_play) == 0 and face_value < 4:
            # Is there anything higher than this in your hand that's less than 5?
            better = [c for c in hand if card_face(c) > face_value and card_face(c) < 5]
            if better:
                score -= 1

        # Add if the total is 11, and you have any tens to play.
        if total == 11:
            if 10 in new_values:
                score += 1

        return score
