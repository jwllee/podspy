#!/usr/bin/env python

"""This is the unit test module for product module in alignment package.

This module contains unit tests for the module.
"""
import pytest
import pandas as pd
import numpy as np

from podspy.petrinet import nets as nts
from podspy.petrinet import factory as fty
from podspy.petrinet import elements as ems
from podspy.petrinet import semantics as smc
from podspy.alignment import product as pdt


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


@pytest.fixture(params=[
    ['a', 'b', 'c'],
    ['a', 'a', 'b', 'c']
])
def trace(request):
    return request.param


class TestSyncNetProduct:
    def test_trace2apn(self, trace):
        net = fty.PetrinetFactory.new_petrinet('net0')
        snp = pdt.SyncNetProduct(trace, net)

        trace_apn = snp.trace2apn(trace)

        assert isinstance(trace_apn, nts.AcceptingPetrinet)
        pn, init, final = trace_apn

        assert isinstance(pn, nts.Petrinet)
        assert isinstance(init, smc.Marking)

        # check trace events are in transitions
        trans_map = {t.label:t for t in pn.transitions}

        for event in trace:
            assert event in trans_map

        # check that there is an arc going from p0 -> t -> p1
        for i in range(len(trace)):
            event_i = trace[i]
            trans_i = trans_map[event_i]

            in_edges = pn.in_edge_map[trans_i]
            out_edges = pn.out_edge_map[trans_i]

            assert len(in_edges) == 1
            assert len(out_edges) == 1

            in_edge = in_edges.pop()
            out_edge = out_edges.pop()

            assert isinstance(in_edge.src, ems.Place)
            assert isinstance(out_edge.target, ems.Place)

            if i == 0:
                assert init.occurrences(in_edge.src) == 1

            if i == (len(trace) - 1):
                assert final.pop().occurrences(out_edge.target) == 1

