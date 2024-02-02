"""Unit tests for the exceedance module."""
import pytest
import numpy as np
import pandas as pd
from hyswap import exceedance


class TestCalculateExceedanceProbabilities:
    def test_calculate_exceedance_probability_from_distribution(self):
        """Test calculate_exceedance_probability_from_distribution."""
        # lognormal distribution test
        x = 1
        mu = 1
        sigma = 0.25
        prob = exceedance.calculate_exceedance_probability_from_distribution(
            x, 'lognormal', mu, sigma)
        assert prob == 0.6132049428659028

    def test_calculate_exceedance_probability_from_distribution_normal(self):
        # normal distribution test
        x = 1
        mu = 1
        sigma = 0.25
        prob = exceedance.calculate_exceedance_probability_from_distribution(
            x, 'normal', mu, sigma)
        assert prob == 0.5

    def test_calculate_exceedance_probability_from_distribution_weibull(self):
        x = 1
        # Weibull distribution test
        k = 1
        lambda_ = 1
        prob = exceedance.calculate_exceedance_probability_from_distribution(
            x, 'weibull', k, lambda_)
        assert prob == 0.36787944117144233

    def test_calculate_exceedance_probability_from_distribution_exp(self):
        x = 1
        lambda_ = 1
        prob = exceedance.calculate_exceedance_probability_from_distribution(
            x, 'exponential', lambda_)
        assert prob == 1.0

    def test_invalid_exceedance_01(self):
        # Test invalid values
        x = 1
        mu = 1
        sigma = 0.25
        k = 1
        lambda_ = 1
        with pytest.raises(TypeError):
            exceedance.calculate_exceedance_probability_from_distribution(
                x, 'exponential', mu, sigma, k, lambda_)

    def test_invalid_exceedance_02(self):
        # Test invalid values
        x = 1
        mu = 1
        sigma = 0.25
        with pytest.raises(ValueError):
            exceedance.calculate_exceedance_probability_from_distribution(
                x, "invalid", mu, sigma)

    def test_invalid_exceedance_03(self):
        # Test invalid values
        x = 1
        mu = 1
        sigma = 0.25
        with pytest.raises(TypeError):
            exceedance.calculate_exceedance_probability_from_distribution(
                x, 'exponential', mu, sigma, k=1, lambda_=1)

    def test_invalid_exceedance_04(self):
        # Test invalid values
        mu = 1
        sigma = 0.25
        with pytest.raises(TypeError):
            exceedance.calculate_exceedance_probability_from_distribution(
                "invalid", 'exponential', mu, sigma)

    def test_invalid_exceedance_05(self):
        # Test invalid values
        x = 1
        mu = 1
        sigma = 0.25
        with pytest.raises(TypeError):
            exceedance.calculate_exceedance_probability_from_distribution(
                x, 5, mu, sigma)


