#!/usr/bin/env python

"""This is the unit test module.

This module tests classes in directed graph module.
"""


from podspy.graph.directed import AbstractDirectedGraphEdge
from podspy.petrinet.elements import *


class TestAbstractDirectedGraphEdge:
    class MockAbstractDirectedGraphEdge(AbstractDirectedGraphEdge):
        def __init__(self, src, target, *args, **kwargs):
            super().__init__(src, target, *args, **kwargs)

    def test_hash_function(self):
        graph, activity_label, place_label = 'graph', 'a', 'p0'
        edge_label = '{}->{}'.format(activity_label, place_label)

        t0 = Transition(graph, activity_label)
        p0 = Place(graph, place_label)

        e0 = TestAbstractDirectedGraphEdge.MockAbstractDirectedGraphEdge(t0, p0, edge_label)

        expected = hash((t0, p0))

        assert hash(e0) == expected
