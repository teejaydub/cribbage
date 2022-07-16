import unittest

from cribbage.learnable_player import run_lengths, pair_values_in_hand, values_to_steps, runs_in_hand

class TestLearnablePlayer(unittest.TestCase):

    def test_steps(self):
        self.assertEqual(values_to_steps([1, 2, 3, 4]), [1, 1, 1])
        self.assertEqual(values_to_steps([1, 1, 1, 1]), [0, 0, 0])
        self.assertEqual(values_to_steps([1, 2, 4, 4]), [1, 2, 0])

    def test_runs(self):
        self.assertEqual(run_lengths(1, []), [])
        self.assertEqual(run_lengths(1, [1]), [1])
        self.assertEqual(run_lengths(1, [0]), [])
        self.assertEqual(run_lengths(1, [0, 0]), [])
        self.assertEqual(run_lengths(1, [1, 0]), [1])
        self.assertEqual(run_lengths(1, [0, 1]), [1])
        self.assertEqual(run_lengths(1, [1, 1]), [2])
        self.assertEqual(run_lengths(1, [1, 1, 0]), [2])
        self.assertEqual(run_lengths(1, [0, 1, 1]), [2])
        self.assertEqual(run_lengths(1, [1, 1, 1]), [3])
        self.assertEqual(run_lengths(1, [1, 2, 1]), [1, 1])

    def test_pairs_in_hand(self):
        self.assertEqual(pair_values_in_hand(values_to_steps([1, 2, 3, 4])), 0)
        self.assertEqual(pair_values_in_hand(values_to_steps([1, 1, 3, 4])), 1)
        self.assertEqual(pair_values_in_hand(values_to_steps([1, 2, 3, 3])), 1)
        self.assertEqual(pair_values_in_hand(values_to_steps([1, 3, 3, 3])), 0)
        self.assertEqual(pair_values_in_hand(values_to_steps([1, 1, 3, 3])), 2)

    def test_runs_in_hand(self):
        self.assertEqual(runs_in_hand(values_to_steps([1, 1, 3, 4])), 0)
        self.assertEqual(runs_in_hand(values_to_steps([1, 2, 3, 3])), 1)
        self.assertEqual(runs_in_hand(values_to_steps([1, 3, 3, 3])), 0)
        self.assertEqual(runs_in_hand(values_to_steps([1, 2, 3, 4])), 1)
        self.assertEqual(runs_in_hand(values_to_steps([1, 2, 4, 5])), 0)


if __name__ == '__main__':
    unittest.main()