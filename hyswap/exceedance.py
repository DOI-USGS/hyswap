"""Exceedance probability calculations."""

import numpy as np
from scipy import stats


def calculate_exceedance_probability_from_distribution(x, dist,
                                                       *args, **kwargs):
    """
    Calculate the exceedance probability of a value.

    Parameters
    ----------
    x : float
        The value for which to calculate the exceedance probability.
    dist : str
        The distribution to use. Must be one of 'lognormal', 'normal',
        'weibull', or 'exponential'.
    *args
        Positional arguments to pass to the distribution.
    **kwargs
        Keyword arguments to pass to the distribution.

    Returns
    -------
    float
        The exceedance probability.
    """
    if dist == 'lognormal':
        return stats.lognorm.sf(x, *args, **kwargs)
    elif dist == 'normal':
        return stats.norm.sf(x, *args, **kwargs)
    elif dist == 'weibull':
        return stats.exponweib.sf(x, *args, **kwargs)
    elif dist == 'exponential':
        return stats.expon.sf(x, *args, **kwargs)
    else:
        raise ValueError("dist must be one of 'lognormal', 'normal'," +
                         "'weibull', or 'exponential'.")


def calculate_exceedance_probability_from_values(x, values_to_compare):
    """
    Calculate the exceedance probability of a value.

    Parameters
    ----------
    x : float
        The value for which to calculate the exceedance probability.
    values_to_compare : array-like
        The values to use to calculate the exceedance probability.

    Returns
    -------
    float
        The exceedance probability.
    """
    return np.sum(values_to_compare >= x) / len(values_to_compare)


def calculate_exceedance_probability_from_distribution_multiple(values, dist,
                                                                *args,
                                                                **kwargs):
    """
    Calculate the exceedance probability of multiple values.

    Parameters
    ----------
    values : array-like
        The values for which to calculate the exceedance probability.
    dist : str
        The distribution to use. Must be one of 'lognormal', 'normal',
        'weibull', or 'exponential'.
    *args
        Positional arguments to pass to the distribution.
    **kwargs
        Keyword arguments to pass to the distribution.

    Returns
    -------
    array-like
        The exceedance probabilities.
    """
    return np.array([calculate_exceedance_probability_from_distribution(
        x, dist, *args, **kwargs) for x in values])


def calculate_exceedance_probability_from_values_multiple(values,
                                                          values_to_compare):
    """
    Calculate the exceedance probability of multiple values.

    Parameters
    ----------
    values : array-like
        The values for which to calculate the exceedance probability.
    values_to_compare : array-like
        The values to use to calculate the exceedance probability.

    Returns
    -------
    array-like
        The exceedance probabilities.
    """
    return np.array([calculate_exceedance_probability_from_values(
        x, values_to_compare) for x in values])
