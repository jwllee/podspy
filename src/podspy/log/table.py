#!/usr/bin/env python

"""This is the example module.

This module does stuff.
"""

__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = ['LogTable', 'XLogToLogTable']


import warnings, logging
import pandas as pd
import numpy as np
import functools as fts
import itertools as its

import podspy.log.constants as const

from opyenxes.model.XLog import XLog
from opyenxes.model.XTrace import XTrace
from opyenxes.model.XEvent import XEvent

from opyenxes.model.XAttributeTimestamp import XAttributeTimestamp
from opyenxes.model.XAttributeID import XAttributeID
from opyenxes.model.XAttributeBoolean import XAttributeBoolean
from opyenxes.model.XAttributeContinuous import XAttributeContinuous
from opyenxes.model.XAttributeLiteral import XAttributeLiteral
from opyenxes.model.XAttributeDiscrete import XAttributeDiscrete

from opyenxes.model.XAttributeContainer import XAttributeContainer
from opyenxes.model.XAttributeList import XAttributeList
from opyenxes.model.XAttributeMap import XAttributeMap

from opyenxes.classification.XEventAndClassifier import XEventAndClassifier
from opyenxes.extension.XExtension import XExtension

from opyenxes.extension.XExtensionManager import XExtensionManager

MANAGER = XExtensionManager()
CONCEPT_EXT = MANAGER.get_by_name('Concept')


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


# get package logger
logger = logging.getLogger('log')


