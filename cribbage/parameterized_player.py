import random

import numpy as np

from heuristicplayer import HeuristicCribbagePlayer

class ParameterizedHeuristicCribbagePlayer(HeuristicCribbagePlayer):
    '''
    A heuristic player where individual heuristics have weighted parameters,
    allowing it to be trained for optimal values of those weights.

    Weights are used by multiplying them with existing heuristic values.

    A set of weights can be chosen at random.  Random weights range from -1 to
    2 * the nominal parammeter value, reflecting the usual levels of
    uncertainty in heuristics - they might actually be harmful, they might be
    better than you intuit, and they might have no real value whatsoever.

    An instance can be converted to and from a short(-ish) string, encoding
    the weight values.

    Weights can be integral or floating point.  The main advantage of integral
    weights is that they can be easy for a human to implement.
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
            # Don't need weights if we're just restoring existing parameters.
            self.parameters = [int(p) for p in parameters.split('/')]
        else:
            # Weight parameters by 1.
            self.weights = [1 for i in range(self.NUM_PARAMS)]
            # The parameters, scaled to the nominal range.  None until first seen.
            self.parameters = [None for i in range(self.NUM_PARAMS)]

    def __str__(self):
        if self.parameters[0]:
            return '/'.join([str(p) for p in self.parameters])
        else:
            return '|'.join([str(w) for w in self.weights])

    def randomize_weights(self):
        ''' Sets weights randomly. '''
        self.weights = [np.clip(random.gauss(mu=1, sigma=1), -1, 2)
            for i in range(self.NUM_PARAMS)]
        self.parameters = [None for i in range(self.NUM_PARAMS)]

    def IP(self, index: int, nominal: int) -> int:
        '''
        Return the nominal value for an integer parameter, modified by its current weight.

        An integral value is returned, within the range [-1..2] * nominal.

        The nominal value for this parameter index should be the same on every call.

        Arguments:
        - `index` - A unique ID for this parameter.  Weights will be consistent for this ID.
        - `nominal` - The nominal value for this parameter.
        '''
        result = self.parameters[index]
        if result is None:
            # First call.  Scale it to the nominal value.
            result = self.weights[index] * nominal
            result = round(result)
            self.parameters[index] = result
        return result

    def FP(self, index: int, nominal: float) -> float:
        '''
        Return the nominal value for a floating-point parameter, modified by its current weight.

        A floating-point value is returned, within the range [-1..2] * nominal.

        The nominal value for this parameter index should be the same on every call.

        Arguments:
        - `index` - A unique ID for this parameter.  Weights will be consistent for this ID.
        - `nominal` - The nominal value for this parameter.
        '''
        result = self.parameters[index]
        if result is None:
            # First call.  Scale it to the nominal value.
            result = self.weights * nominal
            self.parameters[index] = result
        return result