Calculations Quick-Reference
============================

A quick-reference guide to the common types of calculations performed within the ``hyswap`` package is provided below. See the :doc:`Glossary </meta/glossary>` section for definitions of specific terms. Also, refer to the :doc:`API Reference </reference/index>` section for more detailed documentation on specific functions within ``hyswap``. 

Assumptions and Caveats
-----------------------
The ``hyswap`` package functions assume that provided streamflow data has been quality conrolled. No checks on incorrect, missing, or negative values are performed. Users should perform any necessary QA/QC checks on the data prior to using ``hyswap`` functions. Similarly, ``hyswap`` functions on the entire length of streamflow data provided to a given function or plot and therefore may represent a mix of regulated and unregulated flow, or span periods of major watershed changes that potentially violate statistical methods.  


Streamflow Percentiles
----------------------

Streamflow percentiles are a core calculation of ``hyswap`` that are used to determine streamflow conditions (e.g., normal, high-flow, low-flow, drought, flood). Percentiles can be computed for streamflow (discharge), runoff, or *n*-day avearge streamflow. Multiple types of percentiles are used in hydrologic analysis and vary in what subset of observations are used in calculating a given set of percentiles. Percentiles are closely related to exceedance probabilities used to construct flow duration curves (see below). The ``hyswap`` package provides support for the following types of streamflow percentiles:

+---------------------------+-------------------------------------------+
| Percentile Type           | Description                               |
+===========================+===========================================+
| Variable (Day of Year)    | Computed using flow observations for that |
|                           | day from all years of record resulting    |
|                           | in percentile classes/thresholds that     |
|                           | change seasonally and correspond to a     |
|                           | specific day of year. Variable percentiles|
|                           | are useful for characterizing flow        |
|                           | conditions relative to the typrical flow  |
|                           | on a given day of the year. The variable  |
|                           | (day of year) percentile is the standard  |
|                           | percentile that is displayed on the USGS  |
|                           | National Water Dashboard and WaterWatch.  |
+---------------------------+-------------------------------------------+
| Fixed (All days)          | Computed using all flow observations in   | 
|                           | the period of record. Records from all    |
|                           | days of the year are combined resulting   |
|                           | in percentile classes/thresholds that do  |
|                           | not change seasonally. Fixed percentiles  |
|                           | are useful for characterizing flow        |
|                           | conditions relative non-moving phenomena  |
|                           | such as flood stages or dam intakes.      |
+---------------------------+-------------------------------------------+
| Variable Moving Window    | Computed using flow observations for that |
| (Day of Year)             | day plus or minus *n* number of days      |
|                           | (e.g., 7, 14, or 30) from all years of    |
|                           | record resulting in percentile            |
|                           | classes/thresholds that change seasonally |
|                           | and correspond to a specific day of year. |
|                           | Variable moving window percentiles reduce |
|                           | the fluctuation in percentile classes from|
|                           | day-to-day, especially for sites with     |
|                           | short observation records. Variable       |
|                           | moving window are useful for              |
|                           | characterizing flow conditions relative to|
|                           | typical flow expected on a given day of   |
|                           | the year.                                 |
+---------------------------+-------------------------------------------+

By default, ``hyswap`` computes streamflow percentiles using the unbiased Weibull plotting position formula (Weibull, 1939). The Weibull formula has been the standard approach used by hydrologists for generating flow-duration and flood-frequency curves `(Helsel and others, 2020)`_. Weibull plotting position does not set values to either 0 or 100, recognizing the existence of a non-zero probablity of exceeding the maximum or minimum observed value. For further discussion of plotting positions refer to `(Helsel and others, 2020)`_.

``hyswap`` uses the ``numpy.percentile()`` implementation of the Weibull method (Type 6) for calculating percentiles. Additional methods of computing percentiles that exist in the ``numpy.percentile()`` function can be used in ``hyswap``.

Other default settings for percentile calculations are that NA values are dropped, a minimum of 10 years of record length is available for a given day of year, and percentile levels of 0, 5, 10, 25, 50, 75, 90, 95, 100.

By default, ``hyswap`` computes streamflow percentiles using the unbiased Weibull plotting position formula (Weibull, 1939). The Weibull formula has been the standard approach used by hydrologists for generating flow-duration and flood-frequency curves `(Helsel and others, 2020)`_. Weibull plotting positions does not set values onto either 0 or 100, recognizing the existence of a non-zero probablity of exceeding the maximum or minimum observed value. For further discussion of plotting positions refer to `(Helsel and others, 2020)`_.

``hyswap`` uses the ``numpy.percentile()`` implementation of the Weibull method (Type 6) for calculating percentiles

Exceedance Probabilities and Flow-Duration Curves
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In some hydrological studies, particularly those related to floods, a variation of the percentile known as the "percent exceedance" is used. It can be obtained by subtracting the percentile scale value from 100 percent.  For example, a discharge at the 75th percentile is the same as a discharge at the 25th percent exceedance (100-75=25). By default, ``hyswap`` computes streamflow exceedance probabilities using the unbiased Weibull plotting position formula (Weibull, 1939). Additional methods of computing exceedance probabilities can be used in ``hyswap`` including linear (R Type 4), Hazen (R Type 5), Gumbel (R Type 7), Reiss (R Type 8), and Blom (R Type 9). Flow-duration curves computed within ``hyswap`` are a cumulative frequency curve that shows the percent of values that specified discharges were equaled or less than (percentile), or the percent of values that specified discharges were equaled or exceeded (percent exceedance). The Weibull method of computing exceedance probabilities is used by default for computing flow-duration curves.


