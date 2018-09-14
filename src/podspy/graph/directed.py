#!/usr/bin/env python

"""This is the directed graph module.

This module contains directed graph classes.
"""

from abc import ABC, abstractmethod
from podspy.graph import base


class AbstractDirectedGraphEdge(base.AbstractGraphEdge):
    @abstractmethod
    def __init__(self, src, target, *args, **kwargs):
        super().__init__(src, target, *args, **kwargs)
        assert src.graph == target.graph, \
            'source graph {} differs to target graph {}'.format(src.graph,
                                                                target.graph)
        self.graph = src.graph

    def __eq__(self, other):
        equal = super().__eq__(other)
        return equal and self.graph == other.graph

    def __hash__(self):
        # need to override hash method if __eq__ is overridden
        # check out: https://docs.python.org/3/reference/datamodel.html#object.__hash__
        return super().__hash__()

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                   self.src, self.target, self.graph)

    def __str__(self):
        return '{} -> {}'.format(self.src, self.target)


class AbstractDirectedGraphNode(base.AbstractGraphNode):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AbstractDirectedGraph(base.AbstractGraph):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.in_edge_map = dict()
        self.out_edge_map = dict()

    @abstractmethod
    def get_directed_edges(self, src=None, target=None):
        """Get all edges directed from source nodes to target nodes

        :param src: None, single node or node collection of source nodes. If None, then
            it will be all nodes.
        :param target: None, single node or node collection of target nodes. If None, then
            it will be all nodes.
        :return: edges
        """
        return self.get_edges()

    def check_add_edge(self, src, target):
        """Raises error if an edge with given source and target node cannot
        be added validly to the graph.

        :param src: source node
        :param target: target node
        """
        nodes = self.get_nodes()
        if src not in nodes or target not in nodes:
            raise ValueError('Cannot add an arc between {} '
                             'and {}, since one of the nodes '
                             'is not in the graph.'.format(src, target))

    def remove_surrounding_edges(self, node):
        del self.in_edge_map[node]
        del self.out_edge_map[node]

    def graph_element_added(self, element):
        if isinstance(element, AbstractDirectedGraphNode):
            self.in_edge_map[element] = set()
            self.out_edge_map[element] = set()
        if isinstance(element, AbstractDirectedGraphEdge):
            self.in_edge_map[element.target].add(element)
            self.out_edge_map[element.src].add(element)

    def graph_element_removed(self, element):
        if isinstance(element, AbstractDirectedGraphNode):
            del self.in_edge_map[element]
            del self.out_edge_map[element]
        if isinstance(element, AbstractDirectedGraphEdge):
            self.in_edge_map[element.target].remove_all(element)
            self.out_edge_map[element.src].remove_all(element)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.in_edge_map, self.out_edge_map)
