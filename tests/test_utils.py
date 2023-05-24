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


def test_filter_data_by_time():
    """Test the filter_data_by_time function."""
    # make a dataframe
    df = pd.DataFrame({
        'data': [1, 2, 3, 4],
        'date': pd.date_range('2019-01-01', '2019-01-04')})
    # test the function
    data = utils.filter_data_by_time(df, 1, 'data', date_column_name='date')
    assert data.shape == (1,)
    assert data.values == [1]
    # test the function with no date column and dates in the index
    df = df.set_index('date')
    data = utils.filter_data_by_time(df, 2, 'data')
    assert data.shape == (1,)
    assert data.values == [2]
    # test the filtering by month
    df = pd.DataFrame({
        'data': [1, 2, 3, 4],
        'date': pd.date_range('2019-01-01', '2019-05-01', freq='M')})
    data = utils.filter_data_by_time(df, 1, 'data', date_column_name='date',
                                     time_interval='month')
    assert data.shape == (1,)
    assert data.values == [1]
    # test the filtering by year
    df = pd.DataFrame({
        'data': [1, 2, 3, 4],
        'date': pd.date_range('2019-01-01', '2023-01-01', freq='Y')})
    data = utils.filter_data_by_time(df, 2019, 'data', date_column_name='date',
                                     time_interval='year')
    assert data.shape == (1,)
    assert data.values == [1]
    # test the windowing
    df = pd.DataFrame({
        'data': [1, 2, 3, 4],
        'date': pd.date_range('2019-01-01', '2019-01-04')})
    data = utils.filter_data_by_time(df, 2, 'data', date_column_name='date',
                                     leading_values=1)
    assert data.shape == (2,)
    assert np.all(data.values == [1, 2])
    # test tailing window
    data = utils.filter_data_by_time(df, 1, 'data', date_column_name='date',
                                     trailing_values=1)
    assert data.shape == (2,)
    assert np.all(data.values == [1, 2])
    # raise value error for invalid time interval
    with pytest.raises(ValueError):
        utils.filter_data_by_time(df, 1, 'data', date_column_name='date',
                                  time_interval='invalid')


def test_calculate_metadata():
    """Test the calculate_metadata function."""
    # make pandas series of data with datetime index
    data = pd.Series(
        [1, 2, 3, 4],
        index=pd.date_range('2019-01-01', '2023-01-01', freq='Y'))
    # calculate the metadata
    metadata = utils.calculate_metadata(data)
    # check the output
    assert metadata['start_date'] == '2019-12-31'
    assert metadata['end_date'] == '2022-12-31'
    assert metadata['n_years'] == 4
    assert metadata['n_data'] == 4
    assert metadata['n_nans'] == 0
    assert metadata['n_zeros'] == 0
    assert metadata['n_missing_years'] == 0
    assert metadata['n_lows'] == 0
    # remove the second value and recalculate the metadata
    data = data.drop(data.index[1])
    metadata = utils.calculate_metadata(data)
    # check the output
    assert metadata['start_date'] == '2019-12-31'
    assert metadata['end_date'] == '2022-12-31'
    assert metadata['n_years'] == 3
    assert metadata['n_data'] == 3
    assert metadata['n_nans'] == 0
    assert metadata['n_zeros'] == 0
    assert metadata['n_missing_years'] == 1
    assert metadata['n_lows'] == 0
    # make one value a nan and one a zero and recalculate the metadata
    data[0] = np.nan
    data[2] = 0
    metadata = utils.calculate_metadata(data)
    # check the output
    assert metadata['start_date'] == '2019-12-31'
    assert metadata['end_date'] == '2022-12-31'
    assert metadata['n_years'] == 3
    assert metadata['n_data'] == 2
    assert metadata['n_nans'] == 1
    assert metadata['n_zeros'] == 1
    assert metadata['n_missing_years'] == 1
    assert metadata['n_lows'] == 1


def test_adjust_doy_for_water_year():
    """Test the adjust_doy_for_water_year function."""
    # make dummy df
    df = pd.DataFrame({
        'data': np.arange(1, 366),
        'date': pd.date_range('2019-01-01', '2019-12-31')})
    # set date as index
    df = df.set_index('date')
    # set day of year as a column called day
    df['day'] = df.index.dayofyear
    # adjust the day of year for a water year
    df = utils.adjust_doy_for_water_year(df, 'day')
    # check the output, Jan 1 should be day 93
    assert df['day'].tolist()[0] == 93
    # check a leap year
    df = pd.DataFrame({
        'data': np.arange(1, 367),
        'date': pd.date_range('2020-01-01', '2020-12-31')})
    # set date as index
    df = df.set_index('date')
    # set day of year as a column called day
    df['day'] = df.index.dayofyear
    # adjust the day of year for a water year
    df = utils.adjust_doy_for_water_year(df, 'day')
    # check the output, Jan 1 should be day 93
    assert df['day'].tolist()[0] == 93


def test_adjust_doy_for_climate_year():
    """Test the adjust_doy_for_climate_year function."""
    # make dummy df
    df = pd.DataFrame({
        'data': np.arange(1, 366),
        'date': pd.date_range('2019-01-01', '2019-12-31')})
    # set date as index
    df = df.set_index('date')
    # set day of year as a column called day
    df['day'] = df.index.dayofyear
    # adjust the day of year for a water year
    df = utils.adjust_doy_for_climate_year(df, 'day')
    # check the output, Jan 1 should be day 276
    assert df['day'].tolist()[0] == 276
    # check a leap year
    df = pd.DataFrame({
        'data': np.arange(1, 367),
        'date': pd.date_range('2020-01-01', '2020-12-31')})
    # set date as index
    df = df.set_index('date')
    # set day of year as a column called day
    df['day'] = df.index.dayofyear
    # adjust the day of year for a water year
    df = utils.adjust_doy_for_climate_year(df, 'day')
    # check the output, Jan 1 should be day 276
    assert df['day'].tolist()[0] == 276
