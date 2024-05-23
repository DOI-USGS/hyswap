"""Functions for plotting."""
import calendar
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from hyswap.percentiles import calculate_variable_percentile_thresholds_by_day
from hyswap.cumulative import calculate_daily_cumulative_values


def plot_flow_duration_curve(
        values, exceedance_probabilities,
        observations=None, observation_probabilities=None,
        ax=None, title='Flow Duration Curve',
        xlab='Exceedance Probability\n' +
        '(Percentage of time indicated value was equaled or exceeded)',
        ylab='Discharge, ft3/s', grid=True,
        scatter_kwargs={}, **kwargs):
    """ Plot a flow duration curve.

    Flow duration curves are cumulative frequency curves that show the
    percentage of time measured discharge values are equaled or exceeded
    by all other discharge values in the dataset.

    Parameters
    ----------
    values : array-like
        Values to plot along y-axis.
    exceedance_probabilities : array-like
        Exceedance probabilities for each value, likely calculated from
        a function like :obj:`hyswap.exceedance.calculate_exceedance_probability_from_values_multiple`.
    observations : list, numpy.ndarray, optional
        List, numpy array or list-able set of flow observations. Optional, if
        not provided the observations are not plotted.
    observation_probabilities : list, numpy.ndarray, optional
        Exceedance probabilities corresponding to each observation, likely
        calculated from a function like
        :obj:`hyswap.exceedance.calculate_exceedance_probability_from_values_multiple`.
        Optional, if not provided observations are not plotted.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If not provided, a new figure and axes will be
        created.
    title : str, optional
        Title for the plot. If not provided, the default title will be
        'Flow Duration Curve'.
    xlab : str, optional
        Label for the x-axis. If not provided, a default label will be used.
    ylab : str, optional
        Label for the y-axis. If not provided, a default label will be used.
    grid : bool, optional
        Whether to show grid lines on the plot. Default is True.
    scatter_kwargs : dict
        Dictionary containing keyword arguments to pass to the observations
        plotting method, :meth:`matplotlib.axes.Axes.scatter`.
    **kwargs
        Keyword arguments passed to :meth:`matplotlib.axes.Axes.plot`.

    Returns
    -------
    matplotlib.axes.Axes
        Axes object containing the plot.

    Examples
    --------
    Fetch some data from NWIS, calculate the exceedance probabilities and then
    make the flow duration curve.

    .. plot::
        :include-source:

        >>> df, _ = dataretrieval.nwis.get_dv(site='06892350',
        ...                                   parameterCd='00060',
        ...                                   start='1776-07-04',
        ...                                   end='2020-01-01')
        >>> values = np.linspace(df['00060_Mean'].min(),
        ...                      df['00060_Mean'].max(), 10000)
        >>> exceedance_probabilities = hyswap.exceedance.calculate_exceedance_probability_from_values_multiple(  # noqa
        ...     values, df['00060_Mean'])
        >>> ax = hyswap.plots.plot_flow_duration_curve(
        ...     values, exceedance_probabilities,
        ...     title='Flow Duration Curve for USGS Site 06892350')
        >>> plt.tight_layout()
        >>> plt.show()
    """
    # Create axes if not provided
    if ax is None:
        _, ax = plt.subplots()
    # do plotting
    ax.plot(exceedance_probabilities*100, values, **kwargs)
    if (observations is not None) and (observation_probabilities is not None):
        ax.scatter(np.array(observation_probabilities)*100, observations,
                   **scatter_kwargs)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)
    # set log scales for x axis
    ax.set_yscale('log')
    # set limits for axes
    ax.set_xlim(0.1, 99.9)
    # set ticks for axes
    # always use same ticks for x-axis
    ax.set_xticks([0.1, 5, 10, 25, 50, 75, 90, 95, 99.9])
    ax.set_xticklabels([
        '0.1', '5', '10', '25', '50', '75', '90', '95', '99.9'])
    # get y-axis ticks and convert to comma-separated strings
    yticks = ax.get_yticks()
    # min value is 0.1
    # yticks = np.array([i for i in yticks if i >= 0.1])
    # get logs for min/max values rounded to next lowest/highest
    min_vals = np.log10(yticks[yticks <= np.min(values)])
    if len(min_vals) > 0:
        min_tick = min_vals[-1]
    else:
        min_tick = -1.0
    max_tick = np.log10(yticks[yticks >= np.max(values)][0])
    # set list of values using logs
    yticks = list(10**np.arange(min_tick, max_tick+1))
    yticklabels = [f'{int(y):,}' for y in yticks]
    ax.set_yticks(yticks, labels=yticklabels)
    ax.set_ylim(np.min(yticks), np.max(yticks))
    # add grid lines
    if grid:
        ax.grid(which='both', axis='both', alpha=0.5)
    # return the axes
    return ax


