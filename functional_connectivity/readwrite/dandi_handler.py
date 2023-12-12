from dandi.dandiapi import DandiAPIClient
from pynwb import NWBHDF5IO
import requests
import xarray as xr
import pandas as pd
import numpy as np

# import numba as nb
from numba import njit, prange
from ..utils.utils import sizeof_fmt

import warnings

warnings.simplefilter("ignore")

API_DENDIARCHIVE = "https://api.dandiarchive.org/api/dandisets/"


class DandiHandler:
    def __init__(self, dandiset_id: str):
        self.dandiset_id = dandiset_id
        self.version_id = None
        self.filepath = None
        self.asset = None
        self.s3_url = None
        self.io = None
        self.nwbfile = None

        self.behaviors = None  # behavioral labels
        self.units = None  # the 0-or-1 spikes data
        self.data_array = None  # the spike counts data ("all data")

        self.metadata = dict()
        self.metadata["ds_instance"] = requests.get(API_DENDIARCHIVE + dandiset_id + "/?format=json").json()

        self.version2paths = dict()

    def get_all_versions(self):
        return self._collect_values_by_key(self.metadata["ds_instance"], "version")

    def get_all_filepaths_by_version(self, version_id: str = "draft"):
        self.version_id = version_id
        with DandiAPIClient() as client:
            self.asset = client.get_dandiset(self.dandiset_id, version_id).get_assets()
        self.version2paths[version_id] = [asset.path for asset in self.asset]
        return self.version2paths[version_id]

    @staticmethod
    def _collect_values_by_key(data: dict, key: str):
        collection = []

        def __helper(data=data, key=key):
            if isinstance(data, dict):
                for _key, value in data.items():
                    if _key == key:
                        collection.append(value)
                    else:
                        __helper(value)
            elif isinstance(data, list):
                for item in data:
                    __helper(item)

        __helper(data, key)
        return collection

    def get_s3_url(self, version_id: str = None, filepath: str = None):
        if version_id is None:
            raise ValueError("Please specify the version_id (use version_id='...').")
        if filepath is None:
            raise ValueError("Please specify the filepath (use filepath='...').")
        self.filepath = filepath
        with DandiAPIClient() as client:
            self.asset = client.get_dandiset(self.dandiset_id, version_id).get_asset_by_path(filepath)
            self.s3_url = self.asset.get_content_url(follow_redirects=1, strip_query=True)
        print(f"This dataset is of size {sizeof_fmt(self.asset.get_metadata().contentSize)}.")
        return self.s3_url

    def download(self):
        if self.s3_url is None:
            raise FileNotFoundError("Please specify the s3_url (use the function get_s3_url(...)).")

        if self.io is None:
            self.io = NWBHDF5IO(self.s3_url, mode="r", load_namespaces=True, driver="ros3")

    def read(self):
        if self.io is None:
            self.download()
        self.nwbfile = self.io.read()
        return self.nwbfile

    def get_behavior_labels(self, tag: str = "behavior"):
        if self.nwbfile is None:
            self.read()
        self.behaviors = self.nwbfile.processing[tag].fields["data_interfaces"]["states"].to_dataframe()
        return self.behaviors

    def get_units(self):
        if self.nwbfile is None:
            self.read()
        self.units = self.nwbfile.units.to_dataframe()
        return self.units

    @staticmethod
    @njit(parallel=True)
    def _get_spike_counts(n_time_intervals, _spike_times, bv_t_itvls):
        _container = np.zeros(n_time_intervals, dtype=np.float64)
        for j in prange(n_time_intervals):  # timestamp
            for spike in _spike_times:
                if bv_t_itvls[j][0] <= spike < bv_t_itvls[j][1]:
                    _container[j] += 1
        return _container

    def get_spike_counts(self, time_to_bin: int = 100):
        if self.behaviors is None:
            self.get_behavior_labels()

        if self.units is None:
            self.get_units()

        _loc = self.behaviors.loc
        time_intervals = (_loc[:, "stop_time"] - _loc[:, "start_time"]) // time_to_bin
        num_t_itvls = int(sum(time_intervals) + len(time_intervals))
        behavioral_states = np.zeros(num_t_itvls, dtype="S16")
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
        times = pd.IntervalIndex.from_arrays(bv_t_itvls[:, 0], bv_t_itvls[:, 1], closed="left")

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
