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
        :skipif: True  # docstrings test fails with np.float64

        >>> exceedance.calculate_exceedance_probability_from_distribution(
        ...     1, 'lognormal', 1, 0.25)
        0.6132049428659028

    Calculating the exceedance probability of a value of 1 from a normal
    distribution with a mean of 1 and a standard deviation of 0.25.

    .. doctest::
        :skipif: True  # docstrings test fails with np.float64

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


def calculate_exceedance_probability_from_values(x, values_to_compare,
                                                 method="weibull"):
    """
    Calculate the exceedance probability of a value compared to several values.

    This function computes an exceedance probability using common plotting
    position formulas, with the default being the 'Weibull' method (also known
    as Type 6 in R). The value (x) is ranked among the values to compare by
    determining the number that are *greater than or equal to* the
    input value (x), which provides the minimum rank in the case of tied
    values. Additional methods other than the 'Weibull' method can be specified
    and are described in more detail in Helsel et al 2020.

    Helsel, D.R., Hirsch, R.M., Ryberg, K.R., Archfield, S.A.,
      and Gilroy, E.J., 2020, Statistical methods in water resources:
      U.S. Geological Survey Techniques and Methods, book 4, chap. A3,
      458 p., https://doi.org/10.3133/tm4a3. [Supersedes USGS Techniques
      of Water-Resources Investigations, book 4, chap. A3, version 1.1.]

    Parameters
    ----------
    x : float
        The value for which to calculate the exceedance probability.
    values_to_compare : array-like
        The values to use to calculate the exceedance probability.

    method : str, optional
        Method (formulation) of plotting position formula.
        Default is 'weibull' (Type 6). Additional available methods are
        'interpolated_inverted_cdf' (Type 4), 'hazen' (Type 5),
        'linear' (Type 7), 'median_unbiased' (Type 8), and 'normal_unbiased'
        (Type 9).

    Returns
    -------
    float
        The exceedance probability.

    Examples
    --------
    Calculating the exceedance probability of a value of 1 from a set of values
    of 1, 2, 3, and 4.

    .. doctest::
        :skipif: True  # docstrings test fails with np.float64

        >>> exceedance.calculate_exceedance_probability_from_values(
        ...     1, [1, 2, 3, 4], method='linear')
        1.0

    Calculating the exceedance probability of a value of 5 from a set of values
    of 1, 2, 3, and 4.

    .. doctest::
        :skipif: True  # docstrings test fails with np.float64

        >>> exceedance.calculate_exceedance_probability_from_values(
        ...     5, [1, 2, 3, 4])
        0.0

    Fetch some data from NWIS and calculate the exceedance probability
    for a value of 300 cfs. This is close to the maximum stream flow
    value for this gage and date range, so the exceedance probability
    is very small.

    .. doctest::
        :skipif: True  # skips this block of code as it broke CI pipeline

        >>> df, _ = dataretrieval.nwis.get_dv(
        ...    site='10171000',
        ...    start='2000-01-01',
        ...    end='2020-01-01')
        >>> np.round(
        ...    exceedance.calculate_exceedance_probability_from_values(
        ...        300, df['00060_Mean']),
        ...        6)
        0.000137
    """

    if method in ['weibull', 'Type 6']:
        alpha = 0
        beta = 0
    elif method in ['interpolated_inverted_cdf', 'Type 4']:
        alpha = 0
        beta = 1
    elif method in ['hazen', 'Type 5']:
        alpha = 0.5
        beta = 0.5
    elif method in ['linear', 'Type 7']:
        alpha = 1
        beta = 1
    elif method in ['median_unbiased', 'Type 8']:
        alpha = 1/3
        beta = 1/3
    elif method in ['normal_unbiased', 'Type 9']:
        alpha = 3/8
        beta = 3/8
    else:
        raise ValueError("method type not recognized")

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
    exceed_prob = (np.sum(values_to_compare >= x) - alpha) / (len(values_to_compare) + 1 - alpha - beta)  # noqa: E501

    return exceed_prob


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
                                                          values_to_compare,
                                                          method="weibull"):
    """
    Calculate the exceedance probability of multiple values vs a set of values.
    All methods supported in *calculate_exceedance_probability_from_values*
    are supported and by default uses the 'Weibull' method.

    Parameters
    ----------
    values : array-like
        The values for which to calculate the exceedance probability.
    values_to_compare : array-like
        The values to use to calculate the exceedance probability.
    method : str, optional
        Method (formulation) of plotting position formula.
        Default is 'weibull' (Type 6). Additional available methods are
        'interpolated_inverted_cdf' (Type 4), 'hazen' (Type 5),
        'linear' (Type 7), 'median_unbiased' (Type 8), and 'normal_unbiased'
        (Type 9).

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
        ...     [1, 1.25, 2.5], [1, 2, 3, 4], method='Type 4')
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
        x, values_to_compare, method=method) for x in values])
