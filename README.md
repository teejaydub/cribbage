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

- `SimpleCribbagePlayer`, aka **Simon**: Will's implementation in its simplest mode, for a straw man baseline.

Currently, Max is the best player, but Helen is better than Simon.  Typical stats (from `pipenv run compare`):

```
Player       Games won  Percent  Averages for Dealer and Pone                                     Hand counts
Max              17485   59.1%   D crib: 5.0  D hand: 8.0  D play: 3.6  P hand: 8.1  P play: 2.2  4.2+4.4=8.6
Helen            15114   51.1%   D crib: 4.6  D hand: 8.0  D play: 3.6  P hand: 8.0  P play: 2.2  4.2+4.4=8.6
Simon            11801   39.9%   D crib: 4.1  D hand: 8.2  D play: 3.5  P hand: 8.2  P play: 2.0  4.1+4.4=8.5
```
and with just Max and Helen:
```

Player       Games won  Percent  Averages for Dealer and Pone                                     Hand counts
Max              10101   54.9%   D crib: 4.9  D hand: 8.0  D play: 3.5  P hand: 8.1  P play: 2.1  4.3+4.4=8.7
Helen             8299   45.1%   D crib: 4.4  D hand: 8.0  D play: 3.5  P hand: 8.0  P play: 2.0  4.2+4.5=8.7
```


Plans
=====

* Game-centered heuristics
  * Report statistics for point values
    * Predict winner by average point values
      * Use standardized stats
      * Note the score at the beginning of a given phase - when starting a new phase.
      * Starting from where you are, go through the phases in order until reaching the target score.
        * D play and P play simultaneously (if both go over the target, go with the one with higher play value)
          * While playing, use the max of the stat and the points scored so far
        * P hand, D hand, D crib
    * Decide when to play in "risky" or "safe" mode
      * Risky = hoping for max possible points, make the choices with best possible outcomes
      * Safe = make the choices with best expected values
    * Decide when to play in "slow" or "fast" mode
      * When you expect that net point changes will be even, prefer larger or smaller movements, to get in sync with a winning position.

* Improve Max 
  * Explore the full decision tree for pegging?  It's not very large, and we end up exploring much of it anyway.
  * Replace standard point stats with current averages with this player over 100-200 games
* Add God player, who does full lookahead on each round with knowledge of all cards
  * Can play for min/max, where you assume perfect play in your opponent
  * Or if you predict a loss otherwise, go for the most points if your opponent chooses poorly

* Train Helen continuously, choosing random values for heuristic parameters
  and keeping the changes that result in better rankings over many games. See
  if that improves her ranking.
  * Keep track of the number of references to a given parameter?  Some may be beneficial, but only in rare circumstances.
    * P6: use 0, or 2?
    * P5 as well.
    * Could tell "compare" to focus on a given parameter, and include only games where that parameter has been used.
  * Compute correlation of weight with games won, maybe piecewise.
  * Add parameters for all the heuristic scores, even the ones from authorities.
  * Parallelize this, so it can run over multiple processors at once.

* Work on determining which heuristics are most powerful/helpful.  Similar
  process, but pick a set of parameters to clear to 0.

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
