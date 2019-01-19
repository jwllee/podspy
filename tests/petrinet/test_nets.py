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

import pytest
import functools as fct


class TestPetrinet:
    @pytest.fixture(
        scope='function'
    )
    def net_t4_p3_a8(self):
        net = PetrinetFactory.new_petrinet('net0')

        t_a = net.add_transition('a')
        t_b = net.add_transition('b')
        t_c = net.add_transition('c')
        t_d = net.add_transition('d')
        trans = [t_a, t_b, t_c, t_d]

        p_1 = net.add_place('p1')
        p_2 = net.add_place('p2')
        p_3 = net.add_place('p3')
        places = [p_1, p_2, p_3]

        arcs = [
            net.add_arc(p_1, t_a),
            net.add_arc(p_1, t_b),
            net.add_arc(p_2, t_c),
            net.add_arc(p_2, t_d),
            net.add_arc(t_a, p_2),
            net.add_arc(t_b, p_2),
            net.add_arc(t_c, p_3),
            net.add_arc(t_d, p_3)
        ]

        return net, trans, places, arcs

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

        expected_p_to_t_df = pd.DataFrame(mat.copy(), columns=sorted_trans_labels,
                                          index=sorted_place_labels, dtype=np.int)
        expected_p_to_t_df.loc['p1', 'a'] = 1
        expected_p_to_t_df.loc['p2', 'b'] = 1
        expected_p_to_t_df.loc['p3', 'c'] = 1
        expected_p_to_t_df.loc['p4', 'd'] = 1
        expected_p_to_t_df.loc['p5', 'd'] = 1

        mat = np.zeros((4, 6))
        expected_t_to_p_df = pd.DataFrame(mat, columns=sorted_place_labels,
                                          index=sorted_trans_labels, dtype=np.int)
        expected_t_to_p_df.loc['a', 'p2'] = 1
        expected_t_to_p_df.loc['a', 'p3'] = 1
        expected_t_to_p_df.loc['b', 'p4'] = 1
        expected_t_to_p_df.loc['c', 'p5'] = 1
        expected_t_to_p_df.loc['d', 'p6'] = 1

        p_to_t_df, t_to_p_df = net.get_transition_relation_dfs()

        assert_frame_equal(p_to_t_df, expected_p_to_t_df)
        assert_frame_equal(t_to_p_df, expected_t_to_p_df)

    def test_add_transition(self):
        net = PetrinetFactory.new_petrinet('net0')
        t_a = net.add_transition('a')
        assert t_a is not None
        assert t_a.label == 'a'

    def test_add_place(self):
        net = PetrinetFactory.new_petrinet('net0')
        p_1 = net.add_place('p1')
        assert p_1 is not None
        assert p_1.label == 'p1'

    def test_add_arc(self):
        net = PetrinetFactory.new_petrinet('net0')
        t_a = net.add_transition('a')
        p_1 = net.add_place('p1')
        arc = net.add_arc(p_1, t_a)
        assert arc is not None
        assert arc.src == p_1 and arc.target == t_a

    def test_get_edges_from_all_nodes(self, net_t4_p3_a8):
        net, trans, places, arcs = net_t4_p3_a8
        edges = net.get_edges()
        for arc in arcs:
            assert arc in edges

    def test_get_edges_from_some_nodes(self, net_t4_p3_a8):
        net, trans, places, arcs = net_t4_p3_a8
        first_2_trans = trans[:2]
        expected = list(filter(lambda arc: arc.src in first_2_trans or arc.target in first_2_trans, arcs))
        edges = net.get_edges(first_2_trans)
        expected_str = fct.reduce(lambda x, e: x + ['({}, {})'.format(e.src.label, e.target.label)], expected, [])
        edges_str = fct.reduce(lambda x, e: x + ['({},{})'.format(e.src.label, e.target.label)], edges, [])

        for arc in expected:
            assert arc in edges, '({},{}) not in {}'.format(arc.src.label, arc.target.label, edges_str)
        for edge in edges:
            assert edge in expected, '({},{}) not in {}'.format(edge.src.label, edge.target.label, expected_str)

class TestAcceptingPetrinet:
    def test_iterable(self):
        pn = PetrinetFactory.new_petrinet('net_0')
        apn = PetrinetFactory.new_accepting_petrinet(pn)
        pn, init, final = apn

        assert isinstance(pn, nt.Petrinet)
        assert isinstance(init, smc.Marking)
        assert isinstance(final, set)
        assert len(final) == 1