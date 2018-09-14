#!/usr/bin/env python

"""This is the unit test module.

This module tests classes in pnml element module.
"""


from podspy.petrinet.pnml.elements import *


class TestPnml:

    class MockPnmlNet:
        def __init__(self):
            self.converted = False

        def convert_to_net(self, net, marking, final_markings, place_map,
                           trans_map, edge_map):
            self.converted = True

    def test_convert_to_net(self):
        pnml = PnmlElementFactory.create_pnml()
        mock_net0 = TestPnml.MockPnmlNet()

        pnml.net_list.append(mock_net0)

        assert mock_net0.converted == False

        net, marking, final_markings = (None, None, None)
        pnml.convert_to_net(net, marking, final_markings)

        assert mock_net0.converted == True


class TestPnmlElementFactory:
    def test_create_pnml(self):
        pnml = PnmlElementFactory.create_pnml()
        assert isinstance(pnml, Pnml)

    def test_create_arc(self):
        pnml = PnmlElementFactory.create_arc()
        assert isinstance(pnml, PnmlArc)

    def test_create_name(self):
        pnml = PnmlElementFactory.create_name()
        assert isinstance(pnml, PnmlName)

    def test_create_net(self):
        pnml = PnmlElementFactory.create_net()
        assert isinstance(pnml, PnmlNet)

    def test_create_page(self):
        pnml = PnmlElementFactory.create_page()
        assert isinstance(pnml, PnmlPage)

    def test_create_place(self):
        pnml = PnmlElementFactory.create_place()
        assert isinstance(pnml, PnmlPlace)

    def test_create_ref_place(self):
        pnml = PnmlElementFactory.create_ref_place()
        assert isinstance(pnml, PnmlReferencePlace)

    def test_create_ref_trans(self):
        pnml = PnmlElementFactory.create_ref_trans()
        assert isinstance(pnml, PnmlReferenceTransition)

    def test_create_trans(self):
        pnml = PnmlElementFactory.create_trans()
        assert isinstance(pnml, PnmlTransition)

    def test_create_tool_specific(self):
        pnml = PnmlElementFactory.create_tool_specific()
        assert isinstance(pnml, PnmlToolSpecific)
