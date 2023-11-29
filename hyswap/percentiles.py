"""Percentile calculation functions."""

import numpy as np
import pandas as pd
import warnings
from datetime import datetime
from hyswap.utils import filter_data_by_time
from hyswap.utils import calculate_metadata
from hyswap.utils import define_year_doy_columns
from hyswap.utils import set_data_type
from hyswap.utils import rolling_average


def calculate_fixed_percentile_thresholds(
        data,
        percentiles=np.array((0, 5, 10, 25, 75, 90, 95, 100)),
        method='weibull',
        ignore_na=True,
        **kwargs):
    """Calculate fixed percentile thresholds using historic data.

    Parameters
    ----------
    data : array_like
        1D array of data from which to calculate percentile thresholds.

    percentiles : array_like, optional
        Percentiles to calculate. Default is (0, 5, 10, 25, 75, 90, 95, 100).

    method : str, optional
        Method to use to calculate percentiles. Default is 'weibull'.

    ignore_na : bool, optional
        Ignore NA values in percentile calculations

    **kwargs : dict, optional
        Additional keyword arguments to pass to `numpy.percentile`.

    Returns
    -------
    percentiles : pandas.DataFrame
        Percentiles of the data in a DataFrame so the thresholds and
        percentile values are tied together.

    Examples
    --------
    Calculate default percentile thresholds from some synthetic data.

    .. doctest::

        >>> data = np.arange(101)
        >>> results = percentiles.calculate_fixed_percentile_thresholds(
        ...     data, method='linear')
        >>> results
        thresholds  0    5     10    25    75    90    95     100
        values      0.0  5.0  10.0  25.0  75.0  90.0  95.0  100.0

    Calculate a different set of thresholds from some synthetic data.

    .. doctest::

        >>> data = np.arange(101)
        >>> results = percentiles.calculate_fixed_percentile_thresholds(
        ...     data, percentiles=np.array((0, 10, 50, 90, 100)))
        >>> results
        thresholds  0    10    50    90     100
        values      0.0  9.2  50.0  90.8  100.0
    """
    if ignore_na:
        pct = np.nanpercentile(data, percentiles, method=method, **kwargs)
    else:
        pct = np.percentile(data, percentiles, method=method, **kwargs)
    df = pd.DataFrame(data={"values": pct}, index=percentiles).T
    df = df.rename_axis("thresholds", axis="columns")
    return df


