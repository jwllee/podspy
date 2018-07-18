#!/usr/bin/env python

"""This is the base module.

This module contains base graph classes.
"""

from podspy.util import attribute as attrib

from abc import ABC, abstractmethod
import uuid


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


class AbstractGraphElement(ABC):
    @abstractmethod
    def __init__(self, label='no label', _map=None):
        self.label = label
        self.map = _map if _map is not None else dict()
        self.map[attrib.LABEL] = self.label

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.label)

    def __str__(self):
        return self.label


class AbstractGraphEdge(AbstractGraphElement):
    @abstractmethod
    def __init__(self, src, target, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.src = src
        self.target = target
        self.hash = self.src.__hash__() + 37 * self.target.__hash__()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.src == other.src and self.target == other.target

    def __hash__(self):
        return self.hash

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                               self.src, self.target, self.hash)

    def __str__(self):
        return '{} - {}'.format(self.src, self.target)


class AbstractGraphNode(AbstractGraphElement):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = uuid.uuid4()

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._id)

    def __str__(self):
        return 'node {}'.format(self._id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError('Other is of class: {}'.format(other.__class__))
        return self._id < other._id

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError('Other is of class: {}'.format(other.__class__))
        return self._id > other._id

    def __ge__(self, other):
        return self > other or self == other

    def __hash__(self):
        return hash(self._id)


class AbstractGraph(AbstractGraphElement):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = uuid.uuid4()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._id)

    def remove_node_from_collection(self, collection, node):
        """Removes node from collection.

        :param collection: collection of graph elements
        :param node: graph element to remove
        :return: the removed item or None
        """
        for item in collection:
            if item == node:
                collection.remove_all(node)
                return item
        return None

    def get_edges(self, src, target, collection):
        """Gets edges with given source and target from collection.

        :param src: source node
        :param target: target node
        :param collection: collection of edges
        :return: set of edges
        """
        edges = set()
        for e in collection:
            if e.src == src and e.target == target:
                edges.add(e)
        return edges

    def remove_from_edges(self, src, target, collection):
        """Remove edges with the given source and target from the
        collection of edges.

        :param src: source node
        :param target: target node
        :param collection: collection of edges
        :return: set of edges
        """
        for e in collection:
            if e.src == src and e.target == target:
                collection.remove_all(e)
                self.graph_element_removed(e)
                return e
        return None

    def graph_element_removed(self, element):
        """Called every time an element is removed from the graph.

        :param element: removed graph element
        """
        pass

    def graph_element_added(self, element):
        """Called every time an element is added to the graph.

        :param element: added graph element
        """
        pass

    def graph_element_changed(self, element):
        """Called every time an alement is changed in the graph.

        :param element: changed graph element
        """
        pass
