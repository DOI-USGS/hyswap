"""Tests for the percentiles functions."""
import numpy as np
import pandas as pd
import pytest
from hyswap import percentiles


def test_calculate_fixed_percentile_thresholds():
    """Test the calculate_fixed_percentile_thresholds function."""
    # make some data
    data = np.arange(101)
    # test the function
    percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
        data, method='linear')
    assert percentiles_.shape == (8,)
    assert percentiles_ == pytest.approx((0, 5, 10, 25, 75, 90, 95, 100))
    # set some percentile values as opposed to the defaults
    percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
        data, percentiles=np.array((0, 10, 50, 90, 100)))
    assert percentiles_.shape == (5,)
    assert percentiles_ == pytest.approx((0, 9.2, 50, 90.8, 100))
    # pass kwarg through to np.percentile
    percentiles_ = percentiles.calculate_fixed_percentile_thresholds(
        data, method='lower')
    assert percentiles_.shape == (8,)
    assert percentiles_ == pytest.approx((0, 5, 10, 25, 75, 90, 95, 100))


def test_calculate_variable_percentile_thresholds_by_day():
    """Test the calculate_variable_percentile_thresholds_by_day function."""
    # make a dataframe
    df = pd.DataFrame({
        'data': np.arange(101),
        'date': pd.date_range('2019-01-01', '2019-04-11')})
    # test the function
    percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day(
        df, 'data', date_column_name='date')
    assert percentiles_.shape == (101, 8)
    assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
    assert percentiles_.index.get_level_values(1).tolist()[0] == '01-01'
    assert percentiles_.index.get_level_values(0).tolist()[0] == 1
    # test the function with no date column and dates in the index
    df = df.set_index('date')
    percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day(
        df, 'data')
    assert percentiles_.shape == (101, 8)
    assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
    assert percentiles_.index.get_level_values(1).tolist()[0] == '01-01'
    assert percentiles_.index.get_level_values(0).tolist()[0] == 1
    # test the function with a different set of percentiles
    percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day(
        df, 'data', percentiles=np.array((0, 10, 50, 90, 100)))
    assert percentiles_.shape == (101, 5)
    assert percentiles_.columns.tolist() == [0, 10, 50, 90, 100]
    assert percentiles_.index.get_level_values(1).tolist()[0] == '01-01'
    assert percentiles_.index.get_level_values(0).tolist()[0] == 1
    # all percentiles should be NaN because demo dataset is 1 year only
    assert percentiles_.isna().all().all()
    # test the function with a different year type
    percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day(
        df, 'data', year_type='water')
    assert percentiles_.shape == (101, 8)
    assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
    assert percentiles_.index.get_level_values(1).tolist()[0] == '01-01'
    assert percentiles_.index.get_level_values(0).tolist()[0] == 93
    assert percentiles_.index.get_level_values(1).tolist()[-1] == '04-11'
    assert percentiles_.index.get_level_values(0).tolist()[-1] == 193
    # all percentiles should be NaN because demo dataset is 1 year only
    assert percentiles_.isna().all().all()
    # test the function with a different year type and a different set of
    # percentiles
    percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day(
        df, 'data', year_type='climate',
        percentiles=np.array((0, 10, 50, 90, 100)))
    assert percentiles_.shape == (101, 5)
    assert percentiles_.columns.tolist() == [0, 10, 50, 90, 100]
    assert percentiles_.index.get_level_values(1).tolist()[0] == '04-01'
    assert percentiles_.index.get_level_values(0).tolist()[0] == 1
    # all percentiles should be NaN because demo dataset is 1 year only
    assert percentiles_.isna().all().all()
    # make a bigger dummy dataset so values are not NaN
    df = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2000-01-01', '2020-12-31'))),
        'date': pd.date_range('2000-01-01', '2020-12-31')})
    # test the function and check that the percentiles are not NaN
    percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day(
        df, 'data', date_column_name='date')
    assert not percentiles_.isna().all().all()
    # test a longer dummy set that exceeds 1 year
    df = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2000-01-01', '2001-12-31'))),
        'date': pd.date_range('2000-01-01', '2001-12-31')})
    # test the function
    percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day(
        df, 'data', date_column_name='date', year_type='water')
    assert percentiles_.shape == (365, 8)
    assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
    assert percentiles_.index.get_level_values(1).tolist()[0] == '10-01'
    assert percentiles_.index.get_level_values(0).tolist()[0] == 1
    assert percentiles_.index.get_level_values(1).tolist()[-1] == '09-30'
    assert percentiles_.index.get_level_values(0).tolist()[-1] == 365
    # test a longer dummy set that exceeds 1 year
    df = pd.DataFrame({
        'data': np.random.random(
            len(pd.date_range('2001-01-01', '2002-12-31'))),
        'date': pd.date_range('2001-01-01', '2002-12-31')})
    # test the function
    percentiles_ = percentiles.calculate_variable_percentile_thresholds_by_day(
        df, 'data', date_column_name='date', year_type='water')
    assert percentiles_.shape == (365, 8)
    assert percentiles_.columns.tolist() == [0, 5, 10, 25, 75, 90, 95, 100]
    assert percentiles_.index.get_level_values(1).tolist()[0] == '10-01'
    assert percentiles_.index.get_level_values(0).tolist()[0] == 1
    assert percentiles_.index.get_level_values(1).tolist()[-1] == '09-30'
    assert percentiles_.index.get_level_values(0).tolist()[-1] == 365