def plot_raster_hydrograph(df_formatted, ax=None,
                           title='Raster Hydrograph',
                           xlab='Month', ylab='Year',
                           cbarlab='Discharge, ft3/s',
                           **kwargs):
    """Plot a raster hydrograph.

    Raster hydrographs are pixel-based plots for visualizing and identifying
    variations and changes in large multidimensional data sets. Originally
    developed by Keim (2000), they were first applied in hydrology by
    Koehler (2004) as a means of highlighting inter-annual and intra-annual
    changes in streamflow. The raster hydrographs in hyswap, like those
    developed by Koehler, depict years on the y-axis and days along the
    x-axis. Users can choose to plot streamflow (actual values or log values),
    streamflow percentile, or streamflow class (from 1, for low flow, to 7
    for high flow), for Daily, 7-Day, 14-Day, and 28-Day streamflow. For a
    more comprehensive description of raster hydrographs, see Strandhagen
    et al. (2006).

    References:
    Keim, D.A. 2000. Designing pixel-oriented visualization techniques:
    theory and applications. IEEE Transactions on Visualization and
    Computer Graphics, 6(1), 59-78.

    Koehler, R. 2004. Raster Based Analysis and Visualization of Hydrologic
    Time Series. Ph.D  dissertation, University of Arizona. Tucson, AZ, 189 p.

    `Strandhagen, E., Marcus, W.A., and Meacham, J.E. 2006. Views of the
    rivers: representing streamflow of the greater Yellowstone ecosystem.
    Cartographic Perspectives, no. 55, 54-29.`__

    Parameters
    ----------
    df_formatted : pandas.DataFrame
        Formatted dataframe containing the raster hydrograph data.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If not provided, a new figure and axes will be
        created.
    title : str, optional
        Title for the plot. If not provided, the default title will be
        'Streamflow Raster Hydrograph'.
    xlab : str, optional
        Label for the x-axis. If not provided, the default label will be
        'Month'.
    ylab : str, optional
        Label for the y-axis. If not provided, the default label will be
        'Year'.
    cbarlab : str, optional
        Label for the colorbar. If not provided, the default label will be
        'Discharge, ft3/s'.
    **kwargs
        Keyword arguments passed to :meth:`matplotlib.axes.Axes.imshow`.

    Returns
    -------
    matplotlib.axes.Axes
        Axes object containing the plot.

    Examples
    --------
    Fetch some data from NWIS, format it for a raster hydrograph plot and then
    make the raster hydrograph plot.

    .. plot::
        :include-source:

        >>> df, _ = dataretrieval.nwis.get_dv(site='09380000',
        ...                                   parameterCd='00060',
        ...                                   start='1960-01-01',
        ...                                   end='1970-12-31')
        >>> df_rh = hyswap.rasterhydrograph.format_data(df, '00060_Mean')
        >>> fig, ax = plt.subplots(figsize=(6, 6))
        >>> ax = hyswap.plots.plot_raster_hydrograph(
        ...     df_rh, ax=ax, title='Raster Hydrograph for USGS Site 09380000')
        >>> plt.tight_layout()
        >>> plt.show()
    """
    # Create axes if not provided
    if ax is None:
        _, ax = plt.subplots()
    # define min/max values
    min_10 = np.nanmax(
        [np.floor(np.log10(np.nanmin(df_formatted.to_numpy()))), 0]
    )
    max_10 = np.ceil(np.log10(np.nanmax(df_formatted.to_numpy())))
    # pop some kwargs
    cmap = kwargs.pop('cmap', 'YlGnBu')
    aspect = kwargs.pop('aspect', 'auto')
    interpolation = kwargs.pop('interpolation', 'none')
    vmin = kwargs.pop('vmin', int(10**min_10))
    vmax = kwargs.pop('vmax', int(10**max_10))
    norm = kwargs.pop('norm', matplotlib.colors.LogNorm(vmin=vmin, vmax=vmax))
    # do plotting
    img = ax.imshow(df_formatted, aspect=aspect, cmap=cmap,
                    interpolation=interpolation, norm=norm, **kwargs)
    # set labels
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)
    # add colorbar
    cbar = plt.colorbar(img, ax=ax)
    # set colorbar ticks
    cticks = cbar.ax.get_yticks()
    cbar.ax.set_yticks(cticks[1:-1],
                       labels=[f'{int(v):,}' for v in cticks[1:-1]])
    # set colorbar label
    cbar.set_label(cbarlab)
    # cbar height to be same as axes
    cbar.ax.set_aspect('auto')
    # set yticks
    ax.set_yticks(np.arange(-0.5, len(df_formatted.index)), [], minor=True)
    ax.set_yticks(np.arange(len(df_formatted.index)), df_formatted.index)
    # figure out how many labels to show - for example; every 4th label
    # dividing the number of y values by 20 seems to give a good multiple
    # for this plot size
    show_label_multiple = len(ax.get_yaxis().get_ticklabels()) // 20
    # if there were less than 20 labels, you don't need to hide any
    # if there are more, hide all the extra labels so they don't overlap
    if show_label_multiple > 0:
        for i, label in enumerate(ax.get_yaxis().get_ticklabels()):
            if i % show_label_multiple != 0:
                label.set_visible(False)
    # set xticks at start/end of each month
    xvals = df_formatted.columns.values
    months = [int(i.split('-')[0]) for i in xvals]
    month_transitions = np.where(np.diff(months) != 0)[0]
    ax.set_xticks([0] + list(month_transitions),
                  labels=[], minor=False)
    # set xticklabels to be month name at middle of each month
    unique_months = []
    [unique_months.append(x) for x in months if x not in unique_months]
    month_names = [calendar.month_abbr[i] for i in unique_months]
    month_names = [f'{m}' for m in month_names]
    days = [int(i.split('-')[1]) for i in xvals]
    midway_pts = np.where(np.array(days) == 15)[0]
    ax.set_xticks(midway_pts, labels=month_names, minor=True)
    # make minor ticks invisible
    ax.tick_params(which='minor', length=0)
    # return axes
    return ax


