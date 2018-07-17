#!/usr/bin/env python

"""This is the petri net module.

This module contains petri net classes.
"""

from abc import abstractmethod
from podspy.graph import directed
from podspy.petrinet.element import *
import pandas as pd
import numpy as np


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = [
    'ResetNet',
    'ResetInhibitorNet',
    'InhibitorNet',
    'Petrinet'
]


class AbstractResetInhibitorNet(directed.AbstractDirectedGraph):
    @abstractmethod
    def __init__(self, allows_reset, allows_inhibitors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transitions = set()
        self.places = set()
        self.arcs = set()
        self.reset_arcs = set() if allows_reset else frozenset()
        self.inhibitor_arcs = set() if allows_inhibitors else frozenset()

    def get_edges(self, src=None, target=None, collection=None):
        if not (src is None or target is None or collection is None):
            return super().get_edges(src, target, collection)
        else:
            edges = set()
            edges.update(self.arcs)
            edges.update(self.inhibitor_arcs)
            edges.update(self.reset_arcs)

    def get_nodes(self):
        nodes = set()
        nodes.update(self.transitions)
        nodes.update(self.places)
        return nodes

    def add_reset_arc(self, p, t, label=None):
        self.check_add_edge(p, t)
        label = '{} -->> {}'.format(p, t) if label is None else label
        a = ResetArc(p, t, label)
        if a not in self.reset_arcs:
            self.reset_arcs.add(a)
            self.graph_element_added(a)
        else:
            # modify the existing arc label
            for existing in self.reset_arcs:
                if existing == a:
                    if label is not None:
                        existing.label = label
                    # return the existing arc if it's already in the net
                    return existing
        return None

    def remove_reset_arc(self, p, t):
        self.remove_from_edges(p, t, self.reset_arcs)

    def add_inhibitor_arc(self, p, t, label):
        self.check_add_edge(p, t)
        label = '{} ---O {}'.format(p, t) if label is None else label
        a = InhibitorArc(p, t, label)
        if a not in self.inhibitor_arcs:
            self.inhibitor_arcs.add(a)
            self.graph_element_added(a)
        else:
            # modify the existing arc label
            for existing in self.inhibitor_arcs:
                if existing == a:
                    if label is not None:
                        existing.label = label
                    # return the existing arc if it's already in the net
                    return existing
        return None

    def remove_inhibitor_arc(self, p, t):
        self.remove_from_edges(p, t, self.inhibitor_arcs)

    def get_inhibitor_arc(self, p, t):
        arcs = self.get_edges(p, t, self.inhibitor_arcs)
        return next(arcs)

    def get_reset_arc(self, p, t):
        arcs = self.get_edges(p, t, self.reset_arcs)
        return next(arcs)

    def add_transition(self, label):
        t = Transition(self, label)
        self.transitions.add(t)
        self.graph_element_added(t)
        return t

    def add_place(self, label):
        p = Place(self, label)
        self.places.add(p)
        self.graph_element_added(p)
        return p

    def add_arc_private(self, src, target, weight):
        self.check_add_edge(src, target)
        a = Arc(src, target, weight)
        if a not in self.arcs:
            self.arcs.add(a)
            self.graph_element_added(a)
        else:
            for existing in self.arcs:
                if existing == a:
                    existing.weight += weight
                    return existing
        return None

    def add_arc(self, src, target, weight=1):
        return self.add_arc_private(src, target, weight)

    def remove_arc(self, src, target):
        a = self.remove_from_edges(src, target, self.arcs)
        return a

    def remove_edge(self, edge):
        if isinstance(edge, InhibitorArc):
            self.inhibitor_arcs.remove(edge)
        elif isinstance(edge, ResetArc):
            self.reset_arcs.remove(edge)
        elif isinstance(edge, Arc):
            self.arcs.remove(edge)
        else:
            raise ValueError('Do not recognize edge class: '
                             '{}'.format(edge.__class__))
        self.graph_element_removed(edge)

    def remove_place(self, p):
        self.remove_surrounding_edges(p)
        return self.remove_node_from_collection(self.places, p)

    def remove_transition(self, t):
        self.remove_surrounding_edges(t)
        return self.remove_node_from_collection(self.transitions, t)

    def remove_node(self, node):
        if isinstance(node, Place):
            self.remove_place(node)
        elif isinstance(node, Transition):
            self.remove_transition(node)
        else:
            raise ValueError('Do not recognize node class: '
                             '{}'.format(node.__class__))

    def clone_from(self, net, transitions=True, places=True, arcs=True,
                   resets=True, inhibitors=True):
        mapping = dict()

        if transitions:
            for t in net.transitions:
                copy = self.add_transition(t.label)
                copy._is_invisible = t.is_invisible
                copy.local_id = t.local_id
                mapping[t] = copy

        if places:
            for p in net.places:
                copy = self.add_place(p.label)
                copy.local_id = p.local_id
                mapping[p] = copy

        if arcs:
            for a in net.arcs:
                copied_src = mapping[a.src]
                copied_target = mapping[a.target]
                copy = self.add_arc_private(copied_src, copied_target, a.weight)
                copy.local_id = a.local_id
                mapping[a] = copy

        if inhibitors:
            for a in net.inhibitor_arcs:
                copied_src = mapping[a.src]
                copied_target = mapping[a.target]
                copy = self.add_inhibitor_arc(copied_src, copied_target, a.label)
                copy.local_id = a.local_id
                mapping[a] = copy

        if resets:
            for a in net.reset_arcs:
                copied_src = mapping[a.src]
                copied_target = mapping[a.target]
                copy = self.add_reset_arc(copied_src, copied_target, a.label)
                copy.local_id = a.local_id
                mapping[a] = copy

        return mapping


class ResetInhibitorNet(AbstractResetInhibitorNet):
    def __init__(self, label, *args, **kwargs):
        super().__init__(True, True, *args, **kwargs)
        self.label = label

    def __repr__(self):
        return '{}({})'.format(self.__class__, self.label)

    def get_empty_clone(self):
        return ResetInhibitorNet(self.label)


class InhibitorNet(AbstractResetInhibitorNet):
    def __init__(self, label, *args, **kwargs):
        super().__init__(False, True, *args, **kwargs)
        self.label = label

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.label)

    def get_empty_clone(self):
        return InhibitorNet(self.label)


