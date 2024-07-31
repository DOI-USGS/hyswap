# hyswap - HYdrologic Surface Water Analysis Package

[![USGS-category-image](https://img.shields.io/badge/USGS-Core-green.svg)](https://owi.usgs.gov/R/packages.html#core)
[![pipeline-status-image](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/badges/main/pipeline.svg)](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/commits/main)
[![coverage-report-image](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/badges/main/coverage.svg)](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/commits/main)
[![PyPI version](https://badge.fury.io/py/hyswap.svg)](https://badge.fury.io/py/hyswap)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hyswap)](https://img.shields.io/pypi/pyversions/hyswap)

## Overview

`hyswap` (HYdrologic Surface Water Analysis Package), is a Python package which provides a set of functions for manipulating and visualizing USGS water data.
Specifically, a number of functions for calculating statistics (e.g., exceedance probabilities, daily historic percentiles) and generating related plots (e.g., flow duration curves, streamflow duration hydrographs) are available.
These methods are provided in a modular fashion as individual functions, and are designed to give the user flexibility in implementation.

### Project Documentation

For more information, visit the `hyswap` [documentation](https://doi-usgs.github.io/hyswap/).

## Installation

### User Installation via `pip`

One-liner to install `hyswap` via `pip`:

```bash
pip install hyswap
```

*Note:* `hyswap` has 4 dependencies right now, `numpy`, `pandas`, `scipy`, and `matplotlib`, these will be installed automatically when installing the package via `pip`.

### User Installation From Source

To install `hyswap` from source, first you will need to clone the repository.
Next, from the root of the repository, run the following commands in your non-base environment:

```bash
pip install -r requirements.txt
pip install .
```

### Developer Installation

Developer installation should be performed from source.
First you will need to clone the repository.
Next, from the root of the repository, you have two options:

**Option 1: Initiate your own python environment and then `pip install` the required packages**

In a non-base environment, use the `pip` command to install both the `requirements.txt` and the `requirements-dev.txt`. Then run `pip install .` to obtain the source version of `hyswap`.

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install .
```
**Option 2: Use the `environment-dev.yml` to initiate a conda/mamba environment and download required packages from `conda-forge` and `pypi`**

If you are a `conda` or `mamba` user, the shell code below will create a development environment called `hyswap-dev-environment`, activate it, and then install `hyswap` into the environment from source. Replace `conda` with `mamba` where appropriate for `mamba` users.

```bash
conda env create -f environment-dev.yml
conda activate hyswap-dev-environment
pip install .
```

### Testing and Building Documentation Locally

To test the code and building and test the documentation locally, you must have cloned the source repository, follow the instructions above for a "developer installation" first.

To test the package locally, run the following command from the root of the repository:

```bash
pytest
```

To build the documentation locally, run the following commands from the root of the repository:

```bash
cd docs
make docs
```

### Running the Linting and Formatting Checks Locally

To run the linting and formatting checks locally, run the following commands from the root of the repository:

```bash
flake8 .
pydocstringformatter .
```
### Running the Example Workflow Notebooks

The example Jupyter (.ipynb) notebooks contain extended use cases of `hyswap` functions. They are displayed in the [documentation pages](https://doi-usgs.github.io/hyswap/examples/index.html#example-workflow-notebooks), or you may download the notebooks from the 'example_notebooks' folder in this repository. The notebooks sometimes utilize additional packages that are not required to run the `hyswap` functions in isolation. You can use the developer installation instructions to create an environment containing all of the required packages to run the notebooks. Don't forget to also ``pip install hyswap`` into your working environment! 

## Contributing

See the [contributing guidelines](CONTRIBUTING.md) for more information.

## Citation

Hamshaw, S.D., Hariharan, J., Hinman, E.D., Sleckman, M.J., Stanish, L.F., 2024, hyswap: A USGS software package for hydrologic data analysis, DOI: https://doi.org/10.5066/P13SKXA2

## Questions?

Please send an email to comptools@usgs.gov with 'hyswap' noted somewhere in the subject line.

## License

See the [license](LICENSE.md) for more information.

## Disclaimer

See the [disclaimer](DISCLAIMER.md) for more information.
