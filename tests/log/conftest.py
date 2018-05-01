#!/usr/bin/env python


from datetime import datetime as dt
import pandas as pd
import pytest
import functools as fts

from podspy.log.constant import *

from opyenxes.factory.XFactory import XFactory
from opyenxes.extension.XExtensionManager import XExtensionManager
from opyenxes.model.XAttributable import XAttributable

EXTENSION_MANAGER = XExtensionManager()
CONCEPT_EXTENSION = EXTENSION_MANAGER.get_by_name('Concept')


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


# log attributes
log_attributes = [
    (LITERAL, 'concept:name', 'concept:name', None),
    (CONTINUOUS, 'time:total', 'time:total', None)
]


# trace attributes
trace_attributes = [
    (LITERAL, 'concept:name', 'concept:name', None),
    (CONTINUOUS, 'cost:total', 'cost:total', None)
]


# event attributes
event_attributes = [
    (LITERAL, 'concept:name', 'concept:name', None),
    (CONTINUOUS, 'cost:unit', 'cost:unit', None),
    (LITERAL, 'lifecycle:transition', 'lifecycle:transition', None),
    (LITERAL, 'org:group', 'org:group', None),
    (TIMESTAMP, 'time:timestamp', 'time:timestamp', None)
]

# column order:
#   1) caseid
#   2) activity
#   3) concept:name
#   4) cost:unit
#   5) lifecyle:transition
#   6) org:group
#   7) time:timestamp
event_df_columns = [ CASEID, ACTIVITY, 'concept:name', 'cost:unit',
                     'lifecycle:transition', 'org:group', 'time:timestamp' ]
