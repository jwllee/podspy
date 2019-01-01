#!/usr/bin/env python

"""This is the test module.

This module test io module
"""


import pytest, time, os, sys
from datetime import datetime, timedelta, timezone
from urllib.request import urlparse
import numpy as np
from lxml import etree

from podspy.log import constants, data_io
from podspy.log import table as tble


@pytest.fixture(ids=lambda s: str(s[1]), params=[
    # event 0
    ('<event>'
     '<int key="org:resource" value="112"/>'
     '<string key="lifecycle:transition" value="COMPLETE"/>'
     '<string key="concept:name" value="A_SUBMITTED"/>'
     '</event>', {
         'org:resource': 112, 'lifecycle:transition': 'COMPLETE', 'concept:name': 'A_SUBMITTED'
     }),
    # event 1
    ('<event>'
     '<int key="org:resource" value="100"/>'
     '<string key="lifecycle:transition" value="START"/>'
     '<string key="concept:name" value="O_SENT"/>'
     '</event>', {
         'org:resource': 100, 'lifecycle:transition': 'START', 'concept:name': 'O_SENT'
     })
])
def xevent_xml(request):
    return request.param


@pytest.fixture(ids=lambda s: str(s[1]), params=[
    # trace 0
    ('<trace>'
         '<date key="REG_DATE" value="2011-10-01T08:10:30.287+02:00"/>'
         '<string key="concept:name" value="173694"/>'
         '<string key="AMOUNT_REQ" value="7000"/>'
         '<event>'
             '<string key="concept:name" value="A_SUBMITTED"/>'
             '<string key="lifecycle:transition" value="COMPLETE"/>'
         '</event>'
         '<event>'
             '<string key="concept:name" value="A_PARTLYSUBMITTED"/>'
         '</event>'
         '<event>'
             '<string key="concept:name" value="A_ACCEPTED"/>'
         '</event>'
     '</trace>',
     {
         'REG_DATE': datetime.strptime('2011-10-01T08:10:30.287', '%Y-%m-%dT%H:%M:%S.%f').replace(
             tzinfo=timezone(timedelta(hours=2))),
         'concept:name': '173694',
         'AMOUNT_REQ': '7000'
     },
     # check using df.to_dict(orient='list')
     {
         constants.CASEID: ['173694', '173694', '173694'],
         'concept:name': ['A_SUBMITTED', 'A_PARTLYSUBMITTED', 'A_ACCEPTED'],
         'lifecycle:transition': ['COMPLETE', np.nan, np.nan]
     }),
    # trace 1
    ('<trace>'
         '<date key="REG_DATE" value="2011-10-01T08:11:08.865+02:00"/>'
         '<string key="concept:name" value="173697"/>'
         '<string key="AMOUNT_REQ" value="15000"/>'
         '<event>'
             '<string key="concept:name" value="A_SUBMITTED"/>'
             '<string key="lifecycle:transition" value="COMPLETE"/>'
         '</event>'
         '<event>'
             '<string key="concept:name" value="A_DECLINED"/>'
         '</event>'
     '</trace>',
     {
         'REG_DATE': datetime.strptime('2011-10-01T08:11:08.865', '%Y-%m-%dT%H:%M:%S.%f').replace(
             tzinfo=timezone(timedelta(hours=2))),
         'concept:name': '173697',
         'AMOUNT_REQ': '15000'
     },
     {
         constants.CASEID: ['173697', '173697'],
         'concept:name': ['A_SUBMITTED', 'A_DECLINED'],
         'lifecycle:transition': ['COMPLETE', np.nan]
     })
])
def xtrace_xml(request):
    return request.param


