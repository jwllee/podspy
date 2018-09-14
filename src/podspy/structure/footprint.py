#!/usr/bin/env python

"""This is the footprint matrix module.

"""
import numpy as np
import pandas as pd
import logging

from podspy.structure.causal import CausalMatrix


__all__ = [
   'FootprintMatrix'
]


logger = logging.getLogger(__file__)


class FootprintMatrix:
    # there are 4 types of relations
    NEVER_FOLLOW = 0
    CAUSAL_RIGHT = 1
    CAUSAL_LEFT = 2
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
        mat = pd.DataFrame(mat, dtype=np.int)

        # case 1: (a, b) = 0 and (b, a) = 0, then #
        # case 2: (a, b) = 0 and (b, a) > 0, then <-
        # case 3: (a, b) > 0 and (b, a) = 0, then ->
        # case 4: (a, b) > 0 and (b, a) > 0, then ||
        for i in range(nb_acts):
            for j in range(i, nb_acts):
                logger.debug('Checking cell {}, {}'.format(i, j))
                if cmat.matrix.iloc[i, j] == 0:
                    # case 1
                    if cmat.matrix.iloc[j, i] == 0:
                        continue # it is NEVER_FOLLOW by default

                    # case 2
                    elif cmat.matrix.iloc[j, i] > 0:
                        mat.iloc[i, j] = FootprintMatrix.CAUSAL_LEFT
                        mat.iloc[j, i] = FootprintMatrix.CAUSAL_RIGHT

                elif cmat.matrix.iloc[i, j] > 0:
                    # case 3
                    if cmat.matrix.iloc[j, i] == 0:
                        mat.iloc[i, j] = FootprintMatrix.CAUSAL_RIGHT
                        mat.iloc[j, i] = FootprintMatrix.CAUSAL_LEFT

                    # case 4
                    elif cmat.matrix.iloc[j, i] > 0:
                        mat.iloc[i, j] = FootprintMatrix.PARALLEL
                        mat.iloc[j, i] = FootprintMatrix.PARALLEL

        return FootprintMatrix(cmat.activity_list, mat)