events = [
    # case id: 1
    ['1', 'Check stock availability', 'Check stock availability', 0.0, 'start', 'warehouse', dt(year=2017, month=1, day=1, hour=8, minute=0, second=0)],
    ['1', 'Check stock availability', 'Check stock availability', 0.0, 'complete', 'warehouse', dt(year=2017, month=1, day=1, hour=8, minute=0, second=0)],
    ['1', 'Retrieve product from warehouse', 'Retrieve product from warehouse', 0.0, 'start', 'transport', dt(year=2017, month=1, day=2, hour=8, minute=0, second=0)],
    ['1', 'Retrieve product from warehouse', 'Retrieve product from warehouse', 0.0, 'complete', 'transport', dt(year=2017, month=1, day=2, hour=15, minute=0, second=0)],
    ['1', 'Confirm order', 'Confirm order', 0.0, 'start', 'sales', dt(year=2017, month=1, day=3, hour=8, minute=0, second=0)],
    ['1', 'Confirm order', 'Confirm order', 0.0, 'complete', 'sales', dt(year=2017, month=1, day=3, hour=8, minute=0, second=0)],
    ['1', 'Get shipping address', 'Get shipping address', 0.0, 'start', 'sales', dt(year=2017, month=1, day=3, hour=12, minute=0, second=0)],
    ['1', 'Get shipping address', 'Get shipping address', 0.0, 'complete', 'sales', dt(year=2017, month=1, day=3, hour=12, minute=10, second=0)],
    ['1', 'Ship product', 'Ship product', 0.0, 'start', 'transport', dt(year=2017, month=1, day=4, hour=8, minute=0, second=0)],
    ['1', 'Ship product', 'Ship product', 100.0, 'complete', 'transport', dt(year=2017, month=1, day=4, hour=15, minute=0, second=0)],
    ['1', 'Emit invoice', 'Emit invoice', 0.0, 'start', 'sales', dt(year=2017, month=1, day=3, hour=12, minute=15, second=0)],
    ['1', 'Emit invoice', 'Emit invoice', 0.0, 'complete', 'sales', dt(year=2017, month=1, day=3, hour=12, minute=15, second=0)],
    ['1', 'Receive payment', 'Receive payment', 0.0, 'start', 'sales', dt(year=2017, month=1, day=5, hour=8, minute=0, second=0)],
    ['1', 'Receive payment', 'Receive payment', 0.0, 'complete', 'sales', dt(year=2017, month=1, day=5, hour=8, minute=0, second=0)],
    ['1', 'Archive order', 'Archive order', 0.0, 'start', 'sales', dt(year=2017, month=1, day=5, hour=8, minute=10, second=0)],
    ['1', 'Archive order', 'Archive order', 0.0, 'complete', 'sales', dt(year=2017, month=1, day=5, hour=8, minute=15, second=0)],
    # case id: 2
    ['2', 'Check stock availability', 'Check stock availability', 0.0, 'start', 'warehouse', dt(year=2017, month=2, day=1, hour=8, minute=0, second=0)],
    ['2', 'Check stock availability', 'Check stock availability', 0.0, 'complete', 'warehouse', dt(year=2017, month=2, day=1, hour=8, minute=0, second=0)],
    ['2', 'Retrieve product from warehouse', 'Retrieve product from warehouse', 0.0, 'start', 'transport', dt(year=2017, month=2, day=2, hour=8, minute=0, second=0)],
    ['2', 'Retrieve product from warehouse', 'Retrieve product from warehouse', 0.0, 'complete', 'transport', dt(year=2017, month=2, day=2, hour=15, minute=0, second=0)],
    ['2', 'Check raw materials availability', 'Check raw materials availability', 0.0, 'start', 'warehouse', dt(year=2017, month=2, day=3, hour=8, minute=0, second=0)],
    ['2', 'Check raw materials availability', 'Check raw materials availability', 0.0, 'complete', 'warehouse', dt(year=2017, month=2, day=3, hour=8, minute=30, second=0)],
    ['2', 'Request raw materials from supplier 1', 'Request raw materials from supplier 1', 0.0, 'start', 'warehouse', dt(year=2017, month=2, day=3, hour=9, minute=0, second=0)],
    ['2', 'Request raw materials from supplier 1', 'Request raw materials from supplier 1', 0.0, 'complete', 'warehouse', dt(year=2017, month=2, day=3, hour=9, minute=5, second=0)],
    ['2', 'Obtain raw materials from supplier 1', 'Obtain raw materials from supplier 1', 0.0, 'start', 'warehouse', dt(year=2017, month=2, day=5, hour=8, minute=5, second=0)],
    ['2', 'Obtain raw materials from supplier 1', 'Obtain raw materials from supplier 1', 200.0, 'complete', 'warehouse', dt(year=2017, month=2, day=5, hour=8, minute=5, second=0)],
    ['2', 'Manufacture product', 'Manufacture product', 0.0, 'start', 'manufacture', dt(year=2017, month=2, day=6, hour=8, minute=0, second=0)],
    ['2', 'Manufacture product', 'Manufacture product', 1000.0, 'complete', 'manufacture', dt(year=2017, month=2, day=14, hour=8, minute=0, second=0)],
    ['2', 'Get shipping address', 'Get shipping address', 0.0, 'start', 'sales', dt(year=2017, month=2, day=15, hour=12, minute=0, second=0)],
    ['2', 'Get shipping address', 'Get shipping address', 0.0, 'complete', 'sales', dt(year=2017, month=2, day=15, hour=12, minute=10, second=0)],
    ['2', 'Ship product', 'Ship product', 0.0, 'start', 'transport', dt(year=2017, month=2, day=16, hour=8, minute=0, second=0)],
    ['2', 'Ship product', 'Ship product', 100.0, 'complete', 'transport', dt(year=2017, month=2, day=16, hour=15, minute=0, second=0)],
    ['2', 'Emit invoice', 'Emit invoice', 0.0, 'start', 'sales', dt(year=2017, month=2, day=15, hour=12, minute=15, second=0)],
    ['2', 'Emit invoice', 'Emit invoice', 0.0, 'complete', 'sales', dt(year=2017, month=2, day=15, hour=12, minute=15, second=0)],
    ['2', 'Receive payment', 'Receive payment', 0.0, 'start', 'sales', dt(year=2017, month=2, day=17, hour=8, minute=0, second=0)],
    ['2', 'Receive payment', 'Receive payment', 0.0, 'complete', 'sales', dt(year=2017, month=2, day=17, hour=8, minute=0, second=0)],
    ['2', 'Archive order', 'Archive order', 0.0, 'start', 'sales', dt(year=2017, month=2, day=17, hour=8, minute=10, second=0)],
    ['2', 'Archive order', 'Archive order', 0.0, 'complete', 'sales', dt(year=2017, month=2, day=17, hour=8, minute=15, second=0)],
    # case id: 3
    ['3', 'Check stock availability', 'Check stock availability', 0.0, 'start', 'warehouse', dt(year=2017, month=3, day=1, hour=8, minute=0, second=0)],
    ['3', 'Check stock availability', 'Check stock availability', 0.0, 'complete', 'warehouse', dt(year=2017, month=3, day=1, hour=8, minute=0, second=0)],
    ['3', 'Retrieve product from warehouse', 'Retrieve product from warehouse', 0.0, 'start', 'transport', dt(year=2017, month=3, day=2, hour=8, minute=0, second=0)],
    ['3', 'Retrieve product from warehouse', 'Retrieve product from warehouse', 0.0, 'complete', 'transport', dt(year=2017, month=3, day=2, hour=15, minute=0, second=0)],
    ['3', 'Check raw materials availability', 'Check raw materials availability', 0.0, 'start', 'warehouse', dt(year=2017, month=3, day=3, hour=8, minute=0, second=0)],
    ['3', 'Check raw materials availability', 'Check raw materials availability', 0.0, 'complete', 'warehouse', dt(year=2017, month=3, day=3, hour=8, minute=30, second=0)],
    ['3', 'Request raw materials from supplier 2', 'Request raw materials from supplier 2', 0.0, 'start', 'warehouse', dt(year=2017, month=3, day=3, hour=9, minute=0, second=0)],
    ['3', 'Request raw materials from supplier 2', 'Request raw materials from supplier 2', 0.0, 'complete', 'warehouse', dt(year=2017, month=3, day=3, hour=9, minute=5, second=0)],
    ['3', 'Obtain raw materials from supplier 2', 'Obtain raw materials from supplier 2', 0.0, 'start', 'warehouse', dt(year=2017, month=3, day=5, hour=8, minute=5, second=0)],
    ['3', 'Obtain raw materials from supplier 2', 'Obtain raw materials from supplier 2', 300.0, 'complete', 'warehouse', dt(year=2017, month=3, day=5, hour=8, minute=5, second=0)],
    ['3', 'Manufacture product', 'Manufacture product', 0.0, 'start', 'manufacture', dt(year=2017, month=3, day=6, hour=8, minute=0, second=0)],
    ['3', 'Manufacture product', 'Manufacture product', 1000.0, 'complete', 'manufacture', dt(year=2017, month=3, day=14, hour=8, minute=0, second=0)],
    ['3', 'Get shipping address', 'Get shipping address', 0.0, 'start', 'sales', dt(year=2017, month=3, day=15, hour=12, minute=0, second=0)],
    ['3', 'Get shipping address', 'Get shipping address', 0.0, 'complete', 'sales', dt(year=2017, month=3, day=15, hour=12, minute=10, second=0)],
    ['3', 'Ship product', 'Ship product', 0.0, 'start', 'transport', dt(year=2017, month=3, day=16, hour=8, minute=0, second=0)],
    ['3', 'Ship product', 'Ship product', 100.0, 'complete', 'transport', dt(year=2017, month=3, day=16, hour=15, minute=0, second=0)],
    ['3', 'Emit invoice', 'Emit invoice', 0.0, 'start', 'sales', dt(year=2017, month=3, day=15, hour=12, minute=15, second=0)],
    ['3', 'Emit invoice', 'Emit invoice', 0.0, 'complete', 'sales', dt(year=2017, month=3, day=15, hour=12, minute=15, second=0)],
    ['3', 'Receive payment', 'Receive payment', 0.0, 'start', 'sales', dt(year=2017, month=3, day=17, hour=8, minute=0, second=0)],
    ['3', 'Receive payment', 'Receive payment', 0.0, 'complete', 'sales', dt(year=2017, month=3, day=17, hour=8, minute=0, second=0)],
    ['3', 'Archive order', 'Archive order', 0.0, 'start', 'sales', dt(year=2017, month=3, day=17, hour=8, minute=10, second=0)],
    ['3', 'Archive order', 'Archive order', 0.0, 'complete', 'sales', dt(year=2017, month=3, day=17, hour=8, minute=15, second=0)]
]

