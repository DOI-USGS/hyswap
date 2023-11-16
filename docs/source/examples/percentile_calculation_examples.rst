
Percentile Calculation Examples
-------------------------------

Here we showcase the percentile calculation functionality available in the
:obj:`hyswap.percentiles` module.


Calculating Historic Percentiles for One Site
*********************************************

The :obj:`hyswap.percentiles.calculate_fixed_percentile_thresholds` function
is used to calculate a set of percentile thresholds given a set of data.
This function simply calculates one set of fixed percentile thresholds using all available data, 
and is not intended to be used for calculating percentiles for individual days of the year.

By default this method calculates percentiles using the Weibull distribution
with an alpha parameter of 0 and a beta parameter of 0. The Weibull
distribution is set as the default for percentile calculations after the USGS
`Guidelines for determining flood flow frequency — Bulletin 17C`_, Appendix 5.

Below is an example of fetching NWIS streamflow data for a USGS gage and then
calculating the 10th, 50th, and 90th percentiles for that data.

.. code::

    # fetch data from NWIS using dataretrieval
    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

    # calculate percentiles
    pct_values = hyswap.percentiles.calculate_fixed_percentile_thresholds(
        df['00060_Mean'], percentiles=[10, 50, 90])

    # print percentile values (corresponding to 10th, 50th, 90th percentiles)
    print(pct_values)
    [  4.9  75.6 637. ]

The percentile calculation can use a method other than the Weibull method if
desired by specifying a keyword parameter `method`. See the `numpy.percentile`_
documentation for more information on the available methods.


Calculating Historic Variable Percentiles for the Full Year
***********************************************************

The :obj:`hyswap.percentiles` module also contains functionality to calculate
percentile thresholds for each day of the year (variable threshold) using historical values.
This is done using the
:obj:`hyswap.percentiles.calculate_variable_percentile_thresholds_by_day`
function.
This function also defaults to using the Weibull distribution to calculate
percentiles, but can use other methods as well just like the
:obj:`hyswap.percentiles.calculate_fixed_percentile_thresholds` function.

Below is an example of fetching NWIS streamflow data for a USGS gage and then
calculating the 10th, 50th, and 90th percentiles for each day of the year.

.. code::

    # fetch data from NWIS using dataretrieval
    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

    # calculate percentiles by day
    pcts = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        df, '00060_Mean', percentiles=[10, 50, 90])

    # print first 5 rows of the percentile dataframe
    print(pcts.head())
                    10     50      90
    doy month-day
    1   01-01      29.6  226.0  1514.0
    2   01-02      41.0  199.0  1694.0
    3   01-03      43.4  260.0  1724.0
    4   01-04      56.4  239.0  1800.0
    5   01-05      53.8  257.0  1368.0

This function also supports the calculation of percentiles by different types
of years including the standard calendar year, as well as water years and
climate years.
By default, percentiles are only computed for days which have at least 10
years of data available, however this parameter can be altered by setting the
`min_years` parameter to a different value.
Multi-day averaging can also be performed by setting the `data_type` parameter
to a value like `7-day`, `14-day`, or `28-day`, the default value is `daily`
which is no temporal averaging.
See the function documentation
(:obj:`hyswap.percentiles.calculate_variable_percentile_thresholds_by_day`)
for additional details about the parameters
and options for this function.


Interpolating New Percentiles Using Previously Calculated Percentiles
*********************************************************************

To support faster calculations of percentiles without the need to repeatedly
fetch all historic data from NWIS, the
:obj:`hyswap.percentiles.calculate_fixed_percentile_from_value` and 
:obj:`hyswap.percentiles.calculate_variable_percentile_from_value`functions support the
interpolation of a new percentile value for a measurement given a previously
calculated set of percentiles and their associated values.

First is an example of fetching NWIS streamflow data for a USGS gage and then
calculating the 10th, 50th, and 90th fixed-threshold percentiles using all of the data.
Then, a new fixed-threshold percentile value is interpolated for a measurement of 100.0 cfs.

.. code::

    # fetch data from NWIS using dataretrieval
    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

    # calculate percentiles
    pct_values = hyswap.percentiles.calculate_fixed_percentile_thresholds(
        df['00060_Mean'], percentiles=[10, 50, 90])

    # calculate the percentile associated with 100.0 cfs
    pct = hyswap.percentiles.calculate_fixed_percentile_from_value(
        100.0, pct_values)

    # print that percentile value
    print(pct)
    51.74

