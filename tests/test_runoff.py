"""Tests for the runoff.py module."""
import pytest
from hyswap import runoff
import numpy as np
import pandas as pd


def test_convert_cfs_to_runoff():
    """Test the convert_cfs_to_runoff function."""
    mmyr = runoff.convert_cfs_to_runoff(14, 250)
    assert pytest.approx(mmyr, 0.1) == 50.0


def test_convert_cfs_to_runoff_annual():
    """Test the convert_cfs_to_runoff function with annual kwarg."""
    mmyr = runoff.convert_cfs_to_runoff(14, 250, frequency='annual')
    assert pytest.approx(mmyr, 0.1) == 50.0


def test_convert_cfs_to_runoff_monthly():
    """Test the convert_cfs_to_runoff function with monthly kwarg."""
    mmyr = runoff.convert_cfs_to_runoff(14, 250, frequency='monthly')
    assert pytest.approx(mmyr, 0.1) == 4.2


def test_convert_cfs_to_runoff_daily():
    """Test the convert_cfs_to_runoff function with daily kwarg."""
    mmyr = runoff.convert_cfs_to_runoff(14, 250, frequency='daily')
    assert pytest.approx(mmyr, 0.1) == 0.14


def test_convert_cfs_to_runoff_invalid():
    """Test the convert_cfs_to_runoff function with invalid kwarg."""
    with pytest.raises(ValueError):
        runoff.convert_cfs_to_runoff(14, 250, frequency='invalid')


def test_streamflow_to_runoff():
    """Test the streamflow_to_runoff function."""
    df = pd.DataFrame({"streamflow": [14, 15, 16]})
    runoff_df = runoff.streamflow_to_runoff(df, "streamflow", 250)
    assert pytest.approx(runoff_df["runoff"].round(1)) == [50.0, 53.6, 57.2]


@pytest.fixture
def weight_matrix():
    """Load and then return the demo weights matrix df as a test fixture."""
    return pd.read_json("tests/demo_weights.json")


@pytest.fixture
def weight_table():
    """Load and then return the demo weights tabular df as a test fixture."""
    return pd.read_csv("tests/demo_weights_table.csv",
                       converters={0: str, 1: str})


@pytest.fixture
def df_list(weight_matrix):
    """Create a synthetic list of dataframes as a test fixture."""
    siteids = weight_matrix.index.tolist()
    df_list = []
    for siteid in siteids:
        df = pd.DataFrame({
            "site_no": [siteid, siteid, siteid],
            "runoff": list(np.random.random(3))
        })
        df.index = pd.date_range(
            "2000-01-01", periods=3, freq="D").tz_localize("UTC")
        df_list.append(df)
    return df_list


def test_get_date_range(df_list):
    """Test the get_date_range function with no dates."""
    date_range = runoff._get_date_range(df_list, None, None)
    # assertions about the date range
    assert date_range[0].year == 2000
    assert date_range[0].month == 1
    assert date_range[0].day == 1
    assert date_range[-1].year == 2000
    assert date_range[-1].month == 1
    assert date_range[-1].day == 3


def test_get_date_range_start(df_list):
    """Test the get_date_range function with no dates."""
    date_range = runoff._get_date_range(df_list, "1999-12-30", None)
    # assertions about the date range
    assert date_range[0].year == 1999
    assert date_range[0].month == 12
    assert date_range[0].day == 30
    assert date_range[-1].year == 2000
    assert date_range[-1].month == 1
    assert date_range[-1].day == 3


def test_get_date_range_end(df_list):
    """Test the get_date_range function with no dates."""
    date_range = runoff._get_date_range(df_list, None, "2000-01-10")
    # assertions about the date range
    assert date_range[0].year == 2000
    assert date_range[0].month == 1
    assert date_range[0].day == 1
    assert date_range[-1].year == 2000
    assert date_range[-1].month == 1
    assert date_range[-1].day == 10


def test_get_date_range_start_end(df_list):
    """Test the get_date_range function with no dates."""
    date_range = runoff._get_date_range(
        df_list, "1999-12-30", "2000-01-10")
    # assertions about the date range
    assert date_range[0].year == 1999
    assert date_range[0].month == 12
    assert date_range[0].day == 30
    assert date_range[-1].year == 2000
    assert date_range[-1].month == 1
    assert date_range[-1].day == 10


def test_state_runoff(weight_matrix, df_list):
    """Test for the area weighted runoff for a specific state."""
    state_runoff = runoff.calculate_geometric_runoff(
        "AL", df_list, weight_matrix)
    # assertions about the state runoff
    # input was 3 dates so expect there to be 3 dates in the index
    assert len(state_runoff.index) == 3
    assert isinstance(
        state_runoff.index, pd.core.indexes.datetimes.DatetimeIndex)
    # input was 3 sites so expect there to be 3 values, one for each site
    assert len(state_runoff.values) == 3
    assert isinstance(state_runoff.values, np.ndarray)


def test_identify_sites_from_weights(weight_table):
    """Test the identify_sites_from_weights function."""
    siteids = runoff.identify_sites_from_weights(
        geom_id="05090201",
        weights_df=weight_table,
        geom_id_col='huc_cd',
        site_col='site_no',
        wght_in_basin_col='pct_in_basin',
        wght_in_geom_col='pct_in_huc')

    assert siteids == ['03234300']


def test_multiple_runoff(weight_matrix, df_list):
    """Test for the area weighted runoff for multiple states."""
    runoff_df = runoff.calculate_multiple_geometric_runoff(
        ["AL", "NY"], df_list, weight_matrix)
    # assertions about the runoff
    # should have 3 datetime values on the index
    assert len(runoff_df.index) == 3
    assert isinstance(
        runoff_df.index, pd.core.indexes.datetimes.DatetimeIndex)
    # should have both states in the columns
    assert len(runoff_df.columns) == 2
    assert runoff_df.columns.tolist() == ["AL", "NY"]
    # overall shape should be 3 dates x 2 states
    assert runoff_df.shape == (3, 2)
