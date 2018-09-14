#!/usr/bin/env python


from datetime import datetime as dt
import pandas as pd
import pytest
import functools as fts
import itertools as its

from podspy.log.table import LogTable
import podspy.log.constants as const

from opyenxes.factory.XFactory import XFactory
from opyenxes.model.XAttributable import XAttributable
from opyenxes.extension.XExtensionManager import XExtensionManager
from opyenxes.utils.XAttributeUtils import XAttributeType, XAttributeUtils
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
from opyenxes.classification.XEventAndClassifier import XEventAndClassifier
from opyenxes.classification.XEventLifeTransClassifier import XEventLifeTransClassifier

EXTENSION_MANAGER = XExtensionManager()
CONCEPT_EXTENSION = EXTENSION_MANAGER.get_by_name('Concept')
TIME_EXTENSION = EXTENSION_MANAGER.get_by_name('Time')
COST_EXTENSION = EXTENSION_MANAGER.get_by_name('Cost')
LIFECYCLE_EXTENSION = EXTENSION_MANAGER.get_by_name('Lifecycle')
ORG_EXTENSION = EXTENSION_MANAGER.get_by_name('Organizational')


LOG_ATTRIBUTES = [
    (XAttributeType.LITERAL.name, 'concept:name', None),
    (XAttributeType.CONTINUOUS.name, 'total_time', None)
]

LOG_ATTRIBUTE_DICT = {
    'concept:name': 'Test log',
    'total_time': 100
}


TRACE_ATTRIBUTES = [
    (XAttributeType.LITERAL.name, 'concept:name', None),
    (XAttributeType.CONTINUOUS.name, 'cost:total', None)
]

TRACE_ATTRIBUTE_DICT = {
    'concept:name': '',
    'cost:total': 1.
}


EVENT_ATTRIBUTES = [
    (XAttributeType.LITERAL.name, 'concept:name', None),
    (XAttributeType.CONTINUOUS.name, 'cost:unit', None),
    (XAttributeType.LITERAL.name, 'lifecyle:transition', None),
    (XAttributeType.LITERAL.name, 'org:group', None),
    (XAttributeType.TIMESTAMP.name, 'time:timestamp', None)
]

EVENT_ATTRIBUTE_DICT = {
    'concept:name': '',
    'cost:unit': 1.,
    'lifecycle:transition': 'complete',
    'org:group': '',
    'time:timestamp': dt.now()
}


# column order:
#   3) concept:name
#   4) cost:unit
#   5) lifecyle:transition
#   6) org:group
#   7) time:timestamp
EVENT_DF_COLUMNS = [const.CASEID, const.CONCEPT_NAME,
                    const.COST_AMOUNT, const.LIFECYCLE_TRANS,
                    const.ORG_GROUP, const.TIME_TIMESTAMP]