Next is an example of fetching NWIS streamflow data for a USGS gage and then
calculating the variable-threshold percentiles using all of the data.
Then, a new variable-threshold percentile value is interpolated for a measurement
of 100.0 cfs on September 1st.

.. code::

    # fetch data from NWIS using dataretrieval
    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

    # calculate percentiles
    pct_values = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        df,'00060_Mean')

    # calculate the percentile associated with 100.0 cfs for September 1st
    pct = hyswap.percentiles.calculate_variable_percentile_from_value(
        100.0, pct_values, '09-01')

    # print that percentile value
    print(pct)
    90.02

Percentiles can also be calculated for multiple streamflow values at once. Below
is an example of fetching NWIS streamflow data for a USGS gage and then
calculating variable-threshold percentiles using all of the data.
Then, new variable-threshold percentile values are interpolated for measurements
from a recent month.

.. code::

    # fetch data from NWIS using dataretrieval
    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

    # calculate percentiles
    pct_values = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        df,'00060_Mean')

    # fetch data from NWIS using dataretrieval
    new_df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="2023-01-01",
                                      end="2023-01-31")

    # calculate the percentile associated streamflow for January, 2023
    pcts = hyswap.percentiles.calculate_multiple_variable_percentiles_from_values(
        new_df, '00060_Mean', pct_values)

    # print that percentile value
    print(pcts['est_pct'].head())
    
    2023-01-01      24.31
    2023-01-02      21.20
    2023-01-03      29.80
    2023-01-04      77.94
    2023-01-05      73.77


Below is an example of fetching variable-threshold percentiles for January 1st and their
associated values from the NWIS statistics service for a USGS gage and then
calculating a new variable-threshold percentile value for a measurement of 100.0 cfs.

.. code::

    # fetch data from NWIS using dataretrieval
    df, _ = dataretrieval.nwis.get_stats("03586500",
                                         parameterCd="00060",
                                         statReportType="daily")

    # munge the data
    munged_df = hyswap.utils.munge_nwis_stats(df)

    # pull out statistics for Jan. 1
    day1 = munged_df.iloc[0]

    # convert to a compatible dataframe
    day1_df = pd.DataFrame(data={"values": day1.values},
                           index=day1.index.values).T

    # calculate the percentile associated with 100.0 cfs
    pct = hyswap.percentiles.calculate_fixed_percentile_from_value(
        100.0, day1_df)

    # print that percentile value
    print(np.round(pct, 2))
    22.62


Categorizing Streamflow Conditions Based on Estimated Percentiles
*****************************************************************
To support generation of tables, figures and maps of current and past streamflow
conditions, the category of a given streamflow can be determined using
:obj:`hyswap.utils.categorize_flows`. The function assigns a category to a given
streamflow observation based on interpolated percentiles and a given categorization
schema.

Below is an example of fetching NWIS streamflow data for a USGS gage and then
calculating the variable-threshold percentiles using all of the data.
Then, new variable-threshold percentile values are interpolated for measurements
from a recent month and flow categories assigned.

.. code::

    # fetch data from NWIS using dataretrieval
    df, _ = dataretrieval.nwis.get_dv("04288000",
                                      parameterCd="00060",
                                      start="1900-01-01",
                                      end="2022-12-31")

    # calculate percentiles
    pct_values = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        df,'00060_Mean')

    # fetch data from NWIS using dataretrieval
    new_df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="2023-01-01",
                                      end="2023-01-31")

    # calculate the percentile associated with streamflow for January, 2023
    new_df = hyswap.percentiles.calculate_multiple_variable_percentiles_from_values(
        new_df, '00060_Mean', pct_values)

    # categorize streamflow using the default categorization schema
    flow_cat = hyswap.utils.categorize_flows(new_df, 'est_pct', schema_name='NWD')

    # print that flow categorizations
    print(flow_cat[['00060_Mean', 'est_pct', 'flow_cat']].head())
                                00060_Mean  est_pct           flow_cat
    datetime                                                         
    2023-01-01 00:00:00+00:00       112.0    26.70             Normal
    2023-01-02 00:00:00+00:00       103.0    23.75       Below normal
    2023-01-03 00:00:00+00:00       170.0    43.13             Normal
    2023-01-04 00:00:00+00:00       823.0    96.00  Much above normal
    2023-01-05 00:00:00+00:00       559.0    93.34  Much above normal

.. _`numpy.percentile`: https://numpy.org/doc/stable/reference/generated/numpy.percentile.html

.. _`Guidelines for determining flood flow frequency — Bulletin 17C`: https://pubs.er.usgs.gov/publication/tm4B5