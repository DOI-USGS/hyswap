
Streamflow Duration Hydrograph Examples
---------------------------------------

This example shows how a streamflow hydrograph can be constructed by fetching historical streamflow data from NWIS using `dataretrieval`, and then calculating daily percentiles of streamflow for each day of the year.
The resulting hydrograph shows the streamflow values for all of 2022 plotted on top of the historical percentiles which are shown as shaded regions.

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
    # data from 2022
    df_year = df[df.index.year == 2022]
    # make column for day of year
    df_year["doy"] = df_year.index.dayofyear
    # sort data by day of year
    df_year = df_year.sort_values(by="doy")
    # plot data
    ax = hyswap.plots.plot_duration_hydrograph(
        percentiles_by_day,
        df_year,
        "00060_Mean",
        "doy",
        ax=ax,
        data_label="2022",
        title="Percentiles of Discharge by Day of Year - Site 03586500"
    )
    plt.tight_layout()
    plt.show()


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
        title="Percentiles of Discharge by Day of Year - Site 03586500"
    )
    plt.tight_layout()
    plt.show()
