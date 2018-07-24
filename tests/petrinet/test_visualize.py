#!/usr/bin/env python

"""This is the unit test module.

This module tests the visualize module.
"""


import os
from podspy.petrinet.pnml import io
from podspy.petrinet import visualize as vis
import pygraphviz as pgv


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def test_ptnet2dot():
    net_fp = os.path.join('.', 'tests', 'testdata', 'net1.pnml')
    with open(net_fp, 'r') as f:
        pnml = io.import_pnml_from_file(f)
    ptnet, marking, final_markings = io.pnml2ptnet(pnml)

    G = vis.net2dot(ptnet, marking, layout='dot')
    # uncomment to draw out the figure
    # G.draw('./simple-with-marking.png')

    assert isinstance(G, pgv.AGraph)

    G = vis.net2dot(ptnet, layout='dot')
    # same as above
    # G.draw('./simple.png')

    assert isinstance(G, pgv.AGraph)

