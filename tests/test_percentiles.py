"""Tests for the percentiles functions."""
import numpy as np
import pandas as pd
import pytest
from hyswap import percentiles


class TestCalculateFixedPercentileThresholds:
    # datasets for all tests in this class
    data = pd.DataFrame({'values': np.arange(101),
                         'date': pd.date_range('2020-01-01', '2020-04-10')}).set_index('date')  # noqa: E501
    # data with NAs added
    data_w_na = data.copy()
    data_w_na.at['2019-12-31', 'values'] = np.nan
    data_w_na.at['2020-04-11', 'values'] = np.nan

    # data with all NAs
    data_all_na = data.copy()
    data_all_na['values'] = np.nan

    def test_calculate_fixed_percentile_thresholds_defaults(self):
        """Test the calculate_fixed_percentile_thresholds function defaults."""
        # test the function
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data, 'values', method='linear', ignore_na=False,
            include_metadata=False)
        assert percentiles_.shape == (1, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']
        assert percentiles_.values.tolist()[0] == [
            0.0, 5.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 100.0]

    def test_custom_percentiles(self):
        # set some percentile values as opposed to the defaults
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data, 'values', percentiles=np.array((10, 50, 90)),
            include_metadata=False)
        assert percentiles_.shape == (1, 5)
        assert percentiles_.columns.tolist() == ['min', 'p10', 'p50', 'p90',
                                                 'max']
        assert percentiles_.values.tolist()[0] == [
            0.0, 9.200000000000001, 50.0, 90.80000000000001, 100.0]

    def test_percentiles_not_allowed(self):
        # test that 0 and 100 percentiles are ignored
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data, 'values', percentiles=np.array((0, 10, 50, 90, 100)),
            include_metadata=False)
        assert percentiles_.shape == (1, 5)
        assert percentiles_.columns.tolist() == ['min', 'p10', 'p50', 'p90',
                                                 'max']
        assert percentiles_.values.tolist()[0] == [
            0.0, 9.200000000000001, 50.0, 90.80000000000001, 100.0]

    def test_kwargs_to_percentile(self):
        # pass kwarg through to np.percentile
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data, 'values', method='linear', include_metadata=False)
        assert percentiles_.shape == (1, 9)
        assert percentiles_.values.tolist()[0] == [
            0, 5, 10, 25, 50, 75, 90, 95, 100]

    def test_with_nans(self):
        # test with some nan values and ignoring NAs
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data_w_na, 'values',
            method='linear', ignore_na=True, include_metadata=False)
        assert percentiles_.shape == (1, 9)
        assert percentiles_.values.tolist()[0] == [
            0.0, 5.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 100.0]

    def test_with_nans_and_not_ignore_na(self):
        # test with some nan values and not ignoring NAs
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data_w_na, 'values',
            method='linear', ignore_na=False, include_metadata=False,
            include_min_max=False)
        assert percentiles_.shape == (1, 7)
        assert percentiles_.isna().all().all()

    def test_empty_df(self):
        # test with an dataframe with no valid values
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data_all_na, 'values',
            method='linear', ignore_na=True, include_metadata=False,
            include_min_max=False)
        assert percentiles_.shape == (1, 7)
        assert percentiles_.isna().all().all()

    def test_with_no_min_max(self):
        # set to not return min max values
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data, 'values', percentiles=np.array((5, 10, 50, 90, 95)),
            method='linear', include_metadata=False, include_min_max=False)
        assert percentiles_.shape == (1, 5)
        assert percentiles_.columns.tolist() == ['p05', 'p10', 'p50', 'p90',
                                                 'p95']
        assert percentiles_.values.tolist()[0] == [
            5.0, 10.0, 50.0, 90.0, 95.0]

    def test_masking_out_of_range_percentiles(self):
        # check that percentiles out of range of the dataset (due to size)
        # return NA values
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data.head(5), 'values',
            percentiles=np.array((1, 10, 50, 90, 99)),
            include_metadata=False, include_min_max=False)
        assert percentiles_.shape == (1, 5)
        assert percentiles_.columns.tolist() == ['p01', 'p10', 'p50', 'p90',
                                                 'p99']
        assert np.sum(np.isnan(percentiles_.values)) == 4
        assert percentiles_.values.tolist()[0][2] == 2.0

    def test_percentile_calcs_using_array(self):
        # test the function with input just as a 1-D array
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            np.arange(101), method='linear', ignore_na=False,
            include_metadata=False)
        assert percentiles_.shape == (1, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']
        assert percentiles_.values.tolist()[0] == [
            0.0, 5.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 100.0]

    def test_percentile_calcs_using_series(self):
        # test the function with input just as a series
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data['values'], method='linear', ignore_na=False,
            include_metadata=False)
        assert percentiles_.shape == (1, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']
        assert percentiles_.values.tolist()[0] == [
            0.0, 5.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 100.0]

    def test_percentile_calcs_missing_datetime(self):
        # test the function errors if include_metadata=True and no
        # datetime index is present
        with pytest.raises(ValueError):
            percentiles.calculate_fixed_percentile_thresholds(
                np.arange(101), method='linear', ignore_na=False,
                include_metadata=True)

    def test_percentile_calcs_missing_data_col(self):
        # test the function errors if data_column_name not present
        with pytest.raises(ValueError):
            percentiles.calculate_fixed_percentile_thresholds(
                self.data, 'column_A')


class TestCalculateVariablePercentileThresholdsByDay:
    # data for all tests in this class
    small_df = pd.DataFrame({
        'data': np.arange(101),
        'date': pd.date_range('2019-01-01', '2019-04-11')})

    bigger_df = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2000-01-01', '2020-12-31'))),
        'date': pd.date_range('2000-01-01', '2020-12-31')})

    df_dummy = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2000-01-01', '2001-12-31'))),
        'date': pd.date_range('2000-01-01', '2001-12-31')})

    df_dummy_alt = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2001-01-01', '2002-12-31'))),
        'date': pd.date_range('2001-01-01', '2002-12-31')})

    # This dataframe has 2 years of data but is missing values
    # in the month of May.
    include_months = [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12]
    df_dummy_missing_days = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2001-01-01', '2002-12-31'))),
        'date': pd.date_range('2001-01-01', '2002-12-31')})
    df_dummy_missing_days = df_dummy_missing_days[df_dummy_missing_days['date'].dt.month.isin(include_months)] # noqa

    # This dataframe has 10 years of data, but 5 days have nans
    # in year 1.
    df_nans = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2001-01-01', '2010-12-31'))),
        'date': pd.date_range('2001-01-01', '2010-12-31')})
    df_nans.data.iloc[0:5] = np.nan

    def test_calculate_variable_percentile_thresholds_by_day(self):
        """Test with date column."""
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.small_df, 'data', date_column_name='date')
        assert percentiles_.shape == (366, 13)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max',
            'mean', 'count', 'start_yr', 'end_yr']
        assert percentiles_.index[0] == '01-01'

    def test_calculate_variable_percentile_thresholds_by_day_dateindex(self):
        """Test with dates in the index."""
        # test the function with no date column and dates in the index
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.small_df, 'data', include_metadata=False)
        assert percentiles_.shape == (366, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']
        assert percentiles_.index[0] == '01-01'

    def test_calculate_variable_percentile_thresholds_by_day_percentiles(self):
        # test the function with a different set of percentiles
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.small_df, 'data', percentiles=np.array((10, 50, 90)),
            include_metadata=False)
        assert percentiles_.shape == (366, 5)
        assert percentiles_.columns.tolist() == [
            'min', 'p10', 'p50', 'p90', 'max']
        assert percentiles_.index[0] == '01-01'

    def test_non_nans(self):
        """Test that the percentiles are not NaN."""
        # test the function and check that the percentiles are not NaN
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.bigger_df, 'data', date_column_name='date',
            include_metadata=False, include_min_max=False,
            mask_out_of_range=False)
        assert not percentiles_.isna().all().all()
        # test that the function is calculating percentiles for a given
        # day correctly by comparing output to base percentile function
        # calculation
        percentiles_filter_ = percentiles_.filter(items = ['04-01'], axis = 0).iloc[0] # noqa
        filter_df = self.bigger_df.loc[(self.bigger_df['date'].dt.month==4) & (self.bigger_df['date'].dt.day==1)] # noqa
        filter_df_perc = np.nanpercentile(filter_df['data'].round(2), np.array((5, 10, 25, 50, 75, 90, 95)), method='weibull') # noqa
        assert (percentiles_filter_ == filter_df_perc).all()

    def test_longer_dummy_set(self):
        """Test with a longer dummy set."""
        # test a longer dummy set that exceeds 1 year
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.df_dummy, 'data', date_column_name='date',
            include_metadata=False)
        assert percentiles_.shape == (366, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']

    def test_longer_dummy_alt(self):
        """Test with a different longer dummy set."""
        # test a longer dummy set that exceeds 1 year
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.df_dummy_alt, 'data', date_column_name='date',
            include_metadata=False)
        assert percentiles_.shape == (366, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']

    def test_bigger_rolling_avg(self):
        """Test rolling average."""
        # function w/ daily percentiles
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.bigger_df, 'data', date_column_name='date',
            include_metadata=False, include_min_max=False,
            mask_out_of_range=False)
        percentiles_7day = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.bigger_df, 'data', date_column_name='date',
            data_type='7-day', include_metadata=False, include_min_max=False,
            mask_out_of_range=False)
        assert percentiles_.shape == (366, 7)
        assert percentiles_7day.shape == (366, 7)
        assert percentiles_.columns.tolist() == [
            'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95']
        assert percentiles_7day.columns.tolist() == [
            'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95']
        # check that the percentiles are not NaN
        assert not percentiles_.isna().all().all()
        assert not percentiles_7day.isna().all().all()
        # check that the percentiles are not the same
        assert not percentiles_.equals(percentiles_7day)
        # check that 7 day rolling average calculated and handled
        # correctly
        self.bigger_df = self.bigger_df.set_index('date')
        self.bigger_df['data'] = self.bigger_df['data'].rolling('7D', 7).mean().round(2) # noqa
        percentiles_7day_filter_ = percentiles_7day.filter(items=['04-01'], axis=0).iloc[0] # noqa
        filter_df = self.bigger_df.loc[(self.bigger_df.index.month == 4) & (self.bigger_df.index.day == 1)] # noqa
        filter_df_perc = np.nanpercentile(filter_df['data'], np.array((5, 10, 25, 50, 75, 90, 95)), method='weibull') # noqa
        assert (percentiles_7day_filter_ == filter_df_perc).all()

    def test_small_df_trailing_leading_values(self):
        """Test that percentiles are not calculated if there aren't sufficient leading/trailing values""" # noqa
        # test a short dataset lacking leading values
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.small_df, 'data', date_column_name='date',
            leading_values=14,
            trailing_values=14,
            include_metadata=False,
            include_min_max=False,
            mask_out_of_range=False)
        # shouldn't all be na
        assert not percentiles_.isna().all().all()
        # but some should be na
        assert percentiles_['p50'][0:13].isna().all()
        assert percentiles_.shape == (366, 7)
        assert percentiles_.columns.tolist() == [
            'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95']
        # check leading and trailing values calc
        percentiles_filter_ = percentiles_.filter(items=['01-15'], axis=0).iloc[0] # noqa
        self.small_df = self.small_df.set_index('date')
        filter_df = self.small_df.loc[(self.small_df.index >= '2019-01-01') & (self.small_df.index < '2019-01-30')] # noqa
        filter_df_perc = np.nanpercentile(filter_df['data'], np.array((5, 10, 25, 50, 75, 90, 95)), method='weibull') # noqa
        assert (percentiles_filter_ == filter_df_perc).all()

    def test_empty_df(self):
        """Test that function returns empty percentile df."""
        # test the function with an empty DataFrame and check
        # that the percentiles are all NaN
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            pd.DataFrame([]), 'data')
        assert percentiles_.isna().all().all()
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max',
            'mean', 'count', 'start_yr', 'end_yr']

    def test_missing_doys(self):
        """Test that function returns empty percentile df."""
        # test the function can handle when days of the year
        # are missing from the dataframe. These days should
        # not be included or show up as NaN
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.df_dummy_missing_days, 'data', date_column_name='date')
        assert not percentiles_.isna().all().all()
        assert percentiles_.iloc[126].isna().all()
        assert percentiles_.shape == (366, 13)