event_df = pd.DataFrame(events, columns=event_df_columns)
event_df['caseid'] = event_df['caseid'].astype('category')
event_df['activity'] = event_df['activity'].astype('category')
event_df['concept:name'] = event_df['concept:name'].astype('category')
event_df['cost:unit'] = event_df['cost:unit'].apply(pd.to_numeric, downcast='float')
event_df['lifecycle:transition'] = event_df['lifecycle:transition'].astype('category')
event_df['org:group'] = event_df['org:group'].astype('category')
event_df['time:timestamp'] = event_df['time:timestamp'].astype('datetime64[ns]')

# trace dataframe
traces_df_columns = ['concept:name', 'cost:total']
traces = [
    ['1', 100.0],
    ['2', 1300.0],
    ['3', 1400.0]
]

trace_df = pd.DataFrame(traces, columns=traces_df_columns)
trace_df['cost:total'] = trace_df['cost:total'].apply(pd.to_numeric, downcast='float')

# create XLog
xlog = XFactory.create_log()
xlog_name = 'Test log'
CONCEPT_EXTENSION.assign_name(xlog, xlog_name)
total_time = 100
total_time_attribute = XFactory.create_attribute_continuous('time:total', total_time)
xlog.get_attributes()['time:total'] = total_time_attribute

