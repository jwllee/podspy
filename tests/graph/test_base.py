#!/usr/bin/env python

"""This is the unit test module.

This module tests classes in the base module.
"""


from podspy.graph.base import AbstractGraphEdge, AbstractGraph


class TestAbstractGraphEdge:

    class MockAbstractGraphEdge(AbstractGraphEdge):
        def __init__(self, src, target, *args, **kwargs):
            super().__init__(src, target, *args, **kwargs)

    def test_edge_equality(self):
        e0 = TestAbstractGraphEdge.MockAbstractGraphEdge('a', 'b')
        e1 = TestAbstractGraphEdge.MockAbstractGraphEdge('a', 'b')

        assert e0 == e1

        e2 = TestAbstractGraphEdge.MockAbstractGraphEdge('a', 'c')

        assert e0 != e2

    def test_hash(self):
        src, target = 'a', 'b'

        e0 = TestAbstractGraphEdge.MockAbstractGraphEdge(src=src, target=target)
        expected = hash((src, target))

        assert expected == hash(e0)
