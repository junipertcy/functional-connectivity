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

import warnings
warnings.simplefilter('ignore')


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
        return self.s3_url

    def download(self):
        if self.s3_url is None:
            self.get_s3_url()
        if self.io is None:
            self.io = NWBHDF5IO(
                self.s3_url, mode="r", load_namespaces=True, driver="ros3"
            )

    def read(self):
        self.nwbfile = self.io.read()
        return self.nwbfile

    def get_behavior_labels(self, tag="behavior"):
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

    def get_spike_counts(self, time_to_bin=100):
        if self.behaviors is None:
            self.get_behavior_labels()

        if self.units is None:
            self.get_units()

        time_intervals = (
            self.behaviors.loc[:, "stop_time"] - self.behaviors.loc[:, "start_time"]
        ) // time_to_bin
        behavioral_states = []
        behavioral_time_interval_incl = []
        for i in range(len(time_intervals)):
            start_t = self.behaviors.loc[i, "start_time"]
            stop_t = self.behaviors.loc[i, "stop_time"]
            for j in range(int(time_intervals.iloc[i]) + 1):
                behavioral_states += [self.behaviors.loc[i, "label"]]
                if start_t + (j + 1) * time_to_bin > stop_t:
                    behavioral_time_interval_incl += [
                        (start_t + j * time_to_bin, stop_t)
                    ]
                else:
                    behavioral_time_interval_incl += [
                        (start_t + j * time_to_bin, start_t + (j + 1) * time_to_bin)
                    ]

        container = np.zeros(
            (len(self.units), len(behavioral_time_interval_incl)), dtype=np.float64
        )
        n = container.shape[1]
        for i in range(len(self.units)):  # neuron locator
            for j in range(len(behavioral_time_interval_incl)):  # timestamp
                for spike in self.units.iloc[i]["spike_times"]:
                    if (
                        behavioral_time_interval_incl[j][0]
                        <= spike
                        < behavioral_time_interval_incl[j][1]
                    ):  # inclusive
                        container[i, j] += 1

        neurons = [str(node) for node in range(len(self.units))]

        times = pd.IntervalIndex.from_tuples(
            behavioral_time_interval_incl, closed="left"
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