def plot_duration_hydrograph(percentiles_by_day, df, data_col,
                             date_column_name=None,
                             pct_list=[5, 10, 25, 75, 90, 95],
                             data_label=None, ax=None,
                             disclaimer=False,
                             title="Duration Hydrograph",
                             ylab="Discharge, ft3/s",
                             xlab="Month-Year", colors=None, **kwargs):
    """Plot a duration hydrograph.

    The duration hydrograph is a graphical presentation of recent daily
    streamflow (discharge) observed at an individual USGS streamgage,
    plotted over the long-term statistics of streamflow for each day of
    the year at that station. Typically, the statistics (based on quality
    assured and approved data) include the maximum discharge recorded during
    the period of record for each day of the year; the 90th percentile flow
    for each day; the interquartile range (75th percentile on top and 25th
    percentile on the bottom); the 10th percentile flow for each day; and the
    minimum discharge recorded for each day. This function, however, allows
    the user to plot a custom list of percentiles.

    Note: For some streams, flow statistics may have been computed from
    mixed regulated and unregulated flows; this can affect depictions
    of flow conditions.

    Parameters
    ----------
    percentiles_by_day : pandas.DataFrame
        Dataframe containing the percentiles by month-day.
        Note that this plotting function is incompatible
        with percentiles calculated by day-of-year.
    df : pandas.DataFrame
        Dataframe containing the data to plot.
    data_col : str
        Column name of the data to plot.
    date_column_name : str, optional
        Defaults to None. If None, index is assumed to contain datetime
        information.
    pct_list : list, optional
        List of integers corresponding to the percentile values to be
        plotted. Values of 0 and 100 are ignored as unbiased plotting position
        formulas do not assign values to 0 or 100th percentile.
        Defaults to 5, 10, 25, 75, 90, 95.
    data_label : str, optional
        Label for the data to plot. If not provided, a default label will
        be used.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If not provided, a new figure and axes will be
        created.
    disclaimer : bool, optional
        If True, displays the disclaimer 'For some streams, flow
        statistics may have been computed from mixed regulated
        and unregulated flows; this can affect depictions of flow
        conditions.' below the x-axis.
    title : str, optional
        Title for the plot. If not provided, the default title will be
        'Duration Hydrograph'.
    ylab : str, optional
        Label for the y-axis. If not provided, the default label will be
        'Discharge, ft3/s'.
    xlab : str, optional
        Label for the x-axis. If not provided, the default label will be
        'Month'.
    colors : list, optional
        List of colors to use for the lines. If not provided, a default
        list of colors will be used. The max number of colors in this
        list is seven.
    **kwargs
        Keyword arguments passed to :meth:`matplotlib.axes.Axes.fill_between`.

    Returns
    -------
    matplotlib.axes.Axes
        Axes object containing the plot.

    Examples
    --------
    Fetch some data from NWIS and make a streamflow duration hydrograph plot.

    .. plot::
        :include-source:

        >>> df, _ = dataretrieval.nwis.get_dv(site='06892350',
        ...                                   parameterCd='00060',
        ...                                   start='1900-01-01',
        ...                                   end='2022-12-31')
        >>> pct_by_day = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(  # noqa: E501
        ...     df, '00060_Mean')
        >>> df_2022 = df[df.index.year == 2022]
        >>> fig, ax = plt.subplots(figsize=(12, 6))
        >>> ax = hyswap.plots.plot_duration_hydrograph(
        ...     pct_by_day, df_2022, '00060_Mean',
        ...     data_label='2022 Daily Mean Discharge',
        ...     ax=ax, title='Duration Hydrograph for USGS Site 06892350')
        >>> plt.tight_layout()
        >>> plt.show()
    """
    # check that pct_list is present in percentile threshold data
    if all(pct in pct_list + ['min', 'max'] for pct in percentiles_by_day.columns):  # noqa: E501
        raise ValueError('one or more percent values are not in provided' +
                         'percentile threshold data')
    # ignore 0 and 100 percentile levels if provided in pct_list
    if 0 in pct_list:
        pct_list.remove(0)
    if 100 in pct_list:
        pct_list.remove(100)

    # Create axes if not provided
    if ax is None:
        _, ax = plt.subplots()
    # pop some kwargs
    alpha = kwargs.pop('alpha', 0.5)
    zorder = kwargs.pop('zorder', -20)
    if data_label is None:
        label = df[data_col].name
    else:
        label = data_label
    # Add disclaimer if True
    if disclaimer is True:
        txt = 'For some streams, flow statistics may have been computed from mixed \nregulated and unregulated flows; this can affect depictions of flow conditions.'  # noqa: E501
    else:
        txt = ''
    # get colors
    if colors is None:
        colors = ["#e37676", "#e8c285", "#dbf595", "#a1cc9f",
                  "#7bdbd2", "#7587bf", "#ad63ba"]
    # set the df index
    if date_column_name is not None:
        df = df.set_index(date_column_name)
    df['month_day'] = df.index.strftime('%m-%d')
    # Join percentiles with data
    df_combined = pd.merge(df, percentiles_by_day, left_on=df['month_day'], right_index=True, how='left')  # noqa: E501
    # plot the latest data -1 to 0-index day of year
    ax.plot(df_combined.index.values, df[data_col], color='k', zorder=10, label=label)  # noqa: E501
    # sort the list in ascending order
    pct_list.sort()
    # plot the historic percentiles filling between each pair
    ax.fill_between(
            df_combined.index.values,
            df_combined['min'].tolist(),
            df_combined['p' + str(pct_list[0]).zfill(2)].tolist(),
            color=colors[0],
            alpha=alpha,
            linewidth=0,
            label="Min. - {}th Percentile".format(pct_list[0]),
            zorder=zorder
        )
    for i in range(1, len(pct_list)):
        ax.fill_between(
            df_combined.index.values,
            df_combined['p' + str(pct_list[i-1]).zfill(2)].tolist(),
            df_combined['p' + str(pct_list[i]).zfill(2)].tolist(),
            color=colors[i],
            alpha=alpha,
            linewidth=0,
            label="{}th - {}th Percentile".format(
                pct_list[i - 1], pct_list[i]),
            zorder=zorder
        )
    ax.fill_between(
        df_combined.index.values,
        df_combined['p' + str(pct_list[-1]).zfill(2)].tolist(),
        df_combined['max'].tolist(),
        color=colors[-1],
        alpha=alpha,
        linewidth=0,
        label="{}th Percentile - Max.".format(pct_list[-1]),
        zorder=zorder
    )
    # set labels
    ax.set_xlabel(xlab)
    ax.set_xlim(df_combined.index.min(), df_combined.index.max())
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b-%Y'))  # noqa: E501
    plt.xticks(ha='left')
    # other labels
    ax.set_ylabel(ylab)
    ax.set_yscale("log")
    ax.set_title(title)
    # disclaimer
    ax.text(0, -0.18, txt, color='red', transform=ax.transAxes)
    # get y-axis ticks and convert to comma-separated strings
    yticks = ax.get_yticks()
    yticklabels = [f'{float(y):,}' for y in yticks]
    ax.set_yticks(yticks[1:-1], labels=yticklabels[1:-1])
    # two column legend
    ax.legend(loc="best", ncol=2, title='Historical percentiles')
    # return axes
    return ax


