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
Max              77540   59.0%
Helen            67021   51.0%
Simon            52539   40.0%
```

Plans
=====

* Train Helen continuously, choosing random values for heuristic parameters
  and keeping the changes that result in better rankings over many games. See
  if that improves her ranking.
  * Game-centered heuristics
    * Report statistics for point values
      * Analyze point counts
        * How can they all be the same if Max wins so much more?
      * Predict winner by average point values
      * Decide when to play in "risky" or "safe" mode
        * Risky = hoping for max possible points, make the choices with best possible outcomes
        * Safe = make the choices with best expected values
      * Decide when to play in "slow" or "fast" mode
        * When you expect that net point changes will be even, prefer larger or smaller movements, to get in sync with a winning position.
  * Add God player, who does full lookahead on each round with knowledge of all cards
    * Can play for min/max, where you assume perfect play in your opponent
    * Or if you predict a loss otherwise, go for the most points if your opponent chooses poorly
  * Keep track of the number of references to a given parameter?  Some may be beneficial, but only in rare circumstances.
    * P6: use 0, or 2?
    * P5 as well.
    * Could tell "compare" to focus on a given parameter, and include only games where that parameter has been used.
  * Compute correlation of weight with games won, maybe piecewise.
  * Add parameters for all the heuristic scores, even the ones from authorities.
  * Parallelize this, so it can run over multiple processors at once.

* Work on determining which heuristics are most powerful/helpful.  Similar
  process, but pick a set of parameters to clear to 0.

* Explore the full decision tree for pegging?  It's not very large, and we're exploring much of it anyway with Max.

* Start including ideas of conservative vs. risky play - max possible vs. expected value or least-worst.

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
