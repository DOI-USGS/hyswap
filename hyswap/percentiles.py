"""Percentile calculation functions."""

import numpy as np
import pandas as pd
import warnings
from datetime import datetime
from hyswap.utils import filter_data_by_month_day
from hyswap.utils import filter_data_by_time
from hyswap.utils import define_year_doy_columns
from hyswap.utils import set_data_type
from hyswap.utils import rolling_average
from hyswap.exceedance import calculate_exceedance_probability_from_values


def calculate_fixed_percentile_thresholds(
        data,
        data_column_name=None,
        percentiles=np.array((5, 10, 25, 50, 75, 90, 95)),
        method='weibull',
        date_column_name=None,
        ignore_na=True,
        include_min_max=True,
        include_metadata=True,
        mask_out_of_range=True,
        **kwargs):
    """Calculate fixed percentile thresholds using historical data.

    Parameters
    ----------
    data : pandas.DataFrame or array-like
        DataFrame, Series, or 1-D array containing data used to calculate
        percentile thresholds. If DataFrame, "data_column_name" must be
        specified and expects a datetime index unless "date_column_name" is
        provided. If Series, must include a datetime index. If 1-D array, then
        "include_metadata" must be set to False since a datetime index is not
        included with data.

    data_column_name : str, optional
        Name of column containing data to analyze if input is a DataFrame.
        Default is None.

    percentiles : array_like, optional
        Percentiles to calculate. Default is (5, 10, 25, 50, 75, 90, 95).
        Note: Values of 0 and 100 are ignored as unbiased plotting position
        formulas do not assign values to 0 or 100th percentile.

    method : str, optional
        Method to use to calculate percentiles. Default is 'weibull' (Type 6).
        Additional available methods are 'interpolated_inverted_cdf' (Type 4),
        'hazen' (Type 5), 'linear' (Type 7), 'median_unbiased' (Type 8),
        and 'normal_unbiased' (Type 9).

    date_column_name : str, optional
        For data provided as DataFrame, name of column containing date
        information. If None, the index of `data` is used.

    ignore_na : bool, optional
        Ignore NA values in percentile calculations

    include_min_max : bool, optional
        When set to True, include min and max streamflow value in addition to
        streamflow values for percentile levels. Default is True.

    include_metadata : bool, optional
        When set to True, return additional columns describing the data
        including count, mean, start_yr, end_yr. Default is True. Input data
        must include a datetime column as either index or specified by
        date_column_name.

    mask_out_of_range :  bool, optional
        When set to True, percentiles that are beyond the min/max percentile
        ranks of the observed data to be NA. Effect of this being enables is
        that high or low percentiles may not be calculated when few data points
        are available. Default is True.

    **kwargs : dict, optional
        Additional keyword arguments to pass to `numpy.percentile`.

    Returns
    -------
    percentiles : pandas.DataFrame
        Percentiles of the data in a DataFrame so the thresholds and
        percentile values are tied together.

    Examples
    --------
    Calculate percentile thresholds from some synthetic data using 'linear'
    method.

    .. doctest::

        >>> data = pd.DataFrame({'values': np.arange(101),
        ...                      'date': pd.date_range('2020-01-01', '2020-04-10')}).set_index('date')  # noqa: E501
        >>> results = percentiles.calculate_fixed_percentile_thresholds(
        ...     data, 'values', percentiles=[25, 75, 95], method='linear')
        >>> results
                min   p25   p75   p95  max  mean  count start_yr end_yr
        values    0  25.0  75.0  95.0  100  50.0    101     2020   2020

    Calculate percentile thresholds without additional metadata columns

    .. doctest::

        >>> data = np.arange(101)
        >>> results = percentiles.calculate_fixed_percentile_thresholds(
        ...     data, percentiles=[5, 25, 75, 95], method='linear',
        ...     include_metadata=False)
        >>> results
                min  p05   p25   p75   p95  max
        values    0  5.0  25.0  75.0  95.0  100

    Calculate percentile thresholds using default 'weibull' method
        >>> data = np.arange(101)
        >>> results = percentiles.calculate_fixed_percentile_thresholds(
        ...     data, percentiles=[5, 25, 50, 75, 95],
        ...     include_metadata=False)
        >>> results
                min  p05   p25   p50   p75   p95  max
        values    0  4.1  24.5  50.0  75.5  95.9  100

    Calculate percentile thresholds from a small number of observations and
    mask out out of range percentile levels

        >>> data = np.arange(11)
        >>> results = percentiles.calculate_fixed_percentile_thresholds(
        ...     data, percentiles=np.array((1, 10, 50, 90, 99)),
        ...     include_metadata=False)
        >>> results
                min  p01  p10  p50  p90  p99  max
        values    0  NaN  0.2  5.0  9.8  NaN   10
    """
    if isinstance(data, pd.DataFrame):
        # set the df index
        if date_column_name is not None:
            data = data.set_index(date_column_name)
        # If data column name is not in dataframe
        if data_column_name not in data:
            raise ValueError('DataFrame missing data_column_name')
        data = data[data_column_name]

    # ignore 0 and 100 percentiles if passed in
    if isinstance(percentiles, np.ndarray):
        percentiles = percentiles[~np.isin(percentiles, [0, 100])]
    elif isinstance(percentiles, list):
        percentiles = [x for x in percentiles if x not in (0, 100)]

    if ignore_na:
        pct = np.nanpercentile(data, percentiles, method=method, **kwargs)
    else:
        pct = np.percentile(data, percentiles, method=method, **kwargs)

    # round values smaller than three decimal places to zero to avoid extremely
    # small threshold values being returned.
    pct[(pct > 0) & (pct < 0.001)] = 0

    df_out = pd.DataFrame(data={"values": pct}, index=percentiles)

    if mask_out_of_range:
        min_pct_rank = (1 - calculate_exceedance_probability_from_values(np.nanmin(data), data, method=method))*100  # noqa: E501
        max_pct_rank = (1 - calculate_exceedance_probability_from_values(np.nanmax(data), data, method=method))*100  # noqa: E501
        df_out.loc[(df_out.index > max_pct_rank) | (df_out.index < min_pct_rank)] = np.nan  # noqa: E501

    # transpose so percentile levels are columns
    df_out = df_out.T
    df_out.columns = "p" + df_out.columns.astype(str).str.zfill(2)

    if include_min_max:
        # add min as first column of dataframe and max as last column
        if ignore_na:
            df_out.insert(0, 'min', np.min(data))
            df_out['max'] = np.max(data)
        else:
            df_out.insert(0, 'min', np.nanmin(data))
            df_out['max'] = np.nanmax(data)
    if include_metadata:
        if isinstance(data, pd.Series):
            if not data.index.inferred_type == "datetime64":
                raise ValueError("Datetime index must be provided with include_metadata=True.")  # noqa: E501
        else:
            raise ValueError("Data input format must include a datetime index with include_metadata=True.")  # noqa: E501
        if ignore_na:
            df_out['mean'] = np.round(np.nanmean(data), 2)
        else:
            df_out['mean'] = np.round(np.mean(data), 2)
        df_out['count'] = len(data)
        df_out['start_yr'] = data.index.min().strftime('%Y')
        df_out['end_yr'] = data.index.max().strftime('%Y')

    return df_out


