#!/usr/bin/env python

"""This is the pnml element module.

This module contains PNML element classes.
"""
from podspy.petrinet.pnml.base import *
from podspy.petrinet.pnml.graphics import *
from podspy.petrinet.pnml.extension import *

from podspy.petrinet.elements import *
from podspy.petrinet.nets import *
from podspy.petrinet.elements import PetrinetNode

from podspy.utils import attributes as attrib

from abc import abstractmethod
import logging
from enum import Enum
import uuid
from lxml import etree


logger = logging.getLogger(__name__)


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
    'PnmlAnnotation',
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
    def net2pnml(marked_nets, final_marked_nets, layout=None):
        logger.debug('Converting nets to pnml')

        pnml = Pnml()
        pnml.net_list = list()
        net_ctr = 1
        # maps node id to node elements, and allows the generation of new unique node
        # id by using the size of the dict
        id_map = dict()

        for net, marking in marked_nets.items():
            logger.debug('Looping through net: \n{}'.format(net))

            final_markings = final_marked_nets[net]
            pnml_net = PnmlElementFactory.net2pnml_net(net=net,
                                                       net_ctr=net_ctr,
                                                       id_map=id_map,
                                                       marking=marking,
                                                       final_markings=final_markings,
                                                       layout=layout)

            logger.debug('PNML net: \n{}'.format(pnml_net))

            pnml.net_list.append(pnml_net)
            net_ctr += 1

        return pnml, id_map

    @staticmethod
    def create_arc():
        return PnmlArc()

    @staticmethod
    def arc2pnml(edge, id_map, layout=None):
        arc = PnmlArc()
        arc.add_name(edge.label)
        tool_specific = PnmlElementFactory.node2tool_specific(edge)
        arc.tool_specific_list.append(tool_specific)

        arc._id = 'arc{}'.format(len(id_map))
        id_map[edge] = arc._id
        arc.inscription = PnmlElementFactory.create_inscription()
        arc.inscription.add_graph_element(edge, layout)

        arc.target = id_map[edge.target]
        arc.source = id_map[edge.src]

        arc.arc_type = PnmlElementFactory.create_arc_type()
        if isinstance(edge, Arc):
            arc.arc_type.set_normal()
        elif isinstance(edge, ResetArc):
            arc.arc_type.set_reset()
        elif isinstance(edge, InhibitorArc):
            arc.arc_type.set_inhibitor()

        arc.graphics = PnmlGraphicFactory.ele2arc_graphics(edge, layout)
        return arc

    @staticmethod
    def create_arc_type():
        return PnmlArcType()

    @staticmethod
    def create_init_marking():
        return PnmlInitialMarking()

    @staticmethod
    def init_marking2pnml(place, marking, layout=None):
        init_marking = PnmlInitialMarking()
        occ = marking.occurrences(place)
        # place is part of initial marking
        if occ > 0:
            init_marking.add_graph_element(place, layout)
            init_marking.text = PnmlBaseFactory.create_pnml_text(str(occ))
            return init_marking
        return None

    @staticmethod
    def create_inscription():
        return PnmlInscription()

    @staticmethod
    def create_name():
        return PnmlName()

    @staticmethod
    def net2pnml_net(net, net_ctr, id_map, marking=None, final_markings=None, layout=None):
        logger.debug('Converting net to pnml_net...')

        # logger.debug('net: \n{}\n'
        #              'marking: {}\n'
        #              'final_markings: {}\n'
        #              'net_ctr: {}\n'
        #              'id_map: {}\n'
        #              'layout: {}'.format(net, marking, final_markings,
        #                                  net_ctr, id_map, layout))

        pnml_net = PnmlNet()
        pnml_net.add_name(net.label)
        pnml_net._id = "net{}".format(net_ctr)
        pnml_net.type = 'http://www.pnml.org/version-2009/grammar/pnmlcoremodel'
        pnml_net.page_list = list()
        page = PnmlElementFactory.net2page(net, marking, id_map, layout)
        pnml_net.page_list.append(page)

        # convert the final markings
        if final_markings is not None:
            pnml_net.final_markings = PnmlExtensionFactory.final_markings2pnml(net.places,
                                                                               final_markings,
                                                                               id_map)

        return pnml_net

    @staticmethod
    def create_net():
        return PnmlNet()

    @staticmethod
    def create_page():
        return PnmlPage()

    @staticmethod
    def net2page(net, marking, id_map, layout=None):
        page = PnmlPage()
        page._id = 'n{}'.format(len(id_map))
        id_map[page] = page._id

        # add net nodes to node list
        page.node_list = list()
        page.arc_list = list()

        for place in net.places:
            pnml_place = PnmlElementFactory.place2pnml(place, id_map, marking, layout)
            page.node_list.append(pnml_place)

        for trans in net.transitions:
            pnml_trans = PnmlElementFactory.trans2pnml(trans, id_map, layout)
            page.node_list.append(pnml_trans)

        # add edges, i.e., Arc, ResetArc, InhibitorArc
        for edge in net.get_edges():
            pnml_arc = PnmlElementFactory.arc2pnml(edge, id_map, layout)
            page.arc_list.append(pnml_arc)

        return page

    @staticmethod
    def create_place():
        return PnmlPlace()

    @staticmethod
    def place2pnml(place, id_map, marking=None, layout=None):
        pnml_place = PnmlPlace()
        pnml_place.add_id(id_map, element=place)
        pnml_place.add_node_graphics(place, layout=layout)
        pnml_place.add_name(place.label)

        # only create pnml initial marking if there is marking
        if marking is not None:
            pnml_place.initial_marking = PnmlElementFactory.init_marking2pnml(place, marking, layout)

        tool_specific = PnmlElementFactory.node2tool_specific(place)
        pnml_place.tool_specific_list.append(tool_specific)
        return pnml_place

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
    def trans2pnml(trans, id_map, layout=None):
        pnml_trans = PnmlTransition()
        pnml_trans.add_node_graphics(trans, layout)
        pnml_trans.add_id(id_map, element=trans)
        pnml_trans.add_name(trans.label)
        tool_specific = PnmlElementFactory.node2tool_specific(trans)
        pnml_trans.tool_specific_list.append(tool_specific)
        return pnml_trans

    @staticmethod
    def create_tool_specific():
        return PnmlToolSpecific()

    @staticmethod
    def node2tool_specific(node):
        # todo: stop lying here, it's generated from PODSpy, but need to be parsed in ProM tool_specific.tool = PnmlToolSpecific.PROM
        tool_specific = PnmlToolSpecific()
        tool_specific.tool = PnmlToolSpecific.PROM
        tool_specific.version = PnmlToolSpecific.PROM_VERSION
        tool_specific.local_node_id = str(node.local_id) if node.local_id is not None else None

        if isinstance(node, PetrinetNode):
            tool_specific.activity = node.label

        return tool_specific


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
            element.attribs[attrib.LABEL] = self.text.text

        if self.graphics:
            self.graphics.convert_to_net(element)

    def add_graph_element(self, element, layout=None):
        self.graphics = PnmlGraphicFactory.ele2annot_graphics(element, layout)

    def add_text(self, text):
        self.text = PnmlBaseFactory.create_pnml_text(text)

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

    def to_lxml(self):
        ele = etree.Element(Pnml.TAG)
        # each net is a child element
        for net in self.net_list:
            ele.append(net.to_lxml())

        return ele

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

    def add_name(self, name):
        """Adding name to :class:`PnmlBasicObject`

        :param name: name
        """
        self.name = PnmlElementFactory.create_name()
        self.name.add_text(name)

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

    def to_lxml(self):
        ele = etree.Element(PnmlArc.TAG)
        ele.attrib['id'] = self._id
        ele.attrib['source'] = self.source
        ele.attrib['target'] = self.target
        ele.append(self.name.to_lxml())

        for tool in self.tool_specific_list:
            ele.append(tool.to_lxml())

        ele.append(self.arc_type.to_lxml())

        return ele

    def __repr__(self):
        return '{}({}, {}, {}, {}, {}, {})'.format(self.__class__.__name__,
                                                   self._id, self.source,
                                                   self.target, self.inscription,
                                                   self.arc_type, self.graphics)


