#!/usr/bin/env python

"""This is the utils module.

This module contains useful methods for pandas df manipulation and
reading xes log files.
"""


import os, gzip, shutil, tempfile
import pandas as pd


from opyenxes.data_in.XUniversalParser import XUniversalParser
from opyenxes.factory.XFactory import XFactory

from .constants import *


def read_event_log_file(log_filepath):
    if not os.path.isfile(log_filepath):
        raise ValueError('{} is not a log file!'.format(log_filepath))

    with open(log_filepath, 'r') as f:
        logs = XUniversalParser.parse(f)
        log = logs[0]

    return log


def downcast_int_df_columns(df, inplace=True):
    downcasted = df
    if not inplace:
        downcasted = df.copy(deep=True)

    for col in downcasted.select_dtypes(include=['int']).columns:
        downcasted.loc[:,col] = downcasted[col].apply(pd.to_numeric, downcast='unsigned')

    if not inplace:
        return downcasted


def downcast_float_df_columns(df, inplace=True):
    downcasted = df
    if not inplace:
        downcasted = df.copy(deep=True)

    for col in downcasted.select_dtypes(include=['float']).columns:
        downcasted.loc[:,col] = downcasted[col].apply(pd.to_numeric, downcast='float')

    if not inplace:
        return downcasted


def threshold_categorize_str_df_columns(df, threshold=0.5, inplace=True):
    downcasted = df
    if not inplace:
        downcasted = df.copy(deep=True)

    for col in downcasted.select_dtypes(include=['object']).columns:
        nb_unique_vals = downcasted[col].unique().shape[0]
        nb_total_vals = downcasted[col].shape[0]
        if nb_unique_vals / nb_total_vals < threshold:
            downcasted.loc[:,col] = downcasted[col].astype('category')


def optimize_df_dtypes(df, threshold=0.5, inplace=True):
    downcasted = df
    if not inplace:
        downcasted = df.copy(deep=True)
    downcast_int_df_columns(downcasted, inplace)
    downcast_float_df_columns(downcasted, inplace)
    threshold_categorize_str_df_columns(downcasted, threshold, inplace)

    if not inplace:
        return downcasted


def make_xattribute(attr_type, key, value, extension):
    mapping = {
        DISCRETE: XFactory.create_attribute_discrete,
        LITERAL: XFactory.create_attribute_literal,
        CONTINUOUS: XFactory.create_attribute_continuous,
        BOOLEAN: XFactory.create_attribute_boolean,
        TIMESTAMP: XFactory.create_attribute_timestamp
    }
    
    if extension != None:
        xattribute = mapping[attr_type](key, value, extension)
    else:
        xattribute = mapping[attr_type](key, value)
        
    return xattribute


def temp_decompress(fpath):

    # create temporary file to hold the decompressed file
    prefix = fpath.split('.')[-2]
    # get a unique temporary filepath
    temp = tempfile.NamedTemporaryFile(prefix=prefix)
    temp.close()

    with gzip.open(fpath, 'rb') as f_in:
        with open(temp.name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    return temp.name
