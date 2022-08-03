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

Currently, Max is the best player, but Helen is better than Simon.  Typical stats (from `pipenv run compare`):

```
Player       Games won  Percent
Max            2707366   60.5%
Helen          2144663   48.0%
Simon          1855971   41.5%
```

Plans
=====

* Train Helen continuously, choosing random values for heuristic parameters
  and keeping the changes that result in better rankings over many games. See
  if that improves her ranking.
  * Keep track of the number of references to a given parameter?  Some may be beneficial, but only in rare circumstances.
    * P6: use 0, or 2?
    * P5 as well.
    * Could tell "compare" to focus on a given parameter, and include only games where that parameter has been used.
  * Avoid chances for runs
  * P7: Seems clearly better at -1 or 0 than 1.
  * Compute correlation of weight with games won, maybe piecewise.
  * Add parameters for all the heuristic scores, even the ones from authorities.
  * Parallelize this, so it can run over multiple processors at once.

* Work on determining which heuristics are most powerful/helpful.  Similar
  process, but pick a set of parameters to clear to 0.

* Explore the full decision tree for pegging?  It's not very large, and we're exploring much of it anyway with Max.

* Group the heuristics by degree of power, and make players Anna, Ben, and
  Clara, where Anna starts with a heuristic set from Helen that's easy to
  remember, and then each adds some more.

Getting started
===============

`pipenv install` sets up the environment.

`pipenv shell` activates the environment, if you want to run other tools or
use Python interactively.

`pipenv run optimize` compiles Will's C function for scoring hands, to improve
speed.

`pipenv run compare` starts an endless tournament to rank the available players.

`pipenv run train` tries out the heuristics and produces graphs of how weights
relate to games won for each.

`pipenv run test` runs all unit tests.

Links
=====

- https://github.com/wroberts/cribbage
- http://www.cribbageforum.com/index.html
