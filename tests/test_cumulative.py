"""Tests for the cumulative functions."""

import numpy as np
import pandas as pd
import pytest
from hyswap import cumulative


def test_tidy_cumulative_dataframe():
    """Test the _tidy_cumulative_dataframe function."""
    # make a dataframe
    cdf = pd.DataFrame(
        index=np.arange(2000, 2003),
        columns=np.arange(1, 367),
        data=np.arange(1, 1099).reshape(3, 366))
    # test the function
    cdf = cumulative._tidy_cumulative_dataframe(cdf)
    assert cdf.shape == (1098, 3)
    assert cdf.columns.tolist() == ['year', 'day', 'cumulative']
    assert cdf.index.year.unique().tolist() == [2000, 2001, 2002, 2003]
    assert cdf['day'].tolist() == list(range(1, 367)) * 3
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
    assert cdf.columns.tolist() == ['year', 'day', 'cumulative']
    assert cdf.index.year.unique().tolist() == [2019]
    assert cdf['day'].tolist() == list(range(1, 366))
    assert cdf['cumulative'].tolist() == list(np.cumsum(range(1, 366)))
    # test the function with no date column and dates in the index
    df = df.set_index('date')
    cdf = cumulative.calculate_daily_cumulative_values(df, 'data')
    assert cdf.shape == (365, 3)
    assert cdf.columns.tolist() == ['year', 'day', 'cumulative']
    assert cdf.index.year.unique().tolist() == [2019]
    assert cdf['day'].tolist() == list(range(1, 366))
    assert cdf['cumulative'].tolist() == list(np.cumsum(range(1, 366)))