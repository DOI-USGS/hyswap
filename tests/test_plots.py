"""Tests for the plotting functions."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hyswap import exceedance
from hyswap import rasterhydrograph
from hyswap import percentiles
from hyswap import plots
from hyswap import similarity


def test_plot_flow_duration_curve():
    """Test the plot_flow_duration_curve function."""
    values = [1, 1.25, 2.5]
    exceedance_probabilities = exceedance.calculate_exceedance_probability_from_values_multiple(  # noqa: E501
        values, [1, 2, 3, 4])
    ax = plots.plot_flow_duration_curve(values, exceedance_probabilities)
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Exceedance Probability\n' + \
        '(Percentage of time indicated value was equaled or exceeded)'
    assert ax.get_ylabel() == 'Discharge, ft3/s'
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
    ax = plots.plot_duration_hydrograph(pct, df, 'data')
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Month-Year'
    assert ax.get_ylabel() == 'Discharge, ft3/s'
    assert ax.get_title() == 'Duration Hydrograph'
    # make one with custom labels
    ax = plots.plot_duration_hydrograph(pct, df, 'data',
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
    # apply plot function
    ax = plots.plot_cumulative_hydrograph(df,
                                          data_column_name='data',
                                          date_column_name='date',
                                          target_years=2010)
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Month'
    assert ax.get_ylabel() == 'Cumulative discharge, acre-feet'
    assert ax.get_title() == 'Cumulative Streamflow Hydrograph'
    assert len(ax.lines) == 1
    # make one with custom labels
    ax = plots.plot_cumulative_hydrograph(df,
                                          data_column_name='data',
                                          date_column_name='date',
                                          target_years=2010,
                                          title='Test Title',
                                          xlab='Test X Label',
                                          ylab='Test Y Label')
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Test X Label'
    assert ax.get_ylabel() == 'Test Y Label'
    assert ax.get_title() == 'Test Title'
    assert len(ax.lines) == 1
    # make one with min/max lines plotted
    ax = plots.plot_cumulative_hydrograph(df,
                                          data_column_name='data',
                                          date_column_name='date',
                                          target_years=2010,
                                          max_year=True, min_year=True)
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Month'
    assert ax.get_ylabel() == 'Cumulative discharge, acre-feet'
    assert ax.get_title() == 'Cumulative Streamflow Hydrograph'
    assert len(ax.lines) == 3
    assert len(ax.collections) == 1
    # make one with multiple years of data plotted
    _date = pd.date_range('1/1/2010', '12/31/2012')
    df = pd.DataFrame({'date': _date,
                       'data': np.random.rand(len(_date))})
    ax = plots.plot_cumulative_hydrograph(df,
                                          data_column_name='data',
                                          date_column_name='date',
                                          target_years=[2010, 2011],
                                          max_year=True, min_year=True)
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Month'
    assert ax.get_ylabel() == 'Cumulative discharge, acre-feet'
    assert ax.get_title() == 'Cumulative Streamflow Hydrograph'
    assert len(ax.lines) == 4  # min/max, 2010 and 2011 lines
    assert len(ax.collections) == 1
    # close plot
    plt.close()


def test_plot_hydrograph():
    """Test the plot_hydrograph function."""
    # make some data
    df = pd.DataFrame({'date': pd.date_range('1/1/2010', '12/31/2010'),
                       'data': np.random.rand(365)})
    # apply plot function
    ax = plots.plot_hydrograph(df, 'data', 'date',
                               start_date='2/1/2010', end_date='10/30/2010')
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Date'
    assert ax.get_ylabel() == 'Discharge, ft3/s'
    assert ax.get_title() == 'Streamflow Hydrograph'
    assert len(ax.lines) == 1
    # close plot
    plt.close()


def test_plot_similarity_heatmat():
    """Testing the plot_similarity_heatmap function."""
    # make dummy dataframes
    df_1 = pd.DataFrame({
        'data': np.arange(10),
        'date': pd.date_range('2020-01-01', '2020-01-10')})
    df_1.set_index('date', inplace=True)
    df_2 = pd.DataFrame({
        'data': np.arange(10),
        'date': pd.date_range('2020-01-06', '2020-01-15')})
    df_2.set_index('date', inplace=True)
    # calculate similarity matrix (using correlation)
    df_corr, n_obs = similarity.calculate_correlations(
        [df_1, df_2], 'data')
    # plot
    ax = plots.plot_similarity_heatmap(df_corr, n_obs=n_obs,
                                       show_values=True,
                                       title='Test Title')
    # assertions
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Site'
    assert ax.get_ylabel() == 'Site'
    assert ax.get_title() == 'Test Title (n=5)'
    assert len(ax.lines) == 0
    # close plot
    plt.close()

    # make a set with negative values
    df_2 = pd.DataFrame({
        'data': np.random.random(10) * 10,
        'date': pd.date_range('2020-01-06', '2020-01-15')})
    df_2.set_index('date', inplace=True)
    # calculate similarity matrix (using correlation)
    df_corr, n_obs = similarity.calculate_correlations(
        [df_1, df_2], 'data')
    # plot
    ax = plots.plot_similarity_heatmap(df_corr, n_obs=n_obs,
                                       show_values=True,
                                       title='Test Title')
    # assertions
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == 'Site'
    assert ax.get_ylabel() == 'Site'
    assert ax.get_title() == 'Test Title (n=5)'
    assert len(ax.lines) == 0
    # close plot
    plt.close()