EVENTS = [
    # caseid: 1
    ['1', 'Check stock availability', 1.0, 'start', 'warehouse', dt(year=2017, month=1, day=1, hour=8, minute=0, second=0)],
    ['1', 'Check stock availability', 1.0, 'complete', 'warehouse', dt(year=2017, month=1, day=1, hour=8, minute=0, second=0)],
    ['1', 'Retrieve product from warehouse', 1.0, 'start', 'transport', dt(year=2017, month=1, day=2, hour=8, minute=0, second=0)],
    ['1', 'Retrieve product from warehouse', 1.0, 'complete', 'transport', dt(year=2017, month=1, day=2, hour=15, minute=0, second=0)],
    ['1', 'Confirm order', 1.0, 'start', 'sales', dt(year=2017, month=1, day=3, hour=8, minute=0, second=0)],
    ['1', 'Confirm order', 1.0, 'complete', 'sales', dt(year=2017, month=1, day=3, hour=8, minute=0, second=0)],
    ['1', 'Get shipping address', 1.0, 'start', 'sales', dt(year=2017, month=1, day=3, hour=12, minute=0, second=0)],
    ['1', 'Get shipping address', 1.0, 'complete', 'sales', dt(year=2017, month=1, day=3, hour=12, minute=10, second=0)],
    ['1', 'Ship product', 1.0, 'start', 'transport', dt(year=2017, month=1, day=4, hour=8, minute=0, second=0)],
    ['1', 'Ship product', 100.0, 'complete', 'transport', dt(year=2017, month=1, day=4, hour=15, minute=0, second=0)],
    ['1', 'Emit invoice', 1.0, 'start', 'sales', dt(year=2017, month=1, day=3, hour=12, minute=15, second=0)],
    ['1', 'Emit invoice', 1.0, 'complete', 'sales', dt(year=2017, month=1, day=3, hour=12, minute=15, second=0)],
    ['1', 'Receive payment', 1.0, 'start', 'sales', dt(year=2017, month=1, day=5, hour=8, minute=0, second=0)],
    ['1', 'Receive payment', 1.0, 'complete', 'sales', dt(year=2017, month=1, day=5, hour=8, minute=0, second=0)],
    ['1', 'Archive order', 1.0, 'start', 'sales', dt(year=2017, month=1, day=5, hour=8, minute=10, second=0)],
    ['1', 'Archive order', 1.0, 'complete', 'sales', dt(year=2017, month=1, day=5, hour=8, minute=15, second=0)],
    # case id: 2
    ['2', 'Check stock availability', 1.0, 'start', 'warehouse', dt(year=2017, month=2, day=1, hour=8, minute=0, second=0)],
    ['2', 'Check stock availability', 1.0, 'complete', 'warehouse', dt(year=2017, month=2, day=1, hour=8, minute=0, second=0)],
    ['2', 'Retrieve product from warehouse', 1.0, 'start', 'transport', dt(year=2017, month=2, day=2, hour=8, minute=0, second=0)],
    ['2', 'Retrieve product from warehouse', 1.0, 'complete', 'transport', dt(year=2017, month=2, day=2, hour=15, minute=0, second=0)],
    ['2', 'Check raw materials availability', 1.0, 'start', 'warehouse', dt(year=2017, month=2, day=3, hour=8, minute=0, second=0)],
    ['2', 'Check raw materials availability', 1.0, 'complete', 'warehouse', dt(year=2017, month=2, day=3, hour=8, minute=30, second=0)],
    ['2', 'Request raw materials from supplier 1', 1.0, 'start', 'warehouse', dt(year=2017, month=2, day=3, hour=9, minute=0, second=0)],
    ['2', 'Request raw materials from supplier 1', 1.0, 'complete', 'warehouse', dt(year=2017, month=2, day=3, hour=9, minute=5, second=0)],
    ['2', 'Obtain raw materials from supplier 1', 1.0, 'start', 'warehouse', dt(year=2017, month=2, day=5, hour=8, minute=5, second=0)],
    ['2', 'Obtain raw materials from supplier 1', 200.0, 'complete', 'warehouse', dt(year=2017, month=2, day=5, hour=8, minute=5, second=0)],
    ['2', 'Manufacture product', 1.0, 'start', 'manufacture', dt(year=2017, month=2, day=6, hour=8, minute=0, second=0)],
    ['2', 'Manufacture product', 1000.0, 'complete', 'manufacture', dt(year=2017, month=2, day=14, hour=8, minute=0, second=0)],
    ['2', 'Get shipping address', 1.0, 'start', 'sales', dt(year=2017, month=2, day=15, hour=12, minute=0, second=0)],
    ['2', 'Get shipping address', 1.0, 'complete', 'sales', dt(year=2017, month=2, day=15, hour=12, minute=10, second=0)],
    ['2', 'Ship product', 1.0, 'start', 'transport', dt(year=2017, month=2, day=16, hour=8, minute=0, second=0)],
    ['2', 'Ship product', 100.0, 'complete', 'transport', dt(year=2017, month=2, day=16, hour=15, minute=0, second=0)],
    ['2', 'Emit invoice', 1.0, 'start', 'sales', dt(year=2017, month=2, day=15, hour=12, minute=15, second=0)],
    ['2', 'Emit invoice', 1.0, 'complete', 'sales', dt(year=2017, month=2, day=15, hour=12, minute=15, second=0)],
    ['2', 'Receive payment', 1.0, 'start', 'sales', dt(year=2017, month=2, day=17, hour=8, minute=0, second=0)],
    ['2', 'Receive payment', 1.0, 'complete', 'sales', dt(year=2017, month=2, day=17, hour=8, minute=0, second=0)],
    ['2', 'Archive order', 1.0, 'start', 'sales', dt(year=2017, month=2, day=17, hour=8, minute=10, second=0)],
    ['2', 'Archive order', 1.0, 'complete', 'sales', dt(year=2017, month=2, day=17, hour=8, minute=15, second=0)],
    # case id: 3
    ['3', 'Check stock availability', 1.0, 'start', 'warehouse', dt(year=2017, month=3, day=1, hour=8, minute=0, second=0)],
    ['3', 'Check stock availability', 1.0, 'complete', 'warehouse', dt(year=2017, month=3, day=1, hour=8, minute=0, second=0)],
    ['3', 'Retrieve product from warehouse', 1.0, 'start', 'transport', dt(year=2017, month=3, day=2, hour=8, minute=0, second=0)],
    ['3', 'Retrieve product from warehouse', 1.0, 'complete', 'transport', dt(year=2017, month=3, day=2, hour=15, minute=0, second=0)],
    ['3', 'Check raw materials availability', 1.0, 'start', 'warehouse', dt(year=2017, month=3, day=3, hour=8, minute=0, second=0)],
    ['3', 'Check raw materials availability', 1.0, 'complete', 'warehouse', dt(year=2017, month=3, day=3, hour=8, minute=30, second=0)],
    ['3', 'Request raw materials from supplier 2', 1.0, 'start', 'warehouse', dt(year=2017, month=3, day=3, hour=9, minute=0, second=0)],
    ['3', 'Request raw materials from supplier 2', 1.0, 'complete', 'warehouse', dt(year=2017, month=3, day=3, hour=9, minute=5, second=0)],
    ['3', 'Obtain raw materials from supplier 2', 1.0, 'start', 'warehouse', dt(year=2017, month=3, day=5, hour=8, minute=5, second=0)],
    ['3', 'Obtain raw materials from supplier 2', 300.0, 'complete', 'warehouse', dt(year=2017, month=3, day=5, hour=8, minute=5, second=0)],
    ['3', 'Manufacture product', 1.0, 'start', 'manufacture', dt(year=2017, month=3, day=6, hour=8, minute=0, second=0)],
    ['3', 'Manufacture product', 1000.0, 'complete', 'manufacture', dt(year=2017, month=3, day=14, hour=8, minute=0, second=0)],
    ['3', 'Get shipping address', 1.0, 'start', 'sales', dt(year=2017, month=3, day=15, hour=12, minute=0, second=0)],
    ['3', 'Get shipping address', 1.0, 'complete', 'sales', dt(year=2017, month=3, day=15, hour=12, minute=10, second=0)],
    ['3', 'Ship product', 1.0, 'start', 'transport', dt(year=2017, month=3, day=16, hour=8, minute=0, second=0)],
    ['3', 'Ship product', 100.0, 'complete', 'transport', dt(year=2017, month=3, day=16, hour=15, minute=0, second=0)],
    ['3', 'Emit invoice', 1.0, 'start', 'sales', dt(year=2017, month=3, day=15, hour=12, minute=15, second=0)],
    ['3', 'Emit invoice', 1.0, 'complete', 'sales', dt(year=2017, month=3, day=15, hour=12, minute=15, second=0)],
    ['3', 'Receive payment', 1.0, 'start', 'sales', dt(year=2017, month=3, day=17, hour=8, minute=0, second=0)],
    ['3', 'Receive payment', 1.0, 'complete', 'sales', dt(year=2017, month=3, day=17, hour=8, minute=0, second=0)],
    ['3', 'Archive order', 1.0, 'start', 'sales', dt(year=2017, month=3, day=17, hour=8, minute=10, second=0)],
    ['3', 'Archive order', 1.0, 'complete', 'sales', dt(year=2017, month=3, day=17, hour=8, minute=15, second=0)]
]

