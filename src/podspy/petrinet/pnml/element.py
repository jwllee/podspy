#!/usr/bin/env python

"""This is the pnml element module.

This module contains PNML element classes.
"""
from podspy.petrinet.pnml.base import *
from podspy.petrinet.pnml.graphic import *
from podspy.petrinet.pnml.extension import *

from podspy.petrinet.element import *
from podspy.petrinet.net import *

from podspy.util import attribute as attrib

from abc import abstractmethod
import logging
from enum import Enum
import uuid


logger = logging.getLogger(__name__)


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = [
    'Pnml',
    'PnmlInitialMarking',
    'PnmlInscription',
    'PnmlName',
    'PnmlNode',
    'PnmlPage',
    'PnmlPlace',
    'PnmlReferencePlace',
    'PnmlReferenceTransition',
    'PnmlTransition',
    'PnmlArc',
    'PnmlArcType',
    'PnmlNet',
    'PnmlToolSpecific',
    'PnmlElementFactory'
]


class PnmlElementFactory:
    @staticmethod
    def create_pnml():
        return Pnml()

    @staticmethod
    def create_arc():
        return PnmlArc()

    @staticmethod
    def create_arc_type():
        return PnmlArcType()

    @staticmethod
    def create_init_marking():
        return PnmlInitialMarking()

    @staticmethod
    def create_inscription():
        return PnmlInscription()

    @staticmethod
    def create_name():
        return PnmlName()

    @staticmethod
    def create_net():
        return PnmlNet()

    @staticmethod
    def create_page():
        return PnmlPage()

    @staticmethod
    def create_place():
        return PnmlPlace()

    @staticmethod
    def create_ref_place():
        return PnmlReferencePlace()

    @staticmethod
    def create_ref_trans():
        return PnmlReferenceTransition()

    @staticmethod
    def create_trans():
        return PnmlTransition()

    @staticmethod
    def create_tool_specific():
        return PnmlToolSpecific()


class PnmlAnnotation(PnmlElement):
    @abstractmethod
    def __init__(self, tag, text=None):
        super().__init__(tag)
        self.text = text
        self.graphics = None
        self.tool_specific_list = list()

    def add_child(self, child):
        if isinstance(child, PnmlText):
            self.text = child
            added = True
        elif isinstance(child, PnmlAnnotationGraphics):
            self.graphics = child
            added = True
        elif isinstance(child, PnmlToolSpecific):
            self.tool_specific_list.append(child)
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, element):
        if self.text:
            element.map[attrib.LABEL] = self.text.text

        if self.graphics:
            self.graphics.convert_to_net(element)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.text, self.graphics)


class PnmlType(Enum):
    PNML = 1
    EPNML = 2
    LOLA = 3


class Pnml(PnmlElement):
    TAG = 'pnml'

    def __init__(self, type=PnmlType.PNML):
        super().__init__(Pnml.TAG)
        self.type = type
        self.net_list = list()
        self.module = None
        self.configuration = None

    def add_child(self, child):
        # only supporting PnmlNet as children right now...
        if isinstance(child, PnmlNet):
            self.net_list.append(child)
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, net, marking, final_markings=None):
        if final_markings is None:
            final_markings = set()

        if len(self.net_list) > 0:
            place_map = dict()
            trans_map = dict()
            edge_map = dict()
            self.net_list[0].convert_to_net(net, marking, final_markings, place_map,
                                            trans_map, edge_map)

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__,
                                           self.type, self.net_list,
                                           self.module, self.configuration)


class PnmlBasicObject(PnmlElement):
    @abstractmethod
    def __init__(self, tag):
        super().__init__(tag)
        self.name = None
        self.tool_specific_list = list()

    def add_child(self, child):
        if isinstance(child, PnmlName):
            self.name = child
            added = True
        elif isinstance(child, PnmlToolSpecific):
            self.tool_specific_list.append(child)
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, **kwargs):
        element = kwargs['element']
        if self.name:
            self.name.convert_to_net(element)

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self.tag, self.name,
                                       self.tool_specific_list)


