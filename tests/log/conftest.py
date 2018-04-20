#!/usr/bin/env python

"""This is the configuration file containing the test data for the test module Log.

"""


from opyenxes.factory.XFactory import XFactory
from opyenxes.extension.XExtensionManager import XExtensionManager
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
from opyenxes.out.XesXmlGZIPSerializer import XesXmlGZIPSerializer
import math, pytest
from random import randint
import numpy as np
import pandas as pd
from collections import defaultdict as ddict
from podspy.log.storage import *
from podspy.log import utils


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"

MANAGER = XExtensionManager()
CONCEPT_EXT = MANAGER.get_by_name('Concept')
TIME_EXT = MANAGER.get_by_name('Time')
LIFECYCLE_EXT = MANAGER.get_by_name('Lifecycle')
ORGANIZATIONAL_EXT = MANAGER.get_by_name('Organizational')
COST_EXT = MANAGER.get_by_name('Cost')


@pytest.fixture(scope='session')
def name_clf():
    return XEventNameClassifier()


def generate_event_name():
    count = 0
    while True:
        activity = ''
        aux = count
        max_power = int(math.log(aux, 26)) if count > 0 else 0
        for power in range(max_power, 0, -1):
            # we treat 1 as B
            multiple = aux // (26 ** power)
            # need to add padding to be in ASCII range where ord(A) = 65
            char = chr(multiple + 65)
            activity = activity + str(char)
            # update the aux
            aux = aux - (multiple * (26 ** power))
        # count < 26
        activity = activity + str(chr(aux + 65))
        yield 'Activity {}'.format(activity)
        count += 1


def test_event_name_generator():
    generator = generate_event_name()
    assert next(generator) == 'Activity A'
    assert next(generator) == 'Activity B'
    for i in range(674):
        next(generator)
    assert next(generator) == 'Activity BAA'


EVENT_NAME_GENERATOR = generate_event_name()

LOG = XFactory.create_log()
LOG_ATTR_KEYS = [
    (EventStorageFactory.LITERAL, 'concept:name', 'concept:name', None),
    (EventStorageFactory.CONTINUOUS, 'time:total', 'time:total', None)
]

NB_TRACES = 3
TRACES = []
TRACE_ATTR_KEYS = [
    (EventStorageFactory.LITERAL, 'concept:name', 'concept:name', None),
    (EventStorageFactory.CONTINUOUS, 'cost:total', 'cost:total', None)
]

NB_EVENTS = 3
EVENTS = []
EVENT_ATTR_KEYS = [
    (EventStorageFactory.LITERAL, 'concept:name', 'concept:name', None),
    (EventStorageFactory.CONTINUOUS, 'cost:unit', 'cost:unit', None),
    (EventStorageFactory.LITERAL, 'lifecycle:transition', 'lifecycle:transition', None),
    (EventStorageFactory.LITERAL, 'org:group', 'org:group', None),
    (EventStorageFactory.TIMESTAMP, 'time:timestamp', 'time:timestamp', None)
]
LIFECYCLES = [
    'schedule',
    'start',
    'complete'
]
GROUPS = [
    'Developer',
    'Tester',
    'Architect'
]

log_name = 'Test log'
total_time = 100
total_time_attr = XFactory.create_attribute_continuous('time:total', total_time)
CONCEPT_EXT.assign_name(LOG, log_name)
LOG.get_attributes()['time:total'] = total_time_attr

# create dicts for making expected dataframes
LOG_COL_DICT = {}
TRACE_COL_DICT = ddict(list)

EVENT_DF_LIST = []

