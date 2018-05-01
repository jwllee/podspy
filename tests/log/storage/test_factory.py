#!/usr/bin/env python

"""This is the test module for the log storage module.

"""


import pytest

from podspy.log.storage import *
from podspy.log.constant import *

from pandas.util.testing import assert_frame_equal
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def test_simple():
    assert 1 + 1 == 2


@pytest.fixture()
def factory():
    return EventStorageFactory()


def test_traces2df(factory, an_xlog, a_trace_df, a_trace_attribute_list):
    expected_df = a_trace_df

    df = factory.traces2df(an_xlog, a_trace_attribute_list)

    assert_frame_equal(df, expected_df, check_dtype=True)


def test_trace_events_2_df(factory, a_xtrace, an_event_df, an_event_attribute_list):
    caseid = a_xtrace.get_attributes()['concept:name'].get_value()
    expected_df = an_event_df[(an_event_df[CASEID] == caseid)]
    expected_df = expected_df.reset_index(drop=True)

    for col in expected_df.select_dtypes(include=['category']).columns:
        expected_df.loc[:,col] = expected_df[col].astype('str')

        # need to redo whether to categorize data
        nb_unique_vals = expected_df[col].unique().shape[0]
        nb_total = expected_df[col].shape[0]

        if nb_unique_vals / nb_total < 0.5:
            expected_df.loc[:,col] = expected_df[col].astype('category')

    clf = XEventNameClassifier()

    df = factory.trace_events2df(a_xtrace, caseid, an_event_attribute_list, clf)

    assert_frame_equal(df, expected_df, check_dtype=True)


def test_log_events_2_df(factory, an_xlog, an_event_df, an_event_attribute_list):
    expected_df = an_event_df
    clf = XEventNameClassifier()

    df = factory.log_events2df(an_xlog, an_event_attribute_list, clf)

    assert_frame_equal(df, expected_df, check_dtype=True)