class PnmlArc(PnmlBasicObject):
    TAG = 'arc'

    def __init__(self):
        super().__init__(PnmlArc.TAG)
        self._id = None
        self.source = None
        self.target = None
        self.inscription = None
        self.arc_type = None
        self.graphics = None

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        self._id = attrib['id'] if 'id' in attrib else None
        self.source = attrib['source'] if 'source' in attrib else None
        self.target = attrib['target'] if 'target' in attrib else None
        return True

    def add_child(self, child):
        if isinstance(child, PnmlInscription):
            self.inscription = child
            added = True
        elif isinstance(child, PnmlArcGraphics):
            self.graphics = child
            added = True
        elif isinstance(child, PnmlArcType):
            self.arc_type = child
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, net, place_map, transition_map, edge_map):
        weight = 1
        if self.arc_type is None or self.arc_type.is_normal:
            if self.inscription is not None:
                weight = self.inscription.inscription

        # create arc (if source and target can be found)
        arc = None

        # arc type
        is_normal = self.arc_type is None or self.arc_type.is_normal

        if self.arc_type:
            is_inhibitor = self.arc_type.is_inhibitor and isinstance(net, InhibitorNet)
            is_reset = self.arc_type.is_reset and isinstance(net, ResetNet)
        else:
            is_inhibitor = False
            is_reset = False

        # place -> transition
        src, target = (None, None)
        if self.source in place_map and self.target in transition_map:
            src = place_map[self.source]
            target = transition_map[self.target]

        # transition -> place
        elif self.source in transition_map and self.target in place_map:
            src = transition_map[self.source]
            target = place_map[self.target]

        # add arc
        if src and target:
            if is_normal:
                arc = net.add_arc(src, target, weight)
            elif is_inhibitor:
                arc = net.add_inhibitor_arc(src, target, weight)
            elif is_reset:
                arc = net.add_reset_arc(src, target, weight)

        if arc:
            edge_map[self._id] = arc
            # constant for STYLE_SPLINE = 13, todo: change to constant for graphviz
            arc[attrib.STYLE] = 13
            super().convert_to_net(element=arc)
            for tool in self.tool_specific_list:
                tool.convert_to_net(arc)

            if self.graphics:
                self.graphics.convert_to_net(arc)

            if self.inscription:
                self.inscription.convert_to_net(arc)


    def __repr__(self):
        return '{}({}, {}, {}, {}, {}, {})'.format(self.__class__.__name__,
                                                   self._id, self.source,
                                                   self.target, self.inscription,
                                                   self.arc_type, self.graphics)


class PnmlName(PnmlAnnotation):
    TAG = 'name'

    def __init__(self, text=None):
        super().__init__(PnmlName.TAG, text)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.text)


class PnmlNet(PnmlBasicObject):
    TAG = 'net'

    def __init__(self):
        super().__init__(PnmlNet.TAG)
        self._id = None
        self.type = None
        self.page_list = list()
        self.final_markings = None

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        self.type = attrib['type'] if 'type' in attrib else None
        self._id = attrib['id'] if 'id' in attrib else None
        return True

    def add_child(self, child):
        if isinstance(child, PnmlPage):
            # logger.debug('Adding {!r} as child'.format(child))
            self.page_list.append(child)
            added = True
        elif isinstance(child, PnmlFinalMarkings):
            # logger.debug('Adding {!r} as child'.format(child))
            self.final_markings = child
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, net, marking, final_markings,
                       place_map, transition_map, edge_map):
        for page in self.page_list:
            page.convert_to_net(net, marking, place_map, transition_map, edge_map)

        # convert all final markings
        if self.final_markings:
            self.final_markings.convert_to_net(place_map, final_markings)

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self._id, self.type, self.page_list)


class PnmlNode(PnmlBasicObject):
    def __init__(self, tag):
        super().__init__(tag)
        self._id = None
        self.graphics = None

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        self._id = attrib['id'] if 'id' in attrib else None
        return True

    def add_child(self, child):
        if isinstance(child, PnmlNodeGraphics):
            self.graphics = child
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, **kwargs):
        node = kwargs['node']
        node.map[attrib.SIZE] = (40, 40)
        if self.graphics:
            self.graphics.convert_to_net(node)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self._id, self.graphics)


