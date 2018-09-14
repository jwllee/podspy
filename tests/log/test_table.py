#!/usr/bin/env python

"""This is the test module for table module.

"""


import pytest, logging
import pandas as pd
import numpy as np
from podspy.log.table import *
import podspy.log.constants as const

from opyenxes.extension.XExtensionManager import XExtensionManager
from pandas.testing import assert_frame_equal

logger = logging.getLogger('tests')
EXTENSION_MANAGER = XExtensionManager()
CONCEPT_EXTENSION = EXTENSION_MANAGER.get_by_name('Concept')


def test_simple():
    assert 1 + 1 == 2


def test_log_table_construct():
    table = LogTable()
    assert isinstance(table, LogTable) == True


def test_get_event_identity_list(a_log_table, an_event_clf_and_event_identity_list):
    # set the event classifier of the log table
    clf_name = an_event_clf_and_event_identity_list[0]
    expected = an_event_clf_and_event_identity_list[1]
    computed = a_log_table.get_event_identity_list(clf_name)
    assert computed == expected


def test_get_trace_variants_no_activity_column_raises_value_error(a_log_table):
    with pytest.raises(ValueError):
        a_log_table.get_trace_variants()


def test_get_trace_variants_no_caseid_column_raises_value_error(a_log_table):
    with pytest.raises(ValueError):
        a_log_table.get_trace_variants()


def test_get_trace_variants_two_cases_one_variant():
    log_table = LogTable()
    variant = 'a{}b{}c'.format(LogTable.VARIANT_SEP, LogTable.VARIANT_SEP)
    events = ['a', 'b', 'c']
    log_table.event_df[const.ACTIVITY] = events * 2
    log_table.event_df[const.CASEID] = ['0', '0', '0', '1', '1', '1']
    variant_df = log_table.get_trace_variants()

    expected = pd.DataFrame({const.CASEID: ['0', '1'],
                             LogTable.VARIANT_ID: ['variant 0', 'variant 0'],
                             const.VARIANT: [variant, variant]})
    expected = expected[[const.CASEID, LogTable.VARIANT_ID, const.VARIANT]]

    assert_frame_equal(variant_df, expected)

def test_get_trace_variants_two_cases_two_variants():
    log_table = LogTable()
    variant0 = 'a{}b{}c'.format(LogTable.VARIANT_SEP, LogTable.VARIANT_SEP)
    variant1 = 'a{}b{}d'.format(LogTable.VARIANT_SEP, LogTable.VARIANT_SEP)
    events = ['a', 'b', 'c', 'a', 'b', 'd']
    log_table.event_df[const.ACTIVITY] = events
    log_table.event_df[const.CASEID] = ['0', '0', '0', '1', '1', '1']
    variant_df = log_table.get_trace_variants()

    expected = pd.DataFrame({const.CASEID: ['0', '1'],
                             LogTable.VARIANT_ID: ['variant 0', 'variant 1'],
                             const.VARIANT: [variant0, variant1]})
    expected = expected[[const.CASEID, LogTable.VARIANT_ID, const.VARIANT]]

    assert_frame_equal(variant_df, expected)
