"""Unit tests for the utils module."""
import pytest
import pandas as pd
from hyswap import utils


def test_filter_approved_data():
    """Test the filter_approved_data function."""
    data = {"a": ["A", "A", "P", "P"], "b": [1, 2, 3, 4]}
    data_df = pd.DataFrame(data)
    df = utils.filter_approved_data(data_df, filter_column="a")
    assert df["b"].tolist() == [1, 2]
    with pytest.raises(ValueError):
        utils.filter_approved_data(data_df, filter_column=None)


def test_filter_data_by_day():
    """Test the filter_data_by_day function."""
    # make a dataframe
    df = pd.DataFrame({
        'data': [1, 2, 3, 4],
        'date': pd.date_range('2019-01-01', '2019-01-04')})
    # test the function
    data = utils.filter_data_by_day(df, 1, 'data', date_column_name='date')
    assert data.shape == (1,)
    assert data == [1]
    # test the function with no date column and dates in the index
    df = df.set_index('date')
    data = utils.filter_data_by_day(df, 2, 'data')
    assert data.shape == (1,)
    assert data == [2]
