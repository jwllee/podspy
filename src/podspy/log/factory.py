#!/usr/bin/env python

"""This is the factory module for the log package

"""
from opyenxes.model.XLog import XLog
from opyenxes.model.XEvent import XEvent
from opyenxes.utils.XAttributeUtils import XAttributeType as atype
from opyenxes.utils.XAttributeUtils import XAttributeUtils as autils
from opyenxes.model.XAttributeDiscrete import XAttributeDiscrete
from opyenxes.model.XAttributeLiteral import XAttributeLiteral
from opyenxes.model.XAttributeContinuous import XAttributeContinuous
from opyenxes.model.XAttributeBoolean import XAttributeBoolean
from opyenxes.model.XAttributeID import XAttributeID
from opyenxes.model.XAttributeList import XAttributeList
from opyenxes.model.XAttributeContainer import XAttributeContainer
from opyenxes.model.XAttributeTimestamp import XAttributeTimestamp
from opyenxes.classification.XEventAndClassifier import XEventAndClassifier
from . import constants as cst
from . import table as tb

import logging
import pandas as pd
import numpy as np


logger = logging.getLogger(__file__)


__all__ = [
    'LogTableFactory'
]


class LogTableFactory:
    @staticmethod
    def new_log_table(xlog):
        return XLog2LogTable().xlog2table(xlog)


class XLog2LogTable:
    def __init__(self):
        self.__event_ind = 0
        self.__trace_ind = 0
        self.__event_df_dict = dict()
        self.__trace_df_dict = dict()

    def parse_xattribute(self, attrib):
        _type = autils.get_type(attrib)
        if _type == XAttributeContainer or _type == XAttributeList:
            logger.warning('LogTable do not support XAttributeList or XAttributeContainer')
            return None, None, None
        else:
            return attrib.get_key(), attrib.get_value(), attrib.get_extension()

    def parse_xattribute_list(self, attribs):
        parsed = [self.parse_xattribute(attrib) for attrib in attribs]
        parsed = filter(lambda item: item != (None, None, None), parsed)
        return {attrib[0]:attrib for attrib in parsed}

    def parse_xattribute_dict(self, attribs):
        return {key: self.parse_xattribute(val) for key, val in attribs.items()}

    def parse_classifier(self, clf):
        return clf.name(), clf.get_defining_attribute_keys()

    def parse_classifier_list(self, clfs):
        parsed = [self.parse_classifier(clf) for clf in clfs]
        return {clf[0]: clf for clf in parsed}

    def parse_extension(self, ext):
        return ext.get_name(), ext.get_prefix(), ext.get_uri()

    def parse_extension_set(self, exts):
        parsed = [self.parse_extension(ext) for ext in exts]
        return {e[0]: e for e in parsed}

    def xtraces2df(self, traces):
        trace_df_dict = dict()

        for trace in traces:
            attrib_dict = dict(trace.get_attributes())
            trace_df_dict[self.__trace_ind] = attrib_dict
            self.__trace_ind += 1

        return trace_df_dict

    def xevents2df(self, events, caseid):
        event_df_dict = dict()

        for event in events:
            assert isinstance(event, XEvent)
            attrib_dict = self.parse_xattribute_dict(event.get_attributes())
            # add caseid
            attrib_dict[cst.CASEID] = caseid
            event_df_dict[self.__event_ind] = attrib_dict
            self.__event_ind += 1

        return event_df_dict

    def xlog2table(self, xlog):
        assert isinstance(xlog, XLog)
        trace_df_dict = self.xtraces2df(xlog)
        event_df_dict = dict()

        for trace in xlog:
            caseid = trace.get_attributes()['concept:name'].get_value()
            event_df_dict_i = self.xevents2df(trace, caseid)
            event_df_dict.update(event_df_dict_i)

        global_trace_attribs = self.parse_xattribute_list(xlog.get_global_trace_attributes())
        global_event_attribs = self.parse_xattribute_list(xlog.get_global_event_attributes())
        log_attribs = self.parse_xattribute_dict(xlog.get_attributes())

        clfs = self.parse_classifier_list(xlog.get_classifiers())
        exts = self.parse_extension_set(xlog.get_extensions())

        trace_df = pd.DataFrame.from_dict(trace_df_dict, 'index')
        event_df = pd.DataFrame.from_dict(event_df_dict, 'index')

        lt = tb.LogTable(
            trace_df=trace_df,
            event_df=event_df,
            attributes=log_attribs,
            global_trace_attributes=global_trace_attribs,
            global_event_attributes=global_event_attribs,
            classifiers=clfs,
            extensions=exts
        )

        return lt
