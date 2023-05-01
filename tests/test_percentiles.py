"""Tests for the percentiles functions."""
import numpy as np
import pandas as pd
import pytest
from hyswap import percentiles


def test_calculate_historic_percentiles():
    """Test the calculate_historic_percentiles function."""
    # make some data
    data = np.arange(101)
    # test the function
    percentiles_ = percentiles.calculate_historic_percentiles(data,
                                                              method='linear')
    assert percentiles_.shape == (8,)
    assert percentiles_ == pytest.approx((0, 5, 10, 25, 75, 90, 95, 100))
    # set some percentile values as opposed to the defaults
    percentiles_ = percentiles.calculate_historic_percentiles(
        data, percentiles=np.array((0, 10, 50, 90, 100)), method='linear')
    assert percentiles_.shape == (5,)
    assert percentiles_ == pytest.approx((0, 10, 50, 90, 100))
    # pass kwarg through to np.percentile
    percentiles_ = percentiles.calculate_historic_percentiles(
        data, method='lower')
    assert percentiles_.shape == (8,)
    assert percentiles_ == pytest.approx((0, 5, 10, 25, 75, 90, 95, 100))


def test_calculate_percentiles_by_day():
    """Test the calculate_percentiles_by_day function."""
    # make a dataframe
    df = pd.DataFrame({
        'data': np.arange(101),
        'date': pd.date_range('2019-01-01', '2019-04-11')})
    # test the function
    percentiles_ = percentiles.calculate_percentiles_by_day(
        df, 'data', date_column_name='date')
    assert percentiles_.shape == (101, 8)
    assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
    assert percentiles_.index.tolist() == list(range(1, 102))
    # test the function with no date column and dates in the index
    df = df.set_index('date')
    percentiles_ = percentiles.calculate_percentiles_by_day(df, 'data')
    assert percentiles_.shape == (101, 8)
    assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
    assert percentiles_.index.tolist() == list(range(1, 102))
    # test the function with a different set of percentiles
    percentiles_ = percentiles.calculate_percentiles_by_day(
        df, 'data', percentiles=np.array((0, 10, 50, 90, 100)))
    assert percentiles_.shape == (101, 5)
    assert percentiles_.columns.tolist() == [0, 10, 50, 90, 100]
    assert percentiles_.index.tolist() == list(range(1, 102))