def calculate_variable_percentile_thresholds_by_day(
        df,
        data_column_name,
        percentiles=[0, 5, 10, 25, 75, 90, 95, 100],
        method='weibull',
        date_column_name=None,
        data_type='daily',
        year_type='calendar',
        min_years=10,
        leading_values=0,
        trailing_values=0,
        ignore_na=True,
        **kwargs):
    """Calculate variable percentile thresholds of data by day of year.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing data to calculate daily percentile thresholds for.

    data_column_name : str
        Name of column containing data to analyze.

    percentiles : array_like, optional
        Percentile thresholds to calculate, default is
        [0, 5, 10, 25, 75, 90, 95, 100].

    method : str, optional
        Method to use to calculate percentiles. Default is 'weibull'.

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    data_type : str, optional
        The type of data. Must be one of 'daily', '7-day', '14-day', and
        '28-day'. Default is 'daily'. If '7-day', '14-day', or '28-day' is
        specified, the data will be averaged over the specified period. NaN
        values will be used for any days that do not have data. If present,
        NaN values will result in NaN values for the entire period.

    year_type : str, optional
        The type of year to use. Must be one of 'calendar', 'water', or
        'climate'. Default is 'calendar' which starts the year on January 1
        and ends on December 31. 'water' starts the year on October 1 and
        ends on September 30 of the following year which is the "water year".
        For example, October 1, 2010 to September 30, 2011 is "water year
        2011". 'climate' years begin on April 1 and end on March 31 of the
        following year, they are numbered by the ending year. For example,
        April 1, 2010 to March 31, 2011 is "climate year 2011".

    min_years : int, optional
        Minimum number of years of data required to calculate percentile
        thresholds for a given day of year. Default is 10.

    leading_values : int, optional
        For the temporal filtering, this is an argument setting the
        number of leading values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    trailing_values : int, optional
        For the temporal filtering, this is an argument setting the
        number of trailing values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    ignore_na : bool, optional
        Ignore NA values in percentile calculations

    **kwargs : dict, optional
        Additional keyword arguments to pass to `numpy.percentile`.

    Returns
    -------
    percentiles : pandas.DataFrame
        DataFrame containing threshold percentiles of data by day of year.
        Will return a DataFrame of NaNs for each percentile/day if
        provided an empty DataFrame or DataFrame with insufficient data

    Examples
    --------
    Calculate default thresholds by day of year from some real data in
    preparation for plotting.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> df, _ = dataretrieval.nwis.get_dv(
        ...     "03586500", parameterCd="00060",
        ...     start="1776-01-01", end="2022-12-31")
        >>> results = percentiles.calculate_variable_percentile_thresholds_by_day(  # noqa: E501
        ...     df, "00060_Mean")
        >>> len(results.index)  # 366 days in a leap year
        366
        >>> len(results.columns)  # 8 default percentiles
        8
    """
    # If the dataframe is empty, create a dummy dataframe to
    # run through function
    if df.empty:
        warnings.warn('No valid data provided, returning NA values for percentile thresholds')  # noqa: E501
        date_rng = pd.date_range(start='1900-01-01', end='1900-12-31')
        df = pd.DataFrame(index=date_rng)
        df[data_column_name] = np.nan

    # If data column name is not in dataframe
    if data_column_name not in df:
        warnings.warn('DataFrame missing data_column_name, returning NA values for percentile thresholds')  # noqa: E501
        date_rng = pd.date_range(start='1900-01-01', end='1900-12-31')
        df = pd.DataFrame(index=date_rng)
        df[data_column_name] = np.nan

    # define year and day of year columns and convert date column to datetime
    # if necessary
    df = define_year_doy_columns(df, date_column_name=date_column_name,
                                 year_type=year_type, clip_leap_day=True)
    # do rolling average for time as needed
    data_type = set_data_type(data_type)
    df = rolling_average(df, data_column_name, data_type)
    # based on date, get min and max day of year available
    min_day = np.nanmax((1, df.index.dayofyear.min()))
    max_day = np.nanmin((366, df.index.dayofyear.max() + 1))
    # make temporal index
    t_idx = np.arange(min_day, max_day)
    # initialize a DataFrame to hold percentiles by day of year
    percentiles_by_day = pd.DataFrame(index=t_idx, columns=percentiles)
    # loop through days of year available
    for doy in range(min_day, max_day):
        # get historical data for the day of year
        data = filter_data_by_time(df, doy, data_column_name,
                                   leading_values=leading_values,
                                   trailing_values=trailing_values,
                                   drop_na=ignore_na)
        if not data.empty:
            if not np.isnan(data).all():
                meta = calculate_metadata(data)
                # only calculate data if there are at least min_years of data
                # that are not nan
                if meta['n_years'] - meta['n_nans'] >= min_years:
                    # calculate percentiles for the day of year
                    # and add to DataFrame
                    _pct = calculate_fixed_percentile_thresholds(
                        data, percentiles=percentiles, method=method,
                        ignore_na=ignore_na, **kwargs)
                    percentiles_by_day.loc[t_idx == doy, :] = _pct.values.tolist()[0]  # noqa: E501
                else:
                    # if there are not at least 'min_years' of data,
                    # set percentiles to NaN
                    percentiles_by_day.loc[t_idx == doy, :] = np.nan
            else:
                # if all values are NA
                # set percentiles to NaN
                percentiles_by_day.loc[t_idx == doy, :] = np.nan
        else:
            # if the data subset for doy is empty
            # set percentiles to NaN
            percentiles_by_day.loc[t_idx == doy, :] = np.nan
    # replace index with multi-index of doy_index and month-day values
    # month_day values
    month_day = pd.to_datetime(
        percentiles_by_day.index, format='%j').strftime('%m-%d')
    # doy_index values
    doy_index = percentiles_by_day.index.values
    if year_type == 'water':
        doy_index = doy_index - 273
        doy_index[doy_index < 1] += 365
    elif year_type == 'climate':
        doy_index = doy_index - 90
        doy_index[doy_index < 1] += 365
    percentiles_by_day.index = pd.MultiIndex.from_arrays(
        [doy_index, month_day], names=['doy', 'month-day'])

    # sort percentiles by index
    percentiles_by_day.sort_index(inplace=True)

    # return percentiles by day of year
    return percentiles_by_day