class TestCalculateVariablePercentileThresholdsByDayOfYear:
    # data for all tests in this class
    small_df = pd.DataFrame({
        'data': np.arange(101),
        'date': pd.date_range('2019-01-01', '2019-04-11')})

    bigger_df = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2000-01-01', '2020-12-31'))),
        'date': pd.date_range('2000-01-01', '2020-12-31')})

    df_dummy = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2000-01-01', '2001-12-31'))),
        'date': pd.date_range('2000-01-01', '2001-12-31')})

    df_dummy_alt = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2001-01-01', '2002-12-31'))),
        'date': pd.date_range('2001-01-01', '2002-12-31')})

    # This dataframe has 2 years of data but is missing values
    # in the month of May.
    include_months = [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12]
    df_dummy_missing_days = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2001-01-01', '2002-12-31'))),
        'date': pd.date_range('2001-01-01', '2002-12-31')})
    df_dummy_missing_days = df_dummy_missing_days[df_dummy_missing_days['date'].dt.month.isin(include_months)] # noqa

    # This dataframe has 10 years of data, but 5 days have nans
    # in year 1.
    df_nans = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2001-01-01', '2010-12-31'))),
        'date': pd.date_range('2001-01-01', '2010-12-31')})
    df_nans.data.iloc[0:5] = np.nan

    def test_calculate_variable_percentile_thresholds_by_day_of_year(self):
        """Test with date column."""
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.small_df, 'data', date_column_name='date')
        assert percentiles_.shape == (366, 13)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max',
            'mean', 'count', 'start_yr', 'end_yr']
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1
        assert percentiles_.index.get_level_values(1).tolist()[0] == 'calendar'

    def test_calculate_variable_percentile_thresholds_by_day_of_year_dateindex(self): # noqa
        """Test with dates in the index."""
        # test the function with no date column and dates in the index
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.small_df, 'data', include_metadata=False)
        assert percentiles_.shape == (366, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1
        assert percentiles_.index.get_level_values(1).tolist()[0] == 'calendar'

    def test_calculate_variable_percentile_thresholds_by_day_of_year_percentiles(self): # noqa
        # test the function with a different set of percentiles
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.small_df, 'data', percentiles=np.array((10, 50, 90)),
            include_metadata=False)
        assert percentiles_.shape == (366, 5)
        assert percentiles_.columns.tolist() == [
            'min', 'p10', 'p50', 'p90', 'max']
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1
        assert percentiles_.index.get_level_values(1).tolist()[0] == 'calendar'

    def test_calculate_variable_percentile_thresholds_by_day_of_year_year_type(self): # noqa
        """Test with a different year type."""
        # test the function with a different year type
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.small_df, 'data', year_type='water', include_metadata=False)
        assert percentiles_.shape == (366, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1
        assert percentiles_.index.get_level_values(1).tolist()[0] == 'water'

    def test_calculate_variable_percentile_thresholds_by_day_of_year_year_type_percentiles(self): # noqa
        # test the function with a different year type and a different set of
        # percentiles
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.small_df, 'data',
            percentiles=np.array((10, 50, 90)), year_type='water',
            include_metadata=False)
        assert percentiles_.shape == (366, 5)
        assert percentiles_.columns.tolist() == [
            'min', 'p10', 'p50', 'p90', 'max']
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1
        assert percentiles_.index.get_level_values(1).tolist()[0] == 'water'

    def test_non_nans(self):
        """Test that the percentiles are not NaN."""
        # test the function and check that the percentiles are not NaN
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.bigger_df, 'data', date_column_name='date',
            include_metadata=False, include_min_max=False,
            mask_out_of_range=False)
        assert not percentiles_.isna().all().all()
        # test that the function is calculating percentiles for a given
        # day correctly by comparing output to base percentile function
        # calculation
        percentiles_filter_ = percentiles_[percentiles_.index.get_level_values(0) == 133].iloc[0] # noqa
        filter_df = self.bigger_df.loc[(self.bigger_df['date'].dt.day_of_year==133)] # noqa
        filter_df_perc = np.nanpercentile(filter_df['data'].round(2), np.array((5, 10, 25, 50, 75, 90, 95)), method='weibull') # noqa
        assert (percentiles_filter_ == filter_df_perc).all()

    def test_longer_dummy_set(self):
        """Test with a longer dummy set."""
        # test a longer dummy set that exceeds 1 year
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.df_dummy, 'data', date_column_name='date',
            include_metadata=False)
        assert percentiles_.shape == (366, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']

    def test_longer_dummy_alt(self):
        """Test with a different longer dummy set."""
        # test a longer dummy set that exceeds 1 year
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.df_dummy_alt, 'data', date_column_name='date',
            include_metadata=False)
        assert percentiles_.shape == (366, 9)
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max']

    def test_bigger_rolling_avg(self):
        """Test rolling average."""
        # function w/ daily percentiles
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.bigger_df, 'data', date_column_name='date',
            include_metadata=False, include_min_max=False,
            mask_out_of_range=False)
        percentiles_7day = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.bigger_df, 'data', date_column_name='date',
            data_type='7-day', include_metadata=False, include_min_max=False,
            mask_out_of_range=False)
        assert percentiles_.shape == (366, 7)
        assert percentiles_7day.shape == (366, 7)
        assert percentiles_.columns.tolist() == [
            'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95']
        assert percentiles_7day.columns.tolist() == [
            'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95'] # noqa
        # check that the percentiles are not NaN
        assert not percentiles_.isna().all().all()
        assert not percentiles_7day.isna().all().all()
        # check that the percentiles are not the same
        assert not percentiles_.equals(percentiles_7day)
        # check that 7 day rolling average calculated and handled
        # correctly
        self.bigger_df = self.bigger_df.set_index('date')
        self.bigger_df['data'] = self.bigger_df['data'].rolling('7D', 7).mean().round(2) # noqa
        percentiles_7day_filter_ = percentiles_7day[percentiles_7day.index.get_level_values(0) == 133].iloc[0] # noqa
        filter_df = self.bigger_df.loc[(self.bigger_df.index.day_of_year==133)] # noqa
        filter_df_perc = np.nanpercentile(filter_df['data'], np.array((5, 10, 25, 50, 75, 90, 95)), method='weibull') # noqa
        assert (percentiles_7day_filter_ == filter_df_perc).all()

    def test_small_df_trailing_leading_values(self):
        """Test that percentiles are not calculated if there aren't sufficient leading/trailing values""" # noqa
        # test a short dataset lacking leading values
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.small_df, 'data', date_column_name='date',
            leading_values=14,
            trailing_values=14,
            include_metadata=False,
            include_min_max=False,
            mask_out_of_range=False)
        # shouldn't all be na
        assert not percentiles_.isna().all().all()
        # but some should be na
        assert percentiles_['p50'][0:13].isna().all()
        assert percentiles_.shape == (366, 7)
        assert percentiles_.columns.tolist() == [
            'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95']
        # test leading and trailing values calculation
        percentiles_filter_ = percentiles_[percentiles_.index.get_level_values(0) == 15].iloc[0] # noqa
        filter_df = self.small_df.loc[(self.small_df['date'] >= '2019-01-01') & (self.small_df['date'] < '2019-01-30')] # noqa
        filter_df_perc = np.nanpercentile(filter_df['data'], np.array((5, 10, 25, 50, 75, 90, 95)), method='weibull') # noqa
        assert (percentiles_filter_ == filter_df_perc).all()

    def test_empty_df(self):
        """Test that function returns empty percentile df."""
        # test the function with an empty DataFrame and check
        # that the percentiles are all NaN
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            pd.DataFrame([]), 'data')
        assert percentiles_.isna().all().all()
        assert percentiles_.columns.tolist() == [
            'min', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'max',
            'mean', 'count', 'start_yr', 'end_yr']

    def test_missing_doys(self):
        """Test that function returns empty percentile df."""
        # test the function can handle when days of the year
        # are missing from the dataframe. These days should
        # not be included or show up as NaN
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day_of_year( # noqa
            self.df_dummy_missing_days, 'data', date_column_name='date')
        assert not percentiles_.isna().all().all()
        assert percentiles_.iloc[126].isna().all()
        assert percentiles_.shape == (366, 13)
        # assert percentiles_[percentiles_.index.get_level_values('doy') == 5].isna().all() # noqa


