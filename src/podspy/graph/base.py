#!/usr/bin/env python

"""This is the base module.

This module contains base graph classes.
"""

from podspy.utils import attributes as attrib

from abc import ABC, abstractmethod
import uuid, logging


logger = logging.getLogger(__file__)


class AbstractGraphElement(ABC):
    @abstractmethod
    def __init__(self, label='no label', attribs=None):
        self.label = label
        self.attribs = attribs if attribs is not None else dict()
        self.attribs[attrib.LABEL] = self.label

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
        self.hash_cache = hash((self.src, self.target))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.src == other.src and self.target == other.target

    def __hash__(self):
        # need to make sure that hash value is not too big: <= 8 bytes in 64-bit computers
        # check out: https://docs.python.org/3/reference/datamodel.html#object.__hash__
        # logging.debug('Hash value: {}'.format(self.hash_cache))
        return self.hash_cache

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                               self.src, self.target, hash(self))

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
        return self._id.__hash__()


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

    def __iter__(self):
        """Iterate over nodes

        :return: an iterator over nodes
        """
        return iter(self.get_nodes())

    def __contains__(self, n):
        """Returns True if graph has node n, False otherwise.

        :param n: node
        :return: whether if node n is in graph
        """
        return n in self.get_nodes()

    def __len__(self):
        """Number of nodes

        :return: number of nodes
        """
        return len(self.get_nodes())

    @abstractmethod
    def get_nodes(self):
        """Gets all nodes

        :return: nodes
        """
        return frozenset()

    @abstractmethod
    def get_edges(self, nodes=None):
        """Gets edges incident to the nodes, by default it should return all edges

        :param nodes: None, single, or collection of nodes to which the returned edges are incident to
        :return: edges
        """
        return frozenset()

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
