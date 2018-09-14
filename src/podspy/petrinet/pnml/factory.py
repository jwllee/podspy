#!/usr/bin/env python

"""This is the pnml factory module.

This module contains pnml factory class.
"""
import logging

from podspy.petrinet.pnml.base import *
from podspy.petrinet.pnml.elements import *
from podspy.petrinet.pnml.extension import *
from podspy.petrinet.pnml.graphics import *


__all__ = [
    'PnmlFactory'
]


logger = logging.getLogger(__file__)


class PnmlFactory:

    @staticmethod
    def create_pnml(tag, parent_cls):
        # logger.debug('Creating pnml with tag: {} and parent class: {}'.format(tag, parent_cls))
        # special cases with the corresponding pnml creation method
        special_conds = [
            # place
            (PnmlPlace.TAG, PnmlPage, PnmlElementFactory.create_place),
            # marked place
            (PnmlMarkedPlace.TAG, PnmlFinalMarking, PnmlExtensionFactory.create_marked_place),
            # annotation graphics
            (PnmlAnnotationGraphics.TAG, PnmlArcType, PnmlGraphicFactory.create_annot_graphics),
            (PnmlAnnotationGraphics.TAG, PnmlInitialMarking, PnmlGraphicFactory.create_annot_graphics),
            (PnmlAnnotationGraphics.TAG, PnmlInscription, PnmlGraphicFactory.create_annot_graphics),
            (PnmlAnnotationGraphics.TAG, PnmlName, PnmlGraphicFactory.create_annot_graphics),
            # arc graphics
            (PnmlArcGraphics.TAG, PnmlArc, PnmlGraphicFactory.create_arc_graphics),
            # dimension
            (PnmlDimension.TAG, PnmlNodeGraphics, PnmlGraphicFactory.create_dimension),
            # node graphics
            (PnmlNodeGraphics.TAG, PnmlNode, PnmlGraphicFactory.create_node_graphics)
        ]

        # check for special case

        # same pnml tag
        tag_equality = lambda t0, t1: t0 == t1

        # the parent class is subclass of the special condition parent class
        is_subclass = lambda c0, c1: issubclass(c0, c1)

        # check which special condition is met by requiring both conditions to be met
        is_special_list = list(map(
            lambda cond: tag_equality(tag, cond[0]) and is_subclass(parent_cls, cond[1]), special_conds
        ))

        if any(is_special_list):
            # get the special case
            fulfilled = list(filter(

                # see which special condition is met
                lambda pair: pair[0] == True,

                # zip bool and condition list so that the met condition can be picked out
                zip(is_special_list, special_conds)
            ))

            assert len(fulfilled) == 1, 'Meeting more than one special pnml condition: {}'.format(fulfilled)

            # get the first item and then the second item of the pair
            cond = fulfilled[0][1]

            pnml = cond[2]()

        else:
            _map = {
                # base
                PnmlText.TAG: PnmlBaseFactory.create_pnml_text,

                # elements
                Pnml.TAG: PnmlElementFactory.create_pnml,
                PnmlPlace.TAG: PnmlElementFactory.create_place,
                PnmlNet.TAG: PnmlElementFactory.create_net,
                PnmlArc.TAG: PnmlElementFactory.create_arc,
                PnmlArcType.TAG: PnmlElementFactory.create_arc_type,
                PnmlName.TAG: PnmlElementFactory.create_name,
                PnmlPage.TAG: PnmlElementFactory.create_page,
                PnmlReferencePlace.TAG: PnmlElementFactory.create_ref_place,
                PnmlReferenceTransition.TAG: PnmlElementFactory.create_ref_trans,
                PnmlTransition.TAG: PnmlElementFactory.create_trans,
                PnmlToolSpecific.TAG: PnmlElementFactory.create_tool_specific,
                PnmlInitialMarking.TAG: PnmlElementFactory.create_init_marking,
                PnmlInscription.TAG: PnmlElementFactory.create_inscription,

                # graphics
                PnmlFill.TAG: PnmlGraphicFactory.create_fill,
                PnmlFont.TAG: PnmlGraphicFactory.create_font,
                PnmlLine.TAG: PnmlGraphicFactory.create_line,
                PnmlOffset.TAG: PnmlGraphicFactory.create_offset,
                PnmlPosition.TAG: PnmlGraphicFactory.create_position,

                # extensions
                PnmlFinalMarking.TAG: PnmlExtensionFactory.create_final_marking,
                PnmlFinalMarkings.TAG: PnmlExtensionFactory.create_final_markings,
            }

            pnml = _map[tag]()

        return pnml
