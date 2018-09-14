#!/usr/bin/env python3


import logging
import itertools as itrs
import pygraphviz as pgv
from podspy import graph, petrinet


__all__ = [
    'to_agraph'
]


logger = logging.getLogger(__file__)


def get_trans_info(t):
    """Get node information about transition to draw it using graphviz

    :param t: transition
    :return: node_id, node_attribs
    """
    assert isinstance(t, petrinet.Transition)

    _id = str(t._id)
    attribs = {
        'label': t.label,
        'shape': 'square'
    }

    if graph.constants.POSITION in t.attribs:
        attribs['pos'] = t.attribs.get(graph.constants.POSITION)

    if t.is_invisible:
        attribs['color'] = 'black'
        attribs['style'] = 'filled'

    return _id, attribs


def get_place_info(p):
    """Get node information about place to draw it using graphviz

    :param p: place
    :return: node_id, node_attribs
    """
    assert isinstance(p, petrinet.Place)

    _id = str(p._id)
    attribs = {
        'shape': 'circle',
        'label': ''
    }

    if graph.constants.POSITION in p.attribs:
        attribs['pos'] = p.attribs.get(graph.constants.POSITION)
    return _id, attribs


def get_arc_info(a):
    """Get edge information about arc to draw it using graphviz

    :param a: arc
    :return: edge_id, src, target, edge_attribs
    """
    assert isinstance(a, petrinet.Arc)

    src_id, target_id = str(a.src._id), str(a.target._id)
    _id = '{}->{}'.format(src_id, target_id)
    attribs = {
        'color': 'black',
        'arrowType': 'normal',
        'dir': 'forward'
    }

    if a.weight > 1:
        attribs['label'] = str(a.weight)

    return _id, src_id, target_id, attribs


def get_inhibitor_arc_info(a):
    """Get edge information about inhibitor arc to draw it using graphviz

    :param a: inhibitor arc
    :return: edge_id, src, target, edge_attribs
    """
    assert isinstance(a, petrinet.InhibitorArc)

    src_id, target_id = str(a.src._id), str(a.target._id)
    _id = '{}->{}'.format(src_id, target_id)
    attribs = {
        'color': 'black',
        'arrowType': 'odot',
        'dir': 'forward'
    }
    return _id, src_id, target_id, attribs


def get_reset_arc_info(a):
    """Get edge information about reset arc to draw it using graphviz

    :param a: reset arc
    :return: edge_id, src, target, edge_attribs
    """
    assert isinstance(a, petrinet.ResetArc)

    src_id, target_id = str(a.src._id), str(a.target._id)
    _id = '{}->{}'.format(src_id, target_id)
    attribs = {
        'color': 'black',
        'arrowType': 'vee',
        'dir': 'forward'
    }
    return _id, src_id, target_id, attribs


def get_node_info(node):
    if isinstance(node, petrinet.Transition):
        return get_trans_info(node)
    elif isinstance(node, petrinet.Place):
        return get_place_info(node)
    else:
        raise ValueError('{} not a transition nor place'.format(node))


def get_edge_info(edge):
    if isinstance(edge, petrinet.Arc):
        return get_arc_info(edge)
    elif isinstance(edge, petrinet.InhibitorArc):
        return get_inhibitor_arc_info(edge)
    elif isinstance(edge, petrinet.ResetArc):
        return get_reset_arc_info(edge)
    else:
        raise ValueError('Do not recognize edge type: {}'.format(type(edge)))


def add_token(A, p, marking):
    token = marking.occurrences(p)

    if token > 0:
        node_id, _ = get_place_info(p)
        node = A.get_node(node_id)
        node.attr['label'] = str(token)


def net_to_agraph(net, marking=None):
    """Convert petri net to AGraph

    :param net: petri net
    :param marking: current marking of petri net
    :return: graphviz graph
    """
    A = graph.ps_agraph.to_agraph(net, node_func=get_node_info, edge_func=get_edge_info)

    if marking is not None:
        # add tokens from current marking
        for p in net.places:
            add_token(A, p, marking)

    return A