class TestExceedanceFromValues:
    def test_calculate_exceedance_probability_from_values(self):
        """Test the calculate_exceedance_probability_from_values function."""
        # Testing low value of 1
        x = 1
        values_to_compare = np.array([1, 2, 3, 4])
        prob = exceedance.calculate_exceedance_probability_from_values(
            x, values_to_compare, method='linear')
        assert prob == 1.0

    def test_calculate_exceedance_probability_from_values_list(self):
        values_to_compare = [1, 1, 1, 1]  # use a list
        x = 1
        prob = exceedance.calculate_exceedance_probability_from_values(
            x, values_to_compare, method='linear')
        assert prob == 1.0

    def test_calculate_exceedance_probability_from_values_pandas(self):
        values_to_compare = pd.Series([2, 2, 2, 2])  # use a pandas series
        x = 1
        prob = exceedance.calculate_exceedance_probability_from_values(
            x, values_to_compare, method='linear')
        assert prob == 1.0

    def test_calculate_exceedance_probability_from_values_five(self):
        # Testing high value of 5
        x = 5
        values_to_compare = np.array([1, 2, 3, 4])
        prob = exceedance.calculate_exceedance_probability_from_values(
            x, values_to_compare)
        assert prob == 0.0

    def test_calculate_exceedance_probability_from_values_arr(self):
        values_to_compare = np.array([1, 1, 1, 1])
        x = 5
        prob = exceedance.calculate_exceedance_probability_from_values(
            x, values_to_compare)
        assert prob == 0.0

    def test_calculate_exceedance_probability_from_values_mid(self):
        # Testing middle value of 3
        x = 3
        values_to_compare = np.array([1, 2, 3, 4])
        prob = exceedance.calculate_exceedance_probability_from_values(
            x, values_to_compare)
        assert prob == 0.4

    def test_calculate_exceedance_probability_from_values_mid_arr(self):
        values_to_compare = np.array([1, 1, 1, 1])
        x = 3
        prob = exceedance.calculate_exceedance_probability_from_values(
            x, values_to_compare)
        assert prob == 0.0

    def test_invalid_value_01(self):
        x = 3
        # Testing invalid values
        with pytest.raises(TypeError):
            exceedance.calculate_exceedance_probability_from_values(
                x, "invalid")

    def test_invalid_value_02(self):
        values_to_compare = np.array([1, 1, 1, 1])
        with pytest.raises(TypeError):
            exceedance.calculate_exceedance_probability_from_values(
                "invalid", values_to_compare)

    def test_calculate_exceedance_probability_from_values_weibull(self):
        # Testing weibull (Type 6) method
        x1 = 0.0
        x2 = 2.5
        x3 = 5.0
        values_to_compare = np.array([1, 2, 3, 4])
        prob1 = exceedance.calculate_exceedance_probability_from_values(
            x1, values_to_compare, method='weibull')
        prob2 = exceedance.calculate_exceedance_probability_from_values(
            x2, values_to_compare, method='weibull')
        prob3 = exceedance.calculate_exceedance_probability_from_values(
            x3, values_to_compare, method='weibull')
        assert prob1 == 0.8
        assert prob2 == 0.4
        assert prob3 == 0.0

    def test_calculate_exceedance_probability_from_values_type_4(self):
        # Testing Type 4 ('interpolated_inverted_cdf') method
        x1 = 0.0
        x2 = 2.5
        x3 = 5.0
        values_to_compare = np.array([1, 2, 3, 4])
        prob1 = exceedance.calculate_exceedance_probability_from_values(
            x1, values_to_compare, method='Type 4')
        prob2 = exceedance.calculate_exceedance_probability_from_values(
            x2, values_to_compare, method='Type 4')
        prob3 = exceedance.calculate_exceedance_probability_from_values(
            x3, values_to_compare, method='Type 4')
        assert prob1 == 1.0
        assert prob2 == 0.5
        assert prob3 == 0.0

    def test_calculate_exceedance_probability_from_values_hazen(self):
        # Testing hazen (Type 5) method
        x1 = 0.0
        x2 = 2.5
        x3 = 5.0
        values_to_compare = np.array([1, 2, 3, 4])
        prob1 = exceedance.calculate_exceedance_probability_from_values(
            x1, values_to_compare, method='hazen')
        prob2 = exceedance.calculate_exceedance_probability_from_values(
            x2, values_to_compare, method='hazen')
        prob3 = exceedance.calculate_exceedance_probability_from_values(
            x3, values_to_compare, method='hazen')
        assert prob1 == 0.875
        assert prob2 == 0.375
        assert prob3 == -0.125

    def test_calculate_exceedance_probability_from_values_linear(self):
        # Testing linear (Type 7) method
        x1 = 0.0
        x2 = 2.5
        x3 = 5.0
        values_to_compare = np.array([1, 2, 3, 4])
        prob1 = exceedance.calculate_exceedance_probability_from_values(
            x1, values_to_compare, method='linear')
        prob2 = exceedance.calculate_exceedance_probability_from_values(
            x2, values_to_compare, method='linear')
        prob3 = exceedance.calculate_exceedance_probability_from_values(
            x3, values_to_compare, method='linear')
        assert prob1 == 1.0
        assert prob2 == pytest.approx(1/3)
        assert prob3 == pytest.approx(-1/3)

    def test_calculate_exceedance_probability_from_values_type_8(self):
        # Testing Type 8 ('median_unbiased') method
        x1 = 0.0
        x2 = 2.5
        x3 = 5.0
        values_to_compare = np.array([1, 2, 3, 4])
        prob1 = exceedance.calculate_exceedance_probability_from_values(
            x1, values_to_compare, method='Type 8')
        prob2 = exceedance.calculate_exceedance_probability_from_values(
            x2, values_to_compare, method='Type 8')
        prob3 = exceedance.calculate_exceedance_probability_from_values(
            x3, values_to_compare, method='Type 8')
        assert prob1 == pytest.approx(0.85, rel=0.01)
        assert prob2 == pytest.approx(0.384, rel=0.01)
        assert prob3 == pytest.approx(-0.077, rel=0.01)

    def test_calculate_exceedance_probability_from_values_type_9(self):
        # Testing Type 9 ('normal unbiased') method
        x1 = 0.0
        x2 = 2.5
        x3 = 5.0
        values_to_compare = np.array([1, 2, 3, 4])
        prob1 = exceedance.calculate_exceedance_probability_from_values(
            x1, values_to_compare, method='Type 9')
        prob2 = exceedance.calculate_exceedance_probability_from_values(
            x2, values_to_compare, method='Type 9')
        prob3 = exceedance.calculate_exceedance_probability_from_values(
            x3, values_to_compare, method='Type 9')
        assert prob1 == pytest.approx(0.85, rel=0.01)
        assert prob2 == pytest.approx(0.38, rel=0.01)
        assert prob3 == pytest.approx(-0.088, rel=0.01)

    def test_calculate_exceedance_probability_from_values_error(self):
        # Testing invalid method
        x1 = 0.0
        values_to_compare = np.array([1, 2, 3, 4])
        with pytest.raises(ValueError):
            exceedance.calculate_exceedance_probability_from_values(
                x1, values_to_compare, method='invalid')


