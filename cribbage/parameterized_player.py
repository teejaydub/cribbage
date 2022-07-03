import random

import numpy as np

from heuristicplayer import HeuristicCribbagePlayer

class ParameterizedHeuristicCribbagePlayer(HeuristicCribbagePlayer):
    '''
    A heuristic player where individual heuristics have weighted parameters,
    allowing it to be trained for optimal values of those weights.

    Weights are used by multiplying them with existing heuristic values.
    A normal weight would be 1.0.

    A set of weights can be chosen at random.  Random weights range from -1 to
    2 * the nominal parammeter value, reflecting the usual levels of
    uncertainty in heuristics - they might actually be harmful, they might be
    better than you intuit, and they might have no real value whatsoever.

    An instance can be converted to and from a short(-ish) string, encoding
    the weight values.
    '''

    # Override in derived classes to set the number of parameters.
    NUM_PARAMS = 1

    def __init__(self, parameters=None):
        ''' Initializes with the specified parameter string.
            If parameters are not supplied, weight all parameters normally - by 1.
        '''
        # Floats for the weights used.
        super().__init__()
        if parameters:
            # Just restore existing parameters.
            self.parameters = [float(p) for p in parameters.split(', ')]
        else:
            # All weights are 1.
            self.parameers = [1 for i in range(self.NUM_PARAMS)]

    def __str__(self):
        return ', '.join([f"{p:0.2f}" for p in self.parameters])

    def random_weight(self):
        return np.clip(random.gauss(mu=1, sigma=1), -1, 2)

    def randomize_weights(self):
        ''' Set all weights randomly. '''
        self.parameters = [self.random_weight() for i in range(self.NUM_PARAMS)]

    def randomize_one_weight(self):
        ''' Set one weight randomly. '''
        i = random.choice(range(self.NUM_PARAMS))
        oldweight = self.parameters[i]
        while self.parameters[i] == oldweight:
            self.parameters[i] = self.random_weight()

    def P(self, index: int) -> float:
        '''
        Return the weight for a given floating-point parameter.

        A floating-point value is returned, within the range [-1..2].
        Multiply it by whatever nominal value the heuristic currently has, if it's not 1.

        Arguments:
        - `index` - A unique ID for this parameter.  Weights will be consistent for this ID.
        '''
        return self.parameters[index]
