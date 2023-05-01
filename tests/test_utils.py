"""Unit tests for the utils module."""
import pytest
import numpy as np
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


def test_rolling_average():
    """Test the rolling_average function."""
    # make a data frame with some dates and data
    df = pd.DataFrame(
        {"date": pd.date_range("2018-01-01", "2018-01-10"),
            "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
    # set date as index
    df.set_index("date", inplace=True)
    # calculate the rolling average
    df_out = utils.rolling_average(df, "data", "2D")
    # check the output
    assert df_out["data"].tolist() == [1.0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5,
                                       7.5, 8.5, 9.5]
    # check that the data column is in both dataframes
    assert "data" in df.columns
    assert "data" in df_out.columns
    # but check that the data are not equal
    assert df["data"].tolist() != df_out["data"].tolist()
    # try passing a kwarg to the rolling_average function
    df_out = utils.rolling_average(df, "data", "2D", center=True)
    assert df_out["data"].tolist() == [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5,
                                       8.5, 9.5, 10.0]
    # try passing a different kwarg
    df_out = utils.rolling_average(df, "data", "2D", min_periods=2)
    assert np.isnan(df_out["data"].tolist()[0])
    assert df_out['data'].tolist()[1:] == [1.5, 2.5, 3.5, 4.5, 5.5, 6.5,
                                           7.5, 8.5, 9.5]


def test_filter_data_by_day():
    """Test the filter_data_by_day function."""
    # make a dataframe
    df = pd.DataFrame({
        'data': [1, 2, 3, 4],
        'date': pd.date_range('2019-01-01', '2019-01-04')})
    # test the function
    data = utils.filter_data_by_day(df, 1, 'data', date_column_name='date')
    assert data.shape == (1,)
    assert data.values == [1]
    # test the function with no date column and dates in the index
    df = df.set_index('date')
    data = utils.filter_data_by_day(df, 2, 'data')
    assert data.shape == (1,)
    assert data.values == [2]
