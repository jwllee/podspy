#!/usr/bin/env python

"""This is the unit test module.

This module tests pnml io module.
"""

import os, logging

from podspy.petrinet.pnml import io
from podspy.petrinet.net import *
from podspy.petrinet.pnml.element import *
from podspy.petrinet.semantics import *


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


logger = logging.getLogger('tests')


def test_import_pnml():
    net_fp = os.path.join('.', 'tests', 'testdata', 'net1.pnml')
    f = open(net_fp, 'r')
    pnml = io.import_pnml_from_file(f)
    assert pnml is not None
    assert isinstance(pnml, Pnml)


def test_import_petrinet():
    net_fp = os.path.join('.', 'tests', 'testdata', 'simple.pnml')
    f = open(net_fp, 'r')
    pnml = io.import_pnml_from_file(f)
    net, marking, final_markings = io.pnml2ptnet(pnml)

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
