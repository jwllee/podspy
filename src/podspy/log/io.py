#!/usr/bin/env python

"""This is the log io module.

This module contains methods to do io operations for log data.
"""


from .table import LogTable
from lxml import etree
import logging


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
