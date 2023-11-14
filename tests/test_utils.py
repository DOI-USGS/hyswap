"""Unit tests for the utils module."""
import pytest
import numpy as np
import pandas as pd
from hyswap import utils


class TestDataFilters:
    def test_filter_approved_data(self):
        """Test the filter_approved_data function."""
        data = {"a": ["A", "A", "P", "P"], "b": [1, 2, 3, 4]}
        data_df = pd.DataFrame(data)
        df = utils.filter_approved_data(data_df, filter_column="a")
        assert df["b"].tolist() == [1, 2]

    def test_filter_approved_data_error(self):
        """Test the filter_approved_data function."""
        data = {"a": ["A", "A", "P", "P"], "b": [1, 2, 3, 4]}
        data_df = pd.DataFrame(data)
        with pytest.raises(ValueError):
            utils.filter_approved_data(data_df, filter_column=None)


class TestRollingAverage:
    def test_rolling_average(self):
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

    def test_rolling_average_kwarg_01(self):
        # make a data frame with some dates and data
        df = pd.DataFrame(
            {"date": pd.date_range("2018-01-01", "2018-01-10"),
                "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        # set date as index
        df.set_index("date", inplace=True)
        # try passing a kwarg to the rolling_average function
        df_out = utils.rolling_average(df, "data", "2D", center=True)
        assert df_out["data"].tolist() == [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5,
                                           8.5, 9.5, 10.0]

    def test_rolling_average_kwarg_02(self):
        # make a data frame with some dates and data
        df = pd.DataFrame(
            {"date": pd.date_range("2018-01-01", "2018-01-10"),
                "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        # set date as index
        df.set_index("date", inplace=True)
        # try passing a different kwarg
        df_out = utils.rolling_average(df, "data", "2D", min_periods=2)
        assert np.isnan(df_out["data"].tolist()[0])
        assert df_out['data'].tolist()[1:] == [1.5, 2.5, 3.5, 4.5, 5.5, 6.5,
                                               7.5, 8.5, 9.5]


class TestFilterTime:
    def test_filter_data_by_time(self):
        """Test the filter_data_by_time function."""
        # make a dataframe
        df = pd.DataFrame({
            'data': [1, 2, 3, 4],
            'date': pd.date_range('2019-01-01', '2019-01-04')})
        # test the function
        data = utils.filter_data_by_time(df, 1, 'data',
                                         date_column_name='date')
        assert data.shape == (1,)
        assert data.values == [1]

    def test_filter_no_date(self):
        # make a dataframe
        df = pd.DataFrame({
            'data': [1, 2, 3, 4],
            'date': pd.date_range('2019-01-01', '2019-01-04')})
        # test the function with no date column and dates in the index
        df = df.set_index('date')
        data = utils.filter_data_by_time(df, 2, 'data')
        assert data.shape == (1,)
        assert data.values == [2]

    def test_filter_by_month(self):
        # test the filtering by month
        df = pd.DataFrame({
            'data': [1, 2, 3, 4],
            'date': pd.date_range('2019-01-01', '2019-05-01', freq='M')})
        data = utils.filter_data_by_time(df, 1, 'data',
                                         date_column_name='date',
                                         time_interval='month')
        assert data.shape == (1,)
        assert data.values == [1]

    def test_filter_by_year(self):
        # test the filtering by year
        df = pd.DataFrame({
            'data': [1, 2, 3, 4],
            'date': pd.date_range('2019-01-01', '2023-01-01', freq='Y')})
        data = utils.filter_data_by_time(df, 2019, 'data',
                                         date_column_name='date',
                                         time_interval='year')
        assert data.shape == (1,)
        assert data.values == [1]

    def test_filter_windowing(self):
        # test the windowing
        df = pd.DataFrame({
            'data': [1, 2, 3, 4],
            'date': pd.date_range('2019-01-01', '2019-01-04')})
        data = utils.filter_data_by_time(df, 2, 'data',
                                         date_column_name='date',
                                         leading_values=1)
        assert data.shape == (2,)
        assert np.all(data.values == [1, 2])

    def test_filter_tailing_window(self):
        # test tailing window
        df = pd.DataFrame({
            'data': [1, 2, 3, 4],
            'date': pd.date_range('2019-01-01', '2019-01-04')})
        data = utils.filter_data_by_time(df, 1, 'data',
                                         date_column_name='date',
                                         trailing_values=1)
        assert data.shape == (2,)
        assert np.all(data.values == [1, 2])

    def test_filter_error(self):
        df = pd.DataFrame({
            'data': [1, 2, 3, 4],
            'date': pd.date_range('2019-01-01', '2019-01-04')})
        # raise value error for invalid time interval
        with pytest.raises(ValueError):
            utils.filter_data_by_time(df, 1, 'data', date_column_name='date',
                                      time_interval='invalid')

    def test_filter_drop_na(self):
        # test ability to drop nans
        df = pd.DataFrame({
            'data': [1, 2, np.nan, 4],
            'date': pd.date_range('2019-01-01', '2019-01-04')})
        # test the function
        data = utils.filter_data_by_time(df, 1, 'data',
                                         date_column_name='date',
                                         time_interval='month',
                                         drop_na=False)
        data_no_nan = utils.filter_data_by_time(
            df, 1, 'data', date_column_name='date',
            time_interval='month', drop_na=True)
        # assertions
        assert np.isnan(data.values).sum() == 1
        assert np.isnan(data_no_nan.values).sum() == 0
        assert data.shape == (4,)
        assert data_no_nan.shape == (3,)


class TestMetadata:
    def test_calculate_metadata_01(self):
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

    def test_calculate_metadata_02(self):
        """Test the calculate_metadata function."""
        # make pandas series of data with datetime index
        data = pd.Series(
            [1, 2, 3, 4],
            index=pd.date_range('2019-01-01', '2023-01-01', freq='Y'))
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

    def test_calculate_metadata_03(self):
        """Test the calculate_metadata function."""
        # make pandas series of data with datetime index
        data = pd.Series(
            [1, 2, 3, 4],
            index=pd.date_range('2019-01-01', '2023-01-01', freq='Y'))
        # remove the second value
        data = data.drop(data.index[1])
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


class TestDefiningColumns:
    def test_define_year_doy_columns(self):
        """Test the define_year_doy_columns function."""
        # make dummy df
        df = pd.DataFrame({
            'data': np.arange(1, 366),
            'date': pd.date_range('2019-01-01', '2019-12-31')})
        # apply function
        df = utils.define_year_doy_columns(df, date_column_name='date')
        assert df['index_year'].tolist() == [2019] * 365
        assert df['index_doy'].tolist() == list(range(1, 366))
        assert df.index.dayofyear.tolist() == list(range(1, 366))

    def test_define_year_doy_columns_water_year(self):
        # make dummy df
        df = pd.DataFrame({
            'data': np.arange(1, 366),
            'date': pd.date_range('2019-01-01', '2019-12-31')})
        # test with a different year type
        df = utils.define_year_doy_columns(df, date_column_name='date',
                                           year_type='water')
        assert df.index.year.unique().tolist() == [2019]
        assert df['index_year'].unique().tolist() == [2019, 2020]
        assert df['index_doy'].tolist() == list(range(93, 366)) + \
            list(range(1, 93))

    def test_define_year_doy_columns_climate_year(self):
        # make dummy df
        df = pd.DataFrame({
            'data': np.arange(1, 366),
            'date': pd.date_range('2019-01-01', '2019-12-31')})
        # test with climate year
        df = utils.define_year_doy_columns(df, date_column_name='date',
                                           year_type='climate')
        assert df.index.year.unique().tolist() == [2019]
        assert df['index_year'].unique().tolist() == [2019, 2020]
        assert df['index_doy'].tolist() == list(range(276, 366)) + \
            list(range(1, 276))

    def test_define_year_doy_columns_leap_year(self):
        # test with leap year
        df = pd.DataFrame({
            'data': np.arange(1, 367),
            'date': pd.date_range('2020-01-01', '2020-12-31')})
        df = utils.define_year_doy_columns(df, date_column_name='date',
                                           clip_leap_day=False)
        assert df.index.year.unique().tolist() == [2020]
        assert df['index_year'].unique().tolist() == [2020]
        assert df['index_doy'].tolist() == list(range(1, 367))
        assert len(df['index_doy']) == 366

    def test_define_year_doy_columns_leap_clip(self):
        # test with leap year and clip leap day
        df = pd.DataFrame({
            'data': np.arange(1, 367),
            'date': pd.date_range('2020-01-01', '2020-12-31')})
        df = utils.define_year_doy_columns(df, date_column_name='date',
                                           clip_leap_day=True)
        assert df.index.year.unique().tolist() == [2020]
        assert df['index_year'].unique().tolist() == [2020]
        assert df['index_doy'].tolist() == list(range(1, 366))
        assert len(df['index_doy']) == 365

    def test_define_year_doy_columns_water_year_clip(self):
        # water year leap with clip
        df = pd.DataFrame({
            'data': np.arange(1, 367),
            'date': pd.date_range('2020-01-01', '2020-12-31')})
        df = utils.define_year_doy_columns(df, date_column_name='date',
                                           year_type='water',
                                           clip_leap_day=True)
        assert df.index.year.unique().tolist() == [2020]
        assert df['index_year'].unique().tolist() == [2020, 2021]
        assert df['index_doy'].tolist() == list(range(93, 366)) + \
            list(range(1, 93))
        assert len(df['index_doy']) == 365

    def test_define_year_doy_columns_climate_year_clip(self):
        # climate year leap with clip
        df = pd.DataFrame({
            'data': np.arange(1, 367),
            'date': pd.date_range('2020-01-01', '2020-12-31')})
        df = utils.define_year_doy_columns(df, date_column_name='date',
                                           year_type='climate',
                                           clip_leap_day=True)
        assert df.index.year.unique().tolist() == [2020]
        assert df['index_year'].unique().tolist() == [2020, 2021]
        assert df['index_doy'].tolist() == list(range(276, 366)) + \
            list(range(1, 276))
        assert len(df['index_doy']) == 365


class TestMungingNWISStats:
    def test_munge_nwis_stats(self):
        """Test the munge_nwis_stats function."""
        # make a dataframe
        df = pd.DataFrame({
            'month_nu': [1, 2, 3, 4],
            'day_nu': [1, 2, 3, 4],
            'end_yr': [2019, 2019, 2019, 2019],
            'min_va': [1, 2, 3, 4],
            'max_va': [5, 6, 7, 8],
            'mean_va': [9, 10, 11, 12],
            'p05_va': [13, 14, 15, 16],
            'p10_va': [17, 18, 19, 20],
            'p25_va': [21, 22, 23, 24],
            'p50_va': [25, 26, 27, 28],
            'p75_va': [29, 30, 31, 32],
            'p90_va': [33, 34, 35, 36],
            'p95_va': [37, 38, 39, 40],
        })
        # apply the function
        df_slim = utils.munge_nwis_stats(df)
        # check the output
        assert df_slim.shape == (4, 8)
        assert len(df.columns) > len(df_slim.columns)
        assert 0 in df_slim.columns
        assert df_slim.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]

    def test_munge_additional_params(self):
        # make a dataframe
        df = pd.DataFrame({
            'month_nu': [1, 2, 3, 4],
            'day_nu': [1, 2, 3, 4],
            'end_yr': [2019, 2019, 2019, 2019],
            'min_va': [1, 2, 3, 4],
            'max_va': [5, 6, 7, 8],
            'mean_va': [9, 10, 11, 12],
            'p05_va': [13, 14, 15, 16],
            'p10_va': [17, 18, 19, 20],
            'p25_va': [21, 22, 23, 24],
            'p50_va': [25, 26, 27, 28],
            'p75_va': [29, 30, 31, 32],
            'p90_va': [33, 34, 35, 36],
            'p95_va': [37, 38, 39, 40],
        })
        # function w/ additional parameters
        df_slim = utils.munge_nwis_stats(df, ['min_va', 'max_va'], [0, 100])
        assert df_slim.shape == (4, 2)
        assert df_slim.columns.tolist() == [0, 100]
        assert len(df.columns) > len(df_slim.columns)

    def test_munge_raise_error(self):
        # make a dataframe
        df = pd.DataFrame({
            'month_nu': [1, 2, 3, 4],
            'day_nu': [1, 2, 3, 4],
            'end_yr': [2019, 2019, 2019, 2019],
            'min_va': [1, 2, 3, 4],
            'max_va': [5, 6, 7, 8],
            'mean_va': [9, 10, 11, 12],
            'p05_va': [13, 14, 15, 16],
            'p10_va': [17, 18, 19, 20],
            'p25_va': [21, 22, 23, 24],
            'p50_va': [25, 26, 27, 28],
            'p75_va': [29, 30, 31, 32],
            'p90_va': [33, 34, 35, 36],
            'p95_va': [37, 38, 39, 40],
        })
        # raise error if column lists are of different lengths
        with pytest.raises(ValueError):
            utils.munge_nwis_stats(df, ['min_va', 'max_va'], [0, 100, 200])

    def test_munge_specify_water_year(self):
        # make a dataframe
        df = pd.DataFrame({
            'month_nu': [1, 2, 3, 4],
            'day_nu': [1, 2, 3, 4],
            'end_yr': [2019, 2019, 2019, 2019],
            'min_va': [1, 2, 3, 4],
            'max_va': [5, 6, 7, 8],
            'mean_va': [9, 10, 11, 12],
            'p05_va': [13, 14, 15, 16],
            'p10_va': [17, 18, 19, 20],
            'p25_va': [21, 22, 23, 24],
            'p50_va': [25, 26, 27, 28],
            'p75_va': [29, 30, 31, 32],
            'p90_va': [33, 34, 35, 36],
            'p95_va': [37, 38, 39, 40],
        })
        # specify year type
        df_slim = utils.munge_nwis_stats(df, year_type='water')
        assert df_slim.shape == (4, 8)
        assert len(df.columns) > len(df_slim.columns)
        assert 0 in df_slim.columns
        assert df_slim.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]

    def test_munge_specify_climate_year(self):
        # make a dataframe
        df = pd.DataFrame({
            'month_nu': [1, 2, 3, 4],
            'day_nu': [1, 2, 3, 4],
            'end_yr': [2019, 2019, 2019, 2019],
            'min_va': [1, 2, 3, 4],
            'max_va': [5, 6, 7, 8],
            'mean_va': [9, 10, 11, 12],
            'p05_va': [13, 14, 15, 16],
            'p10_va': [17, 18, 19, 20],
            'p25_va': [21, 22, 23, 24],
            'p50_va': [25, 26, 27, 28],
            'p75_va': [29, 30, 31, 32],
            'p90_va': [33, 34, 35, 36],
            'p95_va': [37, 38, 39, 40],
        })
        # check with climate year
        df_slim = utils.munge_nwis_stats(df, year_type='climate')
        assert df_slim.shape == (4, 8)
        assert len(df.columns) > len(df_slim.columns)
        assert 0 in df_slim.columns
        assert df_slim.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]


def test_filter_to_common_time():
    """Test the filter_to_common_time function."""
    # make dummy dataframes
    df_1 = pd.DataFrame({
        'data': np.arange(10),
        'date': pd.date_range('2020-01-01', '2020-01-10')})
    df_1.set_index('date', inplace=True)
    df_2 = pd.DataFrame({
        'data': np.arange(10),
        'date': pd.date_range('2020-01-06', '2020-01-15')})
    df_2.set_index('date', inplace=True)
    # apply the function
    df_list, n_obs = utils.filter_to_common_time([df_1, df_2])
    # check the output
    assert len(df_list) == 2
    assert n_obs == 5


def test_set_data_type():
    """Test the function set_data_type."""
    assert utils.set_data_type('daily') == 'D'
    assert utils.set_data_type('7-day') == '7D'
    assert utils.set_data_type('14-day') == '14D'
    assert utils.set_data_type('28-day') == '28D'


class TestSummaryStatistics:
    def test_calculate_summary_statistics(self):
        """Test the calculate_summary_statistics function."""
        # make test dataframe
        df = pd.DataFrame({
            'datetime': pd.date_range('2000-01-01', '2000-01-10'),
            '00060_Mean': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'site_no': np.ones(10) * 12345678
        })
        # set datetime as index
        df.set_index('datetime', inplace=True)
        # use function
        df_stats = utils.calculate_summary_statistics(df, '00060_Mean')
        # check output
        assert df_stats.shape == (8, 1)
        assert df_stats.columns[0] == 'Summary Statistics'
        assert df_stats.iloc[0, 0] == '12345678'
        assert df_stats.iloc[1, 0] == '2000-01-01'
        assert df_stats.iloc[2, 0] == '2000-01-10'
        assert df_stats.iloc[3, 0] == 10
        assert df_stats.iloc[4, 0] == 1
        assert df_stats.iloc[5, 0] == 5.5
        assert df_stats.iloc[6, 0] == 5.5
        assert df_stats.iloc[7, 0] == 10


class TestSetDataType:
    def test_set_data_type_daily(self):
        """Test the function set_data_type."""
        assert utils.set_data_type('daily') == 'D'

    def test_set_data_type_week(self):
        """Test the function set_data_type."""
        assert utils.set_data_type('7-day') == '7D'

    def test_set_data_type_two_week(self):
        """Test the function set_data_type."""
        assert utils.set_data_type('14-day') == '14D'

    def test_set_data_type_twenty_eight_day(self):
        """Test the function set_data_type."""
        assert utils.set_data_type('28-day') == '28D'


class TestCategorizationSchema:

    def test_retrieve_schema_exists(self):
        """Test the function retrieve_schema."""
        schema = utils.retrieve_schema('NWD')
        assert isinstance(schema, dict)
        assert 'ranges' in schema.keys()
        assert 'labels' in schema.keys()

    def test_retrieve_schema_missing(self):
        """Test the function retrieve_schema."""
        with pytest.raises(ValueError):
            utils.retrieve_schema('abcdef')

    def test_retrieve_schema_casesensitive(self):
        """Test the function retrieve_schema."""
        schema = utils.retrieve_schema('Nwd')
        assert isinstance(schema, dict)


class TestFlowCategorization:
    # define a basic categorization schema
    schema = {'ranges': [0, 25, 75, 100],
              'labels': ['Low', 'Med', 'High'],
              'low_label': 'Lowest',
              'high_label': 'Highest'}

    def test_flow_categorization(self):
        """Test the function flow_categorization."""
        # define a simple dataframe of flow percentiles
        df = pd.DataFrame({
            'datetime': pd.date_range('2000-01-01', '2000-01-06'),
            'est_pct': [10, 50, 74.999, 75, 75.0001, 90]})
        df.set_index('datetime', inplace=True)
        df = utils.categorize_flows(df, 'est_pct', custom_schema=self.schema)
        assert 'flow_cat' in df.columns
        assert df.iloc[0, -1] == 'Low'
        assert df.iloc[1, -1] == 'Med'
        assert df.iloc[2, -1] == 'Med'
        assert df.iloc[3, -1] == 'High'
        assert df.iloc[4, -1] == 'High'
        assert df.iloc[5, -1] == 'High'

    def test_flow_categorization_lowest_highest(self):
        """Test the function flow_categorization."""
        # define a simple dataframe of flow percentiles
        df = pd.DataFrame({
            'datetime': pd.date_range('2000-01-01', '2000-01-02'),
            'est_pct': [0, 100]})
        df.set_index('datetime', inplace=True)
        df = utils.categorize_flows(df, 'est_pct', custom_schema=self.schema)
        assert 'flow_cat' in df.columns
        assert df.iloc[0, -1] == 'Lowest'
        assert df.iloc[1, -1] == 'Highest'

    def test_flow_categorization_nan(self):
        """Test the function flow_categorization."""
        # define a simple dataframe of flow percentiles that are not valid
        df = pd.DataFrame({
            'datetime': pd.date_range('2000-01-01', '2000-01-03'),
            'est_pct': [-1, np.nan, 101]})
        df.set_index('datetime', inplace=True)
        df = utils.categorize_flows(df, 'est_pct', custom_schema=self.schema)
        assert df['flow_cat'].isnull().all()
