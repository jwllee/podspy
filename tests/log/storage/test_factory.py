#!/usr/bin/env python

"""This is the test module for the log storage module.

"""


import pytest
from podspy.log.storage import *
from pandas.util.testing import assert_frame_equal
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def test_simple():
    assert 1 + 1 == 2


@pytest.fixture()
def factory():
    return EventStorageFactory()


def test_traces2df(factory, traces_and_df, trace_attr_list):
    traces = traces_and_df[0]
    expected_df = traces_and_df[1]

    df = factory.traces2df(traces, trace_attr_list)

    assert_frame_equal(df, expected_df, check_dtype=True)


def test_trace_events2df(factory, a_trace_and_df, event_attr_list):
    a_trace = a_trace_and_df[0]
    expected_df = a_trace_and_df[1]

    caseid = expected_df['caseid'].values[0]

    clf = XEventNameClassifier()
    df = factory.trace_events2df(a_trace, caseid, event_attr_list, clf)

    assert_frame_equal(df, expected_df, check_dtype=True)


def test_log_events2df(factory, log_and_event_df, event_attr_list):
    log = log_and_event_df[0]
    expected_df = log_and_event_df[1]

    clf = XEventNameClassifier()
    df = factory.log_events2df(log, event_attr_list, clf)

    assert_frame_equal(df, expected_df, check_dtype=True)