class TestCalculateFixedPercentilesFromValue:
    # define some test values
    data = np.arange(101)
    percentiles_ = np.arange(0, 105, 5)
    pct_df = pd.DataFrame(data={"values": percentiles_}, index=percentiles_).T
    pct_df.columns = "p" + pct_df.columns.astype(str).str.zfill(2)
    low_val = -5
    high_val = 105
    mid_val = 51
    multiple_values = [-5, 7, 51, 98, 105]

    def test_calculate_fixed_percentiles_from_value_low(self):
        """Test with a low value."""
        # test the function
        pct_out = percentiles.calculate_fixed_percentile_from_value(
            self.low_val, self.pct_df)
        assert pct_out == 0.0

    def test_calculate_fixed_percentiles_from_value_mid(self):
        """Test with a mid value."""
        # test the function
        pct_out = percentiles.calculate_fixed_percentile_from_value(
            self.mid_val, self.pct_df)
        assert pct_out == 51.0

    def test_calculate_fixed_percentiles_from_value_high(self):
        """Test with a high value."""
        # test the function
        pct_out = percentiles.calculate_fixed_percentile_from_value(
            self.high_val, self.pct_df)
        assert pct_out == 100.0

    def test_calculate_fixed_percentiles_from_value_multiple(self):
        """Test with multiple values."""
        pct_out = percentiles.calculate_fixed_percentile_from_value(
            self.multiple_values, self.pct_df)
        assert pct_out == pytest.approx([0.0, 7.0, 51.0, 98.0, 100.0])

    def test_calculate_fixed_percentiles_from_value_invalid(self):
        """Test with invalid inputs."""
        with pytest.raises(AttributeError):
            percentiles.calculate_fixed_percentile_from_value(
                self.low_val, [1, 2, 3])


