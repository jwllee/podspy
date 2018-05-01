#!/usr/bin/env python

"""This is the test module for the noise module in log package.

This module test methods.
"""


import pytest
import pandas as pd
from pandas.util.testing import assert_frame_equal

from podspy.log.storage import *
from podspy.log.noise import *


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def simple_test():
    assert 1 + 1 == 2


event_df_columns = [EventStorageFactory.CASEID, EventStorageFactory.ACTIVITY, 'concept:name', 'time:timestamp']

events = [
    ['1', 'a', 'a', 1], ['1', 'b', 'b', 2], ['1', 'c', 'c', 3], ['1', 'd', 'd', 4], ['1', 'e', 'e', 5], ['1', 'f', 'f', 6],
    ['2', 'a', 'a', 1], ['2', 'b', 'b', 2], ['2', 'c', 'c', 3], ['2', 'd', 'd', 4], ['2', 'e', 'e', 5], ['2', 'f', 'f', 6],
    ['3', 'a', 'a', 1], ['3', 'b', 'b', 2], ['3', 'c', 'c', 3], ['3', 'd', 'd', 4], ['3', 'e', 'e', 5], ['3', 'f', 'f', 6],
    ['4', 'q', 'q', 1], ['4', 'r', 'r', 2], ['4', 's', 's', 3], ['4', 't', 't', 4], ['4', 'u', 'u', 5], ['4', 'v', 'v', 6],
    ['5', 'q', 'q', 1], ['5', 'r', 'r', 2], ['5', 's', 's', 3], ['5', 't', 't', 4], ['5', 'u', 'u', 5], ['5', 'v', 'v', 6],
    ['6', 'q', 'q', 1], ['6', 'r', 'r', 2], ['6', 's', 's', 3], ['6', 't', 't', 4], ['6', 'u', 'u', 5], ['6', 'v', 'v', 6]
]

event_df = pd.DataFrame(events, columns=event_df_columns)


@pytest.fixture(scope='function')
def a_simple_event_df():
    return event_df


def test_swap_b_c_in_event_df(a_simple_event_df):
    expected = [
        ['1', 'a', 'a', 1], ['1', 'c', 'c', 2], ['1', 'b', 'b', 3], ['1', 'd', 'd', 4], ['1', 'e', 'e', 5], ['1', 'f', 'f', 6],
        ['2', 'a', 'a', 1], ['2', 'c', 'c', 2], ['2', 'b', 'b', 3], ['2', 'd', 'd', 4], ['2', 'e', 'e', 5], ['2', 'f', 'f', 6],
        ['3', 'a', 'a', 1], ['3', 'c', 'c', 2], ['3', 'b', 'b', 3], ['3', 'd', 'd', 4], ['3', 'e', 'e', 5], ['3', 'f', 'f', 6],
        ['4', 'q', 'q', 1], ['4', 'r', 'r', 2], ['4', 's', 's', 3], ['4', 't', 't', 4], ['4', 'u', 'u', 5], ['4', 'v', 'v', 6],
        ['5', 'q', 'q', 1], ['5', 'r', 'r', 2], ['5', 's', 's', 3], ['5', 't', 't', 4], ['5', 'u', 'u', 5], ['5', 'v', 'v', 6],
        ['6', 'q', 'q', 1], ['6', 'r', 'r', 2], ['6', 's', 's', 3], ['6', 't', 't', 4], ['6', 'u', 'u', 5], ['6', 'v', 'v', 6]
    ]

    expected_df = pd.DataFrame(expected, columns=event_df_columns)

    noisy_df = add_swap_noise(a_simple_event_df, pairs=[['b', 'c']], occur=1.)

    assert_frame_equal(noisy_df, expected_df, check_dtype=True)


def test_swap_b_c_and_t_u_in_event_df(a_simple_event_df):
    expected = [
        ['1', 'a', 'a', 1], ['1', 'c', 'c', 2], ['1', 'b', 'b', 3], ['1', 'd', 'd', 4], ['1', 'e', 'e', 5], ['1', 'f', 'f', 6],
        ['2', 'a', 'a', 1], ['2', 'c', 'c', 2], ['2', 'b', 'b', 3], ['2', 'd', 'd', 4], ['2', 'e', 'e', 5], ['2', 'f', 'f', 6],
        ['3', 'a', 'a', 1], ['3', 'c', 'c', 2], ['3', 'b', 'b', 3], ['3', 'd', 'd', 4], ['3', 'e', 'e', 5], ['3', 'f', 'f', 6],
        ['4', 'q', 'q', 1], ['4', 'r', 'r', 2], ['4', 's', 's', 3], ['4', 'u', 'u', 4], ['4', 't', 't', 5], ['4', 'v', 'v', 6],
        ['5', 'q', 'q', 1], ['5', 'r', 'r', 2], ['5', 's', 's', 3], ['5', 'u', 'u', 4], ['5', 't', 't', 5], ['5', 'v', 'v', 6],
        ['6', 'q', 'q', 1], ['6', 'r', 'r', 2], ['6', 's', 's', 3], ['6', 'u', 'u', 4], ['6', 't', 't', 5], ['6', 'v', 'v', 6]
    ]

    expected_df = pd.DataFrame(expected, columns=event_df_columns)

    noisy_df = add_swap_noise(a_simple_event_df, pairs=[['b', 'c'], ['t', 'u']], occur=1.)

    assert_frame_equal(noisy_df, expected_df, check_dtype=True)


def test_swap_pair_order_b_c_and_b_d(a_simple_event_df):
    expected = [
        ['1', 'a', 'a', 1], ['1', 'c', 'c', 2], ['1', 'd', 'd', 3], ['1', 'b', 'b', 4], ['1', 'e', 'e', 5], ['1', 'f', 'f', 6],
        ['2', 'a', 'a', 1], ['2', 'c', 'c', 2], ['2', 'd', 'd', 3], ['2', 'b', 'b', 4], ['2', 'e', 'e', 5], ['2', 'f', 'f', 6],
        ['3', 'a', 'a', 1], ['3', 'c', 'c', 2], ['3', 'd', 'd', 3], ['3', 'b', 'b', 4], ['3', 'e', 'e', 5], ['3', 'f', 'f', 6],
        ['4', 'q', 'q', 1], ['4', 'r', 'r', 2], ['4', 's', 's', 3], ['4', 't', 't', 4], ['4', 'u', 'u', 5], ['4', 'v', 'v', 6],
        ['5', 'q', 'q', 1], ['5', 'r', 'r', 2], ['5', 's', 's', 3], ['5', 't', 't', 4], ['5', 'u', 'u', 5], ['5', 'v', 'v', 6],
        ['6', 'q', 'q', 1], ['6', 'r', 'r', 2], ['6', 's', 's', 3], ['6', 't', 't', 4], ['6', 'u', 'u', 5], ['6', 'v', 'v', 6]
    ]

    expected_df = pd.DataFrame(expected, columns=event_df_columns)

    noisy_df = add_swap_noise(a_simple_event_df, pairs=[['b', 'c'], ['b', 'd']], occur=1.)

    assert_frame_equal(noisy_df, expected_df, check_dtype=True)


def test_swap_on_realistic_event_df(an_event_df):
    swap_pairs = [
        ['Ship product', 'Emit invoice'],
        ['Archive order', 'Receive payment']
    ]
    noisy_df = add_swap_noise(an_event_df, pairs=swap_pairs, occur=0.5)

    assert isinstance(noisy_df, pd.DataFrame) == True