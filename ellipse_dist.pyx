# -*- coding: utf-8 -*-

import __init__

cimport numpy as np
cimport cython
from cpython cimport array
np.import_array()

ctypedef np.float64_t DTYPE_t
ctypedef np.intp_t ITYPE_t


@cython.boundscheck(False)
@cython.wraparound(False)
def ellipse_dist(bw_list, tol):
    """
    Metric to compute is a point is within an ellipse.
    """

    nb_dim = len(bw_list)

    def _eval(np.ndarray[DTYPE_t] x1, np.ndarray[DTYPE_t] x2):
        """
        Compute wether the points are in the same ellipse.
            The ellipse is defined by the bandwidth list on each dimensions.
            The tol factor control the scale of the ellipse.
        """

        cdef DTYPE_t tmp, acc=0.
        cdef np.intp_t j

        for j in range(nb_dim):
            tmp = (x1[j] - x2[j]) / (bw_list[j] / tol)
            acc += pow(tmp, 2)

        return acc

    return _eval
