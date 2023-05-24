
Raster Hydrographs
------------------

These examples show how raster hydrographs can be constructed by fetching data from NWIS using `dataretrieval`, formatting that data using functions provided by `hyswap` (:obj:`hyswap.rasterhydrograph.format_data`), and then plotting using :obj:`hyswap.plots.plot_raster_hydrograph`.


Daily Data Raster Hydrograph Example (Site 03586500)
****************************************************

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


7-Day Average Raster Hydrograph Example (Site 03586500)
*******************************************************

The same data can be plotted as a 7-day average raster hydrograph by passing the `data_type` argument to :obj:`hyswap.rasterhydrograph.format_data` function.

.. plot::
    :context: reset
    :include-source:

    # get data from a single site
    siteno = "03586500"
    df, _ = dataretrieval.nwis.get_dv(siteno, parameterCd="00060",
                                      start="2000-01-01", end="2020-12-31")

    # format the data for a 7-day rolling average
    df_formatted = hyswap.rasterhydrograph.format_data(
        df, '00060_Mean', data_type='7-day')

    # plot
    fig, ax = plt.subplots()
    ax = hyswap.plots.plot_raster_hydrograph(
        df_formatted, ax=ax,
        title=f"7-Day Average Streamflow Raster Hydrograph for Site {siteno}")
    plt.show()


This resulting 7-day averaged raster hydrograph should look "smoother" than the single day raster hydrograph shown previously.


Raster Hydrograph Over a "Water Year"
*************************************

There is also support for visualizing the raster hydrograph over the course of a water year, which begins on October 1st and ends on September 30th of the following year.
The ending year is the year that is displayed on the y-axis of the raster hydrograph, for example, the water year 2020 would be displayed as 2020 on the y-axis, but would actually contain data from October 1st, 2019 to September 30th, 2020.

.. plot::
    :context: reset
    :include-source:

    # get data from a single site
    siteno = "08110500"
    df, _ = dataretrieval.nwis.get_dv(siteno, parameterCd="00060",
                                      start="1975-01-01", end="1995-12-31")

    # format the data
    df_formatted = hyswap.rasterhydrograph.format_data(
        df, '00060_Mean', year_type='water')

    # plot
    fig, ax = plt.subplots()
    ax = hyswap.plots.plot_raster_hydrograph(
        df_formatted, ax=ax,
        title=f"Streamflow Water Year Raster Hydrograph for Site {siteno}",
        xlab='Day of Water Year', ylab='Water Year')
    plt.show()


Raster Hydrograph Over a "Climate Year" with Alt. Colors
*********************************************************

There is also support for visualizing the raster hydrograph over the course of a climate year, which begins on April 1st and ends on March 31th of the following year.
The ending year is the year that is displayed on the y-axis of the raster hydrograph, for example, the climate year 2020 would be displayed as 2020 on the y-axis, but would actually contain data from April 1st, 2019 to March 31th, 2020.

In this example, we will also change the color of the raster hydrograph to be shades of yellow, orange, and red, and show how that can be done by passing the `cmap` keyword argument to :obj:`hyswap.plots.plot_raster_hydrograph` while specifying a `matplotlib` colormap.

.. plot::
    :context: reset
    :include-source:

    # get data from a single site
    siteno = "12205000"
    df, _ = dataretrieval.nwis.get_dv(siteno, parameterCd="00060",
                                      start="1995-01-01", end="2015-12-31")

    # format the data
    df_formatted = hyswap.rasterhydrograph.format_data(
        df, '00060_Mean', year_type='climate')

    # plot
    fig, ax = plt.subplots()
    ax = hyswap.plots.plot_raster_hydrograph(
        df_formatted, ax=ax,
        title=f"Streamflow Climate Year Raster Hydrograph for Site {siteno}",
        xlab='Day of Climate Year', ylab='Climate Year',
        cmap='YlOrRd')
    plt.show()
