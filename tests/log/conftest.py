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

LOG_ROWS = []
LOG_ATTR_KEYS = [
    'concept:name',
    'time:total'
]

NB_TRACES = 3
TRACES = []
TRACE_ROWS = []
TRACE_ATTR_KEYS = [
    'concept:name',
    'cost:total'
]

NB_EVENTS = 3
EVENTS = []
EVENT_ROWS = []
EVENT_ATTR_KEYS = [
    'concept:name',
    'lifecycle:transition',
    'org:group',
    'time:timestamp'
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
LOG = XFactory.create_log()
CONCEPT_EXT.assign_name(LOG, log_name)
LOG.get_attributes()['time:total'] = total_time_attr

for i in range(NB_TRACES):
    trace = XFactory.create_trace()
    trace_rows = []
    caseid = str(i)

    CONCEPT_EXT.assign_name(trace, caseid)
    total_cost = randint(0, i * 1000)
    total_cost_attr = XFactory.create_attribute_continuous('cost:total', total_cost)

    trace.get_attributes()['cost:total'] = total_cost_attr

    for j in range(NB_EVENTS):
        event = XFactory.create_event()

        activity = next(EVENT_NAME_GENERATOR)
        timestamp_attr = XFactory.create_attribute_timestamp('date', i + 1)
        timestamp = timestamp_attr.get_value()
        lifecycle = np.random.choice(LIFECYCLES)
        lifecycle_attr = XFactory.create_attribute_literal('lifecycle:transition', lifecycle)
        group = np.random.choice(GROUPS)

        CONCEPT_EXT.assign_name(event, activity)
        ORGANIZATIONAL_EXT.assign_group(event, group)
        event.get_attributes()['time:timestamp'] = timestamp_attr
        event.get_attributes()['lifecycle:transition'] = lifecycle_attr

        event_row = ((caseid, activity, timestamp), (activity, lifecycle, group, timestamp))
        trace_row = ((caseid, activity, timestamp), (caseid, total_cost),
                     (activity, lifecycle, group, timestamp))
        log_row = (caseid, activity, timestamp,
                   # log attributes
                   log_name, total_time,
                   # trace attributes
                   caseid, total_cost,
                   # event attributes
                   activity, lifecycle, group, timestamp)

        EVENTS.append((caseid, event))
        EVENT_ROWS.append(event_row)

        trace.append(event)
        trace_rows.append(trace_row)

        LOG_ROWS.append(log_row)

    TRACES.append(trace)
    TRACE_ROWS.append(trace_rows)
    LOG.append(trace)


# store the log in a temporary test data directory
@pytest.fixture(scope='module')
def test_log(tmpdir_factory):
    file = tmpdir_factory.mktemp('data').join('test_log.xes.gz')
    print('test log file: {}'.format(file))

    with file.open('w') as f:
        XesXmlGZIPSerializer.serialize(LOG, file)

    return file


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
def event_attr_keys():
    return EVENT_ATTR_KEYS


@pytest.fixture(scope='function')
def trace_attr_keys():
    return TRACE_ATTR_KEYS


@pytest.fixture(scope='function')
def log_attr_keys():
    return LOG_ATTR_KEYS


@pytest.fixture(scope='function', params=zip(EVENTS, EVENT_ROWS), ids=lambda item: id_func(item[0][1]))
def an_event_and_row(request):
    return request.param


@pytest.fixture(scope='function', params=zip(TRACES, TRACE_ROWS), ids=lambda item: id_func(item[0]))
def a_trace_and_rows(request):
    return request.param


@pytest.fixture(scope='function')
def a_log_and_rows():
    return (LOG, LOG_ROWS)

