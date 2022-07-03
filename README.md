Cribbage
========

Python library for experimenting with the game of cribbage.

I've forked this heavily from https://github.com/wroberts/cribbage.
Thanks very much, Will - your framework made it easy to get started.

Will was interested in training a good computer cribbage player; I'm more
interested in learning what heuristics are best that are learnable by a human.

To that end, I'm developing some `CribbagePlayer` classes here so I can compare their
rankings when they play against each other.  Currently, they include:

- `MaxerCribbagePlayer`, aka **Max**: Uses any convenient techniques, like exhaustive
  lookahead and tables of expected values, that are easy to do in software.

- `HeuristicCribbagePlayer`, aka **Helen**: Uses techniques that I think I could
  reasonably learn and remember - mostly simple rules that are expressed in integer point values.

- `SimpleCribbagePlayer`, aka **Simon**: Will's implementation, for a straw man baseline.

Currently, Max is the best player, but Helen is better than Simon.  Stats:

```
    Player       Games won  Percent
    Max               3503   40.3%
    Helen             2769   31.8%
    Simon             2428   27.9%
```

Plans
=====

* Train Helen continuously, choosing random values for heuristic parameters
  and keeping the changes that result in better rankings over many games. See
  if that improves her ranking.
  * Optimize each parameter individually, with binary search.
  * Instead of a fixed number of games, shoot for a fixed number of usages of that parameter.
  * Add CSV output so we can graph the progress over time.  (Or just show graphs, I guess)
  * Switch to a genetic algorithm, that does round-robin for more players at
    once, then replaces the n-2 worst ones with a genetic combination of the
    2 best ones + 1 small mutation.
  * Add parameters for all the heuristic scores, even the ones from authorities.
  * Parallelize this, so it can run over multiple processors at once.

* Work on determining which heuristics are most powerful/helpful.  Similar
  process, but pick a set of parameters to clear to 0.

* Group the heuristics by degree of power, and make players Anna, Ben, and Clara, where
  Anna starts with a heuristic set from Helen that's easy to remember, and then each
  adds some more.

Getting started
===============

`pipenv install` will set up the environment.

`pipenv shell` will activate the environment.

`pipenv run optimize` will compile Will's C function for scoring hands, to improve speed.

`pipenv run compare` will start an endless tournament to rank the available players.

Links
=====

- https://github.com/wroberts/cribbage
- http://www.cribbageforum.com/index.html