class PnmlPage(PnmlNode):
    TAG = 'page'

    def __init__(self):
        super().__init__(PnmlPage.TAG)
        self.node_list = list()
        self.arc_list = list()
        self.subnet = None

    def add_child(self, child):
        child_cls = [
            PnmlPlace,
            PnmlTransition,
            PnmlReferencePlace,
            PnmlReferenceTransition,
            PnmlPage
        ]
        is_instance = map(lambda c: isinstance(child, c), child_cls)
        if any(is_instance):
            # logger.debug('Adding {!r} as child'.format(child))
            self.node_list.append(child)
            added = True
        elif isinstance(child, PnmlArc):
            self.arc_list.append(child)
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, net, marking, place_map, transition_map, edge_map):
        logger.debug('Converting {!r}'.format(self))
        # convert nodes to net
        self.convert_nodes_to_net(net, marking, place_map, transition_map)

        size = 0
        new_size = len(place_map) + len(transition_map)
        while size != new_size:
            self.convert_ref_nodes_to_net(net, marking, place_map, transition_map)
            size = new_size
            new_size = len(place_map) + len(transition_map)
        self.convert_arcs_to_net(net, marking, place_map, transition_map, edge_map)

    def convert_nodes_to_net(self, net, marking, place_map, transition_map):
        for node in self.node_list:
            if isinstance(node, PnmlPlace):
                node.convert_to_net(net, marking, place_map)
            elif isinstance(node, PnmlTransition):
                node.convert_to_net(net, marking, transition_map)
            elif isinstance(node, PnmlPage):
                node.convert_nodes_to_net(net, marking, place_map, transition_map)

    def convert_ref_nodes_to_net(self, net, marking, place_map, transition_map):
        for node in self.node_list:
            if isinstance(node, PnmlReferencePlace):
                node.convert_to_net(net, place_map)
            elif isinstance(node, PnmlReferenceTransition):
                node.convert_to_net(net, transition_map)
            elif isinstance(node, PnmlPage):
                node.convert_ref_nodes_to_net(net, marking, place_map, transition_map)

    def convert_arcs_to_net(self, net, marking, place_map, transition_map, edge_map):
        for arc in self.arc_list:
            arc.convert_to_net(net, place_map, transition_map, edge_map)

        for node in self.node_list:
            if isinstance(node, PnmlPage):
                node.convert_arcs_to_net(net, marking, place_map, transition_map, edge_map)

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self.node_list, self.arc_list,
                                       self.subnet)


class PnmlPlace(PnmlNode):
    TAG = 'place'

    def __init__(self):
        super().__init__(PnmlPlace.TAG)
        self.initial_marking = None

    def add_child(self, child):
        added = False
        if isinstance(child, PnmlInitialMarking):
            self.initial_marking = child
            added = True
        return added

    def convert_to_net(self, net, marking, place_map):
        logger.debug('Converting {} to place'.format(self))

        if self.name is not None and self.name.text is not None:
            label = self.name.text.text
        else:
            label = self._id

        # add place to net
        place = net.add_place(label)
        super().convert_to_net(node=place)

        # add the initial marking of this place to the marking
        weight = 0
        if self.initial_marking is not None:
            weight = self.initial_marking.initial_marking
        if weight != 0:
            logger.debug('Adding {} tokens from {} to {}'.format(weight, place, marking))
            marking.add(place, weight)

        # register the new place
        place_map[self._id] = place

        for tool in self.tool_specific_list:
            tool.convert_to_net(place)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.initial_marking)


class PnmlReferencePlace(PnmlNode):
    TAG = 'referencePlace'

    def __init__(self):
        super().__init__(PnmlReferencePlace.TAG)
        self.id_ref = None

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        self.id_ref = attrib['ref'] if 'ref' in attrib else None
        return True

    def convert_to_net(self, net, place_map):
        if self._id not in place_map and self.id_ref in place_map:
            place_map[self._id] = place_map[self.id_ref]

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.id_ref)


