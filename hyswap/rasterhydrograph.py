"""Raster hydrograph functionality."""

import pandas as pd
from hyswap.utils import rolling_average
from hyswap.utils import define_year_doy_columns


def format_data(df, data_column_name, date_column_name=None,
                data_type='daily', year_type='calendar',
                begin_year=None, end_year=None, **kwargs):
    """
    Format data for raster hydrograph.

    Parameters
    ----------
    df : pandas.DataFrame
        The data to format. Must have a date column or the index must be the
        date values.
    data_column_name : str
        The name of the column containing the data.
    date_column_name : str, optional
        The name of the column containing the date. Default is None which
        assumes the index is the date.
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
    begin_year : int, optional
        The first year to include in the data. Default is None which uses the
        first year in the data.
    end_year : int, optional
        The last year to include in the data. Default is None which uses the
        last year in the data.
    **kwargs
        Keyword arguments to pass to the pandas.DataFrame.rolling method.

    Returns
    -------
    pandas.DataFrame
        The formatted data starting on the first day of the first year and
        ending on the last day of the last year with the specified data type
        and year type.

    Examples
    --------
    Formatting synthetic daily data for a raster hydrograph.

    .. doctest::

        >>> df = pd.DataFrame({'date': pd.date_range('1/1/2010', '12/31/2010'),
        ...                    'data': np.random.rand(365)})
        >>> df_formatted = rasterhydrograph.format_data(df, 'data', 'date')
        >>> df_formatted.index[0]
        2010
        >>> len(df_formatted.columns)
        365

    Formatting real daily data for a raster hydrograph.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> df, _ = dataretrieval.nwis.get_dv(
        ...     "03586500", parameterCd="00060",
        ...     start="2000-01-01", end="2002-12-31")
        >>> df_formatted = rasterhydrograph.format_data(df, '00060_Mean')
        >>> df_formatted.index[0]
        2000
        >>> len(df_formatted.columns)
        365
    """
    # check inputs, set date to index, define year/doy columns
    df = _check_inputs(df, data_column_name, date_column_name,
                       data_type, year_type, begin_year, end_year)

    # calculate the date range
    date_range = _calculate_date_range(df, begin_year, end_year)

    # format date_range as YYYY-MM-DD
    date_range = date_range.strftime('%Y-%m-%d')

    # set data type
    data_type = _set_data_type(data_type)

    # make output data frame
    # calculation of rolling mean is done on the data column
    df_out = rolling_average(df, data_column_name, data_type, **kwargs)

    # convert date index to YYYY-MM-DD format
    df_out.index = df_out.index.strftime('%Y-%m-%d')

    # fill in missing dates as nan values to complete the years
    df_out = df_out.reindex(index=date_range)

    # convert date index to datetime format
    df_out.index = pd.to_datetime(df_out.index)

    # adjust for leap years by removing NaN rows
    df_out = df_out.dropna(axis=0, how='all')

    # set index to year and day of year columns
    df_out = df_out.pivot(index='index_year', columns='index_doy',
                          values=data_column_name)

    # reverse order of the index so year order matches legacy Water Watch
    df_out = df_out.iloc[::-1]

    # remove all NaN columns and rows
    df_out = df_out.dropna(axis=1, how='all')
    df_out = df_out.dropna(axis=0, how='all')

    return df_out


