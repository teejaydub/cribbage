#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Train the "learnable heuristics" player, Helen, to play better.

Repeatedly tweak one of Helen's parameters, playing many games against Max and
the previous Helen, and keeping the new parameters if they result in an improvement.
'''

import random
import sys

import numpy as np

from game import compare_players

from learnable_player import LearnableHeuristicCribbagePlayer
from maxerplayer import MaxerCribbagePlayer
from test_players import showstats, round_robin

def main():
    n = 2000
    Max = MaxerCribbagePlayer()
    bestHelen = LearnableHeuristicCribbagePlayer()
    newHelen = LearnableHeuristicCribbagePlayer()

    bestHelen = LearnableHeuristicCribbagePlayer('0.15, 1.00, 0.54, 1.73, 1.00, 1.00, 1.00, 1.22, 1.0')

    print("Restoring prior best parameters: " + str(bestHelen))
    print("")

    players = [newHelen, bestHelen, Max]
    player_names = ['New Helen', 'Best Helen', 'Max']

    playing = True
    random.seed()

    print(f"Playing continuously in batches of {n} games each for {len(players)} players - Ctrl+C to stop.")
    print("")

    while playing:
        try:
            newHelen.parameters = list(bestHelen.parameters)
            newHelen.randomize_one_weight()
            print("New Helen's parameters: " + str(newHelen))

            stats = round_robin(players, n)
            showstats(stats, player_names)

            if stats[0] > stats[1] + 0.2:
                print("Old parameters:         " + str(bestHelen))
                print("Now she's the best Helen going forward.")
                bestHelen.parameters = newHelen.parameters
            else:
                print("Keeping former best:    " + str(bestHelen))

            print("")
        except KeyboardInterrupt:
            playing = False
            print("")

if __name__ == "__main__":
    main()
