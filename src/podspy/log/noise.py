#!/usr/bin/env python

"""This is the generate noise module.

This module generates different types of noise by log manipulation.
"""


import pandas as pd
import numpy as np
import logging

from .constant import *


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


logger = logging.getLogger('log')


def add_swap_noise(event_df, pairs, occur=1.):
    """Add swap noise to event dataframe.

    The occurrence of each possible swap is controlled by the occurrence
    probability threshold.

    Parameters
    ----------
    event_df: DataFrame
        Event DataFrame
    pairs: array-like
        Pairs of activities to swap
    occur: float
        Occurrence probability of swap noise

    Returns
    -------
    DataFrame
        Event DataFrame with swap noise added

    """
    noisy = event_df
    for pair in pairs:
        noisy = __add_swap_noise(noisy, pair, occur=occur)
    return noisy


def __add_swap_noise(event_df, pair, occur=1.):
    if len(pair) != 2:
        raise ValueError('Activity pair contains {} elements!'.format(len(pair)))

    noisy = event_df.copy(deep=True)

    activity_0 = pair[0]
    activity_1 = pair[1]

    indexes_0 = noisy[noisy[ACTIVITY] == activity_0].index.values
    indexes_1 = noisy[noisy[ACTIVITY] == activity_1].index.values

    if len(indexes_0) != len(indexes_1):
        msg = 'There are {} events with activity {} and {} events with activity {}!'.format(len(indexes_0), activity_0,
                                                                                            len(indexes_1), activity_1)
        raise ValueError(msg)

    # generate probabilities of swap noise occurrence
    probability = np.random.random(len(indexes_0))

    df = pd.DataFrame({activity_0: indexes_0, activity_1: indexes_1, 'probability': probability})
    # drop the rows where probability does not meet threshold
    df = df[(df['probability'] <= occur)]
    
    logger.debug(df)

    # make the swap noises
    noisy.iloc[df[activity_0].values, (noisy.columns == ACTIVITY)] = activity_1
    noisy.iloc[df[activity_1].values, (noisy.columns == ACTIVITY)] = activity_0

    # may need to change columns with concept:name as well
    if 'concept:name' in noisy.columns:
        noisy.iloc[df[activity_0].values, (noisy.columns == 'concept:name')] = activity_1
        noisy.iloc[df[activity_1].values, (noisy.columns == 'concept:name')] = activity_0

    return noisy
