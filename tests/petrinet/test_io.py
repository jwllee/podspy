#!/usr/bin/env python

"""This is the unit test module.

This module tests pnml io module.
"""

import os, logging, pytest
from io import StringIO

from podspy.petrinet.nets import *
from podspy.petrinet.pnml.elements import *
from podspy.petrinet.semantics import *
from podspy.petrinet import factory as fty, io


logger = logging.getLogger('tests')


@pytest.fixture
def net_fp():
    return os.path.join('.', 'tests', 'testdata', 'net1.pnml')


@pytest.fixture
def apna_fname():
    return 'simple.apna'


def test_import_pnml():
    net_fp = os.path.join('.', 'tests', 'testdata', 'net1.pnml')
    with open(net_fp, 'r') as f:
        pnml = io.import_pnml(f)

    assert pnml is not None
    assert isinstance(pnml, Pnml)


def test_import_petrinet():
    net_fp = os.path.join('.', 'tests', 'testdata', 'simple.pnml')
    with open(net_fp, 'r') as f:
        pnml = io.import_pnml(f)

    net, marking, final_markings = io.pnml_to_pn(pnml)

    assert isinstance(net, Petrinet)
    assert isinstance(marking, Marking)
    assert isinstance(final_markings, set)

    assert len(marking) == 1

    # there are 4 transitions
    logger.debug(net.transitions)

    trans_labels = set(map(lambda t: t.label, net.transitions))

    assert 'A' in trans_labels and \
           'B' in trans_labels and \
           'C' in trans_labels and \
           'skip' in trans_labels

    inv_trans = list(filter(lambda t: t.is_invisible == True, net.transitions))

    assert len(inv_trans) == 1, 'Invisible transitions: {}'.format(inv_trans)
    assert inv_trans[0].is_invisible == True

    # there are 3 places
    place_labels = set(map(lambda p: p.label, net.places))

    assert 'n1' in place_labels and \
           'n2' in place_labels and \
           'n3' in place_labels


def test_ptnet2pnml_without_layout(net_fp):
    with open(net_fp, 'r') as f:
        pnml = io.import_pnml(f)

    apnet = AcceptingPetrinet(*io.pnml_to_pn(pnml))

    converted_pnml = io.apn_to_pnml(apnet)

    assert isinstance(converted_pnml, Pnml)
    assert pnml == converted_pnml


# def test_ptnet2pnml_with_layout(net_fp):
#     with open(net_fp, 'r') as f:
#         pnml = io.import_pnml(f)
#
#     apnet = AcceptingPetrinet(*io.pnml2pn(pnml))
#
#     G = vis.net2dot(apnet.net, apnet.init_marking, layout='dot')
#     converted_pnml = io.apn2pnml(apnet, G)
#
#     assert isinstance(converted_pnml, Pnml)
#     assert pnml == converted_pnml


def test_export_petrinet_without_layout(net_fp):
    with open(net_fp, 'r') as f:
        pnml = io.import_pnml(f)

    net, marking, final_markings = io.pnml_to_pn(pnml)

    assert isinstance(marking, Marking)

    apnet = AcceptingPetrinet(net, marking, final_markings)

    out_f = StringIO('out_f')

    io.export_net(apnet, out_f)

    with open(net_fp, 'r') as f:
        expected = f.read()

    with open('./parsed.pnml', 'w') as f:
        io.export_net(apnet, f)

    assert expected == out_f.getvalue()


# def test_export_petrinet_with_layout(net_fp):
#     with open(net_fp, 'r') as f:
#         pnml = io.import_pnml(f)
#
#     net, marking, final_markings = io.pnml2pn(pnml)
#     G = vis.net2dot(net, marking, layout='dot')
#
#     assert isinstance(marking, Marking)
#
#     apn = fty.PetrinetFactory.new_accepting_petrinet(net, marking, final_markings)
#
#     out_f = StringIO('out_f')
#
#     io.export_net(apn, out_f, layout=G)
#
#     with open(net_fp, 'r') as f:
#         expected = f.read()
#
#     # with open('./parsed.pnml', 'w') as f:
#     #     io.export_pnml_to_file(apnet, f, layout=G)
#
#     assert expected == out_f.getvalue()


def test_import_apna(apna_fname):
    cwd = os.getcwd()
    dirpath = os.path.join('.', 'tests', 'testdata', 'simple-apna')
    os.chdir(dirpath)
    with open(apna_fname, 'r') as f:
        apna = io.import_apna(f)

    assert len(apna) == 2

    apn_0, apn_1 = apna

    assert isinstance(apn_0, AcceptingPetrinet)
    assert isinstance(apn_1, AcceptingPetrinet)

    # apn_0
    pn_0, init_0, final_0 = apn_0

    # apn_1
    pn_1, init_1, final_1 = apn_1

    os.chdir(cwd)

