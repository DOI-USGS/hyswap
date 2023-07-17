"""Tests for the runoff.py module."""
import pytest
from hyswap import runoff
import pandas as pd


def test_convert_cfs_to_mmyr():
    """Test the convert_cfs_to_mmyr function."""
    mmyr = runoff.convert_cfs_to_mmyr(14, 250)
    assert pytest.approx(mmyr, 0.1) == 50.0


def test_streamflow_to_runoff():
    """Test the streamflow_to_runoff function."""
    df = pd.DataFrame({"streamflow": [14, 15, 16]})
    runoff_df = runoff.streamflow_to_runoff(df, "streamflow", 250)
    assert pytest.approx(runoff_df["runoff"].round(1)) == [50.0, 53.6, 57.2]
