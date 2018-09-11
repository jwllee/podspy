#!/usr/bin/env python

"""This is the unit test module for the alpha discovery module.

"""


import pytest, os

from podspy.discovery import alpha
from podspy.petrinet.nets import *
from podspy.petrinet import visualize as vis


class TestAlphaMiner:
    def test_alpha_simple_causal_matrix(self, simple_causal_matrix):
        net = alpha.discover(simple_causal_matrix)

        assert isinstance(net, AcceptingPetrinet)

        net_fp = os.path.join('.', 'tests', 'alpha.png')
        G = vis.net2dot(net.net)
        # G.draw(net_fp)
