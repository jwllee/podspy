#!/usr/bin/env python

"""This is the alpha discovery algorithm module.

"""


__name__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = [
    'FootprintMatrix'
]


import pandas as pd
import numpy as np
import logging
import itertools as itls

from podspy.structure import CausalMatrix
from podspy.petrinet.nets import *
from podspy.petrinet.factory import *
from podspy.petrinet.semantics import *


logger = logging.getLogger(__file__)


class FootprintMatrix:
    # there are 4 types of relations
    NEVER_FOLLOW = 0
    DIRECT_RIGHT = 1
    DIRECT_LEFT = 2
    PARALLEL = 3

    def __init__(self, activity_list=list(), matrix=pd.DataFrame()):
        self.matrix = matrix
        self.activity_list = activity_list

    def __repr__(self):
        return '{} ({}, {})'.format(self.__class__.__name__,
                                self.activity_list, self.matrix.shape)

    def __str__(self):
        return '{}'.format(self.matrix)

    @staticmethod
    def build_from_causal_matrix(cmat):
        assert isinstance(cmat, CausalMatrix)

        nb_acts = len(cmat.activity_list)
        mat = np.zeros(shape=(nb_acts, nb_acts))
        mat = pd.DataFrame(mat)

        # case 1: (a, b) = 0 and (b, a) = 0, then #
        # case 2: (a, b) = 0 and (b, a) > 0, then <-
        # case 3: (a, b) > 0 and (b, a) = 0, then ->
        # case 4: (a, b) > 0 and (b, a) > 0, then ||
        for i in range(nb_acts):
            for j in range(i + 1, nb_acts):
                logger.debug('Checking cell {}, {}'.format(i, j))
                if cmat.matrix.iloc[i, j] == 0:
                    # case 1
                    if cmat.matrix.iloc[j, i] == 0:
                        continue # it is NEVER_FOLLOW by default

                    # case 2
                    elif cmat.matrix.iloc[j, i] > 0:
                        mat.iloc[i, j] = FootprintMatrix.DIRECT_LEFT
                        mat.iloc[j, i] = FootprintMatrix.DIRECT_RIGHT

                elif cmat.matrix.iloc[i, j] > 0:
                    # case 3
                    if cmat.matrix.iloc[j, i] == 0:
                        mat.iloc[i, j] = FootprintMatrix.DIRECT_RIGHT
                        mat.iloc[j, i] = FootprintMatrix.DIRECT_LEFT

                    # case 4
                    elif cmat.matrix.iloc[j, i] > 0:
                        mat.iloc[i, j] = FootprintMatrix.PARALLEL
                        mat.iloc[j, i] = FootprintMatrix.PARALLEL

        return FootprintMatrix(cmat.activity_list, mat)


class CausalPair:
    def __init__(self, A=list(), B=list()):
        self.A = A
        self.B = B

    def add_to_A(self, x):
        self.A += [x]
        self.A = sorted(self.A)

    def add_to_B(self, x):
        self.B += [x]
        self.B = sorted(self.B)

    def is_superset(self, cp):
        assert isinstance(cp, CausalPair), '{} not a causal pair'.format(cp)
        superset = True
        for item in cp.A:
            if item not in self.A:
                # cannot be a superset of cp
                superset = False
                return superset

        for item in cp.B:
            if item not in self.B:
                superset = False
                return superset

        return superset

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.A, self.B)

    def __str__(self):
        return '{} -> {}'.format(self.A, self.B)


def powerset(iterable):
    """Compute the powerset of a collection.
    Taken from https://docs.python.org/2/library/itertools.html#recipes.

    :param iterable: collection of items
    :return: collection of all possible subnets
    """
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itls.chain.from_iterable(itls.combinations(s, r) for r in range(len(s)+1))


def add_to_causal_pair_list(pair, _list):
    i = 0

    while i < len(_list):
        p0 = _list[i]

        if p0.is_superset(pair):
            # no need to further check since pair is contained within one of the causal pairs
            break

        elif pair.is_superset(p0):
            # swap them
            _list[i] = p0
            # no need to further check since we assume p0 is different to the remaining
            break

        i += 1

    if i == len(_list):
        # got to the end without breaking, it is a new causal pair
        _list.append(pair)


