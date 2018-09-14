#!/usr/bin/env python

"""This is the unit test module.

This module test classes in base module.
"""


from podspy.petrinet.pnml.base import *
from podspy.petrinet.pnml import elements as emt
from podspy.utils import attributes as attrib
from collections import namedtuple


class MockPnmlAnnotation(emt.PnmlAnnotation):
    TAG = 'mock'

    def __init__(self, text=None):
        super().__init__(MockPnmlAnnotation.TAG, text)


class MockPnmlGraphics:
    def __init__(self):
        self.converted = False

    def convert_to_net(self, element):
        self.converted = True


class TestPnmlAnnotation:
    MockPnmlText = namedtuple('MockPnmlText', ['text',])
    MockElement = namedtuple('MockElement', ['map'])

    def test_make_annotation(self):
        annot = MockPnmlAnnotation()
        assert isinstance(annot, MockPnmlAnnotation)
        assert isinstance(annot, emt.PnmlAnnotation)

    def test_convert_to_net_has_text(self):
        text = 'hello world'
        mock_pnml_text = TestPnmlAnnotation.MockPnmlText(text=text)
        mock_element = TestPnmlAnnotation.MockElement(map=dict())

        annot = MockPnmlAnnotation(text=mock_pnml_text)
        annot.convert_to_net(mock_element)

        assert len(mock_element.map) == 1
        assert mock_element.map[attrib.LABEL] == text

    def test_convert_to_net_has_graphics(self):
        mock_graphics = MockPnmlGraphics()
        mock_element = TestPnmlAnnotation.MockElement(map=dict())

        annot = MockPnmlAnnotation()
        annot.graphics = mock_graphics

        annot.convert_to_net(mock_element)

        assert mock_graphics.converted == True


class TestPnmlText:
    def test_make_no_text(self):
        text = PnmlBaseFactory.create_pnml_text()
        assert isinstance(text, PnmlText)
        assert text.text == ''

    def test_make_with_text(self):
        text = 'hello world'
        pnml_text = PnmlBaseFactory.create_pnml_text(text)
        assert isinstance(pnml_text, PnmlText)
        assert pnml_text.text == text

    def test_add_text(self):
        text = 'hello world'
        pnml_text = PnmlBaseFactory.create_pnml_text()
        assert pnml_text.text == ''

        # add text
        pnml_text.add_text(text)
        assert pnml_text.text == text
