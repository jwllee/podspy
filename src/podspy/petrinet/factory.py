#!/usr/bin/env python

"""This is the petri net factory module.

This module contains Petri net factory to make petri nets.
"""

from podspy.petrinet import nets as nt
from podspy.petrinet import semantics as smc


__all__ = [
    'PetrinetFactory'
]


class PetrinetFactory:
    @classmethod
    def new_petrinet(cls, label):
        return nt.Petrinet(label)

    @classmethod
    def new_reset_net(cls, label):
        return nt.ResetNet(label)

    @classmethod
    def new_reset_inhibitor_net(cls, label):
        return nt.ResetInhibitorNet(label)

    @classmethod
    def new_inhibitor_net(cls, label):
        return nt.InhibitorNet(label)

    @staticmethod
    def derive_marking(pn):
        init_marking = smc.Marking()
        final_markings = set()

        for p in pn.places:
            # place is part of the initial marking if it does not have ingoing arcs
            if p not in pn.in_edge_map:
                init_marking.add(p, weight=1)
            # place is part of the final marking if it does not have outgoing arcs
            if p not in pn.out_edge_map:
                final_marking = smc.Marking()
                final_marking.add(p, weight=1)
                final_markings.add(final_marking)

        # create an empty final marking if necessary
        if len(final_markings) == 0:
            final_markings.add(smc.Marking())

        return init_marking, final_markings

    @classmethod
    def new_accepting_petrinet(cls, net, init_marking=None, final_markings=None):
        if init_marking is None or len(final_markings) == 0:
            init, final = PetrinetFactory.derive_marking(net)

            if init_marking is None:
                init_marking = init

            if final_markings is None:
                final_markings = final

        apn = nt.AcceptingPetrinet(net, init_marking, final_markings)

        return apn

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