def calculate_fixed_percentile_from_value(value, percentile_df):
    """Calculate percentile from a value and fixed percentile thresholds.

    This function enables faster calculation of the percentile associated with
    a given value if percentile values and corresponding fixed percentile
    thresholds are known from other data from the same station or site.
    This calculation is done using linear interpolation.

    Parameters
    ----------
    value : float, np.ndarray
        New value(s) to calculate percentile for. Can be a single value or an
        array of values.

    percentile_df : pd.DataFrame
        DataFrame where columns are the percentile thresholds values and the
        values are stored in a row called "values". Typically generated by the
        `calculate_fixed_percentile_thresholds` functions but could be
        provided manually or from data pulled from the NWIS stats service.

    Returns
    -------
    percentile : float, np.ndarray
        Percentile associated with the input value(s).

    Examples
    --------
    Calculate the percentile associated with a value from some synthetic data.

    .. doctest::

        >>> data = np.arange(1001)
        >>> pcts_df = percentiles.calculate_fixed_percentile_thresholds(
        ...     data, percentiles=[0, 5, 10, 25, 75, 90, 95, 100],
        ...     method='linear')
        >>> new_percentile = percentiles.calculate_fixed_percentile_from_value(
        ...     500, pcts_df)
        >>> new_percentile
        50.0

    Calculate the percentiles associated with multiple values for some data
    downloaded from NWIS.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> data, _ = dataretrieval.nwis.get_dv(
        ...     "04288000", parameterCd="00060",
        ...     start="1900-01-01", end="2021-12-31")
        >>> pcts_df = percentiles.calculate_fixed_percentile_thresholds(
        ...     data['00060_Mean'],
        ...     percentiles=[0, 5, 10, 25, 75, 90, 95, 100],
        ...     method='linear')
        >>> new_data, _ = dataretrieval.nwis.get_dv(
        ...     "04288000", parameterCd="00060",
        ...     start="2022-01-01", end="2022-01-07")
        >>> new_data['est_pct'] = percentiles.calculate_fixed_percentile_from_value(  # noqa: E501
        ...     new_data['00060_Mean'], pcts_df)
        >>> new_data['est_pct'].to_list()
        [58.41, 75.0, 48.45, 39.16, 45.58, 48.01, 42.04]

    """
    # define values
    thresholds = percentile_df.columns.tolist()
    percentile_values = percentile_df.values.tolist()[0]
    # do and return linear interpolation
    return np.interp(value, percentile_values, thresholds).round(2)


