#!/usr/bin/env python

"""This is the unit test module.

This module tests petri net classes.
"""


from podspy.petrinet.factory import *
from podspy.petrinet import semantics as smc
from podspy.petrinet import nets as nt

import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal


class TestPetrinet:
    def test_get_transition_relation_dfs(self):
        # make net
        net_label = 'net0'
        net = PetrinetFactory.new_petrinet(net_label)

        t_a = net.add_transition('a')
        t_b = net.add_transition('b')
        t_c = net.add_transition('c')
        t_d = net.add_transition('d')

        trans = [t_a, t_b, t_c, t_d]

        p_1 = net.add_place('p1')
        p_2 = net.add_place('p2')
        p_3 = net.add_place('p3')
        p_4 = net.add_place('p4')
        p_5 = net.add_place('p5')
        p_6 = net.add_place('p6')

        places = [p_1, p_2, p_3, p_4, p_5, p_6]

        e_1 = net.add_arc(t_a, p_2, 1)
        e_2 = net.add_arc(t_a, p_3, 1)
        e_3 = net.add_arc(t_b, p_4, 1)
        e_4 = net.add_arc(t_c, p_5, 1)
        e_5 = net.add_arc(t_d, p_6, 1)

        e_6 = net.add_arc(p_1, t_a, 1)
        e_7 = net.add_arc(p_2, t_b, 1)
        e_8 = net.add_arc(p_3, t_c, 1)
        e_9 = net.add_arc(p_4, t_d, 1)
        e_10 = net.add_arc(p_5, t_d, 1)

        mat = np.zeros((6, 4))
        sorted_trans = sorted(trans, key=lambda t: t.label)
        sorted_trans_labels = list(map(lambda t: t.label, sorted_trans))
        sorted_places = sorted(places, key=lambda p: p.label)
        sorted_place_labels = list(map(lambda p: p.label, sorted_places))

        expected_p_to_t_df = pd.DataFrame(mat.copy(), columns=sorted_trans_labels, index=sorted_place_labels)
        expected_p_to_t_df.loc['p1', 'a'] = 1
        expected_p_to_t_df.loc['p2', 'b'] = 1
        expected_p_to_t_df.loc['p3', 'c'] = 1
        expected_p_to_t_df.loc['p4', 'd'] = 1
        expected_p_to_t_df.loc['p5', 'd'] = 1

        expected_t_to_p_df = pd.DataFrame(mat.copy(), columns=sorted_trans_labels, index=sorted_place_labels)
        expected_t_to_p_df.loc['p2', 'a'] = 1
        expected_t_to_p_df.loc['p3', 'a'] = 1
        expected_t_to_p_df.loc['p4', 'b'] = 1
        expected_t_to_p_df.loc['p5', 'c'] = 1
        expected_t_to_p_df.loc['p6', 'd'] = 1

        p_to_t_df, t_to_p_df = net.get_transition_relation_dfs()

        assert_frame_equal(p_to_t_df, expected_p_to_t_df)
        assert_frame_equal(t_to_p_df, expected_t_to_p_df)


class TestAcceptingPetrinet:
    def test_iterable(self):
        pn = PetrinetFactory.new_petrinet('net_0')
        apn = PetrinetFactory.new_accepting_petrinet(pn)
        pn, init, final = apn

        assert isinstance(pn, nt.Petrinet)
        assert isinstance(init, smc.Marking)
        assert isinstance(final, set)
        assert len(final) == 1