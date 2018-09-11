#!/usr/bin/env python

"""This is the conf test module.

"""

__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


import pytest
import pandas as pd
import numpy as np

from podspy.structure import CausalMatrix


@pytest.fixture()
def simple_causal_matrix():
    # causal matrix
    mat = [
        (0, 0, 83, 0, 0),   # a row
        (0, 0, 64, 0, 0),   # b row
        (0, 0, 0, 87, 60),  # c row
        (0, 0, 0, 0, 0),    # d row
        (0, 0, 0, 0, 0)
    ]

    mat = np.array(mat)
    activity_list = ['a', 'b', 'c', 'd', 'e']
    df = pd.DataFrame(mat, index=activity_list, columns=activity_list)
    cmat = CausalMatrix(activity_list, df)

    return cmat
