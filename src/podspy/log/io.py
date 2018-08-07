#!/usr/bin/env python

"""This is the data in module.

This module reads log files.
"""

import logging, uuid, time
from lxml import etree
from podspy.log import constant as const
from podspy.log import table as tble
from podspy.util import conversion as cvrn
from urllib.request import urlparse
import pandas as pd


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


logger = logging.getLogger(__file__)


# tags
LOG = 'log'
TRACE = 'trace'
EVENT = 'event'
EXTENSION = 'extension'
CLASSIFIER = 'classifier'
GLOBAL = 'global'

CONTINUOUS = 'float'
BOOLEAN = 'boolean'
DISCRETE = 'int'
ID = 'id'
LITERAL = 'string'
TIMESTAMP = 'date'
CONTAINER = 'container'
LIST = 'list'


def import_xlog_from_file(fp):
    start = time.time()
    parser = etree.XMLParser(target=LogTableTarget())
    lt = etree.parse(fp, parser)
    diff = time.time() - start

    logger.info('Parsing log to log table took {} seconds'.format(diff))

    return lt


class LogTableTarget:
    """Parser target class to pass to the :class:`lxml.etree.XMLParser` to build a
    :class:`podspy.log.table.LogTable`.

    """
    def __init__(self):
        self.__trace = None
        self.__event = None
        self.__attribute_stack = list()   # stack
        self.__attributable_stack = list()    # stack
        self.__extension = set()
        self.__globals = None

        self.__global_trace_attribs = dict()
        self.__global_event_attribs = dict()
        self.__extensions = dict()
        self.__classifiers = dict()
        self.__log_attribs = dict()
        self.__xes_attribs = dict()
        self.__trace_df_dict = dict()
        self.__event_df_dict = dict()
        self.__caseid = None
        self.__trace_ind = 0
        self.__event_ind = 0

    @staticmethod
    def __get_localname(tag):
        qname = etree.QName(tag)
        return qname.localname

    def parse_extension_elem(self, attrib):
        name = attrib['name']
        prefix = attrib['prefix']
        uri = urlparse(attrib['uri'])

        self.__extensions[name] = (name, prefix, uri)

    def parse_classifier_elem(self, attrib):
        name = attrib['name']
        keys = attrib['keys']

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

        known_keys = set(self.__global_event_attribs.keys())
        # logger.debug('Known classifier keys: {}'.format(known_keys))

        keylist = get_keylist(keys, known_keys)
        self.__classifiers[name] = keylist

    def start(self, tag, attrib_dict):
        localname = self.__get_localname(tag).lower()
        # logger.debug('start {} {}'.format(localname, attrib_dict))
        if localname not in [LITERAL, TIMESTAMP, DISCRETE, CONTINUOUS, LIST, CONTAINER]:
            if localname == EVENT:
                self.__event = dict()
                self.__attributable_stack.append(self.__event)
            elif localname == TRACE:
                self.__trace = dict()
                self.__attributable_stack.append(self.__trace)
            elif localname == LOG:
                # make the xes attributes
                self.__xes_attribs = dict(attrib_dict)
                self.__attributable_stack.append(self.__log_attribs)
            elif localname == EXTENSION:
                self.parse_extension_elem(attrib_dict)
            elif localname == GLOBAL:
                scope = attrib_dict['scope']

                if scope.lower() == TRACE:
                    self.__globals = self.__global_trace_attribs
                elif scope.lower() == EVENT:
                    self.__globals = self.__global_event_attribs

            elif localname == CLASSIFIER:
                self.parse_classifier_elem(attrib_dict)
        else:
            # it's an attribute
            key = attrib_dict.get('key', 'UNKNOWN')
            value = attrib_dict.get('value', '')

            attrib = None

            if localname == LITERAL:
                attrib = (key, value)
                if self.__trace is not None and key == 'concept:name' and self.__event is None:
                    # record caseid
                    self.__caseid = value

            elif localname == TIMESTAMP:
                time = cvrn.parse_timestamp(value)
                attrib = (key, time)

            elif localname == DISCRETE:
                try:
                    int_value = int(value)
                except ValueError as e:
                    logger.error('Cannot convert {} as int: {}'.format(value, e))
                    int_value = 0
                attrib = (key, int_value)

            elif localname == CONTINUOUS:
                try:
                    float_value = float(value)
                except ValueError as e:
                    logger.error('Cannot convert {} as float: {}'.format(value, e))
                    float_value = 0.
                attrib = (key, float_value)

            elif localname == BOOLEAN:
                bool_value = True if value.lower() == 'true' else False
                attrib = (key, bool_value)

            elif localname == ID:
                try:
                    id_value = uuid.UUID(value)
                except ValueError as e:
                    logger.error('Cannot convert {} as id: {}'.format(value, e))
                    id_value = value
                attrib = (key, id_value)

            elif localname == LIST:
                logger.warning('Not supporting list attributes')

            elif localname == CONTINUOUS:
                logger.warning('Not supporting container attributes')

            if attrib is not None:
                self.__attribute_stack.append(attrib)

    def end(self, tag):
        localname = self.__get_localname(tag).lower()
        # logger.debug('end {}'.format(localname))

        if localname == GLOBAL:
            self.__globals = None

        elif localname not in [LITERAL, TIMESTAMP, DISCRETE, CONTINUOUS, BOOLEAN, ID, LIST, CONTAINER]:
            if localname == EVENT:
                self.__event[const.CASEID] = self.__caseid
                self.__event_df_dict[self.__event_ind] = self.__event
                self.__event_ind += 1
                self.__event = None
                self.__attributable_stack.pop()

            elif localname == TRACE:
                self.__trace_df_dict[self.__trace_ind] = self.__trace
                self.__trace_ind += 1
                self.__trace = None
                self.__attributable_stack.pop()

            elif localname == LOG:
                self.__attributable_stack.pop()

        else:
            key, value = self.__attribute_stack.pop()

            if self.__globals is not None:
                self.__globals[key] = value

            else:
                self.__attributable_stack[-1][key] = value

    def data(self, data):
        # logger.debug('data {}'.format(data))
        pass

    def comment(self, text):
        # logger.debug('comment {}'.format(text))
        pass

    def close(self):
        # logger.debug('close')

        event_df = pd.DataFrame.from_dict(self.__event_df_dict, 'index')
        trace_df = pd.DataFrame.from_dict(self.__trace_df_dict, 'index')

        lt = tble.LogTable(
            trace_df=trace_df,
            event_df=event_df,
            attributes=self.__log_attribs,
            global_trace_attributes=self.__global_trace_attribs,
            global_event_attributes=self.__global_event_attribs,
            classifiers=self.__classifiers,
            extensions=self.__extensions
        )

        lt.xes_attributes = self.__xes_attribs

        return lt
