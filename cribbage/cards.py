#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
cards.py
(c) Will Roberts  25 December, 2016

Define cards and card behaviour for cribbage.

Cards are integer values between 0 and 51, inclusive.  This
representation can be broken down into a "face value" (0 representing
Ace to 12 representing King), and a "suit" value (0 representing
Spades to 3 representing Clubs).
'''

import random
import numpy as np

# ------------------------------------------------------------
# Cards

CARD_FACES = 'A234567890JQK'
CARD_SUITS = 'SHDC'
CARD_VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

def make_card(face, suit):
    '''Creates a card value with the given `face` and `suit`.'''
    return face + suit * 13

def split_card(vint):
    '''Splits a card value into its `face` and `suit` values, base 0.'''
    return vint % 13, vint // 13

def split_tostring(splitpair):
    return '{}{}'.format(CARD_FACES[splitpair[0]], CARD_SUITS[splitpair[1]])

def card_tostring(vint):
    '''Returns a string representation of the given card value.'''
    return split_tostring(split_card(vint))

def hand_to_faces(hand, ace):
    ''' Convert a hand to a list of card face indices, starting at the value for ace. '''
    return sorted([split_card(c)[0] + ace for c in hand])  # pair of values, with ace=0

def hand_to_values(hand):
    ''' Convert a hand to a list of card point values. '''
    return np.clip(hand_to_faces(hand, 1), 1, 10)

def hand_tostring(hand):
    '''Return a string representation of an array of cards.'''
    splits = [split_card(c) for c in hand]
    splits = sorted(splits)
    splits = sorted(splits, key=lambda p: p[0])
    return '(' + ' '.join([split_tostring(c) for c in splits]) + ')'

def string_tocard(sval):
    '''Converts a string representation into a card value.'''
    return make_card(CARD_FACES.index(sval[0]), CARD_SUITS.index(sval[1]))

def make_deck():
    '''Creates a list containing all 52 card values.'''
    return list(range(52))

# ------------------------------------------------------------
# Utility Functions

def make_random_hand():
    '''Create a random 4-card cribbage hand.'''
    return random.sample(make_deck(), 4)

def make_random_hand_and_draw():
    '''Create a random 4-card cribbage hand, and a random card as the starter.'''
    hand_draw = random.sample(make_deck(), 5)
    return hand_draw[:4], hand_draw[4]

# ------------------------------------------------------------
# Determining cards' worth (for making 15s and 31s)

def card_worth(card):
    '''
    Returns the number of points the given card value is worth.

    Arguments:
    - `card`:
    '''
    return CARD_VALUES[split_card(card)[0]]

def cards_worth(cards):
    '''
    Calls `card_worth` on every value in `cards` and returns the sum.

    Arguments:
    - `cards`:
    '''
    return sum(card_worth(card) for card in cards)

# ------------------------------------------------------------
# Notes

# def n_choose_k(n,k):
#     '''Returns the number of ways of choosing `k` items from a set of `n`.'''
#     return math.factorial(n) // (math.factorial(k) * math.factorial(n-k))

# the number of ways of making 15s in a given hand with starter card
# n_choose_k(5,2) + n_choose_k(5,3) + n_choose_k(5,4) + n_choose_k(5,5)
# 26
# the number of ways of choosing two cards to discard into the crib
# n_choose_k(6,2)
# 15
