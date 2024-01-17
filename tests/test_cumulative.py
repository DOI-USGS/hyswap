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


class TestDailyCumulativeValues:

    def test_calculate_daily_cumulative_values(self):
        """Test the calculate_daily_cumulative_values function."""
        # make a dataframe
        df = pd.DataFrame({
            'data': np.arange(1, 366),
            'date': pd.date_range('2019-01-01', '2019-12-31')})
        # test the function
        cdf = cumulative.calculate_daily_cumulative_values(
            df, 'data', date_column_name='date')
        assert cdf.shape == (365, 4)
        assert cdf.columns.tolist() == \
            ['index_month_day', 'index_year', 'index_doy', 'cumulative']
        assert cdf.index.year.unique().tolist() == [2019]
        assert cdf['index_doy'].tolist() == list(range(1, 366))
        assert cdf['cumulative'].tolist() == \
            list(np.cumsum(range(1, 366)) * 0.0000229568 * 86400)

    def test_calculate_daily_cumulative_values_no_date_col(self):
        # make a dataframe
        df = pd.DataFrame({
            'data': np.arange(1, 366),
            'date': pd.date_range('2019-01-01', '2019-12-31')})
        # test the function with no date column and dates in the index
        df = df.set_index('date')
        cdf = cumulative.calculate_daily_cumulative_values(df, 'data')
        assert cdf.shape == (365, 4)
        assert cdf.columns.tolist() == \
            ['index_month_day', 'index_year', 'index_doy', 'cumulative']
        assert cdf.index.year.unique().tolist() == [2019]
        assert cdf['index_doy'].tolist() == list(range(1, 366))
        assert cdf['cumulative'].tolist() == \
            list(np.cumsum(range(1, 366)) * 0.0000229568 * 86400)

    def test_calculate_daily_cumulative_values_water_year(self):
        # try for a water year
        df = pd.DataFrame({
            'data': np.ones(len(pd.date_range('2016-10-01', '2019-09-30'))),
            'date': pd.date_range('2016-10-01', '2019-09-30')})
        cdf = cumulative.calculate_daily_cumulative_values(
            df, 'data', date_column_name='date', year_type='water')
        assert cdf.shape == (365*3, 4)
        assert cdf.columns.tolist() == \
            ['index_month_day', 'index_year', 'index_doy', 'cumulative']
        assert cdf.index.year.unique().tolist() == [2016, 2017, 2018, 2019]
        assert cdf['index_year'].unique().tolist() == [2017, 2018, 2019]
        assert cdf['index_doy'].tolist()[0] == 1
        d_list = cdf['index_doy'].unique().tolist()
        d_list.sort()
        assert d_list == list(range(1, 366))
        assert cdf['cumulative'].tolist()[:365] == \
            list(np.cumsum(np.ones(365)) * 0.0000229568 * 86400)

    def test_calculate_daily_cumulative_values_climate_year(self):
        # try for a climate year
        df = pd.DataFrame({
            'data': np.ones(len(pd.date_range('2016-04-01', '2019-03-31'))),
            'date': pd.date_range('2016-04-01', '2019-03-31')})
        cdf = cumulative.calculate_daily_cumulative_values(
            df, 'data', date_column_name='date', year_type='climate')
        assert cdf.shape == (365*3, 4)
        assert cdf.columns.tolist() == \
            ['index_month_day', 'index_year', 'index_doy', 'cumulative']
        assert cdf.index.year.unique().tolist() == [2016, 2017, 2018, 2019]
        assert cdf['index_year'].unique().tolist() == [2017, 2018, 2019]
        assert cdf['index_doy'].tolist()[0] == 1
        d_list = cdf['index_doy'].unique().tolist()
        d_list.sort()
        assert d_list == list(range(1, 366))
        assert cdf['cumulative'].tolist()[:365] == \
            list(np.cumsum(np.ones(365)) * 0.0000229568 * 86400)

    def test_calculate_daily_cumulative_values_cfs(self):
        # make a dataframe
        df = pd.DataFrame({
            'data': np.arange(1, 366),
            'date': pd.date_range('2019-01-01', '2019-12-31')})
        # test the function
        cdf = cumulative.calculate_daily_cumulative_values(
            df, 'data', date_column_name='date', unit='cfs')
        assert cdf['cumulative'].tolist()[:365] == \
            list(np.cumsum(range(1, 366)))

    def test_calculate_daily_cumulative_values_cubic_feet(self):
        # make a dataframe
        df = pd.DataFrame({
            'data': np.arange(1, 366),
            'date': pd.date_range('2019-01-01', '2019-12-31')})
        # test the function
        cdf = cumulative.calculate_daily_cumulative_values(
            df, 'data', date_column_name='date', unit='cubic-feet')
        assert cdf['cumulative'].tolist()[:365] == \
            list(np.cumsum(range(1, 366)) * 86400)

    def test_calculate_daily_cumulative_values_cubic_meters(self):
        # make a dataframe
        df = pd.DataFrame({
            'data': np.arange(1, 366),
            'date': pd.date_range('2019-01-01', '2019-12-31')})
        # test the function
        cdf = cumulative.calculate_daily_cumulative_values(
            df, 'data', date_column_name='date', unit='cubic-meters')
        assert cdf['cumulative'].tolist()[:365] == \
            list(np.cumsum(range(1, 366)) * 0.02831685 * 86400)