class LogTable:
    # default character to separator variants
    VARIANT_SEP = '|'
    VARIANT_ID = 'variant_id'

    def __init__(self, trace_df=None, event_df=None, attributes=None,
                 global_trace_attributes=None, global_event_attributes=None,
                 classifiers=None, extensions=None, variant_sep=VARIANT_SEP,
                 variant_id=VARIANT_ID):
        ''' Container class of event data in tabular format.

        Parameters
        ----------
        trace_df: DataFrame
            DataFrame containing information of each trace in event log
        event_df: DataFrame
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
        self.trace_df = trace_df if trace_df is not None else pd.DataFrame()
        self.event_df = event_df if event_df is not None else pd.DataFrame()
        self.attributes = attributes if attributes is not None else dict()

        self.global_trace_attributes = global_trace_attributes if global_trace_attributes is not None else dict()
        self.global_event_attributes = global_event_attributes if global_event_attributes is not None else dict()
        self.xes_attributes = {'version': 2.0, 'features': []}
        self.classifiers = classifiers if classifiers is not None else dict()
        self.extensions = extensions if extensions is not None else dict()

        self.variant_sep = variant_sep
        self.variant_id = variant_id

    def get_event_identity_list(self, clf_name=None, sort=True):
        if clf_name is None or clf_name not in self.classifiers:
            keys = list(self.classifiers.keys())
            if len(keys) > 0:
                clf_name = keys[0]

        # classifier is a list of column names in event_df
        # use concept:name if there's no classifier
        if len(self.classifiers) == 0:
            warnings.warn('No classifiers! Using concept:name as event classifier!')
            clf = [const.CONCEPT_NAME]
        else:
            clf = self.classifiers[clf_name]
        subset = self.event_df[clf].drop_duplicates()

        logger.debug('Event identity columns with unique rows: \n{}'.format(subset.head(5)))
        logger.debug('Event identity columns with unique rows dtypes: \n{}'.format(subset.dtypes))

        # concat the columns if it involves more than one column
        if len(clf) == 1:
            id_list = its.chain(*subset.values.tolist())
        else:
            id_list = subset.apply(lambda row: '&&'.join(row), axis=1).tolist()

        if sort:
            id_list = sorted(id_list)

        # logging the first five for inspection purpose
        first_five = 5 if len(id_list) > 5 else len(id_list)
        logger.debug('Identity list: {}'.format(id_list[:first_five]))

        return id_list

    def get_trace_variants(self):
        ''' Allocates case ids to trace variants by their activity column

        Returns
        -------
        pd.DataFrame
            Consists two columns: caseid and variant

        '''
        # check if there are caseid and activity columns
        if const.ACTIVITY not in self.event_df.columns:
            raise ValueError('Activity column not defined in event df!')
        if const.CASEID not in self.event_df.columns:
            raise ValueError('Caseid column not defined in event df!')

        # concat events per caseid so a trace of events can be computed before using
        # groupby per trace

        # concat events per caseid to form event strings
        traces = self.event_df.groupby(const.CASEID, as_index=False)
        logger.debug('Traces: \n'.format(traces))
        traces = traces.agg({const.ACTIVITY: lambda values: self.variant_sep.join(values)})
        # rename activity column as variant
        traces.rename({const.ACTIVITY: const.VARIANT}, axis=1, inplace=True)

        # create variant ids
        variant_id = traces[[const.VARIANT]].drop_duplicates().reset_index(drop=True)
        # to get index column for creating variant ids
        variant_id = variant_id.reset_index()
        make_variant_id = lambda val: '{} {}'.format(const.VARIANT, val)
        variant_id[self.variant_id] = variant_id['index'].apply(make_variant_id)
        variant_id = variant_id[[const.VARIANT, self.variant_id]]

        # merge with traces to assign the variant id to each caseid
        variant_df = pd.merge(traces, variant_id, on=const.VARIANT)
        variant_df = variant_df[[const.CASEID, self.variant_id, const.VARIANT]]

        return variant_df


class XLogToLogTable:

    # to myself:
    # Perhaps allow this to be parallelized using multiprocessing?

    def parse_xattribute(self, xattribute):
        if isinstance(xattribute, XAttributeList) or isinstance(xattribute, XAttributeContainer) \
                or isinstance(xattribute, XAttributeMap):
            warnings.warn('Do not support parsing XAttributable of type: {}'.format(xattribute.__class__.__name__))
            return None, None
        elif isinstance(xattribute, XAttributeDiscrete) or isinstance(xattribute, XAttributeLiteral) or \
                isinstance(xattribute, XAttributeContinuous) or isinstance(xattribute, XAttributeBoolean):
            return xattribute.get_key(), xattribute.get_value()
        elif isinstance(xattribute, XAttributeID):
            # uuid4 to string
            return xattribute.get_key(), str(xattribute.get_value().get_uuid())
        elif isinstance(xattribute, XAttributeTimestamp):
            return xattribute.get_key(), xattribute.get_value()
        else:
            raise ValueError('Do not recognize XAttribute type: {}'.format(xattribute.__class__.__name__))

    def parse_xattribute_list(self, xattribute_list):
        logger.debug('Attribute list: {}'.format(xattribute_list))
        parsed = [self.parse_xattribute(a) for a in xattribute_list]
        parsed = list(filter(lambda ele: ele[0] is not None, parsed))
        logger.debug('Parsed attribute list: {}'.format(parsed))
        d = dict(parsed)
        # logger.debug('Parsed attribute dict: {}'.format(d))
        return d

    def parse_xattribute_type(self, xattribute):
        # logger.debug('Parsing XAttribute type: {}'.format(type(xattribute)))
        typemap = {
            XAttributeDiscrete.__name__: np.dtype('i8'),
            XAttributeBoolean.__name__: np.dtype('?'), # bool
            XAttributeContinuous.__name__: np.dtype('f8'),
            # assume longest string only has 4000 characters which is ~500 words
            XAttributeLiteral.__name__: np.dtype('U4000'),
            XAttributeTimestamp.__name__: np.dtype('datetime64[ns]'),
            XAttributeID.__name__: np.dtype('U40')
        }
        if isinstance(xattribute, XAttributeList) or isinstance(xattribute, XAttributeContainer) \
                or isinstance(xattribute, XAttributeMap):
            warnings.warn('Do not support parsing XAttributable of type: {}'.format(xattribute.__class__.__name__))
            return None, None
        classname = xattribute.__class__.__name__
        if classname in typemap:
            return xattribute.get_key(), typemap[classname]
        else:
            raise ValueError('Do not recognize XAttribute type: {}'.format(classname))

    def parse_xattribute_type_list(self, xattribute_list):
        # logger.debug('XAttribute list: \n{}'.format(xattribute_list))
        parsed = [self.parse_xattribute_type(a) for a in xattribute_list]
        parsed = filter(lambda ele: ele[0] is not None, parsed)
        d = dict(parsed)
        return d

    def parse_classifier(self, classifier):
        if isinstance(classifier, XEventAndClassifier):
            warnings.warn('Do not support parsing XEventAndClassifier!')
            return None, None
        else:
            return classifier.name(), classifier.get_defining_attribute_keys()

    def parse_classifier_list(self, classifier_list):
        parsed = [self.parse_classifier(c) for c in classifier_list]
        parsed = filter(lambda ele: ele[0] is not None, parsed)
        d = dict(parsed)
        return d

    def parse_extension(self, extension):
        assert isinstance(extension, XExtension)
        return extension.get_name(), extension.get_prefix(), extension.get_uri()

    def parse_extension_list(self, extension_list):
        parsed = [self.parse_extension(e) for e in extension_list]
        # using extension name as dictionary key
        d = {e[0]: e for e in parsed}
        return d

    def defaultget(self, key, d, default=None):
        return d[key] if key in d else default

    def xtraces2df(self, xtrace_list, attribute_types=None):
        if attribute_types is None:
            aux = map(lambda e: self.parse_xattribute_type_list(e.get_attributes().values()), xtrace_list)
            attribute_types = fts.reduce(lambda all, d: {**all, **d}, aux, dict())

        # create numpy array
        nb_of_traces = len(xtrace_list)
        column_order = sorted(list(attribute_types.keys()))
        dtypes = [(col, attribute_types[col]) for col in column_order]
        array = np.zeros((nb_of_traces,), dtype=dtypes)

        for ind in range(nb_of_traces):
            xtrace = xtrace_list[ind]
            assert isinstance(xtrace, XTrace)
            attributes = self.parse_xattribute_list(xtrace.get_attributes().values())
            trace_row = [self.defaultget(col, attributes, default=None) for col in column_order]
            array[ind] = tuple(trace_row)

        df = pd.DataFrame(array, columns=column_order)
        return df

    def xevents2df(self, caseid_list, xevent_list, attribute_types=None):
        if attribute_types is None:
            # using the attributes of the xevent list only
            aux = map(lambda e: self.parse_xattribute_type_list(e.get_attributes().values()), xevent_list)
            attribute_types = fts.reduce(lambda all, d: {**all, **d}, aux, dict())

        # create numpy array
        nb_of_events = len(xevent_list)
        # ascending column order
        column_order = sorted(list(attribute_types.keys()))
        dtypes = [(const.CASEID, np.dtype('U4000')), ]
        dtypes += [(col, attribute_types[col]) for col in column_order]
        logger.debug('Dtypes: {}'.format(dtypes))
        array = np.zeros((nb_of_events,), dtype=dtypes)
        logger.debug('Event array shape: {}'.format(array.shape))

        logger.debug('Attribute types: {}'.format(attribute_types))

        for ind in range(nb_of_events):
            caseid = caseid_list[ind]
            xevent = xevent_list[ind]
            assert isinstance(xevent, XEvent)
            attributes = self.parse_xattribute_list(xevent.get_attributes().values())
            event_row = [caseid, ] + [self.defaultget(col, attributes, default=None) for col in column_order]
            array[ind] = tuple(event_row)

        column_order = [const.CASEID, ] + column_order
        df = pd.DataFrame(array, columns=column_order)

        logger.debug('Event df: \n{}'.format(df.head()))

        return df

    def xlog2table(self, xlog):
        assert isinstance(xlog, XLog)

        # get the global attributes
        global_trace_attributes = self.parse_xattribute_list(xlog.get_global_trace_attributes())
        global_event_attributes = self.parse_xattribute_list(xlog.get_global_event_attributes())

        attribute_dict = self.parse_xattribute_list(xlog.get_attributes().values())
        classifier_dict = self.parse_classifier_list(xlog.get_classifiers())
        extension_dict = self.parse_extension_list(xlog.get_extensions())

        trace_df = self.xtraces2df(xlog)
        # need to repeat caseid by the number of events in trace
        caseid_list = map(lambda t: [CONCEPT_EXT.extract_name(t)] * len(t), xlog)
        caseid_list = fts.reduce(lambda all, l: all + l, caseid_list)
        xevent_list = fts.reduce(lambda all, t: all + list(t), xlog, [])
        event_df = self.xevents2df(caseid_list, xevent_list)

        log_table = LogTable(trace_df=trace_df, event_df=event_df,
                             attributes=attribute_dict,
                             global_event_attributes=global_event_attributes,
                             global_trace_attributes=global_trace_attributes,
                             classifiers=classifier_dict, extensions=extension_dict)

        return log_table

