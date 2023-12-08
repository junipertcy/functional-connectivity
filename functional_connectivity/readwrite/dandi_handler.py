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

from dandi.dandiapi import DandiAPIClient
from pynwb import NWBHDF5IO
import xarray as xr
import pandas as pd
import numpy as np
# import numba as nb
from numba import njit, prange
from ..utils.utils import sizeof_fmt

import warnings

warnings.simplefilter("ignore")


class DandiHandler:
    def __init__(self, dandiset_id, filepath):
        self.dandiset_id = dandiset_id
        self.filepath = filepath
        self.asset = None
        self.s3_url = None
        self.io = None
        self.nwbfile = None

        self.behaviors = None  # behavioral labels
        self.units = None  # the 0-or-1 spikes data
        self.data_array = None  # the spike counts data ("all data")

    def get_s3_url(self):
        dandiset_id = (
            self.dandiset_id
        )  # PPC_Finger: human posterior parietal cortex recordings during attempted finger movements
        filepath = self.filepath  # 1.5GB file
        with DandiAPIClient() as client:
            self.asset = client.get_dandiset(dandiset_id, "draft").get_asset_by_path(
                filepath
            )
            self.s3_url = self.asset.get_content_url(
                follow_redirects=1, strip_query=True
            )
        print(f"This dataset is of size {sizeof_fmt(self.asset.get_metadata().contentSize)}.")
        return self.s3_url

    def download(self):
        if self.s3_url is None:
            self.get_s3_url()
        if self.io is None:
            self.io = NWBHDF5IO(
                self.s3_url, mode="r", load_namespaces=True, driver="ros3"
            )

    def read(self):
        if self.io is None:
            self.download()
        self.nwbfile = self.io.read()
        return self.nwbfile

    def get_behavior_labels(self, tag="behavior"):
        if self.nwbfile is None:
            self.read()
        self.behaviors = (
            self.nwbfile.processing[tag]
            .fields["data_interfaces"]["states"]
            .to_dataframe()
        )
        return self.behaviors

    def get_units(self):
        if self.nwbfile is None:
            self.read()
        self.units = self.nwbfile.units.to_dataframe()
        return self.units

    @staticmethod
    @njit(parallel=True)
    def _get_spike_counts(
        n_time_intervals, _spike_times, bv_t_itvls
    ):
        _container = np.zeros(n_time_intervals, dtype=np.float64)
        for j in prange(n_time_intervals):  # timestamp
            for spike in _spike_times:
                if bv_t_itvls[j][0] <= spike < bv_t_itvls[j][1]:
                    _container[j] += 1
        return _container

    def get_spike_counts(self, time_to_bin=100):
        if self.behaviors is None:
            self.get_behavior_labels()

        if self.units is None:
            self.get_units()
        
        _loc = self.behaviors.loc
        time_intervals = (_loc[:, "stop_time"] - _loc[:, "start_time"]) // time_to_bin
        num_t_itvls = int(sum(time_intervals) + len(time_intervals))
        behavioral_states = np.zeros(num_t_itvls, dtype='S16')
        bv_t_itvls = np.zeros((num_t_itvls, 2), dtype=np.float64)
        _counter = 0
        for i in range(len(time_intervals)):
            start_t, stop_t = _loc[i, "start_time"], _loc[i, "stop_time"]
            for j in range(int(time_intervals.iloc[i]) + 1):
                behavioral_states[_counter] = _loc[i, "label"]
                bv_t_itvls[_counter, 0] = start_t + j * time_to_bin
                if start_t + (j + 1) * time_to_bin > stop_t:
                    bv_t_itvls[_counter, 1] = stop_t
                else:
                    bv_t_itvls[_counter, 1] = start_t + (j + 1) * time_to_bin
                _counter += 1
        n_neurons = len(self.units)
        n_time_intervals = len(bv_t_itvls)

        container = np.zeros((n_neurons, n_time_intervals), dtype=np.float64)
        for i in range(n_neurons):
            container[i, :] = self._get_spike_counts(n_time_intervals, self.units.iloc[:]["spike_times"][i], bv_t_itvls)
        
        neurons = [str(node) for node in range(len(self.units))]
        times = pd.IntervalIndex.from_arrays(
            bv_t_itvls[:, 0], bv_t_itvls[:, 1], closed="left"
        )

        self.data_array = xr.DataArray(
            container,
            coords={
                "neuron": neurons,
                "time": times,
                "label": ("time", behavioral_states),
                "cell_type": ("neuron", self.units.loc[:, "cell_type"].values.tolist()),
                "shank_id": ("neuron", self.units.loc[:, "shank_id"].values.tolist()),
                "region": ("neuron", self.units.loc[:, "region"].values.tolist()),
            },
            dims=["neuron", "time"],
        )

        return self.data_array
