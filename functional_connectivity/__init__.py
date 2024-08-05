#!/usr/bin/env python3
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
import importlib as _importlib
import os

from functional_connectivity.generators import *
from functional_connectivity.readwrite import *
from functional_connectivity.inference import *
from functional_connectivity.stats import *
from functional_connectivity.utils import *

__package__ = "functional_connectivity"
__title__ = "functional_connectivity: sensing the functional connectivity of the brain"
__description__ = ""
__copyright__ = "Copyright (C) 2023-2024 Tzu-Chi Yen"
__license__ = "LGPL version 3 or above"
__author__ = """\n""".join(
    [
        "Tzu-Chi Yen <tzuchi.yen@colorado.edu>",
    ]
)
__release__ = "0.1.0"
__URL__ = "https://github.com/junipertcy/functional-connectivity"
submodules = ["generators", "readwrite", "inference", "stats", "utils"]

dunder = [
    "__version__",
    "__package__",
    "__title__",
    "__description__",
    "__author__",
    "__URL__",
    "__license__",
    "__release__",
]
__all__ = (
    submodules
    + [
        "show_config",
    ]
    + dunder
)


def __dir__():
    return __all__


def __getattr__(name):
    if name in submodules:
        return _importlib.import_module(f"functional_connectivity.{name}")
    else:
        try:
            return globals()[name]
        except KeyError as err:
            raise AttributeError(
                f"Module 'functional_connectivity' has no attribute '{name}'"
            ) from err


def show_config():
    """Show ``functional_connectivity`` build configuration."""
    print("uname:", " ".join(os.uname()))
