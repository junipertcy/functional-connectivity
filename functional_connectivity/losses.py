#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# functional-connectivity -- Sensing functional connectivity in the brain, in Python
#
# In this version, the code was copy-pasted from the original source code, at
# https://github.com/cvxgrp/strat_models/blob/master/strat_models/losses.py
#
#
# Copyright (C) 2023-2024 Tzu-Chi Yen <tzuchi.yen@colorado.edu>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import numpy as np
from sklearn import preprocessing


class Loss:
    """
    Inputs:
            N/A

    All losses have an attribute of isDistribution, which is a Boolean
    that denotes whether or not a Loss is a distribution estimate
    (i.e., isDistribution==True -> accepts Y,Z, and
               isDistribution==False -> accepts X,Y,Z.)

    All losses implement the following functions:

    1. evaluate(theta, data). Evaluates the regularizer at theta with data.
    2. prox(t, nu, data, warm_start, pool): Evaluates the proximal operator of the regularizer at theta
    """

    def __init__(self):
        pass

    def evaluate(self, theta):
        raise NotImplementedError(
            "This method is not implemented for the parent class."
        )

    def setup(self, data, K):
        """This function has any important setup required for the problem."""
        raise NotImplementedError(
            "This method is not implemented for the parent class."
        )

    def prox(self, t, nu, data, warm_start, pool):
        raise NotImplementedError(
            "This method is not implemented for the parent class."
        )

    def anll(self, data, G):
        return -np.mean(self.logprob(data, G))


def turn_into_iterable(x):
    try:
        iter(x)
    except TypeError:
        return [x]
    else:
        return x


def joint_cov_prox(Y, nu, theta, t):
    """
    Proximal operator for joint covariance estimation
    """
    if Y is None:
        return nu

    n, nk = Y[0].shape
    Yemp = Y[0] @ Y[0].T / nk

    s, Q = np.linalg.eigh(nu / (t * nk) - Yemp)
    w = ((t * nk) * s + np.sqrt(((t * nk) * s) ** 2 + 4 * (t * nk))) / 2
    return Q @ np.diag(w) @ Q.T


class covariance_max_likelihood_loss(Loss):
    """
    f(theta) = Trace(theta @ Y) - logdet(theta)
    """

    def __init__(self):
        super().__init__()
        self.isDistribution = True

    def evaluate(self, theta, data):
        assert "Y" in data
        return np.trace(theta @ data["Y"]) - np.linalg.slogdet(theta)[1]

    def setup(self, data, G):
        Y = data["Y"]
        Z = data["Z"]

        K = len(G.nodes())

        shape = (data["n"], data["n"])
        theta_shape = (K,) + shape

        # preprocess data
        for y, z in zip(Y, Z):
            vertex = G._node[z]
            if "Y" in vertex:
                vertex["Y"] += [y]
            else:
                vertex["Y"] = [y]

        Y_data = []
        for i, node in enumerate(G.nodes()):
            vertex = G._node[node]
            if "Y" in vertex:
                Y = vertex["Y"]
                Y_data += [Y]
                del vertex["Y"]
            else:
                Y_data += [None]

        cache = {
            "Y": Y_data,
            "n": data["n"],
            "theta_shape": theta_shape,
            "shape": shape,
            "K": K,
        }
        return cache

    def prox(self, t, nu, warm_start, pool, cache):
        """
        Proximal operator for joint covariance estimation
        """
        res = pool.starmap(
            joint_cov_prox, zip(cache["Y"], nu, warm_start, t * np.ones(cache["K"]))
        )
        return np.array(res)

    def logprob(self, data, G):
        logprobs = []

        for y, z in zip(data["Y"], data["Z"]):
            n, nk = y.shape
            Y = (y @ y.T) / nk

            if (np.zeros((n, n)) == Y).all():
                continue

            theta = G._node[z]["theta_tilde"]
            logprobs += [np.linalg.slogdet(theta)[1] - np.trace(Y @ theta)]

        return logprobs

    def sample(self, data, G):
        Z = turn_into_iterable(data["Z"])
        sigmas = [np.linalg.inv(G._node[z]["theta"]) for z in Z]

        n = sigmas[0].shape[0]
        return [np.random.multivariate_normal(np.zeros(n), sigma) for sigma in sigmas]
