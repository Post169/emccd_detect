# EMCCD Detect

Given an input fluxmap, emccd_detect will return a simulated EMCCD detector image.


# Version

The latest version of emccd\_detect is 2.2.5.



## Getting Started
### Installing

This package requires Python 3.6 or higher.  emccd\_detect currently uses arCTIc, a package for implementing charge transfer inefficiency (CTI).  The following libraries must be installed in advance if you do not already have them:  `llvm`, `omp`, and `gsl`.  If your C++ is up to date, this should not be an issue.  During the installation process outlined below, pay attention to the output message in the case of a failed installation.  It may say you need to update your C++, and it will probably tell you that and how to do so.

llvm:  https://github.com/llvm/llvm-project/releases/tag/llvmorg-14.0.6

To install emccd\_detect, navigate to the emccd\_detect directory where setup.py is located and use

	pip install .

This will install emccd\_detect and its dependencies, which are as follows:

* arcticpy==2.0
* astropy
* matplotlib
* numpy
* scipy
* pynufft==2020.0.0
* pyyaml


### Usage

For an example of how to use emccd\_detect, see example_script.py.


## Authors

* Bijan Nemati (<bijan.nemati@tellus1.com>)
* Sam Miller (<sam.miller@uah.edu>)
* Kevin Ludwick (<kevin.ludwick@uah.edu>)

