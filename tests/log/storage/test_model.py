#!/usr/bin/env python

"""This is the test module for event storage.

"""


from podspy.log.storage import *


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def test_simple():
    assert 1 + 1 == 2


def test_can_construct_event_storage():
    storage = EventStorage(None, None, None)
    assert isinstance(storage, EventStorage) == True

