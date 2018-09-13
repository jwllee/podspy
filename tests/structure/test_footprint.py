#!/usr/bin/env python

"""This is the unit test module for the footprint module.

"""


import numpy as np
from podspy.structure import FootprintMatrix, CausalMatrix


# some renaming for convenience
n = FootprintMatrix.NEVER_FOLLOW
r = FootprintMatrix.CAUSAL_RIGHT
l = FootprintMatrix.CAUSAL_LEFT
p = FootprintMatrix.PARALLEL


class TestFootprintMatrix:
    def test_build_from_causal_matrix(self, simple_causal_matrix):
        print(simple_causal_matrix)

        footprint = FootprintMatrix.build_from_causal_matrix(simple_causal_matrix)

        assert isinstance(footprint, FootprintMatrix)

        # expected footprint matrix
        # [
        #     (#, #, ->, #, #)
        #     (#, #, ->, #, #)
        #     (<-, <-, #, ->, ->)
        #     (#, #, <-, #, #)
        #     (#, #, <-, #, #)
        # ]

        expected = [
            (n, n, r, n, n),
            (n, n, r, n, n),
            (l, l, n, r, r),
            (n, n, l, n, n),
            (n, n, l, n, n)
        ]
        expected = np.asarray(expected)

        assert (footprint.matrix.values == expected).all()

    def test_build_one_loop_log_table(self, one_loop_log_table):
        cmat = CausalMatrix.build_from_logtable(one_loop_log_table)
        footprint = FootprintMatrix.build_from_causal_matrix(cmat)

        assert isinstance(footprint, FootprintMatrix)

        # expected footprint matrix
        # [
        #   (||, <, >),     # a row
        #   (>,  #, #),     # x row
        #   (<,  #, #)      # y row
        # ]

        expected = [
            (p, l, r),
            (r, n, n),
            (l, n, n)
        ]
        expected = np.asarray(expected)

        assert (footprint.matrix.values == expected).all()

    def test_build_two_loop_log_table(self, two_loop_log_table):
        cmat = CausalMatrix.build_from_logtable(two_loop_log_table)
        footprint = FootprintMatrix.build_from_causal_matrix(cmat)

        assert isinstance(footprint, FootprintMatrix)

        # expected footprint matrix
        # [
        #   (#, ||, <, >),  # a row
        #   (||, #, #, >),  # b row
        #   (>,  #, #, #),  # x row
        #   (<,  <, #, #)   # y row
        # ]

        expected = [
            (n, p, l, r),
            (p, n, n, r),
            (r, n, n, n),
            (l, l, n, n)
        ]
        expected = np.asarray(expected)

        assert (footprint.matrix.values == expected).all()
