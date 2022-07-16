
import random
import numpy as np

from . import cards
from . player import CribbagePlayer
from . heuristicplayer import HeuristicCribbagePlayer
try:
    from . _cribbage_score import score_hand, score_play, get_legal_play_idxs

except ImportError:
    from . cribbage_score import score_hand, score_play

# Tables from Schell, http://www.cribbageforum.com/SchellDiscard.htm
# Indices are card values, 0-12, and values are the expected value of the resulting crib.
DISCARD_TO_OWN_EV = [
    [5.38, 4.23, 4.52, 5.43, 5.45, 3.85, 3.85, 3.80, 3.40, 3.42, 3.65, 3.42, 3.41],
    [4.23, 5.72, 7.00, 4.52, 5.45, 3.93, 3.81, 3.66, 3.71, 3.55, 3.84, 3.58, 3.52],
    [4.52, 7.00, 5.94, 4.91, 5.97, 3.81, 3.58, 3.92, 3.78, 3.57, 3.90, 3.59, 3.67],
    [5.43, 4.52, 4.91, 5.63, 6.48, 3.85, 3.72, 3.83, 3.72, 3.59, 3.88, 3.59, 3.60],
    [5.45, 5.45, 5.97, 6.48, 8.79, 6.63, 6.01, 5.48, 5.43, 6.66, 7.00, 6.63, 6.66],
    [3.85, 3.93, 3.81, 3.85, 6.63, 5.76, 4.98, 4.63, 5.13, 3.17, 3.41, 3.23, 3.13],
    [3.85, 3.81, 3.58, 3.72, 6.01, 4.98, 5.92, 6.53, 4.04, 3.23, 3.53, 3.23, 3.26],
    [3.80, 3.66, 3.92, 3.83, 5.48, 4.63, 6.53, 5.45, 4.72, 3.80, 3.52, 3.19, 3.16],
    [3.40, 3.71, 3.78, 3.72, 5.43, 5.13, 4.04, 4.72, 5.16, 4.29, 3.97, 2.99, 3.06],
    [3.42, 3.55, 3.57, 3.59, 6.66, 3.17, 3.23, 3.80, 4.29, 4.76, 4.61, 3.31, 2.84],
    [3.65, 3.84, 3.90, 3.88, 7.00, 3.41, 3.53, 3.52, 3.97, 4.61, 5.33, 4.81, 3.96],
    [3.42, 3.58, 3.59, 3.59, 6.63, 3.23, 3.23, 3.19, 2.99, 3.31, 4.81, 4.79, 3.46],
    [3.41, 3.52, 3.67, 3.60, 6.66, 3.13, 3.26, 3.16, 3.06, 2.84, 3.96, 3.46, 4.58],
    ]
DISCARD_TO_OTHER_EV = [
    [6.02, 5.07, 5.07, 5.72, 6.01, 4.91, 4.89, 4.85, 4.55, 4.48, 4.68, 4.33, 4.30],
    [5.07, 6.38, 7.33, 5.33, 6.11, 4.97, 4.97, 4.94, 4.70, 4.59, 4.81, 4.56, 4.45],
    [5.07, 7.33, 6.68, 5.96, 6.78, 4.87, 5.01, 5.05, 4.87, 4.63, 4.86, 4.59, 4.48],
    [5.72, 5.33, 5.96, 6.53, 7.26, 5.34, 4.88, 4.94, 4.68, 4.53, 4.85, 4.46, 4.36],
    [6.01, 6.11, 6.78, 7.26, 9.37, 7.47, 7.00, 6.30, 6.15, 7.41, 7.76, 7.34, 7.25],
    [4.91, 4.97, 4.87, 5.34, 7.47, 7.08, 6.42, 5.86, 6.26, 4.31, 4.57, 4.22, 4.14],
    [4.89, 4.97, 5.01, 4.88, 7.00, 6.42, 7.14, 7.63, 5.26, 4.31, 4.68, 4.32, 4.27],
    [4.85, 4.94, 5.05, 4.94, 6.30, 5.86, 7.63, 6.82, 5.83, 5.10, 4.59, 4.31, 4.20],
    [4.55, 4.70, 4.87, 4.68, 6.15, 6.26, 5.26, 5.83, 6.39, 5.43, 4.96, 4.11, 4.03],
    [4.48, 4.59, 4.63, 4.53, 7.41, 4.31, 4.31, 5.10, 5.43, 6.08, 5.63, 4.61, 3.88],
    [4.68, 4.81, 4.86, 4.85, 7.76, 4.57, 4.68, 4.59, 4.96, 5.63, 6.42, 5.46, 4.77],
    [4.33, 4.56, 4.59, 4.46, 7.34, 4.22, 4.32, 4.31, 4.11, 4.61, 5.46, 5.79, 4.49],
    [4.30, 4.45, 4.48, 4.36, 7.25, 4.14, 4.27, 4.20, 4.03, 3.88, 4.77, 4.49, 5.65],
    ]

class MaxerCribbagePlayer(HeuristicCribbagePlayer):
    '''
    Cribbage player that uses statistical tables and lookahead, including
    tools that would be hard to use perfectly as a human.
    '''

    def score_discard(self, keep, discard, is_dealer, deck):
        ''' Return this player's idea of the heuristic score for this discard. '''
        # Find the expected value of the hand, over all possible starters.
        scores = [score_hand(keep, draw=c)
                   for c in deck]
        result = np.mean(scores)

        # Find the value of the discard pair, from a big table.
        dfs = cards.hand_to_faces(discard, 0)  # pair of values, with ace=0
        if is_dealer:
            result += DISCARD_TO_OWN_EV[dfs[0]][dfs[1]]
        else:
            result -= DISCARD_TO_OTHER_EV[dfs[0]][dfs[1]]

        return result

    def score_play(self, linear_play, choice, hand, played_cards, player_score):
        # Start with the points you'll make from this play.
        new_layout = linear_play + [choice]
        new_hand = set(hand) - set([choice])
        score = score_play(new_layout)

        # Subtract what your opponent might make on her next play.
        possible_cards = sorted(set(cards.make_deck()) - set(played_cards) - set(hand))
        next_moves = get_legal_play_idxs(possible_cards, new_layout)
        if next_moves:
            next_score = np.mean([score_play(new_layout + [c]) for c in next_moves])
            score -= next_score

        return score
