#!/usr/bin/env python

"""This is the test module for the factory module of the log package.

"""
import pytest, os, sys, time
from opyenxes.utils.XAttributeUtils import XAttributeType as atype
from opyenxes.factory.XFactory import XFactory
from opyenxes.data_in.XUniversalParser import XUniversalParser
import datetime as dt

from podspy.log import factory as fty


atype_factory_map = {
    atype.DISCRETE: XFactory.create_attribute_discrete,
    atype.LITERAL: XFactory.create_attribute_literal,
    atype.CONTINUOUS: XFactory.create_attribute_continuous,
    atype.BOOLEAN: XFactory.create_attribute_boolean,
    atype.ID: XFactory.create_attribute_id,
    atype.LIST: XFactory.create_attribute_list,
    atype.CONTAINER: XFactory.create_attribute_container,
    atype.TIMESTAMP: XFactory.create_attribute_timestamp
}


@pytest.fixture(
    params=[
        # type, key, value
        (atype.DISCRETE, 'priority', 1),
        (atype.LITERAL, 'gender', 'female'),
        (atype.CONTINUOUS, 'cost', 100.),
        (atype.BOOLEAN, 'is_urgent', True),
        (atype.ID, 'RUT', '1234'),
        (atype.LIST, 'things', ['thing0', 'thing1', 'thing3']),
        (atype.CONTAINER, 'unicode', {'a': 97, 'b': 98, 'c': 99}),
        (atype.TIMESTAMP, 'sent_date', dt.datetime(2018, 1, 1, 1, 1, 1)),
    ]
)
def xattrib(request):
    _type, key, val = request.param
    attrib = atype_factory_map[_type](key, val)
    return attrib, _type, key, val


@pytest.fixture
def xlog():
    xlog_fp = os.path.join('.', 'tests', 'testdata', 'BPIC2012.xes.gz')
    start = time.time()
    with open(xlog_fp, 'r') as f:
        xlog = XUniversalParser.parse(f)[0]
        size = sys.getsizeof(xlog)
        print('BPIC2012 XLog size: {}b'.format(size))
    diff = time.time() - start
    print('Took {} secs to parse BPIC2012'.format(diff))
    return xlog


class TestXLog2LogTable:
    def test_parse_xattribute(self, xattrib):
        attrib, _type, expected_key, expected_val = xattrib
        key, val, ext = fty.XLog2LogTable().parse_xattribute(attrib)

        if not (_type == atype.LIST or _type == atype.CONTAINER):
            assert key == expected_key
            assert val == expected_val
        else:
            assert key is None
            assert val is None

    @pytest.mark.slowtest
    def test_xlog2table(self, xlog):
        start = time.time()
        lt = fty.XLog2LogTable().xlog2table(xlog)
        size = sys.getsizeof(lt)
        diff = time.time() - start
        print('Took {} secs to convert'.format(diff))
        print('Size of LogTable: {}b'.format(size))
