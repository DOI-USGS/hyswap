
Cumulative Streamflow Hydrographs
---------------------------------

The following examples show how to fetch some data, and then calculate values for a cumulative streamflow hydrograph.
Then an example plotting routine to plot the cumulative hydrograph is shown.

First we will fetch some streamflow data from the NWIS service using the `dataretrieval` package.
In this example we will fetch 20 years of data from a single site and then calculate the cumulative streamflow percentiles from that data.

.. plot::
    :context: reset
    :include-source:

    # get some data from the NWIS service
    df, md = dataretrieval.nwis.get_dv(
        '06803495', start='2000-01-01', end='2020-12-31')

Now we can calculate the cumulative streamflow values per year using the :obj:`hyswap.cumulative.calculate_daily_cumulative_values` function.

.. plot::
    :context:
    :include-source:

    # calculate the cumulative streamflow values per year
    cdf = hyswap.cumulative.calculate_daily_cumulative_values(
        df, '00060_Mean', year_type='water')

Next we can use the :obj:`hyswap.percentiles.calculate_variable_percentile_thresholds_by_day` function to calculate the percentiles for each day of the year.

.. plot::
    :context:
    :include-source:

    # calculate the percentiles for each day of the year
    pdf = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        cdf, data_column_name='cumulative', percentiles=[25, 50, 75])

Finally we can plot the cumulative streamflow hydrograph using `matplotlib`.
Finally we can plot the cumulative streamflow hydrograph using the
:obj:`hyswap.plots.plot_cumulative_hydrograph` function.

.. plot::
    :context:
    :include-source:

    # plot the cumulative streamflow hydrograph
    fig, ax = plt.subplots(figsize=(8, 5))
    ax = hyswap.plots.plot_cumulative_hydrograph(
        cdf, 2020, ax=ax, title='Cumulative Streamflow Hydrograph')
    plt.show()