def calculate_variable_percentile_from_value(value, percentile_df, mo_day):
    """Calculate percentile from a value and variable percentile thresholds.

    This function enables faster calculation of the percentile associated with
    a given value for a single day of the year if percentile values and
    corresponding variable percentile thresholds are known from other data from
    the same station or site. This calculation is done using linear
    interpolation.

    Parameters
    ----------
    value : float, np.ndarray
        New value(s) to calculate percentile for. Can be a single value or an
        array of values.

    percentile_df : pd.DataFrame
        DataFrame containing threshold percentiles of data by day of year.
        Typically generated by the `calculate_variable_percentile_thresholds`
        function but could be provided manually or from data pulled from the
        NWIS stats service.

    mo_day : str
        string of month-day of year to lookup percentile thresholds for value

    Returns
    -------
    percentile : float, np.ndarray
        Percentile associated with the input value(s).

    Examples
    --------
    Calculate the percentile associated with a value using flow records
    downloaded from NWIS.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> data, _ = dataretrieval.nwis.get_dv(
        ...     "03586500", parameterCd="00060",
        ...     start="1776-01-01", end="2022-12-31")
        >>> pcts_df = percentiles.calculate_variable_percentile_thresholds_by_day(  # noqa: E501
        ...     data, '00060_Mean',
        ...     percentiles=[0, 5, 10, 25, 75, 90, 95, 100],
        ...     method='linear')
        >>> new_percentile = percentiles.calculate_variable_percentile_from_value(  # noqa: E501
        ...     500, pcts_df, '06-30')
        >>> new_percentile
        96.21
    """
    # retrieve percentile thresholds for the day of year of interest
    pct_values = percentile_df.loc[percentile_df.index.get_level_values('month-day') == mo_day]  # noqa: E501

    if not pct_values.empty:
        pct_values = pct_values.reset_index(drop=True)
        pct_values = pct_values.rename(index={0: "values"})
        # define values
        thresholds = pct_values.columns.tolist()
        percentile_values = pct_values.values.tolist()[0]
        # do and return linear interpolation
        est_pct = np.interp(value, percentile_values, thresholds).round(2)
    else:
        # return NaN if no threshold values are provided
        est_pct = np.nan

    return est_pct


def calculate_multiple_variable_percentiles_from_values(df, data_column_name,
                                                        percentile_df,
                                                        date_column_name=None):
    """Calculate variable percentiles for multiple values

    This function enables calculation of estimated percentiles for multiple
    values across multiple days of the year using existing variable percentile
    thresholds.

    Parameters
    ----------
    df : pd.DataFrame
        Pandas dataframe containing new values to calculate percentiles for.

    data_column_name : str
        Name of column containing data to analyze.

    percentile_df : pd.DataFrame
        DataFrame containing threshold percentiles of data by day of year.
        Typically generated by the `calculate_variable_percentile_thresholds`
        functions but could be provided manually or from data pulled from the
        NWIS stats service.

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    Returns
    -------
    df : pd.DataFrame
        Pandas dataframe of values with estimated percentile column added

    Examples
    --------
    Calculate the percentiles associated with multiple values using flow
    records downloaded from NWIS.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> data, _ = dataretrieval.nwis.get_dv(
        ...     "04288000", parameterCd="00060",
        ...     start="1900-01-01", end="2021-12-31")
        >>> pcts_df = percentiles.calculate_variable_percentile_thresholds_by_day(  # noqa: E501
        ...     data, '00060_Mean',
        ...     percentiles=[0, 5, 10, 25, 75, 90, 95, 100],
        ...     method='linear')
        >>> new_data, _ = dataretrieval.nwis.get_dv(
        ...     "04288000", parameterCd="00060",
        ...     start="2022-01-01", end="2022-01-07")
        >>> new_percentiles = percentiles.calculate_multiple_variable_percentiles_from_values(  # noqa: E501
        ...     new_data, '00060_Mean', pcts_df)
        >>> new_percentiles['est_pct'].to_list()
        [59.59, 77.7, 47.5, 37.5, 50.0, 55.77, 48.71]
    """
    if date_column_name is None:
        date_column_name = 'datetime'

    df = df.reset_index()
    df['est_pct'] = df.apply(lambda row: calculate_variable_percentile_from_value(  # noqa: E501
        row[data_column_name], percentile_df,
        datetime.strftime(row[date_column_name], '%m-%d')), axis=1)
    df['est_pct'] = df['est_pct'].round(2)
    df = df.set_index(date_column_name)

    return df
