import numpy as np

from cribbage import cards
from cribbage import cribbage_score
from cribbage import _cribbage_score
from cribbage.parameterized_player import ParameterizedHeuristicCribbagePlayer


def values_to_steps(values):
    ''' Given a list of numeric values, return a list of the sizes of the steps from one to the next.
        If a list of n values is given, a list of n - 1 values is returned.
    '''
    return [values[i + 1] - values[i] for i in range(len(values) - 1)]

def run_lengths(of_value, values):
    ''' Return a list of the lengths of runs of the given value in a list of values.
        A single appearance of of_value is listed as a run of length 1.
        A number of consecutive instances of of_value are listed as a run of that length.
        Intervening values separate runs.
    '''
    run_len = 0
    result = []
    for v in values:
        if v == of_value:
            run_len += 1
        else:
            if run_len:
                result.append(run_len)
                run_len = 0
    if run_len:
        result.append(run_len)

    return result

def sums_in_hand(values, target):
    ''' Return a count of the distinct ways to sum to the target in the given hand.
        Assumes values has at least one element.
        Arguments:
        * `values`: a list of the card values, from 1-10.
    '''
    if len(values) == 1:
        return values[0] == target
    else:
        result = sums_in_hand(values[1:], target)
        if values[0] == target:
            result += 1
        elif values[0] < target:
            result += sums_in_hand(values[1:], target - values[0])
        return result

def pair_values_in_hand(steps):
    ''' Return a count of the pairs in the given hand.
        Don't count triples or quadruples.
        Assume there are at most 4 cards, so 3 steps.
        Arguments:
        * `steps`: a list of the distances between pairs of subsequent cards in the hand.
    '''
    # Find the runs of same-valued cards.
    same = run_lengths(0, steps)
    # Count the runs of length two.
    return same.count(1)

def pairs_royal_in_hand(steps):
    ''' Return a count of the "pairs royal" (three of a kind) in the given hand.
        Doesn't count quadruples.
        Assumes there are at most 4 cards, so will only return 0 or 1.
        Arguments:
        * `steps`: a list of the distances between pairs of subsequent cards in the hand.
    '''
    # Find the runs of same-valued cards.
    same = run_lengths(0, steps)
    # Count the runs of length three.
    return same.count(2)

def runs_in_hand(steps):
    ''' Return a count of the runs in the given hand - 0 or 1 for a four-card hand.
        Assume hand is sorted by value, and has at most 4 cards.
        Arguments:
        * `steps`: a list of the distances between pairs of subsequent cards in the hand.
    '''
    # Since the hand is sorted, all steps are >= 0.
    # If they're 1, it indicates two adjacent cards that count up.
    # If you have a run of two 1s in steps, it means three adjacent cards.
    ascending = run_lengths(1, steps)
    return len([a for a in ascending if a > 1])

def double_runs_in_hand(steps):
    ''' Return a count of the double runs in the given hand - 0 or 1 for a four-card hand.
        Assume hand is sorted by value, and has exactly 4 cards.
        Arguments:
        * `steps`: a list of the distances between pairs of subsequent cards in the hand.
    '''
    if (steps == [0, 1, 1]) or (steps == [1, 0, 1]) or (steps == [1, 1, 0]):
        return 1
    else:
        return 0

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

        # What's likely to make you extra points in the starter?
        # Leave it to Max to score everything; we humans can just look for some patterns and bump up the expected value.
        # Count points in multiples of 1/12, because that's roughly the probability of getting any given value as starter.
        hand_faces = sorted(cards.hand_to_faces(keep, 1))
        # Find the steps - like [1, 0, 1] for [6, 7, 7, 8]
        hand_steps = values_to_steps(hand_faces)
        twelfths = 0

        # If you have a pair, you can make 4 more with a third, though half those cards are already out.
        twelfths += 0.5 * 4 * pair_values_in_hand(hand_steps)

        # If you have a run, you could extend it by 1 at each end, or count it again if you double any of its cards.
        twelfths += runs_in_hand(hand_steps) * (1 + 3*3 + 1)

        # If you have a double run, you get both of those plus more; the total should work out to about 2 = 24/12.
        twelfths += (24 - 10) * double_runs_in_hand(hand_steps)

        # If you have three of a kind (does anyone really say "pair royal"?), you could get a fourth for 6 more points.
        twelfths += 0.25 * 6 * pairs_royal_in_hand(hand_steps)

        # It's pretty likely that you'll get a ten-valued starter, so any 5 card or sums of 5 have a 4/12 chance of 2 points.
        twelfths += 4 * 2 * sums_in_hand(hand_faces, 5)

        score += round(twelfths / 12)

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
        # Except that a constant score for all discards makes no difference, so go from 0-2.
        span = dfs[1] - dfs[0]
        score = (13 - span) / 6.0 * self.P(1)

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
                # Statistically, this seems not to matter?
                # # And subtract more if it's a ten-card (i.e., you just led with a 5 or summed to 5).
                # if to15 == 10:
                #     score -= 2 * self.P(5)

        # Add if the total is 11, and you have any tens to play.
        # if total == 11:
        #     if 10 in new_values:
        #         score += self.P(6)

        # Leading choices:
        if len(linear_play) == 0:
            # Leading with your highest card < 5 is a good principle.
            # It saves any lower cards for making 31 later.
            face_value = cards.card_face(choice)
            if face_value < 5:
                # Is there anything higher than this in your hand that's less than 5?
                better = [c for c in hand if cards.card_face(c) > face_value and cards.card_face(c) < 5]
                if not better:
                    score += self.P(7)

            # But you might also lead with a 5 if you have 5-x-x-x.
            # Maybe just in the endgame.
            # (http://www.cribbageforum.com/Leading5.htm)
            if face_value == 5 and sum(new_values) == 30 and player_score > 100:
                score += self.P(8) * 2

        return score
