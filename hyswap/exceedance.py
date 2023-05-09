"""Exceedance probability calculations."""

import numpy as np
import pandas as pd
from scipy import stats


def calculate_exceedance_probability_from_distribution(x, dist,
                                                       *args, **kwargs):
    """
    Calculate the exceedance probability of a value relative to a distribution.

    Parameters
    ----------
    x : float
        The value for which to calculate the exceedance probability.
    dist : str
        The distribution to use. Must be one of 'lognormal', 'normal',
        'weibull', or 'exponential'.
    *args
        Positional arguments to pass to the distribution, which is one of
        `stats.lognorm.sf`, `stats.norm.sf`, `stats.exponweib.sf` or
        `stats.expon.sf`, refer to the `scipy.stats` documentation for more
        information about these arguments.
    **kwargs
        Keyword arguments to pass to the distribution, which is one of
        `stats.lognorm.sf`, `stats.norm.sf`, `stats.exponweib.sf` or
        `stats.expon.sf`, refer to the `scipy.stats` documentation for more
        information about these arguments.

    Returns
    -------
    float
        The exceedance probability.

    Examples
    --------
    Calculating the exceedance probability of a value of 1 from a lognormal
    distribution with a mean of 1 and a standard deviation of 0.25.

    .. doctest::

        >>> exceedance.calculate_exceedance_probability_from_distribution(
        ...     1, 'lognormal', 1, 0.25)
        0.6132049428659028

    Calculating the exceedance probability of a value of 1 from a normal
    distribution with a mean of 1 and a standard deviation of 0.25.

    .. doctest::

        >>> exceedance.calculate_exceedance_probability_from_distribution(
        ...     1, 'normal', 1, 0.25)
        0.5
    """
    # type check
    if not isinstance(x, (int, float, np.int64, np.float64, np.float32,
                          np.float16, np.int32, np.int16, np.int8)):
        raise TypeError("x must be a float (or integer).")
    if not isinstance(dist, str):
        raise TypeError("dist must be a string.")
    # do calculation
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
    Calculate the exceedance probability of a value compared to several values.

    This function specifically counts the number of values from the input
    `values_to_compare` that are *greater than or equal to* the input value
    `x`. The choice of greater than or equal, as opposed to solely greater than
    is intentional and follows established USGS practices [1]_.

    .. [1] Searcy, J. K. "Flow-duration curves: Water Supply Paper 1542-A."
           US Geological Survey, Reston, VA (1959).

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

    Examples
    --------
    Calculating the exceedance probability of a value of 1 from a set of values
    of 1, 2, 3, and 4.

    .. doctest::

        >>> exceedance.calculate_exceedance_probability_from_values(
        ...     1, [1, 2, 3, 4])
        1.0

    Calculating the exceedance probability of a value of 5 from a set of values
    of 1, 2, 3, and 4.

    .. doctest::

        >>> exceedance.calculate_exceedance_probability_from_values(
        ...     5, [1, 2, 3, 4])
        0.0
    """
    # some type conversions to get to a numpy array
    if isinstance(values_to_compare, list):
        values_to_compare = np.array(values_to_compare)
    elif isinstance(values_to_compare, pd.Series):
        values_to_compare = values_to_compare.values
    # raise error if not a numpy array
    if not isinstance(values_to_compare, np.ndarray):
        raise TypeError("values_to_compare must be a numpy array, list, " +
                        "or pandas Series.")
    # calculate the exceedance probability
    return np.sum(values_to_compare >= x) / len(values_to_compare)


def calculate_exceedance_probability_from_distribution_multiple(values, dist,
                                                                *args,
                                                                **kwargs):
    """
    Calculate the exceedance probability of multiple values vs a distribution.

    Parameters
    ----------
    values : array-like
        The values for which to calculate the exceedance probability.
    dist : str
        The distribution to use. Must be one of 'lognormal', 'normal',
        'weibull', or 'exponential'.
    *args
        Positional arguments to pass to the distribution, which is one of
        `stats.lognorm.sf`, `stats.norm.sf`, `stats.exponweib.sf` or
        `stats.expon.sf`, refer to the `scipy.stats` documentation for more
        information about these arguments.
    **kwargs
        Keyword arguments to pass to the distribution, which is one of
        `stats.lognorm.sf`, `stats.norm.sf`, `stats.exponweib.sf` or
        `stats.expon.sf`, refer to the `scipy.stats` documentation for more
        information about these arguments.

    Returns
    -------
    array-like
        The exceedance probabilities.

    Examples
    --------
    Calculating the exceedance probability of a set of values of 1, 1.25 and
    1.5 from a lognormal distribution with a mean of 1 and a standard
    deviation of 0.25.

    .. doctest::

        >>> exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        ...     [1, 1.25, 1.5], 'lognormal', 1, 0.25)
        array([0.61320494, 0.5       , 0.41171189])

    Calculating the exceedance probability of a set of values of 1, 2, 3, and 4
    from a normal distribution with a mean of 1 and a standard deviation of
    0.25.

    .. doctest::

        >>> exceedance.calculate_exceedance_probability_from_distribution_multiple(  # noqa: E501
        ...     [1, 2, 3, 4], 'normal', 1, 0.25)
        array([5.00000000e-01, 3.16712418e-05, 6.22096057e-16, 1.77648211e-33])
    """
    return np.array([calculate_exceedance_probability_from_distribution(
        x, dist, *args, **kwargs) for x in values])


def calculate_exceedance_probability_from_values_multiple(values,
                                                          values_to_compare):
    """
    Calculate the exceedance probability of multiple values vs a set of values.

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

    Examples
    --------
    Calculating the exceedance probability of a set of values of 1, 1.25 and
    1.5 from a set of values of 1, 2, 3, and 4.

    .. doctest::

        >>> exceedance.calculate_exceedance_probability_from_values_multiple(
        ...     [1, 1.25, 2.5], [1, 2, 3, 4])
        array([1.  , 0.75, 0.5 ])

    Fetch some data from NWIS and calculate the exceedance probability for a
    set of 5 values spaced evenly between the minimum and maximum values.

    .. doctest::
        :skipif: True  # skips this block of code as it broke CI pipeline

        >>> df, _ = dataretrieval.nwis.get_gwlevels(site='434400121275801',
        ...                                         start='2000-01-01',
        ...                                         end='2020-01-01')
        >>> values = np.linspace(df['lev_va'].min(),
        ...                      df['lev_va'].max(), 5)
        >>> exceedance.calculate_exceedance_probability_from_values_multiple(
        ...     values, df['lev_va'])
        array([1.        , 0.96363636, 0.83636364, 0.47272727, 0.01818182])
    """
    return np.array([calculate_exceedance_probability_from_values(
        x, values_to_compare) for x in values])
