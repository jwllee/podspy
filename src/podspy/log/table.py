#!/usr/bin/env python

"""This is the example module.

This module does stuff.
"""

__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = ['LogTable']


import pandas as pd

# To me:
# there are six types of elementary attributes, and two types of collection attributes
# 1. string
# 2. date
# 3. int
# 4. float
# 5. boolean
# 6. id
# Collection attributes:
# 7. list
# 8. container


class LogTable:
    def __init__(self, trace_table=None, event_table=None, attributes=None,
                 global_trace_attributes=list(), global_event_attributes=list(),
                 classifiers=None, extensions=None):
        ''' Container class of event data in tabular format.

        Parameters
        ----------
        trace_table: DataFrame
            DataFrame containing information of each trace in event log
        event_table: DataFrame
            DataFrame containing information of each event in event log
        attributes: dict
            Dictionary containing attributes on the log level
        global_trace_attributes: dict
            Dictionary containing global trace attributes
        global_event_attributes: dict
            Dictionary containing global event attributes
        classifiers: dict
            Classifiers to give identities to event corresponding to a sub-list of the global event attributes
        extensions: dict
            Extensions to give semantics to attributes, e.g., the concept extension. Each extension is a tuple
            consisting of (name, prefix, uri)
        '''
        self.trace_table = trace_table if trace_table is not None else pd.DataFrame()
        self.event_table = event_table if event_table is not None else pd.DataFrame()
        self.attributes = attributes if attributes is not None else dict()

        self.global_trace_attributes = global_trace_attributes
        self.global_event_attributes = global_event_attributes
        self.xes_attributes = {'version': 2.0, 'features': []}
        # TODO: need to explicitly alert, e.g., warning?, the user that nested attributes are not supported
        self.classifiers = classifiers if classifiers is not None else dict()
        self.extensions = extensions if extensions is not None else dict()
