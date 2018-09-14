#!/usr/bin/env python

"""This is the example module.

This module does stuff.
"""


import pytest
from podspy.petrinet.elements import *
from podspy.petrinet.elements import PetrinetEdge


def test_make_petrinet_node():
    # using a subclass of the abstract petrinet node class to test it
    graph = None
    label = 'a'
    node = Transition(graph, label)
    assert node._id is not None
    assert node.local_id is not None
    assert hash(node) is not None


def test_make_edge():
    # using subclasses of the abstract petrinet edge class to test it
    graph = None
    src = Transition(graph, 'a')
    target = Place(graph, 'b')
    label = 'a to b'
    weight = 1
    edge = Arc(src, target, weight, label)
    assert isinstance(edge, Arc)


def test_edge_equality():
    # using subclasses of the abstract petrinet edge class to test it

    # same source and target and graph
    graph, activity_label, place_label = 'graph', 'a', 'p0'
    n1 = Transition(graph, activity_label)
    n2 = Place(graph, place_label)
    n3 = Place(graph, place_label)
    assert n2 != n3

    # case 1: different source and target mean different edges
    edge_label = '{} -> {}'.format(activity_label, place_label)
    weight = 1
    e1 = Arc(n1, n2, weight)
    e2 = Arc(n1, n3, weight)
    assert e1 != e2

    # case 2: changing the _id of n2 makes the two edges equal
    n3._id = n2._id
    assert e1 == e2

    # case 3: different graphs mean different edges
    graph1 = 'graph1'
    n4 = Transition(graph1, activity_label)
    n5 = Place(graph1, place_label)
    n4._id = n1._id
    n5._id = n2._id
    e3 = Arc(n4, n5, weight)
    assert e1 != e3


class TestPetrinetEdge:
    class MockPetrinetEdge(PetrinetEdge):
        def __init__(self, src, target, label, *args, **kwargs):
            super().__init__(src, target, label, *args, **kwargs)

    def test_hash_function(self):
        graph, activity_label, place_label = 'graph', 'a', 'p0'
        edge_label = '{}->{}'.format(activity_label, place_label)

        t0 = Transition(graph, activity_label)
        p0 = Place(graph, place_label)

        e0 = TestPetrinetEdge.MockPetrinetEdge(t0, p0, edge_label)

        expected = hash((t0, p0))

        assert hash(e0) == expected

