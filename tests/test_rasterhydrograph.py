"""Unit tests for the rasterhydrograph module."""
import pytest
import numpy as np
import pandas as pd
from hyswap import rasterhydrograph


def test_calculate_date_range():
    """Test the private function _calculate_date_range."""
    # define a data frame to use for testing
    dummy_dates = pd.date_range('2018-06-01', '2022-01-31')
    df = pd.DataFrame(
        {'date': dummy_dates, 'value': np.random.rand(len(dummy_dates)),
         'index_year': dummy_dates.year.tolist(),
         'month': dummy_dates.month.tolist(),
         'day': dummy_dates.day.tolist(),
         'index_doy': dummy_dates.dayofyear.tolist()}
        )
    df.set_index('date', inplace=True)
    # test the function with default values
    date_range = rasterhydrograph._calculate_date_range(df, 'calendar',
                                                        None, None)
    assert date_range[0].year == 2018
    assert date_range[0].month == 1
    assert date_range[0].day == 1
    assert date_range[-1].year == 2022
    assert date_range[-1].month == 12
    assert date_range[-1].day == 31
    # test the function specifying start and end years
    date_range = rasterhydrograph._calculate_date_range(df, 'calendar',
                                                        2019, 2020)
    assert date_range[0].year == 2019
    assert date_range[0].month == 1
    assert date_range[0].day == 1
    assert date_range[-1].year == 2020
    assert date_range[-1].month == 12
    assert date_range[-1].day == 31


def test_check_inputs():
    """Test the private function _check_inputs."""
    # make a df
    dummy_dates = pd.date_range('2018-06-01', '2022-01-31')
    df = pd.DataFrame(
        {'date': dummy_dates, 'value': np.random.rand(len(dummy_dates))}
        )
    df_date = df.set_index('date')
    # test the data frame input
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(None, None, None, None,
                                       None, None, None)
    # test the data column name input
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), None, None, 'daily',
                                       'calendar', None, None)
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 1, None, 'daily',
                                       'calendar', None, None)
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 1.0, None, 'daily',
                                       'calendar', None, None)

    # test the date column name input
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', {"a": 1},
                                       'daily', 'calendar', None, None)
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', 1, 'daily',
                                       'calendar', None, None)
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', 1.0, 'daily',
                                       'calendar', None, None)

    # test the data type input
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 1,
                                       None, None, None)
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 1.0,
                                       None, None, None)
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, None,
                                       None, None, None)
    with pytest.raises(ValueError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 'string',
                                       None, None, None)

    # test the year type input
    with pytest.raises(ValueError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 'daily',
                                       1, None, None)
    with pytest.raises(ValueError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 'daily',
                                       1.0, None, None)
    with pytest.raises(ValueError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 'daily',
                                       None, None, None)
    with pytest.raises(ValueError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 'daily',
                                       'string', None, None)

    # test the begin year input
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 'daily',
                                       'calendar', 1.0, None)
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 'daily',
                                       'calendar', 'string', None)
    with pytest.raises(ValueError):
        rasterhydrograph._check_inputs(df, 'data', 'date', 'daily',
                                       'calendar', 2000, None)
    with pytest.raises(ValueError):
        rasterhydrograph._check_inputs(df_date, 'data', None, 'daily',
                                       'calendar', 2000, None)

    # test the end year input
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 'daily',
                                       'calendar', None, 1.0)
    with pytest.raises(TypeError):
        rasterhydrograph._check_inputs(pd.DataFrame(), 'data', None, 'daily',
                                       'calendar', None, 'string')
    with pytest.raises(ValueError):
        rasterhydrograph._check_inputs(df, 'data', 'date', 'daily',
                                       'calendar', None, 3000)
    with pytest.raises(ValueError):
        rasterhydrograph._check_inputs(df_date, 'data', None, 'daily',
                                       'calendar', None, 3000)


