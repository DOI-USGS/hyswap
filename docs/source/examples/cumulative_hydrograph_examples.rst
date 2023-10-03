
Cumulative Streamflow Hydrographs
---------------------------------

The following examples show how to fetch data and calculate values for a cumulative streamflow hydrograph before plotting the cumulative hydrograph using the `hyswap` :obj:`hyswap.plots.plot_cumulative_hydrograph` function.


Cumulative Streamflow Over The 2020 Water Year
**********************************************

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

Then we can plot the cumulative streamflow hydrograph. 

.. plot::
    :context:
    :include-source:

    # plot the cumulative streamflow hydrograph
    fig, ax = plt.subplots(figsize=(8, 5))
    ax = hyswap.plots.plot_cumulative_hydrograph(
        cdf, 2020, ax=ax, year_type='water',
        title='Cumulative Streamflow Hydrograph')
    plt.show()


Cumulative Streamflow Over The 2020 Calendar Year
*************************************************

We can also calculate and visualize the cumulative streamflow hydrograph for the 2020 calendar year, rather than the water year.
The code is very similar, we simply do not specify the `year_type` argument in the :obj:`hyswap.cumulative.calculate_daily_cumulative_values` function, as the default is to use the calendar year.

.. plot::
    :context: reset
    :include-source:

    # get some data from the NWIS service
    df, md = dataretrieval.nwis.get_dv(
        '06803495', start='2000-01-01', end='2020-12-31')

    # calculate the cumulative streamflow values per year
    cdf = hyswap.cumulative.calculate_daily_cumulative_values(
        df, '00060_Mean')

    # plot the cumulative streamflow hydrograph
    fig, ax = plt.subplots(figsize=(8, 5))
    ax = hyswap.plots.plot_cumulative_hydrograph(
        cdf, 2020, ax=ax, title='Cumulative Streamflow Hydrograph')
    plt.show()


Cumulative Streamflow Over The 2020 Climate Year
************************************************

We can also calculate and visualize the cumulative streamflow hydrograph for the 2020 climate year, rather than the water year or the calendar year.
The code is very similar, we simply specify the `year_type` argument in the :obj:`hyswap.cumulative.calculate_daily_cumulative_values` function to be 'climate'.

.. plot::
    :context: reset
    :include-source:

    # get some data from the NWIS service
    df, md = dataretrieval.nwis.get_dv(
        '06803495', start='2000-01-01', end='2020-12-31')

    # calculate the cumulative streamflow values per year
    cdf = hyswap.cumulative.calculate_daily_cumulative_values(
        df, '00060_Mean', year_type='climate')

    # plot the cumulative streamflow hydrograph
    fig, ax = plt.subplots(figsize=(8, 5))
    ax = hyswap.plots.plot_cumulative_hydrograph(
        cdf, 2020, ax=ax, year_type='climate',
        title='Cumulative Streamflow Hydrograph')
    plt.show()


Visualizing the Minimum and Maximum Cumulative Percentile Values
****************************************************************

We can also visualize the minimum and maximum cumulative percentile values for a given year as dotted and dashed lines respectively.
We will use the calendar year example to showcase this functionality.

.. plot::
    :context: reset
    :include-source:

    # get some data from the NWIS service
    df, md = dataretrieval.nwis.get_dv(
        '06803495', start='2000-01-01', end='2020-12-31')

    # calculate the cumulative streamflow values per year
    cdf = hyswap.cumulative.calculate_daily_cumulative_values(
        df, '00060_Mean')

    # plot the cumulative streamflow hydrograph
    fig, ax = plt.subplots(figsize=(8, 5))
    ax = hyswap.plots.plot_cumulative_hydrograph(
        cdf, 2020, max_pct=True, min_pct=True,
        ax=ax, title='Cumulative Streamflow Hydrograph')
    plt.show()


Visualizing Multiple Years of Data
**********************************

We are not limited to explicitly visualizing the cumulative streamflow from individual years.
We can supply multiple `target_years` as a list, and each will be plotted as an individual cumulative discharge line with an associated label in the legend.
Below is an example of this functionality wherein we plot the cumulative discharge for years 2010, 2015, and 2020.

.. plot::
    :context: reset
    :include-source:

    # get some data from the NWIS service
    df, md = dataretrieval.nwis.get_dv(
        '06803495', start='2000-01-01', end='2020-12-31')

    # calculate the cumulative streamflow values per year
    cdf = hyswap.cumulative.calculate_daily_cumulative_values(
        df, '00060_Mean')

    # plot the cumulative streamflow hydrograph
    fig, ax = plt.subplots(figsize=(8, 5))
    ax = hyswap.plots.plot_cumulative_hydrograph(
        cdf, target_years=[2010, 2015, 2020],
        ax=ax, title='Cumulative Streamflow Hydrograph')
    plt.show()


Customizing the Filled Envelope
*******************************

We can customize both the percentile thresholds between which a shaded area is plotted, as well as the color and transparency of the shaded area.
The percentile thresholds used as the upper and lower-bound of the shaded area can be specified using the `envelope_pct` argument.
The color and transparency, as well as other properties, of the filled region can be customized by passing keyword arguments to the :obj:`hyswap.plots.plot_cumulative_hydrograph` function, as those arguments are passed to the :meth:`matplotlib.axes.Axes.fill_between` function.
We provide an example of doing this by filling between the 10th and 90th percentiles, and making the filled region red and semi-transparent.

.. plot::
    :context: reset
    :include-source:

    # get some data from the NWIS service
    df, md = dataretrieval.nwis.get_dv(
        '06803495', start='2000-01-01', end='2020-12-31')

    # calculate the cumulative streamflow values per year
    cdf = hyswap.cumulative.calculate_daily_cumulative_values(
        df, '00060_Mean')

    # plot the cumulative streamflow hydrograph
    fig, ax = plt.subplots(figsize=(8, 5))
    ax = hyswap.plots.plot_cumulative_hydrograph(
        cdf, 2020, envelope_pct=[10, 90], color='red', alpha=0.25,
        ax=ax, title='Cumulative Streamflow Hydrograph')
    plt.show()
