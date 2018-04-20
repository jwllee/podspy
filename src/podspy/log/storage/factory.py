#!/usr/bin/env python

"""This is the factory module.

This module contains factory class to create event storages.

Note:
    - Do not support representing XAttributeList and XAttributeContainer!
"""


from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
from opyenxes.extension.XExtension import XExtension
from opyenxes.utils.XAttributeUtils import XAttributeUtils
from opyenxes.extension.XExtensionManager import XExtensionManager
from podspy.log import utils
from podspy.log.storage import *
import pandas as pd
import functools as fts
import itertools as its


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = ['EventStorageFactory']


class EventStorageFactory:

    MANAGER = XExtensionManager()
    CONCEPT_EXTENSION = MANAGER.get_by_name('Concept')

    CASEID = 'caseid'
    ACTIVITY = 'activity'

    # mapping between XAttribute type strings and pandas dtype
    DISCRETE = 'DISCRETE'
    LITERAL = 'LITERAL'
    CONTINUOUS = 'CONTINUOUS'
    BOOLEAN = 'BOOLEAN'
    TIMESTAMP = 'TIMESTAMP'

    ATTR_2_DTYPE = {
        DISCRETE: 'int',
        LITERAL: 'str',
        CONTINUOUS: 'float',
        BOOLEAN: 'bool',
        TIMESTAMP: 'datetime64[ns]'
    }

    def xes2storage(self, log, clf=XEventNameClassifier()):
        log_attribute_list = sorted(list(self.__get_attribute_set(log, include_value=True)), key=lambda item: item[1])
        trace_attribute_set = self.__get_attribute_set_from_attributable_list(log)
        event_attribute_set = fts.reduce(
            lambda all, trace: all.union(self.__get_attribute_set_from_attributable_list(trace)), log, set())

        trace_attribute_list = sorted(list(trace_attribute_set), key=lambda item: item[1])
        event_attribute_list = sorted(list(event_attribute_set), key=lambda item: item[1])

        # make dataframe for traces and events
        trace_df = self.traces2df(log, trace_attribute_list)
        event_df = self.log_events2df(log, event_attribute_list, clf)

        storage = EventStorage(trace_df, event_df, log_attribute_list, trace_attribute_list, event_attribute_list)
        return storage

    def get_attribute_series(self, attributables, name, attribute_name, dtype):
        l = map(lambda a: a.get_attributes()[name].get_value() if name in a.get_attributes() else None, attributables)
        s = pd.Series(l, dtype=dtype, name=attribute_name)
        return s

    def get_attribute_series_dict(self, attributables, attribute_list):
        series_dict = dict()
        for attribute_tuple in attribute_list:
            type_name = attribute_tuple[0]
            name = attribute_tuple[1]
            attribute_name = attribute_tuple[2]
            if type_name not in EventStorageFactory.ATTR_2_DTYPE:
                # not supporting this XAttribute type
                continue
            dtype = EventStorageFactory.ATTR_2_DTYPE[type_name]
            attribute_series = self.get_attribute_series(attributables, name, attribute_name, dtype)
            series_dict[attribute_name] = attribute_series
        return series_dict

    def traces2df(self, log, trace_attribute_list):
        # do it per trace_attribute rather than per trace so that memory efficient techniques can be used to
        # store series of attribute values with the same type
        filtered_attribute_list = filter(lambda t: t[0] in EventStorageFactory.ATTR_2_DTYPE, trace_attribute_list)
        filtered_attribute_list = list(filtered_attribute_list)
        series_dict = self.get_attribute_series_dict(log, filtered_attribute_list)
        colnames = map(lambda t: t[2], filtered_attribute_list)

        df = pd.DataFrame(series_dict, columns=colnames)

        utils.optimize_df_dtypes(df)

        return df

    def __get_activity_series(self, events, clf):
        activities = map(lambda event: clf.get_class_identity(event), events)
        series = pd.Series(activities, dtype='str', name=EventStorageFactory.ACTIVITY)
        return series

    def trace_events2df(self, trace, caseid, event_attribute_list, clf):
        series_dict = dict()
        s_caseid = pd.Series(list(its.repeat(caseid, times=len(trace))), dtype='str', name=EventStorageFactory.CASEID)
        s_activity = self.__get_activity_series(trace, clf)

        series_dict[s_caseid.name] = s_caseid
        series_dict[s_activity.name] = s_activity

        filtered_attribute_list = filter(lambda t: t[0] in EventStorageFactory.ATTR_2_DTYPE, event_attribute_list)
        filtered_attribute_list = list(filtered_attribute_list)
        d = self.get_attribute_series_dict(trace, filtered_attribute_list)
        series_dict.update(d)
        colnames = map(lambda t: t[2], filtered_attribute_list)
        colnames = [s_caseid.name, s_activity.name] + list(colnames)
        df = pd.DataFrame(series_dict, columns=colnames)

        utils.optimize_df_dtypes(df)

        return df

    def log_events2df(self, log, event_attribute_list, clf):
        event_df_list = list()
        for trace in log:
            caseid = EventStorageFactory.CONCEPT_EXTENSION.extract_name(trace)
            event_df_i = self.trace_events2df(trace, caseid, event_attribute_list, clf)
            event_df_list.append(event_df_i)
        event_df = pd.concat(event_df_list, axis=0)

        utils.optimize_df_dtypes(event_df)

        return event_df

    def __get_attribute_set_from_attributable_list(self, attributables):
        s = fts.reduce(lambda all, a: self.__get_attribute_set(a, all), attributables, set())
        return s

    def __get_attribute_set(self, attributable, attribute_set=set(), include_value=False):
        for name, attribute in attributable.get_attributes().items():
            # we want four things from each attribute:
            # - attribute type name
            # - name
            # - key
            # - extension
            type_name = XAttributeUtils.get_type_string(attribute)
            key = attribute.get_key()
            extension = attribute.get_extension()
            extension_name = extension.get_name() if isinstance(extension, XExtension) else None

            if include_value:
                value = attribute.get_value()
                row = (type_name, name, key, value, extension_name)
            else:
                row = (type_name, name, key, extension_name)

            attribute_set.add(row)
        return attribute_set