def test_format_data():
    """Test the public function format_data."""
    # set up some data for the test
    dummy_dates = pd.date_range('2018-06-01', '2022-01-31')
    df = pd.DataFrame(
        {'date': dummy_dates, 'value': np.random.rand(len(dummy_dates))}
    )
    df_date = df.set_index('date')
    # test the function with a dataframe and a date column
    df_out = rasterhydrograph.format_data(df, 'value', 'date')
    assert len(df_out.index) == 5
    assert len(df_out.columns) == 365
    # assert day 1 of 2018 has no data, is NaN
    assert np.isnan(df_out.loc[2018][0])
    # assert day 350 of 2022 has no data, is NaN
    assert np.isnan(df_out.loc[2022][349])
    # test the function with a dataframe and a date index
    df_out = rasterhydrograph.format_data(df_date, 'value')
    assert len(df_out.index) == 5
    assert len(df_out.columns) == 365
    # assert day 1 of 2018 has no data, is NaN
    assert np.isnan(df_out.loc[2018][0])
    # assert day 350 of 2022 has no data, is NaN
    assert np.isnan(df_out.loc[2022][349])
    # test the function with a dataframe and a date index and beginning year
    df_out = rasterhydrograph.format_data(df_date, 'value', begin_year=2019)
    assert len(df_out.index) == 4
    assert len(df_out.columns) == 365
    # assert day 1 of 2019 has data, is not NaN
    assert ~np.isnan(df_out.loc[2019][0])
    # assert day 350 of 2022 has no data, is NaN
    assert np.isnan(df_out.loc[2022][349])
    # test the function with a dataframe and a date index and ending year
    df_out = rasterhydrograph.format_data(df_date, 'value', end_year=2021)
    assert len(df_out.index) == 4
    assert len(df_out.columns) == 365
    # assert day 1 of 2018 has no data, is NaN
    assert np.isnan(df_out.loc[2018][0])
    # assert day 350 of 2021 has data, is not NaN
    assert ~np.isnan(df_out.loc[2021][349])
    # test the function with a dataframe and a date index and a different
    # data averaging scheme
    df_7out = rasterhydrograph.format_data(df_date, 'value',
                                           data_type='7-day')
    assert len(df_7out.index) == 5
    assert len(df_7out.columns) == 365
    # assert day 1 of 2018 has no data, is NaN
    assert np.isnan(df_7out.loc[2018][0])
    # assert day 350 of 2022 has no data, is NaN
    assert np.isnan(df_7out.loc[2022][349])
    # check that there are non-NaN values in the data frame
    assert ~np.isnan(df_7out.values).all()
    # test the function with a dataframe and a date index and a water year
    df_out_water = rasterhydrograph.format_data(df_date, 'value',
                                                year_type='water')
    assert len(df_out_water.index) == 5
    assert len(df_out_water.columns) == 365
    # check that there are non-NaN values in the data frame
    assert ~np.isnan(df_out_water.values).all()
    # check that day 1 of year 2019 is 10/1/2018
    assert df_out_water.loc[2019][0] == df_out.loc[2018][273]
    # check that the last day of year 2020 is 9/30/2020
    assert df_out_water.loc[2020][364] == df_out.loc[2020][272]
    # test the function with a dataframe and a date index and a different
    # data averaging scheme and a water year
    df_7out_water = rasterhydrograph.format_data(df_date, 'value',
                                                 data_type='7-day',
                                                 year_type='water')
    assert len(df_7out_water.index) == 5
    assert len(df_7out_water.columns) == 365
    # check that there are non-NaN values in the data frame
    assert ~np.isnan(df_7out_water.values).all()
    # check that day 1 of year 2019 is 10/1/2018
    assert df_7out_water.loc[2019][0] == df_7out.loc[2018][273]
    # check that the last day of year 2020 is 9/30/2020
    assert df_7out_water.loc[2020][364] == df_7out.loc[2020][272]
    # test the function with a dataframe and a date index and in a
    # climate year
    df_out_climate = rasterhydrograph.format_data(df_date, 'value',
                                                  year_type='climate')
    assert len(df_out_climate.index) == 4
    assert len(df_out_climate.columns) == 365
    # check that there are non-NaN values in the data frame
    assert ~np.isnan(df_out_climate.values).all()
    # check that day 1 of year 2020 is 4/1/2019
    assert df_out_climate.loc[2020][0] == df_out.loc[2019][90]
    # check that the last day of year 2021 is 3/31/2021
    assert df_out_climate.loc[2021][364] == df_out.loc[2021][89]
    # test the function with a dataframe and a date index and a different
    # data averaging scheme via kwargs and a climate year
    df_7out_climate = rasterhydrograph.format_data(df_date, 'value',
                                                   data_type='7-day',
                                                   year_type='climate',
                                                   center=True)
    assert len(df_7out_climate.index) == 4
    assert len(df_7out_climate.columns) == 365
    # check that there are non-NaN values in the data frame
    assert ~np.isnan(df_7out_climate.values).all()
    # this is a different averaging method so the values will be different
    # set up some data starting earlier in the year
    dummy_dates = pd.date_range('2018-02-01', '2022-01-31')
    df = pd.DataFrame(
        {'date': dummy_dates, 'value': np.random.rand(len(dummy_dates))}
    )
    df_date = df.set_index('date')
    # test the function with a dataframe and a date index and in a
    # climate year
    df_out_climate = rasterhydrograph.format_data(df_date, 'value',
                                                  year_type='climate')
    assert len(df_out_climate.index) == 5
    assert len(df_out_climate.columns) == 365
    # check that there are non-NaN values in the data frame
    assert ~np.isnan(df_out_climate.values).all()
