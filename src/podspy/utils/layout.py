#!/usr/bin/env python

"""This is the layout utils module.

This module contains useful methods related to layout
"""


import logging


logger = logging.getLogger(__file__)


def get_layout_ele(element, layout, default=None):
    l_element = default
    # either node or edge
    if layout.get_node(element):
        l_element = layout.get_node(element)
    elif layout.get_edge(element.src, element.target, key=element):
        l_element = layout.get_edge(element.src, element.target, key=element)
    return l_element


def get_width(element, layout, default=0.):
    if element is None or layout is None:
        return default

    l_element = get_layout_ele(element, layout)

    if l_element and 'width' in l_element.attr:
        try:
            width = float(l_element.attr['width'])
        except Exception as e:
            logger.error(e)
            width = default
    else:
        width = default

    return width


def get_height(element, layout, default=0.):
    if element is None or layout is None:
        return default

    l_element = get_layout_ele(element, layout)

    if l_element and 'height' in l_element.attr:
        try:
            height = float(l_element.attr['height'])
        except Exception as e:
            logger.error(e)
            height = default
    else:
        height = default

    return height


def get_node_pos(element, layout, default=(10., 10.)):
    if element is None or layout is None:
        return default
    l_element = layout.get_node(element)
    if 'pos' in l_element.attr:
        pos = tuple(map(float, l_element.attr['pos'].split(',')))
    else:
        pos = default
    return pos


def get_edge_points(element, layout):
    points = []

    if element is None or layout is None:
        return points

    l_element = layout.get_edge(element.src, element.target, key=element)

    if 'pos' in l_element.attr:
        # check out: https://graphviz.gitlab.io/_pages/doc/info/attrs.html#k:splineType
        pos_str = l_element.attr['pos'].split(' ')
        start_x, start_y = None, None
        end_x, end_y = None, None
        if 'e' in pos_str[0]:
            # edge end point is given
            end_x, end_y = pos_str[0].split(',')[1:]
            pos_str = pos_str[1:]
        if len(pos_str) > 0 and 's' in pos_str[0]:
            start_x, start_y = pos_str[0].split(',')[1:]
            pos_str = pos_str[1:]
        # the rest of the edge points
        for pos_i in pos_str:
            x, y = pos_i.split(',')
            points = points + [(x, y), ]

        # add back start and end points
        if end_x and end_y:
            points = points + [(end_x, end_y), ]
        if start_x and start_y:
            points = [(start_x, start_y), ] + points

        # converting everything to floats
        has_err = False
        for i in range(len(points)):
            point_i = points[i]
            try:
                points[i] = (float(point_i[0]), float(point_i[1]))
            except Exception as e:
                logger.error('Convert {} as float: {}'.format(point_i, e))
                has_err = True  # default to empty list with error

        if has_err:
            points = []

    return points
