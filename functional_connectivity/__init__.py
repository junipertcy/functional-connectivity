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
__package__ = 'functional_connectivity'
__title__ = 'functional_connectivity: sensing the functional connectivity of the brain'
__description__ = ''
__copyright__ = 'Copyright (C) 2023-2024 Tzu-Chi Yen'
__license__ = "LGPL version 3 or above"
__author__ = """\n""".join([
    'Tzu-Chi Yen <tzuchi.yen@colorado.edu>',
])
__URL__ = "https://github.com/junipertcy/functional-connectivity"
__version__ = '0.1.1'
__release__ = '0.1'


__all__ = [
    "__author__",
    "__URL__",
    "__version__",
    "__copyright__",
]

from functional_connectivity import utils
from functional_connectivity.utils import *

from functional_connectivity import stats
from functional_connectivity.stats import *

from functional_connectivity import readwrite
from functional_connectivity.readwrite import *

from functional_connectivity import inference
from functional_connectivity.inference import *

from functional_connectivity import generators
from functional_connectivity.generators import *
