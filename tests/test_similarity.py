"""Tests for the similarity functions."""
import pytest
import numpy as np
import pandas as pd
from hyswap import similarity


def test_calculate_correlations():
    """Test the calculate_correlations function."""
    df1 = pd.DataFrame({'a': np.arange(10), 'b': np.arange(10)})
    df2 = pd.DataFrame({'a': -1*np.arange(10), 'b': np.arange(10)})
    results, n_obs = similarity.calculate_correlations([df1, df2], 'a')
    assert n_obs == 10
    assert results.iloc[0, 0] == pytest.approx(1)
    assert results.iloc[0, 1] == pytest.approx(-1)
    assert results.iloc[1, 0] == pytest.approx(-1)
    assert results.iloc[1, 1] == pytest.approx(1)


def test_calculate_wasserstein_distance():
    """Test the calculate_wasserstein_distance function."""
    df1 = pd.DataFrame({'a': np.arange(10),
                        'b': np.arange(10),
                        'site_no': np.zeros(10)})
    df2 = pd.DataFrame({'a': -1*np.arange(10),
                        'b': np.arange(10),
                        'site_no': np.ones(10)})
    results, n_obs = similarity.calculate_wasserstein_distance([df1, df2], 'a')
    assert n_obs == 10
    assert results.iloc[0, 0] == pytest.approx(0)
    assert results.iloc[0, 1] == pytest.approx(9)
    assert results.iloc[1, 0] == pytest.approx(9)
    assert results.iloc[1, 1] == pytest.approx(0)
    assert results.index[0] == 0
    assert results.index[1] == 1


def test_calculate_energy_distance():
    """Test the calculate_energy_distance function."""
    df1 = pd.DataFrame({'a': np.arange(10), 'b': np.arange(10)})
    df2 = pd.DataFrame({'a': -1*np.arange(10), 'b': np.arange(10)})
    results, n_obs = similarity.calculate_energy_distance(
        [df1, df2], 'a', df_names=['one', 'two'])
    assert n_obs == 10
    assert results.iloc[0, 0] == pytest.approx(0)
    assert np.round(results.iloc[0, 1], 1) == 3.4
    assert np.round(results.iloc[1, 0], 1) == 3.4
    assert results.iloc[1, 1] == pytest.approx(0)
    assert results.index[0] == 'one'
    assert results.index[1] == 'two'
