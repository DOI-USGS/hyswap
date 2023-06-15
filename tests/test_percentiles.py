"""Tests for the percentiles functions."""
import numpy as np
import pandas as pd
import pytest
from hyswap import percentiles


class TestCalculateFixedPercentileThresholds:
    # data value for all tests in this class
    data = np.arange(101)

    def test_calculate_fixed_percentile_thresholds_defaults(self):
        """Test the calculate_fixed_percentile_thresholds function defaults."""
        # test the function
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data, method='linear')
        assert percentiles_.shape == (8,)
        assert percentiles_ == pytest.approx((0, 5, 10, 25, 75, 90, 95, 100))

    def test_custom_percentiles(self):
        # set some percentile values as opposed to the defaults
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data, percentiles=np.array((0, 10, 50, 90, 100)))
        assert percentiles_.shape == (5,)
        assert percentiles_ == pytest.approx((0, 9.2, 50, 90.8, 100))

    def test_kwargs_to_percentile(self):
        # pass kwarg through to np.percentile
        percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
            self.data, method='lower')
        assert percentiles_.shape == (8,)
        assert percentiles_ == pytest.approx((0, 5, 10, 25, 75, 90, 95, 100))


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

    def test_calculate_variable_percentile_thresholds_by_day(self):
        """Test with date column."""
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.small_df, 'data', date_column_name='date')
        assert percentiles_.shape == (101, 8)
        assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
        assert percentiles_.index.get_level_values(1).tolist()[0] == '01-01'
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1

    def test_calculate_variable_percentile_thresholds_by_day_dateindex(self):
        """Test with dates in the index."""
        # test the function with no date column and dates in the index
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.small_df, 'data')
        assert percentiles_.shape == (101, 8)
        assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
        assert percentiles_.index.get_level_values(1).tolist()[0] == '01-01'
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1

    def test_calculate_variable_percentile_thresholds_by_day_percentiles(self):
        # test the function with a different set of percentiles
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.small_df, 'data', percentiles=np.array((0, 10, 50, 90, 100)))
        assert percentiles_.shape == (101, 5)
        assert percentiles_.columns.tolist() == [0, 10, 50, 90, 100]
        assert percentiles_.index.get_level_values(1).tolist()[0] == '01-01'
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1
        # all percentiles should be NaN because demo dataset is 1 year only
        assert percentiles_.isna().all().all()

    def test_calculate_variable_percentile_thresholds_by_day_year_type(self):
        """Test with a different year type."""
        # test the function with a different year type
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.small_df, 'data', year_type='water')
        assert percentiles_.shape == (101, 8)
        assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
        assert percentiles_.index.get_level_values(1).tolist()[0] == '01-01'
        assert percentiles_.index.get_level_values(0).tolist()[0] == 93
        assert percentiles_.index.get_level_values(1).tolist()[-1] == '04-11'
        assert percentiles_.index.get_level_values(0).tolist()[-1] == 193
        # all percentiles should be NaN because demo dataset is 1 year only
        assert percentiles_.isna().all().all()

    def test_calculate_variable_percentile_thresholds_by_day_year_type_percentiles(self): # noqa
        # test the function with a different year type and a different set of
        # percentiles
        self.small_df = self.small_df.set_index('date')
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.small_df, 'data', year_type='climate',
            percentiles=np.array((0, 10, 50, 90, 100)))
        assert percentiles_.shape == (101, 5)
        assert percentiles_.columns.tolist() == [0, 10, 50, 90, 100]
        assert percentiles_.index.get_level_values(1).tolist()[0] == '04-01'
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1
        # all percentiles should be NaN because demo dataset is 1 year only
        assert percentiles_.isna().all().all()

    def test_non_nans(self):
        """Test that the percentiles are not NaN."""
        # test the function and check that the percentiles are not NaN
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.bigger_df, 'data', date_column_name='date')
        assert not percentiles_.isna().all().all()

    def test_longer_dummy_set(self):
        """Test with a longer dummy set."""
        # test a longer dummy set that exceeds 1 year
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.df_dummy, 'data', date_column_name='date', year_type='water')
        assert percentiles_.shape == (365, 8)
        assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
        assert percentiles_.index.get_level_values(1).tolist()[0] == '10-01'
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1
        assert percentiles_.index.get_level_values(1).tolist()[-1] == '09-30'
        assert percentiles_.index.get_level_values(0).tolist()[-1] == 365

    def test_longer_dummy_alt(self):
        """Test with a different longer dummy set."""
        # test a longer dummy set that exceeds 1 year
        # test the function
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.df_dummy_alt, 'data', date_column_name='date',
            year_type='water')
        assert percentiles_.shape == (365, 8)
        assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
        assert percentiles_.index.get_level_values(1).tolist()[0] == '10-01'
        assert percentiles_.index.get_level_values(0).tolist()[0] == 1
        assert percentiles_.index.get_level_values(1).tolist()[-1] == '09-30'
        assert percentiles_.index.get_level_values(0).tolist()[-1] == 365

    def test_bigger_rolling_avg(self):
        """Test rolling average."""
        # function w/ daily percentiles
        percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.bigger_df, 'data', date_column_name='date')
        percentiles_7day = percentiles.calculate_variable_percentile_thresholds_by_day( # noqa
            self.bigger_df, 'data', date_column_name='date',
            data_type='7-day')
        assert percentiles_.shape == (365, 8)
        assert percentiles_7day.shape == (365, 8)
        assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
        assert percentiles_7day.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100] # noqa
        # check that the percentiles are not NaN
        assert not percentiles_.isna().all().all()
        assert not percentiles_7day.isna().all().all()
        # check that the percentiles are not the same
        assert not percentiles_.equals(percentiles_7day)
