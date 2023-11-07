Welcome
=======

Welcome to the documentation for the Python ``hyswap`` package.

`hyswap` (HYdrologic Surface Water Analysis Package), is a Python package which provides a set of functions for manipulating and visualizing USGS water data.
Specifically, a number of functions for calculating statistics (e.g., exceedance probabilities, daily historic percentiles) and generating related plots (e.g., flow duration curves, streamflow duration hydrographs) are available.
These methods are provided in a modular fashion as individual functions, and are designed to give the user flexibility in implementation.
For example, the raster hydrograph functionality is not limited to the visualization of historic streamflow information; it can be applied to any arbitrary information provided to the corresponding functions.
See the :doc:`Examples </examples/index>` section for fairly standard examples of using the functions in `hyswap` to perform typical hydrologic calculations and visualizations.
Read the :doc:`API Reference </reference/index>` if you'd like to see the full set of functions that are available.

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