def calculate_variable_percentile_thresholds_by_day_of_year(
        df,
        data_column_name,
        percentiles=[5, 10, 25, 50, 75, 90, 95],
        method='weibull',
        date_column_name=None,
        data_type='daily',
        year_type='calendar',
        leading_values=0,
        trailing_values=0,
        clip_leap_day=False,
        ignore_na=True,
        include_min_max=True,
        include_metadata=True,
        mask_out_of_range=True,
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
        [5, 10, 25, 50, 75, 90, 95]. Note: Values of 0 and 100 are ignored as
        unbiased plotting position formulas do not assign values to 0 or 100th
        percentile.

    method : str, optional
        Method to use to calculate percentiles. Default is 'weibull' (Type 6).
        Additional available methods are 'interpolated_inverted_cdf' (Type 4),
        'hazen' (Type 5), 'linear' (Type 7), 'median_unbiased' (Type 8),
        and 'normal_unbiased' (Type 9).

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

    leading_values : int, optional
        For the temporal filtering, this is an argument setting the
        number of leading values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    trailing_values : int, optional
        For the temporal filtering, this is an argument setting the
        number of trailing values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    clip_leap_day : bool, optional
        If True, February 29 is removed from the DataFrame. Default is False.

    ignore_na : bool, optional
        Ignore NA values in percentile calculations

    include_min_max : bool, optional
        When set to True, include min and max streamflow value in addition to
        streamflow values for percentile levels. Default is True.

    include_metadata : bool, optional
        When set to True, return additional columns describing the data
        including count, mean, start_yr, end_yr. Default is True

    mask_out_of_range :  bool, optional
        When set to True, percentiles that are beyond the min/max percentile
        ranks of the observed data to be NA. Effect of this being enables is
        that high or low percentiles may not be calculated when few data points
        are available. Default is True.

    **kwargs : dict, optional
        Additional keyword arguments to pass to `numpy.percentile`.

    Returns
    -------
    percentiles : pandas.DataFrame
        DataFrame containing threshold percentiles of data by day of year.
        The DataFrame has a multi-index of 'doy' and 'year_type'.
        Returns a DataFrame of NaNs for each percentile/day if
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
        >>> results = percentiles.calculate_variable_percentile_thresholds_by_day_of_year(  # noqa: E501
        ...     df, "00060_Mean")
        >>> len(results.index)  # 366 days in a leap year
        366
    """
    # If the dataframe is empty, create a dummy dataframe to
    # run through function
    if clip_leap_day:
        # use a non-leap year as reference for empty df
        date_rng = pd.date_range(start='1901-01-01', end='1901-12-31')
    else:
        # use a leap year as reference for empty df
        date_rng = pd.date_range(start='1904-01-01', end='1904-12-31')
    if df.empty:
        warnings.warn('No valid data provided, returning NA values for percentile thresholds')  # noqa: E501
        df = pd.DataFrame(index=date_rng)
        df[data_column_name] = np.nan

    # If data column name is not in dataframe
    if data_column_name not in df:
        warnings.warn('DataFrame missing data_column_name, returning NA values for percentile thresholds')  # noqa: E501
        df = pd.DataFrame(index=date_rng)
        df[data_column_name] = np.nan
    # define year and day of year columns and convert date column to datetime
    # if necessary
    df = define_year_doy_columns(df, date_column_name=date_column_name,
                                 year_type=year_type,
                                 clip_leap_day=clip_leap_day)
    # do rolling average for time as needed
    data_type = set_data_type(data_type)
    df = rolling_average(df, data_column_name, data_type)

    # create an empty dataframe to hold percentiles based on day-of-year
    # ignore 0 and 100 percentiles if passed in
    if isinstance(percentiles, np.ndarray):
        percentiles = percentiles[~np.isin(percentiles, [0, 100])]
    elif isinstance(percentiles, list):
        percentiles = [x for x in percentiles if x not in (0, 100)]
    cols = [f"p{perc:02d}" for perc in percentiles]
    if include_min_max:
        cols = ['min'] + cols + ['max']
    if include_metadata:
        cols = cols + ['mean', 'count', 'start_yr', 'end_yr']
    doy_index = date_rng.day_of_year.values
    percentiles_by_day = pd.DataFrame(index=doy_index,
                                      columns=cols)

    # loop through days of year available
    for doy in doy_index:
        # get historical data for the day of year
        data = filter_data_by_time(df, doy, data_column_name,
                                   leading_values=leading_values,
                                   trailing_values=trailing_values,
                                   drop_na=ignore_na)
        if not data.empty:
            if not np.isnan(data).all():
                # calculate percentiles for the day of year
                # and add to DataFrame
                _pct = calculate_fixed_percentile_thresholds(
                    data.to_frame(), data_column_name,
                    percentiles=percentiles,
                    method=method, ignore_na=ignore_na,
                    include_min_max=include_min_max,
                    include_metadata=include_metadata,
                    mask_out_of_range=mask_out_of_range, **kwargs)
                percentiles_by_day.loc[doy_index == doy, :] = _pct.values.tolist()[0]  # noqa: E501
            else:
                # if all values are NA
                # set percentiles to NaN
                percentiles_by_day.loc[doy_index == doy, :] = np.nan
        else:
            # if the data subset for doy is empty
            # set percentiles to NaN
            percentiles_by_day.loc[doy_index == doy, :] = np.nan
    if clip_leap_day:
        wy_sub = 273
        cy_sub = 90
        wy_cy_sub = 365
    else:
        wy_sub = 274
        cy_sub = 91
        wy_cy_sub = 366
    # sort index by year type
    percentiles_by_day = percentiles_by_day.sort_index()
    if year_type == 'climate':
        doy_index = doy_index - cy_sub
        doy_index[doy_index < 1] += wy_cy_sub
    if year_type == 'water':
        doy_index = doy_index - wy_sub
        doy_index[doy_index < 1] += wy_cy_sub
    # reorder by water year or climate index and rename
    percentiles_by_day = percentiles_by_day.loc[doy_index]
    percentiles_by_day.reset_index(drop=True, inplace=True)
    percentiles_by_day.index = pd.MultiIndex.from_arrays(
        [percentiles_by_day.index + 1, [year_type] * len(doy_index)],
        names=['doy', 'year_type'])

    # return percentiles by day of year
    return percentiles_by_day


def calculate_variable_percentile_thresholds_by_day(
        df,
        data_column_name,
        percentiles=[5, 10, 25, 50, 75, 90, 95],
        method='weibull',
        date_column_name=None,
        data_type='daily',
        leading_values=0,
        trailing_values=0,
        clip_leap_day=False,
        ignore_na=True,
        include_min_max=True,
        include_metadata=True,
        mask_out_of_range=True,
        **kwargs):
    """Calculate variable percentile thresholds of data by day

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing data to calculate daily percentile thresholds for.

    data_column_name : str
        Name of column containing data to analyze.

    percentiles : array_like, optional
        Percentile thresholds to calculate, default is
        [5, 10, 25, 50, 75, 90, 95]. Note: Values of 0 and 100 are ignored as
        unbiased plotting position formulas do not assign values to 0 or 100th
        percentile.

    method : str, optional
        Method to use to calculate percentiles. Default is 'weibull' (Type 6).
        Additional available methods are 'interpolated_inverted_cdf' (Type 4),
        'hazen' (Type 5), 'linear' (Type 7), 'median_unbiased' (Type 8),
        and 'normal_unbiased' (Type 9).

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    data_type : str, optional
        The type of data. Must be one of 'daily', '7-day', '14-day', and
        '28-day'. Default is 'daily'. If '7-day', '14-day', or '28-day' is
        specified, the data will be averaged over the specified period. NaN
        values will be used for any days that do not have data. If present,
        NaN values will result in NaN values for the entire period.

    leading_values : int, optional
        For the temporal filtering, this is an argument setting the
        number of leading values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    trailing_values : int, optional
        For the temporal filtering, this is an argument setting the
        number of trailing values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    clip_leap_day : bool, optional
        If True, February 29 is removed from the DataFrame. Default is False.

    ignore_na : bool, optional
        Ignore NA values in percentile calculations

    include_min_max : bool, optional
        When set to True, include min and max streamflow value in addition to
        streamflow values for percentile levels. Default is True.

    include_metadata : bool, optional
        When set to True, return additional columns describing the data
        including count, mean, start_yr, end_yr. Default is True

    mask_out_of_range :  bool, optional
        When set to True, percentiles that are beyond the min/max percentile
        ranks of the observed data to be NA. Effect of this being enables is
        that high or low percentiles may not be calculated when few data points
        are available. Default is True.

    **kwargs : dict, optional
        Additional keyword arguments to pass to `numpy.percentile`.

    Returns
    -------
    percentiles : pandas.DataFrame
        DataFrame containing threshold percentiles of data by month-day.
        Will return a DataFrame of NaNs for each percentile/day if
        provided an empty DataFrame or DataFrame with insufficient data

    Examples
    --------
    Calculate default thresholds by day from some real data in
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
    """
    # If the dataframe is empty, create a dummy dataframe to
    # run through function
    if clip_leap_day:
        # use a non-leap year as reference for empty df
        date_rng = pd.date_range(start='1901-01-01', end='1901-12-31')
    else:
        # use a leap year as reference for empty df
        date_rng = pd.date_range(start='1904-01-01', end='1904-12-31')
    if df.empty:
        warnings.warn('No valid data provided, returning NA values for percentile thresholds')  # noqa: E501
        df = pd.DataFrame(index=date_rng)
        df[data_column_name] = np.nan
    # If data column name is not in dataframe
    if data_column_name not in df:
        warnings.warn('DataFrame missing data_column_name, returning NA values for percentile thresholds')  # noqa: E501
        df = pd.DataFrame(index=date_rng)
        df[data_column_name] = np.nan

    # set the df index
    if date_column_name is not None:
        df = df.set_index(date_column_name)

    # do rolling average for time as needed
    data_type = set_data_type(data_type)
    df = rolling_average(df, data_column_name, data_type)

    # create an empty dataframe to hold percentiles based on month-day
    # ignore 0 and 100 percentiles if passed in
    if isinstance(percentiles, np.ndarray):
        percentiles = percentiles[~np.isin(percentiles, [0, 100])]
    elif isinstance(percentiles, list):
        percentiles = [x for x in percentiles if x not in (0, 100)]
    cols = [f"p{perc:02d}" for perc in percentiles]
    if include_min_max:
        cols = ['min'] + cols + ['max']
    if include_metadata:
        cols = cols + ['mean', 'count', 'start_yr', 'end_yr']
    month_day_index = date_rng.strftime("%m-%d")
    percentiles_by_day = pd.DataFrame(index=month_day_index,
                                      columns=cols)
    percentiles_by_day.index.names = ['month_day']
    # loop through days of year available
    for month_day in month_day_index:
        # get historical data for the day of year
        data = filter_data_by_month_day(df, month_day, data_column_name,
                                        leading_values=leading_values,
                                        trailing_values=trailing_values,
                                        drop_na=ignore_na)
        if not data.empty:
            if not np.isnan(data).all():
                # calculate percentiles for the day of year
                # and add to DataFrame
                _pct = calculate_fixed_percentile_thresholds(
                    data.to_frame(), data_column_name,
                    percentiles=percentiles,
                    method=method, ignore_na=ignore_na,
                    include_min_max=include_min_max,
                    include_metadata=include_metadata,
                    mask_out_of_range=mask_out_of_range, **kwargs)
                percentiles_by_day.loc[month_day_index == month_day, :] = _pct.values.tolist()[0]  # noqa: E501
            else:
                # if all values are NA
                # set percentiles to NaN
                percentiles_by_day.loc[
                    month_day_index == month_day, :] = np.nan
        else:
            # if the data subset for doy is empty
            # set percentiles to NaN
            percentiles_by_day.loc[month_day_index == month_day, :] = np.nan

    return percentiles_by_day


def calculate_fixed_percentile_from_value(value, percentile_df):
    """Calculate percentile from a value and fixed percentile thresholds.

    This function enables faster calculation of the percentile associated with
    a given value if percentile values and corresponding fixed percentile
    thresholds are known from other data from the same station or site.
    This calculation is done using linear interpolation. A value greater than
    the largest streamflow value in the percentile threshold dataframe results
    in a percentile of 100. A value less than the smallest streamflow value in
    the percentile threshold dataframe results in a percentile of 0.

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
        :skipif: True  # docstrings test fails with np.float64

        >>> data = pd.DataFrame({'values': np.arange(1001),
        ...                      'date': pd.date_range('2020-01-01', '2022-09-27')}).set_index('date')  # noqa: E501
        >>> pcts_df = percentiles.calculate_fixed_percentile_thresholds(
        ...     data, 'values', percentiles=[5, 10, 25, 50, 75, 90, 95])
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
        ...     data, '00060_Mean',
        ...     percentiles=[5, 10, 25, 50, 75, 90, 95,],
        ...     method='linear')
        >>> new_data, _ = dataretrieval.nwis.get_dv(
        ...     "04288000", parameterCd="00060",
        ...     start="2022-01-01", end="2022-01-07")
        >>> new_data['est_pct'] = percentiles.calculate_fixed_percentile_from_value(  # noqa: E501
        ...     new_data['00060_Mean'], pcts_df)
        >>> new_data['est_pct'].to_list()
        [62.9, 75.0, 55.65, 47.54, 53.55, 55.32, 50.97]

    """
    # extract percentile levels and values
    thresholds = [int(col[1:]) for col in percentile_df.filter(like='p')]
    percentile_values = percentile_df.filter(like='p').iloc[0].to_list()
    if 'min' and 'max' in percentile_df.columns:
        thresholds = [0] + thresholds + [100]
        percentile_values = [percentile_df.at['values', 'min']] + \
            percentile_values + [percentile_df.at['values', 'max']]
    # ensure all values are set to float type for interpolation
    thresholds = np.array(thresholds, dtype=np.float32)
    percentile_values = np.array(percentile_values, dtype=np.float32)
    # check if there are NA percentile levels and remove them so they are
    # ignored during interpolation
    na_mask = ~np.isnan(percentile_values)
    percentile_values = percentile_values[na_mask]
    thresholds = thresholds[na_mask]
    # do and return linear interpolation
    if len(percentile_values) > 0:
        estimated_percentile = np.interp(value, percentile_values,
                                         thresholds,
                                         left=0, right=100).round(2)
    else:
        estimated_percentile = np.nan
    return estimated_percentile


def calculate_variable_percentile_from_value(value, percentile_df, month_day):
    """Calculate percentile from a value and variable percentile thresholds.

    This function enables faster calculation of the percentile associated with
    a given value for a single day of the year if percentile values and
    corresponding variable percentile thresholds are known from other data from
    the same station or site. This calculation is done using linear
    interpolation. A value greater than the largest streamflow value in the
    percentile threshold dataframe for the month-day of interest results
    in a percentile of 100. A value less than the smallest streamflow value in
    the percentile threshold dataframe results in a percentile of 0.

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

    month_day : str
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
        ...     percentiles=[5, 10, 25, 50, 75, 90, 95],
        ...     method='linear')
        >>> new_percentile = percentiles.calculate_variable_percentile_from_value(  # noqa: E501
        ...     500, pcts_df, '06-30')
        >>> new_percentile
        96.58
    """
    # retrieve percentile thresholds for the day of year of interest
    pct_values = percentile_df.loc[percentile_df.index.get_level_values('month_day') == month_day]  # noqa: E501

    if not pct_values.empty and not pct_values.isnull().all().all():
        pct_values = pct_values.reset_index(drop=True)
        pct_values = pct_values.rename(index={0: "values"})
        est_pct = calculate_fixed_percentile_from_value(value, pct_values)
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
    thresholds. This calculation is done using linear interpolation.
    A value greater than the largest streamflow value in the
    percentile threshold dataframe for the month-day of interest results
    in a percentile of 100. A value less than the smallest streamflow value in
    the percentile threshold dataframe results in a percentile of 0.

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
        ...     percentiles=[5, 10, 25, 50, 75, 90, 95],
        ...     method='linear')
        >>> new_data, _ = dataretrieval.nwis.get_dv(
        ...     "04288000", parameterCd="00060",
        ...     start="2022-01-01", end="2022-01-07")
        >>> new_percentiles = percentiles.calculate_multiple_variable_percentiles_from_values(  # noqa: E501
        ...     new_data, '00060_Mean', pcts_df)
        >>> new_percentiles['est_pct'].to_list()
        [64.81, 77.7, 56.67, 45.0, 55.59, 59.38, 49.12]
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
