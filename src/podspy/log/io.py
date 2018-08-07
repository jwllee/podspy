#!/usr/bin/env python

"""This is the log io module.

This module contains methods to do io operations for log data.
"""


from .table import LogTable
from lxml import etree
import logging, uuid
from urllib.parse import urlparse
from podspy.util import conversion
import pandas as pd
import numpy as np
from podspy.log import constant as const


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


logger = logging.getLogger(__file__)


# tags
TAG_LOG = 'log'
TAG_TRACE = 'trace'
TAG_EVENT = 'event'
TAG_EXTENSION = 'extension'
TAG_CLASSIFIER = 'classifier'
TAG_GLOBAL = 'global'

TAG_FLOAT = 'float'
TAG_BOOL = 'boolean'
TAG_DISC = 'int'
TAG_ID = 'id'
TAG_LITERAL = 'string'
TAG_TIMESTAMP = 'date'
TAG_CONTAINER = 'container'


def import_logtable_from_xesfile(f):
    """Import a log table from a xes file

    :param f: file object
    :return: a log table
    """
    context = etree.iterparse(f, events=('end',))

    lt = None
    for event, elem in context:
        if elem.tag == TAG_LOG:
            lt = parse_log_elem(elem)
        else:
            logger.warning('Element with tag: {} is not processed'.format(elem.tag))
    return lt


def __is_attrib_tag(tag):
    attrib_tags = [
        TAG_FLOAT, TAG_BOOL, TAG_DISC, TAG_ID, TAG_LITERAL, TAG_TIMESTAMP, TAG_CONTAINER
    ]
    return tag in attrib_tags


def parse_log_elem(elem):
    # use df.append(ss, ignore_index=True) to append series rows to dataframe

    logger.debug('Element: {}'.format(elem))

    # logger.debug('XES attributes: {}'.format(xes_attribs))

    extensions = dict()
    classifiers = dict()
    global_trace_attribs = None
    global_event_attribs = None
    log_attribs = dict()
    xes_attribs = dict()

    trace_df = pd.DataFrame()
    event_df = pd.DataFrame()

    _map = {
        'string': parse_literal_attrib_elem,
        'boolean': parse_bool_attrib_elem,
        'int': parse_discrete_attrib_elem,
        'float': parse_continuous_attrib_elem,
        'date': parse_timestamp_attrib_elem,
        'id': parse_id_attrib_elem
    }

    element = None
    reading_elem = False

    for event, child in elem:
        logger.debug('Event: {} Child: {}'.format(event, child))
        # logger.debug('Processing element with tag: {}'.format(child.tag))
        qname = etree.QName(child.tag)
        tag = qname.localname

        if event == 'start' and tag != TAG_LOG and not reading_elem:
            logger.debug('Start reading {}'.format(tag))
            # start reading an element
            element = tag
            reading_elem = True

        if not(tag == element and event == 'end') and reading_elem:
            logger.debug('Continuing reading {}'.format(element))
            continue
        else:
            element = None
            reading_elem = False

        if tag == TAG_EXTENSION and event == 'end':
            logger.debug('Parsing {} element'.format(tag))
            extensions = parse_extension_elem(child, extensions)

        elif tag == TAG_CLASSIFIER and event == 'end':
            logger.debug('Parsing {} element'.format(tag))
            classifiers = parse_classifier_elem(child, classifiers)

        elif tag == TAG_GLOBAL and event == 'end':
            logger.debug('Parsing {} element'.format(tag))
            scope, attribs = parse_global_attrib_elem(child)
            if scope == TAG_TRACE:
                global_trace_attribs = attribs
                logger.debug('Global trace attribs: {}'.format(global_trace_attribs))
            elif scope == TAG_EVENT:
                global_event_attribs = attribs
                logger.debug('Global event attribs: {}'.format(global_event_attribs))

        elif __is_attrib_tag(tag) and event == 'end':
            logger.debug('Parsing {} element'.format(tag))
            key, val = _map[tag](child)
            log_attribs[key] = val

        elif tag == TAG_TRACE and event == 'end':
            logger.debug('Parsing {} element'.format(tag))
            trace_ss, trace_event_df = parse_trace_elem(child)
            trace_df = trace_df.append(trace_ss, ignore_index=True)
            event_df = pd.concat([event_df, trace_event_df], axis='index')

            # remove the child
            child.clear()

            # # also eliminate now-empty references from the root node to child
            # while child.getprevious() is not None:
            #     del child.getparent()[0]

        elif tag == TAG_LOG:
            logger.debug('Parsing {} element'.format(tag))
            xes_attribs = dict(child.attrib)

    logger.debug('Log attribs: {}'.format(log_attribs))
    logger.debug('Event df: \n{}'.format(event_df))

    lt = LogTable(trace_df=trace_df, event_df=event_df, attributes=log_attribs,
                  global_trace_attributes=global_trace_attribs,
                  global_event_attributes=global_event_attribs,
                  classifiers=classifiers, extensions=extensions)
    lt.xes_attributes = xes_attribs

    return lt


