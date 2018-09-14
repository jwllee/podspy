#!/usr/bin/env python

"""This is the petrinet element module.

This module contains petrinet element classes.
"""


from abc import abstractmethod
import uuid, logging

from podspy.graph import directed
from podspy.utils import attributes as attrib
from podspy.utils import shapes, colors


logger = logging.getLogger(__file__)


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
        self.attribs[attrib.LABEL] = str(self._weight)
        self.attribs[attrib.EDGEEND] = attrib.ARROWTYPE_TECHNICAL
        self.attribs[attrib.EDGEENDFILLED] = True
        self.attribs[attrib.SHOWLABEL] = self._weight > 1

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, weight):
        # update attribute
        self._weight = weight
        self.attribs[attrib.LABEL] = str(weight)
        self.attribs[attrib.SHOWLABEL] = weight > 1

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self.src, self.target, self._weight)

    def __str__(self):
        return '{} -> {}, ({})'.format(self.src, self.target, self._weight)


class InhibitorArc(PetrinetEdge):
    def __init__(self, src, target, label, *args, **kwargs):
        super().__init__(src, target, label, *args, **kwargs)
        self.attribs[attrib.EDGEEND] = attrib.ARROWTYPE_CIRCLE
        self.attribs[attrib.EDGEENDFILLED] = False

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.src, self.target)

    def __str__(self):
        return '{} ---O {}'.format(self.src, self.target)


class ResetArc(PetrinetEdge):
    def __init__(self, src, target, label, *args, **kwargs):
        super().__init__(src, target, label, *args, **kwargs)
        self.attribs[attrib.EDGEEND] = attrib.ARROWTYPE_SIMPLE
        self.attribs[attrib.EDGEENDFILLED] = False

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.src, self.target)

    def __str__(self):
        return '{} -->> {}'.format(self.src, self.target)


class Place(PetrinetNode):
    def __init__(self, graph, label, *args, **kwargs):
        super().__init__(graph, label, *args, **kwargs)
        self.attribs[attrib.SHAPE] = shapes.ELLIPSE
        self.attribs[attrib.RESIZABLE] = True
        self.attribs[attrib.SIZE] = (25, 25)
        self.attribs[attrib.SHOWLABEL] = False

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
            self.attribs[attrib.SIZE] = (30, 30)
            self.attribs[attrib.SHOWLABEL] = False
            self.attribs[attrib.FILLCOLOR] = colors.BLACK
        else:
            self.attribs[attrib.SIZE] = (50, 40)
            self.attribs[attrib.SHOWLABEL] = True
            self.attribs[attrib.FILLCOLOR] = None

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                       self.label, self._is_invisible)

    def __str__(self):
        return '{}, invisible: {}'.format(self.label, self._is_invisible)
