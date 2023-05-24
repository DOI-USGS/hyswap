
Raster Hydrograph Examples
--------------------------

These examples show how raster hydrographs can be constructed by fetching data from NWIS using `dataretrieval`, formatting that data using functions provided by `hyswap` (:obj:`hyswap.rasterhydrograph.format_data`), and then plotting using :obj:`hyswap.plots.plot_raster_hydrograph`.

First we will fetch 20 years of streamflow data for a single site from NWIS using the `dataretrieval` package.

.. plot::
    :context: reset
    :include-source:

    # get data from a single site
    siteno = "03586500"
    df, _ = dataretrieval.nwis.get_dv(siteno, parameterCd="00060",
                                      start="2000-01-01", end="2020-12-31")

This data can be formatted using `hyswap` to prepare it for plotting as a
raster hydrograph.

.. plot::
    :context:
    :include-source:

    # format the data
    df_formatted = hyswap.rasterhydrograph.format_data(df, '00060_Mean')

Now the data is arranged with years on the index (rows) and days of the year as columns, this makes it easy to plot as a raster hydrograph.

.. plot::
    :context:
    :include-source:

    # plot
    fig, ax = plt.subplots()
    ax = hyswap.plots.plot_raster_hydrograph(
        df_formatted, ax=ax,
        title=f"Streamflow Raster Hydrograph for Site {siteno}")
    plt.show()
