#!/usr/bin/env python

"""This is the example module.

This module does stuff.
"""

__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"



class Splittable:
    def __init__(self, n):
        self.content = list(map(lambda item: str(item), range(n)))

    def __iter__(self):
        return iter(self.content)

    class SplittableIterator:
        def __init__(self, content):
            self.content = content

        def __iter__(self):
            return self

        def __next__(self):
            return next(self.content)


def test_splittable_inline_split_to_items():
    s = Splittable(3)
    a, b, c = s

    assert a == '0'
    assert b == '1'
    assert c == '2'


def test_list_as_iterable():
    l = list(map(lambda item: str(item), range(3)))

    for i in l:
        print(i)

    assert len(l) == 3
