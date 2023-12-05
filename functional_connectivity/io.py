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


class DandiHandler():
    def __init__(self, dandiset_id, filepath):
        self.dandiset_id = dandiset_id
        self.filepath = filepath
        self.asset = None
        self.s3_url = None
        self.io = None
        self.nwbfile = None

    def get_s3_url(self):
        dandiset_id = self.dandiset_id  # PPC_Finger: human posterior parietal cortex recordings during attempted finger movements
        filepath = self.filepath  # 1.5GB file
        with DandiAPIClient() as client:
            self.asset = client.get_dandiset(dandiset_id, "draft").get_asset_by_path(filepath)
            self.s3_url = self.asset.get_content_url(follow_redirects=1, strip_query=True)
        return self.s3_url        

    def download(self):
        if self.s3_url is None:
            self.get_s3_url()
        if self.io is None:
            self.io = NWBHDF5IO(self.s3_url, mode="r", load_namespaces=True, driver='ros3')
        

    def read(self):
        self.nwbfile = self.io.read()
        return self.nwbfile
