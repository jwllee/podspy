#!/usr/bin/env python

"""This is the unit test module.

This module tests the log io module.
"""


from podspy.log import io
import pytest, uuid
from lxml import etree
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"



@pytest.fixture(ids=lambda s: s[1], params=[
    ('<classifier name="Operation" keys="Operation"/>', 'Operation', ['Operation'], dict()),
    ('<classifier name="Service Type" keys="Service Type"/>', 'Service Type', ['Service Type'], dict()),
    ('<classifier name="activity classifier" keys="Operation Service Type"/>',
     'activity classifier', ['Operation', 'Service Type'],
     {'Operation': ['Operation'], 'Service Type': ['Service Type']})
])
def classifier_elem(request):
    # need to convert it as etree element
    return etree.fromstring(request.param[0]), request.param[1], request.param[2], request.param[3]


def test_check_classifier_elem_fixture(classifier_elem):
    assert classifier_elem is not None


def test_parse_classifier_elem(classifier_elem):
    existing_clf_dict = classifier_elem[3]
    d = io.parse_classifier_elem(classifier_elem[0], existing_clf_dict)

    expected_name = classifier_elem[1]
    expected_clf_keys = classifier_elem[2]

    assert expected_name in d
    assert d[expected_name] == expected_clf_keys


@pytest.fixture(ids=lambda s: s[1], params=[
    ('<extension name="Concept" prefix="concept" uri="http://www.xes-standard.org/concept.xesext"/>',
     'Concept', 'concept', urlparse('http://www.xes-standard.org/concept.xesext')),
    ('<extension name="Lifecycle" prefix="lifecycle" uri="http://www.xes-standard.org/lifecycle.xesext"/>',
     'Lifecycle', 'lifecycle', urlparse('http://www.xes-standard.org/lifecycle.xesext')),
    ('<extension name="Organizational" prefix="org" uri="http://www.xes-standard.org/org.xesext"/>',
     'Organizational', 'org', urlparse('http://www.xes-standard.org/org.xesext')),
    ('<extension name="3TU metadata" prefix="meta_3TU" uri="http://www.xes-standard.org/meta_3TU.xesext"/>',
     '3TU metadata', 'meta_3TU', urlparse('http://www.xes-standard.org/meta_3TU.xesext'))
])
def extension_elem(request):
    return etree.fromstring(request.param[0]), request.param[1], request.param[2], request.param[3]


def test_check_extension_elem_fixture(extension_elem):
    assert extension_elem is not None


def test_parse_extension_elem(extension_elem):
    d = io.parse_extension_elem(extension_elem[0])

    expected_name = extension_elem[1]
    expected_prefix = extension_elem[2]
    expected_uri = extension_elem[3]

    assert expected_name in d
    extension = d[expected_name]
    assert extension[0] == expected_name
    assert extension[1] == expected_prefix
    assert extension[2].geturl() == expected_uri.geturl()


@pytest.fixture(ids=lambda s: s[1], params=[
    # attribute value is a list of elements
    ('<string key="AMOUNT_REQ" value="UNKNOWN"/>', 'AMOUNT_REQ', 'UNKNOWN'),
    ('<string key="concept:name" value="UNKNOWN"/>', 'concept:name', 'UNKNOWN')
])
def literal_attrib_elem(request):
    return etree.fromstring(request.param[0]), request.param[1], request.param[2]


@pytest.fixture(ids=lambda s: s[1], params=[
    ('<boolean key="IS_LATE" value="false"/>', 'IS_LATE', False),
    ('<boolean key="IS_AUTO" value="True"/>', 'IS_AUTO', True)
])
def bool_attrib_elem(request):
    return etree.fromstring(request.param[0]), request.param[1], request.param[2]


@pytest.fixture(ids=lambda s: s[1], params=[
    ('<int key="meta_general:events_max" value="175"/>', 'meta_general:events_max', 175),
    ('<int key="O_ACCEPTED" value="2243"/>', 'O_ACCEPTED', 2243)
])
def discrete_attrib_elem(request):
    return etree.fromstring(request.param[0]), request.param[1], request.param[2]


@pytest.fixture(ids=lambda s: s[1], params=[
    ('<float key="O_ACCEPTED" value="0.171"/>', 'O_ACCEPTED', 0.171),
    ('<float key="A_ACCEPTED" value="0.391"/>', 'A_ACCEPTED', 0.391)
])
def continuous_attrib_elem(request):
    return etree.fromstring(request.param[0]), request.param[1], request.param[2]


@pytest.fixture(ids=lambda s: s[1], params=[
    ('<id key="CASEID" value="02f4ab28-7b3e-492c-933b-12ee0461643a"/>', 'CASEID',
     uuid.UUID('02f4ab28-7b3e-492c-933b-12ee0461643a')),
    ('<id key="RESOURCEID" value="78ebba5e-8ff2-4cf4-b442-d2fa2b999182"/>', 'RESOURCEID',
     uuid.UUID('78ebba5e-8ff2-4cf4-b442-d2fa2b999182'))
])
def id_attrib_elem(request):
    return etree.fromstring(request.param[0]), request.param[1], request.param[2]


@pytest.fixture(ids=lambda s: s[1], params=[
    ('<date key="REG_DATE" value="1970-01-01T00:00:00.000+01:00"/>', 'REG_DATE',
     datetime.strptime('1970-01-01T00:00:00.000', '%Y-%m-%dT%H:%M:%S.%f').replace(
         tzinfo=timezone(timedelta(hours=1))
     )),

    ('<date key="time:timestamp" value="1970-01-01T00:00:00.000+01:00"/>', 'time:timestamp',
     datetime.strptime('1970-01-01T00:00:00.000', '%Y-%m-%dT%H:%M:%S.%f').replace(
         tzinfo=timezone(timedelta(hours=1))
     ))
])
def timestamp_attrib_elem(request):
    return etree.fromstring(request.param[0]), request.param[1], request.param[2]


