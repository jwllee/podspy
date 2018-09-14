#!/usr/bin/env python

"""This is the conversion module.

This module contains useful conversion methods
"""

from datetime import datetime, timezone, timedelta
import logging


logger = logging.getLogger(__file__)


def inch2point(inch):
    return inch * 72


def point2inch(point):
    return point / 72


def parse_timestamp(timestamp):

    try:
        relative_zone = ''

        if 'z' in timestamp:
            timestamp = timestamp.replace('z', '')
            relative_zone = 'z'
        elif '+' in timestamp:
            relative_zone = timestamp[timestamp.index('+'):]
            timestamp = timestamp[:timestamp.index('+')]
        elif '-' in timestamp[::-1][:7]:
            timestamp = timestamp[::-1]
            relative_zone = timestamp[:timestamp.index('-') + 1]
            timestamp = timestamp[timestamp.index('-') + 1:]
            relative_zone = relative_zone[::-1]
            timestamp = timestamp[::-1]

        if relative_zone != 'z' and relative_zone != '':
            hours, minutes = relative_zone.split(':')
            if '-' in hours:
                minutes = int(minutes) * -1
        else:
            hours = 0
            minutes = 0

        if '.' in timestamp:
            time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')

        time = time.replace(tzinfo=timezone(timedelta(minutes=int(minutes), hours=int(hours))))
        return time

    except ValueError as e:
        logger.error(e)
        return None
