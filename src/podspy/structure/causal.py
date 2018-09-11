#!/usr/bin/env python

"""This is the causal matrix module.

"""


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"
__all__ = [
    'CausalMatrix'
]


import numpy as np
import pandas as pd
import logging
from podspy.log import constants as cnst


logger = logging.getLogger(__file__)


class CausalMatrix:
    def __init__(self, activity_list=list(), matrix=None):
        self.activity_list = activity_list
        self.matrix = matrix

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.activity_list,
                                   self.matrix.shape)

    def __str__(self):
        return '{}'.format(self.matrix)

    @staticmethod
    def build_from_logtable(logtable, sort=True):
        """Factory method to build a causal matrix from a log table.

        :param logtable: log table
        :param sorted: whether to sort the activities
        :return: built causal matrix
        """
        activity_list = logtable.event_df[cnst.ACTIVITY].unique()

        if sort:
            activity_list = sorted(activity_list)

        def get_causal_mat(df):
            events = df[cnst.ACTIVITY].values
            shifted = [np.nan] + list(events)
            shifted_df = pd.DataFrame({'shifted': shifted})
            # need to reset the index of df so that concatenation align
            df = pd.concat([df.reset_index(drop=True), shifted_df], axis=1)
            df = df[[cnst.CASEID, 'shifted', cnst.ACTIVITY]]
            return df

        grouped = logtable.event_df.groupby(cnst.CASEID, as_index=False)
        grouped = grouped.apply(get_causal_mat)
        # exclude any NaN rows
        grouped = grouped.dropna(axis=0, subset=[cnst.ACTIVITY, 'shifted'])

        grouped = grouped.groupby([cnst.ACTIVITY, 'shifted'], as_index=False)
        counts = grouped.agg('count')
        counts.columns = [cnst.ACTIVITY, 'shifted', 'count']

        zeros = np.zeros((len(activity_list), len(activity_list)))
        mat = pd.DataFrame(zeros, index=activity_list, columns=activity_list)

        for activity in counts['shifted'].unique():
            cols = counts.loc[counts['shifted'] == activity, cnst.ACTIVITY].values
            vals = counts.loc[counts['shifted'] == activity, 'count'].values
            logger.debug('Setting columns {} related to "{}" row with values {}'.format(cols, activity, vals))
            mat.loc[activity, cols] = vals

        logger.debug('\n{}'.format(counts))
        logger.debug('\n{}'.format(mat))

        return CausalMatrix(activity_list, mat)