def test_parse_literal_attrib_elem(literal_attrib_elem):
    parsed = io.parse_literal_attrib_elem(literal_attrib_elem[0])

    expected_key = literal_attrib_elem[1]
    expected_val = literal_attrib_elem[2]

    assert len(parsed) == 2
    assert parsed[0] == expected_key
    assert parsed[1] == expected_val


def test_parse_bool_attrib_elem(bool_attrib_elem):
    parsed = io.parse_bool_attrib_elem(bool_attrib_elem[0])

    expected_key = bool_attrib_elem[1]
    expected_val = bool_attrib_elem[2]

    assert len(parsed) == 2
    assert parsed[0] == expected_key
    assert parsed[1] == expected_val


def test_parse_discrete_attrib_elem(discrete_attrib_elem):
    parsed = io.parse_discrete_attrib_elem(discrete_attrib_elem[0])

    expected_key = discrete_attrib_elem[1]
    expected_val = discrete_attrib_elem[2]

    assert len(parsed) == 2
    assert parsed[0] == expected_key
    assert parsed[1] == expected_val


def test_parse_continuous_attrib_elem(continuous_attrib_elem):
    parsed = io.parse_continuous_attrib_elem(continuous_attrib_elem[0])

    expected_key = continuous_attrib_elem[1]
    expected_val = continuous_attrib_elem[2]

    assert len(parsed) == 2
    assert parsed[0] == expected_key
    assert parsed[1] == expected_val


def test_parse_id_attrib_elem(id_attrib_elem):
    parsed = io.parse_id_attrib_elem(id_attrib_elem[0])

    expected_key = id_attrib_elem[1]
    expected_val = id_attrib_elem[2]

    assert len(parsed) == 2
    assert parsed[0] == expected_key
    assert parsed[1] == expected_val


def test_parse_timestamp_attrib_elem(timestamp_attrib_elem):
    parsed = io.parse_timestamp_attrib_elem(timestamp_attrib_elem[0])

    expected_key = timestamp_attrib_elem[1]
    expected_val = timestamp_attrib_elem[2]

    assert len(parsed) == 2
    assert parsed[0] == expected_key
    assert parsed[1] == expected_val


@pytest.fixture
def global_trace_attrib():
    string = '<global scope="trace">' \
                 '<date key="REG_DATE" value="1970-01-01T00:00:00.000+01:00"/>' \
                 '<string key="AMOUNT_REQ" value="UNKNOWN"/>' \
                 '<string key="concept:name" value="UNKNOWN"/>' \
             '</global>'
    expected_scope = 'trace'
    expected_attrib_dict = {
        'REG_DATE': datetime.strptime('1970-01-01T00:00:00.000', '%Y-%m-%dT%H:%M:%S.%f').replace(
                tzinfo=timezone(timedelta(hours=1))),
        'AMOUNT_REQ': 'UNKNOWN',
        'concept:name': 'UNKNOWN'
    }

    return etree.fromstring(string), expected_scope, expected_attrib_dict


@pytest.fixture
def global_event_attrib():
    string = '<global scope="event">' \
                 '<date key="time:timestamp" value="1970-01-01T00:00:00.000+01:00"/>' \
                 '<string key="lifecycle:transition" value="UNKNOWN"/>' \
                 '<string key="concept:name" value="UNKNOWN"/>' \
             '</global>'
    expected_scope = 'event'
    expected_attrib_dict = {
        'time:timestamp': datetime.strptime('1970-01-01T00:00:00.000', '%Y-%m-%dT%H:%M:%S.%f').replace(
                tzinfo=timezone(timedelta(hours=1))),
        'lifecycle:transition': 'UNKNOWN',
        'concept:name': 'UNKNOWN'
    }

    return etree.fromstring(string), expected_scope, expected_attrib_dict


def test_parse_global_trace_attrib(global_trace_attrib):
    parsed = io.parse_global_attrib_elem(global_trace_attrib[0])

    assert len(parsed) == 2
    assert parsed[0] == global_trace_attrib[1]
    assert parsed[1] == global_trace_attrib[2]


def test_parse_global_event_attrib(global_event_attrib):
    parsed = io.parse_global_attrib_elem(global_event_attrib[0])

    assert len(parsed) == 2
    assert parsed[0] == global_event_attrib[1]
    assert parsed[1] == global_event_attrib[2]


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
def xevent(request):
    return etree.fromstring(request.param[0]), request.param[1]


def test_parse_event_elem(xevent):
    parsed = io.parse_event_elem(xevent[0])

    assert isinstance(parsed, pd.Series)
    dict_val = parsed.to_dict()
    assert dict_val == xevent[1]


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
         'concept:name': ['A_SUBMITTED', 'A_DECLINED'],
         'lifecycle:transition': ['COMPLETE', np.nan]
    })
])
def xtrace(request):
    return etree.fromstring(request.param[0]), request.param[1], request.param[2]


def test_parse_xtrace_elem(xtrace):
    parsed = io.parse_trace_elem(xtrace[0])

    assert len(parsed) == 2

    trace_row = parsed[0]
    event_df = parsed[1]

    assert isinstance(trace_row, pd.Series)
    assert isinstance(event_df, pd.DataFrame)

    trace_row_dict = trace_row.to_dict()
    assert trace_row_dict == xtrace[1]

    event_df_dict = event_df.to_dict(orient='list')
    assert event_df_dict == xtrace[2]
