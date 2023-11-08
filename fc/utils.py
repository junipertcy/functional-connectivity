#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# functional-connectivity -- Sensing functional connectivity in the brain, in Python
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
import numba as nb


@nb.njit(parallel=True)
def sum_chunk(arr, n_bins=4):
    container = np.zeros((arr.shape[0], arr.shape[1] // n_bins), dtype=np.float64)
    n = container.shape[1]
    for i in nb.prange(n):
        for j in range(n_bins):
            container[:, i] += arr[:, i * n_bins + j]
    return container