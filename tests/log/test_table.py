#!/usr/bin/env python

"""This is the test module for table module.

"""


import pytest, logging
import pandas as pd
import numpy as np
from podspy.log.table import *
import podspy.log.constant as const

from opyenxes.extension.XExtensionManager import XExtensionManager
from pandas.testing import assert_frame_equal

logger = logging.getLogger('tests')
EXTENSION_MANAGER = XExtensionManager()
CONCEPT_EXTENSION = EXTENSION_MANAGER.get_by_name('Concept')


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def test_simple():
    assert 1 + 1 == 2


def test_log_table_construct():
    table = LogTable()
    assert isinstance(table, LogTable) == True


@pytest.fixture()
def factory():
    return XLogToLogTable()


def test_xevents2df(an_event_df, a_xtrace, factory):
    caseid = CONCEPT_EXTENSION.extract_name(a_xtrace)
    caseid_list = [caseid for _ in range(len(a_xtrace))]
    df = factory.xevents2df(caseid_list, a_xtrace)
    expected = an_event_df[(an_event_df[const.CASEID] == caseid)]
    expected.reset_index(inplace=True, drop=True)
    assert_frame_equal(df, expected)


def test_xtraces2df(a_trace_df, an_xlog, factory):
    df = factory.xtraces2df(an_xlog)
    assert_frame_equal(a_trace_df, df)


def test_xlog2df(a_log_table, an_xlog, factory):
    table = factory.xlog2table(an_xlog)
    expected = a_log_table

    assert table.attributes == expected.attributes
    assert table.global_event_attributes == expected.global_event_attributes
    assert table.global_trace_attributes == expected.global_trace_attributes
    assert table.extensions == expected.extensions
    assert table.classifiers == expected.classifiers
    assert_frame_equal(table.event_df, expected.event_df)
    assert_frame_equal(table.trace_df, expected.trace_df)


def test_get_event_identity_list(a_log_table, an_event_clf_and_event_identity_list):
    # set the event classifier of the log table
    clf_name = an_event_clf_and_event_identity_list[0]
    expected = an_event_clf_and_event_identity_list[1]
    computed = a_log_table.get_event_identity_list(clf_name)
    assert computed == expected
