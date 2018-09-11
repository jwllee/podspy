#!/usr/bin/env python

"""This is the unit test module for the causal matrix module.

"""


import pytest
import functools as fcts
import itertools as itrs
import pandas as pd
import numpy as np

from podspy.structure import CausalMatrix
from podspy.log import constants as cnst
from podspy.log import factory as fty
from podspy.log import table as tb


@pytest.fixture()
def simple_log_table():
    # Contains the following traces (with frequency)
    # 45 <a, c, d>
    # 42 <b, c, d>
    # 38 <a, c, e>
    # 22 <b, c, e>
    t0 = ['a', 'c', 'd']
    t1 = ['b', 'c', 'd']
    t2 = ['a', 'c', 'e']
    t3 = ['b', 'c', 'e']

    traces = [t0, t1, t2, t3]

    freq0 = 45
    freq1 = 42
    freq2 = 38
    freq3 = 22

    freqs = [freq0, freq1, freq2, freq3]

    trace_freq_list = zip(traces, freqs)

    caseid = 0
    event_rows = []

    for trace, freq in trace_freq_list:
        for i in range(freq):
            # repeat the caseid id over all events of a trace
            caseids = itrs.repeat(caseid, len(trace))

            event_row = zip(caseids, trace)
            event_rows += list(event_row)

            caseid += 1

    labels = [cnst.CASEID, cnst.ACTIVITY]
    event_df = pd.DataFrame.from_records(event_rows, columns=labels)

    logtable = tb.LogTable()
    logtable.event_df = event_df

    return logtable


def test_simple_log_table_fixture(simple_log_table):
    assert isinstance(simple_log_table, tb.LogTable)
    print(simple_log_table.event_df.head())


class TestCausalMatrix:
    def test_build_from_logtable(self, simple_log_table):
        # sort activities
        cmat = CausalMatrix.build_from_logtable(simple_log_table, sort=True)

        assert isinstance(cmat, CausalMatrix)

        assert cmat.activity_list == ['a', 'b', 'c', 'd', 'e']

        # expected causal matrix
        # 45 <a, c, d>
        # 42 <b, c, d>
        # 38 <a, c, e>
        # 22 <b, c, e>

        mat = [
            (0, 0, 83, 0, 0),  # a row
            (0, 0, 64, 0, 0),  # b row
            (0, 0, 0, 87, 60), # c row
            (0, 0, 0, 0, 0),   # d row
            (0, 0, 0, 0, 0)    # e row
        ]
        mat = np.array(mat)

        assert isinstance(cmat.matrix, pd.DataFrame)
        assert (cmat.matrix.values == mat).all()
