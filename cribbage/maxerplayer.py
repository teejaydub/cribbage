#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
maxerplayer.py
(c) Timothy Weber, June 2022

Maxer is a player who can do all sorts of math in his head, and has an eidetic memory.
'''

from __future__ import absolute_import, print_function
import random
import numpy as np
from cards import make_deck, hand_tostring
from player import CribbagePlayer
from heuristicplayer import HeuristicCribbagePlayer
try:
    from _cribbage_score import score_hand, score_play
except ImportError:
    from cribbage_score import score_hand, score_play

class MaxerCribbagePlayer(HeuristicCribbagePlayer):
    '''
    Cribbage player that looks for maximum value with no lookahead, choosing randomly thereafter.
    '''

    # def __init__(self):
    #     '''Constructor.'''
    #     super().__init__()

    def score_discard(self, keep, discard, is_dealer, deck):
        ''' Return this player's idea of the heuristic score for this discard. '''
        # Find the best expected value of the score, over all possible starters.
        scores = [score_hand(keep, draw=c)
                   for c in deck]

        # Find the value of the discard pair, from a big table.

        return np.mean(scores)

    def score_play(self, linear_play, choice):
        # The play heuristic equals its immediate score.
        return score_play(linear_play + [choice])
