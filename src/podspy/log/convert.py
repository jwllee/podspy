#!/usr/bin/env python

"""This is the convert module.

This module convert between different representation of event data.
"""


import logging


from . import utils
from .storage import *
from .constant import *


from opyenxes.factory.XFactory import XFactory


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = ['EventStorageToXESConverter']


logger = logging.getLogger('log')


class EventStorageToXESConverter:
    
    def __trace_row_to_xtrace(self, row, trace_attributes):
        logger.debug('Trace df row: {}'.format(row))
        
        xtrace = XFactory.create_trace()
        
        # trace attribute tuple should consist of:
        # 1) attribute type name
        # 2) attribute name (as key at XTrace's attributes)
        # 3) XAttribute key
        # 4) XAttribute XExtension (if any)
        for type_name, name, key, extension in trace_attributes:
            value = row[key]
            xattribute = utils.make_xattribute(type_name, key, value, extension)
            xtrace.get_attributes()[name] = xattribute
        
        return xtrace
    
    def __event_row_to_xevent(self, row, event_attributes):
        xevent = XFactory.create_event()
        
        # same as trace attributes
        for type_name, name, key, extension in event_attributes:
            value = row[key]
            xattribute = utils.make_xattribute(type_name, key, value, extension)
            xevent.get_attributes()[name] = xattribute
            
        return xevent
    
    def event_storage_to_xes(self, storage):
        if not isinstance(storage, EventStorage):
            raise ValueError('{} not an {}'.format(type(storage).__name__, 
                                                   EventStorage.__name__))
        
        xlog = XFactory.create_log()
        
        for row in storage.log_attributes:
            xattribute = utils.make_xattribute(
                row[0], row[2], row[3], row[4]
            )
            name = row[1]
            xlog.get_attributes()[name] = xattribute
            
        xtrace_list = storage.trace_df.apply(
            lambda row: self.__trace_row_to_xtrace(row, storage.trace_attributes), axis=1
        )
        
        for xtrace in xtrace_list:
            caseid = xtrace.get_attributes()['concept:name'].get_value()
            
            xtrace_events = storage.event_df[
                (storage.event_df[CASEID] == caseid)
            ]
            
            logger.debug('Number of events of caseid {}: {}'.format(caseid, 
                                                                    xtrace_events.shape[0]))
            
            xevent_list = xtrace_events.apply(
                lambda row: self.__event_row_to_xevent(row, storage.event_attributes), axis=1
            )
            
            xtrace += xevent_list
            
            xlog.append(xtrace)
            
        return xlog