def parse_classifier_elem(elem, d=None):
    """Parse a XES classifier element as a dict

    :param elem: classifier element to parse
    :param d: dictionary to store the parsed classifier
    :return: the dictionary
    """
    d = d if d is not None else dict()

    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'classifier', 'Element has tag: {}'.format(tag)
    assert 'name' in elem.attrib, 'Classifier element has no name'
    assert 'keys' in elem.attrib, 'Classifier element has no keys'

    name = elem.attrib['name']
    keys = elem.attrib['keys']

    def get_keylist(key_str, keys):
        """Problem: key_str contains keys separated by space, but we don't know which
        space is a separator between two keys and which are simply spaces of a single
        key.

        Solution: given a set of known keys, replace parts of the key_str with '' if
        it correspond to a known key. The rest should be a new key.

        :param key_str: string containing keys
        :param keys: known keys
        :return: list of keys
        """
        if ' ' not in key_str:
            return [key_str]

        # add a space padding to the front and back of the key_str to facilitate replace in forloop
        key_str = ' {} '.format(key_str)
        key_str_1 = str(key_str)
        keylist = []

        for key in keys:
            if ' {} '.format(key) in key_str_1:
                # find out the location of the key in the string so we can order the keys later on
                start_ind = key_str.find(' {} '.format(key))
                keylist.append((key, start_ind))
                key_str_1 = key_str_1.replace(key, '')

        # add the remaining key_str as a new key
        key_str_1 = key_str_1.strip()

        if key_str_1 != '':
            start_ind = key_str.find(key_str_1)
            keylist.append((key_str_1, start_ind))

        # sort the keys
        keylist = sorted(keylist, key=lambda item: item[1])
        keylist, _ = zip(*keylist)

        return list(keylist)

    known_keys = set()
    for v in d.values():
        known_keys.update(set(v))

    logger.debug('Known classifier keys: {}'.format(known_keys))

    keylist = get_keylist(keys, known_keys)
    d[name] = keylist

    return d


def parse_extension_elem(elem, d=None):
    """Parses an element containing information of an XExtension

    :param elem: Element to parse
    :param d: dictionary to put the parsed extension information
    :return: modified dictionary
    """
    d = d if d is not None else dict()

    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'extension', 'Element has tag: {}'.format(tag)
    assert 'name' in elem.attrib, 'Extension element has no name'
    assert 'prefix' in elem.attrib, 'Extension element has no prefix'
    assert 'uri' in elem.attrib, 'Extension element has no uri'

    name = elem.attrib['name']
    prefix = elem.attrib['prefix']
    uri = urlparse(elem.attrib['uri'])

    d[name] = (name, prefix, uri)
    return d


def parse_global_attrib_elem(elem):
    """Parse an element containing global attributes, can be either related to trace or event

    :param elem: element to parse
    :return: dictionary mapping attribute key to attribute value
    """
    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'global', 'Element has tag: {}'.format(tag)
    assert 'scope' in elem.attrib, 'Global attribute has no scope'

    scope = elem.attrib['scope']
    attribs = dict()

    _map = {
        'string': parse_literal_attrib_elem,
        'boolean': parse_bool_attrib_elem,
        'int': parse_discrete_attrib_elem,
        'float': parse_continuous_attrib_elem,
        'date': parse_timestamp_attrib_elem,
        'id': parse_id_attrib_elem
    }

    for child in elem:
        qname = etree.QName(child.tag)
        tag = qname.localname
        if tag in _map:
            key, value = _map[tag](child)
            attribs[key] = value
        else:
            logger.warning('Skipping unsupported attribute type {}: \n{}'.format(child.tag, child))

    return scope, attribs


def parse_literal_attrib_elem(elem):
    """Parse an element of a XAttributeLiteral

    :param elem: element to parse
    :return: the key and literal value
    """
    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'string', 'Element has tag: {}'.format(tag)
    assert 'key' in elem.attrib, 'Literal attribute has no key'
    assert 'value' in elem.attrib, 'Literal attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']

    if len(elem):
        parse_list_attrib_elem(elem)

    return key, value


def parse_bool_attrib_elem(elem):
    """Parse an element of a XAttributeBoolean

    :param elem: element to parse
    :return: the key and boolean value
    """
    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'boolean', 'Element has tag: {}'.format(tag)
    assert 'key' in elem.attrib, 'Boolean attribute has no key'
    assert 'value' in elem.attrib, 'Boolean attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value'].lower()

    if value == 'true':
        bool_val = True
    elif value == 'false':
        bool_val = False
    else:
        logger.warning('Do not recognize boolean value: {}, use default value: {}'.format(value, False))
        bool_val = False

    if len(elem):
        parse_list_attrib_elem(elem)

    return key, bool_val


