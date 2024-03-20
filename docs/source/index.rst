Welcome
=======

Welcome to the documentation for the Python ``hyswap`` package.

`hyswap` (HYdrologic Surface Water Analysis Package), is a Python package which provides a set of functions for manipulating and visualizing USGS water data.
Specifically, a number of functions for calculating statistics (e.g., exceedance probabilities, daily historic percentiles) and generating related plots (e.g., flow duration curves, streamflow duration hydrographs) are available.
These methods are provided in a modular fashion as individual functions, and are designed to give the user flexibility in implementation.
For example, the raster hydrograph functionality is not limited to the visualization of historic streamflow information; it can be applied to any arbitrary information provided to the corresponding functions.
See the :doc:`Simple Examples </examples/index>` section for fairly standard examples of using the functions in `hyswap` to perform typical hydrologic calculations and visualizations.
See the :doc:`Example Workflow Notebooks </examples/index>` section at the bottom of the page for more in depth tutorials of `hyswap` function usage in tandem with other custom functions and spatial packages. If you'd like to download and run the example Jupyter notebooks on your own, navigate to the `example_notebooks`_ subdirectory of the ``hyswap`` repository.
Read the :doc:`API Reference </reference/index>` if you'd like to see the full set of functions that are available.

.. _example_notebooks: https://github.com/DOI-USGS/hyswap/tree/main/example_notebooks

Table of Contents
-----------------

.. toctree::
   :maxdepth: 1

   meta/installation
   examples/index
   meta/glossary
   meta/calculations
   meta/contributing
   meta/disclaimer
   reference/index
