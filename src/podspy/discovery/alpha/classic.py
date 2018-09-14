#!/usr/bin/env python3

"""This is an implementation of the classic alpha mining algorithm [1]_.


.. [1] Van der Aalst, Wil, Ton Weijters, and Laura Maruster. "Workflow mining: Discovering
  process models from event logs." IEEE Transactions on Knowledge & Data Engineering 9 (2004): 1128-1142.

"""


import pandas as pd
import logging
import itertools as itls

from podspy.petrinet.factory import *
from podspy.petrinet.semantics import *
from podspy.structure import FootprintMatrix


logger = logging.getLogger(__file__)


def powerset(iterable):
    """Compute the powerset of a collection.
    Taken from https://docs.python.org/2/library/itertools.html#recipes.

    :param iterable: collection of items
    :return: collection of all possible subnets
    """
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itls.chain.from_iterable(itls.combinations(s, r) for r in range(len(s)+1))


def apply(causal_mat):
    """Applies the alpha mining algorithm to a causal matrix.

    :param causal_mat: causal matrix describing the causal relations between activities
    :return: the discovered accepting petri net
    """

    footprint = FootprintMatrix.build_from_causal_matrix(causal_mat)
    causal_pairs = list()

    logger.debug('Causal matrix: \n{}'.format(causal_mat))
    logger.debug('Footprint: \n{}'.format(footprint))

    target_df = footprint.matrix == FootprintMatrix.CAUSAL_RIGHT
    never_df = footprint.matrix == FootprintMatrix.NEVER_FOLLOW

    assert isinstance(never_df, pd.DataFrame)
    assert isinstance(target_df, pd.DataFrame)

    for i in range(len(footprint.activity_list)):
        # get all the activities that "causes" activity i
        direct_into_i = target_df.iloc[:, i]
        source_activities = footprint.matrix.loc[direct_into_i, i].index.values

        if len(source_activities) == 0:
            continue

        logger.debug('Source activity candidates: {}'.format(source_activities))

        # potentially need to check every combination of source activity sets
        # Comment:
        # ---
        # This part can be improved by looking at the larger subsets A first, and
        # then when looking at the smaller subnets A', if the target B' is subset of
        # target B, you won't have to add to causal_pairs. This means that less
        # filtering for the maximal causal pairs can be done. There's still filtering
        # because you can have the same (A, B) pairs from different activity loops.
        # ---
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

            A = set(A)
            B = set(B)

            logger.debug('Target activities: {}'.format(B))

            # the candidate causal set pairs have to fulfill two requirements
            non_empty = len(A) > 0 and len(B) > 0
            equal = A.issubset(B) and B.issubset(A)

            if non_empty and not equal:
                candidate_cpair = (A, B)
                logger.debug('Adding causal pair: {}'.format(candidate_cpair))
                causal_pairs.append(candidate_cpair)

    # remove redundant causal pairs
    maximal_cpairs = list()

    def contain_pair(p0, p1):
        """Check if a causal pair is contained within another.

        :param p0: parent pair
        :param p1: child pair
        :return: whether if p0 contains p1
        """
        return p1[0].issubset(p0[0]) and p1[1].issubset(p0[1])

    while len(causal_pairs) > 0:
        candidate = causal_pairs.pop(0)
        is_maximal = True

        to_remove = list()
        for i in range(len(causal_pairs)):
            cp = causal_pairs[i]
            if contain_pair(candidate, cp):
                to_remove.append(i)
            elif contain_pair(cp, candidate):
                is_maximal = False
                break

        for i in to_remove:
            causal_pairs.pop(i)

        if is_maximal:
            maximal_cpairs.append(candidate)

        if len(causal_pairs) == 1:
            # this has to be maximal
            maximal_cpairs.append(causal_pairs.pop(0))

    logger.debug('Activities: {}'.format(footprint.activity_list))
    logger.debug('Maximal causal pairs: {}'.format(maximal_cpairs))

    # build petri net model
    label = 'Net by Alpha Miner'
    pn = PetrinetFactory.new_petrinet(label)

    # source and sink transitions
    # an activity is a source activity if there is no causal relations into the activity
    # this means the corresponding column's rows are all 0, ~ is negation
    select_src_acts = ~causal_mat.matrix.any(axis=0)
    # an activity is a target activity if there is no causal relations out of the activity
    # this means the corresponding row's columns are all 0
    select_sink_acts = ~causal_mat.matrix.any(axis=1)

    src_act_list = list(itls.compress(footprint.activity_list, select_src_acts))
    sink_act_list = list(itls.compress(footprint.activity_list, select_sink_acts))

    logger.debug('Source transitions: {}'.format(src_act_list))
    logger.debug('Sink transitions: {}'.format(sink_act_list))

    # add transitions
    trans_refs = dict()

    for activity in footprint.activity_list:
        trans = pn.add_transition(activity)
        trans_refs[activity] = trans

    # add source and sink
    src_place = pn.add_place('i')
    sink_place = pn.add_place('o')

    # add arcs between source and sink places and transitions
    for src_act in src_act_list:
        src_trans = trans_refs[src_act]
        pn.add_arc(src_place, src_trans)

    for sink_act in sink_act_list:
        sink_trans = trans_refs[sink_act]
        pn.add_arc(sink_trans, sink_place)

    for i in range(len(maximal_cpairs)):
        A, B = maximal_cpairs[i]
        A_sorted = sorted([footprint.activity_list[i] for i in A])
        B_sorted = sorted([footprint.activity_list[i] for i in B])
        A_str = ', '.join(A_sorted)
        B_str = ', '.join(B_sorted)
        place_label = '({{{}}}, {{{}}})'.format(A_str, B_str)
        place = pn.add_place(place_label)

        # add corresponding arcs
        for a in A:
            activity = footprint.activity_list[a]
            trans = trans_refs[activity]
            pn.add_arc(trans, place)

        for b in B:
            activity = footprint.activity_list[b]
            trans = trans_refs[activity]
            pn.add_arc(place, trans)

    init_marking = Marking([src_place])
    final_markings= {Marking([sink_place])}
    apn = PetrinetFactory.new_accepting_petrinet(pn, init_marking, final_markings)

    return apn
