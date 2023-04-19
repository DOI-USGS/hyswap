
Raster Hydrograph Examples
--------------------------

These examples show how raster hydrographs can be constructed by fetching data from NWIS using `dataretrieval`, formatting that data using functions provided by `hyswap` (:obj:`hyswap.rasterhydrograph.format_data`), and then plotted using `matplotlib`.

First we will fetch 20 years of streamflow data for a single site from NWIS using the `dataretrieval` package.

.. plot::
    :context: reset
    :include-source:

    # get data from a single site
    df, _ = dataretrieval.nwis.get_dv("03586500", parameterCd="00060",
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
    img = ax.imshow(df_formatted, aspect="auto", cmap="jet_r",
                    interpolation='none', vmin=0)
    plt.colorbar(img, ax=ax, label="Streamflow, cubic feet per second")
    ax.set_yticks(np.arange(-0.5, len(df_formatted.index)), [], minor=True)
    ax.set_yticks(np.arange(len(df_formatted.index)), df_formatted.index)
    ax.set_xlabel("Day of Year")
    ax.set_ylabel("Year")
    ax.set_title("Streamflow Raster Hydrograph for Site 03586500")
    plt.show()
