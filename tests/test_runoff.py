"""Tests for the runoff.py module."""
import pytest
from hyswap import runoff
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
    """Load and then return the demo weights dataframe as a test fixture."""
    return pd.read_json("demo_weights.json")


def test_state_runoff(weight_matrix):
    """Test for the area weighted runoff for a specific state."""
    state_runoff = runoff.state_runoff(weight_matrix, "AL")
    assert pytest.approx(state_runoff) == 0.0
