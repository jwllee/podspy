#!/usr/bin/env python

"""This is the unit test module for the alpha discovery module.

"""


import pytest, os, sys
import pandas as pd
import numpy as np

from podspy.discovery import alpha
from podspy.structure import CausalMatrix
from podspy.petrinet.nets import *
from podspy.petrinet import visualize as vis


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


class TestFootprintMatrix:
    def test_build_from_causal_matrix(self, simple_causal_matrix):
        print(simple_causal_matrix)

        footprint = alpha.FootprintMatrix.build_from_causal_matrix(simple_causal_matrix)

        assert isinstance(footprint, alpha.FootprintMatrix)

        # expected footprint matrix
        # [
        #     (#, #, ->, #, #)
        #     (#, #, ->, #, #)
        #     (<-, <-, #, ->, ->)
        #     (#, #, <-, #, #)
        #     (#, #, <-, #, #)
        # ]

        w = alpha.FootprintMatrix.NEVER_FOLLOW
        x = alpha.FootprintMatrix.DIRECT_RIGHT
        y = alpha.FootprintMatrix.DIRECT_LEFT
        z = alpha.FootprintMatrix.PARALLEL

        expected = [
            (w, w, x, w, w),
            (w, w, x, w, w),
            (y, y, w, x, x),
            (w, w, y, w, w),
            (w, w, y, w, w)
        ]

        assert (footprint.matrix.values == expected).all()


class TestAlphaMiner:
    def test_alpha_simple_causal_matrix(self, simple_causal_matrix):
        net = alpha.discover(simple_causal_matrix)

        assert isinstance(net, AcceptingPetrinet)

        net_fp = os.path.join('.', 'tests', 'alpha.png')
        G = vis.net2dot(net.net)
        # G.draw(net_fp)
