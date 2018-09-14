#!/usr/bin/env python3


from podspy import graph


__all__ = [
    'to_agraph'
]


def to_agraph(G, node_func=None, edge_func=None):
    """Returns a pygraphviz graph from a podspy graph. This is largely based on NetworkX's
    design, except that here a node and edge function are also required since potentially there are
    different types of nodes and edges.

    :param G: graph
    :param node_func: function that returns node_id, and node_attribs given a node
    :param edge_func: function that returns edge_id, source, target, and edge_attribs given an edge
    :return: a pygraphviz graph
    """
    try:
        import pygraphviz as pgv
    except ImportError:
        raise ImportError('requires pygraphviz http://graphviz.github.io')

    assert isinstance(G, graph.base.AbstractGraph)

    directed = isinstance(G, graph.directed.AbstractDirectedGraph)

    A = pgv.AGraph(name=G.label, directed=directed)

    graph_attribs = G.attribs.get(graph.constants.GRAPH, {})
    node_attribs = G.attribs.get(graph.constants.NODE, {})
    edge_attribs = G.attribs.get(graph.constants.EDGE, {})

    A.graph_attr.update(graph_attribs)
    A.node_attr.update(node_attribs)
    A.edge_attr.update(edge_attribs)

    for n in G.get_nodes():
        node_id, node_attribs = node_func(n)
        A.add_node(node_id, **node_attribs)

    for e in G.get_edges():
        edge_id, src, target, edge_attribs = edge_func(e)
        A.add_edge(src, target, key=edge_id, **edge_attribs)

    return A
