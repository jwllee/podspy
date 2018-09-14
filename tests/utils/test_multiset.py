#!/usr/bin/env python

"""This is the unit test module.

This module test classes in the collection module.
"""


import pytest
from podspy.utils.multiset import *


@pytest.fixture(params=[
    [], # empty item list
    ['a', 'b', 'c'],
    ['a', 'a', 'b', 'b', 'b', 'c']
])
def items(request):
    return request.param


class TestHashMultiSet:
    def test_make_multiset(self, items):
        ms = HashMultiSet(items)
        assert isinstance(ms, HashMultiSet)

    def test_len_multiset(self, items):
        ms = HashMultiSet(items)
        assert len(ms) == len(items)

    def test_occurrences(self, items):
        ms = HashMultiSet(items)
        # count items
        d = dict()
        for item in items:
            if item not in d:
                d[item] = 0
            d[item] = d[item] + 1

        for item in set(items):
            assert ms.occurrences(item) == d[item], 'ms: {} != d: {} on item: {}'.format(ms, d, item)

    def test_iterator_multiset(self, items):
        ms = HashMultiSet(items)

        expected = dict()
        for item in items:
            if item not in expected:
                expected[item] = 0
            expected[item] = expected[item] + 1

        tmp = dict()
        for item in ms:
            if item not in tmp:
                tmp[item] = 0
            tmp[item] = tmp[item] + 1

        assert expected == tmp

        # do iteration again to make sure that multiset uses an iterator
        tmp.clear()
        for item in ms:
            if item not in tmp:
                tmp[item] = 0
            tmp[item] = tmp[item] + 1

        assert expected == tmp

    def test_get_baseset(self, items):
        base_set = set(items)
        ms = HashMultiSet(items)

        assert ms.base_set() == base_set

    def test_less_than(self):
        t0 = HashMultiSet()
        o0 = HashMultiSet()

        assert (t0 < o0) == True
        assert (o0 < t0) == True

        t1 = HashMultiSet()
        o1 = HashMultiSet(['a', 'b', 'c'])

        assert (t1 < o1) == True
        assert (o1 < t1) == False

        t2 = HashMultiSet(['a', 'b', 'c'])
        o2 = HashMultiSet(['a', 'a', 'b', 'b', 'b', 'c', 'c'])

        assert (t2 < o2) == True
        assert (o2 < t2) == False

        t3 = HashMultiSet(['a', 'a', 'b', 'c'])
        o3 = HashMultiSet(['a', 'a', 'b', 'c'])

        assert (t3 < o3) == False
        assert (o3 < t3) == False

        t4 = HashMultiSet(['a', 'b', 'b'])
        o4 = HashMultiSet(['b', 'b', 'b', 'c', 'c'])

        assert (t4 < o4) == False
        assert (o4 < t4) == False

        t5 = HashMultiSet(['a', 'b', 'c'])
        o5 = HashMultiSet(['a', 'a', 'b', 'b', 'c'])

        assert (t5 < o5) == False   # item c occurs once in both multisets
        assert (o5 < t5) == False

    def test_less_than_or_equal(self):
        t0 = HashMultiSet()
        o0 = HashMultiSet()

        assert (t0 <= o0) == True
        assert (o0 <= t0) == True

        t1 = HashMultiSet()
        o1 = HashMultiSet(['a', 'b', 'c'])

        assert (t1 <= o1) == True
        assert (o1 <= t1) == False

        t2 = HashMultiSet(['a', 'b', 'c'])
        o2 = HashMultiSet(['a', 'a', 'b', 'b', 'b', 'c', 'c'])

        assert (t2 <= o2) == True
        assert (o2 <= t2) == False

        t3 = HashMultiSet(['a', 'a', 'b', 'c'])
        o3 = HashMultiSet(['a', 'a', 'b', 'c'])

        assert (t3 <= o3) == True
        assert (o3 <= t3) == True

        t4 = HashMultiSet(['a', 'b', 'b'])
        o4 = HashMultiSet(['b', 'b', 'b', 'c', 'c'])

        assert (t4 <= o4) == False
        assert (o4 <= t4) == False

        t5 = HashMultiSet(['a', 'b', 'c'])
        o5 = HashMultiSet(['a', 'a', 'b', 'b', 'c'])

        assert (t5 <= o5) == True
        assert (o5 <= t5) == False

    def test_equal(self):
        t0 = HashMultiSet()
        o0 = HashMultiSet()

        assert (t0 == o0) == True
        assert (o0 == t0) == True

        t1 = HashMultiSet()
        o1 = HashMultiSet(['a', 'b', 'c'])

        assert (t1 == o1) == False
        assert (o1 == t1) == False

        t2 = HashMultiSet(['a', 'b', 'c'])
        o2 = HashMultiSet(['a', 'a', 'b', 'b', 'b', 'c', 'c'])

        assert (t2 == o2) == False
        assert (o2 == t2) == False

        t3 = HashMultiSet(['a', 'a', 'b', 'c'])
        o3 = HashMultiSet(['a', 'a', 'b', 'c'])

        assert (t3 == o3) == True
        assert (o3 == t3) == True

        t4 = HashMultiSet(['a', 'b', 'b'])
        o4 = HashMultiSet(['b', 'b', 'b', 'c', 'c'])

        assert (t4 == o4) == False
        assert (o4 == t4) == False

        t5 = HashMultiSet(['a', 'b', 'c'])
        o5 = HashMultiSet(['a', 'a', 'b', 'b', 'c'])

        assert (t5 == o5) == False
        assert (o5 == t5) == False

    def test_greater_than(self):
        t0 = HashMultiSet()
        o0 = HashMultiSet()

        assert (t0 > o0) == True
        assert (o0 > t0) == True

        t1 = HashMultiSet()
        o1 = HashMultiSet(['a', 'b', 'c'])

        assert (t1 > o1) == False
        assert (o1 > t1) == True

        t2 = HashMultiSet(['a', 'b', 'c'])
        o2 = HashMultiSet(['a', 'a', 'b', 'b', 'b', 'c', 'c'])

        assert (t2 > o2) == False
        assert (o2 > t2) == True

        t3 = HashMultiSet(['a', 'a', 'b', 'c'])
        o3 = HashMultiSet(['a', 'a', 'b', 'c'])

        assert (t3 > o3) == False
        assert (o3 > t3) == False

        t4 = HashMultiSet(['a', 'b', 'b'])
        o4 = HashMultiSet(['b', 'b', 'b', 'c', 'c'])

        assert (t4 > o4) == False
        assert (o4 > t4) == False

        t5 = HashMultiSet(['a', 'b', 'c'])
        o5 = HashMultiSet(['a', 'a', 'b', 'b', 'c'])

        assert (t5 > o5) == False
        assert (o5 > t5) == False # item c occurs once in both multisets

    def test_greater_than_or_equal(self):
        t0 = HashMultiSet()
        o0 = HashMultiSet()

        assert (t0 >= o0) == True
        assert (o0 >= t0) == True

        t1 = HashMultiSet()
        o1 = HashMultiSet(['a', 'b', 'c'])

        assert (t1 >= o1) == False
        assert (o1 >= t1) == True

        t2 = HashMultiSet(['a', 'b', 'c'])
        o2 = HashMultiSet(['a', 'a', 'b', 'b', 'b', 'c', 'c'])

        assert (t2 >= o2) == False
        assert (o2 >= t2) == True

        t3 = HashMultiSet(['a', 'a', 'b', 'c'])
        o3 = HashMultiSet(['a', 'a', 'b', 'c'])

        assert (t3 >= o3) == True
        assert (o3 >= t3) == True

        t4 = HashMultiSet(['a', 'b', 'b'])
        o4 = HashMultiSet(['b', 'b', 'b', 'c', 'c'])

        assert (t4 >= o4) == False
        assert (o4 >= t4) == False

        t5 = HashMultiSet(['a', 'b', 'c'])
        o5 = HashMultiSet(['a', 'a', 'b', 'b', 'c'])

        assert (t5 >= o5) == False
        assert (o5 >= t5) == True

    def test_retain_all(self):
        t0 = HashMultiSet(['a', 'a', 'b', 'c'])
        o0 = HashMultiSet()

        # retain empty multiset results in empty set
        t0.retain_all(o0)
        assert len(t0) == 0

        t1 = HashMultiSet(['a', 'c'])
        o1 = HashMultiSet(['a', 'a', 'b', 'b'])

        t1.retain_all(o1)
        assert t1.occurrences('a') == 1
        assert t1.occurrences('b') == 0
        assert t1.occurrences('c') == 0

        t2 = HashMultiSet(['a', 'a', 'a', 'b', 'b'])
        o2 = HashMultiSet(['a'])

        t2.retain_all(o2)
        assert t2.occurrences('a') == 1
        assert t2.occurrences('b') == 0

    def test_add(self):
        t0 = HashMultiSet()
        o0 = HashMultiSet()

        # make sure the sum multiset is another instance
        s0 = t0 + o0
        assert len(s0) == 0

        s0.add('a', 1)
        assert len(s0) == 1
        assert s0.occurrences('a') == 1
        assert len(t0) == 0 and len(o0) == 0
        assert t0.occurrences('a') == 0 and o0.occurrences('a') == 0

        t1 = HashMultiSet(['a', 'a', 'b'])
        o1 = HashMultiSet(['b'])

        s1 = t1 + o1
        assert len(s1) == 4
        assert s1.occurrences('a') == 2
        assert s1.occurrences('b') == 2

        t2 = HashMultiSet(['a', 'b'])
        o2 = HashMultiSet(['b', 'c'])

        s2 = t2 + o2
        assert len(s2) == 4
        assert s2.occurrences('a') == 1
        assert s2.occurrences('b') == 2
        assert s2.occurrences('c') == 1

    def test_remove(self):
        ms0 = HashMultiSet()
        removed0 = ms0.remove('a')

        assert removed0 == False
        assert len(ms0) == 0

        ms1 = HashMultiSet(['a', 'b'])
        removed1 = ms1.remove('b')

        assert removed1 == True
        assert len(ms1) == 1

    def test_remove_all(self):
        ms0 = HashMultiSet(['a', 'a', 'b'])
        r0 = HashMultiSet(['b'])

        removed0 = ms0.remove_all(r0)
        assert removed0 == True
        assert len(ms0) == 2
        assert ms0.occurrences('b') == 0

    def test_subtract(self):
        t0 = HashMultiSet()
        o0 = HashMultiSet()

        # make sure the result is another instance
        s0 = t0 - o0
        assert len(s0) == 0

        s0.add('a', 1)
        assert len(s0) == 1
        assert s0.occurrences('a') == 1
        assert len(t0) == 0 and len(o0) == 0
        assert t0.occurrences('a') == 0 and o0.occurrences('a') == 0

        t1 = HashMultiSet(['a', 'a', 'b'])
        o1 = HashMultiSet(['b'])

        s1 = t1 - o1
        assert len(s1) == 2
        assert s1.occurrences('a') == 2
        assert s1.occurrences('b') == 0

        t2 = HashMultiSet(['a', 'b'])
        o2 = HashMultiSet(['b', 'c'])

        s2 = t2 - o2
        assert len(s2) == 1
        assert s2.occurrences('a') == 1
        assert s2.occurrences('b') == 0
        assert s2.occurrences('c') == 0

