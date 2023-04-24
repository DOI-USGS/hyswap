"""Percentile calculation functions."""

import numpy as np
import pandas as pd
from hyswap.utils import filter_data_by_day


def calculate_historic_percentiles(
        data, percentiles=np.array((0, 5, 10, 25, 75, 90, 95, 100)),
        **kwargs):
    """Calculate percentiles of historic data.

    Parameters
    ----------
    data : array_like
        1D array of data from which to calculate percentiles.

    percentiles : array_like, optional
        Percentiles to calculate. Default is (0, 5, 10, 25, 75, 90, 95, 100).

    **kwargs : dict, optional
        Additional keyword arguments to pass to `numpy.percentile`.

    Returns
    -------
    percentiles : array_like
        Percentiles of the data.

    Examples
    --------
    Calculate default percentiles from some synthetic data.

    .. doctest::

        >>> data = np.arange(101)
        >>> results = percentiles.calculate_historic_percentiles(data)
        >>> results
        array([  0.,   5.,  10.,  25.,  75.,  90.,  95., 100.])

    Calculate a different set of percentiles from some synthetic data.

    .. doctest::

        >>> data = np.arange(101)
        >>> results = percentiles.calculate_historic_percentiles(
        ...     data, percentiles=np.array((0, 10, 50, 90, 100)))
        >>> results
        array([  0.,  10.,  50.,  90., 100.])
    """
    return np.percentile(data, percentiles, **kwargs)


def calculate_percentiles_by_day(
        df, data_column_name,
        percentiles=np.array((0, 5, 10, 25, 75, 90, 95, 100)),
        date_column_name=None):
    """Calculate percentiles of data by day of year.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing data to calculate daily percentiles for.

    data_column_name : str
        Name of column containing data to analyze.

    percentiles : array_like, optional
        Percentiles to calculate, default is (0, 5, 10, 25, 75, 90, 95, 100).

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    Returns
    -------
    percentiles : pandas.DataFrame
        DataFrame containing percentiles of data by day of year.

    Examples
    --------
    Calculate default percentiles by day of year from some real data in
    preparation for plotting.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> df, _ = dataretrieval.nwis.get_dv(
        ...     "03586500", parameterCd="00060",
        ...     start="1776-01-01", end="2022-12-31")
        >>> results = percentiles.calculate_percentiles_by_day(
        ...     df, "00060_Mean")
        >>> len(results.index)  # 366 days in a leap year
        366
        >>> len(results.columns)  # 8 default percentiles
        8
    """
    # based on date, get min and max day of year available
    if date_column_name is None:
        min_day = df.index.dayofyear.min()
        max_day = df.index.dayofyear.max() + 1
    else:
        min_day = df[date_column_name].dt.dayofyear.min()
        max_day = df[date_column_name].dt.dayofyear.max() + 1
    # make temporal index
    t_idx = np.arange(min_day, max_day)
    # initialize a DataFrame to hold percentiles by day of year
    percentiles_by_day = pd.DataFrame(
        index=t_idx, columns=percentiles
    )
    # loop through days of year available
    for doy in range(min_day, max_day):
        # get historical data for the day of year
        data = filter_data_by_day(df, doy, data_column_name,
                                  date_column_name=date_column_name)
        # could insert other functions here to check or modify data
        # as needed or based on any other criteria

        # calculate percentiles for the day of year and add to DataFrame
        percentiles_by_day.loc[t_idx == doy, :] = \
            calculate_historic_percentiles(data, percentiles=percentiles)

    # return percentiles by day of year
    return percentiles_by_day
