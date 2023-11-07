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
""" functional-connectivity allows you to sense functional connectivity in the brain, in Python.

All functional-connectivity sdists and wheels distributed on PyPI are licensed under LGPL-3.0-or-later.

"""

from os.path import realpath, dirname, join
from setuptools import setup, find_packages
from fc import __version__

DOCLINES = (__doc__ or '').split("\n")

PROJECT_ROOT = dirname(realpath(__file__))

# REQUIREMENTS_FILE = join(PROJECT_ROOT, 'requirements.txt')

# with open(REQUIREMENTS_FILE) as f:
#     install_reqs = f.read().splitlines()

# install_reqs.append('setuptools')

setup(
    name='functional-connectivity',
    version=__version__,
    description=DOCLINES[0],
    long_description="\n".join(DOCLINES[2:]),
    author='Tzu-Chi Yen',
    author_email='tzuchi.yen@colorado.edu',
    license='LGPLv3',
    package_dir={"": "."},
    packages=find_packages(where="."),
    package_data={
        'functional-connectivity': [
            'LICENSE',
            'README.md',
        ]},
    include_package_data=False,
    # install_requires=install_reqs,
    extras_require={
        'test': ['pytest'],
        'docs': ['sphinx']
    },
    url='https://github.com/junipertcy/functional-connectivity',
    platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
    test_suite='pytest',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
    ],
    keywords=[
        'functional-connectivity',
        'keywords-TBD',
    ],
    project_urls={
        'Source Code': 'https://github.com/junipertcy/functional-connectivity',
    },
)