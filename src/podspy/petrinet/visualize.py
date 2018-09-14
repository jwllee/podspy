#!/usr/bin/env python

"""This is the petri net visualize module.

This module contains classes to visualize petri nets.
"""


import pygraphviz as pgv
import logging
import itertools as its
from podspy.petrinet import nets as nts
from podspy.petrinet import semantics as smc
from collections import namedtuple


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


def add_trans_to_dotgraph(t, node_id, G):
    """Add :class:`Transition` to graphviz :class:`AGraph`

    :param t: transition to add
    :param G: graph where transition is to be added
    :param node_id: node id used for identifying transition in AGraph
    :return: graph node
    """
    attrs = {
        'label': t.label,
        'shape': 'square',
    }

    if t.is_invisible:
        attrs['color'] = 'black'
        attrs['style'] = 'filled'

    G.add_node(node_id, **attrs)
    n = G.get_node(node_id)

    # if t.is_invisible:
    #     n.attr['color'] = 'black'
    #     n.attr['style'] = 'filled'

    return n


def add_place_to_dotgraph(p, node_id, G, token=0):
    """Add :class:`Place` to graphviz :class:`AGraph`

    :param p: place to add
    :param G: graph where place is to be added
    :param token: number of tokens in place
    :param node_id: node id used for identifying place in AGraph
    :return: graph node
    """
    attrs = {
        'shape': 'circle',
        'label': ''
    }

    G.add_node(node_id, **attrs)
    n = G.get_node(node_id)

    if token > 0:
        n.attr['label'] = token

    return n


def add_arc_to_dotgraph(src, target, weight, edge_id, G):
    """Add :class:`Arc` to graphviz :class:`AGraph`

    :param G: graph where arc is to be added
    :param src: arc source
    :param target: arc target
    :param weight: arc weight
    :param edge_id: edge id used for identifying arc in AGraph
    :return: graph edge
    """
    # see arrow types @ http://www.graphviz.org/doc/info/attrs.html#d:ratio
    attrs = {
        'color': 'black',
        'arrowType': 'normal',
        'dir': 'forward'
    }
    # edge_id = id_func(a)
    G.add_edge(src, target, key=edge_id, **attrs)
    e = G.get_edge(src, target, key=edge_id)

    # only add edge weight as label if the weight is larger than 1
    if weight > 1:
        e.attr['label'] = weight

    return e


def add_inhibitor_arc_to_dotgraph(src, target, edge_id, G):
    """Add :class:`InhibitorArc` to graphviz :class:`AGraph`

    :param src: arc source
    :param target: arc target
    :param edge_id: edge id used for identifying arc in AGraph
    :param G: graph where arc is to be added
    :return: graph edge
    """
    attrs = {
        'color': 'black',
        'arrowType': 'odot',
        'dir': 'forward'
    }
    G.add_edge(src, target, key=edge_id, **attrs)
    e = G.get_edge(src, target, key=edge_id)

    return e


def add_reset_arc_to_dotgraph(src, target, edge_id, G):
    """Add :class:`ResetArc` to graphviz :class:`AGraph`

    :param src: arc source
    :param target: arc target
    :param edge_id: edge id used for identifying arc in AGraph
    :param G: graph where arc is to be added
    :return: graph edge
    """
    attrs = {
        'color': 'black',
        'arrowType': 'vee',
        'dir': 'forward'
    }
    G.add_edge(src, target, key=edge_id, **attrs)
    e = G.get_edge(src, target, key=edge_id)

    return e


def net2dot(net, marking=None, layout='dot', rankdir='LR', node_id_func=None, edge_id_func=None):
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

    default_node_id_func = lambda n: str(n._id)
    default_edge_id_func = lambda e: '{}->{}'.format(str(e.src._id), str(e.target._id))

    node_id_func = default_node_id_func if node_id_func is None else node_id_func
    edge_id_func = default_edge_id_func if edge_id_func is None else edge_id_func

    # add transitions
    for t in net.transitions:
        node_id = node_id_func(t)
        add_trans_to_dotgraph(t, node_id, G)

    # add places
    for p in net.places:
        node_id = node_id_func(p)
        token = 0
        if marking:
            token = marking.occurrences(p)

        add_place_to_dotgraph(p, node_id, G, token)

    # add edges
    for a in net.arcs:
        # logger.debug('Adding {!s}'.format(a))
        src, target, weight = node_id_func(a.src), node_id_func(a.target), a.weight
        edge_id = edge_id_func(a)
        add_arc_to_dotgraph(src, target, weight, edge_id, G)

    for a in net.reset_arcs:
        src, target = node_id_func(a.src), node_id_func(a.target)
        edge_id = edge_id_func(a)
        add_reset_arc_to_dotgraph(src, target, edge_id, G)

    for a in net.inhibitor_arcs:
        src, target = node_id_func(a.src), node_id_func(a.target)
        edge_id = edge_id_func(a)
        add_inhibitor_arc_to_dotgraph(src, target, edge_id, G)

    G.layout(prog=layout)
    return G


def netarray2dot(nets, layout='dot', rankdir='LR', node_id_func=None, edge_id_func=None,
                 node_constraints=list(), constraint_style='invis'):
    """

    :param nets:
    :param node_constraints: list of node tuples where the nodes of each tuple should be connected
                             by edge constraint
    :param constraint_style: node constraint edge line style
    :return: converted graph
    """
    G = pgv.AGraph(rankdir=rankdir)

    default_node_id_func = lambda n: str(n._id)
    default_edge_id_func = lambda e: '{}->{}'.format(str(e.src._id), str(e.target._id))

    node_id_func = default_node_id_func if node_id_func is None else node_id_func
    edge_id_func = default_edge_id_func if edge_id_func is None else edge_id_func

    for net in nets:
        init, finals = smc.Marking(), set()

        if isinstance(net, nts.AcceptingPetrinet):
            net, init, finals = net

        for t in net.transitions:
            node_id = node_id_func(t)
            add_trans_to_dotgraph(t, node_id, G)

        for p in net.places:
            node_id = node_id_func(p)
            token = init.occurrences(p)
            add_place_to_dotgraph(p, node_id, G, token)

        for a in net.arcs:
            src, target, weight = str(a.src._id), str(a.target._id), a.weight
            edge_id = edge_id_func(a)
            add_arc_to_dotgraph(src, target, weight, edge_id, G)

        for a in net.reset_arcs:
            src, target = node_id_func(a.src), node_id_func(a.target)
            edge_id = edge_id_func(a)
            add_reset_arc_to_dotgraph(src, target, edge_id, G)

        for a in net.inhibitor_arcs:
            src, target = node_id_func(a.src), node_id_func(a.target)
            edge_id = edge_id_func(a)
            add_inhibitor_arc_to_dotgraph(src, target, edge_id, G)

    ArcTuple = namedtuple('ArcTuple', ['src', 'target'])

    for group in node_constraints:
        # add edges between transitions with the same label
        for node_pair in its.combinations(group, 2):
            n0, n1 = node_pair
            arc_tuple = ArcTuple(n0, n1)
            attrs = {
                'style': constraint_style,
                'len': 10,
            }
            edge_id = edge_id_func(arc_tuple)
            n0_id = node_id_func(n0)
            n1_id = node_id_func(n1)
            G.add_edge(n0_id, n1_id, key=edge_id, **attrs)

    G.layout(prog=layout)
    return G
