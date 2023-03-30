"""Unit tests for the utils module."""
import pytest
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
