#!/usr/bin/env python

"""This is the product module.

This module contains functions related to computing the synchronous net product between a trace
and net. However, note that this is not actually practical because this is not very efficient nor
useful (since A* is performed on the state space of the synchronous net product).
"""
import pygraphviz as pgv

from podspy.petrinet import factory as fty
from podspy.petrinet import semantics as smc


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


class SyncNetProduct:
    def __init__(self, trace, net):
        self.trace = trace
        self.net = net

    def trace2apn(self, trace, net_label=''):
        pn = fty.PetrinetFactory.new_petrinet(net_label)
        place_id = 0
        cur_place = pn.add_place('p{}'.format(place_id))
        place_id += 1

        # initial marking
        init = smc.Marking([cur_place, ])
        finals = set()

        for event in trace:
            trans = pn.add_transition(event)
            pn.add_arc(cur_place, trans)
            cur_place = pn.add_place('p{}'.format(place_id))
            place_id += 1
            pn.add_arc(trans, cur_place)

        # final marking
        final = smc.Marking([cur_place, ])
        finals.add(final)

        return fty.PetrinetFactory.new_accepting_petrinet(pn, init, finals)


    def visualize(self, layout='dot', rankdir='LR',
                  mlog_attribs=None, mmodel_attribs=None,
                  msync_attribs=None, minvis_attribs=None,
                  node_id_func=None, edge_id_func=None):
        pass