class ResetNet(AbstractResetInhibitorNet):
    def __init__(self, label, *args, **kwargs):
        super().__init__(True, False, *args, **kwargs)
        self.label = label

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.label)

    def get_empty_clone(self):
        return ResetNet(self.label)


class Petrinet(AbstractResetInhibitorNet):
    def __init__(self, label, *args, **kwargs):
        super().__init__(False, False, *args, **kwargs)
        self.label = label

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.label)

    def get_empty_clone(self):
        return Petrinet(self.label)

    def get_transition_relation_dfs(self):
        nb_trans = len(self.transitions)
        nb_places = len(self.places)
        mat = np.zeros(shape=(nb_places, nb_trans))
        sorted_trans = sorted(self.transitions, key=lambda t: t.label)
        sorted_places = sorted(self.places, key=lambda p: p.label)

        # matrix defining the place to transition relations
        p_to_t_df = pd.DataFrame(mat, columns=sorted_trans, index=sorted_places)

        # matrix defining the transition to place relations
        t_to_p_df = pd.DataFrame(mat, columns=sorted_trans, index=sorted_places)

        for t in sorted_trans:
            # should only have Arc edges as a Petrinet
            out_edges_from_t = filter(lambda e: e.src == t, self.out_edge_map)
            out_p_from_t = map(lambda e: (e.target, e.weight), out_edges_from_t)
            places, weights = zip(*out_p_from_t)
            p_to_t_df.loc[places, t] = weights

            in_edges_to_t = filter(lambda e: e.target == t, self.in_edge_map)
            in_p_to_t = map(lambda e: (e.src, e.weight), in_edges_to_t)
            places, weights = zip(*in_p_to_t)
            t_to_p_df.loc[places, t] = weights

        return p_to_t_df, t_to_p_df

    def __str__(self):
        p_to_t_df, t_to_p_df = self.get_transition_relation_dfs()
        # difference because arcs from places to transitions consume tokens while
        # arcs from transitions to places produce tokens
        full_df = t_to_p_df - p_to_t_df
        return str(full_df)