def plot_cumulative_hydrograph(df,
                               target_years,
                               data_column_name,
                               date_column_name=None,
                               year_type='calendar',
                               unit='acre-feet',
                               envelope_pct=[25, 75],
                               max_year=False, min_year=False,
                               ax=None,
                               disclaimer=False,
                               title="Cumulative Streamflow Hydrograph",
                               ylab="Cumulative discharge, acre-feet",
                               xlab="Month",
                               clip_leap_day=False,
                               **kwargs):
    """Plot a cumulative hydrograph.

    The cumulative-streamflow hydrograph is a graphical presentation of
    recent cumulative daily streamflow (discharge) observed at an
    individual USGS streamgage, plotted over the long-term statistics
    of streamflow for each day of the year at that station. Typically,
    the statistics, based on quality assured and approved data, include
    the maximum annual cumulative discharge recorded during the period
    of record; the mean-daily cumulative flow for each day; the minimum
    cumulative discharge recorded for each day.

    Note: For some streams, flow statistics may have been computed from
    mixed regulated and unregulated flows; this can affect depictions
    of flow conditions.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe containing the data to plot.
    target_years : int, or list
        Target year(s) to plot in black as the line. Can provide a single year
        as an integer, or a list of years.
    data_column_name : str
        Name of column containing data to calculate cumulative values for.
        Discharge data assumed to be in unit of ft3/s.
    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` will be used.
    unit : str, optional
        The unit the user wants to use to report cumulative flow. One of
        'acre-feet', 'cfs', 'cubic-meters', 'cubic-feet'. Assumes input
        data are in cubic feet per second (cfs).
    envelope_pct : list, optional
        List of percentiles to plot as the envelope. Default is [25, 75].
        If an empty list, [], then no envelope is plotted.
    max_year : bool, optional
        If True, plot the cumulative flow for the year with the maximum
        end of the year cumulative value as a dashed line. Default is False.
    min_year : bool, optional
        If True, plot the cumulative flow for the year with the minimum
        end of the year cumulative value as a dashed line. Default is False.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If not provided, a new figure and axes will be
        created.
    disclaimer : bool, optional
        If True, displays the disclaimer 'For some streams, flow
        statistics may have been computed from mixed regulated
        and unregulated flows; this can affect depictions of flow
        conditions.' below the x-axis.
    title : str, optional
        Title for the plot. If not provided, the default title will be
        'Cumulative Streamflow Hydrograph'.
    ylab : str, optional
        Label for the y-axis. If not provided, the default label will be
        'Cumulative Streamflow, ft3/s'.
    xlab : str, optional
        Label for the x-axis. If not provided, the default label will be
        'Month'.
    clip_leap_day : bool, optional
        If True, removes leap day '02-29' from the percentiles dataset
        used to create the plot. Defaults to False.
    **kwargs
        Keyword arguments passed to :meth:`matplotlib.axes.Axes.fill_between`.

    Returns
    -------
    matplotlib.axes.Axes
        Axes object containing the plot.

    Examples
    --------
    Fetch some data from NWIS and make a cumulative hydrograph plot.

    .. plot::
        :include-source:

        >>> df, _ = dataretrieval.nwis.get_dv(site='06892350',
        ...                                   parameterCd='00060',
        ...                                   start='1900-01-01',
        ...                                   end='2021-12-31')
        >>> fig, ax = plt.subplots(figsize=(8, 5))
        >>> ax = hyswap.plots.plot_cumulative_hydrograph(
        ...     df,
        ...     data_column_name='00060_Mean',
        ...     target_years=2020, ax=ax,
        ...     title='2020 Cumulative Streamflow Hydrograph, site 06892350')
        >>> plt.tight_layout()
        >>> plt.show()
    """
    # Create axes if not provided
    if ax is None:
        _, ax = plt.subplots()
    # calculate cumulative values
    cumulative_df = calculate_daily_cumulative_values(
        df=df,
        data_column_name=data_column_name,
        date_column_name=date_column_name,
        year_type=year_type,
        unit=unit,
        clip_leap_day=clip_leap_day
        )
    # calculations for percentiles by day
    pdf = calculate_variable_percentile_thresholds_by_day(
        cumulative_df, data_column_name='cumulative',
        clip_leap_day=clip_leap_day,
        percentiles=envelope_pct)
    # pop some kwargs
    alpha = kwargs.pop('alpha', 0.5)
    zorder = kwargs.pop('zorder', -20)
    color = kwargs.pop('color', 'xkcd:bright green')
    # Add disclaimer if True
    if disclaimer is True:
        txt = 'For some streams, flow statistics may have been computed from mixed \nregulated and unregulated flows; this can affect depictions of flow conditions.'  # noqa: E501
    else:
        txt = ''
    # Incorporate leap year decision into x-axis labels
    if clip_leap_day:
        year = 1901
    else:
        year = 1904
    # Create x-axis scale and labels
    if year_type == 'water':
        month_day_order = pd.date_range(start=f'{year-1}-10-01', end=f'{year}-09-30').strftime('%m-%d')  # noqa: E501
        month_begin_ticks = [f"{str(month).zfill(2)}-01" for month in range(10, 13)] + [f"{str(month).zfill(2)}-01" for month in range(1, 10)]  # noqa: E501
        month_label_ticks = [f"{str(month).zfill(2)}-15" for month in range(10, 13)] + [f"{str(month).zfill(2)}-15" for month in range(1, 10)]  # noqa: E501
        month_labels = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']  # noqa: E501
    elif year_type == 'climate':
        month_day_order = pd.date_range(start=f'{year-1}-04-01', end=f'{year}-03-31').strftime('%m-%d')  # noqa: E501
        month_begin_ticks = [f"{str(month).zfill(2)}-01" for month in range(4, 13)] + [f"{str(month).zfill(2)}-01" for month in range(1, 4)]  # noqa: E501
        month_label_ticks = [f"{str(month).zfill(2)}-15" for month in range(4, 13)] + [f"{str(month).zfill(2)}-15" for month in range(1, 4)]  # noqa: E501
        month_labels = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']  # noqa: E501
    else:
        month_day_order = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31').strftime('%m-%d')  # noqa: E501
        month_begin_ticks = [f"{str(month).zfill(2)}-01" for month in range(1, 13)]  # noqa: E501
        month_label_ticks = [f"{str(month).zfill(2)}-15" for month in range(1, 13)]  # noqa: E501
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']  # noqa: E501
    # Reorder percentile thresholds by year_type
    pdf_reordered = pdf.reindex(month_day_order)
    # plot percentile envelope
    if len(envelope_pct) == 2:
        ax.fill_between(pdf_reordered.index,
                        list(pdf_reordered["p" + str(envelope_pct[0]).zfill(2)].values),  # noqa: E501
                        list(pdf_reordered["p" + str(envelope_pct[1]).zfill(2)].values),  # noqa: E501
                        color=color, alpha=alpha,
                        label=f"{envelope_pct[0]}th - {envelope_pct[1]}th " +
                        "Percentile Envelope",
                        zorder=zorder)
    # plot min/max if desired
    if max_year:
        max_y = cumulative_df.loc[
            cumulative_df['cumulative'].idxmax()]['index_year']
        max_year_df = cumulative_df[
            cumulative_df['index_year'] == max_y]
        ax.plot(
            max_year_df['index_month_day'],
            max_year_df['cumulative'], color='k',
            alpha=0.5, linestyle='--',
            label=f"Highest observed cumulative flow ({max_y})"
            )
    if min_year:
        min_y = cumulative_df.loc[
            cumulative_df['cumulative'].idxmin()]['index_year']
        min_year_df = cumulative_df[
            cumulative_df['index_year'] == min_y]
        ax.plot(
            min_year_df['index_month_day'],
            min_year_df['cumulative'], color='k',
            alpha=0.5, linestyle=':',
            label=f"Lowest observed cumulative flow ({min_y})"
            )
    # handle target years
    col_targets = ['k'] + list(matplotlib.colormaps['tab20'].colors)
    if isinstance(target_years, int):
        target_years = [target_years]  # make int a list
    for i, target_year in enumerate(target_years):
        # get data from target year
        target_year_data = cumulative_df.loc[
            cumulative_df['index_year'] == target_year]
        # plot target year
        ax.plot(target_year_data['index_month_day'],
                target_year_data['cumulative'],
                color=col_targets[i],
                label=f"Observed cumulative flow ({target_year})")
    # Get axis labels and ticks in order
    ax.set_xlim(0, 365)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)
    plt.xticks(month_begin_ticks, labels='')
    ax.set_xticks(month_label_ticks, labels=month_labels, minor=True)
    # make minor x-ticks invisible
    ax.tick_params(axis='x', which='minor', length=0)
    # get y-axis ticks and convert to comma-separated strings
    yticks = ax.get_yticks()
    yticklabels = [f'{int(y):,}' for y in yticks]
    ax.set_yticks(yticks[1:], labels=yticklabels[1:])
    ax.set_ylim(0, yticks.max())
    # disclaimer
    ax.text(0, -0.18, txt, color='red', transform=ax.transAxes)
    # two column legend
    ax.legend(loc="best")
    # return
    return ax


