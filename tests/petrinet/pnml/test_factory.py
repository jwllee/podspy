#!/usr/bin/env python

"""This is the unit test module.

This module tests the pnml factory module.
"""

import pytest


from podspy.petrinet.pnml.factory import PnmlFactory
from podspy.petrinet.pnml.base import *
from podspy.petrinet.pnml.elements import *
from podspy.petrinet.pnml.extension import *
from podspy.petrinet.pnml.graphics import *


@pytest.fixture(params=[
    # base
    PnmlText,

    # elements
    Pnml,
    PnmlNet,
    PnmlArc,
    PnmlName,
    PnmlPage,
    PnmlPlace,
    PnmlReferencePlace,
    PnmlReferenceTransition,
    PnmlTransition,
    PnmlToolSpecific,

    # graphics
    PnmlAnnotationGraphics,
    PnmlArcGraphics,
    PnmlDimension,
    PnmlFill,
    PnmlFont,
    PnmlLine,
    PnmlNodeGraphics,
    PnmlOffset,
    PnmlPosition,

    # extensions
    PnmlArcType,
    PnmlInitialMarking,
    PnmlInscription,
    PnmlFinalMarking,
    PnmlFinalMarkings,
    PnmlMarkedPlace
])
def parent(request):
    return request.param


class TestPnmlFactory:

    def test_create_place(self):
        pnml = PnmlFactory.create_pnml(PnmlPlace.TAG, PnmlPage)
        assert isinstance(pnml, PnmlPlace)

    def test_create_marked_place(self):
        pnml = PnmlFactory.create_pnml(PnmlMarkedPlace.TAG, PnmlFinalMarking)
        assert isinstance(pnml, PnmlMarkedPlace)

    def test_create_annot_graphics(self):
        # 4 possible parent classes
        pnml = PnmlFactory.create_pnml(PnmlAnnotationGraphics.TAG, PnmlArcType)
        assert isinstance(pnml, PnmlAnnotationGraphics)

        pnml = PnmlFactory.create_pnml(PnmlAnnotationGraphics.TAG, PnmlInitialMarking)
        assert isinstance(pnml, PnmlAnnotationGraphics)

        pnml = PnmlFactory.create_pnml(PnmlAnnotationGraphics.TAG, PnmlInscription)
        assert isinstance(pnml, PnmlAnnotationGraphics)

        pnml = PnmlFactory.create_pnml(PnmlAnnotationGraphics.TAG, PnmlName)
        assert isinstance(pnml, PnmlAnnotationGraphics)

    def test_create_arc_graphics(self):
        pnml = PnmlFactory.create_pnml(PnmlArcGraphics.TAG, PnmlArc)
        assert isinstance(pnml, PnmlArcGraphics)

    def test_create_dimension(self):
        pnml = PnmlFactory.create_pnml(PnmlDimension.TAG, PnmlNodeGraphics)
        assert isinstance(pnml, PnmlDimension)

    def test_create_node_graphics(self):
        pnml = PnmlFactory.create_pnml(PnmlNodeGraphics.TAG, PnmlNode)
        assert isinstance(pnml, PnmlNodeGraphics)

    # normal cases
    # base
    def test_create_text(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlText.TAG, parent)
        assert isinstance(pnml, PnmlText)

    # elements
    def test_create_pnml(self, parent):
        pnml = PnmlFactory.create_pnml(Pnml.TAG, parent)
        assert isinstance(pnml, Pnml)

    def test_create_net(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlNet.TAG, parent)
        assert isinstance(pnml, PnmlNet)

    def test_create_arc(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlArc.TAG, parent)
        assert isinstance(pnml, PnmlArc)

    def test_create_name(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlName.TAG, parent)
        assert isinstance(pnml, PnmlName)

    def test_create_page(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlPage.TAG, parent)
        assert isinstance(pnml, PnmlPage)

    def test_create_ref_place(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlReferencePlace.TAG, parent)
        assert isinstance(pnml, PnmlReferencePlace)

    def test_create_ref_trans(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlReferenceTransition.TAG, parent)
        assert isinstance(pnml, PnmlReferenceTransition)

    def test_create_trans(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlTransition.TAG, parent)
        assert isinstance(pnml, PnmlTransition)

    def test_create_tool_specific(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlToolSpecific.TAG, parent)
        assert isinstance(pnml, PnmlToolSpecific)

    # graphics
    def test_create_fill(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlFill.TAG, parent)
        assert isinstance(pnml, PnmlFill)

    def test_create_font(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlFont.TAG, parent)
        assert isinstance(pnml, PnmlFont)

    def test_create_line(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlLine.TAG, parent)
        assert isinstance(pnml, PnmlLine)

    def test_create_offset(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlOffset.TAG, parent)
        assert isinstance(pnml, PnmlOffset)

    def test_create_position(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlPosition.TAG, parent)
        assert isinstance(pnml, PnmlPosition)

    # extensions
    def test_create_arc_type(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlArcType.TAG, parent)
        assert isinstance(pnml, PnmlArcType)

    def test_create_init_marking(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlInitialMarking.TAG, parent)
        assert isinstance(pnml, PnmlInitialMarking)

    def test_create_inscription(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlInscription.TAG, parent)
        assert isinstance(pnml, PnmlInscription)

    def test_create_final_marking(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlFinalMarking.TAG, parent)
        assert isinstance(pnml, PnmlFinalMarking)

    def test_create_final_markings(self, parent):
        pnml = PnmlFactory.create_pnml(PnmlFinalMarkings.TAG, parent)
        assert isinstance(pnml, PnmlFinalMarkings)
