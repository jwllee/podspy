#!/usr/bin/env python

"""This is the unit test module.

This module tests the petrinet semantics module.
"""

from podspy.petrinet.semantics import *
from podspy.petrinet.elements import *

import pandas as pd
import numpy as np

from pandas.testing import assert_series_equal


def test_make_marking():
    graph = 'g0'
    p0 = Place(graph, 'p0')
    p1 = Place(graph, 'p1')
    p2 = Place(graph, 'p2')
    m = Marking([p0, p1, p2])
    assert isinstance(m, Marking)
    assert m.occurrences(p0) == 1
    assert m.occurrences(p1) == 1
    assert m.occurrences(p2) == 1


def test_marking_as_series():
    graph = 'g0'
    p0 = Place(graph, 'p0')
    p1 = Place(graph, 'p1')
    p2 = Place(graph, 'p2')
    p3 = Place(graph, 'p3')
    p4 = Place(graph, 'p4')
    place_list = [p0, p1, p2, p3, p4]
    pname_list = list(map(lambda p: p.label, place_list))

    m0 = Marking([p1, p2, p4])
    ss0 = m0.as_series(place_list)
    expected = pd.Series([0., 1., 1., 0., 1.], index=pname_list)
    assert_series_equal(ss0, expected)

    # multiple tokens in some places
    m1 = Marking([p1, p1, p2, p2, p2, p4])
    ss1 = m1.as_series(place_list)
    expected = pd.Series([0., 2., 3., 0., 1.], index=pname_list)
    assert_series_equal(ss1, expected)

