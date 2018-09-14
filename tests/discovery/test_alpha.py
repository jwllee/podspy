#!/usr/bin/env python

"""This is the unit test module for the alpha discovery module.

"""


import pytest, os
import pandas as pd
import numpy as np

from podspy.discovery import alpha
from podspy.petrinet.nets import *
from podspy.structure import CausalMatrix
from podspy import petrinet


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
        apn = alpha.classic.apply(simple_causal_matrix)

        assert isinstance(apn, AcceptingPetrinet)

        net_fp = os.path.join('.', 'tests', 'alpha.png')
        G = petrinet.to_agraph(apn)
        # G.draw(net_fp, prog='dot')

        net, init_marking, final_markings = apn
        final_marking = final_markings.pop()

        assert isinstance(net, Petrinet)

        assert len(init_marking) == 1, \
            'Initial marking contains {} places'.format(len(init_marking))
        assert len(final_marking) == 1, \
            'Final marking contains {} places'.format(len(final_marking))

        assert len(net.places) == 4
        assert len(net.transitions) == 5

        places = ['i', 'o', '({a, b}, {c})', '({c}, {d, e})']
        trans = ['a', 'b', 'c', 'd', 'e']

        p_to_t_df, t_to_p_df = net.get_transition_relation_dfs()

        p_to_t_df = p_to_t_df.reindex(trans)[places]
        t_to_p_df = t_to_p_df.reindex(trans)[places]

        assert isinstance(p_to_t_df, pd.DataFrame)
        assert isinstance(t_to_p_df, pd.DataFrame)

        assert p_to_t_df.shape == (5, 4)
        assert t_to_p_df.shape == (5, 4)

        expected_p_to_t_vals = np.asarray([
            (1, 0, 0, 0),
            (1, 0, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
            (0, 0, 0, 1)
        ])

        expected_t_to_p_vals = np.asarray([
            (0, 0, 1, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
            (0, 1, 0, 0),
            (0, 1, 0, 0)
        ])

        assert (p_to_t_df.values == expected_p_to_t_vals).all()
        assert (t_to_p_df.values == expected_t_to_p_vals).all()