class TestExceedanceFromMultiple:
    def test_calculate_exceedance_probability_from_distribution_multiple(self):
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

    def test_calculate_exceedance_probability_from_distribution_multiple_normal(self):  # noqa: E501
        x = 1
        mu = 1
        sigma = 0.25
        prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
            [x], 'normal', mu, sigma)
        prob_single = exceedance.calculate_exceedance_probability_from_distribution(  # noqa: E501
            x, 'normal', mu, sigma)
        assert prob == prob_single

    def test_calculate_exceedance_probability_from_distribution_multiple_weibull(self):  # noqa: E501
        x = 1
        k = 1
        lambda_ = 1
        prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
            [x], 'weibull', k, lambda_)
        prob_single = exceedance.calculate_exceedance_probability_from_distribution(  # noqa: E501
            x, 'weibull', k, lambda_)
        assert prob == prob_single

    def test_calculate_exceedance_probability_from_distribution_multiple_exp(self):  # noqa: E501
        x = 1
        lambda_ = 1
        prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
            [x], 'exponential', lambda_)
        prob_single = exceedance.calculate_exceedance_probability_from_distribution(  # noqa: E501
            x, 'exponential', lambda_)
        assert prob == prob_single

    def test_calculate_exceedance_probability_from_distribution_multiple_lognorm(self):  # noqa: E501
        # Test multiple values for normal and lognormal distributions
        values = np.array([1.0, 1.25, 1.5, 1.75, 2.0])
        mu = 1
        sigma = 0.25
        prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
            values, 'lognormal', mu, sigma)
        assert np.allclose(prob, np.array([0.61320494, 0.5, 0.41171189,
                                           0.34256783, 0.28787077]))

    def test_calculate_exceedance_probability_from_distribution_multiple_norm01(self):  # noqa: E501
        values = np.array([1.0, 1.25, 1.5, 1.75, 2.0])
        mu = 1
        sigma = 0.25
        prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
            values, 'normal', mu, sigma)
        assert np.allclose(prob, np.array([0.5, 0.158655254, 0.0227501319,
                                           0.00134989803, 0.0000316712418]))

    def test_calculate_exceedance_probability_from_distribution_multiple_weibull01(self):  # noqa: E501
        # Test weibull and exponential distributions
        values = np.array([1, 2, 3, 4])
        k = 1
        lambda_ = 1
        prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
            values, 'weibull', k, lambda_)
        assert np.allclose(prob, np.array([0.36787944, 0.13533528,
                                           0.04978707, 0.01831564]))

    def test_calculate_exceedance_probability_from_distribution_multiple_exp01(self):  # noqa: E501
        values = np.array([1, 2, 3, 4])
        lambda_ = 1
        prob = exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
            values, 'exponential', lambda_)
        assert np.allclose(prob, np.array([1., 0.36787944,
                                           0.13533528, 0.04978707]))

    def test_calculate_exceedance_probability_from_distribution_multiple_type_error(self):  # noqa: E501
        values = np.array([1, 2, 3, 4])
        mu = 1
        sigma = 0.25
        k = 1
        lambda_ = 1
        # Test invalid values
        with pytest.raises(TypeError):
            exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
                values, 'exponential', mu, sigma, k, lambda_)

    def test_calculate_exceedance_probability_from_distribution_multiple_value_error(self):  # noqa: E501
        values = np.array([1, 2, 3, 4])
        mu = 1
        sigma = 0.25
        with pytest.raises(ValueError):
            exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
                values, "invalid", mu, sigma)


