#!/usr/bin/env python

"""This is the unit test module for the causal matrix module.

"""


import pytest
import functools as fcts
import itertools as itrs
import pandas as pd
import numpy as np

from podspy.structure import CausalMatrix
from podspy.log import constants as cnst
from podspy.log import factory as fty
from podspy.log import table as tb


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
