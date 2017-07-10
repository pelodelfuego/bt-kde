#!/usr/bin/python2
# -*- coding: utf-8 -*-


import __init__

import itertools as it
from operator import itemgetter

import numpy as np
import pandas as pd

from sklearn.neighbors import BallTree
from scipy import stats
from statsmodels.nonparametric.kernel_density import KDEMultivariate

import pyximport; pyximport.install()
from ellipse_dist import ellipse_dist


def _iter_tree_ix(balltree):
    """
    Find 'fuzzy' groups of indexes in a balltree.
        The fuzzyness is defined in the metric used to build the tree.
        Each index if used exactly once.
    """

    node_arr = np.array([dict(node.items() + [('center', bound)]) \
                         for node, bound in it.izip(balltree.node_data, balltree.node_bounds[0])])

    def fetch_ball_ix(i, acc):
        """
        Fetch the indexes in a balltree node and its childrens.
            Assume the metric to be designed for this and < 1. if the childrens node are to include.
        """
        # No more childrens
        if i > len(node_arr):
            return []

        # The node is a group of indexes
        if node_arr[i]['radius'] < 1. or node_arr[i]['is_leaf'] == 1:
            bt_arr_l = balltree.get_arrays()[1]
            ix_l = bt_arr_l[slice(node_arr[i]['idx_start'], node_arr[i]['idx_end'])]

            if node_arr[i]['is_leaf'] == 0:
                return acc + [ix_l.tolist()]
            else:
                return acc + [[ix] for ix in ix_l] # several indexes can be stored into a node (leaf_size)
        else:
            # recc call
            return fetch_ball_ix(2*i+1, acc) + fetch_ball_ix(2*i+2, acc)

    # Init
    return fetch_ball_ix(0, [])


def bt_kde(dist, bw_list, fit_tol=4.):
    """
    Aggregate the distribution according to a tolerance for 'merging points'.
        The tolerance define the metric for the balltree.
        It is the scale factor for the ellipse built based on the bandwidth.
    Also return the pdf function.
    """

    # Store distribution in the balltree
    #   Note: the the metric is defined by the tolerance and the std of the gaussian kernel on each dim
    dist_bt = BallTree(dist, metric=ellipse_dist(bw_list, fit_tol), leaf_size=1)
    dist_arr = np.array(dist_bt.data)

    # Aggregate the point according to the metric
    agg_dist = [(len(ix_l), np.mean(dist_arr[ix_l], axis=0)) for ix_l in _iter_tree_ix(dist_bt)]
    agg_dist = sorted(agg_dist, key=itemgetter(0))

    # Fit several models on the aggregated distribution
    model_l = []
    for weight, values in it.groupby(agg_dist, key=itemgetter(0)):
        node_val = np.array([x[1] for x in values])

        # Check if less points in the cluster than the number of dim due to KDEMultivariate limitation.
        #   In such case, we need to compute every gaussian kernel separatly.
        if len(node_val) <= len(bw_list):
            for nv in node_val:
                model = stats.multivariate_normal(nv, np.diag(bw_list), 1./len(node_val))
                model_l.append((weight, 1., model))
        else:
            # Use a classical KDE and store ponderation of it for later.
            model = KDEMultivariate(node_val, ''.join(['c']*len(bw_list)), bw_list)
            model_l.append((weight, len(node_val), model))


    def pdf(X, pred_tol=4.):
        """
        Predict the proba according to the fited models and a tolerance.
        """

        # Store predict distribution in a balltree
        X_bt = BallTree(X, metric=ellipse_dist(bw_list, pred_tol), leaf_size=1)
        X_arr = np.array(X_bt.data)

        # Aggregate the distribution and store associaton
        agg_dict = {}
        for x_l, agg_x in [(X_arr[ix_l], np.mean(X_arr[ix_l], axis=0)) for ix_l in _iter_tree_ix(X_bt)]:
            agg_dict.update(dict([(tuple(x), tuple(agg_x)) for x in x_l]))

        # Predict on the aggregated distribution (ponderated by cluster size)
        agg_x = map(tuple, set(agg_dict.values()))
        agg_p = [model.pdf(agg_x) * weight * n_obs for (weight, n_obs, model) in model_l]
        agg_p = np.sum(agg_p, axis=0)

        p_dict = dict(zip(agg_x, agg_p))

        # Use previous mapping to return the value
        return np.array([p_dict[agg_dict[tuple(x)]] for x in X])

    return pdf