for i in range(NB_TRACES):
    trace = XFactory.create_trace()
    event_col_dict = ddict(list)
    caseid = str(i)

    CONCEPT_EXT.assign_name(trace, caseid)
    total_cost = randint(0, i * 1000) * 1.
    total_cost_attr = XFactory.create_attribute_continuous('cost:total', total_cost)

    trace.get_attributes()['cost:total'] = total_cost_attr

    # update the column dict on the trace level
    TRACE_COL_DICT['concept:name'].append(caseid)
    TRACE_COL_DICT['cost:total'].append(total_cost)

    for j in range(NB_EVENTS):
        event = XFactory.create_event()

        activity = next(EVENT_NAME_GENERATOR)
        timestamp_attr = XFactory.create_attribute_timestamp('date', i + 1)
        timestamp = timestamp_attr.get_value()
        lifecycle = np.random.choice(LIFECYCLES)
        lifecycle_attr = XFactory.create_attribute_literal('lifecycle:transition', lifecycle)
        group = np.random.choice(GROUPS)
        unit_cost = randint(0, i * 100) * 1.0
        unit_cost_attr = XFactory.create_attribute_continuous('cost:unit', unit_cost)

        CONCEPT_EXT.assign_name(event, activity)
        ORGANIZATIONAL_EXT.assign_group(event, group)
        event.get_attributes()['time:timestamp'] = timestamp_attr
        event.get_attributes()['lifecycle:transition'] = lifecycle_attr
        event.get_attributes()['cost:unit'] = unit_cost_attr

        # update the event column dict
        event_col_dict[EventStorageFactory.CASEID].append(caseid)
        event_col_dict[EventStorageFactory.ACTIVITY].append(activity)
        event_col_dict['concept:name'].append(activity)
        event_col_dict['time:timestamp'].append(timestamp)
        event_col_dict['lifecycle:transition'].append(lifecycle)
        event_col_dict['org:group'].append(group)
        event_col_dict['cost:unit'].append(unit_cost)

        EVENTS.append((caseid, event))

        trace.append(event)

    # create event df for this trace
    columns = [EventStorageFactory.CASEID, EventStorageFactory.ACTIVITY,
               'concept:name', 'cost:unit', 'lifecycle:transition', 'org:group',
               'time:timestamp']
    event_df = pd.DataFrame(event_col_dict, columns=columns)

    utils.optimize_df_dtypes(event_df)

    EVENT_DF_LIST.append(event_df)

    TRACES.append(trace)
    LOG.append(trace)

# make the trace df
columns = ['concept:name', 'cost:total']
TRACE_DF = pd.DataFrame(TRACE_COL_DICT, columns=columns)
utils.optimize_df_dtypes(TRACE_DF)


def id_func(fixture_value):
    concept = XExtensionManager().get_by_name('Concept').extract_name(fixture_value)
    timestamp = XExtensionManager().get_by_name('Time').extract_timestamp(fixture_value)
    attributes = ''
    for name in sorted(fixture_value.get_attributes().keys()):
        val = fixture_value.get_attributes()[name]
        if 'concept:name' in name or 'time:timestamp' in name:
            continue
        attributes = attributes + ', ' + val.get_value() if attributes != '' else val.get_value()
    e = '{}({}, {}, {})'.format(type(fixture_value).__name__, concept, timestamp, attributes)
    return e


# create fixtures
@pytest.fixture(scope='function')
def event_attr_list():
    return EVENT_ATTR_KEYS


@pytest.fixture(scope='function')
def trace_attr_list():
    return TRACE_ATTR_KEYS


@pytest.fixture(scope='function')
def log_attr_list():
    return LOG_ATTR_KEYS


@pytest.fixture(scope='function', params=EVENTS, ids=lambda item: id_func(item[0][1]))
def an_event(request):
    return request.param


@pytest.fixture(scope='function', params=zip(TRACES, EVENT_DF_LIST),
                ids=lambda item: id_func(item[0]))
def a_trace_and_df(request):
    return request.param


@pytest.fixture(scope='function', ids=lambda item: id_func(item[0]))
def traces_and_df():
    return (LOG, TRACE_DF)


@pytest.fixture(scope='function')
def log_and_event_df():
    df = pd.concat(EVENT_DF_LIST)
    utils.optimize_df_dtypes(df)
    return (LOG, df)


