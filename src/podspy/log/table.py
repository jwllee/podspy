#!/usr/bin/env python

"""This is the log table module.

This module contains the LogTable class.
"""

__all__ = [
    'LogTable'
]


import warnings, logging
import pandas as pd
import numpy as np
import functools as fts
import itertools as its

from . import constants as const

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
        """Container class of event data in dataframe format.

        :param trace_df: dataframe containing information of each trace in event log
        :param event_df: dataframe containing information of each event in event log
        :param attributes: dictionary containing attributes on the log level
        :param global_trace_attributes: dictionary containing global trace attributes
        :param global_event_attributes: dictionary containing global event attributes
        :param classifiers: classifiers to give identities to event corresponding to a sub-list
            of the global event attributes
        :param extensions: extensions to give semantics to attributes, e.g., the concept extension.
            Each extension consisting of (name, prefix, uri)
        :param variant_sep: separator of events for variant strings
        :param variant_id: variant id column name
        """
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
        """Get the unique event identities using given classifier

        :param clf_name: classifier name
        :param sort: whether to sort the event identities
        :return: a list of event identities
        """
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
        """Allocate case ids to trace variants by their activity column

        :return: dataframe consisting of caseid and variant columns
        """
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