for caseid, cost_total in traces:
    xtrace = XFactory.create_trace()

    CONCEPT_EXTENSION.assign_name(xtrace, caseid)
    total_cost_attribute = XFactory.create_attribute_continuous('cost:total', cost_total)
    xtrace.get_attributes()['cost:total'] = total_cost_attribute

    trace_events = filter(lambda event: event[0] == caseid, events)

    for caseid_event, activity, concept_name, cost_unit, lifecycle, org, timestamp in trace_events:
        xevent = XFactory.create_event()

        CONCEPT_EXTENSION.assign_name(xevent, concept_name)
        cost_unit_attribute = XFactory.create_attribute_continuous('cost:unit', cost_unit, EXTENSION_MANAGER.get_by_name('Cost'))
        xevent.get_attributes()['cost:unit'] = cost_unit_attribute
        lifecycle_attribute = XFactory.create_attribute_literal('lifecycle:transition', lifecycle, EXTENSION_MANAGER.get_by_name('Lifecycle'))
        xevent.get_attributes()['lifecycle:transition'] = lifecycle_attribute
        org_attribute = XFactory.create_attribute_literal('org:group', org, EXTENSION_MANAGER.get_by_name('Organizational'))
        xevent.get_attributes()['org:group'] = org_attribute
        timestamp_attribute = XFactory.create_attribute_timestamp('time:timestamp', timestamp, EXTENSION_MANAGER.get_by_name('Time'))
        xevent.get_attributes()['time:timestamp'] = timestamp_attribute

        xtrace.append(xevent)

    xlog.append(xtrace)


# make data available as fixtures
def id_function(fixture_value):
    if not isinstance(fixture_value, XAttributable):
        return str(fixture_value)
    concept, timestamp = None, None
    if 'concept:name' in fixture_value.get_attributes():
        concept = fixture_value.get_attributes()['concept:name'].get_value()
    if 'time:timestamp' in fixture_value.get_attributes():
        timestamp = fixture_value.get_attributes()['time:timestamp'].get_value()
    attributes = ''
    for name in sorted(fixture_value.get_attributes().keys()):
        if 'concept:name' in name or 'time:timestamp' in name:
            continue
        value = fixture_value.get_attributes()[name].get_value()
        attributes = attributes + ', ' + value if attributes != '' else value
    string = '{}({}, {}, {})'.format(type(fixture_value).__name__, concept, timestamp, attributes)
    return string


@pytest.fixture(scope='function')
def an_event_attribute_list():
    return event_attributes


@pytest.fixture(scope='function')
def a_trace_attribute_list():
    return trace_attributes


@pytest.fixture(scope='function')
def a_log_attribute_list():
    return log_attributes


@pytest.fixture(scope='function', params=list(fts.reduce(lambda all, t: all + t, xlog, [])), ids=id_function)
def an_event(request):
    return request.param


caseids = map(lambda event: event[0], events)
events_and_caseids = zip(caseids, events)
@pytest.fixture(scope='function', params=events_and_caseids, ids=id_function)
def an_event_and_caseid(request):
    return request.param


@pytest.fixture(scope='function')
def an_event_df():
    return event_df


@pytest.fixture(scope='function')
def a_trace_df():
    return trace_df


@pytest.fixture(scope='function')
def an_xlog():
    return xlog


@pytest.fixture(scope='function', params=xlog, ids=id_function)
def a_xtrace(request):
    return request.param