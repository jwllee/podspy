#!/usr/bin/env python

"""This is the unit test module for the alpha discovery module.

"""


import pytest, os
import pandas as pd
import numpy as np

from podspy.discovery import alpha
from podspy.petrinet.nets import *
from podspy.petrinet import visualize as vis
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


class TestAlphaMiner:
    def test_alpha_simple_causal_matrix(self, simple_causal_matrix):
        net = alpha.discover(simple_causal_matrix)

        assert isinstance(net, AcceptingPetrinet)

        net_fp = os.path.join('.', 'tests', 'alpha.png')
        G = vis.net2dot(net.net)
        # G.draw(net_fp)
