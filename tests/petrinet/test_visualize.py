#!/usr/bin/env python

"""This is the unit test module.

This module tests the visualize module.
"""


import os, logging
from podspy.petrinet.pnml import io
from podspy.petrinet import visualize as vis
import pygraphviz as pgv


logger = logging.getLogger(__file__)


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def test_ptnet2dot():
    net_fp = os.path.join('.', 'tests', 'testdata', 'net1.pnml')
    with open(net_fp, 'r') as f:
        pnml = io.import_pnml_from_file(f)
    ptnet, marking, final_markings = io.pnml2ptnet(pnml)

    G = vis.net2dot(ptnet, marking, layout='dot')

    for t in ptnet.transitions:
        logger.debug(list(G.get_node(t).attr.items()))

    for p in ptnet.places:
        logger.debug(list(G.get_node(p).attr.items()))

    for e in ptnet.arcs:
        logger.debug((e.src, e.target))
        logger.debug(list(G.get_edge(e.src, e.target, key=e).attr.items()))

    # uncomment to draw out the figure
    # G.draw('./simple-with-marking.png')

    assert isinstance(G, pgv.AGraph)

    G = vis.net2dot(ptnet, layout='dot')
    # same as above
    # G.draw('./simple.png')

    assert isinstance(G, pgv.AGraph)

