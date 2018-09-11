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
from podspy.structure import CausalMatrix


logger = logging.getLogger(__file__)


class FootprintMatrix:
    # there are 4 types of relations
    # 1) not following
    # 2) right arrow
    # 3) left arrow
    # 4) parallel
    NEVER_FOLLOW = 0
    DIRECT_RIGHT = 1
    DIRECT_LEFT = 2
    PARALLEL = 3

    def __init__(self, matrix=pd.DataFrame()):
        self.matrix = matrix

    def __repr__(self):
        return '{} ({})'.format(self.__class__.__name__,
                                self.matrix)

    @staticmethod
    def build_from_causal_matrix(cmat):
        assert isinstance(cmat, CausalMatrix)

        nb_acts = len(cmat.activity_list)
        mat = np.zeros(shape=(nb_acts, nb_acts))
        mat = pd.DataFrame(mat, index=cmat.activity_list, columns=cmat.activity_list)

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

        return FootprintMatrix(mat)


def discover(causal_mat):
    pass