@pytest.fixture(ids=lambda s: str(s[1]), params=[
    # trace 0
    (
    '<log xes.version="1.0" xes.features="nested-attributes" openxes.version="1.0RC7" xmlns="http://www.xes-standard.org/">'
        '<extension name="Lifecycle" prefix="lifecycle" uri="http://www.xes-standard.org/lifecycle.xesext"/>'
        '<extension name="Time" prefix="time" uri="http://www.xes-standard.org/time.xesext"/>'
        '<global scope="trace">'
            '<date key="REG_DATE" value="1970-01-01T00:00:00.000+01:00"/>'
            '<string key="concept:name" value="UNKNOWN"/>'
        '</global>'
        '<global scope="event">'
            '<date key="time:timestamp" value="1970-01-01T00:00:00.000+01:00"/>'
            '<string key="concept:name" value="UNKNOWN"/>'
            '<string key="lifecycle:transition" value="UNKNOWN"/>'
        '</global>'
        '<classifier name="Activity classifier" keys="concept:name lifecycle:transition"/>'
        '<classifier name="Resource classifier" keys="org:resource"/>'
        '<string key="meta_3TU:log_type" value="Real-life"/>'
        '<float key="meta_concept:different_names_standard_deviation" value="5.554"/>'
        '<int key="meta_org:different_groups_total" value="1"/>'
        '<trace>'
            '<string key="concept:name" value="173694"/>'
            '<string key="AMOUNT_REQ" value="7000"/>'
            '<event>'
                '<string key="concept:name" value="A_SUBMITTED"/>'
                '<string key="lifecycle:transition" value="COMPLETE"/>'
            '</event>'
            '<event>'
                '<string key="concept:name" value="A_PARTLYSUBMITTED"/>'
            '</event>'
            '<event>'
                '<string key="concept:name" value="A_ACCEPTED"/>'
            '</event>'
        '</trace>'
        '<trace>'
            '<string key="concept:name" value="173697"/>'
            '<string key="AMOUNT_REQ" value="15000"/>'
            '<event>'
                '<string key="concept:name" value="A_SUBMITTED"/>'
                '<string key="lifecycle:transition" value="COMPLETE"/>'
            '</event>'
            '<event>'
                '<string key="concept:name" value="A_DECLINED"/>'
            '</event>'
        '</trace>'
    '</log>',
    (
        # xes attributes
        {
            'xes.version':'1.0',
            'xes.features':'nested-attributes',
            'openxes.version':'1.0RC7',
            # 'xmlns':'http://www.xes-standard.org'
        },
        # extension
        {
            'Lifecycle': ('Lifecycle', 'lifecycle', urlparse('http://www.xes-standard.org/lifecycle.xesext')),
            'Time': ('Time', 'time', urlparse('http://www.xes-standard.org/time.xesext'))
        },
        # classifiers
        {
            'Activity classifier': ['concept:name', 'lifecycle:transition'],
            'Resource classifier': ['org:resource']
        },
        # attributes
        {
            'meta_3TU:log_type': 'Real-life',
            'meta_concept:different_names_standard_deviation': 5.554,
            'meta_org:different_groups_total': 1
        },
        # global trace attributes
        {
            'REG_DATE': datetime.strptime('1970-01-01T00:00:00.000', '%Y-%m-%dT%H:%M:%S.%f').replace(
                tzinfo=timezone(timedelta(hours=1))),
            'concept:name': 'UNKNOWN'
        },
        # global event attributes
        {
            'time:timestamp': datetime.strptime('1970-01-01T00:00:00.000', '%Y-%m-%dT%H:%M:%S.%f').replace(
                tzinfo=timezone(timedelta(hours=1))),
            'concept:name': 'UNKNOWN',
            'lifecycle:transition': 'UNKNOWN'
        },
        # trace df
        {
            'concept:name': ['173694', '173697'],
            'AMOUNT_REQ': ['7000', '15000']
        },
        # event df
        {
            constants.CASEID: ['173694', '173694', '173694', '173697', '173697'],
            'concept:name': ['A_SUBMITTED', 'A_PARTLYSUBMITTED', 'A_ACCEPTED',
                             'A_SUBMITTED', 'A_DECLINED'],
            'lifecycle:transition': ['COMPLETE', np.nan, np.nan, 'COMPLETE', np.nan]
        }
    )
)])
def xlog_xml(request):
    return request.param


def test_feed_parser_interface(xlog_xml):
    parser = etree.XMLParser(target=data_io.LogTableTarget())
    parser.feed(xlog_xml[0])
    parser.close()


def test_parse_log_xml(xlog_xml):
    parser = etree.XMLParser(target=data_io.LogTableTarget())
    parser.feed(xlog_xml[0])
    lt = parser.close()

    assert isinstance(lt, tble.LogTable)

    xes_attribs = lt.xes_attributes
    extensions = lt.extensions
    classifiers = lt.classifiers
    global_trace_attrib = lt.global_trace_attributes
    global_event_attrib = lt.global_event_attributes
    attribs = lt.attributes

    trace_df = lt.trace_df
    trace_df_dict = trace_df.to_dict(orient='list')

    event_df = lt.event_df
    event_df_dict = event_df.to_dict(orient='list')

    expected_xes_attribs = xlog_xml[1][0]
    expected_extensions = xlog_xml[1][1]
    expected_classifiers = xlog_xml[1][2]
    expected_attribs = xlog_xml[1][3]
    expected_global_trace_attribs = xlog_xml[1][4]
    expected_global_event_attribs = xlog_xml[1][5]
    expected_trace_df_dict = xlog_xml[1][6]
    expected_event_df_dict = xlog_xml[1][7]

    assert xes_attribs == expected_xes_attribs
    assert extensions == expected_extensions
    assert classifiers == expected_classifiers
    assert attribs == expected_attribs
    assert global_trace_attrib == expected_global_trace_attribs
    assert global_event_attrib == expected_global_event_attribs
    assert trace_df_dict == expected_trace_df_dict
    assert event_df_dict == expected_event_df_dict


def test_time_parse_log_xml(xlog_xml):
    parser = etree.XMLParser(target=data_io.LogTableTarget())
    start = time.time()
    parser.feed(xlog_xml[0])
    lt = parser.close()
    diff = time.time() - start

    print('Parsing log XML took {} seconds'.format(diff))

    assert isinstance(lt, tble.LogTable)
    # assert 1 == 0


# def test_time_parse_BPIC2012():
#     parser = etree.XMLParser(target=data_in.LogTableTarget())
#     start = time.time()
#     log_file = os.path.join('.', 'tests', 'testdata', 'BPIC2012.xes.gz')
#     lt = etree.parse(log_file, parser)
#     diff = time.time() - start
#
#     print('Parsing BPIC2012 took {} seconds'.format(diff))
#
#     assert isinstance(lt, tble.LogTable)


@pytest.mark.slowtest
def test_time_parse_BPIC2018():
    log_file = os.path.join('.', 'tests', 'testdata', 'BPIC2018.xes.gz')
    lt = data_io.import_log_table(log_file)
    print('Log table is {}b'.format(sys.getsizeof(lt)))
