#!/usr/bin/env python

"""This is the io module.

This module reads log files.
"""

import logging, uuid, time, os, ciso8601, enum
from lxml import etree
from . import constants as const
from . import table as tble
from podspy.utils import conversion as cvrn
from . import utils as log_utils
from urllib.request import urlparse
import pandas as pd


logger = logging.getLogger(__file__)


__all__ = [
    'ImportMode',
    'import_log_table'
]


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


class ImportMode(enum.Enum):
    ALL = 0
    BASIC = 1

    def get_include_attribs(self):
        if self == ImportMode.ALL:
            return None
        elif self == ImportMode.BASIC:
            return {
                EVENT: { 'concept:name', 'org:resource', 'time:timestamp', 'lifecycle:transition' },
                TRACE: { 'concept:name' },
                LOG: {}
            }
        else:
            return None


def import_log_table(fp, caseid_key='concept:name', import_mode=ImportMode.BASIC, include_attribs=None):
    """Import a xes file as log table

    :param fp: file path to the XES file
    :param caseid_key: trace attribute key that allows identification of a unique trace
    :param import_mode: import mode, quick way to limit the event, trace, and log attributes to import for memory reason
    :param include_attribs: event, trace, and log attribute sets to include, require all three if this is not None. For
    example, d = { 'event': { 'e_a0', 'e_a1' }, 'trace': { 't_a0', 't_a1' }, 'log': { 'l_a0', 'l_a1' }}
    :type include_attribs: dict that maps strings to sets or None
    :return: LogTable
    """

    start = time.time()

    import_mode_attribs = import_mode.get_include_attribs()

    if include_attribs is not None:
        if import_mode_attribs is not None:
            include_attribs[EVENT] = include_attribs.get(EVENT, set()).union(import_mode_attribs[EVENT])
            include_attribs[TRACE] = include_attribs.get(TRACE, set()).union(import_mode_attribs[TRACE])
            include_attribs[LOG] = include_attribs.get(LOG, set()).union(import_mode_attribs[LOG])
    else:
        include_attribs = import_mode_attribs

    lt = import_log_table_iterparse(fp, caseid_key, include_attribs)

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
        logger.debug('start {} {}'.format(localname, attrib_dict))
        if localname not in [LITERAL, TIMESTAMP, DISCRETE, BOOLEAN, CONTINUOUS, ID, LIST, CONTAINER]:
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
                attrib = (None, None)

            elif localname == CONTAINER:
                logger.warning('Not supporting container attributes')
                attrib = (None, None)

            if attrib is not None:
                self.__attribute_stack.append(attrib)

    def end(self, tag):
        localname = self.__get_localname(tag).lower()
        logger.debug('end {}'.format(localname))

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

            if key is None and value is None:
                return

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


def is_attrib(tag):
    return tag.endswith((
        LITERAL, TIMESTAMP, DISCRETE, BOOLEAN, CONTINUOUS, ID, LIST, CONTAINER
    ))


def process_attributable(elem, to_include=None):
    result = dict()
    for child in elem:
        tag = child.tag.lower()

        if not is_attrib(tag):
            continue

        key = child.get('key', 'UNKNOWN')
        value = child.get('value', '')

        if to_include is not None and key not in to_include:
            continue

        if tag.endswith(LITERAL):
            result[key] = value
        elif tag == TIMESTAMP:
            time_value = ciso8601.parse_datetime(value)
            result[key] = time_value
        elif tag.endswith(DISCRETE):
            try:
                int_value = int(value)
            except ValueError as e:
                logger.error('Cannot convert {} with discrete value {}: {}'.format(key, value, e))
                int_value = 0
            result[key] = int_value
        elif tag.endswith(CONTINUOUS):
            try:
                float_value = float(value)
            except ValueError as e:
                logger.error('Cannot convert {} with continuous value {}: {}'.format(key, value, e))
                float_value = 0.
            result[key] = float_value
        elif tag.endswith(BOOLEAN):
            bool_value = True if value.lower() == 'true' else False
            result[key] = bool_value
        elif tag.endswith(ID):
            try:
                id_value = uuid.UUID(value)
            except ValueError as e:
                logger.error('Cannot convert {} with ID value {}: {}'.format(key, value, e))
                id_value = value
            result[key] = id_value
        elif tag.endswith(LIST):
            logger.warning('Not supporting list attribute: {}'.format(key))
        elif tag.endswith(CONTAINER):
            logger.warning('Not supporting container attribute: {}'.format(key))
    return result


