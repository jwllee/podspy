#!/usr/bin/env python3


import os
import pygraphviz as pgv

from podspy import petrinet


def test_net_to_agraph():
    net_fp = os.path.join('.', 'tests', 'testdata', 'simple.pnml')

    with open(net_fp, 'r') as f:
        pnml = petrinet.import_pnml(f)

    net, marking, final_markings = petrinet.pnml_to_pn(pnml)

    G = petrinet.to_agraph(net, marking=marking)

    out_fp = './simple-with-marking.png'
    G.draw(out_fp, prog='dot')

    # without marking
    G = petrinet.to_agraph(net)

    out_fp = './simple.png'
    G.draw(out_fp, prog='dot')


def test_apn_to_agraph():
    net_fp = os.path.join('.', 'tests', 'testdata', 'simple.pnml')

    with open(net_fp, 'r') as f:
        pnml = petrinet.import_pnml(f)

    net, marking, final_markings = petrinet.pnml_to_pn(pnml)
    apn = petrinet.PetrinetFactory.new_accepting_petrinet(net, marking, final_markings)

    G = petrinet.to_agraph(apn, marking=marking)

    out_fp = './simple-apn.png'
    G.draw(out_fp, prog='dot')


def test_narray_to_agraph():
    apna_dir = os.path.join('.', 'tests', 'testdata', 'simple-apna')
    apna_fp = os.path.join(apna_dir, 'simple.apna')

    with open(apna_fp, 'r') as f:
        apna = petrinet.import_apna(f)

    nconstraints = list()
    label_to_trans = dict()

    for apn in apna:
        for t in apn.net.transitions:
            if t.label not in label_to_trans:
                label_to_trans[t.label] = list()
            label_to_trans[t.label].append(t)

    for key, values in label_to_trans.items():
        if len(values) > 1:
            # this means this transition has duplicated label
            nconstraints.append(values)

    G = petrinet.to_agraph(apna, nconstraints=nconstraints, cstyle='dotted')

    out_fp = './simple-apna.png'
    G.draw(out_fp, prog='dot')