def _check_inputs(df, data_column_name, date_column_name,
                  data_type, year_type, begin_year, end_year):
    """Private function to check inputs for the format_data function.

    Parameters
    ----------
    df : pandas.DataFrame
        The data to format. Must have a date column or the index must be the
        date values.
    data_column_name : str
        The name of the column containing the data.
    date_column_name : str, None
        The name of the column containing the date or None if the index is
        the date.
    data_type : str
        The type of data. Must be one of 'daily', '7-day', '14-day', and
        '28-day'. If '7-day', '14-day', or '28-day' is
        specified, the data will be averaged over the specified period. NaN
        values will be used for any days that do not have data. If present,
        NaN values will result in NaN values for the entire period.
    year_type : str
        The type of year to use. Must be one of 'calendar' or 'water'.
        'calendar' starts the year on January 1 and ends on
        December 31. 'water' starts the year on October 1 and ends on
        September 30.
    begin_year : int, None
        The first year to include in the data. If None, the first year in
        the data will be used.
    end_year : int, None
        The last year to include in the data. If None, the last year in the
        data will be used.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe with the date column formatted as a datetime and set as
        the index. New year and doy (day of year) columns are added too and
        are set based on the year_type. Feb 29th is also removed from the
        dataframe if it exists.
    """
    # check the data frame
    if not isinstance(df, pd.DataFrame):
        raise TypeError('df must be a pandas.DataFrame')

    # check data type
    if not isinstance(data_type, str):
        raise TypeError('data_type must be a string')
    if data_type not in ['daily', '7-day', '14-day', '28-day']:
        raise ValueError('data_type must be one of "daily", "7-day", '
                         '"14-day", and "28-day"')

    # check data column name
    if not isinstance(data_column_name, str):
        raise TypeError('data_column_name must be a string')

    # check date column name
    if date_column_name is not None:
        if not isinstance(date_column_name, str):
            raise TypeError('date_column_name must be a string')

    # check begin year
    if begin_year is not None:
        if not isinstance(begin_year, int):
            raise TypeError('begin_year must be an integer')
        if date_column_name is not None:
            if begin_year < df['date'].dt.year.min():
                raise ValueError('begin_year must be greater than or equal to '
                                 'the minimum year in the data')
        else:
            if begin_year < df.index.year.min():
                raise ValueError('begin_year must be greater than or equal to '
                                 'the minimum year in the data')

    # check end year
    if end_year is not None:
        if not isinstance(end_year, int):
            raise TypeError('end_year must be an integer')
        if date_column_name is not None:
            if end_year > df['date'].dt.year.max():
                raise ValueError('end_year must be less than or equal to the '
                                 'maximum year in the data')
        else:
            if end_year > df.index.year.max():
                raise ValueError('end_year must be less than or equal to the '
                                 'maximum year in the data')

    # define year and doy columns and set index as date col if needed
    df = define_year_doy_columns(df, date_column_name, year_type,
                                 clip_leap_day=True)

    return df


def _calculate_date_range(df, begin_year, end_year):
    """Private function to calculate the date range and set the index.

    Parameters
    ----------
    df : pandas.DataFrame
        The data to format. Must have a date column or the index must be the
        date values.
    begin_year : int, None
        The first year to include in the data. If None, the first year in
        the data will be used.
    end_year : int, None
        The last year to include in the data. If None, the last year in the
        data will be used.

    Returns
    -------
    date_range : pandas.DatetimeIndex
        The date range.
    """
    # set begin year
    if begin_year is None:
        begin_year = df['index_year'].min()
    begin_date = df.loc[df['index_year'] == begin_year].index.min()

    # set end year
    if end_year is None:
        end_year = df['index_year'].max()
    end_date = df.loc[df['index_year'] == end_year].index.max()

    # set date range
    date_range = pd.date_range(begin_date, end_date)

    return date_range


def _set_data_type(data_type):
    """Private function to set the data type.

    Parameters
    ----------
    data_type : str
        The type of data. Must be one of 'daily', '7-day', '14-day', and
        '28-day'. If '7-day', '14-day', or '28-day' is
        specified, the data will be averaged over the specified period. NaN
        values will be used for any days that do not have data. If present,
        NaN values will result in NaN values for the entire period.

    Returns
    -------
    data_type : str
        The formatted frequency string to be used with
        pandas.DataFrame.rolling to calculate the average over the correct
        temporal period.
    """
    if data_type == 'daily':
        data_type = 'D'
    elif data_type == '7-day':
        data_type = '7D'
    elif data_type == '14-day':
        data_type = '14D'
    elif data_type == '28-day':
        data_type = '28D'

    return data_type
