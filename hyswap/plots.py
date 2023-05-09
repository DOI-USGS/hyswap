"""Functions to make plots."""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from hyswap.percentiles import calculate_percentiles_by_day


def plot_flow_duration_curve(values, exceedance_probabilities,
                             ax=None, title=None, ylab=None,
                             grid=True, **kwargs):
    """Make flow duration curve plot.

    Parameters
    ----------
    values : array-like
        Values to plot along y-axis.
    exceedance_probabilities : array-like
        Exceedance probabilities for each value, likely calculated from
        a function in :obj:`hyswap.stats.exceedance`.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If not provided, a new figure and axes will be
        created.
    title : str, optional
        Title for the plot. If not provided, a default title will be
        used.
    grid : bool, optional
        Whether to show grid lines on the plot. Default is True.
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
    ax.set_xlabel(
        'Exceedance Probability\n' +
        '(Percent of Time Indicated Discharge was Equaled or Exceeded)')
    if ylab is None:
        ax.set_ylabel('Discharge, ft$^3$/s')
    else:
        ax.set_ylabel(ylab)
    if title is None:
        ax.set_title('Flow Duration Curve')
    else:
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
    yticklabels = [f'{int(y):,}' for y in yticks]
    ax.set_yticklabels(yticklabels)
    # add grid lines
    if grid:
        ax.grid(which='both', axis='both', alpha=0.5)
    # return the axes
    return ax


def plot_raster_hydrograph(df_formatted, ax=None, title=None,
                           xlab=None, ylab=None, cbarlab=None,
                           **kwargs):
    """Make raster hydrograph plot.

    Parameters
    ----------
    df_formatted : pandas.DataFrame
        Formatted dataframe containing the raster hydrograph data.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If not provided, a new figure and axes will be
        created.
    title : str, optional
        Title for the plot. If not provided, a default title will be
        used.
    xlab : str, optional
        Label for the x-axis. If not provided, a default label will be
        used.
    ylab : str, optional
        Label for the y-axis. If not provided, a default label will be
        used.
    cbarlab : str, optional
        Label for the colorbar. If not provided, a default label will be
        used.
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
    # pop some kwargs
    cmap = kwargs.pop('cmap', 'YlGnBu')
    aspect = kwargs.pop('aspect', 'auto')
    interpolation = kwargs.pop('interpolation', 'none')
    norm = kwargs.pop('norm', matplotlib.colors.LogNorm())
    # do plotting
    img = ax.imshow(df_formatted, aspect=aspect, cmap=cmap,
                    interpolation=interpolation, norm=norm, **kwargs)
    # set labels
    if xlab is None:
        ax.set_xlabel('Day of Year')
    else:
        ax.set_xlabel(xlab)
    if ylab is None:
        ax.set_ylabel('Year')
    else:
        ax.set_ylabel(ylab)
    if title is None:
        ax.set_title('Streamflow Raster Hydrograph')
    else:
        ax.set_title(title)
    # add colorbar
    cbar = plt.colorbar(img, ax=ax)
    # set colorbar label
    if cbarlab is None:
        cbar.set_label('Streamflow, cubic feet per second')
    else:
        cbar.set_label(cbarlab)
    # cbar height to be same as axes
    cbar.ax.set_aspect('auto')
    # set ticks
    ax.set_yticks(np.arange(-0.5, len(df_formatted.index)), [], minor=True)
    ax.set_yticks(np.arange(len(df_formatted.index)), df_formatted.index)
    # return axes
    return ax


