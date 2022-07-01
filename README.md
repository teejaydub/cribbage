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
    Max               7124   40.2%
    Helen             5513   31.1%
    Simon             5063   28.6%
```

Plans
=====

* Add some more heuristics to express my own intuitions and some from other sources.

* Rework Helen to parameterize all integer constants within the heuristics.

* Train Helen continuously, choosing random values for heuristic parameters and keeping
  the changes that result in better rankings over many games.  See if that improves her ranking.

* Work on determining which heuristics are most powerful/helpful.

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
