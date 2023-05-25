"""Utility functions for hyswap."""


def filter_approved_data(data, filter_column=None):
    """Filter a dataframe to only return approved "A" (or "A, e") data.

    Parameters
    ----------
    data : pandas.DataFrame
        The data to filter.
    filter_column : string
        The column upon which to filter. If None, an error will be raised.

    Returns
    -------
    pandas.DataFrame
        The filtered data.

    Examples
    --------
    Filter synthetic data to only return approved data. First make some
    synthetic data.

    .. doctest::

        >>> df = pd.DataFrame({
        ...     'data': [1, 2, 3, 4],
        ...     'approved': ['A', 'A', 'P', 'P']})
        >>> df.shape
        (4, 2)

    Then filter the data to only return approved data.

    .. doctest::

        >>> df = utils.filter_approved_data(df, filter_column='approved')
        >>> df.shape
        (2, 2)
    """
    if filter_column is None:
        raise ValueError("filter_column must be specified.")
    return data.loc[((data[filter_column] == "A") |
                     (data[filter_column] == "A, e"))]


def rolling_average(df, data_column_name, data_type, **kwargs):
    """Calculate a rolling average for a dataframe.

    Default behavior right-aligns the window used for the rolling average,
    and returns NaN values if any of the values in the window are NaN.
    Properties of the windowing can be changed by passing additional keyword
    arguments which are fed to `pandas.DataFrame.rolling`.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to calculate the rolling average for.
    data_column_name : string
        The name of the column to calculate the rolling average for.
    data_type : string
        The formatted frequency string to be used with
        pandas.DataFrame.rolling to calculate the average over the correct
        temporal period.
    **kwargs
        Additional keyword arguments to be passed to
        `pandas.DataFrame.rolling`.

    Returns
    -------
    pandas.DataFrame
        The output dataframe with the rolling average values.
    """
    df_out = df.copy(deep=True)
    df_out[data_column_name] = df_out[data_column_name].rolling(
        data_type, **kwargs).mean()
    return df_out


def filter_data_by_time(df, value, data_column_name, date_column_name=None,
                        time_interval='day',
                        leading_values=0, trailing_values=0):
    """Filter data by some time interval.

    DataFrame containing data to filter. Expects datetime information to be
    available in the index or in a column named `date_column_name`. The
    returned `pandas.Series` object will have the datetimes for the specified
    time (day, month, year) as the index, and the corresponding data from the
    `data_column_name` column as the values.

    Parameters
    ----------
    value : int
        Time value to use for filtering; value can be a day of year (1-366),
        month (1-12), or year (4 digit year).

    data_column_name : str
        Name of column containing data to filter.

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    time_interval : str, optional
        Time interval to filter by. Must be one of 'day', 'month', or 'year'.
        Default is 'day'.

    leading_values : int, optional
        Number of leading values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    trailing_values : int, optional
        Number of trailing values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    Returns
    -------
    data : pandas.Series
        Data from the specified day of year.

    Examples
    --------
    Filter some synthetic data by day of year. First make some synthetic data.

    .. doctest::

        >>> df = pd.DataFrame({
        ...     'data': [1, 2, 3, 4],
        ...     'date': pd.date_range('2019-01-01', '2019-01-04')})
        >>> df.shape
        (4, 2)

    Then filter the data to get data from day 1.

    .. doctest::

        >>> data = utils.filter_data_by_time(
        ...     df, 1, 'data', date_column_name='date')
        >>> data.shape
        (1,)

    Acquire and filter some real daily data to get all Jan. 1 data.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> df, _ = dataretrieval.nwis.get_dv(
        ...     "03586500", parameterCd="00060",
        ...     start="2000-01-01", end="2003-01-05")
        >>> data = utils.filter_data_by_time(df, 1, '00060_Mean')
        >>> data.shape
        (4,)
    """
    # make date column the index if it is not already
    if date_column_name is not None:
        df = df.set_index(date_column_name)
    # check that time_interval is valid
    if time_interval not in ['day', 'month', 'year']:
        raise ValueError(
            'time_interval must be one of "day", "month", or "year".')
    if time_interval == 'day':
        if (leading_values == 0) and (trailing_values == 0):
            # grab data from the specified day of year
            dff = df.loc[df.index.dayofyear == value, data_column_name]
        else:
            # grab data from the specified day of year and include leading
            # and trailing values
            dff = df.loc[
                (df.index.dayofyear >= value - leading_values) &
                (df.index.dayofyear <= value + trailing_values),
                data_column_name]
    elif time_interval == 'month':
        # grab data from the specified month
        dff = df.loc[df.index.month == value, data_column_name]
    elif time_interval == 'year':
        # grab data from the specified year
        dff = df.loc[df.index.year == value, data_column_name]
    # return data as a pandas Series where the index is the date
    return dff