def plot_hydrograph(df, data_col,
                    date_col=None,
                    start_date=None,
                    end_date=None,
                    ax=None,
                    title='Streamflow Hydrograph',
                    ylab='Discharge, ft3/s',
                    xlab='Date',
                    yscale='log',
                    **kwargs):
    """Plot a simple hydrograph.

    Hydrographs show the streamflow discharge over time at a single station.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the data to plot.

    data_col : str
        Name of the column containing the data to plot.

    date_col : str, optional
        Name of the column containing the dates. If not provided, the index
        will be used.

    start_date : str, optional
        Start date for the plot. If not provided, the minimum date in the
        DataFrame will be used.

    end_date : str, optional
        End date for the plot. If not provided, the maximum date in the
        DataFrame will be used.

    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If not provided, a new figure and axes will be
        created.

    title : str, optional
        Title of the plot. Default is 'Streamflow Hydrograph'.

    ylab : str, optional
        Y-axis label. Default is 'Streamflow, ft3/s'.

    xlab : str, optional
        X-axis label. Default is 'Date'.

    yscale : str, optional
        Y-axis scale. Default is 'log'. Options are 'linear' or 'log'.

    **kwargs
        Additional keyword arguments to pass to matplotlib.pyplot.plot().

    Returns
    -------
    matplotlib.axes.Axes
        Axes object containing the plot.

    Examples
    --------
    Fetch data for a USGS gage and plot the hydrograph.

    .. plot::
        :include-source:

        >>> siteno = '06892350'
        >>> df, _ = dataretrieval.nwis.get_dv(site=siteno,
        ...                                   parameterCd='00060',
        ...                                   start='2019-01-01',
        ...                                   end='2020-01-01')
        >>> ax = hyswap.plots.plot_hydrograph(
        ...     df, data_col='00060_Mean',
        ...     title=f'2019 Hydrograph for Station {siteno}',
        ...     ylab='Discharge, ft3/s',
        ...     xlab='Date', yscale='log')
        >>> plt.tight_layout()
        >>> plt.show()
    """
    # check if ax provided
    if ax is None:
        _, ax = plt.subplots()
    # check if date_col provided
    if date_col is not None:
        df = df.set_index(date_col)
    # sort by date
    df = df.sort_index()
    # check if start_date provided
    if start_date is not None:
        df = df.loc[start_date:]
    # check if end_date provided
    if end_date is not None:
        df = df.loc[:end_date]
    # plot
    ax.plot(df.index, df[data_col], **kwargs)
    # set labels
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)
    # set yscale
    ax.set_yscale(yscale)
    # get y-axis ticks and convert to comma-separated strings
    yticks = ax.get_yticks()
    yticklabels = [f'{int(y):,}' for y in yticks]
    ax.set_yticks(yticks[1:-1], labels=yticklabels[1:-1])
    # return
    return ax


