#!/usr/bin/env python

"""This is the conf test module.

"""

__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


import pytest
import pandas as pd
import numpy as np
import itertools as itrl

from podspy.structure import CausalMatrix
from podspy.log import constants as cnst
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
            caseids = itrl.repeat(caseid, len(trace))

            event_row = zip(caseids, trace)
            event_rows += list(event_row)

            caseid += 1

    labels = [cnst.CASEID, cnst.ACTIVITY]
    event_df = pd.DataFrame.from_records(event_rows, columns=labels)

    logtable = tb.LogTable()
    logtable.event_df = event_df

    return logtable


@pytest.fixture()
def simple_causal_matrix():
    # causal matrix
    mat = [
        (0, 0, 83, 0, 0),   # a row
        (0, 0, 64, 0, 0),   # b row
        (0, 0, 0, 87, 60),  # c row
        (0, 0, 0, 0, 0),    # d row
        (0, 0, 0, 0, 0)
    ]

    mat = np.array(mat)
    activity_list = ['a', 'b', 'c', 'd', 'e']
    df = pd.DataFrame(mat, index=activity_list, columns=activity_list)
    cmat = CausalMatrix(activity_list, df)

    return cmat
