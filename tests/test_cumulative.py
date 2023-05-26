"""Tests for the cumulative functions."""

import numpy as np
import pandas as pd
from hyswap import cumulative


def test_tidy_cumulative_dataframe():
    """Test the _tidy_cumulative_dataframe function."""
    # make a dataframe
    cdf = pd.DataFrame(
        index=np.arange(2000, 2003),
        columns=np.arange(1, 367),
        data=np.arange(1, 1099).reshape(3, 366))
    # test the function
    cdf = cumulative._tidy_cumulative_dataframe(cdf, 'calendar')
    assert cdf.shape == (1098, 3)
    assert cdf.columns.tolist() == ['index_year', 'index_doy', 'cumulative']
    assert cdf.index.year.unique().tolist() == [2000, 2001, 2002, 2003]
    assert cdf['index_doy'].tolist() == list(range(1, 367)) * 3
    assert cdf['cumulative'].tolist() == list(range(1, 1099))


def test_calculate_daily_cumulative_values():
    """Test the calculate_daily_cumulative_values function."""
    # make a dataframe
    df = pd.DataFrame({
        'data': np.arange(1, 366),
        'date': pd.date_range('2019-01-01', '2019-12-31')})
    # test the function
    cdf = cumulative.calculate_daily_cumulative_values(
        df, 'data', date_column_name='date')
    assert cdf.shape == (365, 3)
    assert cdf.columns.tolist() == ['index_year', 'index_doy', 'cumulative']
    assert cdf.index.year.unique().tolist() == [2019]
    assert cdf['index_doy'].tolist() == list(range(1, 366))
    assert cdf['cumulative'].tolist() == list(np.cumsum(range(1, 366)))
    # test the function with no date column and dates in the index
    df = df.set_index('date')
    cdf = cumulative.calculate_daily_cumulative_values(df, 'data')
    assert cdf.shape == (365, 3)
    assert cdf.columns.tolist() == ['index_year', 'index_doy', 'cumulative']
    assert cdf.index.year.unique().tolist() == [2019]
    assert cdf['index_doy'].tolist() == list(range(1, 366))
    assert cdf['cumulative'].tolist() == list(np.cumsum(range(1, 366)))
    # try for a water year
    df = pd.DataFrame({
        'data': np.ones(len(pd.date_range('2016-01-01', '2019-12-31'))),
        'date': pd.date_range('2016-01-01', '2019-12-31')})
    cdf = cumulative.calculate_daily_cumulative_values(
        df, 'data', date_column_name='date', year_type='water')
    assert cdf.shape == (365*3, 3)
    assert cdf.columns.tolist() == ['index_year', 'index_doy', 'cumulative']
    assert cdf.index.year.unique().tolist() == [2017, 2018, 2019, 2020]
    assert cdf['index_doy'].tolist()[0] == 1
    d_list = cdf['index_doy'].unique().tolist()
    d_list.sort()
    assert d_list == list(range(1, 366))
    assert cdf['cumulative'].tolist()[:365] == list(np.cumsum(np.ones(365)))
    # try for a climate year
    cdf = cumulative.calculate_daily_cumulative_values(
        df, 'data', date_column_name='date', year_type='climate')
    assert cdf.shape == (365*3, 3)
    assert cdf.columns.tolist() == ['index_year', 'index_doy', 'cumulative']
    assert cdf.index.year.unique().tolist() == [2017, 2018, 2019, 2020]
    assert cdf['index_doy'].tolist()[0] == 1
    d_list = cdf['index_doy'].unique().tolist()
    d_list.sort()
    assert d_list == list(range(1, 366))
    assert cdf['cumulative'].tolist()[:365] == list(np.cumsum(np.ones(365)))
