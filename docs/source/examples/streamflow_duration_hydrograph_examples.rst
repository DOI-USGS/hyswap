
Streamflow Duration Hydrographs
-------------------------------

These examples show how a streamflow hydrograph can be constructed by fetching historical streamflow data from NWIS using `dataretrieval`, and then calculating daily percentiles of streamflow for each day of the year.
The resulting hydrographs show the streamflow values for all of 2022 plotted on top of the historical percentiles which are shown as shaded regions.


Calculating Percentiles Using `hyswap`
**************************************

First, we will fetch streamflow data for a single gage from NWIS using the `dataretrieval` package.

.. plot::
    :context: reset
    :include-source:

    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

Next we will calculate the percentiles for each day of the year based on historic streamflow data using the :obj:`hyswap.percentiles.calculate_variable_percentile_thresholds_by_day` function.

.. plot::
    :context:
    :include-source:

    percentiles_by_day = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        df, "00060_Mean"
    )

Finally, we will plot the streamflow data for 2022 on top of the historical percentiles.

.. plot::
    :context:
    :include-source:

    # plotting percentiles by day with line shade between
    fig, ax = plt.subplots(figsize=(10, 6))
    # filter down to data from 2022
    df_year = df[df.index.year == 2022]
    # plot data
    ax = hyswap.plots.plot_duration_hydrograph(
        percentiles_by_day,
        df_year,
        "00060_Mean",
        "index_doy",
        ax=ax,
        data_label="2022",
        title="Percentiles of Streamflow by Day of Year - Site 03586500"
    )
    plt.tight_layout()
    plt.show()


Fetching Percentiles from the NWIS Statistics Service
*****************************************************

You don't have to compute the percentiles using `hyswap`.
If you'd rather use the NWIS web service daily percentiles, you can use those values instead.
We provide a convenience utility function to help make this possible, :obj:`hyswap.utils.munge_nwis_stats`.
Below is an example of fetching NWIS daily statistics data using the `dataretrieval` package, and then munging and plotting the data with `hyswap`.

First, we will use `dataretrieval` to fetch both the statistics data from NWIS,
as well as streamflow data from the year 2022.

.. plot::
    :context: reset
    :include-source:

    df_stats, _ = dataretrieval.nwis.get_stats(
        "03586500",
        parameterCd="00060",
        statReportType="daily"
    )

    df_flow, _ = dataretrieval.nwis.get_dv(
        "03586500",
        parameterCd="00060",
        start="2022-01-01",
        end="2022-12-31"
    )

Now that we've retrieved our web data, we will apply some `hyswap` functions to make a duration hydrograph plot.

.. plot::
    :context:
    :include-source:

    # plotting percentiles by day with line shade between
    fig, ax = plt.subplots(figsize=(10, 6))
    # munge the statistics data
    df_stats = hyswap.utils.munge_nwis_stats(df_stats)
    # add day of year column to the flow data
    df_flow["doy"] = df_flow.index.dayofyear
    # plot the duration hydrograph
    ax = hyswap.plots.plot_duration_hydrograph(
        df_stats,
        df_flow,
        "00060_Mean",
        "doy",
        ax=ax,
        data_label="2022",
        title="Percentiles of Streamflow by Day of Year - Site 03586500"
    )
    plt.tight_layout()
    plt.show()


Plotting by Water Year
**********************

The examples above show how to plot the percentiles by day of year using the calendar year.
In this example, we will plot the percentiles by day of water year, as water years are commonly by hydrologists.
The only change this requires from above is specifying the type of year we are planning to use when calculating the daily percentile thresholds.