def color_place(A, p, color):
    """Color a place with specific color

    :param A: graphviz AGraph
    :param p: place
    :param color: color
    """
    node_id, _ = get_place_info(p)
    node = A.get_node(node_id)
    node.attr['style'] = 'filled'
    node.attr['fillcolor'] = color


def apn_to_agraph(apn, marking=None):
    """Convert an accepting petri net into graphviz AGraph

    :param apn: accepting petri net
    :param marking: current marking
    :return: graphviz graph
    """
    net, init_marking, final_markings = apn
    A = net_to_agraph(net, marking=marking)

    assert isinstance(init_marking, petrinet.Marking)

    logger.debug('Adding initial and final markings')

    for p in init_marking:
        color_place(A, p, 'limegreen')

        if marking is None:
            # assume we are at the initial marking if no marking is provided
            add_token(A, p, init_marking)

    for final_marking in final_markings:
        for p in final_marking:
            color_place(A, p, 'orangered')

    return A


def narray_to_agraph(narray, nconstraints=list(), cstyle='invis'):
    """Convert an array of petri nets to graphviz graph

    :param narray: an array of petri nets
    :param nconstraints: nodes to add edge constraints between
    :param cstyle: constraint edge style
    :return: graphviz graph
    """
    A = to_agraph(narray[0])

    for i in range(1, len(narray)):
        net = narray[i]

        if isinstance(net, petrinet.AcceptingPetrinet):
            net, init_marking, final_markings = net
        else:
            init_marking, final_markings = None, None

        # add net info to A
        for t in net.transitions:
            node_id, node_attribs = get_node_info(t)
            A.add_node(node_id, **node_attribs)

        for p in net.places:
            node_id, node_attribs = get_node_info(p)
            A.add_node(node_id, **node_attribs)

        for a in net.arcs:
            edge_id, src, target, edge_attribs = get_edge_info(a)
            A.add_edge(src, target, key=edge_id, **edge_attribs)

        for a in net.reset_arcs:
            edge_id, src, target, edge_attribs = get_edge_info(a)
            A.add_edge(src, target, key=edge_id, **edge_attribs)

        for a in net.inhibitor_arcs:
            edge_id, src, target, edge_attribs = get_edge_info(a)
            A.add_edge(src, target, key=edge_id, **edge_attribs)

        for p in init_marking:
            color_place(A, p, 'limegreen')
            add_token(A, p, init_marking)

        for final_marking in final_markings:
            for p in final_marking:
                color_place(A, p, 'orangered')

    # add node constraints
    for group in nconstraints:
        for pair in itrs.combinations(group, 2):
            n0, n1 = pair
            node_id_0, node_attribs_0 = get_node_info(n0)
            node_id_1, node_attribs_1 = get_node_info(n1)

            attribs = {
                'style': cstyle,
                'len': 10,
                'dir': 'none'
            }
            edge_id = '{}->{}'.format(node_id_0, node_id_1)
            A.add_edge(node_id_0, node_id_1, key=edge_id, **attribs)

    return A


def to_agraph(net, marking=None, **kwargs):
    """Convert petri net to graphviz :class:`AGraph`. Petri net should be subclass of
    :class:`AbstractResetInhibitorNet`

    :param net: petri net, accepting petri net, or net array
    :param marking: current marking of net
    :return: agraph
    """
    if isinstance(net, petrinet.AcceptingPetrinet):
        return apn_to_agraph(net, marking)
    elif isinstance(net, petrinet.nets.AbstractResetInhibitorNet):
        return net_to_agraph(net, marking)
    elif isinstance(net, list):
        return narray_to_agraph(net, **kwargs)
    else:
        raise ValueError('Do not recognize net type of {}'.format(type(net)))
