#!/usr/bin/env python

"""This is the log io module.

This module contains methods to do io operations for log data.
"""


from .table import LogTable
from lxml import etree
import logging, uuid
from urllib.parse import urlparse
from podspy.util import conversion


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


logger = logging.getLogger(__file__)


def import_logtable_from_xesfile(f):
    """Import a log table from a xes file

    :param f: file object
    :return: a log table
    """
    context = etree.iterparse(f, events=('end',))
    for event, elem in context:
        pass


def parse_classifier_elem(elem, d=None):
    """Parse a XES classifier element as a dict

    :param elem: classifier element to parse
    :param d: dictionary to store the parsed classifier
    :return: the dictionary
    """
    d = d if d is not None else dict()

    assert elem.tag == 'classifier', 'Element has tag: {}'.format(elem.tag)
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

    assert elem.tag == 'extension', 'Element has tag: {}'.format(elem.tag)
    assert 'name' in elem.attrib, 'Extension element has no name'
    assert 'prefix' in elem.attrib, 'Extension element has no prefix'
    assert 'uri' in elem.attrib, 'Extension element has no uri'

    name = elem.attrib['name']
    prefix = elem.attrib['prefix']
    uri = urlparse(elem.attrib['uri'])

    d[name] = (name, prefix, uri)
    return d


def parse_literal_attrib_elem(elem):
    """Parse an element of a XAttributeLiteral

    :param elem: element to parse
    :return: the key and literal value
    """
    assert elem.tag == 'string', 'Element has tag: {}'.format(elem.tag)
    assert 'key' in elem.attrib, 'Literal attribute has no key'
    assert 'value' in elem.attrib, 'Literal attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']

    return key, value


def parse_bool_attrib_elem(elem):
    """Parse an element of a XAttributeBoolean

    :param elem: element to parse
    :return: the key and boolean value
    """
    assert elem.tag == 'boolean', 'Element has tag: {}'.format(elem.tag)
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

    return key, bool_val


def parse_discrete_attrib_elem(elem):
    """Parse an element of a XAttributeDiscrete

    :param elem: element to parse
    :return: a tuple containing the key and discrete value
    """
    assert elem.tag == 'int', 'Element has tag: {}'.format(elem.tag)
    assert 'key' in elem.attrib, 'Discrete attribute has no key'
    assert 'value' in elem.attrib, 'Discrete attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']

    try:
        int_value = int(value)
    except ValueError as e:
        logger.error('Cannot convert {} as int: {}'.format(value, e))
        int_value = 0

    return key, int_value


def parse_continuous_attrib_elem(elem):
    """Parse an element of a XAttributeContinuous

    :param elem: element to parse
    :return: a tuple containing the key and continuous value
    """
    assert elem.tag == 'float', 'Element has tag: {}'.format(elem.tag)
    assert 'key' in elem.attrib, 'Continuous attribute has no key'
    assert 'value' in elem.attrib, 'Continuous attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']

    try:
        float_value = float(value)
    except ValueError as e:
        logger.error('Cannot convert {} as float: {}'.format(value, e))
        float_value = 0.

    return key, float_value


def parse_timestamp_attrib_elem(elem):
    """Parse an element of a XAttributeTimestamp

    :param elem: element to parse
    :return: a tuple containing the key and datetime value
    """
    assert elem.tag == 'date', 'Element has tag: {}'.format(elem.tag)
    assert 'key' in elem.attrib, 'Timestamp attribute has no key'
    assert 'value' in elem.attrib, 'Timestamp attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']
    time = conversion.parse_timestamp(value)

    return key, time


def parse_id_attrib_elem(elem):
    """Parse an element of a XAttributeID

    :param elem: element to parse
    :return: a tuple containing the key and id value
    """
    assert elem.tag == 'id', 'Element has tag: {}'.format(elem.tag)
    assert 'key' in elem.attrib, 'ID attribute has no key'
    assert 'value' in elem.attrib, 'ID attribute has no value'

    key = elem.attrib['key']
    value = elem.attrib['value']

    try:
        id_value = uuid.UUID(value)
    except ValueError as e:
        logger.error('Cannot convert {} as uuid: {}'.format(value, e))
        id_value = value

    return key, id_value


def parse_list_attrib_elem(elem):
    logger.warning('List XAttribute is not supported')


def parse_container_attrib_elem(elem):
    logger.warning('Container XAttribute is not supported')