EVENT_DF = pd.DataFrame(EVENTS, columns=EVENT_DF_COLUMNS)

TRACE_DF_COLUMNS = [const.CONCEPT_NAME, const.COST_TOTAL]

TRACES = [
    ['1', 100.0],
    ['2', 1300.0],
    ['3', 1400.0]
]

TRACE_DF = pd.DataFrame(TRACES, columns=TRACE_DF_COLUMNS)

NAME_AND_LIFECYCLE_CLF = XEventAndClassifier([XEventNameClassifier(), XEventLifeTransClassifier()])

CLASSIFIERS = {
    XEventNameClassifier().name(): [const.CONCEPT_NAME],
    NAME_AND_LIFECYCLE_CLF.name(): [const.CONCEPT_NAME, const.LIFECYCLE_TRANS]
}

LOG_TABLE = LogTable(event_df=EVENT_DF, trace_df=TRACE_DF,
                     attributes=LOG_ATTRIBUTE_DICT, classifiers=CLASSIFIERS)

XLOG = XFactory.create_log()
XLOG_NAME = 'Test log'
CONCEPT_EXTENSION.assign_name(XLOG, XLOG_NAME)
TOTAL_TIME = 100
TOTAL_TIME_ATTRIBUTE = XFactory.create_attribute_continuous('total_time', TOTAL_TIME)
XLOG.get_attributes()['total_time'] = TOTAL_TIME_ATTRIBUTE