class TestCalculateVariablePercentileFromValue_s:
    # Test percentile and df
    pct_df = pd.DataFrame(
        np.array(
            [[1, 2, 3, 4, 5],
             [5, np.nan, 6, 7, 8],
             [7, 8, 9, 10, 11],
             [np.nan, np.nan, np.nan, np.nan, np.nan]]
            ),
        columns=['min', 'p25', 'p50', 'p75', 'max'],
        index=['01-01', '01-02', '01-03', '01-04']
        )
    pct_df.index.names = ["month_day"]
    df = pd.DataFrame(
        pd.Series(
            [3.7, 4.1, 9.8, 7.2],
            index=pd.date_range('2024-01-01', '2024-01-04')
            ),
        columns=['00060_Mean']
        )
    df.index.name = 'datetime'
    # easier to define thresholds here that match
    # pct_df col names
    thresholds = np.array([0, 25, 50, 75, 100], dtype=np.float32)

    def test_calculate_variable_percentile_from_value_simple(self):
        """Test with a single value and no np.nans."""
        pct_out = percentiles.calculate_variable_percentile_from_value(
            3.5,
            self.pct_df,
            month_day='01-01'
            )
        percentile_values = np.array(self.pct_df.loc[self.pct_df.index == "01-01"].values.flatten().tolist(), dtype=np.float32) # noqa
        pct_np = np.interp(3.5, percentile_values,self.thresholds, left=0, right=100).round(2) # noqa
        assert pct_out == pct_np

    def test_calculate_variable_percentile_from_value_nan(self):
        """Test with a single value and an np.nan."""
        pct_out = percentiles.calculate_variable_percentile_from_value(
            5.5,
            self.pct_df,
            month_day='01-02'
            )
        percentile_values = np.array(self.pct_df.loc[self.pct_df.index == "01-02"].values.flatten().tolist(), dtype=np.float32) # noqa
        na_mask = ~np.isnan(percentile_values)
        percentile_values = percentile_values[na_mask]
        thresholds = self.thresholds[na_mask]
        pct_np = np.interp(5.5, percentile_values,thresholds, left=0, right=100).round(2) # noqa
        assert pct_out == pct_np

    def test_calculate_variable_percentile_from_value_min(self):
        """Test with a single value below the minimum percentile."""
        pct_out = percentiles.calculate_variable_percentile_from_value(
            0.5,
            self.pct_df,
            month_day='01-01'
            )
        percentile_values = np.array(self.pct_df.loc[self.pct_df.index == "01-01"].values.flatten().tolist(), dtype=np.float32) # noqa
        na_mask = ~np.isnan(percentile_values)
        percentile_values = percentile_values[na_mask]
        thresholds = self.thresholds[na_mask]
        pct_np = np.interp(0.5, percentile_values,thresholds, left=0, right=100).round(2) # noqa
        assert pct_out == pct_np
        assert pct_out == 0.0

    def test_calculate_variable_percentile_from_value_max(self):
        """Test with a single value above the maximum percentile."""
        pct_out = percentiles.calculate_variable_percentile_from_value(
            15,
            self.pct_df,
            month_day='01-03'
            )
        percentile_values = np.array(self.pct_df.loc[self.pct_df.index == "01-03"].values.flatten().tolist(), dtype=np.float32) # noqa
        na_mask = ~np.isnan(percentile_values)
        percentile_values = percentile_values[na_mask]
        thresholds = self.thresholds[na_mask]
        pct_np = np.interp(15, percentile_values,thresholds, left=0, right=100).round(2) # noqa
        assert pct_out == pct_np
        assert pct_out == 100.0

    def test_calculate_variable_percentile_from_value_percentiles_nan(self):
        """Test with a single value above the maximum percentile."""
        pct_out = percentiles.calculate_variable_percentile_from_value(
            5,
            self.pct_df,
            month_day='01-04'
            )
        assert np.isnan(pct_out)

    def test_calculate_multiple_variable_percentiles_from_values_basic(self): # noqa
        """Test with multiple values from a df"""
        pct_df_out = percentiles.calculate_multiple_variable_percentiles_from_values( # noqa
            self.df,
            '00060_Mean',
            self.pct_df
            )
        est_pct1 = np.interp(
            self.df.iloc[0]['00060_Mean'],
            np.array(self.pct_df.loc[self.pct_df.index == "01-01"].values.flatten().tolist(), dtype=np.float32), # noqa
            self.thresholds,
            left=0,
            right=100).round(2)
        est_pct3 = np.interp(
            self.df.iloc[2]['00060_Mean'],
            np.array(self.pct_df.loc[self.pct_df.index == "01-03"].values.flatten().tolist(), dtype=np.float32), # noqa
            self.thresholds,
            left=0,
            right=100).round(2)
        assert pct_df_out.shape == (4, 2)
        assert np.all(pct_df_out.index == self.df.index)
        assert pct_df_out.iloc[0]['est_pct'] == est_pct1
        assert pct_df_out.iloc[2]['est_pct'] == est_pct3
        assert np.isnan(pct_df_out.iloc[3]['est_pct'])
