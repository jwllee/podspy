#!/usr/bin/env python

"""This is the petri net visualize module.

This module contains classes to visualize petri nets.
"""


import pygraphviz as pgv
import logging
import itertools as its
from podspy.petrinet import nets as nts
from podspy.petrinet import semantics as smc


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


logger = logging.getLogger(__file__)


def export_graphviz(net, out_file='net.dot', marking=None, layout='dot'):
    """Export petri nets as graphviz dot files. Function name follows sklearn.tree.export_graphviz api.

    :param net: petri net to convert as dot file
    :param out_file: file to write to
    :param marking: the current marking of the net
    :param layout: layout program
    :return: graphviz graph
    """
    G = net2dot(net, marking=marking, layout=layout)
    G.write(out_file)
    return G


def add_trans_to_dotgraph(t, G):
    """Add :class:`Transition` to graphviz :class:`AGraph`

    :param t: transition to add
    :param G: graph where transition is to be added
    :return: graph node
    """
    attrs = {
        'label': t.label,
        'shape': 'square',
    }

    G.add_node(t, **attrs)
    n = G.get_node(t)

    if t.is_invisible:
        n.attr['color'] = 'black'
        n.attr['style'] = 'filled'

    return n


def add_place_to_dotgraph(p, G, token=0):
    """Add :class:`Place` to graphviz :class:`AGraph`

    :param p: place to add
    :param G: graph where place is to be added
    :param token: number of tokens in place
    :return: graph node
    """
    attrs = {
        'shape': 'circle',
        'label': ''
    }

    G.add_node(p, **attrs)
    n = G.get_node(p)

    if token > 0:
        n.attr['label'] = token

    return n


def add_arc_to_dotgraph(a, G):
    """Add :class:`Arc` to graphviz :class:`AGraph`

    :param a: arc to add
    :param G: graph where arc is to be added
    :return: graph edge
    """
    # see arrow types @ http://www.graphviz.org/doc/info/attrs.html#d:ratio
    attrs = {
        'color': 'black',
        'arrowType': 'normal',
        'dir': 'forward'
    }
    G.add_edge(a.src, a.target, key=a, **attrs)
    e = G.get_edge(a.src, a.target, key=a)

    # only add edge weight as label if the weight is larger than 1
    if a.weight > 1:
        e.attr['label'] = a.weight

    return e


def add_inhibitor_arc_to_dotgraph(a, G):
    """Add :class:`InhibitorArc` to graphviz :class:`AGraph`

    :param a: inhibitor arc to add
    :param G: graph where arc is to be added
    :return: graph edge
    """
    attrs = {
        'color': 'black',
        'arrowType': 'odot',
        'dir': 'forward'
    }
    G.add_edge(a.src, a.target, key=a, **attrs)
    e = G.get_edge(a.src, a.target, key=a)

    return e


def add_reset_arc_to_dotgraph(a, G):
    """Add :class:`ResetArc` to graphviz :class:`AGraph`

    :param a: reset arc to add
    :param G: graph where arc is to be added
    :return: graph edge
    """
    attrs = {
        'color': 'black',
        'arrowType': 'vee',
        'dir': 'forward'
    }
    G.add_edge(a.src, a.target, key=a, **attrs)
    e = G.get_edge(a.src, a.target, key=a)

    return e


def net2dot(net, marking=None, layout='dot', rankdir='LR'):
    """Convert petri net to graphviz :class:`AGraph`. Petri net should be subclass of
    :class:`AbstractResetInhibitorNet`

    :param net: petri net to convert
    :param marking: current marking of net
    :param layout: layout program
    :param rankdir: layout orientation of the graph
    :return: converted graph
    """
    # possible rankdir: TB, LR, BT, RL
    G = pgv.AGraph(rankdir=rankdir)

    # add transitions
    for t in net.transitions:
        add_trans_to_dotgraph(t, G)

    # add places
    for p in net.places:
        token = 0
        if marking:
            token = marking.occurrences(p)

        add_place_to_dotgraph(p, G, token)

    # add edges
    for a in net.arcs:
        # logger.debug('Adding {!s}'.format(a))
        add_arc_to_dotgraph(a, G)

    for a in net.reset_arcs:
        add_reset_arc_to_dotgraph(a, G)

    for a in net.inhibitor_arcs:
        add_inhibitor_arc_to_dotgraph(a, G)

    G.layout(prog=layout)
    return G


def netarray2dot(nets, layout='dot', rankdir='LR', node_constraints=list(), constraint_style='invis'):
    """

    :param nets:
    :param node_constraints: list of node tuples where the nodes of each tuple should be connected
                             by edge constraint
    :param constraint_style: node constraint edge line style
    :return: converted graph
    """
    G = pgv.AGraph(rankdir=rankdir)

    for net in nets:
        init, finals = smc.Marking(), set()

        if isinstance(net, nts.AcceptingPetrinet):
            net, init, finals = net

        for t in net.transitions:
            add_trans_to_dotgraph(t, G)

        for p in net.places:
            token = init.occurrences(p)
            add_place_to_dotgraph(p, G, token)

        for a in net.arcs:
            add_arc_to_dotgraph(a, G)

        for a in net.reset_arcs:
            add_reset_arc_to_dotgraph(a, G)

        for a in net.inhibitor_arcs:
            add_inhibitor_arc_to_dotgraph(a, G)

    for group in node_constraints:
        # add edges between transitions with the same label
        for node_pair in its.combinations(group, 2):
            n0, n1 = node_pair
            attrs = {
                'style': constraint_style,
                'len': 10,
            }
            arc_name = '{}-{}'.format(n0.label, n1.label)
            G.add_edge(n0, n1, key=arc_name, **attrs)

    G.layout(prog=layout)
    return G
