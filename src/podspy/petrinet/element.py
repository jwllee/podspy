#!/usr/bin/env python

"""This is the petrinet element module.

This module contains petrinet element classes.
"""


from abc import abstractmethod
import uuid, logging

from podspy.graph import directed
from podspy.util import attribute as attrib
from podspy.util import shape, color


logger = logging.getLogger(__file__)


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = [
    'Arc',
    'InhibitorArc',
    'ResetArc',
    'Place',
    'Transition'
]


class PetrinetNode(directed.AbstractDirectedGraphNode):
    @abstractmethod
    def __init__(self, graph, label, local_id=uuid.uuid4(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph
        self.label = label
        self.local_id = local_id

    def local_eq(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.local_id == other.local_id

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self.graph, self.label, self.local_id)

    def __str__(self):
        return 'node {}'.format(self._id)


class PetrinetEdge(directed.AbstractDirectedGraphEdge):
    @abstractmethod
    def __init__(self, src, target, label, local_id=uuid.uuid4(), *args, **kwargs):
        super().__init__(src, target, *args, **kwargs)
        self.label = label
        self.local_id = local_id

    def local_eq(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.local_id == other.local_id

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                       self.label, self.local_id)

    def __str__(self):
        return '{}->{}'.format(self.src, self.target)


class Arc(PetrinetEdge):
    def __init__(self, src, target, weight, *args, **kwargs):
        label = str(weight)
        super().__init__(src, target, label, *args, **kwargs)
        self._weight = weight
        self.map[attrib.LABEL] = str(self._weight)
        self.map[attrib.EDGEEND] = attrib.ARROWTYPE_TECHNICAL
        self.map[attrib.EDGEENDFILLED] = True
        self.map[attrib.SHOWLABEL] = self._weight > 1

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, weight):
        # update attribute
        self._weight = weight
        self.map[attrib.LABEL] = str(weight)
        self.map[attrib.SHOWLABEL] = weight > 1

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self.src, self.target, self._weight)

    def __str__(self):
        return '{} -> {}, ({})'.format(self.src, self.target, self._weight)


class InhibitorArc(PetrinetEdge):
    def __init__(self, src, target, label, *args, **kwargs):
        super().__init__(src, target, label, *args, **kwargs)
        self.map[attrib.EDGEEND] = attrib.ARROWTYPE_CIRCLE
        self.map[attrib.EDGEENDFILLED] = False

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.src, self.target)

    def __str__(self):
        return '{} ---O {}'.format(self.src, self.target)


class ResetArc(PetrinetEdge):
    def __int__(self, src, target, label, *args, **kwargs):
        super().__init__(src, target, label, *args, **kwargs)
        self.map[attrib.EDGEEND] = attrib.ARROWTYPE_SIMPLE
        self.map[attrib.EDGEENDFILLED] = False

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.src, self.target)

    def __str__(self):
        return '{} -->> {}'.format(self.src, self.target)


class Place(PetrinetNode):
    def __init__(self, graph, label, *args, **kwargs):
        super().__init__(graph, label, *args, **kwargs)
        self.map[attrib.SHAPE] = shape.ELLIPSE
        self.map[attrib.RESIZABLE] = True
        self.map[attrib.SIZE] = (25, 25)
        self.map[attrib.SHOWLABEL] = False

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)


class Transition(PetrinetNode):
    def __init__(self, graph, label, *args, **kwargs):
        super().__init__(graph, label, *args, **kwargs)
        self._is_invisible = False

    @property
    def is_invisible(self):
        return self._is_invisible

    @is_invisible.setter
    def is_invisible(self, invisible):
        # logger.debug('Setting {} to invisible: {}'.format(self, invisible))
        self._is_invisible = invisible
        if self._is_invisible:
            self.map[attrib.SIZE] = (30, 30)
            self.map[attrib.SHOWLABEL] = False
            self.map[attrib.FILLCOLOR] = color.BLACK
        else:
            self.map[attrib.SIZE] = (50, 40)
            self.map[attrib.SHOWLABEL] = True
            self.map[attrib.FILLCOLOR] = None

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                       self.label, self._is_invisible)

    def __str__(self):
        return '{}, invisible: {}'.format(self.label, self._is_invisible)
