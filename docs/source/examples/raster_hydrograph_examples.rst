
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

Now the data is arranged with years on the index (rows) and days of the year as columns, this makes it easy to plot as a raster hydrograph with :obj:`hyswap.plots.plot_raster_hydrograph`.

.. plot::
    :context:
    :include-source:

    # plot
    fig, ax = plt.subplots()
    ax = hyswap.plots.plot_raster_hydrograph(
        df_formatted, ax=ax,
        title=f"Raster Hydrograph for Site {siteno}")
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
        title=f"7-Day Average Raster Hydrograph for Site {siteno}",
        cbarlab='7-Day Average Streamflow, cubic feet per second')
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
        title=f"'Water Year' Raster Hydrograph for Site {siteno}",
        xlab='Month', ylab='Water Year')
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
        title=f"'Climate Year' Raster Hydrograph for Site {siteno}",
        xlab='Month', ylab='Climate Year',
        cmap='YlOrRd')
    plt.show()


We can also use just a subset of the available data if we wish by specifying start and end years using the `begin_year` and `end_year` keyword arguments to :obj:`hyswap.rasterhydrograph.format_data`.

.. plot::
    :context: reset
    :include-source:

    # get data from a single site
    siteno = "12205000"
    df, _ = dataretrieval.nwis.get_dv(siteno, parameterCd="00060",
                                      start="1995-01-01", end="2015-12-31")

    # format the data to years 2000-2010
    df_formatted = hyswap.rasterhydrograph.format_data(
        df, '00060_Mean', year_type='climate',
        begin_year=2000, end_year=2010)

    # plot
    fig, ax = plt.subplots()
    ax = hyswap.plots.plot_raster_hydrograph(
        df_formatted, ax=ax,
        title=f"2000-2010 'Climate Year' Raster Hydrograph for Site {siteno}",
        xlab='Month', ylab='Climate Year',
        cmap='YlOrRd')
    plt.show()


Raster Hydrograph of Non-Streamflow Data
****************************************

The functions used above to generate raster hydrographs graphically depicting streamflow over time can also be used to visualize other types of data.
For example, we can visualize a "raster hydrograph" of the water level at a station over time.
We will use station 02311500 in Florida as an example.

.. plot::
    :context: reset
    :include-source:

    # get stage data from a single site
    siteno = "02311500"
    parameterCd = "00065"  # code for gage height
    df, _ = dataretrieval.nwis.get_dv(siteno, parameterCd=parameterCd,
                                      start="2000-01-01", end="2020-12-31")

    # format the data
    df_formatted = hyswap.rasterhydrograph.format_data(
        df, '00065_Mean')

    # plot
    fig, ax = plt.subplots()
    ax = hyswap.plots.plot_raster_hydrograph(
        df_formatted, ax=ax,
        title=f"Stage 'Raster Hydrograph' for Site {siteno}",
        cmap='cool', cbarlab='Gage height, feet')
    plt.show()


We can improve this visualization by turning off the logarithmic color scale by setting the normalization of the colorbar to be `None` which overrides the default normalization of `matplotlib.colors.LogNorm`.
The default scheme is logarithmic because this is the most common way to visualize streamflow data, but for other types of data, a linear scale may be more appropriate.


.. plot::
    :context: reset
    :include-source:

    # get stage data from a single site
    siteno = "02311500"
    parameterCd = "00065"  # code for gage height
    df, _ = dataretrieval.nwis.get_dv(siteno, parameterCd=parameterCd,
                                      start="2000-01-01", end="2020-12-31")

    # format the data
    df_formatted = hyswap.rasterhydrograph.format_data(
        df, '00065_Mean')

    # plot
    fig, ax = plt.subplots()
    ax = hyswap.plots.plot_raster_hydrograph(
        df_formatted, ax=ax,
        title=f"Stage 'Raster Hydrograph' for Site {siteno}",
        cmap='cool', cbarlab='Gage height, feet', norm=None)
    plt.show()