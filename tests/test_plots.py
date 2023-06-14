"""Tests for the plotting functions."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hyswap import exceedance
from hyswap import cumulative
from hyswap import rasterhydrograph
from hyswap import percentiles
from hyswap import plots


def test_plot_flow_duration_curve():
    """Test the plot_flow_duration_curve function."""
    values = [1, 1.25, 2.5]
    exceedance_probabilities = exceedance.calculate_exceedance_probability_from_values_multiple(  # noqa: E501
        values, [1, 2, 3, 4])
    ax = plots.plot_flow_duration_curve(values, exceedance_probabilities)
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Exceedance Probability\n' + \
        '(Percentage of time indicated value was equaled or exceeded)'
    assert ax.get_ylabel() == 'Discharge, in Cubic Feet per Second'
    assert ax.get_title() == 'Flow Duration Curve'
    assert len(ax.lines) == 1
    assert len(ax.collections) == 0
    assert len(ax.patches) == 0
    assert len(ax.texts) == 0
    assert len(ax.artists) == 0
    assert len(ax.images) == 0
    assert len(ax.containers) == 0
    assert len(ax.tables) == 0
    assert len(ax.spines) == 4
    # make another axes plot with different labels etc.
    ax = plots.plot_flow_duration_curve(values, exceedance_probabilities,
                                        title='Test Title',
                                        xlab='Test X Label',
                                        ylab='Test Y Label')
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Test X Label'
    assert ax.get_ylabel() == 'Test Y Label'
    assert ax.get_title() == 'Test Title'
    assert len(ax.lines) == 1
    assert len(ax.collections) == 0
    # make another plot with observations on it
    ax = plots.plot_flow_duration_curve(values, exceedance_probabilities,
                                        observations=[1, 2],
                                        observation_probabilities=[0.5, 0.25],
                                        title='Test Title',
                                        xlab='Test X Label',
                                        ylab='Test Y Label',
                                        scatter_kwargs={'c': 'k'})
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Test X Label'
    assert ax.get_ylabel() == 'Test Y Label'
    assert ax.get_title() == 'Test Title'
    assert len(ax.lines) == 1
    assert len(ax.collections) == 1
    # close plot
    plt.close()


def test_plot_raster_hydrograph():
    """Test the plot_raster_hydrograph function."""
    df = pd.DataFrame({'date': pd.date_range('1/1/2010', '12/31/2010'),
                       'data': np.random.rand(365)+100})
    df_formatted = rasterhydrograph.format_data(df, 'data', 'date')
    ax = plots.plot_raster_hydrograph(df_formatted)
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Month'
    assert ax.get_ylabel() == 'Year'
    assert ax.get_title() == 'Raster Hydrograph'
    # make one with custom labels
    ax = plots.plot_raster_hydrograph(df_formatted, title='Test Title',
                                      xlab='Test X Label',
                                      ylab='Test Y Label')
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Test X Label'
    assert ax.get_ylabel() == 'Test Y Label'
    assert ax.get_title() == 'Test Title'
    # close plot
    plt.close()


def test_plot_duration_hydrograph():
    """Test the plot_duration_hydrograph function."""
    df = pd.DataFrame({'date': pd.date_range('1/1/2010', '12/31/2012'),
                       'data': np.random.rand(1096)})
    df.index = df['date']
    pct = percentiles.calculate_variable_percentile_thresholds_by_day(
        df, 'data')
    df['doy'] = df.index.dayofyear
    ax = plots.plot_duration_hydrograph(pct, df, 'data', 'doy')
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Month'
    assert ax.get_ylabel() == 'Discharge, in Cubic Feet per Second'
    assert ax.get_title() == 'Duration Hydrograph'
    # make one with custom labels
    ax = plots.plot_duration_hydrograph(pct, df, 'data', 'doy',
                                        title='Test Title',
                                        xlab='Test X Label',
                                        ylab='Test Y Label',
                                        data_label='Test Data Label')
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Test X Label'
    assert ax.get_ylabel() == 'Test Y Label'
    assert ax.get_title() == 'Test Title'
    # close plot
    plt.close()


def test_plot_cumulative_hydrograph():
    """Test the plot_cumulative_hydrograph function."""
    df = pd.DataFrame({'date': pd.date_range('1/1/2010', '12/31/2010'),
                       'data': np.random.rand(365)})
    df_cumulative = cumulative.calculate_daily_cumulative_values(
        df, 'data', date_column_name='date')
    # apply plot function
    ax = plots.plot_cumulative_hydrograph(df_cumulative, 2010)
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Month'
    assert ax.get_ylabel() == 'Cumulative Streamflow, in Cubic Feet'
    assert ax.get_title() == 'Cumulative Streamflow Hydrograph'
    assert len(ax.lines) == 1
    # make one with custom labels
    ax = plots.plot_cumulative_hydrograph(df_cumulative, 2010,
                                          title='Test Title',
                                          xlab='Test X Label',
                                          ylab='Test Y Label')
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Test X Label'
    assert ax.get_ylabel() == 'Test Y Label'
    assert ax.get_title() == 'Test Title'
    assert len(ax.lines) == 1
    # make one with min/max lines plotted
    ax = plots.plot_cumulative_hydrograph(df_cumulative, 2010,
                                          max_pct=True, min_pct=True)
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Month'
    assert ax.get_ylabel() == 'Cumulative Streamflow, in Cubic Feet'
    assert ax.get_title() == 'Cumulative Streamflow Hydrograph'
    assert len(ax.lines) == 3
    assert len(ax.collections) == 1
    # make one with multiple years of data plotted
    _date = pd.date_range('1/1/2010', '12/31/2012')
    df = pd.DataFrame({'date': _date,
                       'data': np.random.rand(len(_date))})
    df_cumulative = cumulative.calculate_daily_cumulative_values(
        df, 'data', date_column_name='date')
    ax = plots.plot_cumulative_hydrograph(df_cumulative, [2010, 2011],
                                          max_pct=True, min_pct=True)
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Month'
    assert ax.get_ylabel() == 'Cumulative Streamflow, in Cubic Feet'
    assert ax.get_title() == 'Cumulative Streamflow Hydrograph'
    assert len(ax.lines) == 4  # min/max, 2010 and 2011 lines
    assert len(ax.collections) == 1
    # close plot
    plt.close()
