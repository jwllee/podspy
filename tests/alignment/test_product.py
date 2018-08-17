#!/usr/bin/env python

"""This is the unit test module for product module in alignment package.

This module contains unit tests for the module.
"""
import pytest, logging
import pandas as pd
import numpy as np

from podspy.petrinet import nets as nts
from podspy.petrinet import factory as fty
from podspy.petrinet import elements as ems
from podspy.petrinet import semantics as smc
from podspy.alignment import product as pdt
from podspy.petrinet import visualize as vis


logger = logging.getLogger(__file__)


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


@pytest.fixture(params=[
    ['a', 'b', 'c'],
    # ['a', 'a', 'b', 'c'] does not work with duplicated event labels due to lack of mapping
])
def trace(request):
    return request.param


class TestSyncNetProduct:
    def test_product(self):
        # make net
        net0 = fty.PetrinetFactory.new_petrinet('net0')

        # places
        p_init = net0.add_place('init')
        p1 = net0.add_place('p1')
        p2 = net0.add_place('p2')
        p3 = net0.add_place('p3')
        p4 = net0.add_place('p4')
        p5 = net0.add_place('p5')
        p_out = net0.add_place('out')

        # transitions
        trans_a = net0.add_transition('a')
        trans_b = net0.add_transition('b')
        trans_c = net0.add_transition('c')
        trans_d = net0.add_transition('d')
        trans_e = net0.add_transition('e')
        # trans_f = net0.add_transition('f')
        trans_g = net0.add_transition('g')
        trans_h = net0.add_transition('h')

        # arcs
        # place to transition
        net0.add_arc(p_init, trans_a)
        net0.add_arc(p1, trans_b)
        net0.add_arc(p1, trans_c)
        net0.add_arc(p3, trans_e)
        net0.add_arc(p2, trans_d)
        net0.add_arc(p4, trans_e)
        # net0.add_arc(p5, trans_f)
        net0.add_arc(p5, trans_g)
        net0.add_arc(p5, trans_h)

        # transition to place
        net0.add_arc(trans_a, p1)
        net0.add_arc(trans_a, p2)
        net0.add_arc(trans_b, p3)
        net0.add_arc(trans_c, p3)
        net0.add_arc(trans_d, p4)
        net0.add_arc(trans_e, p5)
        # net0.add_arc(trans_f, p1)
        # net0.add_arc(trans_f, p2)
        net0.add_arc(trans_g, p_out)
        net0.add_arc(trans_h, p_out)

        # initial marking
        init = smc.Marking([p_init])
        finals = {smc.Marking([p_out])}
        apn = fty.PetrinetFactory.new_accepting_petrinet(net0, init, finals)

        # output the net
        G = vis.net2dot(net0, marking=init)
        G.draw('./example.png')

        # fitting trace
        trace_0 = ['a', 'c', 'd', 'e', 'g', 'h']

        # looped trace
        trace_1 = ['a', 'c', 'd', 'e', 'f', 'b', 'd', 'e', 'g', 'h']


        # output the snp
        # trace 0
        snp_0 = pdt.SyncNetProductFactory.new_snp(trace_0, apn)
        G = vis.net2dot(snp_0.snp.net, snp_0.snp.init_marking, layout='dot')
        G.draw('./example-snp.png')

        # trace 1
        snp_1 = pdt.SyncNetProductFactory.new_snp(trace_1, apn)
        G = vis.net2dot(snp_1.snp.net, snp_1.snp.init_marking, layout='dot')
        G.draw('./example-snp-1.png')
