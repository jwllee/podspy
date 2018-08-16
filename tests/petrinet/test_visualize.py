#!/usr/bin/env python

"""This is the unit test module.

This module tests the visualize module.
"""


import os, logging, pytest
from podspy.petrinet import visualize as vis, io
import pygraphviz as pgv


logger = logging.getLogger(__file__)


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def test_ptnet2dot():
    net_fp = os.path.join('.', 'tests', 'testdata', 'net1.pnml')
    with open(net_fp, 'r') as f:
        pnml = io.import_pnml(f)
    ptnet, marking, final_markings = io.pnml2pn(pnml)

    G = vis.net2dot(ptnet, marking, layout='dot')

    # uncomment to draw out the figure
    # G.draw('./simple-with-marking.png')

    assert isinstance(G, pgv.AGraph)

    G = vis.net2dot(ptnet, layout='dot')
    # same as above
    # with open('./dotfile', 'w') as f:
    #     print(G, file=f)

    # G.draw('./simple.png')

    assert isinstance(G, pgv.AGraph)


def test_netarray2dot():
    cwd = os.getcwd()
    apna_dir = os.path.join('.', 'tests', 'testdata', 'simple-apna')
    # os.chdir(apna_dir)
    apna_fp = os.path.join(apna_dir, 'simple.apna')

    apna = io.import_apna(apna_fp)

    node_constraints = list()
    label2trans = dict()

    for apn in apna:
        # print('Number of transitions in net: {}'.format(len(apn.net.transitions)))
        for t in apn.net.transitions:
            # print('Transition {}'.format(t.label))
            if t.label not in label2trans:
                label2trans[t.label] = list()
            label2trans[t.label].append(t)

    # print('Number of sub-nets: {}'.format(len(apna)))

    for key, values in label2trans.items():
        if len(values) > 1:
            node_constraints.append(values)
            trans_eq = values[0] == values[1]
            # print('{} == {}: {}'.format(values[0], values[1], trans_eq))

    G = vis.netarray2dot(apna, node_constraints=node_constraints, constraint_style='dotted')
    # os.chdir(cwd)

    # with open('./dotfile', 'w') as f:
    #     print(G, file=f)

    # G.draw('./simple-apna.png')