for caseid, cost_total in TRACES:
    xtrace = XFactory.create_trace()

    CONCEPT_EXTENSION.assign_name(xtrace, caseid)
    COST_EXTENSION.assign_total(xtrace, cost_total)

    trace_events = filter(lambda event: event[0] == caseid, EVENTS)

    for _, concept_name, cost_unit, lifecyle, org, timestamp in trace_events:
        xevent = XFactory.create_event()

        CONCEPT_EXTENSION.assign_name(xevent, concept_name)
        COST_EXTENSION.assign_amount(xevent, cost_unit)
        LIFECYCLE_EXTENSION.assign_transition(xevent, lifecyle)
        ORG_EXTENSION.assign_group(xevent, org)
        TIME_EXTENSION.assign_timestamp(xevent, timestamp)

        xtrace.append(xevent)

    XLOG.append(xtrace)

def id_function(fixture_value):
    if not isinstance(fixture_value, XAttributable):
        return str(fixture_value)
    concept, timestamp = None, None
    if const.CONCEPT_NAME in fixture_value.get_attributes():
        concept = CONCEPT_EXTENSION.extract_name(fixture_value)
    if const.TIME_TIMESTAMP in fixture_value.get_attributes():
        timestamp = TIME_EXTENSION.extract_timestamp(fixture_value).timestamp() * 1000
    attributes = ''
    for name in sorted(fixture_value.get_attributes().keys()):
        if const.CONCEPT_NAME in name or const.TIME_TIMESTAMP in name:
            continue
        value = fixture_value.get_attributes()[name].get_value()
        attributes = attributes + ', ' + value if attributes != '' else value
    string = '{}({}, {}, {})'.format(type(fixture_value).__name__, concept, timestamp, attributes)
    return string


@pytest.fixture(scope='function')
def an_event_attribute_list():
    return EVENT_ATTRIBUTES


@pytest.fixture(scope='function')
def a_trace_attribute_list():
    return TRACE_ATTRIBUTES


@pytest.fixture(scope='function')
def a_log_attribute_list():
    return LOG_ATTRIBUTES


@pytest.fixture(scope='function', params=list(fts.reduce(lambda all, t: all + t, XLOG, [])), ids=id_function)
def an_xevent(request):
    return request.param


@pytest.fixture(scope='function', params=XLOG, ids=id_function)
def a_xtrace(request):
    return request.param


@pytest.fixture(scope='function')
def an_xlog():
    return XLOG


@pytest.fixture(scope='function')
def an_event_df():
    return EVENT_DF


@pytest.fixture(scope='function')
def a_trace_df():
    return TRACE_DF


@pytest.fixture(scope='function')
def a_log_table():
    return LOG_TABLE

# event identities
# XEventNameClassifier
event_identity_list_name = sorted([
    'Check stock availability', 'Retrieve product from warehouse', 'Confirm order',
    'Get shipping address', 'Ship product', 'Emit invoice', 'Receive payment',
    'Archive order', 'Check raw materials availability', 'Request raw materials from supplier 1',
    'Obtain raw materials from supplier 1', 'Manufacture product',
    'Request raw materials from supplier 2', 'Obtain raw materials from supplier 2'
])

# XEventLife
event_identity_list_lifecycle = its.product(event_identity_list_name, ['complete', 'start'])
event_identity_list_lifecycle = list(map(lambda t: '&&'.join(t), event_identity_list_lifecycle))

@pytest.fixture(scope='function', params=[
    (XEventNameClassifier().name(), event_identity_list_name),
    (NAME_AND_LIFECYCLE_CLF.name(), event_identity_list_lifecycle)
])
def an_event_clf_and_event_identity_list(request):
    return request.param