def process_extension(elem):
    name = elem.get('name')
    prefix = elem.get('prefix')
    uri = urlparse(elem.get('uri'))
    return name, prefix, uri


def process_classifier(elem, global_event_attrib_keys):
    name = elem.get('name')
    keys = elem.get('keys')
    key_list = list()

    for key in global_event_attrib_keys:
        if key in keys:
            keys = keys.replace(key, '')
            key_list.append(key)

    return name, key_list


def import_log_table_iterparse(fp, caseid_key, include_attribs=None):
    """
    https://www.ibm.com/developerworks/xml/library/x-hiperfparse/

    :param fp: file path to XES log file
    :param caseid_key: attribute key for trace caseid
    :param include_attribs: dict of string to string set mapping of attributes to include
    :return: LogTable
    """

    log_attrib_dict = dict()
    global_trace_attrib_dict = dict()
    global_event_attrib_dict = dict()
    xes_attrib_dict = dict()
    classifier_dict = dict()
    extension_dict = dict()

    # decompress compressed file if necessary
    fp_final = log_utils.temp_decompress(fp) if fp.endswith('.gz') else fp

    to_include_event = include_attribs.get(EVENT, None) if include_attribs is not None else None
    to_include_trace = include_attribs.get(TRACE, None) if include_attribs is not None else None
    to_include_log = include_attribs.get(LOG, None) if include_attribs is not None else None

    use_caseid_key = to_include_trace is None or caseid_key in to_include_trace

    tag = [ EVENT, TRACE, LOG, CLASSIFIER, EXTENSION, GLOBAL ]
    # ignore namespace
    tag = list(map(lambda t: '{*}' + t, tag))
    context = etree.iterparse(fp_final, events=('end',), tag=tag)

    # temporary variables
    trace_ind, trace_start_ind, trace_end_ind = 0, 0, 0
    trace_events = list()
    traces = list()

    start = time.time()
    for event, elem in context:
        tag = elem.tag.lower()

        if tag.endswith(EVENT):
            # event row is a dict
            event_row = process_attributable(elem, to_include_event)
            trace_events.append(event_row)
            trace_end_ind += 1

        elif tag.endswith(TRACE):
            # trace row is a dict
            trace_row = process_attributable(elem, to_include_trace)
            caseid = trace_row.get(caseid_key, None) if use_caseid_key else trace_ind
            caseid = trace_ind if caseid is None else caseid
            trace_row[const.CASEID] = caseid
            traces.append(trace_row)

            # add back the caseids to the corresponding events
            for i in range(trace_start_ind, trace_end_ind):
                trace_events[i][const.CASEID] = caseid

            # increment trace index
            trace_ind += 1
            trace_start_ind = trace_end_ind

        elif tag.endswith(LOG):
            for key, value in elem.items():
                xes_attrib_dict[key] = value
            log_attrib_dict = process_attributable(elem, to_include_log)

        elif tag.endswith(EXTENSION):
            extension = process_extension(elem)
            extension_dict[extension[0]] = extension

        elif tag.endswith(CLASSIFIER):
            classifier_name, classifier_keys = process_classifier(elem, global_event_attrib_dict)
            classifier_dict[classifier_name] = classifier_keys

        elif tag.endswith(GLOBAL):
            scope = elem.get('scope')
            if scope.lower() == TRACE:
                global_trace_attrib_dict = process_attributable(elem)
            else: # scope == event
                global_event_attrib_dict = process_attributable(elem)

        # It's safe to call clear() here because no descendants will be
        # accessed
        elem.clear()

        # # Also eliminate now-empty references from the root node to elem
        if tag.endswith(TRACE):
            while elem.getprevious() is True:
                prev_sibling = elem.getprevious()
                if not is_attrib(prev_sibling.tag.lower()):
                    elem.getparent().remove(prev_sibling)
                else:
                    break

    end = time.time()
    logger.info('Parsing log took {:.2f}s'.format(end - start))

    del context

    if fp.endswith('.gz'):
        os.remove(fp_final)

    event_df = pd.DataFrame(trace_events)
    trace_df = pd.DataFrame(traces)

    lt = tble.LogTable(
        trace_df=trace_df,
        event_df=event_df,
        attributes=log_attrib_dict,
        global_event_attributes=global_event_attrib_dict,
        global_trace_attributes=global_trace_attrib_dict,
        classifiers=classifier_dict,
        extensions=extension_dict
    )

    return lt
