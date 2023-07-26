Calculations Quick-Reference
========

A quick-reference guide to the common types of calculations performed within the ``hyswap`` package is provided below. See the :doc:`Glossary </meta/glossary>` section for definitions of specific terms. Also, refer to the :doc:`API Reference </reference/index>` section for more detailed documentation on specific functions within ``hyswap``. 

Percentiles
-----------------

Percentiles are a core calculation of ``hyswap`` used to determing streamflow conditions (e.g., normal, high-flow, low-flow, drought, flood). Percentiles can be computed for streamflow (discharge), runoff, or *n*-day avearge streamflow. Multiple types of percentiles are commonly used in hydrologic analysis and vary primarily in what subset of observations are used in calculating percentiles. Percentiles are closely related to exceedance probabilities flow duration curves (see below). The ``hyswap`` package provides support for the following types of streamflow percentiles:

+---------------------------+-------------------------------------------+
| Percentile Type           | Description                               |
+===========================+===========================================+
| Variable (Day of Year)    | Computed using flow observations for that |
|                           | day from all years of record resulting    |
|                           | in percentile classes/thresholds that     |
|                           | change seasonally and correspond to a     |
|                           | specific day of year. Variable percentiles|
|                           | are useful for characterizing flow        |
|                           | conditions relative to the normal flow    |
|                           | on given day of the year. The variable    |
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
|                           |characterizing flow conditions relative to |
|                           | normal flow expected on a given day of the|
|                           | year.                                     |
+---------------------------+-------------------------------------------+

By default, ``hyswap`` computes streamflow percentiles using the unbiased Weibull plotting position formula (Weibull, 1939). The Weibull formula has been the standard approach used by hydrologists for generating flow-duration and flood-frequency curves (Helsel and others, 2020). Weibull plotting positions does not set values onto either 0 or 100, recognizing the existence of a non-zero probablity of exceeding the maximum or minimum observed value. For further discussion of plotting positions refer to Helsel and others (2020).

``hyswap`` uses the ``numpy.percentile()`` implementation of the Weibull method (Type 6) for calculating percentiles

Exceedance Probabilities
^^^^^^^^^^^^^^^^^^^^^^^^

In some hydrological studies, particularly those related to floods, a variation of the percentile known as the "percent exceedance" is used. It is simply obtained by subtracting the percentile scale value from 100 percent.  For example, a discharge at the 75th percentile is the same as a discharge at the 25th percent exceedance (100-75=25).

Flow-Duration Curves
^^^^^^^^^^^^^^^^^^^^^^^^

The flow-duration curve is a cumulative frequency curve that shows the percent of values that specified discharges were equaled or less than (percentile), or the percent of values that specified discharges were equaled or exceeded (percent exceedance).


Area-Based Runoff
-----------------

In addition to information on a per-streamgage basis, ``hyswap`` can generate water information at the regional scale through area-based runoff calculations.

Estimates of hydrologic unit runoff are generated by combining flow data collected at USGS streamgages, the respective drainage basin boundaries of the streamgages, and the boundaries of the 2,110 hydrologic cataloging units. Streamgages are selected for each water-year based on the availability of a complete daily flow dataset for the water-year. Geospatial data representing drainage basin divides for each streamgage location were delineated using the NHDPlus dataset and the accompanying digital elevation model (DEM) based flow direction information (USEPA and USGS, 2005). Basin boundaries with a computed drainage area within 25% of the streamgage drainage basin area reported in the USGS National Water Information System (NWIS) (USGS, 2008) were considered valid for this analysis. In a typical water-year during the period 1971-2000, there were about 6,000 streamgages with a complete daily flow dataset and an acceptable drainage basin boundary. The drainage basin areas of these streamgages ranged from 10 to 180,000 km2 with a median value of 3,000 km2.

Hydrologic cataloging units and associated 8-digit accounting numbers (HUC8s) are a widely used geographic framework for the conterminous United States. Each unit defines a geographic area representing part or all of a surface drainage basin or a combination of drainage basins. Cataloging units subdivide larger accounting units (HUC6s), subregions (HUC4s) and regions (HUC2s) into smaller areas designated by the U.S. Water Resources Council and the USGS's National Water Data Network. Cataloging units range in size from 24 to 22,808 km2 with a median value of 3,133 km2 (Seaber et al., 1987; Steeves et al., 1994).

The figure below illustrates the method used to compute runoff estimates for HUC8s. The first step is to compute runoff values (flow per unit area) for each streamgage basin by dividing the average daily flow for the water-year by the delineated basin area. In the hypothetical example, runoff is estimated at two streamgages (labeled A and B in the figure) by dividing the average daily flow measured at each of two streamgages by their respective drainage basin areas. (The drainage area of basin A is shaded light gray and the drainage area of basin B is shaded dark gray. Note that drainage basin B is nested within drainage basin A).

Each geospatial basin boundary is then overlain on a geospatial dataset of HUC8s (the polygons outlined in bold black lines) to determine the area of intersection within the two datasets. For each overlapping area of HUC8s and drainage basin boundaries, the fraction of the basin in the HUC8 and the fraction of the HUC8 in the basin are calculated. These fractions are then multiplied by each other to compute a weighting factor for each basin. The runoff values and associated weighting factors for all basins with any overlapping area with a HUC8 are combined, and a single weighted-average runoff value is computed for the HUC8.

The weighted-average runoff computations illustrated in the figure were repeated for all combinations of the roughly 6,000 basins and 2,100 hydrologic cataloging units (HUC8s). Runoff values for HUC8s which had no overlapping areas with streamgage basins were computed as the mean of the HUC8 runoff values within the same HUC4 (subregional unit).

.. image:: ../reference/huc8_runoff_example.gif
  :width: 600
  :alt: Map and table that provide an example of the computation of area-based runoff for a given HUC. 

References
----------

Brakebill, J.W., D.M. Wolock, and S.E. Terziotti, 2011. Digital Hydrologic Networks Supporting Applications Related to Spatially Referenced Regression Modeling. Journal of the American Water Resources Association(JAWRA) 47(5):916-932.

Helsel, D.R., Hirsch, R.M., Ryberg, K.R., Archfield, S.A., and Gilroy, E.J., 2020, Statistical methods in water resources: U.S. Geological Survey Techniques and Methods, book 4, chap. A3, 458 p., https://doi.org/10.3133/tm4a3. [Supersedes USGS Techniques of Water-Resources Investigations, book 4, chap. A3, version 1.1.]

Seaber, P.R., F.P. Kapinos, and G.L. Knapp, 1987. Hydrologic Unit Maps. U.S. Geological Survey Water Supply Paper 2294, 63 pp. http://pubs.usgs.gov/wsp/wsp2294/#pdf, accessed February 2009.

Steeves, P. and D. Nebert, 1994. 1:250,000 Scale Hydrologic Units of the United States. U.S. Geological Survey Open-File report 94-0236. http://water.usgs.gov/GIS/metadata/usgswrd/ XML/huc250k.xml, accessed June 2008.

USEPA (U.S. Environmental Protection Agency) and USGS (U.S. Geological Survey), 2005. National Hydrography Dataset Plus (NHDPlus). ftp://ftp.horizon-systems.com/NHDPlus/documentation/ metadata.pdf, accessed December 2009.

USGS (U.S. Geological Survey), 2008. National Water Information System (NWIS): Web Interface. http://waterdata.usgs.gov/nwis, accessed May 2008.

Weibull, W., 1939. The phenomenon of rupture in solids: Ingeniors Vetenskaps Akademien Handlinga, no. 153, 9. 17