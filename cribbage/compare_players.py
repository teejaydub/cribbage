#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sys

import numpy as np

from . game import compare_players

from . randomplayer import RandomCribbagePlayer
from . simpleplayer import SimpleCribbagePlayer
from . learnable_player import LearnableHeuristicCribbagePlayer
from . maxerplayer import MaxerCribbagePlayer

def point_averages(point_types, games_each):
    result = ''
    for t in sorted(point_types.keys()):
        if t.endswith('_pt'):
            base = t.removesuffix('_pt')
            ct = base + '_ct'
            display = base.replace('_', ' ')
            result += "  {}: {:.1f}".format(display, point_types[t] / point_types[ct])
    result += "  {:.1f}+{:.1f}={:.1f}".format(
        point_types['D_hand_ct'] / games_each,
        point_types['P_hand_ct'] / games_each,
        (point_types['D_hand_ct'] + point_types['P_hand_ct']) / games_each)
    return result

def showstats(scores, names, games_each, point_types):
    print("")
    print("{:12} {:9}  {}  {:63}  {}".format('Player', 'Games won', 'Percent',
        'Averages for Dealer and Pone', 'Hand counts'))
    records = zip(scores, names, point_types)
    records = sorted(records, key=lambda r: r[0], reverse=True)  # best first
    for record in records:
        percent = 100 * record[0] / games_each
        print("{:12} {:9.0f}   {:.1f}% {}".format(record[1], record[0], percent,
            point_averages(record[2], games_each)))

def round_robin(players, n=100, point_types=None):
    ''' Play n games between each pair of players, round-robin.
        Return a numpy array of the number of games each player won.
        Total sum of the result will be n * (len(players) choose 2).
        Accumulate point type data if point_types is supplied.
    '''
    result = np.zeros(len(players))

    # Play the first players against all the others.
    me = players[0]
    others = players[1:]
    for i, other in enumerate(others, start=1):
        pt = None
        if point_types:
            pt = [point_types[0], point_types[i]]

        stats = compare_players([me, other], n, point_types=pt)
        result[0] += stats[0]
        result[i] += stats[1]

    # Play all the others round-robin.
    if len(others) > 1:
        other_scores = np.append([0], round_robin(others, n, point_types[1:]))
        result += other_scores
    return result

def main():
    n = 100
    players = [LearnableHeuristicCribbagePlayer(), SimpleCribbagePlayer(), MaxerCribbagePlayer()]
    player_names = ['Helen', 'Simon', 'Max']

    stats = np.zeros(len(players))
    point_types = [{} for p in players]
    games_each = 0
    playing = True
    random.seed()

    print(f"Playing continuously in batches of {n} games for each pair of {len(players)} players - Ctrl+C to stop.")
    while playing:
        try:
            stats += round_robin(players, n, point_types)
            games_each += n * (len(players) - 1)
            showstats(stats, player_names, games_each, point_types)
            print("")
        except KeyboardInterrupt:
            playing = False
            print("")

if __name__ == "__main__":
    main()
