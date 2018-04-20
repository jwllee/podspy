#!/usr/bin/env python

"""This is the storage module.

This module contains classes that can store XLog in an easily processable representation.
"""


import pandas as pd
import numpy as np


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = ['EventStorage']


class EventStorage:

    ATTRIBUTE_TYPE = 'type'
    ATTRIBUTE_KEY = 'key'
    ATTRIBUTE_VALUE = 'value'
    ATTRIBUTE_EXTENSION_NAME = 'extension_name'

    def __init__(self, trace_df, event_df, log_attributes=list(), trace_attributes=list(), event_attributes=list()):
        self.trace_df = trace_df
        self.event_df = event_df

        # each attribute is a map that contains:
        # - attribute type name
        # - key
        # - extension name
        # log attributes contains value as well
        self.log_attributes = log_attributes
        self.trace_attributes = trace_attributes
        self.event_attributes = event_attributes

    def to_json(self):
        # todo: Conversion to json format
        pass

    def from_json(self):
        # todo: Conversion from json format
        pass


