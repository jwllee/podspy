#!/usr/bin/env python

"""This is the configuration file containing the test data for the test module Log.

"""


from opyenxes.factory.XFactory import XFactory
from opyenxes.model.XEvent import XEvent
from opyenxes.extension.XExtensionManager import XExtensionManager
import math, pytest


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


MANAGER = XExtensionManager()
CONCEPT_EXT = MANAGER.get_by_name('Concept')
TIME_EXT = MANAGER.get_by_name('Time')
LIFECYCLE_EXT = MANAGER.get_by_name('Lifecycle')
ORGANIZATIONAL_EXT = MANAGER.get_by_name('Organizational')


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


EVENTS = []
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
for i in range(3):
    event = XFactory.create_event()
    timestamp = XFactory.create_attribute_timestamp('date', i + 1)
    event.get_attributes()['time:timestamp'] = timestamp
    CONCEPT_EXT.assign_name(event, next(EVENT_NAME_GENERATOR))
    lifecycle = XFactory.create_attribute_literal('lifecycle:transition', LIFECYCLES[i])
    event.get_attributes()['lifecycle:transition'] = lifecycle
    ORGANIZATIONAL_EXT.assign_group(event, GROUPS[i])
    EVENTS.append(event)


def id_func(fixture_value):
    concept = XExtensionManager().get_by_name('Concept').extract_name(fixture_value)
    timestamp = XExtensionManager().get_by_name('Time').extract_timestamp(fixture_value)
    attributes = ''
    for name in sorted(fixture_value.get_attributes().keys()):
        val = fixture_value.get_attributes()[name]
        if 'concept:name' in name or 'time:timestamp' in name:
            continue
        attributes = attributes + ', ' + val.get_value() if attributes != '' else val.get_value()
    e = 'XEvent({}, {}, {})'.format(concept, timestamp, attributes)
    return e


# create fixtures
@pytest.fixture(scope='function', params=EVENTS, ids=id_func)
def an_event(request):
    return request.param


