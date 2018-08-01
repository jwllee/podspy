#!/usr/bin/env python

"""This is the petri net factory module.

This module contains Petri net factory to make petri nets.
"""

from podspy.petrinet.net import *


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