class PnmlReferenceTransition(PnmlNode):
    TAG = 'referenceTransition'

    def __init__(self):
        super().__init__(PnmlReferenceTransition.TAG)
        self.id_ref = None

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        self.id_ref = attrib['ref'] if 'ref' in attrib else None
        return True

    def convert_to_net(self, net, transition_map):
        if self._id not in transition_map and self.id_ref in transition_map:
            transition_map[self._id] = transition_map[self.id_ref]

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.id_ref)


class PnmlTransition(PnmlNode):
    TAG = 'transition'

    def __init__(self):
        super().__init__(PnmlTransition.TAG)
        self.receive_list = list()
        self.send_list = list()
        self.sync_list = list()

    def convert_to_net(self, net, marking, transition_map):
        if self.name is not None and self.name.text is not None:
            label = self.name.text.text
        else:
            label = self._id

        # add new transition to net
        trans = net.add_transition(label)
        super().convert_to_net(node=trans)

        for tool in self.tool_specific_list:
            tool.convert_to_net(trans)

        # register new transition found
        transition_map[self._id] = trans

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self.receive_list,
                                       self.send_list,
                                       self.sync_list)


class PnmlToolSpecific(PnmlElement):
    TAG = 'toolspecific'
    PODSPY = 'podspy'
    PROM = 'ProM'
    INVISIBLE = '$invisible$'
    PROM_VERSION = '6.4'

    def __init__(self):
        super().__init__(PnmlToolSpecific.TAG)
        self.tag = PnmlToolSpecific.TAG
        self.tool = None
        self.version = None
        self.activity = None
        self.local_node_id = None

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        self.tool = attrib['tool'] if 'tool' in attrib else None
        self.version = attrib['version'] if 'version' in attrib else None
        self.activity = attrib['activity'] if 'activity' in attrib else None
        self.local_node_id = attrib['localNodeID'] if 'localNodeID' in attrib else None
        return True

    def convert_to_net(self, node):
        # logger.debug('Converting {} with node: {}'.format(self, node))
        right_tool = self.tool == PnmlToolSpecific.PROM or self.tool == PnmlToolSpecific.PODSPY
        right_version = self.version == PnmlToolSpecific.PROM_VERSION
        has_local_id = self.local_node_id is not None
        is_invisible = self.activity == PnmlToolSpecific.INVISIBLE

        if right_tool and right_version:
            if isinstance(node, Transition) and is_invisible:
                node.is_invisible = True
            if has_local_id:
                node.local_id = uuid.UUID(self.local_node_id)

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__,
                                           self.tag, self.version,
                                           self.activity, self.local_node_id)


class PnmlArcType(PnmlAnnotation):
    TAG = 'arctype'
    EPNML_TAG = 'type'

    def __init__(self):
        super().__init__(PnmlArcType.TAG)

    @property
    def is_normal(self):
        no_text = self.text is None
        return no_text or self.text.text == '' or self.text.text == 'normal'

    @property
    def is_reset(self):
        has_text = self.text is not None
        return has_text and self.text.text == 'reset'

    @property
    def is_inhibitor(self):
        has_text = self.text is not None
        return has_text and self.text.text == 'inhibitor'

    @property
    def is_read(self):
        has_text = self.text is not None
        return has_text and self.text.text == 'read'

    def set_normal(self):
        self.text = PnmlBaseFactory.create_pnml_text('normal')

    def set_reset(self):
        self.text = PnmlBaseFactory.create_pnml_text('reset')

    def set_inhibitor(self):
        self.text = PnmlBaseFactory.create_pnml_text('inhibitor')

    def set_read(self):
        self.text = PnmlBaseFactory.create_pnml_text('read')

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)


class PnmlInitialMarking(PnmlAnnotation):
    TAG = 'initialMarking'

    def __init__(self):
        super().__init__(PnmlInitialMarking.TAG)

    @property
    def initial_marking(self):
        try:
            return int(self.text.text)
        except Exception as e:
            logger.error('Parsing {} as initial marking resulted in: {}'.format(self.text, e))
        return 0

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)


class PnmlInscription(PnmlAnnotation):
    TAG = 'inscription'

    def __init__(self):
        super().__init__(PnmlInscription.TAG)

    @property
    def inscription(self):
        try:
            return int(self.text.text)
        except:
            return 1

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)