class TestExceedanceFromValuesMultiple:
    def test_calculate_exceedance_probability_from_values_multiple_01(self):
        """Test calculate_exceedance_probability_from_values_multiple."""
        values = np.array([1, 2, 3, 4])
        values_to_compare = np.array([1, 2, 3, 4])
        prob = exceedance.calculate_exceedance_probability_from_values_multiple(  # noqa: E501
            values, values_to_compare, method='Type 4')
        assert np.allclose(prob, np.array([1.0, 0.75, 0.5, 0.25]))

    def test_calculate_exceedance_probability_from_values_multiple_02(self):
        values = np.array([1, 2, 3, 4])
        values_to_compare = np.array([1, 1, 1, 1])
        prob = exceedance.calculate_exceedance_probability_from_values_multiple(  # noqa: E501
            values, values_to_compare, method='Type 4')
        assert np.allclose(prob, np.array([1.0, 0.0, 0.0, 0.0]))

    def test_calculate_exceedance_probability_from_values_multiple_03(self):
        values = np.array([1, 2, 3, 4])
        values_to_compare = np.array([2, 2, 2, 2])
        prob = exceedance.calculate_exceedance_probability_from_values_multiple(  # noqa: E501
            values, values_to_compare, method='Type 4')
        assert np.allclose(prob, np.array([1.0, 1.0, 0.0, 0.0]))

    def test_calculate_exceedance_probability_from_values_multiple_04(self):
        values = np.array([1, 2, 3, 4])
        values_to_compare = np.array([1, 2, 3, 4, 1, 2, 3, 4])
        prob = exceedance.calculate_exceedance_probability_from_values_multiple(  # noqa: E501
            values, values_to_compare, method='Type 4')
        assert np.allclose(prob, np.array([1.0, 0.75, 0.5, 0.25]))

    def test_calculate_exceedance_probability_from_values_multiple_05(self):
        values = np.array([1, 2, 3, 4])
        values_to_compare = np.array([1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4])
        prob = exceedance.calculate_exceedance_probability_from_values_multiple(  # noqa: E501
            values, values_to_compare, method='Type 4')
        assert np.allclose(prob, np.array([1.0, 0.75, 0.5, 0.25]))
