"""Unit tests for the exceedance module."""
import pytest
import numpy as np
import pandas as pd
from hyswap import exceedance


def test_calculate_exceedance_probability_from_distribution():
    """Test the calculate_exceedance_probability_from_distribution function."""
    # Normal and lognormal distribution tests
    x = 1
    mu = 1
    sigma = 0.25
    prob = exceedance.calculate_exceedance_probability_from_distribution(
        x, 'lognormal', mu, sigma)
    assert prob == 0.6132049428659028
    prob = exceedance.calculate_exceedance_probability_from_distribution(
        x, 'normal', mu, sigma)
    assert prob == 0.5
    # Weibull and exponential distribution tests
    k = 1
    lambda_ = 1
    prob = exceedance.calculate_exceedance_probability_from_distribution(
        x, 'weibull', k, lambda_)
    assert prob == 0.36787944117144233
    prob = exceedance.calculate_exceedance_probability_from_distribution(
        x, 'exponential', lambda_)
    assert prob == 1.0
    # Test invalid values
    with pytest.raises(TypeError):
        exceedance.calculate_exceedance_probability_from_distribution(
            x, 'exponential', mu, sigma, k, lambda_)
    with pytest.raises(ValueError):
        exceedance.calculate_exceedance_probability_from_distribution(
            x, "invalid", mu, sigma)
    with pytest.raises(TypeError):
        exceedance.calculate_exceedance_probability_from_distribution(
            x, 'exponential', mu, sigma, k=1, lambda_=1)
    with pytest.raises(TypeError):
        exceedance.calculate_exceedance_probability_from_distribution(
            "invalid", 'exponential', mu, sigma)
    with pytest.raises(TypeError):
        exceedance.calculate_exceedance_probability_from_distribution(
            x, 5, mu, sigma)


def test_calculate_exceedance_probability_from_values():
    """Test the calculate_exceedance_probability_from_values function."""
    # Testing low value of 1
    x = 1
    values_to_compare = np.array([1, 2, 3, 4])
    prob = exceedance.calculate_exceedance_probability_from_values(
        x, values_to_compare)
    assert prob == 1.0
    values_to_compare = [1, 1, 1, 1]  # use a list
    prob = exceedance.calculate_exceedance_probability_from_values(
        x, values_to_compare)
    assert prob == 1.0
    values_to_compare = pd.Series([2, 2, 2, 2])  # use a pandas series
    prob = exceedance.calculate_exceedance_probability_from_values(
        x, values_to_compare)
    assert prob == 1.0
    # Testing high value of 5
    x = 5
    values_to_compare = np.array([1, 2, 3, 4])
    prob = exceedance.calculate_exceedance_probability_from_values(
        x, values_to_compare)
    assert prob == 0.0
    values_to_compare = np.array([1, 1, 1, 1])
    prob = exceedance.calculate_exceedance_probability_from_values(
        x, values_to_compare)
    assert prob == 0.0
    # Testing middle value of 3
    x = 3
    values_to_compare = np.array([1, 2, 3, 4])
    prob = exceedance.calculate_exceedance_probability_from_values(
        x, values_to_compare)
    assert prob == 0.5
    values_to_compare = np.array([1, 1, 1, 1])
    prob = exceedance.calculate_exceedance_probability_from_values(
        x, values_to_compare)
    assert prob == 0.0
    # Testing invalid values
    with pytest.raises(TypeError):
        exceedance.calculate_exceedance_probability_from_values(
            x, "invalid")
    with pytest.raises(TypeError):
        exceedance.calculate_exceedance_probability_from_values(
            "invalid", values_to_compare)


def test_calculate_exceedance_probability_from_distribution_multiple():
    """Test calculate_exceedance_probability_from_distribution_multiple."""
    # Single values should return the same as the single value function
    x = 1
    mu = 1
    sigma = 0.25
    prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        [x], 'lognormal', mu, sigma)
    prob_single = exceedance.calculate_exceedance_probability_from_distribution(  # noqa: E501
        x, 'lognormal', mu, sigma)
    assert prob == prob_single
    prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        [x], 'normal', mu, sigma)
    prob_single = exceedance.calculate_exceedance_probability_from_distribution(  # noqa: E501
        x, 'normal', mu, sigma)
    assert prob == prob_single
    k = 1
    lambda_ = 1
    prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        [x], 'weibull', k, lambda_)
    prob_single = exceedance.calculate_exceedance_probability_from_distribution(  # noqa: E501
        x, 'weibull', k, lambda_)
    assert prob == prob_single
    prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        [x], 'exponential', lambda_)
    prob_single = exceedance.calculate_exceedance_probability_from_distribution(  # noqa: E501
        x, 'exponential', lambda_)
    assert prob == prob_single
    # Test multiple values for normal and lognormal distributions
    values = np.array([1.0, 1.25, 1.5, 1.75, 2.0])
    mu = 1
    sigma = 0.25
    prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        values, 'lognormal', mu, sigma)
    assert np.allclose(prob, np.array([0.61320494, 0.5, 0.41171189,
                                       0.34256783, 0.28787077]))
    prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        values, 'normal', mu, sigma)
    assert np.allclose(prob, np.array([0.5, 0.158655254, 0.0227501319,
                                       0.00134989803, 0.0000316712418]))
    # Test weibull and exponential distributions
    values = np.array([1, 2, 3, 4])
    k = 1
    lambda_ = 1
    prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        values, 'weibull', k, lambda_)
    assert np.allclose(prob, np.array([0.36787944, 0.13533528,
                                       0.04978707, 0.01831564]))
    prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        values, 'exponential', lambda_)
    assert np.allclose(prob, np.array([1., 0.36787944,
                                       0.13533528, 0.04978707]))
    # Test invalid values
    with pytest.raises(TypeError):
        exceedance.calculate_exceedance_probability_from_distribution_multiple(
            values, 'exponential', mu, sigma, k, lambda_)
    with pytest.raises(ValueError):
        exceedance.calculate_exceedance_probability_from_distribution_multiple(
            values, "invalid", mu, sigma)


def test_calculate_exceedance_probability_from_values_multiple():
    """Test calculate_exceedance_probability_from_values_multiple function."""
    values = np.array([1, 2, 3, 4])
    values_to_compare = np.array([1, 2, 3, 4])
    prob = exceedance.calculate_exceedance_probability_from_values_multiple(
        values, values_to_compare)
    assert np.allclose(prob, np.array([1.0, 0.75, 0.5, 0.25]))
    values_to_compare = np.array([1, 1, 1, 1])
    prob = exceedance.calculate_exceedance_probability_from_values_multiple(
        values, values_to_compare)
    assert np.allclose(prob, np.array([1.0, 0.0, 0.0, 0.0]))
    values_to_compare = np.array([2, 2, 2, 2])
    prob = exceedance.calculate_exceedance_probability_from_values_multiple(
        values, values_to_compare)
    assert np.allclose(prob, np.array([1.0, 1.0, 0.0, 0.0]))
    values_to_compare = np.array([1, 2, 3, 4, 1, 2, 3, 4])
    prob = exceedance.calculate_exceedance_probability_from_values_multiple(
        values, values_to_compare)
    assert np.allclose(prob, np.array([1.0, 0.75, 0.5, 0.25]))
    values_to_compare = np.array([1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4])
    prob = exceedance.calculate_exceedance_probability_from_values_multiple(
        values, values_to_compare)
    assert np.allclose(prob, np.array([1.0, 0.75, 0.5, 0.25]))