def plot_similarity_heatmap(sim_matrix, n_obs=None, cmap='inferno',
                            show_values=False, ax=None,
                            title='Similarity Matrix'):
    """Plot a similarity matrix heatmap.

    The heatmap shows the results of a correlation matrix between
    measurements at two or more sites. Lighter, warmer colors denote
    higher similarity (correlation), while darker colors denote less
    similarity between two sites.

    Parameters
    ----------
    sim_matrix : pandas.DataFrame
        Similarity matrix to plot. Must be square. Can be the output of
        :meth:`hyswap.similarity.calculate_correlations`,
        :meth:`hyswap.similarity.calculate_wasserstein_distance`,
        :meth:`hyswap.similarity.calculate_energy_distance`, or any other
        square matrix represented as a pandas DataFrame.

    cmap : str, optional
        Colormap to use. Default is 'inferno'.

    show_values : bool, optional
        Whether to show the values of the matrix on the plot. Default is False.

    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If not provided, a new figure and axes will be
        created.

    title : str, optional
        Title for the plot. Default is 'Similarity Matrix'.

    Returns
    -------
    matplotlib.axes.Axes
        Axes object containing the plot.

    Examples
    --------
    Calculate the correlation matrix between two sites and plot it as a
    heatmap.

    .. plot::
        :include-source:

        >>> df, _ = dataretrieval.nwis.get_dv(site='06892350',
        ...                                   parameterCd='00060',
        ...                                   start='2010-01-01',
        ...                                   end='2021-12-31')
        >>> df2, _ = dataretrieval.nwis.get_dv(site='06892000',
        ...                                    parameterCd='00060',
        ...                                    start='2010-01-01',
        ...                                    end='2021-12-31')
        >>> corr_matrix, n_obs = hyswap.similarity.calculate_correlations(
        ...     [df, df2], '00060_Mean')
        >>> ax = hyswap.plots.plot_similarity_heatmap(corr_matrix,
        ...                                           show_values=True)
        >>> plt.show()
    """
    # Create axes if not provided
    if ax is None:
        _, ax = plt.subplots()
    # plot heatmap using matplotlib
    vmin = sim_matrix.min().min()
    vmax = sim_matrix.max().max()
    im = ax.imshow(sim_matrix, cmap=cmap,
                   vmin=sim_matrix.min().min(),
                   vmax=sim_matrix.max().max())
    # show values if desired
    if show_values:
        for i in range(sim_matrix.shape[0]):
            for j in range(sim_matrix.shape[1]):
                # if below halfway point, make text white
                if sim_matrix.iloc[i, j] < (vmax - vmin) / 2 + vmin:
                    ax.text(j, i, f'{sim_matrix.iloc[i, j]:.2f}',
                            ha="center", va="center", color="w")
                # otherwise, make text black
                else:
                    ax.text(j, i, f'{sim_matrix.iloc[i, j]:.2f}',
                            ha="center", va="center", color="k")
    # set labels
    if n_obs is not None:
        title = f'{title} (n={n_obs})'
    ax.set_title(title)
    ax.set_xlabel('Site')
    ax.set_ylabel('Site')
    # set ticks at center of each cell
    ax.set_xticks(np.arange(sim_matrix.shape[0]))
    ax.set_yticks(np.arange(sim_matrix.shape[1]))
    # set tick labels
    ax.set_xticklabels(sim_matrix.columns)
    ax.set_yticklabels(sim_matrix.index)
    plt.xticks(rotation=45, ha='right')
    # add colorbar
    plt.colorbar(im, ax=ax)
    # return
    return ax
