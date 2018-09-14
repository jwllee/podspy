#!/usr/bin/env python

"""This is the example module.

This module does stuff.
"""

from podspy.utils.patterns import Singleton


class MockSingleton(Singleton):
    def __init__(self, var='hello world'):
        self.var = var


def test_singleton_is_single():
    s0 = MockSingleton()
    s1 = MockSingleton()

    assert id(s0) == id(s1)
    assert s0 is s1

    # changing the variable of s0 should change s1's as well
    s0.var = 'bye'

    assert s0 is s1
    assert s0.var == s1.var