def parse_discrete_attrib_elem(elem):
    """Parse an element of a XAttributeDiscrete

    :param elem: element to parse
    :return: a tuple containing the key and discrete value
    """
    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'int', 'Element has tag: {}'.format(tag)
    assert 'key' in elem.attrib, 'Discrete attribute has no key'
    assert 'value' in elem.attrib, 'Discrete attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']

    try:
        int_value = int(value)
    except ValueError as e:
        logger.error('Cannot convert {} as int: {}'.format(value, e))
        int_value = 0

    if len(elem):
        parse_list_attrib_elem(elem)

    return key, int_value


def parse_continuous_attrib_elem(elem):
    """Parse an element of a XAttributeContinuous

    :param elem: element to parse
    :return: a tuple containing the key and continuous value
    """
    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'float', 'Element has tag: {}'.format(tag)
    assert 'key' in elem.attrib, 'Continuous attribute has no key'
    assert 'value' in elem.attrib, 'Continuous attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']

    try:
        float_value = float(value)
    except ValueError as e:
        logger.error('Cannot convert {} as float: {}'.format(value, e))
        float_value = 0.

    if len(elem):
        parse_list_attrib_elem(elem)

    return key, float_value


def parse_timestamp_attrib_elem(elem):
    """Parse an element of a XAttributeTimestamp

    :param elem: element to parse
    :return: a tuple containing the key and datetime value
    """
    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'date', 'Element has tag: {}'.format(tag)
    assert 'key' in elem.attrib, 'Timestamp attribute has no key'
    assert 'value' in elem.attrib, 'Timestamp attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']
    time = conversion.parse_timestamp(value)

    if len(elem):
        parse_list_attrib_elem(elem)

    return key, time


def parse_id_attrib_elem(elem):
    """Parse an element of a XAttributeID

    :param elem: element to parse
    :return: a tuple containing the key and id value
    """
    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'id', 'Element has tag: {}'.format(tag)
    assert 'key' in elem.attrib, 'ID attribute has no key'
    assert 'value' in elem.attrib, 'ID attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']

    try:
        id_value = uuid.UUID(value)
    except ValueError as e:
        logger.error('Cannot convert {} as uuid: {}'.format(value, e))
        id_value = value

    if len(elem):
        parse_list_attrib_elem(elem)

    return key, id_value


def parse_list_attrib_elem(elem):
    logger.warning('List XAttribute is not supported')


def parse_container_attrib_elem(elem):
    logger.warning('Container XAttribute is not supported')


def parse_event_elem(elem):
    """Parses an element contianing a :class:`opyenxes.model.XEvent.XEvent`.

    :param elem: element to parse
    :return: a series containing event info
    """
    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'event', 'Element has tag: {}'.format(tag)

    attribs = dict()

    _map = {
        'string': parse_literal_attrib_elem,
        'boolean': parse_bool_attrib_elem,
        'int': parse_discrete_attrib_elem,
        'float': parse_continuous_attrib_elem,
        'date': parse_timestamp_attrib_elem,
        'id': parse_id_attrib_elem
    }

    for child in elem:
        qname = etree.QName(child.tag)
        tag = qname.localname
        if tag in _map:
            key, value = _map[tag](child)
            attribs[key] = value
        else:
            logger.warning('Skipping unsupported attribute type {}: \n{}'.format(child.tag, child))

    ss = pd.Series(attribs)
    return ss


def parse_trace_elem(elem):
    """Parses an element containing a :class:`opyenxes.model.XTrace.XTrace`.

    :param elem: element to parse
    :return: a series row containing trace info, and a dataframe containing event info
    """
    qname = etree.QName(elem.tag)
    tag = qname.localname
    assert tag == 'trace', 'Element has tag: {}'.format(tag)

    event_df = pd.DataFrame()
    attribs = dict()

    _map = {
        'string': parse_literal_attrib_elem,
        'boolean': parse_bool_attrib_elem,
        'int': parse_discrete_attrib_elem,
        'float': parse_continuous_attrib_elem,
        'date': parse_timestamp_attrib_elem,
        'id': parse_id_attrib_elem
    }

    for child in elem:
        qname = etree.QName(child.tag)
        tag = qname.localname
        if tag in _map:
            key, value = _map[tag](child)
            attribs[key] = value
        elif tag == 'event':
            event_ss = parse_event_elem(child)
            event_df = event_df.append(event_ss, ignore_index=True)
        else:
            logger.warning('Skipping unsupported child type {}: \n{}'.format(child.tag, child))

    ss = pd.Series(attribs)

    # add caseid to event_df
    assert 'concept:name' in attribs, 'concept:name (caseid) is missing'
    event_df[const.CASEID] = attribs['concept:name']

    print('Parsed trace with caseid: {}'.format(attribs['concept:name']))

    return ss, event_df
