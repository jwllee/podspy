#!/usr/bin/env python

"""This is the test module for table module.

"""


from podspy.log.table import *


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def test_simple():
    assert 1 + 1 == 2


def test_log_table_construct():
    table = LogTable()
    assert isinstance(table, LogTable) == True

