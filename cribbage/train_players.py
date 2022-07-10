#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Train the "learnable heuristics" player, Helen, to play better.

Repeatedly tweak one of Helen's parameters, playing many games against Max and
the previous Helen, and keeping the new parameters if they result in an improvement.
'''

import random
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from game import compare_players

from learnable_player import LearnableHeuristicCribbagePlayer
from maxerplayer import MaxerCribbagePlayer
from test_players import showstats, round_robin

def main():
    n = 2000
    passes = 2000
    Max = MaxerCribbagePlayer()
    Helen = LearnableHeuristicCribbagePlayer()

    players = [Helen, Max]
    player_names = ['Training Helen', 'Max']

    random.seed()

    data_columns = ['Value', 'Games Won', 'Games Played']
    results = {}  # a dict of one Numpy array with those columns, for each heuristic parameter ID.

    print(f"Playing {passes} passes of {n} games each - Ctrl+C to stop early.")
    print("")

    playing = True
    for pass_num in range(passes):
        try:
            if not playing:
                break
            Helen.randomize_weights()

            stats = round_robin(players, n)

            for i, p in enumerate(Helen.parameters):
                d = [p, stats[0], n]
                if i not in results:
                    results[i] = np.array([d])
                else:
                    results[i] = np.append(results[i], [d], axis=0)

        except KeyboardInterrupt:
            playing = False
            print("")

    # Graph.
    for i in range(Helen.NUM_PARAMS):
        pvals = results[i]
        data = pd.DataFrame(columns=data_columns, data=pvals)
        data.plot.hexbin(0, 1, gridsize=12, title=f"Heuristic {i}")
        plt.show()
        print(pvals)
        print("")

if __name__ == "__main__":
    main()
