#!/usr/bin/env python

"""This is the petri net factory module.

This module contains Petri net factory to make petri nets.
"""

from podspy.petrinet.net import *
from podspy.petrinet import semantics as smc


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = [
    'PetrinetFactory'
]


class PetrinetFactory:
    @classmethod
    def new_petrinet(cls, label):
        return Petrinet(label)

    @classmethod
    def new_reset_net(cls, label):
        return ResetNet(label)

    @classmethod
    def new_reset_inhibitor_net(cls, label):
        return ResetInhibitorNet(label)

    @classmethod
    def new_inhibitor_net(cls, label):
        return InhibitorNet(label)

    @staticmethod
    def derive_marking(pn):
        init_marking = smc.Marking()
        final_markings = set()

        for p in pn.places:
            # place is part of the initial marking if it does not have ingoing arcs
            pass


    @classmethod
    def new_accepting_petrinet(cls, label, init_marking=None, final_markings=set()):
        pn = PetrinetFactory.new_petrinet(label)
        if init_marking is None or len(final_markings) == 0:
            init, final = PetrinetFactory.derive_marking(pn)
        apn = AcceptingPetrinet(pn, init_marking, final_markings)

    @classmethod
    def clone_petrinet(cls, net):
        cloned = PetrinetFactory.new_petrinet(net.label)
        mapping = cloned.clone_from(net)
        return cloned, mapping

    @classmethod
    def clone_reset_net(cls, net):
        cloned = PetrinetFactory.new_reset_net(net.label)
        mapping = cloned.clone_from(net)
        return cloned, mapping

    @classmethod
    def clone_inhibitor_net(cls, net):
        cloned = PetrinetFactory.new_inhibitor_net(net.label)
        mapping = cloned.clone_from(net)
        return cloned, mapping

    @classmethod
    def clone_reset_inhibitor_net(cls, net):
        cloned = PetrinetFactory.new_reset_inhibitor_net(net.label)
        mapping = cloned.clone_from(net)
        return cloned, mapping


