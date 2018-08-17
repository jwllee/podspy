#!/usr/bin/env python

"""This is the product module.

This module contains functions related to computing the synchronous net product between a trace
and net. However, note that this is not actually practical because this is not very efficient nor
useful (since A* is performed on the state space of the synchronous net product).
"""
import pygraphviz as pgv

from podspy.petrinet import factory as fty
from podspy.petrinet import semantics as smc
from podspy.petrinet import nets as nts


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


class SyncNetProductFactory:
    @staticmethod
    def new_snp(trace, apn, label_sync=''):
        pn, init, finals = apn

        if label_sync == '':
            label_sync = 'spn-{}'.format(pn.label)

        pn_sync = fty.PetrinetFactory.new_petrinet(label_sync)

        # add places of net
        place_map = dict()
        for p in pn.places:
            p_sync = pn_sync.add_place(p.label)
            place_map[p.label] = p_sync

        trans_map = dict()
        arc_map = dict()
        trans_list_map = dict()
        for t in pn.transitions:
            if t.label not in trans_list_map:
                trans_list_map[t.label] = list()

            trans_list_map[t.label].append(t)

            # model move
            t_model = pn_sync.add_transition('({}, {})'.format(SyncNetProduct.NOMOVE, t.label))
            trans_map[t] = t_model

            # arcs from pn
            for arc in pn.in_edge_map[t]:
                p_sync = place_map[arc.src.label]
                arc_sync = pn_sync.add_arc(p_sync, t_model, arc.weight)
                arc_map[arc] = arc_sync

            for arc in pn.out_edge_map[t]:
                p_sync = place_map[arc.target.label]
                arc_sync = pn_sync.add_arc(t_model, p_sync, arc.weight)
                arc_map[arc] = arc_sync

        cur_p, init_trace, final_trace = None, None, None
        for i in range(len(trace)):
            if i == 0:
                # initial marking place of trace net
                cur_p = pn_sync.add_place('log-p{}'.format(i))
                init_trace = smc.Marking([cur_p])

            # add log move
            event_i = trace[i]
            t_log = pn_sync.add_transition('({}, {})'.format(event_i, SyncNetProduct.NOMOVE))
            pn_sync.add_arc(cur_p, t_log)
            cur_p = pn_sync.add_place('log-p{}'.format(i + 1))
            pn_sync.add_arc(t_log, cur_p)
            trans_map[event_i] = t_log

            if i == len(trace) - 1:
                final_trace = smc.Marking([cur_p])

            # add sync move, check if net has the event label first
            if event_i in trans_list_map:
                for t in trans_list_map[event_i]:
                    t_sync = pn_sync.add_transition('({}, {})'.format(event_i, t.label))

                    # arcs from net
                    for arc in pn.in_edge_map[t]:
                        p_sync = place_map[arc.src.label]
                        arc_sync = pn_sync.add_arc(p_sync, t_sync, arc.weight)
                        arc_map[arc] = arc_sync

                    for arc in pn.out_edge_map[t]:
                        p_sync = place_map[arc.target.label]
                        arc_sync = pn_sync.add_arc(t_sync, p_sync, arc.weight)
                        arc_map[arc] = arc_sync

                    # arc from trace net
                    for arc in pn_sync.in_edge_map[t_log]:
                        pn_sync.add_arc(arc.src, t_sync, arc.weight)

                    for arc in pn_sync.out_edge_map[t_log]:
                        pn_sync.add_arc(t_sync, arc.target, arc.weight)

        # join init and final markings
        init_sync = init_trace
        for p in init:
            p_sync = place_map[p.label]
            init_sync.add(p_sync)

        finals_sync = set()
        for final in finals:
            # create new final marking that combines the final marking of trace net
            final_sync = final + final_trace
            finals_sync.add(final_sync)

        apn_sync = fty.PetrinetFactory.new_accepting_petrinet(pn_sync, init_sync, finals_sync)
        snp = SyncNetProduct(apn, trace, apn_sync, place_map, trans_map, arc_map)
        return snp


class SyncNetProduct:
    NOMOVE = '>>'

    def __init__(self, apn, trace, snp, place_map, trans_map, arc_map):
        assert isinstance(apn, nts.AcceptingPetrinet)

        self.trace = trace
        self.apn = apn
        self.snp = snp
        self.place_map = place_map
        self.trans_map = trans_map
        self.arc_map = arc_map

    def visualize(self, layout='dot', rankdir='LR',
                  mlog_attribs=None, mmodel_attribs=None,
                  msync_attribs=None, minvis_attribs=None,
                  node_id_func=None, edge_id_func=None):
        G = pgv.AGraph(rankdir=rankdir)

        node_id_func = lambda n: str(n._id)
