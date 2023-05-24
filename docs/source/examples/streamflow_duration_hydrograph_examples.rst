
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
    ax.plot(df_year.index.dayofyear, df_year["00060_Mean"], color="black",
            label="Daily Mean Discharge - 2022")
    # plot historic percentiles filling between each pair
    pct_list = [0, 5, 10, 25, 75, 90, 95, 100]
    pct_colors = ["#e37676", "#e8c285", "#dbf595", "#a1cc9f",
                  "#7bdbd2", "#7587bf", "#ad63ba"]
    for i in range(1, len(pct_list)):
        ax.fill_between(
            percentiles_by_day.index,
            list(percentiles_by_day[pct_list[i - 1]].values),
            list(percentiles_by_day[pct_list[i]].values),
            color=pct_colors[i - 1],
            alpha=0.5,
            label="{}th - {}th Percentile".format(pct_list[i - 1], pct_list[i])
        )
    ax.set_xlabel("Day of Year")
    ax.set_xlim(1, 366)
    ax.set_xticks([1] + list(np.arange(30, 360, 30)) + [366])
    ax.set_ylabel("Discharge (cfs)")
    ax.set_yscale("log")
    ax.set_title("Percentiles of Discharge by Day of Year - Site 03586500")
    # two column legend
    ax.legend(loc="lower left", ncol=2)
    plt.show()