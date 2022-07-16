
import random
import numpy as np

from . import cards
from . player import CribbagePlayer


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
    Abstract base class for cribbage players that make decisions based on heuristic scores.
    '''

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
        deck = sorted(set(cards.make_deck()) - set(hand))
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

    def score_discard(self, keep, discard, is_dealer, deck):
        ''' Return this player's idea of the heuristic score for this discard. '''
        score = self.score_kept_cards(keep)

        # Find the value of the discarded pair.
        dfs = cards.hand_to_faces(discard, 1)
        if is_dealer:
            score += self.score_discard_to_own(dfs)
        else:
            score += self.score_discard_to_other(dfs)

        return score

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
            results[choice] = self.score_play(linear_play, choice, hand, played_cards, player_score)

        # Pick the best choice.
        return hand.index(pick_best(results))

    # The heuristic logic, to be implemented by derived classes:

    def score_kept_cards(self, keep):
        ''' Return the heuristic value of keeping the given hand after discarding.
            Arguments:
            - `keep`: a list of cards to be kept.
        '''
        raise NotImplementedError()

    def score_discard_to_own(self, dfs):
        ''' Return the heuristic value of discarding the given pair of cards to one's own crib.
            Arguments:
            - `dfs`: The two face values to discard, 1-relative.
        '''
        raise NotImplementedError()

    def score_discard_to_other(self, dfs):
        ''' Return the heuristic value of discarding the given pair of cards to the opponent's crib.
            Arguments:
            - `dfs`: The two face values to discard, 1-relative.
        '''
        raise NotImplementedError()

    def score_play(self, linear_play, choice, hand, played_cards, player_score):
        '''
        Return the heuristic value of playing this card.

        Arguments:
        - `linear_play`: the array of card values that have been
          played in this round by both players, zippered into a single
          list
        - `choice`: a card to play
        - `hand`: an array of 1 to 4 card values, including the chosen card
        - `played_cards`: a set of card values, containing all cards
          seen so far in this round (including the starter card)
        - `player_score`: the score of the current player
        '''
        raise NotImplementedError()
