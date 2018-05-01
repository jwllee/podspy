#!/usr/bin/env python


import pytest


from podspy.log.storage import *
from podspy.log.convert import *

from opyenxes.model.XTrace import XTrace
from opyenxes.model.XEvent import XEvent

__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def simple_test():
    assert 1 + 1 == 2


def test_convert_storage_to_xlog(an_xlog):
    factory = EventStorageFactory()
    storage = factory.xes2storage(an_xlog)
    
    converter = EventStorageToXESConverter()
    
    xlog = converter.event_storage_to_xes(storage)
    
    assert len(an_xlog) == len(xlog)
    
    for xtrace, expected_xtrace in zip(xlog, an_xlog):
        assert isinstance(xtrace, XTrace)
        
        for name, xattribute in xtrace.get_attributes().items():
            assert name in expected_xtrace.get_attributes()
            expected_xattribute = xtrace.get_attributes()[name]
            assert xattribute == expected_xattribute
        
        for xevent, expected_xevent in zip(xtrace, expected_xtrace):
            assert isinstance(xevent, XEvent)
            
            for name, xattribute in xevent.get_attributes().items():
                assert name in expected_xevent.get_attributes()
                expected_xattribute = xevent.get_attributes()[name]
                assert xattribute == expected_xattribute
            
            