def discover(causal_mat):
    footprint = FootprintMatrix.build_from_causal_matrix(causal_mat)
    causal_pairs = list()

    logger.debug('Causal matrix: \n{}'.format(causal_mat))
    logger.debug('Footprint: \n{}'.format(footprint))

    target_df = footprint.matrix == FootprintMatrix.DIRECT_RIGHT
    never_df = (footprint.matrix == FootprintMatrix.NEVER_FOLLOW)

    assert isinstance(never_df, pd.DataFrame)
    assert isinstance(target_df, pd.DataFrame)

    for i in range(len(footprint.activity_list)):
        direct_into = footprint.matrix[i] == FootprintMatrix.DIRECT_RIGHT
        source_activities = footprint.matrix.loc[direct_into, i].index.values

        if len(source_activities) == 0:
            continue

        logger.debug('Source activity candidates: {}'.format(source_activities))
        A_list = powerset(source_activities)

        for A in A_list:
            if len(A) == 0:
                continue

            logger.debug('Checking candidate A into "{}": {}'.format(i, A))

            # check that A is valid, i.e., all a_i # a_j
            valid_df_i = never_df.loc[A, A]
            valid_df_i = valid_df_i.all(axis=0)

            if not valid_df_i.all():
                continue

            # since A is valid, expand B beyond to include more than just activity i
            candidates = never_df.loc[never_df[i], i].index.values

            logger.debug('Candidate target activities with "{}": {}'.format(i, candidates))

            target_df_i = target_df.loc[A, candidates]

            # get the common target activities including activity i
            # this means that it needs -> in all A rows
            select_B = target_df_i.all(axis=0)
            # logger.debug('Select B: {}'.format(select_B))
            B = itls.compress(select_B.index.values, select_B)
            B = list(B)

            logger.debug('Target activities: {}'.format(B))

            if len(A) > 0 and len(B) > 0:
                candidate_cpair = CausalPair(list(A), B)
                logger.debug('Adding causal pair: {}'.format(candidate_cpair))
                causal_pairs.append(candidate_cpair)

    # remove redundant causal pairs
    maximal_cpairs = list()
    while len(causal_pairs) > 0:
        candidate_cpair = causal_pairs.pop(0)
        is_maximal = True

        to_remove = list()
        for i in range(len(causal_pairs)):
            cp = causal_pairs[i]
            if candidate_cpair.is_superset(cp):
                to_remove.append(i)
            elif cp.is_superset(candidate_cpair):
                is_maximal = False
                break

        for i in to_remove:
            causal_pairs.pop(i)

        if is_maximal:
            maximal_cpairs.append(candidate_cpair)

        if len(causal_pairs) == 1:
            # this has to be maximal
            maximal_cpairs.append(causal_pairs.pop(0))

    logger.debug('Activities: {}'.format(footprint.activity_list))
    logger.debug('Maximal causal pairs: {}'.format(maximal_cpairs))

    # build petri net model
    label = 'Net by Alpha Miner'
    pn = PetrinetFactory.new_petrinet(label)

    # source and sink transitions
    zero_mat = causal_mat.matrix == 0
    select_src_trans = zero_mat.all(axis=0)
    select_sink_trans = zero_mat.all(axis=1)
    src_act_list = list(itls.compress(footprint.activity_list, select_src_trans))
    sink_act_list = list(itls.compress(footprint.activity_list, select_sink_trans))

    logger.debug('Source transitions: {}'.format(src_act_list))
    logger.debug('Sink transitions: {}'.format(sink_act_list))

    # add transitions
    trans_refs = dict()

    for activity in footprint.activity_list:
        trans = pn.add_transition(activity)
        trans_refs[activity] = trans

    # add source and sink
    place_refs = []
    place_refs.append(pn.add_place('i'))
    place_refs.append(pn.add_place('o'))

    # add arcs between source and sink places and transitions
    for src_act in src_act_list:
        src_trans = trans_refs[src_act]
        pn.add_arc(place_refs[0], src_trans)

    for sink_act in sink_act_list:
        sink_trans = trans_refs[sink_act]
        pn.add_arc(sink_trans, place_refs[1])

    for i in range(len(maximal_cpairs)):
        cpair = maximal_cpairs[i]
        place = pn.add_place('p{}'.format(i))
        place_refs.append(place)

        # add corresponding arcs
        for a in cpair.A:
            activity = footprint.activity_list[a]
            trans = trans_refs[activity]
            pn.add_arc(trans, place)

        for b in cpair.B:
            activity = footprint.activity_list[b]
            trans = trans_refs[activity]
            pn.add_arc(place, trans)

    init_marking = Marking([place_refs[0]])
    final_marking = Marking([place_refs[1]])
    apn = PetrinetFactory.new_accepting_petrinet(pn, init_marking, final_marking)

    return apn
