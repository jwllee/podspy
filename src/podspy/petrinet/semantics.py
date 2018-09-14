#!/usr/bin/env python

"""This is the petri net semantics module.

This module contains classes that relate to the semantics of petri nets.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import itertools as its

from podspy.utils.multiset import SortedMultiSet
from podspy.petrinet.elements import *


__all__ = [
    'Marking',
    'PetrinetExecutionInformation',
    'InhibitorNetSemantics',
    'ResetInhibitorNetSemantics',
    'ResetNetSemantics',
    'ElementaryInhibitorNetSemantics',
    'ElementaryPetrinetSemantics',
    'ElementaryResetInhibitorNetSemantics',
    'ElementaryResetNetSemantics',
    'EfficientPetrinetSemantics'
]


class Marking(SortedMultiSet):
    def __init__(self, *places):
        super().__init__(*places)

    def as_series(self, places):
        '''Converts marking as a series, i.e., vector with labels

        :param places: all the possible places
        :type places: podspy.petrinet.elements.Place
        :return: the state as a series
        :rtype: pandas.Series
        '''
        plabel_list = map(lambda p: p.label, places)
        ss = pd.Series(np.zeros(len(places)), index=plabel_list)
        tplaces, token_cnt = zip(*self.map.items())
        tplabel_list = map(lambda p: p.label, tplaces)
        ss[tplabel_list] = token_cnt
        return ss

    def from_series(self, marking_series, pmap):
        repeat_place = lambda plabel: its.repeat(pmap[plabel], marking_series[plabel])
        places = map(repeat_place, marking_series.index)
        return Marking(places)


class PetrinetExecutionInformation():
    def __init__(self, necessary, tokens_consumed, tokens_produced, transition):
        self.necessary = necessary
        self.tokens_consumed = tokens_consumed
        self.tokens_produced = tokens_produced
        self.transition = transition

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, self.tokens_consumed, self.tokens_produced,
                                           self.necessary, self.transition)

    def __str__(self):
        return '{}, Necessary: {}, Produced: {}, Consumed: {}'.format(self.transition, self.necessary,
                                                                      self.tokens_produced, self.tokens_consumed)


class AbstractResetInhibitorNetSemantics(ABC):
    @abstractmethod
    def __init__(self, state=None, transitions=None):
        self.state = state
        self.transitions = transitions

    def get_required(self, transition):
        '''Gets the required marking (places with tokens) to enable a transition

        :param transition: transition to fire
        :type transition: podspy.petrinet.elements.Transition
        :return: required marking to fire transition
        :rtype: podspy.petrinet.semantics.Marking
        '''
        edges = transition.graph.in_edge_map[transition]
        src_places = map(lambda e: e.src, edges)
        required = Marking(src_places)
        return required

    def get_produced(self, transition):
        edges = transition.graph.out_edge_map[transition]
        produced = Marking()
        for e in edges:
            if isinstance(e, Arc):
                produced.add(e.target, e._weight)
        return produced

    def get_removed(self, transition):
        edges = transition.graph.in_edge_map[transition]
        # get the consumed tokens from executing the transition
        removed = self.get_required(transition)
        for e in edges:
            if isinstance(e, ResetArc):
                removed.add(e.src, self.state.occurrences(e.src))
        return removed

    def is_enabled(self, state, required, transition):
        # the required state is less than or equal to the given state on all
        # the places of the base set of the given state
        # For ProM developers: Note that this is different from the ProM
        # where the multiset.isLessOrEqual(multiset1) is still true if
        # multiset1 contains items that are not in multiset.
        leq = lambda p: required.occurrences(p) <= state.occurrences(p)
        if all(map(leq, state.base_set())):
            for e in transition.graph.get_in_edges(transition):
                if isinstance(e, InhibitorArc):
                    # inhibitor arc prevents the firing the target transition if the source place has tokens
                    if state.occurrences(e.src) > 0:
                        return False
            return True
        return False

    def exec_transition(self, transition):
        '''Execute executable transition

        :param transition: Transition
        :return:
        '''
        required = self.get_required(transition)
        if not self.is_enabled(self.state, required, transition):
            raise ValueError('Transition {} is not enabled in marking {}'.format(transition, self.state))

        # compute the resulting marking following the production and consumption of tokens
        produced = self.get_produced(transition)
        consumed = self.get_removed(transition)
        self.state = self.state + produced - consumed
        return PetrinetExecutionInformation(required, consumed, produced, transition)

    def get_executable_transitions(self):
        enabled = list()
        if self.transitions:
            for t in self.transitions:
                required = self.get_required(t)
                if self.is_enabled(self.state, required, t):
                    enabled.append(t)
        return enabled

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.state, self.transitions)

    def __str__(self):
        return 'Regular Semantics'

    def __eq__(self, other):
        if other is None:
            return False
        return isinstance(other, self.__class__)

    def __hash__(self):
        return hash(self.__class__.__name__)


class AbstractElementarynetSemantics(AbstractResetInhibitorNetSemantics):
    '''Implementation of elementary-net semantics. In this semantics, a transition only fires if all of its output
    places are empty

    '''
    def get_executable_transitions(self):
        if self.state is None:
            return None
        enabled = list()
        for t in self.transitions:
            required = self.get_required(t)
            if self.is_enabled(self.state, required, t):
                # check that all the output places are empty
                # only check the Arc edges
                arcs = filter(lambda e: isinstance(e, Arc), t.graph.out_edge_map[t])
                # we check the output place of the arc: a.target
                not_empty = map(lambda arc: self.state.occurrences(arc.target) > 0, arcs)
                # at least one place is not empty
                if any(not_empty):
                    continue
                # all output places are empty
                enabled.append(t)
        return enabled

    def __str__(self):
        return 'Elementary Semantics'


class InhibitorNetSemantics(AbstractResetInhibitorNetSemantics):
    def __init__(self):
        super().__init__()


class ResetInhibitorNetSemantics(AbstractResetInhibitorNetSemantics):
    def __init__(self):
        super().__init__()


class ResetNetSemantics(AbstractResetInhibitorNetSemantics):
    def __init__(self):
        super().__init__()


class ElementaryInhibitorNetSemantics(AbstractElementarynetSemantics):
    def __init__(self):
        super().__init__()


class ElementaryPetrinetSemantics(AbstractElementarynetSemantics):
    def __init__(self):
        super().__init__()


class ElementaryResetInhibitorNetSemantics(AbstractElementarynetSemantics):
    def __init__(self):
        super().__init__()


class ElementaryResetNetSemantics(AbstractElementarynetSemantics):
    def __init__(self):
        super().__init__()


class EfficientPetrinetSemantics():
    def __init__(self, net, init_marking=None):
        # get the matrices that mark the number of tokens consumed and produced
        # per transition per place
        self.consuming, self.producing = net.get_transition_relation_dfs()
        self.transitions = sorted(net.transitions, key=lambda t: t.label)
        self.places = sorted(net.places, key=lambda p: p.label)
        self.state = init_marking.as_series(self.places)
        # transition relation matrix
        self.effect = self.producing - self.consuming

    def is_enabled(self, transition):
        if transition not in self.transitions:
            raise ValueError('Transition {} is unknown'.format(transition))

        # Conditions for transition to be enabled:
        # - Current state should have more than or equal tokens than the needed_tokens
        #   vector in in all the places
        needed_tokens = self.consuming.loc[:, transition.label]
        diff = self.state - needed_tokens
        return (diff > 0).all()

    def exec_transition(self, transition):
        if transition not in self.transitions:
            raise ValueError('Transition {} is unknown'.format(transition))

        assert self.is_enabled(transition), \
            'Transition {} is not enabled at marking {}'.format(transition, self.state)

        effect_on_tokens = self.effect[transition.label]

        # update current state
        self.state += effect_on_tokens

    def get_executable_transitions(self):
        enabled = filter(lambda t: self.is_enabled(t), self.transitions)
        return list(enabled)