def calculate_metadata(data):
    """Calculate metadata for a series of data.

    Parameters
    ----------
    data : pandas.Series
        The data to calculate the metadata for. Expected to have a datetime
        index.

    Returns
    -------
    dict
        The calculated metadata which includes the number of years of data,
        the number of data points, any gaps in the data, and the start and end
        dates of the data, the number of 0 values, the number of NA values,
        as well as the number of low (typically low flow <= 0.01) values.
    """
    # initialize the metadata dictionary
    meta = {}
    # calculate the number of unique years of data
    meta["n_years"] = len(data.index.year.unique())
    # calculate the number of data points that are not nan
    meta["n_data"] = len(data.loc[~data.isna()])
    # calculate the number of gaps in the data - missing years
    expected_years = data.index.year.max() - data.index.year.min() + 1
    meta["n_missing_years"] = expected_years - meta["n_years"]
    # calculate the start and end dates of the data
    meta["start_date"] = data.index.min().strftime("%Y-%m-%d")
    meta["end_date"] = data.index.max().strftime("%Y-%m-%d")
    # calculate the number of 0 values
    meta["n_zeros"] = len(data.loc[data == 0])
    # calculate the number of nan values
    meta["n_nans"] = len(data.loc[data.isna()])
    # calculate the number of low values (below 0.01)
    meta["n_lows"] = len(data.loc[data <= 0.01])

    return meta


def define_year_doy_columns(df, date_column_name=None, year_type='calendar',
                            clip_leap_day=False):
    """Function to add year and day of year columns to a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing data to filter. Expects datetime information to be
        available in the index or in a column named `date_column_name`.

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    year_type : str, optional
        The type of year to use. Must be one of 'calendar', 'water', or
        'climate'. Default is 'calendar' which starts the year on January 1
        and ends on December 31. 'water' starts the year on October 1 and
        ends on September 30 of the following year which is the "water year".
        For example, October 1, 2010 to September 30, 2011 is "water year
        2011". 'climate' years begin on April 1 and end on March 31 of the
        following year, they are numbered by the ending year. For example,
        April 1, 2010 to March 31, 2011 is "climate year 2011".

    clip_leap_day : bool, optional
        If True, February 29 is removed from the DataFrame. Default is False.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with year and day of year columns added. Also makes the
        date_column_name the index of the DataFrame.
    """
    # set the df index
    if date_column_name is not None:
        df = df.set_index(date_column_name)
    # check that year_type is valid
    if year_type not in ['calendar', 'water', 'climate']:
        raise ValueError(
            'year_type must be one of "calendar", "water", or "climate".')
    # add year and day of year columns
    if year_type == 'calendar':
        df['year'] = df.index.year
        df['doy'] = df.index.dayofyear
    elif year_type == 'water':
        # set water years
        df['year'] = df.index.year.where(df.index.month < 10,
                                         df.index.year + 1)
        # get calendar day of year
        df['doy'] = df.index.dayofyear
        # adjust Oct 1 to be day 1 of water year for leap and non-leap years
        df.loc[df.index.is_leap_year & (df.index.month >= 10), 'doy'] -= 274
        df.loc[~df.index.is_leap_year & (df.index.month >= 10), 'doy'] -= 273
        # adjust Jan 1 accordingly for leap and non-leap years
        df.loc[df.index.month < 10, 'doy'] += 92
    elif year_type == 'climate':
        # set climate years
        df['year'] = df.index.year.where(df.index.month < 4,
                                         df.index.year + 1)
        # get calendar day of year
        df['doy'] = df.index.dayofyear
        # adjust Apr 1 to be day 1 of climate year for leap and non-leap years
        df.loc[df.index.is_leap_year & (df.index.month >= 4), 'doy'] -= 91
        df.loc[~df.index.is_leap_year & (df.index.month >= 4), 'doy'] -= 90
        # adjust Jan 1 to be day 276 of climate year for all years
        df.loc[df.index.month < 4, 'doy'] += 275
    # clip leap year and adjustment
    if clip_leap_day:
        df = df.loc[~((df.index.month == 2) & (df.index.day == 29))]
        if year_type == 'calendar':
            df.loc[df.index.is_leap_year & (df.index.month > 2), 'doy'] -= 1
        elif year_type == 'water':
            df.loc[df.index.is_leap_year &
                   (df.index.month > 2) &
                   (df.index.month < 10), 'doy'] -= 1
        elif year_type == 'climate':
            df.loc[df.index.is_leap_year &
                   (df.index.month > 2) &
                   (df.index.month < 4), 'doy'] -= 1
    # sort the df by year and day of year
    df = df.sort_values(['year', 'doy'])
    return df
