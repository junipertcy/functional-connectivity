[![PythonVersion](https://img.shields.io/pypi/pyversions/functional-connectivity.svg)](https://pypi.org/project/functional-connectivity/)
[![PyPI](https://img.shields.io/pypi/v/functional-connectivity)](https://pypi.org/project/functional-connectivity/)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![license](https://img.shields.io/badge/license-LGPL-green.svg?style=flat)](https://github.com/junipertcy/functional-connectivity/blob/master/LICENSE)



**functional-connectivity** implements a set of tools to detect and sense changes in a functional network from spike counts

This is the software repository behind the paper:

* Tzu-Chi Yen and Yi-Yun Ho, *Mapping functional neuronal networks to behavioral states*, in preparation (2024).

Read it on: [arXiv](https://arxiv.org/).

* For full documentation, please visit [this site](https://docs.netscied.tw/fc/index.html).
* For general Q&A, ideas, or other things, please visit [Discussions](https://github.com/junipertcy/functional-connectivity/discussions).
* For software-related bugs, issues, or suggestions, please use [Issues](https://github.com/junipertcy/functional-connectivity/issues).


Installation
------------
**functional-connectivity** is available on PyPI:
```
pip install functional-connectivity
```

The dependencies needed to interact with Dandi are not installed by default. You will need to run:
* ```pip install --ignore-installed --no-binary=h5py h5py scipy numba```


Development
-----------
Remember that `./docs` contains [the documentation](https://docs.netscied.tw/fc/index.html) of this library.
You would need AWS credentials to be able to execute `./docs/deploy.sh`.



Acknowledgement
---------------
The functional-connectivity library is supported by [The Kavli Foundation](https://www.kavlifoundation.org/). 
TCY wants to thank Rebecca Morrison ([@rebeccaem](https://github.com/rebeccaem)) and Stephen Becker ([@stephenbeckr](https://github.com/stephenbeckr)) for inspirations. 

We also want to thank the authors in these software implementations:
* [cvxgrp/strat_models](https://github.com/cvxgrp/strat_models)
* [GalSha/GLASSO_Framework](https://github.com/GalSha/GLASSO_Framework): [arXiv (2023)](https://arxiv.org/abs/2205.10027)
* [tpetaja1/tvgl](https://github.com/tpetaja1/tvgl): [KDD (2017)](https://dl.acm.org/doi/10.1145/3097983.3098037), time-varying GGM using ADMM and Python 2.7.

License
-------
**functional-connectivity** is open-source and licensed under the [GNU Lesser General Public License v3.0](https://www.gnu.org/licenses/lgpl-3.0.en.html).