.. plot::
    :context: reset
    :include-source:

    # fetch historic data from NWIS
    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

    # calculate historic daily percentile thresholds for water years
    percentiles_by_day = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        df, "00060_Mean", year_type="water"
    )

    # plotting percentiles by day with line shade between
    fig, ax = plt.subplots(figsize=(10, 6))
    # filter down to data from 2022
    df_year = df[df['index_year'] == 2022]
    # plot data
    ax = hyswap.plots.plot_duration_hydrograph(
        percentiles_by_day,
        df_year,
        "00060_Mean",
        "index_doy",
        ax=ax,
        data_label="Water Year 2022",
        title="Percentiles of Streamflow by Day of Year - Site 03586500"
    )
    plt.tight_layout()
    plt.show()


Plotting by Climate Year
************************

The examples above show how to plot the percentiles by day of year using the calendar year.
In this example, we will plot the percentiles by day of climate year.
The only change this requires from above is specifying the type of year we are planning to use when calculating the daily percentile thresholds.

.. plot::
    :context: reset
    :include-source:

    # fetch historic data from NWIS
    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

    # calculate historic daily percentile thresholds for water years
    percentiles_by_day = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        df, "00060_Mean", year_type="climate"
    )

    # plotting percentiles by day with line shade between
    fig, ax = plt.subplots(figsize=(10, 6))
    # filter down to data from 2022
    df_year = df[df['index_year'] == 2022]
    # plot data
    ax = hyswap.plots.plot_duration_hydrograph(
        percentiles_by_day,
        df_year,
        "00060_Mean",
        "index_doy",
        ax=ax,
        data_label="Climate Year 2022",
        title="Percentiles of Streamflow by Day of Year - Site 03586500"
    )
    plt.tight_layout()
    plt.show()


Plotting Custom Set of Percentile Thresholds
*********************************************

In this example we will calculate and plot a unique set of daily percentile thresholds.
We will also specify the colors to be used for the percentile envelopes.

.. plot::
    :context: reset
    :include-source:

    # fetch historic data from NWIS
    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

    # calculate specific historic daily percentile thresholds for water years
    percentiles_by_day = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        df, "00060_Mean", percentiles=[0, 25, 50, 75, 100], year_type="water"
    )

    # plotting percentiles by day with line shade between
    fig, ax = plt.subplots(figsize=(10, 6))
    # filter down to data from 2022
    df_year = df[df['index_year'] == 2022]
    # plot data
    ax = hyswap.plots.plot_duration_hydrograph(
        percentiles_by_day,
        df_year,
        "00060_Mean",
        "index_doy",
        pct_list=[0, 25, 50, 75, 100],
        ax=ax,
        data_label="Water Year 2022",
        title="Percentiles of Streamflow by Day of Year - Site 03586500",
        colors=['r', 'm', 'c', 'b']
    )
    plt.tight_layout()
    plt.show()


Customizing Fill Areas
**********************

In this example we will customize the fill areas between the percentile thresholds by passing keyword arguments to the :obj:`hyswap.plots.plot_duration_hydrograph` function that are then passed through to the :meth:`matplotlib.axes.Axes.fill_between` function.
Specifically we will set the `alpha` argument to 1.0 to make the fill areas opaque (the default value is 0.5 for some transparency).

.. plot::
    :context: reset
    :include-source:

    # fetch historic data from NWIS
    df, _ = dataretrieval.nwis.get_dv("03586500",
                                      parameterCd="00060",
                                      start="1776-01-01",
                                      end="2022-12-31")

    # calculate historic daily percentile thresholds for water years
    percentiles_by_day = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
        df, "00060_Mean", year_type="water"
    )

    # plotting percentiles by day with line shade between
    fig, ax = plt.subplots(figsize=(10, 6))
    # filter down to data from 2022
    df_year = df[df['index_year'] == 2022]
    # plot data
    ax = hyswap.plots.plot_duration_hydrograph(
        percentiles_by_day,
        df_year,
        "00060_Mean",
        "index_doy",
        ax=ax,
        data_label="Water Year 2022",
        title="Percentiles of Streamflow by Day of Year - Site 03586500",
        alpha=1.0
    )
    plt.tight_layout()
    plt.show()
