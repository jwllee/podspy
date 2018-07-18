#!/usr/bin/env python

"""This is the unit test module.

This module tests classes in the base module.
"""


from podspy.graph.base import AbstractGraphEdge, AbstractGraph


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


class MockAbstractGraphEdge(AbstractGraphEdge):
    def __init__(self, src, target, *args, **kwargs):
        super().__init__(src, target, *args, **kwargs)


class TestAbstractGraphEdge:
    def test_edge_equality(self):
        e0 = MockAbstractGraphEdge('a', 'b')
        e1 = MockAbstractGraphEdge('a', 'b')

        assert e0 == e1

        e2 = MockAbstractGraphEdge('a', 'c')

        assert e0 != e2

    def test_hash(self):
        e0 = MockAbstractGraphEdge('a', 'b')
        expected = 'a'.__hash__() + 37 * 'b'.__hash__()

        assert expected == e0.__hash__()
