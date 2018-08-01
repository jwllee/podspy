#!/usr/bin/env python

"""This is the example module.

This module does stuff.
"""


from lxml import etree
import logging

from podspy.petrinet.pnml.factory import *
from podspy.petrinet.pnml.element import *
from podspy.petrinet.pnml.base import *
from podspy.petrinet.pnml.extension import *

from podspy.petrinet.factory import *
from podspy.petrinet.semantics import *
from podspy.petrinet.net import AbstractResetInhibitorNet, AcceptingPetrinet


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


logger = logging.getLogger(__file__)


def make_from_element(element, parent_cls):
    pnml = PnmlFactory.create_pnml(element.tag, parent_cls)

    # logger.debug('Making {!r} into {!r}'.format(element, pnml.__class__.__name__))

    pnml.add_attrib(element.attrib)

    # logger.debug('Adding {} as text to {}'.format(element.text, pnml))
    pnml.add_text(element.text)
    # if isinstance(pnml, PnmlText):
        # logger.debug('After adding {} as text: {}'.format(element.text, pnml))

    for c in element.getchildren():
        # recursively call make from element on the child element
        pnml_child = make_from_element(c, pnml.__class__)

        if isinstance(pnml, PnmlPlace):
            logger.debug('Adding {!r} as child of {!r}'.format(c, pnml.name))
        # if isinstance(pnml, PnmlNet):
        #     logger.debug('Adding {!r} as child of {!r}'.format(pnml_child, pnml))
        # if isinstance(pnml, PnmlName):
        #     logger.debug('Adding {!r} as child of {!r}'.format(pnml_child, pnml))

        pnml.add_child(pnml_child)

    return pnml


def import_pnml_from_file(file):
    tree = etree.parse(file)
    root = tree.getroot()

    # should be <pnml>
    assert root.tag == Pnml.TAG, 'Root tag does not equal {}, not a pnml file'.format(Pnml.TAG)

    pnml = make_from_element(root, None)

    return pnml


def pnml2ptnet(pnml):
    pnml_net = pnml.net_list[0]
    net_label = pnml_net.name.text.text if pnml_net.name else 'net0'
    net = PetrinetFactory.new_petrinet(net_label)
    marking = Marking()
    final_markings = set()
    pnml.convert_to_net(net, marking, final_markings)
    return net, marking, final_markings


def ptnet2pnml(net, marking=None, final_markings=None, layout=None):
    marked_nets = {net: marking}
    final_marked_nets = {net: final_markings}
    pnml, id_map = PnmlElementFactory.net2pnml(marked_nets, final_marked_nets, layout)
    return pnml, id_map


def apnet2pnml(net, layout=None):
    return ptnet2pnml(net.net, net.init_marking, net.final_markings, layout)


def export_net(net, file, marking=None, final_markings=None, layout=None):
    if isinstance(net, AbstractResetInhibitorNet):
        pnml, id_map = ptnet2pnml(net, marking, final_markings, layout)
    elif isinstance(net, AcceptingPetrinet):
        pnml, id_map = apnet2pnml(net, layout)
    else:
        raise ValueError('Do not recognize net class: {}'.format(net.__class__))

    # traverse pnml to convert it as etree
    root = pnml.to_lxml()

    encoding = "ISO-8859-1"
    pretty_print = True

    string = etree.tostring(root, encoding=encoding, pretty_print=pretty_print)

    file.write(string.decode())

    return root, pnml, id_map