class PnmlName(PnmlAnnotation):
    TAG = 'name'

    def __init__(self, text=None):
        super().__init__(PnmlName.TAG, text)

    def to_lxml(self):
        ele = etree.Element(PnmlName.TAG)

        if self.text is not None:
            ele.append(self.text.to_lxml())

        return ele

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

    def to_lxml(self):
        ele = etree.Element(PnmlNet.TAG)
        ele.attrib['id'] = self._id
        ele.attrib['type'] = self.type

        if self.name is not None:
            ele.append(self.name.to_lxml())

        for page in self.page_list:
            ele.append(page.to_lxml())

        ele.append(self.final_markings.to_lxml())
        return ele

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self._id, self.type, self.page_list)


class PnmlNode(PnmlBasicObject):
    @abstractmethod
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
        node.attribs[attrib.SIZE] = (40, 40)
        if self.graphics:
            self.graphics.convert_to_net(node)

    def add_id(self, id_map, element):
        super().add_name(element.label)
        self._id = 'n{}'.format(len(id_map))
        id_map[element] = self._id

    def add_node_graphics(self, element, layout):
        self.graphics = PnmlGraphicFactory.ele2node_graphics(element, layout)

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

    def __hash__(self):
        # todo: need better hash code for PnmlPage
        return hash(PnmlPage.TAG)

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

    def to_lxml(self):
        ele = etree.Element(PnmlPage.TAG)
        ele.attrib['id'] = self._id

        if self.name is not None:
            ele.append(self.name.to_lxml())

        for node in self.node_list:
            ele.append(node.to_lxml())

        for arc in self.arc_list:
            ele.append(arc.to_lxml())

        return ele

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

    def to_lxml(self):
        ele = etree.Element(PnmlPlace.TAG)
        ele.attrib['id'] = self._id
        ele.append(self.name.to_lxml())

        for tool in self.tool_specific_list:
            ele.append(tool.to_lxml())

        if self.graphics is not None:
            ele.append(self.graphics.to_lxml())

        if self.initial_marking is not None:
            ele.append(self.initial_marking.to_lxml())

        return ele

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

    def to_lxml(self):
        ele = etree.Element(PnmlTransition.TAG)
        ele.attrib['id'] = self._id
        ele.append(self.name.to_lxml())

        for tool in self.tool_specific_list:
            ele.append(tool.to_lxml())

        if self.graphics is not None:
            ele.append(self.graphics.to_lxml())

        return ele

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
        # logger.debug('Has tool: {}'.format('tool' in attrib))
        # if 'tool' in attrib:
        #     logger.debug('Tool: {}'.format(attrib['tool']))

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

    def to_lxml(self):
        ele = etree.Element(PnmlToolSpecific.TAG)
        # logger.debug('Tool: {}'.format(self.tool))
        ele.attrib['tool'] = self.tool
        ele.attrib['version'] = self.version
        if self.activity is not None:
            ele.attrib['activity'] = self.activity
        ele.attrib['localNodeID'] = str(self.local_node_id)
        return ele

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

    def to_lxml(self):
        ele = etree.Element(PnmlArcType.TAG)

        if self.text is not None:
            ele.append(self.text.to_lxml())

        return ele

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

    def to_lxml(self):
        ele = etree.Element(PnmlInitialMarking.TAG)

        if self.text is not None:
            ele.append(self.text.to_lxml())

        return ele

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