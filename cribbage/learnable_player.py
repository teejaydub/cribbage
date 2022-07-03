import numpy as np

import cards
import cribbage_score
import _cribbage_score
from parameterized_player import ParameterizedHeuristicCribbagePlayer

class LearnableHeuristicCribbagePlayer(ParameterizedHeuristicCribbagePlayer):
    '''
    A cribbage player with intermediate-level heuristics,
    emphasizing a set of them that can be easily learnable and usable by a human.
    Can be trained automatically to improve its heuristics.
    '''

    NUM_PARAMS = 9

    def score_kept_cards(self, keep):
        # Find the score without a starter.
        score = cribbage_score.score_hand(keep, None)

        # Add one point per card under 5 left in hand, for pegging potential.
        lows = len([c for c in keep if cards.card_worth(c) < 5])
        score += min(lows, self.P(0) * 2)

        return score

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
        score = 4 + (13 - span) / 6.0 * self.P(1)

        # Edge cards are less risky, because they can only be extended in one direction.
        if 1 in dfs or 13 in dfs:
            score -= 1

        # 5s or sums of 5 or 15 are powerful.
        total = sum(np.clip(dfs, 1, 10))
        if 5 in dfs or total == 5 or total == 15:
            score += self.P(2)

        # As a separate step, a pair is a given - but we've already seen some of its effect as a close span.
        if span == 0:
            score += self.P(3)

        # Jacks have a 1/4 chance to make His Nobs.
        jacks = len([f for f in dfs if f == 11])
        score -= jacks / 4

        return -score

    def score_play(self, linear_play, choice, hand, played_cards, player_score):
        # Start with the immediate score.
        new_layout = linear_play + [choice]
        new_hand = set(hand) - set([choice])
        score = _cribbage_score.score_play(new_layout)

        # Subtract if the resulting total is > 4 and less than 15, because your opponent might make it.
        # But that's OK if you can make a pair with the card that will make 15.
        total = cards.cards_worth(new_layout)
        new_values = cards.hand_to_values(new_hand)
        if total > 4 and total < 15:
            to15 = 15 - total
            if to15 not in new_values:
                score -= self.P(4)
                # And subtract more if it's a ten-card.
                if to15 == 10:
                    score -= self.P(5)

        # Add if the total is 11, and you have any tens to play.
        if total == 11:
            if 10 in new_values:
                score += self.P(6)

        # Leading choices:
        if len(linear_play) == 0:
            # Leading with your highest card < 5 is a good principle.
            # It saves any lower cards for making 31 later.
            face_value = cards.card_face(choice)
            if face_value < 4:
                # Is there anything higher than this in your hand that's less than 5?
                better = [c for c in hand if cards.card_face(c) > face_value and cards.card_face(c) < 5]
                if better:
                    score -= self.P(7)

            # But you might also lead with a 5 if you have 5-x-x-x.
            # Maybe just in the endgame.
            # (http://www.cribbageforum.com/Leading5.htm)
            if face_value == 5 and sum(new_values) == 35 and player_score > 100:
                score += self.P(8) * 2

        return score
