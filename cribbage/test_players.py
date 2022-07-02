#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sys

import numpy as np

from game import compare_players

from randomplayer import RandomCribbagePlayer
from simpleplayer import SimpleCribbagePlayer
from learnable_player import LearnableHeuristicCribbagePlayer
from maxerplayer import MaxerCribbagePlayer


def showstats(scores, names):
    print("{:12} {:9}  {}".format('Player', 'Games won', 'Percent'))
    records = zip(scores, names)
    records = sorted(records, key=lambda r: r[0], reverse=True)
    for record in records:
        percent = 100 * record[0] / sum(scores)
        print("{:12} {:9.0f}   {:.1f}%".format(record[1], record[0], percent))

def round_robin(players, n=100):
    ''' Play n games between each pair of players, round-robin.
        Return a numpy array of the number of games each player won.
        Total sum of the result will be n * (len(players) choose 2).
    '''
    result = np.zeros(len(players))

    # Play the first players against all the others.
    me = players[0]
    others = players[1:]
    for i, other in enumerate(others, start=1):
        stats = compare_players([me, other], n)
        result[0] += stats[0]
        result[i] += stats[1]

    # Play all the others round-robin.
    if len(others) > 1:
        other_scores = np.append([0], round_robin(others, n))
        result += other_scores
    return result

n = 100
players = [LearnableHeuristicCribbagePlayer(), SimpleCribbagePlayer(), MaxerCribbagePlayer()]
player_names = ['Helen', 'Simon', 'Max']

trainee = LearnableHeuristicCribbagePlayer()
trainee.randomize_weights()
players.append(trainee)
player_names.append('Trainee')

stats = np.zeros(len(players))
playing = True
random.seed()

print(f"Playing continuously in batches of {n} games each for {len(players)} players - Ctrl+C to stop.")
while playing:
    try:
        stats += round_robin(players, n)
        showstats(stats, player_names)
        print("")
    except KeyboardInterrupt:
        playing = False
        print("Trainee parameters: " + str(trainee))
