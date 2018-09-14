#!/usr/bin/env python

"""This is the pnml extension module.

This module contains PNML extension classes.
"""
import logging

from podspy.petrinet.pnml.base import *
from podspy.petrinet.semantics import Marking
from lxml import etree


__all__ = [
    'PnmlExtensionFactory',
    'PnmlFinalMarking',
    'PnmlFinalMarkings',
    'PnmlMarkedPlace'
]


logger = logging.getLogger(__file__)


class PnmlExtensionFactory:
    @staticmethod
    def create_final_marking():
        return PnmlFinalMarking()

    @staticmethod
    def final_marking2pnml(places, marking, id_map):
        pnml_fmarking = PnmlFinalMarking()
        for place in places:
            # need to find the id of place
            # tmp = list(filter(lambda item: item[1] == place, id_map.items()))
            # assert len(tmp) == 1, 'Should only have one filtered item: {}'.format(tmp)
            # _id = tmp[0][0]
            _id = id_map[place]
            occ = marking.occurrences(place)
            pnml_marked_place = PnmlExtensionFactory.marked_place2pnml(_id, occ)
            pnml_fmarking.marked_place_list.append(pnml_marked_place)
        return pnml_fmarking

    @staticmethod
    def create_final_markings():
        return PnmlFinalMarkings()

    @staticmethod
    def final_markings2pnml(places, final_markings, id_map):
        pnml_fmarkings = PnmlFinalMarkings()
        for marking in final_markings:
            pnml_fmarking = PnmlExtensionFactory.final_marking2pnml(places, marking, id_map)
            pnml_fmarkings.final_marking_list.append(pnml_fmarking)
        return pnml_fmarkings

    @staticmethod
    def create_marked_place():
        return PnmlMarkedPlace()

    @staticmethod
    def marked_place2pnml(place_id, nof_tokens):
        pnml_marked_place = PnmlMarkedPlace()
        pnml_marked_place.id_ref = place_id
        pnml_marked_place.text = PnmlBaseFactory.create_pnml_text(str(nof_tokens))
        return pnml_marked_place


class PnmlFinalMarking(PnmlElement):
    TAG = 'marking'

    def __init__(self):
        super().__init__(PnmlFinalMarking.TAG)
        self.marked_place_list = list()

    def add_child(self, child):
        if isinstance(child, PnmlMarkedPlace):
            self.marked_place_list.append(child)
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, place_map, final_markings):
        final_marking = Marking()

        for marked_place in self.marked_place_list:
            marked_place.convert_to_net(final_marking, place_map)

        final_markings.add(final_marking)

    def to_lxml(self):
        ele = etree.Element(PnmlFinalMarking.TAG)

        for marked_place in self.marked_place_list:
            ele.append(marked_place.to_lxml())

        return ele

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.marked_place_list)


class PnmlFinalMarkings(PnmlElement):
    TAG = 'finalmarkings'

    def __init__(self):
        super().__init__(PnmlFinalMarkings.TAG)
        self.final_marking_list = list()

    def add_child(self, child):
        if isinstance(child, PnmlFinalMarking):
            self.final_marking_list.append(child)
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, place_map, final_markings):
        for final_marking in self.final_marking_list:
            final_marking.convert_to_net(place_map, final_markings)

    def to_lxml(self):
        ele = etree.Element(PnmlFinalMarkings.TAG)

        for marking in self.final_marking_list:
            ele.append(marking.to_lxml())

        return ele

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.final_marking_list)


class PnmlMarkedPlace(PnmlElement):
    TAG = 'place'

    def __init__(self):
        super().__init__(PnmlMarkedPlace.TAG)
        self.id_ref = None
        self.text = None

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        if 'idref' in attrib:
            self.id_ref = attrib['idref']
        elif 'id' in attrib:
            self.id_ref = attrib['id']
        return True

    def add_child(self, child):
        if isinstance(child, PnmlText):
            self.text = child
            added = True
        else:
            added = super().add_child(child)
        return added

    def convert_to_net(self, marking, place_map):
        try:
            place = place_map[self.id_ref]
            weight = int(self.text.text)
            if weight > 0:
                marking.add(place, weight)
        except Exception as e:
            logger.error(e)
            debug = 'Cannot add {} from place_map {} to marking {}'.format(
                self, place_map, marking
            )
            logger.debug(debug)

    def to_lxml(self):
        ele = etree.Element(PnmlMarkedPlace.TAG)
        ele.attrib['idref'] = self.id_ref

        if self.text is not None:
            ele.append(self.text.to_lxml())

        return ele

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.id_ref, self.text)