def plot_duration_hydrograph(percentiles_by_day, df, data_col, doy_col,
                             data_label=None, ax=None,
                             title=None, ylab=None, xlab=None,
                             colors=None, **kwargs):
    """Make duration hydrograph plot.

    Parameters
    ----------
    percentiles_by_day : pandas.DataFrame
        Dataframe containing the percentiles by day.
    df : pandas.DataFrame
        Dataframe containing the data to plot.
    data_col : str
        Column name of the data to plot.
    doy_col : str
        Column name of the day of year.
    data_label : str, optional
        Label for the data to plot. If not provided, a default label will
        be used.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If not provided, a new figure and axes will be
        created.
    title : str, optional
        Title for the plot. If not provided, a default title will be
        used.
    ylab : str, optional
        Label for the y-axis. If not provided, a default label will be
        used.
    xlab : str, optional
        Label for the x-axis. If not provided, a default label will be
        used.
    colors : list, optional
        List of colors to use for the lines. If not provided, a default
        list of colors will be used.
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
        >>> pct_by_day = hyswap.percentiles.calculate_percentiles_by_day(
        ...     df, '00060_Mean')
        >>> df_2022 = df[df.index.year == 2022]
        >>> df_2022['doy'] = df_2022.index.dayofyear
        >>> df_2022 = df_2022.sort_values(by='doy')
        >>> fig, ax = plt.subplots(figsize=(12, 6))
        >>> ax = hyswap.plots.plot_duration_hydrograph(
        ...     pct_by_day, df_2022, '00060_Mean', 'doy',
        ...     data_label='2022 Daily Mean Discharge',
        ...     ax=ax, title='Duration Hydrograph for USGS Site 06892350')
        >>> plt.tight_layout()
        >>> plt.show()
    """
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
    # get colors
    if colors is None:
        colors = ["#e37676", "#e8c285", "#dbf595", "#a1cc9f",
                  "#7bdbd2", "#7587bf", "#ad63ba"]
    # plot the latest data
    ax.plot(df[doy_col], df[data_col], color='k', zorder=10, label=label)
    # plot the historic percentiles filling between each pair
    pct_list = [0, 5, 10, 25, 75, 90, 95, 100]
    for i in range(1, len(pct_list)):
        ax.fill_between(
            percentiles_by_day.index,
            list(percentiles_by_day[pct_list[i - 1]].values),
            list(percentiles_by_day[pct_list[i]].values),
            color=colors[i - 1],
            alpha=alpha,
            label="{}th - {}th Percentile".format(
                pct_list[i - 1], pct_list[i]),
            zorder=zorder, **kwargs
        )
    # set labels
    if xlab is None:
        ax.set_xlabel("Day of Year")
    else:
        ax.set_xlabel(xlab)
    ax.set_xlim(1, 366)
    ax.set_xticks([1] + list(np.arange(30, 360, 30)) + [366])
    if ylab is None:
        ax.set_ylabel("Discharge (cfs)")
    else:
        ax.set_ylabel(ylab)
    ax.set_yscale("log")
    if title is None:
        ax.set_title("Percentiles of Discharge by Day of Year")
    else:
        ax.set_title(title)
    # two column legend
    ax.legend(loc="best", ncol=2)
    # return axes
    return ax


def plot_cumulative_hydrograph(cumulative_percentiles, target_year,
                               ax=None, title=None, ylab=None, xlab=None,
                               **kwargs):
    """Make cumulative hydrograph plot.

    Parameters
    ----------
    cumulative_percentiles : pandas.DataFrame
        Dataframe containing the cumulative percentiles per year, output
        from :obj:`hyswap.cumulative.calculate_daily_cumulative_values`.
    target_year : int
        Target year to plot in black as the line.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If not provided, a new figure and axes will be
        created.
    title : str, optional
        Title for the plot. If not provided, a default title will be
        used.
    ylab : str, optional
        Label for the y-axis. If not provided, a default label will be
        used.
    xlab : str, optional
        Label for the x-axis. If not provided, a default label will be
        used.
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
        >>> cdf = hyswap.cumulative.calculate_daily_cumulative_values(
        ...     df, '00060_Mean')
        >>> fig, ax = plt.subplots(figsize=(8, 5))
        >>> ax = hyswap.plots.plot_cumulative_hydrograph(
        ...     cdf, 2020, ax=ax,
        ...     title='2020 Cumulative Streamflow Hydrograph, site 06892350')
        >>> plt.tight_layout()
        >>> plt.show()
    """
    # Create axes if not provided
    if ax is None:
        _, ax = plt.subplots()
    # calculations for percentiles by day
    pdf = calculate_percentiles_by_day(cumulative_percentiles,
                                       data_column_name='cumulative',
                                       percentiles=[25, 75])
    # pop some kwargs
    alpha = kwargs.pop('alpha', 0.5)
    zorder = kwargs.pop('zorder', -20)
    color = kwargs.pop('color', 'xkcd:bright green')
    # plot 25-75 percentile envelope
    ax.fill_between(pdf.index, list(pdf[25].values), list(pdf[75].values),
                    color=color, alpha=alpha,
                    label="25th - 75th Percentile Envelope",
                    zorder=zorder, **kwargs)
    # get data from target year
    target_year_data = cumulative_percentiles.loc[
        cumulative_percentiles.index.year == target_year, 'cumulative']
    # plot target year
    ax.plot(target_year_data.index.dayofyear, target_year_data,
            color='k', label="{} Cumulative Discharge".format(target_year))
    # set labels
    if xlab is None:
        ax.set_xlabel("Day of Year")
    else:
        ax.set_xlabel(xlab)
    ax.set_xlim(1, 366)
    ax.set_xticks([1] + list(np.arange(30, 360, 30)) + [366])
    if ylab is None:
        ax.set_ylabel("Cumulative Discharge (cfs)")
    else:
        ax.set_ylabel(ylab)
    # title
    if title is None:
        ax.set_title("Cumulative Discharge by Day of Year")
    else:
        ax.set_title(title)
    # legend
    ax.legend(loc="upper left")
    # return
    return ax