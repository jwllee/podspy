#!/usr/bin/env python

"""This is the unit test module for the causal matrix module.

"""


import pandas as pd
import numpy as np

from podspy.structure import CausalMatrix


class TestCausalMatrix:
    def test_build_from_logtable(self, simple_log_table):
        # sort activities
        cmat = CausalMatrix.build_from_logtable(simple_log_table, sort=True)

        assert isinstance(cmat, CausalMatrix)

        assert cmat.activity_list == ['a', 'b', 'c', 'd', 'e']

        # expected causal matrix
        # 45 <a, c, d>
        # 42 <b, c, d>
        # 38 <a, c, e>
        # 22 <b, c, e>

        mat = [
            (0, 0, 83, 0, 0),  # a row
            (0, 0, 64, 0, 0),  # b row
            (0, 0, 0, 87, 60), # c row
            (0, 0, 0, 0, 0),   # d row
            (0, 0, 0, 0, 0)    # e row
        ]
        mat = np.array(mat)

        assert isinstance(cmat.matrix, pd.DataFrame)
        assert (cmat.matrix.values == mat).all()

    def test_build_from_logtable_one_loop(self, one_loop_log_table):
        cmat = CausalMatrix.build_from_logtable(one_loop_log_table, sort=True)

        assert isinstance(cmat, CausalMatrix)

        assert cmat.activity_list == ['a', 'x', 'y']

        # expected causal matrix
        # 45 <x, a, y>
        # 42 <x, a, a, y>
        # 38 <x, a, a, a, y>

        mat = [
            (118, 0, 125),   # a row
            (125, 0, 0),     # x row
            (0, 0, 0)        # y row
        ]
        mat = np.array(mat)

        assert isinstance(cmat.matrix, pd.DataFrame)
        assert (cmat.matrix.values == mat).all()

    def test_build_from_logtable_two_loop(self, two_loop_log_table):
        cmat = CausalMatrix.build_from_logtable(two_loop_log_table, sort=True)

        assert isinstance(cmat, CausalMatrix)

        assert cmat.activity_list == ['a', 'b', 'x', 'y']

        # expected causal matrix
        # 45 <x, a, y>
        # 42 <x, a, b, y>
        # 38 <x, a, b, a, y>
        # 22 <x, a, b, a, b, y>

        mat = [
            (0, 124, 0, 83), # a row
            (60, 0, 0, 64),  # b row
            (147, 0, 0, 0),  # x row
            (0, 0, 0, 0)     # y row
        ]
        mat = np.array(mat)

        assert isinstance(cmat.matrix, pd.DataFrame)
        assert (cmat.matrix.values == mat).all()
