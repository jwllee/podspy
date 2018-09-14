#!/usr/bin/env python

"""This is the example module.

This module does stuff.
"""


from lxml import etree
import logging, os, sys

from podspy.petrinet.pnml import elements as pnml_ems
from podspy.petrinet.pnml import factory as pnml_fty

from podspy.petrinet import factory as fty
from podspy.petrinet import semantics as smc
from podspy.petrinet import nets as nts


logger = logging.getLogger(__file__)


def make_from_element(element, parent_cls):
    pnml = pnml_fty.PnmlFactory.create_pnml(element.tag, parent_cls)

    # logger.debug('Making {!r} into {!r}'.format(element, pnml.__class__.__name__))

    pnml.add_attrib(element.attrib)

    # logger.debug('Adding {} as text to {}'.format(element.text, pnml))
    pnml.add_text(element.text)
    # if isinstance(pnml, PnmlText):
        # logger.debug('After adding {} as text: {}'.format(element.text, pnml))

    for c in element.getchildren():
        # recursively call make from element on the child element
        pnml_child = make_from_element(c, pnml.__class__)

        if isinstance(pnml, pnml_ems.PnmlPlace):
            logger.debug('Adding {!r} as child of {!r}'.format(c, pnml.name))
        # if isinstance(pnml, PnmlNet):
        #     logger.debug('Adding {!r} as child of {!r}'.format(pnml_child, pnml))
        # if isinstance(pnml, PnmlName):
        #     logger.debug('Adding {!r} as child of {!r}'.format(pnml_child, pnml))

        pnml.add_child(pnml_child)

    return pnml


def import_pnml(file):
    tree = etree.parse(file)
    root = tree.getroot()

    # should be <pnml>
    assert root.tag == pnml_ems.Pnml.TAG, 'Root tag does not equal {}, not a pnml file'.format(pnml_ems.Pnml.TAG)

    pnml = make_from_element(root, None)

    return pnml


def import_apnml(file):
    return import_pnml(file)


def import_apna(file, dirpath=None):
    if dirpath is None:
        dirpath = os.path.join(*(file.name.split(os.sep)[:-1]))

    apna = []
    for pn_fp in file:
        pn_fp = os.path.join(dirpath, pn_fp.strip())
        assert os.path.isfile(pn_fp) == True

        with open(pn_fp, 'r') as f:
            pnml = import_apnml(f)
            net, init, final = pnml_to_pn(pnml)

            # logger.debug('No. of trans: {}'.format(len(net.transitions)))
            # for t in net.transitions:
            #     logger.debug('Transition: {}'.format(t.label))

            apn = fty.PetrinetFactory.new_accepting_petrinet(net, init, final)
            apna.append(apn)

    return apna


def pnml_to_pn(pnml):
    pnml_net = pnml.net_list[0]
    net_label = pnml_net.name.text.text if pnml_net.name else 'net0'
    net = fty.PetrinetFactory.new_petrinet(net_label)
    marking = smc.Marking()
    final_markings = set()
    pnml.convert_to_net(net, marking, final_markings)
    return net, marking, final_markings


def pn_to_pnml(net, marking=None, final_markings=None):
    marked_nets = {net: marking}
    final_marked_nets = {net: final_markings}
    pnml, id_map = pnml_fty.PnmlElementFactory.net2pnml(marked_nets, final_marked_nets)
    return pnml, id_map


def apn_to_pnml(net):
    return pn_to_pnml(net.net, net.init_marking, net.final_markings)


def export_net(net, file, marking=None, final_markings=None):
    if isinstance(net, nts.AbstractResetInhibitorNet):
        pnml, id_map = pn_to_pnml(net, marking, final_markings)
    elif isinstance(net, nts.AcceptingPetrinet):
        pnml, id_map = apn_to_pnml(net)
    else:
        raise ValueError('Do not recognize net class: {}'.format(net.__class__))

    # traverse pnml to convert it as etree
    root = pnml.to_lxml()

    encoding = "ISO-8859-1"
    pretty_print = True

    string = etree.tostring(root, encoding=encoding, pretty_print=pretty_print)

    file.write(string.decode())

    return root, pnml, id_map
