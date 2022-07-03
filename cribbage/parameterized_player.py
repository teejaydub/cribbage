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
    '''

    # Override in derived classes to set the number of parameters.
    NUM_PARAMS = 1

    def __init__(self, parameters=None):
        ''' Initializes with the specified parameter string.
            If parameters are not supplied, weight all parameters normally - by 1.
        '''
        # Floats for the weights used.
        super().__init__()
        # Weight parameters by 1.
        self.weights = [1 for i in range(self.NUM_PARAMS)]
        if parameters:
            # Just restore existing parameters.
            self.parameters = [float(p) for p in parameters.split('/')]
        else:
            # The parameters, scaled to the nominal range.  None until first seen.
            self.parameters = [None for i in range(self.NUM_PARAMS)]

    def __str__(self):
        if self.parameters[0]:
            return '/'.join([f"{p:0.2f}" for p in self.parameters if p is not None])
        else:
            return '|'.join([f"{p:0.2f}" for w in self.weights])

    def random_weight(self):
        return np.clip(random.gauss(mu=1, sigma=1), -1, 2)

    def randomize_weights(self):
        ''' Set all weights randomly. '''
        self.weights = [self.random_weight() for i in range(self.NUM_PARAMS)]
        self.parameters = [None for i in range(self.NUM_PARAMS)]

    def randomize_one_weight(self):
        ''' Set one weight randomly. '''
        i = random.choice(range(self.NUM_PARAMS))
        self.weights[i] = self.random_weight()
        self.parameters[i] = None

    def P(self, index: int, nominal: float) -> float:
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
            result = self.weights[index] * nominal
            self.parameters[index] = result
            print(f"new parameter @{index} = {result:.2f} from weight {self.weights[index]:.2f} and nominal {nominal}")
        return result