Area-Based Runoff
-----------------

In addition to information on a per-streamgage basis, ``hyswap`` can generate water information at the regional scale through computation of area-based runoff calculations.

Estimates of hydrologic unit runoff are generated by combining flow data collected at USGS streamgages, the respective drainage basin boundaries of the streamgages, and the boundaries of hydrologic cataloging units. Streamgages are selected for each year based on the availability of a complete daily flow dataset for the year. Geospatial boundaries of streamgages are based on delineated gage drainage areas calcualted using NHDPlus Version 1 data `(U.S. Geological Survey, 2011)`_.

Hydrologic cataloging units and associated 8-digit accounting numbers (HUC8s) are a widely used geographic framework for the conterminous United States (CONUS). Each unit defines a geographic area representing part or all of a surface drainage basin or a combination of drainage basins. Cataloging units subdivide larger accounting units (HUC6s), subregions (HUC4s) and regions (HUC2s) into smaller areas designated by the U.S. Water Resources Council and the USGS's National Water Data Network. Cataloging units range in size from 24 to 22,808 km\ :sup:`2` with a median value of 3,133 km\ :sup:`2` `(Jones and others, 2022)`.

Figure 1 below illustrates the method used to compute runoff estimates for HUC8s. The first step is to compute runoff values (flow per unit area) for each streamgage basin by dividing the average daily flow by the delineated basin area. In the hypothetical example, runoff is estimated at two streamgages (labeled A and B in the figure) by dividing the average daily flow measured at each of two streamgages by their respective drainage basin areas. (The drainage area of basin A is shaded light gray and the drainage area of basin B is shaded dark gray. Note that drainage basin B is nested within drainage basin A).

Each geospatial basin boundary is then overlain on a geospatial dataset of HUC8s (the polygons outlined in bold black lines) to determine the area of intersection within the two datasets. For each overlapping area of HUC8s and drainage basin boundaries, the fraction of the basin in the HUC8 and the fraction of the HUC8 in the basin are calculated. These fractions are then multiplied by each other to compute a weighting factor for each basin. The runoff values and associated weighting factors for all basins with any overlapping area with a HUC8 are combined, and a single weighted-average runoff value is computed for the HUC8.

The weighted-average runoff computations illustrated in the figure can be repeated for all combinations of USGS streamgage basins and hydrologic cataloging units (HUC8s). Runoff values for HUC8s which had no overlapping areas with streamgage basins were computed as the mean of the HUC8 runoff values within the same HUC4 (subregional unit).

.. image:: ../reference/huc8_runoff_example.gif
  :width: 600
  :alt: Map and table that provide an example of the computation of area-based runoff for a given HUC. 

Figure 1. Example computation for computation of runoff for a selected HUC unit. Figure from `(Brakebill and others, 2011)`_

*Description of methods for area-based runoff computation is adapted from USGS WaterWatch*

References
----------

Brakebill, J.W., D.M. Wolock, and S.E. Terziotti, 2011. Digital Hydrologic Networks Supporting Applications Related to Spatially Referenced Regression Modeling. Journal of the American Water Resources Association(JAWRA) 47(5):916-932. `doi.org/10.1111/j.1752-1688.2011.00578.x <https://doi.org/10.1111/j.1752-1688.2011.00578.x>`_`

Helsel, D.R., Hirsch, R.M., Ryberg, K.R., Archfield, S.A., and Gilroy, E.J., 2020, Statistical methods in water resources: U.S. Geological Survey Techniques and Methods, book 4, chap. A3, 458 p., `doi.org/10.3133/tm4a3 <https://doi.org/10.3133/tm4a3>`_. [Supersedes USGS Techniques of Water-Resources Investigations, book 4, chap. A3, version 1.1.]

Jones, K.A., Niknami, L.S., Buto, S.G., and Decker, D., 2022, Federal standards and procedures for the national Watershed Boundary Dataset (WBD) (5 ed.): U.S. Geological Survey Techniques and Methods 11-A3, 54 p., `doi.org/10.3133/tm11A3 <https://doi.org/10.3133/tm11A3>`_.

U.S. Geological Survey, 2011. USGS Streamgage NHDPlus Version 1 Basins 2011. Data Series [DS-719] `water.usgs.gov/lookup/getspatial?streamgagebasins <https://water.usgs.gov/lookup/getspatial?streamgagebasins>`_`

U.S. Geological Survey, 2023. USGS water data for the Nation: U.S. Geological Survey National Water Information System database, accessed at `doi.org/10.5066/F7P55KJN <http://dx.doi.org/10.5066/F7P55KJN>`_`

Weibull, W., 1939. A statistical theory of strength of materials: Ingeniors Vetenskaps Akademien Handlinga, no. 153, 9. 17


.. _(Brakebill and others, 2011): https://doi.org/10.1111/j.1752-1688.2011.00578.x
.. _(Helsel and others, 2020): https://doi.org/10.3133/tm4A3
.. _(Jones and others, 2022): https://doi.org/10.3133/tm11A3
.. _(U.S. Geological Survey, 2011): https://water.usgs.gov/lookup/getspatial?streamgagebasins
.. _(U.S. Geological Survey, 2023): http://dx.doi.org/10.5066/F7P55KJN